"""
Job management specialist agent for Hero365 LiveKit voice system.
"""

from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import logging
import re

from livekit.agents import Agent, RunContext, function_tool
from ..config import LiveKitConfig
from ..business_context_manager import BusinessContextManager

logger = logging.getLogger(__name__)


class JobAgent(Agent):
    """Specialist agent for job management using LiveKit agents"""
    
    def __init__(self, config: LiveKitConfig):
        """
        Initialize job management specialist.
        
        Args:
            config: LiveKit configuration
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        instructions = f"""
        You are the job management specialist for Hero365. You help users manage their 
        jobs efficiently and professionally.
        
        CURRENT DATE AND TIME: Today is {current_date} at {current_time}
        
        You have access to tools for:
        - Creating new jobs
        - Updating job status and details
        - Searching for jobs
        - Getting job details
        - Managing job schedules
        - Tracking job progress
        
        Always be helpful and ask for clarification if needed. When creating jobs,
        collect the required information naturally through conversation.
        
        JOB INFORMATION PRIORITY:
        1. Title (required)
        2. Description (required)
        3. Contact ID (required)
        4. Scheduled date (required)
        5. Duration and priority (optional)
        """
        
        # Initialize as LiveKit Agent with tools
        super().__init__(
            instructions=instructions,
            tools=[
                self.create_job,
                self.search_jobs,
                self.update_job,
                self.get_job_details,
                self.get_upcoming_jobs,
                self.mark_job_complete,
                self.get_job_statistics,
            ]
        )
        
        self.config = config
        self.business_context_manager: Optional[BusinessContextManager] = None
        
        # Job-specific configuration
        self.job_context = {}
        self.current_job = None
        
    def set_business_context(self, business_context_manager: BusinessContextManager):
        """Set business context manager for context-aware operations"""
        self.business_context_manager = business_context_manager
        logger.info("🔧 Business context set for job agent")
    
    @function_tool
    async def create_job(self,
                        ctx: RunContext,
                        title: str,
                        description: str,
                        contact_id: str,
                        scheduled_date: str,
                        estimated_duration: int = 120,
                        priority: str = "medium",
                        notes: Optional[str] = None) -> str:
        """Create a new job with the provided information"""
        try:
            logger.info(f"Creating job: {title}")
            
            # Mock job creation (would integrate with real system)
            job_id = f"job_{uuid.uuid4().hex[:8]}"
            
            response = f"✅ Job '{title}' created successfully! Scheduled for {scheduled_date}. Job ID: {job_id}"
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self._get_context_suggestions()
                if suggestions:
                    response += f"\n💡 Suggested next steps: {suggestions[0]}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            return f"❌ I encountered an error while creating the job: {str(e)}"
    
    @function_tool
    async def search_jobs(self, ctx: RunContext, query: str, limit: int = 10) -> str:
        """Search for jobs by title, description, or status"""
        try:
            logger.info(f"Searching jobs for: {query}")
            
            # Mock search results (would integrate with real system)
            mock_results = [
                {"title": f"Sample Job {i}", "status": "active", "scheduled_date": "2025-07-20"}
                for i in range(1, min(limit, 4))
            ]
            
            if not mock_results:
                return f"No jobs found matching '{query}'"
            
            jobs_text = "\n".join([
                f"• {job['title']} - {job['status']} - {job['scheduled_date']}"
                for job in mock_results
            ])
            
            return f"🔧 Found {len(mock_results)} job(s) matching '{query}':\n{jobs_text}"
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return f"❌ I encountered an error while searching for jobs: {str(e)}"
    
    @function_tool
    async def update_job(self, ctx: RunContext, job_id: str, updates: Dict[str, Any]) -> str:
        """Update job information"""
        try:
            logger.info(f"Updating job: {job_id}")
            
            # Mock job update (would integrate with real system)
            update_fields = ", ".join(updates.keys())
            
            return f"✅ Job {job_id} updated successfully! Updated fields: {update_fields}"
            
        except Exception as e:
            logger.error(f"Error updating job: {e}")
            return f"❌ I encountered an error while updating the job: {str(e)}"
    
    @function_tool
    async def get_job_details(self, ctx: RunContext, job_id: str) -> str:
        """Get detailed information about a specific job"""
        try:
            logger.info(f"Getting job details for: {job_id}")
            
            # Mock job details (would integrate with real system)
            return f"📋 Job Details for {job_id}:\n• Title: Sample Job\n• Status: Active\n• Scheduled: 2025-07-20\n• Duration: 2 hours\n• Priority: Medium"
            
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return f"❌ I encountered an error while getting job details: {str(e)}"
    
    @function_tool
    async def get_upcoming_jobs(self, ctx: RunContext, days: int = 7) -> str:
        """Get upcoming jobs for the next N days"""
        try:
            logger.info(f"Getting upcoming jobs for next {days} days")
            
            # Mock upcoming jobs (would integrate with real system)
            upcoming_jobs = [
                {"title": "Sample Job 1", "date": "2025-07-19", "time": "10:00 AM"},
                {"title": "Sample Job 2", "date": "2025-07-20", "time": "2:00 PM"}
            ]
            
            if not upcoming_jobs:
                return f"📅 No jobs scheduled for the next {days} days"
            
            jobs_text = "\n".join([
                f"• {job['title']} - {job['date']} at {job['time']}"
                for job in upcoming_jobs
            ])
            
            return f"📅 Upcoming jobs for the next {days} days:\n{jobs_text}"
            
        except Exception as e:
            logger.error(f"Error getting upcoming jobs: {e}")
            return f"❌ I encountered an error while getting upcoming jobs: {str(e)}"
    
    @function_tool
    async def mark_job_complete(self, ctx: RunContext, job_id: str, completion_notes: Optional[str] = None) -> str:
        """Mark a job as complete"""
        try:
            logger.info(f"Marking job complete: {job_id}")
            
            # Mock job completion (would integrate with real system)
            response = f"✅ Job {job_id} marked as complete!"
            
            if completion_notes:
                response += f"\n📝 Notes: {completion_notes}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error marking job complete: {e}")
            return f"❌ I encountered an error while marking job complete: {str(e)}"
    
    @function_tool
    async def get_job_statistics(self, ctx: RunContext) -> str:
        """Get job statistics and overview"""
        try:
            logger.info("Getting job statistics")
            
            # Mock job statistics (would integrate with real system)
            stats = {
                "total_jobs": 45,
                "active_jobs": 12,
                "completed_jobs": 28,
                "pending_jobs": 5,
                "overdue_jobs": 2
            }
            
            response = f"📊 Job Statistics:\n"
            response += f"• Total jobs: {stats['total_jobs']}\n"
            response += f"• Active jobs: {stats['active_jobs']}\n"
            response += f"• Completed jobs: {stats['completed_jobs']}\n"
            response += f"• Pending jobs: {stats['pending_jobs']}\n"
            response += f"• Overdue jobs: {stats['overdue_jobs']}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting job statistics: {e}")
            return f"❌ I encountered an error while getting job statistics: {str(e)}"
    
    def _get_context_suggestions(self) -> List[str]:
        """Get contextual suggestions based on business context"""
        suggestions = []
        
        if self.business_context_manager:
            business_context = self.business_context_manager.get_business_context()
            if business_context:
                # Add contextual suggestions based on business state
                suggestions.append("Schedule follow-up call with customer")
                suggestions.append("Create related estimate if needed")
                suggestions.append("Set up materials and equipment")
        
        return suggestions 