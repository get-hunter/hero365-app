"""
Contact Statistics Use Case

Handles the business logic for retrieving comprehensive contact statistics.
"""

import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)

from ...dto.contact_dto import ContactStatisticsDTO
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from ...exceptions.application_exceptions import PermissionDeniedError


class ContactStatisticsUseCase:
    """
    Use case for retrieving contact statistics with permission validation.
    """
    
    def __init__(self, contact_repository: ContactRepository,
                 membership_repository: BusinessMembershipRepository):
        self.contact_repository = contact_repository
        self.membership_repository = membership_repository
    
    async def execute(self, business_id: uuid.UUID, user_id: str) -> ContactStatisticsDTO:
        """
        Get comprehensive contact statistics for a business.
        
        Args:
            business_id: ID of the business
            user_id: ID of the user requesting statistics
            
        Returns:
            ContactStatisticsDTO with comprehensive statistics
            
        Raises:
            PermissionError: If user lacks permission
        """
        # Validate user has permission to view contacts in this business
        await self._validate_user_permission(business_id, user_id, "view_contacts")
        
        stats = await self.contact_repository.get_contact_statistics(business_id)
        
        return ContactStatisticsDTO(
            total_contacts=stats.get("total_contacts", 0),
            active_contacts=stats.get("active_contacts", 0),
            inactive_contacts=stats.get("inactive_contacts", 0),
            archived_contacts=stats.get("archived_contacts", 0),
            blocked_contacts=stats.get("blocked_contacts", 0),
            customers=stats.get("customers", 0),
            leads=stats.get("leads", 0),
            prospects=stats.get("prospects", 0),
            vendors=stats.get("vendors", 0),
            partners=stats.get("partners", 0),
            contractors=stats.get("contractors", 0),
            high_priority=stats.get("high_priority", 0),
            medium_priority=stats.get("medium_priority", 0),
            low_priority=stats.get("low_priority", 0),
            urgent_priority=stats.get("urgent_priority", 0),
            with_email=stats.get("with_email", 0),
            with_phone=stats.get("with_phone", 0),
            assigned_contacts=stats.get("assigned_contacts", 0),
            unassigned_contacts=stats.get("unassigned_contacts", 0),
            never_contacted=stats.get("never_contacted", 0),
            recently_contacted=stats.get("recently_contacted", 0),
            high_value_contacts=stats.get("high_value_contacts", 0),
            total_estimated_value=stats.get("total_estimated_value", 0.0),
            average_estimated_value=stats.get("average_estimated_value", 0.0)
        )
    
    async def _validate_user_permission(self, business_id: uuid.UUID, user_id: str, permission: str) -> None:
        """Validate that user has required permission for the business."""
        membership = await self.membership_repository.get_by_business_and_user(business_id, user_id)
        
        if not membership:
            raise PermissionDeniedError("User is not a member of this business")
        
        if not membership.is_active:
            raise PermissionDeniedError("User membership is inactive")
        
        if not membership.has_permission(permission):
            raise PermissionDeniedError(f"User does not have permission: {permission}") 