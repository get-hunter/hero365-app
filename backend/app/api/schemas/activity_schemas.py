"""
Activity API Schemas

Pydantic models for activity and timeline management API requests and responses.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, validator, root_validator
from pydantic.types import constr


# Enums for API schemas
class ActivityTypeSchema(str, Enum):
    """Activity type enumeration for API."""
    INTERACTION = "interaction"
    STATUS_CHANGE = "status_change"
    TASK = "task"
    REMINDER = "reminder"
    NOTE = "note"
    SYSTEM_EVENT = "system_event"
    SERVICE_EVENT = "service_event"
    FINANCIAL_EVENT = "financial_event"
    DOCUMENT_EVENT = "document_event"


class ActivityStatusSchema(str, Enum):
    """Activity status enumeration for API."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class ActivityPrioritySchema(str, Enum):
    """Activity priority enumeration for API."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Participant schemas
class ActivityParticipantSchema(BaseModel):
    """Schema for activity participants."""
    user_id: str = Field(..., description="User ID of the participant")
    name: str = Field(..., min_length=1, max_length=200, description="Name of the participant")
    role: str = Field(default="participant", description="Role in the activity (organizer, participant, observer)")
    is_primary: bool = Field(default=False, description="Whether this is the primary participant")


class ActivityReminderSchema(BaseModel):
    """Schema for activity reminders."""
    reminder_id: Optional[str] = Field(None, description="Unique identifier for the reminder")
    reminder_time: datetime = Field(..., description="When the reminder should be sent")
    reminder_type: str = Field(default="notification", description="Type of reminder (notification, email, sms)")
    message: Optional[str] = Field(None, max_length=500, description="Custom reminder message")
    is_sent: bool = Field(default=False, description="Whether the reminder has been sent")
    sent_at: Optional[datetime] = Field(None, description="When the reminder was sent")


# Request schemas
class ActivityCreateRequest(BaseModel):
    """Schema for creating a new activity."""
    contact_id: uuid.UUID = Field(..., description="ID of the contact this activity is for")
    activity_type: ActivityTypeSchema = Field(..., description="Type of activity")
    title: constr(min_length=1, max_length=500) = Field(..., description="Activity title")
    description: Optional[str] = Field(None, max_length=2000, description="Detailed description of the activity")
    scheduled_date: Optional[datetime] = Field(None, description="When the activity is scheduled")
    due_date: Optional[datetime] = Field(None, description="When the activity is due")
    priority: ActivityPrioritySchema = Field(default=ActivityPrioritySchema.MEDIUM, description="Activity priority")
    assigned_to: Optional[str] = Field(None, description="User ID of the person assigned to this activity")
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440, description="Duration in minutes (max 24 hours)")
    location: Optional[str] = Field(None, max_length=500, description="Location for the activity")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the activity")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    template_id: Optional[uuid.UUID] = Field(None, description="Template to create activity from")
    participants: List[ActivityParticipantSchema] = Field(default_factory=list, description="Activity participants")
    reminders: List[Dict[str, Any]] = Field(default_factory=list, description="Reminder configurations")

    @validator('due_date')
    def validate_due_date(cls, v, values):
        """Ensure due date is after scheduled date if both are provided."""
        if v and 'scheduled_date' in values and values['scheduled_date']:
            if v < values['scheduled_date']:
                raise ValueError('Due date must be after scheduled date')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags list."""
        if len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        for tag in v:
            if not isinstance(tag, str) or len(tag.strip()) == 0:
                raise ValueError('Tags must be non-empty strings')
            if len(tag) > 50:
                raise ValueError('Each tag must be 50 characters or less')
        return [tag.strip().lower() for tag in v]


