from collections.abc import Generator
from typing import Annotated
import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.core.supabase import supabase_service
from app.models import TokenPayload, User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    # Try to decode as Supabase token first
    supabase_user_data = security.verify_supabase_token(token)
    
    if supabase_user_data:
        # Handle Supabase authentication
        user_id = supabase_user_data.get("id")
        email = supabase_user_data.get("email")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token data",
            )
        
        # Try to find existing user by Supabase ID first, then by email
        user = session.exec(select(User).where(User.id == uuid.UUID(user_id))).first()
        
        if not user:
            # Try to find by email for migration cases
            user = session.exec(select(User).where(User.email == email)).first()
            
            if user:
                # Update the user ID to match Supabase ID
                user.id = uuid.UUID(user_id)
                session.add(user)
                session.commit()
                session.refresh(user)
            else:
                # Create new user from Supabase data
                user_metadata = supabase_user_data.get("user_metadata", {})
                app_metadata = supabase_user_data.get("app_metadata", {})
                
                user = User(
                    id=uuid.UUID(user_id),
                    email=email,
                    full_name=user_metadata.get("full_name"),
                    is_active=True,
                    is_superuser=app_metadata.get("is_superuser", False),
                    hashed_password=""  # Not used with Supabase auth
                )
                session.add(user)
                session.commit()
                session.refresh(user)
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        
        return user
    
    else:
        # Fall back to legacy token validation
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except (InvalidTokenError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        
        user = session.get(User, token_data.sub)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
