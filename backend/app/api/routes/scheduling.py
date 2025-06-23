"""
Intelligent Scheduling API Routes

FastAPI routes for intelligent job scheduling operations with real-time optimization.
Handles schedule optimization, real-time adaptation, and analytics endpoints.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.responses import JSONResponse

from ..deps import get_current_user, get_business_context
from ..schemas.scheduling_schemas import (
    SchedulingOptimizationRequest, SchedulingOptimizationResponse,
    RealTimeAdaptationRequest, RealTimeAdaptationResponse,
    SchedulingAnalyticsRequest, SchedulingAnalyticsResponse,
    RealTimeScheduleStatusResponse, LocationUpdateRequest,
    SchedulingErrorResponse,
    AvailableTimeSlotRequest, AvailableTimeSlotsResponse,
    TimeSlotBookingRequest, TimeSlotBookingResponse,
    WorkingHoursTemplate, CreateWorkingHoursTemplateRequest, WorkingHoursResponse,
    CalendarEvent, CreateCalendarEventRequest, CalendarEventResponse,
    TimeOffRequest, CreateTimeOffRequest, ApproveTimeOffRequest, TimeOffResponse,
    CalendarPreferences, CalendarPreferencesResponse,
    UserAvailability, AvailabilityCheckRequest, AvailabilityCheckResponse,
    TeamAvailabilitySummary, SetUserWorkingHoursRequest
)
from ...application.use_cases.scheduling.intelligent_scheduling_use_case import IntelligentSchedulingUseCase
from ...application.use_cases.scheduling.calendar_management_use_case import CalendarManagementUseCase
from ...application.dto.scheduling_dto import (
    SchedulingOptimizationRequestDTO, RealTimeAdaptationRequestDTO,
    SchedulingAnalyticsRequestDTO, TimeWindowDTO, LocationUpdateDTO,
    AvailableTimeSlotRequestDTO, TimeSlotBookingRequestDTO,
    UpdateWorkingHoursRequestDTO, CalendarPreferencesDTO
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, BusinessLogicError
)
from ...infrastructure.config.dependency_injection import get_intelligent_scheduling_use_case, get_calendar_management_use_case

router = APIRouter(prefix="/scheduling", tags=["Intelligent Scheduling"])
logger = logging.getLogger(__name__)


@router.post(
    "/optimize",
    response_model=SchedulingOptimizationResponse,
    summary="Optimize job scheduling",
    description="Optimize job scheduling using intelligent algorithms with real-time data integration."
)
async def optimize_schedule(
    request: SchedulingOptimizationRequest,
    background_tasks: BackgroundTasks,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    scheduling_use_case: IntelligentSchedulingUseCase = Depends(get_intelligent_scheduling_use_case)
) -> SchedulingOptimizationResponse:
    """
    Optimize job scheduling using intelligent algorithms.
    
    Features:
    - Real-time travel time calculations
    - Weather impact analysis
    - Multi-objective optimization
    - Skill-based assignment
    - Workload balancing
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user["user_id"]
        
        # Convert request to DTO
        request_dto = SchedulingOptimizationRequestDTO(
            job_ids=request.job_ids,
            time_window=TimeWindowDTO(
                start_time=request.time_window.start_time,
                end_time=request.time_window.end_time
            ) if request.time_window else None,
            constraints=request.constraints,
            baseline_metrics=request.baseline_metrics,
            notify_users=request.notify_users,
            optimization_algorithm=request.optimization_algorithm
        )
        
        # Execute optimization
        result = await scheduling_use_case.optimize_schedule(
            business_id, request_dto, current_user_id
        )
        
        # Schedule background analytics update if requested
        if request.update_analytics:
            background_tasks.add_task(
                _update_optimization_analytics,
                business_id, result.optimization_id
            )
        
        return SchedulingOptimizationResponse.model_validate(result)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.post(
    "/real-time-adapt",
    response_model=RealTimeAdaptationResponse,
    summary="Adapt schedule in real-time",
    description="Adapt existing schedules based on real-time disruptions and conditions."
)
async def adapt_schedule_realtime(
    request: RealTimeAdaptationRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    scheduling_use_case: IntelligentSchedulingUseCase = Depends(get_intelligent_scheduling_use_case)
) -> RealTimeAdaptationResponse:
    """
    Adapt existing schedule based on real-time disruptions.
    
    Handles:
    - Traffic delays
    - Weather conditions
    - Emergency job insertions
    - Resource unavailability
    - Customer reschedules
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user["user_id"]
        
        # Convert request to DTO
        request_dto = RealTimeAdaptationRequestDTO(
            disruption=request.disruption,
            adaptation_preferences=request.adaptation_preferences
        )
        
        # Execute adaptation
        result = await scheduling_use_case.adapt_schedule_realtime(
            business_id, request_dto, current_user_id
        )
        
        return RealTimeAdaptationResponse.model_validate(result)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule adaptation failed: {str(e)}")


@router.get(
    "/analytics",
    response_model=SchedulingAnalyticsResponse,
    summary="Get scheduling analytics",
    description="Get comprehensive scheduling performance analytics and insights."
)
async def get_scheduling_analytics(
    start_date: datetime = Query(..., description="Analytics period start date"),
    end_date: datetime = Query(..., description="Analytics period end date"),
    user_id: Optional[str] = Query(None, description="Filter by specific user"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    include_predictions: bool = Query(True, description="Include predictive insights"),
    include_recommendations: bool = Query(True, description="Include improvement recommendations"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    scheduling_use_case: IntelligentSchedulingUseCase = Depends(get_intelligent_scheduling_use_case)
) -> SchedulingAnalyticsResponse:
    """
    Get scheduling performance analytics.
    
    Provides:
    - Key performance indicators
    - Trend analysis
    - Improvement recommendations
    - Predictive insights
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user["user_id"]
        
        # Validate date range
        if end_date <= start_date:
            raise ValidationError("End date must be after start date")
        
        if (end_date - start_date).days > 365:
            raise ValidationError("Analytics period cannot exceed 365 days")
        
        # Convert request to DTO
        request_dto = SchedulingAnalyticsRequestDTO(
            period=TimeWindowDTO(start_time=start_date, end_time=end_date),
            user_id=user_id,
            job_type=job_type,
            include_predictions=include_predictions,
            include_recommendations=include_recommendations
        )
        
        # Get analytics
        result = await scheduling_use_case.get_scheduling_analytics(
            business_id, request_dto, current_user_id
        )
        
        return SchedulingAnalyticsResponse.model_validate(result)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")


