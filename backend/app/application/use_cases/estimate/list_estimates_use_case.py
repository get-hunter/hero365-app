"""
List Estimates Use Case

Handles listing estimates with filtering, pagination, and business logic validation.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.estimate import Estimate
from app.domain.enums import EstimateStatus
from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.exceptions.domain_exceptions import BusinessRuleViolationError
from app.application.dto.estimate_dto import EstimateDTO, EstimateListFilters
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class ListEstimatesUseCase:
    """Use case for listing estimates with filtering and pagination."""
    
    def __init__(self, estimate_repository: EstimateRepository):
        self.estimate_repository = estimate_repository
    
    async def execute(
        self, 
        business_id: uuid.UUID,
        user_id: str,
        filters: EstimateListFilters,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Execute the list estimates use case."""
        try:
            logger.info(f"Listing estimates for business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id)
            
            # Validate pagination parameters
            self._validate_pagination_params(skip, limit)
            
            # Build filters dictionary for repository
            filter_dict = {}
            if filters.status:
                filter_dict["status"] = filters.status
            if filters.contact_id:
                filter_dict["contact_id"] = filters.contact_id
            if filters.project_id:
                filter_dict["project_id"] = filters.project_id
            if filters.job_id:
                filter_dict["job_id"] = filters.job_id
            if filters.date_from:
                filter_dict["date_from"] = filters.date_from
            if filters.date_to:
                filter_dict["date_to"] = filters.date_to
            
            # Get estimates with filters (returns both estimates and total count)
            estimates, total_count = await self.estimate_repository.list_with_pagination(
                business_id=business_id,
                skip=skip,
                limit=limit,
                filters=filter_dict if filter_dict else None
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
                "has_previous": has_previous
            }
            
            logger.info(f"Successfully listed {len(estimate_dtos)} estimates (total: {total_count})")
            
            return result
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation listing estimates: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error listing estimates: {e}")
            raise ApplicationError(f"Failed to list estimates: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to list estimates in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can list estimates
        pass
    
    def _validate_pagination_params(self, skip: int, limit: int) -> None:
        """Validate pagination parameters."""
        if skip < 0:
            raise AppValidationError("Skip parameter cannot be negative")
        
        if limit <= 0:
            raise AppValidationError("Limit parameter must be positive")
        
        if limit > 1000:
            raise AppValidationError("Limit parameter cannot exceed 1000") 