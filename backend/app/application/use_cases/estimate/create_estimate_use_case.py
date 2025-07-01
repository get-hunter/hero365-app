"""
Create Estimate Use Case

Handles the creation of new estimates with comprehensive business logic validation.
"""

import uuid
import logging
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from app.domain.entities.estimate import Estimate, EstimateLineItem, EstimateTerms, AdvancePayment
from app.domain.entities.estimate_template import EstimateTemplate
from app.domain.enums import EstimateStatus, CurrencyCode, TaxType, DiscountType, DocumentType
from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.repositories.estimate_template_repository import EstimateTemplateRepository
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.job_repository import JobRepository
from app.domain.exceptions.domain_exceptions import (
    DomainValidationError, BusinessRuleViolationError, EntityNotFoundError
)
from app.application.dto.estimate_dto import CreateEstimateDTO, EstimateDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class CreateEstimateUseCase:
    """Use case for creating new estimates."""
    
    def __init__(
        self,
        estimate_repository: EstimateRepository,
        estimate_template_repository: EstimateTemplateRepository,
        contact_repository: ContactRepository,
        project_repository: Optional[ProjectRepository] = None,
        job_repository: Optional[JobRepository] = None
    ):
        self.estimate_repository = estimate_repository
        self.estimate_template_repository = estimate_template_repository
        self.contact_repository = contact_repository
        self.project_repository = project_repository
        self.job_repository = job_repository
    
    async def execute(self, request: CreateEstimateDTO, user_id: str, business_id: uuid.UUID) -> EstimateDTO:
        """Execute the create estimate use case."""
        try:
            logger.info(f"Creating estimate for business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id)
            
            # Validate and get related entities
            contact = await self._validate_and_get_contact(request.contact_id, business_id)
            template = await self._get_template_if_specified(request.template_id, business_id)
            project = await self._get_project_if_specified(request.project_id, business_id)
            job = await self._get_job_if_specified(request.job_id, business_id)
            
            # Generate estimate number if not provided
            estimate_number = request.estimate_number
            if not estimate_number:
                estimate_number = await self.estimate_repository.get_next_estimate_number(
                    business_id, request.number_prefix or "EST"
                )
            
            # Check for duplicate estimate number
            if await self.estimate_repository.has_duplicate_estimate_number(
                business_id, estimate_number
            ):
                raise AppValidationError(f"Estimate number '{estimate_number}' already exists")
            
            # Create line items
            line_items = self._create_line_items(request.line_items)
            
            # Create estimate terms if provided
            terms = self._create_estimate_terms(request.terms) if request.terms else None
            
            # Create advance payment if provided
            advance_payment = self._create_advance_payment(request.advance_payment) if request.advance_payment else None
            
            # Create the estimate entity
            estimate = Estimate(
                id=uuid.uuid4(),
                business_id=business_id,
                estimate_number=estimate_number,
                document_type=DocumentType(request.document_type) if request.document_type else DocumentType.ESTIMATE,
                status=EstimateStatus.DRAFT,
                contact_id=request.contact_id,
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
                terms=terms,
                advance_payment=advance_payment,
                template_id=request.template_id,
                template_data=request.template_data or {},
                project_id=request.project_id,
                job_id=request.job_id,
                tags=request.tags or [],
                custom_fields=request.custom_fields or {},
                internal_notes=request.internal_notes,
                issue_date=request.issue_date,
                valid_until_date=request.valid_until_date,
                created_by=user_id,
                created_date=datetime.utcnow(),
                last_modified=datetime.utcnow()
            )
            
            # Validate business rules
            self._validate_business_rules(estimate)
            
            # Save the estimate
            created_estimate = await self.estimate_repository.create(estimate)
            
            # Increment template usage count if template was used
            if template:
                await self.estimate_template_repository.increment_usage_count(template.id)
            
            logger.info(f"Successfully created estimate {created_estimate.id} with number {created_estimate.estimate_number}")
            
            return EstimateDTO.from_entity(created_estimate)
            
        except DomainValidationError as e:
            logger.warning(f"Validation error creating estimate: {e}")
            raise AppValidationError(str(e))
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation creating estimate: {e}")
            raise AppValidationError(str(e))
        except EntityNotFoundError as e:
            logger.warning(f"Entity not found creating estimate: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating estimate: {e}")
            raise ApplicationError(f"Failed to create estimate: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to create estimates in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can create estimates
        pass
    
    async def _validate_and_get_contact(self, contact_id: uuid.UUID, business_id: uuid.UUID):
        """Validate and retrieve the contact."""
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise EntityNotFoundError(f"Contact with ID {contact_id} not found")
        
        if contact.business_id != business_id:
            raise BusinessRuleViolationError("Contact does not belong to the specified business")
        
        return contact
    
    async def _get_template_if_specified(self, template_id: Optional[uuid.UUID], business_id: uuid.UUID) -> Optional[EstimateTemplate]:
        """Get template if specified and validate it."""
        if not template_id:
            return None
        
        template = await self.estimate_template_repository.get_by_id(template_id)
        if not template:
            raise EntityNotFoundError(f"Template with ID {template_id} not found")
        
        if template.business_id and template.business_id != business_id:
            raise BusinessRuleViolationError("Template does not belong to the specified business")
        
        if not template.is_active:
            raise BusinessRuleViolationError("Template is not active")
        
        return template
    
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
    
    def _create_line_items(self, line_items_data: List[dict]) -> List[EstimateLineItem]:
        """Create estimate line items from data."""
        line_items = []
        
        for item_data in line_items_data:
            try:
                line_item = EstimateLineItem(
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
    
    def _create_estimate_terms(self, terms_data: dict) -> EstimateTerms:
        """Create estimate terms from data."""
        try:
            return EstimateTerms(
                payment_terms=terms_data.get("payment_terms", ""),
                validity_period=terms_data.get("validity_period", 30),
                work_schedule=terms_data.get("work_schedule", ""),
                materials_policy=terms_data.get("materials_policy", ""),
                change_order_policy=terms_data.get("change_order_policy", ""),
                warranty_terms=terms_data.get("warranty_terms", ""),
                cancellation_policy=terms_data.get("cancellation_policy", ""),
                acceptance_criteria=terms_data.get("acceptance_criteria", ""),
                additional_terms=terms_data.get("additional_terms", [])
            )
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid terms data: {str(e)}")
    
    def _create_advance_payment(self, advance_data: dict) -> AdvancePayment:
        """Create advance payment from data."""
        try:
            return AdvancePayment(
                amount=Decimal(str(advance_data.get("amount", "0"))),
                percentage=Decimal(str(advance_data.get("percentage", "0"))),
                due_date=advance_data.get("due_date"),
                description=advance_data.get("description", ""),
                is_required=advance_data.get("is_required", False)
            )
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid advance payment data: {str(e)}")
    
    def _validate_business_rules(self, estimate: Estimate) -> None:
        """Validate business rules for the estimate."""
        # Validate financial calculations
        if estimate.get_total_amount() <= 0:
            raise BusinessRuleViolationError("Estimate total amount must be greater than zero")
        
        # Validate line items
        if not estimate.line_items:
            raise BusinessRuleViolationError("Estimate must have at least one line item")
        
        # Validate dates
        if estimate.valid_until_date and estimate.valid_until_date <= date.today():
            raise BusinessRuleViolationError("Valid until date must be in the future")
        
        # Validate advance payment
        if estimate.advance_payment:
            if estimate.advance_payment.amount > estimate.get_total_amount():
                raise BusinessRuleViolationError("Advance payment amount cannot exceed total estimate amount")
            
            if estimate.advance_payment.percentage > Decimal('100'):
                raise BusinessRuleViolationError("Advance payment percentage cannot exceed 100%")
        
        # Additional domain-specific validations
        try:
            estimate.validate()
        except Exception as e:
            raise BusinessRuleViolationError(f"Estimate validation failed: {str(e)}") 