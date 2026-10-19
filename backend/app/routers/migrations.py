"""Alembic migration management endpoints.

Exposes safe, read-only migration metadata (history, current revision,
pending revisions) so ops tooling and the admin portal can inspect schema
state without shell access. Applying/rolling back migrations stays a
CLI/docker-compose operation per docs/DATABASE_MIGRATIONS.md.
"""

import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import User

router = APIRouter()

# backend/ directory contains alembic.ini and the alembic/ folder
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _require_admin(current_user: User) -> None:
    if current_user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Admin access required")


def _get_alembic_config():
    try:
        from alembic.config import Config
    except ImportError:
        raise HTTPException(status_code=501, detail="alembic is not installed")
    ini_path = os.path.join(BACKEND_DIR, "alembic.ini")
    cfg = Config(ini_path) if os.path.exists(ini_path) else Config()
    cfg.set_main_option("script_location", os.path.join(BACKEND_DIR, "alembic"))
    cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    return cfg


@router.get("/history")
def migration_history(current_user: User = Depends(get_current_user)):
    """List all known revisions from the alembic versions directory."""
    _require_admin(current_user)
    versions_dir = os.path.join(BACKEND_DIR, "alembic", "versions")
    history = []
    if os.path.isdir(versions_dir):
        for fname in sorted(os.listdir(versions_dir)):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(versions_dir, fname)
            rev = fname.split("_")[0]
            doc = ""
            with open(path, "r", encoding="utf-8") as fh:
                head = fh.read(500)
                # crude docstring grab: first quoted line
                for line in head.splitlines():
                    s = line.strip().strip('"').strip("'")
                    if s and not s.startswith(("from", "#", '"""')):
                        doc = s
                        break
            history.append({"revision": rev, "file": fname, "description": doc, "path": path})
    return {"count": len(history), "revisions": history}


@router.get("/current")
def current_revision(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Show the revision currently stamped on the database (if any)."""
    _require_admin(current_user)
    from sqlalchemy import text, inspect

    inspector = inspect(db.bind)
    if "alembic_version" not in inspector.get_table_names():
        return {"stamped": False, "revision": None,
                "note": "alembic_version table not found; run 'alembic stamp <rev>' or 'alembic upgrade head'"}
    row = db.execute(text("SELECT version_num FROM alembic_version")).first()
    return {"stamped": row is not None, "revision": row[0] if row else None}


@router.get("/head")
def head_revision(current_user: User = Depends(get_current_user)):
    """Return the latest revision identifier available in the repo."""
    _require_admin(current_user)
    try:
        from alembic.script import ScriptDirectory

        cfg = _get_alembic_config()
        script = ScriptDirectory.from_config(cfg)
        heads = script.get_heads()
        return {"heads": heads}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read alembic scripts: {e}")
