"""
Update Estimate Use Case

Handles updating estimate information with comprehensive business logic validation.
"""

import uuid
import logging
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

from app.domain.entities.estimate import Estimate, EstimateLineItem, EstimateTerms, AdvancePayment
from app.domain.entities.estimate_enums.enums import EstimateStatus
from app.domain.shared.enums import CurrencyCode, TaxType, DiscountType
from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.repositories.contact_repository import ContactRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.job_repository import JobRepository
from app.domain.exceptions.domain_exceptions import (
    DomainValidationError, BusinessRuleViolationError, EntityNotFoundError
)
from app.application.dto.estimate_dto import EstimateUpdateDTO, EstimateDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class UpdateEstimateUseCase:
    """Use case for updating estimates."""
    
    def __init__(
        self,
        estimate_repository: EstimateRepository,
        contact_repository: ContactRepository,
        project_repository: Optional[ProjectRepository] = None,
        job_repository: Optional[JobRepository] = None
    ):
        self.estimate_repository = estimate_repository
        self.contact_repository = contact_repository
        self.project_repository = project_repository
        self.job_repository = job_repository
    
    async def execute(
        self, 
        estimate_id: uuid.UUID,
        request: EstimateUpdateDTO, 
        user_id: str, 
        business_id: uuid.UUID
    ) -> EstimateDTO:
        """Execute the update estimate use case."""
        try:
            logger.info(f"Updating estimate {estimate_id} for business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id, "update")
            
            # Get and validate the estimate
            estimate = await self._validate_and_get_estimate(estimate_id, business_id)
            
            # Validate estimate can be updated
            self._validate_estimate_for_update(estimate)
            
            # Validate and get related entities if they're being updated
            if request.contact_id and request.contact_id != estimate.contact_id:
                contact = await self._validate_and_get_contact(request.contact_id, business_id)
                estimate.contact_id = request.contact_id
                estimate.client_name = contact.get_display_name()
                estimate.client_email = contact.email
                estimate.client_phone = contact.phone
                estimate.client_address = contact.address
            
            if request.project_id is not None and request.project_id != estimate.project_id:
                if request.project_id:
                    await self._validate_and_get_project(request.project_id, business_id)
                estimate.project_id = request.project_id
            
            if request.job_id is not None and request.job_id != estimate.job_id:
                if request.job_id:
                    await self._validate_and_get_job(request.job_id, business_id)
                estimate.job_id = request.job_id
            
            # Update estimate fields
            self._update_estimate_fields(estimate, request)
            
            # Validate business rules
            self._validate_business_rules(estimate)
            
            # Update timestamps
            estimate.last_modified = datetime.utcnow()
            
            # Save the updated estimate
            updated_estimate = await self.estimate_repository.update(estimate)
            
            logger.info(f"Successfully updated estimate {estimate_id}")
            
            return EstimateDTO.from_entity(updated_estimate)
            
        except DomainValidationError as e:
            logger.warning(f"Validation error updating estimate: {e}")
            raise AppValidationError(str(e))
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation updating estimate: {e}")
            raise AppValidationError(str(e))
        except EntityNotFoundError as e:
            logger.warning(f"Entity not found updating estimate: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error updating estimate: {e}")
            raise ApplicationError(f"Failed to update estimate: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str, action: str) -> None:
        """Validate user has permission to update estimates in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can update estimates
        pass
    
    async def _validate_and_get_estimate(self, estimate_id: uuid.UUID, business_id: uuid.UUID) -> Estimate:
        """Validate and retrieve the estimate."""
        estimate = await self.estimate_repository.get_by_id(estimate_id)
        if not estimate:
            raise EntityNotFoundError(f"Estimate with ID {estimate_id} not found")
        
        if estimate.business_id != business_id:
            raise BusinessRuleViolationError("Estimate does not belong to the specified business")
        
        return estimate
    
    def _validate_estimate_for_update(self, estimate: Estimate) -> None:
        """Validate that the estimate can be updated."""
        # Check if estimate is in a state that allows updates
        if estimate.status in [EstimateStatus.CONVERTED, EstimateStatus.EXPIRED, EstimateStatus.CANCELLED]:
            raise BusinessRuleViolationError(
                f"Estimate with status '{estimate.status.value}' cannot be updated"
            )
        
        # Additional business rules can be added here
        # For example, check if user has permission to update this specific estimate
    
    async def _validate_and_get_contact(self, contact_id: uuid.UUID, business_id: uuid.UUID):
        """Validate and retrieve the contact."""
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise EntityNotFoundError(f"Contact with ID {contact_id} not found")
        
        if contact.business_id != business_id:
            raise BusinessRuleViolationError("Contact does not belong to the specified business")
        
        return contact
    
    async def _validate_and_get_project(self, project_id: uuid.UUID, business_id: uuid.UUID):
        """Validate and retrieve the project."""
        if not self.project_repository:
            raise ApplicationError("Project repository not available")
        
        project = await self.project_repository.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError(f"Project with ID {project_id} not found")
        
        if project.business_id != business_id:
            raise BusinessRuleViolationError("Project does not belong to the specified business")
        
        return project
    
    async def _validate_and_get_job(self, job_id: uuid.UUID, business_id: uuid.UUID):
        """Validate and retrieve the job."""
        if not self.job_repository:
            raise ApplicationError("Job repository not available")
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise EntityNotFoundError(f"Job with ID {job_id} not found")
        
        if job.business_id != business_id:
            raise BusinessRuleViolationError("Job does not belong to the specified business")
        
        return job
    
    def _update_estimate_fields(self, estimate: Estimate, request: EstimateUpdateDTO) -> None:
        """Update estimate fields from the request."""
        # Update basic fields
        if request.title is not None:
            estimate.title = request.title
        
        if request.description is not None:
            estimate.description = request.description
        
        if request.currency is not None:
            estimate.currency = CurrencyCode(request.currency)
        
        if request.tax_rate is not None:
            estimate.tax_rate = Decimal(str(request.tax_rate))
        
        if request.tax_type is not None:
            estimate.tax_type = TaxType(request.tax_type)
        
        if request.overall_discount_type is not None:
            estimate.overall_discount_type = DiscountType(request.overall_discount_type)
        
        if request.overall_discount_value is not None:
            estimate.overall_discount_value = Decimal(str(request.overall_discount_value))
        
        if request.valid_until_date is not None:
            estimate.valid_until_date = request.valid_until_date
        
        if request.internal_notes is not None:
            estimate.internal_notes = request.internal_notes
        
        if request.tags is not None:
            estimate.tags = request.tags
        
        if request.custom_fields is not None:
            estimate.custom_fields = request.custom_fields
        
        # Update line items if provided
        if request.line_items is not None:
            estimate.line_items = self._create_line_items(request.line_items)
        
        # Update terms if provided
        if request.terms is not None:
            estimate.terms = self._create_estimate_terms(request.terms)
        
        # Update advance payment if provided
        if request.advance_payment is not None:
            estimate.advance_payment = self._create_advance_payment(request.advance_payment)
    
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
                raise AppValidationError(f"Invalid line item data: {str(e)}")
        
        if not line_items:
            raise AppValidationError("At least one line item is required")
        
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
            raise AppValidationError(f"Invalid terms data: {str(e)}")
    
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
            raise AppValidationError(f"Invalid advance payment data: {str(e)}")
    
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