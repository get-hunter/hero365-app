"""
Job Bulk Operations Use Case

Business logic for bulk job operations in Hero365.
Handles bulk updates, assignments, and other mass operations on jobs.
"""

import uuid

from ...dto.job_dto import JobBulkUpdateDTO
from app.domain.repositories.job_repository import JobRepository
from .job_helper_service import JobHelperService


class JobBulkOperationsUseCase:
    """
    Use case for bulk job operations within Hero365.
    
    Handles bulk updates, mass assignments, and other
    operations that affect multiple jobs simultaneously.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        job_helper_service: JobHelperService
    ):
        self.job_repository = job_repository
        self.job_helper_service = job_helper_service
    
    async def bulk_update_jobs(self, business_id: uuid.UUID, bulk_data: JobBulkUpdateDTO,
                              user_id: str) -> int:
        """Bulk update jobs."""
        
        # Check permission
        await self.job_helper_service.check_permission(business_id, user_id, "edit_jobs")
        
        updated_count = 0
        
        if bulk_data.status:
            updated_count += await self.job_repository.bulk_update_status(
                business_id, bulk_data.job_ids, bulk_data.status
            )
        
        if bulk_data.assigned_to:
            # Validate user exists in business
            await self.job_helper_service.validate_assigned_users(business_id, [bulk_data.assigned_to])
            updated_count += await self.job_repository.bulk_assign_jobs(
                business_id, bulk_data.job_ids, bulk_data.assigned_to
            )
        
        if bulk_data.tags_to_add:
            for tag in bulk_data.tags_to_add:
                await self.job_repository.bulk_add_tag(business_id, bulk_data.job_ids, tag)
        
        return updated_count 