"""
Get Estimate Use Case

Handles retrieving estimate information with comprehensive business logic validation.
"""

import uuid
import logging
from typing import Optional

from app.domain.entities.estimate import Estimate
from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, BusinessRuleViolationError
)
from app.application.dto.estimate_dto import EstimateDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class GetEstimateUseCase:
    """Use case for retrieving estimates."""
    
    def __init__(self, estimate_repository: EstimateRepository):
        self.estimate_repository = estimate_repository
    
    async def execute(
        self, 
        estimate_id: uuid.UUID, 
        user_id: str, 
        business_id: uuid.UUID
    ) -> EstimateDTO:
        """Execute the get estimate use case."""
        try:
            logger.info(f"Getting estimate {estimate_id} for business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id)
            
            # Get and validate the estimate
            estimate = await self._validate_and_get_estimate(estimate_id, business_id)
            
            logger.info(f"Successfully retrieved estimate {estimate_id}")
            
            return EstimateDTO.from_entity(estimate)
            
        except EntityNotFoundError as e:
            logger.warning(f"Entity not found getting estimate: {e}")
            raise AppValidationError(str(e))
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation getting estimate: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting estimate: {e}")
            raise ApplicationError(f"Failed to get estimate: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to view estimates in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can view estimates
        pass
    
    async def _validate_and_get_estimate(self, estimate_id: uuid.UUID, business_id: uuid.UUID) -> Estimate:
        """Validate and retrieve the estimate."""
        estimate = await self.estimate_repository.get_by_id(estimate_id)
        if not estimate:
            raise EntityNotFoundError(f"Estimate with ID {estimate_id} not found")
        
        if estimate.business_id != business_id:
            raise BusinessRuleViolationError("Estimate does not belong to the specified business")
        
        return estimate 