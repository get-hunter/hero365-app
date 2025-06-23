"""
Reminder and Notification Service

Handles automated reminders for activities with multiple delivery methods,
smart scheduling, and notification preferences.
"""

import uuid
import asyncio
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

from ..dto.activity_dto import ActivityReminderDTO, NotificationDTO
from ...domain.repositories.activity_repository import ActivityRepository
from ...domain.repositories.contact_repository import ContactRepository
from ...domain.entities.activity import Activity, ActivityStatus, ActivityPriority
from ...application.ports.email_service import EmailService
from ...application.ports.sms_service import SMSService

logger = logging.getLogger(__name__)


class ReminderType(Enum):
    """Types of reminders that can be sent."""
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    """Priority levels for notifications."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class ReminderTemplate:
    """Template for reminder messages."""
    template_id: str
    name: str
    subject_template: str
    body_template: str
    reminder_type: ReminderType
    activity_types: List[str]
    variables: List[str]
    is_active: bool = True


@dataclass
class NotificationPreference:
    """User notification preferences."""
    user_id: str
    reminder_types: Set[ReminderType]
    quiet_hours_start: Optional[int] = None  # Hour of day (0-23)
    quiet_hours_end: Optional[int] = None
    timezone: str = "UTC"
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    frequency_limit: int = 10  # Max notifications per day


@dataclass
class ReminderSchedule:
    """Schedule configuration for reminders."""
    activity_id: uuid.UUID
    reminder_id: uuid.UUID
    reminder_time: datetime
    reminder_type: ReminderType
    recipient_id: str
    template_id: str
    is_sent: bool = False
    sent_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = None


class ReminderNotificationService:
    """
    Service for managing activity reminders and notifications.
    
    Provides automated reminder scheduling, delivery through multiple channels,
    notification preferences management, and delivery tracking.
    """
    
    def __init__(
        self,
        activity_repository: ActivityRepository,
        contact_repository: ContactRepository,
        email_service: EmailService,
        sms_service: SMSService
    ):
        self.activity_repository = activity_repository
        self.contact_repository = contact_repository
        self.email_service = email_service
        self.sms_service = sms_service
        
        # In-memory storage for preferences and templates
        # In production, these would be stored in database
        self.notification_preferences: Dict[str, NotificationPreference] = {}
        self.reminder_templates: Dict[str, ReminderTemplate] = {}
        self.scheduled_reminders: Dict[str, ReminderSchedule] = {}
        
        # Initialize default templates
        self._initialize_default_templates()
    
    async def schedule_activity_reminders(
        self,
        activity: Activity,
        user_id: str,
        custom_reminders: Optional[List[Dict[str, Any]]] = None
    ) -> List[uuid.UUID]:
        """
        Schedule reminders for an activity.
        
        Args:
            activity: Activity to schedule reminders for
            user_id: User scheduling the reminders
            custom_reminders: Optional custom reminder configurations
            
        Returns:
            List of reminder IDs that were scheduled
        """
        reminder_ids = []
        
        # Use custom reminders if provided, otherwise use defaults
        if custom_reminders:
            reminder_configs = custom_reminders
        else:
            reminder_configs = self._get_default_reminder_configs(activity)
        
        for config in reminder_configs:
            reminder_id = await self._schedule_single_reminder(
                activity=activity,
                config=config,
                user_id=user_id
            )
            if reminder_id:
                reminder_ids.append(reminder_id)
        
        return reminder_ids
    
    async def process_pending_reminders(self) -> Dict[str, int]:
        """
        Process all pending reminders that are due to be sent.
        
        Returns:
            Dictionary with counts of processed reminders by status
        """
        current_time = datetime.utcnow()
        stats = {
            'processed': 0,
            'sent': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Get pending reminders from repository
        pending_reminders = await self.activity_repository.get_pending_reminders(
            due_before=current_time + timedelta(minutes=5)  # 5-minute buffer
        )
        
        for reminder in pending_reminders:
            stats['processed'] += 1
            
            try:
                # Check if user is in quiet hours
                if await self._is_in_quiet_hours(reminder.recipient_id, current_time):
                    # Reschedule for after quiet hours
                    new_time = await self._calculate_next_available_time(
                        reminder.recipient_id, current_time
                    )
                    await self._reschedule_reminder(reminder.reminder_id, new_time)
                    stats['skipped'] += 1
                    continue
                
                # Check frequency limits
                if await self._exceeds_frequency_limit(reminder.recipient_id, current_time):
                    # Reschedule for next day
                    new_time = current_time + timedelta(days=1)
                    await self._reschedule_reminder(reminder.reminder_id, new_time)
                    stats['skipped'] += 1
                    continue
                
                # Send the reminder
                success = await self._send_reminder(reminder)
                
                if success:
                    stats['sent'] += 1
                    # Mark as sent in repository
                    await self.activity_repository.mark_reminder_sent(
                        reminder.activity_id,
                        reminder.reminder_id,
                        datetime.utcnow()
                    )
                else:
                    stats['failed'] += 1
                    # Handle retry logic
                    await self._handle_reminder_failure(reminder)
                
            except Exception as e:
                logger.error(f"Error processing reminder {reminder.reminder_id}: {str(e)}")
                stats['failed'] += 1
                await self._handle_reminder_failure(reminder)
        
        return stats
    
    async def update_notification_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Update notification preferences for a user.
        
        Args:
            user_id: User to update preferences for
            preferences: Dictionary of preference settings
            
        Returns:
            True if preferences were updated successfully
        """
        try:
            # Convert reminder types from strings
            reminder_types = set()
            if preferences.get('email_enabled', True):
                reminder_types.add(ReminderType.EMAIL)
            if preferences.get('sms_enabled', True):
                reminder_types.add(ReminderType.SMS)
            if preferences.get('push_enabled', True):
                reminder_types.add(ReminderType.PUSH_NOTIFICATION)
            
            notification_pref = NotificationPreference(
                user_id=user_id,
                reminder_types=reminder_types,
                quiet_hours_start=preferences.get('quiet_hours_start'),
                quiet_hours_end=preferences.get('quiet_hours_end'),
                timezone=preferences.get('timezone', 'UTC'),
                email_enabled=preferences.get('email_enabled', True),
                sms_enabled=preferences.get('sms_enabled', True),
                push_enabled=preferences.get('push_enabled', True),
                frequency_limit=preferences.get('frequency_limit', 10)
            )
            
            self.notification_preferences[user_id] = notification_pref
            return True
            
        except Exception as e:
            logger.error(f"Error updating notification preferences for user {user_id}: {str(e)}")
            return False
    
    async def get_user_notification_preferences(
        self,
        user_id: str
    ) -> Optional[NotificationPreference]:
        """Get notification preferences for a user."""
        return self.notification_preferences.get(user_id)
    
    async def create_reminder_template(
        self,
        template_data: Dict[str, Any],
        user_id: str
    ) -> str:
        """
        Create a new reminder template.
        
        Args:
            template_data: Template configuration
            user_id: User creating the template
            
        Returns:
            Template ID
        """
        template_id = str(uuid.uuid4())
        
        template = ReminderTemplate(
            template_id=template_id,
            name=template_data['name'],
            subject_template=template_data['subject_template'],
            body_template=template_data['body_template'],
            reminder_type=ReminderType(template_data['reminder_type']),
            activity_types=template_data.get('activity_types', []),
            variables=template_data.get('variables', []),
            is_active=template_data.get('is_active', True)
        )
        
        self.reminder_templates[template_id] = template
        return template_id
    
    async def get_reminder_statistics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get reminder and notification statistics.
        
        Args:
            business_id: Business to get statistics for
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with reminder statistics
        """
        # Get reminder statistics from repository
        stats = await self.activity_repository.get_reminder_statistics(
            business_id=business_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            'total_reminders_scheduled': stats.get('total_scheduled', 0),
            'reminders_sent': stats.get('sent', 0),
            'reminders_failed': stats.get('failed', 0),
            'reminders_pending': stats.get('pending', 0),
            'delivery_rate': (stats.get('sent', 0) / stats.get('total_scheduled', 1)) * 100,
            'reminders_by_type': stats.get('by_type', {}),
            'reminders_by_day': stats.get('by_day', {}),
            'average_delivery_time': stats.get('avg_delivery_time', 0)
        }
    
    async def cancel_activity_reminders(
        self,
        activity_id: uuid.UUID,
        user_id: str
    ) -> bool:
        """
        Cancel all reminders for an activity.
        
        Args:
            activity_id: Activity to cancel reminders for
            user_id: User canceling the reminders
            
        Returns:
            True if reminders were canceled successfully
        """
        try:
            success = await self.activity_repository.cancel_activity_reminders(
                activity_id=activity_id
            )
            
            if success:
                logger.info(f"Canceled reminders for activity {activity_id} by user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error canceling reminders for activity {activity_id}: {str(e)}")
            return False
    
    async def send_immediate_notification(
        self,
        notification: NotificationDTO,
        user_id: str
    ) -> bool:
        """
        Send an immediate notification (not scheduled).
        
        Args:
            notification: Notification to send
            user_id: User to send notification to
            
        Returns:
            True if notification was sent successfully
        """
        try:
            # Get user preferences
            preferences = await self.get_user_notification_preferences(user_id)
            if not preferences:
                # Use default preferences
                preferences = NotificationPreference(
                    user_id=user_id,
                    reminder_types={ReminderType.EMAIL, ReminderType.IN_APP}
                )
            
            # Check if notification type is enabled
            notification_type = ReminderType(notification.notification_type)
            if notification_type not in preferences.reminder_types:
                logger.info(f"Notification type {notification_type} disabled for user {user_id}")
                return False
            
            # Send based on type
            if notification_type == ReminderType.EMAIL:
                return await self._send_email_notification(notification, user_id)
            elif notification_type == ReminderType.SMS:
                return await self._send_sms_notification(notification, user_id)
            elif notification_type == ReminderType.PUSH_NOTIFICATION:
                return await self._send_push_notification(notification, user_id)
            elif notification_type == ReminderType.IN_APP:
                return await self._send_in_app_notification(notification, user_id)
            else:
                logger.warning(f"Unsupported notification type: {notification_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending immediate notification to user {user_id}: {str(e)}")
            return False
    
    # Private helper methods
    
    def _initialize_default_templates(self):
        """Initialize default reminder templates."""
        default_templates = [
            {
                'template_id': 'default_email_reminder',
                'name': 'Default Email Reminder',
                'subject_template': 'Reminder: {activity_title}',
                'body_template': '''
                    Hi {user_name},
                    
                    This is a reminder about your upcoming activity:
                    
                    Title: {activity_title}
                    Scheduled: {scheduled_date}
                    Contact: {contact_name}
                    
                    {activity_description}
                    
                    Best regards,
                    Hero365 Team
                ''',
                'reminder_type': ReminderType.EMAIL,
                'activity_types': [],
                'variables': ['activity_title', 'scheduled_date', 'contact_name', 'activity_description', 'user_name']
            },
            {
                'template_id': 'urgent_task_reminder',
                'name': 'Urgent Task Reminder',
                'subject_template': '🚨 URGENT: {activity_title}',
                'body_template': '''
                    URGENT REMINDER
                    
                    Task: {activity_title}
                    Due: {due_date}
                    Priority: {priority}
                    
                    This task requires immediate attention.
                    
                    {activity_description}
                ''',
                'reminder_type': ReminderType.EMAIL,
                'activity_types': ['task'],
                'variables': ['activity_title', 'due_date', 'priority', 'activity_description']
            },
            {
                'template_id': 'appointment_sms',
                'name': 'Appointment SMS Reminder',
                'subject_template': '',
                'body_template': 'Reminder: {activity_title} at {scheduled_time} with {contact_name}. Reply CONFIRM to acknowledge.',
                'reminder_type': ReminderType.SMS,
                'activity_types': ['interaction'],
                'variables': ['activity_title', 'scheduled_time', 'contact_name']
            }
        ]
        
        for template_data in default_templates:
            template = ReminderTemplate(
                template_id=template_data['template_id'],
                name=template_data['name'],
                subject_template=template_data['subject_template'],
                body_template=template_data['body_template'],
                reminder_type=template_data['reminder_type'],
                activity_types=template_data['activity_types'],
                variables=template_data['variables'],
                is_active=True
            )
            self.reminder_templates[template_data['template_id']] = template
    
    def _get_default_reminder_configs(self, activity: Activity) -> List[Dict[str, Any]]:
        """Get default reminder configurations based on activity type and priority."""
        configs = []
        
        # Base reminders for all activities
        if activity.scheduled_date:
            # 1 day before
            configs.append({
                'reminder_time': activity.scheduled_date - timedelta(days=1),
                'reminder_type': ReminderType.EMAIL.value,
                'template_id': 'default_email_reminder'
            })
            
            # 1 hour before
            configs.append({
                'reminder_time': activity.scheduled_date - timedelta(hours=1),
                'reminder_type': ReminderType.PUSH_NOTIFICATION.value,
                'template_id': 'default_email_reminder'
            })
        
        # Priority-based reminders
        if activity.priority in [ActivityPriority.HIGH, ActivityPriority.URGENT]:
            if activity.due_date:
                # Additional reminder for high priority
                configs.append({
                    'reminder_time': activity.due_date - timedelta(hours=2),
                    'reminder_type': ReminderType.SMS.value,
                    'template_id': 'urgent_task_reminder'
                })
        
        # Activity type-specific reminders
        if activity.activity_type.value == 'interaction' and activity.scheduled_date:
            # SMS reminder for appointments
            configs.append({
                'reminder_time': activity.scheduled_date - timedelta(minutes=30),
                'reminder_type': ReminderType.SMS.value,
                'template_id': 'appointment_sms'
            })
        
        return configs
    
    async def _schedule_single_reminder(
        self,
        activity: Activity,
        config: Dict[str, Any],
        user_id: str
    ) -> Optional[uuid.UUID]:
        """Schedule a single reminder."""
        try:
            reminder_id = uuid.uuid4()
            
            # Create reminder in repository
            success = await self.activity_repository.create_activity_reminder(
                activity_id=activity.id,
                reminder_id=reminder_id,
                reminder_time=config['reminder_time'],
                reminder_type=config['reminder_type'],
                template_id=config.get('template_id', 'default_email_reminder'),
                recipient_id=config.get('recipient_id', activity.assigned_to or user_id),
                metadata=config.get('metadata', {})
            )
            
            if success:
                return reminder_id
            return None
            
        except Exception as e:
            logger.error(f"Error scheduling reminder for activity {activity.id}: {str(e)}")
            return None
    
    async def _send_reminder(self, reminder: ReminderSchedule) -> bool:
        """Send a single reminder."""
        try:
            # Get activity details
            activity = await self.activity_repository.get_by_id(reminder.activity_id)
            if not activity:
                logger.error(f"Activity {reminder.activity_id} not found for reminder")
                return False
            
            # Get contact details
            contact = await self.contact_repository.get_by_id(activity.contact_id)
            
            # Get template
            template = self.reminder_templates.get(reminder.template_id)
            if not template:
                logger.error(f"Template {reminder.template_id} not found")
                return False
            
            # Prepare notification data
            notification_data = {
                'activity_title': activity.title,
                'activity_description': activity.description,
                'scheduled_date': activity.scheduled_date.strftime('%Y-%m-%d %H:%M') if activity.scheduled_date else '',
                'due_date': activity.due_date.strftime('%Y-%m-%d %H:%M') if activity.due_date else '',
                'contact_name': contact.display_name if contact else 'Unknown Contact',
                'priority': activity.priority.value,
                'user_name': reminder.recipient_id  # Would need user lookup for actual name
            }
            
            # Create notification
            notification = NotificationDTO(
                notification_id=str(reminder.reminder_id),
                notification_type=reminder.reminder_type.value,
                recipient_id=reminder.recipient_id,
                title=self._render_template(template.subject_template, notification_data),
                message=self._render_template(template.body_template, notification_data),
                scheduled_time=reminder.reminder_time,
                metadata=reminder.metadata or {}
            )
            
            # Send based on type
            if reminder.reminder_type == ReminderType.EMAIL:
                return await self._send_email_notification(notification, reminder.recipient_id)
            elif reminder.reminder_type == ReminderType.SMS:
                return await self._send_sms_notification(notification, reminder.recipient_id)
            elif reminder.reminder_type == ReminderType.PUSH_NOTIFICATION:
                return await self._send_push_notification(notification, reminder.recipient_id)
            elif reminder.reminder_type == ReminderType.IN_APP:
                return await self._send_in_app_notification(notification, reminder.recipient_id)
            else:
                logger.warning(f"Unsupported reminder type: {reminder.reminder_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending reminder {reminder.reminder_id}: {str(e)}")
            return False
    
    async def _send_email_notification(self, notification: NotificationDTO, user_id: str) -> bool:
        """Send email notification."""
        try:
            # Would need user repository to get email address
            user_email = f"{user_id}@example.com"  # Placeholder
            
            success = await self.email_service.send_email(
                to_email=user_email,
                subject=notification.title,
                body=notification.message,
                is_html=False
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False
    
    async def _send_sms_notification(self, notification: NotificationDTO, user_id: str) -> bool:
        """Send SMS notification."""
        try:
            # Would need user repository to get phone number
            user_phone = "+1234567890"  # Placeholder
            
            success = await self.sms_service.send_sms(
                to_phone=user_phone,
                message=notification.message
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {str(e)}")
            return False
    
    async def _send_push_notification(self, notification: NotificationDTO, user_id: str) -> bool:
        """Send push notification."""
        try:
            # Placeholder for push notification service
            logger.info(f"Push notification sent to {user_id}: {notification.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False
    
    async def _send_in_app_notification(self, notification: NotificationDTO, user_id: str) -> bool:
        """Send in-app notification."""
        try:
            # Placeholder for in-app notification storage
            logger.info(f"In-app notification created for {user_id}: {notification.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating in-app notification: {str(e)}")
            return False
    
    async def _is_in_quiet_hours(self, user_id: str, current_time: datetime) -> bool:
        """Check if user is currently in quiet hours."""
        preferences = self.notification_preferences.get(user_id)
        if not preferences or not preferences.quiet_hours_start or not preferences.quiet_hours_end:
            return False
        
        # Convert to user's timezone
        # For now, assuming UTC
        current_hour = current_time.hour
        
        start_hour = preferences.quiet_hours_start
        end_hour = preferences.quiet_hours_end
        
        if start_hour <= end_hour:
            return start_hour <= current_hour < end_hour
        else:
            # Quiet hours span midnight
            return current_hour >= start_hour or current_hour < end_hour
    
    async def _exceeds_frequency_limit(self, user_id: str, current_time: datetime) -> bool:
        """Check if user has exceeded daily notification frequency limit."""
        preferences = self.notification_preferences.get(user_id)
        if not preferences:
            return False
        
        # Would need to track sent notifications in database
        # For now, returning False
        return False
    
    async def _calculate_next_available_time(self, user_id: str, current_time: datetime) -> datetime:
        """Calculate next available time outside quiet hours."""
        preferences = self.notification_preferences.get(user_id)
        if not preferences or not preferences.quiet_hours_end:
            return current_time + timedelta(hours=1)
        
        # Schedule for after quiet hours end
        next_time = current_time.replace(hour=preferences.quiet_hours_end, minute=0, second=0, microsecond=0)
        
        if next_time <= current_time:
            next_time += timedelta(days=1)
        
        return next_time
    
    async def _reschedule_reminder(self, reminder_id: uuid.UUID, new_time: datetime) -> bool:
        """Reschedule a reminder to a new time."""
        try:
            success = await self.activity_repository.reschedule_reminder(
                reminder_id=reminder_id,
                new_time=new_time
            )
            return success
            
        except Exception as e:
            logger.error(f"Error rescheduling reminder {reminder_id}: {str(e)}")
            return False
    
    async def _handle_reminder_failure(self, reminder: ReminderSchedule) -> bool:
        """Handle failed reminder delivery with retry logic."""
        try:
            if reminder.retry_count < reminder.max_retries:
                # Schedule retry
                retry_time = datetime.utcnow() + timedelta(minutes=30 * (reminder.retry_count + 1))
                success = await self.activity_repository.schedule_reminder_retry(
                    reminder_id=reminder.reminder_id,
                    retry_time=retry_time,
                    retry_count=reminder.retry_count + 1
                )
                return success
            else:
                # Mark as failed after max retries
                await self.activity_repository.mark_reminder_failed(
                    reminder.reminder_id,
                    "Max retries exceeded"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error handling reminder failure {reminder.reminder_id}: {str(e)}")
            return False
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render a template with variables."""
        try:
            return template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing template variable: {str(e)}")
            return template
        except Exception as e:
            logger.error(f"Error rendering template: {str(e)}")
            return template 