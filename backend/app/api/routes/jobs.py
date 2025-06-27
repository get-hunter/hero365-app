"""
Job API Routes

FastAPI routes for job management operations.
Handles all job-related HTTP endpoints with proper validation and error handling.
"""

import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..deps import get_current_user, get_business_context
from ..schemas.job_schemas import (
    JobCreateRequest, JobUpdateRequest, JobStatusUpdateRequest,
    JobAssignmentRequest, JobBulkUpdateRequest, JobSearchRequest,
    JobResponse, JobListResponse, JobStatisticsResponse,
    JobWorkloadResponse, JobScheduleResponse, JobListPaginatedResponse,
    JobActionResponse, JobBulkActionResponse, JobErrorResponse
)
from ...application.use_cases.job.manage_jobs import ManageJobsUseCase
from ...application.dto.job_dto import (
    JobCreateDTO, JobUpdateDTO, JobStatusUpdateDTO, JobAssignmentDTO,
    JobBulkUpdateDTO, JobSearchDTO, JobAddressDTO, JobTimeTrackingDTO,
    JobCostEstimateDTO
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, BusinessRuleViolationError
)
from ...infrastructure.config.dependency_injection import get_manage_jobs_use_case
from ...domain.entities.job import JobType, JobStatus, JobPriority, JobSource


