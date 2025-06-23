"""
Calendar Management Use Case

Handles user calendar management including working hours, events, time off, and availability.
"""

import uuid
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any

from ...dto.scheduling_dto import (
    CalendarEventDTO, TimeOffRequestDTO, WorkingHoursTemplateDTO,
    CalendarPreferencesDTO, UserAvailabilityDTO, TeamAvailabilitySummaryDTO,
    CreateCalendarEventRequestDTO, CreateTimeOffRequestDTO,
    UpdateWorkingHoursRequestDTO, AvailabilityCheckRequestDTO,
    AvailabilityCheckResponseDTO
)
from ...exceptions.application_exceptions import (
    ValidationError, BusinessLogicError, NotFoundError
)
from ...ports.auth_service import AuthServicePort
from ...ports.sms_service import SMSServicePort
from ...ports.email_service import EmailServicePort
from ....domain.entities.user_capabilities import (
    UserCapabilities, CalendarEvent, TimeOffRequest, WorkingHoursTemplate,
    CalendarPreferences, CalendarEventType, TimeOffType, RecurrenceType
)
from ....domain.repositories.user_capabilities_repository import UserCapabilitiesRepository
from ....domain.repositories.business_membership_repository import BusinessMembershipRepository

logger = logging.getLogger(__name__)


