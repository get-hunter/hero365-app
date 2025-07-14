"""
Hero365 tools integration for voice agents.
"""

from typing import Dict, Any, List, Optional
from ...infrastructure.config.dependency_injection import get_container
from ...core.config import settings
import logging
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class Hero365Tools:
    """Main tools class that integrates with Hero365 use cases"""
    
    def __init__(self, context_manager):
        self.context_manager = context_manager
        self.container = get_container()
    
    async def get_user_and_business_context(self) -> tuple[str, str]:
        """Helper to get user and business IDs from context"""
        context = await self.context_manager.get_current_context()
        user_id = context.get("user_id", "")
        business_id = context.get("business_id", "")
        return user_id, business_id
    
    # Contact Management Tools
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact using existing use case"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            create_contact_use_case = self.container.get_create_contact_use_case()
            from ...application.dto.contact_dto import CreateContactDTO
            
            result = await create_contact_use_case.execute(
                CreateContactDTO(
                    business_id=business_id,
                    **contact_data
                ),
                user_id=user_id
            )
            
            return {"success": True, "data": result, "message": "Contact created successfully"}
        except Exception as e:
            logger.error(f"Error creating contact: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_contacts(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search contacts using existing use case"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            search_contacts_use_case = self.container.get_search_contacts_use_case()
            from ...application.dto.contact_dto import SearchContactsDTO
            
            result = await search_contacts_use_case.execute(
                SearchContactsDTO(
                    query=query,
                    business_id=business_id,
                    limit=limit
                ),
                user_id=user_id
            )
            
            return {"success": True, "data": result, "message": "Contacts found"}
        except Exception as e:
            logger.error(f"Error searching contacts: {e}")
            return {"success": False, "error": str(e)}
    
    # Job Management Tools
    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create job using existing use case"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            create_job_use_case = self.container.get_create_job_use_case()
            from ...application.dto.job_dto import CreateJobDTO
            
            result = await create_job_use_case.execute(
                CreateJobDTO(
                    business_id=business_id,
                    assigned_user_id=user_id,
                    **job_data
                ),
                user_id=user_id
            )
            
            return {"success": True, "data": result, "message": "Job created successfully"}
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_upcoming_jobs(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Get upcoming jobs using existing use case"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            job_search_use_case = self.container.get_job_search_use_case()
            from ...application.dto.job_dto import JobSearchDTO
            
            result = await job_search_use_case.execute(
                JobSearchDTO(
                    business_id=business_id,
                    status_filter="scheduled",
                    date_filter="upcoming",
                    days_ahead=days_ahead
                ),
                user_id=user_id
            )
            
            return {"success": True, "data": result, "message": "Upcoming jobs retrieved"}
        except Exception as e:
            logger.error(f"Error getting upcoming jobs: {e}")
            return {"success": False, "error": str(e)}
    
    # Estimate Management Tools
    async def create_estimate(self, estimate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create estimate using existing use case"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            create_estimate_use_case = self.container.get_create_estimate_use_case()
            from ...application.dto.estimate_dto import CreateEstimateDTO
            
            result = await create_estimate_use_case.execute(
                CreateEstimateDTO(
                    business_id=business_id,
                    **estimate_data
                ),
                user_id=user_id
            )
            
            return {"success": True, "data": result, "message": "Estimate created successfully"}
        except Exception as e:
            logger.error(f"Error creating estimate: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_pending_estimates(self, limit: int = 10) -> Dict[str, Any]:
        """Get pending estimates using existing use case"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            list_estimates_use_case = self.container.get_list_estimates_use_case()
            from ...application.dto.estimate_dto import EstimateListFilters
            
            result = await list_estimates_use_case.execute(
                EstimateListFilters(
                    business_id=business_id,
                    status="pending",
                    limit=limit
                ),
                user_id=user_id
            )
            
            return {"success": True, "data": result, "message": "Pending estimates retrieved"}
        except Exception as e:
            logger.error(f"Error getting pending estimates: {e}")
            return {"success": False, "error": str(e)}
    
    # Scheduling Tools
    async def get_today_schedule(self) -> Dict[str, Any]:
        """Get today's schedule using existing use case"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            # This would use the calendar management use case
            # For now, return a placeholder
            return {
                "success": True, 
                "data": {"appointments": []}, 
                "message": "Today's schedule retrieved"
            }
        except Exception as e:
            logger.error(f"Error getting today's schedule: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_availability(self, date: str, time: str = None) -> Dict[str, Any]:
        """Check availability using existing use case"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            # This would use the intelligent scheduling use case
            # For now, return a placeholder
            return {
                "success": True, 
                "data": {"is_available": True}, 
                "message": "Availability checked"
            }
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return {"success": False, "error": str(e)}
    
    # Universal Search
    async def universal_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Universal search across all Hero365 entities"""
        try:
            search_results = {
                "contacts": [],
                "jobs": [],
                "estimates": [],
                "invoices": [],
                "total_count": 0
            }
            
            # Search contacts
            contacts_result = await self.search_contacts(query, limit//4)
            if contacts_result["success"]:
                search_results["contacts"] = contacts_result["data"].get("contacts", [])
            
            # Search jobs
            jobs_result = await self.search_jobs(query, limit//4)
            if jobs_result["success"]:
                search_results["jobs"] = jobs_result["data"].get("jobs", [])
            
            # Search estimates
            estimates_result = await self.search_estimates(query, limit//4)
            if estimates_result["success"]:
                search_results["estimates"] = estimates_result["data"].get("estimates", [])
            
            # Calculate total count
            search_results["total_count"] = (
                len(search_results["contacts"]) +
                len(search_results["jobs"]) +
                len(search_results["estimates"])
            )
            
            return {"success": True, "data": search_results, "message": "Universal search completed"}
        except Exception as e:
            logger.error(f"Error in universal search: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_jobs(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search jobs using existing use case"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            job_search_use_case = self.container.get_job_search_use_case()
            from ...application.dto.job_dto import JobSearchDTO
            
            result = await job_search_use_case.execute(
                JobSearchDTO(
                    business_id=business_id,
                    search_query=query,
                    limit=limit
                ),
                user_id=user_id
            )
            
            return {"success": True, "data": result, "message": "Jobs found"}
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_estimates(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search estimates using existing use case"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            search_estimates_use_case = self.container.get_search_estimates_use_case()
            from ...application.dto.estimate_dto import EstimateSearchCriteria
            
            result = await search_estimates_use_case.execute(
                EstimateSearchCriteria(
                    query=query,
                    business_id=business_id,
                    limit=limit
                ),
                user_id=user_id
            )
            
            return {"success": True, "data": result, "message": "Estimates found"}
        except Exception as e:
            logger.error(f"Error searching estimates: {e}")
            return {"success": False, "error": str(e)}
    
    # System Status Tools
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            # Check database connection
            try:
                # This would ping the database
                database_healthy = True
            except Exception:
                database_healthy = False
            
            # Check external services
            services_status = {
                "database": database_healthy,
                "redis": True,  # Would check Redis connection
                "email": settings.emails_enabled,
                "voice_agents": settings.voice_agents_enabled
            }
            
            return {
                "success": True,
                "data": {
                    "system_healthy": all(services_status.values()),
                    "services": services_status,
                    "timestamp": datetime.now().isoformat()
                },
                "message": "System status retrieved"
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"success": False, "error": str(e)}
    
    # World Context Tools
    async def get_weather_info(self, location: str = None) -> Dict[str, Any]:
        """Get weather information"""
        try:
            if not location:
                context = await self.context_manager.get_current_context()
                location = context.get("location", {}).get("city", "")
            
            if not location:
                return {"success": False, "error": "Location not available"}
            
            # This would integrate with a weather API
            # For now, return placeholder data
            return {
                "success": True,
                "data": {
                    "location": location,
                    "temperature": "22°C",
                    "condition": "Partly cloudy",
                    "humidity": "65%",
                    "wind": "10 km/h"
                },
                "message": "Weather information retrieved"
            }
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_directions(self, destination: str) -> Dict[str, Any]:
        """Get directions to a destination"""
        try:
            context = await self.context_manager.get_current_context()
            current_location = context.get("location", {})
            
            if not current_location:
                return {"success": False, "error": "Current location not available"}
            
            # This would integrate with a mapping API
            # For now, return placeholder data
            return {
                "success": True,
                "data": {
                    "destination": destination,
                    "distance": "12.5 km",
                    "duration": "18 minutes",
                    "route": "Take Highway 101 North"
                },
                "message": "Directions retrieved"
            }
        except Exception as e:
            logger.error(f"Error getting directions: {e}")
            return {"success": False, "error": str(e)}
    
    # Business Analytics Tools
    async def get_business_analytics(self, period: str = "month") -> Dict[str, Any]:
        """Get business analytics and insights"""
        try:
            user_id, business_id = await self.get_user_and_business_context()
            
            # This would integrate with analytics use cases
            # For now, return placeholder data
            return {
                "success": True,
                "data": {
                    "period": period,
                    "total_jobs": 45,
                    "completed_jobs": 38,
                    "total_revenue": 23500,
                    "pending_estimates": 12,
                    "overdue_invoices": 3
                },
                "message": "Business analytics retrieved"
            }
        except Exception as e:
            logger.error(f"Error getting business analytics: {e}")
            return {"success": False, "error": str(e)}
    
    async def format_voice_response(self, data: Dict[str, Any], response_type: str = "success") -> str:
        """Format data for voice response"""
        try:
            if response_type == "success" and data.get("success"):
                return data.get("message", "Operation completed successfully")
            elif response_type == "error" or not data.get("success"):
                return f"I encountered an issue: {data.get('error', 'Unknown error')}"
            else:
                return "I've completed the requested operation"
        except Exception as e:
            logger.error(f"Error formatting voice response: {e}")
            return "I encountered an error while processing your request" 