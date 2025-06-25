"""
Supabase Activity Repository Implementation

Implements the ActivityRepository interface using Supabase as the data store.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from supabase import Client
from postgrest.exceptions import APIError

from app.domain.repositories.activity_repository import ActivityRepository, ActivityTemplateRepository
from app.domain.entities.activity import (
    Activity, ActivityTemplate, ActivityType, ActivityStatus, ActivityPriority,
    ActivityParticipant, ActivityReminder
)
from app.domain.exceptions.domain_exceptions import (
    DomainValidationError, EntityNotFoundError, RepositoryError
)

logger = logging.getLogger(__name__)


class SupabaseActivityRepository(ActivityRepository):
    """
    Supabase implementation of the ActivityRepository interface.
    
    Handles all activity-related database operations using Supabase client.
    """
    
    def __init__(self, client: Client):
        self.client = client
    
    async def create(self, activity: Activity) -> Activity:
        """Create a new activity in the database."""
        try:
            activity_data = {
                'id': str(activity.id),
                'business_id': str(activity.business_id),
                'contact_id': str(activity.contact_id),
                'template_id': str(activity.template_id) if activity.template_id else None,
                'parent_activity_id': str(activity.parent_activity_id) if activity.parent_activity_id else None,
                'activity_type': activity.activity_type.value,
                'title': activity.title,
                'description': activity.description,
                'status': activity.status.value,
                'priority': activity.priority.value,
                'scheduled_date': activity.scheduled_date.isoformat() if activity.scheduled_date else None,
                'due_date': activity.due_date.isoformat() if activity.due_date else None,
                'completed_date': activity.completed_date.isoformat() if activity.completed_date else None,
                'duration_minutes': activity.duration_minutes,
                'location': activity.location,
                'metadata': activity.metadata,
                'tags': activity.tags,
                'created_by': activity.created_by,
                'assigned_to': activity.assigned_to,
                'created_date': activity.created_date.isoformat(),
                'last_modified': activity.last_modified.isoformat()
            }
            
            # Insert activity
            result = self.client.table('activities').insert(activity_data).execute()
            
            if not result.data:
                raise RepositoryError("Failed to create activity")
            
            # Create participants if any
            if activity.participants:
                await self._create_participants(activity.id, activity.participants)
            
            # Create reminders if any
            if activity.reminders:
                await self._create_reminders(activity.id, activity.reminders)
            
            logger.info(f"Created activity {activity.id} for business {activity.business_id}")
            return activity
            
        except APIError as e:
            logger.error(f"Database error creating activity: {str(e)}")
            raise RepositoryError(f"Failed to create activity: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating activity: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def get_by_id(self, activity_id: uuid.UUID) -> Optional[Activity]:
        """Get an activity by ID."""
        try:
            # Get activity with participants and reminders
            result = self.client.table('activities').select(
                '*'
            ).eq('id', str(activity_id)).single().execute()
            
            if not result.data:
                return None
            
            # Get participants
            participants_result = self.client.table('activity_participants').select(
                '*'
            ).eq('activity_id', str(activity_id)).execute()
            
            # Get reminders
            reminders_result = self.client.table('activity_reminders').select(
                '*'
            ).eq('activity_id', str(activity_id)).execute()
            
            return self._map_to_activity(
                result.data,
                participants_result.data or [],
                reminders_result.data or []
            )
            
        except APIError as e:
            logger.error(f"Database error getting activity {activity_id}: {str(e)}")
            raise RepositoryError(f"Failed to get activity: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting activity {activity_id}: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def update(self, activity: Activity) -> Activity:
        """Update an existing activity."""
        try:
            activity_data = {
                'title': activity.title,
                'description': activity.description,
                'status': activity.status.value,
                'priority': activity.priority.value,
                'scheduled_date': activity.scheduled_date.isoformat() if activity.scheduled_date else None,
                'due_date': activity.due_date.isoformat() if activity.due_date else None,
                'completed_date': activity.completed_date.isoformat() if activity.completed_date else None,
                'duration_minutes': activity.duration_minutes,
                'location': activity.location,
                'metadata': activity.metadata,
                'tags': activity.tags,
                'assigned_to': activity.assigned_to,
                'last_modified': activity.last_modified.isoformat()
            }
            
            result = self.client.table('activities').update(activity_data).eq(
                'id', str(activity.id)
            ).execute()
            
            if not result.data:
                raise EntityNotFoundError(f"Activity {activity.id} not found")
            
            # Update participants (delete and recreate for simplicity)
            await self._update_participants(activity.id, activity.participants)
            
            # Update reminders (delete and recreate for simplicity)
            await self._update_reminders(activity.id, activity.reminders)
            
            logger.info(f"Updated activity {activity.id}")
            return activity
            
        except APIError as e:
            logger.error(f"Database error updating activity {activity.id}: {str(e)}")
            raise RepositoryError(f"Failed to update activity: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating activity {activity.id}: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def delete(self, activity_id: uuid.UUID) -> bool:
        """Delete an activity and all related data."""
        try:
            # Delete participants first (foreign key constraint)
            self.client.table('activity_participants').delete().eq(
                'activity_id', str(activity_id)
            ).execute()
            
            # Delete reminders
            self.client.table('activity_reminders').delete().eq(
                'activity_id', str(activity_id)
            ).execute()
            
            # Delete activity
            result = self.client.table('activities').delete().eq(
                'id', str(activity_id)
            ).execute()
            
            success = len(result.data) > 0 if result.data else False
            
            if success:
                logger.info(f"Deleted activity {activity_id}")
            
            return success
            
        except APIError as e:
            logger.error(f"Database error deleting activity {activity_id}: {str(e)}")
            raise RepositoryError(f"Failed to delete activity: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting activity {activity_id}: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def get_contact_timeline(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        activity_types: Optional[List[ActivityType]] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Activity]:
        """Get activities for a contact's timeline."""
        try:
            query = self.client.table('activities').select('*').eq(
                'contact_id', str(contact_id)
            ).eq('business_id', str(business_id))
            
            # Apply filters
            if start_date:
                query = query.gte('created_date', start_date.isoformat())
            
            if end_date:
                query = query.lte('created_date', end_date.isoformat())
            
            if activity_types:
                type_values = [t.value for t in activity_types]
                query = query.in_('activity_type', type_values)
            
            # Order by created_date descending and apply pagination
            result = query.order('created_date', desc=True).range(skip, skip + limit - 1).execute()
            
            activities = []
            for row in result.data or []:
                # Get participants and reminders for each activity
                participants = await self._get_activity_participants(uuid.UUID(row['id']))
                reminders = await self._get_activity_reminders(uuid.UUID(row['id']))
                
                activity = self._map_to_activity(row, participants, reminders)
                activities.append(activity)
            
            return activities
            
        except APIError as e:
            logger.error(f"Database error getting contact timeline: {str(e)}")
            raise RepositoryError(f"Failed to get contact timeline: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting contact timeline: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def get_business_activities(
        self,
        business_id: uuid.UUID,
        activity_types: Optional[List[ActivityType]] = None,
        statuses: Optional[List[ActivityStatus]] = None,
        assigned_to: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Activity]:
        """Get activities for a business with filtering."""
        try:
            query = self.client.table('activities').select('*').eq(
                'business_id', str(business_id)
            )
            
            # Apply filters
            if activity_types:
                type_values = [t.value for t in activity_types]
                query = query.in_('activity_type', type_values)
            
            if statuses:
                status_values = [s.value for s in statuses]
                query = query.in_('status', status_values)
            
            if assigned_to:
                query = query.eq('assigned_to', assigned_to)
            
            if start_date:
                query = query.gte('scheduled_date', start_date.isoformat())
            
            if end_date:
                query = query.lte('scheduled_date', end_date.isoformat())
            
            # Order by scheduled_date descending and apply pagination
            result = query.order('scheduled_date', desc=True).range(skip, skip + limit - 1).execute()
            
            activities = []
            for row in result.data or []:
                # For performance, skip participants and reminders in list view
                activity = self._map_to_activity(row, [], [])
                activities.append(activity)
            
            return activities
            
        except APIError as e:
            logger.error(f"Database error getting business activities: {str(e)}")
            raise RepositoryError(f"Failed to get business activities: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting business activities: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def get_user_activities(
        self,
        business_id: uuid.UUID,
        user_id: str,
        statuses: Optional[List[ActivityStatus]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Activity]:
        """Get activities assigned to a specific user."""
        try:
            query = self.client.table('activities').select('*').eq(
                'business_id', str(business_id)
            ).eq('assigned_to', user_id)
            
            # Apply filters
            if statuses:
                status_values = [s.value for s in statuses]
                query = query.in_('status', status_values)
            
            if start_date:
                query = query.gte('scheduled_date', start_date.isoformat())
            
            if end_date:
                query = query.lte('scheduled_date', end_date.isoformat())
            
            # Order by scheduled_date ascending (upcoming first)
            result = query.order('scheduled_date', desc=False).range(skip, skip + limit - 1).execute()
            
            activities = []
            for row in result.data or []:
                activity = self._map_to_activity(row, [], [])
                activities.append(activity)
            
            return activities
            
        except APIError as e:
            logger.error(f"Database error getting user activities: {str(e)}")
            raise RepositoryError(f"Failed to get user activities: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting user activities: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def get_overdue_activities(
        self,
        business_id: uuid.UUID,
        assigned_to: Optional[str] = None
    ) -> List[Activity]:
        """Get overdue activities."""
        try:
            current_time = datetime.utcnow()
            
            query = self.client.table('activities').select('*').eq(
                'business_id', str(business_id)
            ).in_('status', ['pending', 'in_progress']).lt(
                'due_date', current_time.isoformat()
            ).not_.is_('due_date', 'null')
            
            if assigned_to:
                query = query.eq('assigned_to', assigned_to)
            
            result = query.order('due_date', desc=False).execute()
            
            activities = []
            for row in result.data or []:
                activity = self._map_to_activity(row, [], [])
                activities.append(activity)
            
            return activities
            
        except APIError as e:
            logger.error(f"Database error getting overdue activities: {str(e)}")
            raise RepositoryError(f"Failed to get overdue activities: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting overdue activities: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def get_upcoming_activities(
        self,
        business_id: uuid.UUID,
        days_ahead: int = 7,
        assigned_to: Optional[str] = None
    ) -> List[Activity]:
        """Get upcoming activities within specified days."""
        try:
            current_time = datetime.utcnow()
            end_time = current_time + timedelta(days=days_ahead)
            
            query = self.client.table('activities').select('*').eq(
                'business_id', str(business_id)
            ).in_('status', ['pending', 'in_progress']).gte(
                'scheduled_date', current_time.isoformat()
            ).lte('scheduled_date', end_time.isoformat())
            
            if assigned_to:
                query = query.eq('assigned_to', assigned_to)
            
            result = query.order('scheduled_date', desc=False).execute()
            
            activities = []
            for row in result.data or []:
                activity = self._map_to_activity(row, [], [])
                activities.append(activity)
            
            return activities
            
        except APIError as e:
            logger.error(f"Database error getting upcoming activities: {str(e)}")
            raise RepositoryError(f"Failed to get upcoming activities: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting upcoming activities: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def get_activity_statistics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get activity statistics for analytics."""
        try:
            # Base query
            query = self.client.table('activities').select('*').eq(
                'business_id', str(business_id)
            )
            
            # Apply filters
            if start_date:
                query = query.gte('created_date', start_date.isoformat())
            
            if end_date:
                query = query.lte('created_date', end_date.isoformat())
            
            if user_id:
                query = query.eq('assigned_to', user_id)
            
            result = query.execute()
            activities = result.data or []
            
            # Calculate statistics
            total_activities = len(activities)
            pending_activities = len([a for a in activities if a['status'] == 'pending'])
            in_progress_activities = len([a for a in activities if a['status'] == 'in_progress'])
            completed_activities = len([a for a in activities if a['status'] == 'completed'])
            overdue_activities = len([
                a for a in activities 
                if a['status'] in ['pending', 'in_progress'] and a['due_date'] and 
                datetime.fromisoformat(a['due_date'].replace('Z', '+00:00')) < datetime.utcnow()
            ])
            
            # Group by type
            activities_by_type = {}
            for activity in activities:
                activity_type = activity['activity_type']
                activities_by_type[activity_type] = activities_by_type.get(activity_type, 0) + 1
            
            # Group by priority
            activities_by_priority = {}
            for activity in activities:
                priority = activity['priority']
                activities_by_priority[priority] = activities_by_priority.get(priority, 0) + 1
            
            # Calculate completion rate
            completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0
            
            return {
                'total_activities': total_activities,
                'pending_activities': pending_activities,
                'in_progress_activities': in_progress_activities,
                'completed_activities': completed_activities,
                'overdue_activities': overdue_activities,
                'activities_by_type': activities_by_type,
                'activities_by_priority': activities_by_priority,
                'completion_rate': completion_rate,
                'upcoming_activities_count': 0,  # Would need separate query
                'activities_this_week': 0,  # Would need separate query
                'activities_this_month': 0,  # Would need separate query
                'average_completion_time': 0.0  # Would need more complex calculation
            }
            
        except APIError as e:
            logger.error(f"Database error getting activity statistics: {str(e)}")
            raise RepositoryError(f"Failed to get activity statistics: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting activity statistics: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")

    async def get_contact_activity_count(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        activity_types: Optional[List[ActivityType]] = None
    ) -> int:
        """Get count of activities for a contact."""
        try:
            query = self.client.table('activities').select(
                'id', count='exact'
            ).eq('contact_id', str(contact_id)).eq('business_id', str(business_id))
            
            # Apply date filters
            if start_date:
                query = query.gte('created_date', start_date.isoformat())
            if end_date:
                query = query.lte('created_date', end_date.isoformat())
            
            # Apply activity type filter
            if activity_types:
                type_values = [t.value for t in activity_types]
                query = query.in_('activity_type', type_values)
            
            result = query.execute()
            return result.count or 0
            
        except APIError as e:
            logger.error(f"Database error getting contact activity count: {str(e)}")
            raise RepositoryError(f"Failed to get contact activity count: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting contact activity count: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")

    async def get_contact_activity_summary(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get activity summary for a specific contact."""
        try:
            # Get all activities for the contact
            result = self.client.table('activities').select('*').eq(
                'contact_id', str(contact_id)
            ).eq('business_id', str(business_id)).execute()
            
            activities = result.data or []
            
            if not activities:
                return {
                    'total_activities': 0,
                    'by_type': {},
                    'by_status': {},
                    'last_activity_date': None,
                    'next_scheduled_date': None,
                    'engagement_score': 0
                }
            
            # Calculate summary statistics
            total_activities = len(activities)
            
            # Group by type
            by_type = {}
            for activity in activities:
                activity_type = activity['activity_type']
                by_type[activity_type] = by_type.get(activity_type, 0) + 1
            
            # Group by status
            by_status = {}
            for activity in activities:
                status = activity['status']
                by_status[status] = by_status.get(status, 0) + 1
            
            # Find last activity date
            last_activity_date = None
            completed_activities = [a for a in activities if a['completed_date']]
            if completed_activities:
                last_completed = max(completed_activities, key=lambda x: x['completed_date'])
                last_activity_date = last_completed['completed_date']
            
            # Find next scheduled date
            next_scheduled_date = None
            scheduled_activities = [
                a for a in activities 
                if a['scheduled_date'] and a['status'] in ['pending', 'in_progress']
            ]
            if scheduled_activities:
                next_activity = min(scheduled_activities, key=lambda x: x['scheduled_date'])
                next_scheduled_date = next_activity['scheduled_date']
            
            # Calculate engagement score (simple heuristic)
            completed_count = by_status.get('completed', 0)
            engagement_score = min(100, (completed_count / total_activities * 100)) if total_activities > 0 else 0
            
            return {
                'total_activities': total_activities,
                'by_type': by_type,
                'by_status': by_status,
                'last_activity_date': last_activity_date,
                'next_scheduled_date': next_scheduled_date,
                'engagement_score': round(engagement_score, 2)
            }
            
        except APIError as e:
            logger.error(f"Database error getting contact activity summary: {str(e)}")
            raise RepositoryError(f"Failed to get contact activity summary: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting contact activity summary: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")

    async def get_pending_reminders(
        self,
        business_id: uuid.UUID,
        before_date: datetime
    ) -> List[Activity]:
        """Get activities with pending reminders due before the specified date."""
        try:
            # Query activities with reminders due before the specified date
            # Join with activity_reminders table
            result = self.client.table('activities').select(
                '*, activity_reminders(*)'
            ).eq('business_id', str(business_id)).execute()
            
            activities_with_reminders = []
            
            for activity_data in result.data or []:
                # Check if activity has reminders due before the specified date
                reminders = activity_data.get('activity_reminders', [])
                has_pending_reminder = False
                
                for reminder in reminders:
                    if (reminder.get('is_sent', False) is False and 
                        reminder.get('reminder_time') and
                        datetime.fromisoformat(reminder['reminder_time'].replace('Z', '+00:00')) <= before_date):
                        has_pending_reminder = True
                        break
                
                if has_pending_reminder:
                    # Get participants for this activity
                    participants_result = self.client.table('activity_participants').select(
                        '*'
                    ).eq('activity_id', activity_data['id']).execute()
                    
                    activity = self._map_to_activity(
                        activity_data,
                        participants_result.data or [],
                        reminders
                    )
                    activities_with_reminders.append(activity)
            
            logger.info(f"Found {len(activities_with_reminders)} activities with pending reminders")
            return activities_with_reminders
            
        except APIError as e:
            logger.error(f"Database error getting pending reminders: {str(e)}")
            raise RepositoryError(f"Failed to get pending reminders: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting pending reminders: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    # Helper methods for participants and reminders
    
    async def _create_participants(self, activity_id: uuid.UUID, participants: List[ActivityParticipant]):
        """Create activity participants."""
        if not participants:
            return
        
        participant_data = [
            {
                'activity_id': str(activity_id),
                'user_id': p.user_id,
                'name': p.name,
                'role': p.role,
                'is_primary': p.is_primary
            }
            for p in participants
        ]
        
        self.client.table('activity_participants').insert(participant_data).execute()
    
    async def _create_reminders(self, activity_id: uuid.UUID, reminders: List[ActivityReminder]):
        """Create activity reminders."""
        if not reminders:
            return
        
        reminder_data = [
            {
                'id': str(r.reminder_id),
                'activity_id': str(activity_id),
                'reminder_time': r.reminder_time.isoformat(),
                'reminder_type': r.reminder_type,
                'message': r.message,
                'is_sent': r.is_sent,
                'sent_at': r.sent_at.isoformat() if r.sent_at else None
            }
            for r in reminders
        ]
        
        self.client.table('activity_reminders').insert(reminder_data).execute()
    
    async def _update_participants(self, activity_id: uuid.UUID, participants: List[ActivityParticipant]):
        """Update activity participants (delete and recreate)."""
        # Delete existing
        self.client.table('activity_participants').delete().eq(
            'activity_id', str(activity_id)
        ).execute()
        
        # Create new
        await self._create_participants(activity_id, participants)
    
    async def _update_reminders(self, activity_id: uuid.UUID, reminders: List[ActivityReminder]):
        """Update activity reminders (delete and recreate)."""
        # Delete existing
        self.client.table('activity_reminders').delete().eq(
            'activity_id', str(activity_id)
        ).execute()
        
        # Create new
        await self._create_reminders(activity_id, reminders)
    
    async def _get_activity_participants(self, activity_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get participants for an activity."""
        result = self.client.table('activity_participants').select('*').eq(
            'activity_id', str(activity_id)
        ).execute()
        
        return result.data or []
    
    async def _get_activity_reminders(self, activity_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get reminders for an activity."""
        result = self.client.table('activity_reminders').select('*').eq(
            'activity_id', str(activity_id)
        ).execute()
        
        return result.data or []
    
    def _map_to_activity(
        self,
        row: Dict[str, Any],
        participants_data: List[Dict[str, Any]],
        reminders_data: List[Dict[str, Any]]
    ) -> Activity:
        """Map database row to Activity entity."""
        # Map participants
        participants = [
            ActivityParticipant(
                user_id=p['user_id'],
                name=p['name'],
                role=p['role'],
                is_primary=p['is_primary']
            )
            for p in participants_data
        ]
        
        # Map reminders
        reminders = [
            ActivityReminder(
                reminder_id=uuid.UUID(r['id']),
                reminder_time=datetime.fromisoformat(r['reminder_time'].replace('Z', '+00:00')),
                reminder_type=r['reminder_type'],
                message=r['message'],
                is_sent=r['is_sent'],
                sent_at=datetime.fromisoformat(r['sent_at'].replace('Z', '+00:00')) if r['sent_at'] else None
            )
            for r in reminders_data
        ]
        
        return Activity(
            id=uuid.UUID(row['id']),
            business_id=uuid.UUID(row['business_id']),
            contact_id=uuid.UUID(row['contact_id']),
            activity_type=ActivityType(row['activity_type']),
            title=row['title'],
            description=row['description'],
            status=ActivityStatus(row['status']),
            priority=ActivityPriority(row['priority']),
            scheduled_date=datetime.fromisoformat(row['scheduled_date'].replace('Z', '+00:00')) if row['scheduled_date'] else None,
            due_date=datetime.fromisoformat(row['due_date'].replace('Z', '+00:00')) if row['due_date'] else None,
            completed_date=datetime.fromisoformat(row['completed_date'].replace('Z', '+00:00')) if row['completed_date'] else None,
            duration_minutes=row['duration_minutes'],
            location=row['location'],
            participants=participants,
            reminders=reminders,
            metadata=row['metadata'] or {},
            tags=row['tags'] or [],
            created_by=row['created_by'],
            assigned_to=row['assigned_to'],
            template_id=uuid.UUID(row['template_id']) if row['template_id'] else None,
            parent_activity_id=uuid.UUID(row['parent_activity_id']) if row['parent_activity_id'] else None,
            created_date=datetime.fromisoformat(row['created_date'].replace('Z', '+00:00')),
            last_modified=datetime.fromisoformat(row['last_modified'].replace('Z', '+00:00'))
        )


class SupabaseActivityTemplateRepository(ActivityTemplateRepository):
    """
    Supabase implementation of the ActivityTemplateRepository interface.
    """
    
    def __init__(self, client: Client):
        self.client = client
    
    async def create(self, template: ActivityTemplate) -> ActivityTemplate:
        """Create a new activity template."""
        try:
            template_data = {
                'id': str(template.template_id),
                'name': template.name,
                'description': template.description,
                'activity_type': template.activity_type.value,
                'default_duration': template.default_duration,
                'default_reminders': template.default_reminders,
                'default_participants': template.default_participants,
                'custom_fields': template.custom_fields,
                'is_active': template.is_active,
                'created_by': template.created_by,
                'created_date': template.created_date.isoformat()
            }
            
            result = self.client.table('activity_templates').insert(template_data).execute()
            
            if not result.data:
                raise RepositoryError("Failed to create activity template")
            
            logger.info(f"Created activity template {template.template_id}")
            return template
            
        except APIError as e:
            logger.error(f"Database error creating activity template: {str(e)}")
            raise RepositoryError(f"Failed to create activity template: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating activity template: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def get_by_id(self, template_id: uuid.UUID) -> Optional[ActivityTemplate]:
        """Get an activity template by ID."""
        try:
            result = self.client.table('activity_templates').select('*').eq(
                'id', str(template_id)
            ).single().execute()
            
            if not result.data:
                return None
            
            return self._map_to_template(result.data)
            
        except APIError as e:
            logger.error(f"Database error getting activity template {template_id}: {str(e)}")
            raise RepositoryError(f"Failed to get activity template: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting activity template {template_id}: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def get_by_business(
        self,
        business_id: uuid.UUID,
        activity_type: Optional[ActivityType] = None,
        is_active: bool = True
    ) -> List[ActivityTemplate]:
        """Get activity templates for a business."""
        try:
            query = self.client.table('activity_templates').select('*').eq(
                'is_active', is_active
            )
            
            if activity_type:
                query = query.eq('activity_type', activity_type.value)
            
            result = query.order('name').execute()
            
            templates = []
            for row in result.data or []:
                template = self._map_to_template(row)
                templates.append(template)
            
            return templates
            
        except APIError as e:
            logger.error(f"Database error getting business activity templates: {str(e)}")
            raise RepositoryError(f"Failed to get business activity templates: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting business activity templates: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")
    
    async def create_template(self, template: ActivityTemplate) -> ActivityTemplate:
        """Create a new activity template."""
        return await self.create(template)

    async def get_template_by_id(self, template_id: uuid.UUID) -> Optional[ActivityTemplate]:
        """Get template by ID."""
        return await self.get_by_id(template_id)

    async def update_template(self, template: ActivityTemplate) -> ActivityTemplate:
        """Update an existing template."""
        try:
            template_data = {
                'name': template.name,
                'description': template.description,
                'activity_type': template.activity_type.value,
                'default_duration': template.default_duration,
                'default_reminders': template.default_reminders,
                'default_participants': template.default_participants,
                'custom_fields': template.custom_fields,
                'is_active': template.is_active
            }
            
            result = self.client.table('activity_templates').update(template_data).eq(
                'id', str(template.template_id)
            ).execute()
            
            if not result.data:
                raise EntityNotFoundError(f"Activity template {template.template_id} not found")
            
            logger.info(f"Updated activity template {template.template_id}")
            return template
            
        except APIError as e:
            logger.error(f"Database error updating activity template {template.template_id}: {str(e)}")
            raise RepositoryError(f"Failed to update activity template: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating activity template {template.template_id}: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")

    async def delete_template(self, template_id: uuid.UUID) -> bool:
        """Delete a template."""
        try:
            result = self.client.table('activity_templates').delete().eq(
                'id', str(template_id)
            ).execute()
            
            success = len(result.data) > 0 if result.data else False
            
            if success:
                logger.info(f"Deleted activity template {template_id}")
            
            return success
            
        except APIError as e:
            logger.error(f"Database error deleting activity template {template_id}: {str(e)}")
            raise RepositoryError(f"Failed to delete activity template: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting activity template {template_id}: {str(e)}")
            raise RepositoryError(f"Unexpected error: {str(e)}")

    async def get_business_templates(
        self,
        business_id: uuid.UUID,
        activity_type: Optional[ActivityType] = None,
        is_active: bool = True
    ) -> List[ActivityTemplate]:
        """Get templates for a business."""
        return await self.get_by_business(business_id, activity_type, is_active)

    async def get_templates_by_type(
        self,
        business_id: uuid.UUID,
        activity_type: ActivityType
    ) -> List[ActivityTemplate]:
        """Get templates by activity type."""
        return await self.get_by_business(business_id, activity_type, True)

    def _map_to_template(self, row: Dict[str, Any]) -> ActivityTemplate:
        """Map database row to ActivityTemplate entity."""
        return ActivityTemplate(
            template_id=uuid.UUID(row['id']),
            name=row['name'],
            description=row['description'],
            activity_type=ActivityType(row['activity_type']),
            created_by=row['created_by'],
            default_duration=row['default_duration'],
            default_reminders=row['default_reminders'] or [],
            default_participants=row['default_participants'] or [],
            custom_fields=row['custom_fields'] or {},
            is_active=row['is_active'],
            created_date=datetime.fromisoformat(row['created_date'].replace('Z', '+00:00'))
        ) 