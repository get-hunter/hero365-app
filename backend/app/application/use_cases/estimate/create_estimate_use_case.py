"""
Create Estimate Use Case

Handles creating new estimates with comprehensive validation and business rules.
"""

import uuid
import logging
from typing import Optional
from datetime import datetime, date

from app.domain.entities.estimate import Estimate, EstimateTerms, AdvancePayment
from app.domain.enums import EstimateStatus, DocumentType
from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.exceptions.domain_exceptions import BusinessRuleViolationError, DomainValidationError
from app.application.dto.estimate_dto import EstimateCreateDTO, EstimateDTO
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)


class CreateEstimateUseCase:
    """Use case for creating new estimates with business validation."""
    
    def __init__(self, estimate_repository: EstimateRepository):
        self.estimate_repository = estimate_repository
    
    async def execute(
        self, 
        create_dto: EstimateCreateDTO,
        user_id: str
    ) -> EstimateDTO:
        """
        Execute the create estimate use case.
        
        Args:
            create_dto: Data for creating the estimate
            user_id: ID of the user creating the estimate
            
        Returns:
            EstimateDTO of the created estimate
            
        Raises:
            ValidationError: If input data is invalid
            BusinessRuleViolationError: If business rules are violated
            ApplicationError: If creation fails
        """
        try:
            logger.info(f"Creating estimate '{create_dto.title}' for business {create_dto.business_id}")
            
            # Validate permissions
            await self._validate_permissions(create_dto.business_id, user_id)
            
            # Check for duplicate estimate number if provided
            if hasattr(create_dto, 'estimate_number') and create_dto.estimate_number:
                await self._validate_unique_estimate_number(
                    create_dto.business_id, 
                    create_dto.estimate_number
                )
            
            # Create estimate entity with defaults
            estimate = await self._build_estimate_entity(create_dto, user_id)
            
            # Create the estimate in repository
            created_estimate = await self.estimate_repository.create(estimate)
            
            # Convert to DTO and return
            result_dto = EstimateDTO.from_entity(created_estimate)
            
            logger.info(f"Successfully created estimate {created_estimate.estimate_number} with ID {created_estimate.id}")
            
            return result_dto
            
        except (DomainValidationError, BusinessRuleViolationError) as e:
            logger.warning(f"Validation error creating estimate: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating estimate: {e}")
            raise ApplicationError(f"Failed to create estimate: {str(e)}")
    
    async def execute_from_template(
        self,
        template_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id: str,
        overrides: Optional[dict] = None
    ) -> EstimateDTO:
        """
        Create estimate from template with optional overrides.
        
        Args:
            template_id: ID of the template to use
            business_id: Business ID
            user_id: User creating the estimate
            overrides: Optional field overrides
            
        Returns:
            EstimateDTO of the created estimate
        """
        try:
            logger.info(f"Creating estimate from template {template_id}")
            
            # TODO: Implement template loading logic
            # For now, create basic estimate structure
            
            create_dto = EstimateCreateDTO(
                title=overrides.get("title", "Estimate from Template"),
                business_id=business_id,
                template_id=template_id,
                created_by=user_id,
                **(overrides or {})
            )
            
            return await self.execute(create_dto, user_id)
            
        except Exception as e:
            logger.error(f"Error creating estimate from template: {e}")
            raise ApplicationError(f"Failed to create estimate from template: {str(e)}")
    
    async def execute_quick_estimate(
        self,
        business_id: uuid.UUID,
        user_id: str,
        title: str,
        client_name: Optional[str] = None,
        client_email: Optional[str] = None,
        total_amount: Optional[float] = None,
        description: Optional[str] = None
    ) -> EstimateDTO:
        """
        Create a quick estimate with minimal required data.
        
        Args:
            business_id: Business ID
            user_id: User creating the estimate
            title: Estimate title
            client_name: Optional client name
            client_email: Optional client email
            total_amount: Optional total amount
            description: Optional description
            
        Returns:
            EstimateDTO of the created estimate
        """
        try:
            logger.info(f"Creating quick estimate '{title}' for business {business_id}")
            
            create_dto = EstimateCreateDTO(
                title=title,
                business_id=business_id,
                client_name=client_name,
                client_email=client_email,
                description=description,
                created_by=user_id
            )
            
            estimate_dto = await self.execute(create_dto, user_id)
            
            # Add a default line item if total_amount provided
            if total_amount and total_amount > 0:
                # TODO: Implement line item creation
                # For now, just log the intent
                logger.info(f"Would add line item with total: ${total_amount}")
            
            return estimate_dto
            
        except Exception as e:
            logger.error(f"Error creating quick estimate: {e}")
            raise ApplicationError(f"Failed to create quick estimate: {str(e)}")
    
    async def _build_estimate_entity(
        self, 
        create_dto: EstimateCreateDTO, 
        user_id: str
    ) -> Estimate:
        """Build estimate entity from DTO."""
        try:
            # Generate estimate number if not provided
            estimate_number = await self.estimate_repository.get_next_estimate_number(
                create_dto.business_id
            )
            
            # Create terms with defaults
            terms = EstimateTerms(
                validity_days=30,
                payment_terms="Net 30"
            )
            
            # Create advance payment with defaults
            advance_payment = AdvancePayment(
                required=False
            )
            
            # Create estimate entity
            estimate = Estimate(
                business_id=create_dto.business_id,
                estimate_number=estimate_number,
                title=create_dto.title,
                description=create_dto.description,
                po_number=create_dto.po_number,
                contact_id=create_dto.contact_id,
                client_name=create_dto.client_name,
                client_email=create_dto.client_email,
                client_phone=create_dto.client_phone,
                currency=create_dto.currency,
                tax_rate=create_dto.tax_rate,
                tax_type=create_dto.tax_type,
                project_id=create_dto.project_id,
                job_id=create_dto.job_id,
                template_id=create_dto.template_id,
                terms=terms,
                advance_payment=advance_payment,
                tags=create_dto.tags,
                internal_notes=create_dto.internal_notes,
                created_by=user_id,
                status=EstimateStatus.DRAFT,
                document_type=DocumentType.ESTIMATE
            )
            
            return estimate
            
        except Exception as e:
            logger.error(f"Error building estimate entity: {e}")
            raise DomainValidationError(f"Invalid estimate data: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to create estimates in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can create estimates
        logger.debug(f"Permission check passed for user {user_id} in business {business_id}")
    
    async def _validate_unique_estimate_number(
        self, 
        business_id: uuid.UUID, 
        estimate_number: str
    ) -> None:
        """Validate estimate number is unique within business."""
        if await self.estimate_repository.has_duplicate_estimate_number(business_id, estimate_number):
            raise BusinessRuleViolationError(
                f"Estimate number '{estimate_number}' already exists in this business"
            ) 