"""
Get Estimate Use Case

Handles retrieving estimates with business validation and permissions.
"""

import uuid
import logging
from typing import Optional

from app.domain.entities.estimate import Estimate
from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.exceptions.domain_exceptions import BusinessRuleViolationError
from app.application.dto.estimate_dto import EstimateDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError, NotFoundError
)

logger = logging.getLogger(__name__)


class GetEstimateUseCase:
    """Use case for retrieving estimates with business validation."""
    
    def __init__(self, estimate_repository: EstimateRepository):
        self.estimate_repository = estimate_repository
    
    async def execute(
        self, 
        estimate_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        include_sensitive_data: bool = False
    ) -> EstimateDTO:
        """
        Execute the get estimate use case.
        
        Args:
            estimate_id: ID of the estimate to retrieve
            business_id: Business ID for permission validation
            user_id: ID of the user requesting the estimate
            include_sensitive_data: Whether to include sensitive data like internal notes
            
        Returns:
            EstimateDTO of the requested estimate
            
        Raises:
            NotFoundError: If estimate doesn't exist
            ValidationError: If permissions are invalid
            ApplicationError: If retrieval fails
        """
        try:
            logger.info(f"Getting estimate {estimate_id} for user {user_id}")
            
            # Retrieve the estimate
            estimate = await self.estimate_repository.get_by_id(estimate_id)
            if not estimate:
                raise NotFoundError(f"Estimate with ID {estimate_id} not found")
            
            # Validate permissions
            await self._validate_permissions(estimate, business_id, user_id)
            
            # Convert to DTO
            estimate_dto = EstimateDTO.from_entity(estimate)
            
            # Remove sensitive data if not authorized
            if not include_sensitive_data:
                estimate_dto = self._sanitize_sensitive_data(estimate_dto)
            
            # Track view if this is a client viewing their estimate
            if await self._should_track_view(estimate, user_id):
                await self._track_estimate_view(estimate, user_id)
            
            logger.info(f"Successfully retrieved estimate {estimate.estimate_number}")
            
            return estimate_dto
            
        except NotFoundError:
            raise
        except BusinessRuleViolationError as e:
            logger.warning(f"Permission error retrieving estimate: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error retrieving estimate: {e}")
            raise ApplicationError(f"Failed to retrieve estimate: {str(e)}")
    
    async def execute_by_number(
        self,
        estimate_number: str,
        business_id: uuid.UUID,
        user_id: str,
        include_sensitive_data: bool = False
    ) -> EstimateDTO:
        """
        Get estimate by estimate number within a business.
        
        Args:
            estimate_number: Estimate number to find
            business_id: Business ID
            user_id: User requesting the estimate
            include_sensitive_data: Whether to include sensitive data
            
        Returns:
            EstimateDTO of the requested estimate
        """
        try:
            logger.info(f"Getting estimate by number {estimate_number} for business {business_id}")
            
            # Search for estimate by number using filters
            estimates, total = await self.estimate_repository.list_with_filters(
                business_id=business_id,
                filters={"estimate_number_contains": estimate_number},
                limit=1
            )
            
            if not estimates:
                raise NotFoundError(f"Estimate with number {estimate_number} not found")
            
            # Get the exact match
            estimate = None
            for est in estimates:
                if est.estimate_number == estimate_number:
                    estimate = est
                    break
            
            if not estimate:
                raise NotFoundError(f"Estimate with number {estimate_number} not found")
            
            return await self.execute(
                estimate.id, 
                business_id, 
                user_id, 
                include_sensitive_data
            )
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving estimate by number: {e}")
            raise ApplicationError(f"Failed to retrieve estimate by number: {str(e)}")
    
    async def execute_for_client_view(
        self,
        estimate_id: uuid.UUID,
        access_token: Optional[str] = None
    ) -> EstimateDTO:
        """
        Get estimate for client viewing (public access with token).
        
        Args:
            estimate_id: ID of the estimate
            access_token: Optional access token for private estimates
            
        Returns:
            EstimateDTO with client-appropriate data
        """
        try:
            logger.info(f"Getting estimate {estimate_id} for client view")
            
            # Retrieve the estimate
            estimate = await self.estimate_repository.get_by_id(estimate_id)
            if not estimate:
                raise NotFoundError(f"Estimate with ID {estimate_id} not found")
            
            # Validate client access
            await self._validate_client_access(estimate, access_token)
            
            # Convert to DTO and sanitize for client
            estimate_dto = EstimateDTO.from_entity(estimate)
            estimate_dto = self._sanitize_for_client_view(estimate_dto)
            
            # Mark as viewed by client
            await self._mark_estimate_viewed(estimate)
            
            logger.info(f"Successfully provided client view for estimate {estimate.estimate_number}")
            
            return estimate_dto
            
        except NotFoundError:
            raise
        except BusinessRuleViolationError as e:
            logger.warning(f"Client access error: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Error providing client view: {e}")
            raise ApplicationError(f"Failed to provide client view: {str(e)}")
    
    async def _validate_permissions(
        self, 
        estimate: Estimate, 
        business_id: uuid.UUID, 
        user_id: str
    ) -> None:
        """Validate user has permission to view this estimate."""
        if estimate.business_id != business_id:
            raise BusinessRuleViolationError(
                f"Estimate does not belong to business {business_id}"
            )
        
        # TODO: Implement more granular permission checking
        # For now, assume users can view estimates in their business
        logger.debug(f"Permission check passed for estimate {estimate.id}")
    
    async def _validate_client_access(
        self, 
        estimate: Estimate, 
        access_token: Optional[str]
    ) -> None:
        """Validate client access to estimate."""
        # Check if estimate is in a viewable state
        from app.domain.enums import EstimateStatus
        
        viewable_statuses = [
            EstimateStatus.SENT,
            EstimateStatus.VIEWED,
            EstimateStatus.APPROVED,
            EstimateStatus.REJECTED
        ]
        
        if estimate.status not in viewable_statuses:
            raise BusinessRuleViolationError(
                "Estimate is not available for client viewing"
            )
        
        # TODO: Implement access token validation if needed
        # For now, allow access to sent estimates
        logger.debug(f"Client access validated for estimate {estimate.id}")
    
    def _sanitize_sensitive_data(self, estimate_dto: EstimateDTO) -> EstimateDTO:
        """Remove sensitive data from estimate DTO."""
        # Remove internal notes and other sensitive fields
        estimate_dto.internal_notes = None
        # Could remove other sensitive fields as needed
        return estimate_dto
    
    def _sanitize_for_client_view(self, estimate_dto: EstimateDTO) -> EstimateDTO:
        """Remove internal data for client viewing."""
        # Remove all internal fields
        estimate_dto.internal_notes = None
        estimate_dto.created_by = None
        # Remove business-specific identifiers
        estimate_dto.template_id = None
        
        return estimate_dto
    
    async def _should_track_view(self, estimate: Estimate, user_id: str) -> bool:
        """Determine if this view should be tracked."""
        # Track if it's not the creator viewing their own estimate
        return estimate.created_by != user_id
    
    async def _track_estimate_view(self, estimate: Estimate, user_id: str) -> None:
        """Track that the estimate was viewed."""
        try:
            # This would typically update view tracking
            logger.info(f"Tracking view of estimate {estimate.id} by user {user_id}")
            # TODO: Implement view tracking logic
        except Exception as e:
            # Don't fail the request if tracking fails
            logger.warning(f"Failed to track estimate view: {e}")
    
    async def _mark_estimate_viewed(self, estimate: Estimate) -> None:
        """Mark estimate as viewed by client."""
        try:
            from app.domain.enums import EstimateStatus
            
            if estimate.status == EstimateStatus.SENT:
                estimate.mark_as_viewed("client")
                await self.estimate_repository.update(estimate)
                logger.info(f"Marked estimate {estimate.estimate_number} as viewed")
        except Exception as e:
            # Don't fail the request if status update fails
            logger.warning(f"Failed to mark estimate as viewed: {e}") 