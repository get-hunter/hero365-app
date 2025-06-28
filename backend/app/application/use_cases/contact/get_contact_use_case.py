"""
Get Contact Use Case

Handles the business logic for retrieving contacts.
"""

import uuid
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

from ...dto.contact_dto import ContactResponseDTO, ContactAddressDTO
from app.api.schemas.contact_schemas import UserDetailLevel
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.contact import Contact, ContactType, ContactStatus, ContactPriority, ContactSource, RelationshipStatus, LifecycleStage
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from ...exceptions.application_exceptions import PermissionDeniedError


class GetContactUseCase:
    """
    Use case for retrieving contacts with permission validation.
    """
    
    def __init__(self, contact_repository: ContactRepository,
                 membership_repository: BusinessMembershipRepository):
        self.contact_repository = contact_repository
        self.membership_repository = membership_repository
    
    async def execute(self, contact_id: uuid.UUID, user_id: str, 
                     include_user_details: UserDetailLevel = UserDetailLevel.BASIC) -> ContactResponseDTO:
        """
        Get a contact by ID with permission validation and optional user data.
        
        Args:
            contact_id: ID of the contact to retrieve
            user_id: ID of the user requesting the contact
            include_user_details: Level of user detail to include
            
        Returns:
            ContactResponseDTO with contact information
            
        Raises:
            EntityNotFoundError: If contact doesn't exist
            PermissionError: If user lacks permission
        """
        if include_user_details == UserDetailLevel.NONE:
            # Use regular repository method
            contact = await self.contact_repository.get_by_id(contact_id)
            if not contact:
                raise EntityNotFoundError("Contact not found")
            
            # Validate user has permission to view contacts in this business
            await self._validate_user_permission(contact.business_id, user_id, "view_contacts")
            
            return self._contact_to_response_dto(contact)
        else:
            # Use repository method with user data
            contact_data = await self.contact_repository.get_by_id_with_users(contact_id, include_user_details)
            if not contact_data:
                raise EntityNotFoundError("Contact not found")
            
            # Validate user has permission to view contacts in this business
            await self._validate_user_permission(uuid.UUID(contact_data["business_id"]), user_id, "view_contacts")
            
            return self._contact_dict_to_response_dto(contact_data, include_user_details)
    
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
    
    def _contact_dict_to_response_dto(self, contact_data: Dict[str, Any], user_detail_level: UserDetailLevel) -> ContactResponseDTO:
        """Convert contact dictionary data with user information to response DTO."""
        
        # Handle address from JSONB field
        address_dto = None
        if contact_data.get("address"):
            try:
                if isinstance(contact_data["address"], str):
                    import json
                    address_data = json.loads(contact_data["address"])
                else:
                    address_data = contact_data["address"]
                
                if address_data and any(address_data.get(field) for field in ['street_address', 'city', 'state', 'postal_code']):
                    address_dto = ContactAddressDTO(
                        street_address=address_data.get("street_address"),
                        city=address_data.get("city"),
                        state=address_data.get("state"),
                        postal_code=address_data.get("postal_code"),
                        country=address_data.get("country", "US"),
                        latitude=address_data.get("latitude"),
                        longitude=address_data.get("longitude"),
                        access_notes=address_data.get("access_notes"),
                        place_id=address_data.get("place_id"),
                        formatted_address=address_data.get("formatted_address"),
                        address_type=address_data.get("address_type")
                    )
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.warning(f"Failed to parse address JSON for contact {contact_data.get('id')}: {str(e)}")
                address_dto = None
        
        # Handle tags with safe JSON parsing
        tags = []
        if contact_data.get("tags"):
            if isinstance(contact_data["tags"], str):
                try:
                    import json
                    tags = json.loads(contact_data["tags"])
                except (json.JSONDecodeError, ValueError) as e:
                    # If JSON parsing fails, log the error and default to empty list
                    logger.warning(f"Failed to parse tags JSON for contact {contact_data.get('id')}: {str(e)}")
                    tags = []
            else:
                tags = contact_data["tags"] or []
        
        # Handle custom fields with safe JSON parsing
        custom_fields = {}
        if contact_data.get("custom_fields"):
            if isinstance(contact_data["custom_fields"], str):
                try:
                    import json
                    custom_fields = json.loads(contact_data["custom_fields"])
                except (json.JSONDecodeError, ValueError) as e:
                    # If JSON parsing fails, log the error and default to empty dict
                    logger.warning(f"Failed to parse custom_fields JSON for contact {contact_data.get('id')}: {str(e)}")
                    custom_fields = {}
            else:
                custom_fields = contact_data["custom_fields"] or {}
        
        # Handle dates
        created_date = None
        if contact_data.get("created_date"):
            if isinstance(contact_data["created_date"], str):
                created_date = datetime.fromisoformat(contact_data["created_date"].replace('Z', '+00:00'))
            else:
                created_date = contact_data["created_date"]
        
        last_modified = None
        if contact_data.get("last_modified"):
            if isinstance(contact_data["last_modified"], str):
                last_modified = datetime.fromisoformat(contact_data["last_modified"].replace('Z', '+00:00'))
            else:
                last_modified = contact_data["last_modified"]
        
        last_contacted = None
        if contact_data.get("last_contacted"):
            if isinstance(contact_data["last_contacted"], str):
                last_contacted = datetime.fromisoformat(contact_data["last_contacted"].replace('Z', '+00:00'))
            else:
                last_contacted = contact_data["last_contacted"]
        
        # Handle user references based on detail level
        assigned_to = contact_data.get("assigned_to")
        created_by = contact_data.get("created_by")
        
        if user_detail_level == UserDetailLevel.BASIC and isinstance(assigned_to, dict):
            assigned_to = {
                "id": assigned_to["id"],
                "display_name": assigned_to["display_name"],
                "email": assigned_to.get("email")
            }
        elif user_detail_level == UserDetailLevel.FULL and isinstance(assigned_to, dict):
            assigned_to = {
                "id": assigned_to["id"],
                "display_name": assigned_to["display_name"],
                "email": assigned_to.get("email"),
                "full_name": assigned_to.get("full_name"),
                "phone": assigned_to.get("phone"),
                "role": assigned_to.get("role"),
                "department": assigned_to.get("department"),
                "is_active": assigned_to.get("is_active", True)
            }
        
        if user_detail_level == UserDetailLevel.BASIC and isinstance(created_by, dict):
            created_by = {
                "id": created_by["id"],
                "display_name": created_by["display_name"],
                "email": created_by.get("email")
            }
        elif user_detail_level == UserDetailLevel.FULL and isinstance(created_by, dict):
            created_by = {
                "id": created_by["id"],
                "display_name": created_by["display_name"],
                "email": created_by.get("email"),
                "full_name": created_by.get("full_name"),
                "phone": created_by.get("phone"),
                "role": created_by.get("role"),
                "department": created_by.get("department"),
                "is_active": created_by.get("is_active", True)
            }
        
        # Create temporary contact entity for computed fields
        # Ensure at least one contact method for validation (use placeholder if none exist)
        email = contact_data.get("email") or None
        phone = contact_data.get("phone") or None
        mobile_phone = contact_data.get("mobile_phone") or None
        
        # If no contact methods exist, provide a placeholder email to pass validation
        if not email and not phone and not mobile_phone:
            email = "placeholder@example.com"
        
        # Handle relationship_status and lifecycle_stage with defaults
        relationship_status_str = contact_data.get("relationship_status", "prospect")
        lifecycle_stage_str = contact_data.get("lifecycle_stage", "awareness")
        
        # Convert to enums if they are strings with safe parsing
        if isinstance(relationship_status_str, str):
            try:
                relationship_status_enum = RelationshipStatus(relationship_status_str)
            except ValueError as e:
                # Handle invalid enum values - map common variations or default to PROSPECT
                status_mapping = {
                    'active_customer': RelationshipStatus.ACTIVE_CLIENT,
                    'customer': RelationshipStatus.ACTIVE_CLIENT,
                    'client': RelationshipStatus.ACTIVE_CLIENT,
                    'lead': RelationshipStatus.QUALIFIED_LEAD,
                    'potential': RelationshipStatus.PROSPECT
                }
                relationship_status_enum = status_mapping.get(relationship_status_str.lower(), RelationshipStatus.PROSPECT)
                logger.warning(f"Invalid relationship_status '{relationship_status_str}' for contact {contact_data.get('id')}, mapped to {relationship_status_enum.value}")
        else:
            relationship_status_enum = relationship_status_str or RelationshipStatus.PROSPECT
            
        if isinstance(lifecycle_stage_str, str):
            try:
                lifecycle_stage_enum = LifecycleStage(lifecycle_stage_str)
            except ValueError as e:
                # Handle invalid enum values - default to AWARENESS
                stage_mapping = {
                    'customer': LifecycleStage.CUSTOMER,
                    'client': LifecycleStage.CUSTOMER,
                    'new': LifecycleStage.AWARENESS,
                    'lead': LifecycleStage.INTEREST
                }
                lifecycle_stage_enum = stage_mapping.get(lifecycle_stage_str.lower(), LifecycleStage.AWARENESS)
                logger.warning(f"Invalid lifecycle_stage '{lifecycle_stage_str}' for contact {contact_data.get('id')}, mapped to {lifecycle_stage_enum.value}")
        else:
            lifecycle_stage_enum = lifecycle_stage_str or LifecycleStage.AWARENESS
        
        # Safe enum conversions for other fields
        try:
            contact_type_enum = ContactType(contact_data["contact_type"])
        except ValueError:
            contact_type_enum = ContactType.PROSPECT
            logger.warning(f"Invalid contact_type '{contact_data.get('contact_type')}' for contact {contact_data.get('id')}, defaulted to prospect")
        
        try:
            status_enum = ContactStatus(contact_data["status"])
        except ValueError:
            status_enum = ContactStatus.ACTIVE
            logger.warning(f"Invalid status '{contact_data.get('status')}' for contact {contact_data.get('id')}, defaulted to active")
        
        try:
            priority_enum = ContactPriority(contact_data.get("priority", "medium"))
        except ValueError:
            priority_enum = ContactPriority.MEDIUM
            logger.warning(f"Invalid priority '{contact_data.get('priority')}' for contact {contact_data.get('id')}, defaulted to medium")
        
        source_enum = None
        if contact_data.get("source"):
            try:
                source_enum = ContactSource(contact_data["source"])
            except ValueError:
                source_enum = None
                logger.warning(f"Invalid source '{contact_data.get('source')}' for contact {contact_data.get('id')}, set to None")

        temp_contact = Contact(
            id=uuid.UUID(contact_data["id"]),
            business_id=uuid.UUID(contact_data["business_id"]),
            contact_type=contact_type_enum,
            status=status_enum,
            relationship_status=relationship_status_enum,
            lifecycle_stage=lifecycle_stage_enum,
            first_name=contact_data.get("first_name"),
            last_name=contact_data.get("last_name"),
            company_name=contact_data.get("company_name"),
            email=email,
            phone=phone,
            mobile_phone=mobile_phone,
            priority=priority_enum,
            source=source_enum,
        )
        
        return ContactResponseDTO(
            id=uuid.UUID(contact_data["id"]),
            business_id=uuid.UUID(contact_data["business_id"]),
            contact_type=contact_type_enum,
            status=status_enum,
            relationship_status=relationship_status_enum,
            lifecycle_stage=lifecycle_stage_enum,
            first_name=contact_data.get("first_name"),
            last_name=contact_data.get("last_name"),
            company_name=contact_data.get("company_name"),
            job_title=contact_data.get("job_title"),
            email=contact_data.get("email"),
            phone=contact_data.get("phone"),
            mobile_phone=contact_data.get("mobile_phone"),
            website=contact_data.get("website"),
            address=address_dto,
            priority=priority_enum,
            source=source_enum,
            tags=tags,
            notes=contact_data.get("notes"),
            estimated_value=float(contact_data["estimated_value"]) if contact_data.get("estimated_value") else None,
            currency=contact_data.get("currency", "USD"),
            assigned_to=assigned_to,
            created_by=created_by,
            custom_fields=custom_fields,
            created_date=created_date,
            last_modified=last_modified,
            last_contacted=last_contacted,
            display_name=temp_contact.get_display_name(),
            primary_contact_method=temp_contact.get_primary_contact_method(),
            type_display=temp_contact.get_type_display(),
            status_display=temp_contact.get_status_display(),
            priority_display=temp_contact.get_priority_display(),
            source_display=temp_contact.get_source_display(),
            relationship_status_display=temp_contact.get_relationship_status_display(),
            lifecycle_stage_display=temp_contact.get_lifecycle_stage_display()
        ) 