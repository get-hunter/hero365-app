"""
Voice agent tools for invoice management.
Provides voice-activated invoice operations for Hero365.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from decimal import Decimal

from livekit.agents import function_tool

from app.infrastructure.config.dependency_injection import DependencyContainer
from app.application.use_cases.invoice.create_invoice_use_case import CreateInvoiceUseCase
from app.application.use_cases.invoice.get_invoice_use_case import GetInvoiceUseCase
from app.application.use_cases.invoice.list_invoices_use_case import ListInvoicesUseCase
from app.application.use_cases.invoice.update_invoice_use_case import UpdateInvoiceUseCase
from app.application.use_cases.invoice.delete_invoice_use_case import DeleteInvoiceUseCase
from app.application.use_cases.invoice.search_invoices_use_case import SearchInvoicesUseCase
from app.application.use_cases.invoice.process_payment_use_case import ProcessPaymentUseCase
from app.application.dto.invoice_dto import (
    InvoiceDTO,
    CreateInvoiceDTO,
    ProcessPaymentDTO,
    InvoiceLineItemDTO,
    InvoiceSearchCriteria,
    InvoiceListFilters,
)
from app.application.dto.contact_dto import ContactSearchDTO
from app.domain.enums import InvoiceStatus, PaymentStatus

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
        logger.warning("Agent context not available for invoice tools")
        return {"business_id": None, "user_id": None}
    return _current_context


@function_tool
async def create_invoice(
    contact_id: str,
    title: str,
    description: Optional[str] = None,
    amount: float = 0.0,
    due_days: int = 30,
    project_id: Optional[str] = None,
    job_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new invoice for a client.
    
    Args:
        contact_id: ID of the client contact
        title: Invoice title or description
        description: Detailed invoice description
        amount: Invoice amount (will create a single line item if > 0)
        due_days: Days until invoice is due (default: 30)
        project_id: Optional project ID to associate with invoice
        job_id: Optional job ID to associate with invoice
    
    Returns:
        Dictionary with invoice creation result
    """
    try:
        container = DependencyContainer()
        create_invoice_use_case = container.get_create_invoice_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to create invoice. Please try again."
            }
        
        # Calculate due date
        due_date = datetime.now().date() + timedelta(days=due_days)
        
        # Create line items if amount is provided
        line_items = []
        if amount > 0:
            line_items.append({
                "description": title,
                "quantity": 1,
                "unit_price": amount,
                "total": amount
            })
        
        invoice_dto = CreateInvoiceDTO(
            contact_id=uuid.UUID(contact_id),
            title=title,
            description=description,
            line_items=line_items,
            due_date=due_date,
            project_id=uuid.UUID(project_id) if project_id else None,
            job_id=uuid.UUID(job_id) if job_id else None
        )
        
        result = await create_invoice_use_case.execute(invoice_dto, business_id, user_id)
        
        logger.info(f"Created invoice via voice agent: {result.id}")
        
        return {
            "success": True,
            "invoice_id": str(result.id),
            "invoice_number": result.invoice_number,
            "title": result.title,
            "total_amount": float(result.total_amount),
            "due_date": result.due_date.isoformat() if result.due_date else None,
            "message": f"Invoice {result.invoice_number} created successfully for ${result.total_amount}"
        }
        
    except Exception as e:
        logger.error(f"Error creating invoice via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create invoice. Please try again or contact support."
        }


