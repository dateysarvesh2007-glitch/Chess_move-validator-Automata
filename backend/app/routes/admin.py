from fastapi import APIRouter, Depends, HTTPException
import os

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Dependency for admin authentication
from app.dependencies import get_admin_token

@router.get("/status")
def admin_status(admin: bool = Depends(get_admin_token)):
    """Protected admin status endpoint."""
    return {"status": "admin ok", "service": "ChessMove Validator", "env": os.getenv("ENV", "dev")}

@router.post("/purge")
def purge_data(admin: bool = Depends(get_admin_token)):
    """Placeholder admin action to purge temporary data (no-op)."""
    # Real implementation would clear caches, temporary files, etc.
    return {"result": "purge executed (no-op)"}
