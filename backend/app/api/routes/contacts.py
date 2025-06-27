"""
Contact API Routes

REST API endpoints for contact management operations.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body

from ..deps import get_current_user, get_business_context
from ..middleware.permissions import (
    require_view_contacts_dep, require_edit_contacts_dep, require_delete_contacts_dep
)
from ..schemas.contact_schemas import (
    ContactCreateRequest, ContactUpdateRequest, ContactSearchRequest,
    ContactBulkUpdateRequest, ContactConversionRequest, ContactAssignmentRequest,
    ContactTagOperationRequest, ContactResponse, ContactListResponse,
    ContactStatisticsResponse, ContactBulkOperationResponse, MessageResponse,
    ContactInteractionCreateRequest, ContactInteractionResponse, ContactInteractionListResponse,
    ContactStatusUpdateRequest, ContactStatusUpdateResponse, UserDetailLevel
)
from ...application.use_cases.contact.create_contact_use_case import CreateContactUseCase
from ...application.use_cases.contact.get_contact_use_case import GetContactUseCase
from ...application.use_cases.contact.update_contact_use_case import UpdateContactUseCase
from ...application.use_cases.contact.delete_contact_use_case import DeleteContactUseCase
from ...application.use_cases.contact.list_contacts_use_case import ListContactsUseCase
from ...application.use_cases.contact.search_contacts_use_case import SearchContactsUseCase
from ...application.use_cases.contact.contact_statistics_use_case import ContactStatisticsUseCase
from ...application.use_cases.contact.contact_interaction_use_case import ContactInteractionUseCase
from ...application.use_cases.contact.contact_status_management_use_case import ContactStatusManagementUseCase
from ...application.use_cases.contact.bulk_contact_operations_use_case import BulkContactOperationsUseCase
from ...application.dto.contact_dto import (
    ContactCreateDTO, ContactUpdateDTO, ContactSearchDTO, ContactBulkUpdateDTO,
    ContactConversionDTO, ContactAssignmentDTO, ContactTagOperationDTO,
    ContactAddressDTO
)
from ...domain.entities.contact import ContactType, ContactStatus, ContactPriority, ContactSource, RelationshipStatus, LifecycleStage
from ...infrastructure.config.dependency_injection import (
    get_create_contact_use_case, get_get_contact_use_case, get_update_contact_use_case,
    get_delete_contact_use_case, get_list_contacts_use_case, get_search_contacts_use_case,
    get_contact_statistics_use_case, get_contact_interaction_use_case,
    get_contact_status_management_use_case, get_bulk_contact_operations_use_case
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, operation_id="create_contact_no_slash")
async def create_contact(
    request: ContactCreateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: CreateContactUseCase = Depends(get_create_contact_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Create a new contact.
    
    Creates a new contact for the current business with the provided information.
    Requires 'edit_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 ContactAPI: Starting contact creation for business {business_id}")
    logger.info(f"🔧 ContactAPI: Request data: {request}")
    
    try:
        # Convert address if provided
        address_dto = None
        if request.address:
            logger.info(f"🔧 ContactAPI: Converting address: {request.address}")
            address_dto = ContactAddressDTO(
                street_address=request.address.street_address,
                city=request.address.city,
                state=request.address.state,
                postal_code=request.address.postal_code,
                country=request.address.country
            )
        
        logger.info(f"🔧 ContactAPI: Creating DTO with contact_type: {request.contact_type}")
        
        # Create DTO
        create_dto = ContactCreateDTO(
            business_id=business_id,
            contact_type=ContactType(request.contact_type.value),
            first_name=request.first_name,
            last_name=request.last_name,
            company_name=request.company_name,
            job_title=request.job_title,
            email=request.email,
            phone=request.phone,
            mobile_phone=request.mobile_phone,
            website=request.website,
            address=address_dto,
            priority=ContactPriority(request.priority.value),
            source=ContactSource(request.source.value) if request.source else None,
            tags=request.tags,
            notes=request.notes,
            estimated_value=request.estimated_value,
            currency=request.currency,
            assigned_to=request.assigned_to,
            created_by=current_user["sub"],
            custom_fields=request.custom_fields
        )
        
        logger.info(f"🔧 ContactAPI: DTO created successfully, calling use case")
        
        contact_dto = await use_case.execute(create_dto, current_user["sub"])
        logger.info(f"🔧 ContactAPI: Use case completed successfully")
        return _contact_dto_to_response(contact_dto)
    except Exception as e:
        logger.error(f"❌ ContactAPI: Error creating contact: {str(e)}")
        logger.error(f"❌ ContactAPI: Error type: {type(e)}")
        import traceback
        logger.error(f"❌ ContactAPI: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: uuid.UUID = Path(..., description="Contact ID"),
    include_user_details: UserDetailLevel = Query(UserDetailLevel.BASIC, description="Level of user detail to include"),
    current_user: dict = Depends(get_current_user),
    use_case: GetContactUseCase = Depends(get_get_contact_use_case),
    _: bool = Depends(require_view_contacts_dep)
):
    """
    Get a contact by ID.
    
    Retrieves detailed information about a specific contact with optional user data.
    Requires 'view_contacts' permission.
    """
    try:
        contact_dto = await use_case.execute(contact_id, current_user["sub"], include_user_details)
        return _contact_dto_to_response(contact_dto)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: uuid.UUID = Path(..., description="Contact ID"),
    request: ContactUpdateRequest = Body(...),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: UpdateContactUseCase = Depends(get_update_contact_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Update a contact.
    
    Updates an existing contact with the provided information.
    Requires 'edit_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 ContactAPI: Starting contact update for contact {contact_id}")
    logger.info(f"🔧 ContactAPI: Request data: {request}")
    
    try:
        # Convert address if provided
        address_dto = None
        if request.address:
            logger.info(f"🔧 ContactAPI: Converting address: {request.address}")
            address_dto = ContactAddressDTO(
                street_address=request.address.street_address,
                city=request.address.city,
                state=request.address.state,
                postal_code=request.address.postal_code,
                country=request.address.country
            )
        
        # Create update DTO
        update_dto = ContactUpdateDTO(
            contact_id=contact_id,
            business_id=business_id,
            first_name=request.first_name,
            last_name=request.last_name,
            company_name=request.company_name,
            job_title=request.job_title,
            email=request.email,
            phone=request.phone,
            mobile_phone=request.mobile_phone,
            website=request.website,
            address=address_dto,
            priority=ContactPriority(request.priority.value) if request.priority else None,
            source=ContactSource(request.source.value) if request.source else None,
            tags=request.tags,
            notes=request.notes,
            estimated_value=request.estimated_value,
            currency=request.currency,
            assigned_to=request.assigned_to,
            custom_fields=request.custom_fields
        )
        
        logger.info(f"🔧 ContactAPI: DTO created successfully, calling use case")
        
        contact_dto = await use_case.execute(update_dto, current_user["sub"])
        logger.info(f"🔧 ContactAPI: Use case completed successfully")
        return _contact_dto_to_response(contact_dto)
    except Exception as e:
        logger.error(f"❌ ContactAPI: Error updating contact: {str(e)}")
        logger.error(f"❌ ContactAPI: Error type: {type(e)}")
        import traceback
        logger.error(f"❌ ContactAPI: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{contact_id}", response_model=MessageResponse)
async def delete_contact(
    contact_id: uuid.UUID = Path(..., description="Contact ID"),
    current_user: dict = Depends(get_current_user),
    use_case: DeleteContactUseCase = Depends(get_delete_contact_use_case),
    _: bool = Depends(require_delete_contacts_dep)
):
    """
    Delete a contact.
    
    Permanently deletes a contact and all associated data.
    Requires 'delete_contacts' permission.
    """
    try:
        success = await use_case.execute(contact_id, current_user["sub"])
        if success:
            return MessageResponse(message="Contact deleted successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=ContactListResponse)
@router.get("", response_model=ContactListResponse, operation_id="list_contacts_no_slash")
async def list_contacts(
    business_context: dict = Depends(get_business_context),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_user_details: UserDetailLevel = Query(UserDetailLevel.BASIC, description="Level of user detail to include"),
    current_user: dict = Depends(get_current_user),
    use_case: ListContactsUseCase = Depends(get_list_contacts_use_case),
    _: bool = Depends(require_view_contacts_dep)
):
    """
    List contacts for the current business.
    
    Retrieves a paginated list of contacts with optional user detail information.
    Requires 'view_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        contact_list_dto = await use_case.execute(
            business_id, current_user["sub"], skip, limit, include_user_details
        )
        
        logger.info(f"🔧 ContactAPI: Retrieved {len(contact_list_dto.contacts)} contacts from use case")
        
        # Convert contacts one by one to catch which one fails
        converted_contacts = []
        for i, contact in enumerate(contact_list_dto.contacts):
            try:
                logger.info(f"🔧 ContactAPI: Converting contact {i+1}/{len(contact_list_dto.contacts)} - ID: {contact.id}")
                converted_contact = _contact_dto_to_response(contact)
                converted_contacts.append(converted_contact)
            except Exception as contact_error:
                logger.error(f"❌ ContactAPI: Failed to convert contact {i+1} (ID: {contact.id}): {str(contact_error)}")
                raise contact_error
        
        return ContactListResponse(
            contacts=converted_contacts,
            total_count=contact_list_dto.total_count,
            page=contact_list_dto.page,
            per_page=contact_list_dto.per_page,
            has_next=contact_list_dto.has_next,
            has_previous=contact_list_dto.has_previous
        )
    except Exception as e:
        logger.error(f"❌ ContactAPI: Error in list_contacts: {str(e)}")
        import traceback
        logger.error(f"❌ ContactAPI: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/search", response_model=ContactListResponse)
