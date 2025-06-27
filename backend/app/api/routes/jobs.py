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
    JobActionResponse, JobBulkActionResponse, JobErrorResponse,
    JobTypeSchema, JobStatusSchema, JobPrioritySchema, JobSourceSchema,
    JobAddressSchema, JobTimeTrackingSchema, JobCostEstimateSchema,
    JobContactSchema
)
from ...application.use_cases.job.create_job_use_case import CreateJobUseCase
from ...application.use_cases.job.get_job_use_case import GetJobUseCase
from ...application.use_cases.job.update_job_use_case import UpdateJobUseCase
from ...application.use_cases.job.delete_job_use_case import DeleteJobUseCase
from ...application.use_cases.job.job_status_management_use_case import JobStatusManagementUseCase
from ...application.use_cases.job.job_assignment_use_case import JobAssignmentUseCase
from ...application.use_cases.job.job_search_use_case import JobSearchUseCase
from ...application.use_cases.job.job_analytics_use_case import JobAnalyticsUseCase
from ...application.use_cases.job.job_scheduling_use_case import JobSchedulingUseCase
from ...application.use_cases.job.job_bulk_operations_use_case import JobBulkOperationsUseCase
from ...application.dto.job_dto import (
    JobCreateDTO, JobUpdateDTO, JobStatusUpdateDTO, JobAssignmentDTO,
    JobBulkUpdateDTO, JobSearchDTO, JobAddressDTO, JobTimeTrackingDTO,
    JobCostEstimateDTO
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, BusinessRuleViolationError
)
from ...infrastructure.config.dependency_injection import (
    get_create_job_use_case, get_get_job_use_case, get_update_job_use_case,
    get_delete_job_use_case, get_job_status_management_use_case, get_job_assignment_use_case,
    get_job_search_use_case, get_job_analytics_use_case, get_job_scheduling_use_case,
    get_job_bulk_operations_use_case
)
from ...domain.enums import JobType, JobStatus, JobPriority, JobSource


router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job",
    description="Create a new job with the provided details. Job number will be auto-generated if not provided."
)
@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job",
    description="Create a new job with the provided details. Job number will be auto-generated if not provided.",
    operation_id="create_job_no_slash"
)
async def create_job(
    job_data: JobCreateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: CreateJobUseCase = Depends(get_create_job_use_case)
) -> JobResponse:
    """Create a new job."""
    try:
        user_id = current_user["sub"]
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
        
        result = await use_case.execute(business_id, create_dto, user_id)
        return _convert_job_dto_to_response(result)
        
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
    use_case: GetJobUseCase = Depends(get_get_job_use_case)
) -> JobResponse:
    """Get a job by ID."""
    try:
        user_id = current_user["sub"]
        
        result = await use_case.execute(job_id, user_id)
        response = _convert_job_dto_to_response(result)
        return response
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        import traceback
        print(f"ERROR in get_job: {str(e)}")
        print(f"ERROR type: {type(e)}")
        print(f"Traceback: {traceback.format_exc()}")
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
    use_case: UpdateJobUseCase = Depends(get_update_job_use_case)
) -> JobResponse:
    """Update an existing job."""
    try:
        user_id = current_user["sub"]
        
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
            job_id=job_id,
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
        
        result = await use_case.execute(job_id, update_dto, user_id)
        return _convert_job_dto_to_response(result)
        
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


