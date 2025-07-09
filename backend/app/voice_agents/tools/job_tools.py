"""
Job Management Tools for Voice Agents

This module provides voice agent tools for job management,
integrating with existing Hero365 use cases.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from contextvars import ContextVar

from livekit.agents import function_tool

from app.infrastructure.config.dependency_injection import DependencyContainer
from app.application.use_cases.job import (
    CreateJobUseCase, GetJobUseCase, UpdateJobUseCase, DeleteJobUseCase,
    JobSearchUseCase, JobSchedulingUseCase, JobStatusManagementUseCase
)
from app.application.dto.job_dto import JobCreateDTO, JobUpdateDTO, JobSearchDTO
from app.domain.enums import JobStatus, JobPriority, JobType, JobSource

logger = logging.getLogger(__name__)

# Context variable to store the current agent context
_current_context: ContextVar[Dict[str, Any]] = ContextVar('current_context', default={})


def set_current_context(context: Dict[str, Any]) -> None:
    """Set the current agent context."""
    _current_context.set(context)


def get_current_context() -> Dict[str, Any]:
    """Get the current agent context."""
    context = _current_context.get()
    if not context.get("business_id") or not context.get("user_id"):
        logger.warning("Agent context not available for job tools")
        return {"business_id": None, "user_id": None}
    return context


@function_tool
async def create_job(
    title: str,
    description: str,
    client_contact_id: str,
    scheduled_date: str,
    estimated_duration: int = 60,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Create a new job for the business.
    
    Args:
        title: Job title or description
        description: Detailed job description
        client_contact_id: ID of the client contact
        scheduled_date: Date for the job (YYYY-MM-DD format)
        estimated_duration: Estimated duration in minutes (default: 60)
        priority: Job priority (low, medium, high, urgent)
    
    Returns:
        Dictionary with job creation result
    """
    try:
        container = DependencyContainer()
        create_job_use_case = container.get_create_job_use_case()
        
        context = get_current_context()
        business_id = context.get("business_id")
        user_id = context.get("user_id")
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to create job. Please try again."
            }
        
        # Convert priority string to enum
        try:
            job_priority = JobPriority(priority.upper())
        except ValueError:
            job_priority = JobPriority.MEDIUM
        
        job_dto = JobCreateDTO(
            business_id=uuid.UUID(business_id),
            contact_id=uuid.UUID(client_contact_id) if client_contact_id else None,
            title=title,
            description=description,
            job_type=JobType.SERVICE,  # Default job type
            priority=job_priority,
            source=JobSource.VOICE_AGENT,
            scheduled_start=datetime.fromisoformat(scheduled_date) if scheduled_date else None
        )
        
        result = await create_job_use_case.execute(job_dto, business_id, user_id)
        
        logger.info(f"Created job via voice agent: {result.id}")
        
        return {
            "success": True,
            "job_id": str(result.id),
            "title": result.title,
            "scheduled_date": result.scheduled_date,
            "message": f"Job '{title}' created successfully and scheduled for {scheduled_date}"
        }
        
    except Exception as e:
        logger.error(f"Error creating job via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create job. Please try again or contact support."
        }


@function_tool
async def get_upcoming_jobs(days_ahead: int = 7, limit: int = 10) -> Dict[str, Any]:
    """
    Get upcoming jobs for the next specified days.
    
    Args:
        days_ahead: Number of days ahead to look (default: 7)
        limit: Maximum number of jobs to return (default: 10)
    
    Returns:
        Dictionary with upcoming jobs list
    """
    try:
        container = DependencyContainer()
        job_repository = container.get_job_repository()
        
        context = get_current_context()
        business_id = context.get("business_id")
        user_id = context.get("user_id")
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve jobs. Please try again."
            }
        
        # Calculate date range
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Get jobs scheduled in the date range with specific statuses
        jobs = await job_repository.get_scheduled_jobs(
            business_id=uuid.UUID(business_id),
            start_date=start_date,
            end_date=end_date,
            skip=0,
            limit=limit
        )
        
        # Filter jobs to only include scheduled and in_progress statuses
        filtered_jobs = [
            job for job in jobs 
            if job.status in [JobStatus.SCHEDULED, JobStatus.IN_PROGRESS]
        ]
        
        upcoming_jobs = []
        for job in filtered_jobs:
            upcoming_jobs.append({
                "id": str(job.id),
                "title": job.title,
                "client": job.client_name if hasattr(job, 'client_name') else 'Unknown',
                "scheduled_date": job.scheduled_start.date() if job.scheduled_start else None,
                "scheduled_time": job.scheduled_start.time() if job.scheduled_start else None,
                "status": job.status.value,
                "priority": job.priority.value,
                "estimated_duration": job.time_tracking.estimated_hours if job.time_tracking else None
            })
        
        logger.info(f"Retrieved {len(upcoming_jobs)} upcoming jobs via voice agent")
        
        return {
            "success": True,
            "jobs": upcoming_jobs,
            "total_count": len(upcoming_jobs),
            "date_range": f"{start_date.date()} to {end_date.date()}",
            "message": f"Found {len(upcoming_jobs)} upcoming jobs in the next {days_ahead} days"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving upcoming jobs via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve upcoming jobs. Please try again."
        }