@function_tool
async def get_unpaid_invoices(limit: int = 10) -> Dict[str, Any]:
    """
    Get unpaid invoices for the business.
    
    Args:
        limit: Maximum number of invoices to return (default: 10)
    
    Returns:
        Dictionary with unpaid invoices list
    """
    try:
        container = DependencyContainer()
        invoice_repository = container.get_invoice_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve invoices. Please try again."
            }
        
        # Get unpaid invoices directly from repository
        invoices = await invoice_repository.get_by_status(
            business_id=uuid.UUID(business_id),
            status=InvoiceStatus.SENT,
            skip=0,
            limit=limit
        )
        
        unpaid_invoices = []
        total_unpaid = Decimal('0')
        
        for invoice in invoices:
            invoice_data = {
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "title": invoice.title,
                "total_amount": float(invoice.total_amount),
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "days_overdue": (datetime.now().date() - invoice.due_date).days if invoice.due_date and invoice.due_date < datetime.now().date() else 0,
                "status": invoice.status.value
            }
            unpaid_invoices.append(invoice_data)
            total_unpaid += invoice.total_amount
        
        logger.info(f"Retrieved {len(unpaid_invoices)} unpaid invoices via voice agent")
        
        return {
            "success": True,
            "invoices": unpaid_invoices,
            "total_count": len(unpaid_invoices),
            "total_unpaid_amount": float(total_unpaid),
            "message": f"Found {len(unpaid_invoices)} unpaid invoices totaling ${total_unpaid}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving unpaid invoices via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve unpaid invoices. Please try again."
        }


@function_tool
async def get_overdue_invoices(limit: int = 10) -> Dict[str, Any]:
    """
    Get overdue invoices for the business.
    
    Args:
        limit: Maximum number of invoices to return (default: 10)
    
    Returns:
        Dictionary with overdue invoices list
    """
    try:
        container = DependencyContainer()
        invoice_repository = container.get_invoice_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve overdue invoices. Please try again."
            }
        
        # Get overdue invoices directly from repository
        invoices = await invoice_repository.get_overdue_invoices(
            business_id=uuid.UUID(business_id),
            skip=0,
            limit=limit
        )
        
        overdue_invoices = []
        total_overdue = Decimal('0')
        
        for invoice in invoices:
            days_overdue = (datetime.now().date() - invoice.due_date).days if invoice.due_date else 0
            invoice_data = {
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "title": invoice.title,
                "total_amount": float(invoice.total_amount),
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "days_overdue": days_overdue,
                "status": invoice.status.value
            }
            overdue_invoices.append(invoice_data)
            total_overdue += invoice.total_amount
        
        logger.info(f"Retrieved {len(overdue_invoices)} overdue invoices via voice agent")
        
        return {
            "success": True,
            "invoices": overdue_invoices,
            "total_count": len(overdue_invoices),
            "total_overdue_amount": float(total_overdue),
            "message": f"Found {len(overdue_invoices)} overdue invoices totaling ${total_overdue}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving overdue invoices via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve overdue invoices. Please try again."
        }


