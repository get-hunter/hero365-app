"""
User Capabilities Repository Interface

Domain repository interface for user capabilities management.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
import uuid

from ..entities.user_capabilities import UserCapabilities


class UserCapabilitiesRepository(ABC):
    """Repository interface for user capabilities management."""
    
    @abstractmethod
    async def create(self, user_capabilities: UserCapabilities) -> UserCapabilities:
        """Create new user capabilities."""
        pass
    
    @abstractmethod
    async def get_by_id(self, capabilities_id: uuid.UUID) -> Optional[UserCapabilities]:
        """Get user capabilities by ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, business_id: uuid.UUID, user_id: str) -> Optional[UserCapabilities]:
        """Get user capabilities by user ID within a business."""
        pass
    
    @abstractmethod
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[UserCapabilities]:
        """Get all user capabilities for a business."""
        pass
    
    @abstractmethod
    async def update(self, user_capabilities: UserCapabilities) -> UserCapabilities:
        """Update user capabilities."""
        pass
    
    @abstractmethod
    async def delete(self, capabilities_id: uuid.UUID) -> bool:
        """Delete user capabilities."""
        pass
    
    @abstractmethod
    async def get_users_with_skill(self, business_id: uuid.UUID, skill_name: str, min_level: str = "beginner") -> List[UserCapabilities]:
        """Get users with specific skill and minimum level."""
        pass
    
    @abstractmethod
    async def get_available_users(self, business_id: uuid.UUID, start_time: str, end_time: str) -> List[UserCapabilities]:
        """Get users available during specific time window."""
        pass 