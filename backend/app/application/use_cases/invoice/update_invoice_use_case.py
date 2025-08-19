"""
Update Invoice Use Case

Handles the updating of existing invoices with comprehensive business logic validation.
"""

import uuid
import logging
from typing import Optional
from datetime import datetime

from app.domain.entities.invoice import Invoice, InvoiceLineItem
from app.domain.entities.invoice_enums.enums import InvoiceStatus
from app.domain.shared.enums import CurrencyCode, TaxType, DiscountType
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.domain.repositories.template_repository import TemplateRepository
from app.domain.entities.template import TemplateType
from app.domain.exceptions.domain_exceptions import (
    DomainValidationError, BusinessRuleViolationError, EntityNotFoundError
)
from app.application.dto.invoice_dto import UpdateInvoiceDTO, InvoiceDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class UpdateInvoiceUseCase:
    """Use case for updating existing invoices."""
    
    def __init__(self, invoice_repository: InvoiceRepository, template_repository: TemplateRepository = None):
        self.invoice_repository = invoice_repository
        self.template_repository = template_repository
    
    async def execute(self, request: UpdateInvoiceDTO, user_id: str) -> InvoiceDTO:
        """Execute the update invoice use case."""
        try:
            logger.info(f"Updating invoice {request.invoice_id} for business {request.business_id} by user {user_id}")
            
            # Validate and get existing invoice
            invoice = await self._validate_and_get_invoice(request.invoice_id, request.business_id)
            
            # Validate invoice can be updated
            self._validate_invoice_for_update(invoice)
            
            # Validate template if provided
            if request.template_id is not None:
                validated_template_id = await self._validate_template(request.template_id, request.business_id)
                request.template_id = validated_template_id
            
            # Update invoice fields
            self._update_invoice_fields(invoice, request)
            
            # Update line items if provided
            if request.line_items is not None:
                self._update_line_items(invoice, request.line_items)
            
            # Update timestamp and user
            invoice.last_modified = datetime.utcnow()
            
            # Validate business rules after update
            self._validate_business_rules(invoice)
            
            # Save the updated invoice
            updated_invoice = await self.invoice_repository.update(invoice)
            
            logger.info(f"Successfully updated invoice {updated_invoice.id}")
            
            return InvoiceDTO.from_entity(updated_invoice)
            
        except DomainValidationError as e:
            logger.warning(f"Validation error updating invoice: {e}")
            raise AppValidationError(str(e))
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation updating invoice: {e}")
            raise AppValidationError(str(e))
        except EntityNotFoundError as e:
            logger.warning(f"Entity not found updating invoice: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error updating invoice: {e}")
            raise ApplicationError(f"Failed to update invoice: {str(e)}")
    
    async def _validate_and_get_invoice(self, invoice_id: uuid.UUID, business_id: uuid.UUID) -> Invoice:
        """Validate and retrieve the invoice."""
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            raise EntityNotFoundError(f"Invoice with ID {invoice_id} not found")
        
        if invoice.business_id != business_id:
            raise BusinessRuleViolationError("Invoice does not belong to the specified business")
        
        return invoice
    
    def _validate_invoice_for_update(self, invoice: Invoice) -> None:
        """Validate that the invoice can be updated."""
        # Check if invoice has payments - limit updates if it does
        if invoice.payments and len(invoice.payments) > 0:
            logger.info(f"Invoice {invoice.id} has payments, limiting updateable fields")
            # Note: We still allow updates but caller should be aware of limitations
        
        # Check if invoice is in a status that allows updates
        restricted_statuses = [InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]
        restricted_status_values = [status.value for status in restricted_statuses]
        
        # Handle both enum and string status values (due to use_enum_values: True)
        current_status = invoice.status.value if hasattr(invoice.status, 'value') else invoice.status
        
        if current_status in restricted_status_values:
            raise BusinessRuleViolationError(
                f"Invoice with status '{current_status}' cannot be updated"
            )
    
    async def _validate_template(self, template_id: uuid.UUID, business_id: uuid.UUID) -> Optional[uuid.UUID]:
        """Validate template exists or return default template."""
        if self.template_repository is None:
            logger.info(f"Template repository is None, returning template_id {template_id} as-is")
            return template_id
            
        try:
            # Check if template exists
            logger.info(f"Looking up template {template_id} in database")
            template = await self.template_repository.get_by_id(template_id)
            if template:
                logger.info(f"Found template: id={template.id}, business_id={template.business_id}, is_system={template.is_system}, is_active={template.is_active}")
                logger.info(f"Checking if template belongs to business {business_id} or is system template")
                
                # Validate it's either a system template or belongs to this business
                if template.is_system or template.business_id == business_id:
                    logger.info(f"Template validation passed, using template {template_id}")
                    return template_id
                else:
                    logger.warning(f"Template {template_id} doesn't belong to business {business_id} (template.business_id={template.business_id}, is_system={template.is_system})")
            else:
                logger.warning(f"Template {template_id} not found in database")
            
            # Get default template as fallback
            logger.info(f"Attempting to get default template for business {business_id} and type INVOICE")
            default_template = await self.template_repository.get_default_template(
                business_id=business_id,
                template_type=TemplateType.INVOICE
            )
            
            if default_template:
                logger.warning(f"CLIENT DATA ISSUE: Template {template_id} not found/invalid. Using default template {default_template.id} ({default_template.name}). Client should refresh template cache.")
                return default_template.id
            else:
                logger.error("CRITICAL: No default template found, setting template_id to None")
                return None
                
        except Exception as e:
            logger.error(f"Error validating template: {e}")
            return None
    
    def _update_invoice_fields(self, invoice: Invoice, request: UpdateInvoiceDTO) -> None:
        """Update invoice fields with provided values."""
        if request.title is not None:
            invoice.title = request.title
        
        if request.description is not None:
            invoice.description = request.description
        
        if request.currency is not None:
            invoice.currency = CurrencyCode(request.currency)
        
        if request.tax_rate is not None:
            invoice.tax_rate = request.tax_rate
        
        if request.tax_type is not None:
            invoice.tax_type = TaxType(request.tax_type)
        
        if request.overall_discount_type is not None:
            invoice.overall_discount_type = DiscountType(request.overall_discount_type)
        
        if request.overall_discount_value is not None:
            invoice.overall_discount_value = request.overall_discount_value
        
        if request.template_id is not None:
            # Note: Template validation happens in execute method now
            invoice.template_id = request.template_id
        
        if request.template_data is not None:
            invoice.template_data = request.template_data
        
        if request.tags is not None:
            invoice.tags = request.tags
        
        if request.custom_fields is not None:
            invoice.custom_fields = request.custom_fields
        
        if request.internal_notes is not None:
            invoice.internal_notes = request.internal_notes
        
        if request.due_date is not None:
            invoice.due_date = request.due_date
        
        if request.payment_instructions is not None:
            invoice.payment_instructions = request.payment_instructions
    
    def _update_line_items(self, invoice: Invoice, line_items_dto) -> None:
        """Update invoice line items."""
        # Convert DTOs to domain entities
        updated_line_items = []
        
        for item_dto in line_items_dto:
            line_item = InvoiceLineItem(
                id=item_dto.id or uuid.uuid4(),
                description=item_dto.description,
                quantity=item_dto.quantity,
                unit_price=item_dto.unit_price,
                unit=item_dto.unit,
                category=item_dto.category,
                discount_type=DiscountType(item_dto.discount_type),
                discount_value=item_dto.discount_value,
                tax_rate=item_dto.tax_rate,
                notes=item_dto.notes
            )
            updated_line_items.append(line_item)
        
        invoice.line_items = updated_line_items
    
    def _validate_business_rules(self, invoice: Invoice) -> None:
        """Validate business rules for the updated invoice."""
        # Validate that the invoice has at least one line item
        if not invoice.line_items or len(invoice.line_items) == 0:
            raise BusinessRuleViolationError("Invoice must have at least one line item")
        
        # Validate line items
        for line_item in invoice.line_items:
            if line_item.quantity <= 0:
                raise BusinessRuleViolationError("Line item quantity must be greater than zero")
            
            if line_item.unit_price < 0:
                raise BusinessRuleViolationError("Line item unit price cannot be negative")
        
        # Validate financial calculations
        try:
            total_amount = invoice.get_total_amount()
            if total_amount < 0:
                raise BusinessRuleViolationError("Invoice total cannot be negative")
        except Exception as e:
            raise BusinessRuleViolationError(f"Invalid financial calculation: {str(e)}")
        
        # Validate currency consistency
        for line_item in invoice.line_items:
            # All line items should be compatible with invoice currency
            pass  # Domain entities should handle this
        
        logger.debug(f"Business rule validation passed for invoice {invoice.id}") 