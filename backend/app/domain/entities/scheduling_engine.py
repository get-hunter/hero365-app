"""
Intelligent Job Scheduling Engine

Core domain entity for optimizing job assignments considering user capabilities,
travel time, and business constraints using advanced scheduling algorithms.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple, Annotated
from enum import Enum
from decimal import Decimal
import math
from pydantic import BaseModel, Field, field_validator, model_validator, UUID4, BeforeValidator

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError

# Configure logging
logger = logging.getLogger(__name__)


# Custom Pydantic validators for automatic string-to-enum conversion
def validate_scheduling_objective(v) -> 'SchedulingObjective':
    """Convert string to SchedulingObjective enum."""
    if isinstance(v, str):
        return SchedulingObjective(v)
    return v

def validate_scheduling_constraint(v) -> 'SchedulingConstraint':
    """Convert string to SchedulingConstraint enum."""
    if isinstance(v, str):
        return SchedulingConstraint(v)
    return v


class SchedulingObjective(Enum):
    """Optimization objectives for scheduling."""
    MINIMIZE_TRAVEL_TIME = "minimize_travel_time"
    MAXIMIZE_UTILIZATION = "maximize_utilization"
    BALANCE_WORKLOAD = "balance_workload"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_CUSTOMER_SATISFACTION = "maximize_customer_satisfaction"


class SchedulingConstraint(Enum):
    """Types of scheduling constraints."""
    TIME_WINDOW = "time_window"
    SKILL_REQUIREMENT = "skill_requirement"
    TRAVEL_DISTANCE = "travel_distance"
    WORKLOAD_CAPACITY = "workload_capacity"
    AVAILABILITY = "availability"
    EQUIPMENT_REQUIREMENT = "equipment_requirement"


class TravelTimeCalculation(BaseModel):
    """Value object for travel time calculations."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    origin_lat: float = Field(ge=-90, le=90)
    origin_lng: float = Field(ge=-180, le=180)
    destination_lat: float = Field(ge=-90, le=90)
    destination_lng: float = Field(ge=-180, le=180)
    travel_time_minutes: Decimal = Field(ge=0)
    distance_km: Decimal = Field(ge=0)
    traffic_factor: Decimal = Field(default=Decimal("1.0"), gt=0)
    
    @classmethod
    def calculate_haversine_distance(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> Decimal:
        """Calculate distance using Haversine formula."""
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in kilometers
        r = 6371
        return Decimal(str(c * r))
    
    @classmethod
    def estimate_travel_time(cls, distance_km: Decimal, avg_speed_kmh: Decimal = Decimal("30")) -> Decimal:
        """Estimate travel time based on distance and average speed."""
        hours = distance_km / avg_speed_kmh
        return hours * Decimal("60")  # Convert to minutes


class SchedulingCandidate(BaseModel):
    """Represents a user candidate for job assignment."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    user_id: str = Field(min_length=1)
    skill_match_score: Decimal = Field(ge=0, le=1)  # 0-1
    travel_time_minutes: Decimal = Field(ge=0)
    efficiency_multiplier: Decimal = Field(gt=0)
    current_workload: int = Field(ge=0)
    availability_score: Decimal = Field(ge=0, le=1)  # 0-1
    cost_per_hour: Decimal = Field(ge=0)
    priority_bonus: Decimal = Field(default=Decimal("0"), ge=0)
    
    def calculate_total_score(self, weights: Dict[str, Decimal]) -> Decimal:
        """Calculate weighted total score for ranking."""
        score = (
            weights.get("skill_match", Decimal("0.3")) * self.skill_match_score +
            weights.get("travel_efficiency", Decimal("0.25")) * self._get_travel_efficiency_score() +
            weights.get("availability", Decimal("0.2")) * self.availability_score +
            weights.get("efficiency", Decimal("0.15")) * (self.efficiency_multiplier - Decimal("1.0")) +
            weights.get("workload_balance", Decimal("0.1")) * self._get_workload_balance_score() +
            self.priority_bonus
        )
        return max(Decimal("0"), min(Decimal("1"), score))
    
    def _get_travel_efficiency_score(self) -> Decimal:
        """Convert travel time to efficiency score (lower time = higher score)."""
        if self.travel_time_minutes <= 15:
            return Decimal("1.0")
        elif self.travel_time_minutes <= 30:
            return Decimal("0.8")
        elif self.travel_time_minutes <= 45:
            return Decimal("0.6")
        elif self.travel_time_minutes <= 60:
            return Decimal("0.4")
        else:
            return Decimal("0.2")
    
    def _get_workload_balance_score(self) -> Decimal:
        """Score based on current workload (lower workload = higher score)."""
        if self.current_workload == 0:
            return Decimal("1.0")
        elif self.current_workload <= 2:
            return Decimal("0.8")
        elif self.current_workload <= 4:
            return Decimal("0.6")
        else:
            return Decimal("0.4")


class SchedulingResult(BaseModel):
    """Result of job scheduling operation."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    job_id: UUID4
    assigned_user_id: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    estimated_travel_time: Optional[Decimal] = Field(default=None, ge=0)
    confidence_score: Optional[Decimal] = Field(default=None, ge=0, le=1)
    alternative_candidates: List[str] = Field(default_factory=list)
    scheduling_notes: Optional[str] = None
    constraints_violated: List[str] = Field(default_factory=list)
    is_feasible: bool = True


class IntelligentSchedulingEngine:
    """
    Advanced scheduling engine for optimizing job assignments.
    
    Uses multiple algorithms and heuristics to assign jobs to users
    considering skills, travel time, workload, and business constraints.
    """
    
    def __init__(self, 
                 default_objectives: List[SchedulingObjective] = None,
                 default_weights: Dict[str, Decimal] = None):
        self.default_objectives = default_objectives or [
            SchedulingObjective.MINIMIZE_TRAVEL_TIME,
            SchedulingObjective.MAXIMIZE_UTILIZATION
        ]
        self.default_weights = default_weights or {
            "skill_match": Decimal("0.3"),
            "travel_efficiency": Decimal("0.25"),
            "availability": Decimal("0.2"),
            "efficiency": Decimal("0.15"),
            "workload_balance": Decimal("0.1")
        }
    
    def schedule_job(self, 
                    job_data: Dict[str, Any],
                    candidate_users: List[Dict[str, Any]],
                    constraints: List[Dict[str, Any]] = None,
                    objectives: List[SchedulingObjective] = None) -> SchedulingResult:
        """
        Schedule a single job to the best available user.
        
        Args:
            job_data: Job information including location, requirements, time window
            candidate_users: List of potential users with capabilities
            constraints: Additional scheduling constraints
            objectives: Optimization objectives
            
        Returns:
            SchedulingResult with assignment details
        """
        try:
            # Validate inputs
            self._validate_job_data(job_data)
            
            if not candidate_users:
                return SchedulingResult(
                    job_id=uuid.UUID(job_data["id"]),
                    is_feasible=False,
                    scheduling_notes="No candidate users available"
                )
            
            # Generate scheduling candidates
            candidates = self._generate_candidates(job_data, candidate_users)
            
            # Apply constraints
            feasible_candidates = self._apply_constraints(candidates, constraints or [])
            
            if not feasible_candidates:
                return SchedulingResult(
                    job_id=uuid.UUID(job_data["id"]),
                    is_feasible=False,
                    scheduling_notes="No feasible candidates after applying constraints"
                )
            
            # Rank candidates using optimization objectives
            ranked_candidates = self._rank_candidates(feasible_candidates, objectives)
            
            # Select best candidate
            best_candidate = ranked_candidates[0]
            
            # Calculate optimal schedule time
            optimal_schedule = self._calculate_optimal_schedule_time(job_data, best_candidate)
            
            return SchedulingResult(
                job_id=uuid.UUID(job_data["id"]),
                assigned_user_id=best_candidate.user_id,
                scheduled_start=optimal_schedule["start"],
                scheduled_end=optimal_schedule["end"],
                estimated_travel_time=best_candidate.travel_time_minutes,
                confidence_score=best_candidate.calculate_total_score(self.default_weights),
                alternative_candidates=[c.user_id for c in ranked_candidates[1:3]],  # Top 2 alternatives
                is_feasible=True
            )
            
        except Exception as e:
            return SchedulingResult(
                job_id=uuid.UUID(job_data["id"]),
                is_feasible=False,
                scheduling_notes=f"Scheduling error: {str(e)}"
            )
    
    def schedule_multiple_jobs(self,
                              jobs_data: List[Dict[str, Any]],
                              available_users: List[Dict[str, Any]],
                              optimization_horizon_hours: int = 24) -> List[SchedulingResult]:
        """
        Schedule multiple jobs optimally considering interdependencies.
        
        Uses a priority-based greedy algorithm with local optimization.
        """
        results = []
        user_schedules = {user["user_id"]: [] for user in available_users}
        
        # Sort jobs by priority and urgency
        sorted_jobs = self._prioritize_jobs(jobs_data)
        
        for job_data in sorted_jobs:
            # Get updated candidate users (considering current assignments)
            updated_candidates = self._update_candidates_with_current_schedule(
                available_users, user_schedules, job_data
            )
            
            # Schedule this job
            result = self.schedule_job(job_data, updated_candidates)
            
            # Update user schedules if assignment was successful
            if result.is_feasible and result.assigned_user_id:
                user_schedules[result.assigned_user_id].append({
                    "job_id": result.job_id,
                    "start": result.scheduled_start,
                    "end": result.scheduled_end,
                    "travel_time": result.estimated_travel_time
                })
            
            results.append(result)
        
        return results
    
    def optimize_existing_schedule(self,
                                  current_assignments: List[Dict[str, Any]],
                                  available_users: List[Dict[str, Any]]) -> List[SchedulingResult]:
        """
        Optimize an existing schedule using local search algorithms.
        
        Attempts to improve current assignments through swapping and rescheduling.
        """
        # Implementation of optimization algorithms
        # Could use simulated annealing, genetic algorithms, or constraint programming
        pass
    
    def _validate_job_data(self, job_data: Dict[str, Any]) -> None:
        """Validate job data structure."""
        required_fields = ["id", "location_lat", "location_lng", "required_skills"]
        for field in required_fields:
            if field not in job_data:
                raise DomainValidationError(f"Job data missing required field: {field}")
    
    def _generate_candidates(self, job_data: Dict[str, Any], users: List[Dict[str, Any]]) -> List[SchedulingCandidate]:
        """Generate scheduling candidates with scores."""
        candidates = []
        
        for user in users:
            # Calculate travel time and distance
            travel_calc = TravelTimeCalculation.calculate_haversine_distance(
                user.get("home_base_latitude", 0),
                user.get("home_base_longitude", 0),
                job_data["location_lat"],
                job_data["location_lng"]
            )
            travel_time = TravelTimeCalculation.estimate_travel_time(travel_calc)
            
            # Calculate skill match score
            skill_score = self._calculate_skill_match_score(
                job_data.get("required_skills", []),
                user.get("skills", [])
            )
            
            # Calculate availability score
            availability_score = self._calculate_availability_score(
                user.get("availability_windows", []),
                job_data.get("preferred_time_window")
            )
            
            candidate = SchedulingCandidate(
                user_id=user["user_id"],
                skill_match_score=skill_score,
                travel_time_minutes=travel_time,
                efficiency_multiplier=user.get("efficiency_multiplier", Decimal("1.0")),
                current_workload=user.get("current_workload", 0),
                availability_score=availability_score,
                cost_per_hour=user.get("cost_per_hour", Decimal("50"))
            )
            
            candidates.append(candidate)
        
        return candidates
    
    def _calculate_skill_match_score(self, required_skills: List[str], user_skills: List[Dict]) -> Decimal:
        """Calculate how well user skills match job requirements."""
        if not required_skills:
            return Decimal("1.0")
        
        total_score = Decimal("0")
        user_skill_map = {skill["skill_id"]: skill for skill in user_skills}
        
        for required_skill in required_skills:
            if required_skill in user_skill_map:
                skill = user_skill_map[required_skill]
                level_scores = {
                    "beginner": Decimal("0.6"),
                    "intermediate": Decimal("0.75"),
                    "advanced": Decimal("0.9"),
                    "expert": Decimal("1.0"),
                    "master": Decimal("1.1")
                }
                total_score += level_scores.get(skill.get("level", "beginner"), Decimal("0.6"))
            else:
                total_score += Decimal("0.2")  # Partial credit for adaptability
        
        return total_score / Decimal(str(len(required_skills)))
    
    def _calculate_availability_score(self, availability_windows: List[Dict], preferred_window: Dict = None) -> Decimal:
        """Calculate availability score based on time preferences."""
        if not availability_windows:
            return Decimal("0.5")  # Default availability
        
        # Simplified availability calculation
        # In practice, this would consider actual time windows, current bookings, etc.
        return Decimal("0.8")  # Placeholder
    
    def _apply_constraints(self, candidates: List[SchedulingCandidate], constraints: List[Dict]) -> List[SchedulingCandidate]:
        """Filter candidates based on hard constraints."""
        feasible_candidates = []
        
        for candidate in candidates:
            is_feasible = True
            
            for constraint in constraints:
                constraint_type = constraint.get("type")
                
                if constraint_type == "max_travel_time":
                    max_travel = constraint.get("value", 60)
                    if candidate.travel_time_minutes > max_travel:
                        is_feasible = False
                        break
                
                elif constraint_type == "min_skill_score":
                    min_score = constraint.get("value", 0.7)
                    if candidate.skill_match_score < min_score:
                        is_feasible = False
                        break
                
                elif constraint_type == "max_workload":
                    max_workload = constraint.get("value", 5)
                    if candidate.current_workload >= max_workload:
                        is_feasible = False
                        break
            
            if is_feasible:
                feasible_candidates.append(candidate)
        
        return feasible_candidates
    
    def _rank_candidates(self, candidates: List[SchedulingCandidate], objectives: List[SchedulingObjective] = None) -> List[SchedulingCandidate]:
        """Rank candidates based on optimization objectives."""
        objectives = objectives or self.default_objectives
        
        # Calculate scores and sort
        for candidate in candidates:
            candidate.total_score = candidate.calculate_total_score(self.default_weights)
        
        return sorted(candidates, key=lambda c: c.total_score, reverse=True)
    
    def _calculate_optimal_schedule_time(self, job_data: Dict[str, Any], candidate: SchedulingCandidate) -> Dict[str, datetime]:
        """Calculate optimal start and end times for the job."""
        # This would integrate with calendar systems and consider:
        # - Job duration
        # - Travel time
        # - User availability
        # - Customer preferences
        
        # Simplified implementation
        now = datetime.utcnow()
        travel_buffer = timedelta(minutes=float(candidate.travel_time_minutes))
        job_duration = timedelta(hours=job_data.get("estimated_duration_hours", 2))
        
        start_time = now + travel_buffer + timedelta(hours=1)  # 1 hour buffer
        end_time = start_time + job_duration
        
        return {
            "start": start_time,
            "end": end_time
        }
    
    def _prioritize_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort jobs by priority for scheduling order."""
        def priority_score(job):
            priority_weight = {"emergency": 100, "urgent": 80, "high": 60, "medium": 40, "low": 20}
            base_score = priority_weight.get(job.get("priority", "medium"), 40)
            
            # Add urgency based on due date
            if job.get("due_date"):
                due_date = datetime.fromisoformat(job["due_date"])
                hours_until_due = (due_date - datetime.utcnow()).total_seconds() / 3600
                urgency_bonus = max(0, 50 - hours_until_due)  # More urgent = higher score
                base_score += urgency_bonus
            
            return base_score
        
        return sorted(jobs, key=priority_score, reverse=True)
    
    def _update_candidates_with_current_schedule(self, users: List[Dict], schedules: Dict, job_data: Dict) -> List[Dict]:
        """Update user data with current schedule information."""
        updated_users = []
        
        for user in users:
            updated_user = user.copy()
            user_id = user["user_id"]
            
            # Update current workload
            current_jobs = len(schedules.get(user_id, []))
            updated_user["current_workload"] = current_jobs
            
            # Calculate total scheduled hours for the day
            total_hours = sum(
                (job["end"] - job["start"]).total_seconds() / 3600
                for job in schedules.get(user_id, [])
                if job["start"].date() == datetime.utcnow().date()
            )
            updated_user["scheduled_hours_today"] = total_hours
            
            updated_users.append(updated_user)
        
        return updated_users 