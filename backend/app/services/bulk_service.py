"""Bulk Import/Export service.

Implements the Asynchronous communication pattern from the architecture
blueprint (docs/ARCHITECTURE_DECISIONS.md + knowledge-base 05_architecture_visualization.md):
"Task queued, processed later (report generation, bulk import)".

Supported entities: contacts, products, employees, tasks.
Supported formats: CSV and JSON (import), CSV / JSON / XLSX (export).
Every bulk operation is written to the audit trail via log_activity().
"""

import csv
import io
import json
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Contact, Employee, Product, Task
from app.services.activity_log import log_activity

# ---------------------------------------------------------------------------
# Entity registry: field allow-lists guard against injection of unknown cols
# ---------------------------------------------------------------------------

ENTITY_MODELS = {
    "contacts": Contact,
    "products": Product,
    "employees": Employee,
    "tasks": Task,
}

ENTITY_FIELDS = {
    "contacts": [
        "first_name", "last_name", "email", "phone", "title",
        "status", "source", "notes", "lifetime_value",
    ],
    "products": [
        "sku", "name", "description", "category", "unit_price",
        "cost_price", "quantity_in_stock", "reorder_level", "reorder_quantity",
    ],
    "employees": [
        "employee_code", "job_title", "salary", "hire_date",
        "status", "employment_type", "address",
    ],
    "tasks": [
        "project_id", "title", "description", "status",
        "priority", "assigned_to", "due_date", "estimated_hours",
    ],
}

# Fields that must be present on every imported row
ENTITY_REQUIRED = {
    "contacts": ["first_name", "last_name"],
    "products": ["sku", "name"],
    "employees": ["employee_code", "job_title", "hire_date"],
    "tasks": ["project_id", "title"],
}

MAX_BULK_ROWS = 10_000


class BulkValidationError(Exception):
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("; ".join(errors[:20]))


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_rows(content: bytes, filename: str, entity: str) -> List[Dict[str, Any]]:
    """Parse uploaded file content into a list of row dicts."""
    ext = (filename or "").lower().rsplit(".", 1)[-1]
    text = content.decode("utf-8-sig")

    if ext == "json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise BulkValidationError([f"Invalid JSON: {e}"])
        if not isinstance(data, list):
            raise BulkValidationError(["JSON payload must be an array of objects"])
        return data

    if ext == "csv":
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise BulkValidationError(["CSV file has no header row"])
        return [dict(row) for row in reader]

    if ext in ("xlsx", "xls"):
        try:
            from openpyxl import load_workbook
        except ImportError:
            raise BulkValidationError(["Excel support requires the 'openpyxl' package"])
        wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        rows_iter = ws.iter_rows(values_only=True)
        header = next(rows_iter, None)
        if not header:
            raise BulkValidationError(["Spreadsheet has no header row"])
        header = [str(h).strip() if h is not None else "" for h in header]
        return [
            {h: v for h, v in zip(header, row)}
            for row in rows_iter
            if any(v is not None and str(v).strip() != "" for v in row)
        ]

    raise BulkValidationError([f"Unsupported file format: .{ext} (use csv, json, or xlsx)"])


def validate_and_clean_rows(rows: List[Dict[str, Any]], entity: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Filter rows to allow-listed fields, drop empties, report problems."""
    allowed = set(ENTITY_FIELDS[entity])
    required = ENTITY_REQUIRED[entity]
    clean: List[Dict[str, Any]] = []
    errors: List[str] = []

    for i, raw in enumerate(rows, start=2):  # line 1 = header in CSV
        if len(clean) >= MAX_BULK_ROWS:
            errors.append(f"Row limit of {MAX_BULK_ROWS} reached; remaining rows skipped")
            break
        if not isinstance(raw, dict):
            errors.append(f"Line {i}: not an object/row, skipped")
            continue
        row = {}
        for key, value in raw.items():
            if key is None:
                continue
            key = str(key).strip().lower()
            if key not in allowed:
                continue  # silently ignore unknown columns
            if value == "" or value is None:
                continue
            row[key] = value
        missing = [f for f in required if f not in row]
        if missing:
            errors.append(f"Line {i}: missing required field(s): {', '.join(missing)}")
            continue
        clean.append(row)

    return clean, errors


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def import_entity(db: Session, entity: str, rows: List[Dict[str, Any]], user_id: Optional[int]) -> Dict[str, Any]:
    model = ENTITY_MODELS[entity]
    created, failed = 0, []
    for i, row in enumerate(rows, start=1):
        try:
            db.add(model(**row))
            db.commit()
            created += 1
        except Exception as e:
            db.rollback()
            failed.append({"row": i, "error": str(e)[:200]})
    log_activity(
        db, user_id=user_id, action="bulk_import",
        entity_type=entity, details={"created": created, "failed": len(failed)},
    )
    return {"entity": entity, "created": created, "failed": failed}


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_entity(db: Session, entity: str, fmt: str = "json") -> Tuple[bytes, str, str]:
    """Return (content_bytes, media_type, filename) for the entity table."""
    model = ENTITY_MODELS[entity]
    fields = ENTITY_FIELDS[entity]
    records: List[Dict[str, Any]] = []
    for obj in db.query(model).all():
        rec = {}
        for f in fields:
            v = getattr(obj, f, None)
            rec[f] = str(v) if v is not None and not isinstance(v, (int, float, bool)) else v
        records.append(rec)

    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
        return buf.getvalue().encode("utf-8"), "text/csv", f"{entity}_export.csv"

    if fmt == "xlsx":
        try:
            from openpyxl import Workbook
        except ImportError:
            raise BulkValidationError(["Excel export requires the 'openpyxl' package"])
        wb = Workbook()
        ws = wb.active
        ws.title = entity
        ws.append(fields)
        for rec in records:
            ws.append([rec.get(f) for f in fields])
        out = io.BytesIO()
        wb.save(out)
        return out.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", f"{entity}_export.xlsx"

    return json.dumps(records, indent=2, default=str).encode("utf-8"), "application/json", f"{entity}_export.json"