async def search_contacts(
    request: ContactSearchRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: SearchContactsUseCase = Depends(get_search_contacts_use_case),
    _: bool = Depends(require_view_contacts_dep)
):
    """
    Search contacts with advanced filtering.
    
    Performs advanced search across contacts with multiple filtering options.
    Requires 'view_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Create search DTO
        search_dto = ContactSearchDTO(
            business_id=business_id,
            search_term=request.search_term,
            contact_type=ContactType(request.contact_type.value) if request.contact_type else None,
            status=ContactStatus(request.status.value) if request.status else None,
            priority=ContactPriority(request.priority.value) if request.priority else None,
            source=ContactSource(request.source.value) if request.source else None,
            assigned_to=request.assigned_to,
            has_email=request.has_email,
            has_phone=request.has_phone,
            min_estimated_value=request.min_estimated_value,
            max_estimated_value=request.max_estimated_value,
            never_contacted=request.never_contacted,
            skip=request.skip,
            limit=request.limit
        )
        
        contact_list_dto = await use_case.execute(search_dto, current_user["sub"])
        
        return ContactListResponse(
            contacts=[_contact_dto_to_response(contact) for contact in contact_list_dto.contacts],
            total_count=contact_list_dto.total_count,
            page=contact_list_dto.page,
            per_page=contact_list_dto.per_page,
            has_next=contact_list_dto.has_next,
            has_previous=contact_list_dto.has_previous
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bulk-update", response_model=ContactBulkOperationResponse)
async def bulk_update_contacts(
    request: ContactBulkUpdateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: BulkContactOperationsUseCase = Depends(get_bulk_contact_operations_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Perform bulk updates on multiple contacts.
    
    Updates multiple contacts at once with the same changes.
    Requires 'edit_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Create bulk update DTO
        bulk_dto = ContactBulkUpdateDTO(
            business_id=business_id,
            contact_ids=request.contact_ids,
            status=ContactStatus(request.status.value) if request.status else None,
            assigned_to=request.assigned_to,
            tags_to_add=request.tags_to_add
        )
        
        updated_count = await use_case.bulk_update(bulk_dto, current_user["sub"])
        
        return ContactBulkOperationResponse(
            success=True,
            message=f"Successfully updated {updated_count} contacts",
            updated_count=updated_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{contact_id}/convert", response_model=ContactResponse)
async def convert_contact_type(
    contact_id: uuid.UUID = Path(..., description="Contact ID"),
    request: ContactConversionRequest = Body(...),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ContactStatusManagementUseCase = Depends(get_contact_status_management_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Convert a contact from one type to another.
    
    Changes the contact type and applies appropriate business logic.
    Requires 'edit_contacts' permission.
    """
    try:
        # Create conversion DTO
        conversion_dto = ContactConversionDTO(
            contact_id=contact_id,
            from_type=ContactType(request.from_type.value),
            to_type=ContactType(request.to_type.value),
            notes=request.notes
        )
        
        contact_dto = await use_case.convert_contact_type(conversion_dto, current_user["sub"])
        return _contact_dto_to_response(contact_dto)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/assign", response_model=ContactBulkOperationResponse)
