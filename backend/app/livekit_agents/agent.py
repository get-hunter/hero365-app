"""
Hero365 Agent - Organized Single Agent with All Business Tools
Clean architecture with separated tool classes
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from livekit.agents import Agent

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
    Single powerful Hero365 Voice Agent with organized tool architecture.
    Uses clean separation of concerns with individual tool classes.
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
You are the Hero365 AI Assistant, a comprehensive voice agent for home service businesses.

CURRENT DATE AND TIME: Today is {current_date} at {current_time}

CORE CAPABILITIES:
You have direct access to all Hero365 business tools and can help with:

📞 CONTACT MANAGEMENT:
- Create new contacts with smart defaults
- Search for existing contacts
- Get contact suggestions based on recent activity
- Get any contact information (phone, email, address, company, etc.)
- Update contact information
- Get contact details and interaction history
- Add notes and schedule follow-ups

🔧 JOB MANAGEMENT:
- Create new jobs with full details
- Search and filter jobs by status
- Get upcoming jobs and schedules
- Update job information and status
- Mark jobs as complete
- Get job statistics and insights

📊 ESTIMATE MANAGEMENT:
- Create detailed estimates
- Search and manage estimates
- Get recent estimates and suggestions
- Convert estimates to invoices
- Update estimate status and details

🌤️ BUSINESS INTELLIGENCE:
- Get weather information for job planning
- Search for nearby places and services
- Get directions to job sites
- Universal search across all business data
- Business analytics and insights
- Real-time web search capabilities

🎯 CONTEXTUAL AWARENESS:
- Access to current business context and metrics
- Smart suggestions based on recent activity
- Proactive insights and recommendations
- Context-aware responses and actions

INTERACTION STYLE:
- Be conversational, helpful, and professional
- Use natural language and avoid technical jargon
- Provide specific, actionable information
- Ask clarifying questions when needed
- Be proactive with relevant suggestions
- Reference business context naturally in responses

IMPORTANT GUIDELINES:
1. Always use the available tools to get real, current data
2. When users ask about business information, use get_business_info
3. When users ask about their details, use get_user_info
4. For business overviews, use get_business_status
5. When users ask for any contact information, use get_contact_info with the appropriate info_type
6. Always provide accurate, up-to-date information
7. Be helpful and efficient in your responses
8. Use contextual insights to provide better service
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
    
    def get_business_info(self):
        """Get current business information including name, type, and contact details"""
        return self.business_info_tools.get_business_info()
    
    def get_user_info(self):
        """Get current user information"""
        return self.business_info_tools.get_user_info()
    
    def get_business_status(self):
        """Get complete business status and activity overview"""
        return self.business_info_tools.get_business_status()
    
    # =============================================================================
    # CONTACT MANAGEMENT TOOLS - Delegate to ContactTools
    # =============================================================================
    
    def create_contact(self, name: str, phone: str = None, email: str = None, 
                      contact_type: str = "lead", address: str = None):
        """Create a new contact with context-aware assistance"""
        return self.contact_tools.create_contact(name, phone, email, contact_type, address)
    
    def search_contacts(self, query: str, limit: int = 10):
        """Search for contacts with context-aware suggestions"""
        return self.contact_tools.search_contacts(query, limit)
    
    def get_suggested_contacts(self, limit: int = 5):
        """Get suggested contacts based on business context and recent activity"""
        return self.contact_tools.get_suggested_contacts(limit)
    
    def get_contact_info(self, contact_name: str, info_type: str = "all"):
        """Get specific information about a contact by name (phone, email, address, etc.)"""
        return self.contact_tools.get_contact_info(contact_name, info_type)
    
    # =============================================================================
    # JOB MANAGEMENT TOOLS - Delegate to JobTools
    # =============================================================================
    
    def create_job(self, title: str, description: str, contact_id: str = None,
                  scheduled_date: str = None, priority: str = "medium", 
                  estimated_duration: int = None):
        """Create a new job with context-aware assistance"""
        return self.job_tools.create_job(title, description, contact_id, 
                                       scheduled_date, priority, estimated_duration)
    
    def get_upcoming_jobs(self, days_ahead: int = 7):
        """Get upcoming jobs with context-aware insights"""
        return self.job_tools.get_upcoming_jobs(days_ahead)
    
    def update_job_status(self, job_id: str, status: str):
        """Update job status"""
        return self.job_tools.update_job_status(job_id, status)
    
    def get_suggested_jobs(self, limit: int = 5):
        """Get suggested jobs based on business context and activity"""
        return self.job_tools.get_suggested_jobs(limit)
    
    def search_jobs(self, query: str, limit: int = 10):
        """Search for jobs with context-aware suggestions"""
        return self.job_tools.search_jobs(query, limit)
    
    # =============================================================================
    # ESTIMATE MANAGEMENT TOOLS - Delegate to EstimateTools
    # =============================================================================
    
    def create_estimate(self, title: str, description: str, contact_id: str = None,
                       total_amount: float = None, valid_until: str = None):
        """Create a new estimate with context-aware assistance"""
        return self.estimate_tools.create_estimate(title, description, contact_id,
                                                 total_amount, valid_until)
    
    def get_recent_estimates(self, limit: int = 10):
        """Get recent estimates with context-aware insights"""
        return self.estimate_tools.get_recent_estimates(limit)
    
    def get_suggested_estimates(self, limit: int = 5):
        """Get suggested estimates based on business context and opportunities"""
        return self.estimate_tools.get_suggested_estimates(limit)
    
    def search_estimates(self, query: str, limit: int = 10):
        """Search for estimates with context-aware suggestions"""
        return self.estimate_tools.search_estimates(query, limit)
    
    def update_estimate_status(self, estimate_id: str, status: str):
        """Update estimate status"""
        return self.estimate_tools.update_estimate_status(estimate_id, status)
    
    def convert_estimate_to_invoice(self, estimate_id: str):
        """Convert an approved estimate to an invoice"""
        return self.estimate_tools.convert_estimate_to_invoice(estimate_id)
    
    # =============================================================================
    # BUSINESS INTELLIGENCE TOOLS - Delegate to IntelligenceTools
    # =============================================================================
    
    def get_weather(self, location: str = None):
        """Get current weather information with business context awareness"""
        return self.intelligence_tools.get_weather(location)
    
    def search_places(self, query: str, location: str = None, radius: int = 5000):
        """Search for places nearby with business context awareness"""
        return self.intelligence_tools.search_places(query, location, radius)
    
    def get_directions(self, destination: str, origin: str = None, mode: str = "driving"):
        """Get directions with business context awareness"""
        return self.intelligence_tools.get_directions(destination, origin, mode)
    
    def universal_search(self, query: str, limit: int = 10):
        """Context-aware universal search across all Hero365 data"""
        return self.intelligence_tools.universal_search(query, limit)
    
    def get_business_analytics(self, period: str = "month"):
        """Get business analytics with contextual insights"""
        return self.intelligence_tools.get_business_analytics(period)
    
    def get_contextual_insights(self):
        """Get contextual business insights and suggestions based on current state"""
        return self.intelligence_tools.get_contextual_insights()
    
    def web_search(self, query: str, num_results: int = 5):
        """Perform web search with business context awareness"""
        return self.intelligence_tools.web_search(query, num_results)
    
    def get_business_recommendations(self):
        """Get AI-powered business recommendations based on current context"""
        return self.intelligence_tools.get_business_recommendations() 