@router.get(
    "/analytics/predictions",
    response_model=dict,
    summary="Get scheduling predictions",
    description="Get predictive analytics for upcoming scheduling needs and capacity planning."
)
async def get_scheduling_predictions(
    forecast_days: int = Query(7, ge=1, le=30, description="Number of days to forecast"),
    job_types: Optional[List[str]] = Query(None, description="Filter by job types"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    scheduling_use_case: IntelligentSchedulingUseCase = Depends(get_intelligent_scheduling_use_case)
) -> dict:
    """
    Get predictive analytics for scheduling optimization.
    
    Forecasts:
    - Expected job volume
    - Resource demand patterns
    - Capacity gaps
    - Optimization opportunities
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user["user_id"]
        
        # Implementation for predictions would go here
        # For now, return a placeholder response
        forecast_end = datetime.utcnow() + timedelta(days=forecast_days)
        
        return {
            "forecast_period": {
                "start_date": datetime.utcnow().isoformat(),
                "end_date": forecast_end.isoformat()
            },
            "predictions": {
                "expected_job_volume": 45,
                "resource_demand": [
                    {
                        "date": (datetime.utcnow() + timedelta(days=i)).date().isoformat(),
                        "required_technicians": 8 + (i % 3),
                        "skills_in_demand": ["electrical", "plumbing"],
                        "peak_hours": ["09:00", "14:00"]
                    }
                    for i in range(forecast_days)
                ],
                "capacity_gaps": [],
            },
            "optimization_opportunities": [
                {
                    "date": (datetime.utcnow() + timedelta(days=2)).date().isoformat(),
                    "type": "route_optimization",
                    "potential_savings": {
                        "time_minutes": 120,
                        "cost_dollars": 85.50
                    }
                }
            ]
        }
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Predictions generation failed: {str(e)}")


@router.get(
    "/real-time/status",
    response_model=RealTimeScheduleStatusResponse,
    summary="Get real-time schedule status",
    description="Get current status of all active jobs and real-time performance metrics."
)
async def get_realtime_schedule_status(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    scheduling_use_case: IntelligentSchedulingUseCase = Depends(get_intelligent_scheduling_use_case)
) -> RealTimeScheduleStatusResponse:
    """
    Get real-time status of current schedules.
    
    Provides:
    - Active job statuses
    - Real-time locations
    - Performance metrics
    - Delay alerts
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user["user_id"]
        
        # Implementation would get real-time data
        # For now, return a placeholder response
        current_time = datetime.utcnow()
        
        return RealTimeScheduleStatusResponse(
            current_time=current_time,
            active_jobs=[
                {
                    "job_id": str(uuid.uuid4()),
                    "assigned_user_id": "user_123",
                    "status": "in_progress",
                    "scheduled_start": current_time - timedelta(hours=1),
                    "actual_start": current_time - timedelta(minutes=55),
                    "estimated_completion": current_time + timedelta(hours=1),
                    "location": {"latitude": 40.7128, "longitude": -74.0060},
                    "delay_minutes": 5,
                    "alerts": []
                }
            ],
            performance_today={
                "jobs_completed": 12,
                "jobs_in_progress": 8,
                "jobs_delayed": 2,
                "average_delay_minutes": 8.5,
                "on_time_percentage": 87.5
            },
            alerts=[],
            system_health="healthy"
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


@router.post(
    "/real-time/update-location",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Update user location",
    description="Update user location for real-time tracking and optimization."
)
async def update_user_location(
    request: LocationUpdateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user)
) -> None:
    """
    Update user location for real-time tracking.
    
    Used for:
    - Real-time route optimization
    - Accurate travel time calculations
    - Emergency response coordination
    - Performance monitoring
    """
    try:
        business_id = business_context["business_id"]
        
        # Convert request to DTO
        location_dto = LocationUpdateDTO(
            user_id=request.user_id,
            latitude=request.location.latitude,
            longitude=request.location.longitude,
            accuracy_meters=request.location.accuracy_meters,
            timestamp=request.location.timestamp,
            status=request.status
        )
        
        # Implementation would update location in real-time tracking system
        # For now, just validate the request
        if not (-90 <= location_dto.latitude <= 90):
            raise ValidationError("Invalid latitude value")
        
        if not (-180 <= location_dto.longitude <= 180):
            raise ValidationError("Invalid longitude value")
        
        # Location update would be processed here
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Location update failed: {str(e)}")


@router.get(
    "/optimization-history",
    response_model=List[dict],
    summary="Get optimization history",
    description="Get history of schedule optimizations and their performance."
)
async def get_optimization_history(
    days: int = Query(30, ge=1, le=90, description="Number of days of history"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user)
) -> List[dict]:
    """Get optimization history for performance tracking."""
    try:
        business_id = business_context["business_id"]
        
        # Implementation would get optimization history from database
        # For now, return placeholder data
        history = []
        for i in range(min(limit, 10)):
            history.append({
                "optimization_id": str(uuid.uuid4()),
                "timestamp": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                "jobs_optimized": 15 + i,
                "travel_time_saved_minutes": 45 + (i * 5),
                "success_rate": 0.95 - (i * 0.01),
                "algorithm_used": "intelligent"
            })
        
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


@router.delete(
    "/optimization/{optimization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel optimization",
    description="Cancel a running optimization process."
)
async def cancel_optimization(
    optimization_id: str,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user)
) -> None:
    """Cancel a running optimization process."""
    try:
        business_id = business_context["business_id"]
        
        # Implementation would cancel the optimization
        # For now, just validate the ID format
        try:
            uuid.UUID(optimization_id)
        except ValueError:
            raise ValidationError("Invalid optimization ID format")
        
        # Cancellation logic would go here
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cancellation failed: {str(e)}")


