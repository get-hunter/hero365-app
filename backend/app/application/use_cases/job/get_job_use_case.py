"""
Get Job Use Case

Business logic for job retrieval operations in Hero365.
Handles job fetching by ID with permission validation.
"""

import uuid

from ...dto.job_dto import JobResponseDTO
from ...exceptions.application_exceptions import NotFoundError
from app.domain.repositories.job_repository import JobRepository
from .job_helper_service import JobHelperService


class GetJobUseCase:
    """
    Use case for retrieving jobs within Hero365.
    
    Handles job retrieval by ID with proper permission checks
    and data transformation to response DTOs.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        job_helper_service: JobHelperService
    ):
        self.job_repository = job_repository
        self.job_helper_service = job_helper_service
    
    async def execute(self, job_id: uuid.UUID, user_id: str) -> JobResponseDTO:
        """Get a job by ID."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self.job_helper_service.check_permission(job.business_id, user_id, "view_jobs")
        
        return await self.job_helper_service.convert_to_response_dto(job) 