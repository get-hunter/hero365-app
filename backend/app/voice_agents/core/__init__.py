"""
Voice Agents Core Module

Base classes and utilities for voice agent implementations.
"""

from .base_agent import BaseVoiceAgent
from .voice_config import VoiceConfig, AgentType

__all__ = [
    "BaseVoiceAgent",
    "VoiceConfig",
    "AgentType"
] 