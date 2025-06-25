"""
Manage Activities Use Case

Handles the business logic for activity management, timeline generation,
and activity template operations.
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ...dto.activity_dto import (
    ActivityCreateDTO, ActivityUpdateDTO, ActivityResponseDTO, ActivityListDTO,
    ActivityTemplateCreateDTO, ActivityTemplateResponseDTO, TimelineRequestDTO,
    TimelineResponseDTO, ActivityReminderDTO
)
from app.domain.repositories.activity_repository import ActivityRepository, ActivityTemplateRepository
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.entities.activity import Activity, ActivityTemplate, ActivityType, ActivityStatus, ActivityPriority
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, DomainValidationError
from ...exceptions.application_exceptions import (
    ApplicationError, ValidationError, BusinessLogicError, PermissionDeniedError
)


class ManageActivitiesUseCase:
    """
    Use case for managing activities and timeline with comprehensive business logic.
    
    Handles activity creation, updates, deletion, timeline generation, and template management
    with proper business validation and permission checks.
    """
    
    def __init__(
        self,
        activity_repository: ActivityRepository,
        template_repository: ActivityTemplateRepository,
        contact_repository: ContactRepository,
        membership_repository: BusinessMembershipRepository
    ):
        self.activity_repository = activity_repository
        self.template_repository = template_repository
        self.contact_repository = contact_repository
        self.membership_repository = membership_repository
    
    # Activity CRUD Operations
    
    async def create_activity(self, dto: ActivityCreateDTO, user_id: str) -> ActivityResponseDTO:
        """
        Create a new activity with validation.
        
        Args:
            dto: Activity creation data
            user_id: ID of the user creating the activity
            
        Returns:
            ActivityResponseDTO with created activity information
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business rules are violated
            PermissionError: If user lacks permission
        """
        # Validate user has permission to edit contacts in this business
        await self._validate_user_permission(dto.business_id, user_id, "edit_contacts")
        
        # Validate contact exists and user has access
        contact = await self.contact_repository.get_by_id(dto.contact_id)
        if not contact or contact.business_id != dto.business_id:
            raise ValidationError("Contact not found or access denied")
        
        # Create activity from template if specified
        if dto.template_id:
            template = await self.template_repository.get_template_by_id(dto.template_id)
            if not template or template.business_id != dto.business_id:
                raise ValidationError("Template not found or access denied")
            
            activity = Activity.from_template(
                template=template,
                business_id=dto.business_id,
                contact_id=dto.contact_id,
                created_by=user_id,
                scheduled_date=dto.scheduled_date,
                title=dto.title or template.name,
                description=dto.description or template.description,
                priority=dto.priority or ActivityPriority.MEDIUM,
                assigned_to=dto.assigned_to,
                due_date=dto.due_date
            )
        else:
            # Create activity directly
            activity = Activity.create_activity(
                business_id=dto.business_id,
                contact_id=dto.contact_id,
                activity_type=dto.activity_type,
                title=dto.title,
                created_by=user_id,
                description=dto.description,
                scheduled_date=dto.scheduled_date,
                due_date=dto.due_date,
                priority=dto.priority,
                assigned_to=dto.assigned_to,
                duration_minutes=dto.duration_minutes,
                location=dto.location,
                tags=dto.tags,
                metadata=dto.metadata
            )
        
        # Add participants if specified
        if dto.participants:
            for participant in dto.participants:
                activity.add_participant(
                    user_id=participant['user_id'],
                    name=participant['name'],
                    role=participant.get('role', 'participant'),
                    is_primary=participant.get('is_primary', False)
                )
        
        # Add reminders if specified
        if dto.reminders:
            for reminder in dto.reminders:
                activity.add_reminder(
                    reminder_time=reminder['reminder_time'],
                    reminder_type=reminder.get('reminder_type', 'notification'),
                    message=reminder.get('message')
                )
        
        # Save to repository
        created_activity = await self.activity_repository.create(activity)
        
        return self._activity_to_response_dto(created_activity)
    
    async def get_activity(self, activity_id: uuid.UUID, user_id: str) -> ActivityResponseDTO:
        """
        Get an activity by ID with permission validation.
        
        Args:
            activity_id: ID of the activity to retrieve
            user_id: ID of the user requesting the activity
            
        Returns:
            ActivityResponseDTO with activity information
            
        Raises:
            EntityNotFoundError: If activity doesn't exist
            PermissionError: If user lacks permission
        """
        activity = await self.activity_repository.get_by_id(activity_id)
        if not activity:
            raise EntityNotFoundError("Activity not found")
        
        # Validate user has permission to view contacts in this business
        await self._validate_user_permission(activity.business_id, user_id, "view_contacts")
        
        return self._activity_to_response_dto(activity)
    
    async def update_activity(self, dto: ActivityUpdateDTO, user_id: str) -> ActivityResponseDTO:
        """
        Update an existing activity.
        
        Args:
            dto: Activity update data
            user_id: ID of the user updating the activity
            
        Returns:
            ActivityResponseDTO with updated activity information
            
        Raises:
            EntityNotFoundError: If activity doesn't exist
            ValidationError: If validation fails
            PermissionError: If user lacks permission
        """
        # Get existing activity
        activity = await self.activity_repository.get_by_id(dto.activity_id)
        if not activity:
            raise EntityNotFoundError("Activity not found")
        
        # Validate user has permission to edit contacts in this business
        await self._validate_user_permission(activity.business_id, user_id, "edit_contacts")
        
        # Update activity fields
        if dto.title is not None:
            activity.title = dto.title
        if dto.description is not None:
            activity.description = dto.description
        if dto.status is not None:
            activity.update_status(dto.status, user_id, dto.notes)
        if dto.priority is not None:
            activity.priority = dto.priority
        if dto.scheduled_date is not None:
            if dto.scheduled_date != activity.scheduled_date:
                activity.reschedule(dto.scheduled_date, user_id, dto.reschedule_reason)
            else:
                activity.scheduled_date = dto.scheduled_date
        if dto.due_date is not None:
            activity.due_date = dto.due_date
        if dto.duration_minutes is not None:
            activity.duration_minutes = dto.duration_minutes
        if dto.location is not None:
            activity.location = dto.location
        if dto.assigned_to is not None:
            activity.assigned_to = dto.assigned_to
        if dto.tags is not None:
            activity.tags = dto.tags
        if dto.metadata is not None:
            activity.metadata.update(dto.metadata)
        
        activity.last_modified = datetime.utcnow()
        
        # Save updated activity
        updated_activity = await self.activity_repository.update(activity)
        
        return self._activity_to_response_dto(updated_activity)
    
    async def delete_activity(self, activity_id: uuid.UUID, user_id: str) -> bool:
        """
        Delete an activity.
        
        Args:
            activity_id: ID of the activity to delete
            user_id: ID of the user deleting the activity
            
        Returns:
            True if deleted successfully
            
        Raises:
            EntityNotFoundError: If activity doesn't exist
            PermissionError: If user lacks permission
        """
        # Get activity to check permissions
        activity = await self.activity_repository.get_by_id(activity_id)
        if not activity:
            raise EntityNotFoundError("Activity not found")
        
        # Validate user has permission to delete activities in this business
        await self._validate_user_permission(activity.business_id, user_id, "delete_contacts")
        
        return await self.activity_repository.delete(activity_id)
    
    # Timeline Operations
    
    async def get_contact_timeline(self, dto: TimelineRequestDTO, user_id: str) -> TimelineResponseDTO:
        """
        Get activity timeline for a contact.
        
        Args:
            dto: Timeline request parameters
            user_id: ID of the user requesting the timeline
            
        Returns:
            TimelineResponseDTO with timeline activities
            
        Raises:
            PermissionError: If user lacks permission
        """
        # Validate user has permission to view contacts in this business
        await self._validate_user_permission(dto.business_id, user_id, "view_contacts")
        
        # Get activities from repository
        activities = await self.activity_repository.get_contact_timeline(
            contact_id=dto.contact_id,
            business_id=dto.business_id,
            start_date=dto.start_date,
            end_date=dto.end_date,
            activity_types=dto.activity_types,
            skip=dto.skip,
            limit=dto.limit
        )
        
        # Get total count
        total_count = await self.activity_repository.get_contact_activity_count(
            contact_id=dto.contact_id,
            business_id=dto.business_id,
            start_date=dto.start_date,
            end_date=dto.end_date,
            activity_types=dto.activity_types
        )
        
        # Convert to timeline entries
        timeline_entries = []
        for activity in activities:
            timeline_entries.append(activity.to_timeline_entry())
        
        return TimelineResponseDTO(
            contact_id=dto.contact_id,
            timeline_entries=timeline_entries,
            total_count=total_count,
            skip=dto.skip,
            limit=dto.limit,
            start_date=dto.start_date,
            end_date=dto.end_date
        )
    
    async def get_user_activities(
        self,
        business_id: uuid.UUID,
        user_id: str,
        statuses: Optional[List[ActivityStatus]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> ActivityListDTO:
        """
        Get activities assigned to a user.
        
        Args:
            business_id: Business ID
            user_id: User ID for both permission check and activity filter
            statuses: Optional status filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            ActivityListDTO with user's activities
        """
        # Validate user has permission to view activities in this business
        await self._validate_user_permission(business_id, user_id, "view_contacts")
        
        # Get activities from repository
        activities = await self.activity_repository.get_user_activities(
            business_id=business_id,
            user_id=user_id,
            statuses=statuses,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        # Convert to response DTOs
        activity_responses = [self._activity_to_response_dto(activity) for activity in activities]
        
        return ActivityListDTO(
            activities=activity_responses,
            total_count=len(activity_responses),  # This would need a separate count query in production
            skip=skip,
            limit=limit
        )
    
    async def get_overdue_activities(self, business_id: uuid.UUID, user_id: str, assigned_to: Optional[str] = None) -> List[ActivityResponseDTO]:
        """
        Get overdue activities for a business or user.
        
        Args:
            business_id: Business ID
            user_id: ID of the user requesting overdue activities
            assigned_to: Optional filter for specific user
            
        Returns:
            List of overdue activities
        """
        # Validate user has permission to view activities in this business
        await self._validate_user_permission(business_id, user_id, "view_contacts")
        
        # Get overdue activities
        activities = await self.activity_repository.get_overdue_activities(
            business_id=business_id,
            assigned_to=assigned_to
        )
        
        return [self._activity_to_response_dto(activity) for activity in activities]
    
    async def get_upcoming_activities(
        self,
        business_id: uuid.UUID,
        user_id: str,
        days_ahead: int = 7,
        assigned_to: Optional[str] = None
    ) -> List[ActivityResponseDTO]:
        """
        Get upcoming activities for a business or user.
        
        Args:
            business_id: Business ID
            user_id: ID of the user requesting upcoming activities
            days_ahead: Number of days to look ahead
            assigned_to: Optional filter for specific user
            
        Returns:
            List of upcoming activities
        """
        # Validate user has permission to view activities in this business
        await self._validate_user_permission(business_id, user_id, "view_contacts")
        
        # Get upcoming activities
        activities = await self.activity_repository.get_upcoming_activities(
            business_id=business_id,
            days_ahead=days_ahead,
            assigned_to=assigned_to
        )
        
        return [self._activity_to_response_dto(activity) for activity in activities]
    
    # Template Operations
    
    async def create_activity_template(self, dto: ActivityTemplateCreateDTO, user_id: str) -> ActivityTemplateResponseDTO:
        """
        Create a new activity template.
        
        Args:
            dto: Template creation data
            user_id: ID of the user creating the template
            
        Returns:
            ActivityTemplateResponseDTO with created template
        """
        # Validate user has permission to manage templates in this business
        await self._validate_user_permission(dto.business_id, user_id, "edit_contacts")
        
        # Create template
        template = ActivityTemplate(
            template_id=uuid.uuid4(),
            name=dto.name,
            description=dto.description,
            activity_type=dto.activity_type,
            default_duration=dto.default_duration,
            default_reminders=dto.default_reminders,
            default_participants=dto.default_participants,
            custom_fields=dto.custom_fields,
            created_by=user_id
        )
        
        # Save to repository
        created_template = await self.template_repository.create_template(template)
        
        return self._template_to_response_dto(created_template)
    
    async def get_business_templates(
        self,
        business_id: uuid.UUID,
        user_id: str,
        activity_type: Optional[ActivityType] = None
    ) -> List[ActivityTemplateResponseDTO]:
        """
        Get activity templates for a business.
        
        Args:
            business_id: Business ID
            user_id: ID of the user requesting templates
            activity_type: Optional filter by activity type
            
        Returns:
            List of activity templates
        """
        # Validate user has permission to view activities in this business
        await self._validate_user_permission(business_id, user_id, "view_contacts")
        
        # Get templates from repository
        templates = await self.template_repository.get_business_templates(
            business_id=business_id,
            activity_type=activity_type,
            is_active=True
        )
        
        return [self._template_to_response_dto(template) for template in templates]
    
    # Reminder Operations
    
    async def get_pending_reminders(self, business_id: uuid.UUID, user_id: str) -> List[ActivityReminderDTO]:
        """
        Get pending reminders for activities.
        
        Args:
            business_id: Business ID
            user_id: ID of the user requesting reminders
            
        Returns:
            List of pending reminders
        """
        # Validate user has permission to view activities in this business
        await self._validate_user_permission(business_id, user_id, "view_contacts")
        
        # Get activities with pending reminders
        before_date = datetime.utcnow() + timedelta(hours=1)  # Next hour
        activities = await self.activity_repository.get_pending_reminders(
            business_id=business_id,
            before_date=before_date
        )
        
        # Extract reminders
        reminders = []
        for activity in activities:
            for reminder in activity.reminders:
                if not reminder.is_sent and reminder.reminder_time <= before_date:
                    reminders.append(ActivityReminderDTO(
                        reminder_id=reminder.reminder_id,
                        activity_id=activity.id,
                        contact_id=activity.contact_id,
                        activity_title=activity.title,
                        reminder_time=reminder.reminder_time,
                        reminder_type=reminder.reminder_type,
                        message=reminder.message
                    ))
        
        return reminders
    
    async def mark_reminder_sent(self, activity_id: uuid.UUID, reminder_id: uuid.UUID, user_id: str) -> bool:
        """
        Mark a reminder as sent.
        
        Args:
            activity_id: Activity ID
            reminder_id: Reminder ID
            user_id: ID of the user marking the reminder
            
        Returns:
            True if marked successfully
        """
        # Get activity
        activity = await self.activity_repository.get_by_id(activity_id)
        if not activity:
            raise EntityNotFoundError("Activity not found")
        
        # Validate user has permission
        await self._validate_user_permission(activity.business_id, user_id, "edit_contacts")
        
        # Mark reminder as sent
        activity.mark_reminder_sent(reminder_id)
        
        # Save updated activity
        await self.activity_repository.update(activity)
        
        return True
    
    # Statistics and Analytics
    
    async def get_activity_statistics(
        self,
        business_id: uuid.UUID,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filter_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get activity statistics for a business or user.
        
        Args:
            business_id: Business ID
            user_id: ID of the user requesting statistics
            start_date: Optional start date filter
            end_date: Optional end date filter
            filter_user_id: Optional filter for specific user's activities
            
        Returns:
            Dictionary with activity statistics
        """
        # Validate user has permission to view activities in this business
        await self._validate_user_permission(business_id, user_id, "view_contacts")
        
        # Get statistics from repository
        return await self.activity_repository.get_activity_statistics(
            business_id=business_id,
            start_date=start_date,
            end_date=end_date,
            user_id=filter_user_id
        )
    
    async def get_contact_activity_summary(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get activity summary for a specific contact.
        
        Args:
            contact_id: Contact ID
            business_id: Business ID
            user_id: ID of the user requesting summary
            
        Returns:
            Dictionary with contact activity summary
        """
        # Validate user has permission to view activities in this business
        await self._validate_user_permission(business_id, user_id, "view_contacts")
        
        # Get summary from repository
        return await self.activity_repository.get_contact_activity_summary(
            contact_id=contact_id,
            business_id=business_id
        )
    
    # Helper Methods
    
    async def _validate_user_permission(self, business_id: uuid.UUID, user_id: str, permission: str) -> None:
        """Validate that user has required permission for the business."""
        membership = await self.membership_repository.get_by_business_and_user(business_id, user_id)
        
        if not membership:
            raise PermissionDeniedError("User is not a member of this business")
        
        if not membership.is_active:
            raise PermissionDeniedError("User membership is inactive")
        
        if not membership.has_permission(permission):
            raise PermissionDeniedError(f"User does not have permission: {permission}")
    
    def _activity_to_response_dto(self, activity: Activity) -> ActivityResponseDTO:
        """Convert Activity entity to response DTO."""
        return ActivityResponseDTO(
            id=activity.id,
            business_id=activity.business_id,
            contact_id=activity.contact_id,
            template_id=activity.template_id,
            parent_activity_id=activity.parent_activity_id,
            activity_type=activity.activity_type,
            title=activity.title,
            description=activity.description,
            status=activity.status,
            priority=activity.priority,
            scheduled_date=activity.scheduled_date,
            due_date=activity.due_date,
            completed_date=activity.completed_date,
            duration_minutes=activity.duration_minutes,
            location=activity.location,
            participants=[
                {
                    'user_id': p.user_id,
                    'name': p.name,
                    'role': p.role,
                    'is_primary': p.is_primary
                } for p in activity.participants
            ],
            reminders=[
                {
                    'reminder_id': str(r.reminder_id),
                    'reminder_time': r.reminder_time,
                    'reminder_type': r.reminder_type,
                    'message': r.message,
                    'is_sent': r.is_sent,
                    'sent_at': r.sent_at
                } for r in activity.reminders
            ],
            metadata=activity.metadata,
            tags=activity.tags,
            created_by=activity.created_by,
            assigned_to=activity.assigned_to,
            created_date=activity.created_date,
            last_modified=activity.last_modified,
            is_overdue=activity.is_overdue(),
            duration_display=activity.get_duration_display(),
            status_display=activity.get_status_display(),
            priority_display=activity.get_priority_display(),
            type_display=activity.get_type_display()
        )
    
    def _template_to_response_dto(self, template: ActivityTemplate) -> ActivityTemplateResponseDTO:
        """Convert ActivityTemplate entity to response DTO."""
        return ActivityTemplateResponseDTO(
            template_id=template.template_id,
            name=template.name,
            description=template.description,
            activity_type=template.activity_type,
            default_duration=template.default_duration,
            default_reminders=template.default_reminders,
            default_participants=template.default_participants,
            custom_fields=template.custom_fields,
            is_active=template.is_active,
            created_by=template.created_by,
            created_date=template.created_date
        ) 