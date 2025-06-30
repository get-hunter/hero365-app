"""
Process Payment Use Case

Handles the processing of payments for invoices with proper business logic validation.
"""

import uuid
import logging
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.domain.entities.invoice import Invoice, Payment
from app.domain.enums import InvoiceStatus, PaymentStatus, PaymentMethod
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.domain.exceptions.domain_exceptions import (
    DomainValidationError, BusinessRuleViolationError, EntityNotFoundError
)
from app.application.dto.invoice_dto import ProcessPaymentDTO, InvoiceDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class ProcessPaymentUseCase:
    """Use case for processing payments on invoices."""
    
    def __init__(self, invoice_repository: InvoiceRepository):
        self.invoice_repository = invoice_repository
    
    async def execute(
        self, 
        invoice_id: uuid.UUID, 
        request: ProcessPaymentDTO, 
        user_id: str, 
        business_id: uuid.UUID
    ) -> InvoiceDTO:
        """Execute the process payment use case."""
        try:
            logger.info(f"Processing payment for invoice {invoice_id} in business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id)
            
            # Get and validate the invoice
            invoice = await self._validate_and_get_invoice(invoice_id, business_id)
            
            # Validate payment can be processed
            self._validate_payment_processing(invoice, request)
            
            # Create the payment
            payment = Payment(
                id=uuid.uuid4(),
                amount=Decimal(str(request.amount)),
                payment_date=request.payment_date or datetime.utcnow(),
                payment_method=PaymentMethod(request.payment_method),
                status=PaymentStatus.COMPLETED,  # Assuming successful processing
                reference=request.reference,
                transaction_id=request.transaction_id,
                notes=request.notes,
                processed_by=user_id,
                refunded_amount=Decimal('0')
            )
            
            # Add payment to invoice
            invoice.payments.append(payment)
            
            # Update invoice status based on payment
            self._update_invoice_status(invoice)
            
            # Update timestamps
            invoice.last_modified = datetime.utcnow()
            if invoice.status == InvoiceStatus.PAID and not invoice.paid_date:
                invoice.paid_date = datetime.utcnow()
            
            # Validate business rules after payment
            self._validate_business_rules_after_payment(invoice)
            
            # Save the updated invoice
            updated_invoice = await self.invoice_repository.update(invoice)
            
            logger.info(f"Successfully processed payment of {payment.amount} for invoice {invoice_id}")
            
            return InvoiceDTO.from_entity(updated_invoice)
            
        except DomainValidationError as e:
            logger.warning(f"Validation error processing payment: {e}")
            raise AppValidationError(str(e))
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation processing payment: {e}")
            raise AppValidationError(str(e))
        except EntityNotFoundError as e:
            logger.warning(f"Entity not found processing payment: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error processing payment: {e}")
            raise ApplicationError(f"Failed to process payment: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to process payments in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can process payments
        pass
    
    async def _validate_and_get_invoice(self, invoice_id: uuid.UUID, business_id: uuid.UUID) -> Invoice:
        """Validate and retrieve the invoice."""
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            raise EntityNotFoundError(f"Invoice with ID {invoice_id} not found")
        
        if invoice.business_id != business_id:
            raise BusinessRuleViolationError("Invoice does not belong to the specified business")
        
        return invoice
    
    def _validate_payment_processing(self, invoice: Invoice, request: ProcessPaymentDTO) -> None:
        """Validate that payment can be processed for this invoice."""
        # Check invoice status
        if invoice.status in [InvoiceStatus.CANCELLED, InvoiceStatus.VOID]:
            raise BusinessRuleViolationError(
                f"Cannot process payment for invoice with status '{invoice.status.value}'"
            )
        
        # Check if invoice is already fully paid
        if invoice.status == InvoiceStatus.PAID:
            raise BusinessRuleViolationError("Invoice is already fully paid")
        
        # Validate payment amount
        payment_amount = Decimal(str(request.amount))
        if payment_amount <= 0:
            raise ValidationError("Payment amount must be greater than zero")
        
        # Check if payment would exceed invoice total
        current_balance = invoice.get_balance_due()
        if payment_amount > current_balance:
            raise BusinessRuleViolationError(
                f"Payment amount ${payment_amount} exceeds remaining balance ${current_balance}"
            )
        
        # Validate payment method
        if not request.payment_method:
            raise ValidationError("Payment method is required")
        
        # Validate payment date
        if request.payment_date and request.payment_date > datetime.utcnow():
            raise ValidationError("Payment date cannot be in the future")
    
    def _update_invoice_status(self, invoice: Invoice) -> None:
        """Update invoice status based on payment status."""
        balance_due = invoice.get_balance_due()
        
        if balance_due <= 0:
            # Invoice is fully paid
            invoice.status = InvoiceStatus.PAID
        elif invoice.get_total_payments() > 0:
            # Invoice is partially paid
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        
        # Check if invoice is overdue
        if invoice.status != InvoiceStatus.PAID and invoice.is_overdue():
            if invoice.status == InvoiceStatus.PARTIALLY_PAID:
                # Keep partially paid status even if overdue
                pass
            else:
                invoice.status = InvoiceStatus.OVERDUE
    
    def _validate_business_rules_after_payment(self, invoice: Invoice) -> None:
        """Validate business rules after payment processing."""
        # Ensure total payments don't exceed invoice total
        if invoice.get_total_payments() > invoice.get_total_amount():
            raise BusinessRuleViolationError("Total payments cannot exceed invoice total amount")
        
        # Validate payment calculations
        balance_due = invoice.get_balance_due()
        if balance_due < 0:
            raise BusinessRuleViolationError("Invoice balance cannot be negative")
        
        # Additional domain-specific validations
        try:
            invoice.validate()
        except Exception as e:
            raise BusinessRuleViolationError(f"Invoice validation failed after payment: {str(e)}") 