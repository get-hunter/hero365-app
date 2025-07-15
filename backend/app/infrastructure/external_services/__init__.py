"""
External Services Infrastructure

Implementations of external service integrations like email, SMS, authentication providers.
Contains adapters for third-party services following the ports and adapters pattern.
"""

from .supabase_auth_adapter import SupabaseAuthAdapter
from .resend_email_adapter import ResendEmailAdapter
from .twilio_sms_adapter import TwilioSMSAdapter
from .openai_embedding_adapter import OpenAIEmbeddingAdapter

__all__ = [
    "SupabaseAuthAdapter",
    "ResendEmailAdapter", 
    "TwilioSMSAdapter",
    "OpenAIEmbeddingAdapter",
] 