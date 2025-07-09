"""
Voice agent tools for estimate management.
Provides voice-activated estimate operations for Hero365.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from decimal import Decimal

from livekit.agents import function_tool

from app.infrastructure.config.dependency_injection import get_container
from app.application.use_cases.estimate.create_estimate_use_case import CreateEstimateUseCase
from app.application.use_cases.estimate.get_estimate_use_case import GetEstimateUseCase
from app.application.use_cases.estimate.list_estimates_use_case import ListEstimatesUseCase
from app.application.use_cases.estimate.update_estimate_use_case import UpdateEstimateUseCase
from app.application.use_cases.estimate.delete_estimate_use_case import DeleteEstimateUseCase
from app.application.use_cases.estimate.search_estimates_use_case import SearchEstimatesUseCase
from app.application.use_cases.estimate.convert_estimate_to_invoice_use_case import ConvertEstimateToInvoiceUseCase
from app.application.dto.estimate_dto import (
    EstimateDTO,
    CreateEstimateDTO,
    EstimateLineItemDTO,
    EstimateSearchCriteria,
    EstimateListFilters,
    UpdateEstimateDTO,
)
from app.application.dto.contact_dto import ContactSearchDTO
from app.domain.enums import EstimateStatus, DocumentType

logger = logging.getLogger(__name__)

# Global context storage for the worker environment
_current_context: Dict[str, Any] = {}

def set_current_context(context: Dict[str, Any]) -> None:
    """Set the current agent context."""
    global _current_context
    _current_context = context

def get_current_context() -> Dict[str, Any]:
    """Get the current agent context."""
    global _current_context
    if not _current_context.get("business_id") or not _current_context.get("user_id"):
        logger.warning("Agent context not available for estimate tools")
        return {"business_id": None, "user_id": None}
    return _current_context


@function_tool
async def create_estimate(
    contact_id: str,
    title: str,
    description: Optional[str] = None,
    amount: float = 0.0,
    valid_days: int = 30,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new estimate for a client.
    
    Args:
        contact_id: ID of the client contact
        title: Estimate title or description
        description: Detailed estimate description
        amount: Estimate amount (will create a single line item if > 0)
        valid_days: Days until estimate expires (default: 30)
        project_id: Optional project ID to associate with estimate
    
    Returns:
        Dictionary with estimate creation result
    """
    try:
        container = get_container()
        create_estimate_use_case = container.get_create_estimate_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to create estimate. Please try again."
            }
        
        # Calculate expiration date
        expiration_date = datetime.now().date() + timedelta(days=valid_days)
        
        # Create line items if amount is provided
        line_items = []
        if amount > 0:
            line_items.append({
                "description": title,
                "quantity": 1,
                "unit_price": amount,
                "total": amount
            })
        
        estimate_dto = CreateEstimateDTO(
            contact_id=uuid.UUID(contact_id),
            title=title,
            description=description,
            line_items=line_items,
            expiration_date=expiration_date,
            project_id=uuid.UUID(project_id) if project_id else None
        )
        
        result = await create_estimate_use_case.execute(estimate_dto, business_id, user_id)
        
        logger.info(f"Created estimate via voice agent: {result.id}")
        
        return {
            "success": True,
            "estimate_id": str(result.id),
            "estimate_number": result.estimate_number,
            "title": result.title,
            "total_amount": float(result.total_amount),
            "expiration_date": result.expiration_date.isoformat() if result.expiration_date else None,
            "message": f"Estimate {result.estimate_number} created successfully for ${result.total_amount}"
        }
        
    except Exception as e:
        logger.error(f"Error creating estimate via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create estimate. Please try again or contact support."
        }


@function_tool
async def get_pending_estimates(limit: int = 10) -> Dict[str, Any]:
    """
    Get pending estimates for the business.
    
    Args:
        limit: Maximum number of estimates to return (default: 10)
    
    Returns:
        Dictionary with pending estimates list
    """
    try:
        container = get_container()
        estimate_repository = container.get_estimate_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve estimates. Please try again."
            }
        
        # Get pending estimates directly from repository
        estimates = await estimate_repository.get_by_status(
            business_id=uuid.UUID(business_id),
            status=EstimateStatus.SENT,
            skip=0,
            limit=limit
        )
        
        pending_estimates = []
        total_pending = Decimal('0')
        
        for estimate in estimates:
            estimate_data = {
                "id": str(estimate.id),
                "estimate_number": estimate.estimate_number,
                "title": estimate.title,
                "total_amount": float(estimate.total_amount),
                "expiration_date": estimate.expiration_date.isoformat() if estimate.expiration_date else None,
                "days_until_expiry": (estimate.expiration_date - datetime.now().date()).days if estimate.expiration_date else None,
                "status": estimate.status.value
            }
            pending_estimates.append(estimate_data)
            total_pending += estimate.total_amount
        
        logger.info(f"Retrieved {len(pending_estimates)} pending estimates via voice agent")
        
        return {
            "success": True,
            "estimates": pending_estimates,
            "total_count": len(pending_estimates),
            "total_pending_amount": float(total_pending),
            "message": f"Found {len(pending_estimates)} pending estimates totaling ${total_pending}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving pending estimates via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve pending estimates. Please try again."
        }


