"""
Timeline Aggregation Service

Provides unified timeline feeds by aggregating activities, interactions, and system events.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum

from ..dto.activity_dto import TimelineEntryDTO, TimelineResponseDTO
from ...domain.repositories.activity_repository import ActivityRepository
from ...domain.repositories.contact_repository import ContactRepository
from ...domain.entities.activity import ActivityType
from ...domain.entities.contact import InteractionType


class TimelineEventType(Enum):
    """Types of events that can appear in the timeline."""
    ACTIVITY = "activity"
    INTERACTION = "interaction"
    STATUS_CHANGE = "status_change"
    SYSTEM_EVENT = "system_event"
    MILESTONE = "milestone"


class TimelineEvent(BaseModel):
    """Unified timeline event structure."""
    id: str
    event_type: TimelineEventType
    timestamp: datetime
    title: str
    description: str
    actor_id: str
    actor_name: str
    metadata: Dict[str, Any]
    priority: str = "medium"
    tags: List[str] = Field(default_factory=list)
    related_entities: Dict[str, str] = Field(default_factory=dict)  # {entity_type: entity_id}


class TimelineAggregationService:
    """
    Service for aggregating and organizing timeline events from multiple sources.
    
    Combines activities, contact interactions, status changes, and system events
    into a unified, chronological timeline with intelligent grouping and filtering.
    """
    
    def __init__(
        self,
        activity_repository: ActivityRepository,
        contact_repository: ContactRepository
    ):
        self.activity_repository = activity_repository
        self.contact_repository = contact_repository
    
    async def get_unified_contact_timeline(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[TimelineEventType]] = None,
        include_system_events: bool = True,
        group_by_day: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> TimelineResponseDTO:
        """
        Get a unified timeline for a contact combining all event types.
        
        Args:
            contact_id: Contact to get timeline for
            business_id: Business context
            start_date: Optional start date filter
            end_date: Optional end date filter
            event_types: Optional filter by event types
            include_system_events: Whether to include system-generated events
            group_by_day: Whether to group events by day
            skip: Number of events to skip
            limit: Maximum number of events to return
            
        Returns:
            TimelineResponseDTO with unified timeline entries
        """
        # Collect events from all sources
        all_events = []
        
        # Get activity events
        if not event_types or TimelineEventType.ACTIVITY in event_types:
            activity_events = await self._get_activity_events(
                contact_id, business_id, start_date, end_date
            )
            all_events.extend(activity_events)
        
        # Get interaction events from contact history
        if not event_types or TimelineEventType.INTERACTION in event_types:
            interaction_events = await self._get_interaction_events(
                contact_id, business_id, start_date, end_date
            )
            all_events.extend(interaction_events)
        
        # Get status change events
        if not event_types or TimelineEventType.STATUS_CHANGE in event_types:
            status_events = await self._get_status_change_events(
                contact_id, business_id, start_date, end_date
            )
            all_events.extend(status_events)
        
        # Get system events if requested
        if include_system_events and (not event_types or TimelineEventType.SYSTEM_EVENT in event_types):
            system_events = await self._get_system_events(
                contact_id, business_id, start_date, end_date
            )
            all_events.extend(system_events)
        
        # Get milestone events
        if not event_types or TimelineEventType.MILESTONE in event_types:
            milestone_events = await self._get_milestone_events(
                contact_id, business_id, start_date, end_date
            )
            all_events.extend(milestone_events)
        
        # Sort events by timestamp (most recent first)
        all_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        total_count = len(all_events)
        paginated_events = all_events[skip:skip + limit]
        
        # Group by day if requested
        if group_by_day:
            paginated_events = self._group_events_by_day(paginated_events)
        
        # Convert to timeline entries
        timeline_entries = [
            self._event_to_timeline_entry(event) for event in paginated_events
        ]
        
        return TimelineResponseDTO(
            contact_id=contact_id,
            timeline_entries=timeline_entries,
            total_count=total_count,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_business_activity_feed(
        self,
        business_id: uuid.UUID,
        user_id: str,
        days_back: int = 7,
        event_types: Optional[List[TimelineEventType]] = None,
        limit: int = 100
    ) -> List[TimelineEvent]:
        """
        Get recent activity feed for a business.
        
        Args:
            business_id: Business to get feed for
            user_id: User requesting the feed (for permissions)
            days_back: Number of days to look back
            event_types: Optional filter by event types
            limit: Maximum number of events to return
            
        Returns:
            List of recent timeline events
        """
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get recent activities across all contacts
        activities = await self.activity_repository.get_business_activities(
            business_id=business_id,
            start_date=start_date,
            limit=limit
        )
        
        # Convert to timeline events
        events = []
        for activity in activities:
            event = TimelineEvent(
                id=f"activity_{activity.id}",
                event_type=TimelineEventType.ACTIVITY,
                timestamp=activity.scheduled_date or activity.created_date,
                title=activity.title,
                description=activity.description,
                actor_id=activity.created_by,
                actor_name=activity.created_by,  # Would need user lookup for actual name
                metadata={
                    'activity_type': activity.activity_type.value,
                    'status': activity.status.value,
                    'priority': activity.priority.value,
                    'contact_id': str(activity.contact_id)
                },
                priority=activity.priority.value,
                tags=activity.tags,
                related_entities={
                    'contact': str(activity.contact_id),
                    'activity': str(activity.id)
                }
            )
            events.append(event)
        
        # Sort by timestamp
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return events[:limit]
    
    async def get_user_activity_digest(
        self,
        business_id: uuid.UUID,
        user_id: str,
        period: str = "week"  # "day", "week", "month"
    ) -> Dict[str, Any]:
        """
        Get activity digest for a user.
        
        Args:
            business_id: Business context
            user_id: User to get digest for
            period: Time period for digest
            
        Returns:
            Dictionary with digest information
        """
        # Calculate date range based on period
        now = datetime.utcnow()
        if period == "day":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now - timedelta(days=7)
        
        # Get user's activities
        user_activities = await self.activity_repository.get_user_activities(
            business_id=business_id,
            user_id=user_id,
            start_date=start_date,
            end_date=now
        )
        
        # Calculate metrics
        total_activities = len(user_activities)
        completed_activities = len([a for a in user_activities if a.status.value == 'completed'])
        overdue_activities = len([a for a in user_activities if a.is_overdue()])
        
        # Group by type
        activities_by_type = {}
        for activity in user_activities:
            activity_type = activity.activity_type.value
            activities_by_type[activity_type] = activities_by_type.get(activity_type, 0) + 1
        
        # Recent achievements (completed high-priority activities)
        achievements = [
            a for a in user_activities 
            if a.status.value == 'completed' and a.priority.value in ['high', 'urgent']
        ][-5:]  # Last 5 achievements
        
        return {
            'period': period,
            'start_date': start_date,
            'end_date': now,
            'total_activities': total_activities,
            'completed_activities': completed_activities,
            'overdue_activities': overdue_activities,
            'completion_rate': (completed_activities / total_activities * 100) if total_activities > 0 else 0,
            'activities_by_type': activities_by_type,
            'recent_achievements': [
                {
                    'id': str(a.id),
                    'title': a.title,
                    'completed_date': a.completed_date,
                    'priority': a.priority.value
                } for a in achievements
            ]
        }
    
    # Private helper methods
    
    async def _get_activity_events(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[TimelineEvent]:
        """Get timeline events from activities."""
        activities = await self.activity_repository.get_contact_timeline(
            contact_id=contact_id,
            business_id=business_id,
            start_date=start_date,
            end_date=end_date,
            limit=1000  # Get all for aggregation
        )
        
        events = []
        for activity in activities:
            event = TimelineEvent(
                id=f"activity_{activity.id}",
                event_type=TimelineEventType.ACTIVITY,
                timestamp=activity.scheduled_date or activity.created_date,
                title=activity.title,
                description=activity.description,
                actor_id=activity.created_by,
                actor_name=activity.created_by,  # Would need user lookup
                metadata={
                    'activity_type': activity.activity_type.value,
                    'status': activity.status.value,
                    'priority': activity.priority.value,
                    'duration_minutes': activity.duration_minutes,
                    'location': activity.location
                },
                priority=activity.priority.value,
                tags=activity.tags,
                related_entities={
                    'activity': str(activity.id),
                    'contact': str(contact_id)
                }
            )
            events.append(event)
        
        return events
    
    async def _get_interaction_events(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[TimelineEvent]:
        """Get timeline events from contact interactions."""
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact or not contact.interaction_history:
            return []
        
        events = []
        for i, interaction in enumerate(contact.interaction_history):
            interaction_date = datetime.fromisoformat(interaction.get('timestamp', datetime.utcnow().isoformat()))
            
            # Apply date filters
            if start_date and interaction_date < start_date:
                continue
            if end_date and interaction_date > end_date:
                continue
            
            event = TimelineEvent(
                id=f"interaction_{contact_id}_{i}",
                event_type=TimelineEventType.INTERACTION,
                timestamp=interaction_date,
                title=f"{interaction.get('type', 'Contact')} Interaction",
                description=interaction.get('description', ''),
                actor_id=interaction.get('created_by', 'system'),
                actor_name=interaction.get('created_by', 'System'),
                metadata={
                    'interaction_type': interaction.get('type'),
                    'outcome': interaction.get('outcome'),
                    'next_action': interaction.get('next_action'),
                    'duration_minutes': interaction.get('duration_minutes')
                },
                priority="medium",
                tags=interaction.get('tags', []),
                related_entities={
                    'contact': str(contact_id),
                    'interaction': f"{contact_id}_{i}"
                }
            )
            events.append(event)
        
        return events
    
    async def _get_status_change_events(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[TimelineEvent]:
        """Get timeline events from contact status changes."""
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact or not contact.status_history:
            return []
        
        events = []
        for i, status_change in enumerate(contact.status_history):
            change_date = datetime.fromisoformat(status_change.get('changed_at', datetime.utcnow().isoformat()))
            
            # Apply date filters
            if start_date and change_date < start_date:
                continue
            if end_date and change_date > end_date:
                continue
            
            event = TimelineEvent(
                id=f"status_change_{contact_id}_{i}",
                event_type=TimelineEventType.STATUS_CHANGE,
                timestamp=change_date,
                title=f"Status Changed: {status_change.get('from_status')} → {status_change.get('to_status')}",
                description=status_change.get('notes', ''),
                actor_id=status_change.get('changed_by', 'system'),
                actor_name=status_change.get('changed_by', 'System'),
                metadata={
                    'from_status': status_change.get('from_status'),
                    'to_status': status_change.get('to_status'),
                    'reason': status_change.get('reason')
                },
                priority="medium",
                tags=['status-change'],
                related_entities={
                    'contact': str(contact_id),
                    'status_change': f"{contact_id}_{i}"
                }
            )
            events.append(event)
        
        return events
    
    async def _get_system_events(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[TimelineEvent]:
        """Get system-generated timeline events."""
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            return []
        
        events = []
        
        # Contact creation event
        if not start_date or contact.created_date >= start_date:
            if not end_date or contact.created_date <= end_date:
                event = TimelineEvent(
                    id=f"system_contact_created_{contact_id}",
                    event_type=TimelineEventType.SYSTEM_EVENT,
                    timestamp=contact.created_date,
                    title="Contact Created",
                    description=f"Contact {contact.display_name} was added to the system",
                    actor_id=contact.created_by,
                    actor_name=contact.created_by,
                    metadata={
                        'event_type': 'contact_created',
                        'contact_type': contact.contact_type.value,
                        'source': contact.source.value if contact.source else None
                    },
                    priority="low",
                    tags=['system', 'creation'],
                    related_entities={
                        'contact': str(contact_id)
                    }
                )
                events.append(event)
        
        # Last contacted event
        if contact.last_contacted:
            if not start_date or contact.last_contacted >= start_date:
                if not end_date or contact.last_contacted <= end_date:
                    event = TimelineEvent(
                        id=f"system_last_contacted_{contact_id}",
                        event_type=TimelineEventType.SYSTEM_EVENT,
                        timestamp=contact.last_contacted,
                        title="Last Contact Updated",
                        description="Contact timestamp was updated",
                        actor_id="system",
                        actor_name="System",
                        metadata={
                            'event_type': 'last_contacted_updated'
                        },
                        priority="low",
                        tags=['system', 'contact-update'],
                        related_entities={
                            'contact': str(contact_id)
                        }
                    )
                    events.append(event)
        
        return events
    
    async def _get_milestone_events(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[TimelineEvent]:
        """Get milestone events (significant achievements or changes)."""
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            return []
        
        events = []
        
        # Check for relationship status milestones
        if contact.status_history:
            for i, status_change in enumerate(contact.status_history):
                change_date = datetime.fromisoformat(status_change.get('changed_at', datetime.utcnow().isoformat()))
                to_status = status_change.get('to_status')
                
                # Apply date filters
                if start_date and change_date < start_date:
                    continue
                if end_date and change_date > end_date:
                    continue
                
                # Check if this is a milestone status
                milestone_statuses = ['active_client', 'qualified_lead', 'opportunity']
                if to_status in milestone_statuses:
                    milestone_titles = {
                        'active_client': '🎉 Became Active Client',
                        'qualified_lead': '📈 Qualified as Lead',
                        'opportunity': '💼 Identified as Opportunity'
                    }
                    
                    event = TimelineEvent(
                        id=f"milestone_{contact_id}_{to_status}_{i}",
                        event_type=TimelineEventType.MILESTONE,
                        timestamp=change_date,
                        title=milestone_titles.get(to_status, f"Milestone: {to_status}"),
                        description=f"Contact reached {to_status} status",
                        actor_id=status_change.get('changed_by', 'system'),
                        actor_name=status_change.get('changed_by', 'System'),
                        metadata={
                            'milestone_type': 'status_milestone',
                            'status': to_status,
                            'previous_status': status_change.get('from_status')
                        },
                        priority="high",
                        tags=['milestone', 'achievement', to_status],
                        related_entities={
                            'contact': str(contact_id),
                            'milestone': f"{to_status}_{i}"
                        }
                    )
                    events.append(event)
        
        return events
    
    def _group_events_by_day(self, events: List[TimelineEvent]) -> List[TimelineEvent]:
        """Group events by day for better visualization."""
        if not events:
            return events
        
        # For now, just return events as-is
        # In a full implementation, you might create day separator events
        # or modify the event structure to include day grouping information
        return events
    
    def _event_to_timeline_entry(self, event: TimelineEvent) -> TimelineEntryDTO:
        """Convert a TimelineEvent to a TimelineEntryDTO."""
        return TimelineEntryDTO(
            id=event.id,
            type=event.event_type.value,
            title=event.title,
            description=event.description,
            timestamp=event.timestamp,
            status=event.metadata.get('status', 'active'),
            priority=event.priority,
            created_by=event.actor_id,
            assigned_to=event.metadata.get('assigned_to'),
            metadata=event.metadata,
            tags=event.tags,
            is_overdue=False,  # Would need logic to determine this
            type_display=self._get_type_display(event.event_type),
            status_display=event.metadata.get('status', 'Active').title(),
            priority_display=event.priority.title()
        )
    
    def _get_type_display(self, event_type: TimelineEventType) -> str:
        """Get human-readable display name for event type."""
        display_names = {
            TimelineEventType.ACTIVITY: "Activity",
            TimelineEventType.INTERACTION: "Interaction",
            TimelineEventType.STATUS_CHANGE: "Status Change",
            TimelineEventType.SYSTEM_EVENT: "System Event",
            TimelineEventType.MILESTONE: "Milestone"
        }
        return display_names.get(event_type, event_type.value.title()) 