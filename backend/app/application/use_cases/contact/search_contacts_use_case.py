"""
Search Contacts Use Case

Handles the business logic for searching contacts with advanced filtering.
"""

import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)

from ...dto.contact_dto import ContactSearchDTO, ContactListDTO, ContactResponseDTO, ContactAddressDTO
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.contact import Contact
from ...exceptions.application_exceptions import PermissionDeniedError


class SearchContactsUseCase:
    """
    Use case for searching contacts with advanced filtering and permission validation.
    """
    
    def __init__(self, contact_repository: ContactRepository,
                 membership_repository: BusinessMembershipRepository):
        self.contact_repository = contact_repository
        self.membership_repository = membership_repository
    
    async def execute(self, search_dto: ContactSearchDTO, user_id: str) -> ContactListDTO:
        """
        Search contacts with advanced filtering.
        
        Args:
            search_dto: Search parameters
            user_id: ID of the user performing search
            
        Returns:
            ContactListDTO with matching contacts
            
        Raises:
            PermissionError: If user lacks permission
        """
        # Validate user has permission to view contacts in this business
        await self._validate_user_permission(search_dto.business_id, user_id, "view_contacts")
        
        # For now, implement basic search - in production, this would use advanced filtering
        if search_dto.search_term:
            contacts = await self.contact_repository.search_contacts(
                search_dto.business_id, search_dto.search_term, search_dto.skip, search_dto.limit
            )
        else:
            contacts = await self.contact_repository.get_by_business_id(
                search_dto.business_id, search_dto.skip, search_dto.limit
            )
        
        # Apply additional filters (this would be optimized in the repository layer)
        filtered_contacts = []
        for contact in contacts:
            if self._matches_search_criteria(contact, search_dto):
                filtered_contacts.append(contact)
        
        total_count = len(filtered_contacts)
        contact_dtos = [self._contact_to_response_dto(contact) for contact in filtered_contacts]
        
        page = (search_dto.skip // search_dto.limit) + 1
        has_next = (search_dto.skip + search_dto.limit) < total_count
        has_previous = search_dto.skip > 0
        
        return ContactListDTO(
            contacts=contact_dtos,
            total_count=total_count,
            page=page,
            per_page=search_dto.limit,
            has_next=has_next,
            has_previous=has_previous
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
    
    def _matches_search_criteria(self, contact: Contact, search_dto: ContactSearchDTO) -> bool:
        """Check if contact matches search criteria."""
        # This is a simplified version - in production, filtering would be done at the database level
        
        if search_dto.contact_type and contact.contact_type != search_dto.contact_type:
            return False
        
        if search_dto.status and contact.status != search_dto.status:
            return False
        
        if search_dto.priority and contact.priority != search_dto.priority:
            return False
        
        if search_dto.source and contact.source != search_dto.source:
            return False
        
        if search_dto.assigned_to and contact.assigned_to != search_dto.assigned_to:
            return False
        
        if search_dto.has_email is not None:
            if search_dto.has_email and not contact.email:
                return False
            if not search_dto.has_email and contact.email:
                return False
        
        if search_dto.has_phone is not None:
            if search_dto.has_phone and not (contact.phone or contact.mobile_phone):
                return False
            if not search_dto.has_phone and (contact.phone or contact.mobile_phone):
                return False
        
        if search_dto.min_estimated_value is not None:
            if not contact.estimated_value or contact.estimated_value < search_dto.min_estimated_value:
                return False
        
        if search_dto.max_estimated_value is not None:
            if not contact.estimated_value or contact.estimated_value > search_dto.max_estimated_value:
                return False
        
        if search_dto.never_contacted is not None:
            if search_dto.never_contacted and contact.last_contacted:
                return False
            if not search_dto.never_contacted and not contact.last_contacted:
                return False
        
        return True
    
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