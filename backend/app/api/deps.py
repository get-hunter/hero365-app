from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.core.db import engine
from app.core.supabase import supabase_service
from app.core.security import ALGORITHM

reusable_oauth2 = HTTPBearer(
    scheme_name="Authorization"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(reusable_oauth2)]


def get_current_user(token: TokenDep) -> dict:
    """
    Get current user directly from Supabase.
    """
    try:
        # Extract token from Authorization header
        token_str = token.credentials
        
        # Verify with Supabase
        supabase_user_data = supabase_service.verify_token(token_str)
        
        if supabase_user_data:
            return supabase_user_data
        
        # If Supabase verification fails, try legacy JWT verification
        try:
            payload = jwt.decode(
                token_str, settings.SECRET_KEY, algorithms=[ALGORITHM]
            )
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )
            
            # Return legacy user format
            return {
                "id": email,  # Use email as ID for legacy tokens
                "email": email,
                "phone": None,
                "user_metadata": {},
                "app_metadata": {},
            }
        except (InvalidTokenError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )


CurrentUser = Annotated[dict, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> dict:
    """
    Get current active superuser from Supabase user metadata
    """
    app_metadata = current_user.get("app_metadata", {})
    if not app_metadata.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not enough permissions"
        )
    return current_user
