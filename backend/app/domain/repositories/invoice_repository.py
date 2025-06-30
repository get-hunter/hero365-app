"""
Invoice Repository Interface

Defines the contract for invoice data access operations.
Follows the Repository pattern for clean architecture.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from ..entities.invoice import Invoice
from ..enums import InvoiceStatus, PaymentStatus, PaymentMethod, CurrencyCode


class InvoiceRepository(ABC):
    """
    Abstract repository interface for invoice data access operations.
    
    Defines all methods needed for invoice management without
    specifying implementation details.
    """
    
    @abstractmethod
    async def create(self, invoice: Invoice) -> Invoice:
        """Create a new invoice."""
        pass
    
    @abstractmethod
    async def get_by_id(self, invoice_id: uuid.UUID) -> Optional[Invoice]:
        """Get invoice by ID."""
        pass
    
    @abstractmethod
    async def get_by_invoice_number(self, business_id: uuid.UUID, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number within a business."""
        pass
    
    @abstractmethod
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices by business ID with pagination."""
        pass
    
    @abstractmethod
    async def get_by_contact_id(self, contact_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices by contact ID with pagination."""
        pass
    
    @abstractmethod
    async def get_by_project_id(self, project_id: uuid.UUID, business_id: uuid.UUID,
                               skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices associated with a specific project."""
        pass
    
    @abstractmethod
    async def get_by_job_id(self, job_id: uuid.UUID, business_id: uuid.UUID,
                           skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices associated with a specific job."""
        pass
    
    @abstractmethod
    async def get_by_estimate_id(self, estimate_id: uuid.UUID, business_id: uuid.UUID,
                                skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices converted from a specific estimate."""
        pass
    
    @abstractmethod
    async def get_by_status(self, business_id: uuid.UUID, status: InvoiceStatus,
                           skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices by status within a business."""
        pass
    
    @abstractmethod
    async def get_by_assigned_user(self, business_id: uuid.UUID, user_id: str,
                                  skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices assigned to a specific user within a business."""
        pass
    
    @abstractmethod
    async def get_by_template_id(self, business_id: uuid.UUID, template_id: uuid.UUID,
                                skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices using a specific template within a business."""
        pass
    
    @abstractmethod
    async def get_by_date_range(self, business_id: uuid.UUID, start_date: datetime,
                               end_date: datetime, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices within a date range."""
        pass
    
    @abstractmethod
    async def get_overdue_invoices(self, business_id: uuid.UUID,
                                  skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get overdue invoices within a business."""
        pass
    
    @abstractmethod
    async def get_due_soon(self, business_id: uuid.UUID, days: int = 7,
                          skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices due within the specified number of days."""
        pass
    
    @abstractmethod
    async def get_unpaid_invoices(self, business_id: uuid.UUID,
                                 skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get unpaid invoices within a business."""
        pass
    
    @abstractmethod
    async def get_partially_paid_invoices(self, business_id: uuid.UUID,
                                         skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get partially paid invoices within a business."""
        pass
    
    @abstractmethod
    async def get_by_payment_method(self, business_id: uuid.UUID, payment_method: PaymentMethod,
                                   skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices by payment method within a business."""
        pass
    
    @abstractmethod
    async def get_by_value_range(self, business_id: uuid.UUID, min_value: Decimal,
                                max_value: Decimal, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices within a value range."""
        pass
    
    @abstractmethod
    async def search_invoices(self, business_id: uuid.UUID, search_term: str,
                             skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Search invoices within a business by title, description, or invoice number."""
        pass
    
    @abstractmethod
    async def get_by_currency(self, business_id: uuid.UUID, currency: CurrencyCode,
                             skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices by currency within a business."""
        pass
    
    @abstractmethod
    async def update(self, invoice: Invoice) -> Invoice:
        """Update an existing invoice."""
        pass
    
    @abstractmethod
    async def delete(self, invoice_id: uuid.UUID) -> bool:
        """Delete an invoice by ID."""
        pass
    
    @abstractmethod
    async def bulk_update_status(self, business_id: uuid.UUID, invoice_ids: List[uuid.UUID],
                                status: InvoiceStatus) -> int:
        """Bulk update invoice status."""
        pass
    
    @abstractmethod
    async def bulk_assign_invoices(self, business_id: uuid.UUID, invoice_ids: List[uuid.UUID],
                                  user_id: str) -> int:
        """Bulk assign invoices to a user."""
        pass
    
    @abstractmethod
    async def bulk_mark_overdue(self, business_id: uuid.UUID, invoice_ids: List[uuid.UUID]) -> int:
        """Bulk mark invoices as overdue."""
        pass
    
    @abstractmethod
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Count total invoices for a business."""
        pass
    
    @abstractmethod
    async def count_by_status(self, business_id: uuid.UUID, status: InvoiceStatus) -> int:
        """Count invoices by status within a business."""
        pass
    
    @abstractmethod
    async def count_by_contact(self, contact_id: uuid.UUID) -> int:
        """Count invoices for a specific contact."""
        pass
    
    @abstractmethod
    async def get_invoice_statistics(self, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive invoice statistics for a business."""
        pass
    
    @abstractmethod
    async def get_payment_analytics(self, business_id: uuid.UUID, start_date: datetime,
                                   end_date: datetime) -> Dict[str, Any]:
        """Get payment analytics for a period."""
        pass
    
    @abstractmethod
    async def get_revenue_analytics(self, business_id: uuid.UUID, start_date: datetime,
                                   end_date: datetime) -> Dict[str, Any]:
        """Get revenue analytics for a period."""
        pass
    
    @abstractmethod
    async def get_outstanding_balance(self, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get outstanding balance summary for a business."""
        pass
    
    @abstractmethod
    async def exists(self, invoice_id: uuid.UUID) -> bool:
        """Check if an invoice exists."""
        pass
    
    @abstractmethod
    async def has_duplicate_invoice_number(self, business_id: uuid.UUID, invoice_number: str,
                                          exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if invoice number already exists within business."""
        pass
    
    @abstractmethod
    async def get_next_invoice_number(self, business_id: uuid.UUID, prefix: str = "INV") -> str:
        """Generate next available invoice number for a business."""
        pass
    
    @abstractmethod
    async def get_user_workload(self, business_id: uuid.UUID, user_id: str) -> Dict[str, Any]:
        """Get invoice workload statistics for a user."""
        pass
    
    @abstractmethod
    async def get_monthly_revenue(self, business_id: uuid.UUID, year: int, month: int) -> Dict[str, Any]:
        """Get monthly revenue statistics."""
        pass
    
    @abstractmethod
    async def get_top_clients_by_revenue(self, business_id: uuid.UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top clients by total revenue."""
        pass
    
    @abstractmethod
    async def get_aging_report(self, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get accounts receivable aging report."""
        pass
    
    @abstractmethod
    async def get_payment_history(self, invoice_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get payment history for a specific invoice."""
        pass
    
    @abstractmethod
    async def get_refund_history(self, invoice_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get refund history for a specific invoice."""
        pass 