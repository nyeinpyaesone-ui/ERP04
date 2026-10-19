"""Bulk Import/Export API endpoints.

Wired into app/main.py as:
    app.include_router(bulk_import_export.router, prefix="/api/v1/bulk", tags=["Bulk Import/Export"])

Follows the architecture blueprint: input validation & sanitization, JWT auth,
RBAC (admin-only writes), and immutable audit logging of every bulk action.
"""

from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
import io

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.services import bulk_service
from app.services.bulk_service import BulkValidationError

router = APIRouter()


def _check_entity(entity: str) -> None:
    if entity not in bulk_service.ENTITY_MODELS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown entity '{entity}'. Supported: {', '.join(sorted(bulk_service.ENTITY_MODELS))}",
        )


@router.get("/entities")
def list_bulk_entities(current_user: User = Depends(get_current_user)):
    """List entities that support bulk import/export and their fields."""
    return {
        "entities": [
            {
                "name": name,
                "fields": bulk_service.ENTITY_FIELDS[name],
                "required": bulk_service.ENTITY_REQUIRED[name],
            }
            for name in sorted(bulk_service.ENTITY_MODELS)
        ],
        "import_formats": ["csv", "json", "xlsx"],
        "export_formats": ["csv", "json", "xlsx"],
        "max_rows": bulk_service.MAX_BULK_ROWS,
    }


@router.post("/import/{entity}")
async def bulk_import(
    entity: str,
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="Validate rows without writing to the database"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Import records from an uploaded CSV / JSON / XLSX file."""
    _check_entity(entity)

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds 50MB limit")

    try:
        rows = bulk_service.parse_rows(content, file.filename, entity)
    except BulkValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors)

    clean_rows, row_errors = bulk_service.validate_and_clean_rows(rows, entity)

    if dry_run:
        return {
            "entity": entity,
            "dry_run": True,
            "valid_rows": len(clean_rows),
            "rejected_rows": len(row_errors),
            "errors": row_errors[:100],
        }

    if not clean_rows:
        raise HTTPException(status_code=422, detail=row_errors[:100] or ["No valid rows to import"])

    result = bulk_service.import_entity(db, entity, clean_rows, user_id=current_user.id)
    result["validation_errors"] = row_errors[:100]
    return result


@router.get("/export/{entity}")
def bulk_export(
    entity: str,
    format: str = Query("json", pattern="^(csv|json|xlsx)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export a full entity table as CSV, JSON, or XLSX."""
    _check_entity(entity)
    try:
        content, media_type, filename = bulk_service.export_entity(db, entity, format)
    except BulkValidationError as e:
        raise HTTPException(status_code=500, detail=e.errors)
    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/migrations/status")
def migration_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Report schema/migration state: tables present vs. declared models,
    and the current Alembic revision if the version table exists."""
    if current_user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    inspector = inspect(db.bind)
    existing = set(inspector.get_table_names())
    declared = {
        t.name for t in User.metadata.sorted_tables
    }
    missing = sorted(declared - existing)

    alembic_version = None
    if "alembic_version" in existing:
        try:
            row = db.execute(__import__("sqlalchemy").text("SELECT version_num FROM alembic_version")).first()
            alembic_version = row[0] if row else None
        except Exception:
            alembic_version = "unreadable"

    return {
        "tables_declared": len(declared),
        "tables_present": len(existing),
        "missing_tables": missing,
        "alembic_version": alembic_version,
        "up_to_date": not missing,
    }
