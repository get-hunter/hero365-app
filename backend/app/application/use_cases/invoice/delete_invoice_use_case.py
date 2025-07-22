"""
Delete Invoice Use Case

Handles the deletion of invoices with comprehensive business logic validation.
"""

import uuid
import logging
from typing import Dict, Any
from datetime import datetime

from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_enums.enums import InvoiceStatus
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.domain.exceptions.domain_exceptions import (
    BusinessRuleViolationError, EntityNotFoundError
)
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class DeleteInvoiceUseCase:
    """Use case for deleting invoices."""
    
    def __init__(self, invoice_repository: InvoiceRepository):
        self.invoice_repository = invoice_repository
    
    async def execute(self, invoice_id: uuid.UUID, business_id: uuid.UUID, user_id: str) -> Dict[str, Any]:
        """Execute the delete invoice use case."""
        try:
            logger.info(f"Deleting invoice {invoice_id} for business {business_id} by user {user_id}")
            
            # Validate and get existing invoice
            invoice = await self._validate_and_get_invoice(invoice_id, business_id)
            
            # Validate invoice can be deleted
            self._validate_invoice_for_deletion(invoice)
            
            # Perform additional business rule validations
            await self._validate_deletion_business_rules(invoice)
            
            # Delete the invoice
            success = await self.invoice_repository.delete(invoice_id)
            
            if not success:
                raise ApplicationError("Failed to delete invoice from repository")
            
            logger.info(f"Successfully deleted invoice {invoice_id}")
            
            return {
                "success": True,
                "message": f"Invoice {invoice_id} deleted successfully",
                "invoice_id": str(invoice_id),
                "deleted_by": user_id,
                "deleted_at": datetime.utcnow().isoformat()
            }
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation deleting invoice: {e}")
            raise AppValidationError(str(e))
        except EntityNotFoundError as e:
            logger.warning(f"Entity not found deleting invoice: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error deleting invoice: {e}")
            raise ApplicationError(f"Failed to delete invoice: {str(e)}")
    
    async def _validate_and_get_invoice(self, invoice_id: uuid.UUID, business_id: uuid.UUID) -> Invoice:
        """Validate and retrieve the invoice."""
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            raise EntityNotFoundError(f"Invoice with ID {invoice_id} not found")
        
        if invoice.business_id != business_id:
            raise BusinessRuleViolationError("Invoice does not belong to the specified business")
        
        return invoice
    
    def _validate_invoice_for_deletion(self, invoice: Invoice) -> None:
        """Validate that the invoice can be deleted."""
        # Primary business rule: Only draft invoices can be deleted
        if invoice.status != InvoiceStatus.DRAFT:
            raise BusinessRuleViolationError(
                f"Only draft invoices can be deleted. Current status: {invoice.status.value}"
            )
        
        # Check if invoice has any payments
        if invoice.payments and len(invoice.payments) > 0:
            raise BusinessRuleViolationError(
                "Cannot delete invoice that has payments. Please process refunds first."
            )
        
        # Check if invoice has been sent or viewed
        if invoice.sent_date:
            raise BusinessRuleViolationError(
                "Cannot delete invoice that has been sent to client"
            )
        
        if invoice.viewed_date:
            raise BusinessRuleViolationError(
                "Cannot delete invoice that has been viewed by client"
            )
        
        logger.debug(f"Invoice {invoice.id} validation passed for deletion")
    
    async def _validate_deletion_business_rules(self, invoice: Invoice) -> None:
        """Perform additional business rule validations for deletion."""
        # Check for any related records that might prevent deletion
        # This is where you could add checks for:
        # - Related project records
        # - Integration with external systems
        # - Audit trail requirements
        # - etc.
        
        # For now, we'll keep it simple and assume no additional restrictions
        logger.debug(f"Additional business rule validation passed for invoice {invoice.id}")
    
    def _log_deletion_audit(self, invoice: Invoice, user_id: str) -> None:
        """Log the deletion for audit purposes."""
        logger.info(
            f"AUDIT: Invoice deleted - "
            f"ID: {invoice.id}, "
            f"Number: {invoice.invoice_number}, "
            f"Business: {invoice.business_id}, "
            f"Client: {invoice.client_name}, "
            f"Amount: {invoice.get_total_amount()}, "
            f"Deleted by: {user_id}"
        ) 