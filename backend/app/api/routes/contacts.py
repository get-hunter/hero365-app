"""
Contact API Routes

REST API endpoints for contact management operations.
"""

import uuid
import logging
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
from ...application.use_cases.contact.manage_contacts import ManageContactsUseCase
from ...application.dto.contact_dto import (
    ContactCreateDTO, ContactUpdateDTO, ContactSearchDTO, ContactBulkUpdateDTO,
    ContactConversionDTO, ContactAssignmentDTO, ContactTagOperationDTO,
    ContactAddressDTO
)
from ...domain.entities.contact import ContactType, ContactStatus, ContactPriority, ContactSource
from ...infrastructure.config.dependency_injection import get_manage_contacts_use_case

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    request: ContactCreateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
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
        
        contact_dto = await use_case.create_contact(create_dto, current_user["sub"])
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
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_view_contacts_dep)
):
    """
    Get a contact by ID.
    
    Retrieves detailed information about a specific contact with optional user data.
    Requires 'view_contacts' permission.
    """
    try:
        contact_dto = await use_case.get_contact(contact_id, current_user["sub"], include_user_details)
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
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
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
        
        contact_dto = await use_case.update_contact(update_dto, current_user["sub"])
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
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_delete_contacts_dep)
):
    """
    Delete a contact.
    
    Permanently deletes a contact and all associated data.
    Requires 'delete_contacts' permission.
    """
    try:
        success = await use_case.delete_contact(contact_id, current_user["sub"])
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
async def list_contacts(
    business_context: dict = Depends(get_business_context),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_user_details: UserDetailLevel = Query(UserDetailLevel.BASIC, description="Level of user detail to include"),
    current_user: dict = Depends(get_current_user),
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_view_contacts_dep)
):
    """
    List contacts for the business.
    
    Retrieves a paginated list of contacts for the current business.
    Requires 'view_contacts' permission.
    """
    user_id = current_user["sub"]
    business_id = uuid.UUID(business_context["business_id"])
    
    # Log user context for debugging
    logger.info(f"📱 ContactsAPI: List contacts request from user {user_id}")
    logger.info(f"🏢 ContactsAPI: Business context: {business_context}")
    logger.info(f"👤 ContactsAPI: User has business memberships: {len(current_user.get('business_memberships', []))}")
    
    # Find current business membership for logging
    business_memberships = current_user.get('business_memberships', [])
    current_membership = None
    for membership in business_memberships:
        if membership.get('business_id') == str(business_id):
            current_membership = membership
            break
    
    if current_membership:
        logger.info(f"🔑 ContactsAPI: Current membership found:")
        logger.info(f"    Role: {current_membership.get('role')}")
        logger.info(f"    Permissions: {current_membership.get('permissions', [])}")
        # Note: The wildcard permission check is now handled correctly in the middleware and entity layer
    else:
        logger.warning(f"⚠️  ContactsAPI: No membership found for business {business_id}")
    
    try:
        contact_list_dto = await use_case.get_business_contacts(
            business_id, current_user["sub"], skip, limit, include_user_details
        )
        
        logger.info(f"📊 ContactsAPI: Returning {len(contact_list_dto.contacts)} contacts (total: {contact_list_dto.total_count})")
        
        return ContactListResponse(
            contacts=[_contact_dto_to_response(contact) for contact in contact_list_dto.contacts],
            total_count=contact_list_dto.total_count,
            page=contact_list_dto.page,
            per_page=contact_list_dto.per_page,
            has_next=contact_list_dto.has_next,
            has_previous=contact_list_dto.has_previous
        )
    except Exception as e:
        logger.error(f"❌ ContactsAPI: Error getting contacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/search", response_model=ContactListResponse)
