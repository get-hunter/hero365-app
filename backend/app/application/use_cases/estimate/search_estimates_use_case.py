"""
Search Estimates Use Case

Handles searching estimates with advanced filtering and business logic validation.
"""

import uuid
import logging
from typing import List, Dict, Any

from app.domain.entities.estimate import Estimate
from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.exceptions.domain_exceptions import BusinessRuleViolationError
from app.application.dto.estimate_dto import EstimateDTO, EstimateFilters
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class SearchEstimatesUseCase:
    """Use case for searching estimates with advanced criteria."""
    
    def __init__(self, estimate_repository: EstimateRepository):
        self.estimate_repository = estimate_repository
    
    async def execute(
        self, 
        business_id: uuid.UUID,
        user_id: str,
        search_criteria: EstimateFilters,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Execute the search estimates use case."""
        try:
            logger.info(f"Searching estimates for business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id)
            
            # Validate pagination parameters
            self._validate_pagination_params(skip, limit)
            
            # Validate search criteria
            self._validate_search_criteria(search_criteria)
            
            # Perform search
            estimates = await self.estimate_repository.search(
                business_id=business_id,
                search_criteria=search_criteria,
                skip=skip,
                limit=limit
            )
            
            # Get total count for pagination
            total_count = await self.estimate_repository.count_search_results(
                business_id=business_id,
                search_criteria=search_criteria
            )
            
            # Convert to DTOs
            estimate_dtos = [EstimateDTO.from_entity(estimate) for estimate in estimates]
            
            # Calculate pagination info
            has_next = skip + len(estimates) < total_count
            has_previous = skip > 0
            
            result = {
                "estimates": estimate_dtos,
                "total_count": total_count,
                "page_count": len(estimate_dtos),
                "skip": skip,
                "limit": limit,
                "has_next": has_next,
                "has_previous": has_previous,
                "search_criteria": search_criteria.__dict__
            }
            
            logger.info(f"Successfully found {len(estimate_dtos)} estimates (total: {total_count})")
            
            return result
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation searching estimates: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error searching estimates: {e}")
            raise ApplicationError(f"Failed to search estimates: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to search estimates in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can search estimates
        pass
    
    def _validate_pagination_params(self, skip: int, limit: int) -> None:
        """Validate pagination parameters."""
        if skip < 0:
            raise AppValidationError("Skip parameter cannot be negative")
        
        if limit <= 0:
            raise AppValidationError("Limit parameter must be positive")
        
        if limit > 1000:
            raise AppValidationError("Limit parameter cannot exceed 1000")
    
    def _validate_search_criteria(self, criteria: EstimateFilters) -> None:
        """Validate search criteria."""
        # Validate text search parameters
        if criteria.search_text and len(criteria.search_text.strip()) < 2:
            raise AppValidationError("Search text must be at least 2 characters long")
        
        # Validate amount ranges
        if criteria.min_amount is not None and criteria.min_amount < 0:
            raise AppValidationError("Minimum amount cannot be negative")
        
        if criteria.max_amount is not None and criteria.max_amount < 0:
            raise AppValidationError("Maximum amount cannot be negative")
        
        if (criteria.min_amount is not None and criteria.max_amount is not None and 
            criteria.min_amount > criteria.max_amount):
            raise AppValidationError("Minimum amount cannot be greater than maximum amount")
        
        # Validate date ranges
        if (criteria.date_from is not None and criteria.date_to is not None and 
            criteria.date_from > criteria.date_to):
            raise AppValidationError("Start date cannot be after end date")
        
        # Validate status list
        if criteria.statuses and len(criteria.statuses) == 0:
            raise AppValidationError("Status list cannot be empty if provided") 