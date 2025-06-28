"""
Create Job Use Case

Business logic for job creation operations in Hero365.
Handles new job creation with validation and business rules.
"""

import uuid
from datetime import datetime
import logging

from ...dto.job_dto import JobCreateDTO, JobResponseDTO
from ...exceptions.application_exceptions import ValidationError
from app.domain.entities.job import (
    Job, JobAddress, JobTimeTracking, JobCostEstimate
)
from app.domain.repositories.job_repository import JobRepository
from app.domain.repositories.contact_repository import ContactRepository
from .job_helper_service import JobHelperService

logger = logging.getLogger(__name__)

class CreateJobUseCase:
    """
    Use case for creating new jobs within Hero365.
    
    Handles job creation with proper validation, permission checks,
    and business rule enforcement.
    """
    
    def __init__(
        self,
        job_repository: JobRepository,
        contact_repository: ContactRepository,
        job_helper_service: JobHelperService
    ):
        self.job_repository = job_repository
        self.contact_repository = contact_repository
        self.job_helper_service = job_helper_service
    
    async def execute(self, business_id: uuid.UUID, job_data: JobCreateDTO, 
                     created_by: str) -> JobResponseDTO:
        """Create a new job."""
        
        try:
            logger.info(f"Starting job creation for business {business_id} by user {created_by}")
            
            # Verify user has permission to create jobs
            logger.info("Checking create_jobs permission...")
            await self.job_helper_service.check_permission(business_id, created_by, "create_jobs")
            logger.info("Permission check passed")
            
            # Validate contact exists if provided
            if job_data.contact_id:
                logger.info(f"Validating contact {job_data.contact_id}...")
                contact = await self.contact_repository.get_by_id(job_data.contact_id)
                logger.info(f"Contact query result: {contact}")
                if not contact:
                    logger.error(f"Contact {job_data.contact_id} not found")
                    raise ValidationError("Invalid contact ID")
                if str(contact.business_id) != str(business_id):
                    logger.error(f"Contact business_id {contact.business_id} does not match job business_id {business_id}")
                    raise ValidationError("Invalid contact ID")
                logger.info("Contact validation passed")
            
            # Generate job number if not provided
            logger.info("Generating job number...")
            job_number = job_data.job_number
            if not job_number:
                job_number = await self.job_repository.get_next_job_number(business_id)
            else:
                # Check for duplicate job number
                if await self.job_repository.has_duplicate_job_number(business_id, job_number):
                    raise ValidationError(f"Job number '{job_number}' already exists")
            logger.info(f"Job number: {job_number}")
            
            # Validate assigned users exist in business
            if job_data.assigned_to:
                logger.info("Validating assigned users...")
                await self.job_helper_service.validate_assigned_users(business_id, job_data.assigned_to)
                logger.info("Assigned users validation passed")
            
            # Create job address if provided
            logger.info("Creating job address...")
            job_address = None
            if job_data.job_address:
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
            else:
                # Create a default address with placeholder values
                job_address = JobAddress(
                    street_address="No address provided",
                    city="Unknown",
                    state="Unknown",
                    postal_code="00000",
                    country="US"
                )
            logger.info("Job address created")
            
            # Create job
            logger.info("Creating job entity...")
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
            logger.info("Job entity created")
            
            # Set time tracking if provided
            if job_data.time_tracking:
                logger.info("Setting time tracking...")
                job.time_tracking = JobTimeTracking(
                    estimated_hours=job_data.time_tracking.estimated_hours,
                    actual_hours=job_data.time_tracking.actual_hours,
                    billable_hours=job_data.time_tracking.billable_hours,
                    start_time=job_data.time_tracking.start_time,
                    end_time=job_data.time_tracking.end_time,
                    break_time_minutes=job_data.time_tracking.break_time_minutes
                )
                logger.info("Time tracking set")
            
            # Set cost estimate if provided
            if job_data.cost_estimate:
                logger.info("Setting cost estimate...")
                job.cost_estimate = JobCostEstimate(
                    labor_cost=job_data.cost_estimate.labor_cost,
                    material_cost=job_data.cost_estimate.material_cost,
                    equipment_cost=job_data.cost_estimate.equipment_cost,
                    overhead_cost=job_data.cost_estimate.overhead_cost,
                    markup_percentage=job_data.cost_estimate.markup_percentage,
                    tax_percentage=job_data.cost_estimate.tax_percentage,
                    discount_amount=job_data.cost_estimate.discount_amount
                )
                logger.info("Cost estimate set")
            
            # Save job
            logger.info("Saving job to repository...")
            created_job = await self.job_repository.create(job)
            logger.info(f"Job saved with ID: {created_job.id}")
            
            # Convert to response DTO
            logger.info("Converting to response DTO...")
            result = await self.job_helper_service.convert_to_response_dto(created_job)
            logger.info("Job creation completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating job: {str(e)}", exc_info=True)
            raise 