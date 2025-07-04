"""
Voice Session Domain Entity

Core business entity for voice agent session management in Hero365.
Handles voice conversation lifecycle, context management, and session analytics.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal

from ..enums import VoiceSessionStatus, AgentType
from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError


@dataclass
class VoiceSessionAnalytics:
    """Value object for voice session analytics."""
    total_commands: int = 0
    successful_commands: int = 0
    failed_commands: int = 0
    average_response_time: Optional[Decimal] = None
    total_duration_seconds: Optional[int] = None
    interruption_count: int = 0
    sentiment_score: Optional[Decimal] = None  # -1.0 to 1.0
    confidence_score: Optional[Decimal] = None  # 0.0 to 1.0
    tools_used: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate analytics data."""
        if self.total_commands < 0:
            raise DomainValidationError("Total commands cannot be negative")
        if self.successful_commands < 0:
            raise DomainValidationError("Successful commands cannot be negative")
        if self.failed_commands < 0:
            raise DomainValidationError("Failed commands cannot be negative")
        if self.successful_commands + self.failed_commands > self.total_commands:
            raise DomainValidationError("Sum of successful and failed commands cannot exceed total")
        if self.interruption_count < 0:
            raise DomainValidationError("Interruption count cannot be negative")
        if self.sentiment_score is not None and not (-1.0 <= float(self.sentiment_score) <= 1.0):
            raise DomainValidationError("Sentiment score must be between -1.0 and 1.0")
        if self.confidence_score is not None and not (0.0 <= float(self.confidence_score) <= 1.0):
            raise DomainValidationError("Confidence score must be between 0.0 and 1.0")
    
    def get_success_rate(self) -> Decimal:
        """Calculate command success rate."""
        if self.total_commands > 0:
            return Decimal(self.successful_commands) / Decimal(self.total_commands) * Decimal("100")
        return Decimal("0")
    
    def get_average_response_time_ms(self) -> Optional[int]:
        """Get average response time in milliseconds."""
        if self.average_response_time:
            return int(self.average_response_time * 1000)
        return None
    
    def add_command_result(self, success: bool, response_time_ms: int):
        """Add a command result to analytics."""
        self.total_commands += 1
        if success:
            self.successful_commands += 1
        else:
            self.failed_commands += 1
        
        # Update average response time
        if self.average_response_time is None:
            self.average_response_time = Decimal(response_time_ms) / Decimal("1000")
        else:
            total_time = self.average_response_time * Decimal(self.total_commands - 1)
            new_time = Decimal(response_time_ms) / Decimal("1000")
            self.average_response_time = (total_time + new_time) / Decimal(self.total_commands)


