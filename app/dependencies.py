"""
Shared FastAPI dependencies for protected routes.
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import models
from app.auth_utils import decode_access_token
from app.config import settings
from app.database import get_db

# FastAPI auto-detects this as an OpenAPI security scheme, which is what
# makes the padlock/"Authorize" button appear in Swagger UI. auto_error=False
# means it does NOT reject the request by itself if the header is missing -
# it just returns None, so we can fall through to checking the cookie below.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_admin(
    request: Request,
    db: Session = Depends(get_db),
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> models.Admin:
    """
    Identifies the current admin from EITHER of two places, checked in order:

    1. An "Authorization: Bearer <token>" header - this is what Swagger UI's
       "Authorize" button sends, and what any non-browser API client would use.
    2. The httpOnly "access_token" cookie - this is what the Next.js
       frontend relies on; browsers attach it automatically.
    """
    token: Optional[str] = None

    if bearer is not None:
        token = bearer.credentials
    else:
        token = request.cookies.get(settings.auth_cookie_name)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    username = decode_access_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session, please log in again",
        )

    admin = db.query(models.Admin).filter(models.Admin.username == username).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session, please log in again",
        )

    return admin
