"""
Scheduling DTOs

Data Transfer Objects for intelligent scheduling operations.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, time
from decimal import Decimal


@dataclass
class SchedulingConstraintsDTO:
    """DTO for scheduling constraints."""
    max_travel_time_minutes: Optional[int] = None
    working_hours_start: Optional[time] = None
    working_hours_end: Optional[time] = None
    max_jobs_per_user: Optional[int] = None
    require_skill_match: bool = True
    allow_overtime: bool = False
    optimization_objectives: List[str] = field(default_factory=lambda: ["minimize_travel_time", "maximize_utilization"])


@dataclass
class TimeWindowDTO:
    """DTO for time window specification."""
    start_time: datetime
    end_time: datetime


@dataclass
class SchedulingOptimizationRequestDTO:
    """DTO for schedule optimization request."""
    job_ids: Optional[List[str]] = None  # If None, optimize all unscheduled jobs
    time_window: Optional[TimeWindowDTO] = None
    constraints: SchedulingConstraintsDTO = field(default_factory=SchedulingConstraintsDTO)
    baseline_metrics: Optional[Dict[str, Any]] = None
    notify_users: bool = True
    optimization_algorithm: str = "intelligent"  # intelligent, genetic, local_search


@dataclass
class OptimizedJobAssignmentDTO:
    """DTO for optimized job assignment result."""
    job_id: str
    assigned_user_id: Optional[str]
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    estimated_travel_time_minutes: Decimal
    confidence_score: Decimal
    alternative_candidates: List[str]
    optimization_notes: Optional[str]


@dataclass
class OptimizationMetricsDTO:
    """DTO for optimization performance metrics."""
    total_jobs: int
    successfully_scheduled: int
    scheduling_success_rate: Decimal
    total_travel_time_minutes: Decimal
    average_travel_time_per_job: Decimal
    average_confidence_score: Decimal
    travel_time_savings_percent: Optional[Decimal] = None
    utilization_improvement_percent: Optional[Decimal] = None
    optimization_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SchedulingOptimizationResponseDTO:
    """DTO for schedule optimization response."""
    optimization_id: str
    optimized_assignments: List[OptimizedJobAssignmentDTO]
    optimization_metrics: OptimizationMetricsDTO
    success: bool
    message: str
    warnings: List[str] = field(default_factory=list)


@dataclass
class DisruptionDTO:
    """DTO for schedule disruption information."""
    type: str  # traffic_delay, weather, emergency_job, resource_unavailable, customer_reschedule
    affected_job_ids: List[str]
    affected_user_ids: List[str]
    severity: str  # low, medium, high, critical
    expected_duration_minutes: Optional[int]
    location: Optional[Dict[str, float]]  # latitude, longitude
    description: Optional[str]


@dataclass
class AdaptationPreferencesDTO:
    """DTO for schedule adaptation preferences."""
    allow_overtime: bool = False
    max_schedule_delay_minutes: int = 60
    notify_customers: bool = True
    notify_technicians: bool = True
    prefer_same_technician: bool = True
    max_reassignments: int = 5


@dataclass
class RealTimeAdaptationRequestDTO:
    """DTO for real-time schedule adaptation request."""
    disruption: DisruptionDTO
    adaptation_preferences: AdaptationPreferencesDTO = field(default_factory=AdaptationPreferencesDTO)


@dataclass
class AdaptedJobDTO:
    """DTO for adapted job information."""
    job_id: str
    original_schedule: Dict[str, Any]  # start, end, assigned_user
    new_schedule: Dict[str, Any]  # start, end, assigned_user
    adaptation_reason: str
    impact_score: Decimal


@dataclass
class AdaptationImpactSummaryDTO:
    """DTO for adaptation impact summary."""
    jobs_rescheduled: int
    users_affected: int
    customer_notifications_sent: int
    total_delay_minutes: int
    adaptation_success_rate: Decimal


@dataclass
class RealTimeAdaptationResponseDTO:
    """DTO for real-time adaptation response."""
    adaptation_id: str
    status: str  # success, partial, failed
    adapted_assignments: List[AdaptedJobDTO]
    impact_summary: AdaptationImpactSummaryDTO
    notifications_sent: List[str]
    message: str
    recommendations: List[str] = field(default_factory=list)


@dataclass
class SchedulingAnalyticsRequestDTO:
    """DTO for scheduling analytics request."""
    period: TimeWindowDTO
    user_id: Optional[str] = None
    job_type: Optional[str] = None
    include_predictions: bool = True
    include_recommendations: bool = True


@dataclass
class SchedulingKPIsDTO:
    """DTO for scheduling key performance indicators."""
    average_jobs_per_technician_per_day: Decimal
    average_travel_time_per_job_minutes: Decimal
    first_time_fix_rate_percent: Decimal
    resource_utilization_rate_percent: Decimal
    schedule_adherence_rate_percent: Decimal
    customer_satisfaction_score: Optional[Decimal]
    on_time_completion_rate_percent: Decimal
    emergency_response_time_minutes: Optional[Decimal]


@dataclass
class ImprovementRecommendationDTO:
    """DTO for improvement recommendation."""
    type: str  # skill_training, capacity_adjustment, schedule_optimization, route_optimization
    description: str
    priority: str  # low, medium, high
    expected_impact: str
    implementation_effort: str  # low, medium, high
    estimated_roi_percent: Optional[Decimal]


@dataclass
class PredictiveInsightDTO:
    """DTO for predictive scheduling insight."""
    prediction_type: str  # demand_forecast, capacity_shortage, weather_impact
    forecast_date: datetime
    prediction_confidence: Decimal
    impact_description: str
    recommended_actions: List[str]


@dataclass
class TrendAnalysisDTO:
    """DTO for trend analysis."""
    metric_name: str
    trend_direction: str  # improving, declining, stable
    change_percent: Decimal
    time_period_days: int
    significance_level: str  # low, medium, high


@dataclass
class SchedulingAnalyticsResponseDTO:
    """DTO for scheduling analytics response."""
    period: TimeWindowDTO
    kpis: SchedulingKPIsDTO
    recommendations: List[ImprovementRecommendationDTO]
    predictions: List[PredictiveInsightDTO]
    trend_analysis: List[TrendAnalysisDTO]
    data_quality_score: Decimal = field(default=Decimal("1.0"))


@dataclass
class RealTimeStatusDTO:
    """DTO for real-time job status."""
    job_id: str
    assigned_user_id: str
    status: str  # scheduled, in_progress, delayed, completed
    scheduled_start: datetime
    actual_start: Optional[datetime]
    estimated_completion: datetime
    current_location: Optional[Dict[str, float]]
    delay_minutes: int
    alerts: List[str]


@dataclass
class DailyPerformanceDTO:
    """DTO for daily performance metrics."""
    date: datetime
    jobs_completed: int
    jobs_in_progress: int
    jobs_delayed: int
    average_delay_minutes: Decimal
    on_time_percentage: Decimal
    total_travel_time_minutes: Decimal
    utilization_rate_percent: Decimal


@dataclass
class RealTimeScheduleStatusResponseDTO:
    """DTO for real-time schedule status response."""
    current_time: datetime
    active_jobs: List[RealTimeStatusDTO]
    daily_performance: DailyPerformanceDTO
    alerts: List[str]
    system_health: str  # healthy, warning, critical


@dataclass
class LocationUpdateDTO:
    """DTO for user location update."""
    user_id: str
    latitude: float
    longitude: float
    accuracy_meters: int
    timestamp: datetime
    status: str  # available, traveling, on_job, break, unavailable


@dataclass
class WeatherImpactDTO:
    """DTO for weather impact analysis."""
    impact_level: str  # none, low, moderate, high, severe
    affected_job_types: List[str]
    recommended_actions: List[str]
    safety_concerns: List[str]
    schedule_adjustment_minutes: int
    work_feasibility_score: Decimal


@dataclass
class TravelTimeResultDTO:
    """DTO for travel time calculation result."""
    distance_km: Decimal
    duration_minutes: Decimal
    duration_in_traffic_minutes: Optional[Decimal]
    traffic_conditions: Optional[str]
    route_polyline: Optional[str]


@dataclass
class RouteOptimizationResultDTO:
    """DTO for route optimization result."""
    total_distance_km: Decimal
    total_duration_minutes: Decimal
    waypoints_order: List[int]
    route_legs: List[Dict[str, Any]]
    estimated_fuel_cost: Optional[Decimal]
    traffic_warnings: List[str]


@dataclass
class AvailableTimeSlotRequestDTO:
    """DTO for available time slots request."""
    job_type: str
    estimated_duration_hours: float
    required_skills: List[str] = field(default_factory=list)
    job_address: Optional[Dict[str, Any]] = None
    preferred_date_range: TimeWindowDTO = None
    customer_preferences: Optional[Dict[str, Any]] = None
    priority: str = "medium"


@dataclass
class TimeSlotDTO:
    """DTO for individual time slot."""
    slot_id: str
    start_time: datetime
    end_time: datetime
    available_technicians: List[Dict[str, Any]]
    confidence_score: float
    estimated_travel_time_minutes: int
    pricing_info: Optional[Dict[str, Any]] = None
    weather_impact: Optional[Dict[str, Any]] = None
    slot_quality_score: float = 0.8
    notes: Optional[str] = None


@dataclass
class AvailableTimeSlotsResponseDTO:
    """DTO for available time slots response."""
    request_id: str
    available_slots: List[TimeSlotDTO]
    total_slots_found: int
    search_criteria: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)
    alternative_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    booking_deadline: Optional[datetime] = None


@dataclass
class TimeSlotBookingRequestDTO:
    """DTO for time slot booking request."""
    slot_id: str
    customer_contact: Dict[str, Any]
    job_details: Dict[str, Any]
    special_instructions: Optional[str] = None
    confirm_booking: bool = True


@dataclass
class TimeSlotBookingResponseDTO:
    """DTO for time slot booking response."""
    booking_id: str
    job_id: str
    status: str
    scheduled_slot: TimeSlotDTO
    assigned_technician: Dict[str, Any]
    confirmation_details: Dict[str, Any]
    next_steps: List[str]
    cancellation_policy: str 