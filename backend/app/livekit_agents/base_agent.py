"""
Base Agent Class for Hero365 LiveKit Agents
Provides common functionality and Hero365-specific context
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from livekit.agents import Agent, RunContext
from .tools.hero365_tools_wrapper import Hero365ToolsWrapper
from .config import config
from ..infrastructure.config.dependency_injection import get_container
import logging

logger = logging.getLogger(__name__)

class Hero365BaseAgent(Agent, ABC):
    """Base class for all Hero365 agents with common functionality"""
    
    def __init__(self, name: str, instructions: str, tools: Optional[List] = None):
        # Initialize with Hero365-specific instructions
        hero365_context = f"""
        You are {name}, part of the Hero365 AI-native ERP system for blue-collar businesses.
        
        CONTEXT:
        - Hero365 serves construction, plumbing, electrical, and home service businesses
        - Users are contractors, technicians, and business owners
        - Focus on practical, actionable responses
        - Use industry-appropriate language and terminology
        - Be helpful, professional, and efficient
        
        CAPABILITIES:
        - Contact management (create, search, update contacts)
        - Job management (create, schedule, track jobs)
        - Estimate creation and management
        - Scheduling and calendar management
        - Weather information for job planning
        - Location services and directions
        - Universal search across all business data
        - Business analytics and reporting
        
        INSTRUCTIONS:
        {instructions}
        
        IMPORTANT GUIDELINES:
        - Always confirm actions before executing them
        - Provide clear, concise responses
        - Use emojis appropriately for better UX
        - Ask for clarification if request is ambiguous
        - Prioritize user safety and business efficiency
        - Use professional but friendly tone
        - Be patient with users who may not be tech-savvy
        - Provide step-by-step guidance when needed
        """
        
        # Initialize tools
        all_tools = tools or []
        self.hero365_tools = Hero365ToolsWrapper()
        
        # Add all Hero365 tools
        all_tools.extend([
            self.hero365_tools.create_contact,
            self.hero365_tools.search_contacts,
            self.hero365_tools.create_job,
            self.hero365_tools.get_upcoming_jobs,
            self.hero365_tools.create_estimate,
            self.hero365_tools.get_weather,
            self.hero365_tools.search_places,
            self.hero365_tools.get_directions,
            self.hero365_tools.universal_search,
            self.hero365_tools.get_business_analytics,
            self.hero365_tools.web_search,
        ])
        
        super().__init__(
            instructions=hero365_context,
            tools=all_tools
        )
        
        self.agent_name = name
        self.session_context: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, Any]] = []
    
    async def on_enter(self, ctx: RunContext):
        """Called when agent becomes active"""
        logger.info(f"🎯 {self.agent_name} activated")
        
        # Initialize session context
        self.session_context = {
            "agent_name": self.agent_name,
            "session_id": getattr(ctx, 'session_id', None),
            "user_id": getattr(ctx, 'user_data', {}).get("user_id") if hasattr(ctx, 'user_data') else None,
            "business_id": getattr(ctx, 'user_data', {}).get("business_id") if hasattr(ctx, 'user_data') else None,
            "activation_time": logger.info(f"🎯 Agent activated at {logger.info}"),
        }
        
        # Call agent-specific initialization
        await self.initialize_agent(ctx)
    
    async def on_exit(self, ctx: RunContext):
        """Called when agent is deactivated"""
        logger.info(f"👋 {self.agent_name} deactivated")
        await self.cleanup_agent(ctx)
    
    @abstractmethod
    async def initialize_agent(self, ctx: RunContext):
        """Agent-specific initialization logic"""
        pass
    
    @abstractmethod
    async def cleanup_agent(self, ctx: RunContext):
        """Agent-specific cleanup logic"""
        pass
    
    async def get_session_context(self) -> Dict[str, Any]:
        """Get current session context"""
        return self.session_context.copy()
    
    async def update_session_context(self, updates: Dict[str, Any]):
        """Update session context"""
        self.session_context.update(updates)
        logger.debug(f"Context updated for {self.agent_name}: {updates}")
    
    async def add_to_conversation_history(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add message to conversation history"""
        entry = {
            "role": role,
            "content": content,
            "timestamp": logger.info(f"Adding to conversation history"),
            "agent": self.agent_name,
            "metadata": metadata or {}
        }
        self.conversation_history.append(entry)
        
        # Keep only last 50 messages to prevent memory issues
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    async def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    async def handle_user_message(self, ctx: RunContext, message: str) -> str:
        """Handle user message with common processing"""
        try:
            # Add user message to history
            await self.add_to_conversation_history("user", message)
            
            # Process message with agent-specific logic
            response = await self.process_message(ctx, message)
            
            # Add response to history
            await self.add_to_conversation_history("assistant", response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling user message in {self.agent_name}: {e}")
            error_response = f"I apologize, but I encountered an error while processing your request. Please try again or rephrase your message."
            await self.add_to_conversation_history("assistant", error_response, {"error": str(e)})
            return error_response
    
    @abstractmethod
    async def process_message(self, ctx: RunContext, message: str) -> str:
        """Process user message - implemented by specific agents"""
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.agent_name,
            "type": self.__class__.__name__,
            "capabilities": self.get_capabilities(),
            "active_tools": len(self.tools) if hasattr(self, 'tools') else 0,
            "conversation_length": len(self.conversation_history),
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities - can be overridden by subclasses"""
        return [
            "Contact management",
            "Job management", 
            "Estimate creation",
            "Weather information",
            "Location services",
            "Universal search",
            "Business analytics",
            "Web search",
        ]
    
    async def format_response_for_voice(self, response: str) -> str:
        """Format response for voice output"""
        # Remove excessive formatting that doesn't work well with TTS
        formatted = response.replace("**", "").replace("*", "")
        
        # Replace bullet points with natural language
        formatted = formatted.replace("•", "").replace("-", "")
        
        # Add natural pauses for better speech flow
        formatted = formatted.replace("\n", ". ")
        formatted = formatted.replace(". .", ".")
        formatted = formatted.replace(":..", ":")
        
        # Ensure proper sentence endings
        if formatted and not formatted.endswith(('.', '!', '?')):
            formatted += "."
        
        return formatted.strip()
    
    async def get_contextual_greeting(self) -> str:
        """Get contextual greeting based on time and user context"""
        import datetime
        current_hour = datetime.datetime.now().hour
        
        if current_hour < 12:
            greeting = "Good morning"
        elif current_hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        return f"{greeting}! I'm {self.agent_name.replace('Hero365 ', '')}, your Hero365 assistant. How can I help you today?"
    
    async def provide_help_information(self) -> str:
        """Provide help information about agent capabilities"""
        capabilities = self.get_capabilities()
        help_text = f"I'm {self.agent_name} and I can help you with:\n"
        
        for i, capability in enumerate(capabilities, 1):
            help_text += f"{i}. {capability}\n"
        
        help_text += "\nJust tell me what you need help with, and I'll take care of it!"
        return help_text 