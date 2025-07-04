"""
Voice Session Data Transfer Objects

DTOs for voice session management operations following clean architecture principles.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass

from app.domain.enums import VoiceSessionStatus, AgentType


@dataclass
class VoiceSessionContextDTO:
    """DTO for voice session context information."""
    current_location: Optional[str] = None
    current_job_id: Optional[uuid.UUID] = None
    current_contact_id: Optional[uuid.UUID] = None
    current_project_id: Optional[uuid.UUID] = None
    session_metadata: Dict[str, Any] = None
    conversation_state: Dict[str, Any] = None

    def __post_init__(self):
        if self.session_metadata is None:
            self.session_metadata = {}
        if self.conversation_state is None:
            self.conversation_state = {}

    @classmethod
    def from_entity(cls, context) -> 'VoiceSessionContextDTO':
        """Create DTO from domain entity."""
        return cls(
            current_location=context.current_location,
            current_job_id=context.current_job_id,
            current_contact_id=context.current_contact_id,
            current_project_id=context.current_project_id,
            session_metadata=context.session_metadata.copy() if context.session_metadata else {},
            conversation_state=context.conversation_state.copy() if context.conversation_state else {}
        )


@dataclass
class VoiceSessionAnalyticsDTO:
    """DTO for voice session analytics information."""
    total_interactions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    average_response_time_ms: Optional[float] = None
    total_duration_seconds: Optional[int] = None
    interruption_count: int = 0
    sentiment_score: Optional[float] = None
    confidence_score: Optional[float] = None
    tools_used: List[str] = None
    tool_execution_log: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []
        if self.tool_execution_log is None:
            self.tool_execution_log = []

    @classmethod
    def from_entity(cls, analytics) -> 'VoiceSessionAnalyticsDTO':
        """Create DTO from domain entity."""
        return cls(
            total_interactions=analytics.total_interactions,
            successful_actions=analytics.successful_actions,
            failed_actions=analytics.failed_actions,
            average_response_time_ms=float(analytics.average_response_time_ms) if analytics.average_response_time_ms else None,
            total_duration_seconds=analytics.total_duration_seconds,
            interruption_count=analytics.interruption_count,
            sentiment_score=float(analytics.sentiment_score) if analytics.sentiment_score else None,
            confidence_score=float(analytics.confidence_score) if analytics.confidence_score else None,
            tools_used=analytics.tools_used.copy() if analytics.tools_used else [],
            tool_execution_log=[]  # Will be populated from session data
        )

    def get_success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_interactions > 0:
            return (self.successful_actions / self.total_interactions) * 100
        return 0.0

    def get_average_response_time_seconds(self) -> Optional[float]:
        """Get average response time in seconds."""
        if self.average_response_time_ms:
            return self.average_response_time_ms / 1000
        return None


# Create Voice Session DTOs
@dataclass
class CreateVoiceSessionDTO:
    """DTO for creating a new voice session."""
    business_id: uuid.UUID
    user_id: str
    agent_type: AgentType
    session_timeout_minutes: int = 60
    voice_enabled: bool = True
    background_mode: bool = False
    emergency_mode: bool = False
    custom_settings: Dict[str, Any] = None
    
    # Context initialization
    current_location: Optional[str] = None
    current_job_id: Optional[uuid.UUID] = None
    current_contact_id: Optional[uuid.UUID] = None
    current_project_id: Optional[uuid.UUID] = None
    session_metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}
        if self.session_metadata is None:
            self.session_metadata = {}


@dataclass
class UpdateVoiceSessionDTO:
    """DTO for updating an existing voice session."""
    status: Optional[VoiceSessionStatus] = None
    session_timeout_minutes: Optional[int] = None
    voice_enabled: Optional[bool] = None
    background_mode: Optional[bool] = None
    emergency_mode: Optional[bool] = None
    session_notes: Optional[str] = None
    custom_settings: Optional[Dict[str, Any]] = None
    
    # Context updates
    current_location: Optional[str] = None
    current_job_id: Optional[uuid.UUID] = None
    current_contact_id: Optional[uuid.UUID] = None
    current_project_id: Optional[uuid.UUID] = None
    session_metadata: Optional[Dict[str, Any]] = None
    conversation_state: Optional[Dict[str, Any]] = None


@dataclass
class VoiceSessionResponseDTO:
    """DTO for voice session entity with full information."""
    id: uuid.UUID
    business_id: uuid.UUID
    user_id: str
    agent_type: AgentType
    status: VoiceSessionStatus
    livekit_room_name: str
    livekit_room_token: Optional[str] = None
    session_timeout_minutes: int = 60
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    # Context and analytics
    context: Optional[VoiceSessionContextDTO] = None
    analytics: Optional[VoiceSessionAnalyticsDTO] = None
    
    # Session data
    conversation_transcript: Optional[str] = None
    audio_recording_url: Optional[str] = None
    voice_enabled: bool = True
    background_mode: bool = False
    emergency_mode: bool = False
    session_notes: Optional[str] = None
    error_log: List[str] = None
    custom_settings: Dict[str, Any] = None

    def __post_init__(self):
        if self.error_log is None:
            self.error_log = []
        if self.custom_settings is None:
            self.custom_settings = {}

    @classmethod
    def from_entity(cls, session) -> 'VoiceSessionResponseDTO':
        """Create DTO from domain entity."""
        return cls(
            id=session.id,
            business_id=session.business_id,
            user_id=session.user_id,
            agent_type=session.agent_type,
            status=session.status,
            livekit_room_name=session.livekit_room_name,
            livekit_room_token=session.livekit_room_token,
            session_timeout_minutes=session.session_timeout_minutes,
            started_at=session.started_at,
            ended_at=session.ended_at,
            last_activity=session.last_activity,
            context=VoiceSessionContextDTO.from_entity(session.context),
            analytics=VoiceSessionAnalyticsDTO.from_entity(session.analytics),
            conversation_transcript=session.conversation_transcript,
            audio_recording_url=session.audio_recording_url,
            voice_enabled=session.voice_enabled,
            background_mode=session.background_mode,
            emergency_mode=session.emergency_mode,
            session_notes=session.session_notes,
            error_log=session.error_log.copy() if session.error_log else [],
            custom_settings=session.custom_settings.copy() if session.custom_settings else {}
        )

    def get_session_duration_minutes(self) -> Optional[float]:
        """Get session duration in minutes."""
        if self.started_at and self.ended_at:
            duration = self.ended_at - self.started_at
            return round(duration.total_seconds() / 60, 2)
        elif self.started_at:
            # Session still active
            duration = datetime.utcnow() - self.started_at
            return round(duration.total_seconds() / 60, 2)
        return None

    def is_active(self) -> bool:
        """Check if session is currently active."""
        return self.status in [VoiceSessionStatus.ACTIVE, VoiceSessionStatus.PAUSED]

    def get_status_display(self) -> str:
        """Get human-readable status."""
        return self.status.get_display()

    def get_agent_type_display(self) -> str:
        """Get human-readable agent type."""
        return self.agent_type.get_display()


@dataclass
class VoiceSessionSummaryDTO:
    """DTO for voice session summary in lists."""
    id: uuid.UUID
    user_id: str
    agent_type: AgentType
    status: VoiceSessionStatus
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    total_interactions: int = 0
    success_rate: float = 0.0
    is_emergency: bool = False

    @classmethod
    def from_entity(cls, session) -> 'VoiceSessionSummaryDTO':
        """Create summary DTO from domain entity."""
        duration = None
        if session.started_at and session.ended_at:
            duration_delta = session.ended_at - session.started_at
            duration = round(duration_delta.total_seconds() / 60, 2)
        
        success_rate = 0.0
        if session.analytics.total_interactions > 0:
            success_rate = (session.analytics.successful_actions / session.analytics.total_interactions) * 100

        return cls(
            id=session.id,
            user_id=session.user_id,
            agent_type=session.agent_type,
            status=session.status,
            started_at=session.started_at,
            ended_at=session.ended_at,
            duration_minutes=duration,
            total_interactions=session.analytics.total_interactions,
            success_rate=round(success_rate, 2),
            is_emergency=session.emergency_mode
        )


@dataclass
class VoiceSessionListDTO:
    """DTO for voice session list responses."""
    sessions: List[VoiceSessionSummaryDTO]
    total_count: int
    page: int
    limit: int
    has_next: bool
    has_previous: bool
    
    # Summary statistics
    active_sessions_count: int = 0
    total_duration_minutes: float = 0.0
    average_success_rate: float = 0.0

    @classmethod
    def from_entities(cls, sessions: List, total_count: int, page: int, limit: int) -> 'VoiceSessionListDTO':
        """Create list DTO from domain entities."""
        session_dtos = [VoiceSessionSummaryDTO.from_entity(session) for session in sessions]
        
        # Calculate summary statistics
        active_count = len([s for s in session_dtos if s.status in [VoiceSessionStatus.ACTIVE, VoiceSessionStatus.PAUSED]])
        total_duration = sum(s.duration_minutes for s in session_dtos if s.duration_minutes)
        avg_success_rate = sum(s.success_rate for s in session_dtos) / len(session_dtos) if session_dtos else 0.0

        return cls(
            sessions=session_dtos,
            total_count=total_count,
            page=page,
            limit=limit,
            has_next=(page * limit) < total_count,
            has_previous=page > 1,
            active_sessions_count=active_count,
            total_duration_minutes=round(total_duration, 2),
            average_success_rate=round(avg_success_rate, 2)
        )


@dataclass
class VoiceSessionSearchDTO:
    """DTO for voice session search criteria."""
    business_id: uuid.UUID
    user_id: Optional[str] = None
    agent_type: Optional[AgentType] = None
    status: Optional[VoiceSessionStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    emergency_mode: Optional[bool] = None
    has_errors: Optional[bool] = None
    min_duration_minutes: Optional[int] = None
    max_duration_minutes: Optional[int] = None
    min_interactions: Optional[int] = None
    tools_used: Optional[List[str]] = None
    limit: int = 50
    offset: int = 0
    sort_by: str = "started_at"
    sort_order: str = "desc"  # "asc" or "desc"


# Mobile-optimized DTOs
@dataclass
class MobileVoiceSessionDTO:
    """DTO optimized for mobile app consumption."""
    id: uuid.UUID
    agent_type: AgentType
    status: VoiceSessionStatus
    room_name: str
    started_at: datetime
    room_token: Optional[str] = None
    duration_minutes: Optional[float] = None
    is_emergency: bool = False
    voice_enabled: bool = True
    background_mode: bool = False
    
    # Current context (minimal)
    current_job_name: Optional[str] = None
    current_contact_name: Optional[str] = None
    current_project_name: Optional[str] = None
    
    # Quick stats
    interactions_count: int = 0
    last_activity: Optional[datetime] = None

    @classmethod
    def from_entity(cls, session, context_names: Optional[Dict[str, str]] = None) -> 'MobileVoiceSessionDTO':
        """Create mobile DTO from domain entity with optional context names."""
        if context_names is None:
            context_names = {}

        duration = None
        if session.started_at and session.ended_at:
            duration_delta = session.ended_at - session.started_at
            duration = round(duration_delta.total_seconds() / 60, 2)

        return cls(
            id=session.id,
            agent_type=session.agent_type,
            status=session.status,
            room_name=session.livekit_room_name,
            room_token=session.livekit_room_token,
            started_at=session.started_at,
            duration_minutes=duration,
            is_emergency=session.emergency_mode,
            voice_enabled=session.voice_enabled,
            background_mode=session.background_mode,
            current_job_name=context_names.get('job_name'),
            current_contact_name=context_names.get('contact_name'),
            current_project_name=context_names.get('project_name'),
            interactions_count=session.analytics.total_interactions,
            last_activity=session.last_activity
        )


@dataclass
class VoiceSessionStatisticsDTO:
    """DTO for voice session statistics and analytics."""
    business_id: uuid.UUID
    date_range_start: datetime
    date_range_end: datetime
    
    # Session counts
    total_sessions: int = 0
    active_sessions: int = 0
    completed_sessions: int = 0
    failed_sessions: int = 0
    emergency_sessions: int = 0
    
    # Duration statistics
    total_duration_minutes: float = 0.0
    average_duration_minutes: float = 0.0
    median_duration_minutes: float = 0.0
    
    # Interaction statistics
    total_interactions: int = 0
    total_successful_actions: int = 0
    total_failed_actions: int = 0
    overall_success_rate: float = 0.0
    
    # Agent type breakdown
    agent_type_breakdown: Dict[str, int] = None
    
    # Top tools used
    top_tools_used: List[Dict[str, Any]] = None
    
    # Performance metrics
    average_response_time_ms: float = 0.0
    user_satisfaction_score: Optional[float] = None

    def __post_init__(self):
        if self.agent_type_breakdown is None:
            self.agent_type_breakdown = {}
        if self.top_tools_used is None:
            self.top_tools_used = []


@dataclass
class VoiceToolExecutionDTO:
    """DTO for voice tool execution tracking."""
    session_id: uuid.UUID
    tool_name: str
    success: bool
    execution_time_ms: int
    timestamp: datetime
    result_summary: Optional[str] = None
    error_message: Optional[str] = None
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {} 