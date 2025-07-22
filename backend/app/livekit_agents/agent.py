"""
Hero365 Agent - Organized Single Agent with All Business Tools
Clean architecture with separated tool classes
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from livekit.agents import Agent, function_tool

from .context import BusinessContextManager
from .tools import (
    BusinessInfoTools,
    ContactTools,
    JobTools,
    EstimateTools,
    IntelligenceTools
)

logger = logging.getLogger(__name__)


def log_tool_call(tool_name: str, result: str):
    """Helper function to log tool calls to console"""
    print(f"\n🔧 TOOL CALL: {tool_name}")
    print(f"📋 Result: {result[:200]}..." if len(result) > 200 else f"📋 Result: {result}")
    logger.info(f"Tool {tool_name}: {result[:100]}...")


class Hero365Agent(Agent):
    """
    Hero365 Voice Agent - A powerful AI assistant for home service businesses.
    
    This agent follows best practices in prompt engineering:
    - Clear role definition and tool-oriented approach
    - Structured guidelines for tool usage
    - Context-aware responses with business intelligence
    - Professional yet conversational interaction style
    - Real-time data access through organized tool classes
    """
    
    def __init__(self, business_context: dict = None, user_context: dict = None):
        logger.info("🚀 Hero365Agent.__init__ called")
        
        # Initialize business context
        self.business_context = business_context or {}
        self.user_context = user_context or {}
        
        # Merge contexts for easier access
        if user_context:
            self.business_context.update(user_context)
        
        # Initialize business context manager for tools
        self.business_context_manager: Optional[BusinessContextManager] = None
        
        # Initialize tool classes
        self._initialize_tools()
        
        # Generate comprehensive instructions
        instructions = self._generate_comprehensive_instructions()
        
        # Initialize as LiveKit Agent
        super().__init__(instructions=instructions)
        
        logger.info(f"✅ Hero365Agent initialized with context: {bool(self.business_context)}")
    
    def _initialize_tools(self):
        """Initialize all tool classes with context"""
        self.business_info_tools = BusinessInfoTools(
            self.business_context, 
            self.business_context_manager
        )
        
        self.contact_tools = ContactTools(
            self.business_context, 
            self.business_context_manager
        )
        
        self.job_tools = JobTools(
            self.business_context, 
            self.business_context_manager
        )
        
        self.estimate_tools = EstimateTools(
            self.business_context, 
            self.business_context_manager
        )
        
        self.intelligence_tools = IntelligenceTools(
            self.business_context, 
            self.business_context_manager
        )
    
    def _generate_comprehensive_instructions(self) -> str:
        """Generate comprehensive instructions for the all-in-one agent"""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        base_instructions = f"""
You are the Hero365 AI Assistant, a powerful voice business management assistant for home service companies. You operate exclusively through voice conversation to help users manage their business operations efficiently.

CURRENT DATE AND TIME: Today is {current_date} at {current_time}

YOUR ROLE:
You are the business partner and assistant for a home service professional. You have complete access to their business data and can help them manage contacts, jobs, estimates, and gain business insights. Your goal is to be conversational, helpful, and proactive in managing their business needs.

CONVERSATION GUIDELINES:
- Be natural and conversational - you're speaking, not typing
- NEVER mention technical terms like "tools", "functions", "repositories", or "database queries"
- Instead of saying "I'll search the database", say "Let me check that for you"
- Instead of saying "I'll use the contact tool", say "I'll look up that contact information"
- Always explain what you're doing in business terms: "I'm checking your recent contacts", "Let me pull up your estimates"
- If something takes a moment to process, say "One moment while I check that"
- Be proactive - if you notice something relevant, mention it
- Ask follow-up questions to be more helpful

BUSINESS CAPABILITIES:
You have complete access to help with:

CONTACT MANAGEMENT:
- Find and manage customer information instantly
- Add new contacts with smart suggestions
- Track customer history and interactions
- Get contact details by simply asking "What's John's phone number?"

