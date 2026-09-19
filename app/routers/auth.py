"""
Auth routes - API version 1.

There is no public signup endpoint here on purpose: admins are created
with the app/create_admin.py CLI script, run manually, not exposed over HTTP.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth_utils import create_access_token, verify_password
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_admin

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=schemas.AdminLoginResponse, summary="Log in as an admin")
def login(credentials: schemas.AdminLogin, response: Response, db: Session = Depends(get_db)):
    """Verifies credentials and sets a signed JWT in an httpOnly cookie on success."""
    admin = db.query(models.Admin).filter(models.Admin.username == credentials.username).first()

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )

    if not admin:
        raise invalid_credentials
    if not verify_password(credentials.password, admin.password_hash):
        raise invalid_credentials

    token = create_access_token(subject=admin.username)

    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=False,       # set True when served over HTTPS
        samesite="lax",
        max_age=settings.jwt_expire_minutes * 60,
        path="/",
    )

    return schemas.AdminLoginResponse(
        success=True,
        message="Login successful",
        username=admin.username,
        access_token=token,
    )


@router.post("/logout", summary="Log out the current admin")
def logout(response: Response):
    response.delete_cookie(key=settings.auth_cookie_name, path="/")
    return {"success": True, "message": "Logged out"}


@router.get("/me", response_model=schemas.AdminMeResponse, summary="Get the currently logged-in admin")
def me(admin: models.Admin = Depends(get_current_admin)):
    return admin
