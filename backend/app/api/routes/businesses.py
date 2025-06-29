"""
Business Management API Routes

FastAPI routes for business management endpoints.
"""

import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, Query

from ..controllers.business_controller import BusinessController
from ..schemas.business_schemas import (
    BusinessCreateRequest, BusinessResponse, UserBusinessSummaryResponse,
    BusinessInvitationCreateRequest, BusinessInvitationResponse,
    BusinessInvitationAcceptRequest, BusinessMembershipResponse,
    BusinessDetailResponse, BusinessUpdateRequest, BusinessMembershipUpdateRequest
)
from ..schemas.common_schemas import Message
from ..deps import get_current_user, get_business_controller

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.get("/debug", status_code=200)
async def debug_endpoint():
    """Debug endpoint to test if business routes are working."""
    logger.info("🔧 Debug endpoint called")
    return {"message": "Business routes are working", "status": "ok"}


@router.post("", response_model=BusinessResponse, status_code=201)
async def create_business(
    request: BusinessCreateRequest,
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> BusinessResponse:
    """
    Create a new business.
    
    Creates a new business with the current user as the owner.
    Automatically creates an owner membership for the user.
    """
    logger.info(f"create_business endpoint called")
    logger.info(f"Current user: {current_user}")
    logger.info(f"Business request: name={request.name}, industry={request.industry}")
    logger.info(f"Controller instance: {controller}")
    
    try:
        result = await controller.create_business(request, current_user["sub"])
        logger.info(f"Business creation successful: {result.id}")
        
        # Log the complete response before returning
        logger.info(f"HTTP Response (201 Created): {result.model_dump_json(indent=2)}")
        logger.info(f"Business {result.id} created successfully for user {current_user.get('email', current_user['sub'])}")
        
        return result
    except Exception as e:
        logger.error(f"Exception in create_business endpoint: {type(e).__name__}: {str(e)}")
        raise


@router.get("/me", response_model=List[UserBusinessSummaryResponse])
async def get_my_businesses(
    skip: int = Query(0, ge=0, description="Number of businesses to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of businesses to return"),
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> List[UserBusinessSummaryResponse]:
    """
    Get all businesses for the current user.
    
    Returns businesses where the user is a member (owner, admin, employee, etc.)
    with their membership information and business summaries.
    """
    return await controller.get_user_businesses(current_user["sub"], skip, limit)


@router.post("/{business_id}/invite", response_model=BusinessInvitationResponse, status_code=201)
async def invite_team_member(
    business_id: uuid.UUID,
    request: BusinessInvitationCreateRequest,
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> BusinessInvitationResponse:
    """
    Invite a team member to join a business.
    
    Sends an invitation to the specified email or phone number.
    Requires the user to have team:invite permission for the business.
    """
    # Get user name from current user (assuming it's in the token)
    user_name = current_user.get("name", current_user.get("email", "Unknown User"))
    
    return await controller.invite_team_member(
        business_id, 
        request, 
        current_user["sub"],
        user_name
    )


@router.post("/invitations/accept", response_model=BusinessMembershipResponse)
async def accept_invitation(
    request: BusinessInvitationAcceptRequest,
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> BusinessMembershipResponse:
    """
    Accept a business invitation.
    
    Accepts a pending invitation and creates a business membership for the user.
    The invitation must be valid and not expired.
    """
    return await controller.accept_invitation(request, current_user["sub"])


# Additional business management endpoints


@router.get("/{business_id}", response_model=BusinessDetailResponse)
async def get_business_detail(
    business_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> BusinessDetailResponse:
    """
    Get detailed business information.
    
    Returns comprehensive business information including team members,
    statistics, and user's role within the business.
    """
    return await controller.get_business_detail(business_id, current_user["sub"])


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: uuid.UUID,
    request: BusinessUpdateRequest,
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> BusinessResponse:
    """
    Update business information.
    
    Allows business owners and admins with proper permissions
    to update business details.
    """
    return await controller.update_business(business_id, request, current_user["sub"])


@router.get("/{business_id}/members", response_model=List[BusinessMembershipResponse])
async def get_business_members(
    business_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of members to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of members to return"),
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> List[BusinessMembershipResponse]:
    """
    Get business team members.
    
    Returns a list of all active team members for the business.
    """
    # This uses the same detail endpoint which includes team members
    detail = await controller.get_business_detail(business_id, current_user["sub"])
    return detail.team_members[skip:skip + limit]


@router.put("/{business_id}/members/{membership_id}", response_model=BusinessMembershipResponse)
async def update_member_role(
    business_id: uuid.UUID,
    membership_id: uuid.UUID,
    request: BusinessMembershipUpdateRequest,
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> BusinessMembershipResponse:
    """
    Update team member role and permissions.
    
    Allows business owners and admins to update team member
    roles, permissions, and other membership details.
    """
    return await controller.update_member_role(
        business_id, membership_id, request, current_user["sub"]
    )


@router.delete("/{business_id}/members/{membership_id}", response_model=Message)
async def remove_team_member(
    business_id: uuid.UUID,
    membership_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> Message:
    """
    Remove a team member from the business.
    
    Deactivates the team member's access to the business.
    Business owners cannot remove themselves.
    """
    success = await controller.remove_team_member(
        business_id, membership_id, current_user["sub"]
    )
    
    if success:
        return Message(message="Team member removed successfully")
    else:
        return Message(message="Failed to remove team member")


@router.get("/{business_id}/invitations", response_model=List[BusinessInvitationResponse])
async def get_business_invitations(
    business_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of invitations to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of invitations to return"),
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> List[BusinessInvitationResponse]:
    """
    Get business invitations.
    
    Returns all invitations sent for the business.
    Requires appropriate permissions to view invitations.
    """
    return await controller.get_business_invitations(
        business_id, current_user["sub"], skip, limit
    )


@router.delete("/invitations/{invitation_id}", response_model=Message)
async def cancel_invitation(
    invitation_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> Message:
    """
    Cancel a pending invitation.
    
    Allows business owners, admins, or the invitation sender
    to cancel a pending invitation.
    """
    success = await controller.cancel_invitation(invitation_id, current_user["sub"])
    
    if success:
        return Message(message="Invitation cancelled successfully")
    else:
        return Message(message="Failed to cancel invitation")


@router.post("/invitations/{invitation_id}/decline", response_model=Message)
async def decline_invitation(
    invitation_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    controller: BusinessController = Depends(get_business_controller)
) -> Message:
    """
    Decline a business invitation.
    
    Allows the invitation recipient to decline a pending invitation.
    """
    success = await controller.decline_invitation(invitation_id, current_user["sub"])
    
    if success:
        return Message(message="Invitation declined successfully")
    else:
        return Message(message="Failed to decline invitation") 