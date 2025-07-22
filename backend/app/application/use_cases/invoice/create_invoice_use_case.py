"""
Create Invoice Use Case

Handles the creation of new invoices with comprehensive business logic validation.
"""

import uuid
import logging
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.domain.entities.invoice import Invoice, InvoiceLineItem, PaymentTerms
from app.domain.entities.invoice_enums.enums import InvoiceStatus
from app.domain.shared.enums import CurrencyCode, TaxType, DiscountType, PaymentMethod
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.job_repository import JobRepository
from app.domain.exceptions.domain_exceptions import (
    DomainValidationError, BusinessRuleViolationError, EntityNotFoundError
)
from app.application.dto.invoice_dto import CreateInvoiceDTO, InvoiceDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class CreateInvoiceUseCase:
    """Use case for creating new invoices."""
    
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        contact_repository: ContactRepository,
        project_repository: Optional[ProjectRepository] = None,
        job_repository: Optional[JobRepository] = None
    ):
        self.invoice_repository = invoice_repository
        self.contact_repository = contact_repository
        self.project_repository = project_repository
        self.job_repository = job_repository
    
    async def execute(self, request: CreateInvoiceDTO, user_id: str, business_id: uuid.UUID) -> InvoiceDTO:
        """Execute the create invoice use case."""
        try:
            logger.info(f"Creating invoice for business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id)
            
            # Validate and get related entities
            contact = await self._validate_and_get_contact(request.contact_id, business_id)
            project = await self._get_project_if_specified(request.project_id, business_id)
            job = await self._get_job_if_specified(request.job_id, business_id)
            
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
            
            # Create line items
            line_items = self._create_line_items(request.line_items)
            
            # Create payment terms
            payment_terms = self._create_payment_terms(request)
            
            # Calculate due date
            issue_date = request.issue_date or date.today()
            due_date = request.due_date or (issue_date + timedelta(days=payment_terms.net_days))
            
            # Create the invoice entity
            invoice = Invoice(
                id=uuid.uuid4(),
                business_id=business_id,
                invoice_number=invoice_number,
                status=InvoiceStatus.DRAFT,
                client_id=request.contact_id,
                client_name=contact.get_display_name(),
                client_email=contact.email,
                client_phone=contact.phone,
                client_address=contact.address,
                title=request.title,
                description=request.description,
                po_number=request.po_number,
                line_items=line_items,
                currency=CurrencyCode(request.currency) if request.currency else CurrencyCode.USD,
                tax_rate=Decimal(str(request.tax_rate)) if request.tax_rate else Decimal('0'),
                tax_type=TaxType(request.tax_type) if request.tax_type else TaxType.PERCENTAGE,
                overall_discount_type=DiscountType(request.overall_discount_type) if request.overall_discount_type else DiscountType.NONE,
                overall_discount_value=Decimal(str(request.overall_discount_value)) if request.overall_discount_value else Decimal('0'),
                payments=[],  # No payments initially
                payment_terms=payment_terms,
                template_id=request.template_id,
                template_data=request.template_data or {},
                estimate_id=request.estimate_id,  # Link to estimate if created from one
                project_id=request.project_id,
                job_id=request.job_id,
                contact_id=request.contact_id,
                tags=request.tags or [],
                custom_fields=request.custom_fields or {},
                internal_notes=request.internal_notes,
                created_by=user_id,
                created_date=datetime.utcnow(),
                last_modified=datetime.utcnow(),
                issue_date=request.issue_date,
                due_date=due_date
            )
            
            # Validate business rules
            self._validate_business_rules(invoice)
            
            # Save the invoice
            created_invoice = await self.invoice_repository.create(invoice)
            
            logger.info(f"Successfully created invoice {created_invoice.id} with number {created_invoice.invoice_number}")
            
            return InvoiceDTO.from_entity(created_invoice)
            
        except DomainValidationError as e:
            logger.warning(f"Validation error creating invoice: {e}")
            raise AppValidationError(str(e))
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation creating invoice: {e}")
            raise AppValidationError(str(e))
        except EntityNotFoundError as e:
            logger.warning(f"Entity not found creating invoice: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating invoice: {e}")
            raise ApplicationError(f"Failed to create invoice: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to create invoices in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can create invoices
        pass
    
    async def _validate_and_get_contact(self, contact_id: uuid.UUID, business_id: uuid.UUID):
        """Validate and retrieve the contact."""
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise EntityNotFoundError(f"Contact with ID {contact_id} not found")
        
        if contact.business_id != business_id:
            raise BusinessRuleViolationError("Contact does not belong to the specified business")
        
        return contact
    
    async def _get_project_if_specified(self, project_id: Optional[uuid.UUID], business_id: uuid.UUID):
        """Get project if specified and validate it."""
        if not project_id or not self.project_repository:
            return None
        
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError(f"Project with ID {project_id} not found")
        
        if project.business_id != business_id:
            raise BusinessRuleViolationError("Project does not belong to the specified business")
        
        return project
    
    async def _get_job_if_specified(self, job_id: Optional[uuid.UUID], business_id: uuid.UUID):
        """Get job if specified and validate it."""
        if not job_id or not self.job_repository:
            return None
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise EntityNotFoundError(f"Job with ID {job_id} not found")
        
        if job.business_id != business_id:
            raise BusinessRuleViolationError("Job does not belong to the specified business")
        
        return job
    
    def _create_line_items(self, line_items_data: List[dict]) -> List[InvoiceLineItem]:
        """Create invoice line items from data."""
        line_items = []
        
        for item_data in line_items_data:
            try:
                line_item = InvoiceLineItem(
                    id=uuid.uuid4(),
                    description=item_data.get("description", ""),
                    quantity=Decimal(str(item_data.get("quantity", "1"))),
                    unit_price=Decimal(str(item_data.get("unit_price", "0"))),
                    unit=item_data.get("unit"),
                    category=item_data.get("category"),
                    discount_type=DiscountType(item_data.get("discount_type", "none")),
                    discount_value=Decimal(str(item_data.get("discount_value", "0"))),
                    tax_rate=Decimal(str(item_data.get("tax_rate", "0"))),
                    notes=item_data.get("notes")
                )
                line_items.append(line_item)
            except (ValueError, TypeError) as e:
                raise ValidationError(f"Invalid line item data: {str(e)}")
        
        if not line_items:
            raise ValidationError("At least one line item is required")
        
        return line_items
    
    def _create_payment_terms(self, request: CreateInvoiceDTO) -> PaymentTerms:
        """Create payment terms from request data."""
        try:
            return PaymentTerms(
                net_days=request.payment_net_days or 30,
                discount_percentage=Decimal(str(request.early_payment_discount_percentage or 0)),
                discount_days=request.early_payment_discount_days or 0,
                late_fee_percentage=Decimal(str(request.late_fee_percentage or 0)),
                late_fee_grace_days=request.late_fee_grace_days or 0,
                payment_instructions=request.payment_instructions or "Payment due within terms specified."
            )
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid payment terms data: {str(e)}")
    
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
            logger.warning(f"Invoice due date {invoice.due_date} is in the past or today")
        
        # Additional domain-specific validations
        try:
            invoice.validate()
        except Exception as e:
            raise BusinessRuleViolationError(f"Invoice validation failed: {str(e)}") 