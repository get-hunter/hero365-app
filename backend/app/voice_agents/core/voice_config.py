"""
Voice Agent Configuration

This module provides configuration classes for voice agents,
including model settings, voice preferences, and capability definitions.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class AgentType(Enum):
    """Voice agent types"""
    PERSONAL = "personal"
    SALES = "sales"
    SUPPORT = "support"
    TECHNICAL = "technical"


class VoiceModel(Enum):
    """Available voice models"""
    SONIC_2 = "sonic-2"
    SONIC_1 = "sonic-1"


class VoiceProfile(Enum):
    """Voice profiles for different use cases"""
    PROFESSIONAL = "f786b574-daa5-4673-aa0c-cbe3e8534c02"  # Professional male voice
    FRIENDLY = "a0e99841-438c-4a64-b679-ae501e7d6091"      # Friendly female voice
    AUTHORITATIVE = "b7d50908-b17c-442d-ad8d-810c63997ed9"  # Authoritative voice
    CASUAL = "79a125e8-cd45-4c13-8a67-188112f4dd22"        # Casual voice


@dataclass
class VoiceAgentConfig:
    """Configuration for voice agents"""
    
    # Agent identification
    agent_type: AgentType
    agent_name: str
    
    # Voice settings
    voice_model: VoiceModel = VoiceModel.SONIC_2
    voice_profile: VoiceProfile = VoiceProfile.PROFESSIONAL
    language: str = "multi"
    
    # LLM settings
    llm_model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    # Session settings
    max_conversation_duration: int = 1800  # 30 minutes
    auto_disconnect_timeout: int = 300     # 5 minutes of silence
    enable_noise_cancellation: bool = True
    enable_turn_detection: bool = True
    
    # Capabilities
    tools_enabled: List[str] = field(default_factory=list)
    max_tools_per_turn: int = 3
    
    # Security settings
    enable_conversation_recording: bool = True
    enable_analytics: bool = True
    require_user_consent: bool = True
    
    # Custom settings
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "agent_type": self.agent_type.value,
            "agent_name": self.agent_name,
            "voice_model": self.voice_model.value,
            "voice_profile": self.voice_profile.value,
            "language": self.language,
            "llm_model": self.llm_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "max_conversation_duration": self.max_conversation_duration,
            "auto_disconnect_timeout": self.auto_disconnect_timeout,
            "enable_noise_cancellation": self.enable_noise_cancellation,
            "enable_turn_detection": self.enable_turn_detection,
            "tools_enabled": self.tools_enabled,
            "max_tools_per_turn": self.max_tools_per_turn,
            "enable_conversation_recording": self.enable_conversation_recording,
            "enable_analytics": self.enable_analytics,
            "require_user_consent": self.require_user_consent,
            "custom_config": self.custom_config
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "VoiceAgentConfig":
        """Create configuration from dictionary"""
        return cls(
            agent_type=AgentType(config_dict["agent_type"]),
            agent_name=config_dict["agent_name"],
            voice_model=VoiceModel(config_dict.get("voice_model", "sonic-2")),
            voice_profile=VoiceProfile(config_dict.get("voice_profile", VoiceProfile.PROFESSIONAL.value)),
            language=config_dict.get("language", "multi"),
            llm_model=config_dict.get("llm_model", "gpt-4o-mini"),
            temperature=config_dict.get("temperature", 0.7),
            max_tokens=config_dict.get("max_tokens"),
            max_conversation_duration=config_dict.get("max_conversation_duration", 1800),
            auto_disconnect_timeout=config_dict.get("auto_disconnect_timeout", 300),
            enable_noise_cancellation=config_dict.get("enable_noise_cancellation", True),
            enable_turn_detection=config_dict.get("enable_turn_detection", True),
            tools_enabled=config_dict.get("tools_enabled", []),
            max_tools_per_turn=config_dict.get("max_tools_per_turn", 3),
            enable_conversation_recording=config_dict.get("enable_conversation_recording", True),
            enable_analytics=config_dict.get("enable_analytics", True),
            require_user_consent=config_dict.get("require_user_consent", True),
            custom_config=config_dict.get("custom_config", {})
        )


@dataclass
class PersonalAgentConfig(VoiceAgentConfig):
    """Configuration specific to personal voice agents"""
    
    def __post_init__(self):
        self.agent_type = AgentType.PERSONAL
        self.voice_profile = VoiceProfile.FRIENDLY
        self.tools_enabled = [
            "job_management",
            "project_tracking", 
            "invoice_handling",
            "estimate_creation",
            "contact_management",
            "inventory_management",
            "navigation_assistance",
            "reminder_system"
        ]


@dataclass
class SalesAgentConfig(VoiceAgentConfig):
    """Configuration specific to sales voice agents"""
    
    def __post_init__(self):
        self.agent_type = AgentType.SALES
        self.voice_profile = VoiceProfile.PROFESSIONAL
        self.tools_enabled = [
            "lead_qualification",
            "product_catalog",
            "pricing_tools",
            "estimate_creation",
            "appointment_scheduling",
            "crm_integration"
        ]


@dataclass  
class SupportAgentConfig(VoiceAgentConfig):
    """Configuration specific to support voice agents"""
    
    def __post_init__(self):
        self.agent_type = AgentType.SUPPORT
        self.voice_profile = VoiceProfile.FRIENDLY
        self.tools_enabled = [
            "job_rescheduling",
            "issue_resolution",
            "feedback_collection",
            "appointment_management",
            "service_history"
        ]


# Default configurations
DEFAULT_PERSONAL_CONFIG = PersonalAgentConfig(
    agent_type=AgentType.PERSONAL,
    agent_name="Hero365 Personal Assistant",
    max_conversation_duration=3600,  # 1 hour for personal use
)

DEFAULT_SALES_CONFIG = SalesAgentConfig(
    agent_type=AgentType.SALES,
    agent_name="Hero365 Sales Agent",
    max_conversation_duration=900,   # 15 minutes for sales calls
    temperature=0.8,  # More creative for sales conversations
)

DEFAULT_SUPPORT_CONFIG = SupportAgentConfig(
    agent_type=AgentType.SUPPORT,
    agent_name="Hero365 Support Agent", 
    max_conversation_duration=1200,  # 20 minutes for support calls
) 