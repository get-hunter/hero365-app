"""
Hero365 Voice Agent Worker for LiveKit Integration
Simplified single-agent architecture with direct tool access
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    function_tool,
    WorkerOptions,
    cli,
)
from livekit.plugins import deepgram, openai, cartesia, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from .config import LiveKitConfig
from .context_preloader import ContextPreloader
from .context_validator import ContextValidator
from .business_context_manager import BusinessContextManager
from ..infrastructure.config.dependency_injection import get_container

logger = logging.getLogger(__name__)


class Hero365Agent(Agent):
    """
    Single powerful Hero365 Voice Agent with direct access to all business tools.
    Inspired by Cursor's agent architecture - one agent, all capabilities.
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
        
        # Generate comprehensive instructions
        instructions = self._generate_comprehensive_instructions()
        
        # Initialize as LiveKit Agent
        super().__init__(instructions=instructions)
        
        logger.info(f"✅ Hero365Agent initialized with context: {bool(self.business_context)}")
    
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
5. Always provide accurate, up-to-date information
6. Be helpful and efficient in your responses
7. Use contextual insights to provide better service
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
        logger.info("📊 Business context manager set for Hero365Agent")
    
    # =============================================================================
    # BUSINESS INFORMATION TOOLS
    # =============================================================================
    
    @function_tool
    async def get_business_info(self) -> str:
        """Get current business information including name, type, and contact details"""
        logger.info("🏢 get_business_info tool called")
        
        if not self.business_context:
            return "Business information is not available at the moment."
            
        info = []
        if self.business_context.get('business_name'):
            info.append(f"Business Name: {self.business_context['business_name']}")
        if self.business_context.get('business_type'):
            info.append(f"Business Type: {self.business_context['business_type']}")
        if self.business_context.get('phone'):
            info.append(f"Phone: {self.business_context['phone']}")
        if self.business_context.get('email'):
            info.append(f"Email: {self.business_context['email']}")
        if self.business_context.get('address'):
            info.append(f"Address: {self.business_context['address']}")
            
        return "\n".join(info) if info else "Business information is not available."

    @function_tool
    async def get_user_info(self) -> str:
        """Get current user information"""
        logger.info("👤 get_user_info tool called")
        
        if not self.business_context:
            return "User information is not available at the moment."
            
        info = []
        if self.business_context.get('user_name'):
            info.append(f"Name: {self.business_context['user_name']}")
        if self.business_context.get('user_email'):
            info.append(f"Email: {self.business_context['user_email']}")
        if self.business_context.get('user_role'):
            info.append(f"Role: {self.business_context['user_role']}")
        if self.business_context.get('user_id'):
            info.append(f"User ID: {self.business_context['user_id']}")
            
        return "\n".join(info) if info else "User information is not available."

    @function_tool
    async def get_business_status(self) -> str:
        """Get complete business status and activity overview"""
        logger.info("📊 get_business_status tool called")
        
        if not self.business_context:
            return "Business status is not available at the moment."
            
        status = []
        if self.business_context.get('business_name'):
            status.append(f"Business: {self.business_context['business_name']}")
        if self.business_context.get('business_type'):
            status.append(f"Type: {self.business_context['business_type']}")
        if self.business_context.get('active_jobs'):
            status.append(f"Active Jobs: {self.business_context['active_jobs']}")
        if self.business_context.get('pending_estimates'):
            status.append(f"Pending Estimates: {self.business_context['pending_estimates']}")
        if self.business_context.get('total_contacts'):
            status.append(f"Total Contacts: {self.business_context['total_contacts']}")
        if self.business_context.get('recent_contacts_count'):
            status.append(f"Recent Contacts: {self.business_context['recent_contacts_count']}")
        if self.business_context.get('revenue_this_month'):
            status.append(f"Revenue This Month: ${self.business_context['revenue_this_month']}")
        if self.business_context.get('jobs_this_week'):
            status.append(f"Jobs This Week: {self.business_context['jobs_this_week']}")
            
        return "\n".join(status) if status else "Business status is not available."

    # =============================================================================
    # CONTACT MANAGEMENT TOOLS
    # =============================================================================
    
    @function_tool
    async def create_contact(
        self,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        contact_type: str = "lead",
        address: Optional[str] = None
    ) -> str:
        """Create a new contact with context-aware assistance.
        
        Args:
            name: Contact's full name (required)
            phone: Contact's phone number
            email: Contact's email address  
            contact_type: Type of contact (lead, customer, vendor)
            address: Contact's physical address
        """
        try:
            logger.info(f"📞 Creating contact: {name}")
            
            # Check if contact already exists using business context
            if self.business_context_manager:
                existing_contact = self.business_context_manager.find_contact_by_name(name)
                if existing_contact:
                    return f"ℹ️ Contact '{name}' already exists. Would you like to update their information instead?"
            
            # Simulate contact creation (replace with actual API call)
            response = f"✅ Successfully created contact '{name}'"
            if phone:
                response += f" with phone {phone}"
            if email:
                response += f" and email {email}"
            response += f" as a {contact_type}."
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.follow_ups:
                    response += f"\n💡 Suggested next step: {suggestions.follow_ups[0]}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error creating contact: {e}")
            return f"❌ Error creating contact: {str(e)}"

    @function_tool
    async def search_contacts(self, query: str, limit: int = 10) -> str:
        """Search for contacts with context-aware suggestions.
        
        Args:
            query: Search query (name, phone, email, etc.)
            limit: Maximum number of results to return
        """
        try:
            logger.info(f"🔍 Searching contacts for: {query}")
            
            # First check business context for quick matches
            if self.business_context_manager:
                context_match = self.business_context_manager.find_contact_by_name(query)
                if context_match:
                    return f"🎯 Found in recent contacts: {context_match.name} - {context_match.phone or 'No phone'} - {context_match.email or 'No email'}"
            
            # Simulate search results (replace with actual API call)
            contacts = [
                {"name": f"Sample Contact {i}", "phone": f"555-000{i}", "email": f"contact{i}@example.com"}
                for i in range(1, min(limit, 4))
            ]
            
            if contacts:
                response = f"🔍 Found {len(contacts)} contacts matching '{query}':\n"
                for i, contact in enumerate(contacts, 1):
                    response += f"{i}. {contact['name']} - {contact['phone']} - {contact['email']}\n"
                
                # Add contextual suggestions
                if self.business_context_manager:
                    suggestions = self.business_context_manager.get_contextual_suggestions()
                    if suggestions and suggestions.follow_ups:
                        response += f"\n💡 Related suggestion: {suggestions.follow_ups[0]}"
                
                return response
            else:
                return f"🔍 No contacts found matching '{query}'. Would you like to create a new contact with that name?"
                
        except Exception as e:
            logger.error(f"❌ Error searching contacts: {e}")
            return f"❌ Error searching contacts: {str(e)}"

    @function_tool
    async def get_suggested_contacts(self, limit: int = 5) -> str:
        """Get suggested contacts based on business context and recent activity.
        
        Args:
            limit: Maximum number of suggestions to return
        """
        try:
            logger.info("💡 Getting suggested contacts")
            
            if not self.business_context_manager:
                return "📞 Business context not available for contact suggestions"
            
            # Get recent contacts from business context
            recent_contacts = self.business_context_manager.get_recent_contacts(limit)
            
            if recent_contacts:
                response = f"📞 Recent contacts you might want to reach out to:\n"
                for i, contact in enumerate(recent_contacts, 1):
                    priority_icon = "🔥" if contact.priority.value == "high" else "📞"
                    response += f"{i}. {priority_icon} {contact.name} - {contact.phone or 'No phone'}\n"
                
                # Add contextual suggestions
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.follow_ups:
                    response += f"\n💡 Consider: {', '.join(suggestions.follow_ups[:2])}"
                
                return response
            else:
                return "📞 No recent contacts found. Would you like to create a new contact?"
                
        except Exception as e:
            logger.error(f"❌ Error getting contact suggestions: {e}")
            return f"❌ Error getting contact suggestions: {str(e)}"

    # =============================================================================
    # JOB MANAGEMENT TOOLS
    # =============================================================================
    
    @function_tool
    async def create_job(
        self,
        title: str,
        description: str,
        contact_id: Optional[str] = None,
        scheduled_date: Optional[str] = None,
        priority: str = "medium",
        estimated_duration: Optional[int] = None
    ) -> str:
        """Create a new job with context-aware assistance.
        
        Args:
            title: Job title/summary
            description: Detailed job description
            contact_id: ID of the contact for this job
            scheduled_date: When the job is scheduled (YYYY-MM-DD format)
            priority: Job priority (low, medium, high, urgent)
            estimated_duration: Estimated duration in hours
        """
        try:
            logger.info(f"🔧 Creating job: {title}")
            
            # If no contact_id provided, try to find from title/description
            if not contact_id and self.business_context_manager:
                recent_contacts = self.business_context_manager.get_recent_contacts(10)
                for contact in recent_contacts:
                    if contact.name.lower() in title.lower() or contact.name.lower() in description.lower():
                        contact_id = contact.id
                        break
            
            # Simulate job creation (replace with actual API call)
            response = f"✅ Successfully created job '{title}'"
            if scheduled_date:
                response += f" scheduled for {scheduled_date}"
            if priority != "medium":
                response += f" with {priority} priority"
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.quick_actions:
                    response += f"\n💡 Next step: {suggestions.quick_actions[0]}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error creating job: {e}")
            return f"❌ Error creating job: {str(e)}"

    @function_tool
    async def get_upcoming_jobs(self, days_ahead: int = 7) -> str:
        """Get upcoming jobs with context-aware insights.
        
        Args:
            days_ahead: Number of days to look ahead for jobs
        """
        try:
            logger.info(f"📅 Getting upcoming jobs for next {days_ahead} days")
            
            # Get context overview if available
            context_response = ""
            if self.business_context_manager:
                business_summary = self.business_context_manager.get_business_summary()
                if business_summary:
                    context_response = f"📊 Overview: {business_summary.active_jobs} active jobs, {business_summary.upcoming_appointments} upcoming appointments\n\n"
            
            # Simulate upcoming jobs (replace with actual API call)
            jobs = [
                {"title": f"Sample Job {i}", "scheduled_date": "2024-12-01", "priority": "medium"}
                for i in range(1, 4)
            ]
            
            if jobs:
                response = context_response + f"📅 Upcoming jobs for the next {days_ahead} days:\n"
                for i, job in enumerate(jobs, 1):
                    priority_icon = "🔥" if job.get('priority') == "high" else "📅"
                    response += f"{i}. {priority_icon} {job['title']} - {job['scheduled_date']}\n"
                
                # Add contextual suggestions
                if self.business_context_manager:
                    suggestions = self.business_context_manager.get_contextual_suggestions()
                    if suggestions and suggestions.quick_actions:
                        response += f"\n💡 Consider: {', '.join(suggestions.quick_actions[:2])}"
                
                return response
            else:
                return context_response + f"📅 No upcoming jobs for the next {days_ahead} days"
                
        except Exception as e:
            logger.error(f"❌ Error getting upcoming jobs: {e}")
            return f"❌ Error getting upcoming jobs: {str(e)}"

    @function_tool
    async def update_job_status(self, job_id: str, status: str) -> str:
        """Update job status.
        
        Args:
            job_id: The ID of the job to update
            status: New status (pending, in_progress, completed, cancelled)
        """
        try:
            logger.info(f"🔄 Updating job {job_id} status to {status}")
            
            # Simulate job update (replace with actual API call)
            response = f"✅ Job {job_id} status updated to '{status}'"
            
            if status == "completed":
                response += ". Great work! 🎉"
            elif status == "in_progress":
                response += ". Job is now active. 🔧"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error updating job status: {e}")
            return f"❌ Error updating job status: {str(e)}"

    # =============================================================================
    # ESTIMATE MANAGEMENT TOOLS
    # =============================================================================
    
    @function_tool
    async def create_estimate(
        self,
        title: str,
        description: str,
        contact_id: Optional[str] = None,
        total_amount: Optional[float] = None,
        valid_until: Optional[str] = None
    ) -> str:
        """Create a new estimate with context-aware assistance.
        
        Args:
            title: Estimate title/summary
            description: Detailed estimate description
            contact_id: ID of the contact for this estimate
            total_amount: Total estimated amount
            valid_until: Estimate validity date (YYYY-MM-DD format)
        """
        try:
            logger.info(f"📊 Creating estimate: {title}")
            
            # If no contact_id provided, try to find from title/description
            if not contact_id and self.business_context_manager:
                recent_contacts = self.business_context_manager.get_recent_contacts(10)
                for contact in recent_contacts:
                    if contact.name.lower() in title.lower() or contact.name.lower() in description.lower():
                        contact_id = contact.id
                        break
            
            # Simulate estimate creation (replace with actual API call)
            response = f"✅ Successfully created estimate '{title}'"
            if total_amount:
                response += f" for ${total_amount:,.2f}"
            if valid_until:
                response += f" valid until {valid_until}"
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.opportunities:
                    response += f"\n💡 Next step: {suggestions.opportunities[0]}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error creating estimate: {e}")
            return f"❌ Error creating estimate: {str(e)}"

    @function_tool
    async def get_recent_estimates(self, limit: int = 10) -> str:
        """Get recent estimates with context-aware insights.
        
        Args:
            limit: Maximum number of estimates to return
        """
        try:
            logger.info(f"📋 Getting recent estimates (limit: {limit})")
            
            if not self.business_context_manager:
                return "📊 Business context not available for estimate insights"
            
            # Get recent estimates from business context
            recent_estimates = self.business_context_manager.get_recent_estimates(limit)
            
            if recent_estimates:
                response = f"📋 Recent estimates:\n"
                for i, estimate in enumerate(recent_estimates, 1):
                    status_icon = "💰" if estimate.status == "approved" else "📊"
                    amount_str = f"${estimate.total_amount:,.2f}" if estimate.total_amount else "No amount"
                    response += f"{i}. {status_icon} {estimate.title} - {estimate.status} - {amount_str} - {estimate.contact_name}\n"
                
                # Add contextual suggestions
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.opportunities:
                    response += f"\n💡 Opportunities: {', '.join(suggestions.opportunities[:2])}"
                
                return response
            else:
                return "📋 No recent estimates found. Would you like to create a new estimate?"
                
        except Exception as e:
            logger.error(f"❌ Error getting recent estimates: {e}")
            return f"❌ Error getting recent estimates: {str(e)}"

    # =============================================================================
    # BUSINESS INTELLIGENCE TOOLS
    # =============================================================================
    
    @function_tool
    async def get_weather(self, location: Optional[str] = None) -> str:
        """Get current weather information with business context awareness.
        
        Args:
            location: Location to get weather for (if not provided, uses business location)
        """
        try:
            # Use business location as default if available
            if not location and self.business_context_manager:
                business_context = self.business_context_manager.get_business_context()
                if business_context and business_context.address:
                    location = business_context.address
            
            logger.info(f"🌤️ Getting weather for: {location or 'current location'}")
            
            # Simulate weather info (replace with actual API call)
            response = f"Current weather in {location or 'your area'}: 72°F, partly cloudy with light winds."
            
            # Add context-aware suggestions for outdoor jobs
            if self.business_context_manager:
                upcoming_jobs = self.business_context_manager.get_recent_jobs(5)
                outdoor_jobs = [j for j in upcoming_jobs if any(word in j.title.lower() for word in ["exterior", "outdoor", "roof", "siding", "landscape"])]
                
                if outdoor_jobs:
                    response += f"\n🔧 Weather impact: {len(outdoor_jobs)} outdoor jobs might be affected"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error getting weather: {e}")
            return f"❌ Error getting weather: {str(e)}"

    @function_tool
    async def universal_search(self, query: str, limit: int = 10) -> str:
        """Context-aware universal search across all Hero365 data.
        
        Args:
            query: Search query
            limit: Maximum number of results per category
        """
        try:
            logger.info(f"🔍 Universal search for: {query}")
            
            # Check business context for quick matches
            context_results = []
            if self.business_context_manager:
                contact_match = self.business_context_manager.find_contact_by_name(query)
                if contact_match:
                    context_results.append(f"📞 Recent contact: {contact_match.name}")
                
                job_match = self.business_context_manager.find_job_by_title(query)
                if job_match:
                    context_results.append(f"🔧 Recent job: {job_match.title}")
                
                estimate_match = self.business_context_manager.find_estimate_by_title(query)
                if estimate_match:
                    context_results.append(f"📊 Recent estimate: {estimate_match.title}")
            
            # Simulate universal search results (replace with actual API call)
            total_count = 3
            contacts = [{"name": f"Contact {query}", "phone": "555-0001"}]
            jobs = [{"title": f"Job {query}", "status": "active"}]
            estimates = [{"title": f"Estimate {query}", "status": "draft"}]
            
            response = ""
            
            # Add context results first
            if context_results:
                response += f"🎯 Quick matches from recent activity:\n"
                for context_result in context_results:
                    response += f"• {context_result}\n"
                response += "\n"
            
            if total_count > 0:
                response += f"🔍 Found {total_count} total results for '{query}':\n"
                
                # Contacts
                if contacts:
                    response += f"\n📞 Contacts ({len(contacts)}):\n"
                    for contact in contacts:
                        response += f"• {contact['name']}\n"
                
                # Jobs
                if jobs:
                    response += f"\n🔧 Jobs ({len(jobs)}):\n"
                    for job in jobs:
                        response += f"• {job['title']}\n"
                
                # Estimates
                if estimates:
                    response += f"\n📋 Estimates ({len(estimates)}):\n"
                    for estimate in estimates:
                        response += f"• {estimate['title']}\n"
                
                return response
            else:
                if context_results:
                    return response + f"No additional results found for '{query}'"
                else:
                    return f"🔍 No results found for '{query}'"
                
        except Exception as e:
            logger.error(f"❌ Error in universal search: {e}")
            return f"❌ Error in search: {str(e)}"

    @function_tool
    async def get_business_analytics(self, period: str = "month") -> str:
        """Get business analytics with contextual insights.
        
        Args:
            period: Time period for analytics (day, week, month, year)
        """
        try:
            logger.info(f"📊 Getting business analytics for: {period}")
            
            # Add business context summary
            context_summary = ""
            if self.business_context_manager:
                business_summary = self.business_context_manager.get_business_summary()
                if business_summary:
                    context_summary = f"📊 Current snapshot: {business_summary.active_jobs} active jobs, {business_summary.pending_estimates} pending estimates\n\n"
            
            # Simulate analytics data (replace with actual API call)
            response = context_summary + f"📊 Business Analytics for {period}:\n"
            response += f"• Total Jobs: 15\n"
            response += f"• Completed Jobs: 10\n"
            response += f"• Total Revenue: $25,000.00\n"
            response += f"• Pending Estimates: 5\n"
            response += f"• Overdue Invoices: 2\n"
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.urgent_items:
                    response += f"\n🔥 Urgent attention needed: {suggestions.urgent_items[0]}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")
            return f"❌ Error getting analytics: {str(e)}"

    @function_tool
    async def get_contextual_insights(self) -> str:
        """Get contextual business insights and suggestions based on current state."""
        try:
            logger.info("🔍 Getting contextual insights")
            
            if not self.business_context_manager:
                return "🔍 Business context not available for insights"
            
            business_summary = self.business_context_manager.get_business_summary()
            suggestions = self.business_context_manager.get_contextual_suggestions()
            
            if not business_summary:
                return "🔍 No business data available for insights"
            
            response = f"🔍 Business Insights:\n"
            response += f"📊 Overview: {business_summary.active_jobs} active jobs, {business_summary.pending_estimates} pending estimates\n"
            response += f"📅 This week: {business_summary.jobs_this_week} jobs scheduled\n"
            
            if suggestions:
                if suggestions.urgent_items:
                    response += f"\n🔥 Urgent items:\n"
                    for item in suggestions.urgent_items[:3]:
                        response += f"• {item}\n"
                
                if suggestions.quick_actions:
                    response += f"\n⚡ Quick actions:\n"
                    for action in suggestions.quick_actions[:3]:
                        response += f"• {action}\n"
                
                if suggestions.opportunities:
                    response += f"\n💡 Opportunities:\n"
                    for opportunity in suggestions.opportunities[:3]:
                        response += f"• {opportunity}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error getting contextual insights: {e}")
            return f"❌ Error getting contextual insights: {str(e)}"


