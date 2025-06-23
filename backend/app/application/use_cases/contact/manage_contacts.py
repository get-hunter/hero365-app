"""
Manage Contacts Use Case

Handles the business logic for contact management operations including CRUD, search, and bulk operations.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ...dto.contact_dto import (
    ContactCreateDTO, ContactUpdateDTO, ContactResponseDTO, ContactListDTO,
    ContactSearchDTO, ContactBulkUpdateDTO, ContactStatisticsDTO,
    ContactConversionDTO, ContactAssignmentDTO, ContactTagOperationDTO,
    ContactAddressDTO
)
from ....domain.repositories.contact_repository import ContactRepository
from ....domain.repositories.business_repository import BusinessRepository
from ....domain.repositories.business_membership_repository import BusinessMembershipRepository
from ....domain.entities.contact import Contact, ContactType, ContactStatus, ContactPriority, ContactSource, ContactAddress
from ....domain.exceptions.domain_exceptions import EntityNotFoundError, DuplicateEntityError
from ...exceptions.application_exceptions import (
    ApplicationError, ValidationError, BusinessLogicError, PermissionDeniedError
)


class ManageContactsUseCase:
    """
    Use case for managing contacts with comprehensive business logic.
    
    Handles contact creation, updates, deletion, search, and bulk operations
    with proper business validation and permission checks.
    """
    
    def __init__(self, contact_repository: ContactRepository,
                 business_repository: BusinessRepository,
                 membership_repository: BusinessMembershipRepository):
        self.contact_repository = contact_repository
        self.business_repository = business_repository
        self.membership_repository = membership_repository
    
    async def create_contact(self, dto: ContactCreateDTO, user_id: str) -> ContactResponseDTO:
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
            contact_address = ContactAddress(
                street_address=dto.address.street_address,
                city=dto.address.city,
                state=dto.address.state,
                postal_code=dto.address.postal_code,
                country=dto.address.country
            )
        
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
    
    async def get_contact(self, contact_id: uuid.UUID, user_id: str) -> ContactResponseDTO:
        """
        Get a contact by ID with permission validation.
        
        Args:
            contact_id: ID of the contact to retrieve
            user_id: ID of the user requesting the contact
            
        Returns:
            ContactResponseDTO with contact information
            
        Raises:
            EntityNotFoundError: If contact doesn't exist
            PermissionError: If user lacks permission
        """
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise EntityNotFoundError("Contact not found")
        
        # Validate user has permission to view contacts in this business
        await self._validate_user_permission(contact.business_id, user_id, "view_contacts")
        
        return self._contact_to_response_dto(contact)
    
    async def update_contact(self, dto: ContactUpdateDTO, user_id: str) -> ContactResponseDTO:
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
            contact.address = ContactAddress(
                street_address=dto.address.street_address,
                city=dto.address.city,
                state=dto.address.state,
                postal_code=dto.address.postal_code,
                country=dto.address.country
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
    
    async def delete_contact(self, contact_id: uuid.UUID, user_id: str) -> bool:
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
    
    async def get_business_contacts(self, business_id: uuid.UUID, user_id: str,
                                  skip: int = 0, limit: int = 100) -> ContactListDTO:
        """
        Get contacts for a business with pagination.
        
        Args:
            business_id: ID of the business
            user_id: ID of the user requesting contacts
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            ContactListDTO with contacts and pagination info
            
        Raises:
            PermissionError: If user lacks permission
        """
        # Validate user has permission to view contacts in this business
        await self._validate_user_permission(business_id, user_id, "view_contacts")
        
        contacts = await self.contact_repository.get_by_business_id(business_id, skip, limit)
        total_count = await self.contact_repository.count_by_business(business_id)
        
        contact_dtos = [self._contact_to_response_dto(contact) for contact in contacts]
        
        page = (skip // limit) + 1
        has_next = (skip + limit) < total_count
        has_previous = skip > 0
        
        return ContactListDTO(
            contacts=contact_dtos,
            total_count=total_count,
            page=page,
            per_page=limit,
            has_next=has_next,
            has_previous=has_previous
        )
    
    async def search_contacts(self, search_dto: ContactSearchDTO, user_id: str) -> ContactListDTO:
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
    
    async def bulk_update_contacts(self, dto: ContactBulkUpdateDTO, user_id: str) -> int:
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
    
    async def get_contact_statistics(self, business_id: uuid.UUID, user_id: str) -> ContactStatisticsDTO:
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
    
    async def mark_contact_contacted(self, contact_id: uuid.UUID, user_id: str) -> ContactResponseDTO:
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
    
    async def add_contact_interaction(self, contact_id: uuid.UUID, interaction_data: dict, user_id: str):
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
        from ....domain.entities.contact import InteractionType
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
    
    async def get_contact_interactions(self, contact_id: uuid.UUID, user_id: str, skip: int = 0, limit: int = 50):
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
    
    async def update_contact_status(self, contact_id: uuid.UUID, status_data: dict, user_id: str):
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
        from ....domain.entities.contact import RelationshipStatus, LifecycleStage
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
    
    # Helper methods
    
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
            source_display=contact.get_source_display()
        )
    
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