@dataclass
class VoiceSessionContext:
    """Value object for voice session context."""
    business_id: uuid.UUID
    user_id: str
    agent_type: AgentType
    current_location: Optional[str] = None
    current_job_id: Optional[uuid.UUID] = None
    current_contact_id: Optional[uuid.UUID] = None
    current_project_id: Optional[uuid.UUID] = None
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    conversation_state: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate context data."""
        if not self.business_id:
            raise DomainValidationError("Business ID is required")
        if not self.user_id:
            raise DomainValidationError("User ID is required")
    
    def update_current_job(self, job_id: Optional[uuid.UUID]):
        """Update current job context."""
        self.current_job_id = job_id
    
    def update_current_contact(self, contact_id: Optional[uuid.UUID]):
        """Update current contact context."""
        self.current_contact_id = contact_id
    
    def update_location(self, location: Optional[str]):
        """Update current location."""
        self.current_location = location
    
    def set_conversation_state(self, key: str, value: Any):
        """Set conversation state value."""
        self.conversation_state[key] = value
    
    def get_conversation_state(self, key: str) -> Any:
        """Get conversation state value."""
        return self.conversation_state.get(key)


@dataclass
class VoiceSession:
    """
    Voice Session domain entity representing an active voice conversation.
    
    This entity contains all business logic for voice session management,
    command processing, context tracking, and session analytics.
    """
    
    # Required fields
    id: uuid.UUID
    business_id: uuid.UUID
    user_id: str
    agent_type: AgentType
    status: VoiceSessionStatus
    
    # Session configuration
    livekit_room_name: str
    livekit_room_token: Optional[str] = None
    session_timeout_minutes: int = 60  # Default 1 hour
    
    # Context and tracking
    context: VoiceSessionContext = field(default_factory=lambda: VoiceSessionContext)
    analytics: VoiceSessionAnalytics = field(default_factory=VoiceSessionAnalytics)
    
    # Session lifecycle
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Voice data
    commands_processed: List[uuid.UUID] = field(default_factory=list)
    conversation_transcript: Optional[str] = None
    audio_recording_url: Optional[str] = None
    
    # Session settings
    voice_enabled: bool = True
    background_mode: bool = False  # For mobile background processing
    emergency_mode: bool = False
    
    # Metadata
    session_notes: Optional[str] = None
    error_log: List[str] = field(default_factory=list)
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate session data after initialization."""
        self._validate_session_rules()
        # Set context if not provided
        if not hasattr(self.context, 'business_id'):
            self.context = VoiceSessionContext(
                business_id=self.business_id,
                user_id=self.user_id,
                agent_type=self.agent_type
            )
    
    def _validate_session_rules(self) -> None:
        """Validate core session business rules."""
        if not self.business_id:
            raise DomainValidationError("Session must belong to a business")
        if not self.user_id:
            raise DomainValidationError("Session must belong to a user")
        if not self.livekit_room_name:
            raise DomainValidationError("LiveKit room name is required")
        if self.session_timeout_minutes <= 0:
            raise DomainValidationError("Session timeout must be positive")
    
    @classmethod
    def create_session(
        cls,
        business_id: uuid.UUID,
        user_id: str,
        agent_type: AgentType,
        livekit_room_name: str,
        livekit_room_token: Optional[str] = None,
        session_timeout_minutes: int = 60,
        background_mode: bool = False,
        emergency_mode: bool = False
    ) -> 'VoiceSession':
        """Create a new voice session with validation."""
        
        session_id = uuid.uuid4()
        
        context = VoiceSessionContext(
            business_id=business_id,
            user_id=user_id,
            agent_type=agent_type
        )
        
        session = cls(
            id=session_id,
            business_id=business_id,
            user_id=user_id,
            agent_type=agent_type,
            status=VoiceSessionStatus.INITIALIZING,
            livekit_room_name=livekit_room_name,
            livekit_room_token=livekit_room_token,
            session_timeout_minutes=session_timeout_minutes,
            context=context,
            background_mode=background_mode,
            emergency_mode=emergency_mode
        )
        
        return session
    
    def start_session(self) -> None:
        """Start the voice session."""
        if self.status != VoiceSessionStatus.INITIALIZING:
            raise BusinessRuleViolationError("Session must be initializing to start")
        
        self.status = VoiceSessionStatus.ACTIVE
        self.started_at = datetime.now(timezone.utc)
        self.last_activity = self.started_at
    
    def end_session(self, reason: Optional[str] = None) -> None:
        """End the voice session."""
        if self.status in [VoiceSessionStatus.ENDED, VoiceSessionStatus.FAILED]:
            raise BusinessRuleViolationError("Session is already ended")
        
        self.status = VoiceSessionStatus.ENDED
        self.ended_at = datetime.now(timezone.utc)
        
        if reason:
            self.session_notes = f"Session ended: {reason}"
        
        # Calculate final analytics
        if self.started_at and self.ended_at:
            duration = (self.ended_at - self.started_at).total_seconds()
            self.analytics.total_duration_seconds = int(duration)
    
    def pause_session(self) -> None:
        """Pause the voice session."""
        if self.status != VoiceSessionStatus.ACTIVE:
            raise BusinessRuleViolationError("Only active sessions can be paused")
        
        self.status = VoiceSessionStatus.PAUSED
        self.last_activity = datetime.now(timezone.utc)
    
    def resume_session(self) -> None:
        """Resume a paused voice session."""
        if self.status != VoiceSessionStatus.PAUSED:
            raise BusinessRuleViolationError("Only paused sessions can be resumed")
        
        self.status = VoiceSessionStatus.ACTIVE
        self.last_activity = datetime.now(timezone.utc)
    
    def fail_session(self, error_message: str) -> None:
        """Mark session as failed with error."""
        self.status = VoiceSessionStatus.FAILED
        self.ended_at = datetime.now(timezone.utc)
        self.error_log.append(f"[{self.ended_at}] Session failed: {error_message}")
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
    
    def is_expired(self) -> bool:
        """Check if session has expired."""
        if self.status in [VoiceSessionStatus.ENDED, VoiceSessionStatus.FAILED]:
            return True
        
        timeout_threshold = self.started_at + timedelta(minutes=self.session_timeout_minutes)
        return datetime.now(timezone.utc) > timeout_threshold
    
    def is_idle(self, idle_minutes: int = 10) -> bool:
        """Check if session is idle."""
        if self.status != VoiceSessionStatus.ACTIVE:
            return False
        
        idle_threshold = self.last_activity + timedelta(minutes=idle_minutes)
        return datetime.now(timezone.utc) > idle_threshold
    
    def add_command(self, command_id: uuid.UUID, success: bool, response_time_ms: int) -> None:
        """Add a processed command to the session."""
        self.commands_processed.append(command_id)
        self.analytics.add_command_result(success, response_time_ms)
        self.update_activity()
    
    def add_error(self, error_message: str) -> None:
        """Add an error to the session log."""
        timestamp = datetime.now(timezone.utc)
        self.error_log.append(f"[{timestamp}] {error_message}")
    
    def update_transcript(self, new_content: str) -> None:
        """Update conversation transcript."""
        if self.conversation_transcript:
            self.conversation_transcript += f"\n{new_content}"
        else:
            self.conversation_transcript = new_content
        
        self.update_activity()
    
    def enable_emergency_mode(self) -> None:
        """Enable emergency mode for urgent actions."""
        self.emergency_mode = True
        self.session_timeout_minutes = 120  # Extend timeout for emergencies
    
    def disable_emergency_mode(self) -> None:
        """Disable emergency mode."""
        self.emergency_mode = False
        self.session_timeout_minutes = 60  # Reset to default
    
    def get_session_duration(self) -> Optional[timedelta]:
        """Get session duration."""
        if self.started_at:
            end_time = self.ended_at or datetime.now(timezone.utc)
            return end_time - self.started_at
        return None
    
    def get_session_duration_minutes(self) -> Optional[int]:
        """Get session duration in minutes."""
        duration = self.get_session_duration()
        if duration:
            return int(duration.total_seconds() / 60)
        return None
    
    def get_idle_time_minutes(self) -> int:
        """Get idle time in minutes."""
        idle_time = datetime.now(timezone.utc) - self.last_activity
        return int(idle_time.total_seconds() / 60)
    
    def get_status_display(self) -> str:
        """Get human-readable status."""
        return self.status.get_display()
    
    def get_agent_type_display(self) -> str:
        """Get human-readable agent type."""
        return self.agent_type.get_display()
    
    def is_mobile_session(self) -> bool:
        """Check if this is a mobile/personal assistant session."""
        return self.agent_type == AgentType.PERSONAL_ASSISTANT
    
    def is_outbound_session(self) -> bool:
        """Check if this is an outbound caller session."""
        return self.agent_type == AgentType.OUTBOUND_CALLER
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get session analytics summary."""
        return {
            "total_commands": self.analytics.total_commands,
            "success_rate": float(self.analytics.get_success_rate()),
            "average_response_time_ms": self.analytics.get_average_response_time_ms(),
            "duration_minutes": self.get_session_duration_minutes(),
            "interruption_count": self.analytics.interruption_count,
            "sentiment_score": float(self.analytics.sentiment_score) if self.analytics.sentiment_score else None,
            "confidence_score": float(self.analytics.confidence_score) if self.analytics.confidence_score else None,
            "tools_used": self.analytics.tools_used,
            "status": self.get_status_display()
        } 