JOB MANAGEMENT: 
- Track current and upcoming jobs
- Update job statuses and progress
- Schedule new work and manage timelines
- Get overviews like "What jobs do I have this week?"

ESTIMATE MANAGEMENT:
- Review pending and recent estimates
- Get all pending estimates regardless of age
- Update estimate statuses
- Convert approved estimates to invoices
- Track estimate follow-ups and opportunities

BUSINESS INTELLIGENCE:
- Get weather for job planning
- Find nearby suppliers and services
- Provide business analytics and insights
- Search across all your business data instantly

RESPONSE APPROACH:
1. ALWAYS prioritize getting real, current data from the business
2. Be conversational and natural - you're having a spoken conversation
3. If you need to look something up, explain what you're checking in simple terms
4. Provide specific, actionable information
5. Suggest next steps when relevant
6. If you can't help with something specific, suggest the closest thing you can do
7. Keep responses concise but complete - people are listening, not reading
8. Use natural speech patterns with appropriate pauses indicated by punctuation
9. When users ask for "pending estimates", use get_pending_estimates to get ALL pending estimates regardless of age
10. When users ask for "recent estimates", use get_recent_estimates which shows estimates from the last 30 days

CONTEXT AWARENESS:
- Remember this is a voice conversation - format responses for speaking
- Use "and" instead of "&", spell out numbers under 10
- Break up long lists into conversational chunks
- Always acknowledge what the user asked before providing the answer

ERROR HANDLING:
- If something isn't working, explain it simply without technical details
- Offer alternatives when possible
- Never say "error" or mention system issues - instead say things like "I'm having trouble finding that" or "Let me try a different approach"
"""
        
        # Add business-specific context if available
        if self.business_context:
            business_name = self.business_context.get('business_name', 'your business')
            business_type = self.business_context.get('business_type', 'home service business')
            user_name = self.business_context.get('user_name', 'User')
            
            context_instructions = f"""
            
CURRENT SESSION CONTEXT:
- You are speaking with {user_name} from {business_name}
- This is a {business_type}
- You have access to current business information and activity
- You can provide personalized assistance based on their specific needs

