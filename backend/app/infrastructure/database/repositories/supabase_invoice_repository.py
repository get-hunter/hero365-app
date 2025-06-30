"""
Supabase Invoice Repository Implementation

Repository implementation using Supabase client SDK for invoice management operations.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal
import json

from supabase import Client

from app.domain.repositories.invoice_repository import InvoiceRepository
from app.domain.entities.invoice import (
    Invoice, InvoiceLineItem, Payment, PaymentTerms, 
    InvoiceEmailTracking, InvoiceStatusHistoryEntry
)
from app.domain.enums import (
    InvoiceStatus, PaymentStatus, PaymentMethod, CurrencyCode, 
    TaxType, DiscountType, EmailStatus
)
from app.domain.value_objects.address import Address
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, DatabaseError
)

logger = logging.getLogger(__name__)

class SupabaseInvoiceRepository(InvoiceRepository):
    """Supabase implementation of InvoiceRepository."""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "invoices"
    
    async def create(self, invoice: Invoice) -> Invoice:
        """Create a new invoice in Supabase."""
        try:
            invoice_data = self._invoice_to_dict(invoice)
            response = self.client.table(self.table_name).insert(invoice_data).execute()
            
            if response.data:
                return self._dict_to_invoice(response.data[0])
            else:
                raise DatabaseError("Failed to create invoice")
                
        except Exception as e:
            if "duplicate key" in str(e).lower():
                raise DuplicateEntityError(f"Invoice with number '{invoice.invoice_number}' already exists")
            raise DatabaseError(f"Failed to create invoice: {str(e)}")
    
    async def get_by_id(self, invoice_id: uuid.UUID) -> Optional[Invoice]:
        """Get invoice by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", str(invoice_id)).execute()
            
            if response.data:
                return self._dict_to_invoice(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invoice by ID: {str(e)}")
    
    async def get_by_invoice_number(self, business_id: uuid.UUID, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("invoice_number", invoice_number).execute()
            
            if response.data:
                return self._dict_to_invoice(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invoice by number: {str(e)}")
    
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices by business ID with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by business: {str(e)}")
    
    async def get_by_contact_id(self, contact_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices by contact ID with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "contact_id", str(contact_id)
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by contact: {str(e)}")
    
    async def get_by_project_id(self, project_id: uuid.UUID, business_id: uuid.UUID,
                               skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices associated with a specific project."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "project_id", str(project_id)
            ).eq("business_id", str(business_id)).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by project: {str(e)}")
    
    async def get_by_job_id(self, job_id: uuid.UUID, business_id: uuid.UUID,
                           skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices associated with a specific job."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "job_id", str(job_id)
            ).eq("business_id", str(business_id)).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by job: {str(e)}")
    
    async def get_by_estimate_id(self, estimate_id: uuid.UUID, business_id: uuid.UUID,
                                skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices converted from a specific estimate."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "estimate_id", str(estimate_id)
            ).eq("business_id", str(business_id)).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by estimate: {str(e)}")
    
    async def get_by_status(self, business_id: uuid.UUID, status: InvoiceStatus,
                           skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices by status within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", status.value).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by status: {str(e)}")
    
    async def get_overdue_invoices(self, business_id: uuid.UUID,
                                  skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get overdue invoices within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", InvoiceStatus.OVERDUE.value).range(
                skip, skip + limit - 1
            ).order("due_date", desc=False).execute()
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get overdue invoices: {str(e)}")
    
    async def update(self, invoice: Invoice) -> Invoice:
        """Update an existing invoice."""
        try:
            invoice_data = self._invoice_to_dict(invoice)
            invoice_data["last_modified"] = datetime.utcnow().isoformat()
            
            response = self.client.table(self.table_name).update(invoice_data).eq(
                "id", str(invoice.id)
            ).execute()
            
            if response.data:
                return self._dict_to_invoice(response.data[0])
            else:
                raise EntityNotFoundError(f"Invoice with ID {invoice.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update invoice: {str(e)}")
    
    async def delete(self, invoice_id: uuid.UUID) -> bool:
        """Delete an invoice by ID."""
        try:
            response = self.client.table(self.table_name).delete().eq("id", str(invoice_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete invoice: {str(e)}")
    
    def _invoice_to_dict(self, invoice: Invoice) -> dict:
        """Convert Invoice entity to database dictionary."""
        return {
            "id": str(invoice.id),
            "business_id": str(invoice.business_id),
            "invoice_number": invoice.invoice_number,
            "status": invoice.status.value,
            "client_id": str(invoice.client_id) if invoice.client_id else None,
            "client_name": invoice.client_name,
            "client_email": invoice.client_email,
            "client_phone": invoice.client_phone,
            "client_address": invoice.client_address.to_dict() if invoice.client_address else None,
            "title": invoice.title,
            "description": invoice.description,
            "line_items": [self._line_item_to_dict(item) for item in invoice.line_items],
            "currency": invoice.currency.value,
            "tax_rate": float(invoice.tax_rate),
            "tax_type": invoice.tax_type.value,
            "overall_discount_type": invoice.overall_discount_type.value,
            "overall_discount_value": float(invoice.overall_discount_value),
            "payments": [self._payment_to_dict(payment) for payment in invoice.payments],
            "payment_terms": self._payment_terms_to_dict(invoice.payment_terms),
            "template_id": str(invoice.template_id) if invoice.template_id else None,
            "template_data": invoice.template_data,
            "estimate_id": str(invoice.estimate_id) if invoice.estimate_id else None,
            "project_id": str(invoice.project_id) if invoice.project_id else None,
            "job_id": str(invoice.job_id) if invoice.job_id else None,
            "contact_id": str(invoice.contact_id) if invoice.contact_id else None,
            "tags": invoice.tags,
            "custom_fields": invoice.custom_fields,
            "internal_notes": invoice.internal_notes,
            "created_by": invoice.created_by,
            "created_date": invoice.created_date.isoformat(),
            "last_modified": invoice.last_modified.isoformat(),
            "sent_date": invoice.sent_date.isoformat() if invoice.sent_date else None,
            "viewed_date": invoice.viewed_date.isoformat() if invoice.viewed_date else None,
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "paid_date": invoice.paid_date.isoformat() if invoice.paid_date else None,
            # Calculated fields for database storage
            "line_items_subtotal": float(invoice.get_line_items_subtotal()),
            "total_discount": float(invoice.get_line_items_discount_total() + invoice.get_overall_discount_amount()),
            "tax_amount": float(invoice.get_tax_amount()),
            "total_amount": float(invoice.get_total_amount()),
            "total_payments": float(invoice.get_total_payments()),
            "balance_due": float(invoice.get_balance_due()),
            "is_paid": invoice.is_paid(),
            "is_overdue": invoice.is_overdue()
        }
    
    def _line_item_to_dict(self, line_item: InvoiceLineItem) -> dict:
        """Convert InvoiceLineItem to dictionary."""
        return {
            "id": str(line_item.id),
            "description": line_item.description,
            "quantity": float(line_item.quantity),
            "unit_price": float(line_item.unit_price),
            "unit": line_item.unit,
            "category": line_item.category,
            "discount_type": line_item.discount_type.value,
            "discount_value": float(line_item.discount_value),
            "tax_rate": float(line_item.tax_rate),
            "notes": line_item.notes
        }
    
    def _payment_to_dict(self, payment: Payment) -> dict:
        """Convert Payment to dictionary."""
        return {
            "id": str(payment.id),
            "amount": float(payment.amount),
            "payment_date": payment.payment_date.isoformat(),
            "payment_method": payment.payment_method.value,
            "status": payment.status.value,
            "reference": payment.reference,
            "transaction_id": payment.transaction_id,
            "notes": payment.notes,
            "processed_by": payment.processed_by,
            "refunded_amount": float(payment.refunded_amount),
            "refund_date": payment.refund_date.isoformat() if payment.refund_date else None,
            "refund_reason": payment.refund_reason
        }
    
    def _payment_terms_to_dict(self, payment_terms: PaymentTerms) -> dict:
        """Convert PaymentTerms to dictionary."""
        return {
            "net_days": payment_terms.net_days,
            "discount_percentage": float(payment_terms.discount_percentage),
            "discount_days": payment_terms.discount_days,
            "late_fee_percentage": float(payment_terms.late_fee_percentage),
            "late_fee_grace_days": payment_terms.late_fee_grace_days,
            "payment_instructions": payment_terms.payment_instructions
        }
    
    def _dict_to_invoice(self, data: dict) -> Invoice:
        """Convert database dictionary to Invoice entity."""
        
        def safe_json_parse(value, default=None):
            if value is None:
                return default if default is not None else []
            if isinstance(value, (list, dict)):
                return value
            try:
                return json.loads(value) if isinstance(value, str) else value
            except (json.JSONDecodeError, TypeError):
                return default if default is not None else []
        
        def safe_uuid_parse(value):
            if value is None:
                return None
            try:
                return uuid.UUID(value)
            except (ValueError, TypeError):
                return None
        
        def safe_datetime_parse(value):
            if value is None:
                return None
            try:
                if isinstance(value, str):
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                return value
            except (ValueError, TypeError):
                return None
        
        def safe_date_parse(value):
            if value is None:
                return None
            try:
                if isinstance(value, str):
                    return date.fromisoformat(value)
                return value
            except (ValueError, TypeError):
                return None
        
        # Parse line items
        line_items_data = safe_json_parse(data.get("line_items", []))
        line_items = []
        for item_data in line_items_data:
            try:
                line_item = InvoiceLineItem(
                    id=uuid.UUID(item_data["id"]),
                    description=item_data.get("description", ""),
                    quantity=Decimal(str(item_data.get("quantity", "1"))),
                    unit_price=Decimal(str(item_data.get("unit_price", "0"))),
                    unit=item_data.get("unit"),
                    category=item_data.get("category"),
                    discount_type=DiscountType(item_data.get("discount_type", "none")),
                    discount_value=Decimal(str(item_data.get("discount_value", "0"))),
                    tax_rate=Decimal(str(item_data.get("tax_rate", "0"))),
                    notes=item_data.get("notes")
                )
                line_items.append(line_item)
            except Exception as e:
                logger.warning(f"Failed to parse line item: {e}")
                continue
        
        # Parse payments
        payments_data = safe_json_parse(data.get("payments", []))
        payments = []
        for payment_data in payments_data:
            try:
                payment = Payment(
                    id=uuid.UUID(payment_data["id"]),
                    amount=Decimal(str(payment_data.get("amount", "0"))),
                    payment_date=safe_datetime_parse(payment_data.get("payment_date")),
                    payment_method=PaymentMethod(payment_data.get("payment_method", "cash")),
                    status=PaymentStatus(payment_data.get("status", "completed")),
                    reference=payment_data.get("reference"),
                    transaction_id=payment_data.get("transaction_id"),
                    notes=payment_data.get("notes"),
                    processed_by=payment_data.get("processed_by"),
                    refunded_amount=Decimal(str(payment_data.get("refunded_amount", "0"))),
                    refund_date=safe_datetime_parse(payment_data.get("refund_date")),
                    refund_reason=payment_data.get("refund_reason")
                )
                payments.append(payment)
            except Exception as e:
                logger.warning(f"Failed to parse payment: {e}")
                continue
        
        # Parse payment terms
        payment_terms_data = safe_json_parse(data.get("payment_terms", {}), {})
        payment_terms = PaymentTerms(
            net_days=payment_terms_data.get("net_days", 30),
            discount_percentage=Decimal(str(payment_terms_data.get("discount_percentage", "0"))),
            discount_days=payment_terms_data.get("discount_days", 0),
            late_fee_percentage=Decimal(str(payment_terms_data.get("late_fee_percentage", "0"))),
            late_fee_grace_days=payment_terms_data.get("late_fee_grace_days", 0),
            payment_instructions=payment_terms_data.get("payment_instructions")
        )
        
        return Invoice(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            invoice_number=data.get("invoice_number"),
            status=InvoiceStatus(data.get("status", "draft")),
            client_id=safe_uuid_parse(data.get("client_id")),
            client_name=data.get("client_name"),
            client_email=data.get("client_email"),
            client_phone=data.get("client_phone"),
            title=data.get("title", ""),
            description=data.get("description"),
            line_items=line_items,
            currency=CurrencyCode(data.get("currency", "USD")),
            tax_rate=Decimal(str(data.get("tax_rate", "0"))),
            tax_type=TaxType(data.get("tax_type", "percentage")),
            overall_discount_type=DiscountType(data.get("overall_discount_type", "none")),
            overall_discount_value=Decimal(str(data.get("overall_discount_value", "0"))),
            payments=payments,
            payment_terms=payment_terms,
            template_id=safe_uuid_parse(data.get("template_id")),
            template_data=safe_json_parse(data.get("template_data", {}), {}),
            estimate_id=safe_uuid_parse(data.get("estimate_id")),
            project_id=safe_uuid_parse(data.get("project_id")),
            job_id=safe_uuid_parse(data.get("job_id")),
            contact_id=safe_uuid_parse(data.get("contact_id")),
            tags=safe_json_parse(data.get("tags", [])),
            custom_fields=safe_json_parse(data.get("custom_fields", {}), {}),
            internal_notes=data.get("internal_notes"),
            created_by=data.get("created_by"),
            created_date=safe_datetime_parse(data["created_date"]) or datetime.now(),
            last_modified=safe_datetime_parse(data["last_modified"]) or datetime.now(),
            sent_date=safe_datetime_parse(data.get("sent_date")),
            viewed_date=safe_datetime_parse(data.get("viewed_date")),
            due_date=safe_date_parse(data.get("due_date")),
            paid_date=safe_datetime_parse(data.get("paid_date"))
        )

    # Implement remaining required methods with basic implementations
    async def get_by_assigned_user(self, business_id: uuid.UUID, user_id: str, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).eq("created_by", user_id).range(skip, skip + limit - 1).execute()
            return [self._dict_to_invoice(data) for data in response.data]
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by assigned user: {str(e)}")

    async def get_by_template_id(self, business_id: uuid.UUID, template_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).eq("template_id", str(template_id)).range(skip, skip + limit - 1).execute()
            return [self._dict_to_invoice(data) for data in response.data]
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by template: {str(e)}")

    async def get_by_date_range(self, business_id: uuid.UUID, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).gte("created_date", start_date.isoformat()).lte("created_date", end_date.isoformat()).range(skip, skip + limit - 1).execute()
            return [self._dict_to_invoice(data) for data in response.data]
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by date range: {str(e)}")

    async def get_due_soon(self, business_id: uuid.UUID, days: int = 7, skip: int = 0, limit: int = 100) -> List[Invoice]:
        # Placeholder implementation
        return []

    async def get_unpaid_invoices(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).eq("is_paid", False).range(skip, skip + limit - 1).execute()
            return [self._dict_to_invoice(data) for data in response.data]
        except Exception as e:
            raise DatabaseError(f"Failed to get unpaid invoices: {str(e)}")

    async def get_partially_paid_invoices(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).eq("status", InvoiceStatus.PARTIALLY_PAID.value).range(skip, skip + limit - 1).execute()
            return [self._dict_to_invoice(data) for data in response.data]
        except Exception as e:
            raise DatabaseError(f"Failed to get partially paid invoices: {str(e)}")

    async def get_by_payment_method(self, business_id: uuid.UUID, payment_method: PaymentMethod, skip: int = 0, limit: int = 100) -> List[Invoice]:
        # Complex query - placeholder implementation
        return []

    async def get_by_value_range(self, business_id: uuid.UUID, min_value: Decimal, max_value: Decimal, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).gte("total_amount", float(min_value)).lte("total_amount", float(max_value)).range(skip, skip + limit - 1).execute()
            return [self._dict_to_invoice(data) for data in response.data]
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by value range: {str(e)}")

    async def search_invoices(self, business_id: uuid.UUID, search_term: str, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).or_(f"title.ilike.%{search_term}%,description.ilike.%{search_term}%,invoice_number.ilike.%{search_term}%").range(skip, skip + limit - 1).execute()
            return [self._dict_to_invoice(data) for data in response.data]
        except Exception as e:
            raise DatabaseError(f"Failed to search invoices: {str(e)}")

    async def get_by_currency(self, business_id: uuid.UUID, currency: CurrencyCode, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).eq("currency", currency.value).range(skip, skip + limit - 1).execute()
            return [self._dict_to_invoice(data) for data in response.data]
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by currency: {str(e)}")

    async def bulk_update_status(self, business_id: uuid.UUID, invoice_ids: List[uuid.UUID], status: InvoiceStatus) -> int:
        return 0  # Placeholder

    async def bulk_assign_invoices(self, business_id: uuid.UUID, invoice_ids: List[uuid.UUID], user_id: str) -> int:
        return 0  # Placeholder

    async def bulk_mark_overdue(self, business_id: uuid.UUID, invoice_ids: List[uuid.UUID]) -> int:
        return 0  # Placeholder

    async def count_by_business(self, business_id: uuid.UUID) -> int:
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("business_id", str(business_id)).execute()
            return response.count or 0
        except Exception as e:
            raise DatabaseError(f"Failed to count invoices by business: {str(e)}")

    async def count_by_status(self, business_id: uuid.UUID, status: InvoiceStatus) -> int:
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("business_id", str(business_id)).eq("status", status.value).execute()
            return response.count or 0
        except Exception as e:
            raise DatabaseError(f"Failed to count invoices by status: {str(e)}")

    async def count_by_contact(self, contact_id: uuid.UUID) -> int:
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq("contact_id", str(contact_id)).execute()
            return response.count or 0
        except Exception as e:
            raise DatabaseError(f"Failed to count invoices by contact: {str(e)}")



    async def exists(self, invoice_id: uuid.UUID) -> bool:
        try:
            response = self.client.table(self.table_name).select("id").eq("id", str(invoice_id)).execute()
            return len(response.data) > 0
        except Exception as e:
            raise DatabaseError(f"Failed to check invoice existence: {str(e)}")

    async def has_duplicate_invoice_number(self, business_id: uuid.UUID, invoice_number: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
        try:
            query = self.client.table(self.table_name).select("id").eq("business_id", str(business_id)).eq("invoice_number", invoice_number)
            if exclude_id:
                query = query.neq("id", str(exclude_id))
            response = query.execute()
            return len(response.data) > 0
        except Exception as e:
            raise DatabaseError(f"Failed to check duplicate invoice number: {str(e)}")

    async def get_next_invoice_number(self, business_id: uuid.UUID, prefix: str = "INV") -> str:
        today = date.today()
        return f"{prefix}-{today.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"



    async def get_payment_history(self, invoice_id: uuid.UUID) -> List[Dict[str, Any]]:
        return []  # Placeholder

    async def get_refund_history(self, invoice_id: uuid.UUID) -> List[Dict[str, Any]]:
        return []  # Placeholder



    async def list_with_pagination(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[Invoice], int]:
        """List invoices with pagination and filters."""
        try:
            # Build the base query with count
            query = self.client.table(self.table_name).select("*", count="exact").eq("business_id", str(business_id))
            
            # Apply filters if provided
            if filters:
                if "status" in filters:
                    query = query.eq("status", filters["status"].value if hasattr(filters["status"], 'value') else filters["status"])
                if "contact_id" in filters:
                    query = query.eq("contact_id", str(filters["contact_id"]))
                if "project_id" in filters:
                    query = query.eq("project_id", str(filters["project_id"]))
                if "job_id" in filters:
                    query = query.eq("job_id", str(filters["job_id"]))
                if "overdue_only" in filters and filters["overdue_only"]:
                    query = query.eq("status", InvoiceStatus.OVERDUE.value)
            
            # Add pagination and ordering
            query = query.range(skip, skip + limit - 1).order("created_date", desc=True)
            
            # Execute the query
            response = query.execute()
            
            # Convert the data to Invoice entities
            invoices = [self._dict_to_invoice(invoice_data) for invoice_data in response.data]
            total_count = response.count or 0
            
            return invoices, total_count
            
        except Exception as e:
            raise DatabaseError(f"Failed to list invoices with pagination: {str(e)}") 