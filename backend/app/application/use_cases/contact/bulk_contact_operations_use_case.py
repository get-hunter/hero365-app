"""
Bulk Contact Operations Use Case

Handles the business logic for bulk operations on multiple contacts.
"""

import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)

from ...dto.contact_dto import ContactBulkUpdateDTO
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from ...exceptions.application_exceptions import PermissionDeniedError


class BulkContactOperationsUseCase:
    """
    Use case for performing bulk operations on multiple contacts.
    """
    
    def __init__(self, contact_repository: ContactRepository,
                 membership_repository: BusinessMembershipRepository):
        self.contact_repository = contact_repository
        self.membership_repository = membership_repository
    
    async def bulk_update(self, dto: ContactBulkUpdateDTO, user_id: str) -> int:
        """
        Perform bulk updates on multiple contacts.
        
        Args:
            dto: Bulk update parameters
            user_id: ID of the user performing updates
            
        Returns:
            Number of contacts updated
            
        Raises:
            PermissionError: If user lacks permission
        """
        # Validate user has permission to edit contacts in this business
        await self._validate_user_permission(dto.business_id, user_id, "edit_contacts")
        
        updated_count = 0
        
        # Update status if provided
        if dto.status is not None:
            updated_count += await self.contact_repository.bulk_update_status(
                dto.business_id, dto.contact_ids, dto.status
            )
        
        # Assign contacts if provided
        if dto.assigned_to is not None:
            updated_count += await self.contact_repository.bulk_assign_contacts(
                dto.business_id, dto.contact_ids, dto.assigned_to
            )
        
        # Add tags if provided
        if dto.tags_to_add:
            for tag in dto.tags_to_add:
                await self.contact_repository.bulk_add_tag(
                    dto.business_id, dto.contact_ids, tag
                )
        
        return updated_count
    
    async def _validate_user_permission(self, business_id: uuid.UUID, user_id: str, permission: str) -> None:
        """Validate that user has required permission for the business."""
        membership = await self.membership_repository.get_by_business_and_user(business_id, user_id)
        
        if not membership:
            raise PermissionDeniedError("User is not a member of this business")
        
        if not membership.is_active:
            raise PermissionDeniedError("User membership is inactive")
        
        if not membership.has_permission(permission):
            raise PermissionDeniedError(f"User does not have permission: {permission}") 