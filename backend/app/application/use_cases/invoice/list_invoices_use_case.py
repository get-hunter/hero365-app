"""
List Invoices Use Case

Handles listing invoices with filtering, pagination, and business logic validation.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.entities.invoice import Invoice
from app.domain.enums import InvoiceStatus
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.domain.exceptions.domain_exceptions import BusinessRuleViolationError
from app.application.dto.invoice_dto import InvoiceDTO, InvoiceListFilters
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError as AppValidationError
)

logger = logging.getLogger(__name__)

class ListInvoicesUseCase:
    """Use case for listing invoices with filtering and pagination."""
    
    def __init__(self, invoice_repository: InvoiceRepository):
        self.invoice_repository = invoice_repository
    
    async def execute(
        self, 
        business_id: uuid.UUID,
        user_id: str,
        filters: InvoiceListFilters,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Execute the list invoices use case."""
        try:
            logger.info(f"Listing invoices for business {business_id} by user {user_id}")
            
            # Validate business context and permissions
            await self._validate_permissions(business_id, user_id)
            
            # Validate pagination parameters
            self._validate_pagination_params(skip, limit)
            
            # Get invoices with filters
            invoices = await self.invoice_repository.get_by_business_id(
                business_id=business_id,
                status=filters.status,
                contact_id=filters.contact_id,
                project_id=filters.project_id,
                job_id=filters.job_id,
                date_from=filters.date_from,
                date_to=filters.date_to,
                overdue_only=filters.overdue_only,
                skip=skip,
                limit=limit
            )
            
            # Get total count for pagination
            total_count = await self.invoice_repository.count_by_business_id(
                business_id=business_id,
                status=filters.status,
                contact_id=filters.contact_id,
                project_id=filters.project_id,
                job_id=filters.job_id,
                date_from=filters.date_from,
                date_to=filters.date_to,
                overdue_only=filters.overdue_only
            )
            
            # Convert to DTOs
            invoice_dtos = [InvoiceDTO.from_entity(invoice) for invoice in invoices]
            
            # Calculate pagination info
            has_next = skip + len(invoices) < total_count
            has_previous = skip > 0
            
            result = {
                "invoices": invoice_dtos,
                "total_count": total_count,
                "page_count": len(invoice_dtos),
                "skip": skip,
                "limit": limit,
                "has_next": has_next,
                "has_previous": has_previous
            }
            
            logger.info(f"Successfully listed {len(invoice_dtos)} invoices (total: {total_count})")
            
            return result
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation listing invoices: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error listing invoices: {e}")
            raise ApplicationError(f"Failed to list invoices: {str(e)}")
    
    async def _validate_permissions(self, business_id: uuid.UUID, user_id: str) -> None:
        """Validate user has permission to list invoices in this business."""
        # TODO: Implement permission checking logic
        # For now, we assume all authenticated users can list invoices
        pass
    
    def _validate_pagination_params(self, skip: int, limit: int) -> None:
        """Validate pagination parameters."""
        if skip < 0:
            raise AppValidationError("Skip parameter cannot be negative")
        
        if limit <= 0:
            raise AppValidationError("Limit parameter must be positive")
        
        if limit > 1000:
            raise AppValidationError("Limit parameter cannot exceed 1000") 