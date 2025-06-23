"""
Scheduling API Schemas

Pydantic schemas for intelligent scheduling API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, time
from decimal import Decimal
from enum import Enum


class OptimizationAlgorithm(str, Enum):
    """Available optimization algorithms."""
    INTELLIGENT = "intelligent"
    GENETIC = "genetic"
    LOCAL_SEARCH = "local_search"
    GREEDY = "greedy"


class DisruptionType(str, Enum):
    """Types of schedule disruptions."""
    TRAFFIC_DELAY = "traffic_delay"
    WEATHER = "weather"
    EMERGENCY_JOB = "emergency_job"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    CUSTOMER_RESCHEDULE = "customer_reschedule"
    EQUIPMENT_FAILURE = "equipment_failure"


class DisruptionSeverity(str, Enum):
    """Severity levels for disruptions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Request Schemas

class SchedulingConstraints(BaseModel):
    """Scheduling constraints configuration."""
    max_travel_time_minutes: Optional[int] = Field(None, ge=1, le=480, description="Maximum travel time per job")
    working_hours_start: Optional[time] = Field(None, description="Working hours start time")
    working_hours_end: Optional[time] = Field(None, description="Working hours end time")
    max_jobs_per_user: Optional[int] = Field(None, ge=1, le=20, description="Maximum jobs per user per day")
    require_skill_match: bool = Field(True, description="Require exact skill matching")
    allow_overtime: bool = Field(False, description="Allow overtime scheduling")
    optimization_objectives: List[str] = Field(
        default=["minimize_travel_time", "maximize_utilization"],
        description="Optimization objectives in priority order"
    )

    @validator('working_hours_end')
    def validate_working_hours(cls, v, values):
        if v and 'working_hours_start' in values and values['working_hours_start']:
            if v <= values['working_hours_start']:
                raise ValueError('Working hours end must be after start time')
        return v


class TimeWindow(BaseModel):
    """Time window specification."""
    start_time: datetime = Field(..., description="Window start time")
    end_time: datetime = Field(..., description="Window end time")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v


class SchedulingOptimizationRequest(BaseModel):
    """Request for schedule optimization."""
    job_ids: Optional[List[str]] = Field(None, description="Specific job IDs to optimize (null for all unscheduled)")
    time_window: Optional[TimeWindow] = Field(None, description="Time window for optimization")
    constraints: SchedulingConstraints = Field(default_factory=SchedulingConstraints, description="Optimization constraints")
    baseline_metrics: Optional[Dict[str, Any]] = Field(None, description="Baseline metrics for comparison")
    notify_users: bool = Field(True, description="Send notifications to assigned users")
    optimization_algorithm: OptimizationAlgorithm = Field(OptimizationAlgorithm.INTELLIGENT, description="Algorithm to use")
    update_analytics: bool = Field(True, description="Update analytics after optimization")

    class Config:
        json_schema_extra = {
            "example": {
                "job_ids": ["job_123", "job_456"],
                "time_window": {
                    "start_time": "2024-01-15T08:00:00Z",
                    "end_time": "2024-01-15T18:00:00Z"
                },
                "constraints": {
                    "max_travel_time_minutes": 60,
                    "working_hours_start": "08:00:00",
                    "working_hours_end": "17:00:00",
                    "max_jobs_per_user": 8,
                    "require_skill_match": True,
                    "allow_overtime": False,
                    "optimization_objectives": ["minimize_travel_time", "maximize_utilization"]
                },
                "notify_users": True,
                "optimization_algorithm": "intelligent"
            }
        }


class Disruption(BaseModel):
    """Schedule disruption information."""
    type: DisruptionType = Field(..., description="Type of disruption")
    affected_job_ids: List[str] = Field(..., description="Job IDs affected by disruption")
    affected_user_ids: List[str] = Field(default_factory=list, description="User IDs affected by disruption")
    severity: DisruptionSeverity = Field(..., description="Severity of disruption")
    expected_duration_minutes: Optional[int] = Field(None, ge=0, le=1440, description="Expected duration in minutes")
    location: Optional[Dict[str, float]] = Field(None, description="Location coordinates (lat, lng)")
    description: Optional[str] = Field(None, max_length=500, description="Disruption description")

    @validator('location')
    def validate_location(cls, v):
        if v is not None:
            if 'latitude' not in v or 'longitude' not in v:
                raise ValueError('Location must contain latitude and longitude')
            if not (-90 <= v['latitude'] <= 90):
                raise ValueError('Latitude must be between -90 and 90')
            if not (-180 <= v['longitude'] <= 180):
                raise ValueError('Longitude must be between -180 and 180')
        return v