@router.post(
    "/available-slots",
    response_model=AvailableTimeSlotsResponse,
    summary="Get available time slots",
    description="Get available time slots for customer booking based on job requirements and preferences."
)
async def get_available_time_slots(
    request: AvailableTimeSlotRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    scheduling_use_case: IntelligentSchedulingUseCase = Depends(get_intelligent_scheduling_use_case)
) -> AvailableTimeSlotsResponse:
    """
    Get available time slots for customer booking.
    
    Features:
    - Real-time technician availability
    - Skill-based matching
    - Travel time calculations
    - Weather impact analysis
    - Dynamic pricing
    - Quality scoring
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        # Convert request to DTO
        request_dto = AvailableTimeSlotRequestDTO(
            job_type=request.job_type,
            estimated_duration_hours=request.estimated_duration_hours,
            required_skills=request.required_skills,
            job_address=request.job_address,
            preferred_date_range=TimeWindowDTO(
                start_time=request.preferred_date_range.start_time,
                end_time=request.preferred_date_range.end_time
            ),
            customer_preferences=request.customer_preferences,
            priority=request.priority
        )
        
        # Get available time slots
        result = await scheduling_use_case.get_available_time_slots(
            business_id, request_dto, current_user_id
        )
        
        return AvailableTimeSlotsResponse.model_validate(result)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available slots: {str(e)}")


@router.post(
    "/book-slot",
    response_model=TimeSlotBookingResponse,
    summary="Book a time slot",
    description="Book a specific time slot for a customer and create a scheduled job."
)
async def book_time_slot(
    request: TimeSlotBookingRequest,
    background_tasks: BackgroundTasks,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    scheduling_use_case: IntelligentSchedulingUseCase = Depends(get_intelligent_scheduling_use_case)
) -> TimeSlotBookingResponse:
    """
    Book a specific time slot for a customer.
    
    Features:
    - Slot availability validation
    - Job creation and assignment
    - Automatic notifications
    - Confirmation details
    - Booking policies
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        # Convert request to DTO
        request_dto = TimeSlotBookingRequestDTO(
            slot_id=request.slot_id,
            customer_contact=request.customer_contact,
            job_details=request.job_details,
            special_instructions=request.special_instructions,
            confirm_booking=request.confirm_booking
        )
        
        # Book the time slot
        result = await scheduling_use_case.book_time_slot(
            business_id, request_dto, current_user_id
        )
        
        # Schedule background task for additional processing
        background_tasks.add_task(
            _process_booking_analytics,
            business_id, result.booking_id
        )
        
        return TimeSlotBookingResponse.model_validate(result)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to book time slot: {str(e)}")


