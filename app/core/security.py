from pwdlib import PasswordHash
import jwt
import secrets
import hashlib
from datetime import datetime,timedelta,timezone

from app.core.config import settings

# Recommeded password hashing configuration
# argon2id is used because the argon2 extra is installed

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using Argon2id.
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against its stored hash.
    """
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(
    subject:str,
    expires_delta:timedelta | None = None
)->str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub":subject,
        "exp":expire,
        "iat":datetime.now(timezone.utc)
    }
    
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    
def generate_refresh_token()->str:
    """Generate a cryptographically secure random refresh token"""
    return secrets.token_urlsafe(64)


def hash_refresh_token(token:str)->str:
    """Generate a SHA-256 hash of the refresh token"""
    return hashlib.sha256(token.encode('utf-8')).hexdigest()