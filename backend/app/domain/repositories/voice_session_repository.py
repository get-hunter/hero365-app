"""
Voice Session Repository Interface

Repository interface for voice session management with comprehensive CRUD operations,
session tracking, and analytics capabilities.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime

from ..entities.voice_session import VoiceSession
from ..enums import VoiceSessionStatus, AgentType


class VoiceSessionRepository(ABC):
    """Repository interface for voice session management operations."""
    
    # Basic CRUD operations
    @abstractmethod
    async def create(self, session: VoiceSession) -> VoiceSession:
        """Create a new voice session."""
        pass
    
    @abstractmethod
    async def get_by_id(self, business_id: uuid.UUID, session_id: uuid.UUID) -> Optional[VoiceSession]:
        """Get voice session by ID."""
        pass
    
    @abstractmethod
    async def get_by_livekit_room(self, business_id: uuid.UUID, room_name: str) -> Optional[VoiceSession]:
        """Get voice session by LiveKit room name."""
        pass
    
    @abstractmethod
    async def update(self, session: VoiceSession) -> VoiceSession:
        """Update an existing voice session."""
        pass
    
    @abstractmethod
    async def delete(self, business_id: uuid.UUID, session_id: uuid.UUID) -> bool:
        """Delete a voice session."""
        pass
    
    # Session management operations
    @abstractmethod
    async def get_active_sessions(
        self,
        business_id: uuid.UUID,
        user_id: Optional[str] = None,
        agent_type: Optional[AgentType] = None
    ) -> List[VoiceSession]:
        """Get all active voice sessions."""
        pass
    
    @abstractmethod
    async def get_user_active_session(self, business_id: uuid.UUID, user_id: str) -> Optional[VoiceSession]:
        """Get user's current active session."""
        pass
    
    @abstractmethod
    async def get_expired_sessions(self, business_id: uuid.UUID) -> List[VoiceSession]:
        """Get sessions that have expired."""
        pass
    
    @abstractmethod
    async def get_idle_sessions(
        self,
        business_id: uuid.UUID,
        idle_minutes: int = 10
    ) -> List[VoiceSession]:
        """Get sessions that are idle."""
        pass
    
    @abstractmethod
    async def end_expired_sessions(self, business_id: uuid.UUID) -> int:
        """End all expired sessions and return count."""
        pass
    
    # List and search operations
    @abstractmethod
    async def list_by_business(
        self,
        business_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
        status: Optional[VoiceSessionStatus] = None,
        agent_type: Optional[AgentType] = None,
        user_id: Optional[str] = None
    ) -> List[VoiceSession]:
        """List voice sessions for a business with optional filtering."""
        pass
    
    @abstractmethod
    async def list_by_user(
        self,
        business_id: uuid.UUID,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        status: Optional[VoiceSessionStatus] = None
    ) -> List[VoiceSession]:
        """List voice sessions for a specific user."""
        pass
    
    @abstractmethod
    async def search_sessions(
        self,
        business_id: uuid.UUID,
        query: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VoiceSession]:
        """Search sessions by transcript or session notes."""
        pass
    
    # Analytics and reporting operations
    @abstractmethod
    async def get_session_analytics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        agent_type: Optional[AgentType] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive session analytics."""
        pass
    
    @abstractmethod
    async def get_user_session_stats(
        self,
        business_id: uuid.UUID,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get session statistics for a specific user."""
        pass
    
    @abstractmethod
    async def get_agent_performance_metrics(
        self,
        business_id: uuid.UUID,
        agent_type: AgentType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get performance metrics for agent type."""
        pass
    
    @abstractmethod
    async def get_session_duration_analytics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get session duration analytics."""
        pass
    
    @abstractmethod
    async def get_command_success_rate(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        agent_type: Optional[AgentType] = None
    ) -> Decimal:
        """Get overall command success rate."""
        pass
    
    # Session context and command tracking
    @abstractmethod
    async def update_session_context(
        self,
        business_id: uuid.UUID,
        session_id: uuid.UUID,
        context_updates: Dict[str, Any]
    ) -> bool:
        """Update session context data."""
        pass
    
    @abstractmethod
    async def add_command_to_session(
        self,
        business_id: uuid.UUID,
        session_id: uuid.UUID,
        command_id: uuid.UUID,
        success: bool,
        response_time_ms: int
    ) -> bool:
        """Add a processed command to the session."""
        pass
    
    @abstractmethod
    async def update_session_transcript(
        self,
        business_id: uuid.UUID,
        session_id: uuid.UUID,
        new_content: str
    ) -> bool:
        """Update session conversation transcript."""
        pass
    
    # Mobile and real-time operations
    @abstractmethod
    async def get_sessions_for_mobile(
        self,
        business_id: uuid.UUID,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get mobile-optimized session data."""
        pass
    
    @abstractmethod
    async def get_session_status_updates(
        self,
        business_id: uuid.UUID,
        session_ids: List[uuid.UUID]
    ) -> Dict[uuid.UUID, Dict[str, Any]]:
        """Get real-time status updates for sessions."""
        pass
    
    # Emergency and high-priority operations
    @abstractmethod
    async def get_emergency_sessions(
        self,
        business_id: uuid.UUID,
        active_only: bool = True
    ) -> List[VoiceSession]:
        """Get sessions in emergency mode."""
        pass
    
    @abstractmethod
    async def escalate_session_to_emergency(
        self,
        business_id: uuid.UUID,
        session_id: uuid.UUID
    ) -> bool:
        """Escalate session to emergency mode."""
        pass
    
    # Bulk operations
    @abstractmethod
    async def bulk_end_sessions(
        self,
        business_id: uuid.UUID,
        session_ids: List[uuid.UUID],
        reason: str
    ) -> int:
        """Bulk end multiple sessions."""
        pass
    
    @abstractmethod
    async def cleanup_old_sessions(
        self,
        business_id: uuid.UUID,
        older_than_days: int = 30
    ) -> int:
        """Clean up old completed sessions."""
        pass
    
    # Advanced search and filtering
    @abstractmethod
    async def advanced_search(
        self,
        business_id: uuid.UUID,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Advanced session search with multiple filters."""
        pass
    
    @abstractmethod
    async def get_filter_options(
        self,
        business_id: uuid.UUID
    ) -> Dict[str, List[Any]]:
        """Get available filter options for session search."""
        pass
    
    # Session statistics
    @abstractmethod
    async def count_sessions(
        self,
        business_id: uuid.UUID,
        status: Optional[VoiceSessionStatus] = None,
        agent_type: Optional[AgentType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count sessions with optional filters."""
        pass
    
    @abstractmethod
    async def get_concurrent_session_limit(self, business_id: uuid.UUID) -> int:
        """Get maximum concurrent sessions allowed for business."""
        pass
    
    @abstractmethod
    async def get_current_concurrent_sessions(self, business_id: uuid.UUID) -> int:
        """Get current number of concurrent active sessions."""
        pass 