@router.get(
    "/slots/{slot_id}/availability",
    response_model=Dict[str, Any],
    summary="Check slot availability",
    description="Check if a specific time slot is still available for booking."
)
async def check_slot_availability(
    slot_id: str,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    scheduling_use_case: IntelligentSchedulingUseCase = Depends(get_intelligent_scheduling_use_case)
) -> Dict[str, Any]:
    """
    Check if a specific time slot is still available.
    
    Returns:
    - Availability status
    - Expiration time
    - Alternative slots if unavailable
    """
    try:
        business_id = business_context["business_id"]
        
        # Validate slot availability
        is_available = await scheduling_use_case._validate_slot_availability(
            business_id, slot_id
        )
        
        return {
            "slot_id": slot_id,
            "is_available": is_available,
            "checked_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=15)).isoformat(),
            "message": "Slot is available" if is_available else "Slot is no longer available"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check slot availability: {str(e)}")


@router.post(
    "/slots/bulk-check",
    response_model=List[Dict[str, Any]],
    summary="Bulk check slot availability",
    description="Check availability for multiple time slots at once."
)
async def bulk_check_slot_availability(
    slot_ids: List[str],
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    scheduling_use_case: IntelligentSchedulingUseCase = Depends(get_intelligent_scheduling_use_case)
) -> List[Dict[str, Any]]:
    """
    Check availability for multiple time slots.
    
    Useful for:
    - Refreshing slot lists
    - Validating cart items
    - Real-time availability updates
    """
    try:
        business_id = business_context["business_id"]
        results = []
        
        for slot_id in slot_ids[:20]:  # Limit to 20 slots per request
            is_available = await scheduling_use_case._validate_slot_availability(
                business_id, slot_id
            )
            
            results.append({
                "slot_id": slot_id,
                "is_available": is_available,
                "checked_at": datetime.utcnow().isoformat()
            })
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check slots availability: {str(e)}")


# Background task functions
async def _update_optimization_analytics(business_id: uuid.UUID, optimization_id: str):
    """Background task to update optimization analytics."""
    try:
        # Implementation would update analytics in background
        pass
    except Exception as e:
        logger.error(f"Failed to update optimization analytics: {str(e)}")


async def _process_booking_analytics(business_id: uuid.UUID, booking_id: str):
    """Process booking analytics in the background."""
    try:
        # This would update booking analytics, send follow-up emails, etc.
        logger.info(f"Processing booking analytics for booking {booking_id}")
        # Implementation would go here
    except Exception as e:
        logger.error(f"Error processing booking analytics: {str(e)}")


# =============================================================================
# CALENDAR MANAGEMENT ENDPOINTS
# =============================================================================

# Working Hours Management
@router.post(
    "/working-hours/templates",
    response_model=WorkingHoursResponse,
    summary="Create working hours template",
    description="Create a new working hours template for the business."
)
async def create_working_hours_template(
    request: CreateWorkingHoursTemplateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> WorkingHoursResponse:
    """
    Create a working hours template.
    
    Features:
    - Define weekly schedule patterns
    - Set break and lunch times
    - Configure flexibility settings
    - Reusable across team members
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        # Convert request to DTO
        request_dto = UpdateWorkingHoursRequestDTO(
            template_name=request.name,
            description=request.description,
            monday_start=request.monday_start,
            monday_end=request.monday_end,
            tuesday_start=request.tuesday_start,
            tuesday_end=request.tuesday_end,
            wednesday_start=request.wednesday_start,
            wednesday_end=request.wednesday_end,
            thursday_start=request.thursday_start,
            thursday_end=request.thursday_end,
            friday_start=request.friday_start,
            friday_end=request.friday_end,
            saturday_start=request.saturday_start,
            saturday_end=request.saturday_end,
            sunday_start=request.sunday_start,
            sunday_end=request.sunday_end,
            break_duration_minutes=request.break_duration_minutes,
            lunch_start_time=request.lunch_start_time,
            lunch_duration_minutes=request.lunch_duration_minutes
        )
        
        template = await calendar_use_case.create_working_hours_template(
            business_id, request_dto, current_user_id
        )
        
        return WorkingHoursResponse(
            message="Working hours template created successfully",
            template=WorkingHoursTemplate.model_validate(template.__dict__)
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create working hours template: {str(e)}")


@router.get(
    "/working-hours/templates",
    response_model=List[WorkingHoursTemplate],
    summary="Get working hours templates",
    description="Get all working hours templates for the business."
)
async def get_working_hours_templates(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> List[WorkingHoursTemplate]:
    """Get all working hours templates for the business."""
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        templates = await calendar_use_case.get_working_hours_templates(
            business_id, current_user_id
        )
        
        return [WorkingHoursTemplate.model_validate(template.__dict__) for template in templates]
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get working hours templates: {str(e)}")


@router.post(
    "/users/{user_id}/working-hours",
    response_model=WorkingHoursResponse,
    summary="Set user working hours",
    description="Set working hours for a specific user."
)
async def set_user_working_hours(
    user_id: str,
    request: SetUserWorkingHoursRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> WorkingHoursResponse:
    """
    Set working hours for a user.
    
    Features:
    - Use existing template or create custom hours
    - Individual schedule configuration
    - Flexible break and lunch times
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        # Convert request to DTO
        request_dto = UpdateWorkingHoursRequestDTO(
            template_id=request.template_id,
            monday_start=request.monday_start,
            monday_end=request.monday_end,
            tuesday_start=request.tuesday_start,
            tuesday_end=request.tuesday_end,
            wednesday_start=request.wednesday_start,
            wednesday_end=request.wednesday_end,
            thursday_start=request.thursday_start,
            thursday_end=request.thursday_end,
            friday_start=request.friday_start,
            friday_end=request.friday_end,
            saturday_start=request.saturday_start,
            saturday_end=request.saturday_end,
            sunday_start=request.sunday_start,
            sunday_end=request.sunday_end,
            break_duration_minutes=request.break_duration_minutes,
            lunch_start_time=request.lunch_start_time,
            lunch_duration_minutes=request.lunch_duration_minutes
        )
        
        template = await calendar_use_case.set_user_working_hours(
            business_id, user_id, request_dto, current_user_id
        )
        
        return WorkingHoursResponse(
            message="User working hours set successfully",
            template=WorkingHoursTemplate.model_validate(template.__dict__)
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set user working hours: {str(e)}")


# Calendar Events Management
@router.post(
    "/users/{user_id}/calendar/events",
    response_model=CalendarEventResponse,
    summary="Create calendar event",
    description="Create a calendar event for a user."
)
async def create_calendar_event(
    user_id: str,
    request: CreateCalendarEventRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> CalendarEventResponse:
    """
    Create a calendar event.
    
    Features:
    - Various event types (meetings, breaks, personal)
    - Recurring event patterns
    - Scheduling impact configuration
    - Timezone support
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        # Convert request to DTO
        request_dto = CreateCalendarEventRequestDTO(
            title=request.title,
            description=request.description,
            event_type=request.event_type.value,
            start_datetime=request.start_datetime,
            end_datetime=request.end_datetime,
            is_all_day=request.is_all_day,
            timezone=request.timezone,
            recurrence_type=request.recurrence_type.value,
            recurrence_end_date=request.recurrence_end_date,
            recurrence_count=request.recurrence_count,
            recurrence_interval=request.recurrence_interval,
            recurrence_days_of_week=request.recurrence_days_of_week,
            blocks_scheduling=request.blocks_scheduling,
            allows_emergency_override=request.allows_emergency_override
        )
        
        event = await calendar_use_case.create_calendar_event(
            business_id, user_id, request_dto, current_user_id
        )
        
        return CalendarEventResponse(
            message="Calendar event created successfully",
            event=CalendarEvent.model_validate(event.__dict__)
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create calendar event: {str(e)}")


@router.get(
    "/users/{user_id}/calendar/events",
    response_model=List[CalendarEvent],
    summary="Get calendar events",
    description="Get calendar events for a user within a date range."
)
async def get_calendar_events(
    user_id: str,
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> List[CalendarEvent]:
    """Get calendar events for a user within a date range."""
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        events = await calendar_use_case.get_calendar_events(
            business_id, user_id, start_date, end_date, current_user_id
        )
        
        return [CalendarEvent.model_validate(event.__dict__) for event in events]
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get calendar events: {str(e)}")


@router.delete(
    "/calendar/events/{event_id}",
    summary="Delete calendar event",
    description="Delete a calendar event."
)
async def delete_calendar_event(
    event_id: str,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
):
    """Delete a calendar event."""
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        success = await calendar_use_case.delete_calendar_event(
            business_id, event_id, current_user_id
        )
        
        if success:
            return {"message": "Calendar event deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Calendar event not found")
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete calendar event: {str(e)}")


# Time Off Management
@router.post(
    "/users/{user_id}/time-off",
    response_model=TimeOffResponse,
    summary="Create time off request",
    description="Create a time off request for a user."
)
async def create_time_off_request(
    user_id: str,
    request: CreateTimeOffRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> TimeOffResponse:
    """
    Create a time off request.
    
    Features:
    - Various time off types (vacation, sick, personal)
    - Approval workflow
    - Scheduling impact configuration
    - Emergency contact settings
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        # Convert request to DTO
        request_dto = CreateTimeOffRequestDTO(
            time_off_type=request.time_off_type.value,
            start_date=request.start_date,
            end_date=request.end_date,
            reason=request.reason,
            notes=request.notes,
            affects_scheduling=request.affects_scheduling,
            emergency_contact_allowed=request.emergency_contact_allowed
        )
        
        time_off = await calendar_use_case.create_time_off_request(
            business_id, user_id, request_dto, current_user_id
        )
        
        return TimeOffResponse(
            message="Time off request created successfully",
            time_off_request=TimeOffRequest.model_validate(time_off.__dict__)
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create time off request: {str(e)}")


@router.post(
    "/time-off/{time_off_id}/approve",
    response_model=TimeOffResponse,
    summary="Approve/deny time off request",
    description="Approve or deny a time off request."
)
async def approve_time_off_request(
    time_off_id: str,
    request: ApproveTimeOffRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> TimeOffResponse:
    """
    Approve or deny a time off request.
    
    Features:
    - Admin approval workflow
    - Denial reasons
    - Automatic notifications
    - Schedule impact updates
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        approved = request.status.value == "approved"
        
        time_off = await calendar_use_case.approve_time_off_request(
            business_id, time_off_id, approved, request.denial_reason, current_user_id
        )
        
        return TimeOffResponse(
            message=f"Time off request {'approved' if approved else 'denied'} successfully",
            time_off_request=TimeOffRequest.model_validate(time_off.__dict__)
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process time off request: {str(e)}")


@router.get(
    "/time-off",
    response_model=List[TimeOffRequest],
    summary="Get time off requests",
    description="Get time off requests for the business or specific user."
)
async def get_time_off_requests(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> List[TimeOffRequest]:
    """Get time off requests with optional filtering."""
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        requests = await calendar_use_case.get_time_off_requests(
            business_id, user_id, status, current_user_id
        )
        
        return [TimeOffRequest.model_validate(req.__dict__) for req in requests]
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get time off requests: {str(e)}")


# Availability Management
@router.post(
    "/availability/check",
    response_model=AvailabilityCheckResponse,
    summary="Check user availability",
    description="Check availability for multiple users within a time period."
)
async def check_user_availability(
    request: AvailabilityCheckRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> AvailabilityCheckResponse:
    """
    Check user availability.
    
    Features:
    - Multi-user availability check
    - Comprehensive availability data
    - Working hours consideration
    - Time off and calendar events
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        # Convert request to DTO
        request_dto = AvailabilityCheckRequestDTO(
            user_ids=request.user_ids,
            start_datetime=request.start_datetime,
            end_datetime=request.end_datetime,
            include_time_off=request.include_time_off,
            include_calendar_events=request.include_calendar_events,
            include_working_hours=request.include_working_hours
        )
        
        result = await calendar_use_case.check_user_availability(
            business_id, request_dto, current_user_id
        )
        
        return AvailabilityCheckResponse.model_validate(result.__dict__)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check availability: {str(e)}")


@router.get(
    "/availability/team-summary",
    response_model=TeamAvailabilitySummary,
    summary="Get team availability summary",
    description="Get comprehensive team availability summary for a date range."
)
async def get_team_availability_summary(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> TeamAvailabilitySummary:
    """
    Get team availability summary.
    
    Features:
    - Team-wide availability overview
    - Daily availability breakdown
    - Coverage gap identification
    - Peak availability hours
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        summary = await calendar_use_case.get_team_availability_summary(
            business_id, start_date, end_date, current_user_id
        )
        
        return TeamAvailabilitySummary.model_validate(summary.__dict__)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get team availability summary: {str(e)}")


# Calendar Preferences Management
@router.post(
    "/users/{user_id}/calendar/preferences",
    response_model=CalendarPreferencesResponse,
    summary="Update calendar preferences",
    description="Update user calendar and scheduling preferences."
)
async def update_calendar_preferences(
    user_id: str,
    preferences: CalendarPreferences,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> CalendarPreferencesResponse:
    """
    Update calendar preferences.
    
    Features:
    - Timezone and format settings
    - Notification preferences
    - Scheduling behavior configuration
    - Availability preferences
    """
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        # Convert to DTO
        preferences_dto = CalendarPreferencesDTO(
            user_id=user_id,
            business_id=str(business_id),
            timezone=preferences.timezone,
            date_format=preferences.date_format,
            time_format=preferences.time_format,
            week_start_day=preferences.week_start_day,
            preferred_working_hours_template_id=preferences.preferred_working_hours_template_id,
            min_time_between_jobs_minutes=preferences.min_time_between_jobs_minutes,
            max_commute_time_minutes=preferences.max_commute_time_minutes,
            allows_back_to_back_jobs=preferences.allows_back_to_back_jobs,
            requires_prep_time_minutes=preferences.requires_prep_time_minutes,
            job_reminder_minutes_before=preferences.job_reminder_minutes_before,
            schedule_change_notifications=preferences.schedule_change_notifications,
            new_job_notifications=preferences.new_job_notifications,
            cancellation_notifications=preferences.cancellation_notifications,
            auto_accept_jobs_in_hours=preferences.auto_accept_jobs_in_hours,
            auto_decline_outside_hours=preferences.auto_decline_outside_hours,
            emergency_availability_outside_hours=preferences.emergency_availability_outside_hours,
            weekend_availability=preferences.weekend_availability,
            holiday_availability=preferences.holiday_availability,
            travel_buffer_percentage=preferences.travel_buffer_percentage,
            job_buffer_minutes=preferences.job_buffer_minutes
        )
        
        updated_prefs = await calendar_use_case.update_calendar_preferences(
            business_id, user_id, preferences_dto, current_user_id
        )
        
        return CalendarPreferencesResponse(
            message="Calendar preferences updated successfully",
            preferences=CalendarPreferences.model_validate(updated_prefs.__dict__)
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update calendar preferences: {str(e)}")


@router.get(
    "/users/{user_id}/calendar/preferences",
    response_model=CalendarPreferences,
    summary="Get calendar preferences",
    description="Get user calendar and scheduling preferences."
)
async def get_calendar_preferences(
    user_id: str,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    calendar_use_case: CalendarManagementUseCase = Depends(get_calendar_management_use_case)
) -> CalendarPreferences:
    """Get user calendar preferences."""
    try:
        business_id = business_context["business_id"]
        current_user_id = current_user.get("user_id")
        
        preferences = await calendar_use_case.get_calendar_preferences(
            business_id, user_id, current_user_id
        )
        
        if not preferences:
            raise HTTPException(status_code=404, detail="Calendar preferences not found")
        
        return CalendarPreferences.model_validate(preferences.__dict__)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get calendar preferences: {str(e)}")

# Note: Exception handlers would be added at the main app level, not router level
# These are commented out as APIRouter doesn't support exception_handler decorator
# They would be implemented in the main FastAPI app instance 