@function_tool
async def get_invoices_by_status(status: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get invoices filtered by status.
    
    Args:
        status: Invoice status (draft, sent, viewed, paid, overdue, cancelled)
        limit: Maximum number of invoices to return (default: 10)
    
    Returns:
        Dictionary with filtered invoices
    """
    try:
        container = DependencyContainer()
        invoice_repository = container.get_invoice_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve invoices by status. Please try again."
            }
        
        # Convert status string to enum
        try:
            status_enum = InvoiceStatus(status.upper())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid status: {status}",
                "message": "Valid statuses are: draft, sent, viewed, paid, overdue, cancelled"
            }
        
        # Get invoices by status directly from repository
        invoices = await invoice_repository.get_by_status(
            business_id=uuid.UUID(business_id),
            status=status_enum,
            skip=0,
            limit=limit
        )
        
        invoice_list = []
        total_amount = Decimal('0')
        
        for invoice in invoices:
            invoice_list.append({
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "title": invoice.title,
                "total_amount": float(invoice.total_amount),
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "status": invoice.status.value
            })
            total_amount += invoice.total_amount
        
        logger.info(f"Retrieved {len(invoice_list)} invoices with status {status} via voice agent")
        
        return {
            "success": True,
            "invoices": invoice_list,
            "status_filter": status,
            "total_count": len(invoice_list),
            "total_amount": float(total_amount),
            "message": f"Found {len(invoice_list)} invoices with status: {status}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving invoices by status via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve invoices by status. Please try again."
        }


@function_tool
async def process_payment(invoice_id: str, amount: float, payment_method: str = "cash") -> Dict[str, Any]:
    """
    Process a payment for an invoice.
    
    Args:
        invoice_id: ID of the invoice to process payment for
        amount: Payment amount
        payment_method: Payment method (cash, check, card, bank_transfer)
    
    Returns:
        Dictionary with payment processing result
    """
    try:
        container = DependencyContainer()
        process_payment_use_case = container.get_process_payment_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to process payment. Please try again."
            }
        
        payment_dto = ProcessPaymentDTO(
            invoice_id=uuid.UUID(invoice_id),
            amount=Decimal(str(amount)),
            payment_method=payment_method,
            payment_date=datetime.now().date()
        )
        
        result = await process_payment_use_case.execute(payment_dto, business_id, user_id)
        
        logger.info(f"Processed payment for invoice {invoice_id} via voice agent")
        
        return {
            "success": True,
            "invoice_id": invoice_id,
            "payment_amount": amount,
            "payment_method": payment_method,
            "remaining_balance": float(result.remaining_balance) if hasattr(result, 'remaining_balance') else 0,
            "message": f"Payment of ${amount} processed successfully for invoice {invoice_id}"
        }
        
    except Exception as e:
        logger.error(f"Error processing payment via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process payment. Please try again."
        }


@function_tool
async def get_invoice_details(invoice_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific invoice.
    
    Args:
        invoice_id: ID of the invoice to retrieve
    
    Returns:
        Dictionary with invoice details
    """
    try:
        container = DependencyContainer()
        get_invoice_use_case = container.get_get_invoice_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve invoice details. Please try again."
            }
        
        result = await get_invoice_use_case.execute(
            invoice_id=uuid.UUID(invoice_id),
            business_id=business_id,
            user_id=user_id
        )
        
        logger.info(f"Retrieved invoice details for {invoice_id} via voice agent")
        
        return {
            "success": True,
            "invoice": {
                "id": str(result.id),
                "invoice_number": result.invoice_number,
                "title": result.title,
                "description": result.description,
                "status": result.status.value,
                "total_amount": float(result.total_amount),
                "paid_amount": float(result.paid_amount) if hasattr(result, 'paid_amount') else 0,
                "remaining_balance": float(result.remaining_balance) if hasattr(result, 'remaining_balance') else float(result.total_amount),
                "issue_date": result.issue_date.isoformat() if result.issue_date else None,
                "due_date": result.due_date.isoformat() if result.due_date else None,
                "line_items": [
                    {
                        "description": item.description,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price),
                        "total": float(item.total)
                    } for item in result.line_items
                ] if hasattr(result, 'line_items') else []
            },
            "message": f"Retrieved details for invoice {result.invoice_number}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving invoice details via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve invoice details. Please try again."
        }


@function_tool
async def search_invoices(search_term: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search invoices by number, title, or description.
    
    Args:
        search_term: Text to search for in invoice numbers, titles, or descriptions
        limit: Maximum number of invoices to return (default: 10)
    
    Returns:
        Dictionary with search results
    """
    try:
        container = DependencyContainer()
        search_invoices_use_case = container.get_search_invoices_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to search invoices. Please try again."
            }
        
        search_criteria = InvoiceSearchCriteria(
            search_text=search_term
        )
        
        results = await search_invoices_use_case.search_invoices(
            business_id=business_id,
            criteria=search_criteria,
            user_id=user_id,
            skip=0,
            limit=limit
        )
        
        invoices = []
        for invoice in results:
            invoices.append({
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "title": invoice.title,
                "status": invoice.status.value,
                "total_amount": float(invoice.total_amount),
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None
            })
        
        logger.info(f"Found {len(invoices)} invoices matching '{search_term}' via voice agent")
        
        return {
            "success": True,
            "invoices": invoices,
            "search_term": search_term,
            "total_count": len(invoices),
            "message": f"Found {len(invoices)} invoices matching '{search_term}'"
        }
        
    except Exception as e:
        logger.error(f"Error searching invoices via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to search invoices. Please try again."
        } 