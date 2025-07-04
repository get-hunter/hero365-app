"""
Voice Session API Schemas

Pydantic schemas for voice session management API endpoints.
Handles request/response validation and serialization.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, field_serializer, ConfigDict
from pydantic.types import StringConstraints
from typing_extensions import Annotated

from ...utils import format_datetime_utc
from ...domain.enums import VoiceSessionStatus, AgentType
from ..converters import EnumConverter, SupabaseConverter

# Use centralized enums directly as API schemas
VoiceSessionStatusSchema = VoiceSessionStatus
AgentTypeSchema = AgentType


class VoiceSessionContextSchema(BaseModel):
    """Schema for voice session context information."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    current_location: Optional[str] = Field(None, description="Current location context")
    current_job_id: Optional[uuid.UUID] = Field(None, description="Current job ID")
    current_contact_id: Optional[uuid.UUID] = Field(None, description="Current contact ID")
    current_project_id: Optional[uuid.UUID] = Field(None, description="Current project ID")
    session_metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    conversation_state: Dict[str, Any] = Field(default_factory=dict, description="Conversation state")

    @field_validator('current_job_id', 'current_contact_id', 'current_project_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)


class VoiceSessionAnalyticsSchema(BaseModel):
    """Schema for voice session analytics information."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    total_interactions: int = Field(0, ge=0, description="Total interactions count")
    successful_actions: int = Field(0, ge=0, description="Successful actions count")
    failed_actions: int = Field(0, ge=0, description="Failed actions count")
    average_response_time_ms: Optional[float] = Field(None, description="Average response time in milliseconds")
    total_duration_seconds: Optional[int] = Field(None, description="Total duration in seconds")
    interruption_count: int = Field(0, ge=0, description="Number of interruptions")
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Sentiment score (-1 to 1)")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score (0 to 1)")
    tools_used: List[str] = Field(default_factory=list, description="List of tools used")
    tool_execution_log: List[Dict[str, Any]] = Field(default_factory=list, description="Tool execution log")


class VoiceSessionCreateRequest(BaseModel):
    """Schema for creating a new voice session."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    agent_type: AgentTypeSchema = Field(..., description="Type of voice agent")
    session_timeout_minutes: int = Field(60, ge=1, le=480, description="Session timeout in minutes")
    voice_enabled: bool = Field(True, description="Whether voice is enabled")
    background_mode: bool = Field(False, description="Whether to run in background mode")
    emergency_mode: bool = Field(False, description="Whether this is an emergency session")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom session settings")
    
    # Context initialization
    current_location: Optional[str] = Field(None, description="Current location")
    current_job_id: Optional[uuid.UUID] = Field(None, description="Current job ID")
    current_contact_id: Optional[uuid.UUID] = Field(None, description="Current contact ID")
    current_project_id: Optional[uuid.UUID] = Field(None, description="Current project ID")
    session_metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")

    @field_validator('agent_type', mode='before')
    @classmethod
    def validate_agent_type(cls, v):
        return EnumConverter.safe_agent_type(v)

    @field_validator('current_job_id', 'current_contact_id', 'current_project_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)


class VoiceSessionUpdateRequest(BaseModel):
    """Schema for updating a voice session."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    status: Optional[VoiceSessionStatusSchema] = Field(None, description="Session status")
    session_timeout_minutes: Optional[int] = Field(None, ge=1, le=480, description="Session timeout in minutes")
    voice_enabled: Optional[bool] = Field(None, description="Whether voice is enabled")
    background_mode: Optional[bool] = Field(None, description="Whether to run in background mode")
    emergency_mode: Optional[bool] = Field(None, description="Whether this is an emergency session")
    session_notes: Optional[str] = Field(None, max_length=2000, description="Session notes")
    custom_settings: Optional[Dict[str, Any]] = Field(None, description="Custom session settings")
    
    # Context updates
    current_location: Optional[str] = Field(None, description="Current location")
    current_job_id: Optional[uuid.UUID] = Field(None, description="Current job ID")
    current_contact_id: Optional[uuid.UUID] = Field(None, description="Current contact ID")
    current_project_id: Optional[uuid.UUID] = Field(None, description="Current project ID")
    session_metadata: Optional[Dict[str, Any]] = Field(None, description="Session metadata")
    conversation_state: Optional[Dict[str, Any]] = Field(None, description="Conversation state")

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_voice_session_status(v)

    @field_validator('current_job_id', 'current_contact_id', 'current_project_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)


class VoiceSessionResponse(BaseModel):
    """Schema for voice session response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Session ID")
    business_id: uuid.UUID = Field(..., description="Business ID")
    user_id: str = Field(..., description="User ID")
    agent_type: AgentTypeSchema = Field(..., description="Agent type")
    status: VoiceSessionStatusSchema = Field(..., description="Session status")
    livekit_room_name: str = Field(..., description="LiveKit room name")
    livekit_room_token: Optional[str] = Field(None, description="LiveKit room token")
    session_timeout_minutes: int = Field(..., description="Session timeout in minutes")
    started_at: datetime = Field(..., description="Session start time")
    ended_at: Optional[datetime] = Field(None, description="Session end time")
    last_activity: datetime = Field(..., description="Last activity time")
    
    # Context and analytics
    context: VoiceSessionContextSchema = Field(..., description="Session context")
    analytics: VoiceSessionAnalyticsSchema = Field(..., description="Session analytics")
    
    # Session data
    conversation_transcript: Optional[str] = Field(None, description="Conversation transcript")
    audio_recording_url: Optional[str] = Field(None, description="Audio recording URL")
    voice_enabled: bool = Field(..., description="Whether voice is enabled")
    background_mode: bool = Field(..., description="Whether running in background mode")
    emergency_mode: bool = Field(..., description="Whether this is an emergency session")
    session_notes: Optional[str] = Field(None, description="Session notes")
    error_log: List[str] = Field(default_factory=list, description="Error log")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")
    
    # Computed fields
    duration_minutes: Optional[float] = Field(None, description="Session duration in minutes")
    is_active: bool = Field(..., description="Whether session is active")
    status_display: str = Field(..., description="Human-readable status")
    agent_type_display: str = Field(..., description="Human-readable agent type")

    @field_validator('agent_type', mode='before')
    @classmethod
    def validate_agent_type(cls, v):
        return EnumConverter.safe_agent_type(v)

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_voice_session_status(v)

    @field_validator('id', 'business_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)

    @field_validator('started_at', 'ended_at', 'last_activity', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('started_at', 'ended_at', 'last_activity')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class VoiceSessionSummaryResponse(BaseModel):
    """Schema for voice session summary response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    agent_type: AgentTypeSchema = Field(..., description="Agent type")
    status: VoiceSessionStatusSchema = Field(..., description="Session status")
    started_at: datetime = Field(..., description="Session start time")
    ended_at: Optional[datetime] = Field(None, description="Session end time")
    duration_minutes: Optional[float] = Field(None, description="Session duration in minutes")
    total_interactions: int = Field(..., description="Total interactions")
    success_rate: float = Field(..., description="Success rate percentage")
    is_emergency: bool = Field(..., description="Whether this is an emergency session")

    @field_validator('agent_type', mode='before')
    @classmethod
    def validate_agent_type(cls, v):
        return EnumConverter.safe_agent_type(v)

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_voice_session_status(v)

    @field_validator('started_at', 'ended_at', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('started_at', 'ended_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class VoiceSessionListResponse(BaseModel):
    """Schema for voice session list response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    sessions: List[VoiceSessionSummaryResponse] = Field(..., description="List of sessions")
    total_count: int = Field(..., ge=0, description="Total number of sessions")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")
    
    # Summary statistics
    active_sessions_count: int = Field(..., description="Number of active sessions")
    total_duration_minutes: float = Field(..., description="Total duration of all sessions")
    average_success_rate: float = Field(..., description="Average success rate")


class VoiceSessionSearchRequest(BaseModel):
    """Schema for voice session search request."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    agent_type: Optional[AgentTypeSchema] = Field(None, description="Filter by agent type")
    status: Optional[VoiceSessionStatusSchema] = Field(None, description="Filter by status")
    start_date: Optional[datetime] = Field(None, description="Filter by start date (from)")
    end_date: Optional[datetime] = Field(None, description="Filter by end date (to)")
    emergency_mode: Optional[bool] = Field(None, description="Filter by emergency mode")
    has_errors: Optional[bool] = Field(None, description="Filter by error presence")
    min_duration_minutes: Optional[int] = Field(None, ge=0, description="Minimum duration in minutes")
    max_duration_minutes: Optional[int] = Field(None, ge=0, description="Maximum duration in minutes")
    min_interactions: Optional[int] = Field(None, ge=0, description="Minimum interactions count")
    tools_used: Optional[List[str]] = Field(None, description="Filter by tools used")
    limit: int = Field(50, ge=1, le=100, description="Number of results per page")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    sort_by: str = Field("started_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    @field_validator('agent_type', mode='before')
    @classmethod
    def validate_agent_type(cls, v):
        return EnumConverter.safe_agent_type(v) if v else None

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_voice_session_status(v) if v else None

    @field_validator('start_date', 'end_date', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)


class MobileVoiceSessionResponse(BaseModel):
    """Schema for mobile-optimized voice session response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Session ID")
    agent_type: AgentTypeSchema = Field(..., description="Agent type")
    status: VoiceSessionStatusSchema = Field(..., description="Session status")
    room_name: str = Field(..., description="LiveKit room name")
    room_token: Optional[str] = Field(None, description="LiveKit room token")
    started_at: datetime = Field(..., description="Session start time")
    duration_minutes: Optional[float] = Field(None, description="Session duration in minutes")
    is_emergency: bool = Field(..., description="Whether this is an emergency session")
    voice_enabled: bool = Field(..., description="Whether voice is enabled")
    background_mode: bool = Field(..., description="Whether running in background mode")
    
    # Current context (minimal)
    current_job_name: Optional[str] = Field(None, description="Current job name")
    current_contact_name: Optional[str] = Field(None, description="Current contact name")
    current_project_name: Optional[str] = Field(None, description="Current project name")
    
    # Quick stats
    interactions_count: int = Field(..., description="Number of interactions")
    last_activity: datetime = Field(..., description="Last activity time")

    @field_validator('agent_type', mode='before')
    @classmethod
    def validate_agent_type(cls, v):
        return EnumConverter.safe_agent_type(v)

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_voice_session_status(v)

    @field_validator('started_at', 'last_activity', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('started_at', 'last_activity')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class VoiceSessionStatisticsResponse(BaseModel):
    """Schema for voice session statistics response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    date_range_start: datetime = Field(..., description="Statistics date range start")
    date_range_end: datetime = Field(..., description="Statistics date range end")
    
    # Session counts
    total_sessions: int = Field(..., description="Total number of sessions")
    active_sessions: int = Field(..., description="Number of active sessions")
    completed_sessions: int = Field(..., description="Number of completed sessions")
    failed_sessions: int = Field(..., description="Number of failed sessions")
    emergency_sessions: int = Field(..., description="Number of emergency sessions")
    
    # Duration statistics
    total_duration_minutes: float = Field(..., description="Total duration of all sessions")
    average_duration_minutes: float = Field(..., description="Average session duration")
    median_duration_minutes: float = Field(..., description="Median session duration")
    
    # Interaction statistics
    total_interactions: int = Field(..., description="Total number of interactions")
    total_successful_actions: int = Field(..., description="Total successful actions")
    total_failed_actions: int = Field(..., description="Total failed actions")
    overall_success_rate: float = Field(..., description="Overall success rate")
    
    # Agent type breakdown
    agent_type_breakdown: Dict[str, int] = Field(..., description="Breakdown by agent type")
    
    # Top tools used
    top_tools_used: List[Dict[str, Any]] = Field(..., description="Most used tools")
    
    # Performance metrics
    average_response_time_ms: float = Field(..., description="Average response time")
    user_satisfaction_score: Optional[float] = Field(None, description="User satisfaction score")

    @field_validator('date_range_start', 'date_range_end', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('date_range_start', 'date_range_end')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class VoiceToolExecutionResponse(BaseModel):
    """Schema for voice tool execution response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    session_id: uuid.UUID = Field(..., description="Session ID")
    tool_name: str = Field(..., description="Tool name")
    success: bool = Field(..., description="Whether execution was successful")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    timestamp: datetime = Field(..., description="Execution timestamp")
    result_summary: Optional[str] = Field(None, description="Summary of execution result")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")

    @field_validator('session_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)

    @field_validator('timestamp', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('timestamp')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


# VoiceSessionActionResponse removed - using continuous conversation instead of discrete commands