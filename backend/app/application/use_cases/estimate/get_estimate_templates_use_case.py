"""
Get Estimate Templates Use Case

Handles retrieving estimate templates with filtering and business logic validation.
"""

import uuid
import logging
from typing import List, Optional
from datetime import datetime

from app.domain.entities.estimate_template import EstimateTemplate
from app.domain.enums import TemplateType
from app.domain.repositories.estimate_template_repository import EstimateTemplateRepository
from app.domain.exceptions.domain_exceptions import BusinessRuleViolationError
from app.application.dto.estimate_dto import (
    EstimateTemplateListFilters, EstimateTemplateListResponseDTO, EstimateTemplateResponseDTO
)
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class GetEstimateTemplatesUseCase:
    """Use case for retrieving estimate templates with filtering."""
    
    def __init__(self, estimate_template_repository: EstimateTemplateRepository):
        self.estimate_template_repository = estimate_template_repository
    
    async def execute(
        self, 
        filters: EstimateTemplateListFilters,
        user_id: str
    ) -> EstimateTemplateListResponseDTO:
        """Execute the get estimate templates use case."""
        try:
            logger.info(f"Getting estimate templates for business {filters.business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(filters.business_id, user_id)
            
            # Validate pagination parameters
            self._validate_pagination_params(filters.skip, filters.limit)
            
            # Get templates with filters
            if filters.template_type:
                try:
                    template_type = TemplateType(filters.template_type)
                    templates = await self.estimate_template_repository.get_by_type(
                        business_id=filters.business_id,
                        template_type=template_type,
                        skip=filters.skip,
                        limit=filters.limit
                    )
                except ValueError:
                    # Invalid template type, return empty list
                    templates = []
            elif filters.is_active is not None:
                if filters.is_active:
                    templates = await self.estimate_template_repository.get_active_templates(
                        business_id=filters.business_id,
                        skip=filters.skip,
                        limit=filters.limit
                    )
                else:
                    # Get all templates and filter inactive ones
                    all_templates = await self.estimate_template_repository.get_by_business_id(
                        business_id=filters.business_id,
                        skip=filters.skip,
                        limit=filters.limit
                    )
                    templates = [t for t in all_templates if not t.is_active]
            else:
                templates = await self.estimate_template_repository.get_by_business_id(
                    business_id=filters.business_id,
                    skip=filters.skip,
                    limit=filters.limit
                )
            
            # Get total count for pagination
            total_count = await self.estimate_template_repository.count_by_business(
                business_id=filters.business_id
            )
            
            # Convert to DTOs
            template_dtos = [EstimateTemplateResponseDTO.from_entity(template) for template in templates]
            
            # Calculate pagination info
            has_next = filters.skip + len(templates) < total_count
            has_previous = filters.skip > 0
            
            logger.info(f"Successfully retrieved {len(templates)} estimate templates")
            
            return EstimateTemplateListResponseDTO(
                templates=template_dtos,
                total_count=total_count,
                page=filters.skip // filters.limit + 1,
                per_page=filters.limit,
                has_next=has_next,
                has_prev=has_previous
            )
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation getting estimate templates: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error getting estimate templates: {e}")
            raise ApplicationError(f"Failed to get estimate templates: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to view estimate templates in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can view estimate templates
        pass
    
    def _validate_pagination_params(self, skip: int, limit: int) -> None:
        """Validate pagination parameters."""
        if skip < 0:
            raise AppValidationError("Skip parameter must be non-negative")
        
        if limit <= 0:
            raise AppValidationError("Limit parameter must be positive")
        
        if limit > 1000:
            raise AppValidationError("Limit parameter cannot exceed 1000") 