@router.delete(
    "/{job_id}",
    response_model=JobActionResponse,
    summary="Delete job",
    description="Delete a job. Cannot delete completed or invoiced jobs."
)
async def delete_job(
    job_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    use_case: DeleteJobUseCase = Depends(get_delete_job_use_case)
) -> JobActionResponse:
    """Delete a job."""
    try:
        user_id = current_user["sub"]
        
        success = await use_case.execute(job_id, user_id)
        
        if success:
            return JobActionResponse(
                success=True,
                message="Job deleted successfully",
                job_id=job_id
            )
        else:
            raise HTTPException(status_code=404, detail="Job not found")
            
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
@router.get(
    "",
    response_model=JobListPaginatedResponse,
    summary="List jobs",
    description="Get a paginated list of jobs for the current business.",
    operation_id="list_jobs_no_slash"
)
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of jobs to return"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: JobSearchUseCase = Depends(get_job_search_use_case)
) -> JobListPaginatedResponse:
    """List jobs for the current business."""
    user_id = current_user["sub"]
    business_id = business_context["business_id"]
    
    # Use list_jobs method to get all jobs
    results = await use_case.list_jobs(
        business_id=business_id,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    
    # Convert jobs to response DTOs
    return JobListPaginatedResponse(
        jobs=[_convert_job_list_dto_to_response(job) for job in results],
        total=len(results),
        skip=skip,
        limit=limit,
        has_more=len(results) == limit
    )


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
    use_case: JobSearchUseCase = Depends(get_job_search_use_case)
) -> JobListPaginatedResponse:
    """Search jobs with filters."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        search_dto = JobSearchDTO(
            business_id=business_id,
            search_term=search_request.search_term,
            job_type=JobType(search_request.job_type) if search_request.job_type else None,
            status=JobStatus(search_request.status) if search_request.status else None,
            priority=JobPriority(search_request.priority) if search_request.priority else None,
            source=JobSource(search_request.source) if search_request.source else None,
            assigned_to=search_request.assigned_to,
            contact_id=search_request.contact_id,
            is_overdue=search_request.is_overdue,
            is_emergency=search_request.is_emergency,
            skip=search_request.skip or 0,
            limit=search_request.limit or 100
        )
        
        results = await use_case.search_jobs(business_id, search_dto, user_id)
        
        return JobListPaginatedResponse(
            jobs=[_convert_job_list_dto_to_response(job) for job in results],
            total=len(results),
            skip=search_request.skip or 0,
            limit=search_request.limit or 100,
            has_more=len(results) == (search_request.limit or 100)
        )
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
    use_case: JobStatusManagementUseCase = Depends(get_job_status_management_use_case)
) -> JobResponse:
    """Update job status."""
    try:
        user_id = current_user["sub"]
        
        status_dto = JobStatusUpdateDTO(
            job_id=job_id,
            status=JobStatus(status_data.status),
            notes=status_data.notes
        )
        
        result = await use_case.update_job_status(job_id, status_dto, user_id)
        return _convert_job_dto_to_response(result)
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
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
    use_case: JobAssignmentUseCase = Depends(get_job_assignment_use_case)
) -> JobResponse:
    """Assign job to users."""
    try:
        user_id = current_user["sub"]
        
        assignment_dto = JobAssignmentDTO(
            job_id=job_id,
            user_ids=assignment_data.user_ids,
            replace_existing=assignment_data.replace_existing
        )
        
        result = await use_case.assign_job(job_id, assignment_dto, user_id)
        return _convert_job_dto_to_response(result)
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
    use_case: JobBulkOperationsUseCase = Depends(get_job_bulk_operations_use_case)
) -> JobBulkActionResponse:
    """Bulk update jobs."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        bulk_dto = JobBulkUpdateDTO(
            business_id=business_id,
            job_ids=bulk_data.job_ids,
            status=JobStatus(bulk_data.status) if bulk_data.status else None,
            assigned_to=bulk_data.assigned_to,
            tags_to_add=bulk_data.tags_to_add
        )
        
        updated_count = await use_case.bulk_update_jobs(business_id, bulk_dto, user_id)
        
        return JobBulkActionResponse(
            success=True,
            message=f"Successfully updated {updated_count} jobs",
            updated_count=updated_count
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
    use_case: JobAnalyticsUseCase = Depends(get_job_analytics_use_case)
) -> JobStatisticsResponse:
    """Get job statistics."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        stats = await use_case.get_job_statistics(business_id, user_id)
        
        return JobStatisticsResponse(
            total_jobs=stats.total_jobs,
            jobs_by_status=stats.jobs_by_status,
            jobs_by_type=stats.jobs_by_type,
            jobs_by_priority=stats.jobs_by_priority,
            overdue_jobs=stats.overdue_jobs,
            emergency_jobs=stats.emergency_jobs,
            jobs_in_progress=stats.jobs_in_progress,
            completed_this_month=stats.completed_this_month,
            revenue_this_month=stats.revenue_this_month,
            average_job_value=stats.average_job_value,
            top_job_types=stats.top_job_types,
            completion_rate=stats.completion_rate,
            on_time_completion_rate=stats.on_time_completion_rate
        )
        
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
    use_case: JobAnalyticsUseCase = Depends(get_job_analytics_use_case)
) -> JobWorkloadResponse:
    """Get user workload."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        workload = await use_case.get_user_workload(business_id, target_user_id, user_id)
        
        return JobWorkloadResponse(
            user_id=workload.user_id,
            total_assigned_jobs=workload.total_assigned_jobs,
            jobs_in_progress=workload.jobs_in_progress,
            overdue_jobs=workload.overdue_jobs,
            scheduled_this_week=workload.scheduled_this_week,
            total_estimated_hours=workload.total_estimated_hours,
            total_actual_hours=workload.total_actual_hours,
            utilization_rate=workload.utilization_rate,
            completion_rate=workload.completion_rate
        )
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
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
    use_case: JobSchedulingUseCase = Depends(get_job_scheduling_use_case)
) -> JobScheduleResponse:
    """Get daily schedule."""
    try:
        requesting_user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        schedule = await use_case.get_daily_schedule(business_id, date, requesting_user_id, user_id)
        
        return JobScheduleResponse(
            date=schedule.date,
            jobs=[_convert_job_list_dto_to_response(job) for job in schedule.jobs],
            total_jobs=schedule.total_jobs,
            total_hours=schedule.total_hours,
            conflicts=schedule.conflicts
        )
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/{job_id}/start",
    response_model=JobResponse,
    summary="Start job",
    description="Start a job (convenience endpoint for status update to in_progress)."
)
async def start_job(
    job_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    use_case: JobStatusManagementUseCase = Depends(get_job_status_management_use_case)
) -> JobResponse:
    """Start a job."""
    try:
        user_id = current_user["sub"]
        
        result = await use_case.start_job(job_id, user_id)
        return _convert_job_dto_to_response(result)
        
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
    use_case: JobStatusManagementUseCase = Depends(get_job_status_management_use_case)
) -> JobResponse:
    """Complete a job."""
    try:
        user_id = current_user["sub"]
        
        result = await use_case.complete_job(job_id, user_id, completion_notes)
        return _convert_job_dto_to_response(result)
        
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
    use_case: JobStatusManagementUseCase = Depends(get_job_status_management_use_case)
) -> JobResponse:
    """Cancel a job."""
    try:
        user_id = current_user["sub"]
        
        result = await use_case.cancel_job(job_id, user_id, reason)
        return _convert_job_dto_to_response(result)
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Helper functions

