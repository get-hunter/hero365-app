"""
Hero365 Triage Agent - Main routing agent for all user requests
Routes users to appropriate specialists based on their needs
"""

from typing import Dict, Any, Optional, List
from livekit.agents import function_tool, RunContext
from .base_agent import Hero365BaseAgent
from .tools.hero365_tools_wrapper import Hero365ToolsWrapper
from ..infrastructure.config.dependency_injection import get_container
import logging

logger = logging.getLogger(__name__)

class Hero365TriageAgent(Hero365BaseAgent):
    """Main triage agent that routes user requests to appropriate specialists"""
    
    def __init__(self, config):
        instructions = """
        You are Hero365's intelligent triage agent. Your role is to:
        
        1. UNDERSTAND what the user wants to do
        2. ROUTE them to the appropriate specialist or handle simple requests directly
        3. COLLECT necessary information before routing
        4. PROVIDE helpful guidance throughout the process
        
        ROUTING GUIDELINES:
        - Contact-related: Creating, searching, updating contacts → Use contact tools directly
        - Job-related: Creating, scheduling, tracking jobs → Use job tools directly
        - Estimate-related: Creating, managing estimates → Use estimate tools directly
        - Calendar/Schedule-related: Appointments, availability → Use scheduling tools
        - Weather/Location: Handle directly with available tools
        - General questions: Answer directly or search universally
        - Analytics/Reports: Use business analytics tools
        
        CONVERSATION FLOW:
        1. Greet new users warmly
        2. Ask clarifying questions if needed
        3. Confirm understanding before taking action
        4. Use appropriate tools to fulfill requests
        5. Provide clear next steps
        
        IMPORTANT:
        - You have access to all Hero365 tools directly
        - No need to "route" to other agents - you can handle everything
        - Focus on getting the job done efficiently
        - Always confirm important actions before executing
        - Provide natural, conversational responses
        """
        
        super().__init__(
            name="Hero365 Triage Agent",
            instructions=instructions,
            tools=[
                self.route_to_contact_management,
                self.route_to_job_management,
                self.route_to_estimate_management,
                self.route_to_scheduling,
                self.handle_general_inquiry,
                self.provide_system_help,
            ]
        )
        
        self.request_history = []
        self.user_preferences = {}
        
        # Initialize tools wrapper
        self.tools_wrapper = Hero365ToolsWrapper()
        
    def get_available_tools(self):
        """Get list of available tools from the wrapper"""
        return self.tools_wrapper.get_available_tools()
    
    async def initialize_agent(self, ctx: RunContext):
        """Initialize triage agent"""
        logger.info("🎯 Hero365 Triage Agent initialized")
        
        # Generate contextual greeting
        greeting = await self.get_contextual_greeting()
        
        # Provide initial greeting and capabilities
        await ctx.session.generate_reply(
            instructions=f"""
            {greeting}
            
            I'm here to help you manage your business operations efficiently. 
            I can help you with contacts, jobs, estimates, scheduling, weather, 
            directions, and much more. 
            
            What would you like to work on today?
            """
        )
    
    async def cleanup_agent(self, ctx: RunContext):
        """Clean up triage agent"""
        logger.info("👋 Hero365 Triage Agent cleaned up")
    
    async def process_message(self, ctx: RunContext, message: str) -> str:
        """Process user message and determine appropriate action"""
        try:
            # Track request
            self.request_history.append({
                "message": message,
                "timestamp": logger.info("Processing message"),
                "session_id": ctx.session_id if hasattr(ctx, 'session_id') else None
            })
            
            # Analyze message intent
            intent = await self.analyze_message_intent(message)
            
            # Handle based on intent
            if intent == "greeting":
                return await self.handle_greeting()
            elif intent == "help":
                return await self.provide_help_information()
            elif intent == "contact":
                return await self.route_to_contact_management(ctx, message, "general")
            elif intent == "job":
                return await self.route_to_job_management(ctx, message, "general")
            elif intent == "estimate":
                return await self.route_to_estimate_management(ctx, message, "general")
            elif intent == "scheduling":
                return await self.route_to_scheduling(ctx, message, "general")
            elif intent == "weather":
                return await self.hero365_tools.get_weather(ctx)
            elif intent == "search":
                search_query = await self.extract_search_query(message)
                return await self.hero365_tools.universal_search(ctx, search_query)
            else:
                return await self.handle_general_inquiry(ctx, message)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I apologize, but I encountered an error. Could you please rephrase your request?"
    
    async def analyze_message_intent(self, message: str) -> str:
        """Analyze user message to determine intent"""
        message_lower = message.lower()
        
        # Greeting patterns
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return "greeting"
        
        # Help patterns
        if any(word in message_lower for word in ["help", "what can you do", "capabilities", "assist"]):
            return "help"
        
        # Contact patterns
        if any(word in message_lower for word in ["contact", "customer", "client", "phone", "email"]):
            return "contact"
        
        # Job patterns
        if any(word in message_lower for word in ["job", "work", "task", "project", "install", "repair"]):
            return "job"
        
        # Estimate patterns
        if any(word in message_lower for word in ["estimate", "quote", "proposal", "price", "cost"]):
            return "estimate"
        
        # Scheduling patterns
        if any(word in message_lower for word in ["schedule", "appointment", "calendar", "book", "time"]):
            return "scheduling"
        
        # Weather patterns
        if any(word in message_lower for word in ["weather", "temperature", "rain", "forecast"]):
            return "weather"
        
        # Search patterns
        if any(word in message_lower for word in ["search", "find", "look for", "locate"]):
            return "search"
        
        return "general"
    
    async def extract_search_query(self, message: str) -> str:
        """Extract search query from message"""
        # Simple extraction - in production, use more sophisticated NLP
        search_words = ["search for", "find", "look for", "locate", "search"]
        message_lower = message.lower()
        
        for word in search_words:
            if word in message_lower:
                return message_lower.replace(word, "").strip()
        
        return message
    
    async def handle_greeting(self) -> str:
        """Handle greeting messages"""
        return await self.get_contextual_greeting()
    
    @function_tool
    async def route_to_contact_management(
        self,
        ctx: RunContext,
        user_request: str,
        action_type: str,
        additional_info: Optional[str] = None
    ) -> str:
        """Handle contact management requests.
        
        Args:
            user_request: The user's original request
            action_type: Type of contact action (create, search, update, etc.)
            additional_info: Any additional context or information
        """
        try:
            logger.info(f"🔄 Handling contact management: {action_type}")
            
            request_lower = user_request.lower()
            
            # Determine specific action
            if any(word in request_lower for word in ["create", "add", "new"]):
                return "I'll help you create a new contact. I'll need the contact's name and either a phone number or email address. What's the contact's name?"
            
            elif any(word in request_lower for word in ["search", "find", "look"]):
                return "I'll help you search for contacts. What name, phone number, or email should I search for?"
            
            elif any(word in request_lower for word in ["list", "show", "all"]):
                return await self.hero365_tools.search_contacts(ctx, "", 10)
            
            else:
                return "I can help you with contact management. Would you like to create a new contact, search for existing contacts, or something else?"
                
        except Exception as e:
            logger.error(f"Error in contact management: {e}")
            return "I encountered an issue with contact management. Please try again or be more specific about what you need."
    
    @function_tool
    async def route_to_job_management(
        self,
        ctx: RunContext,
        user_request: str,
        action_type: str,
        additional_info: Optional[str] = None
    ) -> str:
        """Handle job management requests.
        
        Args:
            user_request: The user's original request
            action_type: Type of job action (create, schedule, track, etc.)
            additional_info: Any additional context or information
        """
        try:
            logger.info(f"🔄 Handling job management: {action_type}")
            
            request_lower = user_request.lower()
            
            # Determine specific action
            if any(word in request_lower for word in ["create", "add", "new", "schedule"]):
                return "I'll help you create a new job. What's the job title or description?"
            
            elif any(word in request_lower for word in ["upcoming", "next", "scheduled"]):
                return await self.hero365_tools.get_upcoming_jobs(ctx, 7)
            
            elif any(word in request_lower for word in ["today", "today's"]):
                return await self.hero365_tools.get_upcoming_jobs(ctx, 1)
            
            elif any(word in request_lower for word in ["search", "find", "look"]):
                return "What job would you like me to search for?"
            
            else:
                return "I can help you with job management. Would you like to create a new job, view upcoming jobs, or search for specific jobs?"
                
        except Exception as e:
            logger.error(f"Error in job management: {e}")
            return "I encountered an issue with job management. Please try again or be more specific about what you need."
    
    @function_tool
    async def route_to_estimate_management(
        self,
        ctx: RunContext,
        user_request: str,
        action_type: str,
        additional_info: Optional[str] = None
    ) -> str:
        """Handle estimate management requests.
        
        Args:
            user_request: The user's original request
            action_type: Type of estimate action (create, update, send, etc.)
            additional_info: Any additional context or information
        """
        try:
            logger.info(f"🔄 Handling estimate management: {action_type}")
            
            request_lower = user_request.lower()
            
            # Determine specific action
            if any(word in request_lower for word in ["create", "add", "new"]):
                return "I'll help you create a new estimate. What's the estimate title or what work needs to be quoted?"
            
            elif any(word in request_lower for word in ["pending", "waiting", "outstanding"]):
                return "Let me check your pending estimates..."
            
            elif any(word in request_lower for word in ["search", "find", "look"]):
                return "What estimate would you like me to search for?"
            
            else:
                return "I can help you with estimate management. Would you like to create a new estimate, check pending estimates, or search for specific estimates?"
                
        except Exception as e:
            logger.error(f"Error in estimate management: {e}")
            return "I encountered an issue with estimate management. Please try again or be more specific about what you need."
    
    @function_tool
    async def route_to_scheduling(
        self,
        ctx: RunContext,
        user_request: str,
        action_type: str,
        additional_info: Optional[str] = None
    ) -> str:
        """Handle scheduling requests.
        
        Args:
            user_request: The user's original request
            action_type: Type of scheduling action (book, check, reschedule, etc.)
            additional_info: Any additional context or information
        """
        try:
            logger.info(f"🔄 Handling scheduling: {action_type}")
            
            request_lower = user_request.lower()
            
            # Determine specific action
            if any(word in request_lower for word in ["book", "schedule", "appointment"]):
                return "I'll help you schedule an appointment. What type of appointment do you need to book?"
            
            elif any(word in request_lower for word in ["today", "today's", "schedule"]):
                return "Let me check today's schedule for you..."
            
            elif any(word in request_lower for word in ["available", "availability", "free"]):
                return "What date would you like me to check availability for?"
            
            else:
                return "I can help you with scheduling. Would you like to book an appointment, check today's schedule, or check availability for a specific date?"
                
        except Exception as e:
            logger.error(f"Error in scheduling: {e}")
            return "I encountered an issue with scheduling. Please try again or be more specific about what you need."
    
    @function_tool
    async def handle_general_inquiry(
        self,
        ctx: RunContext,
        user_request: str,
        inquiry_type: str = "general"
    ) -> str:
        """Handle general inquiries that don't fit specific categories.
        
        Args:
            user_request: The user's request
            inquiry_type: Type of inquiry (weather, directions, search, etc.)
        """
        try:
            logger.info(f"🔍 Handling general inquiry: {inquiry_type}")
            
            request_lower = user_request.lower()
            
            # Weather inquiries
            if any(word in request_lower for word in ["weather", "temperature", "rain", "forecast"]):
                return await self.hero365_tools.get_weather(ctx)
            
            # Direction inquiries
            elif any(word in request_lower for word in ["directions", "navigate", "route", "how to get"]):
                return "Where would you like directions to?"
            
            # Search inquiries
            elif any(word in request_lower for word in ["search", "find", "look for"]):
                search_query = await self.extract_search_query(user_request)
                return await self.hero365_tools.universal_search(ctx, search_query)
            
            # Analytics inquiries
            elif any(word in request_lower for word in ["analytics", "report", "revenue", "performance"]):
                return await self.hero365_tools.get_business_analytics(ctx)
            
            # General web search
            elif any(word in request_lower for word in ["what is", "tell me about", "information about"]):
                return await self.hero365_tools.web_search(ctx, user_request)
            
            else:
                return f"I understand you're asking about {inquiry_type}. Could you be more specific about what you need help with? I can assist with contacts, jobs, estimates, scheduling, weather, directions, and more."
                
        except Exception as e:
            logger.error(f"Error handling general inquiry: {e}")
            return "I encountered an issue with your request. Could you please rephrase or be more specific about what you need help with?"
    
    @function_tool
    async def provide_system_help(self, ctx: RunContext) -> str:
        """Provide comprehensive help information about the system."""
        help_info = await self.provide_help_information()
        
        additional_help = """
        
        QUICK EXAMPLES:
        • "Create a contact for John Smith" - I'll guide you through creating a contact
        • "What jobs do I have tomorrow?" - I'll show your upcoming jobs
        • "Create an estimate for kitchen remodel" - I'll help you create an estimate
        • "What's the weather like?" - I'll get current weather information
        • "Search for plumber contacts" - I'll search your contacts
        • "Show me business analytics" - I'll provide business insights
        
        Just speak naturally and I'll understand what you need!
        """
        
        return help_info + additional_help
    
    def get_capabilities(self) -> List[str]:
        """Get triage agent specific capabilities"""
        return [
            "Intelligent request routing",
            "Contact management",
            "Job management",
            "Estimate creation and management",
            "Scheduling and calendar management",
            "Weather information",
            "Location services and directions",
            "Universal search across all data",
            "Business analytics and reporting",
            "Web search for general information",
            "Natural language understanding",
            "Context-aware responses",
        ] 