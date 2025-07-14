"""
Base agent class for all Hero365 voice agents with shared business logic.
"""

from typing import Dict, Any, Optional
from abc import ABC
from .context_manager import ContextManager
from ...infrastructure.config.dependency_injection import get_container
import logging

logger = logging.getLogger(__name__)


class BaseVoiceAgent(ABC):
    """
    Base class for all Hero365 voice agents using OpenAI Agents SDK.
    
    Provides shared business logic, context management, and infrastructure integration
    while allowing each specialist agent to implement their own OpenAI Agents SDK agent.
    """
    
    def __init__(self, 
                 name: str,
                 instructions: str,
                 context_manager: ContextManager,
                 tools: Optional[list] = None):
        """
        Initialize base voice agent with shared infrastructure.
        
        Args:
            name: Agent name for identification
            instructions: Agent-specific instructions (used by subclasses)
            context_manager: Shared context manager instance
            tools: Unused parameter (kept for compatibility)
        """
        self.agent_name = name
        self.instructions = instructions
        self.context_manager = context_manager
        self.container = get_container()
        
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
        """
        Helper to get user and business IDs from context.
        
        Returns:
            Tuple of (user_id, business_id)
        """
        context = await self.get_context()
        user_id = context.get("user_id", "")
        business_id = context.get("business_id", "")
        return user_id, business_id
    
    async def get_user_info(self) -> Dict[str, Any]:
        """
        Get user information from context.
        
        Returns:
            Dictionary containing user information
        """
        context = await self.get_context()
        return {
            "user_id": context.get("user_id", ""),
            "user_name": context.get("user_name", ""),
            "business_id": context.get("business_id", ""),
            "business_name": context.get("business_name", ""),
            "user_role": context.get("user_role", ""),
        }
    
    async def log_agent_action(self, action: str, details: Dict[str, Any] = None):
        """
        Log agent action for debugging and monitoring.
        
        Args:
            action: Description of the action taken
            details: Optional additional details about the action
        """
        try:
            log_data = {
                "agent": self.agent_name,
                "action": action,
                "timestamp": "now",  # Could use proper timestamp
                **(details or {})
            }
            
            await self.update_context({
                "last_agent_action": log_data
            })
            
            logger.info(f"{self.agent_name}: {action}", extra=details)
            
        except Exception as e:
            logger.error(f"Error logging action for {self.agent_name}: {e}")
    
    def get_agent_capabilities(self) -> list[str]:
        """
        Get list of capabilities for this agent.
        Should be overridden by subclasses.
        
        Returns:
            List of capability descriptions
        """
        return [
            "Context-aware assistance",
            "Business operation support", 
            "Natural conversation"
        ] 