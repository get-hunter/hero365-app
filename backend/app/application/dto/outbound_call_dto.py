"""
Outbound Call Data Transfer Objects

DTOs for outbound call management and campaign operations following clean architecture principles.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass

from app.domain.enums import CallStatus, AgentType, CallOutcome, CampaignStatus, CampaignType


@dataclass
class OutboundCallRecipientDTO:
    """DTO for outbound call recipient information."""
    contact_id: uuid.UUID
    contact_name: str
    phone_number: str
    email: Optional[str] = None
    preferred_call_time: Optional[str] = None
    timezone: Optional[str] = None
    language_preference: Optional[str] = None
    customer_segment: Optional[str] = None
    previous_interactions: int = 0
    last_contact_date: Optional[datetime] = None
    do_not_call: bool = False
    
    # Campaign-specific data
    campaign_data: Dict[str, Any] = None
    personalization_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.campaign_data is None:
            self.campaign_data = {}
        if self.personalization_data is None:
            self.personalization_data = {}

    @classmethod
    def from_entity(cls, recipient) -> 'OutboundCallRecipientDTO':
        """Create DTO from domain entity."""
        return cls(
            contact_id=recipient.contact_id,
            contact_name=recipient.contact_name,
            phone_number=recipient.phone_number,
            email=recipient.email,
            preferred_call_time=recipient.preferred_call_time,
            timezone=recipient.timezone,
            language_preference=recipient.language_preference,
            customer_segment=recipient.customer_segment,
            previous_interactions=recipient.previous_interactions,
            last_contact_date=recipient.last_contact_date,
            do_not_call=recipient.do_not_call,
            campaign_data=recipient.campaign_data.copy() if recipient.campaign_data else {},
            personalization_data=recipient.personalization_data.copy() if recipient.personalization_data else {}
        )


@dataclass
class OutboundCallScriptDTO:
    """DTO for outbound call script information."""
    opening_message: str
    main_talking_points: List[str]
    objection_handling: Dict[str, str]
    closing_message: str
    call_to_action: str
    fallback_options: List[str]
    max_call_duration_minutes: int = 15
    allow_interruptions: bool = True
    personalization_tokens: List[str] = None
    
    # Voice settings
    voice_tone: str = "professional"
    speaking_rate: float = 1.0
    pause_duration_ms: int = 500

    def __post_init__(self):
        if self.personalization_tokens is None:
            self.personalization_tokens = []

    @classmethod
    def from_entity(cls, script) -> 'OutboundCallScriptDTO':
        """Create DTO from domain entity."""
        return cls(
            opening_message=script.opening_message,
            main_talking_points=script.main_talking_points.copy(),
            objection_handling=script.objection_handling.copy(),
            closing_message=script.closing_message,
            call_to_action=script.call_to_action,
            fallback_options=script.fallback_options.copy(),
            max_call_duration_minutes=script.max_call_duration_minutes,
            allow_interruptions=script.allow_interruptions,
            personalization_tokens=script.personalization_tokens.copy() if script.personalization_tokens else [],
            voice_tone=script.voice_tone,
            speaking_rate=script.speaking_rate,
            pause_duration_ms=script.pause_duration_ms
        )


@dataclass
class OutboundCallResultDTO:
    """DTO for outbound call result information."""
    call_connected: bool
    call_duration_seconds: int
    outcome: CallOutcome
    outcome_details: str
    customer_response: str
    next_action: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    appointment_scheduled: bool = False
    appointment_datetime: Optional[datetime] = None
    lead_score: Optional[int] = None
    conversation_transcript: Optional[str] = None
    call_recording_url: Optional[str] = None
    agent_notes: Optional[str] = None
    
    # Analytics
    sentiment_score: Optional[float] = None
    engagement_level: Optional[str] = None
    interruption_count: int = 0
    customer_satisfaction: Optional[int] = None

    @classmethod
    def from_entity(cls, result) -> 'OutboundCallResultDTO':
        """Create DTO from domain entity."""
        return cls(
            call_connected=result.call_connected,
            call_duration_seconds=result.call_duration_seconds,
            outcome=result.outcome,
            outcome_details=result.outcome_details,
            customer_response=result.customer_response,
            next_action=result.next_action,
            follow_up_required=result.follow_up_required,
            follow_up_date=result.follow_up_date,
            appointment_scheduled=result.appointment_scheduled,
            appointment_datetime=result.appointment_datetime,
            lead_score=result.lead_score,
            conversation_transcript=result.conversation_transcript,
            call_recording_url=result.call_recording_url,
            agent_notes=result.agent_notes,
            sentiment_score=float(result.sentiment_score) if result.sentiment_score else None,
            engagement_level=result.engagement_level,
            interruption_count=result.interruption_count,
            customer_satisfaction=result.customer_satisfaction
        )


# Create Outbound Call DTOs
@dataclass
class CreateOutboundCallDTO:
    """DTO for creating a new outbound call."""
    business_id: uuid.UUID
    recipient: OutboundCallRecipientDTO
    script: OutboundCallScriptDTO
    campaign_id: Optional[uuid.UUID] = None
    agent_type: AgentType = AgentType.OUTBOUND_CALLER
    priority: int = 1
    scheduled_for: Optional[datetime] = None
    
    # Settings
    custom_settings: Optional[Dict[str, Any]] = None
    
    # Campaign context
    campaign_goal: Optional[str] = None
    campaign_context: Optional[Dict[str, Any]] = None
    
    # Retry configuration
    max_retry_attempts: int = 3
    retry_delay_minutes: int = 60
    
    # Voice session settings
    voice_enabled: bool = True
    background_mode: bool = False

    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}
        if self.campaign_context is None:
            self.campaign_context = {}


@dataclass
class UpdateOutboundCallDTO:
    """DTO for updating an existing outbound call."""
    status: Optional[CallStatus] = None
    priority: Optional[int] = None
    scheduled_for: Optional[datetime] = None
    attempted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: Optional[int] = None
    next_retry_at: Optional[datetime] = None
    
    # Result information
    result: Optional[OutboundCallResultDTO] = None
    
    # Session reference
    voice_session_id: Optional[uuid.UUID] = None
    
    # Campaign updates
    campaign_context: Optional[Dict[str, Any]] = None
    custom_settings: Optional[Dict[str, Any]] = None


@dataclass
class OutboundCallResponseDTO:
    """DTO for outbound call entity with full information."""
    id: uuid.UUID
    business_id: uuid.UUID
    agent_type: AgentType
    status: CallStatus
    priority: int
    recipient: OutboundCallRecipientDTO
    script: OutboundCallScriptDTO
    campaign_id: Optional[uuid.UUID] = None
    scheduled_for: Optional[datetime] = None
    attempted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None
    
    # Result information
    result: Optional[OutboundCallResultDTO] = None
    
    # Session reference
    voice_session_id: Optional[uuid.UUID] = None
    
    # Campaign context
    campaign_goal: Optional[str] = None
    campaign_context: Optional[Dict[str, Any]] = None
    
    # Settings
    max_retry_attempts: int = 3
    retry_delay_minutes: int = 60
    custom_settings: Optional[Dict[str, Any]] = None
    
    # Audit fields
    created_by: str = ""
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None

    def __post_init__(self):
        if self.campaign_context is None:
            self.campaign_context = {}
        if self.custom_settings is None:
            self.custom_settings = {}

    @classmethod
    def from_entity(cls, call) -> 'OutboundCallResponseDTO':
        """Create DTO from domain entity."""
        return cls(
            id=call.id,
            business_id=call.business_id,
            campaign_id=call.campaign_id,
            agent_type=call.agent_type,
            status=call.status,
            priority=call.priority,
            scheduled_for=call.scheduled_for,
            attempted_at=call.attempted_at,
            completed_at=call.completed_at,
            retry_count=call.retry_count,
            next_retry_at=call.next_retry_at,
            recipient=OutboundCallRecipientDTO.from_entity(call.recipient),
            script=OutboundCallScriptDTO.from_entity(call.script),
            result=OutboundCallResultDTO.from_entity(call.result) if call.result else None,
            voice_session_id=call.voice_session_id,
            campaign_goal=call.campaign_goal,
            campaign_context=call.campaign_context.copy() if call.campaign_context else {},
            max_retry_attempts=call.max_retry_attempts,
            retry_delay_minutes=call.retry_delay_minutes,
            custom_settings=call.custom_settings.copy() if call.custom_settings else {},
            created_by=call.created_by,
            created_date=call.created_date,
            last_modified=call.last_modified
        )

    def get_call_duration_minutes(self) -> Optional[float]:
        """Get call duration in minutes."""
        if self.result and self.result.call_duration_seconds:
            return round(self.result.call_duration_seconds / 60, 2)
        return None

    def is_due_for_retry(self) -> bool:
        """Check if call is due for retry."""
        if not self.next_retry_at:
            return False
        return datetime.utcnow() >= self.next_retry_at

    def get_status_display(self) -> str:
        """Get human-readable status."""
        return self.status.get_display()

    def get_outcome_display(self) -> Optional[str]:
        """Get human-readable outcome."""
        if self.result:
            return self.result.outcome.get_display()
        return None


@dataclass
class OutboundCallSummaryDTO:
    """DTO for outbound call summary in lists."""
    id: uuid.UUID
    contact_name: str
    phone_number: str
    status: CallStatus
    priority: int
    campaign_id: Optional[uuid.UUID] = None
    scheduled_for: Optional[datetime] = None
    attempted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    outcome: Optional[CallOutcome] = None
    call_duration_minutes: Optional[float] = None
    retry_count: int = 0
    appointment_scheduled: bool = False
    follow_up_required: bool = False

    @classmethod
    def from_entity(cls, call) -> 'OutboundCallSummaryDTO':
        """Create summary DTO from domain entity."""
        duration = None
        if call.result and call.result.call_duration_seconds:
            duration = round(call.result.call_duration_seconds / 60, 2)

        return cls(
            id=call.id,
            contact_name=call.recipient.contact_name,
            phone_number=call.recipient.phone_number,
            campaign_id=call.campaign_id,
            status=call.status,
            priority=call.priority,
            scheduled_for=call.scheduled_for,
            attempted_at=call.attempted_at,
            completed_at=call.completed_at,
            outcome=call.result.outcome if call.result else None,
            call_duration_minutes=duration,
            retry_count=call.retry_count,
            appointment_scheduled=call.result.appointment_scheduled if call.result else False,
            follow_up_required=call.result.follow_up_required if call.result else False
        )


@dataclass
class OutboundCallListDTO:
    """DTO for outbound call list responses."""
    calls: List[OutboundCallSummaryDTO]
    total_count: int
    page: int
    limit: int
    has_next: bool
    has_previous: bool
    
    # Summary statistics
    pending_calls_count: int = 0
    completed_calls_count: int = 0
    successful_calls_count: int = 0
    total_duration_minutes: float = 0.0
    average_success_rate: float = 0.0

    @classmethod
    def from_entities(cls, calls: List, total_count: int, page: int, limit: int) -> 'OutboundCallListDTO':
        """Create list DTO from domain entities."""
        call_dtos = [OutboundCallSummaryDTO.from_entity(call) for call in calls]
        
        # Calculate summary statistics
        pending_count = len([c for c in call_dtos if c.status == CallStatus.PENDING])
        completed_count = len([c for c in call_dtos if c.status == CallStatus.COMPLETED])
        successful_count = len([c for c in call_dtos if c.outcome in [CallOutcome.APPOINTMENT_SCHEDULED, CallOutcome.INTERESTED, CallOutcome.CALLBACK_REQUESTED]])
        total_duration = sum(c.call_duration_minutes for c in call_dtos if c.call_duration_minutes)
        success_rate = (successful_count / completed_count * 100) if completed_count > 0 else 0.0

        return cls(
            calls=call_dtos,
            total_count=total_count,
            page=page,
            limit=limit,
            has_next=(page * limit) < total_count,
            has_previous=page > 1,
            pending_calls_count=pending_count,
            completed_calls_count=completed_count,
            successful_calls_count=successful_count,
            total_duration_minutes=round(total_duration, 2),
            average_success_rate=round(success_rate, 2)
        )


@dataclass
class OutboundCallSearchDTO:
    """DTO for outbound call search criteria."""
    business_id: uuid.UUID
    campaign_id: Optional[uuid.UUID] = None
    status: Optional[CallStatus] = None
    outcome: Optional[CallOutcome] = None
    priority: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    attempted_start: Optional[datetime] = None
    attempted_end: Optional[datetime] = None
    contact_name: Optional[str] = None
    phone_number: Optional[str] = None
    appointment_scheduled: Optional[bool] = None
    follow_up_required: Optional[bool] = None
    min_duration_minutes: Optional[int] = None
    max_duration_minutes: Optional[int] = None
    limit: int = 50
    offset: int = 0
    sort_by: str = "scheduled_for"
    sort_order: str = "asc"  # "asc" or "desc"


# Campaign DTOs
@dataclass
class CampaignSummaryDTO:
    """DTO for campaign summary information."""
    id: uuid.UUID
    name: str
    campaign_type: CampaignType
    status: CampaignStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    total_calls: int = 0
    completed_calls: int = 0
    successful_calls: int = 0
    success_rate: float = 0.0
    average_call_duration: float = 0.0
    appointments_scheduled: int = 0

    @classmethod
    def from_entity(cls, campaign) -> 'CampaignSummaryDTO':
        """Create summary DTO from domain entity."""
        return cls(
            id=campaign.id,
            name=campaign.name,
            campaign_type=campaign.campaign_type,
            status=campaign.status,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            total_calls=campaign.total_calls,
            completed_calls=campaign.completed_calls,
            successful_calls=campaign.successful_calls,
            success_rate=campaign.get_success_rate(),
            average_call_duration=campaign.get_average_call_duration(),
            appointments_scheduled=campaign.appointments_scheduled
        )


# Mobile-optimized DTOs
@dataclass
class MobileOutboundCallDTO:
    """DTO optimized for mobile app consumption."""
    id: uuid.UUID
    contact_name: str
    phone_number: str
    status: CallStatus
    priority: int
    scheduled_for: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    outcome: Optional[CallOutcome] = None
    campaign_name: Optional[str] = None
    appointment_scheduled: bool = False
    follow_up_required: bool = False
    next_retry_at: Optional[datetime] = None

    @classmethod
    def from_entity(cls, call, campaign_name: Optional[str] = None) -> 'MobileOutboundCallDTO':
        """Create mobile DTO from domain entity."""
        duration = None
        if call.result and call.result.call_duration_seconds:
            duration = round(call.result.call_duration_seconds / 60, 2)

        return cls(
            id=call.id,
            contact_name=call.recipient.contact_name,
            phone_number=call.recipient.phone_number,
            status=call.status,
            priority=call.priority,
            scheduled_for=call.scheduled_for,
            duration_minutes=duration,
            outcome=call.result.outcome if call.result else None,
            campaign_name=campaign_name,
            appointment_scheduled=call.result.appointment_scheduled if call.result else False,
            follow_up_required=call.result.follow_up_required if call.result else False,
            next_retry_at=call.next_retry_at
        )


@dataclass
class OutboundCallStatisticsDTO:
    """DTO for outbound call statistics and analytics."""
    business_id: uuid.UUID
    date_range_start: datetime
    date_range_end: datetime
    
    # Call counts
    total_calls: int = 0
    pending_calls: int = 0
    completed_calls: int = 0
    failed_calls: int = 0
    
    # Success metrics
    successful_calls: int = 0
    appointments_scheduled: int = 0
    callbacks_requested: int = 0
    overall_success_rate: float = 0.0
    
    # Duration statistics
    total_duration_minutes: float = 0.0
    average_duration_minutes: float = 0.0
    median_duration_minutes: float = 0.0
    
    # Outcome breakdown
    outcome_breakdown: Dict[str, int] = None
    
    # Campaign performance
    campaign_performance: List[Dict[str, Any]] = None
    
    # Time-based analytics
    peak_calling_hours: List[Dict[str, Any]] = None
    daily_performance: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.outcome_breakdown is None:
            self.outcome_breakdown = {}
        if self.campaign_performance is None:
            self.campaign_performance = []
        if self.peak_calling_hours is None:
            self.peak_calling_hours = []
        if self.daily_performance is None:
            self.daily_performance = []


@dataclass
class CallQueueStatusDTO:
    """DTO for call queue status information."""
    business_id: uuid.UUID
    total_pending: int = 0
    high_priority_pending: int = 0
    scheduled_next_hour: int = 0
    scheduled_today: int = 0
    overdue_calls: int = 0
    retry_due_calls: int = 0
    active_sessions: int = 0
    queue_processing_rate: float = 0.0  # calls per hour
    estimated_completion_time: Optional[datetime] = None 