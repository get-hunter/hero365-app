"""
Intelligent Scheduling Use Case

Business logic for intelligent job scheduling with real-time optimization
using external services for travel time and weather data integration.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import logging

from ...dto.scheduling_dto import (
    SchedulingOptimizationRequestDTO, SchedulingOptimizationResponseDTO,
    RealTimeAdaptationRequestDTO, RealTimeAdaptationResponseDTO,
    SchedulingAnalyticsRequestDTO, SchedulingAnalyticsResponseDTO
)
from ...exceptions.application_exceptions import (
    ValidationError, NotFoundError, BusinessLogicError
)
from ....domain.entities.job import Job, JobType, JobPriority, JobStatus
from ....domain.entities.user_capabilities import UserCapabilities
from ....domain.entities.scheduling_engine import IntelligentSchedulingEngine, SchedulingResult
from ....domain.repositories.job_repository import JobRepository
from ....domain.repositories.user_capabilities_repository import UserCapabilitiesRepository
from ....domain.repositories.business_membership_repository import BusinessMembershipRepository
from ...ports.external_services import (
    RouteOptimizationPort, TravelTimePort, WeatherServicePort, NotificationServicePort
)

logger = logging.getLogger(__name__)


class IntelligentSchedulingUseCase:
    """
    Use case for intelligent job scheduling with real-time optimization.
    
    Integrates with external services to provide advanced scheduling capabilities
    including travel time optimization, weather impact analysis, and real-time adaptation.
    """
    
    def __init__(self,
                 job_repository: JobRepository,
                 user_capabilities_repository: Optional[UserCapabilitiesRepository],
                 business_membership_repository: BusinessMembershipRepository,
                 route_optimization_service: RouteOptimizationPort,
                 travel_time_service: TravelTimePort,
                 weather_service: WeatherServicePort,
                 notification_service: NotificationServicePort):
        self.job_repository = job_repository
        self.user_capabilities_repository = user_capabilities_repository
        self.business_membership_repository = business_membership_repository
        self.route_optimization_service = route_optimization_service
        self.travel_time_service = travel_time_service
        self.weather_service = weather_service
        self.notification_service = notification_service
        self.scheduling_engine = IntelligentSchedulingEngine()
    
    async def optimize_schedule(self,
                              business_id: uuid.UUID,
                              request: SchedulingOptimizationRequestDTO,
                              user_id: str) -> SchedulingOptimizationResponseDTO:
        """
        Optimize job scheduling using intelligent algorithms and real-time data.
        
        Args:
            business_id: Business context
            request: Optimization request with jobs and constraints
            user_id: User making the request
            
        Returns:
            Optimized schedule with assignments and metrics
        """
        try:
            # Validate permissions
            await self._check_scheduling_permission(business_id, user_id)
            
            # Get jobs to optimize
            jobs = await self._get_jobs_for_optimization(business_id, request.job_ids)
            
            # Get available users with capabilities
            available_users = await self._get_available_users(business_id, request.time_window)
            
            if not available_users:
                raise BusinessLogicError("No available users found for scheduling optimization")
            
            # Enhance with real-time data
            enhanced_jobs = await self._enhance_jobs_with_realtime_data(jobs)
            enhanced_users = await self._enhance_users_with_realtime_data(available_users)
            
            # Perform optimization
            optimization_results = await self._optimize_job_assignments(
                enhanced_jobs, enhanced_users, request.constraints
            )
            
            # Calculate optimization metrics
            metrics = await self._calculate_optimization_metrics(
                jobs, optimization_results, request.baseline_metrics
            )
            
            # Save optimized assignments
            await self._save_optimized_assignments(optimization_results)
            
            # Send notifications if requested
            if request.notify_users:
                await self._send_optimization_notifications(optimization_results)
            
            return SchedulingOptimizationResponseDTO(
                optimization_id=str(uuid.uuid4()),
                optimized_assignments=optimization_results,
                optimization_metrics=metrics,
                success=True,
                message="Schedule optimization completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Error optimizing schedule: {str(e)}")
            raise BusinessLogicError(f"Schedule optimization failed: {str(e)}")
    
    async def adapt_schedule_realtime(self,
                                    business_id: uuid.UUID,
                                    request: RealTimeAdaptationRequestDTO,
                                    user_id: str) -> RealTimeAdaptationResponseDTO:
        """
        Adapt existing schedule based on real-time disruptions.
        
        Args:
            business_id: Business context
            request: Adaptation request with disruption details
            user_id: User making the request
            
        Returns:
            Adapted schedule with changes and notifications
        """
        try:
            # Validate permissions
            await self._check_scheduling_permission(business_id, user_id)
            
            # Analyze disruption impact
            impact_analysis = await self._analyze_disruption_impact(
                business_id, request.disruption
            )
            
            # Get affected jobs and users
            affected_jobs = await self._get_affected_jobs(
                business_id, request.disruption.affected_job_ids
            )
            
            # Generate adaptation strategies
            adaptation_strategies = await self._generate_adaptation_strategies(
                affected_jobs, impact_analysis, request.adaptation_preferences
            )
            
            # Select and execute optimal strategy
            optimal_strategy = self._select_optimal_adaptation_strategy(adaptation_strategies)
            adaptation_result = await self._execute_adaptation_strategy(optimal_strategy)
            
            # Send notifications
            notifications_sent = await self._send_adaptation_notifications(
                adaptation_result, request.adaptation_preferences.notify_customers
            )
            
            return RealTimeAdaptationResponseDTO(
                adaptation_id=str(uuid.uuid4()),
                status="success",
                adapted_assignments=adaptation_result.adapted_jobs,
                impact_summary=adaptation_result.impact_summary,
                notifications_sent=notifications_sent,
                message="Schedule adaptation completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Error adapting schedule: {str(e)}")
            raise BusinessLogicError(f"Schedule adaptation failed: {str(e)}")
    
    async def get_scheduling_analytics(self,
                                     business_id: uuid.UUID,
                                     request: SchedulingAnalyticsRequestDTO,
                                     user_id: str) -> SchedulingAnalyticsResponseDTO:
        """
        Get comprehensive scheduling performance analytics.
        
        Args:
            business_id: Business context
            request: Analytics request with filters
            user_id: User making the request
            
        Returns:
            Scheduling analytics and performance metrics
        """
        try:
            # Validate permissions
            await self._check_analytics_permission(business_id, user_id)
            
            # Get historical job data
            historical_jobs = await self._get_historical_jobs(business_id, request)
            
            # Calculate KPIs
            kpis = await self._calculate_scheduling_kpis(historical_jobs, request.period)
            
            # Generate improvement recommendations
            recommendations = await self._generate_improvement_recommendations(
                business_id, kpis, historical_jobs
            )
            
            # Get predictive insights
            predictions = await self._generate_predictive_insights(business_id, request)
            
            return SchedulingAnalyticsResponseDTO(
                period=request.period,
                kpis=kpis,
                recommendations=recommendations,
                predictions=predictions,
                trend_analysis=await self._calculate_trend_analysis(historical_jobs)
            )
            
        except Exception as e:
            logger.error(f"Error getting scheduling analytics: {str(e)}")
            raise BusinessLogicError(f"Analytics generation failed: {str(e)}")
    
    async def _enhance_jobs_with_realtime_data(self, jobs: List[Job]) -> List[Dict[str, Any]]:
        """Enhance job data with real-time weather and traffic information."""
        enhanced_jobs = []
        
        for job in jobs:
            job_data = {
                "id": str(job.id),
                "title": job.title,
                "job_type": job.job_type.value,
                "priority": job.priority.value,
                "scheduled_start": job.scheduled_start,
                "scheduled_end": job.scheduled_end,
                "location": {
                    "latitude": job.job_address.latitude if job.job_address else 0.0,
                    "longitude": job.job_address.longitude if job.job_address else 0.0,
                    "address": job.job_address.get_full_address() if job.job_address else "No address"
                },
                "required_skills": job.custom_fields.get("required_skills", []),
                "estimated_duration_hours": job.time_tracking.estimated_hours or Decimal("2.0")
            }
            
            # Add weather impact analysis
            if job.scheduled_start and job.job_address and job.job_address.latitude and job.job_address.longitude:
                try:
                    weather_impact = await self.weather_service.get_weather_impact(
                        job.job_address.latitude,
                        job.job_address.longitude,
                        job.job_type.value,
                        job.scheduled_start
                    )
                    job_data["weather_impact"] = weather_impact
                except Exception as e:
                    logger.warning(f"Could not get weather data for job {job.id}: {str(e)}")
                    job_data["weather_impact"] = None
            
            enhanced_jobs.append(job_data)
        
        return enhanced_jobs
    
    async def _enhance_users_with_realtime_data(self, users: List[UserCapabilities]) -> List[Dict[str, Any]]:
        """Enhance user data with real-time location and availability."""
        enhanced_users = []
        
        for user in users:
            user_data = {
                "user_id": user.user_id,
                "skills": [
                    {
                        "skill_id": skill.skill_id,
                        "name": skill.name,
                        "level": skill.level.value,
                        "proficiency_score": float(skill.proficiency_score or 50)
                    }
                    for skill in user.skills
                ],
                "location": {
                    "latitude": user.home_base_latitude or 0.0,
                    "longitude": user.home_base_longitude or 0.0
                },
                "availability_windows": [
                    {
                        "day_of_week": window.day_of_week,
                        "start_time": window.start_time,
                        "end_time": window.end_time,
                        "capacity": float(window.capacity_percentage or 100)
                    }
                    for window in (user.availability_windows or [])
                ],
                "workload_capacity": {
                    "max_concurrent_jobs": user.workload_capacity.max_concurrent_jobs if user.workload_capacity else 5,
                    "max_daily_hours": float(user.workload_capacity.max_daily_hours) if user.workload_capacity else 8.0,
                    "max_travel_distance_km": float(user.workload_capacity.max_travel_distance_km) if user.workload_capacity else 50.0
                },
                "performance_metrics": {
                    "average_rating": float(user.average_job_rating or 4.0),
                    "completion_rate": float(user.completion_rate or 0.95),
                    "punctuality_score": float(user.punctuality_score or 0.90)
                }
            }
            
            # Add current workload
            current_jobs = await self.job_repository.get_by_assigned_user(
                user.business_id, user.user_id, skip=0, limit=100
            )
            active_jobs = [j for j in current_jobs if j.status in [JobStatus.SCHEDULED, JobStatus.IN_PROGRESS]]
            user_data["current_workload"] = len(active_jobs)
            
            enhanced_users.append(user_data)
        
        return enhanced_users
    
    async def _optimize_job_assignments(self,
                                      jobs: List[Dict[str, Any]],
                                      users: List[Dict[str, Any]],
                                      constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Optimize job assignments using the scheduling engine."""
        optimization_results = []
        
        # Use travel time matrix for better optimization
        if len(jobs) > 1 and len(users) > 1:
            travel_matrix = await self._get_travel_time_matrix(jobs, users)
        else:
            travel_matrix = {}
        
        for job_data in jobs:
            try:
                # Calculate travel times for this job
                job_location = job_data["location"]
                candidate_users = []
                
                for user_data in users:
                    user_location = user_data["location"]
                    
                    if user_location["latitude"] and user_location["longitude"]:
                        travel_time_result = await self.travel_time_service.get_travel_time(
                            user_location, job_location
                        )
                        travel_time_minutes = travel_time_result.get("duration_minutes", 30)
                    else:
                        travel_time_minutes = 30  # Default fallback
                    
                    candidate_users.append({
                        **user_data,
                        "travel_time_minutes": travel_time_minutes
                    })
                
                # Use scheduling engine
                result = self.scheduling_engine.schedule_job(
                    job_data, candidate_users, [constraints]
                )
                
                if result.is_feasible:
                    optimization_results.append({
                        "job_id": result.job_id,
                        "assigned_user_id": result.assigned_user_id,
                        "scheduled_start": result.scheduled_start,
                        "scheduled_end": result.scheduled_end,
                        "estimated_travel_time_minutes": float(result.estimated_travel_time or 0),
                        "confidence_score": float(result.confidence_score or 0.5),
                        "alternative_candidates": result.alternative_candidates,
                        "optimization_notes": result.scheduling_notes
                    })
                else:
                    logger.warning(f"Could not optimize job {job_data['id']}: {result.scheduling_notes}")
                    
            except Exception as e:
                logger.error(f"Error optimizing job {job_data['id']}: {str(e)}")
                continue
        
        return optimization_results
    
    async def _get_travel_time_matrix(self, 
                                    jobs: List[Dict[str, Any]], 
                                    users: List[Dict[str, Any]]) -> Dict:
        """Get travel time matrix for optimization."""
        try:
            origins = [user["location"] for user in users if user["location"]["latitude"]]
            destinations = [job["location"] for job in jobs if job["location"]["latitude"]]
            
            if not origins or not destinations:
                return {}
            
            return await self.route_optimization_service.get_travel_time_matrix(
                origins, destinations
            )
        except Exception as e:
            logger.warning(f"Could not get travel time matrix: {str(e)}")
            return {}
    
    async def _check_scheduling_permission(self, business_id: uuid.UUID, user_id: str) -> None:
        """Check if user has permission to perform scheduling operations."""
        membership = await self.business_membership_repository.get_by_user_and_business(
            user_id, business_id
        )
        
        if not membership or not membership.is_active:
            raise ValidationError("User is not an active member of this business")
        
        if not membership.has_permission("schedule_jobs"):
            raise ValidationError("User does not have permission to schedule jobs")
    
    async def _check_analytics_permission(self, business_id: uuid.UUID, user_id: str) -> None:
        """Check if user has permission to view analytics."""
        membership = await self.business_membership_repository.get_by_user_and_business(
            user_id, business_id
        )
        
        if not membership or not membership.is_active:
            raise ValidationError("User is not an active member of this business")
        
        if not membership.has_permission("view_analytics"):
            raise ValidationError("User does not have permission to view analytics")
    
    async def _get_jobs_for_optimization(self, 
                                       business_id: uuid.UUID, 
                                       job_ids: Optional[List[str]]) -> List[Job]:
        """Get jobs for optimization."""
        if job_ids:
            jobs = []
            for job_id in job_ids:
                job = await self.job_repository.get_by_id(uuid.UUID(job_id))
                if job and job.business_id == business_id:
                    jobs.append(job)
            return jobs
        else:
            # Get unscheduled or reschedulable jobs
            return await self.job_repository.get_by_status(
                business_id, JobStatus.DRAFT, skip=0, limit=100
            )
    
    async def _get_available_users(self, 
                                 business_id: uuid.UUID, 
                                 time_window: Optional[Dict]) -> List[UserCapabilities]:
        """Get available users for scheduling."""
        # Get all active business members
        memberships = await self.business_membership_repository.get_business_members(business_id)
        
        user_capabilities = []
        
        # If user capabilities repository is not available, create basic capabilities for each member
        if self.user_capabilities_repository is None:
            # Create basic user capabilities for each active member
            for membership in memberships:
                if membership.is_active:
                    # Create a basic UserCapabilities object with default values
                    basic_capabilities = UserCapabilities(
                        user_id=membership.user_id,
                        business_id=business_id,
                        skills=[],  # No specific skills defined
                        certifications=[],
                        availability_windows=[],  # Available all the time by default
                        workload_capacity=None,  # No capacity limits
                        home_base_latitude=None,
                        home_base_longitude=None,
                        is_active=True
                    )
                    user_capabilities.append(basic_capabilities)
        else:
            # Use the actual user capabilities repository
            for membership in memberships:
                if membership.is_active:
                    capabilities = await self.user_capabilities_repository.get_by_user_id(
                        business_id, membership.user_id
                    )
                    if capabilities and capabilities.is_active:
                        user_capabilities.append(capabilities)
        
        return user_capabilities
    
    async def _calculate_optimization_metrics(self,
                                            original_jobs: List[Job],
                                            optimized_results: List[Dict[str, Any]],
                                            baseline_metrics: Optional[Dict]) -> Dict[str, Any]:
        """Calculate optimization improvement metrics."""
        total_travel_time = sum(
            result.get("estimated_travel_time_minutes", 0) 
            for result in optimized_results
        )
        
        successfully_scheduled = len(optimized_results)
        total_jobs = len(original_jobs)
        
        average_confidence = sum(
            result.get("confidence_score", 0) 
            for result in optimized_results
        ) / max(len(optimized_results), 1)
        
        return {
            "total_jobs": total_jobs,
            "successfully_scheduled": successfully_scheduled,
            "scheduling_success_rate": successfully_scheduled / max(total_jobs, 1),
            "total_travel_time_minutes": total_travel_time,
            "average_travel_time_per_job": total_travel_time / max(successfully_scheduled, 1),
            "average_confidence_score": average_confidence,
            "optimization_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _save_optimized_assignments(self, optimization_results: List[Dict[str, Any]]) -> None:
        """Save optimized job assignments to database."""
        for result in optimization_results:
            try:
                job = await self.job_repository.get_by_id(uuid.UUID(result["job_id"]))
                if job:
                    # Update job assignment and schedule
                    if result["assigned_user_id"]:
                        job.assign_team_member(result["assigned_user_id"])
                    
                    if result["scheduled_start"] and result["scheduled_end"]:
                        job.update_schedule(result["scheduled_start"], result["scheduled_end"])
                    
                    await self.job_repository.update(job)
                    
            except Exception as e:
                logger.error(f"Error saving assignment for job {result['job_id']}: {str(e)}")
    
    async def _send_optimization_notifications(self, optimization_results: List[Dict[str, Any]]) -> None:
        """Send notifications about schedule optimization."""
        notifications = []
        
        for result in optimization_results:
            if result["assigned_user_id"]:
                notifications.append({
                    "user_id": result["assigned_user_id"],
                    "message": f"New job assignment: {result['job_id']}",
                    "notification_type": "job_assignment"
                })
        
        if notifications:
            await self.notification_service.send_bulk_notifications(notifications)
    
    # Additional helper methods for disruption handling, analytics, etc.
    # ... (implementation continues with remaining methods)
    
    async def _analyze_disruption_impact(self, business_id: uuid.UUID, disruption: Dict) -> Dict:
        """Analyze the impact of a disruption on the schedule."""
        # Implementation for disruption impact analysis
        return {"impact_level": "moderate", "affected_jobs_count": len(disruption.get("affected_job_ids", []))}
    
    async def _get_affected_jobs(self, business_id: uuid.UUID, job_ids: List[str]) -> List[Job]:
        """Get jobs affected by disruption."""
        jobs = []
        for job_id in job_ids:
            job = await self.job_repository.get_by_id(uuid.UUID(job_id))
            if job and job.business_id == business_id:
                jobs.append(job)
        return jobs 