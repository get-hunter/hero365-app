"""
Intelligent Scheduling API Routes

FastAPI routes for intelligent job scheduling operations with real-time optimization.
Handles schedule optimization, real-time adaptation, and analytics endpoints.
"""

import uuid
import logging
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.responses import JSONResponse

from ..deps import get_current_user, get_business_context
from ..schemas.scheduling_schemas import (
    SchedulingOptimizationRequest, SchedulingOptimizationResponse,
    RealTimeAdaptationRequest, RealTimeAdaptationResponse,
    SchedulingAnalyticsRequest, SchedulingAnalyticsResponse,
    RealTimeScheduleStatusResponse, LocationUpdateRequest,
    SchedulingErrorResponse
)
from ...application.use_cases.scheduling.intelligent_scheduling_use_case import IntelligentSchedulingUseCase
from ...application.dto.scheduling_dto import (
    SchedulingOptimizationRequestDTO, RealTimeAdaptationRequestDTO,
    SchedulingAnalyticsRequestDTO, TimeWindowDTO, LocationUpdateDTO
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, BusinessLogicError
)
from ...infrastructure.config.dependency_injection import get_intelligent_scheduling_use_case

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


# Background task functions
async def _update_optimization_analytics(business_id: uuid.UUID, optimization_id: str):
    """Background task to update optimization analytics."""
    try:
        # Implementation would update analytics in background
        pass
    except Exception as e:
        logger.error(f"Failed to update optimization analytics: {str(e)}")


# Note: Exception handlers would be added at the main app level, not router level
# These are commented out as APIRouter doesn't support exception_handler decorator
# They would be implemented in the main FastAPI app instance 