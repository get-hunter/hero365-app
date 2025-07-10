"""
Voice Agents Module

This module provides voice agent capabilities for Hero365 using OpenAI's voice agents SDK.
Includes personal agents for business operations and outbound calling agents.
"""

from .core.base_agent import BaseVoiceAgent
from .personal.openai_personal_agent import OpenAIPersonalAgent
from .tools.hero365_tools import Hero365Tools

__all__ = [
    "BaseVoiceAgent",
    "OpenAIPersonalAgent", 
    "Hero365Tools"
] 