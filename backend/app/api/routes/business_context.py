"""
Business Context API Routes

API endpoints for managing user's business context and switching between businesses.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
import uuid

from ..middleware.auth_handler import require_authenticated_user
from ...core.auth_facade import auth_facade
from ...infrastructure.config.dependency_injection import get_container

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/business-context", tags=["Business Context"])


class BusinessContextResponse(BaseModel):
    """Schema for business context response."""
    
    current_business_id: str = Field(..., description="Current business ID")
    available_businesses: List[dict] = Field(..., description="List of businesses user can access")
    user_id: str = Field(..., description="User ID")
    new_token: str = Field(..., description="New JWT token with updated business context")


class SwitchBusinessContextRequest(BaseModel):
    """Schema for switching business context."""
    
    business_id: str = Field(..., description="Business ID to switch to")
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class BusinessContextInfoResponse(BaseModel):
    """Schema for current business context information."""
    
    current_business_id: Optional[str] = Field(None, description="Current business ID")
    available_businesses: List[dict] = Field(..., description="List of businesses user can access")
    user_id: str = Field(..., description="User ID")


@router.get("/current", response_model=BusinessContextInfoResponse)
async def get_current_business_context(request: Request) -> BusinessContextInfoResponse:
    """
    Get current business context information.
    
    Returns the user's current business context and list of available businesses.
    """
    current_user = require_authenticated_user(request)
    user_id = current_user.get('id') or current_user.get('sub')
    
    logger.info(f"📱 BusinessContext API: Getting current context for user {user_id}")
    
    try:
        # Get user's business memberships
        business_memberships = await auth_facade._get_user_business_memberships(user_id)
        logger.info(f"📊 BusinessContext API: Found {len(business_memberships)} business memberships for user")
        
        # Get current business context
        current_business_id = current_user.get('current_business_id')
        logger.info(f"🏢 BusinessContext API: Current business ID: {current_business_id}")
        
        # Format available businesses
        available_businesses = []
        for i, membership in enumerate(business_memberships):
            logger.info(f"👤 BusinessContext API: Processing membership {i+1}: business_id={membership['business_id']}, role={membership['role']}, permissions_count={len(membership.get('permissions', []))}")
            
            # Get business details
            business_repo = get_container().get_business_repository()
            business = await business_repo.get_by_id(uuid.UUID(membership["business_id"]))
            
            if business:
                business_info = {
                    "business_id": membership["business_id"],
                    "business_name": business.name,
                    "role": membership["role"],
                    "permissions": membership["permissions"],
                    "role_level": membership["role_level"]
                }
                available_businesses.append(business_info)
                
                # Log detailed permissions for current business
                if membership["business_id"] == current_business_id:
                    logger.info(f"🔑 BusinessContext API: CURRENT BUSINESS PERMISSIONS:")
                    logger.info(f"    Role: {membership['role']}")
                    logger.info(f"    Role Level: {membership['role_level']}")
                    logger.info(f"    Permissions: {membership['permissions']}")
                    logger.info(f"    Has view_contacts: {'view_contacts' in membership.get('permissions', [])}")
                    logger.info(f"    Has edit_contacts: {'edit_contacts' in membership.get('permissions', [])}")
        
        response_data = BusinessContextInfoResponse(
            current_business_id=current_business_id,
            available_businesses=available_businesses,
            user_id=user_id
        )
        
        logger.info(f"📤 BusinessContext API: Sending response to app:")
        logger.info(f"    Current business: {current_business_id}")
        logger.info(f"    Available businesses count: {len(available_businesses)}")
        logger.info(f"    Response: {response_data.model_dump()}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error getting business context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get business context"
        )


@router.post("/switch", response_model=BusinessContextResponse)
async def switch_business_context(
    request: SwitchBusinessContextRequest,
    current_request: Request
) -> BusinessContextResponse:
    """
    Switch user's current business context.
    
    Changes the user's active business context and returns a new JWT token
    with the updated business context.
    """
    current_user = require_authenticated_user(current_request)
    user_id = current_user.get('id') or current_user.get('sub')
    
    try:
        # Validate business ID format
        try:
            target_business_uuid = uuid.UUID(request.business_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid business ID format"
            )
        
        # Switch business context and get new token
        new_token = await auth_facade.switch_business_context(user_id, request.business_id)
        
        # Get updated business memberships
        business_memberships = await auth_facade._get_user_business_memberships(user_id)
        
        # Format available businesses
        available_businesses = []
        for membership in business_memberships:
            # Get business details
            business_repo = get_container().get_business_repository()
            business = await business_repo.get_by_id(uuid.UUID(membership["business_id"]))
            
            if business:
                available_businesses.append({
                    "business_id": membership["business_id"],
                    "business_name": business.name,
                    "role": membership["role"],
                    "permissions": membership["permissions"],
                    "role_level": membership["role_level"]
                })
        
        logger.info(f"User {user_id} switched to business context {request.business_id}")
        
        return BusinessContextResponse(
            current_business_id=request.business_id,
            available_businesses=available_businesses,
            user_id=user_id,
            new_token=new_token
        )
        
    except ValueError as e:
        logger.warning(f"Business context switch validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error switching business context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch business context"
        )


@router.get("/available-businesses")
async def get_available_businesses(request: Request) -> List[dict]:
    """
    Get list of businesses the current user can access.
    
    Returns a list of businesses the authenticated user is a member of.
    """
    current_user = require_authenticated_user(request)
    user_id = current_user.get('id') or current_user.get('sub')
    
    try:
        # Get user's business memberships
        business_memberships = await auth_facade._get_user_business_memberships(user_id)
        
        # Format available businesses with detailed information
        available_businesses = []
        for membership in business_memberships:
            # Get business details
            business_repo = get_container().get_business_repository()
            business = await business_repo.get_by_id(uuid.UUID(membership["business_id"]))
            
            if business:
                # Get team member count
                membership_repo = get_container().get_business_membership_repository()
                team_count = await membership_repo.count_active_business_members(business.id)
                
                available_businesses.append({
                    "business_id": membership["business_id"],
                    "business_name": business.name,
                    "industry": business.industry,
                    "company_size": business.company_size.value,
                    "role": membership["role"],
                    "permissions": membership["permissions"],
                    "role_level": membership["role_level"],
                    "team_member_count": team_count,
                    "is_active": business.is_active,
                    "created_date": business.created_date.isoformat() if business.created_date else None
                })
        
        return available_businesses
        
    except Exception as e:
        logger.error(f"Error getting available businesses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available businesses"
        )


@router.post("/refresh-token")
async def refresh_business_context_token(request: Request) -> dict:
    """
    Refresh the current JWT token with updated business context.
    
    Useful when business memberships or permissions have changed.
    """
    current_user = require_authenticated_user(request)
    user_id = current_user.get('id') or current_user.get('sub')
    current_business_id = current_user.get('current_business_id')
    
    try:
        # Create new token with current business context
        new_token = await auth_facade.create_enhanced_jwt_token(user_id, current_business_id)
        
        logger.info(f"Refreshed business context token for user {user_id}")
        
        return {
            "access_token": new_token,
            "token_type": "bearer",
            "current_business_id": current_business_id,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error refreshing business context token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh business context token"
        ) 