def _convert_job_type_to_api_enum(domain_type: JobType) -> JobTypeSchema:
    """Convert domain JobType to API JobTypeSchema."""
    return domain_type  # Since we're now using the same centralized enum


def _convert_job_status_to_api_enum(domain_status: JobStatus) -> JobStatusSchema:
    """Convert domain JobStatus to API JobStatusSchema."""
    return domain_status  # Since we're now using the same centralized enum


def _convert_job_priority_to_api_enum(domain_priority: JobPriority) -> JobPrioritySchema:
    """Convert domain JobPriority to API JobPrioritySchema."""
    return domain_priority  # Since we're now using the same centralized enum


def _convert_job_source_to_api_enum(domain_source: JobSource) -> JobSourceSchema:
    """Convert domain JobSource to API JobSourceSchema."""
    return domain_source  # Since we're now using the same centralized enum


def _convert_job_dto_to_response(job_dto) -> JobResponse:
    """Convert JobResponseDTO to JobResponse."""
    return JobResponse(
        id=job_dto.id,
        business_id=job_dto.business_id,
        contact_id=job_dto.contact_id,
        contact=job_dto.contact,
        job_number=job_dto.job_number,
        title=job_dto.title,
        description=job_dto.description,
        job_type=_convert_job_type_to_api_enum(job_dto.job_type),
        status=_convert_job_status_to_api_enum(job_dto.status),
        priority=_convert_job_priority_to_api_enum(job_dto.priority),
        source=_convert_job_source_to_api_enum(job_dto.source) if job_dto.source else None,
        job_address=JobAddressSchema(
            street_address=job_dto.job_address.street_address,
            city=job_dto.job_address.city,
            state=job_dto.job_address.state,
            postal_code=job_dto.job_address.postal_code,
            country=job_dto.job_address.country,
            latitude=job_dto.job_address.latitude,
            longitude=job_dto.job_address.longitude,
            access_notes=job_dto.job_address.access_notes
        ) if job_dto.job_address else None,
        scheduled_start=job_dto.scheduled_start,
        scheduled_end=job_dto.scheduled_end,
        actual_start=job_dto.actual_start,
        actual_end=job_dto.actual_end,
        assigned_to=job_dto.assigned_to,
        created_by=job_dto.created_by,
        time_tracking=JobTimeTrackingSchema(
            estimated_hours=job_dto.time_tracking.estimated_hours,
            actual_hours=job_dto.time_tracking.actual_hours,
            billable_hours=job_dto.time_tracking.billable_hours,
            start_time=job_dto.time_tracking.start_time,
            end_time=job_dto.time_tracking.end_time,
            break_time_minutes=job_dto.time_tracking.break_time_minutes
        ) if job_dto.time_tracking else None,
        cost_estimate=JobCostEstimateSchema(
            labor_cost=job_dto.cost_estimate.labor_cost,
            material_cost=job_dto.cost_estimate.material_cost,
            equipment_cost=job_dto.cost_estimate.equipment_cost,
            overhead_cost=job_dto.cost_estimate.overhead_cost,
            markup_percentage=job_dto.cost_estimate.markup_percentage,
            tax_percentage=job_dto.cost_estimate.tax_percentage,
            discount_amount=job_dto.cost_estimate.discount_amount
        ) if job_dto.cost_estimate else None,
        tags=job_dto.tags,
        notes=job_dto.notes,
        internal_notes=job_dto.internal_notes,
        customer_requirements=job_dto.customer_requirements,
        completion_notes=job_dto.completion_notes,
        custom_fields=job_dto.custom_fields,
        created_date=job_dto.created_date,
        last_modified=job_dto.last_modified,
        completed_date=job_dto.completed_date,
        is_overdue=job_dto.is_overdue,
        is_emergency=job_dto.is_emergency,
        duration_days=job_dto.duration_days,
        estimated_revenue=job_dto.estimated_revenue,
        profit_margin=job_dto.profit_margin,
        status_display=job_dto.status_display,
        priority_display=job_dto.priority_display,
        type_display=job_dto.type_display
    )


def _convert_job_list_dto_to_response(job_dto) -> JobListResponse:
    """Convert JobListDTO to JobListResponse."""
    return JobListResponse(
        id=job_dto.id,
        contact_id=job_dto.contact_id,
        contact=job_dto.contact,
        job_number=job_dto.job_number,
        title=job_dto.title,
        job_type=_convert_job_type_to_api_enum(job_dto.job_type),
        status=_convert_job_status_to_api_enum(job_dto.status),
        priority=_convert_job_priority_to_api_enum(job_dto.priority),
        scheduled_start=job_dto.scheduled_start,
        scheduled_end=job_dto.scheduled_end,
        assigned_to=job_dto.assigned_to,
        estimated_revenue=job_dto.estimated_revenue,
        is_overdue=job_dto.is_overdue,
        is_emergency=job_dto.is_emergency,
        created_date=job_dto.created_date,
        last_modified=job_dto.last_modified,
        status_display=job_dto.status_display,
        priority_display=job_dto.priority_display,
        type_display=job_dto.type_display
    ) 