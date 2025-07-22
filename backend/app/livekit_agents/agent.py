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
You are the Hero365 AI Assistant, a powerful voice agent for home service businesses. You operate exclusively to help users manage their business operations efficiently.

CURRENT DATE AND TIME: Today is {current_date} at {current_time}

YOUR ROLE:
You are pair programming with a USER to solve their business management tasks. Each task may require creating new records, modifying existing data, searching for information, or simply answering questions about their business.

AVAILABLE TOOLS:
You have direct access to all Hero365 business tools and can help with:

CONTACT MANAGEMENT:
- Create new contacts with smart defaults
- Search for existing contacts by name, phone, or email
- Get contact suggestions based on recent activity
- Retrieve any contact information (phone, email, address, company, etc.)
- Update contact information and details
- Get contact interaction history and notes

JOB MANAGEMENT:
- Create new jobs with full details and scheduling
- Search and filter jobs by status, date, or contact
- Get upcoming jobs and schedules
- Update job information, status, and progress
- Mark jobs as complete or reschedule
- Get job statistics and performance insights

ESTIMATE MANAGEMENT:
- Create detailed estimates with line items
- Search and manage estimates by status or contact
- Get recent estimates and conversion opportunities
- Convert approved estimates to invoices
- Update estimate status and pricing details

BUSINESS INTELLIGENCE:
- Get weather information for job planning and scheduling
- Search for nearby places, suppliers, and services
- Get directions to job sites and customer locations
- Universal search across all business data
- Business analytics and performance insights
- Real-time web search for market information

INTERACTION GUIDELINES:
- Be conversational, helpful, and professional
- Use natural language and avoid technical jargon
- Provide specific, actionable information
- Ask clarifying questions when needed
- Be proactive with relevant suggestions
- Reference business context naturally in responses

TOOL USAGE GUIDELINES:
1. ALWAYS use the available tools to get real, current data
2. When users ask about business information, use get_business_info
3. When users ask about their details, use get_user_info
4. For business overviews, use get_business_status
5. When users ask for contact information, use get_contact_info with appropriate info_type
6. When users ask for job information, use search_jobs or get_upcoming_jobs
7. When users ask for estimate information, use search_estimates or get_recent_estimates
8. When users ask what you can do, use get_available_tools to show capabilities
9. Always provide accurate, up-to-date information from the database
10. Be helpful and efficient in your responses
11. Use contextual insights to provide better service
12. If a user asks for something you can't do, suggest the closest available tool

