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
            logger.info(f"🔧 ListInvoicesUseCase: Starting execution for business {business_id} by user {user_id}")
            logger.info(f"🔧 ListInvoicesUseCase: Filters: {filters}")
            logger.info(f"🔧 ListInvoicesUseCase: Pagination - skip: {skip}, limit: {limit}")
            
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
            if filters.overdue_only:
                filter_dict["overdue_only"] = filters.overdue_only
            
            logger.info(f"🔧 ListInvoicesUseCase: Built filter dict: {filter_dict}")
            
            # Get invoices with filters (returns both invoices and total count)
            logger.info(f"🔧 ListInvoicesUseCase: Calling repository.list_with_pagination...")
            invoices, total_count = await self.invoice_repository.list_with_pagination(
                business_id=business_id,
                skip=skip,
                limit=limit,
                filters=filter_dict if filter_dict else None
            )
            
            logger.info(f"🔧 ListInvoicesUseCase: Repository returned {len(invoices)} invoices, total_count: {total_count}")
            
            # Log details about each invoice entity
            for i, invoice in enumerate(invoices):
                logger.info(f"🔧 ListInvoicesUseCase: Invoice {i+1}: ID={invoice.id}, number={invoice.invoice_number}")
                logger.info(f"🔧 ListInvoicesUseCase: Invoice {i+1}: status={invoice.status}, line_items_count={len(invoice.line_items)}")
                if hasattr(invoice, 'get_total_amount'):
                    logger.info(f"🔧 ListInvoicesUseCase: Invoice {i+1}: total_amount={invoice.get_total_amount()}")
                else:
                    logger.info(f"🔧 ListInvoicesUseCase: Invoice {i+1}: No get_total_amount method")
                
                # Log line items details
                for j, item in enumerate(invoice.line_items):
                    logger.info(f"🔧 ListInvoicesUseCase: Invoice {i+1}, LineItem {j+1}: {item.description}, qty={item.quantity}, price={item.unit_price}")
                    if hasattr(item, 'get_line_total'):
                        logger.info(f"🔧 ListInvoicesUseCase: Invoice {i+1}, LineItem {j+1}: line_total={item.get_line_total()}")
            
            # Convert to DTOs
            logger.info(f"🔧 ListInvoicesUseCase: Converting {len(invoices)} invoices to DTOs...")
            invoice_dtos = []
            for i, invoice in enumerate(invoices):
                logger.info(f"🔧 ListInvoicesUseCase: Converting invoice {i+1} to DTO...")
                try:
                    dto = InvoiceDTO.from_entity(invoice)
                    logger.info(f"🔧 ListInvoicesUseCase: DTO {i+1}: total_amount={dto.total_amount}, line_items_count={len(dto.line_items)}")
                    invoice_dtos.append(dto)
                except Exception as e:
                    logger.error(f"❌ ListInvoicesUseCase: Error converting invoice {i+1} to DTO: {e}")
                    raise
            
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
            
            logger.info(f"🔧 ListInvoicesUseCase: Successfully prepared result with {len(invoice_dtos)} DTOs")
            logger.info(f"🔧 ListInvoicesUseCase: Result summary - total_count: {total_count}, has_next: {has_next}, has_previous: {has_previous}")
            
            return result
            
        except BusinessRuleViolationError as e:
            logger.warning(f"Business rule violation listing invoices: {e}")
            raise AppValidationError(str(e))
        except Exception as e:
            logger.error(f"❌ ListInvoicesUseCase: Unexpected error listing invoices: {e}")
            logger.error(f"❌ ListInvoicesUseCase: Error type: {type(e)}")
            import traceback
            logger.error(f"❌ ListInvoicesUseCase: Traceback: {traceback.format_exc()}")
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