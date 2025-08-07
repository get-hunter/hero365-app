"""
Activity Domain Entity

Represents activities in the customer timeline including interactions, status changes,
reminders, tasks, and system events.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Annotated
from enum import Enum
from pydantic import BaseModel, Field, field_validator, UUID4, BeforeValidator

from ..exceptions.domain_exceptions import DomainValidationError

# Configure logging
logger = logging.getLogger(__name__)


# Custom Pydantic validators for automatic string-to-enum conversion
def validate_activity_type(v) -> 'ActivityType':
    """Convert string to ActivityType enum."""
    if isinstance(v, str):
        return ActivityType(v)
    return v

def validate_activity_status(v) -> 'ActivityStatus':
    """Convert string to ActivityStatus enum."""
    if isinstance(v, str):
        return ActivityStatus(v)
    return v

def validate_activity_priority(v) -> 'ActivityPriority':
    """Convert string to ActivityPriority enum."""
    if isinstance(v, str):
        return ActivityPriority(v)
    return v


class ActivityType(Enum):
    """Types of activities that can be tracked."""
    INTERACTION = "interaction"  # Customer interactions (calls, emails, meetings)
    STATUS_CHANGE = "status_change"  # Contact status or lifecycle changes
    TASK = "task"  # Tasks related to the contact
    REMINDER = "reminder"  # Reminders and follow-ups
    NOTE = "note"  # General notes and observations
    SYSTEM_EVENT = "system_event"  # System-generated events
    SERVICE_EVENT = "service_event"  # Service-related activities
    FINANCIAL_EVENT = "financial_event"  # Payment, invoice, quote events
    DOCUMENT_EVENT = "document_event"  # Document uploads, proposals sent


class ActivityStatus(Enum):
    """Status of an activity."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class ActivityPriority(Enum):
    """Priority levels for activities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ActivityParticipant(BaseModel):
    """Represents a participant in an activity."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    user_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    role: str = Field(min_length=1)  # "organizer", "participant", "observer"
    is_primary: bool = False


