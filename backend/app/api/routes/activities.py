"""
Activity API Routes

REST endpoints for activity and timeline management with comprehensive RBAC integration.
"""

import uuid
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from fastapi.responses import JSONResponse

from ..deps import get_current_user, get_business_context
from ..middleware.permissions import require_view_contacts, require_edit_contacts, require_delete_contacts
from ..schemas.activity_schemas import (
    ActivityCreateRequest, ActivityUpdateRequest, ActivityResponse, ActivityListResponse,
    ActivityTemplateCreateRequest, ActivityTemplateResponse, TimelineRequest, TimelineResponse,
    ActivityStatisticsResponse, ContactActivitySummaryResponse, ActivityReminderResponse,
    DashboardActivitiesResponse, MessageResponse, BulkOperationResponse, PaginationParams,
    ActivityBulkUpdateRequest, ActivitySearchRequest
)
from ...application.use_cases.activity.manage_activities import ManageActivitiesUseCase
from ...application.dto.activity_dto import (
    ActivityCreateDTO, ActivityUpdateDTO, TimelineRequestDTO, ActivityTemplateCreateDTO
)
from ...domain.entities.activity import ActivityType, ActivityStatus, ActivityPriority
from ...infrastructure.config.dependency_injection import get_manage_activities_use_case

router = APIRouter(prefix="/activities", tags=["activities"])


# Activity CRUD Endpoints