async def search_contacts(
    request: ContactSearchRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_view_contacts_dep)
):
    """
    Search contacts with advanced filtering.
    
    Performs advanced search and filtering on contacts.
    Requires 'view_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    # Create search DTO
    search_dto = ContactSearchDTO(
        business_id=business_id,
        search_term=request.search_term,
        contact_type=ContactType(request.contact_type.value) if request.contact_type else None,
        status=ContactStatus(request.status.value) if request.status else None,
        priority=ContactPriority(request.priority.value) if request.priority else None,
        source=ContactSource(request.source.value) if request.source else None,
        assigned_to=request.assigned_to,
        tags=request.tags,
        has_email=request.has_email,
        has_phone=request.has_phone,
        min_estimated_value=request.min_estimated_value,
        max_estimated_value=request.max_estimated_value,
        created_after=request.created_after,
        created_before=request.created_before,
        last_contacted_after=request.last_contacted_after,
        last_contacted_before=request.last_contacted_before,
        never_contacted=request.never_contacted,
        skip=request.skip,
        limit=request.limit,
        sort_by=request.sort_by,
        sort_order=request.sort_order,
        include_user_details=request.include_user_details
    )
    
    try:
        contact_list_dto = await use_case.search_contacts(search_dto, current_user["sub"])
        
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
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Perform bulk updates on multiple contacts.
    
    Updates multiple contacts with the same changes.
    Requires 'edit_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    # Create bulk update DTO
    bulk_update_dto = ContactBulkUpdateDTO(
        business_id=business_id,
        contact_ids=request.contact_ids,
        status=ContactStatus(request.status.value) if request.status else None,
        priority=ContactPriority(request.priority.value) if request.priority else None,
        assigned_to=request.assigned_to,
        tags_to_add=request.tags_to_add,
        tags_to_remove=request.tags_to_remove,
        custom_fields=request.custom_fields
    )
    
    try:
        updated_count = await use_case.bulk_update_contacts(bulk_update_dto, current_user["sub"])
        
        return ContactBulkOperationResponse(
            updated_count=updated_count,
            success=True,
            message=f"Successfully updated {updated_count} contacts"
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
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Convert a contact from one type to another.
    
    Changes the contact type (e.g., lead to customer) with business rule validation.
    Requires 'edit_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    # Get current contact to determine from_type
    try:
        current_contact = await use_case.get_contact(contact_id, current_user["sub"])
        
        conversion_dto = ContactConversionDTO(
            contact_id=contact_id,
            business_id=business_id,
            from_type=current_contact.contact_type,
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
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Assign multiple contacts to a user.
    
    Assigns or unassigns multiple contacts to/from a team member.
    Requires 'edit_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    assignment_dto = ContactAssignmentDTO(
        business_id=business_id,
        contact_ids=request.contact_ids,
        assigned_to=request.assigned_to,
        notes=request.notes
    )
    
    try:
        # Use bulk assignment functionality
        bulk_update_dto = ContactBulkUpdateDTO(
            business_id=business_id,
            contact_ids=request.contact_ids,
            assigned_to=request.assigned_to
        )
        
        updated_count = await use_case.bulk_update_contacts(bulk_update_dto, current_user["sub"])
        
        action = "assigned" if request.assigned_to else "unassigned"
        return ContactBulkOperationResponse(
            updated_count=updated_count,
            success=True,
            message=f"Successfully {action} {updated_count} contacts"
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
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Add, remove, or replace tags on multiple contacts.
    
    Performs tag operations on multiple contacts.
    Requires 'edit_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    try:
        # Convert to bulk update based on operation
        bulk_update_dto = ContactBulkUpdateDTO(
            business_id=business_id,
            contact_ids=request.contact_ids
        )
        
        if request.operation == "add":
            bulk_update_dto.tags_to_add = request.tags
        elif request.operation == "remove":
            bulk_update_dto.tags_to_remove = request.tags
        elif request.operation == "replace":
            # For replace, we need to handle this differently
            # This would require a more sophisticated implementation
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Tag replacement not yet implemented"
            )
        
        updated_count = await use_case.bulk_update_contacts(bulk_update_dto, current_user["sub"])
        
        return ContactBulkOperationResponse(
            updated_count=updated_count,
            success=True,
            message=f"Successfully {request.operation}ed tags on {updated_count} contacts"
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
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Mark a contact as contacted.
    
    Updates the last_contacted timestamp for the contact.
    Requires 'edit_contacts' permission.
    """
    try:
        contact_dto = await use_case.mark_contact_contacted(contact_id, current_user["sub"])
        return _contact_dto_to_response(contact_dto)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/statistics/overview", response_model=ContactStatisticsResponse)