BUSINESS METRICS (if available):
- Active Jobs: {self.business_context.get('active_jobs', 'N/A')}
- Pending Estimates: {self.business_context.get('pending_estimates', 'N/A')}
- Recent Contacts: {self.business_context.get('recent_contacts_count', 'N/A')}
- Revenue This Month: ${self.business_context.get('revenue_this_month', 'N/A')}
"""
            base_instructions += context_instructions
        
        return base_instructions
    
    def set_business_context_manager(self, manager: BusinessContextManager):
        """Set the business context manager for enhanced tool functionality"""
        self.business_context_manager = manager
        
        # Update all tool classes with the new context manager
        self.business_info_tools.business_context_manager = manager
        self.contact_tools.business_context_manager = manager
        self.job_tools.business_context_manager = manager
        self.estimate_tools.business_context_manager = manager
        self.intelligence_tools.business_context_manager = manager
        
        logger.info("📊 Business context manager set for Hero365Agent and all tools")
    
    # =============================================================================
    # BUSINESS INFORMATION TOOLS - Delegate to BusinessInfoTools
    # =============================================================================
    
    @function_tool
    async def get_business_info(self):
        """Get current business information including name, type, and contact details"""
        result = await self.business_info_tools.get_business_info()
        log_tool_call("get_business_info", result)
        return result
    
    @function_tool
    async def get_user_info(self):
        """Get current user information"""
        result = await self.business_info_tools.get_user_info()
        log_tool_call("get_user_info", result)
        return result
    
    @function_tool
    async def get_business_status(self):
        """Get complete business status and activity overview"""
        result = await self.business_info_tools.get_business_status()
        log_tool_call("get_business_status", result)
        return result
    
    # =============================================================================
    # CONTACT MANAGEMENT TOOLS - Delegate to ContactTools
    # =============================================================================
    
    @function_tool
    async def create_contact(self, name: str, phone: str = None, email: str = None, 
                      contact_type: str = "lead", address: str = None):
        """Create a new contact with context-aware assistance"""
        result = await self.contact_tools.create_contact(name, phone, email, contact_type, address)
        log_tool_call("create_contact", result)
        return result
    
    @function_tool
    async def search_contacts(self, query: str, limit: int = 10):
        """Search for contacts with context-aware suggestions"""
        result = await self.contact_tools.search_contacts(query, limit)
        log_tool_call("search_contacts", result)
        return result
    
    @function_tool
    async def get_suggested_contacts(self, limit: int = 5):
        """Get suggested contacts based on business context and recent activity"""
        result = await self.contact_tools.get_suggested_contacts(limit)
        log_tool_call("get_suggested_contacts", result)
        return result
    
    @function_tool
    async def get_contact_info(self, contact_name: str, info_type: str = "all"):
        """Get specific information about a contact by name (phone, email, address, etc.)"""
        result = await self.contact_tools.get_contact_info(contact_name, info_type)
        log_tool_call("get_contact_info", result)
        return result
    
    # =============================================================================
    # JOB MANAGEMENT TOOLS - Delegate to JobTools
    # =============================================================================
    
    @function_tool
    async def create_job(self, title: str, description: str, contact_id: str = None,
                  scheduled_date: str = None, priority: str = "medium", 
                  estimated_duration: int = None):
        """Create a new job with context-aware assistance"""
        result = await self.job_tools.create_job(title, description, contact_id, 
                                       scheduled_date, priority, estimated_duration)
        log_tool_call("create_job", result)
        return result
    
    @function_tool
    async def get_upcoming_jobs(self, days_ahead: int = 7):
        """Get upcoming jobs for the next specified number of days"""
        result = await self.job_tools.get_upcoming_jobs(days_ahead)
        log_tool_call("get_upcoming_jobs", result)
        return result
    
    @function_tool
    async def update_job_status(self, job_id: str, status: str):
        """Update the status of a specific job"""
        result = await self.job_tools.update_job_status(job_id, status)
        log_tool_call("update_job_status", result)
        return result
    
    @function_tool
    async def get_suggested_jobs(self, limit: int = 5):
        """Get suggested jobs based on business context and recent activity"""
        result = await self.job_tools.get_suggested_jobs(limit)
        log_tool_call("get_suggested_jobs", result)
        return result
    
    @function_tool
    async def search_jobs(self, query: str, limit: int = 10):
        """Search for jobs with context-aware suggestions"""
        result = await self.job_tools.search_jobs(query, limit)
        log_tool_call("search_jobs", result)
        return result
    
    # =============================================================================
    # ESTIMATE MANAGEMENT TOOLS - Delegate to EstimateTools
    # =============================================================================
    
    @function_tool
    async def create_estimate(self, title: str, description: str, contact_id: str = None,
                       total_amount: float = None, valid_until: str = None):
        """Create a new estimate with context-aware assistance"""
        result = await self.estimate_tools.create_estimate(title, description, contact_id, 
                                                  total_amount, valid_until)
        log_tool_call("create_estimate", result)
        return result
    
    @function_tool
    async def get_recent_estimates(self, limit: int = 10):
        """Get recent estimates for the business"""
        result = await self.estimate_tools.get_recent_estimates(limit)
        log_tool_call("get_recent_estimates", result)
        return result
    
    @function_tool
    async def get_pending_estimates(self, limit: int = 10):
        """Get all pending estimates regardless of age"""
        result = await self.estimate_tools.get_pending_estimates(limit)
        log_tool_call("get_pending_estimates", result)
        return result
    
    @function_tool
    async def get_suggested_estimates(self, limit: int = 5):
        """Get suggested estimates based on business context and recent activity"""
        result = await self.estimate_tools.get_suggested_estimates(limit)
        log_tool_call("get_suggested_estimates", result)
        return result
    
    @function_tool
    async def search_estimates(self, query: str, limit: int = 10):
        """Search for estimates with context-aware suggestions"""
        result = await self.estimate_tools.search_estimates(query, limit)
        log_tool_call("search_estimates", result)
        return result
    
    @function_tool
    async def update_estimate_status(self, estimate_id: str, status: str):
        """Update the status of a specific estimate"""
        result = await self.estimate_tools.update_estimate_status(estimate_id, status)
        log_tool_call("update_estimate_status", result)
        return result
    
    @function_tool
    async def convert_estimate_to_invoice(self, estimate_id: str):
        """Convert an approved estimate to an invoice"""
        result = await self.estimate_tools.convert_estimate_to_invoice(estimate_id)
        log_tool_call("convert_estimate_to_invoice", result)
        return result
    
    # =============================================================================
    # BUSINESS INTELLIGENCE TOOLS - Delegate to IntelligenceTools
    # =============================================================================
    
    @function_tool
    async def get_weather(self, location: str = None):
        """Get weather information for business planning"""
        result = await self.intelligence_tools.get_weather(location)
        log_tool_call("get_weather", result)
        return result
    
    @function_tool
    async def search_places(self, query: str, location: str = None, radius: int = 5000):
        """Search for nearby places, suppliers, and services"""
        result = await self.intelligence_tools.search_places(query, location, radius)
        log_tool_call("search_places", result)
        return result
    
    @function_tool
    async def get_directions(self, destination: str, origin: str = None, mode: str = "driving"):
        """Get directions to job sites and customer locations"""
        result = await self.intelligence_tools.get_directions(destination, origin, mode)
        log_tool_call("get_directions", result)
        return result
    
    @function_tool
    async def universal_search(self, query: str, limit: int = 10):
        """Universal search across all business data"""
        result = await self.intelligence_tools.universal_search(query, limit)
        log_tool_call("universal_search", result)
        return result
    
    @function_tool
    async def get_business_analytics(self, period: str = "month"):
        """Get business analytics and performance insights"""
        result = await self.intelligence_tools.get_business_analytics(period)
        log_tool_call("get_business_analytics", result)
        return result
    
    @function_tool
    async def get_contextual_insights(self):
        """Get contextual business insights based on current data"""
        result = await self.intelligence_tools.get_contextual_insights()
        log_tool_call("get_contextual_insights", result)
        return result
    
    @function_tool
    async def web_search(self, query: str, num_results: int = 5):
        """Perform web search with business context awareness"""
        result = await self.intelligence_tools.web_search(query, num_results)
        log_tool_call("web_search", result)
        return result
    
    @function_tool
    async def get_business_recommendations(self):
        """Get AI-powered business recommendations based on current context"""
        result = await self.intelligence_tools.get_business_recommendations()
        log_tool_call("get_business_recommendations", result)
        return result
    
    @function_tool
    async def get_available_tools(self):
        """Get a list of available tools and their capabilities for user reference"""
        return """
Available Hero365 Tools:

Contact Management:
- create_contact(name, phone, email, contact_type, address)
- search_contacts(query, limit)
- get_suggested_contacts(limit)
- get_contact_info(contact_name, info_type)

Job Management:
- create_job(title, description, contact_id, scheduled_date, priority, estimated_duration)
- get_upcoming_jobs(days_ahead)
- update_job_status(job_id, status)
- get_suggested_jobs(limit)
- search_jobs(query, limit)

Estimate Management:
- create_estimate(title, description, contact_id, total_amount, valid_until)
- get_recent_estimates(limit)
- get_pending_estimates(limit)
- get_suggested_estimates(limit)
- search_estimates(query, limit)
- update_estimate_status(estimate_id, status)
- convert_estimate_to_invoice(estimate_id)

Business Intelligence:
- get_weather(location)
- search_places(query, location, radius)
- get_directions(destination, origin, mode)
- universal_search(query, limit)
- get_business_analytics(period)
- get_contextual_insights()
- web_search(query, num_results)
- get_business_recommendations()

Business Information:
- get_business_info()
- get_user_info()
- get_business_status()

All tools provide real-time data from your Hero365 business database.
"""