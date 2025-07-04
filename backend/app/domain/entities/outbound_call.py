"""
Outbound Call Domain Entity

Core business entity for outbound call management in Hero365.
Handles call scheduling, execution, outcome tracking, and campaign management.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal

from ..enums import CallStatus, CallPurpose, CallOutcome, AgentType
from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError


@dataclass
class CallRecipient:
    """Value object for call recipient information."""
    contact_id: Optional[uuid.UUID] = None
    name: str = ""
    phone_number: str = ""
    email: Optional[str] = None
    preferred_contact_time: Optional[str] = None  # e.g., "morning", "afternoon", "evening"
    time_zone: str = "UTC"
    language: str = "en"
    do_not_call: bool = False
    
    def __post_init__(self):
        """Validate recipient data."""
        if not self.phone_number or not self.phone_number.strip():
            raise DomainValidationError("Phone number is required")
        if self.do_not_call:
            raise BusinessRuleViolationError("Cannot call recipient on do-not-call list")
    
    def format_phone_number(self) -> str:
        """Format phone number for display."""
        # Basic formatting - could be enhanced with proper phone number library
        digits = ''.join(filter(str.isdigit, self.phone_number))
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"1-({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return self.phone_number
    
    def is_business_hours(self, current_time: datetime) -> bool:
        """Check if current time is within business hours for recipient."""
        # Simple business hours check - could be enhanced
        hour = current_time.hour
        if self.preferred_contact_time == "morning":
            return 9 <= hour <= 12
        elif self.preferred_contact_time == "afternoon":
            return 12 <= hour <= 17
        elif self.preferred_contact_time == "evening":
            return 17 <= hour <= 20
        else:
            return 9 <= hour <= 17  # Default business hours


@dataclass
class CallScript:
    """Value object for call script and conversation flow."""
    opening_script: str = ""
    main_script: str = ""
    closing_script: str = ""
    objection_handling: Dict[str, str] = field(default_factory=dict)
    questions: List[str] = field(default_factory=list)
    call_to_action: str = ""
    max_duration_minutes: int = 10
    
    def __post_init__(self):
        """Validate script data."""
        if not self.opening_script or not self.opening_script.strip():
            raise DomainValidationError("Opening script is required")
        if self.max_duration_minutes <= 0:
            raise DomainValidationError("Max duration must be positive")
    
    def get_full_script(self) -> str:
        """Get complete script text."""
        script_parts = []
        if self.opening_script:
            script_parts.append(f"Opening: {self.opening_script}")
        if self.main_script:
            script_parts.append(f"Main: {self.main_script}")
        if self.questions:
            script_parts.append(f"Questions: {', '.join(self.questions)}")
        if self.call_to_action:
            script_parts.append(f"Call to Action: {self.call_to_action}")
        if self.closing_script:
            script_parts.append(f"Closing: {self.closing_script}")
        return " | ".join(script_parts)


@dataclass
class CallAnalytics:
    """Value object for call analytics and performance metrics."""
    dial_attempts: int = 0
    connection_duration_seconds: Optional[int] = None
    talk_time_seconds: Optional[int] = None
    hold_time_seconds: Optional[int] = None
    sentiment_score: Optional[Decimal] = None  # -1.0 to 1.0
    engagement_score: Optional[Decimal] = None  # 0.0 to 1.0
    interruption_count: int = 0
    objections_raised: int = 0
    questions_asked: int = 0
    questions_answered: int = 0
    
    def __post_init__(self):
        """Validate analytics data."""
        if self.dial_attempts < 0:
            raise DomainValidationError("Dial attempts cannot be negative")
        if self.sentiment_score is not None and not (-1.0 <= float(self.sentiment_score) <= 1.0):
            raise DomainValidationError("Sentiment score must be between -1.0 and 1.0")
        if self.engagement_score is not None and not (0.0 <= float(self.engagement_score) <= 1.0):
            raise DomainValidationError("Engagement score must be between 0.0 and 1.0")
    
    def get_talk_time_minutes(self) -> Optional[float]:
        """Get talk time in minutes."""
        if self.talk_time_seconds:
            return round(self.talk_time_seconds / 60, 2)
        return None
    
    def get_connection_rate(self) -> Decimal:
        """Get connection success rate."""
        if self.dial_attempts > 0:
            connected = 1 if self.connection_duration_seconds and self.connection_duration_seconds > 0 else 0
            return Decimal(connected) / Decimal(self.dial_attempts) * Decimal("100")
        return Decimal("0")
    
    def get_engagement_rate(self) -> Decimal:
        """Get engagement rate based on questions answered."""
        if self.questions_asked > 0:
            return Decimal(self.questions_answered) / Decimal(self.questions_asked) * Decimal("100")
        return Decimal("0")


@dataclass
class OutboundCall:
    """
    Outbound Call domain entity representing an automated business call.
    
    This entity contains all business logic for call management,
    scheduling, execution, outcome tracking, and campaign integration.
    """
    
    # Required fields (no defaults)
    id: uuid.UUID
    business_id: uuid.UUID
    purpose: CallPurpose
    status: CallStatus
    recipient: CallRecipient
    script: CallScript
    
    # Optional fields (with defaults)
    campaign_id: Optional[uuid.UUID] = None
    
    # Call configuration
    priority: int = 1  # 1-5, 5 being highest priority
    max_attempts: int = 3
    retry_interval_minutes: int = 60
    
    # Scheduling
    scheduled_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    
    # Execution tracking
    current_attempt: int = 0
    session_id: Optional[uuid.UUID] = None
    livekit_room_name: Optional[str] = None
    
    # Call outcome
    outcome: Optional[CallOutcome] = None
    outcome_notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    
    # Analytics
    analytics: CallAnalytics = field(default_factory=CallAnalytics)
    
    # Audio and conversation
    conversation_transcript: Optional[str] = None
    audio_recording_url: Optional[str] = None
    
    # Metadata
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate call data after initialization."""
        self._validate_call_rules()
    
    def _validate_call_rules(self) -> None:
        """Validate core call business rules."""
        if not self.business_id:
            raise DomainValidationError("Call must belong to a business")
        if self.priority < 1 or self.priority > 5:
            raise DomainValidationError("Priority must be between 1 and 5")
        if self.max_attempts < 1:
            raise DomainValidationError("Max attempts must be positive")
        if self.retry_interval_minutes < 0:
            raise DomainValidationError("Retry interval cannot be negative")
        if self.current_attempt < 0:
            raise DomainValidationError("Current attempt cannot be negative")
    
    @classmethod
    def create_call(
        cls,
        business_id: uuid.UUID,
        purpose: CallPurpose,
        recipient_phone: str,
        recipient_name: str,
        script: CallScript,
        campaign_id: Optional[uuid.UUID] = None,
        contact_id: Optional[uuid.UUID] = None,
        scheduled_time: Optional[datetime] = None,
        priority: int = 1,
        max_attempts: int = 3,
        created_by: str = "system"
    ) -> 'OutboundCall':
        """Create a new outbound call with validation."""
        
        call_id = uuid.uuid4()
        
        recipient = CallRecipient(
            contact_id=contact_id,
            name=recipient_name,
            phone_number=recipient_phone
        )
        
        call = cls(
            id=call_id,
            business_id=business_id,
            campaign_id=campaign_id,
            purpose=purpose,
            status=CallStatus.SCHEDULED,
            recipient=recipient,
            script=script,
            priority=priority,
            max_attempts=max_attempts,
            scheduled_time=scheduled_time or datetime.now(timezone.utc),
            created_by=created_by
        )
        
        return call
    
    def start_call(self, session_id: uuid.UUID, livekit_room_name: str) -> None:
        """Start the outbound call."""
        if self.status != CallStatus.SCHEDULED and self.status != CallStatus.QUEUED:
            raise BusinessRuleViolationError("Call must be scheduled or queued to start")
        
        if self.current_attempt >= self.max_attempts:
            raise BusinessRuleViolationError("Maximum call attempts reached")
        
        self.current_attempt += 1
        self.analytics.dial_attempts += 1
        self.status = CallStatus.DIALING
        self.session_id = session_id
        self.livekit_room_name = livekit_room_name
        self.actual_start_time = datetime.now(timezone.utc)
        self.last_modified = datetime.now(timezone.utc)
    
    def mark_ringing(self) -> None:
        """Mark call as ringing."""
        if self.status != CallStatus.DIALING:
            raise BusinessRuleViolationError("Call must be dialing to mark as ringing")
        
        self.status = CallStatus.RINGING
        self.last_modified = datetime.now(timezone.utc)
    
    def mark_connected(self) -> None:
        """Mark call as connected."""
        if self.status != CallStatus.RINGING:
            raise BusinessRuleViolationError("Call must be ringing to mark as connected")
        
        self.status = CallStatus.CONNECTED
        self.last_modified = datetime.now(timezone.utc)
    
    def mark_in_progress(self) -> None:
        """Mark call as in progress."""
        if self.status != CallStatus.CONNECTED:
            raise BusinessRuleViolationError("Call must be connected to mark as in progress")
        
        self.status = CallStatus.IN_PROGRESS
        self.last_modified = datetime.now(timezone.utc)
    
    def complete_call(self, outcome: CallOutcome, outcome_notes: Optional[str] = None) -> None:
        """Complete the call with outcome."""
        if self.status not in [CallStatus.IN_PROGRESS, CallStatus.CONNECTED, CallStatus.RINGING]:
            raise BusinessRuleViolationError("Call must be active to complete")
        
        self.status = CallStatus.COMPLETED
        self.outcome = outcome
        self.outcome_notes = outcome_notes
        self.actual_end_time = datetime.now(timezone.utc)
        self.last_modified = datetime.now(timezone.utc)
        
        # Calculate analytics
        if self.actual_start_time and self.actual_end_time:
            duration = (self.actual_end_time - self.actual_start_time).total_seconds()
            self.analytics.connection_duration_seconds = int(duration)
            self.analytics.talk_time_seconds = int(duration)
        
        # Determine if follow-up is needed
        self._determine_follow_up_needed()
    
    def fail_call(self, reason: str) -> None:
        """Mark call as failed."""
        self.status = CallStatus.FAILED
        self.outcome = CallOutcome.NO_RESPONSE
        self.outcome_notes = reason
        self.actual_end_time = datetime.now(timezone.utc)
        self.last_modified = datetime.now(timezone.utc)
        
        # Schedule retry if attempts remaining
        if self.current_attempt < self.max_attempts:
            self._schedule_retry()
    
    def mark_no_answer(self) -> None:
        """Mark call as no answer."""
        self.status = CallStatus.NO_ANSWER
        self.outcome = CallOutcome.NO_RESPONSE
        self.actual_end_time = datetime.now(timezone.utc)
        self.last_modified = datetime.now(timezone.utc)
        
        if self.current_attempt < self.max_attempts:
            self._schedule_retry()
    
    def mark_busy(self) -> None:
        """Mark call as busy."""
        self.status = CallStatus.BUSY
        self.outcome = CallOutcome.NO_RESPONSE
        self.actual_end_time = datetime.now(timezone.utc)
        self.last_modified = datetime.now(timezone.utc)
        
        if self.current_attempt < self.max_attempts:
            self._schedule_retry()
    
    def mark_voicemail(self) -> None:
        """Mark call as reached voicemail."""
        self.status = CallStatus.VOICEMAIL
        self.outcome = CallOutcome.VOICEMAIL_LEFT
        self.actual_end_time = datetime.now(timezone.utc)
        self.last_modified = datetime.now(timezone.utc)
    
    def cancel_call(self, reason: str) -> None:
        """Cancel the call."""
        if self.status in [CallStatus.COMPLETED, CallStatus.FAILED]:
            raise BusinessRuleViolationError("Cannot cancel completed or failed call")
        
        self.status = CallStatus.CANCELLED
        self.outcome_notes = f"Cancelled: {reason}"
        self.last_modified = datetime.now(timezone.utc)
    
    def _schedule_retry(self) -> None:
        """Schedule a retry attempt."""
        if self.current_attempt < self.max_attempts:
            self.status = CallStatus.SCHEDULED
            self.scheduled_time = datetime.now(timezone.utc) + timedelta(minutes=self.retry_interval_minutes)
    
    def _determine_follow_up_needed(self) -> None:
        """Determine if follow-up is needed based on outcome."""
        follow_up_outcomes = [
            CallOutcome.PARTIAL_SUCCESS,
            CallOutcome.CALLBACK_REQUESTED,
            CallOutcome.RESCHEDULED,
            CallOutcome.VOICEMAIL_LEFT
        ]
        
        if self.outcome in follow_up_outcomes:
            self.follow_up_required = True
            # Schedule follow-up based on outcome
            if self.outcome == CallOutcome.CALLBACK_REQUESTED:
                self.follow_up_date = datetime.now(timezone.utc) + timedelta(hours=2)
            elif self.outcome == CallOutcome.RESCHEDULED:
                self.follow_up_date = datetime.now(timezone.utc) + timedelta(days=1)
            else:
                self.follow_up_date = datetime.now(timezone.utc) + timedelta(days=3)
    
    def update_conversation_transcript(self, transcript: str) -> None:
        """Update conversation transcript."""
        self.conversation_transcript = transcript
        self.last_modified = datetime.now(timezone.utc)
    
    def update_analytics(self, analytics: CallAnalytics) -> None:
        """Update call analytics."""
        self.analytics = analytics
        self.last_modified = datetime.now(timezone.utc)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the call."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.last_modified = datetime.now(timezone.utc)
    
    def is_due_for_retry(self) -> bool:
        """Check if call is due for retry."""
        if self.status != CallStatus.SCHEDULED:
            return False
        if self.current_attempt >= self.max_attempts:
            return False
        if self.scheduled_time:
            return datetime.now(timezone.utc) >= self.scheduled_time
        return True
    
    def is_completed(self) -> bool:
        """Check if call is completed."""
        return self.status in [CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.CANCELLED]
    
    def is_successful(self) -> bool:
        """Check if call was successful."""
        return self.outcome == CallOutcome.SUCCESSFUL
    
    def is_high_priority(self) -> bool:
        """Check if call is high priority."""
        return self.priority >= 4
    
    def is_emergency(self) -> bool:
        """Check if call is emergency priority."""
        return self.priority == 5
    
    def get_call_duration_minutes(self) -> Optional[float]:
        """Get call duration in minutes."""
        if self.actual_start_time and self.actual_end_time:
            duration = self.actual_end_time - self.actual_start_time
            return round(duration.total_seconds() / 60, 2)
        return None
    
    def get_status_display(self) -> str:
        """Get human-readable status."""
        return self.status.get_display()
    
    def get_purpose_display(self) -> str:
        """Get human-readable purpose."""
        return self.purpose.get_display()
    
    def get_outcome_display(self) -> str:
        """Get human-readable outcome."""
        if self.outcome:
            return self.outcome.get_display()
        return "Pending"
    
    def get_recipient_display(self) -> str:
        """Get formatted recipient information."""
        return f"{self.recipient.name} ({self.recipient.format_phone_number()})"
    
    def get_call_summary(self) -> Dict[str, Any]:
        """Get call summary for reporting."""
        return {
            "id": str(self.id),
            "purpose": self.get_purpose_display(),
            "recipient": self.get_recipient_display(),
            "status": self.get_status_display(),
            "outcome": self.get_outcome_display(),
            "attempts": self.current_attempt,
            "duration_minutes": self.get_call_duration_minutes(),
            "talk_time_minutes": self.analytics.get_talk_time_minutes(),
            "connection_rate": float(self.analytics.get_connection_rate()),
            "engagement_rate": float(self.analytics.get_engagement_rate()),
            "sentiment_score": float(self.analytics.sentiment_score) if self.analytics.sentiment_score else None,
            "follow_up_required": self.follow_up_required,
            "follow_up_date": self.follow_up_date.isoformat() if self.follow_up_date else None,
            "created_date": self.created_date.isoformat(),
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "priority": self.priority,
            "tags": self.tags
        } 