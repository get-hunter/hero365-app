"""
Convert Estimate to Invoice Use Case

Handles the conversion of approved estimates into invoices with proper business logic.
"""

import uuid
import logging
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

from app.domain.entities.estimate import Estimate
from app.domain.entities.invoice import Invoice, InvoiceLineItem, Payment, PaymentTerms
from app.domain.enums import EstimateStatus, InvoiceStatus, PaymentMethod, PaymentStatus
from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.domain.exceptions.domain_exceptions import (
    DomainValidationError, BusinessRuleViolationError, EntityNotFoundError
)
from app.application.dto.estimate_dto import EstimateDTO
from app.application.dto.invoice_dto import InvoiceDTO, CreateInvoiceFromEstimateDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class ConvertEstimateToInvoiceUseCase:
    """Use case for converting estimates to invoices."""
    
    def __init__(
        self,
        estimate_repository: EstimateRepository,
        invoice_repository: InvoiceRepository
    ):
        self.estimate_repository = estimate_repository
        self.invoice_repository = invoice_repository
    
    async def execute(
        self, 
        estimate_id: uuid.UUID, 
        request: CreateInvoiceFromEstimateDTO,
        user_id: str, 
        business_id: uuid.UUID
    ) -> InvoiceDTO:
        """Execute the convert estimate to invoice use case."""
        try:
            logger.info(f"Converting estimate {estimate_id} to invoice for business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id)
            
            # Get and validate the estimate
            estimate = await self._validate_and_get_estimate(estimate_id, business_id)
            
            # Validate estimate can be converted
            self._validate_estimate_for_conversion(estimate)
            
            # Generate invoice number if not provided
            invoice_number = request.invoice_number
            if not invoice_number:
                invoice_number = await self.invoice_repository.get_next_invoice_number(
                    business_id, request.number_prefix or "INV"
                )
            
            # Check for duplicate invoice number
            if await self.invoice_repository.has_duplicate_invoice_number(
                business_id, invoice_number
            ):
                raise AppValidationError(f"Invoice number '{invoice_number}' already exists")
            
            # Convert estimate line items to invoice line items
            invoice_line_items = self._convert_line_items(estimate.line_items)
            
            # Create payment terms
            payment_terms = self._create_payment_terms(request, estimate)
            
            # Create the invoice entity
            invoice = Invoice(
                id=uuid.uuid4(),
                business_id=business_id,
                invoice_number=invoice_number,
                status=InvoiceStatus.DRAFT,
                client_id=estimate.contact_id,
                client_name=estimate.client_name,
                client_email=estimate.client_email,
                client_phone=estimate.client_phone,
                client_address=estimate.client_address,
                title=request.title or estimate.title,
                description=request.description or estimate.description,
                line_items=invoice_line_items,
                currency=estimate.currency,
                tax_rate=estimate.tax_rate,
                tax_type=estimate.tax_type,
                overall_discount_type=estimate.overall_discount_type,
                overall_discount_value=estimate.overall_discount_value,
                payments=[],  # No payments initially
                payment_terms=payment_terms,
                template_id=estimate.template_id,
                template_data=estimate.template_data.copy(),
                estimate_id=estimate.id,  # Link back to the original estimate
                project_id=estimate.project_id,
                job_id=estimate.job_id,
                contact_id=estimate.contact_id,
                tags=estimate.tags.copy(),
                custom_fields=estimate.custom_fields.copy(),
                internal_notes=request.internal_notes or estimate.internal_notes,
                created_by=user_id,
                created_date=datetime.utcnow(),
                last_modified=datetime.utcnow(),
                due_date=request.due_date or self._calculate_due_date(payment_terms.net_days)
            )
            
            # Record advance payment if it was part of the estimate
            if estimate.advance_payment and estimate.advance_payment.amount > 0:
                advance_payment = Payment(
                    id=uuid.uuid4(),
                    amount=estimate.advance_payment.amount,
                    payment_date=datetime.utcnow(),
                    payment_method=PaymentMethod.CASH,  # Default, can be updated later
                    status=PaymentStatus.COMPLETED,
                    reference="Advance payment from estimate",
                    notes=f"Advance payment from estimate {estimate.estimate_number}",
                    processed_by=user_id,
                    refunded_amount=Decimal('0')
                )
                invoice.payments.append(advance_payment)
                
                # Update invoice status if fully paid
                if invoice.get_balance_due() <= 0:
                    invoice.status = InvoiceStatus.PAID
                    invoice.paid_date = datetime.utcnow()
                elif invoice.get_total_payments() > 0:
                    invoice.status = InvoiceStatus.PARTIALLY_PAID
            
            # Validate business rules
            self._validate_business_rules(invoice)
            
            # Save the invoice
            created_invoice = await self.invoice_repository.create(invoice)
            
            # Update estimate status to converted
            estimate.status = EstimateStatus.CONVERTED
            estimate.last_modified = datetime.utcnow()
            await self.estimate_repository.update(estimate)
            
            logger.info(f"Successfully converted estimate {estimate_id} to invoice {created_invoice.id} with number {created_invoice.invoice_number}")
            
            return InvoiceDTO.from_entity(created_invoice)
            
        except DomainValidationError as e:
            logger.warning(f"Validation error converting estimate to invoice: {e}")
            raise AppValidationError(str(e))
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation converting estimate to invoice: {e}")
            raise AppValidationError(str(e))
        except EntityNotFoundError as e:
            logger.warning(f"Entity not found converting estimate to invoice: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error converting estimate to invoice: {e}")
            raise ApplicationError(f"Failed to convert estimate to invoice: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to convert estimates in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can convert estimates
        pass
    
    async def _validate_and_get_estimate(self, estimate_id: uuid.UUID, business_id: uuid.UUID) -> Estimate:
        """Validate and retrieve the estimate."""
        estimate = await self.estimate_repository.get_by_id(estimate_id)
        if not estimate:
            raise EntityNotFoundError(f"Estimate with ID {estimate_id} not found")
        
        if estimate.business_id != business_id:
            raise BusinessRuleViolationError("Estimate does not belong to the specified business")
        
        return estimate
    
    def _validate_estimate_for_conversion(self, estimate: Estimate) -> None:
        """Validate that the estimate can be converted to an invoice."""
        # Check estimate status
        if estimate.status not in [EstimateStatus.SENT, EstimateStatus.VIEWED, EstimateStatus.ACCEPTED]:
            raise BusinessRuleViolationError(
                f"Estimate with status '{estimate.status.value}' cannot be converted to invoice. "
                f"Only sent, viewed, or accepted estimates can be converted."
            )
        
        # Check if estimate is expired
        if estimate.valid_until_date and estimate.valid_until_date < date.today():
            raise BusinessRuleViolationError("Cannot convert expired estimate to invoice")
        
        # Check if estimate has already been converted
        if estimate.status == EstimateStatus.CONVERTED:
            raise BusinessRuleViolationError("Estimate has already been converted to an invoice")
        
        # Validate financial amounts
        if estimate.get_total_amount() <= 0:
            raise BusinessRuleViolationError("Cannot convert estimate with zero or negative total amount")
        
        # Validate line items
        if not estimate.line_items:
            raise BusinessRuleViolationError("Cannot convert estimate without line items")
    
    def _convert_line_items(self, estimate_line_items) -> list:
        """Convert estimate line items to invoice line items."""
        invoice_line_items = []
        
        for estimate_item in estimate_line_items:
            invoice_item = InvoiceLineItem(
                id=uuid.uuid4(),
                description=estimate_item.description,
                quantity=estimate_item.quantity,
                unit_price=estimate_item.unit_price,
                unit=estimate_item.unit,
                category=estimate_item.category,
                discount_type=estimate_item.discount_type,
                discount_value=estimate_item.discount_value,
                tax_rate=estimate_item.tax_rate,
                notes=estimate_item.notes
            )
            invoice_line_items.append(invoice_item)
        
        return invoice_line_items
    
    def _create_payment_terms(self, request: CreateInvoiceFromEstimateDTO, estimate: Estimate) -> PaymentTerms:
        """Create payment terms for the invoice."""
        # Use request payment terms if provided, otherwise default values
        net_days = request.payment_net_days if request.payment_net_days is not None else 30
        
        return PaymentTerms(
            net_days=net_days,
            discount_percentage=Decimal(str(request.early_payment_discount_percentage or 0)),
            discount_days=request.early_payment_discount_days or 0,
            late_fee_percentage=Decimal(str(request.late_fee_percentage or 0)),
            late_fee_grace_days=request.late_fee_grace_days or 0,
            payment_instructions=request.payment_instructions or "Payment due within terms specified."
        )
    
    def _calculate_due_date(self, net_days: int) -> date:
        """Calculate the due date based on net days."""
        from datetime import timedelta
        return date.today() + timedelta(days=net_days)
    
    def _validate_business_rules(self, invoice: Invoice) -> None:
        """Validate business rules for the invoice."""
        # Validate financial calculations
        if invoice.get_total_amount() <= 0:
            raise BusinessRuleViolationError("Invoice total amount must be greater than zero")
        
        # Validate line items
        if not invoice.line_items:
            raise BusinessRuleViolationError("Invoice must have at least one line item")
        
        # Validate dates
        if invoice.due_date and invoice.due_date <= date.today():
            raise BusinessRuleViolationError("Invoice due date should be in the future")
        
        # Validate payment calculations
        if invoice.get_total_payments() > invoice.get_total_amount():
            raise BusinessRuleViolationError("Total payments cannot exceed invoice total amount")
        
        # Additional domain-specific validations
        try:
            invoice.validate()
        except Exception as e:
            raise BusinessRuleViolationError(f"Invoice validation failed: {str(e)}") 