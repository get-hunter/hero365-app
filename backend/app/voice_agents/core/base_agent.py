"""
Base Voice Agent for Hero365

This module provides the base class for all Hero365 voice agents,
using the LiveKit Agents framework for voice interactions.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class BaseVoiceAgent(ABC):
    """Base class for all Hero365 voice agents"""
    
    def __init__(self, 
                 business_context: Dict[str, Any],
                 user_context: Optional[Dict[str, Any]] = None,
                 agent_config: Optional[Dict[str, Any]] = None):
        
        self.agent_id = str(uuid.uuid4())
        self.business_context = business_context
        self.user_context = user_context or {}
        self.agent_config = agent_config or {}
        self.created_at = datetime.now()
        
        logger.info(f"Initialized {self.__class__.__name__} agent {self.agent_id}")
    
    @abstractmethod
    def get_tools(self) -> List[Callable]:
        """Return list of tools available to this agent"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt for this agent"""
        pass
    
    @abstractmethod
    async def on_agent_start(self) -> None:
        """Called when agent starts"""
        pass
    
    @abstractmethod
    async def on_agent_stop(self) -> None:
        """Called when agent stops"""
        pass
    
    def get_current_business_id(self) -> str:
        """Get current business ID from context"""
        return self.business_context.get("id", "")
    
    def get_current_user_id(self) -> str:
        """Get current user ID from context"""
        return self.user_context.get("id", "")
    
    def get_business_name(self) -> str:
        """Get business name for personalization"""
        return self.business_context.get("name", "Your Business")
    
    def get_user_name(self) -> str:
        """Get user name for personalization"""
        return self.user_context.get("name", "User")
    
    async def record_interaction(self, 
                               interaction_type: str,
                               details: Dict[str, Any]) -> None:
        """Record agent interaction for analytics"""
        
        interaction_data = {
            "agent_id": self.agent_id,
            "agent_type": self.__class__.__name__,
            "interaction_type": interaction_type,
            "business_id": self.get_current_business_id(),
            "user_id": self.get_current_user_id(),
            "details": details,
            "timestamp": datetime.now()
        }
        
        # TODO: Implement interaction recording with existing activity system
        logger.info(f"Recorded interaction: {interaction_type} for agent {self.agent_id}") 