"""
Job management specialist agent for Hero365 LiveKit voice system.
"""

from typing import Optional, List
import uuid
from datetime import datetime
import logging

from livekit.agents import llm, function_tool
from ..base_agent import Hero365BaseAgent
from ..config import LiveKitConfig

logger = logging.getLogger(__name__)


class JobAgent(Hero365BaseAgent):
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
        
        super().__init__(
            name="Job Management Specialist",
            instructions=instructions
        )
    
    @function_tool
    async def create_job(self,
                        title: str,
                        description: str,
                        contact_id: str,
                        scheduled_date: str,
                        estimated_duration: int = 120,
                        priority: str = "medium",
                        notes: Optional[str] = None) -> str:
        """Create a new job with the provided information"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the create job use case
            create_job_use_case = self.container.get_create_job_use_case()
            
            from ...application.dto.job_dto import CreateJobDTO
            
            # Execute use case
            result = await create_job_use_case.execute(
                CreateJobDTO(
                    title=title,
                    description=description,
                    contact_id=contact_id,
                    scheduled_date=scheduled_date,
                    estimated_duration=estimated_duration,
                    priority=priority,
                    notes=notes,
                    business_id=business_id,
                    assigned_user_id=user_id
                ),
                user_id=user_id
            )
            
            return f"✅ Job '{title}' created successfully! Scheduled for {scheduled_date}. Job ID: {result.id}"
            
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            return f"❌ I encountered an error while creating the job: {str(e)}"
    
    @function_tool
    async def update_job_status(self,
                               job_id: str,
                               new_status: str,
                               notes: Optional[str] = None) -> str:
        """Update the status of an existing job"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the update job use case
            update_job_use_case = self.container.get_update_job_use_case()
            
            from ...application.dto.job_dto import UpdateJobDTO
            
            # Execute use case
            result = await update_job_use_case.execute(
                UpdateJobDTO(
                    job_id=job_id,
                    status=new_status,
                    notes=notes,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return f"✅ Job status updated to '{new_status}' successfully!"
            
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
            return f"❌ I encountered an error while updating the job status: {str(e)}"
    
    @function_tool
    async def get_job_details(self, job_id: str) -> str:
        """Get detailed information about a specific job"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the get job details use case
            get_job_details_use_case = self.container.get_get_job_details_use_case()
            
            from ...application.dto.job_dto import GetJobDetailsDTO
            
            # Execute use case
            result = await get_job_details_use_case.execute(
                GetJobDetailsDTO(
                    job_id=job_id,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            job = result.job
            details = f"""
🔧 Job Details:
• Title: {job.title}
• Description: {job.description}
• Status: {job.status}
• Scheduled: {job.scheduled_date}
• Duration: {job.estimated_duration} minutes
• Priority: {job.priority}
• Contact: {job.contact_id}
• Notes: {job.notes or 'None'}
• Created: {job.created_at}
            """
            
            return details.strip()
            
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return f"❌ I encountered an error while getting job details: {str(e)}"
    
    @function_tool
    async def search_jobs(self, query: str, limit: int = 10) -> str:
        """Search for jobs by title, description, or status"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the search jobs use case
            search_jobs_use_case = self.container.get_search_jobs_use_case()
            
            from ...application.dto.job_dto import SearchJobsDTO
            
            # Execute use case
            result = await search_jobs_use_case.execute(
                SearchJobsDTO(
                    query=query,
                    limit=limit,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if not result.jobs:
                return f"No jobs found matching '{query}'"
            
            jobs_text = "\n".join([
                f"• {job.title} - {job.status} - {job.scheduled_date}"
                for job in result.jobs
            ])
            
            return f"🔧 Found {len(result.jobs)} job(s) matching '{query}':\n{jobs_text}"
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return f"❌ I encountered an error while searching for jobs: {str(e)}"
    
    @function_tool
    async def get_upcoming_jobs(self, days_ahead: int = 7, limit: int = 10) -> str:
        """Get upcoming jobs within the specified number of days"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the upcoming jobs use case
            get_upcoming_jobs_use_case = self.container.get_get_upcoming_jobs_use_case()
            
            from ...application.dto.job_dto import GetUpcomingJobsDTO
            
            # Execute use case
            result = await get_upcoming_jobs_use_case.execute(
                GetUpcomingJobsDTO(
                    days_ahead=days_ahead,
                    limit=limit,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            if not result.jobs:
                return f"No upcoming jobs in the next {days_ahead} days"
            
            jobs_text = "\n".join([
                f"• {job.title} - {job.scheduled_date} - {job.status}"
                for job in result.jobs
            ])
            
            return f"📅 Upcoming jobs in the next {days_ahead} days:\n{jobs_text}"
            
        except Exception as e:
            logger.error(f"Error getting upcoming jobs: {e}")
            return f"❌ I encountered an error while getting upcoming jobs: {str(e)}"
    
    @function_tool
    async def mark_job_complete(self, job_id: str, completion_notes: Optional[str] = None) -> str:
        """Mark a job as complete"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the mark job complete use case
            mark_job_complete_use_case = self.container.get_mark_job_complete_use_case()
            
            from ...application.dto.job_dto import MarkJobCompleteDTO
            
            # Execute use case
            result = await mark_job_complete_use_case.execute(
                MarkJobCompleteDTO(
                    job_id=job_id,
                    completion_notes=completion_notes,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return f"✅ Job marked as complete successfully!"
            
        except Exception as e:
            logger.error(f"Error marking job complete: {e}")
            return f"❌ I encountered an error while marking the job complete: {str(e)}"
    
    @function_tool
    async def get_job_statistics(self) -> str:
        """Get job statistics and overview"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get job statistics through search with different filters
            search_jobs_use_case = self.container.get_search_jobs_use_case()
            
            from ...application.dto.job_dto import SearchJobsDTO
            
            # Get pending jobs
            pending_result = await search_jobs_use_case.execute(
                SearchJobsDTO(
                    query="pending",
                    limit=100,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            # Get completed jobs
            completed_result = await search_jobs_use_case.execute(
                SearchJobsDTO(
                    query="completed",
                    limit=100,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            # Get in progress jobs
            in_progress_result = await search_jobs_use_case.execute(
                SearchJobsDTO(
                    query="in_progress",
                    limit=100,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            stats = f"""
📊 Job Statistics:
• Pending: {len(pending_result.jobs)}
• In Progress: {len(in_progress_result.jobs)}
• Completed: {len(completed_result.jobs)}
• Total: {len(pending_result.jobs) + len(in_progress_result.jobs) + len(completed_result.jobs)}
            """
            
            return stats.strip()
            
        except Exception as e:
            logger.error(f"Error getting job statistics: {e}")
            return f"❌ I encountered an error while getting job statistics: {str(e)}"
    
    def get_specialist_capabilities(self) -> List[str]:
        """Get list of capabilities for this specialist agent"""
        return [
            "Create new jobs with title, description, and scheduling",
            "Update job status and progress",
            "Search for jobs by title, description, or status",
            "Get detailed job information",
            "View upcoming jobs and schedules",
            "Mark jobs as complete",
            "Get job statistics and overview",
            "Natural conversation for job management",
            "Automatic parameter collection through conversation"
        ]
    
    async def initialize_agent(self, ctx):
        """Initialize job agent"""
        logger.info("🔧 Job Agent initialized")
    
    async def cleanup_agent(self, ctx):
        """Clean up job agent"""
        logger.info("👋 Job Agent cleaned up")
    
    async def process_message(self, ctx, message: str) -> str:
        """Process user message"""
        # Process job-related messages
        return f"Job agent processing: {message}" 