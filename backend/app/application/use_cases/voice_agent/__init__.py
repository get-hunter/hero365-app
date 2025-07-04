"""
Voice Agent Use Cases Module

This module contains all voice agent-related use cases following clean architecture principles.
Each use case handles specific aspects of voice interaction management and tool execution.
"""

# Core voice session management
from .start_voice_session_use_case import StartVoiceSessionUseCase
# from .process_voice_command_use_case import ProcessVoiceCommandUseCase - removed
from .end_voice_session_use_case import EndVoiceSessionUseCase

# Personal assistant use cases
from .personal_assistant_tools_use_case import PersonalAssistantToolsUseCase
from .emergency_scheduling_use_case import EmergencySchedulingUseCase
from .voice_field_notes_use_case import VoiceFieldNotesUseCase

# Outbound calling use cases
from .schedule_outbound_call_use_case import ScheduleOutboundCallUseCase
from .campaign_management_use_case import CampaignManagementUseCase

# Helper services
from .voice_agent_helper_service import VoiceAgentHelperService

__all__ = [
    # Core voice session management
    "StartVoiceSessionUseCase",
    # "ProcessVoiceCommandUseCase" removed - using continuous conversation instead
    "EndVoiceSessionUseCase",
    
    # Personal assistant use cases
    "PersonalAssistantToolsUseCase",
    "EmergencySchedulingUseCase", 
    "VoiceFieldNotesUseCase",
    
    # Outbound calling use cases
    "ScheduleOutboundCallUseCase",
    "CampaignManagementUseCase",
    
    # Helper services
    "VoiceAgentHelperService",
] 