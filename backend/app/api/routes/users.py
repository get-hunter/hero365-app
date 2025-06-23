"""
User Management API Routes

FastAPI routes for user management endpoints.
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, field_serializer

from ..deps import get_current_user, get_business_controller
from app.api.schemas.common_schemas import Message
from app.api.controllers.business_controller import BusinessController
from app.utils import format_datetime_utc
from fastapi import Request

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class BusinessMembershipSummary(BaseModel):
    """Summary of user's business membership."""
    model_config = ConfigDict(json_encoders={datetime: format_datetime_utc})
    
    business_id: str
    business_name: str
    role: str
    is_owner: bool
    is_active: bool
    joined_date: datetime
    
    @field_serializer('joined_date')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to standardized UTC format."""
        return format_datetime_utc(dt)


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: format_datetime_utc})
    
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    supabase_id: str
    created_at: datetime
    updated_at: datetime
    business_memberships: List[BusinessMembershipSummary] = []
    has_businesses: bool
    needs_onboarding: bool
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to standardized UTC format."""
        return format_datetime_utc(dt)


def determine_onboarding_status(business_memberships: List[BusinessMembershipSummary]) -> bool:
    """
    Simplified onboarding completion logic.
    
    User has completed onboarding if they have at least one active business membership.
    This covers both scenarios:
    1. User created a business during onboarding (becomes owner)
    2. User joined an existing business (becomes member)
    
    Args:
        business_memberships: List of user's business memberships
        
    Returns:
        bool: True if user needs onboarding, False if onboarding is complete
    """
    # Check if user has any active business memberships
    has_active_memberships = any(
        membership.is_active for membership in business_memberships
    )
    
    # User needs onboarding if they don't have any active business memberships
    needs_onboarding = not has_active_memberships
    
    logger.info(f"Onboarding status: has_active_memberships={has_active_memberships}, needs_onboarding={needs_onboarding}")
    
    return needs_onboarding


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> UserProfileResponse:
    """
    Get current user profile with simplified onboarding status.
    
    Onboarding completion is determined solely by business membership:
    - User has active business membership = onboarding complete
    - User has no active business membership = needs onboarding
    
    This handles both cases:
    1. User creates business during onboarding (becomes owner)
    2. User joins existing business (becomes member)
    """
    try:
        user_metadata = current_user.get("user_metadata", {})
        user_id = current_user["sub"]
        
        # Get user's business memberships
        business_memberships = []
        
        try:
            user_businesses = await controller.get_user_businesses(user_id, skip=0, limit=100)
            
            for business_summary in user_businesses:
                membership_summary = BusinessMembershipSummary(
                    business_id=str(business_summary.business.id),
                    business_name=business_summary.business.name,
                    role=business_summary.membership.role_display,
                    is_owner=business_summary.is_owner,
                    is_active=business_summary.membership.is_active,
                    joined_date=business_summary.membership.joined_date
                )
                business_memberships.append(membership_summary)
        except Exception as e:
            logger.error(f"Error getting business memberships for user {user_id}: {str(e)}")
            # Continue without business data rather than failing the whole request
        
        # Simplified onboarding status based only on business memberships
        needs_onboarding = determine_onboarding_status(business_memberships)
        has_businesses = len(business_memberships) > 0
        
        # Handle datetime fields - they come as datetime objects from Supabase
        created_at = current_user.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        elif created_at is None:
            created_at = datetime.utcnow()
        
        # Use last_sign_in_at as updated_at since Supabase doesn't have updated_at
        updated_at = current_user.get("last_sign_in_at") or created_at
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        
        return UserProfileResponse(
            id=user_id,
            email=current_user.get("email"),
            phone=current_user.get("phone"),
            full_name=user_metadata.get("full_name"),
            is_active=True,
            is_superuser=False,
            supabase_id=user_id,
            created_at=created_at,
            updated_at=updated_at,
            business_memberships=business_memberships,
            has_businesses=has_businesses,
            needs_onboarding=needs_onboarding
        )
    except Exception as e:
        logger.error(f"Failed to get user profile for {current_user.get('sub', 'unknown')}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )


class BusinessContextRequest(BaseModel):
    """Request model for updating business context."""
    business_id: str


@router.put("/me/business-context", response_model=Message)
async def update_user_business_context(
    request: BusinessContextRequest,
    current_request: Request,
    current_user: dict = Depends(get_current_user)
) -> Message:
    """
    Update the user's current business context.
    
    This endpoint allows switching the user's active business context.
    It redirects to the business context switch endpoint.
    """
    try:
        # Import here to avoid circular imports
        from ...core.auth_facade import auth_facade
        
        user_id = current_user["sub"]
        
        # Switch business context using the auth facade
        new_token = await auth_facade.switch_business_context(user_id, request.business_id)
        
        logger.info(f"User {user_id} switched to business context {request.business_id}")
        
        return Message(message=f"Business context updated to {request.business_id}")
        
    except ValueError as e:
        logger.warning(f"Business context switch validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating business context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update business context"
        ) 