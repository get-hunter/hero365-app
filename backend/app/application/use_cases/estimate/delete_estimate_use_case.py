"""
Delete Estimate Use Case

Handles deleting estimates with comprehensive business logic validation.
"""

import uuid
import logging

from app.domain.entities.estimate import Estimate
from app.domain.enums import EstimateStatus
from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.exceptions.domain_exceptions import (
    BusinessRuleViolationError, EntityNotFoundError
)
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class DeleteEstimateUseCase:
    """Use case for deleting estimates."""
    
    def __init__(self, estimate_repository: EstimateRepository):
        self.estimate_repository = estimate_repository
    
    async def execute(
        self, 
        estimate_id: uuid.UUID, 
        user_id: str, 
        business_id: uuid.UUID
    ) -> None:
        """Execute the delete estimate use case."""
        try:
            logger.info(f"Deleting estimate {estimate_id} for business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id, "delete")
            
            # Get and validate the estimate
            estimate = await self._validate_and_get_estimate(estimate_id, business_id)
            
            # Validate estimate can be deleted
            self._validate_estimate_for_deletion(estimate)
            
            # Delete the estimate
            await self.estimate_repository.delete(estimate_id)
            
            logger.info(f"Successfully deleted estimate {estimate_id}")
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation deleting estimate: {e}")
            raise AppValidationError(str(e))
        except EntityNotFoundError as e:
            logger.warning(f"Entity not found deleting estimate: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error deleting estimate: {e}")
            raise ApplicationError(f"Failed to delete estimate: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str, action: str) -> None:
        """Validate user has permission to delete estimates in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can delete estimates
        pass
    
    async def _validate_and_get_estimate(self, estimate_id: uuid.UUID, business_id: uuid.UUID) -> Estimate:
        """Validate and retrieve the estimate."""
        estimate = await self.estimate_repository.get_by_id(estimate_id)
        if not estimate:
            raise EntityNotFoundError(f"Estimate with ID {estimate_id} not found")
        
        if estimate.business_id != business_id:
            raise BusinessRuleViolationError("Estimate does not belong to the specified business")
        
        return estimate
    
    def _validate_estimate_for_deletion(self, estimate: Estimate) -> None:
        """Validate that the estimate can be deleted."""
        # Only allow deletion of draft estimates
        if estimate.status not in [EstimateStatus.DRAFT]:
            raise BusinessRuleViolationError(
                f"Only draft estimates can be deleted. Current status: {estimate.status.value}"
            )
        
        # Check if estimate has been converted to an invoice
        if estimate.status == EstimateStatus.CONVERTED:
            raise BusinessRuleViolationError(
                "Cannot delete estimate that has been converted to an invoice"
            )
        
        # Additional business rules can be added here
        # For example, check if user has permission to delete this specific estimate
        # or if there are any related records that prevent deletion 