class CalendarManagementUseCase:
    """Use case for comprehensive calendar management."""
    
    def __init__(
        self,
        user_capabilities_repository: UserCapabilitiesRepository,
        business_membership_repository: BusinessMembershipRepository,
        auth_service: AuthServicePort,
        sms_service: Optional[SMSServicePort] = None,
        email_service: Optional[EmailServicePort] = None
    ):
        self.user_capabilities_repository = user_capabilities_repository
        self.business_membership_repository = business_membership_repository
        self.auth_service = auth_service
        self.sms_service = sms_service
        self.email_service = email_service
    
    # Working Hours Management
    async def create_working_hours_template(
        self,
        business_id: uuid.UUID,
        request: UpdateWorkingHoursRequestDTO,
        current_user_id: str
    ) -> WorkingHoursTemplateDTO:
        """Create a new working hours template."""
        try:
            # Check permissions
            await self._check_admin_permission(business_id, current_user_id)
            
            # Create template
            template = WorkingHoursTemplate(
                id=uuid.uuid4(),
                name=request.template_name or f"Template {datetime.utcnow().strftime('%Y-%m-%d')}",
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
            
            # Save template
            saved_template = await self.user_capabilities_repository.create_working_hours_template(template)
            
            logger.info(f"Created working hours template {saved_template.id} for business {business_id}")
            
            return self._convert_template_to_dto(saved_template)
            
        except Exception as e:
            logger.error(f"Error creating working hours template: {str(e)}")
            raise BusinessLogicError(f"Failed to create working hours template: {str(e)}")
    
    async def get_working_hours_templates(
        self,
        business_id: uuid.UUID,
        current_user_id: str
    ) -> List[WorkingHoursTemplateDTO]:
        """Get all working hours templates for a business."""
        try:
            # Check permissions
            await self._check_member_permission(business_id, current_user_id)
            
            templates = await self.user_capabilities_repository.get_business_working_hours_templates(business_id)
            
            return [self._convert_template_to_dto(template) for template in templates]
            
        except Exception as e:
            logger.error(f"Error getting working hours templates: {str(e)}")
            raise BusinessLogicError(f"Failed to get working hours templates: {str(e)}")
    
    async def set_user_working_hours(
        self,
        business_id: uuid.UUID,
        user_id: str,
        request: UpdateWorkingHoursRequestDTO,
        current_user_id: str
    ) -> WorkingHoursTemplateDTO:
        """Set working hours for a user."""
        try:
            # Check permissions (user can set their own, or admin can set anyone's)
            if user_id != current_user_id:
                await self._check_admin_permission(business_id, current_user_id)
            else:
                await self._check_member_permission(business_id, current_user_id)
            
            # Get user capabilities
            user_capabilities = await self.user_capabilities_repository.get_by_user_id(business_id, user_id)
            if not user_capabilities:
                raise NotFoundError("User capabilities", user_id)
            
            # Create or update working hours template
            if request.template_id:
                # Use existing template
                template = await self.user_capabilities_repository.get_working_hours_template(
                    uuid.UUID(request.template_id)
                )
                if not template:
                    raise NotFoundError("Working hours template", request.template_id)
            else:
                # Create custom template for user
                template = WorkingHoursTemplate(
                    id=uuid.uuid4(),
                    name=f"Custom Hours - {user_id}",
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
                
                template = await self.user_capabilities_repository.create_working_hours_template(template)
            
            # Set template for user
            user_capabilities.set_working_hours_template(template)
            await self.user_capabilities_repository.update(user_capabilities)
            
            logger.info(f"Set working hours for user {user_id} in business {business_id}")
            
            return self._convert_template_to_dto(template)
            
        except Exception as e:
            logger.error(f"Error setting user working hours: {str(e)}")
            raise BusinessLogicError(f"Failed to set working hours: {str(e)}")
    
    # Calendar Events Management
    async def create_calendar_event(
        self,
        business_id: uuid.UUID,
        user_id: str,
        request: CreateCalendarEventRequestDTO,
        current_user_id: str
    ) -> CalendarEventDTO:
        """Create a calendar event."""
        try:
            # Check permissions
            if user_id != current_user_id:
                await self._check_admin_permission(business_id, current_user_id)
            else:
                await self._check_member_permission(business_id, current_user_id)
            
            # Create calendar event
            event = CalendarEvent(
                id=uuid.uuid4(),
                user_id=user_id,
                business_id=business_id,
                title=request.title,
                description=request.description,
                event_type=CalendarEventType(request.event_type),
                start_datetime=request.start_datetime,
                end_datetime=request.end_datetime,
                is_all_day=request.is_all_day,
                timezone=request.timezone,
                recurrence_type=RecurrenceType(request.recurrence_type),
                recurrence_end_date=request.recurrence_end_date,
                recurrence_count=request.recurrence_count,
                recurrence_interval=request.recurrence_interval,
                recurrence_days_of_week=request.recurrence_days_of_week,
                blocks_scheduling=request.blocks_scheduling,
                allows_emergency_override=request.allows_emergency_override
            )
            
            # Save event
            saved_event = await self.user_capabilities_repository.add_calendar_event(
                user_id, business_id, event
            )
            
            logger.info(f"Created calendar event {saved_event.id} for user {user_id}")
            
            return self._convert_event_to_dto(saved_event)
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            raise BusinessLogicError(f"Failed to create calendar event: {str(e)}")
    
    async def get_calendar_events(
        self,
        business_id: uuid.UUID,
        user_id: str,
        start_date: date,
        end_date: date,
        current_user_id: str
    ) -> List[CalendarEventDTO]:
        """Get calendar events for a user within date range."""
        try:
            # Check permissions
            if user_id != current_user_id:
                await self._check_admin_permission(business_id, current_user_id)
            else:
                await self._check_member_permission(business_id, current_user_id)
            
            events = await self.user_capabilities_repository.get_calendar_events(
                user_id, business_id, start_date, end_date
            )
            
            return [self._convert_event_to_dto(event) for event in events]
            
        except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            raise BusinessLogicError(f"Failed to get calendar events: {str(e)}")
    
    async def delete_calendar_event(
        self,
        business_id: uuid.UUID,
        event_id: str,
        current_user_id: str
    ) -> bool:
        """Delete a calendar event."""
        try:
            # Check permissions (event owner or admin)
            await self._check_member_permission(business_id, current_user_id)
            
            success = await self.user_capabilities_repository.delete_calendar_event(uuid.UUID(event_id))
            
            if success:
                logger.info(f"Deleted calendar event {event_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting calendar event: {str(e)}")
            raise BusinessLogicError(f"Failed to delete calendar event: {str(e)}")
    
    # Time Off Management
    async def create_time_off_request(
        self,
        business_id: uuid.UUID,
        user_id: str,
        request: CreateTimeOffRequestDTO,
        current_user_id: str
    ) -> TimeOffRequestDTO:
        """Create a time off request."""
        try:
            # Check permissions
            if user_id != current_user_id:
                await self._check_admin_permission(business_id, current_user_id)
            else:
                await self._check_member_permission(business_id, current_user_id)
            
            # Create time off request
            time_off = TimeOffRequest(
                id=uuid.uuid4(),
                user_id=user_id,
                business_id=business_id,
                time_off_type=TimeOffType(request.time_off_type),
                start_date=request.start_date,
                end_date=request.end_date,
                reason=request.reason,
                notes=request.notes,
                requested_by=current_user_id,
                affects_scheduling=request.affects_scheduling,
                emergency_contact_allowed=request.emergency_contact_allowed
            )
            
            # Save request
            saved_request = await self.user_capabilities_repository.create_time_off_request(time_off)
            
            # Send notification to admins
            await self._notify_time_off_request(business_id, saved_request)
            
            logger.info(f"Created time off request {saved_request.id} for user {user_id}")
            
            return self._convert_time_off_to_dto(saved_request)
            
        except Exception as e:
            logger.error(f"Error creating time off request: {str(e)}")
            raise BusinessLogicError(f"Failed to create time off request: {str(e)}")
    
    async def approve_time_off_request(
        self,
        business_id: uuid.UUID,
        time_off_id: str,
        approved: bool,
        denial_reason: Optional[str],
        current_user_id: str
    ) -> TimeOffRequestDTO:
        """Approve or deny a time off request."""
        try:
            # Check admin permissions
            await self._check_admin_permission(business_id, current_user_id)
            
            if approved:
                time_off = await self.user_capabilities_repository.approve_time_off_request(
                    uuid.UUID(time_off_id), current_user_id
                )
            else:
                time_off = await self.user_capabilities_repository.deny_time_off_request(
                    uuid.UUID(time_off_id), current_user_id, denial_reason or "No reason provided"
                )
            
            # Send notification to requester
            await self._notify_time_off_decision(business_id, time_off)
            
            logger.info(f"{'Approved' if approved else 'Denied'} time off request {time_off_id}")
            
            return self._convert_time_off_to_dto(time_off)
            
        except Exception as e:
            logger.error(f"Error processing time off request: {str(e)}")
            raise BusinessLogicError(f"Failed to process time off request: {str(e)}")
    
    async def get_time_off_requests(
        self,
        business_id: uuid.UUID,
        user_id: Optional[str],
        status: Optional[str],
        current_user_id: str
    ) -> List[TimeOffRequestDTO]:
        """Get time off requests."""
        try:
            # Check permissions
            if user_id and user_id != current_user_id:
                await self._check_admin_permission(business_id, current_user_id)
            else:
                await self._check_member_permission(business_id, current_user_id)
            
            if user_id:
                requests = await self.user_capabilities_repository.get_time_off_requests(
                    user_id, business_id, status
                )
            else:
                # Admin getting all pending requests
                requests = await self.user_capabilities_repository.get_pending_time_off_requests(business_id)
            
            return [self._convert_time_off_to_dto(req) for req in requests]
            
        except Exception as e:
            logger.error(f"Error getting time off requests: {str(e)}")
            raise BusinessLogicError(f"Failed to get time off requests: {str(e)}")
    
    # Availability Management
    async def check_user_availability(
        self,
        business_id: uuid.UUID,
        request: AvailabilityCheckRequestDTO,
        current_user_id: str
    ) -> AvailabilityCheckResponseDTO:
        """Check availability for multiple users."""
        try:
            # Check permissions
            await self._check_member_permission(business_id, current_user_id)
            
            user_availability = []
            
            for user_id in request.user_ids:
                availability = await self._get_user_availability_for_period(
                    business_id, user_id, request.start_datetime, request.end_datetime,
                    request.include_time_off, request.include_calendar_events, request.include_working_hours
                )
                user_availability.append(availability)
            
            # Generate summary
            summary = self._generate_availability_summary(user_availability)
            
            return AvailabilityCheckResponseDTO(
                request_id=str(uuid.uuid4()),
                check_datetime=datetime.utcnow(),
                user_availability=user_availability,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error checking user availability: {str(e)}")
            raise BusinessLogicError(f"Failed to check availability: {str(e)}")
    
    async def get_team_availability_summary(
        self,
        business_id: uuid.UUID,
        start_date: date,
        end_date: date,
        current_user_id: str
    ) -> TeamAvailabilitySummaryDTO:
        """Get team availability summary."""
        try:
            # Check permissions
            await self._check_member_permission(business_id, current_user_id)
            
            summary = await self.user_capabilities_repository.get_team_availability_summary(
                business_id, start_date, end_date
            )
            
            return TeamAvailabilitySummaryDTO(
                business_id=str(business_id),
                start_date=start_date,
                end_date=end_date,
                total_team_members=summary.get("total_team_members", 0),
                available_members=summary.get("available_members", 0),
                members_on_time_off=summary.get("members_on_time_off", 0),
                members_with_limited_availability=summary.get("members_with_limited_availability", 0),
                daily_availability=summary.get("daily_availability", []),
                member_summaries=summary.get("member_summaries", []),
                peak_availability_hours=summary.get("peak_availability_hours", []),
                coverage_gaps=summary.get("coverage_gaps", [])
            )
            
        except Exception as e:
            logger.error(f"Error getting team availability summary: {str(e)}")
            raise BusinessLogicError(f"Failed to get team availability summary: {str(e)}")
    
    # Calendar Preferences Management
    async def update_calendar_preferences(
        self,
        business_id: uuid.UUID,
        user_id: str,
        preferences: CalendarPreferencesDTO,
        current_user_id: str
    ) -> CalendarPreferencesDTO:
        """Update user calendar preferences."""
        try:
            # Check permissions
            if user_id != current_user_id:
                await self._check_admin_permission(business_id, current_user_id)
            else:
                await self._check_member_permission(business_id, current_user_id)
            
            # Convert DTO to entity
            prefs_entity = CalendarPreferences(
                user_id=user_id,
                business_id=business_id,
                timezone=preferences.timezone,
                date_format=preferences.date_format,
                time_format=preferences.time_format,
                week_start_day=preferences.week_start_day,
                preferred_working_hours_template_id=uuid.UUID(preferences.preferred_working_hours_template_id) if preferences.preferred_working_hours_template_id else None,
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
            
            # Save preferences
            saved_prefs = await self.user_capabilities_repository.update_calendar_preferences(
                user_id, business_id, prefs_entity
            )
            
            logger.info(f"Updated calendar preferences for user {user_id}")
            
            return self._convert_preferences_to_dto(saved_prefs)
            
        except Exception as e:
            logger.error(f"Error updating calendar preferences: {str(e)}")
            raise BusinessLogicError(f"Failed to update calendar preferences: {str(e)}")
    
    async def get_calendar_preferences(
        self,
        business_id: uuid.UUID,
        user_id: str,
        current_user_id: str
    ) -> Optional[CalendarPreferencesDTO]:
        """Get user calendar preferences."""
        try:
            # Check permissions
            if user_id != current_user_id:
                await self._check_admin_permission(business_id, current_user_id)
            else:
                await self._check_member_permission(business_id, current_user_id)
            
            preferences = await self.user_capabilities_repository.get_calendar_preferences(
                user_id, business_id
            )
            
            return self._convert_preferences_to_dto(preferences) if preferences else None
            
        except Exception as e:
            logger.error(f"Error getting calendar preferences: {str(e)}")
            raise BusinessLogicError(f"Failed to get calendar preferences: {str(e)}")
    
    # Helper Methods
    async def _check_member_permission(self, business_id: uuid.UUID, user_id: str) -> None:
        """Check if user is a member of the business."""
        membership = await self.business_membership_repository.get_by_user_and_business(
            user_id, business_id
        )
        if not membership:
            raise ValidationError("User is not a member of this business")
    
    async def _check_admin_permission(self, business_id: uuid.UUID, user_id: str) -> None:
        """Check if user has admin permissions."""
        membership = await self.business_membership_repository.get_by_user_and_business(
            user_id, business_id
        )
        if not membership or membership.role not in ["admin", "owner"]:
            raise ValidationError("Insufficient permissions")
    
    async def _get_user_availability_for_period(
        self,
        business_id: uuid.UUID,
        user_id: str,
        start_datetime: datetime,
        end_datetime: datetime,
        include_time_off: bool,
        include_calendar_events: bool,
        include_working_hours: bool
    ) -> UserAvailabilityDTO:
        """Get detailed availability for a user in a time period."""
        # Get user capabilities
        user_capabilities = await self.user_capabilities_repository.get_by_user_id(business_id, user_id)
        if not user_capabilities:
            return UserAvailabilityDTO(
                user_id=user_id,
                date=start_datetime.date(),
                is_available=False,
                unavailable_reason="User capabilities not found"
            )
        
        # Check availability for each day in the period
        current_date = start_datetime.date()
        end_date = end_datetime.date()
        available_slots = []
        time_off_list = []
        calendar_events_list = []
        total_available_hours = 0.0
        
        while current_date <= end_date:
            # Get available slots for this date
            if user_capabilities.working_hours_template:
                day_slots = user_capabilities.get_available_time_slots_for_date(current_date)
                available_slots.extend([
                    {"start": slot[0], "end": slot[1]} for slot in day_slots
                ])
                
                # Calculate available hours
                for slot in day_slots:
                    duration = (slot[1] - slot[0]).total_seconds() / 3600
                    total_available_hours += duration
            
            current_date += timedelta(days=1)
        
        # Get time off if requested
        if include_time_off:
            time_off_requests = await self.user_capabilities_repository.get_time_off_requests(
                user_id, business_id, "approved"
            )
            time_off_list = [self._convert_time_off_to_dto(req) for req in time_off_requests
                           if req.start_date <= end_datetime.date() and req.end_date >= start_datetime.date()]
        
        # Get calendar events if requested
        if include_calendar_events:
            events = await self.user_capabilities_repository.get_calendar_events(
                user_id, business_id, start_datetime.date(), end_datetime.date()
            )
            calendar_events_list = [self._convert_event_to_dto(event) for event in events]
        
        # Determine overall availability
        is_available = len(available_slots) > 0 and not any(
            req.affects_scheduling for req in time_off_list
        )
        
        unavailable_reason = None
        if not is_available:
            if not available_slots:
                unavailable_reason = "No working hours configured"
            elif any(req.affects_scheduling for req in time_off_list):
                unavailable_reason = "On approved time off"
        
        return UserAvailabilityDTO(
            user_id=user_id,
            date=start_datetime.date(),
            available_slots=available_slots,
            total_available_hours=total_available_hours,
            working_hours=self._get_working_hours_for_date(user_capabilities, start_datetime.date()),
            time_off=time_off_list,
            calendar_events=calendar_events_list,
            is_available=is_available,
            unavailable_reason=unavailable_reason
        )
    
    def _get_working_hours_for_date(self, user_capabilities: UserCapabilities, check_date: date) -> Optional[Dict[str, Any]]:
        """Get working hours for a specific date."""
        if not user_capabilities.working_hours_template:
            return None
        
        day_of_week = check_date.weekday()
        working_hours = user_capabilities.working_hours_template.get_working_hours_for_day(day_of_week)
        
        if working_hours:
            return {
                "start": working_hours[0],
                "end": working_hours[1]
            }
        
        return None
    
    def _generate_availability_summary(self, user_availability: List[UserAvailabilityDTO]) -> Dict[str, Any]:
        """Generate summary from user availability data."""
        total_users = len(user_availability)
        available_users = sum(1 for ua in user_availability if ua.is_available)
        
        return {
            "total_users_checked": total_users,
            "available_users": available_users,
            "unavailable_users": total_users - available_users,
            "availability_percentage": (available_users / total_users * 100) if total_users > 0 else 0,
            "total_available_hours": sum(ua.total_available_hours for ua in user_availability)
        }
    
    async def _notify_time_off_request(self, business_id: uuid.UUID, time_off: TimeOffRequest) -> None:
        """Send notification about new time off request."""
        try:
            # Get business admins
            # This would typically involve getting admin users from the business
            # For now, we'll just log the notification
            logger.info(f"Time off request notification: {time_off.id} for user {time_off.user_id}")
            
            # TODO: Implement actual notification logic
            # - Get admin users
            # - Send email/SMS notifications
            # - Create in-app notifications
            
        except Exception as e:
            logger.warning(f"Failed to send time off request notification: {str(e)}")
    
    async def _notify_time_off_decision(self, business_id: uuid.UUID, time_off: TimeOffRequest) -> None:
        """Send notification about time off decision."""
        try:
            logger.info(f"Time off decision notification: {time_off.id} - {time_off.status}")
            
            # TODO: Implement actual notification logic
            # - Send notification to requester
            # - Update job scheduling if approved
            
        except Exception as e:
            logger.warning(f"Failed to send time off decision notification: {str(e)}")
    
    # DTO Conversion Methods
    def _convert_template_to_dto(self, template: WorkingHoursTemplate) -> WorkingHoursTemplateDTO:
        """Convert working hours template entity to DTO."""
        return WorkingHoursTemplateDTO(
            id=str(template.id),
            name=template.name,
            description=template.description,
            monday_start=template.monday_start,
            monday_end=template.monday_end,
            tuesday_start=template.tuesday_start,
            tuesday_end=template.tuesday_end,
            wednesday_start=template.wednesday_start,
            wednesday_end=template.wednesday_end,
            thursday_start=template.thursday_start,
            thursday_end=template.thursday_end,
            friday_start=template.friday_start,
            friday_end=template.friday_end,
            saturday_start=template.saturday_start,
            saturday_end=template.saturday_end,
            sunday_start=template.sunday_start,
            sunday_end=template.sunday_end,
            break_duration_minutes=template.break_duration_minutes,
            lunch_start_time=template.lunch_start_time,
            lunch_duration_minutes=template.lunch_duration_minutes,
            allows_flexible_start=template.allows_flexible_start,
            flexible_start_window_minutes=template.flexible_start_window_minutes,
            allows_overtime=template.allows_overtime,
            max_overtime_hours_per_day=float(template.max_overtime_hours_per_day),
            total_weekly_hours=float(template.get_total_weekly_hours())
        )
    
    def _convert_event_to_dto(self, event: CalendarEvent) -> CalendarEventDTO:
        """Convert calendar event entity to DTO."""
        return CalendarEventDTO(
            id=str(event.id),
            user_id=event.user_id,
            business_id=str(event.business_id),
            title=event.title,
            description=event.description,
            event_type=event.event_type.value,
            start_datetime=event.start_datetime,
            end_datetime=event.end_datetime,
            is_all_day=event.is_all_day,
            timezone=event.timezone,
            recurrence_type=event.recurrence_type.value,
            recurrence_end_date=event.recurrence_end_date,
            recurrence_count=event.recurrence_count,
            recurrence_interval=event.recurrence_interval,
            recurrence_days_of_week=event.recurrence_days_of_week,
            blocks_scheduling=event.blocks_scheduling,
            allows_emergency_override=event.allows_emergency_override,
            created_date=event.created_date,
            last_modified=event.last_modified,
            is_active=event.is_active
        )
    
    def _convert_time_off_to_dto(self, time_off: TimeOffRequest) -> TimeOffRequestDTO:
        """Convert time off request entity to DTO."""
        return TimeOffRequestDTO(
            id=str(time_off.id),
            user_id=time_off.user_id,
            business_id=str(time_off.business_id),
            time_off_type=time_off.time_off_type.value,
            start_date=time_off.start_date,
            end_date=time_off.end_date,
            reason=time_off.reason,
            notes=time_off.notes,
            status=time_off.status,
            requested_by=time_off.requested_by,
            approved_by=time_off.approved_by,
            approval_date=time_off.approval_date,
            denial_reason=time_off.denial_reason,
            affects_scheduling=time_off.affects_scheduling,
            emergency_contact_allowed=time_off.emergency_contact_allowed,
            created_date=time_off.created_date,
            last_modified=time_off.last_modified,
            duration_days=time_off.get_duration_days()
        )
    
    def _convert_preferences_to_dto(self, preferences: CalendarPreferences) -> CalendarPreferencesDTO:
        """Convert calendar preferences entity to DTO."""
        return CalendarPreferencesDTO(
            user_id=preferences.user_id,
            business_id=str(preferences.business_id),
            timezone=preferences.timezone,
            date_format=preferences.date_format,
            time_format=preferences.time_format,
            week_start_day=preferences.week_start_day,
            preferred_working_hours_template_id=str(preferences.preferred_working_hours_template_id) if preferences.preferred_working_hours_template_id else None,
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
            travel_buffer_percentage=float(preferences.travel_buffer_percentage),
            job_buffer_minutes=preferences.job_buffer_minutes,
            created_date=preferences.created_date,
            last_modified=preferences.last_modified
        ) 