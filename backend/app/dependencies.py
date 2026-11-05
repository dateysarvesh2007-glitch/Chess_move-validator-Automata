import os
from fastapi import Header, HTTPException, Depends

def get_admin_token(x_admin_token: str = Header(..., alias="X-Admin-Token")):
    """Simple admin token check.
    The token is stored in the environment variable ADMIN_TOKEN.
    Raise 403 if missing or incorrect.
    """
    expected = os.getenv("ADMIN_TOKEN")
    if not expected:
        raise HTTPException(status_code=500, detail="ADMIN_TOKEN not configured on server")
    if x_admin_token != expected:
        raise HTTPException(status_code=403, detail="Invalid admin token")
    return True
