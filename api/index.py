"""Vercel Serverless Function entrypoint for FastAPI backend."""

import sys
from pathlib import Path

# Add backend directory to sys.path for runtime execution
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from app.main import app  # type: ignore[import-not-found]
except ImportError:
    # Fallback to satisfy IDE static analysis / language servers
    from backend.app.main import app  # type: ignore[import-not-found]

__all__ = ["app"]
