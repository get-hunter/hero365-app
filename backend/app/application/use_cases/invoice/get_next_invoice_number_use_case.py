"""
Get Next Invoice Number Use Case

Provides the next available invoice number for a business without creating an invoice.
"""

import uuid
import logging
from typing import Optional

from app.domain.repositories.invoice_repository import InvoiceRepository
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class GetNextInvoiceNumberUseCase:
    """Use case for getting the next available invoice number."""
    
    def __init__(self, invoice_repository: InvoiceRepository):
        self.invoice_repository = invoice_repository
    
    async def execute(
        self, 
        business_id: uuid.UUID, 
        user_id: str,
        prefix: str = "INV"
    ) -> str:
        """
        Execute the get next invoice number use case.
        
        Args:
            business_id: UUID of the business
            user_id: ID of the user requesting the number
            prefix: Prefix for the document number (default: "INV")
            
        Returns:
            str: The next available invoice number
        """
        try:
            logger.info(f"Getting next invoice number for business {business_id} with prefix {prefix}")
            
            # Validate parameters
            if not business_id:
                raise AppValidationError("Business ID is required")
            
            if not user_id:
                raise AppValidationError("User ID is required")
            
            if not prefix:
                prefix = "INV"
            
            # Get next number from repository
            next_number = await self.invoice_repository.get_next_invoice_number(
                business_id, prefix
            )
            
            logger.info(f"Next invoice number for business {business_id}: {next_number}")
            return next_number
            
        except AppValidationError:
            raise
        except Exception as e:
            logger.error(f"Error getting next invoice number: {str(e)}")
            raise ApplicationError(f"Failed to get next invoice number: {str(e)}") 