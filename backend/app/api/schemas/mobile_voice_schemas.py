"""
Pydantic schemas for Mobile Voice Integration API
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class NetworkType(str, Enum):
    """Network connection types"""
    wifi = "wifi"
    cellular = "cellular"
    unknown = "unknown"


class SessionType(str, Enum):
    """Voice session types"""
    general = "general"
    contact_management = "contact_management"
    job_scheduling = "job_scheduling"
    estimate_creation = "estimate_creation"
    emergency = "emergency"


class VoiceSessionStatus(str, Enum):
    """Voice session status"""
    active = "active"
    inactive = "inactive"
    connecting = "connecting"
    disconnected = "disconnected"
    error = "error"


class MobileDeviceInfo(BaseModel):
    """Mobile device information"""
    model_config = ConfigDict(from_attributes=True)
    
    device_name: Optional[str] = Field(None, description="Device name (e.g., 'John's iPhone')")
    device_model: str = Field(..., description="Device model (e.g., 'iPhone 15 Pro')")
    os_version: str = Field(..., description="Operating system version")
    app_version: str = Field(..., description="Hero365 app version")
    network_type: NetworkType = Field(default=NetworkType.unknown, description="Network connection type")
    battery_level: Optional[float] = Field(None, ge=0, le=1, description="Battery level (0.0 to 1.0)")
    is_low_power_mode: bool = Field(default=False, description="Whether device is in low power mode")
    screen_brightness: Optional[float] = Field(None, ge=0, le=1, description="Screen brightness (0.0 to 1.0)")
    available_storage_gb: Optional[float] = Field(None, description="Available storage in GB")


class VoiceSessionRequest(BaseModel):
    """Request to start a voice session"""
    model_config = ConfigDict(from_attributes=True)
    
    device_info: MobileDeviceInfo = Field(..., description="Mobile device information")
    session_type: SessionType = Field(default=SessionType.general, description="Type of voice session")
    preferred_agent: Optional[str] = Field(None, description="Preferred agent to start with")
    language: Optional[str] = Field("en-US", description="Preferred language for voice interaction")
    background_audio_enabled: bool = Field(default=True, description="Whether background audio is enabled")
    max_duration_minutes: Optional[int] = Field(60, le=480, description="Maximum session duration in minutes (0 means unlimited)")
    user_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User voice preferences")
    
    @field_validator('max_duration_minutes')
    @classmethod
    def validate_max_duration_minutes(cls, v):
        """Validate max_duration_minutes allowing 0 for unlimited"""
        if v is None:
            return 60  # default
        if v == 0:
            return None  # unlimited session
        if v < 1:
            raise ValueError("max_duration_minutes must be 0 (unlimited) or >= 1")
        return v


class VoiceSessionResponse(BaseModel):
    """Response when starting a voice session"""
    model_config = ConfigDict(from_attributes=True)
    
    session_id: str = Field(..., description="Unique session identifier")
    room_name: str = Field(..., description="LiveKit room name")
    access_token: str = Field(..., description="LiveKit access token for mobile app")
    livekit_url: str = Field(..., description="LiveKit server URL")
    voice_config: Dict[str, Any] = Field(..., description="Voice pipeline configuration")
    agent_capabilities: List[str] = Field(..., description="Available agent capabilities")
    session_expires_at: datetime = Field(..., description="Session expiration time")
    status: VoiceSessionStatus = Field(..., description="Current session status")


class ConversationEntry(BaseModel):
    """Single conversation entry"""
    model_config = ConfigDict(from_attributes=True)
    
    timestamp: datetime = Field(..., description="Message timestamp")
    participant_type: str = Field(..., description="'user' or 'agent'")
    content: str = Field(..., description="Message content")
    agent_name: Optional[str] = Field(None, description="Agent name if participant is agent")
    confidence: Optional[float] = Field(None, description="Speech recognition confidence")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class VoiceSessionStatusResponse(BaseModel):
    """Voice session status response"""
    model_config = ConfigDict(from_attributes=True)
    
    session_id: str = Field(..., description="Session identifier")
    status: VoiceSessionStatus = Field(..., description="Current session status")
    started_at: datetime = Field(..., description="Session start time")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    current_agent: str = Field(..., description="Currently active agent")
    function_calls_count: int = Field(..., description="Number of function calls made")
    voice_interactions_count: int = Field(..., description="Number of voice interactions")
    errors_count: int = Field(..., description="Number of errors encountered")
    recent_conversation: List[ConversationEntry] = Field(..., description="Recent conversation entries")
    room_active: bool = Field(..., description="Whether LiveKit room is active")


class DeviceState(BaseModel):
    """Current device state"""
    model_config = ConfigDict(from_attributes=True)
    
    is_foreground: bool = Field(default=True, description="Whether app is in foreground")
    is_locked: bool = Field(default=False, description="Whether device is locked")
    network_type: NetworkType = Field(default=NetworkType.unknown, description="Current network type")
    battery_level: Optional[float] = Field(None, ge=0, le=1, description="Current battery level")
    is_charging: bool = Field(default=False, description="Whether device is charging")
    volume_level: Optional[float] = Field(None, ge=0, le=1, description="Device volume level")


class VoicePreferences(BaseModel):
    """Voice interaction preferences"""
    model_config = ConfigDict(from_attributes=True)
    
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0, description="TTS voice speed")
    voice_pitch: float = Field(default=1.0, ge=0.5, le=2.0, description="TTS voice pitch")
    noise_cancellation: bool = Field(default=True, description="Enable noise cancellation")
    echo_cancellation: bool = Field(default=True, description="Enable echo cancellation")
    auto_gain_control: bool = Field(default=True, description="Enable automatic gain control")
    silence_timeout_ms: int = Field(default=3000, ge=1000, le=10000, description="Silence timeout in milliseconds")
    response_timeout_ms: int = Field(default=10000, ge=5000, le=30000, description="Response timeout in milliseconds")


class PerformanceMetrics(BaseModel):
    """Performance metrics from mobile app"""
    model_config = ConfigDict(from_attributes=True)
    
    audio_latency_ms: Optional[float] = Field(None, description="Audio latency in milliseconds")
    network_latency_ms: Optional[float] = Field(None, description="Network latency in milliseconds")
    packet_loss_rate: Optional[float] = Field(None, ge=0, le=1, description="Packet loss rate")
    jitter_ms: Optional[float] = Field(None, description="Network jitter in milliseconds")
    cpu_usage_percent: Optional[float] = Field(None, ge=0, le=100, description="CPU usage percentage")
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB")
    battery_drain_rate: Optional[float] = Field(None, description="Battery drain rate per hour")


class SessionStateUpdate(BaseModel):
    """Update session state from mobile app"""
    model_config = ConfigDict(from_attributes=True)
    
    device_state: Optional[DeviceState] = Field(None, description="Current device state")
    voice_preferences: Optional[VoicePreferences] = Field(None, description="Updated voice preferences")
    performance_metrics: Optional[PerformanceMetrics] = Field(None, description="Performance metrics")
    user_feedback: Optional[str] = Field(None, description="User feedback about the session")


# Use VoiceSessionStatusResponse as the main status model


class AgentCapability(BaseModel):
    """Agent capability information"""
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., description="Agent display name")
    description: str = Field(..., description="Agent description")
    capabilities: List[str] = Field(..., description="List of agent capabilities")
    specialized: bool = Field(default=True, description="Whether this is a specialized agent")
    availability: str = Field(default="available", description="Agent availability status")


class WebRTCStats(BaseModel):
    """WebRTC connection statistics"""
    model_config = ConfigDict(from_attributes=True)
    
    connection_state: str = Field(..., description="WebRTC connection state")
    ice_connection_state: str = Field(..., description="ICE connection state")
    bytes_sent: int = Field(default=0, description="Total bytes sent")
    bytes_received: int = Field(default=0, description="Total bytes received")
    packets_sent: int = Field(default=0, description="Total packets sent")
    packets_received: int = Field(default=0, description="Total packets received")
    packets_lost: int = Field(default=0, description="Total packets lost")
    round_trip_time_ms: Optional[float] = Field(None, description="Round trip time in milliseconds")
    audio_level: Optional[float] = Field(None, ge=0, le=1, description="Audio level (0.0 to 1.0)")


class SessionAnalytics(BaseModel):
    """Session analytics and insights"""
    model_config = ConfigDict(from_attributes=True)
    
    session_id: str = Field(..., description="Session identifier")
    total_duration_seconds: float = Field(..., description="Total session duration")
    voice_interaction_count: int = Field(..., description="Number of voice interactions")
    function_calls_count: int = Field(..., description="Number of function calls")
    agents_used: List[str] = Field(..., description="List of agents used in session")
    most_used_features: List[str] = Field(..., description="Most frequently used features")
    error_count: int = Field(..., description="Number of errors encountered")
    user_satisfaction_score: Optional[float] = Field(None, ge=1, le=5, description="User satisfaction score (1-5)")
    network_quality_score: Optional[float] = Field(None, ge=0, le=1, description="Average network quality")
    audio_quality_score: Optional[float] = Field(None, ge=0, le=1, description="Average audio quality")


class MobilePushNotification(BaseModel):
    """Push notification for mobile app"""
    model_config = ConfigDict(from_attributes=True)
    
    session_id: str = Field(..., description="Associated session ID")
    notification_type: str = Field(..., description="Type of notification")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional notification data")
    priority: str = Field(default="normal", description="Notification priority (normal, high)")
    expires_at: Optional[datetime] = Field(None, description="Notification expiration time")


class OfflineQueueItem(BaseModel):
    """Item in offline queue for when connectivity is restored"""
    model_config = ConfigDict(from_attributes=True)
    
    item_id: str = Field(..., description="Unique item identifier")
    item_type: str = Field(..., description="Type of queued item")
    data: Dict[str, Any] = Field(..., description="Item data")
    created_at: datetime = Field(..., description="When item was queued")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    priority: int = Field(default=1, description="Processing priority (1=high, 5=low)")


class MobileErrorReport(BaseModel):
    """Error report from mobile app"""
    model_config = ConfigDict(from_attributes=True)
    
    session_id: Optional[str] = Field(None, description="Associated session ID")
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    stack_trace: Optional[str] = Field(None, description="Error stack trace")
    device_info: MobileDeviceInfo = Field(..., description="Device information")
    app_state: Dict[str, Any] = Field(..., description="App state when error occurred")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    user_action: Optional[str] = Field(None, description="User action that triggered the error")


class VoiceCommandRecognition(BaseModel):
    """Voice command recognition result"""
    model_config = ConfigDict(from_attributes=True)
    
    recognized_text: str = Field(..., description="Recognized speech text")
    confidence_score: float = Field(..., ge=0, le=1, description="Recognition confidence")
    intent: Optional[str] = Field(None, description="Detected intent")
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted entities")
    language: str = Field(default="en-US", description="Detected language")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    alternative_transcriptions: List[str] = Field(default_factory=list, description="Alternative transcriptions")


class AgentResponseMetadata(BaseModel):
    """Metadata for agent responses"""
    model_config = ConfigDict(from_attributes=True)
    
    agent_name: str = Field(..., description="Name of responding agent")
    response_time_ms: float = Field(..., description="Response generation time")
    function_calls_made: List[str] = Field(default_factory=list, description="Function calls made during response")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Response confidence")
    context_used: List[str] = Field(default_factory=list, description="Context elements used")
    tokens_used: Optional[int] = Field(None, description="LLM tokens used")
    cost_estimate: Optional[float] = Field(None, description="Estimated cost in USD") 