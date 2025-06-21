from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.auth_facade import auth_facade

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """Legacy token creation - kept for backward compatibility."""
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Legacy password verification - kept for backward compatibility."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Legacy password hashing - kept for backward compatibility."""
    return pwd_context.hash(password)


async def verify_supabase_token(token: str) -> Optional[dict]:
    """Verify Supabase JWT token and return user data."""
    try:
        user_data = await auth_facade.verify_token(token)
        return user_data
    except Exception as e:
        return None


async def decode_token(token: str) -> Optional[dict]:
    """Decode JWT token - supports both legacy and Supabase tokens."""
    try:
        # First try to verify as Supabase token
        supabase_user = await verify_supabase_token(token)
        if supabase_user:
            return supabase_user
        
        # Fall back to legacy token verification
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