router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job",
    description="Create a new job with the provided details. Job number will be auto-generated if not provided."
)
async def create_job(
    job_data: JobCreateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobResponse:
    """Create a new job."""
    try:
        user_id = current_user["id"]
        business_id = business_context["business_id"]
        
        # Convert request to DTO
        job_address_dto = None
        if job_data.job_address:
            job_address_dto = JobAddressDTO(
                street_address=job_data.job_address.street_address,
                city=job_data.job_address.city,
                state=job_data.job_address.state,
                postal_code=job_data.job_address.postal_code,
                country=job_data.job_address.country,
                latitude=job_data.job_address.latitude,
                longitude=job_data.job_address.longitude,
                access_notes=job_data.job_address.access_notes
            )
        
        time_tracking_dto = None
        if job_data.time_tracking:
            time_tracking_dto = JobTimeTrackingDTO(
                estimated_hours=job_data.time_tracking.estimated_hours,
                actual_hours=job_data.time_tracking.actual_hours,
                billable_hours=job_data.time_tracking.billable_hours,
                start_time=job_data.time_tracking.start_time,
                end_time=job_data.time_tracking.end_time,
                break_time_minutes=job_data.time_tracking.break_time_minutes
            )
        
        cost_estimate_dto = None
        if job_data.cost_estimate:
            cost_estimate_dto = JobCostEstimateDTO(
                labor_cost=job_data.cost_estimate.labor_cost,
                material_cost=job_data.cost_estimate.material_cost,
                equipment_cost=job_data.cost_estimate.equipment_cost,
                overhead_cost=job_data.cost_estimate.overhead_cost,
                markup_percentage=job_data.cost_estimate.markup_percentage,
                tax_percentage=job_data.cost_estimate.tax_percentage,
                discount_amount=job_data.cost_estimate.discount_amount
            )
        
        create_dto = JobCreateDTO(
            business_id=business_id,
            title=job_data.title,
            description=job_data.description,
            job_type=JobType(job_data.job_type),
            priority=JobPriority(job_data.priority) if job_data.priority else JobPriority.MEDIUM,
            source=JobSource(job_data.source) if job_data.source else JobSource.MANUAL,
            job_number=job_data.job_number,
            contact_id=job_data.contact_id,
            job_address=job_address_dto,
            scheduled_start=job_data.scheduled_start,
            scheduled_end=job_data.scheduled_end,
            assigned_to=job_data.assigned_to,
            tags=job_data.tags,
            notes=job_data.notes,
            internal_notes=job_data.internal_notes,
            customer_requirements=job_data.customer_requirements,
            time_tracking=time_tracking_dto,
            cost_estimate=cost_estimate_dto,
            custom_fields=job_data.custom_fields
        )
        
        result = await manage_jobs_use_case.create_job(business_id, create_dto, user_id)
        return JobResponse.model_validate(result)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job by ID",
    description="Retrieve a specific job by its ID."
)
async def get_job(
    job_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobResponse:
    """Get a job by ID."""
    try:
        user_id = current_user["id"]
        
        result = await manage_jobs_use_case.get_job(job_id, user_id)
        return JobResponse.model_validate(result)
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put(
    "/{job_id}",
    response_model=JobResponse,
    summary="Update job",
    description="Update an existing job with the provided details."
)
async def update_job(
    job_id: uuid.UUID,
    job_data: JobUpdateRequest,
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobResponse:
    """Update an existing job."""
    try:
        user_id = current_user["id"]
        
        # Convert request to DTO
        job_address_dto = None
        if job_data.job_address:
            job_address_dto = JobAddressDTO(
                street_address=job_data.job_address.street_address,
                city=job_data.job_address.city,
                state=job_data.job_address.state,
                postal_code=job_data.job_address.postal_code,
                country=job_data.job_address.country,
                latitude=job_data.job_address.latitude,
                longitude=job_data.job_address.longitude,
                access_notes=job_data.job_address.access_notes
            )
        
        time_tracking_dto = None
        if job_data.time_tracking:
            time_tracking_dto = JobTimeTrackingDTO(
                estimated_hours=job_data.time_tracking.estimated_hours,
                actual_hours=job_data.time_tracking.actual_hours,
                billable_hours=job_data.time_tracking.billable_hours,
                start_time=job_data.time_tracking.start_time,
                end_time=job_data.time_tracking.end_time,
                break_time_minutes=job_data.time_tracking.break_time_minutes
            )
        
        cost_estimate_dto = None
        if job_data.cost_estimate:
            cost_estimate_dto = JobCostEstimateDTO(
                labor_cost=job_data.cost_estimate.labor_cost,
                material_cost=job_data.cost_estimate.material_cost,
                equipment_cost=job_data.cost_estimate.equipment_cost,
                overhead_cost=job_data.cost_estimate.overhead_cost,
                markup_percentage=job_data.cost_estimate.markup_percentage,
                tax_percentage=job_data.cost_estimate.tax_percentage,
                discount_amount=job_data.cost_estimate.discount_amount
            )
        
        update_dto = JobUpdateDTO(
            title=job_data.title,
            description=job_data.description,
            job_type=JobType(job_data.job_type) if job_data.job_type else None,
            priority=JobPriority(job_data.priority) if job_data.priority else None,
            source=JobSource(job_data.source) if job_data.source else None,
            job_address=job_address_dto,
            scheduled_start=job_data.scheduled_start,
            scheduled_end=job_data.scheduled_end,
            assigned_to=job_data.assigned_to,
            tags=job_data.tags,
            notes=job_data.notes,
            internal_notes=job_data.internal_notes,
            customer_requirements=job_data.customer_requirements,
            completion_notes=job_data.completion_notes,
            time_tracking=time_tracking_dto,
            cost_estimate=cost_estimate_dto,
            custom_fields=job_data.custom_fields
        )
        
        result = await manage_jobs_use_case.update_job(job_id, update_dto, user_id)
        return JobResponse.model_validate(result)
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete(
    "/{job_id}",
    response_model=JobActionResponse,
    summary="Delete job",
    description="Delete a job. Cannot delete completed or invoiced jobs."
)
async def delete_job(
    job_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobActionResponse:
    """Delete a job."""
    try:
        user_id = current_user["id"]
        
        success = await manage_jobs_use_case.delete_job(job_id, user_id)
        
        if success:
            return JobActionResponse(
                success=True,
                message="Job deleted successfully",
                job_id=job_id
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to delete job")
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/",
    response_model=JobListPaginatedResponse,
    summary="List jobs",
    description="Get a paginated list of jobs for the current business."
)
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of jobs to return"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobListPaginatedResponse:
    """List jobs for a business."""
    try:
        business_id = business_context["business_id"]
        user_id = current_user["id"]
        
        jobs = await manage_jobs_use_case.list_jobs(business_id, user_id, skip, limit)
        
        # Convert to response DTOs
        job_responses = [JobListResponse.model_validate(job) for job in jobs]
        
        # Get total count (this could be optimized with a separate count query)
        total = len(job_responses) + skip  # Simplified for now
        has_more = len(job_responses) == limit
        
        return JobListPaginatedResponse(
            jobs=job_responses,
            total=total,
            skip=skip,
            limit=limit,
            has_more=has_more
        )
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/search",
    response_model=JobListPaginatedResponse,
    summary="Search jobs",
    description="Search jobs with various filters and criteria."
)
async def search_jobs(
    search_request: JobSearchRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobListPaginatedResponse:
    """Search jobs with filters."""
    try:
        business_id = business_context["business_id"]
        user_id = current_user["id"]
        
        # Convert request to DTO
        search_dto = JobSearchDTO(
            search_term=search_request.search_term,
            job_type=JobType(search_request.job_type) if search_request.job_type else None,
            status=JobStatus(search_request.status) if search_request.status else None,
            priority=JobPriority(search_request.priority) if search_request.priority else None,
            source=JobSource(search_request.source) if search_request.source else None,
            assigned_to=search_request.assigned_to,
            contact_id=search_request.contact_id,
            tags=search_request.tags,
            scheduled_start_from=search_request.scheduled_start_from,
            scheduled_start_to=search_request.scheduled_start_to,
            scheduled_end_from=search_request.scheduled_end_from,
            scheduled_end_to=search_request.scheduled_end_to,
            created_from=search_request.created_from,
            created_to=search_request.created_to,
            is_overdue=search_request.is_overdue,
            is_emergency=search_request.is_emergency,
            min_revenue=search_request.min_revenue,
            max_revenue=search_request.max_revenue,
            skip=search_request.skip,
            limit=search_request.limit,
            sort_by=search_request.sort_by,
            sort_order=search_request.sort_order
        )
        
        jobs = await manage_jobs_use_case.search_jobs(business_id, search_dto, user_id)
        
        # Convert to response DTOs
        job_responses = [JobListResponse.model_validate(job) for job in jobs]
        
        # Get total count (this could be optimized with a separate count query)
        total = len(job_responses) + search_request.skip  # Simplified for now
        has_more = len(job_responses) == search_request.limit
        
        return JobListPaginatedResponse(
            jobs=job_responses,
            total=total,
            skip=search_request.skip,
            limit=search_request.limit,
            has_more=has_more
        )
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch(
    "/{job_id}/status",
    response_model=JobResponse,
    summary="Update job status",
    description="Update the status of a job with optional notes."
)
async def update_job_status(
    job_id: uuid.UUID,
    status_data: JobStatusUpdateRequest,
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobResponse:
    """Update job status."""
    try:
        user_id = current_user["id"]
        
        status_dto = JobStatusUpdateDTO(
            status=JobStatus(status_data.status),
            notes=status_data.notes
        )
        
        result = await manage_jobs_use_case.update_job_status(job_id, status_dto, user_id)
        return JobResponse.model_validate(result)
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch(
    "/{job_id}/assign",
    response_model=JobResponse,
    summary="Assign job to users",
    description="Assign a job to one or more users."
)
async def assign_job(
    job_id: uuid.UUID,
    assignment_data: JobAssignmentRequest,
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobResponse:
    """Assign job to users."""
    try:
        user_id = current_user["id"]
        
        assignment_dto = JobAssignmentDTO(
            user_ids=assignment_data.user_ids,
            replace_existing=assignment_data.replace_existing
        )
        
        result = await manage_jobs_use_case.assign_job(job_id, assignment_dto, user_id)
        return JobResponse.model_validate(result)
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/bulk-update",
    response_model=JobBulkActionResponse,
    summary="Bulk update jobs",
    description="Update multiple jobs at once with the same changes."
)
async def bulk_update_jobs(
    bulk_data: JobBulkUpdateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobBulkActionResponse:
    """Bulk update jobs."""
    try:
        business_id = business_context["business_id"]
        user_id = current_user["id"]
        
        bulk_dto = JobBulkUpdateDTO(
            job_ids=bulk_data.job_ids,
            status=JobStatus(bulk_data.status) if bulk_data.status else None,
            assigned_to=bulk_data.assigned_to,
            tags_to_add=bulk_data.tags_to_add,
            tags_to_remove=bulk_data.tags_to_remove,
            priority=JobPriority(bulk_data.priority) if bulk_data.priority else None
        )
        
        updated_count = await manage_jobs_use_case.bulk_update_jobs(business_id, bulk_dto, user_id)
        
        return JobBulkActionResponse(
            success=True,
            message=f"Successfully updated {updated_count} jobs",
            updated_count=updated_count,
            failed_count=len(bulk_data.job_ids) - updated_count
        )
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/statistics",
    response_model=JobStatisticsResponse,
    summary="Get job statistics",
    description="Get comprehensive job statistics for the current business."
)
async def get_job_statistics(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobStatisticsResponse:
    """Get job statistics."""
    try:
        business_id = business_context["business_id"]
        user_id = current_user["id"]
        
        stats = await manage_jobs_use_case.get_job_statistics(business_id, user_id)
        return JobStatisticsResponse.model_validate(stats)
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/workload/{user_id}",
    response_model=JobWorkloadResponse,
    summary="Get user workload",
    description="Get workload statistics for a specific user."
)
async def get_user_workload(
    target_user_id: str,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobWorkloadResponse:
    """Get user workload."""
    try:
        business_id = business_context["business_id"]
        user_id = current_user["id"]
        
        workload = await manage_jobs_use_case.get_user_workload(business_id, target_user_id, user_id)
        return JobWorkloadResponse.model_validate(workload)
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/schedule/daily",
    response_model=JobScheduleResponse,
    summary="Get daily schedule",
    description="Get jobs scheduled for a specific day."
)
async def get_daily_schedule(
    date: datetime = Query(..., description="Date to get schedule for"),
    user_id: Optional[str] = Query(None, description="Filter by specific user"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobScheduleResponse:
    """Get daily job schedule."""
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user["id"]
        
        schedule = await manage_jobs_use_case.get_daily_schedule(
            business_id, date, current_user_id, user_id
        )
        return JobScheduleResponse.model_validate(schedule)
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Convenience endpoints for common job actions

@router.post(
    "/{job_id}/start",
    response_model=JobResponse,
    summary="Start job",
    description="Start a job (convenience endpoint for status update to in_progress)."
)
async def start_job(
    job_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobResponse:
    """Start a job."""
    try:
        user_id = current_user["id"]
        
        result = await manage_jobs_use_case.start_job(job_id, user_id)
        return JobResponse.model_validate(result)
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/{job_id}/complete",
    response_model=JobResponse,
    summary="Complete job",
    description="Complete a job with optional completion notes."
)
async def complete_job(
    job_id: uuid.UUID,
    completion_notes: Optional[str] = Query(None, description="Notes about job completion"),
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobResponse:
    """Complete a job."""
    try:
        user_id = current_user["id"]
        
        result = await manage_jobs_use_case.complete_job(job_id, user_id, completion_notes)
        return JobResponse.model_validate(result)
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/{job_id}/cancel",
    response_model=JobResponse,
    summary="Cancel job",
    description="Cancel a job with a reason."
)
async def cancel_job(
    job_id: uuid.UUID,
    reason: str = Query(..., description="Reason for cancellation"),
    current_user: dict = Depends(get_current_user),
    manage_jobs_use_case: ManageJobsUseCase = Depends(get_manage_jobs_use_case)
) -> JobResponse:
    """Cancel a job."""
    try:
        user_id = current_user["id"]
        
        result = await manage_jobs_use_case.cancel_job(job_id, user_id, reason)
        return JobResponse.model_validate(result)
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 