RESPONSE FORMAT:
- Provide clear, concise answers
- Include relevant details when appropriate
- Suggest next steps or related actions
- Reference specific data from your tools
- Be conversational but professional
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
        return await self.business_info_tools.get_business_info()
    
    @function_tool
    async def get_user_info(self):
        """Get current user information"""
        return await self.business_info_tools.get_user_info()
    
    @function_tool
    async def get_business_status(self):
        """Get complete business status and activity overview"""
        return await self.business_info_tools.get_business_status()
    
    # =============================================================================
    # CONTACT MANAGEMENT TOOLS - Delegate to ContactTools
    # =============================================================================
    
    @function_tool
    async def create_contact(self, name: str, phone: str = None, email: str = None, 
                      contact_type: str = "lead", address: str = None):
        """Create a new contact with context-aware assistance"""
        return await self.contact_tools.create_contact(name, phone, email, contact_type, address)
    
    @function_tool
    async def search_contacts(self, query: str, limit: int = 10):
        """Search for contacts with context-aware suggestions"""
        return await self.contact_tools.search_contacts(query, limit)
    
    @function_tool
    async def get_suggested_contacts(self, limit: int = 5):
        """Get suggested contacts based on business context and recent activity"""
        return await self.contact_tools.get_suggested_contacts(limit)
    
    @function_tool
    async def get_contact_info(self, contact_name: str, info_type: str = "all"):
        """Get specific information about a contact by name (phone, email, address, etc.)"""
        return await self.contact_tools.get_contact_info(contact_name, info_type)
    
    # =============================================================================
    # JOB MANAGEMENT TOOLS - Delegate to JobTools
    # =============================================================================
    
    @function_tool
    async def create_job(self, title: str, description: str, contact_id: str = None,
                  scheduled_date: str = None, priority: str = "medium", 
                  estimated_duration: int = None):
        """Create a new job with context-aware assistance"""
        return await self.job_tools.create_job(title, description, contact_id, 
                                       scheduled_date, priority, estimated_duration)
    
    @function_tool
    async def get_upcoming_jobs(self, days_ahead: int = 7):
        """Get upcoming jobs for the next specified number of days"""
        return await self.job_tools.get_upcoming_jobs(days_ahead)
    
    @function_tool
    async def update_job_status(self, job_id: str, status: str):
        """Update the status of a specific job"""
        return await self.job_tools.update_job_status(job_id, status)
    
    @function_tool
    async def get_suggested_jobs(self, limit: int = 5):
        """Get suggested jobs based on business context and recent activity"""
        return await self.job_tools.get_suggested_jobs(limit)
    
    @function_tool
    async def search_jobs(self, query: str, limit: int = 10):
        """Search for jobs with context-aware suggestions"""
        return await self.job_tools.search_jobs(query, limit)
    
    # =============================================================================
    # ESTIMATE MANAGEMENT TOOLS - Delegate to EstimateTools
    # =============================================================================
    
    @function_tool
    async def create_estimate(self, title: str, description: str, contact_id: str = None,
                       total_amount: float = None, valid_until: str = None):
        """Create a new estimate with context-aware assistance"""
        return await self.estimate_tools.create_estimate(title, description, contact_id, 
                                                  total_amount, valid_until)
    
    @function_tool
    async def get_recent_estimates(self, limit: int = 10):
        """Get recent estimates for the business"""
        return await self.estimate_tools.get_recent_estimates(limit)
    
    @function_tool
    async def get_suggested_estimates(self, limit: int = 5):
        """Get suggested estimates based on business context and recent activity"""
        return await self.estimate_tools.get_suggested_estimates(limit)
    
    @function_tool
    async def search_estimates(self, query: str, limit: int = 10):
        """Search for estimates with context-aware suggestions"""
        return await self.estimate_tools.search_estimates(query, limit)
    
    @function_tool
    async def update_estimate_status(self, estimate_id: str, status: str):
        """Update the status of a specific estimate"""
        return await self.estimate_tools.update_estimate_status(estimate_id, status)
    
    @function_tool
    async def convert_estimate_to_invoice(self, estimate_id: str):
        """Convert an approved estimate to an invoice"""
        return await self.estimate_tools.convert_estimate_to_invoice(estimate_id)
    
    # =============================================================================
    # BUSINESS INTELLIGENCE TOOLS - Delegate to IntelligenceTools
    # =============================================================================
    
    @function_tool
    async def get_weather(self, location: str = None):
        """Get weather information for business planning"""
        return await self.intelligence_tools.get_weather(location)
    
    @function_tool
    async def search_places(self, query: str, location: str = None, radius: int = 5000):
        """Search for nearby places, suppliers, and services"""
        return await self.intelligence_tools.search_places(query, location, radius)
    
    @function_tool
    async def get_directions(self, destination: str, origin: str = None, mode: str = "driving"):
        """Get directions to job sites and customer locations"""
        return await self.intelligence_tools.get_directions(destination, origin, mode)
    
    @function_tool
    async def universal_search(self, query: str, limit: int = 10):
        """Universal search across all business data"""
        return await self.intelligence_tools.universal_search(query, limit)
    
    @function_tool
    async def get_business_analytics(self, period: str = "month"):
        """Get business analytics and performance insights"""
        return await self.intelligence_tools.get_business_analytics(period)
    
    @function_tool
    async def get_contextual_insights(self):
        """Get contextual business insights based on current data"""
        return await self.intelligence_tools.get_contextual_insights()
    
    @function_tool
    async def web_search(self, query: str, num_results: int = 5):
        """Perform web search with business context awareness"""
        return await self.intelligence_tools.web_search(query, num_results)
    
    @function_tool
    async def get_business_recommendations(self):
        """Get AI-powered business recommendations based on current context"""
        return await self.intelligence_tools.get_business_recommendations()
    
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