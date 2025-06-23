"""
Activity DTOs

Data Transfer Objects for activity and timeline management operations.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from ...domain.entities.activity import ActivityType, ActivityStatus, ActivityPriority


@dataclass
class ActivityCreateDTO:
    """DTO for creating a new activity."""
    business_id: uuid.UUID
    contact_id: uuid.UUID
    activity_type: ActivityType
    title: str
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    priority: ActivityPriority = ActivityPriority.MEDIUM
    assigned_to: Optional[str] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    template_id: Optional[uuid.UUID] = None
    participants: List[Dict[str, Any]] = None
    reminders: List[Dict[str, Any]] = None


@dataclass
class ActivityUpdateDTO:
    """DTO for updating an existing activity."""
    activity_id: uuid.UUID
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ActivityStatus] = None
    priority: Optional[ActivityPriority] = None
    scheduled_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    reschedule_reason: Optional[str] = None


@dataclass
class ActivityResponseDTO:
    """DTO for activity response data."""
    id: uuid.UUID
    business_id: uuid.UUID
    contact_id: uuid.UUID
    template_id: Optional[uuid.UUID]
    parent_activity_id: Optional[uuid.UUID]
    activity_type: ActivityType
    title: str
    description: str
    status: ActivityStatus
    priority: ActivityPriority
    scheduled_date: Optional[datetime]
    due_date: Optional[datetime]
    completed_date: Optional[datetime]
    duration_minutes: Optional[int]
    location: Optional[str]
    participants: List[Dict[str, Any]]
    reminders: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    tags: List[str]
    created_by: str
    assigned_to: Optional[str]
    created_date: datetime
    last_modified: datetime
    is_overdue: bool
    duration_display: str
    status_display: str
    priority_display: str
    type_display: str


@dataclass
class ActivityListDTO:
    """DTO for paginated activity lists."""
    activities: List[ActivityResponseDTO]
    total_count: int
    skip: int
    limit: int


@dataclass
class ActivityTemplateCreateDTO:
    """DTO for creating activity templates."""
    business_id: uuid.UUID
    name: str
    description: str
    activity_type: ActivityType
    default_duration: Optional[int] = None
    default_reminders: List[Dict[str, Any]] = None
    default_participants: List[str] = None
    custom_fields: Dict[str, Any] = None


@dataclass
class ActivityTemplateResponseDTO:
    """DTO for activity template response data."""
    template_id: uuid.UUID
    name: str
    description: str
    activity_type: ActivityType
    default_duration: Optional[int]
    default_reminders: List[Dict[str, Any]]
    default_participants: List[str]
    custom_fields: Dict[str, Any]
    is_active: bool
    created_by: str
    created_date: datetime


@dataclass
class TimelineRequestDTO:
    """DTO for timeline request parameters."""
    contact_id: uuid.UUID
    business_id: uuid.UUID
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    activity_types: Optional[List[ActivityType]] = None
    skip: int = 0
    limit: int = 50


@dataclass
class TimelineEntryDTO:
    """DTO for individual timeline entries."""
    id: str
    type: str
    title: str
    description: str
    timestamp: datetime
    status: str
    priority: str
    created_by: str
    assigned_to: Optional[str]
    metadata: Dict[str, Any]
    tags: List[str]
    is_overdue: bool
    type_display: str
    status_display: str
    priority_display: str


@dataclass
class TimelineResponseDTO:
    """DTO for timeline response data."""
    contact_id: uuid.UUID
    timeline_entries: List[TimelineEntryDTO]
    total_count: int
    skip: int
    limit: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]


@dataclass
class ActivityReminderDTO:
    """DTO for activity reminders."""
    reminder_id: uuid.UUID
    activity_id: uuid.UUID
    contact_id: uuid.UUID
    activity_title: str
    reminder_time: datetime
    reminder_type: str
    message: Optional[str]


@dataclass
class ActivityStatisticsDTO:
    """DTO for activity statistics."""
    total_activities: int
    pending_activities: int
    in_progress_activities: int
    completed_activities: int
    overdue_activities: int
    activities_by_type: Dict[str, int]
    activities_by_priority: Dict[str, int]
    average_completion_time: Optional[float]
    upcoming_activities_count: int
    activities_this_week: int
    activities_this_month: int


@dataclass
class ContactActivitySummaryDTO:
    """DTO for contact activity summary."""
    contact_id: uuid.UUID
    total_activities: int
    last_activity_date: Optional[datetime]
    next_scheduled_activity: Optional[datetime]
    activities_by_type: Dict[str, int]
    overdue_activities: int
    upcoming_activities: int
    activity_score: float  # Engagement score based on activity frequency


@dataclass
class ActivityParticipantDTO:
    """DTO for activity participants."""
    user_id: str
    name: str
    role: str
    is_primary: bool


@dataclass
class ActivitySearchDTO:
    """DTO for activity search parameters."""
    business_id: uuid.UUID
    contact_ids: Optional[List[uuid.UUID]] = None
    activity_types: Optional[List[ActivityType]] = None
    statuses: Optional[List[ActivityStatus]] = None
    priorities: Optional[List[ActivityPriority]] = None
    assigned_to: Optional[str] = None
    created_by: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    due_start_date: Optional[datetime] = None
    due_end_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    search_term: Optional[str] = None
    include_overdue: bool = True
    include_completed: bool = True
    sort_by: str = "scheduled_date"
    sort_order: str = "desc"
    skip: int = 0
    limit: int = 100


@dataclass
class ActivityBulkUpdateDTO:
    """DTO for bulk activity updates."""
    business_id: uuid.UUID
    activity_ids: List[uuid.UUID]
    status: Optional[ActivityStatus] = None
    priority: Optional[ActivityPriority] = None
    assigned_to: Optional[str] = None
    tags_to_add: Optional[List[str]] = None
    tags_to_remove: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    reschedule_date: Optional[datetime] = None
    notes: Optional[str] = None


@dataclass
class ActivityRescheduleDTO:
    """DTO for rescheduling activities."""
    activity_id: uuid.UUID
    new_scheduled_date: datetime
    reason: Optional[str] = None
    update_reminders: bool = True


@dataclass
class ActivityCompletionDTO:
    """DTO for completing activities."""
    activity_id: uuid.UUID
    completion_notes: Optional[str] = None
    outcome: Optional[str] = None
    next_actions: Optional[List[str]] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None


@dataclass
class DashboardActivitiesDTO:
    """DTO for dashboard activity overview."""
    overdue_activities: List[ActivityResponseDTO]
    upcoming_activities: List[ActivityResponseDTO]
    recent_activities: List[ActivityResponseDTO]
    activity_statistics: ActivityStatisticsDTO
    reminders_due: List[ActivityReminderDTO]
    high_priority_count: int
    completion_rate: float


@dataclass
class CalendarEventDTO:
    """DTO for calendar integration."""
    activity_id: uuid.UUID
    title: str
    description: str
    start_time: datetime
    end_time: Optional[datetime]
    location: Optional[str]
    attendees: List[str]
    reminder_minutes: List[int]
    is_all_day: bool = False
    recurrence_rule: Optional[str] = None


@dataclass
class ActivityNotificationDTO:
    """DTO for activity notifications."""
    notification_id: uuid.UUID
    activity_id: uuid.UUID
    recipient_user_id: str
    notification_type: str  # "reminder", "assignment", "overdue", "status_change"
    title: str
    message: str
    scheduled_time: datetime
    is_sent: bool = False
    delivery_method: str = "notification"  # "notification", "email", "sms"


@dataclass
class ActivityTemplateUsageDTO:
    """DTO for template usage statistics."""
    template_id: uuid.UUID
    template_name: str
    usage_count: int
    last_used: Optional[datetime]
    average_duration: Optional[int]
    completion_rate: float
    most_common_outcomes: List[str] 