async def get_contact_statistics(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_view_contacts_dep)
):
    """
    Get comprehensive contact statistics.
    
    Retrieves detailed statistics about contacts for the business.
    Requires 'view_contacts' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    try:
        stats_dto = await use_case.get_contact_statistics(business_id, current_user["sub"])
        
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
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Add an interaction record to a contact.
    
    Creates a new interaction record for the specified contact.
    Requires 'edit_contacts' permission.
    """
    interaction_data = {
        "type": request.type.value,
        "description": request.description,
        "outcome": request.outcome,
        "next_action": request.next_action,
        "scheduled_follow_up": request.scheduled_follow_up
    }
    
    try:
        interaction_id = await use_case.add_contact_interaction(
            contact_id, interaction_data, current_user["sub"]
        )
        
        # Return the interaction response
        from datetime import datetime
        return ContactInteractionResponse(
            id=interaction_id,
            contact_id=contact_id,
            type=request.type,
            description=request.description,
            timestamp=datetime.utcnow(),
            outcome=request.outcome,
            next_action=request.next_action,
            scheduled_follow_up=request.scheduled_follow_up,
            performed_by=current_user.get("name", "Unknown"),
            performed_by_id=current_user["sub"]
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
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_view_contacts_dep)
):
    """
    Get interaction history for a contact.
    
    Retrieves paginated list of interactions for the specified contact.
    Requires 'view_contacts' permission.
    """
    try:
        result = await use_case.get_contact_interactions(
            contact_id, current_user["sub"], skip, limit
        )
        
        # Convert domain objects to response schemas
        interaction_responses = []
        for interaction in result["interactions"]:
            interaction_responses.append(ContactInteractionResponse(
                id=interaction.id,
                contact_id=contact_id,
                type=interaction.interaction_type.value,
                description=interaction.description,
                timestamp=interaction.timestamp,
                outcome=interaction.outcome,
                next_action=interaction.next_action,
                scheduled_follow_up=interaction.scheduled_follow_up,
                performed_by=interaction.performed_by,
                performed_by_id=interaction.performed_by_id
            ))
        
        return ContactInteractionListResponse(
            interactions=interaction_responses,
            total=result["total"],
            skip=result["skip"],
            limit=result["limit"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{contact_id}/status", response_model=ContactStatusUpdateResponse)
async def update_contact_status(
    contact_id: uuid.UUID = Path(..., description="Contact ID"),
    request: ContactStatusUpdateRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    use_case: ManageContactsUseCase = Depends(get_manage_contacts_use_case),
    _: bool = Depends(require_edit_contacts_dep)
):
    """
    Update contact relationship status and lifecycle stage.
    
    Updates the relationship status and optionally the lifecycle stage for the specified contact.
    Automatically tracks status change history.
    Requires 'edit_contacts' permission.
    """
    status_data = {
        "relationship_status": request.relationship_status.value,
        "lifecycle_stage": request.lifecycle_stage.value if request.lifecycle_stage else None,
        "reason": request.reason,
        "notes": request.notes
    }
    
    try:
        result = await use_case.update_contact_status(
            contact_id, status_data, current_user["sub"]
        )
        
        return ContactStatusUpdateResponse(
            contact_id=result["contact_id"],
            old_status=result["old_status"],
            new_status=result["new_status"],
            old_lifecycle_stage=result["old_lifecycle_stage"],
            new_lifecycle_stage=result["new_lifecycle_stage"],
            changed_by=current_user.get("name", "Unknown"),
            timestamp=result["timestamp"],
            reason=result["reason"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Helper function to convert DTO to response
def _contact_dto_to_response(contact_dto) -> ContactResponse:
    """Convert ContactResponseDTO to ContactResponse schema."""
    # Convert address if present
    address_schema = None
    if contact_dto.address:
        address_schema = {
            "street_address": contact_dto.address.street_address,
            "city": contact_dto.address.city,
            "state": contact_dto.address.state,
            "postal_code": contact_dto.address.postal_code,
            "country": contact_dto.address.country
        }
    
    return ContactResponse(
        id=contact_dto.id,
        business_id=contact_dto.business_id,
        contact_type=contact_dto.contact_type.value,
        status=contact_dto.status.value,
        relationship_status=contact_dto.relationship_status.value if hasattr(contact_dto, 'relationship_status') and contact_dto.relationship_status else "prospect",
        lifecycle_stage=contact_dto.lifecycle_stage.value if hasattr(contact_dto, 'lifecycle_stage') and contact_dto.lifecycle_stage else "awareness",
        first_name=contact_dto.first_name,
        last_name=contact_dto.last_name,
        company_name=contact_dto.company_name,
        job_title=contact_dto.job_title,
        email=contact_dto.email,
        phone=contact_dto.phone,
        mobile_phone=contact_dto.mobile_phone,
        website=contact_dto.website,
        address=address_schema,
        priority=contact_dto.priority.value,
        source=contact_dto.source.value if contact_dto.source else None,
        tags=contact_dto.tags,
        notes=contact_dto.notes,
        estimated_value=contact_dto.estimated_value,
        currency=contact_dto.currency,
        assigned_to=contact_dto.assigned_to,
        created_by=contact_dto.created_by,
        custom_fields=contact_dto.custom_fields,
        status_history=getattr(contact_dto, 'status_history', []),
        interaction_history=getattr(contact_dto, 'interaction_history', []),
        created_date=contact_dto.created_date,
        last_modified=contact_dto.last_modified,
        last_contacted=contact_dto.last_contacted,
        display_name=contact_dto.display_name,
        primary_contact_method=contact_dto.primary_contact_method,
        type_display=contact_dto.type_display,
        status_display=contact_dto.status_display,
        priority_display=contact_dto.priority_display,
        source_display=contact_dto.source_display,
        relationship_status_display=getattr(contact_dto, 'relationship_status_display', contact_dto.relationship_status.value if hasattr(contact_dto, 'relationship_status') and contact_dto.relationship_status else "Prospect"),
        lifecycle_stage_display=getattr(contact_dto, 'lifecycle_stage_display', contact_dto.lifecycle_stage.value if hasattr(contact_dto, 'lifecycle_stage') and contact_dto.lifecycle_stage else "Awareness")
    ) 