class AdaptationPreferences(BaseModel):
    """Schedule adaptation preferences."""
    allow_overtime: bool = Field(False, description="Allow overtime to handle disruption")
    max_schedule_delay_minutes: int = Field(60, ge=0, le=480, description="Maximum acceptable delay")
    notify_customers: bool = Field(True, description="Send notifications to customers")
    notify_technicians: bool = Field(True, description="Send notifications to technicians")
    prefer_same_technician: bool = Field(True, description="Prefer keeping same technician when possible")
    max_reassignments: int = Field(5, ge=1, le=20, description="Maximum number of job reassignments")


class RealTimeAdaptationRequest(BaseModel):
    """Request for real-time schedule adaptation."""
    disruption: Disruption = Field(..., description="Disruption information")
    adaptation_preferences: AdaptationPreferences = Field(
        default_factory=AdaptationPreferences,
        description="Adaptation preferences"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "disruption": {
                    "type": "traffic_delay",
                    "affected_job_ids": ["job_123"],
                    "affected_user_ids": ["user_456"],
                    "severity": "medium",
                    "expected_duration_minutes": 45,
                    "location": {"latitude": 40.7128, "longitude": -74.0060},
                    "description": "Heavy traffic on I-95 causing delays"
                },
                "adaptation_preferences": {
                    "allow_overtime": False,
                    "max_schedule_delay_minutes": 60,
                    "notify_customers": True,
                    "notify_technicians": True,
                    "prefer_same_technician": True,
                    "max_reassignments": 3
                }
            }
        }


