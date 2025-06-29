"""
Supabase Job Repository Implementation

Implements job data access operations using Supabase.
Handles all job-related database operations with proper error handling.
"""

import uuid
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from supabase import Client

logger = logging.getLogger(__name__)
from app.domain.entities.job import (
    Job, 
    JobTimeTracking, JobCostEstimate
)
from app.domain.value_objects.address import Address
from app.domain.enums import JobType, JobStatus, JobPriority, JobSource
from app.domain.repositories.job_repository import JobRepository
from app.domain.exceptions.domain_exceptions import DomainValidationError


class SupabaseJobRepository(JobRepository):
    """
    Supabase implementation of the Job repository.
    
    Handles all job data access operations using Supabase client.
    """
    
    def __init__(self, client: Client):
        self.client = client
    
    async def create(self, job: Job) -> Job:
        """Create a new job."""
        try:
            job_data = self._job_to_dict(job)
            
            result = self.client.table("jobs").insert(job_data).execute()
            
            if not result.data:
                raise DomainValidationError("Failed to create job")
            
            return self._dict_to_job(result.data[0])
        
        except Exception as e:
            raise DomainValidationError(f"Failed to create job: {str(e)}")
    
    async def get_by_id(self, job_id: uuid.UUID) -> Optional[Job]:
        """Get job by ID."""
        try:
            result = self.client.table("jobs").select("*").eq("id", str(job_id)).execute()
            
            if not result.data:
                return None
            
            return self._dict_to_job(result.data[0])
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get job: {str(e)}")
    
    async def get_by_job_number(self, business_id: uuid.UUID, job_number: str) -> Optional[Job]:
        """Get job by job number within a business."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("job_number", job_number)
                     .execute())
            
            if not result.data:
                return None
            
            return self._dict_to_job(result.data[0])
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get job by number: {str(e)}")
    
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by business ID with pagination."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get jobs by business: {str(e)}")
    
    async def get_by_contact_id(self, contact_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by contact ID with pagination."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("contact_id", str(contact_id))
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get jobs by contact: {str(e)}")
    
    async def get_by_status(self, business_id: uuid.UUID, status: JobStatus,
                           skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by status within a business."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("status", status.value)
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get jobs by status: {str(e)}")
    
    async def get_by_type(self, business_id: uuid.UUID, job_type: JobType,
                         skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by type within a business."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("job_type", job_type.value)
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get jobs by type: {str(e)}")
    
    async def get_by_priority(self, business_id: uuid.UUID, priority: JobPriority,
                             skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by priority within a business."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("priority", priority.value)
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get jobs by priority: {str(e)}")
    
    async def get_by_assigned_user(self, business_id: uuid.UUID, user_id: str,
                                  skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs assigned to a specific user within a business."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .contains("assigned_to", [user_id])
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get jobs by assigned user: {str(e)}")
    
    async def get_by_project_id(self, project_id: uuid.UUID, business_id: uuid.UUID,
                               skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs associated with a specific project."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("project_id", str(project_id))
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get jobs by project: {str(e)}")
    
    async def get_scheduled_jobs(self, business_id: uuid.UUID, start_date: datetime,
                                end_date: datetime, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs scheduled within a date range."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .gte("scheduled_start", start_date.isoformat())
                     .lte("scheduled_end", end_date.isoformat())
                     .order("scheduled_start", desc=False)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get scheduled jobs: {str(e)}")
    
    async def get_overdue_jobs(self, business_id: uuid.UUID,
                              skip: int = 0, limit: int = 100) -> List[Job]:
        """Get overdue jobs within a business."""
        try:
            now = datetime.now(timezone.utc).isoformat()
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .in_("status", ["scheduled", "in_progress"])
                     .lt("scheduled_end", now)
                     .order("scheduled_end", desc=False)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get overdue jobs: {str(e)}")
    
    async def get_emergency_jobs(self, business_id: uuid.UUID,
                                skip: int = 0, limit: int = 100) -> List[Job]:
        """Get emergency priority jobs within a business."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("priority", "emergency")
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get emergency jobs: {str(e)}")
    
    async def get_jobs_by_tag(self, business_id: uuid.UUID, tag: str,
                             skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs with a specific tag within a business."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .contains("tags", [tag])
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get jobs by tag: {str(e)}")
    
    async def search_jobs(self, business_id: uuid.UUID, search_term: str,
                         skip: int = 0, limit: int = 100) -> List[Job]:
        """Search jobs within a business by title, description, or job number."""
        try:
            # Use text search on title, description, and job_number
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .or_(f"title.ilike.%{search_term}%,description.ilike.%{search_term}%,job_number.ilike.%{search_term}%")
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to search jobs: {str(e)}")
    
    async def get_jobs_in_progress(self, business_id: uuid.UUID,
                                  skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs currently in progress within a business."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("status", "in_progress")
                     .order("actual_start", desc=False)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get jobs in progress: {str(e)}")
    
    async def get_completed_jobs(self, business_id: uuid.UUID, start_date: datetime,
                                end_date: datetime, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs completed within a date range."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("status", "completed")
                     .gte("completed_date", start_date.isoformat())
                     .lte("completed_date", end_date.isoformat())
                     .order("completed_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get completed jobs: {str(e)}")
    
    async def get_revenue_by_period(self, business_id: uuid.UUID, start_date: datetime,
                                   end_date: datetime) -> Dict[str, Any]:
        """Get revenue statistics for a period."""
        try:
            # This would typically be done with a database function or aggregation
            # For now, we'll get the jobs and calculate in Python
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .in_("status", ["completed", "invoiced", "paid"])
                     .gte("completed_date", start_date.isoformat())
                     .lte("completed_date", end_date.isoformat())
                     .execute())
            
            jobs = [self._dict_to_job(job_data) for job_data in result.data]
            
            total_revenue = sum(job.get_estimated_revenue() for job in jobs)
            total_jobs = len(jobs)
            average_job_value = total_revenue / total_jobs if total_jobs > 0 else Decimal("0")
            
            return {
                "period_start": start_date,
                "period_end": end_date,
                "total_revenue": total_revenue,
                "total_jobs": total_jobs,
                "average_job_value": average_job_value
            }
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get revenue by period: {str(e)}")
    
    async def update(self, job: Job) -> Job:
        """Update an existing job."""
        try:
            job_data = self._job_to_dict(job)
            job_data.pop("id", None)  # Remove ID from update data
            
            result = (self.client.table("jobs")
                     .update(job_data)
                     .eq("id", str(job.id))
                     .execute())
            
            if not result.data:
                raise DomainValidationError("Failed to update job")
            
            return self._dict_to_job(result.data[0])
        
        except Exception as e:
            raise DomainValidationError(f"Failed to update job: {str(e)}")
    
    async def delete(self, job_id: uuid.UUID) -> bool:
        """Delete a job by ID."""
        try:
            result = (self.client.table("jobs")
                     .delete()
                     .eq("id", str(job_id))
                     .execute())
            
            return len(result.data) > 0
        
        except Exception as e:
            raise DomainValidationError(f"Failed to delete job: {str(e)}")
    
    async def bulk_update_status(self, business_id: uuid.UUID, job_ids: List[uuid.UUID],
                                status: JobStatus) -> int:
        """Bulk update job status."""
        try:
            job_ids_str = [str(job_id) for job_id in job_ids]
            
            result = (self.client.table("jobs")
                     .update({"status": status.value, "last_modified": datetime.utcnow().isoformat()})
                     .eq("business_id", str(business_id))
                     .in_("id", job_ids_str)
                     .execute())
            
            return len(result.data)
        
        except Exception as e:
            raise DomainValidationError(f"Failed to bulk update status: {str(e)}")
    
    async def bulk_assign_jobs(self, business_id: uuid.UUID, job_ids: List[uuid.UUID],
                              user_id: str) -> int:
        """Bulk assign jobs to a user."""
        try:
            # This is a simplified version - in reality, we'd need to handle merging with existing assignments
            job_ids_str = [str(job_id) for job_id in job_ids]
            
            result = (self.client.table("jobs")
                     .update({"assigned_to": [user_id], "last_modified": datetime.utcnow().isoformat()})
                     .eq("business_id", str(business_id))
                     .in_("id", job_ids_str)
                     .execute())
            
            return len(result.data)
        
        except Exception as e:
            raise DomainValidationError(f"Failed to bulk assign jobs: {str(e)}")
    
    async def bulk_add_tag(self, business_id: uuid.UUID, job_ids: List[uuid.UUID],
                          tag: str) -> int:
        """Bulk add tag to jobs."""
        try:
            # This would require a more complex query to append to existing tags
            # For now, simplified implementation
            job_ids_str = [str(job_id) for job_id in job_ids]
            
            # We'd need to fetch existing jobs, modify tags, then update
            # This is a simplified placeholder
            updated_count = 0
            for job_id in job_ids_str:
                job_result = self.client.table("jobs").select("tags").eq("id", job_id).execute()
                if job_result.data:
                    existing_tags = job_result.data[0].get("tags", [])
                    if tag not in existing_tags:
                        existing_tags.append(tag)
                        self.client.table("jobs").update({
                            "tags": existing_tags,
                            "last_modified": datetime.utcnow().isoformat()
                        }).eq("id", job_id).execute()
                        updated_count += 1
            
            return updated_count
        
        except Exception as e:
            raise DomainValidationError(f"Failed to bulk add tag: {str(e)}")
    
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Count total jobs for a business."""
        try:
            result = (self.client.table("jobs")
                     .select("id", count="exact")
                     .eq("business_id", str(business_id))
                     .execute())
            
            return result.count or 0
        
        except Exception as e:
            raise DomainValidationError(f"Failed to count jobs: {str(e)}")
    
    async def count_by_status(self, business_id: uuid.UUID, status: JobStatus) -> int:
        """Count jobs by status within a business."""
        try:
            result = (self.client.table("jobs")
                     .select("id", count="exact")
                     .eq("business_id", str(business_id))
                     .eq("status", status.value)
                     .execute())
            
            return result.count or 0
        
        except Exception as e:
            raise DomainValidationError(f"Failed to count jobs by status: {str(e)}")
    
    async def count_by_type(self, business_id: uuid.UUID, job_type: JobType) -> int:
        """Count jobs by type within a business."""
        try:
            result = (self.client.table("jobs")
                     .select("id", count="exact")
                     .eq("business_id", str(business_id))
                     .eq("job_type", job_type.value)
                     .execute())
            
            return result.count or 0
        
        except Exception as e:
            raise DomainValidationError(f"Failed to count jobs by type: {str(e)}")
    
    async def count_by_priority(self, business_id: uuid.UUID, priority: JobPriority) -> int:
        """Count jobs by priority within a business."""
        try:
            result = (self.client.table("jobs")
                     .select("id", count="exact")
                     .eq("business_id", str(business_id))
                     .eq("priority", priority.value)
                     .execute())
            
            return result.count or 0
        
        except Exception as e:
            raise DomainValidationError(f"Failed to count jobs by priority: {str(e)}")
    
    async def get_job_statistics(self, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive job statistics for a business."""
        try:
            # This would typically use a database function for better performance
            # For now, we'll use the RPC call to the function we created in migration
            result = self.client.rpc("get_job_statistics", {"p_business_id": str(business_id)}).execute()
            
            if result.data:
                return result.data
            
            return {}
        
        except Exception as e:
            # Fallback to basic statistics if RPC fails
            total_jobs = await self.count_by_business(business_id)
            return {
                "total_jobs": total_jobs,
                "jobs_by_status": {},
                "jobs_by_type": {},
                "jobs_by_priority": {},
                "overdue_jobs": 0,
                "emergency_jobs": 0,
                "jobs_in_progress": 0,
                "completed_this_month": 0,
                "revenue_this_month": 0,
                "average_job_value": 0,
                "completion_rate": 0,
                "on_time_completion_rate": 0
            }
    
    async def exists(self, job_id: uuid.UUID) -> bool:
        """Check if a job exists."""
        try:
            result = (self.client.table("jobs")
                     .select("id")
                     .eq("id", str(job_id))
                     .execute())
            
            return len(result.data) > 0
        
        except Exception as e:
            return False
    
    async def has_duplicate_job_number(self, business_id: uuid.UUID, job_number: str,
                                      exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if job number already exists within business."""
        try:
            query = (self.client.table("jobs")
                    .select("id")
                    .eq("business_id", str(business_id))
                    .eq("job_number", job_number))
            
            if exclude_id:
                query = query.neq("id", str(exclude_id))
            
            result = query.execute()
            
            return len(result.data) > 0
        
        except Exception as e:
            return False
    
    async def get_next_job_number(self, business_id: uuid.UUID, prefix: str = "JOB") -> str:
        """Generate next available job number for a business."""
        try:
            # Use the database function we created
            result = self.client.rpc("get_next_job_number", {
                "p_business_id": str(business_id),
                "p_prefix": prefix
            }).execute()
            
            if result.data:
                return result.data
            
            # Fallback method
            return f"{prefix}-000001"
        
        except Exception as e:
            # Fallback method
            import random
            return f"{prefix}-{random.randint(100000, 999999)}"
    
    # Additional methods for completeness
    
    async def get_jobs_requiring_follow_up(self, business_id: uuid.UUID,
                                          skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs that require follow-up (completed but not invoiced)."""
        try:
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("status", "completed")
                     .order("completed_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get jobs requiring follow-up: {str(e)}")
    
    async def get_user_workload(self, business_id: uuid.UUID, user_id: str) -> Dict[str, Any]:
        """Get workload statistics for a specific user."""
        try:
            # Get all jobs assigned to user
            result = (self.client.table("jobs")
                     .select("*")
                     .eq("business_id", str(business_id))
                     .contains("assigned_to", [user_id])
                     .execute())
            
            jobs = [self._dict_to_job(job_data) for job_data in result.data]
            
            total_assigned = len(jobs)
            jobs_in_progress = len([j for j in jobs if j.status == JobStatus.IN_PROGRESS])
            overdue_jobs = len([j for j in jobs if j.is_overdue()])
            
            # Calculate this week's scheduled jobs
            now = datetime.utcnow()
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            
            scheduled_this_week = len([
                j for j in jobs 
                if j.scheduled_start and week_start <= j.scheduled_start <= week_end
            ])
            
            total_estimated_hours = sum(
                j.time_tracking.estimated_hours or Decimal("0") for j in jobs
            )
            
            total_actual_hours = sum(
                j.time_tracking.actual_hours or Decimal("0") for j in jobs
            )
            
            return {
                "total_assigned_jobs": total_assigned,
                "jobs_in_progress": jobs_in_progress,
                "overdue_jobs": overdue_jobs,
                "scheduled_this_week": scheduled_this_week,
                "total_estimated_hours": total_estimated_hours,
                "total_actual_hours": total_actual_hours,
                "utilization_rate": 0.0,  # Would need more complex calculation
                "completion_rate": 0.0   # Would need more complex calculation
            }
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get user workload: {str(e)}")
    
    async def get_daily_schedule(self, business_id: uuid.UUID, date: datetime,
                                user_id: Optional[str] = None) -> List[Job]:
        """Get jobs scheduled for a specific day."""
        try:
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            query = (self.client.table("jobs")
                    .select("*")
                    .eq("business_id", str(business_id))
                    .gte("scheduled_start", start_of_day.isoformat())
                    .lte("scheduled_start", end_of_day.isoformat())
                    .order("scheduled_start", desc=False))
            
            if user_id:
                query = query.contains("assigned_to", [user_id])
            
            result = query.execute()
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get daily schedule: {str(e)}")
    
    async def get_weekly_schedule(self, business_id: uuid.UUID, start_date: datetime,
                                 user_id: Optional[str] = None) -> List[Job]:
        """Get jobs scheduled for a specific week."""
        try:
            end_date = start_date + timedelta(days=6)
            
            query = (self.client.table("jobs")
                    .select("*")
                    .eq("business_id", str(business_id))
                    .gte("scheduled_start", start_date.isoformat())
                    .lte("scheduled_start", end_date.isoformat())
                    .order("scheduled_start", desc=False))
            
            if user_id:
                query = query.contains("assigned_to", [user_id])
            
            result = query.execute()
            
            return [self._dict_to_job(job_data) for job_data in result.data]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get weekly schedule: {str(e)}")
    
    async def get_monthly_revenue(self, business_id: uuid.UUID, year: int, month: int) -> Dict[str, Any]:
        """Get revenue statistics for a specific month."""
        try:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
            
            return await self.get_revenue_by_period(business_id, start_date, end_date)
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get monthly revenue: {str(e)}")
    
    async def get_top_customers_by_revenue(self, business_id: uuid.UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top customers by total job revenue."""
        try:
            # This would typically be done with a complex query
            # For now, we'll get all completed jobs and aggregate in Python
            result = (self.client.table("jobs")
                     .select("contact_id, cost_estimate")
                     .eq("business_id", str(business_id))
                     .in_("status", ["completed", "invoiced", "paid"])
                     .is_("contact_id", "not.null")
                     .execute())
            
            # Aggregate revenue by contact
            contact_revenue = {}
            for job_data in result.data:
                contact_id = job_data.get("contact_id")
                if contact_id:
                    cost_estimate = job_data.get("cost_estimate", {})
                    revenue = (
                        Decimal(str(cost_estimate.get("labor_cost", 0))) +
                        Decimal(str(cost_estimate.get("material_cost", 0))) +
                        Decimal(str(cost_estimate.get("equipment_cost", 0))) +
                        Decimal(str(cost_estimate.get("overhead_cost", 0)))
                    )
                    
                    if contact_id in contact_revenue:
                        contact_revenue[contact_id] += revenue
                    else:
                        contact_revenue[contact_id] = revenue
            
            # Sort and limit
            sorted_customers = sorted(
                contact_revenue.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
            
            return [
                {"contact_id": contact_id, "total_revenue": float(revenue)}
                for contact_id, revenue in sorted_customers
            ]
        
        except Exception as e:
            raise DomainValidationError(f"Failed to get top customers: {str(e)}")
    
    # Helper methods for data conversion
    
    def _job_to_dict(self, job: Job) -> Dict[str, Any]:
        """Convert Job entity to dictionary for database storage."""
        return {
            "id": str(job.id),
            "business_id": str(job.business_id),
            "contact_id": str(job.contact_id) if job.contact_id else None,
            "project_id": str(job.project_id) if job.project_id else None,
            "job_number": job.job_number,
            "title": job.title,
            "description": job.description,
            "job_type": job.job_type.value,
            "status": job.status.value,
            "priority": job.priority.value,
            "source": job.source.value,
            "job_address": job.job_address.to_dict(),
            "scheduled_start": job.scheduled_start.isoformat() if job.scheduled_start else None,
            "scheduled_end": job.scheduled_end.isoformat() if job.scheduled_end else None,
            "actual_start": job.actual_start.isoformat() if job.actual_start else None,
            "actual_end": job.actual_end.isoformat() if job.actual_end else None,
            "assigned_to": job.assigned_to,
            "created_by": job.created_by,
            "time_tracking": {
                "estimated_hours": float(job.time_tracking.estimated_hours) if job.time_tracking.estimated_hours else None,
                "actual_hours": float(job.time_tracking.actual_hours) if job.time_tracking.actual_hours else None,
                "billable_hours": float(job.time_tracking.billable_hours) if job.time_tracking.billable_hours else None,
                "start_time": job.time_tracking.start_time.isoformat() if job.time_tracking.start_time else None,
                "end_time": job.time_tracking.end_time.isoformat() if job.time_tracking.end_time else None,
                "break_time_minutes": job.time_tracking.break_time_minutes
            },
            "cost_estimate": {
                "labor_cost": float(job.cost_estimate.labor_cost),
                "material_cost": float(job.cost_estimate.material_cost),
                "equipment_cost": float(job.cost_estimate.equipment_cost),
                "overhead_cost": float(job.cost_estimate.overhead_cost),
                "markup_percentage": float(job.cost_estimate.markup_percentage),
                "tax_percentage": float(job.cost_estimate.tax_percentage),
                "discount_amount": float(job.cost_estimate.discount_amount)
            },
            "tags": job.tags,
            "notes": job.notes,
            "internal_notes": job.internal_notes,
            "customer_requirements": job.customer_requirements,
            "completion_notes": job.completion_notes,
            "custom_fields": job.custom_fields,
            "created_date": job.created_date.isoformat(),
            "last_modified": job.last_modified.isoformat(),
            "completed_date": job.completed_date.isoformat() if job.completed_date else None
        }
    
    def _dict_to_job(self, data: Dict[str, Any]) -> Job:
        """Convert dictionary from database to Job entity."""
        # Parse address using unified Address value object
        job_address = None
        if data.get("job_address"):
            try:
                from app.application.utils.address_utils import AddressUtils
                job_address = AddressUtils.parse_address_from_jsonb(data.get("job_address"))
            except Exception as e:
                logger.warning(f"Failed to parse job address for job {data.get('id')}: {str(e)}")
                # Create minimal address as fallback
                job_address = Address.create_minimal(
                    street_address="Address unavailable",
                    city="Unknown",
                    state="Unknown", 
                    postal_code="00000"
                )
        else:
            # Default address for jobs without address data
            job_address = Address.create_minimal(
                street_address="No address provided",
                city="Unknown",
                state="Unknown",
                postal_code="00000"
            )
        
        # Parse time tracking
        time_data = data.get("time_tracking", {})
        time_tracking = JobTimeTracking(
            estimated_hours=Decimal(str(time_data.get("estimated_hours"))) if time_data.get("estimated_hours") else None,
            actual_hours=Decimal(str(time_data.get("actual_hours"))) if time_data.get("actual_hours") else None,
            billable_hours=Decimal(str(time_data.get("billable_hours"))) if time_data.get("billable_hours") else None,
            start_time=self._parse_datetime(time_data.get("start_time")) if time_data.get("start_time") else None,
            end_time=self._parse_datetime(time_data.get("end_time")) if time_data.get("end_time") else None,
            break_time_minutes=time_data.get("break_time_minutes", 0)
        )
        
        # Parse cost estimate
        cost_data = data.get("cost_estimate", {})
        cost_estimate = JobCostEstimate(
            labor_cost=Decimal(str(cost_data.get("labor_cost", 0))),
            material_cost=Decimal(str(cost_data.get("material_cost", 0))),
            equipment_cost=Decimal(str(cost_data.get("equipment_cost", 0))),
            overhead_cost=Decimal(str(cost_data.get("overhead_cost", 0))),
            markup_percentage=Decimal(str(cost_data.get("markup_percentage", 20))),
            tax_percentage=Decimal(str(cost_data.get("tax_percentage", 0))),
            discount_amount=Decimal(str(cost_data.get("discount_amount", 0)))
        )
        
        # Parse enums with fallback for invalid values
        try:
            job_type = JobType(data["job_type"])
        except ValueError:
            job_type = JobType.OTHER
        
        try:
            status = JobStatus(data["status"])
        except ValueError:
            status = JobStatus.DRAFT
        
        try:
            priority = JobPriority(data["priority"])
        except ValueError:
            priority = JobPriority.MEDIUM
        
        try:
            source = JobSource(data["source"])
        except ValueError:
            source = JobSource.OTHER

        # Create job entity
        job = Job(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            contact_id=uuid.UUID(data["contact_id"]) if data.get("contact_id") else None,
            project_id=uuid.UUID(data["project_id"]) if data.get("project_id") else None,
            job_number=data["job_number"],
            title=data["title"],
            description=data.get("description"),
            job_type=job_type,
            status=status,
            priority=priority,
            source=source,
            job_address=job_address,
            scheduled_start=self._parse_datetime(data.get("scheduled_start")) if data.get("scheduled_start") else None,
            scheduled_end=self._parse_datetime(data.get("scheduled_end")) if data.get("scheduled_end") else None,
            actual_start=self._parse_datetime(data.get("actual_start")) if data.get("actual_start") else None,
            actual_end=self._parse_datetime(data.get("actual_end")) if data.get("actual_end") else None,
            assigned_to=data.get("assigned_to", []),
            created_by=data["created_by"],
            time_tracking=time_tracking,
            cost_estimate=cost_estimate,
            tags=data.get("tags", []),
            notes=data.get("notes"),
            internal_notes=data.get("internal_notes"),
            customer_requirements=data.get("customer_requirements"),
            completion_notes=data.get("completion_notes"),
            custom_fields=data.get("custom_fields", {}),
            created_date=self._parse_datetime(data["created_date"]),
            last_modified=self._parse_datetime(data["last_modified"]),
            completed_date=self._parse_datetime(data.get("completed_date")) if data.get("completed_date") else None
        )
        
        return job 
    
    def _parse_datetime(self, datetime_str: str) -> datetime:
        """Parse datetime string and ensure it's timezone-aware (UTC)."""
        if not datetime_str:
            return None
            
        dt = datetime.fromisoformat(datetime_str)
        
        # If datetime is naive, assume it's UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt