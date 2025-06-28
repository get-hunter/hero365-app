"""
Create Contact Use Case

Handles the business logic for creating new contacts.
"""

import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

from ...dto.contact_dto import ContactCreateDTO, ContactResponseDTO, ContactAddressDTO
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_repository import BusinessRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.contact import Contact
from app.domain.value_objects.address import Address
from ...exceptions.application_exceptions import (
    ValidationError, BusinessLogicError, PermissionDeniedError
)


class CreateContactUseCase:
    """
    Use case for creating new contacts with validation and permission checks.
    """
    
    def __init__(self, contact_repository: ContactRepository,
                 business_repository: BusinessRepository,
                 membership_repository: BusinessMembershipRepository):
        self.contact_repository = contact_repository
        self.business_repository = business_repository
        self.membership_repository = membership_repository
    
    async def execute(self, dto: ContactCreateDTO, user_id: str) -> ContactResponseDTO:
        """
        Create a new contact with validation.
        
        Args:
            dto: Contact creation data
            user_id: ID of the user creating the contact
            
        Returns:
            ContactResponseDTO with created contact information
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
            PermissionError: If user lacks permission
        """
        # Validate user has permission to create contacts in this business
        await self._validate_user_permission(dto.business_id, user_id, "edit_contacts")
        
        # Validate business exists
        business = await self.business_repository.get_by_id(dto.business_id)
        if not business:
            raise ValidationError("Business not found")
        
        # Check for duplicate email/phone if provided
        if dto.email:
            existing = await self.contact_repository.get_by_email(dto.business_id, dto.email)
            if existing:
                raise BusinessLogicError(f"Contact with email {dto.email} already exists")
        
        if dto.phone:
            existing = await self.contact_repository.get_by_phone(dto.business_id, dto.phone)
            if existing:
                raise BusinessLogicError(f"Contact with phone {dto.phone} already exists")
        
        # Create contact entity
        contact_address = None
        if dto.address:
            contact_address = Address(
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
        
        # Debug logging
        logger.info(f"🔧 Creating contact with data:")
        logger.info(f"    Business ID: {dto.business_id}")
        logger.info(f"    Contact Type: {dto.contact_type}")
        logger.info(f"    First Name: {dto.first_name}")
        logger.info(f"    Last Name: {dto.last_name}")
        logger.info(f"    Email: {dto.email}")
        logger.info(f"    Phone: {dto.phone}")
        logger.info(f"    Created By: {user_id}")
        logger.info(f"    Custom Fields: {dto.custom_fields}")
        
        contact = Contact.create_contact(
            business_id=dto.business_id,
            contact_type=dto.contact_type,
            first_name=dto.first_name,
            last_name=dto.last_name,
            company_name=dto.company_name,
            email=dto.email,
            phone=dto.phone,
            created_by=user_id,
            job_title=dto.job_title,
            mobile_phone=dto.mobile_phone,
            website=dto.website,
            address=contact_address,
            priority=dto.priority,
            source=dto.source,
            tags=dto.tags.copy() if dto.tags else [],
            notes=dto.notes,
            estimated_value=dto.estimated_value,
            currency=dto.currency,
            assigned_to=dto.assigned_to,
            custom_fields=dto.custom_fields.copy() if dto.custom_fields else {}
        )
        
        # Save to repository
        created_contact = await self.contact_repository.create(contact)
        
        return self._contact_to_response_dto(created_contact)
    
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