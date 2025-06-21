import uuid
from typing import Annotated
import logging

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from supabase import Client

from app.core.config import settings
from app.core.auth_facade import auth_facade
from app.infrastructure.config.dependency_injection import get_container

# Configure logging
logger = logging.getLogger(__name__)

reusable_oauth2 = HTTPBearer(
    scheme_name="Authorization"
)


def get_supabase_client() -> Client:
    """Get Supabase client from dependency container."""
    return get_container()._get_supabase_client()


SupabaseDep = Annotated[Client, Depends(get_supabase_client)]
TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(reusable_oauth2)]


async def get_current_user(
    supabase: SupabaseDep, token: TokenDep
) -> dict:
    """
    Get current user from Supabase Auth token.
    
    Returns Supabase user data directly without creating local user records.
    This simplifies the authentication flow and removes the need for user sync.
    
    Returns:
        dict: Supabase user data containing id, email, user_metadata, etc.
    """
    try:
        logger.info(f"get_current_user called with token: {token.credentials[:50]}...")
        
        # Get user from Supabase Auth using the token
        logger.info("Making request to Supabase Auth get_user")
        user_response = supabase.auth.get_user(token.credentials)
        logger.info(f"Supabase Auth response: user={user_response.user is not None}")
        
        if not user_response.user:
            logger.warning("Supabase Auth returned no user")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_data = {
            "sub": user_response.user.id,  # Keep 'sub' for JWT compatibility
            "id": user_response.user.id,
            "email": user_response.user.email,
            "phone": user_response.user.phone,
            "user_metadata": user_response.user.user_metadata or {},
            "created_at": user_response.user.created_at,
            "last_sign_in_at": user_response.user.last_sign_in_at,
            "is_active": True  # Supabase users are active by default
        }
        
        logger.info(f"Successfully authenticated user: {user_data['sub']}, email: {user_data['email']}")
        
        # Return Supabase user data directly
        return user_data
        
    except HTTPException:
        logger.warning("HTTPException in get_current_user - re-raising")
        raise
    except Exception as e:
        logger.error(f"Exception in get_current_user: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUser = Annotated[dict, Depends(get_current_user)]


def get_business_controller():
    """Get business controller with dependencies."""
    logger.info("get_business_controller called")
    try:
        from app.api.controllers.business_controller import BusinessController
        container = get_container()
        logger.info("Container retrieved successfully")
        
        controller = BusinessController(
            create_business_use_case=container.get_create_business_use_case(),
            invite_team_member_use_case=container.get_invite_team_member_use_case(),
            accept_invitation_use_case=container.get_accept_invitation_use_case(),
            get_user_businesses_use_case=container.get_get_user_businesses_use_case(),
            get_business_detail_use_case=container.get_get_business_detail_use_case(),
            update_business_use_case=container.get_update_business_use_case(),
            manage_team_member_use_case=container.get_manage_team_member_use_case(),
            manage_invitations_use_case=container.get_manage_invitations_use_case()
        )
        logger.info("BusinessController created successfully")
        return controller
    except Exception as e:
        logger.error(f"Exception in get_business_controller: {type(e).__name__}: {str(e)}")
        raise


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
