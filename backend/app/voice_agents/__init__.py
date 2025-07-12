"""
Voice Agents Module

This module provides voice agent capabilities for Hero365 using a triage-based system.
Includes specialized agents for different business domains and intelligent routing.
"""

from .core.base_agent import BaseVoiceAgent
from .tools.hero365_tools import Hero365Tools

__all__ = [
    "BaseVoiceAgent",
    "Hero365Tools"
] 