class LocationData(BaseModel):
    """Location data for tracking."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    accuracy_meters: int = Field(..., ge=1, le=10000, description="Location accuracy in meters")
    timestamp: datetime = Field(..., description="Location timestamp")


class LocationUpdateRequest(BaseModel):
    """Request to update user location."""
    user_id: str = Field(..., description="User ID")
    location: LocationData = Field(..., description="Location data")
    status: str = Field(..., description="User status")

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["available", "traveling", "on_job", "break", "unavailable"]
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


# Response Schemas

class OptimizedJobAssignment(BaseModel):
    """Optimized job assignment result."""
    job_id: str = Field(..., description="Job ID")
    assigned_user_id: Optional[str] = Field(None, description="Assigned user ID")
    scheduled_start: Optional[datetime] = Field(None, description="Scheduled start time")
    scheduled_end: Optional[datetime] = Field(None, description="Scheduled end time")
    estimated_travel_time_minutes: Decimal = Field(..., description="Estimated travel time")
    confidence_score: Decimal = Field(..., ge=0, le=1, description="Assignment confidence score")
    alternative_candidates: List[str] = Field(default_factory=list, description="Alternative candidate user IDs")
    optimization_notes: Optional[str] = Field(None, description="Optimization notes")


class OptimizationMetrics(BaseModel):
    """Optimization performance metrics."""
    total_jobs: int = Field(..., ge=0, description="Total jobs processed")
    successfully_scheduled: int = Field(..., ge=0, description="Successfully scheduled jobs")
    scheduling_success_rate: Decimal = Field(..., ge=0, le=1, description="Scheduling success rate")
    total_travel_time_minutes: Decimal = Field(..., ge=0, description="Total travel time")
    average_travel_time_per_job: Decimal = Field(..., ge=0, description="Average travel time per job")
    average_confidence_score: Decimal = Field(..., ge=0, le=1, description="Average confidence score")
    travel_time_savings_percent: Optional[Decimal] = Field(None, description="Travel time savings percentage")
    utilization_improvement_percent: Optional[Decimal] = Field(None, description="Utilization improvement percentage")
    optimization_timestamp: datetime = Field(..., description="Optimization timestamp")


class SchedulingOptimizationResponse(BaseModel):
    """Response for schedule optimization."""
    optimization_id: str = Field(..., description="Optimization ID")
    optimized_assignments: List[OptimizedJobAssignment] = Field(..., description="Optimized job assignments")
    optimization_metrics: OptimizationMetrics = Field(..., description="Optimization metrics")
    success: bool = Field(..., description="Optimization success status")
    message: str = Field(..., description="Response message")
    warnings: List[str] = Field(default_factory=list, description="Optimization warnings")


class AdaptedJob(BaseModel):
    """Adapted job information."""
    job_id: str = Field(..., description="Job ID")
    original_schedule: Dict[str, Any] = Field(..., description="Original schedule")
    new_schedule: Dict[str, Any] = Field(..., description="New schedule")
    adaptation_reason: str = Field(..., description="Reason for adaptation")
    impact_score: Decimal = Field(..., ge=0, le=1, description="Impact score")


class AdaptationImpactSummary(BaseModel):
    """Adaptation impact summary."""
    jobs_rescheduled: int = Field(..., ge=0, description="Number of jobs rescheduled")
    users_affected: int = Field(..., ge=0, description="Number of users affected")
    customer_notifications_sent: int = Field(..., ge=0, description="Customer notifications sent")
    total_delay_minutes: int = Field(..., ge=0, description="Total delay in minutes")
    adaptation_success_rate: Decimal = Field(..., ge=0, le=1, description="Adaptation success rate")


class RealTimeAdaptationResponse(BaseModel):
    """Response for real-time adaptation."""
    adaptation_id: str = Field(..., description="Adaptation ID")
    status: str = Field(..., description="Adaptation status")
    adapted_assignments: List[AdaptedJob] = Field(..., description="Adapted job assignments")
    impact_summary: AdaptationImpactSummary = Field(..., description="Impact summary")
    notifications_sent: List[str] = Field(..., description="Notifications sent")
    message: str = Field(..., description="Response message")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class SchedulingKPIs(BaseModel):
    """Scheduling key performance indicators."""
    average_jobs_per_technician_per_day: Decimal = Field(..., description="Average jobs per technician per day")
    average_travel_time_per_job_minutes: Decimal = Field(..., description="Average travel time per job")
    first_time_fix_rate_percent: Decimal = Field(..., description="First time fix rate percentage")
    resource_utilization_rate_percent: Decimal = Field(..., description="Resource utilization rate")
    schedule_adherence_rate_percent: Decimal = Field(..., description="Schedule adherence rate")
    customer_satisfaction_score: Optional[Decimal] = Field(None, description="Customer satisfaction score")
    on_time_completion_rate_percent: Decimal = Field(..., description="On-time completion rate")
    emergency_response_time_minutes: Optional[Decimal] = Field(None, description="Emergency response time")


class ImprovementRecommendation(BaseModel):
    """Improvement recommendation."""
    type: str = Field(..., description="Recommendation type")
    description: str = Field(..., description="Recommendation description")
    priority: str = Field(..., description="Priority level")
    expected_impact: str = Field(..., description="Expected impact")
    implementation_effort: str = Field(..., description="Implementation effort")
    estimated_roi_percent: Optional[Decimal] = Field(None, description="Estimated ROI percentage")


class PredictiveInsight(BaseModel):
    """Predictive scheduling insight."""
    prediction_type: str = Field(..., description="Prediction type")
    forecast_date: datetime = Field(..., description="Forecast date")
    prediction_confidence: Decimal = Field(..., ge=0, le=1, description="Prediction confidence")
    impact_description: str = Field(..., description="Impact description")
    recommended_actions: List[str] = Field(..., description="Recommended actions")


class TrendAnalysis(BaseModel):
    """Trend analysis data."""
    metric_name: str = Field(..., description="Metric name")
    trend_direction: str = Field(..., description="Trend direction")
    change_percent: Decimal = Field(..., description="Change percentage")
    time_period_days: int = Field(..., description="Time period in days")
    significance_level: str = Field(..., description="Significance level")


class SchedulingAnalyticsResponse(BaseModel):
    """Response for scheduling analytics."""
    period: TimeWindow = Field(..., description="Analytics period")
    kpis: SchedulingKPIs = Field(..., description="Key performance indicators")
    recommendations: List[ImprovementRecommendation] = Field(..., description="Improvement recommendations")
    predictions: List[PredictiveInsight] = Field(..., description="Predictive insights")
    trend_analysis: List[TrendAnalysis] = Field(..., description="Trend analysis")
    data_quality_score: Decimal = Field(default=Decimal("1.0"), description="Data quality score")


class RealTimeJobStatus(BaseModel):
    """Real-time job status."""
    job_id: str = Field(..., description="Job ID")
    assigned_user_id: str = Field(..., description="Assigned user ID")
    status: str = Field(..., description="Current status")
    scheduled_start: datetime = Field(..., description="Scheduled start time")
    actual_start: Optional[datetime] = Field(None, description="Actual start time")
    estimated_completion: datetime = Field(..., description="Estimated completion time")
    current_location: Optional[Dict[str, float]] = Field(None, description="Current location")
    delay_minutes: int = Field(..., description="Delay in minutes")
    alerts: List[str] = Field(default_factory=list, description="Active alerts")


class DailyPerformance(BaseModel):
    """Daily performance metrics."""
    date: datetime = Field(..., description="Performance date")
    jobs_completed: int = Field(..., ge=0, description="Jobs completed")
    jobs_in_progress: int = Field(..., ge=0, description="Jobs in progress")
    jobs_delayed: int = Field(..., ge=0, description="Jobs delayed")
    average_delay_minutes: Decimal = Field(..., ge=0, description="Average delay in minutes")
    on_time_percentage: Decimal = Field(..., ge=0, le=100, description="On-time percentage")
    total_travel_time_minutes: Decimal = Field(..., ge=0, description="Total travel time")
    utilization_rate_percent: Decimal = Field(..., ge=0, le=100, description="Utilization rate")


class RealTimeScheduleStatusResponse(BaseModel):
    """Response for real-time schedule status."""
    current_time: datetime = Field(..., description="Current timestamp")
    active_jobs: List[RealTimeJobStatus] = Field(..., description="Active job statuses")
    daily_performance: DailyPerformance = Field(..., description="Daily performance metrics")
    alerts: List[str] = Field(default_factory=list, description="System alerts")
    system_health: str = Field(..., description="System health status")


class SchedulingErrorResponse(BaseModel):
    """Error response for scheduling operations."""
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Error details")
    timestamp: datetime = Field(..., description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid scheduling constraints",
                "details": {
                    "field_errors": [
                        {"field": "max_travel_time_minutes", "error": "Must be between 1 and 480"}
                    ]
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


# Additional utility schemas

class SchedulingAnalyticsRequest(BaseModel):
    """Request for scheduling analytics (used internally)."""
    period: TimeWindow = Field(..., description="Analytics period")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    job_type: Optional[str] = Field(None, description="Filter by job type")
    include_predictions: bool = Field(True, description="Include predictions")
    include_recommendations: bool = Field(True, description="Include recommendations")


class AvailableTimeSlotRequest(BaseModel):
    """Request for available time slots."""
    job_type: str = Field(..., description="Type of job/service")
    estimated_duration_hours: float = Field(..., ge=0.5, le=8, description="Estimated job duration in hours")
    required_skills: List[str] = Field(default_factory=list, description="Required skills for the job")
    job_address: Optional[Dict[str, Any]] = Field(None, description="Job location details")
    preferred_date_range: TimeWindow = Field(..., description="Customer's preferred date range")
    customer_preferences: Optional[Dict[str, Any]] = Field(None, description="Customer scheduling preferences")
    priority: str = Field("medium", description="Job priority level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_type": "plumbing_repair",
                "estimated_duration_hours": 2.0,
                "required_skills": ["plumbing", "pipe_repair"],
                "job_address": {
                    "street_address": "123 Main St",
                    "city": "Boston",
                    "state": "MA",
                    "latitude": 42.3601,
                    "longitude": -71.0589
                },
                "preferred_date_range": {
                    "start_time": "2024-01-15T08:00:00Z",
                    "end_time": "2024-01-17T18:00:00Z"
                },
                "customer_preferences": {
                    "avoid_early_morning": True,
                    "preferred_technician": "tech_123",
                    "allow_weekend": False
                },
                "priority": "high"
            }
        }


class TimeSlot(BaseModel):
    """Individual time slot option."""
    slot_id: str = Field(..., description="Unique slot identifier")
    start_time: datetime = Field(..., description="Slot start time")
    end_time: datetime = Field(..., description="Slot end time")
    available_technicians: List[Dict[str, Any]] = Field(..., description="Available technicians for this slot")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in slot availability")
    estimated_travel_time_minutes: int = Field(..., ge=0, description="Estimated travel time to location")
    pricing_info: Optional[Dict[str, Any]] = Field(None, description="Pricing information for this slot")
    weather_impact: Optional[Dict[str, Any]] = Field(None, description="Weather conditions impact")
    slot_quality_score: float = Field(..., ge=0, le=1, description="Overall slot quality score")
    notes: Optional[str] = Field(None, description="Additional notes about this slot")


class AvailableTimeSlotsResponse(BaseModel):
    """Response with available time slots."""
    request_id: str = Field(..., description="Unique request identifier")
    available_slots: List[TimeSlot] = Field(..., description="List of available time slots")
    total_slots_found: int = Field(..., ge=0, description="Total number of slots found")
    search_criteria: Dict[str, Any] = Field(..., description="Applied search criteria")
    recommendations: List[str] = Field(default_factory=list, description="Scheduling recommendations")
    alternative_suggestions: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative options")
    booking_deadline: Optional[datetime] = Field(None, description="Deadline to book these slots")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_789",
                "available_slots": [
                    {
                        "slot_id": "slot_001",
                        "start_time": "2024-01-15T09:00:00Z",
                        "end_time": "2024-01-15T11:00:00Z",
                        "available_technicians": [
                            {
                                "technician_id": "tech_123",
                                "name": "John Smith",
                                "rating": 4.8,
                                "specialties": ["plumbing", "pipe_repair"]
                            }
                        ],
                        "confidence_score": 0.95,
                        "estimated_travel_time_minutes": 25,
                        "pricing_info": {
                            "base_rate": 120.00,
                            "travel_fee": 15.00,
                            "total_estimate": 135.00
                        },
                        "weather_impact": {
                            "conditions": "clear",
                            "impact_score": 0.9
                        },
                        "slot_quality_score": 0.92,
                        "notes": "Optimal slot with experienced technician"
                    }
                ],
                "total_slots_found": 5,
                "search_criteria": {
                    "job_type": "plumbing_repair",
                    "duration_hours": 2.0,
                    "date_range": "2024-01-15 to 2024-01-17"
                },
                "recommendations": [
                    "Morning slots have higher availability",
                    "Tuesday has the most experienced technicians available"
                ],
                "alternative_suggestions": [
                    {
                        "type": "extend_date_range",
                        "description": "Extend search to next week for 15 more options"
                    }
                ],
                "booking_deadline": "2024-01-14T18:00:00Z"
            }
        }


class TimeSlotBookingRequest(BaseModel):
    """Request to book a specific time slot."""
    slot_id: str = Field(..., description="Selected time slot ID")
    customer_contact: Dict[str, Any] = Field(..., description="Customer contact information")
    job_details: Dict[str, Any] = Field(..., description="Detailed job information")
    special_instructions: Optional[str] = Field(None, description="Special instructions for technician")
    confirm_booking: bool = Field(True, description="Confirm the booking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "slot_id": "slot_001",
                "customer_contact": {
                    "name": "Jane Doe",
                    "phone": "+1234567890",
                    "email": "jane@example.com"
                },
                "job_details": {
                    "description": "Kitchen sink pipe leak repair",
                    "urgency_level": "medium",
                    "access_instructions": "Use side entrance"
                },
                "special_instructions": "Please call 30 minutes before arrival",
                "confirm_booking": True
            }
        }


class TimeSlotBookingResponse(BaseModel):
    """Response for time slot booking."""
    booking_id: str = Field(..., description="Unique booking identifier")
    job_id: str = Field(..., description="Created job ID")
    status: str = Field(..., description="Booking status")
    scheduled_slot: TimeSlot = Field(..., description="Confirmed time slot details")
    assigned_technician: Dict[str, Any] = Field(..., description="Assigned technician information")
    confirmation_details: Dict[str, Any] = Field(..., description="Booking confirmation details")
    next_steps: List[str] = Field(..., description="Next steps for customer")
    cancellation_policy: str = Field(..., description="Cancellation policy information") 