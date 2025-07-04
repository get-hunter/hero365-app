"""
Outbound Call API Schemas

Pydantic schemas for outbound call management and campaign API endpoints.
Handles request/response validation and serialization.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, field_serializer, ConfigDict
from pydantic.types import StringConstraints
from typing_extensions import Annotated

from ...utils import format_datetime_utc
from ...domain.enums import CallStatus, AgentType, CallOutcome, CampaignStatus, CampaignType
from ..converters import EnumConverter, SupabaseConverter

# Use centralized enums directly as API schemas
CallStatusSchema = CallStatus
AgentTypeSchema = AgentType
CallOutcomeSchema = CallOutcome
CampaignStatusSchema = CampaignStatus
CampaignTypeSchema = CampaignType


class OutboundCallRecipientSchema(BaseModel):
    """Schema for outbound call recipient information."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    contact_id: uuid.UUID = Field(..., description="Contact ID")
    contact_name: str = Field(..., min_length=1, max_length=200, description="Contact name")
    phone_number: str = Field(..., min_length=10, max_length=20, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")
    preferred_call_time: Optional[str] = Field(None, description="Preferred call time")
    timezone: Optional[str] = Field(None, description="Timezone")
    language_preference: Optional[str] = Field(None, description="Language preference")
    customer_segment: Optional[str] = Field(None, description="Customer segment")
    previous_interactions: int = Field(0, ge=0, description="Number of previous interactions")
    last_contact_date: Optional[datetime] = Field(None, description="Last contact date")
    do_not_call: bool = Field(False, description="Do not call flag")
    
    # Campaign-specific data
    campaign_data: Dict[str, Any] = Field(default_factory=dict, description="Campaign-specific data")
    personalization_data: Dict[str, Any] = Field(default_factory=dict, description="Personalization data")

    @field_validator('contact_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)

    @field_validator('last_contact_date', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('last_contact_date')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class OutboundCallScriptSchema(BaseModel):
    """Schema for outbound call script information."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    opening_message: str = Field(..., min_length=10, max_length=500, description="Opening message")
    main_talking_points: List[str] = Field(..., min_length=1, description="Main talking points")
    objection_handling: Dict[str, str] = Field(..., description="Objection handling responses")
    closing_message: str = Field(..., min_length=10, max_length=500, description="Closing message")
    call_to_action: str = Field(..., min_length=5, max_length=200, description="Call to action")
    fallback_options: List[str] = Field(default_factory=list, description="Fallback options")
    max_call_duration_minutes: int = Field(15, ge=1, le=60, description="Maximum call duration")
    allow_interruptions: bool = Field(True, description="Allow interruptions")
    personalization_tokens: List[str] = Field(default_factory=list, description="Personalization tokens")
    
    # Voice settings
    voice_tone: str = Field("professional", description="Voice tone")
    speaking_rate: float = Field(1.0, ge=0.5, le=2.0, description="Speaking rate")
    pause_duration_ms: int = Field(500, ge=100, le=2000, description="Pause duration in milliseconds")


class OutboundCallResultSchema(BaseModel):
    """Schema for outbound call result information."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    call_connected: bool = Field(..., description="Whether call was connected")
    call_duration_seconds: int = Field(..., ge=0, description="Call duration in seconds")
    outcome: CallOutcomeSchema = Field(..., description="Call outcome")
    outcome_details: str = Field(..., description="Outcome details")
    customer_response: str = Field(..., description="Customer response")
    next_action: Optional[str] = Field(None, description="Next action to take")
    follow_up_required: bool = Field(False, description="Whether follow-up is required")
    follow_up_date: Optional[datetime] = Field(None, description="Follow-up date")
    appointment_scheduled: bool = Field(False, description="Whether appointment was scheduled")
    appointment_datetime: Optional[datetime] = Field(None, description="Appointment date/time")
    lead_score: Optional[int] = Field(None, ge=0, le=100, description="Lead score (0-100)")
    conversation_transcript: Optional[str] = Field(None, description="Conversation transcript")
    call_recording_url: Optional[str] = Field(None, description="Call recording URL")
    agent_notes: Optional[str] = Field(None, max_length=1000, description="Agent notes")
    
    # Analytics
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Sentiment score")
    engagement_level: Optional[str] = Field(None, description="Engagement level")
    interruption_count: int = Field(0, ge=0, description="Number of interruptions")
    customer_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="Customer satisfaction (1-5)")

    @field_validator('outcome', mode='before')
    @classmethod
    def validate_outcome(cls, v):
        return EnumConverter.safe_call_outcome(v)

    @field_validator('follow_up_date', 'appointment_datetime', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('follow_up_date', 'appointment_datetime')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class OutboundCallCreateRequest(BaseModel):
    """Schema for creating a new outbound call."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    campaign_id: Optional[uuid.UUID] = Field(None, description="Campaign ID")
    agent_type: AgentTypeSchema = Field(AgentType.OUTBOUND_CALLER, description="Agent type")
    priority: int = Field(1, ge=1, le=5, description="Call priority (1-5)")
    scheduled_for: Optional[datetime] = Field(None, description="Scheduled time for call")
    
    # Recipient information
    recipient: OutboundCallRecipientSchema = Field(..., description="Call recipient")
    
    # Script and settings
    script: OutboundCallScriptSchema = Field(..., description="Call script")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")
    
    # Campaign context
    campaign_goal: Optional[str] = Field(None, description="Campaign goal")
    campaign_context: Dict[str, Any] = Field(default_factory=dict, description="Campaign context")
    
    # Retry configuration
    max_retry_attempts: int = Field(3, ge=1, le=10, description="Maximum retry attempts")
    retry_delay_minutes: int = Field(60, ge=15, le=1440, description="Retry delay in minutes")
    
    # Voice session settings
    voice_enabled: bool = Field(True, description="Whether voice is enabled")
    background_mode: bool = Field(False, description="Whether to run in background mode")

    @field_validator('campaign_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)

    @field_validator('agent_type', mode='before')
    @classmethod
    def validate_agent_type(cls, v):
        return EnumConverter.safe_agent_type(v)

    @field_validator('scheduled_for', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('scheduled_for')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class OutboundCallUpdateRequest(BaseModel):
    """Schema for updating an outbound call."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    status: Optional[CallStatusSchema] = Field(None, description="Call status")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Call priority")
    scheduled_for: Optional[datetime] = Field(None, description="Scheduled time for call")
    attempted_at: Optional[datetime] = Field(None, description="Attempt timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    retry_count: Optional[int] = Field(None, ge=0, description="Retry count")
    next_retry_at: Optional[datetime] = Field(None, description="Next retry timestamp")
    
    # Result information
    result: Optional[OutboundCallResultSchema] = Field(None, description="Call result")
    
    # Session reference
    voice_session_id: Optional[uuid.UUID] = Field(None, description="Voice session ID")
    
    # Campaign updates
    campaign_context: Optional[Dict[str, Any]] = Field(None, description="Campaign context")
    custom_settings: Optional[Dict[str, Any]] = Field(None, description="Custom settings")

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_call_status(v)

    @field_validator('voice_session_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)

    @field_validator('scheduled_for', 'attempted_at', 'completed_at', 'next_retry_at', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('scheduled_for', 'attempted_at', 'completed_at', 'next_retry_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class OutboundCallResponse(BaseModel):
    """Schema for outbound call response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Call ID")
    business_id: uuid.UUID = Field(..., description="Business ID")
    campaign_id: Optional[uuid.UUID] = Field(None, description="Campaign ID")
    agent_type: AgentTypeSchema = Field(..., description="Agent type")
    status: CallStatusSchema = Field(..., description="Call status")
    priority: int = Field(..., description="Call priority")
    scheduled_for: Optional[datetime] = Field(None, description="Scheduled time")
    attempted_at: Optional[datetime] = Field(None, description="Attempt timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    retry_count: int = Field(..., description="Retry count")
    next_retry_at: Optional[datetime] = Field(None, description="Next retry timestamp")
    
    # Recipient and script
    recipient: OutboundCallRecipientSchema = Field(..., description="Call recipient")
    script: OutboundCallScriptSchema = Field(..., description="Call script")
    
    # Result information
    result: Optional[OutboundCallResultSchema] = Field(None, description="Call result")
    
    # Session reference
    voice_session_id: Optional[uuid.UUID] = Field(None, description="Voice session ID")
    
    # Campaign context
    campaign_goal: Optional[str] = Field(None, description="Campaign goal")
    campaign_context: Dict[str, Any] = Field(default_factory=dict, description="Campaign context")
    
    # Settings
    max_retry_attempts: int = Field(..., description="Maximum retry attempts")
    retry_delay_minutes: int = Field(..., description="Retry delay in minutes")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")
    
    # Audit fields
    created_by: str = Field(..., description="Created by user")
    created_date: datetime = Field(..., description="Creation date")
    last_modified: datetime = Field(..., description="Last modification date")
    
    # Computed fields
    call_duration_minutes: Optional[float] = Field(None, description="Call duration in minutes")
    is_due_for_retry: bool = Field(..., description="Whether due for retry")
    status_display: str = Field(..., description="Human-readable status")
    outcome_display: Optional[str] = Field(None, description="Human-readable outcome")

    @field_validator('agent_type', mode='before')
    @classmethod
    def validate_agent_type(cls, v):
        return EnumConverter.safe_agent_type(v)

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_call_status(v)

    @field_validator('id', 'business_id', 'campaign_id', 'voice_session_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)

    @field_validator('scheduled_for', 'attempted_at', 'completed_at', 'next_retry_at', 'created_date', 'last_modified', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('scheduled_for', 'attempted_at', 'completed_at', 'next_retry_at', 'created_date', 'last_modified')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class OutboundCallSummaryResponse(BaseModel):
    """Schema for outbound call summary response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Call ID")
    contact_name: str = Field(..., description="Contact name")
    phone_number: str = Field(..., description="Phone number")
    campaign_id: Optional[uuid.UUID] = Field(None, description="Campaign ID")
    status: CallStatusSchema = Field(..., description="Call status")
    priority: int = Field(..., description="Call priority")
    scheduled_for: Optional[datetime] = Field(None, description="Scheduled time")
    attempted_at: Optional[datetime] = Field(None, description="Attempt timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    outcome: Optional[CallOutcomeSchema] = Field(None, description="Call outcome")
    call_duration_minutes: Optional[float] = Field(None, description="Call duration in minutes")
    retry_count: int = Field(..., description="Retry count")
    appointment_scheduled: bool = Field(..., description="Whether appointment was scheduled")
    follow_up_required: bool = Field(..., description="Whether follow-up is required")

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_call_status(v)

    @field_validator('outcome', mode='before')
    @classmethod
    def validate_outcome(cls, v):
        return EnumConverter.safe_call_outcome(v) if v else None

    @field_validator('id', 'campaign_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)

    @field_validator('scheduled_for', 'attempted_at', 'completed_at', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('scheduled_for', 'attempted_at', 'completed_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class OutboundCallListResponse(BaseModel):
    """Schema for outbound call list response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    calls: List[OutboundCallSummaryResponse] = Field(..., description="List of calls")
    total_count: int = Field(..., ge=0, description="Total number of calls")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")
    
    # Summary statistics
    pending_calls_count: int = Field(..., description="Number of pending calls")
    completed_calls_count: int = Field(..., description="Number of completed calls")
    successful_calls_count: int = Field(..., description="Number of successful calls")
    total_duration_minutes: float = Field(..., description="Total duration of all calls")
    average_success_rate: float = Field(..., description="Average success rate")


class OutboundCallSearchRequest(BaseModel):
    """Schema for outbound call search request."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    campaign_id: Optional[uuid.UUID] = Field(None, description="Filter by campaign ID")
    status: Optional[CallStatusSchema] = Field(None, description="Filter by status")
    outcome: Optional[CallOutcomeSchema] = Field(None, description="Filter by outcome")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Filter by priority")
    scheduled_start: Optional[datetime] = Field(None, description="Filter by scheduled start date")
    scheduled_end: Optional[datetime] = Field(None, description="Filter by scheduled end date")
    attempted_start: Optional[datetime] = Field(None, description="Filter by attempted start date")
    attempted_end: Optional[datetime] = Field(None, description="Filter by attempted end date")
    contact_name: Optional[str] = Field(None, description="Filter by contact name")
    phone_number: Optional[str] = Field(None, description="Filter by phone number")
    appointment_scheduled: Optional[bool] = Field(None, description="Filter by appointment scheduled")
    follow_up_required: Optional[bool] = Field(None, description="Filter by follow-up required")
    min_duration_minutes: Optional[int] = Field(None, ge=0, description="Minimum duration in minutes")
    max_duration_minutes: Optional[int] = Field(None, ge=0, description="Maximum duration in minutes")
    limit: int = Field(50, ge=1, le=100, description="Number of results per page")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    sort_by: str = Field("scheduled_for", description="Sort field")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")

    @field_validator('campaign_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_call_status(v) if v else None

    @field_validator('outcome', mode='before')
    @classmethod
    def validate_outcome(cls, v):
        return EnumConverter.safe_call_outcome(v) if v else None

    @field_validator('scheduled_start', 'scheduled_end', 'attempted_start', 'attempted_end', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('scheduled_start', 'scheduled_end', 'attempted_start', 'attempted_end')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class CampaignSummaryResponse(BaseModel):
    """Schema for campaign summary response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Campaign ID")
    name: str = Field(..., description="Campaign name")
    campaign_type: CampaignTypeSchema = Field(..., description="Campaign type")
    status: CampaignStatusSchema = Field(..., description="Campaign status")
    start_date: datetime = Field(..., description="Campaign start date")
    end_date: Optional[datetime] = Field(None, description="Campaign end date")
    total_calls: int = Field(..., description="Total number of calls")
    completed_calls: int = Field(..., description="Number of completed calls")
    successful_calls: int = Field(..., description="Number of successful calls")
    success_rate: float = Field(..., description="Success rate percentage")
    average_call_duration: float = Field(..., description="Average call duration")
    appointments_scheduled: int = Field(..., description="Number of appointments scheduled")

    @field_validator('campaign_type', mode='before')
    @classmethod
    def validate_campaign_type(cls, v):
        return EnumConverter.safe_campaign_type(v)

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_campaign_status(v)

    @field_validator('id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)

    @field_validator('start_date', 'end_date', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('start_date', 'end_date')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class MobileOutboundCallResponse(BaseModel):
    """Schema for mobile-optimized outbound call response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(..., description="Call ID")
    contact_name: str = Field(..., description="Contact name")
    phone_number: str = Field(..., description="Phone number")
    status: CallStatusSchema = Field(..., description="Call status")
    priority: int = Field(..., description="Call priority")
    scheduled_for: Optional[datetime] = Field(None, description="Scheduled time")
    duration_minutes: Optional[float] = Field(None, description="Call duration in minutes")
    outcome: Optional[CallOutcomeSchema] = Field(None, description="Call outcome")
    campaign_name: Optional[str] = Field(None, description="Campaign name")
    appointment_scheduled: bool = Field(..., description="Whether appointment was scheduled")
    follow_up_required: bool = Field(..., description="Whether follow-up is required")
    next_retry_at: Optional[datetime] = Field(None, description="Next retry time")

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        return EnumConverter.safe_call_status(v)

    @field_validator('outcome', mode='before')
    @classmethod
    def validate_outcome(cls, v):
        return EnumConverter.safe_call_outcome(v) if v else None

    @field_validator('id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        return SupabaseConverter.safe_uuid_field(v)

    @field_validator('scheduled_for', 'next_retry_at', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('scheduled_for', 'next_retry_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class OutboundCallStatisticsResponse(BaseModel):
    """Schema for outbound call statistics response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    date_range_start: datetime = Field(..., description="Statistics date range start")
    date_range_end: datetime = Field(..., description="Statistics date range end")
    
    # Call counts
    total_calls: int = Field(..., description="Total number of calls")
    pending_calls: int = Field(..., description="Number of pending calls")
    completed_calls: int = Field(..., description="Number of completed calls")
    failed_calls: int = Field(..., description="Number of failed calls")
    
    # Success metrics
    successful_calls: int = Field(..., description="Number of successful calls")
    appointments_scheduled: int = Field(..., description="Number of appointments scheduled")
    callbacks_requested: int = Field(..., description="Number of callbacks requested")
    overall_success_rate: float = Field(..., description="Overall success rate")
    
    # Duration statistics
    total_duration_minutes: float = Field(..., description="Total duration of all calls")
    average_duration_minutes: float = Field(..., description="Average call duration")
    median_duration_minutes: float = Field(..., description="Median call duration")
    
    # Outcome breakdown
    outcome_breakdown: Dict[str, int] = Field(..., description="Breakdown by outcome")
    
    # Campaign performance
    campaign_performance: List[Dict[str, Any]] = Field(..., description="Performance by campaign")
    
    # Time-based analytics
    peak_calling_hours: List[Dict[str, Any]] = Field(..., description="Peak calling hours")
    daily_performance: List[Dict[str, Any]] = Field(..., description="Daily performance")

    @field_validator('date_range_start', 'date_range_end', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('date_range_start', 'date_range_end')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class CallQueueStatusResponse(BaseModel):
    """Schema for call queue status response."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )
    
    total_pending: int = Field(..., description="Total pending calls")
    high_priority_pending: int = Field(..., description="High priority pending calls")
    scheduled_next_hour: int = Field(..., description="Calls scheduled for next hour")
    scheduled_today: int = Field(..., description="Calls scheduled for today")
    overdue_calls: int = Field(..., description="Overdue calls")
    retry_due_calls: int = Field(..., description="Calls due for retry")
    active_sessions: int = Field(..., description="Active voice sessions")
    queue_processing_rate: float = Field(..., description="Queue processing rate (calls/hour)")
    estimated_completion_time: Optional[datetime] = Field(None, description="Estimated completion time")

    @field_validator('estimated_completion_time', mode='before')
    @classmethod
    def validate_datetime_fields(cls, v):
        return SupabaseConverter.safe_datetime_field(v)

    @field_serializer('estimated_completion_time')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        return format_datetime_utc(value) if value else None


class OutboundCallActionResponse(BaseModel):
    """Schema for outbound call action responses."""
    success: bool = True
    message: str
    call_id: Optional[uuid.UUID] = None
    session_id: Optional[uuid.UUID] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Outbound call created successfully",
                "call_id": "550e8400-e29b-41d4-a716-446655440000",
                "session_id": "550e8400-e29b-41d4-a716-446655440001"
            }
        }
    } 