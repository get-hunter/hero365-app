"""
External Services Infrastructure

Implementations of external service integrations like email, SMS, authentication providers.
Contains adapters for third-party services following the ports and adapters pattern.
"""

from .supabase_auth_adapter import SupabaseAuthAdapter
from .resend_email_adapter import ResendEmailAdapter
from .twilio_sms_adapter import TwilioSMSAdapter
from .livekit_voice_agent_service import LiveKitVoiceAgentService, create_livekit_voice_agent_service
# Voice agent factory is now integrated into the service

__all__ = [
    "SupabaseAuthAdapter",
    "ResendEmailAdapter", 
    "TwilioSMSAdapter",
    "LiveKitVoiceAgentService",
    "create_livekit_voice_agent_service",
] 