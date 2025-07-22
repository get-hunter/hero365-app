"""
Estimate Service

Unified facade for estimate operations that orchestrates use cases.
Provides high-level interface for both API controllers and voice agents.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal

from app.domain.entities.estimate import Estimate
from app.domain.entities.estimate_enums.enums import EstimateStatus
from app.domain.shared.enums import CurrencyCode
from app.domain.repositories.estimate_repository import EstimateRepository, CommonEstimateQueries
from app.application.dto.estimate_dto import (
    EstimateDTO, EstimateCreateDTO, EstimateUpdateDTO, EstimateFilters
)
from app.application.use_cases.estimate.create_estimate_use_case import CreateEstimateUseCase
from app.application.use_cases.estimate.get_estimate_use_case import GetEstimateUseCase
from app.application.use_cases.estimate.list_estimates_use_case import ListEstimatesUseCase
from app.application.use_cases.estimate.change_estimate_status_use_case import ChangeEstimateStatusUseCase
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError, NotFoundError
)

logger = logging.getLogger(__name__)


class EstimateService:
    """
    Unified service for estimate operations.
    
    Provides high-level facade over use cases with convenience methods
    for common operations. Used by both API controllers and voice agents.
    """
    
    def __init__(
        self,
        estimate_repository: EstimateRepository,
        create_use_case: Optional[CreateEstimateUseCase] = None,
        get_use_case: Optional[GetEstimateUseCase] = None,
        list_use_case: Optional[ListEstimatesUseCase] = None,
        status_use_case: Optional[ChangeEstimateStatusUseCase] = None
    ):
        self.estimate_repository = estimate_repository
        
        # Initialize use cases with dependency injection or create defaults
        self.create_use_case = create_use_case or CreateEstimateUseCase(estimate_repository)
        self.get_use_case = get_use_case or GetEstimateUseCase(estimate_repository)
        self.list_use_case = list_use_case or ListEstimatesUseCase(estimate_repository)
        self.status_use_case = status_use_case or ChangeEstimateStatusUseCase(estimate_repository)
    
    # High-level CRUD operations
    async def create_estimate(
        self,
        create_data: Union[EstimateCreateDTO, Dict[str, Any]],
        user_id: str
    ) -> EstimateDTO:
        """Create a new estimate."""
        try:
            if isinstance(create_data, dict):
                create_dto = EstimateCreateDTO(**create_data)
            else:
                create_dto = create_data
                
            return await self.create_use_case.execute(create_dto, user_id)
            
        except Exception as e:
            logger.error(f"Service error creating estimate: {e}")
            raise
    
    async def get_estimate(
        self,
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        include_sensitive_data: bool = False
    ) -> EstimateDTO:
        """Get estimate by ID."""
        try:
            return await self.get_use_case.execute(
                estimate_id, business_id, user_id, include_sensitive_data
            )
            
        except Exception as e:
            logger.error(f"Service error getting estimate: {e}")
            raise
    
    async def get_estimate_by_number(
        self,
        estimate_number: str,
        business_id: uuid.UUID,
        user_id: str,
        include_sensitive_data: bool = False
    ) -> EstimateDTO:
        """Get estimate by estimate number."""
        try:
            return await self.get_use_case.execute_by_number(
                estimate_number, business_id, user_id, include_sensitive_data
            )
            
        except Exception as e:
            logger.error(f"Service error getting estimate by number: {e}")
            raise
    
    async def list_estimates(
        self,
        business_id: uuid.UUID,
        user_id: str,
        filters: Optional[Union[EstimateFilters, Dict[str, Any]]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List estimates with filtering and pagination."""
        try:
            if isinstance(filters, dict):
                filters = EstimateFilters(**filters) if filters else None
                
            return await self.list_use_case.execute(
                business_id, user_id, filters, skip, limit
            )
            
        except Exception as e:
            logger.error(f"Service error listing estimates: {e}")
            raise
    
    # Convenience methods for common patterns
    async def get_recent_estimates(
        self,
        business_id: uuid.UUID,
        user_id: str,
        days: int = 30,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get recent estimates."""
        try:
            return await self.list_use_case.execute_with_common_filters(
                business_id, user_id, "recent", 0, limit, days=days
            )
            
        except Exception as e:
            logger.error(f"Service error getting recent estimates: {e}")
            raise
    
    async def get_pending_estimates(
        self,
        business_id: uuid.UUID,
        user_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get estimates pending approval."""
        try:
            return await self.list_use_case.execute_with_common_filters(
                business_id, user_id, "pending", 0, limit
            )
            
        except Exception as e:
            logger.error(f"Service error getting pending estimates: {e}")
            raise
    
    async def get_draft_estimates(
        self,
        business_id: uuid.UUID,
        user_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get draft estimates."""
        try:
            return await self.list_use_case.execute_with_common_filters(
                business_id, user_id, "draft", 0, limit
            )
            
        except Exception as e:
            logger.error(f"Service error getting draft estimates: {e}")
            raise
    
    async def get_expiring_estimates(
        self,
        business_id: uuid.UUID,
        user_id: str,
        days: int = 7,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get estimates expiring soon."""
        try:
            return await self.list_use_case.execute_with_common_filters(
                business_id, user_id, "expiring_soon", 0, limit, days=days
            )
            
        except Exception as e:
            logger.error(f"Service error getting expiring estimates: {e}")
            raise
    
    async def search_estimates(
        self,
        business_id: uuid.UUID,
        user_id: str,
        search_term: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search estimates."""
        try:
            filters = EstimateFilters(search_term=search_term)
            return await self.list_estimates(
                business_id, user_id, filters, 0, limit
            )
            
        except Exception as e:
            logger.error(f"Service error searching estimates: {e}")
            raise
    
    # Status management operations
    async def send_estimate(
        self,
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        client_email: Optional[str] = None
    ) -> EstimateDTO:
        """Send estimate to client."""
        try:
            return await self.status_use_case.send_estimate(
                estimate_id, business_id, user_id, client_email
            )
            
        except Exception as e:
            logger.error(f"Service error sending estimate: {e}")
            raise
    
    async def approve_estimate(
        self,
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        approval_notes: Optional[str] = None
    ) -> EstimateDTO:
        """Approve estimate."""
        try:
            return await self.status_use_case.approve_estimate(
                estimate_id, business_id, user_id, approval_notes
            )
            
        except Exception as e:
            logger.error(f"Service error approving estimate: {e}")
            raise
    
    async def reject_estimate(
        self,
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        rejection_reason: Optional[str] = None
    ) -> EstimateDTO:
        """Reject estimate."""
        try:
            return await self.status_use_case.reject_estimate(
                estimate_id, business_id, user_id, rejection_reason
            )
            
        except Exception as e:
            logger.error(f"Service error rejecting estimate: {e}")
            raise
    
    async def cancel_estimate(
        self,
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        cancellation_reason: Optional[str] = None
    ) -> EstimateDTO:
        """Cancel estimate."""
        try:
            return await self.status_use_case.cancel_estimate(
                estimate_id, business_id, user_id, cancellation_reason
            )
            
        except Exception as e:
            logger.error(f"Service error cancelling estimate: {e}")
            raise
    
    async def change_estimate_status(
        self,
        estimate_id: uuid.UUID,
        new_status: Union[EstimateStatus, str],
        business_id: uuid.UUID,
        user_id: str,
        reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> EstimateDTO:
        """Change estimate status."""
        try:
            if isinstance(new_status, str):
                parsed_status = EstimateStatus.parse_from_string(new_status)
                if not parsed_status:
                    raise ValidationError(f"Invalid status '{new_status}'. Valid options are: draft, sent, viewed, approved, rejected, cancelled, converted, expired")
                new_status = parsed_status
                
            return await self.status_use_case.execute(
                estimate_id, new_status, business_id, user_id, reason, notes
            )
            
        except Exception as e:
            logger.error(f"Service error changing estimate status: {e}")
            raise
    
    # Voice agent convenience methods
    async def create_quick_estimate(
        self,
        business_id: uuid.UUID,
        user_id: str,
        title: str,
        client_name: Optional[str] = None,
        client_email: Optional[str] = None,
        total_amount: Optional[float] = None,
        description: Optional[str] = None
    ) -> EstimateDTO:
        """Create a quick estimate with minimal data - optimized for voice input."""
        try:
            return await self.create_use_case.execute_quick_estimate(
                business_id, user_id, title, client_name, client_email,
                total_amount, description
            )
            
        except Exception as e:
            logger.error(f"Service error creating quick estimate: {e}")
            raise
    
    async def create_estimate_from_template(
        self,
        template_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        overrides: Optional[Dict[str, Any]] = None
    ) -> EstimateDTO:
        """Create estimate from template."""
        try:
            return await self.create_use_case.execute_from_template(
                template_id, business_id, user_id, overrides
            )
            
        except Exception as e:
            logger.error(f"Service error creating estimate from template: {e}")
            raise
    
    async def get_estimate_suggestions(
        self,
        business_id: uuid.UUID,
        user_id: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get suggested estimates (drafts needing attention)."""
        try:
            return await self.get_draft_estimates(business_id, user_id, limit)
            
        except Exception as e:
            logger.error(f"Service error getting estimate suggestions: {e}")
            raise
    
    # Analytics and reporting methods
    async def get_estimate_stats(
        self,
        business_id: uuid.UUID,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get estimate statistics for a period."""
        try:
            logger.info(f"Getting estimate stats for business {business_id}")
            
            # Get counts for different statuses
            stats = {}
            
            # Recent estimates
            recent = await self.get_recent_estimates(business_id, user_id, period_days, 1000)
            stats["total_recent"] = recent["total_count"]
            
            # Pending estimates
            pending = await self.get_pending_estimates(business_id, user_id, 1000)
            stats["total_pending"] = pending["total_count"]
            
            # Draft estimates
            drafts = await self.get_draft_estimates(business_id, user_id, 1000)
            stats["total_drafts"] = drafts["total_count"]
            
            # Expiring estimates
            expiring = await self.get_expiring_estimates(business_id, user_id, 7, 1000)
            stats["total_expiring"] = expiring["total_count"]
            
            # Calculate totals and percentages
            if recent["estimates"]:
                total_value = sum(
                    float(est.total_amount) for est in recent["estimates"] 
                    if est.total_amount
                )
                stats["total_value"] = total_value
                stats["average_value"] = total_value / len(recent["estimates"]) if recent["estimates"] else 0
            else:
                stats["total_value"] = 0
                stats["average_value"] = 0
            
            stats["period_days"] = period_days
            
            logger.info(f"Generated estimate stats: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Service error getting estimate stats: {e}")
            raise
    
    async def get_estimate_count(
        self,
        business_id: uuid.UUID,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Get count of estimates matching filters."""
        try:
            return await self.estimate_repository.count_with_filters(business_id, filters)
            
        except Exception as e:
            logger.error(f"Service error getting estimate count: {e}")
            raise
    
    # Utility methods
    async def estimate_exists(
        self,
        estimate_id: uuid.UUID,
        business_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if estimate exists."""
        try:
            if not await self.estimate_repository.exists(estimate_id):
                return False
            
            if business_id:
                # Additional check for business ownership
                try:
                    estimate = await self.estimate_repository.get_by_id(estimate_id)
                    return estimate and estimate.business_id == business_id
                except:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Service error checking estimate existence: {e}")
            return False
    

    
    def format_estimate_for_display(self, estimate: EstimateDTO) -> str:
        """Format estimate for natural language display (helper for voice agent)."""
        try:
            display_parts = [
                f"Estimate {estimate.estimate_number}",
                f"titled '{estimate.title}'",
                f"for {estimate.client_display_name}",
                f"worth ${float(estimate.total_amount):,.2f}",
                f"with status {estimate.status_display.lower()}"
            ]
            
            return " ".join(display_parts)
            
        except Exception as e:
            logger.warning(f"Error formatting estimate for display: {e}")
            return f"Estimate {estimate.estimate_number if hasattr(estimate, 'estimate_number') else 'Unknown'}"
    
    def get_available_status_transitions(self, current_status: EstimateStatus) -> List[EstimateStatus]:
        """Get available status transitions for current status."""
        try:
            transitions = {
                EstimateStatus.DRAFT: [EstimateStatus.SENT, EstimateStatus.CANCELLED],
                EstimateStatus.SENT: [EstimateStatus.VIEWED, EstimateStatus.APPROVED, EstimateStatus.REJECTED, EstimateStatus.CANCELLED],
                EstimateStatus.VIEWED: [EstimateStatus.APPROVED, EstimateStatus.REJECTED, EstimateStatus.CANCELLED],
                EstimateStatus.APPROVED: [EstimateStatus.CONVERTED, EstimateStatus.CANCELLED],
                EstimateStatus.REJECTED: [],
                EstimateStatus.CANCELLED: [],
                EstimateStatus.CONVERTED: [],
                EstimateStatus.EXPIRED: [EstimateStatus.SENT, EstimateStatus.CANCELLED]
            }
            
            return transitions.get(current_status, [])
            
        except Exception as e:
            logger.warning(f"Error getting status transitions: {e}")
            return [] 