from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.models.admin_session import AdminSession

from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from app.models.admin import Admin
from app.models.admin_session import AdminSession
from app.schemas.auth import LoginRequest


def login_admin(db: Session, login_data: LoginRequest):
    statement = select(Admin).where(Admin.email == str(login_data.email).lower())

    admin = db.scalar(statement)

    if (
        not admin
        or not verify_password(
            login_data.password, admin.hashed_password if admin else ""
        )
        or not admin.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(admin.id))
    refresh_token = generate_refresh_token()
    token_hash = hash_refresh_token(refresh_token)

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    admin_session = AdminSession(
        admin_id=admin.id, token_hash=token_hash, expires_at=expires_at
    )
    try:
        db.add(admin_session)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


def refresh_admin_session(db: Session, refresh_token: str):
    token_hash = hash_refresh_token(refresh_token)

    statement = select(AdminSession).where(AdminSession.token_hash == token_hash)
    admin_session = db.scalar(statement)
    now = datetime.now(timezone.utc)

    # Reject invalid ,revoked , or expired sessions
    if (
        not admin_session
        or admin_session.revoked_at is not None
        or admin_session.expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

        # Retrieve the admin
    admin = db.get(Admin, admin_session.admin_id)
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Generate new tokens
    new_access_token = create_access_token(subject=str(admin.id))
    new_refresh_token = generate_refresh_token()
    new_token_hash = hash_refresh_token(new_access_token)

    new_expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    try:
        # Revokenthe old sesssion
        admin_session.revoked_at = now

        # Create new session
        new_session = AdminSession(
            admin_id=admin.id, token_hash=new_token_hash, expires_at=new_expires_at
        )
        db.add(new_session)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    }
