"""
Job Scheduling Use Case

Business logic for job scheduling and calendar management in Hero365.
Handles daily schedules, schedule conflicts, and time management.
"""

import uuid
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from ...dto.job_dto import JobScheduleDTO
from app.domain.repositories.job_repository import JobRepository
from .job_helper_service import JobHelperService


class JobSchedulingUseCase:
    """
    Use case for job scheduling and calendar management within Hero365.
    
    Handles daily schedules, schedule conflicts, time management,
    and calendar operations with proper validation.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        job_helper_service: JobHelperService
    ):
        self.job_repository = job_repository
        self.job_helper_service = job_helper_service
    
    async def get_daily_schedule(self, business_id: uuid.UUID, date: datetime,
                                user_id: str, target_user_id: Optional[str] = None) -> JobScheduleDTO:
        """Get daily job schedule."""
        
        # Check permission
        await self.job_helper_service.check_permission(business_id, user_id, "view_jobs")
        
        jobs = await self.job_repository.get_daily_schedule(business_id, date, target_user_id)
        
        job_list_dtos = [await self.job_helper_service.convert_to_list_dto(job) for job in jobs]
        
        total_hours = sum(
            job.time_tracking.estimated_hours or Decimal("0") 
            for job in jobs
        )
        
        return JobScheduleDTO(
            date=date,
            jobs=job_list_dtos,
            total_jobs=len(jobs),
            total_hours=total_hours,
            conflicts=self._detect_schedule_conflicts(jobs)
        )
    
    def _detect_schedule_conflicts(self, jobs: List) -> List[str]:
        """Detect schedule conflicts between jobs."""
        # TODO: Implement conflict detection logic
        # This would check for overlapping time slots, resource conflicts, etc.
        conflicts = []
        
        # Example conflict detection logic would go here
        # For now, returning empty list as placeholder
        
        return conflicts 