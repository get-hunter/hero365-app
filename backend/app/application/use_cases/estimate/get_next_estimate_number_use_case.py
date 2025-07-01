"""
Get Next Estimate Number Use Case

Provides the next available estimate number for a business without creating an estimate.
"""

import uuid
import logging
from typing import Optional

from app.domain.repositories.estimate_repository import EstimateRepository
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class GetNextEstimateNumberUseCase:
    """Use case for getting the next available estimate number."""
    
    def __init__(self, estimate_repository: EstimateRepository):
        self.estimate_repository = estimate_repository
    
    async def execute(
        self, 
        business_id: uuid.UUID, 
        user_id: str,
        prefix: str = "EST",
        document_type: str = "estimate"
    ) -> str:
        """
        Execute the get next estimate number use case.
        
        Args:
            business_id: UUID of the business
            user_id: ID of the user requesting the number
            prefix: Prefix for the document number (default: "EST")
            document_type: Type of document - "estimate" or "quote" (default: "estimate")
            
        Returns:
            str: The next available document number
        """
        try:
            logger.info(f"Getting next estimate number for business {business_id} with prefix {prefix}")
            
            # Validate parameters
            if not business_id:
                raise AppValidationError("Business ID is required")
            
            if not user_id:
                raise AppValidationError("User ID is required")
            
            if document_type not in ["estimate", "quote"]:
                raise AppValidationError("Document type must be 'estimate' or 'quote'")
            
            # Set default prefix based on document type if not provided
            if not prefix:
                prefix = "QUO" if document_type == "quote" else "EST"
            
            # Get next number from repository
            next_number = await self.estimate_repository.get_next_estimate_number(
                business_id, prefix
            )
            
            logger.info(f"Next estimate number for business {business_id}: {next_number}")
            return next_number
            
        except AppValidationError:
            raise
        except Exception as e:
            logger.error(f"Error getting next estimate number: {str(e)}")
            raise ApplicationError(f"Failed to get next estimate number: {str(e)}") 