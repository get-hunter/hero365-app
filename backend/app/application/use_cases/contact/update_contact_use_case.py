"""
Update Contact Use Case

Handles the business logic for updating existing contacts.
"""

import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

from ...dto.contact_dto import ContactUpdateDTO, ContactResponseDTO, ContactAddressDTO
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.contact import Contact
from app.domain.value_objects.address import Address
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from ...exceptions.application_exceptions import (
    ValidationError, BusinessLogicError, PermissionDeniedError
)


class UpdateContactUseCase:
    """
    Use case for updating existing contacts with validation and permission checks.
    """
    
    def __init__(self, contact_repository: ContactRepository,
                 membership_repository: BusinessMembershipRepository):
        self.contact_repository = contact_repository
        self.membership_repository = membership_repository
    
    async def execute(self, dto: ContactUpdateDTO, user_id: str) -> ContactResponseDTO:
        """
        Update an existing contact.
        
        Args:
            dto: Contact update data
            user_id: ID of the user updating the contact
            
        Returns:
            ContactResponseDTO with updated contact information
            
        Raises:
            EntityNotFoundError: If contact doesn't exist
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
            PermissionError: If user lacks permission
        """
        # Get existing contact
        contact = await self.contact_repository.get_by_id(dto.contact_id)
        if not contact:
            raise EntityNotFoundError("Contact not found")
        
        # Validate user has permission to edit contacts in this business
        await self._validate_user_permission(contact.business_id, user_id, "edit_contacts")
        
        # Check for duplicate email/phone if being updated
        if dto.email and dto.email != contact.email:
            if await self.contact_repository.has_duplicate_email(
                contact.business_id, dto.email, exclude_id=contact.id
            ):
                raise BusinessLogicError(f"Contact with email {dto.email} already exists")
        
        if dto.phone and dto.phone != contact.phone:
            if await self.contact_repository.has_duplicate_phone(
                contact.business_id, dto.phone, exclude_id=contact.id
            ):
                raise BusinessLogicError(f"Contact with phone {dto.phone} already exists")
        
        # Update contact fields
        if dto.first_name is not None:
            contact.first_name = dto.first_name
        if dto.last_name is not None:
            contact.last_name = dto.last_name
        if dto.company_name is not None:
            contact.company_name = dto.company_name
        if dto.job_title is not None:
            contact.job_title = dto.job_title
        if dto.email is not None:
            contact.email = dto.email
        if dto.phone is not None:
            contact.phone = dto.phone
        if dto.mobile_phone is not None:
            contact.mobile_phone = dto.mobile_phone
        if dto.website is not None:
            contact.website = dto.website
        if dto.address is not None:
            contact.address = Address(
                street_address=dto.address.street_address,
                city=dto.address.city,
                state=dto.address.state,
                postal_code=dto.address.postal_code,
                country=dto.address.country or "US",
                latitude=dto.address.latitude,
                longitude=dto.address.longitude,
                access_notes=dto.address.access_notes,
                place_id=dto.address.place_id,
                formatted_address=dto.address.formatted_address,
                address_type=dto.address.address_type
            )
        if dto.priority is not None:
            contact.priority = dto.priority
        if dto.source is not None:
            contact.source = dto.source
        if dto.tags is not None:
            contact.tags = dto.tags.copy()
        if dto.notes is not None:
            contact.notes = dto.notes
        if dto.estimated_value is not None:
            contact.estimated_value = dto.estimated_value
        if dto.currency is not None:
            contact.currency = dto.currency
        if dto.assigned_to is not None:
            contact.assigned_to = dto.assigned_to
        if dto.custom_fields is not None:
            contact.custom_fields.update(dto.custom_fields)
        
        contact.last_modified = datetime.utcnow()
        
        # Save updated contact
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
                country=contact.address.country,
                latitude=contact.address.latitude,
                longitude=contact.address.longitude,
                access_notes=contact.address.access_notes,
                place_id=contact.address.place_id,
                formatted_address=contact.address.formatted_address,
                address_type=contact.address.address_type
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