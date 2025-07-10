"""
Voice Agent Configuration

Configuration classes and enums for voice agent settings.
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel


class AgentType(str, Enum):
    """Types of voice agents"""
    PERSONAL = "personal"
    OUTBOUND = "outbound"
    SUPPORT = "support"


class VoiceProfile(str, Enum):
    """Voice profile options"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    TECHNICAL = "technical"


class VoiceModel(str, Enum):
    """Voice model options"""
    SONIC_2 = "sonic-2"
    GPT_4O_MINI_TTS = "gpt-4o-mini-tts"
    CARTESIA = "cartesia"


class VoiceConfig(BaseModel):
    """Base voice configuration"""
    agent_type: AgentType
    voice_profile: VoiceProfile = VoiceProfile.PROFESSIONAL
    voice_model: VoiceModel = VoiceModel.GPT_4O_MINI_TTS
    max_conversation_duration: int = 3600  # 1 hour
    enable_noise_cancellation: bool = True
    temperature: float = 0.7
    safety_mode: bool = True
    
    class Config:
        use_enum_values = True


class PersonalAgentConfig(VoiceConfig):
    """Configuration for personal voice agents"""
    agent_type: AgentType = AgentType.PERSONAL
    agent_name: str = "Personal Assistant"
    enable_job_management: bool = True
    enable_project_management: bool = True
    enable_invoice_management: bool = True
    enable_estimate_management: bool = True
    enable_contact_management: bool = True
    enable_navigation: bool = True
    
    
class OutboundAgentConfig(VoiceConfig):
    """Configuration for outbound calling agents"""
    agent_type: AgentType = AgentType.OUTBOUND
    agent_name: str = "Outbound Agent"
    call_purpose: str = "general"
    max_call_duration: int = 1800  # 30 minutes
    enable_call_recording: bool = True
    enable_call_transcription: bool = True 