class ActivityUpdateRequest(BaseModel):
    """Schema for updating an existing activity."""
    title: Optional[constr(min_length=1, max_length=500)] = Field(None, description="Activity title")
    description: Optional[str] = Field(None, max_length=2000, description="Activity description")
    status: Optional[ActivityStatusSchema] = Field(None, description="Activity status")
    priority: Optional[ActivityPrioritySchema] = Field(None, description="Activity priority")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled date/time")
    due_date: Optional[datetime] = Field(None, description="Due date/time")
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440, description="Duration in minutes")
    location: Optional[str] = Field(None, max_length=500, description="Activity location")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")
    tags: Optional[List[str]] = Field(None, description="Activity tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    notes: Optional[str] = Field(None, max_length=1000, description="Update notes")
    reschedule_reason: Optional[str] = Field(None, max_length=500, description="Reason for rescheduling")

    @validator('due_date')
    def validate_due_date(cls, v, values):
        """Ensure due date is after scheduled date if both are provided."""
        if v and 'scheduled_date' in values and values['scheduled_date']:
            if v < values['scheduled_date']:
                raise ValueError('Due date must be after scheduled date')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags list."""
        if v is not None:
            if len(v) > 20:
                raise ValueError('Maximum 20 tags allowed')
            for tag in v:
                if not isinstance(tag, str) or len(tag.strip()) == 0:
                    raise ValueError('Tags must be non-empty strings')
                if len(tag) > 50:
                    raise ValueError('Each tag must be 50 characters or less')
            return [tag.strip().lower() for tag in v]
        return v


class ActivityBulkUpdateRequest(BaseModel):
    """Schema for bulk updating activities."""
    activity_ids: List[uuid.UUID] = Field(..., min_items=1, max_items=100, description="List of activity IDs to update")
    status: Optional[ActivityStatusSchema] = Field(None, description="New status for all activities")
    priority: Optional[ActivityPrioritySchema] = Field(None, description="New priority for all activities")
    assigned_to: Optional[str] = Field(None, description="New assignee for all activities")
    tags_to_add: Optional[List[str]] = Field(None, description="Tags to add to all activities")
    tags_to_remove: Optional[List[str]] = Field(None, description="Tags to remove from all activities")
    due_date: Optional[datetime] = Field(None, description="New due date for all activities")
    reschedule_date: Optional[datetime] = Field(None, description="New scheduled date for all activities")
    notes: Optional[str] = Field(None, max_length=1000, description="Bulk update notes")


class ActivitySearchRequest(BaseModel):
    """Schema for searching activities."""
    contact_ids: Optional[List[uuid.UUID]] = Field(None, description="Filter by contact IDs")
    activity_types: Optional[List[ActivityTypeSchema]] = Field(None, description="Filter by activity types")
    statuses: Optional[List[ActivityStatusSchema]] = Field(None, description="Filter by statuses")
    priorities: Optional[List[ActivityPrioritySchema]] = Field(None, description="Filter by priorities")
    assigned_to: Optional[str] = Field(None, description="Filter by assigned user")
    created_by: Optional[str] = Field(None, description="Filter by creator")
    start_date: Optional[datetime] = Field(None, description="Filter activities after this date")
    end_date: Optional[datetime] = Field(None, description="Filter activities before this date")
    due_start_date: Optional[datetime] = Field(None, description="Filter by due date start")
    due_end_date: Optional[datetime] = Field(None, description="Filter by due date end")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    search_term: Optional[str] = Field(None, max_length=200, description="Search in title and description")
    include_overdue: bool = Field(default=True, description="Include overdue activities")
    include_completed: bool = Field(default=True, description="Include completed activities")
    sort_by: str = Field(default="scheduled_date", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


class TimelineRequest(BaseModel):
    """Schema for timeline requests."""
    contact_id: uuid.UUID = Field(..., description="Contact ID for timeline")
    start_date: Optional[datetime] = Field(None, description="Timeline start date")
    end_date: Optional[datetime] = Field(None, description="Timeline end date")
    activity_types: Optional[List[ActivityTypeSchema]] = Field(None, description="Filter by activity types")
    include_system_events: bool = Field(default=True, description="Include system-generated events")


# Response schemas
class ActivityResponse(BaseModel):
    """Schema for activity response data."""
    id: uuid.UUID = Field(..., description="Activity ID")
    business_id: uuid.UUID = Field(..., description="Business ID")
    contact_id: uuid.UUID = Field(..., description="Contact ID")
    template_id: Optional[uuid.UUID] = Field(None, description="Template ID if created from template")
    parent_activity_id: Optional[uuid.UUID] = Field(None, description="Parent activity ID")
    activity_type: ActivityTypeSchema = Field(..., description="Activity type")
    title: str = Field(..., description="Activity title")
    description: str = Field(..., description="Activity description")
    status: ActivityStatusSchema = Field(..., description="Current status")
    priority: ActivityPrioritySchema = Field(..., description="Activity priority")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled date/time")
    due_date: Optional[datetime] = Field(None, description="Due date/time")
    completed_date: Optional[datetime] = Field(None, description="Completion date/time")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    location: Optional[str] = Field(None, description="Activity location")
    participants: List[ActivityParticipantSchema] = Field(default_factory=list, description="Activity participants")
    reminders: List[ActivityReminderSchema] = Field(default_factory=list, description="Activity reminders")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="Activity tags")
    created_by: str = Field(..., description="Creator user ID")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")
    created_date: datetime = Field(..., description="Creation timestamp")
    last_modified: datetime = Field(..., description="Last modification timestamp")
    is_overdue: bool = Field(..., description="Whether the activity is overdue")
    duration_display: str = Field(..., description="Human-readable duration")
    status_display: str = Field(..., description="Human-readable status")
    priority_display: str = Field(..., description="Human-readable priority")
    type_display: str = Field(..., description="Human-readable activity type")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class ActivityListResponse(BaseModel):
    """Schema for paginated activity lists."""
    activities: List[ActivityResponse] = Field(..., description="List of activities")
    total_count: int = Field(..., description="Total number of activities")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum number of items returned")
    has_more: bool = Field(..., description="Whether there are more items")

    @validator('has_more', always=True)
    def calculate_has_more(cls, v, values):
        """Calculate if there are more items."""
        if 'total_count' in values and 'skip' in values and 'limit' in values:
            return values['skip'] + values['limit'] < values['total_count']
        return False


# Template schemas
class ActivityTemplateCreateRequest(BaseModel):
    """Schema for creating activity templates."""
    name: constr(min_length=1, max_length=200) = Field(..., description="Template name")
    description: str = Field(..., max_length=1000, description="Template description")
    activity_type: ActivityTypeSchema = Field(..., description="Activity type")
    default_duration: Optional[int] = Field(None, ge=1, le=1440, description="Default duration in minutes")
    default_reminders: List[Dict[str, Any]] = Field(default_factory=list, description="Default reminder configurations")
    default_participants: List[str] = Field(default_factory=list, description="Default participant user IDs")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom template fields")


class ActivityTemplateResponse(BaseModel):
    """Schema for activity template response."""
    template_id: uuid.UUID = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    activity_type: ActivityTypeSchema = Field(..., description="Activity type")
    default_duration: Optional[int] = Field(None, description="Default duration in minutes")
    default_reminders: List[Dict[str, Any]] = Field(default_factory=list, description="Default reminders")
    default_participants: List[str] = Field(default_factory=list, description="Default participants")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")
    is_active: bool = Field(..., description="Whether template is active")
    created_by: str = Field(..., description="Creator user ID")
    created_date: datetime = Field(..., description="Creation timestamp")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


# Timeline schemas
class TimelineEntryResponse(BaseModel):
    """Schema for timeline entry response."""
    id: str = Field(..., description="Entry ID")
    type: str = Field(..., description="Entry type")
    title: str = Field(..., description="Entry title")
    description: str = Field(..., description="Entry description")
    timestamp: datetime = Field(..., description="Entry timestamp")
    status: str = Field(..., description="Entry status")
    priority: str = Field(..., description="Entry priority")
    created_by: str = Field(..., description="Creator user ID")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="Entry tags")
    is_overdue: bool = Field(..., description="Whether entry is overdue")
    type_display: str = Field(..., description="Human-readable type")
    status_display: str = Field(..., description="Human-readable status")
    priority_display: str = Field(..., description="Human-readable priority")


class TimelineResponse(BaseModel):
    """Schema for timeline response."""
    contact_id: uuid.UUID = Field(..., description="Contact ID")
    timeline_entries: List[TimelineEntryResponse] = Field(..., description="Timeline entries")
    total_count: int = Field(..., description="Total number of entries")
    skip: int = Field(..., description="Number of entries skipped")
    limit: int = Field(..., description="Maximum number of entries returned")
    start_date: Optional[datetime] = Field(None, description="Timeline start date")
    end_date: Optional[datetime] = Field(None, description="Timeline end date")
    has_more: bool = Field(..., description="Whether there are more entries")

    @validator('has_more', always=True)
    def calculate_has_more(cls, v, values):
        """Calculate if there are more entries."""
        if 'total_count' in values and 'skip' in values and 'limit' in values:
            return values['skip'] + values['limit'] < values['total_count']
        return False


# Statistics schemas
class ActivityStatisticsResponse(BaseModel):
    """Schema for activity statistics response."""
    total_activities: int = Field(..., description="Total number of activities")
    pending_activities: int = Field(..., description="Number of pending activities")
    in_progress_activities: int = Field(..., description="Number of in-progress activities")
    completed_activities: int = Field(..., description="Number of completed activities")
    overdue_activities: int = Field(..., description="Number of overdue activities")
    activities_by_type: Dict[str, int] = Field(..., description="Activities grouped by type")
    activities_by_priority: Dict[str, int] = Field(..., description="Activities grouped by priority")
    average_completion_time: Optional[float] = Field(None, description="Average completion time in hours")
    upcoming_activities_count: int = Field(..., description="Number of upcoming activities")
    activities_this_week: int = Field(..., description="Activities scheduled this week")
    activities_this_month: int = Field(..., description="Activities scheduled this month")
    completion_rate: float = Field(..., description="Overall completion rate percentage")


class ContactActivitySummaryResponse(BaseModel):
    """Schema for contact activity summary response."""
    contact_id: uuid.UUID = Field(..., description="Contact ID")
    total_activities: int = Field(..., description="Total activities for this contact")
    last_activity_date: Optional[datetime] = Field(None, description="Date of last activity")
    next_scheduled_activity: Optional[datetime] = Field(None, description="Next scheduled activity date")
    activities_by_type: Dict[str, int] = Field(..., description="Activities grouped by type")
    overdue_activities: int = Field(..., description="Number of overdue activities")
    upcoming_activities: int = Field(..., description="Number of upcoming activities")
    activity_score: float = Field(..., description="Engagement score based on activity frequency")


# Reminder schemas
class ActivityReminderResponse(BaseModel):
    """Schema for activity reminder response."""
    reminder_id: uuid.UUID = Field(..., description="Reminder ID")
    activity_id: uuid.UUID = Field(..., description="Activity ID")
    contact_id: uuid.UUID = Field(..., description="Contact ID")
    activity_title: str = Field(..., description="Activity title")
    reminder_time: datetime = Field(..., description="Reminder time")
    reminder_type: str = Field(..., description="Reminder type")
    message: Optional[str] = Field(None, description="Reminder message")


# Dashboard schemas
class DashboardActivitiesResponse(BaseModel):
    """Schema for dashboard activities overview."""
    overdue_activities: List[ActivityResponse] = Field(..., description="Overdue activities")
    upcoming_activities: List[ActivityResponse] = Field(..., description="Upcoming activities")
    recent_activities: List[ActivityResponse] = Field(..., description="Recent activities")
    activity_statistics: ActivityStatisticsResponse = Field(..., description="Activity statistics")
    reminders_due: List[ActivityReminderResponse] = Field(..., description="Due reminders")
    high_priority_count: int = Field(..., description="Number of high priority activities")
    completion_rate: float = Field(..., description="Completion rate percentage")


# Common response schemas
class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Whether operation was successful")


class BulkOperationResponse(BaseModel):
    """Schema for bulk operation responses."""
    success_count: int = Field(..., description="Number of successful operations")
    error_count: int = Field(..., description="Number of failed operations")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    message: str = Field(..., description="Overall operation message")


# Pagination schemas
class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum number of items to return") 