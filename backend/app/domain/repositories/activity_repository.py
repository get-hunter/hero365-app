"""
Activity Repository Interface

Defines the contract for activity data access operations.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..entities.activity import Activity, ActivityTemplate, ActivityType, ActivityStatus, ActivityPriority


class ActivityRepository(ABC):
    """Repository interface for activity management."""
    
    @abstractmethod
    async def create(self, activity: Activity) -> Activity:
        """Create a new activity."""
        pass
    
    @abstractmethod
    async def get_by_id(self, activity_id: uuid.UUID) -> Optional[Activity]:
        """Get activity by ID."""
        pass
    
    @abstractmethod
    async def update(self, activity: Activity) -> Activity:
        """Update an existing activity."""
        pass
    
    @abstractmethod
    async def delete(self, activity_id: uuid.UUID) -> bool:
        """Delete an activity."""
        pass
    
    # Contact timeline queries
    @abstractmethod
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
        """Get timeline activities for a contact."""
        pass
    
    @abstractmethod
    async def get_contact_activity_count(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        activity_types: Optional[List[ActivityType]] = None
    ) -> int:
        """Get count of activities for a contact."""
        pass
    
    # Business activities queries
    @abstractmethod
    async def get_business_activities(
        self,
        business_id: uuid.UUID,
        activity_types: Optional[List[ActivityType]] = None,
        statuses: Optional[List[ActivityStatus]] = None,
        assigned_to: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Activity]:
        """Get activities for a business with filtering."""
        pass
    
    @abstractmethod
    async def get_user_activities(
        self,
        business_id: uuid.UUID,
        user_id: str,
        statuses: Optional[List[ActivityStatus]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Activity]:
        """Get activities assigned to a user."""
        pass
    
    # Overdue and upcoming activities
    @abstractmethod
    async def get_overdue_activities(
        self,
        business_id: uuid.UUID,
        assigned_to: Optional[str] = None
    ) -> List[Activity]:
        """Get overdue activities."""
        pass
    
    @abstractmethod
    async def get_upcoming_activities(
        self,
        business_id: uuid.UUID,
        days_ahead: int = 7,
        assigned_to: Optional[str] = None
    ) -> List[Activity]:
        """Get upcoming activities within specified days."""
        pass
    
    # Reminders
    @abstractmethod
    async def get_pending_reminders(
        self,
        business_id: uuid.UUID,
        before_date: datetime
    ) -> List[Activity]:
        """Get activities with pending reminders due before the specified date."""
        pass
    
    # Activity statistics
    @abstractmethod
    async def get_activity_statistics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get activity statistics for a business or user."""
        pass
    
    @abstractmethod
    async def get_contact_activity_summary(
        self,
        contact_id: uuid.UUID,
        business_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get activity summary for a specific contact."""
        pass


class ActivityTemplateRepository(ABC):
    """Repository interface for activity template management."""
    
    @abstractmethod
    async def create_template(self, template: ActivityTemplate) -> ActivityTemplate:
        """Create a new activity template."""
        pass
    
    @abstractmethod
    async def get_template_by_id(self, template_id: uuid.UUID) -> Optional[ActivityTemplate]:
        """Get template by ID."""
        pass
    
    @abstractmethod
    async def update_template(self, template: ActivityTemplate) -> ActivityTemplate:
        """Update an existing template."""
        pass
    
    @abstractmethod
    async def delete_template(self, template_id: uuid.UUID) -> bool:
        """Delete a template."""
        pass
    
    @abstractmethod
    async def get_business_templates(
        self,
        business_id: uuid.UUID,
        activity_type: Optional[ActivityType] = None,
        is_active: bool = True
    ) -> List[ActivityTemplate]:
        """Get templates for a business."""
        pass
    
    @abstractmethod
    async def get_templates_by_type(
        self,
        business_id: uuid.UUID,
        activity_type: ActivityType
    ) -> List[ActivityTemplate]:
        """Get templates by activity type."""
        pass 