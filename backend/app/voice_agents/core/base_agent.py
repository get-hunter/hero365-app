"""
Base Voice Agent

Abstract base class for all Hero365 voice agents using OpenAI's Realtime API.
Provides common functionality and integration with Hero365's business logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncIterator
from agents import Agent, function_tool
from agents.voice import VoicePipeline, VoiceWorkflowBase, AudioInput, VoicePipelineConfig
from app.infrastructure.config.dependency_injection import get_container


class BaseVoiceAgent(ABC):
    """Base class for all Hero365 voice agents using OpenAI Realtime API"""
    
    def __init__(self, 
                 business_context: Dict[str, Any],
                 user_context: Dict[str, Any],
                 agent_config: Optional[Dict[str, Any]] = None):
        """
        Initialize base voice agent
        
        Args:
            business_context: Business information and context
            user_context: User information and preferences
            agent_config: Agent-specific configuration
        """
        self.business_context = business_context
        self.user_context = user_context
        self.agent_config = agent_config or {}
        self.container = get_container()
        
    @abstractmethod
    def get_instructions(self) -> str:
        """Return system instructions for the agent"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Any]:
        """Return list of tools available to this agent"""
        pass
    
    def get_handoffs(self) -> List[Agent]:
        """Return list of agents this agent can hand off to (override in subclasses)"""
        return []
    
    def create_agent(self) -> Agent:
        """Create OpenAI agent instance with tools and instructions"""
        return Agent(
            name=self.get_agent_name(),
            instructions=self.get_instructions(),
            tools=self.get_tools(),
            handoffs=self.get_handoffs(),
            model="gpt-4o-mini"  # Use efficient model by default
        )
    
    def create_voice_pipeline(self) -> VoicePipeline:
        """Create voice pipeline for realtime audio processing"""
        from agents.voice import SingleAgentVoiceWorkflow
        
        # Create voice-optimized instructions
        voice_instructions = self._get_voice_optimized_instructions()
        
        # Create voice agent with optimized instructions
        voice_agent = Agent(
            name=self.get_agent_name(),
            instructions=voice_instructions,
            tools=self.get_tools(),
            handoffs=self.get_handoffs(),
            model="gpt-4o-mini-tts"  # Use TTS-optimized model
        )
        
        # Create voice pipeline configuration
        config = VoicePipelineConfig(
            tts_settings=self._get_tts_settings()
        )
        
        # Create workflow and pipeline
        workflow = SingleAgentVoiceWorkflow(voice_agent)
        return VoicePipeline(workflow=workflow, config=config)
    
    def _get_voice_optimized_instructions(self) -> str:
        """Get voice-optimized instructions"""
        base_instructions = self.get_instructions()
        
        voice_optimization = """
[Voice Output Optimization]
Your responses will be delivered as audio, so:
1. Use a friendly, natural tone that sounds conversational when spoken
2. Keep responses concise and clear - ideally 1-2 sentences per key point
3. Avoid technical jargon and complex terminology
4. Use simple, direct language that's easy to understand when heard
5. Provide only essential information to avoid overwhelming the listener
6. Structure responses with natural pauses and clear transitions
"""
        
        return voice_optimization + "\n\n" + base_instructions
    
    def _get_tts_settings(self):
        """Get TTS settings optimized for the agent type"""
        from agents.voice import TTSModelSettings
        
        # Get user preferences
        is_driving = self.is_driving_mode()
        business_name = self.business_context.get('name', 'Hero365')
        
        if is_driving:
            instructions = f"Voice: Clear, calm, and professional for {business_name}. " \
                          "Tone: Reassuring and steady for driving safety. " \
                          "Pace: Moderate speed with clear enunciation. " \
                          "Keep responses brief and direct."
        else:
            instructions = f"Voice: Friendly, warm, and professional for {business_name}. " \
                          "Tone: Helpful and engaging, creating a welcoming atmosphere. " \
                          "Pace: Natural conversational speed with appropriate pauses. " \
                          "Emotion: Supportive and confident."
        
        return TTSModelSettings(instructions=instructions)
    
    def get_agent_name(self) -> str:
        """Get agent name for identification"""
        business_name = self.business_context.get('name', 'Hero365')
        return f"{business_name} {self.__class__.__name__.replace('Agent', '')} Assistant"
    
    def get_business_id(self) -> str:
        """Get current business ID from context"""
        return self.business_context.get('id', '')
    
    def get_user_id(self) -> str:
        """Get current user ID from context"""
        return self.user_context.get('id', '')
    
    def get_personalized_greeting(self) -> str:
        """Generate personalized greeting based on context"""
        user_name = self.user_context.get('name', 'there')
        business_name = self.business_context.get('name', 'Hero365')
        
        if self.is_driving_mode():
            return f"Hi {user_name}! I'm your {business_name} assistant. I'll keep responses brief since you're driving. How can I help?"
        else:
            return f"Hi {user_name}! I'm your {business_name} assistant. How can I help you today?"
    
    def is_driving_mode(self) -> bool:
        """Check if user is in driving mode for safety"""
        return self.user_context.get('is_driving', False)
    
    def get_safety_mode(self) -> bool:
        """Check if safety mode is enabled"""
        return self.user_context.get('safety_mode', True)
    
    def get_context_summary(self) -> str:
        """Get summary of current context for debugging"""
        return f"Business: {self.business_context.get('name', 'Unknown')}, " \
               f"User: {self.user_context.get('name', 'Unknown')}, " \
               f"Driving: {self.is_driving_mode()}" 