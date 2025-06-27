"""
Contact Status Management Use Case

Handles the business logic for managing contact status and lifecycle changes.
"""

import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

from ...dto.contact_dto import ContactConversionDTO, ContactResponseDTO, ContactAddressDTO
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.contact import Contact, ContactType, RelationshipStatus, LifecycleStage
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from ...exceptions.application_exceptions import BusinessLogicError, PermissionDeniedError


class ContactStatusManagementUseCase:
    """
    Use case for managing contact status, lifecycle, and type conversions.
    """
    
    def __init__(self, contact_repository: ContactRepository,
                 membership_repository: BusinessMembershipRepository):
        self.contact_repository = contact_repository
        self.membership_repository = membership_repository
    
    async def convert_contact_type(self, dto: ContactConversionDTO, user_id: str) -> ContactResponseDTO:
        """
        Convert a contact from one type to another.
        
        Args:
            dto: Conversion parameters
            user_id: ID of the user performing conversion
            
        Returns:
            ContactResponseDTO with updated contact
            
        Raises:
            EntityNotFoundError: If contact doesn't exist
            BusinessLogicError: If conversion is not allowed
            PermissionError: If user lacks permission
        """
        contact = await self.contact_repository.get_by_id(dto.contact_id)
        if not contact:
            raise EntityNotFoundError("Contact not found")
        
        # Validate user has permission to edit contacts in this business
        await self._validate_user_permission(contact.business_id, user_id, "edit_contacts")
        
        # Perform conversion based on business rules
        if dto.to_type == ContactType.CUSTOMER:
            contact.convert_to_customer()
        elif dto.to_type == ContactType.LEAD and contact.contact_type == ContactType.PROSPECT:
            contact.convert_to_lead()
        else:
            # For other conversions, just update the type
            contact.contact_type = dto.to_type
            contact.last_modified = datetime.utcnow()
        
        # Add conversion note if provided
        if dto.notes:
            existing_notes = contact.notes or ""
            conversion_note = f"\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Converted from {dto.from_type.value} to {dto.to_type.value}: {dto.notes}"
            contact.notes = existing_notes + conversion_note
        
        updated_contact = await self.contact_repository.update(contact)
        return self._contact_to_response_dto(updated_contact)
    
    async def update_status(self, contact_id: uuid.UUID, status_data: dict, user_id: str):
        """
        Update contact relationship status and lifecycle stage.
        
        Args:
            contact_id: ID of the contact
            status_data: Status update data containing relationship_status, lifecycle_stage, etc.
            user_id: ID of the user updating the status
            
        Returns:
            Status update result with old and new status
            
        Raises:
            EntityNotFoundError: If contact doesn't exist
            PermissionError: If user lacks permission
        """
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise EntityNotFoundError("Contact not found")
        
        # Validate user has permission to edit contacts in this business
        await self._validate_user_permission(contact.business_id, user_id, "edit_contacts")
        
        # Store old status for response
        old_status = contact.relationship_status
        old_lifecycle = contact.lifecycle_stage
        
        # Update status based on provided data
        new_status = RelationshipStatus(status_data["relationship_status"])
        new_lifecycle = None
        
        if status_data.get("lifecycle_stage"):
            new_lifecycle = LifecycleStage(status_data["lifecycle_stage"])
        
        # Use domain method to update status (handles business logic)
        if new_status == RelationshipStatus.QUALIFIED_LEAD:
            contact.progress_to_qualified_lead(
                reason=status_data.get("reason"),
                notes=status_data.get("notes"),
                changed_by=user_id
            )
        elif new_status == RelationshipStatus.OPPORTUNITY:
            contact.progress_to_opportunity(
                reason=status_data.get("reason"),
                notes=status_data.get("notes"),
                changed_by=user_id
            )
        elif new_status == RelationshipStatus.ACTIVE_CLIENT:
            contact.convert_to_client(
                reason=status_data.get("reason"),
                notes=status_data.get("notes"),
                changed_by=user_id
            )
        elif new_status == RelationshipStatus.LOST_LEAD:
            contact.mark_as_lost_lead(
                reason=status_data.get("reason"),
                notes=status_data.get("notes"),
                changed_by=user_id
            )
        elif new_status == RelationshipStatus.INACTIVE:
            contact.mark_as_inactive(
                reason=status_data.get("reason"),
                notes=status_data.get("notes"),
                changed_by=user_id
            )
        elif new_status == RelationshipStatus.PAST_CLIENT:
            contact.mark_as_past_client(
                reason=status_data.get("reason"),
                notes=status_data.get("notes"),
                changed_by=user_id
            )
        else:
            # Direct status update for other cases
            contact.update_relationship_status(
                new_status=new_status,
                lifecycle_stage=new_lifecycle,
                reason=status_data.get("reason"),
                notes=status_data.get("notes"),
                changed_by=user_id
            )
        
        # Save updated contact
        await self.contact_repository.update(contact)
        
        return {
            "contact_id": contact_id,
            "old_status": old_status,
            "new_status": contact.relationship_status,
            "old_lifecycle_stage": old_lifecycle,
            "new_lifecycle_stage": contact.lifecycle_stage,
            "changed_by": user_id,
            "timestamp": datetime.utcnow(),
            "reason": status_data.get("reason")
        }
    
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