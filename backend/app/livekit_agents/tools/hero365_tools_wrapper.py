"""
Hero365 Tools Wrapper for LiveKit Agents
Integrates existing Hero365 tools with LiveKit function_tool decorator
"""

from typing import Dict, Any, Optional
from livekit.agents import function_tool, RunContext
from ...voice_agents.tools.hero365_tools import Hero365Tools
from ...voice_agents.tools.world_context_tools import world_context_tools
from ...infrastructure.config.dependency_injection import get_container
import logging

logger = logging.getLogger(__name__)

class Hero365ToolsWrapper:
    """Wrapper for Hero365 tools to work with LiveKit function_tool decorator"""
    
    def __init__(self, context_manager=None):
        self.hero365_tools = Hero365Tools(context_manager)
        
    def get_available_tools(self):
        """Get list of available tools as functions"""
        return [
            self.create_contact,
            self.search_contacts,
            self.create_job,
            self.get_upcoming_jobs,
            self.create_estimate,
            self.get_weather,
            self.search_places,
            self.get_directions,
            self.universal_search,
            self.get_business_analytics,
            self.web_search
        ]
    
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
        """Create a new contact in Hero365.
        
        Args:
            name: Contact's full name (required)
            phone: Contact's phone number
            email: Contact's email address  
            contact_type: Type of contact (lead, customer, vendor)
            address: Contact's physical address
        """
        try:
            contact_data = {
                "name": name,
                "phone": phone,
                "email": email,
                "contact_type": contact_type,
                "address": address
            }
            
            result = await self.hero365_tools.create_contact(contact_data)
            
            if result["success"]:
                return f"✅ Successfully created contact '{name}'. {result.get('message', '')}"
            else:
                return f"❌ Failed to create contact: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in create_contact: {e}")
            return f"❌ Error creating contact: {str(e)}"
    
    @function_tool
    async def search_contacts(self, ctx: RunContext, query: str, limit: int = 10) -> str:
        """Search for contacts in Hero365.
        
        Args:
            query: Search query (name, phone, email, etc.)
            limit: Maximum number of results to return
        """
        try:
            result = await self.hero365_tools.search_contacts(query, limit)
            
            if result["success"]:
                contacts = result["data"].get("contacts", [])
                if contacts:
                    response = f"🔍 Found {len(contacts)} contacts matching '{query}':\n"
                    for i, contact in enumerate(contacts[:5], 1):
                        response += f"{i}. {contact.get('name', 'Unknown')} - {contact.get('phone', 'No phone')} - {contact.get('email', 'No email')}\n"
                    return response
                else:
                    return f"🔍 No contacts found matching '{query}'"
            else:
                return f"❌ Search failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in search_contacts: {e}")
            return f"❌ Error searching contacts: {str(e)}"
    
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
        """Create a new job in Hero365.
        
        Args:
            title: Job title/summary
            description: Detailed job description
            contact_id: ID of the contact for this job
            scheduled_date: When the job is scheduled (YYYY-MM-DD format)
            priority: Job priority (low, medium, high, urgent)
            estimated_duration: Estimated duration in hours
        """
        try:
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
                return f"✅ Successfully created job '{title}'. {result.get('message', '')}"
            else:
                return f"❌ Failed to create job: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in create_job: {e}")
            return f"❌ Error creating job: {str(e)}"
    
    @function_tool
    async def get_upcoming_jobs(self, ctx: RunContext, days_ahead: int = 7) -> str:
        """Get upcoming jobs for the next specified days.
        
        Args:
            days_ahead: Number of days to look ahead for jobs
        """
        try:
            result = await self.hero365_tools.get_upcoming_jobs(days_ahead)
            
            if result["success"]:
                jobs = result["data"].get("jobs", [])
                if jobs:
                    response = f"📅 Upcoming jobs for the next {days_ahead} days:\n"
                    for i, job in enumerate(jobs[:10], 1):
                        response += f"{i}. {job.get('title', 'Untitled')} - {job.get('scheduled_date', 'No date')}\n"
                    return response
                else:
                    return f"📅 No upcoming jobs for the next {days_ahead} days"
            else:
                return f"❌ Failed to get upcoming jobs: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in get_upcoming_jobs: {e}")
            return f"❌ Error getting upcoming jobs: {str(e)}"
    
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
        """Create a new estimate in Hero365.
        
        Args:
            title: Estimate title/summary
            description: Detailed estimate description
            contact_id: ID of the contact for this estimate
            total_amount: Total estimated amount
            valid_until: Estimate validity date (YYYY-MM-DD format)
        """
        try:
            estimate_data = {
                "title": title,
                "description": description,
                "contact_id": contact_id,
                "total_amount": total_amount,
                "valid_until": valid_until
            }
            
            result = await self.hero365_tools.create_estimate(estimate_data)
            
            if result["success"]:
                return f"✅ Successfully created estimate '{title}'. {result.get('message', '')}"
            else:
                return f"❌ Failed to create estimate: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in create_estimate: {e}")
            return f"❌ Error creating estimate: {str(e)}"
    
    @function_tool
    async def get_weather(self, ctx: RunContext, location: Optional[str] = None) -> str:
        """Get current weather information.
        
        Args:
            location: Location to get weather for (if not provided, uses user's location)
        """
        try:
            result = await self.hero365_tools.get_weather_info(location)
            
            if result["success"]:
                return result.get("voice_response", "Weather information retrieved successfully")
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
        """Search for places nearby.
        
        Args:
            query: What to search for (e.g., "hardware store", "restaurant")
            location: Location to search near (if not provided, uses user's location)
            radius: Search radius in meters
        """
        try:
            result = await self.hero365_tools.search_places(query, location, radius)
            
            if result["success"]:
                return result.get("voice_response", "Places search completed successfully")
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
        """Get directions to a destination.
        
        Args:
            destination: Where to go
            origin: Starting point (if not provided, uses user's location)
            mode: Travel mode (driving, walking, transit)
        """
        try:
            result = await self.hero365_tools.get_directions(destination, origin, mode)
            
            if result["success"]:
                return result.get("voice_response", "Directions retrieved successfully")
            else:
                return result.get("voice_response", f"❌ Failed to get directions: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in get_directions: {e}")
            return f"❌ Error getting directions: {str(e)}"
    
    @function_tool
    async def universal_search(self, ctx: RunContext, query: str, limit: int = 10) -> str:
        """Search across all Hero365 data (contacts, jobs, estimates, etc.).
        
        Args:
            query: Search query
            limit: Maximum number of results per category
        """
        try:
            result = await self.hero365_tools.universal_search(query, limit)
            
            if result["success"]:
                data = result["data"]
                total_count = data.get("total_count", 0)
                
                if total_count > 0:
                    response = f"🔍 Found {total_count} results for '{query}':\n"
                    
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
                    return f"🔍 No results found for '{query}'"
            else:
                return f"❌ Search failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in universal_search: {e}")
            return f"❌ Error in search: {str(e)}"
    
    @function_tool
    async def get_business_analytics(self, ctx: RunContext, period: str = "month") -> str:
        """Get business analytics and insights.
        
        Args:
            period: Time period for analytics (day, week, month, year)
        """
        try:
            result = await self.hero365_tools.get_business_analytics(period)
            
            if result["success"]:
                data = result["data"]
                response = f"📊 Business Analytics for {period}:\n"
                response += f"• Total Jobs: {data.get('total_jobs', 0)}\n"
                response += f"• Completed Jobs: {data.get('completed_jobs', 0)}\n"
                response += f"• Total Revenue: ${data.get('total_revenue', 0):,.2f}\n"
                response += f"• Pending Estimates: {data.get('pending_estimates', 0)}\n"
                response += f"• Overdue Invoices: {data.get('overdue_invoices', 0)}\n"
                return response
            else:
                return f"❌ Failed to get analytics: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in get_business_analytics: {e}")
            return f"❌ Error getting analytics: {str(e)}"
    
    @function_tool
    async def web_search(self, ctx: RunContext, query: str, num_results: int = 5) -> str:
        """Perform web search for general information.
        
        Args:
            query: Search query
            num_results: Number of results to return
        """
        try:
            result = await self.hero365_tools.web_search(query, num_results)
            
            if result["success"]:
                return result.get("voice_response", "Web search completed successfully")
            else:
                return result.get("voice_response", f"❌ Failed to search web: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in web_search: {e}")
            return f"❌ Error searching web: {str(e)}" 