"""
Delete Contact Use Case

Handles the business logic for deleting contacts.
"""

import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)

from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from ...exceptions.application_exceptions import PermissionDeniedError


class DeleteContactUseCase:
    """
    Use case for deleting contacts with permission checks.
    """
    
    def __init__(self, contact_repository: ContactRepository,
                 membership_repository: BusinessMembershipRepository):
        self.contact_repository = contact_repository
        self.membership_repository = membership_repository
    
    async def execute(self, contact_id: uuid.UUID, user_id: str) -> bool:
        """
        Delete a contact.
        
        Args:
            contact_id: ID of the contact to delete
            user_id: ID of the user deleting the contact
            
        Returns:
            True if contact was deleted
            
        Raises:
            EntityNotFoundError: If contact doesn't exist
            PermissionError: If user lacks permission
        """
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise EntityNotFoundError("Contact not found")
        
        # Validate user has permission to delete contacts in this business
        await self._validate_user_permission(contact.business_id, user_id, "delete_contacts")
        
        return await self.contact_repository.delete(contact_id)
    
    async def _validate_user_permission(self, business_id: uuid.UUID, user_id: str, permission: str) -> None:
        """Validate that user has required permission for the business."""
        membership = await self.membership_repository.get_by_business_and_user(business_id, user_id)
        
        if not membership:
            raise PermissionDeniedError("User is not a member of this business")
        
        if not membership.is_active:
            raise PermissionDeniedError("User membership is inactive")
        
        if not membership.has_permission(permission):
            raise PermissionDeniedError(f"User does not have permission: {permission}") 