@function_tool
async def get_expired_estimates(limit: int = 10) -> Dict[str, Any]:
    """
    Get expired estimates for the business.
    
    Args:
        limit: Maximum number of estimates to return (default: 10)
    
    Returns:
        Dictionary with expired estimates list
    """
    try:
        container = get_container()
        estimate_repository = container.get_estimate_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve expired estimates. Please try again."
            }
        
        # Get expired estimates directly from repository
        estimates = await estimate_repository.get_expired_estimates(
            business_id=uuid.UUID(business_id),
            skip=0,
            limit=limit
        )
        
        expired_estimates = []
        total_expired = Decimal('0')
        
        for estimate in estimates:
            days_expired = (datetime.now().date() - estimate.expiration_date).days if estimate.expiration_date else 0
            estimate_data = {
                "id": str(estimate.id),
                "estimate_number": estimate.estimate_number,
                "title": estimate.title,
                "total_amount": float(estimate.total_amount),
                "expiration_date": estimate.expiration_date.isoformat() if estimate.expiration_date else None,
                "days_expired": days_expired,
                "status": estimate.status.value
            }
            expired_estimates.append(estimate_data)
            total_expired += estimate.total_amount
        
        logger.info(f"Retrieved {len(expired_estimates)} expired estimates via voice agent")
        
        return {
            "success": True,
            "estimates": expired_estimates,
            "total_count": len(expired_estimates),
            "total_expired_amount": float(total_expired),
            "message": f"Found {len(expired_estimates)} expired estimates totaling ${total_expired}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving expired estimates via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve expired estimates. Please try again."
        }


@function_tool
async def get_estimates_by_status(status: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get estimates filtered by status.
    
    Args:
        status: Estimate status (draft, sent, viewed, accepted, rejected, expired)
        limit: Maximum number of estimates to return (default: 10)
    
    Returns:
        Dictionary with filtered estimates
    """
    try:
        container = get_container()
        estimate_repository = container.get_estimate_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve estimates by status. Please try again."
            }
        
        # Convert status string to enum
        try:
            status_enum = EstimateStatus(status.upper())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid status: {status}",
                "message": "Valid statuses are: draft, sent, viewed, accepted, rejected, expired"
            }
        
        # Get estimates by status directly from repository
        estimates = await estimate_repository.get_by_status(
            business_id=uuid.UUID(business_id),
            status=status_enum,
            skip=0,
            limit=limit
        )
        
        estimate_list = []
        total_amount = Decimal('0')
        
        for estimate in estimates:
            estimate_list.append({
                "id": str(estimate.id),
                "estimate_number": estimate.estimate_number,
                "title": estimate.title,
                "total_amount": float(estimate.total_amount),
                "expiration_date": estimate.expiration_date.isoformat() if estimate.expiration_date else None,
                "status": estimate.status.value
            })
            total_amount += estimate.total_amount
        
        logger.info(f"Retrieved {len(estimate_list)} estimates with status {status} via voice agent")
        
        return {
            "success": True,
            "estimates": estimate_list,
            "status_filter": status,
            "total_count": len(estimate_list),
            "total_amount": float(total_amount),
            "message": f"Found {len(estimate_list)} estimates with status: {status}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving estimates by status via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve estimates by status. Please try again."
        }


@function_tool
async def convert_estimate_to_invoice(estimate_id: str) -> Dict[str, Any]:
    """
    Convert an accepted estimate to an invoice.
    
    Args:
        estimate_id: ID of the estimate to convert
    
    Returns:
        Dictionary with conversion result
    """
    try:
        container = get_container()
        convert_estimate_use_case = container.get_convert_estimate_to_invoice_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to convert estimate to invoice. Please try again."
            }
        
        result = await convert_estimate_use_case.execute(
            estimate_id=uuid.UUID(estimate_id),
            business_id=business_id,
            user_id=user_id
        )
        
        logger.info(f"Converted estimate {estimate_id} to invoice via voice agent")
        
        return {
            "success": True,
            "estimate_id": estimate_id,
            "invoice_id": str(result.id),
            "invoice_number": result.invoice_number,
            "total_amount": float(result.total_amount),
            "message": f"Estimate converted to invoice {result.invoice_number} successfully"
        }
        
    except Exception as e:
        logger.error(f"Error converting estimate to invoice via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to convert estimate to invoice. Please try again."
        }


@function_tool
async def get_estimate_details(estimate_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific estimate.
    
    Args:
        estimate_id: ID of the estimate to retrieve
    
    Returns:
        Dictionary with estimate details
    """
    try:
        container = get_container()
        get_estimate_use_case = container.get_get_estimate_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve estimate details. Please try again."
            }
        
        result = await get_estimate_use_case.execute(
            estimate_id=uuid.UUID(estimate_id),
            business_id=business_id,
            user_id=user_id
        )
        
        logger.info(f"Retrieved estimate details for {estimate_id} via voice agent")
        
        return {
            "success": True,
            "estimate": {
                "id": str(result.id),
                "estimate_number": result.estimate_number,
                "title": result.title,
                "description": result.description,
                "status": result.status.value,
                "total_amount": float(result.total_amount),
                "issue_date": result.issue_date.isoformat() if result.issue_date else None,
                "expiration_date": result.expiration_date.isoformat() if result.expiration_date else None,
                "line_items": [
                    {
                        "description": item.description,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price),
                        "total": float(item.total)
                    } for item in result.line_items
                ] if hasattr(result, 'line_items') else []
            },
            "message": f"Retrieved details for estimate {result.estimate_number}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving estimate details via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve estimate details. Please try again."
        }


