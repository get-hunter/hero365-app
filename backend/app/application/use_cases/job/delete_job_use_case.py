"""
Delete Job Use Case

Business logic for job deletion operations in Hero365.
Handles job deletion with validation and business rules.
"""

import uuid

from ...exceptions.application_exceptions import (
    NotFoundError, BusinessRuleViolationError
)
from app.domain.entities.job import JobStatus
from app.domain.repositories.job_repository import JobRepository
from .job_helper_service import JobHelperService


class DeleteJobUseCase:
    """
    Use case for deleting jobs within Hero365.
    
    Handles job deletion with proper permission checks
    and business rule validation.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        job_helper_service: JobHelperService
    ):
        self.job_repository = job_repository
        self.job_helper_service = job_helper_service
    
    async def execute(self, job_id: uuid.UUID, user_id: str) -> bool:
        """Delete a job."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self.job_helper_service.check_permission(job.business_id, user_id, "delete_jobs")
        
        # Business rule: Cannot delete completed or invoiced jobs
        if job.status in [JobStatus.COMPLETED, JobStatus.INVOICED, JobStatus.PAID]:
            raise BusinessRuleViolationError("Cannot delete completed or invoiced jobs")
        
        return await self.job_repository.delete(job_id) 