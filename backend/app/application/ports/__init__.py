"""
Application Ports Package

This package contains the abstract interfaces (ports) that define the contracts
for external services and infrastructure components.
"""

from .auth_service import AuthServicePort, AuthUser, AuthToken, AuthResult, AuthProvider
from .email_service import (
    EmailServicePort, EmailMessage, EmailResult, EmailTemplate, 
    EmailAttachment, EmailPriority
)
from .sms_service import SMSServicePort, SMSMessage, SMSResult
from .external_services import (
    WeatherServicePort, RouteOptimizationPort, TravelTimePort
)
from .voice_agent_service import (
    VoiceAgentServicePort, VoiceToolRegistry, VoiceCommandProcessor,
    VoiceAgentTool, VoiceSessionConfig, OutboundCallConfig, 
    VoiceAgentResult, LiveKitRoomConfig
)

__all__ = [
    # Auth Service
    "AuthServicePort",
    "AuthUser", 
    "AuthToken",
    "AuthResult",
    "AuthProvider",
    
    # Email Service
    "EmailServicePort",
    "EmailMessage",
    "EmailResult", 
    "EmailTemplate",
    "EmailAttachment",
    "EmailPriority",
    
    # SMS Service
    "SMSServicePort",
    "SMSMessage",
    "SMSResult",
    
    # External Services
    "WeatherServicePort",
    "RouteOptimizationPort", 
    "TravelTimePort",
    
    # Voice Agent Service
    "VoiceAgentServicePort",
    "VoiceToolRegistry",
    "VoiceCommandProcessor",
    "VoiceAgentTool",
    "VoiceSessionConfig",
    "OutboundCallConfig",
    "VoiceAgentResult",
    "LiveKitRoomConfig",
] 