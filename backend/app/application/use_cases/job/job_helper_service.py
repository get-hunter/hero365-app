"""
Job Helper Service

Common utilities and services for job use cases.
Contains shared functionality like permission checks and DTO conversions.
"""

import uuid
from typing import List

from ...dto.job_dto import (
    JobResponseDTO, JobListDTO, JobAddressDTO, JobTimeTrackingDTO, 
    JobCostEstimateDTO
)
from ...exceptions.application_exceptions import (
    ValidationError, PermissionDeniedError
)
from app.domain.entities.job import Job
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.repositories.contact_repository import ContactRepository


class JobHelperService:
    """
    Helper service for common job-related operations.
    
    Contains shared functionality used across multiple job use cases
    including permission checks and DTO conversions.
    """
    
    def __init__(
        self,
        business_membership_repository: BusinessMembershipRepository,
        contact_repository: ContactRepository
    ):
        self.business_membership_repository = business_membership_repository
        self.contact_repository = contact_repository
    
    async def check_permission(self, business_id: uuid.UUID, user_id: str, permission: str) -> None:
        """Check if user has permission for the business."""
        membership = await self.business_membership_repository.get_by_business_and_user(
            business_id, user_id
        )
        
        if not membership:
            raise PermissionDeniedError("User is not a member of this business")
        
        if not membership.has_permission(permission):
            raise PermissionDeniedError(f"User does not have {permission} permission")
    
    async def validate_assigned_users(self, business_id: uuid.UUID, user_ids: List[str]) -> None:
        """Validate that all user IDs are members of the business."""
        for user_id in user_ids:
            membership = await self.business_membership_repository.get_by_business_and_user(
                business_id, user_id
            )
            if not membership:
                raise ValidationError(f"User {user_id} is not a member of this business")
    
    async def convert_to_response_dto(self, job: Job) -> JobResponseDTO:
        """Convert Job entity to JobResponseDTO."""
        
        # Fetch contact data if contact_id exists
        contact_dto = None
        if job.contact_id:
            contact = await self.contact_repository.get_by_id(job.contact_id)
            if contact:
                from ...dto.job_dto import JobContactDTO
                contact_dto = JobContactDTO(
                    id=contact.id,
                    display_name=contact.get_display_name(),
                    company_name=contact.company_name,
                    email=contact.email,
                    phone=contact.phone,
                    mobile_phone=contact.mobile_phone,
                    primary_contact_method=contact.get_primary_contact_method()
                )
        
        return JobResponseDTO(
            id=job.id,
            business_id=job.business_id,
            contact_id=job.contact_id,
            contact=contact_dto,
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
    
    async def convert_to_list_dto(self, job: Job) -> JobListDTO:
        """Convert Job entity to JobListDTO."""
        
        # Fetch contact data if contact_id exists
        contact_dto = None
        if job.contact_id:
            contact = await self.contact_repository.get_by_id(job.contact_id)
            if contact:
                from ...dto.job_dto import JobContactDTO
                contact_dto = JobContactDTO(
                    id=contact.id,
                    display_name=contact.get_display_name(),
                    company_name=contact.company_name,
                    email=contact.email,
                    phone=contact.phone,
                    mobile_phone=contact.mobile_phone,
                    primary_contact_method=contact.get_primary_contact_method()
                )
        
        return JobListDTO(
            id=job.id,
            contact_id=job.contact_id,
            contact=contact_dto,
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