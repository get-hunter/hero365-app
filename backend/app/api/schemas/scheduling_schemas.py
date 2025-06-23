"""
Scheduling API Schemas

Pydantic schemas for intelligent scheduling API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, time, date
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
    performance_date: datetime = Field(..., description="Performance date")
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


# Calendar Management Enums
class RecurrenceType(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class TimeOffType(str, Enum):
    VACATION = "vacation"
    SICK_LEAVE = "sick_leave"
    PERSONAL = "personal"
    HOLIDAY = "holiday"
    TRAINING = "training"
    EMERGENCY = "emergency"
    UNPAID = "unpaid"


class CalendarEventType(str, Enum):
    WORK_SCHEDULE = "work_schedule"
    TIME_OFF = "time_off"
    BREAK = "break"
    MEETING = "meeting"
    TRAINING = "training"
    PERSONAL = "personal"


class TimeOffStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"


# Working Hours Management
class WorkingHoursTemplate(BaseModel):
    """Working hours template schema."""
    id: Optional[str] = Field(None, description="Template ID")
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    
    # Weekly schedule
    monday_start: Optional[time] = Field(None, description="Monday start time")
    monday_end: Optional[time] = Field(None, description="Monday end time")
    tuesday_start: Optional[time] = Field(None, description="Tuesday start time")
    tuesday_end: Optional[time] = Field(None, description="Tuesday end time")
    wednesday_start: Optional[time] = Field(None, description="Wednesday start time")
    wednesday_end: Optional[time] = Field(None, description="Wednesday end time")
    thursday_start: Optional[time] = Field(None, description="Thursday start time")
    thursday_end: Optional[time] = Field(None, description="Thursday end time")
    friday_start: Optional[time] = Field(None, description="Friday start time")
    friday_end: Optional[time] = Field(None, description="Friday end time")
    saturday_start: Optional[time] = Field(None, description="Saturday start time")
    saturday_end: Optional[time] = Field(None, description="Saturday end time")
    sunday_start: Optional[time] = Field(None, description="Sunday start time")
    sunday_end: Optional[time] = Field(None, description="Sunday end time")
    
    # Break configurations
    break_duration_minutes: int = Field(30, ge=0, le=120, description="Break duration in minutes")
    lunch_start_time: Optional[time] = Field(None, description="Lunch start time")
    lunch_duration_minutes: int = Field(60, ge=0, le=180, description="Lunch duration in minutes")
    
    # Flexibility settings
    allows_flexible_start: bool = Field(False, description="Allow flexible start time")
    flexible_start_window_minutes: int = Field(30, ge=0, le=120, description="Flexible start window")
    allows_overtime: bool = Field(False, description="Allow overtime")
    max_overtime_hours_per_day: float = Field(2.0, ge=0, le=8, description="Max overtime hours per day")
    
    total_weekly_hours: Optional[float] = Field(None, description="Total weekly hours (calculated)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Standard Business Hours",
                "description": "Monday to Friday, 9 AM to 5 PM",
                "monday_start": "09:00:00",
                "monday_end": "17:00:00",
                "tuesday_start": "09:00:00",
                "tuesday_end": "17:00:00",
                "wednesday_start": "09:00:00",
                "wednesday_end": "17:00:00",
                "thursday_start": "09:00:00",
                "thursday_end": "17:00:00",
                "friday_start": "09:00:00",
                "friday_end": "17:00:00",
                "break_duration_minutes": 30,
                "lunch_start_time": "12:00:00",
                "lunch_duration_minutes": 60,
                "allows_flexible_start": True,
                "flexible_start_window_minutes": 30
            }
        }


class CreateWorkingHoursTemplateRequest(BaseModel):
    """Request to create working hours template."""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    
    # Weekly schedule
    monday_start: Optional[time] = None
    monday_end: Optional[time] = None
    tuesday_start: Optional[time] = None
    tuesday_end: Optional[time] = None
    wednesday_start: Optional[time] = None
    wednesday_end: Optional[time] = None
    thursday_start: Optional[time] = None
    thursday_end: Optional[time] = None
    friday_start: Optional[time] = None
    friday_end: Optional[time] = None
    saturday_start: Optional[time] = None
    saturday_end: Optional[time] = None
    sunday_start: Optional[time] = None
    sunday_end: Optional[time] = None
    
    # Break configurations
    break_duration_minutes: int = Field(30, ge=0, le=120)
    lunch_start_time: Optional[time] = None
    lunch_duration_minutes: int = Field(60, ge=0, le=180)
    
    # Flexibility settings
    allows_flexible_start: bool = False
    flexible_start_window_minutes: int = Field(30, ge=0, le=120)
    allows_overtime: bool = False
    max_overtime_hours_per_day: float = Field(2.0, ge=0, le=8)


# Calendar Events
class CalendarEvent(BaseModel):
    """Calendar event schema."""
    id: Optional[str] = Field(None, description="Event ID")
    title: str = Field(..., min_length=1, max_length=200, description="Event title")
    description: Optional[str] = Field(None, max_length=1000, description="Event description")
    event_type: CalendarEventType = Field(CalendarEventType.WORK_SCHEDULE, description="Event type")
    
    start_datetime: datetime = Field(..., description="Event start time")
    end_datetime: datetime = Field(..., description="Event end time")
    is_all_day: bool = Field(False, description="All-day event")
    timezone: str = Field("UTC", description="Event timezone")
    
    # Recurrence
    recurrence_type: RecurrenceType = Field(RecurrenceType.NONE, description="Recurrence pattern")
    recurrence_end_date: Optional[date] = Field(None, description="Recurrence end date")
    recurrence_count: Optional[int] = Field(None, ge=1, le=365, description="Number of occurrences")
    recurrence_interval: int = Field(1, ge=1, le=30, description="Recurrence interval")
    recurrence_days_of_week: List[int] = Field(default_factory=list, description="Days of week (0=Monday)")
    
    # Scheduling impact
    blocks_scheduling: bool = Field(True, description="Blocks job scheduling")
    allows_emergency_override: bool = Field(False, description="Allow emergency override")
    
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    is_active: bool = True
    
    @validator('end_datetime')
    def validate_end_time(cls, v, values):
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('End time must be after start time')
        return v
    
    @validator('recurrence_days_of_week')
    def validate_days_of_week(cls, v):
        if v and any(day < 0 or day > 6 for day in v):
            raise ValueError('Days of week must be between 0 (Monday) and 6 (Sunday)')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Team Meeting",
                "description": "Weekly team standup meeting",
                "event_type": "meeting",
                "start_datetime": "2024-01-15T10:00:00Z",
                "end_datetime": "2024-01-15T11:00:00Z",
                "recurrence_type": "weekly",
                "recurrence_days_of_week": [0],  # Monday
                "blocks_scheduling": True
            }
        }


class CreateCalendarEventRequest(BaseModel):
    """Request to create calendar event."""
    title: str = Field(..., min_length=1, max_length=200, description="Event title")
    description: Optional[str] = Field(None, max_length=1000, description="Event description")
    event_type: CalendarEventType = Field(CalendarEventType.WORK_SCHEDULE, description="Event type")
    
    start_datetime: datetime = Field(..., description="Event start time")
    end_datetime: datetime = Field(..., description="Event end time")
    is_all_day: bool = Field(False, description="All-day event")
    timezone: str = Field("UTC", description="Event timezone")
    
    # Recurrence
    recurrence_type: RecurrenceType = Field(RecurrenceType.NONE, description="Recurrence pattern")
    recurrence_end_date: Optional[date] = Field(None, description="Recurrence end date")
    recurrence_count: Optional[int] = Field(None, ge=1, le=365, description="Number of occurrences")
    recurrence_interval: int = Field(1, ge=1, le=30, description="Recurrence interval")
    recurrence_days_of_week: List[int] = Field(default_factory=list, description="Days of week (0=Monday)")
    
    # Scheduling impact
    blocks_scheduling: bool = Field(True, description="Blocks job scheduling")
    allows_emergency_override: bool = Field(False, description="Allow emergency override")
    
    @validator('end_datetime')
    def validate_end_time(cls, v, values):
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('End time must be after start time')
        return v


# Time Off Management
class TimeOffRequest(BaseModel):
    """Time off request schema."""
    id: Optional[str] = Field(None, description="Request ID")
    time_off_type: TimeOffType = Field(..., description="Type of time off")
    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for time off")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    status: TimeOffStatus = Field(TimeOffStatus.PENDING, description="Request status")
    requested_by: Optional[str] = Field(None, description="User who requested")
    approved_by: Optional[str] = Field(None, description="User who approved/denied")
    approval_date: Optional[datetime] = Field(None, description="Approval/denial date")
    denial_reason: Optional[str] = Field(None, max_length=500, description="Reason for denial")
    
    affects_scheduling: bool = Field(True, description="Affects job scheduling")
    emergency_contact_allowed: bool = Field(False, description="Allow emergency contact")
    
    duration_days: Optional[int] = Field(None, description="Duration in days (calculated)")
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after or equal to start date')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "time_off_type": "vacation",
                "start_date": "2024-02-15",
                "end_date": "2024-02-19",
                "reason": "Family vacation",
                "affects_scheduling": True,
                "emergency_contact_allowed": False
            }
        }


class CreateTimeOffRequest(BaseModel):
    """Request to create time off."""
    time_off_type: TimeOffType = Field(..., description="Type of time off")
    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for time off")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    affects_scheduling: bool = Field(True, description="Affects job scheduling")
    emergency_contact_allowed: bool = Field(False, description="Allow emergency contact")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after or equal to start date')
        return v


class ApproveTimeOffRequest(BaseModel):
    """Request to approve/deny time off."""
    status: TimeOffStatus = Field(..., description="New status (approved/denied)")
    denial_reason: Optional[str] = Field(None, max_length=500, description="Reason for denial")
    
    @validator('denial_reason')
    def validate_denial_reason(cls, v, values):
        if values.get('status') == TimeOffStatus.DENIED and not v:
            raise ValueError('Denial reason is required when denying time off')
        return v


# Calendar Preferences
class CalendarPreferences(BaseModel):
    """Calendar preferences schema."""
    timezone: str = Field("UTC", description="User timezone")
    date_format: str = Field("YYYY-MM-DD", description="Preferred date format")
    time_format: str = Field("24h", description="Time format (12h/24h)")
    week_start_day: int = Field(0, ge=0, le=6, description="Week start day (0=Monday)")
    
    # Scheduling preferences
    preferred_working_hours_template_id: Optional[str] = Field(None, description="Preferred template ID")
    min_time_between_jobs_minutes: int = Field(30, ge=0, le=240, description="Min time between jobs")
    max_commute_time_minutes: int = Field(60, ge=0, le=240, description="Max commute time")
    allows_back_to_back_jobs: bool = Field(False, description="Allow back-to-back jobs")
    requires_prep_time_minutes: int = Field(15, ge=0, le=60, description="Required prep time")
    
    # Notification preferences
    job_reminder_minutes_before: List[int] = Field(default_factory=lambda: [60, 15], description="Reminder times")
    schedule_change_notifications: bool = Field(True, description="Schedule change notifications")
    new_job_notifications: bool = Field(True, description="New job notifications")
    cancellation_notifications: bool = Field(True, description="Cancellation notifications")
    
    # Availability preferences
    auto_accept_jobs_in_hours: bool = Field(False, description="Auto-accept jobs during working hours")
    auto_decline_outside_hours: bool = Field(True, description="Auto-decline jobs outside hours")
    emergency_availability_outside_hours: bool = Field(False, description="Emergency availability")
    weekend_availability: bool = Field(False, description="Weekend availability")
    holiday_availability: bool = Field(False, description="Holiday availability")
    
    # Buffer times
    travel_buffer_percentage: float = Field(1.2, ge=1.0, le=3.0, description="Travel time buffer")
    job_buffer_minutes: int = Field(15, ge=0, le=60, description="Job buffer time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timezone": "America/New_York",
                "time_format": "12h",
                "min_time_between_jobs_minutes": 30,
                "max_commute_time_minutes": 45,
                "job_reminder_minutes_before": [60, 15],
                "auto_decline_outside_hours": True,
                "weekend_availability": False,
                "travel_buffer_percentage": 1.2
            }
        }


# Availability Management
class UserAvailability(BaseModel):
    """User availability information."""
    user_id: str = Field(..., description="User ID")
    availability_date: date = Field(..., description="Date")
    available_slots: List[Dict[str, datetime]] = Field(default_factory=list, description="Available time slots")
    total_available_hours: float = Field(0.0, ge=0, description="Total available hours")
    working_hours: Optional[Dict[str, time]] = Field(None, description="Working hours for the day")
    time_off: List["TimeOffRequest"] = Field(default_factory=list, description="Time off on this date")
    calendar_events: List["CalendarEvent"] = Field(default_factory=list, description="Calendar events")
    is_available: bool = Field(True, description="Overall availability")
    unavailable_reason: Optional[str] = Field(None, description="Reason if unavailable")


class AvailabilityCheckRequest(BaseModel):
    """Request to check user availability."""
    user_ids: List[str] = Field(..., min_items=1, description="User IDs to check")
    start_datetime: datetime = Field(..., description="Start of time period")
    end_datetime: datetime = Field(..., description="End of time period")
    include_time_off: bool = Field(True, description="Include time off information")
    include_calendar_events: bool = Field(True, description="Include calendar events")
    include_working_hours: bool = Field(True, description="Include working hours")
    
    @validator('end_datetime')
    def validate_end_datetime(cls, v, values):
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('End datetime must be after start datetime')
        return v


class AvailabilityCheckResponse(BaseModel):
    """Response for availability check."""
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    check_datetime: datetime = Field(..., description="When the check was performed")
    user_availability: List[UserAvailability] = Field(..., description="User availability details")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Summary information")


class TeamAvailabilitySummary(BaseModel):
    """Team availability summary."""
    business_id: str = Field(..., description="Business ID")
    start_date: date = Field(..., description="Period start date")
    end_date: date = Field(..., description="Period end date")
    total_team_members: int = Field(0, ge=0, description="Total team members")
    available_members: int = Field(0, ge=0, description="Available members")
    members_on_time_off: int = Field(0, ge=0, description="Members on time off")
    members_with_limited_availability: int = Field(0, ge=0, description="Members with limited availability")
    daily_availability: List[Dict[str, Any]] = Field(default_factory=list, description="Daily breakdown")
    member_summaries: List[UserAvailability] = Field(default_factory=list, description="Individual summaries")
    peak_availability_hours: List[Dict[str, Any]] = Field(default_factory=list, description="Peak hours")
    coverage_gaps: List[Dict[str, Any]] = Field(default_factory=list, description="Coverage gaps")


# Set User Working Hours Request
class SetUserWorkingHoursRequest(BaseModel):
    """Request to set user working hours."""
    template_id: Optional[str] = Field(None, description="Use existing template")
    
    # Or specify custom hours
    monday_start: Optional[time] = None
    monday_end: Optional[time] = None
    tuesday_start: Optional[time] = None
    tuesday_end: Optional[time] = None
    wednesday_start: Optional[time] = None
    wednesday_end: Optional[time] = None
    thursday_start: Optional[time] = None
    thursday_end: Optional[time] = None
    friday_start: Optional[time] = None
    friday_end: Optional[time] = None
    saturday_start: Optional[time] = None
    saturday_end: Optional[time] = None
    sunday_start: Optional[time] = None
    sunday_end: Optional[time] = None
    
    break_duration_minutes: int = Field(30, ge=0, le=120)
    lunch_start_time: Optional[time] = None
    lunch_duration_minutes: int = Field(60, ge=0, le=180)


# Response schemas
class WorkingHoursResponse(BaseModel):
    """Working hours response."""
    message: str = Field(..., description="Response message")
    template: Optional["WorkingHoursTemplate"] = Field(None, description="Working hours template")


class CalendarEventResponse(BaseModel):
    """Calendar event response."""
    message: str = Field(..., description="Response message")
    event: Optional["CalendarEvent"] = Field(None, description="Calendar event")


class TimeOffResponse(BaseModel):
    """Time off response."""
    message: str = Field(..., description="Response message")
    time_off_request: Optional["TimeOffRequest"] = Field(None, description="Time off request")


class CalendarPreferencesResponse(BaseModel):
    """Calendar preferences response."""
    message: str = Field(..., description="Response message")
    preferences: Optional["CalendarPreferences"] = Field(None, description="Calendar preferences") 