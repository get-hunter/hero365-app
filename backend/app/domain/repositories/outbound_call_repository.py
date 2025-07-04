"""
Outbound Call Repository Interface

Repository interface for outbound call management with comprehensive CRUD operations,
call scheduling, tracking, and campaign management capabilities.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime

from ..entities.outbound_call import OutboundCall
from ..enums import CallStatus, CallPurpose, CallOutcome


class OutboundCallRepository(ABC):
    """Repository interface for outbound call management operations."""
    
    # Basic CRUD operations
    @abstractmethod
    async def create(self, call: OutboundCall) -> OutboundCall:
        """Create a new outbound call."""
        pass
    
    @abstractmethod
    async def get_by_id(self, business_id: uuid.UUID, call_id: uuid.UUID) -> Optional[OutboundCall]:
        """Get outbound call by ID."""
        pass
    
    @abstractmethod
    async def get_by_session_id(self, business_id: uuid.UUID, session_id: uuid.UUID) -> Optional[OutboundCall]:
        """Get outbound call by voice session ID."""
        pass
    
    @abstractmethod
    async def update(self, call: OutboundCall) -> OutboundCall:
        """Update an existing outbound call."""
        pass
    
    @abstractmethod
    async def delete(self, business_id: uuid.UUID, call_id: uuid.UUID) -> bool:
        """Delete an outbound call."""
        pass
    
    # Call scheduling and queue management
    @abstractmethod
    async def get_due_calls(
        self,
        business_id: uuid.UUID,
        priority_threshold: int = 1
    ) -> List[OutboundCall]:
        """Get calls that are due to be made."""
        pass
    
    @abstractmethod
    async def get_scheduled_calls(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[OutboundCall]:
        """Get scheduled calls within date range."""
        pass
    
    @abstractmethod
    async def get_retry_calls(self, business_id: uuid.UUID) -> List[OutboundCall]:
        """Get calls that need to be retried."""
        pass
    
    @abstractmethod
    async def get_active_calls(
        self,
        business_id: uuid.UUID,
        include_queued: bool = True
    ) -> List[OutboundCall]:
        """Get currently active calls."""
        pass
    
    @abstractmethod
    async def get_next_call_in_queue(
        self,
        business_id: uuid.UUID,
        campaign_id: Optional[uuid.UUID] = None
    ) -> Optional[OutboundCall]:
        """Get next call to be made from queue."""
        pass
    
    # List and search operations
    @abstractmethod
    async def list_by_business(
        self,
        business_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
        status: Optional[CallStatus] = None,
        purpose: Optional[CallPurpose] = None,
        campaign_id: Optional[uuid.UUID] = None
    ) -> List[OutboundCall]:
        """List outbound calls for a business with optional filtering."""
        pass
    
    @abstractmethod
    async def list_by_campaign(
        self,
        business_id: uuid.UUID,
        campaign_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
        status: Optional[CallStatus] = None
    ) -> List[OutboundCall]:
        """List calls for a specific campaign."""
        pass
    
    @abstractmethod
    async def search_calls(
        self,
        business_id: uuid.UUID,
        query: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[OutboundCall]:
        """Search calls by recipient name, phone, or notes."""
        pass
    
    # Campaign management operations
    @abstractmethod
    async def get_campaign_calls(
        self,
        business_id: uuid.UUID,
        campaign_id: uuid.UUID,
        status: Optional[CallStatus] = None,
        outcome: Optional[CallOutcome] = None
    ) -> List[OutboundCall]:
        """Get all calls for a campaign."""
        pass
    
    @abstractmethod
    async def get_campaign_analytics(
        self,
        business_id: uuid.UUID,
        campaign_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get analytics for a specific campaign."""
        pass
    
    @abstractmethod
    async def pause_campaign_calls(
        self,
        business_id: uuid.UUID,
        campaign_id: uuid.UUID
    ) -> int:
        """Pause all scheduled calls for a campaign."""
        pass
    
    @abstractmethod
    async def resume_campaign_calls(
        self,
        business_id: uuid.UUID,
        campaign_id: uuid.UUID
    ) -> int:
        """Resume all paused calls for a campaign."""
        pass
    
    # Contact and recipient management
    @abstractmethod
    async def get_calls_by_contact(
        self,
        business_id: uuid.UUID,
        contact_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[OutboundCall]:
        """Get all calls for a specific contact."""
        pass
    
    @abstractmethod
    async def get_calls_by_phone_number(
        self,
        business_id: uuid.UUID,
        phone_number: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[OutboundCall]:
        """Get all calls for a specific phone number."""
        pass
    
    @abstractmethod
    async def check_do_not_call_list(
        self,
        business_id: uuid.UUID,
        phone_number: str
    ) -> bool:
        """Check if phone number is on do-not-call list."""
        pass
    
    @abstractmethod
    async def add_to_do_not_call_list(
        self,
        business_id: uuid.UUID,
        phone_number: str,
        reason: str
    ) -> bool:
        """Add phone number to do-not-call list."""
        pass
    
    # Analytics and reporting operations
    @abstractmethod
    async def get_call_analytics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        purpose: Optional[CallPurpose] = None,
        campaign_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get comprehensive call analytics."""
        pass
    
    @abstractmethod
    async def get_success_rate_by_purpose(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Decimal]:
        """Get success rates by call purpose."""
        pass
    
    @abstractmethod
    async def get_daily_call_volumes(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Get daily call volumes."""
        pass
    
    @abstractmethod
    async def get_agent_performance_metrics(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get outbound caller agent performance metrics."""
        pass
    
    @abstractmethod
    async def get_conversion_funnel_data(
        self,
        business_id: uuid.UUID,
        campaign_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get conversion funnel analytics."""
        pass
    
    # Follow-up management
    @abstractmethod
    async def get_follow_up_calls(
        self,
        business_id: uuid.UUID,
        due_before: Optional[datetime] = None
    ) -> List[OutboundCall]:
        """Get calls that require follow-up."""
        pass
    
    @abstractmethod
    async def schedule_follow_up(
        self,
        business_id: uuid.UUID,
        original_call_id: uuid.UUID,
        follow_up_date: datetime,
        purpose: CallPurpose,
        notes: Optional[str] = None
    ) -> OutboundCall:
        """Schedule a follow-up call."""
        pass
    
    @abstractmethod
    async def mark_follow_up_completed(
        self,
        business_id: uuid.UUID,
        call_id: uuid.UUID,
        follow_up_call_id: uuid.UUID
    ) -> bool:
        """Mark follow-up as completed."""
        pass
    
    # Call outcome and result tracking
    @abstractmethod
    async def update_call_outcome(
        self,
        business_id: uuid.UUID,
        call_id: uuid.UUID,
        outcome: CallOutcome,
        notes: Optional[str] = None
    ) -> bool:
        """Update call outcome."""
        pass
    
    @abstractmethod
    async def get_calls_by_outcome(
        self,
        business_id: uuid.UUID,
        outcome: CallOutcome,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[OutboundCall]:
        """Get calls by specific outcome."""
        pass
    
    # Bulk operations
    @abstractmethod
    async def bulk_schedule_calls(
        self,
        business_id: uuid.UUID,
        calls: List[Dict[str, Any]]
    ) -> List[OutboundCall]:
        """Bulk schedule multiple calls."""
        pass
    
    @abstractmethod
    async def bulk_update_status(
        self,
        business_id: uuid.UUID,
        call_ids: List[uuid.UUID],
        status: CallStatus
    ) -> int:
        """Bulk update call status."""
        pass
    
    @abstractmethod
    async def bulk_cancel_calls(
        self,
        business_id: uuid.UUID,
        call_ids: List[uuid.UUID],
        reason: str
    ) -> int:
        """Bulk cancel calls."""
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
        """Advanced call search with multiple filters."""
        pass
    
    @abstractmethod
    async def get_filter_options(
        self,
        business_id: uuid.UUID
    ) -> Dict[str, List[Any]]:
        """Get available filter options for call search."""
        pass
    
    # Call statistics
    @abstractmethod
    async def count_calls(
        self,
        business_id: uuid.UUID,
        status: Optional[CallStatus] = None,
        purpose: Optional[CallPurpose] = None,
        campaign_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count calls with optional filters."""
        pass
    
    @abstractmethod
    async def get_call_queue_size(self, business_id: uuid.UUID) -> int:
        """Get current size of call queue."""
        pass
    
    @abstractmethod
    async def get_average_call_duration(
        self,
        business_id: uuid.UUID,
        purpose: Optional[CallPurpose] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[Decimal]:
        """Get average call duration."""
        pass 