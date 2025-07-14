"""
Base agent class for all Hero365 voice agents with shared context management.
"""

from typing import Dict, Any, List, Optional, Type
from abc import ABC, abstractmethod
# from openai_agents import Agent, tool
from .context_manager import ContextManager
from ...infrastructure.config.dependency_injection import get_container
import asyncio
import logging

logger = logging.getLogger(__name__)


class BaseVoiceAgent(ABC):
    """Base class for all Hero365 voice agents with shared context"""
    
    def __init__(self, 
                 name: str,
                 instructions: str,
                 context_manager: ContextManager,
                 tools: List[Any] = None,
                 model: str = "gpt-4o"):
        """
        Initialize base voice agent with shared context management.
        
        Args:
            name: Agent name for identification
            instructions: Agent-specific instructions
            context_manager: Shared context manager instance
            tools: List of tools available to this agent
            model: OpenAI model to use
        """
        self.context_manager = context_manager
        self.container = get_container()
        self.agent_name = name
        self.base_instructions = instructions
        
    def _build_system_prompt(self, instructions: str) -> str:
        """Build comprehensive system prompt with context"""
        return f"""
        You are {self.agent_name}, a specialist AI assistant for Hero365, an AI-native ERP system 
        for home services businesses and independent contractors.
        
        CORE INSTRUCTIONS:
        {instructions}
        
        BEHAVIOR GUIDELINES:
        - Be conversational and natural - you're speaking, not typing
        - Keep responses concise but informative (under 100 words when possible)
        - Always consider the user's current context and location
        - Seamlessly hand off to other specialists when needed
        - Never mention the handoff process to the user
        - Maintain conversation continuity across agents
        - Use the user's name naturally in conversation
        - Be proactive and helpful, anticipating needs
        
        CONTEXT AWARENESS:
        - You have access to the user's business information
        - You understand their role and permissions
        - You know their location and recent activities
        - You can reference previous conversations
        - You have access to real-time business data
        
        VOICE OPTIMIZATION:
        - Speak naturally, as if in person
        - Use contractions and casual language
        - Avoid technical jargon unless necessary
        - Provide step-by-step guidance for complex tasks
        - Ask clarifying questions when needed
        """
    
    async def get_context(self) -> Dict[str, Any]:
        """Get current context for agent"""
        try:
            return await self.context_manager.get_current_context()
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return {}
    
    async def update_context(self, updates: Dict[str, Any]):
        """Update context with new information"""
        try:
            await self.context_manager.update_context(updates)
        except Exception as e:
            logger.error(f"Error updating context: {e}")
    
    async def get_user_and_business_ids(self) -> tuple[str, str]:
        """Helper to get user and business IDs from context"""
        context = await self.get_context()
        user_id = context.get("user_id", "")
        business_id = context.get("business_id", "")
        return user_id, business_id
    
    async def format_success_response(self, 
                                     action: str, 
                                     result: Any, 
                                     message: str) -> str:
        """Format success response for voice output"""
        # Update context with action taken
        await self.update_context({
            "conversation": {
                "agent": self.agent_name,
                "action": action,
                "result": str(result),
                "timestamp": asyncio.get_event_loop().time()
            }
        })
        
        return message
    
    async def format_error_response(self, 
                                   action: str, 
                                   error: Exception, 
                                   fallback_message: str) -> str:
        """Format error response for voice output"""
        logger.error(f"Error in {self.agent_name} during {action}: {error}")
        
        # Update context with error
        await self.update_context({
            "conversation": {
                "agent": self.agent_name,
                "action": action,
                "error": str(error),
                "timestamp": asyncio.get_event_loop().time()
            }
        })
        
        return fallback_message
    
    @abstractmethod
    def get_handoffs(self) -> List[Any]:
        """Return list of agents this agent can hand off to"""
        return []
    
    # @tool
    async def get_agent_status(self) -> str:
        """Get current status of this agent"""
        context = await self.get_context()
        return f"""
        I'm {self.agent_name}, currently helping {context.get('user_name', 'you')} 
        with {context.get('business_name', 'your business')} operations.
        
        I can help with tasks related to my specialty area.
        """
        
    def get_agent_capabilities(self) -> List[str]:
        """Get list of capabilities for this agent"""
        return [
            "Context-aware assistance",
            "Business operation support", 
            "Natural conversation",
            "Handoff to specialists"
        ] 