"""
Job Management Tools

Voice agent tools for job management using Hero365's job use cases.
"""

from typing import List, Any, Dict, Optional
from datetime import datetime, timedelta
import uuid
from app.infrastructure.config.dependency_injection import get_container
from app.application.use_cases.job import (
    CreateJobUseCase,
    UpdateJobUseCase,
    GetJobUseCase,
    DeleteJobUseCase,
    JobSearchUseCase
)
from app.application.dto.job_dto import JobCreateDTO, JobUpdateDTO, JobSearchDTO
from app.domain.enums import JobType, JobStatus, JobPriority, JobSource


class JobTools:
    """Job management tools for voice agents"""
    
    def __init__(self, business_id: str, user_id: str):
        """
        Initialize job tools with business and user context
        
        Args:
            business_id: Current business ID
            user_id: Current user ID
        """
        self.business_id = business_id
        self.user_id = user_id
        self.container = get_container()
    
    def get_tools(self) -> List[Any]:
        """Get all job management tools"""
        return [
            self.create_job,
            self.get_upcoming_jobs,
            self.update_job_status,
            self.get_job_details,
            self.reschedule_job,
            self.get_jobs_by_status,
            self.get_today_jobs
        ]
    
    def create_job(self, 
                   title: str,
                   description: str,
                   client_contact_id: str,
                   scheduled_date: str,
                   job_type: str = "service",
                   priority: str = "medium",
                   location: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new job for the business
        
        Args:
            title: Job title
            description: Job description
            client_contact_id: ID of the client contact
            scheduled_date: Scheduled date (YYYY-MM-DD HH:MM format)
            job_type: Type of job (service, maintenance, installation, repair)
            priority: Job priority (low, medium, high)
            location: Job location address
        """
        try:
            create_job_use_case = self.container.get(CreateJobUseCase)
            
            # Convert string enums to enum values
            job_type_enum = JobType.SERVICE if job_type == "service" else JobType.MAINTENANCE
            priority_enum = JobPriority.MEDIUM
            if priority == "low":
                priority_enum = JobPriority.LOW
            elif priority == "high":
                priority_enum = JobPriority.HIGH
            
            job_dto = JobCreateDTO(
                business_id=uuid.UUID(self.business_id),
                contact_id=uuid.UUID(client_contact_id) if client_contact_id else None,
                title=title,
                description=description,
                job_type=job_type_enum,
                priority=priority_enum,
                source=JobSource.VOICE_AGENT,
                scheduled_start=datetime.fromisoformat(scheduled_date) if scheduled_date else None,
                notes=f"Created via voice agent. Location: {location}" if location else "Created via voice agent"
            )
            
            result = create_job_use_case.execute(job_dto)
            
            return {
                "success": True,
                "job_id": str(result.id),
                "message": f"Job '{title}' created successfully and scheduled for {scheduled_date}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating job: {str(e)}"
            }
    
    def get_upcoming_jobs(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Get upcoming jobs for the next specified days
        
        Args:
            days_ahead: Number of days to look ahead (default: 7)
        """
        try:
            job_search_use_case = self.container.get(JobSearchUseCase)
            
            # Calculate date range
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days_ahead)
            
            search_dto = JobSearchDTO(
                scheduled_start_from=start_date,
                scheduled_start_to=end_date
            )
            
            jobs = job_search_use_case.search_jobs(
                business_id=uuid.UUID(self.business_id),
                search_params=search_dto,
                user_id=self.user_id
            )
            
            job_list = []
            for job in jobs:
                job_list.append({
                    "id": str(job.id),
                    "title": job.title,
                    "client": job.contact.display_name if job.contact else "No client",
                    "scheduled_date": job.scheduled_start.isoformat() if job.scheduled_start else None,
                    "status": job.status.value,
                    "location": "Location not available"
                })
            
            return {
                "success": True,
                "jobs": job_list,
                "count": len(job_list),
                "message": f"Found {len(job_list)} upcoming jobs in the next {days_ahead} days"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting upcoming jobs: {str(e)}"
            }
    
    def update_job_status(self, job_id: str, new_status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Update job status with optional notes
        
        Args:
            job_id: Job ID to update
            new_status: New status (scheduled, in_progress, completed, cancelled)
            notes: Optional notes about the status change
        """
        try:
            update_job_use_case = self.container.get(UpdateJobUseCase)
            
            # Convert string status to enum
            status_enum = JobStatus.SCHEDULED
            if new_status == "in_progress":
                status_enum = JobStatus.IN_PROGRESS
            elif new_status == "completed":
                status_enum = JobStatus.COMPLETED
            elif new_status == "cancelled":
                status_enum = JobStatus.CANCELLED
            
            update_dto = JobUpdateDTO(
                notes=notes
            )
            
            result = update_job_use_case.execute(job_id, update_dto, self.business_id, self.user_id)
            
            return {
                "success": True,
                "message": f"Job status updated to {new_status}",
                "job_id": job_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating job status: {str(e)}"
            }
    
    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific job
        
        Args:
            job_id: Job ID to get details for
        """
        try:
            get_job_use_case = self.container.get(GetJobUseCase)
            
            job = get_job_use_case.execute(job_id, self.business_id, self.user_id)
            
            return {
                "success": True,
                "job": {
                    "id": str(job.id),
                    "title": job.title,
                    "description": job.description,
                    "client": job.contact.display_name if job.contact else "No client",
                    "scheduled_date": job.scheduled_start.isoformat() if job.scheduled_start else None,
                    "status": job.status.value,
                    "location": "Location not available",
                    "priority": job.priority.value,
                    "created_at": job.created_date.isoformat() if job.created_date else None
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting job details: {str(e)}"
            }
    
    def reschedule_job(self, job_id: str, new_date: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Reschedule a job to a new date
        
        Args:
            job_id: Job ID to reschedule
            new_date: New scheduled date (YYYY-MM-DD HH:MM format)
            reason: Optional reason for rescheduling
        """
        try:
            update_job_use_case = self.container.get(UpdateJobUseCase)
            
            update_dto = JobUpdateDTO(
                scheduled_start=datetime.fromisoformat(new_date) if new_date else None,
                notes=f"Rescheduled: {reason}" if reason else "Rescheduled"
            )
            
            result = update_job_use_case.execute(job_id, update_dto, self.business_id, self.user_id)
            
            return {
                "success": True,
                "message": f"Job rescheduled to {new_date}",
                "job_id": job_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error rescheduling job: {str(e)}"
            }
    
    def get_jobs_by_status(self, status: str) -> Dict[str, Any]:
        """
        Get jobs filtered by status
        
        Args:
            status: Job status to filter by (scheduled, in_progress, completed, cancelled)
        """
        try:
            job_search_use_case = self.container.get(JobSearchUseCase)
            
            # Convert string status to enum
            status_enum = JobStatus.SCHEDULED
            if status == "in_progress":
                status_enum = JobStatus.IN_PROGRESS
            elif status == "completed":
                status_enum = JobStatus.COMPLETED
            elif status == "cancelled":
                status_enum = JobStatus.CANCELLED
            
            search_dto = JobSearchDTO(
                status=status_enum
            )
            
            jobs = job_search_use_case.search_jobs(
                business_id=uuid.UUID(self.business_id),
                search_params=search_dto,
                user_id=self.user_id
            )
            
            job_list = []
            for job in jobs:
                job_list.append({
                    "id": str(job.id),
                    "title": job.title,
                    "client": job.contact.display_name if job.contact else "No client",
                    "scheduled_date": job.scheduled_start.isoformat() if job.scheduled_start else None,
                    "location": "Location not available"
                })
            
            return {
                "success": True,
                "jobs": job_list,
                "count": len(job_list),
                "message": f"Found {len(job_list)} jobs with status '{status}'"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting jobs by status: {str(e)}"
            }
    
    def get_today_jobs(self) -> Dict[str, Any]:
        """Get all jobs scheduled for today"""
        try:
            job_search_use_case = self.container.get(JobSearchUseCase)
            
            today = datetime.now().date()
            search_dto = JobSearchDTO(
                scheduled_start_from=datetime.combine(today, datetime.min.time()),
                scheduled_start_to=datetime.combine(today, datetime.max.time())
            )
            
            jobs = job_search_use_case.search_jobs(
                business_id=uuid.UUID(self.business_id),
                search_params=search_dto,
                user_id=self.user_id
            )
            
            job_list = []
            for job in jobs:
                job_list.append({
                    "id": str(job.id),
                    "title": job.title,
                    "client": job.contact.display_name if job.contact else "No client",
                    "scheduled_time": job.scheduled_start.isoformat() if job.scheduled_start else None,
                    "location": "Location not available",
                    "status": job.status.value
                })
            
            return {
                "success": True,
                "jobs": job_list,
                "count": len(job_list),
                "message": f"Found {len(job_list)} jobs scheduled for today"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting today's jobs: {str(e)}"
            } 