async def entrypoint(ctx: JobContext):
    """
    Enhanced entrypoint for the simplified Hero365 Voice Agent
    """
    try:
        logger.info(f"🚀 Hero365 Voice Agent starting for job: {ctx.job.id}")
        
        # Initialize context validator
        validator = ContextValidator()
        
        # Connect to the room first
        await ctx.connect()
        logger.info(f"✅ Connected to room: {ctx.room.name}")
        
        # Extract and validate business context
        business_context = None
        user_context = None
        
        try:
            # Parse room metadata for preloaded context
            if ctx.room.metadata:
                room_metadata = json.loads(ctx.room.metadata)
                logger.info(f"📊 Room metadata parsed successfully")
                
                # Extract preloaded context
                preloaded_context = room_metadata.get('preloaded_context')
                if preloaded_context:
                    logger.info(f"🔧 Found preloaded context in room metadata")
                    
                    # Validate preloaded context
                    is_valid, errors = validator.validate_preloaded_context(preloaded_context)
                    if not is_valid:
                        logger.warning(f"⚠️ Preloaded context validation failed: {errors}")
                        for error in errors:
                            logger.warning(f"  - {error}")
                    else:
                        logger.info(f"✅ Preloaded context validation passed")
                    
                    # Deserialize context for agent use
                    context_preloader = ContextPreloader()
                    agent_context = context_preloader.deserialize_context(preloaded_context)
                    
                    if agent_context:
                        # Validate agent context
                        agent_valid, agent_errors = validator.validate_agent_context(agent_context)
                        if not agent_valid:
                            logger.warning(f"⚠️ Agent context validation failed: {agent_errors}")
                            for error in agent_errors:
                                logger.warning(f"  - {error}")
                        else:
                            logger.info(f"✅ Agent context validation passed")
                        
                        # Log context status
                        validator.log_context_status(agent_context, "Preloaded Agent")
                        
                        # Generate context report
                        report = validator.generate_context_report(agent_context)
                        logger.info(f"📋 Context Report: {report['validation_status']}, {report['completeness']:.1%} complete")
                        
                        business_context = agent_context
                        user_context = {
                            'user_name': agent_context.get('user_name'),
                            'user_email': agent_context.get('user_email'),
                            'user_role': agent_context.get('user_role'),
                            'user_id': agent_context.get('user_id'),
                            'user_permissions': agent_context.get('user_permissions', []),
                            'user_preferences': agent_context.get('user_preferences', {})
                        }
                        logger.info(f"✅ Context deserialized successfully for agent")
                    else:
                        logger.warning("⚠️ Failed to deserialize preloaded context")
                else:
                    logger.warning("⚠️ No preloaded context found in room metadata")
                    
        except Exception as e:
            logger.error(f"❌ Error extracting context from room metadata: {e}")
        
        # Fallback: Try to extract basic info from metadata and load context
        if not business_context:
            logger.info("🔄 Attempting fallback context loading")
            try:
                if ctx.room.metadata:
                    room_metadata = json.loads(ctx.room.metadata)
                    user_id = room_metadata.get('user_id')
                    business_id = room_metadata.get('business_id')
                    
                    if user_id and business_id:
                        logger.info(f"🔧 Loading context via fallback for user_id: {user_id}, business_id: {business_id}")
                        
                        # Initialize business context manager and load context
                        context_manager = BusinessContextManager()
                        container = get_container()
                        user_info = room_metadata.get('user_info')
                        await context_manager.initialize(user_id, business_id, container, user_info)
                        
                        # Convert to agent context format
                        business_ctx = context_manager.get_business_context()
                        user_ctx = context_manager.get_user_context()
                        
                        if business_ctx:
                            business_context = {
                                'business_name': business_ctx.business_name,
                                'business_type': business_ctx.business_type,
                                'phone': business_ctx.phone,
                                'email': business_ctx.email,
                                'address': business_ctx.address,
                                'timezone': business_ctx.timezone,
                                'active_jobs': business_ctx.active_jobs,
                                'pending_estimates': business_ctx.pending_estimates,
                                'recent_contacts_count': business_ctx.recent_contacts_count,
                                'recent_jobs_count': business_ctx.recent_jobs_count,
                                'recent_estimates_count': business_ctx.recent_estimates_count,
                                'last_refresh': business_ctx.last_refresh.isoformat() if business_ctx.last_refresh else None
                            }
                            
                            # Validate fallback context
                            fallback_valid, fallback_errors = validator.validate_agent_context(business_context)
                            if not fallback_valid:
                                logger.warning(f"⚠️ Fallback context validation failed: {fallback_errors}")
                            else:
                                logger.info(f"✅ Fallback context validation passed")
                            
                            # Log fallback context status
                            validator.log_context_status(business_context, "Fallback")
                            
                        if user_ctx:
                            user_context = {
                                'user_name': user_ctx.name,
                                'user_email': user_ctx.email,
                                'user_role': user_ctx.role,
                                'user_id': user_ctx.user_id,
                                'user_permissions': user_ctx.permissions,
                                'user_preferences': user_ctx.preferences
                            }
                            
                        logger.info(f"✅ Fallback context loaded successfully")
                    else:
                        logger.warning("⚠️ No user_id or business_id found for fallback loading")
                        
            except Exception as e:
                logger.error(f"❌ Error in fallback context loading: {e}")
        
        # Final context validation and logging
        if business_context:
            # Generate final context report
            final_report = validator.generate_context_report(business_context)
            logger.info(f"🎯 Final Context Report:")
            logger.info(f"  Status: {final_report['validation_status']}")
            logger.info(f"  Completeness: {final_report['completeness']:.1%}")
            logger.info(f"  Errors: {len(final_report['errors'])}")
            logger.info(f"  Warnings: {len(final_report['warnings'])}")
            
            # Log business details
            business_name = business_context.get('business_name', 'Unknown')
            business_type = business_context.get('business_type', 'Unknown')
            user_name = business_context.get('user_name', 'Unknown')
            logger.info(f"🏢 Agent will serve {user_name} from {business_name} ({business_type})")
            
            # Log metrics
            active_jobs = business_context.get('active_jobs', 0)
            pending_estimates = business_context.get('pending_estimates', 0)
            total_contacts = business_context.get('total_contacts', 0)
            logger.info(f"📊 Business Metrics: {active_jobs} active jobs, {pending_estimates} pending estimates, {total_contacts} total contacts")
            
        else:
            logger.warning("⚠️ Agent will start without business context - limited functionality available")
        
        # Initialize the single powerful agent
        agent = Hero365Agent(business_context=business_context, user_context=user_context)
        
        # Set up business context manager if available
        if business_context:
            try:
                context_manager = BusinessContextManager()
                container = get_container()
                user_id = business_context.get('user_id')
                business_id = business_context.get('business_id')
                
                if user_id and business_id:
                    await context_manager.initialize(user_id, business_id, container)
                    agent.set_business_context_manager(context_manager)
                    logger.info("✅ Business context manager set for agent")
            except Exception as e:
                logger.warning(f"⚠️ Could not set business context manager: {e}")
        
        # Get configuration
        config = LiveKitConfig()
        voice_config = config.get_voice_pipeline_config()
        
        # Create agent session with proper configuration
        session = AgentSession(
            stt=deepgram.STT(
                model=voice_config["stt"]["model"],
                language=voice_config["stt"]["language"],
                keywords=[(keyword, 1.5) for keyword in voice_config["stt"]["keywords"]],
                smart_format=True,
                interim_results=voice_config["stt"]["interim_results"],
            ),
            llm=openai.LLM(
                model=voice_config["llm"]["model"],
                temperature=voice_config["llm"]["temperature"],
            ),
            tts=cartesia.TTS(
                voice=voice_config["tts"]["voice"],
                model=voice_config["tts"]["model"],
                language=voice_config["tts"]["language"],
            ),
            vad=silero.VAD.load(
                min_silence_duration=voice_config["turn_detection"]["min_silence_duration"],
                min_speech_duration=voice_config["turn_detection"]["min_speech_duration"],
            ),
            turn_detection=MultilingualModel(),
        )
        
        # Start the session
        await session.start(
            room=ctx.room,
            agent=agent,
        )
        
        # Generate context-aware initial greeting
        greeting_instructions = "Greet the user warmly and introduce yourself as their Hero365 business assistant."
        if business_context and business_context.get('business_name'):
            greeting_instructions += f" Mention that you're here to help with {business_context['business_name']} and can assist with contacts, jobs, estimates, and business insights. Ask how you can help them today."
        else:
            greeting_instructions += " Mention that you can help with contacts, jobs, estimates, and business management. Ask how you can help them with their business today."
        
        await session.generate_reply(instructions=greeting_instructions)
        
        logger.info("🎤 Hero365 Agent ready - single powerful agent with all capabilities")
        
    except Exception as e:
        logger.error(f"❌ Error in entrypoint: {e}")
        raise


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    ) 