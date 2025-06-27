"""
Job Search Use Case

Business logic for job search and filtering operations in Hero365.
Handles job listing, searching, and filtering with various criteria.
"""

import uuid
from typing import List

from ...dto.job_dto import JobListDTO, JobSearchDTO
from app.domain.repositories.job_repository import JobRepository
from .job_helper_service import JobHelperService


class JobSearchUseCase:
    """
    Use case for searching and listing jobs within Hero365.
    
    Handles job listing, search with filters, and various
    query operations with proper permission validation.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        job_helper_service: JobHelperService
    ):
        self.job_repository = job_repository
        self.job_helper_service = job_helper_service
    
    async def list_jobs(self, business_id: uuid.UUID, user_id: str,
                       skip: int = 0, limit: int = 100) -> List[JobListDTO]:
        """List jobs for a business."""
        
        # Check permission
        await self.job_helper_service.check_permission(business_id, user_id, "view_jobs")
        
        jobs = await self.job_repository.get_by_business_id(business_id, skip, limit)
        
        return [await self.job_helper_service.convert_to_list_dto(job) for job in jobs]
    
    async def search_jobs(self, business_id: uuid.UUID, search_params: JobSearchDTO,
                         user_id: str) -> List[JobListDTO]:
        """Search jobs with filters."""
        
        # Check permission
        await self.job_helper_service.check_permission(business_id, user_id, "view_jobs")
        
        # Apply filters based on search parameters
        jobs = []
        
        if search_params.search_term:
            jobs = await self.job_repository.search_jobs(
                business_id, search_params.search_term, search_params.skip, search_params.limit
            )
        elif search_params.status:
            jobs = await self.job_repository.get_by_status(
                business_id, search_params.status, search_params.skip, search_params.limit
            )
        elif search_params.job_type:
            jobs = await self.job_repository.get_by_type(
                business_id, search_params.job_type, search_params.skip, search_params.limit
            )
        elif search_params.priority:
            jobs = await self.job_repository.get_by_priority(
                business_id, search_params.priority, search_params.skip, search_params.limit
            )
        elif search_params.assigned_to:
            jobs = await self.job_repository.get_by_assigned_user(
                business_id, search_params.assigned_to, search_params.skip, search_params.limit
            )
        elif search_params.contact_id:
            jobs = await self.job_repository.get_by_contact_id(
                search_params.contact_id, search_params.skip, search_params.limit
            )
        elif search_params.is_overdue:
            jobs = await self.job_repository.get_overdue_jobs(
                business_id, search_params.skip, search_params.limit
            )
        elif search_params.is_emergency:
            jobs = await self.job_repository.get_emergency_jobs(
                business_id, search_params.skip, search_params.limit
            )
        else:
            jobs = await self.job_repository.get_by_business_id(
                business_id, search_params.skip, search_params.limit
            )
        
        return [await self.job_helper_service.convert_to_list_dto(job) for job in jobs] 