async def assign_contacts(
    request: ContactAssignmentRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: BulkContactOperationsUseCase = Depends(get_bulk_contact_operations_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Assign multiple contacts to a team member.
    
    Bulk assigns contacts to a specific user for management.
    Requires 'edit_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Create bulk assignment DTO
        bulk_dto = ContactBulkUpdateDTO(
            business_id=business_id,
            contact_ids=request.contact_ids,
            assigned_to=request.assigned_to
        )
        
        updated_count = await use_case.bulk_update(bulk_dto, current_user["sub"])
        
        return ContactBulkOperationResponse(
            success=True,
            message=f"Successfully assigned {updated_count} contacts",
            updated_count=updated_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/tags", response_model=ContactBulkOperationResponse)
async def manage_contact_tags(
    request: ContactTagOperationRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: BulkContactOperationsUseCase = Depends(get_bulk_contact_operations_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Add or remove tags from multiple contacts.
    
    Manages tags across multiple contacts in bulk operations.
    Requires 'edit_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Create bulk tag operation DTO
        bulk_dto = ContactBulkUpdateDTO(
            business_id=business_id,
            contact_ids=request.contact_ids,
            tags_to_add=request.tags if request.operation == "add" else None
        )
        
        updated_count = await use_case.bulk_update(bulk_dto, current_user["sub"])
        
        operation_text = "added tags to" if request.operation == "add" else "removed tags from"
        return ContactBulkOperationResponse(
            success=True,
            message=f"Successfully {operation_text} {updated_count} contacts",
            updated_count=updated_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{contact_id}/mark-contacted", response_model=ContactResponse)
async def mark_contact_contacted(
    contact_id: uuid.UUID = Path(..., description="Contact ID"),
    current_user: dict = Depends(get_current_user),
    use_case: ContactInteractionUseCase = Depends(get_contact_interaction_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Mark a contact as contacted.
    
    Updates the last contacted timestamp for tracking purposes.
    Requires 'edit_contacts' permission.
    """
    try:
        contact_dto = await use_case.mark_contacted(contact_id, current_user["sub"])
        return _contact_dto_to_response(contact_dto)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/statistics/overview", response_model=ContactStatisticsResponse)
async def get_contact_statistics(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ContactStatisticsUseCase = Depends(get_contact_statistics_use_case),
    _: bool = Depends(require_view_contacts_dep)
):
    """
    Get comprehensive contact statistics.
    
    Returns overview statistics for all contacts in the business.
    Requires 'view_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        stats_dto = await use_case.execute(business_id, current_user["sub"])
        
        return ContactStatisticsResponse(
            total_contacts=stats_dto.total_contacts,
            active_contacts=stats_dto.active_contacts,
            inactive_contacts=stats_dto.inactive_contacts,
            archived_contacts=stats_dto.archived_contacts,
            blocked_contacts=stats_dto.blocked_contacts,
            customers=stats_dto.customers,
            leads=stats_dto.leads,
            prospects=stats_dto.prospects,
            vendors=stats_dto.vendors,
            partners=stats_dto.partners,
            contractors=stats_dto.contractors,
            high_priority=stats_dto.high_priority,
            medium_priority=stats_dto.medium_priority,
            low_priority=stats_dto.low_priority,
            urgent_priority=stats_dto.urgent_priority,
            with_email=stats_dto.with_email,
            with_phone=stats_dto.with_phone,
            assigned_contacts=stats_dto.assigned_contacts,
            unassigned_contacts=stats_dto.unassigned_contacts,
            never_contacted=stats_dto.never_contacted,
            recently_contacted=stats_dto.recently_contacted,
            high_value_contacts=stats_dto.high_value_contacts,
            total_estimated_value=stats_dto.total_estimated_value,
            average_estimated_value=stats_dto.average_estimated_value
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{contact_id}/interactions", response_model=ContactInteractionResponse, status_code=status.HTTP_201_CREATED)
async def add_contact_interaction(
    contact_id: uuid.UUID = Path(..., description="Contact ID"),
    request: ContactInteractionCreateRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    use_case: ContactInteractionUseCase = Depends(get_contact_interaction_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Add an interaction record to a contact.
    
    Records a new interaction (call, email, meeting, etc.) with the contact.
    Requires 'edit_contacts' permission.
    """
    try:
        interaction_data = {
            "type": request.interaction_type.value,
            "description": request.description,
            "outcome": request.outcome,
            "next_action": request.next_action,
            "scheduled_follow_up": request.scheduled_follow_up
        }
        
        interaction_id = await use_case.add_interaction(contact_id, interaction_data, current_user["sub"])
        
        return ContactInteractionResponse(
            id=interaction_id,
            contact_id=contact_id,
            interaction_type=request.interaction_type,
            description=request.description,
            outcome=request.outcome,
            next_action=request.next_action,
            scheduled_follow_up=request.scheduled_follow_up,
            performed_by=current_user["sub"],
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{contact_id}/interactions", response_model=ContactInteractionListResponse)
async def get_contact_interactions(
    contact_id: uuid.UUID = Path(..., description="Contact ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    current_user: dict = Depends(get_current_user),
    use_case: ContactInteractionUseCase = Depends(get_contact_interaction_use_case),
    _: bool = Depends(require_view_contacts_dep)
):
    """
    Get interaction history for a contact.
    
    Retrieves paginated list of all interactions with the contact.
    Requires 'view_contacts' permission.
    """
    try:
        interactions_data = await use_case.get_interactions(contact_id, current_user["sub"], skip, limit)
        
        return ContactInteractionListResponse(
            interactions=interactions_data["interactions"],
            total_count=interactions_data["total"],
            page=(skip // limit) + 1,
            per_page=limit,
            has_next=(skip + limit) < interactions_data["total"],
            has_previous=skip > 0
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{contact_id}/status", response_model=ContactStatusUpdateResponse)
async def update_contact_status(
    contact_id: uuid.UUID = Path(..., description="Contact ID"),
    request: ContactStatusUpdateRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    use_case: ContactStatusManagementUseCase = Depends(get_contact_status_management_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Update contact relationship status and lifecycle stage.
    
    Changes the contact's relationship status and/or lifecycle stage with business logic.
    Requires 'edit_contacts' permission.
    """
    try:
        status_data = {
            "relationship_status": request.relationship_status.value,
            "lifecycle_stage": request.lifecycle_stage.value if request.lifecycle_stage else None,
            "reason": request.reason,
            "notes": request.notes
        }
        
        result = await use_case.update_status(contact_id, status_data, current_user["sub"])
        
        return ContactStatusUpdateResponse(
            contact_id=result["contact_id"],
            old_status=result["old_status"],
            new_status=result["new_status"],
            old_lifecycle_stage=result["old_lifecycle_stage"],
            new_lifecycle_stage=result["new_lifecycle_stage"],
            changed_by=result["changed_by"],
            timestamp=result["timestamp"],
            reason=result["reason"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


def _contact_dto_to_response(contact_dto) -> ContactResponse:
    """Convert ContactResponseDTO to API response model."""
    # Convert address if present
    address_response = None
    if contact_dto.address:
        from ..schemas.contact_schemas import ContactAddressSchema
        address_response = ContactAddressSchema(
            street_address=contact_dto.address.street_address,
            city=contact_dto.address.city,
            state=contact_dto.address.state,
            postal_code=contact_dto.address.postal_code,
            country=contact_dto.address.country
        )
    
    # Convert enum values to schema enums
    from ..schemas.contact_schemas import (
        ContactTypeSchema, ContactStatusSchema, ContactPrioritySchema, 
        ContactSourceSchema, RelationshipStatusSchema, LifecycleStageSchema
    )
    
    return ContactResponse(
        id=contact_dto.id,
        business_id=contact_dto.business_id,
        contact_type=ContactTypeSchema(contact_dto.contact_type.value),
        status=ContactStatusSchema(contact_dto.status.value),
        relationship_status=RelationshipStatusSchema(contact_dto.relationship_status.value),
        lifecycle_stage=LifecycleStageSchema(contact_dto.lifecycle_stage.value),
        first_name=contact_dto.first_name,
        last_name=contact_dto.last_name,
        company_name=contact_dto.company_name,
        job_title=contact_dto.job_title,
        email=contact_dto.email,
        phone=contact_dto.phone,
        mobile_phone=contact_dto.mobile_phone,
        website=contact_dto.website,
        address=address_response,
        priority=ContactPrioritySchema(contact_dto.priority.value),
        source=ContactSourceSchema(contact_dto.source.value) if contact_dto.source else None,
        tags=contact_dto.tags or [],
        notes=contact_dto.notes,
        estimated_value=contact_dto.estimated_value,
        currency=contact_dto.currency or "USD",
        assigned_to=contact_dto.assigned_to,
        created_by=contact_dto.created_by,
        custom_fields=contact_dto.custom_fields or {},
        status_history=[],  # Empty list for now
        interaction_history=[],  # Empty list for now
        created_date=contact_dto.created_date,
        last_modified=contact_dto.last_modified,
        last_contacted=contact_dto.last_contacted,
        display_name=contact_dto.display_name,
        primary_contact_method=contact_dto.primary_contact_method,
        type_display=contact_dto.type_display,
        status_display=contact_dto.status_display,
        priority_display=contact_dto.priority_display,
        source_display=contact_dto.source_display,
        relationship_status_display=contact_dto.relationship_status_display,
        lifecycle_stage_display=contact_dto.lifecycle_stage_display
    ) 