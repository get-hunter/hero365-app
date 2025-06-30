"""
Get Invoice Use Case

Handles retrieving invoice information with comprehensive business logic validation.
"""

import uuid
import logging
from typing import Optional

from app.domain.entities.invoice import Invoice
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, BusinessRuleViolationError
)
from app.application.dto.invoice_dto import InvoiceDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class GetInvoiceUseCase:
    """Use case for retrieving invoices."""
    
    def __init__(self, invoice_repository: InvoiceRepository):
        self.invoice_repository = invoice_repository
    
    async def execute(
        self, 
        invoice_id: uuid.UUID, 
        user_id: str, 
        business_id: uuid.UUID
    ) -> InvoiceDTO:
        """Execute the get invoice use case."""
        try:
            logger.info(f"Getting invoice {invoice_id} for business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id)
            
            # Get and validate the invoice
            invoice = await self._validate_and_get_invoice(invoice_id, business_id)
            
            logger.info(f"Successfully retrieved invoice {invoice_id}")
            
            return InvoiceDTO.from_entity(invoice)
            
        except EntityNotFoundError as e:
            logger.warning(f"Entity not found getting invoice: {e}")
            raise AppValidationError(str(e))
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation getting invoice: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting invoice: {e}")
            raise ApplicationError(f"Failed to get invoice: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to view invoices in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can view invoices
        pass
    
    async def _validate_and_get_invoice(self, invoice_id: uuid.UUID, business_id: uuid.UUID) -> Invoice:
        """Validate and retrieve the invoice."""
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            raise EntityNotFoundError(f"Invoice with ID {invoice_id} not found")
        
        if invoice.business_id != business_id:
            raise BusinessRuleViolationError("Invoice does not belong to the specified business")
        
        return invoice 