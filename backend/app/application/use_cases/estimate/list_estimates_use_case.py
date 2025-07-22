"""
List Estimates Use Case

Handles listing estimates with filtering, pagination, and business logic validation.
Updated to use simplified repository interface and Pydantic filters.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.estimate import Estimate
from app.domain.entities.estimate_enums.enums import EstimateStatus
from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.exceptions.domain_exceptions import BusinessRuleViolationError
from app.application.dto.estimate_dto import EstimateDTO, EstimateFilters
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
        filters: EstimateFilters,
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
            
            # Convert Pydantic filters to dictionary
            filter_dict = filters.to_query_dict() if filters else {}
            
            # Get estimates with filters using simplified repository interface
            estimates, total_count = await self.estimate_repository.list_with_filters(
                business_id=business_id,
                filters=filter_dict,
                sort_by=filters.sort_by if filters else "created_date",
                sort_desc=filters.sort_desc if filters else True,
                skip=skip,
                limit=limit
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
                "filters_applied": filters.has_filters() if filters else False
            }
            
            logger.info(f"Successfully listed {len(estimate_dtos)} estimates (total: {total_count})")
            
            return result
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation listing estimates: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error listing estimates: {e}")
            raise ApplicationError(f"Failed to list estimates: {str(e)}")
    
    async def execute_with_common_filters(
        self,
        business_id: uuid.UUID,
        user_id: str,
        filter_type: str,
        skip: int = 0,
        limit: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute with common filter patterns for convenience.
        
        Args:
            business_id: Business ID
            user_id: User ID
            filter_type: Type of filter ('recent', 'pending', 'draft', 'expired', 'expiring_soon')
            skip: Pagination skip
            limit: Pagination limit
            **kwargs: Additional parameters (e.g., days for recent/expiring_soon)
        """
        try:
            from app.domain.repositories.estimate_repository import CommonEstimateQueries
            
            # Build query based on filter type
            if filter_type == "recent":
                days = kwargs.get("days", 30)
                query_builder = CommonEstimateQueries.recent_estimates(days)
            elif filter_type == "pending":
                query_builder = CommonEstimateQueries.pending_estimates()
            elif filter_type == "draft":
                query_builder = CommonEstimateQueries.draft_estimates()
            elif filter_type == "expired":
                query_builder = CommonEstimateQueries.expired_estimates()
            elif filter_type == "expiring_soon":
                days = kwargs.get("days", 7)
                query_builder = CommonEstimateQueries.expiring_soon_estimates(days)
            else:
                raise AppValidationError(f"Invalid filter type: {filter_type}")
            
            # Apply pagination
            query_builder.paginate(skip, limit)
            
            # Execute query
            estimates, total_count = await self.estimate_repository.execute_query(
                business_id, query_builder
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
                "filter_type": filter_type,
                "filter_params": kwargs
            }
            
            logger.info(f"Successfully listed {len(estimate_dtos)} {filter_type} estimates")
            return result
            
        except AppValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing {filter_type} estimates: {e}")
            raise ApplicationError(f"Failed to list {filter_type} estimates: {str(e)}")
    
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