class ActivityReminder(BaseModel):
    """Reminder configuration for an activity."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    reminder_id: UUID4 = Field(default_factory=uuid.uuid4)
    reminder_time: datetime = Field(default_factory=datetime.utcnow)
    reminder_type: str = Field(default="notification", min_length=1)  # "notification", "email", "sms"
    message: Optional[str] = None
    is_sent: bool = False
    sent_at: Optional[datetime] = None


class ActivityTemplate(BaseModel):
    """Template for creating standardized activities."""
    model_config = {"use_enum_values": True, "validate_assignment": True}
    
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    activity_type: Annotated[ActivityType, BeforeValidator(validate_activity_type)]
    created_by: str = Field(min_length=1)
    template_id: UUID4 = Field(default_factory=uuid.uuid4)
    default_duration: Optional[int] = Field(default=None, gt=0)  # in minutes
    default_reminders: List[Dict[str, Any]] = Field(default_factory=list)
    default_participants: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_date: datetime = Field(default_factory=datetime.utcnow)


class Activity:
    """
    Activity domain entity representing all types of customer activities.
    
    Provides a unified model for tracking interactions, status changes, tasks,
    reminders, and other customer-related activities in a timeline format.
    """
    
    def __init__(
        self,
        id: uuid.UUID,
        business_id: uuid.UUID,
        contact_id: uuid.UUID,
        activity_type: ActivityType,
        title: str,
        description: Optional[str] = None,
        status: ActivityStatus = ActivityStatus.PENDING,
        priority: ActivityPriority = ActivityPriority.MEDIUM,
        scheduled_date: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
        completed_date: Optional[datetime] = None,
        duration_minutes: Optional[int] = None,
        location: Optional[str] = None,
        participants: List[ActivityParticipant] = None,
        reminders: List[ActivityReminder] = None,
        metadata: Dict[str, Any] = None,
        tags: List[str] = None,
        created_by: str = "",
        assigned_to: Optional[str] = None,
        template_id: Optional[uuid.UUID] = None,
        parent_activity_id: Optional[uuid.UUID] = None,
        created_date: datetime = None,
        last_modified: datetime = None
    ):
        self.id = id
        self.business_id = business_id
        self.contact_id = contact_id
        self.activity_type = activity_type
        self.title = title
        self.description = description or ""
        self.status = status
        self.priority = priority
        self.scheduled_date = scheduled_date
        self.due_date = due_date
        self.completed_date = completed_date
        self.duration_minutes = duration_minutes
        self.location = location
        self.participants = participants or []
        self.reminders = reminders or []
        self.metadata = metadata or {}
        self.tags = tags or []
        self.created_by = created_by
        self.assigned_to = assigned_to
        self.template_id = template_id
        self.parent_activity_id = parent_activity_id
        self.created_date = created_date or datetime.utcnow()
        self.last_modified = last_modified or datetime.utcnow()
        
        self._validate()
    
    @classmethod
    def create_activity(
        cls,
        business_id: uuid.UUID,
        contact_id: uuid.UUID,
        activity_type: ActivityType,
        title: str,
        created_by: str,
        description: Optional[str] = None,
        scheduled_date: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
        priority: ActivityPriority = ActivityPriority.MEDIUM,
        assigned_to: Optional[str] = None,
        template_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> 'Activity':
        """Create a new activity with validation."""
        return cls(
            id=uuid.uuid4(),
            business_id=business_id,
            contact_id=contact_id,
            activity_type=activity_type,
            title=title,
            description=description,
            scheduled_date=scheduled_date,
            due_date=due_date,
            priority=priority,
            created_by=created_by,
            assigned_to=assigned_to,
            template_id=template_id,
            **kwargs
        )
    
    @classmethod
    def from_template(
        cls,
        template: ActivityTemplate,
        business_id: uuid.UUID,
        contact_id: uuid.UUID,
        created_by: str,
        scheduled_date: Optional[datetime] = None,
        **overrides
    ) -> 'Activity':
        """Create an activity from a template."""
        activity_data = {
            'business_id': business_id,
            'contact_id': contact_id,
            'activity_type': template.activity_type,
            'title': template.name,
            'description': template.description,
            'created_by': created_by,
            'template_id': template.template_id,
            'scheduled_date': scheduled_date,
            'duration_minutes': template.default_duration,
            'metadata': template.custom_fields.copy()
        }
        
        # Apply any overrides
        activity_data.update(overrides)
        
        activity = cls.create_activity(**activity_data)
        
        # Add default reminders from template
        for reminder_config in template.default_reminders:
            activity.add_reminder_from_config(reminder_config)
        
        return activity
    
    def _validate(self):
        """Validate activity data."""
        if not self.title or not self.title.strip():
            raise DomainValidationError("Activity title is required")
        
        if not self.created_by:
            raise DomainValidationError("Activity creator is required")
        
        if self.due_date and self.scheduled_date and self.due_date < self.scheduled_date:
            raise DomainValidationError("Due date cannot be before scheduled date")
        
        if self.completed_date and self.status != ActivityStatus.COMPLETED:
            raise DomainValidationError("Activity must be marked as completed when completion date is set")
    
    def update_status(self, new_status: ActivityStatus, updated_by: str, notes: Optional[str] = None):
        """Update activity status with validation."""
        old_status = self.status
        self.status = new_status
        self.last_modified = datetime.utcnow()
        
        # Set completion date when marking as completed
        if new_status == ActivityStatus.COMPLETED and not self.completed_date:
            self.completed_date = datetime.utcnow()
        elif new_status != ActivityStatus.COMPLETED:
            self.completed_date = None
        
        # Add status change to metadata
        if 'status_history' not in self.metadata:
            self.metadata['status_history'] = []
        
        self.metadata['status_history'].append({
            'from_status': old_status.value,
            'to_status': new_status.value,
            'changed_by': updated_by,
            'changed_at': self.last_modified.isoformat(),
            'notes': notes
        })
    
    def reschedule(self, new_scheduled_date: datetime, updated_by: str, reason: Optional[str] = None):
        """Reschedule the activity."""
        old_date = self.scheduled_date
        self.scheduled_date = new_scheduled_date
        self.last_modified = datetime.utcnow()
        
        # Add reschedule to metadata
        if 'reschedule_history' not in self.metadata:
            self.metadata['reschedule_history'] = []
        
        self.metadata['reschedule_history'].append({
            'from_date': old_date.isoformat() if old_date else None,
            'to_date': new_scheduled_date.isoformat(),
            'rescheduled_by': updated_by,
            'rescheduled_at': self.last_modified.isoformat(),
            'reason': reason
        })
        
        # Update reminders if needed
        self._update_reminders_for_reschedule()
    
    def add_participant(self, user_id: str, name: str, role: str = "participant", is_primary: bool = False):
        """Add a participant to the activity."""
        # Check if participant already exists
        for participant in self.participants:
            if participant.user_id == user_id:
                participant.role = role
                participant.is_primary = is_primary
                return
        
        self.participants.append(ActivityParticipant(
            user_id=user_id,
            name=name,
            role=role,
            is_primary=is_primary
        ))
        self.last_modified = datetime.utcnow()
    
    def remove_participant(self, user_id: str):
        """Remove a participant from the activity."""
        self.participants = [p for p in self.participants if p.user_id != user_id]
        self.last_modified = datetime.utcnow()
    
    def add_reminder(self, reminder_time: datetime, reminder_type: str = "notification", message: Optional[str] = None) -> uuid.UUID:
        """Add a reminder to the activity."""
        reminder = ActivityReminder(
            reminder_time=reminder_time,
            reminder_type=reminder_type,
            message=message
        )
        self.reminders.append(reminder)
        self.last_modified = datetime.utcnow()
        return reminder.reminder_id
    
    def add_reminder_from_config(self, config: Dict[str, Any]):
        """Add a reminder from template configuration."""
        if self.scheduled_date:
            minutes_before = config.get('minutes_before', 60)
            reminder_time = self.scheduled_date - timedelta(minutes=minutes_before)
            
            self.add_reminder(
                reminder_time=reminder_time,
                reminder_type=config.get('type', 'notification'),
                message=config.get('message')
            )
    
    def mark_reminder_sent(self, reminder_id: uuid.UUID):
        """Mark a reminder as sent."""
        for reminder in self.reminders:
            if reminder.reminder_id == reminder_id:
                reminder.is_sent = True
                reminder.sent_at = datetime.utcnow()
                break
        self.last_modified = datetime.utcnow()
    
    def _update_reminders_for_reschedule(self):
        """Update reminder times when activity is rescheduled."""
        if not self.scheduled_date:
            return
        
        for reminder in self.reminders:
            if not reminder.is_sent:
                # Calculate the time difference from original scheduled time
                # This is a simplified approach - in practice, you might want more sophisticated logic
                original_minutes_before = 60  # default
                reminder.reminder_time = self.scheduled_date - timedelta(minutes=original_minutes_before)
    
    def is_overdue(self) -> bool:
        """Check if activity is overdue."""
        if self.status in [ActivityStatus.COMPLETED, ActivityStatus.CANCELLED]:
            return False
        
        check_date = self.due_date or self.scheduled_date
        return check_date and check_date < datetime.utcnow()
    
    def get_duration_display(self) -> str:
        """Get human-readable duration."""
        if not self.duration_minutes:
            return "No duration set"
        
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        return f"{minutes}m"
    
    def get_status_display(self) -> str:
        """Get human-readable status."""
        status_display = {
            ActivityStatus.PENDING: "Pending",
            ActivityStatus.IN_PROGRESS: "In Progress", 
            ActivityStatus.COMPLETED: "Completed",
            ActivityStatus.CANCELLED: "Cancelled",
            ActivityStatus.OVERDUE: "Overdue"
        }
        return status_display.get(self.status, self.status.value)
    
    def get_priority_display(self) -> str:
        """Get human-readable priority."""
        priority_display = {
            ActivityPriority.LOW: "Low",
            ActivityPriority.MEDIUM: "Medium",
            ActivityPriority.HIGH: "High", 
            ActivityPriority.URGENT: "Urgent"
        }
        return priority_display.get(self.priority, self.priority.value)
    
    def get_type_display(self) -> str:
        """Get human-readable activity type."""
        type_display = {
            ActivityType.INTERACTION: "Customer Interaction",
            ActivityType.STATUS_CHANGE: "Status Change",
            ActivityType.TASK: "Task",
            ActivityType.REMINDER: "Reminder",
            ActivityType.NOTE: "Note",
            ActivityType.SYSTEM_EVENT: "System Event",
            ActivityType.SERVICE_EVENT: "Service Activity",
            ActivityType.FINANCIAL_EVENT: "Financial Activity",
            ActivityType.DOCUMENT_EVENT: "Document Activity"
        }
        return type_display.get(self.activity_type, self.activity_type.value)
    
    def to_timeline_entry(self) -> Dict[str, Any]:
        """Convert activity to timeline entry format."""
        return {
            'id': str(self.id),
            'type': self.activity_type.value,
            'title': self.title,
            'description': self.description,
            'timestamp': self.scheduled_date or self.created_date,
            'status': self.status.value,
            'priority': self.priority.value,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'metadata': self.metadata,
            'tags': self.tags,
            'is_overdue': self.is_overdue(),
            'type_display': self.get_type_display(),
            'status_display': self.get_status_display(),
            'priority_display': self.get_priority_display()
        } 