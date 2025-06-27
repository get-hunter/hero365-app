"""
List Contacts Use Case

Handles the business logic for retrieving lists of contacts for a business.
"""

import uuid
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

from ...dto.contact_dto import ContactListDTO, ContactResponseDTO, ContactAddressDTO
from app.api.schemas.contact_schemas import UserDetailLevel
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.contact import Contact
from app.domain.enums import ContactType, ContactStatus, ContactPriority, ContactSource, RelationshipStatus, LifecycleStage
from ...exceptions.application_exceptions import PermissionDeniedError


class ListContactsUseCase:
    """
    Use case for retrieving lists of contacts with pagination and permission validation.
    """
    
    def __init__(self, contact_repository: ContactRepository,
                 membership_repository: BusinessMembershipRepository):
        self.contact_repository = contact_repository
        self.membership_repository = membership_repository
    
    async def execute(self, business_id: uuid.UUID, user_id: str,
                     skip: int = 0, limit: int = 100,
                     include_user_details: UserDetailLevel = UserDetailLevel.BASIC) -> ContactListDTO:
        """
        Get contacts for a business with pagination and optional user data.
        
        Args:
            business_id: ID of the business
            user_id: ID of the user requesting contacts
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_user_details: Level of user detail to include
            
        Returns:
            ContactListDTO with contacts and pagination info
            
        Raises:
            PermissionError: If user lacks permission
        """
        # Validate user has permission to view contacts in this business
        await self._validate_user_permission(business_id, user_id, "view_contacts")
        
        if include_user_details == UserDetailLevel.NONE:
            # Use regular repository method
            contacts = await self.contact_repository.get_by_business_id(business_id, skip, limit)
            contact_dtos = [self._contact_to_response_dto(contact) for contact in contacts]
        else:
            # Use repository method with user data - simplified approach
            contacts_data = await self.contact_repository.get_by_business_id_with_users(
                business_id, include_user_details, skip, limit
            )
            # Use simplified conversion with better error handling
            contact_dtos = []
            for contact_data in contacts_data:
                try:
                    dto = self._contact_dict_to_response_dto_simple(contact_data, include_user_details)
                    contact_dtos.append(dto)
                except Exception as e:
                    logger.warning(f"Skipping invalid contact {contact_data.get('id', 'unknown')}: {e}")
                    continue
        
        total_count = await self.contact_repository.count_by_business(business_id)
        
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
        # Handle address JSON parsing
        address_dto = None
        if contact_data.get("address"):
            if isinstance(contact_data["address"], str):
                try:
                    import json
                    address_data = json.loads(contact_data["address"])
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse address JSON for contact {contact_data.get('id')}: {str(e)}")
                    address_data = None
            else:
                address_data = contact_data["address"]
            
            if address_data:
                address_dto = ContactAddressDTO(
                    street_address=address_data.get("street_address"),
                    city=address_data.get("city"),
                    state=address_data.get("state"),
                    postal_code=address_data.get("postal_code"),
                    country=address_data.get("country")
                )
        
        # Handle tags and custom_fields JSON parsing
        tags = []
        if contact_data.get("tags"):
            if isinstance(contact_data["tags"], str):
                try:
                    import json
                    tags = json.loads(contact_data["tags"])
                except (json.JSONDecodeError, ValueError):
                    tags = []
            else:
                tags = contact_data["tags"] or []
        
        custom_fields = {}
        if contact_data.get("custom_fields"):
            if isinstance(contact_data["custom_fields"], str):
                try:
                    import json
                    custom_fields = json.loads(contact_data["custom_fields"])
                except (json.JSONDecodeError, ValueError):
                    custom_fields = {}
            else:
                custom_fields = contact_data["custom_fields"] or {}
        
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
        
        # Safe enum conversions
        try:
            contact_type_enum = ContactType(contact_data["contact_type"])
        except ValueError:
            contact_type_enum = ContactType.PROSPECT
        
        try:
            status_enum = ContactStatus(contact_data["status"])
        except ValueError:
            status_enum = ContactStatus.ACTIVE
            
        try:
            relationship_status_enum = RelationshipStatus(contact_data.get("relationship_status", "prospect"))
        except ValueError:
            relationship_status_enum = RelationshipStatus.PROSPECT
            
        try:
            lifecycle_stage_enum = LifecycleStage(contact_data.get("lifecycle_stage", "awareness"))
        except ValueError:
            lifecycle_stage_enum = LifecycleStage.AWARENESS
            
        try:
            priority_enum = ContactPriority(contact_data.get("priority", "medium"))
        except ValueError:
            priority_enum = ContactPriority.MEDIUM
            
        try:
            source_enum = ContactSource(contact_data["source"]) if contact_data.get("source") else None
        except ValueError:
            source_enum = None
        
        # Parse datetime fields
        created_date = None
        if contact_data.get("created_date"):
            try:
                from datetime import datetime
                if isinstance(contact_data["created_date"], str):
                    created_date = datetime.fromisoformat(contact_data["created_date"].replace("Z", "+00:00"))
                else:
                    created_date = contact_data["created_date"]
            except (ValueError, TypeError):
                created_date = None
                
        last_modified = None
        if contact_data.get("last_modified"):
            try:
                from datetime import datetime
                if isinstance(contact_data["last_modified"], str):
                    last_modified = datetime.fromisoformat(contact_data["last_modified"].replace("Z", "+00:00"))
                else:
                    last_modified = contact_data["last_modified"]
            except (ValueError, TypeError):
                last_modified = None
                
        last_contacted = None
        if contact_data.get("last_contacted"):
            try:
                from datetime import datetime
                if isinstance(contact_data["last_contacted"], str):
                    last_contacted = datetime.fromisoformat(contact_data["last_contacted"].replace("Z", "+00:00"))
                else:
                    last_contacted = contact_data["last_contacted"]
            except (ValueError, TypeError):
                last_contacted = None
        
        # Create temporary contact for computed fields
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
            email=contact_data.get("email"),
            phone=contact_data.get("phone"),
            priority=priority_enum,
            source=source_enum
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
            estimated_value=contact_data.get("estimated_value"),
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
    
    def _contact_dict_to_response_dto_simple(self, contact_data: Dict[str, Any], user_detail_level: UserDetailLevel) -> ContactResponseDTO:
        """Simplified conversion using enum converters."""
        from app.api.converters import EnumConverter, SupabaseConverter
        
        # Safe enum conversions
        contact_type = EnumConverter.safe_contact_type(contact_data.get("contact_type"))
        status = EnumConverter.safe_contact_status(contact_data.get("status"))
        relationship_status = EnumConverter.safe_relationship_status(contact_data.get("relationship_status"))
        lifecycle_stage = EnumConverter.safe_lifecycle_stage(contact_data.get("lifecycle_stage"))
        priority = EnumConverter.safe_contact_priority(contact_data.get("priority"))
        source = EnumConverter.safe_contact_source(contact_data.get("source"))
        
        # Safe field parsing
        tags = SupabaseConverter.parse_list_field(contact_data.get("tags"), [])
        custom_fields = SupabaseConverter.parse_dict_field(contact_data.get("custom_fields"), {})
        created_date = SupabaseConverter.parse_datetime(contact_data.get("created_date"))
        last_modified = SupabaseConverter.parse_datetime(contact_data.get("last_modified"))
        last_contacted = SupabaseConverter.parse_datetime(contact_data.get("last_contacted"))
        
        # Handle address
        address_dto = None
        if contact_data.get("address"):
            address_data = SupabaseConverter.parse_dict_field(contact_data.get("address"))
            if address_data:
                address_dto = ContactAddressDTO(
                    street_address=address_data.get("street_address"),
                    city=address_data.get("city"),
                    state=address_data.get("state"),
                    postal_code=address_data.get("postal_code"),
                    country=address_data.get("country")
                )
        
        # Handle user references
        assigned_to = contact_data.get("assigned_to")
        created_by = contact_data.get("created_by")
        
        # Create temp contact for computed fields
        temp_contact = Contact(
            id=uuid.UUID(contact_data["id"]),
            business_id=uuid.UUID(contact_data["business_id"]),
            contact_type=contact_type,
            status=status,
            relationship_status=relationship_status,
            lifecycle_stage=lifecycle_stage,
            first_name=contact_data.get("first_name"),
            last_name=contact_data.get("last_name"),
            company_name=contact_data.get("company_name"),
            email=contact_data.get("email"),
            phone=contact_data.get("phone"),
            priority=priority,
            source=source
        )
        
        return ContactResponseDTO(
            id=uuid.UUID(contact_data["id"]),
            business_id=uuid.UUID(contact_data["business_id"]),
            contact_type=contact_type,
            status=status,
            relationship_status=relationship_status,
            lifecycle_stage=lifecycle_stage,
            first_name=contact_data.get("first_name"),
            last_name=contact_data.get("last_name"),
            company_name=contact_data.get("company_name"),
            job_title=contact_data.get("job_title"),
            email=contact_data.get("email"),
            phone=contact_data.get("phone"),
            mobile_phone=contact_data.get("mobile_phone"),
            website=contact_data.get("website"),
            address=address_dto,
            priority=priority,
            source=source,
            tags=tags,
            notes=contact_data.get("notes"),
            estimated_value=contact_data.get("estimated_value"),
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