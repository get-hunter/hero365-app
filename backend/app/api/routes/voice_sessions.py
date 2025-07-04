"""
Voice Session API Routes

REST API endpoints for voice session management and LiveKit integration.
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
from ..schemas.voice_session_schemas import (
    VoiceSessionCreateRequest, VoiceSessionUpdateRequest, VoiceSessionSearchRequest,
    VoiceSessionResponse, VoiceSessionSummaryResponse, VoiceSessionListResponse,
    VoiceSessionStatisticsResponse, VoiceToolExecutionResponse
)
from ..schemas.activity_schemas import MessageResponse
from ...application.use_cases.voice_agent.start_voice_session_use_case import StartVoiceSessionUseCase
from ...application.use_cases.voice_agent.end_voice_session_use_case import EndVoiceSessionUseCase
from ...application.dto.voice_session_dto import (
    CreateVoiceSessionDTO, UpdateVoiceSessionDTO, VoiceSessionSearchDTO
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, BusinessRuleViolationError
)
from ...infrastructure.config.dependency_injection import (
    get_voice_session_repository, get_start_voice_session_use_case,
    get_end_voice_session_use_case, get_voice_agent_service
)
from ...domain.enums import VoiceSessionStatus, AgentType
from ..converters import EnumConverter

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice-sessions", tags=["voice-sessions"])


def _check_voice_agent_service_availability():
    """Check if voice agent service is available."""
    service = get_voice_agent_service()
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice agent service is not available. LiveKit packages are not installed."
        )
    return service


@router.post("/", response_model=VoiceSessionResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=VoiceSessionResponse, status_code=status.HTTP_201_CREATED, operation_id="create_voice_session_no_slash")
async def create_voice_session(
    request: VoiceSessionCreateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: StartVoiceSessionUseCase = Depends(get_start_voice_session_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Create and start a new voice session.
    
    Creates a new voice session with LiveKit room setup and agent initialization.
    Requires 'edit_projects' permission.
    """
    # Check if voice agent service is available
    _check_voice_agent_service_availability()
    
    business_id = uuid.UUID(business_context["business_id"])
    user_id = current_user["sub"]
    logger.info(f"🎤 VoiceSessionAPI: Starting voice session for business {business_id}, user {user_id}")
    logger.info(f"🎤 VoiceSessionAPI: Request data: agent_type={request.agent_type}")
    
    try:
        # Create DTO
        create_dto = CreateVoiceSessionDTO(
            business_id=business_id,
            user_id=user_id,
            agent_type=EnumConverter.safe_agent_type(request.agent_type) if request.agent_type else AgentType.PERSONAL_ASSISTANT,
            session_timeout_minutes=request.session_timeout_minutes,
            voice_enabled=request.voice_enabled,
            background_mode=request.background_mode,
            emergency_mode=request.emergency_mode,
            custom_settings=request.custom_settings or {},
            current_location=request.current_location,
            current_job_id=request.current_job_id,
            current_contact_id=request.current_contact_id,
            current_project_id=request.current_project_id,
            session_metadata=request.session_metadata or {}
        )
        
        logger.info(f"🎤 VoiceSessionAPI: DTO created successfully, calling use case")
        
        session_dto = await use_case.execute(create_dto, user_id, business_id)
        logger.info(f"🎤 VoiceSessionAPI: Use case completed successfully")
        
        return _voice_session_dto_to_response(session_dto)
        
    except ValidationError as e:
        logger.error(f"❌ VoiceSessionAPI: Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionDeniedError as e:
        logger.error(f"❌ VoiceSessionAPI: Permission denied: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BusinessRuleViolationError as e:
        logger.error(f"❌ VoiceSessionAPI: Business rule violation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ VoiceSessionAPI: Error creating voice session: {str(e)}")
        logger.error(f"❌ VoiceSessionAPI: Error type: {type(e)}")
        import traceback
        logger.error(f"❌ VoiceSessionAPI: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{session_id}", response_model=VoiceSessionResponse)
async def get_voice_session(
    session_id: uuid.UUID = Path(..., description="Voice Session ID"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    voice_session_repository = Depends(get_voice_session_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get a voice session by ID.
    
    Retrieves detailed information about a specific voice session.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🎤 VoiceSessionAPI: Getting voice session {session_id} for business {business_id}")
    
    try:
        session = await voice_session_repository.get_by_id(business_id, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice session with ID {session_id} not found"
            )
        
        from ...application.dto.voice_session_dto import VoiceSessionResponseDTO
        session_dto = VoiceSessionResponseDTO.from_entity(session)
        return _voice_session_dto_to_response(session_dto)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ VoiceSessionAPI: Error getting voice session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{session_id}", response_model=VoiceSessionResponse)
async def update_voice_session(
    session_id: uuid.UUID = Path(..., description="Voice Session ID"),
    request: VoiceSessionUpdateRequest = Body(...),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    voice_session_repository = Depends(get_voice_session_repository),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Update a voice session.
    
    Updates an existing voice session with the provided information.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🎤 VoiceSessionAPI: Updating voice session {session_id} for business {business_id}")
    
    try:
        # Get existing session
        session = await voice_session_repository.get_by_id(business_id, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice session with ID {session_id} not found"
            )
        
        # Create update DTO
        update_dto = UpdateVoiceSessionDTO(
            status=EnumConverter.safe_voice_session_status(request.status) if request.status else None,
            session_timeout_minutes=request.session_timeout_minutes,
            voice_enabled=request.voice_enabled,
            background_mode=request.background_mode,
            emergency_mode=request.emergency_mode,
            session_notes=request.session_notes,
            custom_settings=request.custom_settings,
            current_location=request.current_location,
            current_job_id=request.current_job_id,
            current_contact_id=request.current_contact_id,
            current_project_id=request.current_project_id,
            session_metadata=request.session_metadata,
            conversation_state=request.conversation_state
        )
        
        # Update session
        updated_session = await voice_session_repository.update(business_id, session_id, update_dto)
        
        from ...application.dto.voice_session_dto import VoiceSessionResponseDTO
        session_dto = VoiceSessionResponseDTO.from_entity(updated_session)
        return _voice_session_dto_to_response(session_dto)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ VoiceSessionAPI: Error updating voice session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{session_id}", response_model=MessageResponse)
async def delete_voice_session(
    session_id: uuid.UUID = Path(..., description="Voice Session ID"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: EndVoiceSessionUseCase = Depends(get_end_voice_session_use_case),
    _: bool = Depends(require_delete_projects_dep)
):
    """
    End and delete a voice session.
    
    Properly terminates a voice session, cleans up LiveKit resources, and deletes the session.
    Requires 'delete_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    user_id = current_user["sub"]
    logger.info(f"🎤 VoiceSessionAPI: Ending voice session {session_id} for business {business_id}")
    
    try:
        await use_case.execute(session_id, user_id, business_id)
        return MessageResponse(message="Voice session ended successfully")
        
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"❌ VoiceSessionAPI: Error ending voice session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/", response_model=VoiceSessionListResponse)
@router.get("", response_model=VoiceSessionListResponse, operation_id="list_voice_sessions_no_slash")
async def list_voice_sessions(
    business_context: dict = Depends(get_business_context),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by session status"),
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    emergency_mode: Optional[bool] = Query(None, description="Filter by emergency mode"),
    current_user: dict = Depends(get_current_user),
    voice_session_repository = Depends(get_voice_session_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    List voice sessions.
    
    Retrieves a paginated list of voice sessions with optional filtering.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🎤 VoiceSessionAPI: Listing voice sessions for business {business_id}")
    
    try:
        # Create search criteria
        search_criteria = VoiceSessionSearchDTO(
            business_id=business_id,
            user_id=user_id,
            agent_type=EnumConverter.safe_agent_type(agent_type) if agent_type else None,
            status=EnumConverter.safe_voice_session_status(status) if status else None,
            emergency_mode=emergency_mode,
            limit=limit,
            offset=skip
        )
        
        sessions, total_count = await voice_session_repository.search(search_criteria)
        
        from ...application.dto.voice_session_dto import VoiceSessionListDTO
        session_list_dto = VoiceSessionListDTO.from_entities(
            sessions, total_count, skip // limit + 1, limit
        )
        
        return _voice_session_list_dto_to_response(session_list_dto)
        
    except Exception as e:
        logger.error(f"❌ VoiceSessionAPI: Error listing voice sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/search", response_model=VoiceSessionListResponse)
async def search_voice_sessions(
    request: VoiceSessionSearchRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    voice_session_repository = Depends(get_voice_session_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Search voice sessions with advanced criteria.
    
    Performs advanced search on voice sessions with multiple filtering options.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🎤 VoiceSessionAPI: Searching voice sessions for business {business_id}")
    
    try:
        # Create search criteria
        search_criteria = VoiceSessionSearchDTO(
            business_id=business_id,
            user_id=request.user_id,
            agent_type=EnumConverter.safe_agent_type(request.agent_type) if request.agent_type else None,
            status=EnumConverter.safe_voice_session_status(request.status) if request.status else None,
            start_date=request.start_date,
            end_date=request.end_date,
            emergency_mode=request.emergency_mode,
            has_errors=request.has_errors,
            min_duration_minutes=request.min_duration_minutes,
            max_duration_minutes=request.max_duration_minutes,
            min_interactions=request.min_interactions,
            tools_used=request.tools_used,
            limit=request.limit,
            offset=request.offset,
            sort_by=request.sort_by,
            sort_order=request.sort_order
        )
        
        sessions, total_count = await voice_session_repository.search(search_criteria)
        
        from ...application.dto.voice_session_dto import VoiceSessionListDTO
        session_list_dto = VoiceSessionListDTO.from_entities(
            sessions, total_count, request.offset // request.limit + 1, request.limit
        )
        
        return _voice_session_list_dto_to_response(session_list_dto)
        
    except Exception as e:
        logger.error(f"❌ VoiceSessionAPI: Error searching voice sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )





@router.get("/statistics/summary", response_model=VoiceSessionStatisticsResponse)
async def get_voice_session_statistics(
    business_context: dict = Depends(get_business_context),
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    current_user: dict = Depends(get_current_user),
    voice_session_repository = Depends(get_voice_session_repository),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get voice session statistics.
    
    Retrieves comprehensive analytics and statistics for voice sessions.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🎤 VoiceSessionAPI: Getting voice session statistics for business {business_id}")
    
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            from datetime import timedelta
            start_date = end_date - timedelta(days=30)
        
        statistics = await voice_session_repository.get_session_statistics(
            business_id, start_date, end_date
        )
        
        return _voice_session_statistics_dto_to_response(statistics)
        
    except Exception as e:
        logger.error(f"❌ VoiceSessionAPI: Error getting voice session statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Helper functions for DTO to response conversion

def _voice_session_dto_to_response(session_dto) -> VoiceSessionResponse:
    """Convert VoiceSessionResponseDTO to API response schema."""
    return VoiceSessionResponse(
        id=session_dto.id,
        business_id=session_dto.business_id,
        user_id=session_dto.user_id,
        agent_type=session_dto.agent_type.value,
        status=session_dto.status.value,
        livekit_room_name=session_dto.livekit_room_name,
        livekit_room_token=session_dto.livekit_room_token,
        session_timeout_minutes=session_dto.session_timeout_minutes,
        started_at=session_dto.started_at,
        ended_at=session_dto.ended_at,
        last_activity=session_dto.last_activity,
        context=session_dto.context.__dict__ if session_dto.context else None,
        analytics=session_dto.analytics.__dict__ if session_dto.analytics else None,
        conversation_transcript=session_dto.conversation_transcript,
        audio_recording_url=session_dto.audio_recording_url,
        voice_enabled=session_dto.voice_enabled,
        background_mode=session_dto.background_mode,
        emergency_mode=session_dto.emergency_mode,
        session_notes=session_dto.session_notes,
        error_log=session_dto.error_log,
        custom_settings=session_dto.custom_settings
    )


def _voice_session_list_dto_to_response(list_dto) -> VoiceSessionListResponse:
    """Convert VoiceSessionListDTO to API response schema."""
    return VoiceSessionListResponse(
        sessions=[
            VoiceSessionSummaryResponse(
                id=session.id,
                user_id=session.user_id,
                agent_type=session.agent_type.value,
                status=session.status.value,
                started_at=session.started_at,
                ended_at=session.ended_at,
                duration_minutes=session.duration_minutes,
                total_interactions=session.total_interactions,
                success_rate=session.success_rate,
                is_emergency=session.is_emergency
            )
            for session in list_dto.sessions
        ],
        total_count=list_dto.total_count,
        page=list_dto.page,
        limit=list_dto.limit,
        has_next=list_dto.has_next,
        has_previous=list_dto.has_previous,
        active_sessions_count=list_dto.active_sessions_count,
        total_duration_minutes=list_dto.total_duration_minutes,
        average_success_rate=list_dto.average_success_rate
    )





def _voice_session_statistics_dto_to_response(stats_dto) -> VoiceSessionStatisticsResponse:
    """Convert VoiceSessionStatisticsDTO to API response schema."""
    return VoiceSessionStatisticsResponse(
        business_id=stats_dto.business_id,
        date_range_start=stats_dto.date_range_start,
        date_range_end=stats_dto.date_range_end,
        total_sessions=stats_dto.total_sessions,
        active_sessions=stats_dto.active_sessions,
        completed_sessions=stats_dto.completed_sessions,
        failed_sessions=stats_dto.failed_sessions,
        emergency_sessions=stats_dto.emergency_sessions,
        total_duration_minutes=stats_dto.total_duration_minutes,
        average_duration_minutes=stats_dto.average_duration_minutes,
        median_duration_minutes=stats_dto.median_duration_minutes,
        total_interactions=stats_dto.total_interactions,
        total_successful_actions=stats_dto.total_successful_actions,
        total_failed_actions=stats_dto.total_failed_actions,
        overall_success_rate=stats_dto.overall_success_rate,
        agent_type_breakdown=stats_dto.agent_type_breakdown,
        top_tools_used=stats_dto.top_tools_used,
        average_response_time_ms=stats_dto.average_response_time_ms,
        user_satisfaction_score=stats_dto.user_satisfaction_score
    ) 