"""
Job Management Tools for Hero365 LiveKit Agents
"""

import logging
from typing import Dict, Any, Optional
from livekit.agents import function_tool

from ..context import BusinessContextManager

logger = logging.getLogger(__name__)


class JobTools:
    """Job management tools for the Hero365 agent"""
    
    def __init__(self, session_context: Dict[str, Any], context_intelligence: Optional[Any] = None):
        self.session_context = session_context
        self.context_intelligence = context_intelligence
    
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
            if not contact_id and self.context_intelligence:
                recent_contacts = self.context_intelligence.get_recent_contacts(10)
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
            if self.context_intelligence:
                suggestions = self.context_intelligence.get_contextual_suggestions()
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
            if self.context_intelligence:
                business_summary = self.context_intelligence.get_business_summary()
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
                if self.context_intelligence:
                    suggestions = self.context_intelligence.get_contextual_suggestions()
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

    @function_tool
    async def get_suggested_jobs(self, limit: int = 5) -> str:
        """Get suggested jobs based on business context and activity.
        
        Args:
            limit: Maximum number of suggestions to return
        """
        try:
            logger.info("💡 Getting suggested jobs")
            
            if not self.context_intelligence:
                return "🔧 Business context not available for job suggestions"
            
            # Get recent jobs from business context
            recent_jobs = self.context_intelligence.get_recent_jobs(limit)
            
            if recent_jobs:
                response = f"🔧 Recent jobs that might need attention:\n"
                for i, job in enumerate(recent_jobs, 1):
                    priority_icon = "🔥" if job.priority.value == "high" else "🔧"
                    response += f"{i}. {priority_icon} {job.title} - {job.status.value} - {job.contact_name}\n"
                
                # Add contextual suggestions
                suggestions = self.context_intelligence.get_contextual_suggestions()
                if suggestions and suggestions.quick_actions:
                    response += f"\n💡 Quick actions: {', '.join(suggestions.quick_actions[:2])}"
                
                return response
            else:
                return "🔧 No recent jobs found. Would you like to create a new job?"
                
        except Exception as e:
            logger.error(f"❌ Error getting job suggestions: {e}")
            return f"❌ Error getting job suggestions: {str(e)}"

    @function_tool
    async def search_jobs(self, query: str, limit: int = 10) -> str:
        """Search for jobs with context-aware suggestions.
        
        Args:
            query: Search query (title, description, contact name, etc.)
            limit: Maximum number of results to return
        """
        try:
            logger.info(f"🔍 Searching jobs for: {query}")
            
            # First check business context for quick matches
            if self.context_intelligence:
                context_match = self.context_intelligence.find_job_by_title(query)
                if context_match:
                    return f"🎯 Found in recent jobs: {context_match.title} - {context_match.status.value} - {context_match.contact_name}"
            
            # Simulate search results (replace with actual API call)
            jobs = [
                {"title": f"Sample Job {i}", "status": "active", "contact_name": f"Contact {i}"}
                for i in range(1, min(limit, 4))
            ]
            
            if jobs:
                response = f"🔍 Found {len(jobs)} jobs matching '{query}':\n"
                for i, job in enumerate(jobs, 1):
                    response += f"{i}. {job['title']} - {job['status']} - {job['contact_name']}\n"
                
                # Add contextual suggestions
                if self.context_intelligence:
                    suggestions = self.context_intelligence.get_contextual_suggestions()
                    if suggestions and suggestions.quick_actions:
                        response += f"\n💡 Related suggestion: {suggestions.quick_actions[0]}"
                
                return response
            else:
                return f"🔍 No jobs found matching '{query}'. Would you like to create a new job?"
                
        except Exception as e:
            logger.error(f"❌ Error searching jobs: {e}")
            return f"❌ Error searching jobs: {str(e)}" 