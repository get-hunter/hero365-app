"""
Voice Agent Service Port

Abstract interface for voice agent services using LiveKit Agents 1.0.
Defines the contract for voice session management, agent creation, and tool integration.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Callable, Protocol
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime

from ...domain.entities.voice_session import VoiceSession
from ...domain.entities.outbound_call import OutboundCall
from ...domain.enums import AgentType, VoiceSessionStatus, CallStatus


class VoiceAgentTool(Protocol):
    """Protocol for voice agent tools."""
    
    @property
    def name(self) -> str:
        """Tool name for voice agent registration."""
        ...
    
    @property
    def description(self) -> str:
        """Tool description for LLM context."""
        ...
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with provided parameters."""
        ...


@dataclass
class VoiceSessionConfig:
    """Configuration for voice session creation."""
    agent_type: AgentType
    business_id: uuid.UUID
    user_id: uuid.UUID
    language: str = "en-US"
    max_duration_minutes: int = 30
    emergency_mode: bool = False
    tools: List[str] = None
    custom_instructions: Optional[str] = None


@dataclass
class OutboundCallConfig:
    """Configuration for outbound call creation."""
    business_id: uuid.UUID
    recipient_phone: str
    recipient_name: str
    
    # SIP Configuration
    sip_trunk_id: Optional[str] = None
    transfer_to: Optional[str] = None
    wait_until_answered: bool = True
    
    # Call Configuration
    campaign_id: Optional[uuid.UUID] = None
    script_instructions: Optional[str] = None
    max_duration_minutes: int = 10
    priority: int = 1
    max_attempts: int = 3
    
    # Agent Configuration
    tools: List[str] = None
    agent_instructions: Optional[str] = None
    
    # Dial Information
    dial_info: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize dial_info if not provided."""
        if self.dial_info is None:
            self.dial_info = {
                "phone_number": self.recipient_phone,
                "transfer_to": self.transfer_to,
                "recipient_name": self.recipient_name,
                "sip_trunk_id": self.sip_trunk_id,
                "wait_until_answered": self.wait_until_answered
            }


@dataclass
class VoiceAgentResult:
    """Result from voice agent operation."""
    success: bool
    session_id: Optional[uuid.UUID] = None
    room_name: Optional[str] = None
    join_token: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class LiveKitRoomConfig:
    """LiveKit room configuration."""
    room_name: str
    participant_identity: str
    participant_name: str
    participant_metadata: Dict[str, Any]
    room_metadata: Dict[str, Any]
    max_participants: int = 10
    empty_timeout_seconds: int = 300
    departure_timeout_seconds: int = 60


class VoiceAgentServicePort(ABC):
    """
    Abstract interface for voice agent services.
    
    This port defines the contract for voice agent operations including
    session management, agent creation, tool registration, and LiveKit integration.
    """
    
    @abstractmethod
    async def create_voice_session(self, config: VoiceSessionConfig) -> VoiceAgentResult:
        """
        Create a new voice session with personal assistant.
        
        Args:
            config: Voice session configuration
            
        Returns:
            VoiceAgentResult with session details and join token
        """
        pass
    
    @abstractmethod
    async def create_outbound_call(self, config: OutboundCallConfig) -> VoiceAgentResult:
        """
        Create a new outbound call session.
        
        Args:
            config: Outbound call configuration
            
        Returns:
            VoiceAgentResult with call details and session info
        """
        pass
    
    @abstractmethod
    async def end_voice_session(self, session_id: uuid.UUID) -> VoiceAgentResult:
        """
        End an active voice session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            VoiceAgentResult with termination status
        """
        pass
    
    @abstractmethod
    async def get_session_status(self, session_id: uuid.UUID) -> VoiceAgentResult:
        """
        Get current status of a voice session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            VoiceAgentResult with session status
        """
        pass
    
    @abstractmethod
    async def register_voice_tool(self, tool: VoiceAgentTool, agent_types: List[AgentType]) -> bool:
        """
        Register a voice tool for use by agents.
        
        Args:
            tool: Voice tool implementation
            agent_types: List of agent types that can use this tool
            
        Returns:
            True if registration successful
        """
        pass
    
    @abstractmethod
    async def unregister_voice_tool(self, tool_name: str) -> bool:
        """
        Unregister a voice tool.
        
        Args:
            tool_name: Name of tool to unregister
            
        Returns:
            True if unregistration successful
        """
        pass
    
    @abstractmethod
    async def get_available_tools(self, agent_type: AgentType) -> List[str]:
        """
        Get list of available tools for an agent type.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            List of available tool names
        """
        pass
    
    @abstractmethod
    async def create_room_token(self, room_config: LiveKitRoomConfig) -> str:
        """
        Create a join token for a LiveKit room.
        
        Args:
            room_config: Room configuration
            
        Returns:
            JWT token for room access
        """
        pass
    
    @abstractmethod
    async def get_service_health(self) -> Dict[str, Any]:
        """
        Check if the voice agent service is healthy.
        
        Returns:
            Health status dictionary
        """
        pass
    
    @abstractmethod
    async def transfer_call(self, session_id: uuid.UUID, transfer_to: str) -> VoiceAgentResult:
        """
        Transfer an active call to another number.
        
        Args:
            session_id: Session identifier
            transfer_to: Phone number to transfer to
            
        Returns:
            VoiceAgentResult with transfer status
        """
        pass
    
    @abstractmethod
    async def hangup_call(self, session_id: uuid.UUID) -> VoiceAgentResult:
        """
        Hang up an active call.
        
        Args:
            session_id: Session identifier
            
        Returns:
            VoiceAgentResult with hangup status
        """
        pass
    
    @abstractmethod
    async def handle_answering_machine(self, session_id: uuid.UUID) -> VoiceAgentResult:
        """
        Handle detection of answering machine/voicemail.
        
        Args:
            session_id: Session identifier
            
        Returns:
            VoiceAgentResult with handling status
        """
        pass


class VoiceToolRegistry(ABC):
    """
    Abstract interface for voice tool registry.
    
    Manages registration and discovery of voice tools for agents.
    """
    
    @abstractmethod
    async def register_tool(self, tool: VoiceAgentTool, agent_types: List[AgentType]) -> bool:
        """Register a voice tool for specific agent types."""
        pass
    
    @abstractmethod
    async def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a voice tool."""
        pass
    
    @abstractmethod
    async def get_tools_for_agent(self, agent_type: AgentType) -> List[VoiceAgentTool]:
        """Get all tools available for an agent type."""
        pass
    
    @abstractmethod
    async def get_tool_by_name(self, tool_name: str) -> Optional[VoiceAgentTool]:
        """Get a specific tool by name."""
        pass


class VoiceCommandProcessor(ABC):
    """
    Abstract interface for voice command processing.
    
    Handles natural language processing and intent recognition for voice commands.
    """
    
    @abstractmethod
    async def process_voice_command(self, 
                                  command_text: str, 
                                  session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a voice command and extract intent and parameters.
        
        Args:
            command_text: Transcribed voice command
            session_context: Current session context
            
        Returns:
            Processed command with intent and parameters
        """
        pass
    
    @abstractmethod
    async def validate_command_parameters(self, 
                                        intent: str, 
                                        parameters: Dict[str, Any]) -> bool:
        """
        Validate command parameters for execution.
        
        Args:
            intent: Recognized intent
            parameters: Extracted parameters
            
        Returns:
            True if parameters are valid
        """
        pass 