@function_tool
async def update_job_status(job_id: str, new_status: str, notes: Optional[str] = None) -> Dict[str, Any]:
    """
    Update job status with optional notes.
    
    Args:
        job_id: ID of the job to update
        new_status: New status (scheduled, in_progress, completed, cancelled)
        notes: Optional notes about the status change
    
    Returns:
        Dictionary with update result
    """
    try:
        container = DependencyContainer()
        job_status_use_case = container.get_job_status_management_use_case()
        
        context = get_current_context()
        business_id = context.get("business_id")
        user_id = context.get("user_id")
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to update job status. Please try again."
            }
        
        # Convert status string to enum
        try:
            status_enum = JobStatus(new_status.upper())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid status: {new_status}",
                "message": "Valid statuses are: scheduled, in_progress, completed, cancelled"
            }
        
        # Create update DTO
        update_dto = JobUpdateDTO(
            notes=notes
        )
        
        result = await job_status_use_case.update_job_status(
            job_id, status_enum, business_id, user_id, notes
        )
        
        logger.info(f"Updated job {job_id} status to {new_status} via voice agent")
        
        return {
            "success": True,
            "job_id": job_id,
            "new_status": new_status,
            "notes": notes,
            "message": f"Job status updated to {new_status}"
        }
        
    except Exception as e:
        logger.error(f"Error updating job status via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to update job status. Please try again."
        }


@function_tool
async def reschedule_job(
    job_id: str, 
    new_date: str, 
    new_time: Optional[str] = None,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reschedule a job to a new date and time.
    
    Args:
        job_id: ID of the job to reschedule
        new_date: New date (YYYY-MM-DD format)
        new_time: New time (HH:MM format, optional)
        reason: Reason for rescheduling (optional)
    
    Returns:
        Dictionary with reschedule result
    """
    try:
        container = DependencyContainer()
        job_scheduling_use_case = container.get_job_scheduling_use_case()
        
        context = get_current_context()
        business_id = context.get("business_id")
        user_id = context.get("user_id")
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to reschedule job. Please try again."
            }
        
        result = await job_scheduling_use_case.reschedule_job(
            job_id=job_id,
            new_scheduled_date=new_date,
            new_scheduled_time=new_time,
            reason=reason,
            business_id=business_id,
            user_id=user_id
        )
        
        logger.info(f"Rescheduled job {job_id} to {new_date} via voice agent")
        
        return {
            "success": True,
            "job_id": job_id,
            "new_date": new_date,
            "new_time": new_time,
            "reason": reason,
            "message": f"Job rescheduled to {new_date}" + (f" at {new_time}" if new_time else "")
        }
        
    except Exception as e:
        logger.error(f"Error rescheduling job via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to reschedule job. Please try again."
        }


@function_tool
async def get_job_details(job_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific job.
    
    Args:
        job_id: ID of the job to retrieve
    
    Returns:
        Dictionary with job details
    """
    try:
        container = DependencyContainer()
        get_job_use_case = container.get_get_job_use_case()
        
        context = get_current_context()
        business_id = context.get("business_id")
        user_id = context.get("user_id")
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve job details. Please try again."
            }
        
        job = await get_job_use_case.execute(job_id, business_id, user_id)
        
        logger.info(f"Retrieved job details for {job_id} via voice agent")
        
        return {
            "success": True,
            "job": {
                "id": str(job.id),
                "title": job.title,
                "description": job.description,
                "status": job.status.value,
                "priority": job.priority.value if hasattr(job, 'priority') else 'medium',
                "scheduled_date": job.scheduled_date,
                "scheduled_time": job.scheduled_time if hasattr(job, 'scheduled_time') else None,
                "estimated_duration": job.estimated_duration,
                "client_contact_id": job.client_contact_id,
                "created_at": job.created_at.isoformat() if hasattr(job, 'created_at') else None
            },
            "message": f"Retrieved details for job: {job.title}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving job details via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve job details. Please check the job ID."
        }


@function_tool
async def get_jobs_by_status(status: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get jobs filtered by status.
    
    Args:
        status: Job status to filter by (scheduled, in_progress, completed, cancelled)
        limit: Maximum number of jobs to return (default: 10)
    
    Returns:
        Dictionary with filtered jobs
    """
    try:
        container = DependencyContainer()
        job_repository = container.get_job_repository()
        
        context = get_current_context()
        business_id = context.get("business_id")
        user_id = context.get("user_id")
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve jobs by status. Please try again."
            }
        
        # Convert status string to enum
        try:
            status_enum = JobStatus(status.upper())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid status: {status}",
                "message": "Valid statuses are: scheduled, in_progress, completed, cancelled"
            }
        
        # Get jobs by status directly from repository
        jobs = await job_repository.get_by_status(
            business_id=uuid.UUID(business_id),
            status=status_enum,
            skip=0,
            limit=limit
        )
        
        job_list = []
        for job in jobs:
            job_list.append({
                "id": str(job.id),
                "title": job.title,
                "scheduled_date": job.scheduled_start.date() if job.scheduled_start else None,
                "client": job.client_name if hasattr(job, 'client_name') else 'Unknown',
                "priority": job.priority.value
            })
        
        logger.info(f"Retrieved {len(job_list)} jobs with status {status} via voice agent")
        
        return {
            "success": True,
            "jobs": job_list,
            "status_filter": status,
            "total_count": len(job_list),
            "message": f"Found {len(job_list)} jobs with status: {status}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving jobs by status via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve jobs by status. Please try again."
        } 