@function_tool
async def update_estimate_status(estimate_id: str, new_status: str, notes: Optional[str] = None) -> Dict[str, Any]:
    """
    Update estimate status with optional notes.
    
    Args:
        estimate_id: ID of the estimate to update
        new_status: New status (draft, sent, viewed, accepted, rejected, expired)
        notes: Optional notes about the status change
    
    Returns:
        Dictionary with update result
    """
    try:
        container = get_container()
        update_estimate_use_case = container.get_update_estimate_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to update estimate status. Please try again."
            }
        
        # Convert status string to enum
        try:
            status_enum = EstimateStatus(new_status.upper())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid status: {new_status}",
                "message": "Valid statuses are: draft, sent, viewed, accepted, rejected, expired"
            }
        
        # Update estimate status
        try:
            container = get_container()
            update_use_case = container.get_update_estimate_use_case()
            
            # Create update DTO
            update_dto = UpdateEstimateDTO(
                title=None,  # Don't change title
                description=notes
            )
            
            updated_estimate = await update_use_case.execute(
                estimate_id=uuid.UUID(estimate_id),
                request=update_dto,
                user_id=user_id,
                business_id=business_id
            )
            
            return {
                "success": True,
                "message": f"Estimate {estimate_id} status updated to {new_status}",
                "estimate": {
                    "id": str(updated_estimate.id),
                    "estimate_number": updated_estimate.estimate_number,
                    "status": updated_estimate.status,
                    "title": updated_estimate.title,
                    "total_amount": float(updated_estimate.total_amount) if updated_estimate.total_amount else 0.0
                }
            }
        except Exception as e:
            logger.error(f"Error updating estimate status via voice agent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update estimate status. Please try again."
            }
        
    except Exception as e:
        logger.error(f"Error updating estimate status via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to update estimate status. Please try again."
        }


@function_tool
async def search_estimates(search_term: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search estimates by number, title, or description.
    
    Args:
        search_term: Text to search for in estimate numbers, titles, or descriptions
        limit: Maximum number of estimates to return (default: 10)
    
    Returns:
        Dictionary with search results
    """
    try:
        container = get_container()
        search_estimates_use_case = container.get_search_estimates_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to search estimates. Please try again."
            }
        
        # Search estimates
        try:
            container = get_container()
            search_use_case = container.get_search_estimates_use_case()
            
            search_criteria = EstimateSearchCriteria(
                search_term=search_term
            )
            
            results = await search_use_case.execute(
                business_id=business_id,
                user_id=user_id,
                search_criteria=search_criteria,
                skip=0,
                limit=10
            )
            
            estimates = results.get("estimates", [])
            
            if not estimates:
                return {
                    "success": True,
                    "message": f"No estimates found matching '{search_term}'",
                    "estimates": []
                }
            
            estimate_list = []
            for estimate in estimates:
                estimate_list.append({
                    "id": str(estimate.id),
                    "estimate_number": estimate.estimate_number,
                    "status": estimate.status,
                    "title": estimate.title,
                    "client_name": estimate.client_name,
                    "total_amount": float(estimate.total_amount) if estimate.total_amount else 0.0,
                    "created_date": estimate.created_date.strftime("%Y-%m-%d") if estimate.created_date else None
                })
            
            return {
                "success": True,
                "message": f"Found {len(estimates)} estimates matching '{search_term}'",
                "estimates": estimate_list
            }
        except Exception as e:
            logger.error(f"Error searching estimates via voice agent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to search estimates. Please try again."
            }
        
    except Exception as e:
        logger.error(f"Error searching estimates via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to search estimates. Please try again."
        } 