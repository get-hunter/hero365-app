"""
Base Voice Agent

Abstract base class for all Hero365 voice agents using OpenAI's voice agents SDK.
Provides common functionality and integration with Hero365's business logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from agents import Agent, tool
from app.infrastructure.config.dependency_injection import get_container


class BaseVoiceAgent(ABC):
    """Base class for all Hero365 voice agents using OpenAI agents SDK"""
    
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
    
    @abstractmethod
    def get_handoffs(self) -> List[Agent]:
        """Return list of agents this agent can hand off to"""
        pass
    
    def create_agent(self) -> Agent:
        """Create OpenAI agent instance with tools and instructions"""
        return Agent(
            name=self.get_agent_name(),
            instructions=self.get_instructions(),
            tools=self.get_tools(),
            handoffs=self.get_handoffs()
        )
    
    def get_agent_name(self) -> str:
        """Get agent name for identification"""
        business_name = self.business_context.get('name', 'Hero365')
        return f"{business_name} Assistant"
    
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
        
        return f"Hi {user_name}! I'm your {business_name} assistant. How can I help you today?"
    
    def is_driving_mode(self) -> bool:
        """Check if user is in driving mode for safety"""
        return self.user_context.get('is_driving', False)
    
    def get_safety_mode(self) -> bool:
        """Check if safety mode is enabled"""
        return self.user_context.get('safety_mode', True) 