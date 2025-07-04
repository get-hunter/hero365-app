"""
Outbound Call API Routes

REST API endpoints for outbound call management and campaign operations.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body

from ..deps import get_current_user, get_business_context
from ..middleware.permissions import (
    require_view_projects_dep, require_edit_projects_dep, require_delete_projects_dep
)
from ..schemas.outbound_call_schemas import (
    OutboundCallCreateRequest, OutboundCallUpdateRequest, OutboundCallSearchRequest,
    OutboundCallResponse, OutboundCallSummaryResponse, OutboundCallListResponse,
    OutboundCallStatisticsResponse, MobileOutboundCallResponse, OutboundCallActionResponse,
    OutboundCallRecipientSchema, OutboundCallScriptSchema
)
from ..schemas.activity_schemas import MessageResponse
from ...application.use_cases.voice_agent.schedule_outbound_call_use_case import ScheduleOutboundCallUseCase
from ...application.use_cases.voice_agent.campaign_management_use_case import CampaignManagementUseCase
from ...application.dto.outbound_call_dto import (
    CreateOutboundCallDTO, UpdateOutboundCallDTO, OutboundCallSearchDTO,
    OutboundCallRecipientDTO, OutboundCallScriptDTO
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, BusinessRuleViolationError
)
from ...infrastructure.config.dependency_injection import (
    get_outbound_call_repository, get_schedule_outbound_call_use_case,
    get_campaign_management_use_case, get_voice_agent_service
)
from ...domain.enums import CallStatus, CallOutcome, AgentType, CampaignType, CampaignStatus
from ..converters import EnumConverter

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/outbound-calls", tags=["outbound-calls"])


def _check_voice_agent_service_availability():
    """Check if voice agent service is available."""
    service = get_voice_agent_service()
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice agent service is not available. LiveKit packages are not installed."
        )
    return service


@router.post("/", response_model=OutboundCallResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=OutboundCallResponse, status_code=status.HTTP_201_CREATED, operation_id="create_outbound_call_no_slash")
async def create_outbound_call(
    request: OutboundCallCreateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ScheduleOutboundCallUseCase = Depends(get_schedule_outbound_call_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Schedule a new outbound call.
    
    Creates and schedules a new outbound call with campaign context.
    Requires 'edit_projects' permission.
    """
    # Check if voice agent service is available
    _check_voice_agent_service_availability()
    
    business_id = uuid.UUID(business_context["business_id"])
    user_id = current_user["sub"]
    logger.info(f"📞 OutboundCallAPI: Scheduling outbound call for business {business_id}")
    logger.info(f"📞 OutboundCallAPI: Request data: contact={request.recipient.contact_name}")
    
    try:
        # Create recipient DTO
        recipient_dto = OutboundCallRecipientDTO(
            contact_id=request.recipient.contact_id,
            contact_name=request.recipient.contact_name,
            phone_number=request.recipient.phone_number,
            email=request.recipient.email,
            preferred_call_time=request.recipient.preferred_call_time,
            timezone=request.recipient.timezone,
            language_preference=request.recipient.language_preference,
            customer_segment=request.recipient.customer_segment,
            previous_interactions=request.recipient.previous_interactions,
            last_contact_date=request.recipient.last_contact_date,
            do_not_call=request.recipient.do_not_call,
            campaign_data=request.recipient.campaign_data or {},
            personalization_data=request.recipient.personalization_data or {}
        )
        
        # Create script DTO
        script_dto = OutboundCallScriptDTO(
            opening_message=request.script.opening_message,
            main_talking_points=request.script.main_talking_points,
            objection_handling=request.script.objection_handling,
            closing_message=request.script.closing_message,
            call_to_action=request.script.call_to_action,
            fallback_options=request.script.fallback_options,
            max_call_duration_minutes=request.script.max_call_duration_minutes,
            allow_interruptions=request.script.allow_interruptions,
            personalization_tokens=request.script.personalization_tokens or [],
            voice_tone=request.script.voice_tone,
            speaking_rate=request.script.speaking_rate,
            pause_duration_ms=request.script.pause_duration_ms
        )
        
        # Create outbound call DTO
        create_dto = CreateOutboundCallDTO(
            business_id=business_id,
            recipient=recipient_dto,
            script=script_dto,
            campaign_id=request.campaign_id,
            agent_type=EnumConverter.safe_agent_type(request.agent_type, AgentType.OUTBOUND_CALLER),
            priority=request.priority,
            scheduled_for=request.scheduled_for,
            custom_settings=request.custom_settings or {},
            campaign_goal=request.campaign_goal,
            campaign_context=request.campaign_context or {},
            max_retry_attempts=request.max_retry_attempts,
            retry_delay_minutes=request.retry_delay_minutes,
            voice_enabled=request.voice_enabled,
            background_mode=request.background_mode
        )
        
        logger.info(f"📞 OutboundCallAPI: DTO created successfully, calling use case")
        
        call_dto = await use_case.execute(create_dto, user_id, business_id)
        logger.info(f"📞 OutboundCallAPI: Use case completed successfully")
        
        return _outbound_call_dto_to_response(call_dto)
        
    except ValidationError as e:
        logger.error(f"❌ OutboundCallAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionDeniedError as e:
        logger.error(f"❌ OutboundCallAPI: Permission denied: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BusinessRuleViolationError as e:
        logger.error(f"❌ OutboundCallAPI: Business rule violation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ OutboundCallAPI: Error creating outbound call: {str(e)}")
        logger.error(f"❌ OutboundCallAPI: Error type: {type(e)}")
        import traceback
        logger.error(f"❌ OutboundCallAPI: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{call_id}", response_model=OutboundCallResponse)
async def get_outbound_call(
    call_id: uuid.UUID = Path(..., description="Outbound Call ID"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    outbound_call_repository = Depends(get_outbound_call_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get an outbound call by ID.
    
    Retrieves detailed information about a specific outbound call.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"📞 OutboundCallAPI: Getting outbound call {call_id} for business {business_id}")
    
    try:
        call = await outbound_call_repository.get_by_id(business_id, call_id)
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outbound call with ID {call_id} not found"
            )
        
        from ...application.dto.outbound_call_dto import OutboundCallResponseDTO
        call_dto = OutboundCallResponseDTO.from_entity(call)
        return _outbound_call_dto_to_response(call_dto)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ OutboundCallAPI: Error getting outbound call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{call_id}", response_model=OutboundCallResponse)
async def update_outbound_call(
    call_id: uuid.UUID = Path(..., description="Outbound Call ID"),
    request: OutboundCallUpdateRequest = Body(...),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    outbound_call_repository = Depends(get_outbound_call_repository),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Update an outbound call.
    
    Updates an existing outbound call with the provided information.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"📞 OutboundCallAPI: Updating outbound call {call_id} for business {business_id}")
    
    try:
        # Get existing call
        call = await outbound_call_repository.get_by_id(business_id, call_id)
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outbound call with ID {call_id} not found"
            )
        
        # Create update DTO
        update_dto = UpdateOutboundCallDTO(
            status=EnumConverter.safe_call_status(request.status, None) if request.status else None,
            priority=request.priority,
            scheduled_for=request.scheduled_for,
            attempted_at=request.attempted_at,
            completed_at=request.completed_at,
            retry_count=request.retry_count,
            next_retry_at=request.next_retry_at,
            result=request.result,
            voice_session_id=request.voice_session_id,
            campaign_context=request.campaign_context,
            custom_settings=request.custom_settings
        )
        
        # Update call
        updated_call = await outbound_call_repository.update(business_id, call_id, update_dto)
        
        from ...application.dto.outbound_call_dto import OutboundCallResponseDTO
        call_dto = OutboundCallResponseDTO.from_entity(updated_call)
        return _outbound_call_dto_to_response(call_dto)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ OutboundCallAPI: Error updating outbound call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{call_id}", response_model=MessageResponse)
async def delete_outbound_call(
    call_id: uuid.UUID = Path(..., description="Outbound Call ID"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    outbound_call_repository = Depends(get_outbound_call_repository),
    _: bool = Depends(require_delete_projects_dep)
):
    """
    Delete an outbound call.
    
    Cancels and deletes an outbound call. Cannot delete calls that are in progress.
    Requires 'delete_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"📞 OutboundCallAPI: Deleting outbound call {call_id} for business {business_id}")
    
    try:
        # Get existing call
        call = await outbound_call_repository.get_by_id(business_id, call_id)
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outbound call with ID {call_id} not found"
            )
        
        # Check if call can be deleted
        if call.status in [CallStatus.IN_PROGRESS, CallStatus.CONNECTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete calls that are in progress"
            )
        
        await outbound_call_repository.delete(business_id, call_id)
        return MessageResponse(message="Outbound call deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ OutboundCallAPI: Error deleting outbound call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/", response_model=OutboundCallListResponse)
@router.get("", response_model=OutboundCallListResponse, operation_id="list_outbound_calls_no_slash")
async def list_outbound_calls(
    business_context: dict = Depends(get_business_context),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by call status"),
    campaign_id: Optional[uuid.UUID] = Query(None, description="Filter by campaign ID"),
    outcome: Optional[str] = Query(None, description="Filter by call outcome"),
    scheduled_start: Optional[datetime] = Query(None, description="Filter by scheduled start date"),
    scheduled_end: Optional[datetime] = Query(None, description="Filter by scheduled end date"),
    current_user: dict = Depends(get_current_user),
    outbound_call_repository = Depends(get_outbound_call_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    List outbound calls.
    
    Retrieves a paginated list of outbound calls with optional filtering.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"📞 OutboundCallAPI: Listing outbound calls for business {business_id}")
    
    try:
        # Create search criteria
        search_criteria = OutboundCallSearchDTO(
            business_id=business_id,
            campaign_id=campaign_id,
            status=EnumConverter.safe_call_status(status, None) if status else None,
            outcome=EnumConverter.safe_call_outcome(outcome, None) if outcome else None,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            limit=limit,
            offset=skip
        )
        
        calls, total_count = await outbound_call_repository.search(search_criteria)
        
        from ...application.dto.outbound_call_dto import OutboundCallListDTO
        call_list_dto = OutboundCallListDTO.from_entities(
            calls, total_count, skip // limit + 1, limit
        )
        
        return _outbound_call_list_dto_to_response(call_list_dto)
        
    except Exception as e:
        logger.error(f"❌ OutboundCallAPI: Error listing outbound calls: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/search", response_model=OutboundCallListResponse)
async def search_outbound_calls(
    request: OutboundCallSearchRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    outbound_call_repository = Depends(get_outbound_call_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Search outbound calls with advanced criteria.
    
    Performs advanced search on outbound calls with multiple filtering options.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"📞 OutboundCallAPI: Searching outbound calls for business {business_id}")
    
    try:
        # Create search criteria
        search_criteria = OutboundCallSearchDTO(
            business_id=business_id,
            campaign_id=request.campaign_id,
            status=EnumConverter.safe_call_status(request.status, None) if request.status else None,
            outcome=EnumConverter.safe_call_outcome(request.outcome, None) if request.outcome else None,
            priority=request.priority,
            scheduled_start=request.scheduled_start,
            scheduled_end=request.scheduled_end,
            attempted_start=request.attempted_start,
            attempted_end=request.attempted_end,
            contact_name=request.contact_name,
            phone_number=request.phone_number,
            appointment_scheduled=request.appointment_scheduled,
            follow_up_required=request.follow_up_required,
            min_duration_minutes=request.min_duration_minutes,
            max_duration_minutes=request.max_duration_minutes,
            limit=request.limit,
            offset=request.offset,
            sort_by=request.sort_by,
            sort_order=request.sort_order
        )
        
        calls, total_count = await outbound_call_repository.search(search_criteria)
        
        from ...application.dto.outbound_call_dto import OutboundCallListDTO
        call_list_dto = OutboundCallListDTO.from_entities(
            calls, total_count, request.offset // request.limit + 1, request.limit
        )
        
        return _outbound_call_list_dto_to_response(call_list_dto)
        
    except Exception as e:
        logger.error(f"❌ OutboundCallAPI: Error searching outbound calls: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{call_id}/start", response_model=OutboundCallActionResponse)
async def start_outbound_call(
    call_id: uuid.UUID = Path(..., description="Outbound Call ID"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    outbound_call_repository = Depends(get_outbound_call_repository),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Start an outbound call immediately.
    
    Initiates an outbound call by updating its status and scheduling.
    Requires 'edit_projects' permission.
    """
    # Check if voice agent service is available
    _check_voice_agent_service_availability()
    
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"📞 OutboundCallAPI: Starting outbound call {call_id}")
    
    try:
        # Update call status to in progress
        update_dto = UpdateOutboundCallDTO(
            status=CallStatus.IN_PROGRESS,
            attempted_at=datetime.utcnow()
        )
        
        updated_call = await outbound_call_repository.update(business_id, call_id, update_dto)
        
        return OutboundCallActionResponse(
            success=True,
            message="Outbound call started successfully",
            call_id=call_id
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"❌ OutboundCallAPI: Error starting outbound call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{call_id}/complete", response_model=OutboundCallActionResponse)
async def complete_outbound_call(
    call_id: uuid.UUID = Path(..., description="Outbound Call ID"),
    outcome: str = Body(..., description="Call outcome"),
    outcome_details: str = Body(..., description="Outcome details"),
    call_duration_seconds: int = Body(..., description="Call duration in seconds"),
    customer_response: str = Body(..., description="Customer response"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    outbound_call_repository = Depends(get_outbound_call_repository),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Complete an outbound call with results.
    
    Marks an outbound call as completed and records the outcome.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"📞 OutboundCallAPI: Completing outbound call {call_id}")
    
    try:
        from ...application.dto.outbound_call_dto import OutboundCallResultDTO
        
        # Create result DTO
        result_dto = OutboundCallResultDTO(
            call_connected=True,
            call_duration_seconds=call_duration_seconds,
            outcome=EnumConverter.safe_call_outcome(outcome, CallOutcome.OTHER),
            outcome_details=outcome_details,
            customer_response=customer_response
        )
        
        # Update call with completion data
        update_dto = UpdateOutboundCallDTO(
            status=CallStatus.COMPLETED,
            completed_at=datetime.utcnow(),
            result=result_dto
        )
        
        updated_call = await outbound_call_repository.update(business_id, call_id, update_dto)
        
        return OutboundCallActionResponse(
            success=True,
            message="Outbound call completed successfully",
            call_id=call_id
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"❌ OutboundCallAPI: Error completing outbound call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{call_id}/mobile", response_model=MobileOutboundCallResponse)
async def get_mobile_outbound_call(
    call_id: uuid.UUID = Path(..., description="Outbound Call ID"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    outbound_call_repository = Depends(get_outbound_call_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get mobile-optimized outbound call data.
    
    Retrieves outbound call information optimized for mobile app consumption.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"📞 OutboundCallAPI: Getting mobile outbound call {call_id}")
    
    try:
        call = await outbound_call_repository.get_by_id(business_id, call_id)
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outbound call with ID {call_id} not found"
            )
        
        # Get campaign name for mobile optimization
        campaign_name = None
        if call.campaign_id:
            campaign_name = await outbound_call_repository.get_campaign_name(business_id, call.campaign_id)
        
        from ...application.dto.outbound_call_dto import MobileOutboundCallDTO
        mobile_dto = MobileOutboundCallDTO.from_entity(call, campaign_name)
        
        return _mobile_outbound_call_dto_to_response(mobile_dto)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ OutboundCallAPI: Error getting mobile outbound call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/statistics/summary", response_model=OutboundCallStatisticsResponse)
async def get_outbound_call_statistics(
    business_context: dict = Depends(get_business_context),
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    current_user: dict = Depends(get_current_user),
    outbound_call_repository = Depends(get_outbound_call_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get outbound call statistics.
    
    Retrieves comprehensive analytics and statistics for outbound calls.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"📞 OutboundCallAPI: Getting outbound call statistics for business {business_id}")
    
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            from datetime import timedelta
            start_date = end_date - timedelta(days=30)
        
        statistics = await outbound_call_repository.get_call_statistics(
            business_id, start_date, end_date
        )
        
        return _outbound_call_statistics_dto_to_response(statistics)
        
    except Exception as e:
        logger.error(f"❌ OutboundCallAPI: Error getting outbound call statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/campaigns", response_model=OutboundCallActionResponse)
async def create_campaign(
    name: str = Body(..., description="Campaign name"),
    campaign_type: str = Body(..., description="Campaign type"),
    description: Optional[str] = Body(None, description="Campaign description"),
    start_date: datetime = Body(..., description="Campaign start date"),
    end_date: Optional[datetime] = Body(None, description="Campaign end date"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: CampaignManagementUseCase = Depends(get_campaign_management_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Create a new outbound call campaign.
    
    Creates a new campaign for organizing outbound calls.
    Requires 'edit_projects' permission.
    """
    # Check if voice agent service is available
    _check_voice_agent_service_availability()
    
    business_id = uuid.UUID(business_context["business_id"])
    user_id = current_user["sub"]
    logger.info(f"📞 OutboundCallAPI: Creating campaign for business {business_id}")
    
    try:
        campaign_id = await use_case.create_campaign(
            business_id=business_id,
            user_id=user_id,
            name=name,
            campaign_type=EnumConverter.safe_campaign_type(campaign_type, CampaignType.LEAD_GENERATION),
            description=description,
            start_date=start_date,
            end_date=end_date
        )
        
        return OutboundCallActionResponse(
            success=True,
            message="Campaign created successfully",
            campaign_id=campaign_id
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ OutboundCallAPI: Error creating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Helper functions for DTO to response conversion

def _outbound_call_dto_to_response(call_dto) -> OutboundCallResponse:
    """Convert OutboundCallResponseDTO to API response schema."""
    return OutboundCallResponse(
        id=call_dto.id,
        business_id=call_dto.business_id,
        campaign_id=call_dto.campaign_id,
        agent_type=call_dto.agent_type.value,
        status=call_dto.status.value,
        priority=call_dto.priority,
        scheduled_for=call_dto.scheduled_for,
        attempted_at=call_dto.attempted_at,
        completed_at=call_dto.completed_at,
        retry_count=call_dto.retry_count,
        next_retry_at=call_dto.next_retry_at,
        recipient=OutboundCallRecipientSchema(
            contact_id=call_dto.recipient.contact_id,
            contact_name=call_dto.recipient.contact_name,
            phone_number=call_dto.recipient.phone_number,
            email=call_dto.recipient.email,
            preferred_call_time=call_dto.recipient.preferred_call_time,
            timezone=call_dto.recipient.timezone,
            language_preference=call_dto.recipient.language_preference,
            customer_segment=call_dto.recipient.customer_segment,
            previous_interactions=call_dto.recipient.previous_interactions,
            last_contact_date=call_dto.recipient.last_contact_date,
            do_not_call=call_dto.recipient.do_not_call,
            campaign_data=call_dto.recipient.campaign_data,
            personalization_data=call_dto.recipient.personalization_data
        ),
        script=OutboundCallScriptSchema(
            opening_message=call_dto.script.opening_message,
            main_talking_points=call_dto.script.main_talking_points,
            objection_handling=call_dto.script.objection_handling,
            closing_message=call_dto.script.closing_message,
            call_to_action=call_dto.script.call_to_action,
            fallback_options=call_dto.script.fallback_options,
            max_call_duration_minutes=call_dto.script.max_call_duration_minutes,
            allow_interruptions=call_dto.script.allow_interruptions,
            personalization_tokens=call_dto.script.personalization_tokens,
            voice_tone=call_dto.script.voice_tone,
            speaking_rate=call_dto.script.speaking_rate,
            pause_duration_ms=call_dto.script.pause_duration_ms
        ),
        result=call_dto.result.__dict__ if call_dto.result else None,
        voice_session_id=call_dto.voice_session_id,
        campaign_goal=call_dto.campaign_goal,
        campaign_context=call_dto.campaign_context,
        max_retry_attempts=call_dto.max_retry_attempts,
        retry_delay_minutes=call_dto.retry_delay_minutes,
        custom_settings=call_dto.custom_settings,
        created_by=call_dto.created_by,
        created_date=call_dto.created_date,
        last_modified=call_dto.last_modified
    )


def _outbound_call_list_dto_to_response(list_dto) -> OutboundCallListResponse:
    """Convert OutboundCallListDTO to API response schema."""
    return OutboundCallListResponse(
        calls=[
            OutboundCallSummaryResponse(
                id=call.id,
                contact_name=call.contact_name,
                phone_number=call.phone_number,
                campaign_id=call.campaign_id,
                status=call.status.value,
                priority=call.priority,
                scheduled_for=call.scheduled_for,
                attempted_at=call.attempted_at,
                completed_at=call.completed_at,
                outcome=call.outcome.value if call.outcome else None,
                call_duration_minutes=call.call_duration_minutes,
                retry_count=call.retry_count,
                appointment_scheduled=call.appointment_scheduled,
                follow_up_required=call.follow_up_required
            )
            for call in list_dto.calls
        ],
        total_count=list_dto.total_count,
        page=list_dto.page,
        limit=list_dto.limit,
        has_next=list_dto.has_next,
        has_previous=list_dto.has_previous,
        pending_calls_count=list_dto.pending_calls_count,
        completed_calls_count=list_dto.completed_calls_count,
        successful_calls_count=list_dto.successful_calls_count,
        total_duration_minutes=list_dto.total_duration_minutes,
        average_success_rate=list_dto.average_success_rate
    )


def _mobile_outbound_call_dto_to_response(mobile_dto) -> MobileOutboundCallResponse:
    """Convert MobileOutboundCallDTO to API response schema."""
    return MobileOutboundCallResponse(
        id=mobile_dto.id,
        contact_name=mobile_dto.contact_name,
        phone_number=mobile_dto.phone_number,
        status=mobile_dto.status.value,
        priority=mobile_dto.priority,
        scheduled_for=mobile_dto.scheduled_for,
        duration_minutes=mobile_dto.duration_minutes,
        outcome=mobile_dto.outcome.value if mobile_dto.outcome else None,
        campaign_name=mobile_dto.campaign_name,
        appointment_scheduled=mobile_dto.appointment_scheduled,
        follow_up_required=mobile_dto.follow_up_required,
        next_retry_at=mobile_dto.next_retry_at
    )


def _outbound_call_statistics_dto_to_response(stats_dto) -> OutboundCallStatisticsResponse:
    """Convert OutboundCallStatisticsDTO to API response schema."""
    return OutboundCallStatisticsResponse(
        business_id=stats_dto.business_id,
        date_range_start=stats_dto.date_range_start,
        date_range_end=stats_dto.date_range_end,
        total_calls=stats_dto.total_calls,
        pending_calls=stats_dto.pending_calls,
        completed_calls=stats_dto.completed_calls,
        failed_calls=stats_dto.failed_calls,
        successful_calls=stats_dto.successful_calls,
        appointments_scheduled=stats_dto.appointments_scheduled,
        callbacks_requested=stats_dto.callbacks_requested,
        overall_success_rate=stats_dto.overall_success_rate,
        total_duration_minutes=stats_dto.total_duration_minutes,
        average_duration_minutes=stats_dto.average_duration_minutes,
        median_duration_minutes=stats_dto.median_duration_minutes,
        outcome_breakdown=stats_dto.outcome_breakdown,
        campaign_performance=stats_dto.campaign_performance,
        peak_calling_hours=stats_dto.peak_calling_hours,
        daily_performance=stats_dto.daily_performance
    ) 