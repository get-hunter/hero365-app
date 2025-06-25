"""
Job Management Use Cases

Business logic for job management operations in Hero365.
Handles job creation, updates, status transitions, and analytics.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from ...dto.job_dto import (
    JobCreateDTO, JobUpdateDTO, JobResponseDTO, JobListDTO, JobSearchDTO,
    JobStatusUpdateDTO, JobAssignmentDTO, JobBulkUpdateDTO, JobStatisticsDTO,
    JobRevenueDTO, JobWorkloadDTO, JobScheduleDTO, JobTimeTrackingDTO,
    JobCostEstimateDTO, JobAddressDTO, JobExportDTO, JobImportDTO, 
    JobImportResultDTO, JobConversionDTO
)
from ...exceptions.application_exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, BusinessRuleViolationError
)
from app.domain.entities.job import (
    Job, JobType, JobStatus, JobPriority, JobSource, JobAddress, 
    JobTimeTracking, JobCostEstimate
)
from app.domain.repositories.job_repository import JobRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.repositories.contact_repository import ContactRepository


class ManageJobsUseCase:
    """
    Use case for managing jobs within Hero365.
    
    Handles all job-related business operations including creation,
    updates, status transitions, assignments, and analytics.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        business_membership_repository: BusinessMembershipRepository,
        contact_repository: ContactRepository
    ):
        self.job_repository = job_repository
        self.business_membership_repository = business_membership_repository
        self.contact_repository = contact_repository
    
    async def create_job(self, business_id: uuid.UUID, job_data: JobCreateDTO, 
                        created_by: str) -> JobResponseDTO:
        """Create a new job."""
        
        # Verify user has permission to create jobs
        await self._check_permission(business_id, created_by, "create_jobs")
        
        # Validate contact exists if provided
        if job_data.contact_id:
            contact = await self.contact_repository.get_by_id(job_data.contact_id)
            if not contact or contact.business_id != business_id:
                raise ValidationError("Invalid contact ID")
        
        # Generate job number if not provided
        job_number = job_data.job_number
        if not job_number:
            job_number = await self.job_repository.get_next_job_number(business_id)
        else:
            # Check for duplicate job number
            if await self.job_repository.has_duplicate_job_number(business_id, job_number):
                raise ValidationError(f"Job number '{job_number}' already exists")
        
        # Validate assigned users exist in business
        if job_data.assigned_to:
            await self._validate_assigned_users(business_id, job_data.assigned_to)
        
        # Create job address
        job_address = JobAddress(
            street_address=job_data.job_address.street_address,
            city=job_data.job_address.city,
            state=job_data.job_address.state,
            postal_code=job_data.job_address.postal_code,
            country=job_data.job_address.country,
            latitude=job_data.job_address.latitude,
            longitude=job_data.job_address.longitude,
            access_notes=job_data.job_address.access_notes
        )
        
        # Create job
        job = Job.create_job(
            business_id=business_id,
            contact_id=job_data.contact_id,
            job_number=job_number,
            title=job_data.title,
            description=job_data.description,
            job_type=job_data.job_type,
            priority=job_data.priority,
            source=job_data.source,
            job_address=job_address,
            created_by=created_by,
            scheduled_start=job_data.scheduled_start,
            scheduled_end=job_data.scheduled_end,
            assigned_to=job_data.assigned_to or [],
            tags=job_data.tags or [],
            notes=job_data.notes,
            customer_requirements=job_data.customer_requirements,
            custom_fields=job_data.custom_fields or {}
        )
        
        # Set time tracking if provided
        if job_data.time_tracking:
            job.time_tracking = JobTimeTracking(
                estimated_hours=job_data.time_tracking.estimated_hours,
                actual_hours=job_data.time_tracking.actual_hours,
                billable_hours=job_data.time_tracking.billable_hours,
                start_time=job_data.time_tracking.start_time,
                end_time=job_data.time_tracking.end_time,
                break_time_minutes=job_data.time_tracking.break_time_minutes
            )
        
        # Set cost estimate if provided
        if job_data.cost_estimate:
            job.cost_estimate = JobCostEstimate(
                labor_cost=job_data.cost_estimate.labor_cost,
                material_cost=job_data.cost_estimate.material_cost,
                equipment_cost=job_data.cost_estimate.equipment_cost,
                overhead_cost=job_data.cost_estimate.overhead_cost,
                markup_percentage=job_data.cost_estimate.markup_percentage,
                tax_percentage=job_data.cost_estimate.tax_percentage,
                discount_amount=job_data.cost_estimate.discount_amount
            )
        
        # Save job
        created_job = await self.job_repository.create(job)
        
        return await self._convert_to_response_dto(created_job)
    
    async def get_job(self, job_id: uuid.UUID, user_id: str) -> JobResponseDTO:
        """Get a job by ID."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self._check_permission(job.business_id, user_id, "view_jobs")
        
        return await self._convert_to_response_dto(job)
    
    async def update_job(self, job_id: uuid.UUID, job_data: JobUpdateDTO, 
                        user_id: str) -> JobResponseDTO:
        """Update an existing job."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self._check_permission(job.business_id, user_id, "edit_jobs")
        
        # Validate assigned users if provided
        if job_data.assigned_to is not None:
            await self._validate_assigned_users(job.business_id, job_data.assigned_to)
        
        # Update job fields
        if job_data.title is not None:
            job.title = job_data.title
        if job_data.description is not None:
            job.description = job_data.description
        if job_data.job_type is not None:
            job.job_type = job_data.job_type
        if job_data.priority is not None:
            job.priority = job_data.priority
        if job_data.source is not None:
            job.source = job_data.source
        if job_data.scheduled_start is not None or job_data.scheduled_end is not None:
            job.update_schedule(job_data.scheduled_start, job_data.scheduled_end)
        if job_data.assigned_to is not None:
            job.assigned_to = job_data.assigned_to
        if job_data.tags is not None:
            job.tags = job_data.tags
        if job_data.notes is not None:
            job.notes = job_data.notes
        if job_data.internal_notes is not None:
            job.internal_notes = job_data.internal_notes
        if job_data.customer_requirements is not None:
            job.customer_requirements = job_data.customer_requirements
        if job_data.completion_notes is not None:
            job.completion_notes = job_data.completion_notes
        if job_data.custom_fields is not None:
            job.custom_fields = job_data.custom_fields
        
        # Update job address if provided
        if job_data.job_address:
            job.job_address = JobAddress(
                street_address=job_data.job_address.street_address,
                city=job_data.job_address.city,
                state=job_data.job_address.state,
                postal_code=job_data.job_address.postal_code,
                country=job_data.job_address.country,
                latitude=job_data.job_address.latitude,
                longitude=job_data.job_address.longitude,
                access_notes=job_data.job_address.access_notes
            )
        
        # Update time tracking if provided
        if job_data.time_tracking:
            job.time_tracking = JobTimeTracking(
                estimated_hours=job_data.time_tracking.estimated_hours,
                actual_hours=job_data.time_tracking.actual_hours,
                billable_hours=job_data.time_tracking.billable_hours,
                start_time=job_data.time_tracking.start_time,
                end_time=job_data.time_tracking.end_time,
                break_time_minutes=job_data.time_tracking.break_time_minutes
            )
        
        # Update cost estimate if provided
        if job_data.cost_estimate:
            job.cost_estimate = JobCostEstimate(
                labor_cost=job_data.cost_estimate.labor_cost,
                material_cost=job_data.cost_estimate.material_cost,
                equipment_cost=job_data.cost_estimate.equipment_cost,
                overhead_cost=job_data.cost_estimate.overhead_cost,
                markup_percentage=job_data.cost_estimate.markup_percentage,
                tax_percentage=job_data.cost_estimate.tax_percentage,
                discount_amount=job_data.cost_estimate.discount_amount
            )
        
        job.last_modified = datetime.utcnow()
        
        # Save updated job
        updated_job = await self.job_repository.update(job)
        
        return await self._convert_to_response_dto(updated_job)
    
    async def update_job_status(self, job_id: uuid.UUID, status_data: JobStatusUpdateDTO,
                               user_id: str) -> JobResponseDTO:
        """Update job status."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self._check_permission(job.business_id, user_id, "edit_jobs")
        
        # Update status using domain logic
        job.update_status(status_data.status, user_id, status_data.notes)
        
        # Save updated job
        updated_job = await self.job_repository.update(job)
        
        return await self._convert_to_response_dto(updated_job)
    
    async def assign_job(self, job_id: uuid.UUID, assignment_data: JobAssignmentDTO,
                        user_id: str) -> JobResponseDTO:
        """Assign job to users."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self._check_permission(job.business_id, user_id, "edit_jobs")
        
        # Validate assigned users
        await self._validate_assigned_users(job.business_id, assignment_data.user_ids)
        
        if assignment_data.replace_existing:
            job.assigned_to = assignment_data.user_ids
        else:
            for user_id_to_assign in assignment_data.user_ids:
                job.assign_team_member(user_id_to_assign)
        
        # Save updated job
        updated_job = await self.job_repository.update(job)
        
        return await self._convert_to_response_dto(updated_job)
    
    async def delete_job(self, job_id: uuid.UUID, user_id: str) -> bool:
        """Delete a job."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self._check_permission(job.business_id, user_id, "delete_jobs")
        
        # Business rule: Cannot delete completed or invoiced jobs
        if job.status in [JobStatus.COMPLETED, JobStatus.INVOICED, JobStatus.PAID]:
            raise BusinessRuleViolationError("Cannot delete completed or invoiced jobs")
        
        return await self.job_repository.delete(job_id)
    
    async def list_jobs(self, business_id: uuid.UUID, user_id: str,
                       skip: int = 0, limit: int = 100) -> List[JobListDTO]:
        """List jobs for a business."""
        
        # Check permission
        await self._check_permission(business_id, user_id, "view_jobs")
        
        jobs = await self.job_repository.get_by_business_id(business_id, skip, limit)
        
        return [await self._convert_to_list_dto(job) for job in jobs]
    
    async def search_jobs(self, business_id: uuid.UUID, search_params: JobSearchDTO,
                         user_id: str) -> List[JobListDTO]:
        """Search jobs with filters."""
        
        # Check permission
        await self._check_permission(business_id, user_id, "view_jobs")
        
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
        
        return [await self._convert_to_list_dto(job) for job in jobs]
    
    async def get_job_statistics(self, business_id: uuid.UUID, user_id: str) -> JobStatisticsDTO:
        """Get job statistics for a business."""
        
        # Check permission
        await self._check_permission(business_id, user_id, "view_jobs")
        
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
    
    async def bulk_update_jobs(self, business_id: uuid.UUID, bulk_data: JobBulkUpdateDTO,
                              user_id: str) -> int:
        """Bulk update jobs."""
        
        # Check permission
        await self._check_permission(business_id, user_id, "edit_jobs")
        
        updated_count = 0
        
        if bulk_data.status:
            updated_count += await self.job_repository.bulk_update_status(
                business_id, bulk_data.job_ids, bulk_data.status
            )
        
        if bulk_data.assigned_to:
            # Validate user exists in business
            await self._validate_assigned_users(business_id, [bulk_data.assigned_to])
            updated_count += await self.job_repository.bulk_assign_jobs(
                business_id, bulk_data.job_ids, bulk_data.assigned_to
            )
        
        if bulk_data.tags_to_add:
            for tag in bulk_data.tags_to_add:
                await self.job_repository.bulk_add_tag(business_id, bulk_data.job_ids, tag)
        
        return updated_count
    
    async def start_job(self, job_id: uuid.UUID, user_id: str) -> JobResponseDTO:
        """Start a job (convenience method)."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self._check_permission(job.business_id, user_id, "edit_jobs")
        
        job.start_job(user_id)
        
        updated_job = await self.job_repository.update(job)
        return await self._convert_to_response_dto(updated_job)
    
    async def complete_job(self, job_id: uuid.UUID, user_id: str,
                          completion_notes: Optional[str] = None) -> JobResponseDTO:
        """Complete a job (convenience method)."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self._check_permission(job.business_id, user_id, "edit_jobs")
        
        job.complete_job(user_id, completion_notes)
        
        updated_job = await self.job_repository.update(job)
        return await self._convert_to_response_dto(updated_job)
    
    async def cancel_job(self, job_id: uuid.UUID, user_id: str, reason: str) -> JobResponseDTO:
        """Cancel a job (convenience method)."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self._check_permission(job.business_id, user_id, "edit_jobs")
        
        job.cancel_job(user_id, reason)
        
        updated_job = await self.job_repository.update(job)
        return await self._convert_to_response_dto(updated_job)
    
    async def get_user_workload(self, business_id: uuid.UUID, target_user_id: str,
                               user_id: str) -> JobWorkloadDTO:
        """Get workload for a specific user."""
        
        # Check permission
        await self._check_permission(business_id, user_id, "view_jobs")
        
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
    
    async def get_daily_schedule(self, business_id: uuid.UUID, date: datetime,
                                user_id: str, target_user_id: Optional[str] = None) -> JobScheduleDTO:
        """Get daily job schedule."""
        
        # Check permission
        await self._check_permission(business_id, user_id, "view_jobs")
        
        jobs = await self.job_repository.get_daily_schedule(business_id, date, target_user_id)
        
        job_list_dtos = [await self._convert_to_list_dto(job) for job in jobs]
        
        total_hours = sum(
            job.time_tracking.estimated_hours or Decimal("0") 
            for job in jobs
        )
        
        return JobScheduleDTO(
            date=date,
            jobs=job_list_dtos,
            total_jobs=len(jobs),
            total_hours=total_hours,
            conflicts=[]  # TODO: Implement conflict detection
        )
    
    # Helper methods
    
    async def _check_permission(self, business_id: uuid.UUID, user_id: str, permission: str) -> None:
        """Check if user has permission for the business."""
        membership = await self.business_membership_repository.get_by_business_and_user(
            business_id, user_id
        )
        
        if not membership:
            raise PermissionDeniedError("User is not a member of this business")
        
        if not membership.has_permission(permission):
            raise PermissionDeniedError(f"User does not have {permission} permission")
    
    async def _validate_assigned_users(self, business_id: uuid.UUID, user_ids: List[str]) -> None:
        """Validate that all user IDs are members of the business."""
        for user_id in user_ids:
            membership = await self.business_membership_repository.get_by_business_and_user(
                business_id, user_id
            )
            if not membership:
                raise ValidationError(f"User {user_id} is not a member of this business")
    
    async def _convert_to_response_dto(self, job: Job) -> JobResponseDTO:
        """Convert Job entity to JobResponseDTO."""
        return JobResponseDTO(
            id=job.id,
            business_id=job.business_id,
            contact_id=job.contact_id,
            job_number=job.job_number,
            title=job.title,
            description=job.description,
            job_type=job.job_type,
            status=job.status,
            priority=job.priority,
            source=job.source,
            job_address=JobAddressDTO(
                street_address=job.job_address.street_address,
                city=job.job_address.city,
                state=job.job_address.state,
                postal_code=job.job_address.postal_code,
                country=job.job_address.country,
                latitude=job.job_address.latitude,
                longitude=job.job_address.longitude,
                access_notes=job.job_address.access_notes
            ),
            scheduled_start=job.scheduled_start,
            scheduled_end=job.scheduled_end,
            actual_start=job.actual_start,
            actual_end=job.actual_end,
            assigned_to=job.assigned_to,
            created_by=job.created_by,
            time_tracking=JobTimeTrackingDTO(
                estimated_hours=job.time_tracking.estimated_hours,
                actual_hours=job.time_tracking.actual_hours,
                billable_hours=job.time_tracking.billable_hours,
                start_time=job.time_tracking.start_time,
                end_time=job.time_tracking.end_time,
                break_time_minutes=job.time_tracking.break_time_minutes
            ),
            cost_estimate=JobCostEstimateDTO(
                labor_cost=job.cost_estimate.labor_cost,
                material_cost=job.cost_estimate.material_cost,
                equipment_cost=job.cost_estimate.equipment_cost,
                overhead_cost=job.cost_estimate.overhead_cost,
                markup_percentage=job.cost_estimate.markup_percentage,
                tax_percentage=job.cost_estimate.tax_percentage,
                discount_amount=job.cost_estimate.discount_amount
            ),
            tags=job.tags,
            notes=job.notes,
            internal_notes=job.internal_notes,
            customer_requirements=job.customer_requirements,
            completion_notes=job.completion_notes,
            custom_fields=job.custom_fields,
            created_date=job.created_date,
            last_modified=job.last_modified,
            completed_date=job.completed_date,
            is_overdue=job.is_overdue(),
            is_emergency=job.is_emergency(),
            duration_days=job.get_duration_days(),
            estimated_revenue=job.get_estimated_revenue(),
            profit_margin=job.get_profit_margin(),
            status_display=job.get_status_display(),
            priority_display=job.get_priority_display(),
            type_display=job.get_type_display()
        )
    
    async def _convert_to_list_dto(self, job: Job) -> JobListDTO:
        """Convert Job entity to JobListDTO."""
        return JobListDTO(
            id=job.id,
            job_number=job.job_number,
            title=job.title,
            job_type=job.job_type,
            status=job.status,
            priority=job.priority,
            scheduled_start=job.scheduled_start,
            scheduled_end=job.scheduled_end,
            assigned_to=job.assigned_to,
            estimated_revenue=job.get_estimated_revenue(),
            is_overdue=job.is_overdue(),
            is_emergency=job.is_emergency(),
            created_date=job.created_date,
            last_modified=job.last_modified,
            status_display=job.get_status_display(),
            priority_display=job.get_priority_display(),
            type_display=job.get_type_display()
        ) 