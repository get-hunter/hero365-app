"""
Hero365 Tools Wrapper for LiveKit Agents with Business Context Awareness
Integrates existing Hero365 tools with LiveKit function_tool decorator and business context
"""

from typing import Dict, Any, Optional, List
from livekit.agents import function_tool, RunContext
from ...infrastructure.config.dependency_injection import get_container
from ..business_context_manager import BusinessContextManager
import logging

logger = logging.getLogger(__name__)

class Hero365Tools:
    """Temporary implementation of Hero365Tools for testing"""
    
    def __init__(self, context_manager=None):
        self.context_manager = context_manager
        
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Temporary implementation - create contact"""
        try:
            # Simulate contact creation
            name = contact_data.get("name", "Unknown")
            logger.info(f"Creating contact: {name}")
            return {
                "success": True,
                "message": f"Contact '{name}' created successfully",
                "data": {"contact_id": "temp_id_123"}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_contacts(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Temporary implementation - search contacts"""
        try:
            # Simulate search results
            logger.info(f"Searching contacts for: {query}")
            return {
                "success": True,
                "data": {
                    "contacts": [
                        {"name": f"Sample Contact {i}", "phone": f"555-000{i}", "email": f"contact{i}@example.com"}
                        for i in range(1, min(limit, 4))
                    ]
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Temporary implementation - create job"""
        try:
            title = job_data.get("title", "Unknown Job")
            logger.info(f"Creating job: {title}")
            return {
                "success": True,
                "message": f"Job '{title}' created successfully",
                "data": {"job_id": "temp_job_123"}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_upcoming_jobs(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Temporary implementation - get upcoming jobs"""
        try:
            logger.info(f"Getting upcoming jobs for {days_ahead} days")
            return {
                "success": True,
                "data": {
                    "jobs": [
                        {"title": f"Sample Job {i}", "scheduled_date": "2024-12-01", "priority": "medium"}
                        for i in range(1, 4)
                    ]
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_estimate(self, estimate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Temporary implementation - create estimate"""
        try:
            title = estimate_data.get("title", "Unknown Estimate")
            logger.info(f"Creating estimate: {title}")
            return {
                "success": True,
                "message": f"Estimate '{title}' created successfully",
                "data": {"estimate_id": "temp_estimate_123"}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_weather_info(self, location: str = None) -> Dict[str, Any]:
        """Temporary implementation - get weather"""
        try:
            logger.info(f"Getting weather for: {location or 'current location'}")
            return {
                "success": True,
                "voice_response": f"Current weather in {location or 'your area'}: 72°F, partly cloudy with light winds."
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_places(self, query: str, location: str = None, radius: int = 5000) -> Dict[str, Any]:
        """Temporary implementation - search places"""
        try:
            logger.info(f"Searching for {query} near {location or 'current location'}")
            return {
                "success": True,
                "voice_response": f"Found several {query} locations within {radius} meters of {location or 'your area'}."
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_directions(self, destination: str, origin: str = None, mode: str = "driving") -> Dict[str, Any]:
        """Temporary implementation - get directions"""
        try:
            logger.info(f"Getting directions from {origin or 'current location'} to {destination}")
            return {
                "success": True,
                "voice_response": f"Directions from {origin or 'your location'} to {destination}: Take the main route, approximately 15 minutes by {mode}."
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def universal_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Temporary implementation - universal search"""
        try:
            logger.info(f"Universal search for: {query}")
            return {
                "success": True,
                "data": {
                    "total_count": 3,
                    "contacts": [{"name": f"Contact {query}", "phone": "555-0001"}],
                    "jobs": [{"title": f"Job {query}", "status": "active"}],
                    "estimates": [{"title": f"Estimate {query}", "status": "draft"}]
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_business_analytics(self, period: str = "month") -> Dict[str, Any]:
        """Temporary implementation - business analytics"""
        try:
            logger.info(f"Getting business analytics for: {period}")
            return {
                "success": True,
                "data": {
                    "total_jobs": 15,
                    "completed_jobs": 10,
                    "total_revenue": 25000.00,
                    "pending_estimates": 5,
                    "overdue_invoices": 2
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def web_search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Temporary implementation - web search"""
        try:
            logger.info(f"Web search for: {query}")
            return {
                "success": True,
                "voice_response": f"I found information about {query}. Here are the key details from my search results."
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

class Hero365ToolsWrapper:
    """Context-aware wrapper for Hero365 tools to work with LiveKit function_tool decorator"""
    
    def __init__(self, context_manager=None):
        self.hero365_tools = Hero365Tools(context_manager)
        self.business_context_manager: Optional[BusinessContextManager] = None
        
    def set_business_context(self, business_context_manager: BusinessContextManager):
        """Set business context manager for context-aware operations"""
        self.business_context_manager = business_context_manager
        
    def get_available_tools(self):
        """Get list of available tools as functions"""
        return [
            self.create_contact,
            self.search_contacts,
            self.get_suggested_contacts,
            self.create_job,
            self.get_upcoming_jobs,
            self.get_suggested_jobs,
            self.create_estimate,
            self.get_recent_estimates,
            self.get_suggested_estimates,
            self.get_weather,
            self.search_places,
            self.get_directions,
            self.universal_search,
            self.get_business_analytics,
            self.get_contextual_insights,
            self.web_search
        ]
    
    def _get_context_suggestions(self, context_type: str) -> List[str]:
        """Get contextual suggestions based on business context"""
        if not self.business_context_manager:
            return []
        
        suggestions = self.business_context_manager.get_contextual_suggestions()
        if not suggestions:
            return []
        
        context_map = {
            "contacts": suggestions.follow_ups,
            "jobs": suggestions.quick_actions,
            "estimates": suggestions.opportunities,
            "urgent": suggestions.urgent_items
        }
        
        return context_map.get(context_type, [])
    
    def _get_smart_defaults(self, data_type: str) -> Dict[str, Any]:
        """Get smart defaults based on business context"""
        if not self.business_context_manager:
            return {}
        
        business_context = self.business_context_manager.get_business_context()
        if not business_context:
            return {}
        
        # Smart defaults based on business context
        defaults = {
            "contact_type": "customer",
            "priority": "medium",
            "timezone": business_context.timezone,
            "business_address": business_context.address
        }
        
        return defaults
    
    @function_tool
    async def create_contact(
        self,
        ctx: RunContext,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        contact_type: str = "lead",
        address: Optional[str] = None
    ) -> str:
        """Create a new contact in Hero365 with context-aware assistance.
        
        Args:
            name: Contact's full name (required)
            phone: Contact's phone number
            email: Contact's email address  
            contact_type: Type of contact (lead, customer, vendor)
            address: Contact's physical address
        """
        try:
            # Get smart defaults from business context
            defaults = self._get_smart_defaults("contact")
            
            # Check if contact already exists
            existing_contact = None
            if self.business_context_manager:
                existing_contact = self.business_context_manager.find_contact_by_name(name)
            
            if existing_contact:
                return f"ℹ️ Contact '{name}' already exists. Would you like to update their information instead?"
            
            contact_data = {
                "name": name,
                "phone": phone,
                "email": email,
                "contact_type": contact_type,
                "address": address
            }
            
            result = await self.hero365_tools.create_contact(contact_data)
            
            if result["success"]:
                response = f"✅ Successfully created contact '{name}'"
                
                # Add contextual suggestions
                suggestions = self._get_context_suggestions("contacts")
                if suggestions:
                    response += f"\n💡 Suggested next steps: {suggestions[0]}"
                
                return response
            else:
                return f"❌ Failed to create contact: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in create_contact: {e}")
            return f"❌ Error creating contact: {str(e)}"
    
    @function_tool
    async def search_contacts(self, ctx: RunContext, query: str, limit: int = 10) -> str:
        """Search for contacts with context-aware suggestions.
        
        Args:
            query: Search query (name, phone, email, etc.)
            limit: Maximum number of results to return
        """
        try:
            # First check business context for quick matches
            if self.business_context_manager:
                context_match = self.business_context_manager.find_contact_by_name(query)
                if context_match:
                    return f"🎯 Found in recent contacts: {context_match.name} - {context_match.phone or 'No phone'} - {context_match.email or 'No email'}"
            
            result = await self.hero365_tools.search_contacts(query, limit)
            
            if result["success"]:
                contacts = result["data"].get("contacts", [])
                if contacts:
                    response = f"🔍 Found {len(contacts)} contacts matching '{query}':\n"
                    for i, contact in enumerate(contacts[:5], 1):
                        response += f"{i}. {contact.get('name', 'Unknown')} - {contact.get('phone', 'No phone')} - {contact.get('email', 'No email')}\n"
                    
                    # Add contextual suggestions
                    suggestions = self._get_context_suggestions("contacts")
                    if suggestions:
                        response += f"\n💡 Related suggestions: {', '.join(suggestions[:2])}"
                    
                    return response
                else:
                    # Suggest creating a new contact
                    return f"🔍 No contacts found matching '{query}'. Would you like to create a new contact with that name?"
            else:
                return f"❌ Search failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in search_contacts: {e}")
            return f"❌ Error searching contacts: {str(e)}"
    
    @function_tool
    async def get_suggested_contacts(self, ctx: RunContext, limit: int = 5) -> str:
        """Get suggested contacts based on business context and recent activity.
        
        Args:
            limit: Maximum number of suggestions to return
        """
        try:
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
                suggestions = self._get_context_suggestions("contacts")
                if suggestions:
                    response += f"\n💡 Consider: {', '.join(suggestions[:2])}"
                
                return response
            else:
                return "📞 No recent contacts found. Would you like to create a new contact?"
                
        except Exception as e:
            logger.error(f"Error in get_suggested_contacts: {e}")
            return f"❌ Error getting contact suggestions: {str(e)}"
    
    @function_tool
    async def create_job(
        self,
        ctx: RunContext,
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
            # Get smart defaults from business context
            defaults = self._get_smart_defaults("job")
            
            # If no contact_id provided, try to find from title/description
            if not contact_id and self.business_context_manager:
                # Look for contact names in title or description
                recent_contacts = self.business_context_manager.get_recent_contacts(10)
                for contact in recent_contacts:
                    if contact.name.lower() in title.lower() or contact.name.lower() in description.lower():
                        contact_id = contact.id
                        break
            
            job_data = {
                "title": title,
                "description": description,
                "contact_id": contact_id,
                "scheduled_date": scheduled_date,
                "priority": priority,
                "estimated_duration": estimated_duration
            }
            
            result = await self.hero365_tools.create_job(job_data)
            
            if result["success"]:
                response = f"✅ Successfully created job '{title}'"
                
                # Add contextual suggestions
                suggestions = self._get_context_suggestions("jobs")
                if suggestions:
                    response += f"\n💡 Next steps: {suggestions[0]}"
                
                return response
            else:
                return f"❌ Failed to create job: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in create_job: {e}")
            return f"❌ Error creating job: {str(e)}"
    
    @function_tool
    async def get_upcoming_jobs(self, ctx: RunContext, days_ahead: int = 7) -> str:
        """Get upcoming jobs with context-aware insights.
        
        Args:
            days_ahead: Number of days to look ahead for jobs
        """
        try:
            # First check business context for quick overview
            if self.business_context_manager:
                business_summary = self.business_context_manager.get_business_summary()
                if business_summary:
                    context_response = f"📊 Quick overview: {business_summary.active_jobs} active jobs, {business_summary.upcoming_appointments} upcoming appointments\n\n"
                else:
                    context_response = ""
            else:
                context_response = ""
            
            result = await self.hero365_tools.get_upcoming_jobs(days_ahead)
            
            if result["success"]:
                jobs = result["data"].get("jobs", [])
                if jobs:
                    response = context_response + f"📅 Upcoming jobs for the next {days_ahead} days:\n"
                    for i, job in enumerate(jobs[:10], 1):
                        priority_icon = "🔥" if job.get('priority') == "high" else "📅"
                        response += f"{i}. {priority_icon} {job.get('title', 'Untitled')} - {job.get('scheduled_date', 'No date')}\n"
                    
                    # Add contextual suggestions
                    suggestions = self._get_context_suggestions("jobs")
                    if suggestions:
                        response += f"\n💡 Consider: {', '.join(suggestions[:2])}"
                    
                    return response
                else:
                    return context_response + f"📅 No upcoming jobs for the next {days_ahead} days"
            else:
                return f"❌ Failed to get upcoming jobs: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in get_upcoming_jobs: {e}")
            return f"❌ Error getting upcoming jobs: {str(e)}"
    
    @function_tool
    async def get_suggested_jobs(self, ctx: RunContext, limit: int = 5) -> str:
        """Get suggested jobs based on business context and activity.
        
        Args:
            limit: Maximum number of suggestions to return
        """
        try:
            if not self.business_context_manager:
                return "🔧 Business context not available for job suggestions"
            
            # Get recent jobs from business context
            recent_jobs = self.business_context_manager.get_recent_jobs(limit)
            
            if recent_jobs:
                response = f"🔧 Recent jobs that might need attention:\n"
                for i, job in enumerate(recent_jobs, 1):
                    priority_icon = "🔥" if job.priority == "high" else "🔧"
                    response += f"{i}. {priority_icon} {job.title} - {job.status} - {job.contact_name}\n"
                
                # Add contextual suggestions
                suggestions = self._get_context_suggestions("jobs")
                if suggestions:
                    response += f"\n💡 Quick actions: {', '.join(suggestions[:2])}"
                
                return response
            else:
                return "🔧 No recent jobs found. Would you like to create a new job?"
                
        except Exception as e:
            logger.error(f"Error in get_suggested_jobs: {e}")
            return f"❌ Error getting job suggestions: {str(e)}"
    
    @function_tool
    async def create_estimate(
        self,
        ctx: RunContext,
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
            # If no contact_id provided, try to find from title/description
            if not contact_id and self.business_context_manager:
                # Look for contact names in title or description
                recent_contacts = self.business_context_manager.get_recent_contacts(10)
                for contact in recent_contacts:
                    if contact.name.lower() in title.lower() or contact.name.lower() in description.lower():
                        contact_id = contact.id
                        break
            
            estimate_data = {
                "title": title,
                "description": description,
                "contact_id": contact_id,
                "total_amount": total_amount,
                "valid_until": valid_until
            }
            
            result = await self.hero365_tools.create_estimate(estimate_data)
            
            if result["success"]:
                response = f"✅ Successfully created estimate '{title}'"
                
                # Add contextual suggestions
                suggestions = self._get_context_suggestions("estimates")
                if suggestions:
                    response += f"\n💡 Next steps: {suggestions[0]}"
                
                return response
            else:
                return f"❌ Failed to create estimate: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in create_estimate: {e}")
            return f"❌ Error creating estimate: {str(e)}"
    
    @function_tool
    async def get_recent_estimates(self, ctx: RunContext, limit: int = 10) -> str:
        """Get recent estimates with context-aware insights.
        
        Args:
            limit: Maximum number of estimates to return
        """
        try:
            if not self.business_context_manager:
                return "📊 Business context not available for estimate insights"
            
            # Get recent estimates from business context
            recent_estimates = self.business_context_manager.get_recent_estimates(limit)
            
            if recent_estimates:
                response = f"📊 Recent estimates:\n"
                for i, estimate in enumerate(recent_estimates, 1):
                    status_icon = "💰" if estimate.status == "approved" else "📊"
                    amount_str = f"${estimate.total_amount:,.2f}" if estimate.total_amount else "No amount"
                    response += f"{i}. {status_icon} {estimate.title} - {estimate.status} - {amount_str} - {estimate.contact_name}\n"
                
                # Add contextual suggestions
                suggestions = self._get_context_suggestions("estimates")
                if suggestions:
                    response += f"\n💡 Opportunities: {', '.join(suggestions[:2])}"
                
                return response
            else:
                return "📊 No recent estimates found. Would you like to create a new estimate?"
                
        except Exception as e:
            logger.error(f"Error in get_recent_estimates: {e}")
            return f"❌ Error getting recent estimates: {str(e)}"
    
    @function_tool
    async def get_suggested_estimates(self, ctx: RunContext, limit: int = 5) -> str:
        """Get suggested estimates based on business context and opportunities.
        
        Args:
            limit: Maximum number of suggestions to return
        """
        try:
            if not self.business_context_manager:
                return "📊 Business context not available for estimate suggestions"
            
            # Get recent estimates from business context
            recent_estimates = self.business_context_manager.get_recent_estimates(limit)
            
            if recent_estimates:
                # Focus on draft estimates that need action
                draft_estimates = [e for e in recent_estimates if e.status == "draft"]
                
                if draft_estimates:
                    response = f"📊 Draft estimates that need attention:\n"
                    for i, estimate in enumerate(draft_estimates, 1):
                        response += f"{i}. 📝 {estimate.title} - {estimate.contact_name}"
                        if estimate.total_amount:
                            response += f" - ${estimate.total_amount:,.2f}"
                        response += "\n"
                    
                    # Add contextual suggestions
                    suggestions = self._get_context_suggestions("estimates")
                    if suggestions:
                        response += f"\n💡 Next steps: {', '.join(suggestions[:2])}"
                    
                    return response
                else:
                    return "📊 No draft estimates found. All estimates are up to date!"
            else:
                return "📊 No recent estimates found. Would you like to create a new estimate?"
                
        except Exception as e:
            logger.error(f"Error in get_suggested_estimates: {e}")
            return f"❌ Error getting estimate suggestions: {str(e)}"
    
    @function_tool
    async def get_contextual_insights(self, ctx: RunContext) -> str:
        """Get contextual business insights and suggestions based on current state.
        """
        try:
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
            logger.error(f"Error in get_contextual_insights: {e}")
            return f"❌ Error getting contextual insights: {str(e)}"
    
    @function_tool
    async def get_weather(self, ctx: RunContext, location: Optional[str] = None) -> str:
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
            
            result = await self.hero365_tools.get_weather_info(location)
            
            if result["success"]:
                response = result.get("voice_response", "Weather information retrieved successfully")
                
                # Add context-aware suggestions for outdoor jobs
                if self.business_context_manager:
                    upcoming_jobs = self.business_context_manager.get_recent_jobs(5)
                    outdoor_jobs = [j for j in upcoming_jobs if any(word in j.title.lower() for word in ["exterior", "outdoor", "roof", "siding", "landscape"])]
                    
                    if outdoor_jobs:
                        response += f"\n🔧 Weather impact: {len(outdoor_jobs)} outdoor jobs might be affected"
                
                return response
            else:
                return result.get("voice_response", f"❌ Failed to get weather: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in get_weather: {e}")
            return f"❌ Error getting weather: {str(e)}"
    
    @function_tool
    async def search_places(
        self,
        ctx: RunContext,
        query: str,
        location: Optional[str] = None,
        radius: int = 5000
    ) -> str:
        """Search for places nearby with business context awareness.
        
        Args:
            query: What to search for (e.g., "hardware store", "restaurant")
            location: Location to search near (if not provided, uses business location)
            radius: Search radius in meters
        """
        try:
            # Use business location as default if available
            if not location and self.business_context_manager:
                business_context = self.business_context_manager.get_business_context()
                if business_context and business_context.address:
                    location = business_context.address
            
            result = await self.hero365_tools.search_places(query, location, radius)
            
            if result["success"]:
                response = result.get("voice_response", "Places search completed successfully")
                
                # Add context-aware suggestions
                if "supply" in query.lower() or "hardware" in query.lower():
                    suggestions = self._get_context_suggestions("jobs")
                    if suggestions:
                        response += f"\n💡 For current jobs: {suggestions[0]}"
                
                return response
            else:
                return result.get("voice_response", f"❌ Failed to search places: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in search_places: {e}")
            return f"❌ Error searching places: {str(e)}"
    
    @function_tool
    async def get_directions(
        self,
        ctx: RunContext,
        destination: str,
        origin: Optional[str] = None,
        mode: str = "driving"
    ) -> str:
        """Get directions with business context awareness.
        
        Args:
            destination: Where to go
            origin: Starting point (if not provided, uses business location)
            mode: Travel mode (driving, walking, transit)
        """
        try:
            # Use business location as default origin if available
            if not origin and self.business_context_manager:
                business_context = self.business_context_manager.get_business_context()
                if business_context and business_context.address:
                    origin = business_context.address
            
            result = await self.hero365_tools.get_directions(destination, origin, mode)
            
            if result["success"]:
                response = result.get("voice_response", "Directions retrieved successfully")
                
                # Add context-aware job suggestions
                if self.business_context_manager:
                    # Check if destination matches any job locations
                    recent_jobs = self.business_context_manager.get_recent_jobs(10)
                    matching_jobs = [j for j in recent_jobs if j.location and destination.lower() in j.location.lower()]
                    
                    if matching_jobs:
                        response += f"\n🔧 Related jobs at this location: {matching_jobs[0].title}"
                
                return response
            else:
                return result.get("voice_response", f"❌ Failed to get directions: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in get_directions: {e}")
            return f"❌ Error getting directions: {str(e)}"
    
    @function_tool
    async def universal_search(self, ctx: RunContext, query: str, limit: int = 10) -> str:
        """Context-aware universal search across all Hero365 data.
        
        Args:
            query: Search query
            limit: Maximum number of results per category
        """
        try:
            # First check business context for quick matches
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
            
            # Perform full search
            result = await self.hero365_tools.universal_search(query, limit)
            
            if result["success"]:
                data = result["data"]
                total_count = data.get("total_count", 0)
                
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
                    contacts = data.get("contacts", [])
                    if contacts:
                        response += f"\n📞 Contacts ({len(contacts)}):\n"
                        for contact in contacts[:3]:
                            response += f"• {contact.get('name', 'Unknown')}\n"
                    
                    # Jobs
                    jobs = data.get("jobs", [])
                    if jobs:
                        response += f"\n🔧 Jobs ({len(jobs)}):\n"
                        for job in jobs[:3]:
                            response += f"• {job.get('title', 'Untitled')}\n"
                    
                    # Estimates
                    estimates = data.get("estimates", [])
                    if estimates:
                        response += f"\n📋 Estimates ({len(estimates)}):\n"
                        for estimate in estimates[:3]:
                            response += f"• {estimate.get('title', 'Untitled')}\n"
                    
                    return response
                else:
                    if context_results:
                        return response + f"No additional results found for '{query}'"
                    else:
                        return f"🔍 No results found for '{query}'"
            else:
                return f"❌ Search failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in universal_search: {e}")
            return f"❌ Error in search: {str(e)}"
    
    @function_tool
    async def get_business_analytics(self, ctx: RunContext, period: str = "month") -> str:
        """Get business analytics with contextual insights.
        
        Args:
            period: Time period for analytics (day, week, month, year)
        """
        try:
            # Add business context summary
            context_summary = ""
            if self.business_context_manager:
                business_summary = self.business_context_manager.get_business_summary()
                if business_summary:
                    context_summary = f"📊 Current snapshot: {business_summary.active_jobs} active jobs, {business_summary.pending_estimates} pending estimates\n\n"
            
            result = await self.hero365_tools.get_business_analytics(period)
            
            if result["success"]:
                data = result["data"]
                response = context_summary + f"📊 Business Analytics for {period}:\n"
                response += f"• Total Jobs: {data.get('total_jobs', 0)}\n"
                response += f"• Completed Jobs: {data.get('completed_jobs', 0)}\n"
                response += f"• Total Revenue: ${data.get('total_revenue', 0):,.2f}\n"
                response += f"• Pending Estimates: {data.get('pending_estimates', 0)}\n"
                response += f"• Overdue Invoices: {data.get('overdue_invoices', 0)}\n"
                
                # Add contextual suggestions
                suggestions = self._get_context_suggestions("urgent")
                if suggestions:
                    response += f"\n🔥 Urgent attention needed: {suggestions[0]}"
                
                return response
            else:
                return f"❌ Failed to get analytics: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in get_business_analytics: {e}")
            return f"❌ Error getting analytics: {str(e)}"
    
    @function_tool
    async def web_search(self, ctx: RunContext, query: str, num_results: int = 5) -> str:
        """Perform web search with business context awareness.
        
        Args:
            query: Search query
            num_results: Number of results to return
        """
        try:
            result = await self.hero365_tools.web_search(query, num_results)
            
            if result["success"]:
                response = result.get("voice_response", "Web search completed successfully")
                
                # Add context-aware suggestions for business-related searches
                if any(word in query.lower() for word in ["contractor", "service", "repair", "installation"]):
                    suggestions = self._get_context_suggestions("jobs")
                    if suggestions:
                        response += f"\n💡 Related to your business: {suggestions[0]}"
                
                return response
            else:
                return result.get("voice_response", f"❌ Failed to search web: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in web_search: {e}")
            return f"❌ Error searching web: {str(e)}" 