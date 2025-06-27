"""
Job Analytics Use Case

Business logic for job analytics and statistics in Hero365.
Handles job statistics, workload analysis, and reporting operations.
"""

import uuid
from decimal import Decimal

from ...dto.job_dto import JobStatisticsDTO, JobWorkloadDTO
from app.domain.repositories.job_repository import JobRepository
from .job_helper_service import JobHelperService


class JobAnalyticsUseCase:
    """
    Use case for job analytics and statistics within Hero365.
    
    Handles job statistics, workload analysis, performance metrics,
    and reporting operations with proper permission validation.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        job_helper_service: JobHelperService
    ):
        self.job_repository = job_repository
        self.job_helper_service = job_helper_service
    
    async def get_job_statistics(self, business_id: uuid.UUID, user_id: str) -> JobStatisticsDTO:
        """Get job statistics for a business."""
        
        # Check permission
        await self.job_helper_service.check_permission(business_id, user_id, "view_jobs")
        
        stats = await self.job_repository.get_job_statistics(business_id)
        
        return JobStatisticsDTO(
            total_jobs=stats.get("total_jobs", 0),
            jobs_by_status=stats.get("jobs_by_status", {}),
            jobs_by_type=stats.get("jobs_by_type", {}),
            jobs_by_priority=stats.get("jobs_by_priority", {}),
            overdue_jobs=stats.get("overdue_jobs", 0),
            emergency_jobs=stats.get("emergency_jobs", 0),
            jobs_in_progress=stats.get("jobs_in_progress", 0),
            completed_this_month=stats.get("completed_this_month", 0),
            revenue_this_month=Decimal(str(stats.get("revenue_this_month", 0))),
            average_job_value=Decimal(str(stats.get("average_job_value", 0))),
            top_job_types=stats.get("top_job_types", []),
            completion_rate=float(stats.get("completion_rate", 0)),
            on_time_completion_rate=float(stats.get("on_time_completion_rate", 0))
        )
    
    async def get_user_workload(self, business_id: uuid.UUID, target_user_id: str,
                               user_id: str) -> JobWorkloadDTO:
        """Get workload for a specific user."""
        
        # Check permission
        await self.job_helper_service.check_permission(business_id, user_id, "view_jobs")
        
        workload = await self.job_repository.get_user_workload(business_id, target_user_id)
        
        return JobWorkloadDTO(
            user_id=target_user_id,
            total_assigned_jobs=workload.get("total_assigned_jobs", 0),
            jobs_in_progress=workload.get("jobs_in_progress", 0),
            overdue_jobs=workload.get("overdue_jobs", 0),
            scheduled_this_week=workload.get("scheduled_this_week", 0),
            total_estimated_hours=Decimal(str(workload.get("total_estimated_hours", 0))),
            total_actual_hours=Decimal(str(workload.get("total_actual_hours", 0))),
            utilization_rate=float(workload.get("utilization_rate", 0)),
            completion_rate=float(workload.get("completion_rate", 0))
        ) 