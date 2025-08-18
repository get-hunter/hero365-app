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
from app.domain.entities.invoice_enums.enums import InvoiceStatus, PaymentStatus
from app.domain.shared.enums import PaymentMethod, CurrencyCode, TaxType, DiscountType
from app.domain.entities.estimate_enums.enums import EmailStatus
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
        """Get invoice by ID with line items and payments."""
        try:
            # Fetch main invoice record
            response = self.client.table(self.table_name).select("*").eq("id", str(invoice_id)).execute()
            
            if not response.data:
                return None
            
            # Fetch line items for this invoice
            line_items_response = self.client.table("invoice_line_items").select("*").eq(
                "invoice_id", str(invoice_id)
            ).order("sort_order").execute()
            
            # Fetch payments for this invoice
            payments_response = self.client.table("payments").select("*").eq(
                "invoice_id", str(invoice_id)
            ).order("payment_date").execute()
            
            # Enrich invoice data with line items and payments
            invoice_data = response.data[0]
            invoice_data["_line_items"] = line_items_response.data
            invoice_data["_payments"] = payments_response.data
            
            return self._dict_to_invoice(invoice_data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invoice by ID: {str(e)}")
    
    async def get_by_invoice_number(self, business_id: uuid.UUID, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number within a business."""
        try:
            # Fetch main invoice record
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("invoice_number", invoice_number).execute()
            
            if not response.data:
                return None
            
            invoice_id = response.data[0]["id"]
            
            # Fetch line items for this invoice
            line_items_response = self.client.table("invoice_line_items").select("*").eq(
                "invoice_id", invoice_id
            ).order("sort_order").execute()
            
            # Fetch payments for this invoice
            payments_response = self.client.table("payments").select("*").eq(
                "invoice_id", invoice_id
            ).order("payment_date").execute()
            
            # Enrich invoice data with line items and payments
            invoice_data = response.data[0]
            invoice_data["_line_items"] = line_items_response.data
            invoice_data["_payments"] = payments_response.data
            
            return self._dict_to_invoice(invoice_data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invoice by number: {str(e)}")
    
    async def _enrich_invoices_with_details(self, invoice_data_list: List[dict]) -> List[dict]:
        """
        Efficiently fetch and attach line items and payments to invoice data.
        
        Args:
            invoice_data_list: List of invoice dictionaries from database
            
        Returns:
            List of enriched invoice dictionaries with line_items and payments
        """
        if not invoice_data_list:
            return invoice_data_list
        
        # Extract all invoice IDs for bulk fetching
        invoice_ids = [invoice_data["id"] for invoice_data in invoice_data_list]
        
        # Bulk fetch line items for all invoices in one query
        line_items_response = self.client.table("invoice_line_items").select("*").in_("invoice_id", invoice_ids).order("invoice_id").order("sort_order").execute()
        
        # Bulk fetch payments for all invoices in one query  
        payments_response = self.client.table("payments").select("*").in_("invoice_id", invoice_ids).order("invoice_id").order("payment_date").execute()
        
        # Group line items by invoice_id
        line_items_by_invoice = {}
        for line_item in line_items_response.data:
            invoice_id = line_item["invoice_id"]
            if invoice_id not in line_items_by_invoice:
                line_items_by_invoice[invoice_id] = []
            line_items_by_invoice[invoice_id].append(line_item)
        
        # Group payments by invoice_id
        payments_by_invoice = {}
        for payment in payments_response.data:
            invoice_id = payment["invoice_id"]
            if invoice_id not in payments_by_invoice:
                payments_by_invoice[invoice_id] = []
            payments_by_invoice[invoice_id].append(payment)
        
        # Attach line items and payments to their respective invoices
        for invoice_data in invoice_data_list:
            invoice_id = invoice_data["id"]
            invoice_data["line_items"] = line_items_by_invoice.get(invoice_id, [])
            invoice_data["payments"] = payments_by_invoice.get(invoice_id, [])
        
        return invoice_data_list

    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices by business ID with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in enriched_data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by business: {str(e)}")
    
    async def get_by_contact_id(self, contact_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices by contact ID with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "contact_id", str(contact_id)
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in enriched_data]
            
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
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in enriched_data]
            
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
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in enriched_data]
            
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
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in enriched_data]
            
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
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in enriched_data]
            
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
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(invoice_data) for invoice_data in enriched_data]
            
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
                # After update, fetch the complete invoice with line items and payments
                # like we do in get_by_id
                invoice_id = invoice.id
                
                # Fetch line items for this invoice
                line_items_response = self.client.table("invoice_line_items").select("*").eq(
                    "invoice_id", str(invoice_id)
                ).order("sort_order").execute()
                
                # Fetch payments for this invoice
                payments_response = self.client.table("payments").select("*").eq(
                    "invoice_id", str(invoice_id)
                ).order("payment_date").execute()
                
                # Enrich invoice data with line items and payments
                updated_invoice_data = response.data[0]
                updated_invoice_data["_line_items"] = line_items_response.data
                updated_invoice_data["_payments"] = payments_response.data
                
                return self._dict_to_invoice(updated_invoice_data)
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
        """Convert Invoice entity to database dictionary - only fields that exist in DB schema."""
        def get_enum_value(field_value):
            """Helper to safely get enum value (handles both string and enum types)."""
            return field_value.value if hasattr(field_value, 'value') else field_value
        
        return {
            # Core fields that exist in DB schema
            "id": str(invoice.id),
            "business_id": str(invoice.business_id),
            "invoice_number": invoice.invoice_number,
            "title": invoice.title,
            "description": invoice.description,
            "status": get_enum_value(invoice.status),
            "contact_id": str(invoice.contact_id) if invoice.contact_id else None,  # DB uses contact_id, not client_id
            "project_id": str(invoice.project_id) if invoice.project_id else None,
            "job_id": str(invoice.job_id) if invoice.job_id else None,
            "estimate_id": str(invoice.estimate_id) if invoice.estimate_id else None,
            "template_id": str(invoice.template_id) if invoice.template_id else None,
            "currency": get_enum_value(invoice.currency),
            "subtotal": float(invoice.get_line_items_subtotal()),
            "discount_type": get_enum_value(invoice.overall_discount_type),
            "discount_value": float(invoice.overall_discount_value),
            "discount_amount": float(invoice.get_overall_discount_amount()),
            "tax_type": get_enum_value(invoice.tax_type),
            "tax_rate": float(invoice.tax_rate),
            "tax_amount": float(invoice.get_tax_amount()),
            "total_amount": float(invoice.get_total_amount()),
            "amount_paid": float(invoice.get_total_payments()),
            "amount_due": float(invoice.get_balance_due()),
            "issue_date": invoice.issue_date.isoformat() if invoice.issue_date else None,
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "payment_terms": f"Net {invoice.payment_terms.net_days}" if invoice.payment_terms else None,
            "late_fee_percentage": float(invoice.payment_terms.late_fee_percentage) if invoice.payment_terms else 0.0,
            "late_fee_amount": 0.0,  # No late fees applied during template updates
            "late_fee_applied": False,
            "payment_instructions": invoice.payment_terms.payment_instructions if invoice.payment_terms else None,
            "notes": invoice.internal_notes,
            "created_by": invoice.created_by,
            "created_date": invoice.created_date.isoformat(),
            "last_modified": invoice.last_modified.isoformat()
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
            "discount_type": line_item.discount_type.value if hasattr(line_item.discount_type, 'value') else line_item.discount_type,
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
            "payment_method": payment.payment_method.value if hasattr(payment.payment_method, 'value') else payment.payment_method,
            "status": payment.status.value if hasattr(payment.status, 'value') else payment.status,
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
                return default
            if isinstance(value, (dict, list)):
                return value
            try:
                return json.loads(value) if isinstance(value, str) else value
            except (json.JSONDecodeError, TypeError):
                return default

        def safe_uuid_parse(value):
            if value is None:
                return None
            try:
                return uuid.UUID(str(value))
            except (ValueError, TypeError):
                return None

        def safe_datetime_parse(value):
            if value is None:
                return None
            try:
                if isinstance(value, datetime):
                    return value
                return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
            except (ValueError, TypeError):
                return None

        def safe_date_parse(value):
            if value is None:
                return None
            try:
                if isinstance(value, date):
                    return value
                return datetime.fromisoformat(str(value)).date()
            except (ValueError, TypeError):
                return None

        # Parse line items (from separate table or JSON field)
        line_items_data = data.get("_line_items", data.get("line_items", []))
        # If it's a string, try to parse as JSON (backward compatibility)
        if isinstance(line_items_data, str):
            line_items_data = safe_json_parse(line_items_data, [])
        
        line_items = []
        for item_data in line_items_data:
            try:
                line_item = InvoiceLineItem(
                    id=safe_uuid_parse(item_data.get("id")) or uuid.uuid4(),
                    description=item_data.get("name") or item_data.get("description", ""),  # DB uses 'name' field
                    quantity=Decimal(str(item_data.get("quantity", "1"))),
                    unit_price=Decimal(str(item_data.get("unit_price", "0"))),
                    unit=item_data.get("unit"),
                    category=item_data.get("category"),  # May not exist in DB, will be None
                    discount_type=DiscountType(item_data.get("discount_type", "none")),
                    discount_value=Decimal(str(item_data.get("discount_value", "0"))),
                    tax_rate=Decimal(str(item_data.get("tax_rate", "0"))),
                    notes=item_data.get("notes")
                )
                line_items.append(line_item)
            except Exception as e:
                # Skip invalid line items but log the error
                print(f"Warning: Skipping invalid line item: {e}")
                continue

        # Parse payments (from separate table or JSON field)
        payments_data = data.get("_payments", data.get("payments", []))
        # If it's a string, try to parse as JSON (backward compatibility)
        if isinstance(payments_data, str):
            payments_data = safe_json_parse(payments_data, [])
        
        payments = []
        for payment_data in payments_data:
            try:
                payment = Payment(
                    id=safe_uuid_parse(payment_data.get("id")) or uuid.uuid4(),
                    amount=Decimal(str(payment_data.get("amount", "0"))),
                    payment_date=safe_datetime_parse(payment_data.get("payment_date")) or datetime.now(),
                    payment_method=PaymentMethod(payment_data.get("payment_method", "cash")),
                    status=PaymentStatus(payment_data.get("payment_status") or payment_data.get("status", "completed")),
                    reference=payment_data.get("reference_number") or payment_data.get("reference"),
                    transaction_id=payment_data.get("transaction_id"),
                    notes=payment_data.get("notes"),
                    processed_by=payment_data.get("created_by") or payment_data.get("processed_by"),
                    refunded_amount=Decimal(str(payment_data.get("refund_amount", "0")))
                )
                payments.append(payment)
            except Exception as e:
                # Skip invalid payments but log the error
                print(f"Warning: Skipping invalid payment: {e}")
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
        
        # Handle client_name - fetch from contact if missing
        client_name = data.get("client_name")
        contact_id = safe_uuid_parse(data.get("contact_id"))
        
        # If client_name is missing but contact_id is present, fetch contact details
        if not client_name and contact_id:
            try:
                contact_response = self.client.table("contacts").select("first_name, last_name, company_name").eq("id", str(contact_id)).execute()
                if contact_response.data:
                    contact = contact_response.data[0]
                    first_name = contact.get("first_name", "")
                    last_name = contact.get("last_name", "")
                    company_name = contact.get("company_name", "")
                    
                    if company_name:
                        client_name = company_name
                    elif first_name or last_name:
                        client_name = f"{first_name} {last_name}".strip()
                    else:
                        client_name = "Unknown Client"
            except Exception as e:
                # If contact fetch fails, use a default
                print(f"Warning: Could not fetch contact details for invoice: {e}")
                client_name = "Unknown Client"
        
        # Parse client address
        client_address = None
        if data.get("client_address"):
            try:
                address_data = safe_json_parse(data["client_address"])
                if address_data:
                    from app.domain.value_objects.address import Address
                    # Handle both legacy and new address formats
                    street_address = address_data.get("street_address") or address_data.get("street", "")
                    
                    client_address = Address(
                        street_address=street_address,
                        city=address_data.get("city", ""),
                        state=address_data.get("state", ""),
                        postal_code=address_data.get("postal_code", ""),
                        country=address_data.get("country", "US")
                    )
            except Exception as e:
                print(f"Warning: Failed to parse client address: {e}")
        
        return Invoice(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            invoice_number=data.get("invoice_number"),
            status=InvoiceStatus(data.get("status", "draft")),
            client_id=safe_uuid_parse(data.get("client_id")),
            client_name=client_name,
            client_email=data.get("client_email"),
            client_phone=data.get("client_phone"),
            client_address=client_address,
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
            contact_id=contact_id,
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
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(data) for data in enriched_data]
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by assigned user: {str(e)}")

    async def get_by_template_id(self, business_id: uuid.UUID, template_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).eq("template_id", str(template_id)).range(skip, skip + limit - 1).execute()
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(data) for data in enriched_data]
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by template: {str(e)}")

    async def get_by_date_range(self, business_id: uuid.UUID, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).gte("created_date", start_date.isoformat()).lte("created_date", end_date.isoformat()).range(skip, skip + limit - 1).execute()
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(data) for data in enriched_data]
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by date range: {str(e)}")

    async def get_due_soon(self, business_id: uuid.UUID, days: int = 7, skip: int = 0, limit: int = 100) -> List[Invoice]:
        # Placeholder implementation
        return []

    async def get_unpaid_invoices(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).eq("is_paid", False).range(skip, skip + limit - 1).execute()
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(data) for data in enriched_data]
        except Exception as e:
            raise DatabaseError(f"Failed to get unpaid invoices: {str(e)}")

    async def get_partially_paid_invoices(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).eq("status", InvoiceStatus.PARTIALLY_PAID.value).range(skip, skip + limit - 1).execute()
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(data) for data in enriched_data]
        except Exception as e:
            raise DatabaseError(f"Failed to get partially paid invoices: {str(e)}")

    async def get_by_payment_method(self, business_id: uuid.UUID, payment_method: PaymentMethod, skip: int = 0, limit: int = 100) -> List[Invoice]:
        # Complex query - placeholder implementation
        return []

    async def get_by_value_range(self, business_id: uuid.UUID, min_value: Decimal, max_value: Decimal, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).gte("total_amount", float(min_value)).lte("total_amount", float(max_value)).range(skip, skip + limit - 1).execute()
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(data) for data in enriched_data]
        except Exception as e:
            raise DatabaseError(f"Failed to get invoices by value range: {str(e)}")

    async def search_invoices(self, business_id: uuid.UUID, search_term: str, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).or_(f"title.ilike.%{search_term}%,description.ilike.%{search_term}%,invoice_number.ilike.%{search_term}%").range(skip, skip + limit - 1).execute()
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(data) for data in enriched_data]
        except Exception as e:
            raise DatabaseError(f"Failed to search invoices: {str(e)}")

    async def get_by_currency(self, business_id: uuid.UUID, currency: CurrencyCode, skip: int = 0, limit: int = 100) -> List[Invoice]:
        try:
            response = self.client.table(self.table_name).select("*").eq("business_id", str(business_id)).eq("currency", currency.value).range(skip, skip + limit - 1).execute()
            
            # Enrich with line items and payments
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            return [self._dict_to_invoice(data) for data in enriched_data]
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
        """Generate next invoice number for a business using database function."""
        try:
            response = self.client.rpc("get_next_invoice_number", {
                "business_uuid": str(business_id),
                "prefix": prefix
            }).execute()
            
            if response.data:
                return response.data
            else:
                # Fallback to simple sequential number
                return f"{prefix}-000001"
                
        except Exception as e:
            # Log the error but don't fail - use fallback
            logger.warning(f"Failed to get next invoice number from database: {str(e)}")
            return f"{prefix}-000001"

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
            
            # Early return if no invoices found
            if not response.data:
                return [], 0
            
            # Enrich with line items and payments using helper method
            enriched_data = await self._enrich_invoices_with_details(response.data)
            
            # Convert the enriched data to Invoice entities
            invoices = [self._dict_to_invoice(invoice_data) for invoice_data in enriched_data]
            total_count = response.count or 0
            
            return invoices, total_count
            
        except Exception as e:
            raise DatabaseError(f"Failed to list invoices with pagination: {str(e)}") 