@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
@require_edit_contacts
async def create_activity(
    request: ActivityCreateRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Create a new activity.
    
    Creates a new activity for a contact with optional template-based creation,
    participants, and reminders. Requires 'edit_contacts' permission.
    """
    # Convert request to DTO
    dto = ActivityCreateDTO(
        business_id=business_context["business_id"],
        contact_id=request.contact_id,
        activity_type=ActivityType(request.activity_type.value),
        title=request.title,
        description=request.description,
        scheduled_date=request.scheduled_date,
        due_date=request.due_date,
        priority=ActivityPriority(request.priority.value),
        assigned_to=request.assigned_to,
        duration_minutes=request.duration_minutes,
        location=request.location,
        tags=request.tags,
        metadata=request.metadata,
        template_id=request.template_id,
        participants=[
            {
                'user_id': p.user_id,
                'name': p.name,
                'role': p.role,
                'is_primary': p.is_primary
            } for p in request.participants
        ],
        reminders=request.reminders
    )
    
    # Create activity
    activity = await use_case.create_activity(dto, current_user["id"])
    
    return activity


@router.get("/{activity_id}", response_model=ActivityResponse)
@require_view_contacts
async def get_activity(
    activity_id: uuid.UUID = Path(..., description="Activity ID"),
    current_user: dict = Depends(get_current_user),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Get an activity by ID.
    
    Retrieves detailed information about a specific activity.
    Requires 'view_contacts' permission.
    """
    activity = await use_case.get_activity(activity_id, current_user["id"])
    return activity


@router.put("/{activity_id}", response_model=ActivityResponse)
@require_edit_contacts
async def update_activity(
    activity_id: uuid.UUID = Path(..., description="Activity ID"),
    request: ActivityUpdateRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Update an existing activity.
    
    Updates activity details, status, scheduling, and assignments.
    Requires 'edit_contacts' permission.
    """
    # Convert request to DTO
    dto = ActivityUpdateDTO(
        activity_id=activity_id,
        title=request.title,
        description=request.description,
        status=ActivityStatus(request.status.value) if request.status else None,
        priority=ActivityPriority(request.priority.value) if request.priority else None,
        scheduled_date=request.scheduled_date,
        due_date=request.due_date,
        duration_minutes=request.duration_minutes,
        location=request.location,
        assigned_to=request.assigned_to,
        tags=request.tags,
        metadata=request.metadata,
        notes=request.notes,
        reschedule_reason=request.reschedule_reason
    )
    
    # Update activity
    activity = await use_case.update_activity(dto, current_user["id"])
    
    return activity


@router.delete("/{activity_id}", response_model=MessageResponse)
@require_delete_contacts
async def delete_activity(
    activity_id: uuid.UUID = Path(..., description="Activity ID"),
    current_user: dict = Depends(get_current_user),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Delete an activity.
    
    Permanently deletes an activity and all associated data.
    Requires 'delete_contacts' permission.
    """
    success = await use_case.delete_activity(activity_id, current_user["id"])
    
    if success:
        return MessageResponse(message="Activity deleted successfully")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete activity"
        )


# Activity Search and Listing

@router.post("/search", response_model=ActivityListResponse)
@require_view_contacts
async def search_activities(
    search_request: ActivitySearchRequest = Body(...),
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Search activities with advanced filtering.
    
    Provides comprehensive search and filtering capabilities for activities
    including date ranges, status, priority, assignment, and text search.
    Requires 'view_contacts' permission.
    """
    # Get business activities with filtering
    activities = await use_case.get_business_activities(
        business_id=business_context["business_id"],
        activity_types=[ActivityType(t.value) for t in search_request.activity_types] if search_request.activity_types else None,
        statuses=[ActivityStatus(s.value) for s in search_request.statuses] if search_request.statuses else None,
        assigned_to=search_request.assigned_to,
        start_date=search_request.start_date,
        end_date=search_request.end_date,
        skip=pagination.skip,
        limit=pagination.limit
    )
    
    return activities


@router.get("/user/assigned", response_model=ActivityListResponse)
@require_view_contacts
async def get_user_activities(
    pagination: PaginationParams = Depends(),
    statuses: Optional[List[str]] = Query(None, description="Filter by activity statuses"),
    start_date: Optional[datetime] = Query(None, description="Filter activities after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter activities before this date"),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Get activities assigned to the current user.
    
    Retrieves activities assigned to the authenticated user with optional filtering.
    Requires 'view_contacts' permission.
    """
    # Convert status strings to enums
    status_enums = None
    if statuses:
        status_enums = [ActivityStatus(s) for s in statuses]
    
    activities = await use_case.get_user_activities(
        business_id=business_context["business_id"],
        user_id=current_user["id"],
        statuses=status_enums,
        start_date=start_date,
        end_date=end_date,
        skip=pagination.skip,
        limit=pagination.limit
    )
    
    return activities


@router.get("/overdue", response_model=List[ActivityResponse])
@require_view_contacts
async def get_overdue_activities(
    assigned_to: Optional[str] = Query(None, description="Filter by assigned user"),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Get overdue activities.
    
    Retrieves all overdue activities for the business or a specific user.
    Requires 'view_contacts' permission.
    """
    activities = await use_case.get_overdue_activities(
        business_id=business_context["business_id"],
        user_id=current_user["id"],
        assigned_to=assigned_to
    )
    
    return activities


@router.get("/upcoming", response_model=List[ActivityResponse])
@require_view_contacts
async def get_upcoming_activities(
    days_ahead: int = Query(default=7, ge=1, le=30, description="Number of days to look ahead"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned user"),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Get upcoming activities.
    
    Retrieves activities scheduled within the specified number of days.
    Requires 'view_contacts' permission.
    """
    activities = await use_case.get_upcoming_activities(
        business_id=business_context["business_id"],
        user_id=current_user["id"],
        days_ahead=days_ahead,
        assigned_to=assigned_to
    )
    
    return activities


# Timeline Endpoints

@router.post("/timeline", response_model=TimelineResponse)
@require_view_contacts
async def get_contact_timeline(
    timeline_request: TimelineRequest = Body(...),
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Get activity timeline for a contact.
    
    Retrieves a chronological timeline of all activities for a specific contact
    with optional filtering by date range and activity types.
    Requires 'view_contacts' permission.
    """
    # Convert request to DTO
    dto = TimelineRequestDTO(
        contact_id=timeline_request.contact_id,
        business_id=business_context["business_id"],
        start_date=timeline_request.start_date,
        end_date=timeline_request.end_date,
        activity_types=[ActivityType(t.value) for t in timeline_request.activity_types] if timeline_request.activity_types else None,
        skip=pagination.skip,
        limit=pagination.limit
    )
    
    timeline = await use_case.get_contact_timeline(dto, current_user["id"])
    
    return timeline


# Bulk Operations

@router.post("/bulk-update", response_model=BulkOperationResponse)
@require_edit_contacts
async def bulk_update_activities(
    bulk_request: ActivityBulkUpdateRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Bulk update multiple activities.
    
    Updates multiple activities at once with the same changes.
    Useful for batch operations like status changes or reassignments.
    Requires 'edit_contacts' permission.
    """
    success_count = 0
    error_count = 0
    errors = []
    
    for activity_id in bulk_request.activity_ids:
        try:
            # Create update DTO for each activity
            dto = ActivityUpdateDTO(
                activity_id=activity_id,
                status=ActivityStatus(bulk_request.status.value) if bulk_request.status else None,
                priority=ActivityPriority(bulk_request.priority.value) if bulk_request.priority else None,
                assigned_to=bulk_request.assigned_to,
                due_date=bulk_request.due_date,
                scheduled_date=bulk_request.reschedule_date,
                notes=bulk_request.notes
            )
            
            await use_case.update_activity(dto, current_user["id"])
            success_count += 1
            
        except Exception as e:
            error_count += 1
            errors.append(f"Activity {activity_id}: {str(e)}")
    
    return BulkOperationResponse(
        success_count=success_count,
        error_count=error_count,
        errors=errors,
        message=f"Bulk update completed: {success_count} successful, {error_count} failed"
    )


# Template Endpoints

@router.post("/templates", response_model=ActivityTemplateResponse, status_code=status.HTTP_201_CREATED)
@require_edit_contacts
async def create_activity_template(
    request: ActivityTemplateCreateRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Create a new activity template.
    
    Creates a reusable template for standardizing activity creation.
    Requires 'edit_contacts' permission.
    """
    # Convert request to DTO
    dto = ActivityTemplateCreateDTO(
        business_id=business_context["business_id"],
        name=request.name,
        description=request.description,
        activity_type=ActivityType(request.activity_type.value),
        default_duration=request.default_duration,
        default_reminders=request.default_reminders,
        default_participants=request.default_participants,
        custom_fields=request.custom_fields
    )
    
    template = await use_case.create_activity_template(dto, current_user["id"])
    
    return template


@router.get("/templates", response_model=List[ActivityTemplateResponse])
@require_view_contacts
async def get_activity_templates(
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Get activity templates for the business.
    
    Retrieves all active templates with optional filtering by activity type.
    Requires 'view_contacts' permission.
    """
    activity_type_enum = None
    if activity_type:
        activity_type_enum = ActivityType(activity_type)
    
    templates = await use_case.get_business_templates(
        business_id=business_context["business_id"],
        user_id=current_user["id"],
        activity_type=activity_type_enum
    )
    
    return templates


# Statistics and Analytics

@router.get("/statistics", response_model=ActivityStatisticsResponse)
@require_view_contacts
async def get_activity_statistics(
    start_date: Optional[datetime] = Query(None, description="Statistics start date"),
    end_date: Optional[datetime] = Query(None, description="Statistics end date"),
    user_filter: Optional[str] = Query(None, description="Filter statistics for specific user"),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Get activity statistics for the business.
    
    Provides comprehensive analytics including completion rates, activity distributions,
    and performance metrics. Requires 'view_contacts' permission.
    """
    statistics = await use_case.get_activity_statistics(
        business_id=business_context["business_id"],
        user_id=current_user["id"],
        start_date=start_date,
        end_date=end_date,
        filter_user_id=user_filter
    )
    
    return ActivityStatisticsResponse(**statistics)


@router.get("/contacts/{contact_id}/summary", response_model=ContactActivitySummaryResponse)
@require_view_contacts
async def get_contact_activity_summary(
    contact_id: uuid.UUID = Path(..., description="Contact ID"),
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Get activity summary for a specific contact.
    
    Provides engagement metrics and activity overview for a contact.
    Requires 'view_contacts' permission.
    """
    summary = await use_case.get_contact_activity_summary(
        contact_id=contact_id,
        business_id=business_context["business_id"],
        user_id=current_user["id"]
    )
    
    return ContactActivitySummaryResponse(**summary)


# Reminder Management

@router.get("/reminders/pending", response_model=List[ActivityReminderResponse])
@require_view_contacts
async def get_pending_reminders(
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Get pending reminders for activities.
    
    Retrieves all reminders that are due to be sent within the next hour.
    Requires 'view_contacts' permission.
    """
    reminders = await use_case.get_pending_reminders(
        business_id=business_context["business_id"],
        user_id=current_user["id"]
    )
    
    return reminders


@router.post("/reminders/{reminder_id}/mark-sent", response_model=MessageResponse)
@require_edit_contacts
async def mark_reminder_sent(
    reminder_id: uuid.UUID = Path(..., description="Reminder ID"),
    activity_id: uuid.UUID = Query(..., description="Activity ID"),
    current_user: dict = Depends(get_current_user),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Mark a reminder as sent.
    
    Updates the reminder status to indicate it has been delivered.
    Requires 'edit_contacts' permission.
    """
    success = await use_case.mark_reminder_sent(
        activity_id=activity_id,
        reminder_id=reminder_id,
        user_id=current_user["id"]
    )
    
    if success:
        return MessageResponse(message="Reminder marked as sent")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark reminder as sent"
        )


# Dashboard Overview

@router.get("/dashboard", response_model=DashboardActivitiesResponse)
@require_view_contacts
async def get_dashboard_activities(
    current_user: dict = Depends(get_current_user),
    business_context: dict = Depends(get_business_context),
    use_case: ManageActivitiesUseCase = Depends(get_manage_activities_use_case)
):
    """
    Get dashboard overview of activities.
    
    Provides a comprehensive overview including overdue activities, upcoming tasks,
    recent activities, statistics, and pending reminders for dashboard display.
    Requires 'view_contacts' permission.
    """
    # Get various activity lists
    overdue_activities = await use_case.get_overdue_activities(
        business_id=business_context["business_id"],
        user_id=current_user["id"],
        assigned_to=current_user["id"]
    )
    
    upcoming_activities = await use_case.get_upcoming_activities(
        business_id=business_context["business_id"],
        user_id=current_user["id"],
        days_ahead=7,
        assigned_to=current_user["id"]
    )
    
    user_activities = await use_case.get_user_activities(
        business_id=business_context["business_id"],
        user_id=current_user["id"],
        statuses=[ActivityStatus.COMPLETED],
        skip=0,
        limit=5
    )
    
    statistics = await use_case.get_activity_statistics(
        business_id=business_context["business_id"],
        user_id=current_user["id"],
        filter_user_id=current_user["id"]
    )
    
    reminders = await use_case.get_pending_reminders(
        business_id=business_context["business_id"],
        user_id=current_user["id"]
    )
    
    # Count high priority activities
    high_priority_count = len([a for a in overdue_activities + upcoming_activities if a.priority in ['high', 'urgent']])
    
    # Calculate completion rate
    total_activities = statistics.get('total_activities', 0)
    completed_activities = statistics.get('completed_activities', 0)
    completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0
    
    return DashboardActivitiesResponse(
        overdue_activities=overdue_activities[:10],  # Limit to 10 most urgent
        upcoming_activities=upcoming_activities[:10],
        recent_activities=user_activities.activities,
        activity_statistics=ActivityStatisticsResponse(**statistics),
        reminders_due=reminders,
        high_priority_count=high_priority_count,
        completion_rate=completion_rate
    ) 