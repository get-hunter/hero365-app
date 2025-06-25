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
    SchedulingAnalyticsRequestDTO, SchedulingAnalyticsResponseDTO,
    AvailableTimeSlotRequestDTO, AvailableTimeSlotsResponseDTO,
    TimeSlotBookingRequestDTO, TimeSlotBookingResponseDTO,
    TimeSlotDTO, CalendarEventDTO, TimeOffRequestDTO, WorkingHoursTemplateDTO,
    CalendarPreferencesDTO, UserAvailabilityDTO
)
from ...exceptions.application_exceptions import (
    ValidationError, NotFoundError, BusinessLogicError
)
from app.domain.entities.job import Job, JobType, JobPriority, JobStatus
from app.domain.entities.user_capabilities import UserCapabilities
from app.domain.entities.scheduling_engine import IntelligentSchedulingEngine, SchedulingResult
from app.domain.repositories.job_repository import JobRepository
from app.domain.repositories.user_capabilities_repository import UserCapabilitiesRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
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
    
    async def get_available_time_slots(self,
                                     business_id: uuid.UUID,
                                     request: AvailableTimeSlotRequestDTO,
                                     user_id: Optional[str] = None) -> AvailableTimeSlotsResponseDTO:
        """
        Get available time slots for customer booking.
        
        Args:
            business_id: Business context
            request: Time slot request with job requirements
            user_id: Optional user making the request
            
        Returns:
            Available time slots with technician assignments
        """
        try:
            # Get available users with capabilities
            available_users = await self._get_available_users(business_id, request.preferred_date_range)
            
            if not available_users:
                return AvailableTimeSlotsResponseDTO(
                    request_id=str(uuid.uuid4()),
                    available_slots=[],
                    total_slots_found=0,
                    search_criteria=self._build_search_criteria(request),
                    recommendations=["No technicians available in the requested time range. Please try a different date range."],
                    alternative_suggestions=[{
                        "type": "extend_date_range",
                        "description": "Extend your search to the next week for more options"
                    }]
                )
            
            # Generate time slots based on availability
            time_slots = await self._generate_available_time_slots(
                business_id, request, available_users
            )
            
            # Enhance slots with real-time data
            enhanced_slots = await self._enhance_slots_with_realtime_data(
                time_slots, request
            )
            
            # Rank and filter slots
            ranked_slots = self._rank_time_slots(enhanced_slots, request.customer_preferences)
            
            # Generate recommendations
            recommendations = self._generate_slot_recommendations(ranked_slots, request)
            
            # Generate alternative suggestions
            alternatives = await self._generate_alternative_suggestions(
                business_id, request, len(ranked_slots)
            )
            
            return AvailableTimeSlotsResponseDTO(
                request_id=str(uuid.uuid4()),
                available_slots=ranked_slots,
                total_slots_found=len(ranked_slots),
                search_criteria=self._build_search_criteria(request),
                recommendations=recommendations,
                alternative_suggestions=alternatives,
                booking_deadline=datetime.utcnow() + timedelta(hours=24)  # 24-hour booking window
            )
            
        except Exception as e:
            logger.error(f"Error getting available time slots: {str(e)}")
            raise BusinessLogicError(f"Failed to get available time slots: {str(e)}")

    async def book_time_slot(self,
                           business_id: uuid.UUID,
                           request: TimeSlotBookingRequestDTO,
                           user_id: Optional[str] = None) -> TimeSlotBookingResponseDTO:
        """
        Book a specific time slot for a customer.
        
        Args:
            business_id: Business context
            request: Booking request with slot and customer details
            user_id: Optional user making the booking
            
        Returns:
            Booking confirmation with job details
        """
        try:
            # Validate slot availability
            slot_valid = await self._validate_slot_availability(
                business_id, request.slot_id
            )
            
            if not slot_valid:
                raise BusinessLogicError("Selected time slot is no longer available")
            
            # Create job from booking request
            job = await self._create_job_from_booking(business_id, request)
            
            # Assign technician to the job
            assignment_result = await self._assign_technician_to_slot(
                business_id, request.slot_id, job.id
            )
            
            # Send confirmation notifications
            await self._send_booking_confirmations(
                business_id, job, assignment_result, request.customer_contact
            )
            
            # Build response
            return TimeSlotBookingResponseDTO(
                booking_id=str(uuid.uuid4()),
                job_id=str(job.id),
                status="confirmed",
                scheduled_slot=assignment_result["slot"],
                assigned_technician=assignment_result["technician"],
                confirmation_details={
                    "booking_time": datetime.utcnow().isoformat(),
                    "confirmation_number": f"HERO-{str(uuid.uuid4())[:8].upper()}",
                    "customer_email": request.customer_contact.get("email"),
                    "customer_phone": request.customer_contact.get("phone")
                },
                next_steps=[
                    "You will receive a confirmation email shortly",
                    "The technician will call 30 minutes before arrival",
                    "Prepare the work area and ensure access to the job location"
                ],
                cancellation_policy="Free cancellation up to 2 hours before scheduled time"
            )
            
        except Exception as e:
            logger.error(f"Error booking time slot: {str(e)}")
            raise BusinessLogicError(f"Failed to book time slot: {str(e)}")
    
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

    async def _generate_available_time_slots(self,
                                           business_id: uuid.UUID,
                                           request: AvailableTimeSlotRequestDTO,
                                           available_users: List[UserCapabilities]) -> List[TimeSlotDTO]:
        """Generate available time slots based on user availability and job requirements."""
        time_slots = []
        slot_duration = timedelta(hours=request.estimated_duration_hours)
        
        # Define time slot intervals (e.g., every 30 minutes)
        slot_interval = timedelta(minutes=30)
        
        # Get date range
        start_date = request.preferred_date_range.start_time
        end_date = request.preferred_date_range.end_time
        
        current_time = start_date
        
        while current_time < end_date:
            slot_end = current_time + slot_duration
            
            # Don't generate slots that extend beyond the requested range
            if slot_end > end_date:
                break
            
            # Check each available user for this time slot
            for user in available_users:
                if await self._is_user_available_for_slot(user, current_time, slot_end, request.required_skills):
                    # Calculate travel time if job address is provided
                    travel_time_minutes = 0
                    if request.job_address and user.home_base_latitude and user.home_base_longitude:
                        try:
                            travel_time_minutes = await self.route_optimization_service.calculate_travel_time(
                                (user.home_base_latitude, user.home_base_longitude),
                                (request.job_address.get("latitude", 0), request.job_address.get("longitude", 0))
                            )
                        except Exception as e:
                            logger.warning(f"Failed to calculate travel time: {str(e)}")
                            travel_time_minutes = 30  # Default fallback
                    
                    # Calculate base quality score
                    quality_score = self._calculate_slot_quality_score(
                        user, current_time, slot_end, request
                    )
                    
                    # Get weather impact if available
                    weather_impact = None
                    if self.weather_service:
                        try:
                            weather_data = await self.weather_service.get_weather_impact(
                                request.job_address.get("latitude", 0) if request.job_address else 0,
                                request.job_address.get("longitude", 0) if request.job_address else 0,
                                current_time,
                                request.job_type
                            )
                            weather_impact = weather_data
                        except Exception as e:
                            logger.warning(f"Failed to get weather impact: {str(e)}")
                    
                    # Calculate dynamic pricing
                    base_price = 100.0  # Base price
                    pricing_factors = self._calculate_pricing_factors(current_time, request.priority, quality_score)
                    estimated_price = base_price * pricing_factors["total_multiplier"]
                    
                    # Create time slot
                    slot = TimeSlotDTO(
                        slot_id=str(uuid.uuid4()),
                        start_time=current_time,
                        end_time=slot_end,
                        available_technicians=[{
                            "technician_id": user.user_id,
                            "name": f"Technician {user.user_id}",  # Would get from user service
                            "skills": [skill.skill_id for skill in user.skills],
                            "rating": float(user.average_job_rating) if user.average_job_rating else 4.5,
                            "travel_time_minutes": travel_time_minutes
                        }],
                        estimated_duration_hours=request.estimated_duration_hours,
                        slot_quality_score=quality_score,
                        pricing_info={
                            "base_price": base_price,
                            "estimated_price": estimated_price,
                            "pricing_factors": pricing_factors
                        },
                        weather_impact=weather_impact,
                        travel_time_minutes=travel_time_minutes,
                        confidence_score=0.85,  # Base confidence
                        alternative_times=[],  # Would be populated with nearby slots
                        booking_deadline=current_time - timedelta(hours=2),  # 2 hours before
                        cancellation_policy="24_hours"
                    )
                    
                    # Enhance slot with calendar-aware data
                    slot = await self._enhance_time_slot_with_calendar_data(slot, user)
                    
                    time_slots.append(slot)
            
            current_time += slot_interval
        
        return time_slots

    async def _enhance_slots_with_realtime_data(self,
                                              time_slots: List[TimeSlotDTO],
                                              request: AvailableTimeSlotRequestDTO) -> List[TimeSlotDTO]:
        """Enhance time slots with real-time data like weather and pricing."""
        enhanced_slots = []
        
        for slot in time_slots:
            enhanced_slot = slot
            
            # Add weather impact if job address is provided
            if request.job_address and "latitude" in request.job_address:
                try:
                    weather_data = await self.weather_service.get_weather_impact(
                        request.job_address["latitude"],
                        request.job_address["longitude"],
                        request.job_type,
                        slot.start_time
                    )
                    enhanced_slot.weather_impact = {
                        "conditions": weather_data.get("conditions", "unknown"),
                        "impact_score": float(weather_data.get("impact_score", 0.8)),
                        "recommendations": weather_data.get("recommendations", [])
                    }
                except Exception as e:
                    logger.warning(f"Could not get weather data for slot {slot.slot_id}: {str(e)}")
            
            # Add pricing information
            try:
                pricing = await self._calculate_slot_pricing(slot, request)
                enhanced_slot.pricing_info = pricing
            except Exception as e:
                logger.warning(f"Could not calculate pricing for slot {slot.slot_id}: {str(e)}")
            
            enhanced_slots.append(enhanced_slot)
        
        return enhanced_slots

    def _rank_time_slots(self, time_slots: List[TimeSlotDTO], customer_preferences: Optional[Dict]) -> List[TimeSlotDTO]:
        """Rank time slots based on quality score and customer preferences."""
        def slot_score(slot: TimeSlotDTO) -> float:
            base_score = slot.slot_quality_score
            
            # Apply customer preferences
            if customer_preferences:
                if customer_preferences.get("avoid_early_morning") and slot.start_time.hour < 9:
                    base_score -= 0.2
                
                if customer_preferences.get("preferred_technician"):
                    preferred_tech = customer_preferences["preferred_technician"]
                    if any(tech["technician_id"] == preferred_tech for tech in slot.available_technicians):
                        base_score += 0.3
                
                if not customer_preferences.get("allow_weekend", True):
                    if slot.start_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
                        base_score -= 0.3
            
            # Weather impact
            if slot.weather_impact:
                base_score += slot.weather_impact.get("impact_score", 0) * 0.1
            
            return base_score
        
        # Sort by score (highest first) and return top 10
        ranked_slots = sorted(time_slots, key=slot_score, reverse=True)
        return ranked_slots[:10]

    def _generate_slot_recommendations(self, time_slots: List[TimeSlotDTO], request: AvailableTimeSlotRequestDTO) -> List[str]:
        """Generate recommendations based on available slots."""
        recommendations = []
        
        if not time_slots:
            recommendations.append("No slots available in the requested time range")
            return recommendations
        
        # Analyze time patterns
        morning_slots = [s for s in time_slots if 6 <= s.start_time.hour < 12]
        afternoon_slots = [s for s in time_slots if 12 <= s.start_time.hour < 18]
        
        if len(morning_slots) > len(afternoon_slots):
            recommendations.append("Morning slots have higher availability")
        elif len(afternoon_slots) > len(morning_slots):
            recommendations.append("Afternoon slots have better availability")
        
        # Analyze day patterns
        weekday_slots = [s for s in time_slots if s.start_time.weekday() < 5]
        weekend_slots = [s for s in time_slots if s.start_time.weekday() >= 5]
        
        if len(weekday_slots) > len(weekend_slots):
            recommendations.append("Weekday slots offer more options")
        
        # Find best quality slots
        best_slots = [s for s in time_slots if s.slot_quality_score > 0.8]
        if best_slots:
            best_day = max(set(s.start_time.strftime("%A") for s in best_slots), 
                          key=lambda day: len([s for s in best_slots if s.start_time.strftime("%A") == day]))
            recommendations.append(f"{best_day} has the most experienced technicians available")
        
        return recommendations

    async def _generate_alternative_suggestions(self,
                                              business_id: uuid.UUID,
                                              request: AvailableTimeSlotRequestDTO,
                                              current_slots_count: int) -> List[Dict[str, Any]]:
        """Generate alternative suggestions if few slots are available."""
        suggestions = []
        
        if current_slots_count < 3:
            # Suggest extending date range
            suggestions.append({
                "type": "extend_date_range",
                "description": "Extend search to next week for more options",
                "impact": "Could provide 10-15 additional time slots"
            })
            
            # Suggest flexible timing
            suggestions.append({
                "type": "flexible_timing",
                "description": "Consider flexible start times (±1 hour)",
                "impact": "Could double available options"
            })
        
        if current_slots_count < 5:
            # Suggest skill flexibility
            if request.required_skills:
                suggestions.append({
                    "type": "skill_flexibility",
                    "description": "Consider technicians with related skills",
                    "impact": "Could provide 5-8 additional qualified technicians"
                })
        
        return suggestions

    def _build_search_criteria(self, request: AvailableTimeSlotRequestDTO) -> Dict[str, Any]:
        """Build search criteria summary."""
        return {
            "job_type": request.job_type,
            "duration_hours": request.estimated_duration_hours,
            "required_skills": request.required_skills,
            "date_range": f"{request.preferred_date_range.start_time.strftime('%Y-%m-%d')} to {request.preferred_date_range.end_time.strftime('%Y-%m-%d')}",
            "priority": request.priority,
            "location": request.job_address.get("city", "Not specified") if request.job_address else "Not specified"
        }

    async def _is_user_available_for_slot(self,
                                        user: UserCapabilities,
                                        start_time: datetime,
                                        end_time: datetime,
                                        required_skills: List[str]) -> bool:
        """Check if user is available for a specific time slot."""
        # Check day of week availability using enhanced calendar system
        if not user.is_available_on_datetime(start_time):
            return False
        
        # Check if user has required skills
        if not user.matches_job_requirements(required_skills):
            return False
        
        # Check working hours template
        if user.working_hours_template:
            day_of_week = start_time.weekday()
            working_hours = user.working_hours_template.get_working_hours_for_day(day_of_week)
            if not working_hours:
                return False
            
            start_time_only = start_time.time()
            end_time_only = end_time.time()
            work_start, work_end = working_hours
            
            # Check if slot fits within working hours
            if not (work_start <= start_time_only and end_time_only <= work_end):
                return False
        
        # Check for time off conflicts
        for time_off in user.time_off_requests:
            if (time_off.is_approved() and time_off.affects_scheduling and
                time_off.overlaps_with_date(start_time.date())):
                return False
        
        # Check for calendar event conflicts
        for event in user.calendar_events:
            if (event.blocks_scheduling and event.is_active_on_date(start_time.date())):
                # Check time overlap
                event_start = datetime.combine(start_time.date(), event.start_datetime.time())
                event_end = datetime.combine(start_time.date(), event.end_datetime.time())
                
                # Check for overlap
                if not (end_time <= event_start or start_time >= event_end):
                    # Allow emergency override if configured
                    if not event.allows_emergency_override:
                        return False
        
        # Check calendar preferences
        if user.calendar_preferences:
            prefs = user.calendar_preferences
            
            # Check weekend availability
            if start_time.weekday() >= 5 and not prefs.weekend_availability:
                return False
            
            # Check auto-decline outside hours
            if prefs.auto_decline_outside_hours:
                if user.working_hours_template:
                    day_of_week = start_time.weekday()
                    working_hours = user.working_hours_template.get_working_hours_for_day(day_of_week)
                    if working_hours:
                        start_time_only = start_time.time()
                        work_start, work_end = working_hours
                        if not (work_start <= start_time_only <= work_end):
                            return False
        
        return True

    async def _enhance_time_slot_with_calendar_data(self,
                                                  slot: TimeSlotDTO,
                                                  user: UserCapabilities) -> TimeSlotDTO:
        """Enhance time slot with calendar-aware data."""
        # Apply calendar preferences for better scoring
        if user.calendar_preferences:
            prefs = user.calendar_preferences
            
            # Adjust quality score based on preferences
            quality_adjustment = 0.0
            
            # Prefer slots within preferred working hours
            if user.working_hours_template:
                day_of_week = slot.start_time.weekday()
                working_hours = user.working_hours_template.get_working_hours_for_day(day_of_week)
                if working_hours:
                    work_start, work_end = working_hours
                    slot_start = slot.start_time.time()
                    
                    # Bonus for being within core hours
                    if work_start <= slot_start <= work_end:
                        quality_adjustment += 0.1
            
            # Apply travel buffer preferences
            if hasattr(slot, 'travel_time_minutes') and slot.travel_time_minutes:
                buffered_time = slot.travel_time_minutes * float(prefs.travel_buffer_percentage)
                slot.travel_time_minutes = int(buffered_time)
            
            # Apply job buffer time
            if prefs.job_buffer_minutes > 0:
                # Extend slot duration by buffer time
                buffer_delta = timedelta(minutes=prefs.job_buffer_minutes)
                slot.end_time = slot.end_time + buffer_delta
            
            # Update quality score
            slot.slot_quality_score = min(1.0, slot.slot_quality_score + quality_adjustment)
        
        return slot

    def _calculate_slot_quality_score(self,
                                    user: UserCapabilities,
                                    start_time: datetime,
                                    end_time: datetime,
                                    request: AvailableTimeSlotRequestDTO) -> float:
        """Calculate quality score for a time slot considering calendar preferences."""
        base_score = 0.7  # Base quality score
        
        # Skill match bonus
        if user.matches_job_requirements(request.required_skills):
            base_score += 0.2
        
        # Performance metrics bonus
        if user.average_job_rating:
            rating_bonus = (float(user.average_job_rating) - 3.0) / 2.0 * 0.1  # Scale 3-5 to 0-0.1
            base_score += rating_bonus
        
        # Calendar preferences adjustments
        if user.calendar_preferences:
            prefs = user.calendar_preferences
            
            # Preferred time bonus
            if user.working_hours_template:
                day_of_week = start_time.weekday()
                working_hours = user.working_hours_template.get_working_hours_for_day(day_of_week)
                if working_hours:
                    work_start, work_end = working_hours
                    slot_start = start_time.time()
                    
                    # Calculate how centered the slot is within working hours
                    work_duration = datetime.combine(datetime.today(), work_end) - datetime.combine(datetime.today(), work_start)
                    work_midpoint = datetime.combine(datetime.today(), work_start) + work_duration / 2
                    slot_time = datetime.combine(datetime.today(), slot_start)
                    
                    # Closer to midpoint = higher score
                    time_diff = abs((slot_time - work_midpoint).total_seconds())
                    max_diff = work_duration.total_seconds() / 2
                    centrality_score = 1.0 - (time_diff / max_diff)
                    base_score += centrality_score * 0.1
            
            # Weekend penalty if not preferred
            if start_time.weekday() >= 5 and not prefs.weekend_availability:
                base_score -= 0.2
        
        # Time of day preferences
        hour = start_time.hour
        if 9 <= hour <= 17:  # Business hours bonus
            base_score += 0.05
        elif hour < 8 or hour > 18:  # Early/late penalty
            base_score -= 0.1
        
        return max(0.0, min(1.0, base_score))

    # Additional helper methods for booking functionality
    async def _validate_slot_availability(self, business_id: uuid.UUID, slot_id: str) -> bool:
        """Validate that a time slot is still available for booking."""
        # In production, this would check against current bookings
        # For now, return True (assuming slots are still available)
        return True

    async def _create_job_from_booking(self, business_id: uuid.UUID, request: TimeSlotBookingRequestDTO) -> Job:
        """Create a job from a booking request."""
        # This would create a new job using the job repository
        # For now, return a mock job
        from app.domain.entities.job import JobStatus, JobType
        
        job = Job(
            id=uuid.uuid4(),
            business_id=business_id,
            title=request.job_details.get("description", "Service Request"),
            description=request.job_details.get("description", ""),
            job_type=JobType.SERVICE,  # Default to service
            status=JobStatus.SCHEDULED,
            priority="medium",
            estimated_duration_hours=2.0,  # Would get from slot data
            customer_contact=request.customer_contact
        )
        
        return job

    async def _assign_technician_to_slot(self, business_id: uuid.UUID, slot_id: str, job_id: uuid.UUID) -> Dict[str, Any]:
        """Assign a technician to a booked time slot."""
        # This would handle the actual assignment logic
        # For now, return mock assignment data
        return {
            "slot": TimeSlotDTO(
                slot_id=slot_id,
                start_time=datetime.utcnow() + timedelta(hours=24),
                end_time=datetime.utcnow() + timedelta(hours=26),
                available_technicians=[],
                confidence_score=0.95,
                estimated_travel_time_minutes=25,
                slot_quality_score=0.9
            ),
            "technician": {
                "technician_id": "tech_123",
                "name": "John Smith",
                "phone": "+1234567890",
                "rating": 4.8,
                "specialties": ["plumbing", "electrical"]
            }
        }

    async def _send_booking_confirmations(self,
                                        business_id: uuid.UUID,
                                        job: Job,
                                        assignment_result: Dict[str, Any],
                                        customer_contact: Dict[str, Any]) -> None:
        """Send booking confirmation notifications."""
        try:
            # Send customer confirmation
            if customer_contact.get("email"):
                await self.notification_service.send_email_notification({
                    "to": customer_contact["email"],
                    "subject": "Booking Confirmation - Hero365",
                    "template": "booking_confirmation",
                    "data": {
                        "customer_name": customer_contact.get("name"),
                        "job_details": job.title,
                        "technician_name": assignment_result["technician"]["name"],
                        "scheduled_time": assignment_result["slot"].start_time.isoformat()
                    }
                })
            
            # Send technician notification
            technician_id = assignment_result["technician"]["technician_id"]
            await self.notification_service.send_notification({
                "user_id": technician_id,
                "message": f"New job assignment: {job.title}",
                "type": "job_assignment",
                "data": {
                    "job_id": str(job.id),
                    "customer_contact": customer_contact
                }
            })
            
        except Exception as e:
            logger.error(f"Error sending booking confirmations: {str(e)}") 