"""
Update Job Use Case

Business logic for job update operations in Hero365.
Handles job updates with validation and business rules.
"""

import uuid
from datetime import datetime

from ...dto.job_dto import JobUpdateDTO, JobResponseDTO
from ...exceptions.application_exceptions import NotFoundError
from app.domain.entities.job import (
    JobTimeTracking, JobCostEstimate
)
from app.domain.value_objects.address import Address
from app.domain.repositories.job_repository import JobRepository
from .job_helper_service import JobHelperService


class UpdateJobUseCase:
    """
    Use case for updating existing jobs within Hero365.
    
    Handles job updates with proper validation, permission checks,
    and business rule enforcement.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        job_helper_service: JobHelperService
    ):
        self.job_repository = job_repository
        self.job_helper_service = job_helper_service
    
    async def execute(self, job_id: uuid.UUID, job_data: JobUpdateDTO, 
                     user_id: str) -> JobResponseDTO:
        """Update an existing job."""
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        
        # Check permission
        await self.job_helper_service.check_permission(job.business_id, user_id, "edit_jobs")
        
        # Validate assigned users if provided
        if job_data.assigned_to is not None:
            await self.job_helper_service.validate_assigned_users(job.business_id, job_data.assigned_to)
        
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
            job.job_address = Address(
                street_address=job_data.job_address.street_address,
                city=job_data.job_address.city,
                state=job_data.job_address.state,
                postal_code=job_data.job_address.postal_code,
                country=job_data.job_address.country or "US",
                latitude=job_data.job_address.latitude,
                longitude=job_data.job_address.longitude,
                access_notes=job_data.job_address.access_notes,
                place_id=job_data.job_address.place_id,
                formatted_address=job_data.job_address.formatted_address,
                address_type=job_data.job_address.address_type
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
        
        return await self.job_helper_service.convert_to_response_dto(updated_job) 