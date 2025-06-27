"""
Job Assignment Use Case

Business logic for job assignment and team management operations in Hero365.
Handles job assignments to team members and workload management.
"""

import uuid

from ...dto.job_dto import JobAssignmentDTO, JobResponseDTO
from ...exceptions.application_exceptions import NotFoundError
from app.domain.repositories.job_repository import JobRepository
from .job_helper_service import JobHelperService


class JobAssignmentUseCase:
    """
    Use case for managing job assignments within Hero365.
    
    Handles job assignments to team members and validates
    user permissions and business membership.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        job_helper_service: JobHelperService
    ):
        self.job_repository = job_repository
        self.job_helper_service = job_helper_service
    
    async def assign_job(self, job_id: uuid.UUID, assignment_data: JobAssignmentDTO,
                        user_id: str) -> JobResponseDTO:
        """Assign job to users."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self.job_helper_service.check_permission(job.business_id, user_id, "edit_jobs")
        
        # Validate assigned users
        await self.job_helper_service.validate_assigned_users(job.business_id, assignment_data.user_ids)
        
        if assignment_data.replace_existing:
            job.assigned_to = assignment_data.user_ids
        else:
            for user_id_to_assign in assignment_data.user_ids:
                job.assign_team_member(user_id_to_assign)
        
        # Save updated job
        updated_job = await self.job_repository.update(job)
        
        return await self.job_helper_service.convert_to_response_dto(updated_job) 