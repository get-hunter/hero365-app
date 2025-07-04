"""
External Services Infrastructure

Implementations of external service integrations like email, SMS, authentication providers.
Contains adapters for third-party services following the ports and adapters pattern.
"""

from .supabase_auth_adapter import SupabaseAuthAdapter
from .resend_email_adapter import ResendEmailAdapter
from .twilio_sms_adapter import TwilioSMSAdapter
from .livekit_voice_agent_adapter import LiveKitVoiceAgentAdapter, create_livekit_voice_agent_adapter
from .voice_agent_factory import VoiceAgentFactory, create_voice_agent_factory

__all__ = [
    "SupabaseAuthAdapter",
    "ResendEmailAdapter", 
    "TwilioSMSAdapter",
    "LiveKitVoiceAgentAdapter",
    "create_livekit_voice_agent_adapter",
    "VoiceAgentFactory",
    "create_voice_agent_factory",
] 