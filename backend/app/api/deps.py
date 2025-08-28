import uuid
from typing import Annotated, Optional
import logging

import jwt
from fastapi import Depends, HTTPException, status, Request
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
TokenDep = Annotated[HTTPAuthorizationCredentials | None, Depends(reusable_oauth2)]


async def get_current_user(
    supabase: SupabaseDep, token: TokenDep
) -> dict:
    """
    Get current user from business context JWT token.
    
    Uses business context JWT tokens with business membership and role information for authentication.
    
    Returns:
        dict: User data containing id, email, business context, etc.
    """
    try:
        # Handle case where no token is provided
        if not token:
            logger.warning("No token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"get_current_user called with token: {token.credentials[:50]}...")
        
        # Validate business context JWT token
        logger.info("Validating business context JWT token")
        business_payload = await auth_facade.verify_business_context_token(token.credentials)
        
        if not business_payload:
            logger.warning("Business context JWT token validation failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("Business context JWT token validated successfully")
        
        # Get user ID from payload
        user_id = business_payload.get("sub") or business_payload.get("user_id")
        
        # Fetch user details from Supabase to get email and metadata
        try:
            logger.info(f"Making request to Supabase Auth get_user_by_id for user: {user_id}")
            user_response = supabase.auth.admin.get_user_by_id(user_id)
            if not user_response.user:
                logger.warning(f"User {user_id} not found in auth.users - rejecting token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account no longer exists",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user_email = user_response.user.email
            user_phone = user_response.user.phone
            user_metadata = user_response.user.user_metadata if user_response.user else {}
            logger.info(f"Fetched user details: email={user_email}")
            
        except HTTPException:
            # Re-raise HTTP exceptions (like user not found)
            raise
        except Exception as e:
            logger.error(f"Failed to fetch user details for {user_id}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {str(e)}")
            
            # Check if it's a Supabase auth error specifically
            if "AuthApiError" in str(type(e)) or "invalid JWT" in str(e).lower():
                logger.error(f"Supabase AuthApiError detected: {str(e)}")
                # This indicates the Supabase service key or setup is the issue
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication service error - invalid token signature",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # For other errors, also reject but with different message
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to verify user account",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user data from business context JWT payload with fetched user details
        user_data = {
            "sub": user_id,
            "id": user_id,
            "email": user_email,
            "phone": user_phone,
            "user_metadata": user_metadata,
            "current_business_id": business_payload.get("current_business_id"),
            "business_memberships": business_payload.get("business_memberships", []),
            "is_active": True,
            "token_type": "business_context_jwt"
        }
        
        logger.info(f"Successfully authenticated user via business context JWT: {user_data['sub']}, email: {user_data['email']}")
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


async def get_business_context(request: Request) -> dict:
    """
    Get business context from request.
    
    This function extracts business context that was set by the BusinessContextMiddleware
    or from the authenticated user's current business context.
    
    Args:
        request: FastAPI request object
        
    Returns:
        dict: Business context with business_id and other relevant info
        
    Raises:
        HTTPException: If business context is not available
    """
    try:
        # Get business_id from request state (set by BusinessContextMiddleware)
        business_id = getattr(request.state, "business_id", None)
        if business_id:
            return {"business_id": business_id}
        
        # Fallback: try to extract business_id from path parameters
        if hasattr(request, "path_params") and "business_id" in request.path_params:
            business_id = request.path_params["business_id"]
            # Validate UUID format
            uuid.UUID(business_id)
            return {"business_id": business_id}
        
        # Fallback: try to get from authenticated user's current business context
        user = getattr(request.state, "user", {})
        current_business_id = user.get("current_business_id")
        if current_business_id:
            # Validate UUID format
            uuid.UUID(current_business_id)
            return {"business_id": current_business_id}
        
        # Final fallback: if user has business memberships, use the first one
        business_memberships = user.get("business_memberships", [])
        if business_memberships:
            first_business_id = business_memberships[0].get("business_id")
            if first_business_id:
                # Validate UUID format
                uuid.UUID(first_business_id)
                logger.info(f"Using first business membership as context: {first_business_id}")
                return {"business_id": first_business_id}
        
        # Last resort: try to get business memberships from the auth facade if not in token
        if not business_memberships:
            try:
                from ..core.auth_facade import auth_facade
                user_id = user.get("id") or user.get("sub")
                if user_id:
                    logger.info(f"Fetching business memberships for user {user_id}")
                    fresh_memberships = await auth_facade._get_user_business_memberships(user_id)
                    if fresh_memberships:
                        first_business_id = fresh_memberships[0].get("business_id")
                        if first_business_id:
                            # Validate UUID format
                            uuid.UUID(first_business_id)
                            logger.info(f"Using fetched business membership as context: {first_business_id}")
                            return {"business_id": first_business_id}
            except Exception as e:
                logger.error(f"Failed to fetch business memberships: {str(e)}")
                pass
        
        # If no business context available, raise error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business context required for this operation"
        )
        
    except ValueError as e:
        logger.error(f"Invalid business ID format: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid business ID format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting business context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid business context: {str(e)}"
        )


BusinessContext = Annotated[dict, Depends(get_business_context)]
