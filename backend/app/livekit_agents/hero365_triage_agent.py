"""
Hero365 Triage Agent - Handles general inquiries and initial user interactions
Works with the main agent's intelligent routing system
"""

from typing import Dict, Any, Optional, List
from livekit.agents import Agent, function_tool, RunContext
from .tools.hero365_tools_wrapper import Hero365ToolsWrapper
from .config import LiveKitConfig
from ..infrastructure.config.dependency_injection import get_container
import logging

logger = logging.getLogger(__name__)

class Hero365TriageAgent(Agent):
    """Triage agent that handles general inquiries and initial user interactions"""
    
    def __init__(self, config: LiveKitConfig):
        instructions = """
        You are Hero365's general assistant. Your role is to:
        
        1. Handle general inquiries and questions
        2. Provide initial greetings and help
        3. Answer questions about weather, directions, and general business topics
        4. Use available tools to provide helpful information
        5. Provide natural, conversational responses
        
        IMPORTANT:
        - Never mention routing, specialists, or handoffs to users
        - Focus on being helpful and natural
        - If you can't handle a specific request, respond naturally without mentioning limitations
        - Use tools when appropriate to provide accurate information
        """
        
        # Initialize business context manager
        self.config = config
        self.request_history = []
        self.user_preferences = {}
        
        # Initialize tools wrapper
        self.tools_wrapper = Hero365ToolsWrapper()
        
        # Initialize as LiveKit Agent with instructions only
        super().__init__(instructions=instructions)
        
        logger.info("🎯 Triage agent initialized successfully")
    
    def set_business_context(self, business_context_manager):
        """Set business context manager for context-aware operations"""
        if self.tools_wrapper:
            self.tools_wrapper.set_business_context(business_context_manager)
        logger.info("📊 Business context set for triage agent")
    
    @function_tool
    async def get_weather(
        self,
        ctx: RunContext,
        location: Optional[str] = None
    ) -> str:
        """Get current weather information for a location.
        
        Args:
            location: Location to get weather for (optional, uses business location if not provided)
        """
        try:
            if self.tools_wrapper:
                result = await self.tools_wrapper.get_weather(ctx=ctx, location=location)
                return result
            else:
                return "Weather service is not available right now. Please try again later."
                
        except Exception as e:
            logger.error(f"❌ Error getting weather: {e}")
            return f"❌ Error getting weather: {str(e)}"
    
    @function_tool
    async def search_places(
        self,
        ctx: RunContext,
        query: str,
        location: Optional[str] = None
    ) -> str:
        """Search for places and businesses near a location.
        
        Args:
            query: What to search for (e.g., "hardware store", "restaurants")
            location: Location to search near (optional, uses business location if not provided)
        """
        try:
            if self.tools_wrapper:
                result = await self.tools_wrapper.search_places(ctx=ctx, query=query, location=location)
                return result
            else:
                return f"Place search is not available right now. I'd search for '{query}' near your location."
                
        except Exception as e:
            logger.error(f"❌ Error searching places: {e}")
            return f"❌ Error searching places: {str(e)}"
    
    @function_tool
    async def get_directions(
        self,
        ctx: RunContext,
        destination: str,
        origin: Optional[str] = None
    ) -> str:
        """Get directions from origin to destination.
        
        Args:
            destination: Where to go
            origin: Starting point (optional, uses business location if not provided)
        """
        try:
            if self.tools_wrapper:
                result = await self.tools_wrapper.get_directions(ctx=ctx, destination=destination, origin=origin)
                return result
            else:
                return f"Directions service is not available right now. I'd get directions to '{destination}' from your location."
                
        except Exception as e:
            logger.error(f"❌ Error getting directions: {e}")
            return f"❌ Error getting directions: {str(e)}"
    
    @function_tool
    async def web_search(
        self,
        ctx: RunContext,
        query: str
    ) -> str:
        """Search the web for information.
        
        Args:
            query: What to search for
        """
        try:
            if self.tools_wrapper:
                result = await self.tools_wrapper.web_search(ctx=ctx, query=query)
                return result
            else:
                return f"Web search is not available right now. I'd search for '{query}' on the web."
                
        except Exception as e:
            logger.error(f"❌ Error searching web: {e}")
            return f"❌ Error searching web: {str(e)}"
    
    @function_tool
    async def get_business_overview(
        self,
        ctx: RunContext
    ) -> str:
        """Get an overview of the business and current status.
        """
        try:
            if self.tools_wrapper:
                result = await self.tools_wrapper.get_business_analytics(ctx=ctx)
                return result
            else:
                return "Business overview is not available right now. I can help you with general questions about your business."
                
        except Exception as e:
            logger.error(f"❌ Error getting business overview: {e}")
            return f"❌ Error getting business overview: {str(e)}"
    
    @function_tool
    async def universal_search(
        self,
        ctx: RunContext,
        query: str
    ) -> str:
        """Search across all business data including contacts, jobs, estimates, and more.
        
        Args:
            query: What to search for
        """
        try:
            if self.tools_wrapper:
                result = await self.tools_wrapper.universal_search(ctx=ctx, query=query)
                return result
            else:
                return f"Universal search is not available right now. I'd search for '{query}' across your business data."
                
        except Exception as e:
            logger.error(f"❌ Error in universal search: {e}")
            return f"❌ Error in universal search: {str(e)}" 