"""
Job Repository Interface

Defines the contract for job data access operations.
Follows the Repository pattern for clean architecture.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..entities.job import Job, JobStatus, JobType, JobPriority


class JobRepository(ABC):
    """
    Abstract repository interface for job data access operations.
    
    Defines all methods needed for job management without
    specifying implementation details.
    """
    
    @abstractmethod
    async def create(self, job: Job) -> Job:
        """Create a new job."""
        pass
    
    @abstractmethod
    async def get_by_id(self, job_id: uuid.UUID) -> Optional[Job]:
        """Get job by ID."""
        pass
    
    @abstractmethod
    async def get_by_job_number(self, business_id: uuid.UUID, job_number: str) -> Optional[Job]:
        """Get job by job number within a business."""
        pass
    
    @abstractmethod
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by business ID with pagination."""
        pass
    
    @abstractmethod
    async def get_by_contact_id(self, contact_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by contact ID with pagination."""
        pass
    
    @abstractmethod
    async def get_by_status(self, business_id: uuid.UUID, status: JobStatus,
                           skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by status within a business."""
        pass
    
    @abstractmethod
    async def get_by_type(self, business_id: uuid.UUID, job_type: JobType,
                         skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by type within a business."""
        pass
    
    @abstractmethod
    async def get_by_priority(self, business_id: uuid.UUID, priority: JobPriority,
                             skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs by priority within a business."""
        pass
    
    @abstractmethod
    async def get_by_assigned_user(self, business_id: uuid.UUID, user_id: str,
                                  skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs assigned to a specific user within a business."""
        pass
    
    @abstractmethod
    async def get_scheduled_jobs(self, business_id: uuid.UUID, start_date: datetime,
                                end_date: datetime, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs scheduled within a date range."""
        pass
    
    @abstractmethod
    async def get_overdue_jobs(self, business_id: uuid.UUID,
                              skip: int = 0, limit: int = 100) -> List[Job]:
        """Get overdue jobs within a business."""
        pass
    
    @abstractmethod
    async def get_emergency_jobs(self, business_id: uuid.UUID,
                                skip: int = 0, limit: int = 100) -> List[Job]:
        """Get emergency priority jobs within a business."""
        pass
    
    @abstractmethod
    async def get_jobs_by_tag(self, business_id: uuid.UUID, tag: str,
                             skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs with a specific tag within a business."""
        pass
    
    @abstractmethod
    async def search_jobs(self, business_id: uuid.UUID, search_term: str,
                         skip: int = 0, limit: int = 100) -> List[Job]:
        """Search jobs within a business by title, description, or job number."""
        pass
    
    @abstractmethod
    async def get_jobs_in_progress(self, business_id: uuid.UUID,
                                  skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs currently in progress within a business."""
        pass
    
    @abstractmethod
    async def get_completed_jobs(self, business_id: uuid.UUID, start_date: datetime,
                                end_date: datetime, skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs completed within a date range."""
        pass
    
    @abstractmethod
    async def get_revenue_by_period(self, business_id: uuid.UUID, start_date: datetime,
                                   end_date: datetime) -> Dict[str, Any]:
        """Get revenue statistics for a period."""
        pass
    
    @abstractmethod
    async def update(self, job: Job) -> Job:
        """Update an existing job."""
        pass
    
    @abstractmethod
    async def delete(self, job_id: uuid.UUID) -> bool:
        """Delete a job by ID."""
        pass
    
    @abstractmethod
    async def bulk_update_status(self, business_id: uuid.UUID, job_ids: List[uuid.UUID],
                                status: JobStatus) -> int:
        """Bulk update job status."""
        pass
    
    @abstractmethod
    async def bulk_assign_jobs(self, business_id: uuid.UUID, job_ids: List[uuid.UUID],
                              user_id: str) -> int:
        """Bulk assign jobs to a user."""
        pass
    
    @abstractmethod
    async def bulk_add_tag(self, business_id: uuid.UUID, job_ids: List[uuid.UUID],
                          tag: str) -> int:
        """Bulk add tag to jobs."""
        pass
    
    @abstractmethod
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Count total jobs for a business."""
        pass
    
    @abstractmethod
    async def count_by_status(self, business_id: uuid.UUID, status: JobStatus) -> int:
        """Count jobs by status within a business."""
        pass
    
    @abstractmethod
    async def count_by_type(self, business_id: uuid.UUID, job_type: JobType) -> int:
        """Count jobs by type within a business."""
        pass
    
    @abstractmethod
    async def count_by_priority(self, business_id: uuid.UUID, priority: JobPriority) -> int:
        """Count jobs by priority within a business."""
        pass
    
    @abstractmethod
    async def get_job_statistics(self, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive job statistics for a business."""
        pass
    
    @abstractmethod
    async def exists(self, job_id: uuid.UUID) -> bool:
        """Check if a job exists."""
        pass
    
    @abstractmethod
    async def has_duplicate_job_number(self, business_id: uuid.UUID, job_number: str,
                                      exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if job number already exists within business."""
        pass
    
    @abstractmethod
    async def get_next_job_number(self, business_id: uuid.UUID, prefix: str = "JOB") -> str:
        """Generate next available job number for a business."""
        pass
    
    @abstractmethod
    async def get_jobs_requiring_follow_up(self, business_id: uuid.UUID,
                                          skip: int = 0, limit: int = 100) -> List[Job]:
        """Get jobs that require follow-up (completed but not invoiced)."""
        pass
    
    @abstractmethod
    async def get_user_workload(self, business_id: uuid.UUID, user_id: str) -> Dict[str, Any]:
        """Get workload statistics for a specific user."""
        pass
    
    @abstractmethod
    async def get_daily_schedule(self, business_id: uuid.UUID, date: datetime,
                                user_id: Optional[str] = None) -> List[Job]:
        """Get jobs scheduled for a specific day."""
        pass
    
    @abstractmethod
    async def get_weekly_schedule(self, business_id: uuid.UUID, start_date: datetime,
                                 user_id: Optional[str] = None) -> List[Job]:
        """Get jobs scheduled for a specific week."""
        pass
    
    @abstractmethod
    async def get_monthly_revenue(self, business_id: uuid.UUID, year: int, month: int) -> Dict[str, Any]:
        """Get revenue statistics for a specific month."""
        pass
    
    @abstractmethod
    async def get_top_customers_by_revenue(self, business_id: uuid.UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top customers by total job revenue."""
        pass 