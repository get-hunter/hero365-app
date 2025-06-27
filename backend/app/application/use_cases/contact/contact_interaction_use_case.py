"""
Contact Interaction Use Case

Handles the business logic for managing contact interactions.
"""

import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

from ...dto.contact_dto import ContactResponseDTO, ContactAddressDTO
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.contact import Contact, InteractionType
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from ...exceptions.application_exceptions import PermissionDeniedError


class ContactInteractionUseCase:
    """
    Use case for managing contact interactions with permission validation.
    """
    
    def __init__(self, contact_repository: ContactRepository,
                 membership_repository: BusinessMembershipRepository):
        self.contact_repository = contact_repository
        self.membership_repository = membership_repository
    
    async def add_interaction(self, contact_id: uuid.UUID, interaction_data: dict, user_id: str):
        """
        Add an interaction record to a contact.
        
        Args:
            contact_id: ID of the contact
            interaction_data: Interaction data containing type, description, etc.
            user_id: ID of the user adding the interaction
            
        Returns:
            Interaction record ID
            
        Raises:
            EntityNotFoundError: If contact doesn't exist
            PermissionError: If user lacks permission
        """
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise EntityNotFoundError("Contact not found")
        
        # Validate user has permission to edit contacts in this business
        await self._validate_user_permission(contact.business_id, user_id, "edit_contacts")
        
        # Add interaction to contact
        interaction_id = contact.add_interaction(
            interaction_type=InteractionType(interaction_data["type"]),
            description=interaction_data["description"],
            outcome=interaction_data.get("outcome"),
            next_action=interaction_data.get("next_action"),
            scheduled_follow_up=interaction_data.get("scheduled_follow_up"),
            performed_by=user_id
        )
        
        # Update last contacted timestamp
        contact.update_last_contacted()
        
        # Save updated contact
        await self.contact_repository.update(contact)
        
        return interaction_id
    
    async def get_interactions(self, contact_id: uuid.UUID, user_id: str, skip: int = 0, limit: int = 50):
        """
        Get interaction history for a contact.
        
        Args:
            contact_id: ID of the contact
            user_id: ID of the user requesting interactions
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of interaction records
            
        Raises:
            EntityNotFoundError: If contact doesn't exist
            PermissionError: If user lacks permission
        """
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise EntityNotFoundError("Contact not found")
        
        # Validate user has permission to view contacts in this business
        await self._validate_user_permission(contact.business_id, user_id, "view_contacts")
        
        # Get interactions from contact (sorted by timestamp, newest first)
        interactions = sorted(
            contact.interaction_history or [],
            key=lambda x: x.timestamp,
            reverse=True
        )
        
        # Apply pagination
        paginated_interactions = interactions[skip:skip + limit]
        
        return {
            "interactions": paginated_interactions,
            "total": len(interactions),
            "skip": skip,
            "limit": limit
        }
    
    async def mark_contacted(self, contact_id: uuid.UUID, user_id: str) -> ContactResponseDTO:
        """
        Mark a contact as contacted (updates last_contacted timestamp).
        
        Args:
            contact_id: ID of the contact
            user_id: ID of the user marking contact
            
        Returns:
            ContactResponseDTO with updated contact
            
        Raises:
            EntityNotFoundError: If contact doesn't exist
            PermissionError: If user lacks permission
        """
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise EntityNotFoundError("Contact not found")
        
        # Validate user has permission to edit contacts in this business
        await self._validate_user_permission(contact.business_id, user_id, "edit_contacts")
        
        contact.update_last_contacted()
        updated_contact = await self.contact_repository.update(contact)
        
        return self._contact_to_response_dto(updated_contact)
    
    async def _validate_user_permission(self, business_id: uuid.UUID, user_id: str, permission: str) -> None:
        """Validate that user has required permission for the business."""
        membership = await self.membership_repository.get_by_business_and_user(business_id, user_id)
        
        if not membership:
            raise PermissionDeniedError("User is not a member of this business")
        
        if not membership.is_active:
            raise PermissionDeniedError("User membership is inactive")
        
        if not membership.has_permission(permission):
            raise PermissionDeniedError(f"User does not have permission: {permission}")
    
    def _contact_to_response_dto(self, contact: Contact) -> ContactResponseDTO:
        """Convert Contact entity to response DTO."""
        address_dto = None
        if contact.address:
            address_dto = ContactAddressDTO(
                street_address=contact.address.street_address,
                city=contact.address.city,
                state=contact.address.state,
                postal_code=contact.address.postal_code,
                country=contact.address.country
            )
        
        return ContactResponseDTO(
            id=contact.id,
            business_id=contact.business_id,
            contact_type=contact.contact_type,
            status=contact.status,
            relationship_status=contact.relationship_status,
            lifecycle_stage=contact.lifecycle_stage,
            first_name=contact.first_name,
            last_name=contact.last_name,
            company_name=contact.company_name,
            job_title=contact.job_title,
            email=contact.email,
            phone=contact.phone,
            mobile_phone=contact.mobile_phone,
            website=contact.website,
            address=address_dto,
            priority=contact.priority,
            source=contact.source,
            tags=contact.tags.copy(),
            notes=contact.notes,
            estimated_value=contact.estimated_value,
            currency=contact.currency,
            assigned_to=contact.assigned_to,
            created_by=contact.created_by,
            custom_fields=contact.custom_fields.copy(),
            created_date=contact.created_date,
            last_modified=contact.last_modified,
            last_contacted=contact.last_contacted,
            display_name=contact.get_display_name(),
            primary_contact_method=contact.get_primary_contact_method(),
            type_display=contact.get_type_display(),
            status_display=contact.get_status_display(),
            priority_display=contact.get_priority_display(),
            source_display=contact.get_source_display(),
            relationship_status_display=contact.get_relationship_status_display(),
            lifecycle_stage_display=contact.get_lifecycle_stage_display()
        ) 