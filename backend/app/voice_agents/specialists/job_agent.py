"""
Job management specialist agent for Hero365 voice system.
"""

from typing import Dict, Any, List, Optional
# from openai_agents import tool, handoff
from ..core.base_agent import BaseVoiceAgent
from ..core.context_manager import ContextManager
import logging

logger = logging.getLogger(__name__)


class JobAgent(BaseVoiceAgent):
    """Specialist agent for job management"""
    
    def __init__(self, context_manager: ContextManager):
        """
        Initialize job management specialist.
        
        Args:
            context_manager: Shared context manager
        """
        instructions = """
        You are the job management specialist for Hero365. You help users manage their jobs, 
        including creating new jobs, updating job status, scheduling jobs, and tracking job progress.
        
        You understand the job lifecycle and can help with scheduling, status updates, 
        completion tracking, and job-related documentation.
        
        Be helpful and guide users through job management tasks efficiently.
        """
        
        super().__init__(
            name="Job Specialist",
            instructions=instructions,
            context_manager=context_manager,
            tools=[
                self.create_job,
                self.update_job_status,
                self.get_job_details,
                self.get_upcoming_jobs,
                self.get_jobs_by_status,
                self.reschedule_job,
                self.add_job_note,
                self.mark_job_complete,
                self.assign_job,
                self.get_job_analytics,
                self.search_jobs
            ]
        )
    
    def get_handoffs(self) -> List:
        """Return list of agents this agent can hand off to"""
        return []  # These would be populated when initializing the system
    
    # @tool
    async def create_job(self, 
                        title: str,
                        description: str,
                        contact_id: str,
                        scheduled_date: str,
                        estimated_duration: int = 120,
                        priority: str = "medium",
                        notes: str = None) -> str:
        """Create a new job"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the create job use case
            create_job_use_case = self.container.get_create_job_use_case()
            
            # Import the DTO
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
            
            return await self.format_success_response(
                "create_job",
                result,
                f"Excellent! I've created the job '{title}' scheduled for {scheduled_date}. The job ID is {result.id}. What else would you like to do with this job?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "create_job",
                e,
                f"I couldn't create the job '{title}'. Please check the details and try again."
            )
    
    # @tool
    async def update_job_status(self, job_id: str, new_status: str, notes: str = None) -> str:
        """Update job status"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the job status management use case
            job_status_use_case = self.container.get_job_status_management_use_case()
            
            # Import the DTO
            from ...application.dto.job_dto import JobStatusUpdateDTO
            
            # Execute use case
            result = await job_status_use_case.execute(
                JobStatusUpdateDTO(
                    job_id=job_id,
                    new_status=new_status,
                    notes=notes,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "update_job_status",
                result,
                f"Perfect! I've updated the job status to '{new_status}'. The job has been updated successfully."
            )
            
        except Exception as e:
            return await self.format_error_response(
                "update_job_status",
                e,
                f"I couldn't update the job status. Please check the job ID and try again."
            )
    
    # @tool
    async def get_job_details(self, job_id: str) -> str:
        """Get detailed information about a job"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the get job use case
            get_job_use_case = self.container.get_get_job_use_case()
            
            # Import the DTO
            from ...application.dto.job_dto import GetJobDTO
            
            # Execute use case
            result = await get_job_use_case.execute(
                GetJobDTO(
                    job_id=job_id,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            job = result.job
            details = f"""
            Here are the details for "{job.title}":
            
            • Status: {job.status}
            • Scheduled: {job.scheduled_date.strftime('%B %d, %Y at %I:%M %p')}
            • Duration: {job.estimated_duration} minutes
            • Priority: {job.priority}
            • Contact: {job.contact_name if hasattr(job, 'contact_name') else 'N/A'}
            • Created: {job.created_at.strftime('%B %d, %Y')}
            """
            
            if job.description:
                details += f"\n• Description: {job.description}"
            
            if job.notes:
                details += f"\n• Notes: {job.notes}"
            
            details += "\n\nWhat would you like to do with this job?"
            
            return await self.format_success_response(
                "get_job_details",
                result,
                details
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_job_details",
                e,
                f"I couldn't find the job with ID {job_id}. Please check the ID and try again."
            )
    
    # @tool
    async def get_upcoming_jobs(self, days_ahead: int = 7, limit: int = 10) -> str:
        """Get upcoming jobs for the next few days"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the job search use case
            job_search_use_case = self.container.get_job_search_use_case()
            
            # Import the DTO
            from ...application.dto.job_dto import JobSearchDTO
            
            # Execute use case
            result = await job_search_use_case.execute(
                JobSearchDTO(
                    business_id=business_id,
                    status_filter="scheduled",
                    date_filter="upcoming",
                    days_ahead=days_ahead,
                    limit=limit
                ),
                user_id=user_id
            )
            
            if not result.jobs:
                return f"You don't have any jobs scheduled for the next {days_ahead} days. Would you like me to help you create a new job?"
            
            job_list = []
            for job in result.jobs:
                job_info = f"• {job.title} on {job.scheduled_date.strftime('%B %d')} at {job.scheduled_date.strftime('%I:%M %p')}"
                if hasattr(job, 'contact_name'):
                    job_info += f" - {job.contact_name}"
                job_list.append(job_info)
            
            jobs_text = "\n".join(job_list)
            
            return await self.format_success_response(
                "get_upcoming_jobs",
                result,
                f"Here are your upcoming jobs for the next {days_ahead} days:\n\n{jobs_text}\n\nWould you like me to get more details about any of these jobs?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_upcoming_jobs",
                e,
                f"I'm having trouble getting your upcoming jobs. Let me help you with something else."
            )
    
    # @tool
    async def get_jobs_by_status(self, status: str, limit: int = 10) -> str:
        """Get jobs by their status"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the job search use case
            job_search_use_case = self.container.get_job_search_use_case()
            
            # Import the DTO
            from ...application.dto.job_dto import JobSearchDTO
            
            # Execute use case
            result = await job_search_use_case.execute(
                JobSearchDTO(
                    business_id=business_id,
                    status_filter=status,
                    limit=limit
                ),
                user_id=user_id
            )
            
            if not result.jobs:
                return f"You don't have any jobs with status '{status}'. Would you like me to help you with other jobs?"
            
            job_list = []
            for job in result.jobs:
                job_info = f"• {job.title}"
                if job.scheduled_date:
                    job_info += f" - {job.scheduled_date.strftime('%B %d, %Y')}"
                if hasattr(job, 'contact_name'):
                    job_info += f" - {job.contact_name}"
                job_list.append(job_info)
            
            jobs_text = "\n".join(job_list)
            
            return await self.format_success_response(
                "get_jobs_by_status",
                result,
                f"Here are your jobs with status '{status}':\n\n{jobs_text}\n\nWould you like me to update any of these jobs or get more details?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_jobs_by_status",
                e,
                f"I'm having trouble getting jobs with status '{status}'. Let me help you with something else."
            )
    
    # @tool
    async def reschedule_job(self, job_id: str, new_date: str, reason: str = None) -> str:
        """Reschedule a job to a new date"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the job scheduling use case
            job_scheduling_use_case = self.container.get_job_scheduling_use_case()
            
            # Import the DTO
            from ...application.dto.job_dto import JobRescheduleDTO
            
            # Execute use case
            result = await job_scheduling_use_case.execute(
                JobRescheduleDTO(
                    job_id=job_id,
                    new_scheduled_date=new_date,
                    reason=reason,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "reschedule_job",
                result,
                f"Great! I've rescheduled the job to {new_date}. The job has been updated successfully."
            )
            
        except Exception as e:
            return await self.format_error_response(
                "reschedule_job",
                e,
                f"I couldn't reschedule the job. Please check the job ID and date format and try again."
            )
    
    # @tool
    async def add_job_note(self, job_id: str, note: str) -> str:
        """Add a note to a job"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the update job use case
            update_job_use_case = self.container.get_update_job_use_case()
            
            # Import the DTO
            from ...application.dto.job_dto import UpdateJobDTO
            
            # Get current job first to append the note
            get_job_use_case = self.container.get_get_job_use_case()
            from ...application.dto.job_dto import GetJobDTO
            
            current_job = await get_job_use_case.execute(
                GetJobDTO(job_id=job_id, business_id=business_id),
                user_id=user_id
            )
            
            # Append new note to existing notes
            existing_notes = current_job.job.notes or ""
            new_notes = f"{existing_notes}\n\n{note}" if existing_notes else note
            
            # Execute use case
            result = await update_job_use_case.execute(
                UpdateJobDTO(
                    job_id=job_id,
                    notes=new_notes,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "add_job_note",
                result,
                f"I've added the note to the job. The note has been saved successfully."
            )
            
        except Exception as e:
            return await self.format_error_response(
                "add_job_note",
                e,
                f"I couldn't add the note to the job. Please try again."
            )
    
    # @tool
    async def mark_job_complete(self, job_id: str, completion_notes: str = None) -> str:
        """Mark a job as complete"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the job status management use case
            job_status_use_case = self.container.get_job_status_management_use_case()
            
            # Import the DTO
            from ...application.dto.job_dto import JobStatusUpdateDTO
            
            # Execute use case
            result = await job_status_use_case.execute(
                JobStatusUpdateDTO(
                    job_id=job_id,
                    new_status="completed",
                    notes=completion_notes,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "mark_job_complete",
                result,
                f"Excellent! I've marked the job as complete. Would you like me to help you create an invoice for this job or move on to the next task?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "mark_job_complete",
                e,
                f"I couldn't mark the job as complete. Please check the job ID and try again."
            )
    
    # @tool
    async def assign_job(self, job_id: str, user_id_to_assign: str) -> str:
        """Assign a job to a user"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the job assignment use case
            job_assignment_use_case = self.container.get_job_assignment_use_case()
            
            # Import the DTO
            from ...application.dto.job_dto import JobAssignmentDTO
            
            # Execute use case
            result = await job_assignment_use_case.execute(
                JobAssignmentDTO(
                    job_id=job_id,
                    assigned_user_id=user_id_to_assign,
                    business_id=business_id
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "assign_job",
                result,
                f"Perfect! I've assigned the job to the specified user. The assignment has been saved successfully."
            )
            
        except Exception as e:
            return await self.format_error_response(
                "assign_job",
                e,
                f"I couldn't assign the job. Please check the job ID and user ID and try again."
            )
    
    # @tool
    async def get_job_analytics(self, period: str = "month") -> str:
        """Get job analytics and statistics"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the job analytics use case
            job_analytics_use_case = self.container.get_job_analytics_use_case()
            
            # Import the DTO
            from ...application.dto.job_dto import JobAnalyticsDTO
            
            # Execute use case
            result = await job_analytics_use_case.execute(
                JobAnalyticsDTO(
                    business_id=business_id,
                    period=period
                ),
                user_id=user_id
            )
            
            return await self.format_success_response(
                "get_job_analytics",
                result,
                f"""
                Here's your job analytics for the {period}:
                
                • Total jobs: {result.total_jobs}
                • Completed: {result.completed_jobs}
                • In progress: {result.in_progress_jobs}
                • Scheduled: {result.scheduled_jobs}
                • Overdue: {result.overdue_jobs}
                • Average completion time: {result.average_completion_time} hours
                
                Would you like me to help you with any specific jobs or dive deeper into these metrics?
                """
            )
            
        except Exception as e:
            return await self.format_error_response(
                "get_job_analytics",
                e,
                f"I'm having trouble getting your job analytics. Let me help you with something specific instead."
            )
    
    # @tool
    async def search_jobs(self, query: str, limit: int = 10) -> str:
        """Search for jobs"""
        try:
            user_id, business_id = await self.get_user_and_business_ids()
            
            # Get the job search use case
            job_search_use_case = self.container.get_job_search_use_case()
            
            # Import the DTO
            from ...application.dto.job_dto import JobSearchDTO
            
            # Execute use case
            result = await job_search_use_case.execute(
                JobSearchDTO(
                    business_id=business_id,
                    search_query=query,
                    limit=limit
                ),
                user_id=user_id
            )
            
            if not result.jobs:
                return f"I didn't find any jobs matching '{query}'. Would you like me to search for something else or create a new job?"
            
            job_list = []
            for job in result.jobs:
                job_info = f"• {job.title} - {job.status}"
                if job.scheduled_date:
                    job_info += f" - {job.scheduled_date.strftime('%B %d, %Y')}"
                if hasattr(job, 'contact_name'):
                    job_info += f" - {job.contact_name}"
                job_list.append(job_info)
            
            jobs_text = "\n".join(job_list)
            
            return await self.format_success_response(
                "search_jobs",
                result,
                f"I found {len(result.jobs)} jobs matching '{query}':\n\n{jobs_text}\n\nWould you like me to get more details about any of these jobs?"
            )
            
        except Exception as e:
            return await self.format_error_response(
                "search_jobs",
                e,
                f"I'm having trouble searching for '{query}'. Let me try a different approach or you can be more specific."
            )
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of capabilities for this agent"""
        return [
            "Create new jobs",
            "Update job status",
            "Get job details",
            "View upcoming jobs",
            "Filter jobs by status",
            "Reschedule jobs",
            "Add job notes",
            "Mark jobs complete",
            "Assign jobs to users",
            "Job analytics and reporting",
            "Search jobs"
        ] 