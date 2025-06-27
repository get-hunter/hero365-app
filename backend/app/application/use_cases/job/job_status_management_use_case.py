"""
Job Status Management Use Case

Business logic for job status transitions and lifecycle management in Hero365.
Handles status updates, job start/complete/cancel operations.
"""

import uuid
from typing import Optional

from ...dto.job_dto import JobStatusUpdateDTO, JobResponseDTO
from ...exceptions.application_exceptions import NotFoundError
from app.domain.repositories.job_repository import JobRepository
from .job_helper_service import JobHelperService


class JobStatusManagementUseCase:
    """
    Use case for managing job status transitions within Hero365.
    
    Handles status updates, job lifecycle operations like start,
    complete, and cancel with proper business rule validation.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        job_helper_service: JobHelperService
    ):
        self.job_repository = job_repository
        self.job_helper_service = job_helper_service
    
    async def update_job_status(self, job_id: uuid.UUID, status_data: JobStatusUpdateDTO,
                               user_id: str) -> JobResponseDTO:
        """Update job status."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self.job_helper_service.check_permission(job.business_id, user_id, "edit_jobs")
        
        # Update status using domain logic
        job.update_status(status_data.status, user_id, status_data.notes)
        
        # Save updated job
        updated_job = await self.job_repository.update(job)
        
        return await self.job_helper_service.convert_to_response_dto(updated_job)
    
    async def start_job(self, job_id: uuid.UUID, user_id: str) -> JobResponseDTO:
        """Start a job (convenience method)."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self.job_helper_service.check_permission(job.business_id, user_id, "edit_jobs")
        
        job.start_job(user_id)
        
        updated_job = await self.job_repository.update(job)
        return await self.job_helper_service.convert_to_response_dto(updated_job)
    
    async def complete_job(self, job_id: uuid.UUID, user_id: str,
                          completion_notes: Optional[str] = None) -> JobResponseDTO:
        """Complete a job (convenience method)."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self.job_helper_service.check_permission(job.business_id, user_id, "edit_jobs")
        
        job.complete_job(user_id, completion_notes)
        
        updated_job = await self.job_repository.update(job)
        return await self.job_helper_service.convert_to_response_dto(updated_job)
    
    async def cancel_job(self, job_id: uuid.UUID, user_id: str, reason: str) -> JobResponseDTO:
        """Cancel a job (convenience method)."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self.job_helper_service.check_permission(job.business_id, user_id, "edit_jobs")
        
        job.cancel_job(user_id, reason)
        
        updated_job = await self.job_repository.update(job)
        return await self.job_helper_service.convert_to_response_dto(updated_job) 