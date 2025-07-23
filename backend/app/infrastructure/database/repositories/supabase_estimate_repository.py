"""
Supabase Estimate Repository Implementation

Repository implementation using Supabase client SDK for estimate management operations.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

from supabase import Client

from app.domain.repositories.estimate_repository import EstimateRepository
from app.domain.entities.estimate import (
    Estimate, EstimateLineItem, AdvancePayment, EstimateTerms, 
    EmailTracking, StatusHistoryEntry
)
from app.domain.entities.estimate_enums.enums import EstimateStatus, DocumentType, EmailStatus
from app.domain.shared.enums import CurrencyCode, TaxType, DiscountType, AdvancePaymentType, TemplateType
from app.domain.value_objects.address import Address
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, DatabaseError, DomainValidationError
)

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseEstimateRepository(EstimateRepository):
    """
    Supabase client implementation of EstimateRepository.
    
    This repository uses Supabase client SDK for all estimate database operations,
    leveraging RLS, real-time features, and built-in auth integration.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "estimates"
        logger.info(f"SupabaseEstimateRepository initialized with client: {self.client}")
    
    async def create(self, estimate: Estimate) -> Estimate:
        """Create a new estimate in Supabase."""
        logger.info(f"create() called for estimate: {estimate.title}, business: {estimate.business_id}")
        
        try:
            estimate_data = self._estimate_to_dict(estimate)
            logger.info(f"Estimate data prepared: {estimate_data['title']}")
            
            logger.info("Making request to Supabase table.insert")
            response = self.client.table(self.table_name).insert(estimate_data).execute()
            logger.info(f"Supabase response received: data={response.data is not None}")
            
            if response.data:
                estimate_id = uuid.UUID(response.data[0]['id'])
                logger.info(f"Estimate created successfully in Supabase: {estimate_id}")
                
                # Create line items separately
                if estimate.line_items:
                    line_items_data = []
                    for i, line_item in enumerate(estimate.line_items):
                        line_item_data = self._line_item_to_dict(line_item, estimate_id, i)
                        line_items_data.append(line_item_data)
                    
                    logger.info(f"Creating {len(line_items_data)} line items")
                    line_items_response = self.client.table("estimate_line_items").insert(line_items_data).execute()
                    logger.info(f"Line items created: {len(line_items_response.data) if line_items_response.data else 0}")
                
                # Fetch the complete estimate with line items
                return await self.get_by_id(estimate_id)
            else:
                logger.error("Failed to create estimate - no data returned from Supabase")
                raise DatabaseError("Failed to create estimate - no data returned")
                
        except Exception as e:
            logger.error(f"Exception in create(): {type(e).__name__}: {str(e)}")
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"Estimate with number '{estimate.estimate_number}' already exists")
            raise DatabaseError(f"Failed to create estimate: {str(e)}")
    
    async def get_by_id(self, estimate_id: uuid.UUID) -> Optional[Estimate]:
        """Get estimate by ID."""
        try:
            # Fetch estimate
            response = self.client.table(self.table_name).select("*").eq("id", str(estimate_id)).execute()
            
            if not response.data:
                return None
            
            # Fetch line items
            line_items_response = self.client.table("estimate_line_items").select("*").eq(
                "estimate_id", str(estimate_id)
            ).order("sort_order").execute()
            
            # Add line items to estimate data
            estimate_data = response.data[0]
            estimate_data["_line_items"] = line_items_response.data
            
            return self._dict_to_estimate(estimate_data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimate by ID: {str(e)}")
    
    async def get_by_estimate_number(self, business_id: uuid.UUID, estimate_number: str) -> Optional[Estimate]:
        """Get estimate by estimate number within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("estimate_number", estimate_number).execute()
            
            if response.data:
                return self._dict_to_estimate(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimate by number: {str(e)}")
    
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates by business ID with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimates by business: {str(e)}")
    
    async def get_recent_by_business(self, business_id: uuid.UUID, days: int = 30, limit: int = 10) -> List[Estimate]:
        """Get recent estimates by business ID within the specified number of days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).gte("created_date", cutoff_date.isoformat()).range(
                0, limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get recent estimates by business: {str(e)}")
    
    async def get_by_contact_id(self, contact_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates by contact ID with pagination."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "contact_id", str(contact_id)
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimates by contact: {str(e)}")
    
    async def get_by_project_id(self, project_id: uuid.UUID, business_id: uuid.UUID,
                               skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates associated with a specific project."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "project_id", str(project_id)
            ).eq("business_id", str(business_id)).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimates by project: {str(e)}")
    
    async def get_by_job_id(self, job_id: uuid.UUID, business_id: uuid.UUID,
                           skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates associated with a specific job."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "job_id", str(job_id)
            ).eq("business_id", str(business_id)).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimates by job: {str(e)}")
    
    async def get_by_status(self, business_id: uuid.UUID, status: EstimateStatus,
                           skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates by status within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", status.value).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimates by status: {str(e)}")
    
    async def get_by_assigned_user(self, business_id: uuid.UUID, user_id: str,
                                  skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates assigned to a specific user within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("created_by", user_id).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimates by assigned user: {str(e)}")
    
    async def get_by_template_id(self, business_id: uuid.UUID, template_id: uuid.UUID,
                                skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates using a specific template within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("template_id", str(template_id)).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimates by template: {str(e)}")
    
    async def get_by_date_range(self, business_id: uuid.UUID, start_date: datetime,
                               end_date: datetime, skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates within a date range."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).gte("created_date", start_date.isoformat()).lte(
                "created_date", end_date.isoformat()
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimates by date range: {str(e)}")
    
    async def get_expired_estimates(self, business_id: uuid.UUID,
                                   skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates that have expired but not yet marked as expired."""
        try:
            # Using Supabase function to get expired estimates
            response = self.client.rpc("get_expired_estimates", {
                "p_business_id": str(business_id),
                "p_limit": limit,
                "p_offset": skip
            }).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get expired estimates: {str(e)}")
    
    async def get_expiring_soon(self, business_id: uuid.UUID, days: int = 7,
                               skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates expiring within the specified number of days."""
        try:
            response = self.client.rpc("get_expiring_estimates", {
                "p_business_id": str(business_id),
                "p_days": days,
                "p_limit": limit,
                "p_offset": skip
            }).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get expiring estimates: {str(e)}")
    
    async def get_pending_approval(self, business_id: uuid.UUID,
                                  skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates pending client approval (sent but not approved/rejected)."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).in_("status", [EstimateStatus.SENT.value, EstimateStatus.VIEWED.value]).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get pending approval estimates: {str(e)}")
    
    async def get_by_value_range(self, business_id: uuid.UUID, min_value: Decimal,
                                max_value: Decimal, skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates within a value range."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).gte("total_amount", float(min_value)).lte(
                "total_amount", float(max_value)
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimates by value range: {str(e)}")
    
    async def search_estimates(self, business_id: uuid.UUID, search_term: str,
                              skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Search estimates within a business by title, description, or estimate number."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).or_(
                f"title.ilike.%{search_term}%,description.ilike.%{search_term}%,estimate_number.ilike.%{search_term}%,client_name.ilike.%{search_term}%"
            ).range(skip, skip + limit - 1).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search estimates: {str(e)}")
    
    async def get_by_currency(self, business_id: uuid.UUID, currency: CurrencyCode,
                             skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates by currency within a business."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("currency", currency.value).range(
                skip, skip + limit - 1
            ).order("created_date", desc=True).execute()
            
            return [self._dict_to_estimate(estimate_data) for estimate_data in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get estimates by currency: {str(e)}")
    
    async def update(self, estimate: Estimate) -> Estimate:
        """Update an existing estimate."""
        try:
            estimate_data = self._estimate_to_dict(estimate)
            estimate_data["last_modified"] = datetime.utcnow().isoformat()
            
            response = self.client.table(self.table_name).update(estimate_data).eq(
                "id", str(estimate.id)
            ).execute()
            
            if response.data:
                return self._dict_to_estimate(response.data[0])
            else:
                raise EntityNotFoundError(f"Estimate with ID {estimate.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateEntityError(f"Estimate number conflicts with existing estimate")
            raise DatabaseError(f"Failed to update estimate: {str(e)}")
    
    async def delete(self, estimate_id: uuid.UUID) -> bool:
        """Delete an estimate by ID."""
        try:
            response = self.client.table(self.table_name).delete().eq("id", str(estimate_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete estimate: {str(e)}")
    
    async def bulk_update_status(self, business_id: uuid.UUID, estimate_ids: List[uuid.UUID],
                                status: EstimateStatus) -> int:
        """Bulk update estimate status."""
        try:
            id_strings = [str(id) for id in estimate_ids]
            
            response = self.client.table(self.table_name).update({
                "status": status.value,
                "last_modified": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_("id", id_strings).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk update estimate status: {str(e)}")
    
    async def bulk_assign_estimates(self, business_id: uuid.UUID, estimate_ids: List[uuid.UUID],
                                   user_id: str) -> int:
        """Bulk assign estimates to a user."""
        try:
            id_strings = [str(id) for id in estimate_ids]
            
            response = self.client.table(self.table_name).update({
                "created_by": user_id,
                "last_modified": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_("id", id_strings).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk assign estimates: {str(e)}")
    
    async def bulk_expire_estimates(self, business_id: uuid.UUID, estimate_ids: List[uuid.UUID]) -> int:
        """Bulk mark estimates as expired."""
        try:
            id_strings = [str(id) for id in estimate_ids]
            
            response = self.client.table(self.table_name).update({
                "status": EstimateStatus.EXPIRED.value,
                "last_modified": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_("id", id_strings).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk expire estimates: {str(e)}")
    
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Count total estimates for a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count estimates by business: {str(e)}")
    
    async def count_by_status(self, business_id: uuid.UUID, status: EstimateStatus) -> int:
        """Count estimates by status within a business."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            ).eq("status", status.value).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count estimates by status: {str(e)}")
    
    async def count_by_contact(self, contact_id: uuid.UUID) -> int:
        """Count estimates for a specific contact."""
        try:
            response = self.client.table(self.table_name).select("id", count="exact").eq(
                "contact_id", str(contact_id)
            ).execute()
            
            return response.count or 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count estimates by contact: {str(e)}")
    
    async def exists(self, estimate_id: uuid.UUID) -> bool:
        """Check if an estimate exists."""
        try:
            response = self.client.table(self.table_name).select("id").eq("id", str(estimate_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check estimate existence: {str(e)}")
    
    async def has_duplicate_estimate_number(self, business_id: uuid.UUID, estimate_number: str,
                                           exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if estimate number already exists within business."""
        try:
            query = self.client.table(self.table_name).select("id").eq(
                "business_id", str(business_id)
            ).eq("estimate_number", estimate_number)
            
            if exclude_id:
                query = query.neq("id", str(exclude_id))
            
            response = query.execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check duplicate estimate number: {str(e)}")
    
    async def get_next_estimate_number(self, business_id: uuid.UUID, prefix: str = "EST") -> str:
        """Generate next estimate number for a business."""
        try:
            # Determine document type from prefix
            document_type = "quote" if prefix == "QUO" else "estimate"
            
            response = self.client.rpc("get_next_document_number", {
                "business_uuid": str(business_id),
                "doc_type": document_type
            }).execute()
            
            if response.data:
                return response.data
            else:
                # Fallback to simple sequential number
                return f"{prefix}-000001"
                
        except Exception as e:
            # Log the error but don't fail - use fallback
            logger.warning(f"Failed to get next estimate number from database: {str(e)}")
            return f"{prefix}-000001"

    async def list_with_pagination(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[Estimate], int]:
        """List estimates with pagination and filters."""
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
            
            # Add pagination and ordering
            query = query.range(skip, skip + limit - 1).order("created_date", desc=True)
            
            # Execute the query
            response = query.execute()
            
            # Fetch line items for all estimates in one query
            estimate_ids = [estimate["id"] for estimate in response.data]
            line_items_response = []
            if estimate_ids:
                line_items_response = self.client.table("estimate_line_items").select("*").in_(
                    "estimate_id", estimate_ids
                ).order("sort_order").execute()
            
            # Group line items by estimate_id
            line_items_by_estimate = {}
            for item in line_items_response.data:
                estimate_id = item["estimate_id"]
                if estimate_id not in line_items_by_estimate:
                    line_items_by_estimate[estimate_id] = []
                line_items_by_estimate[estimate_id].append(item)
            
            # Convert the data to Estimate entities with line items
            estimates = []
            for estimate_data in response.data:
                estimate_data["_line_items"] = line_items_by_estimate.get(estimate_data["id"], [])
                estimates.append(self._dict_to_estimate(estimate_data))
            
            total_count = response.count or 0
            
            return estimates, total_count
            
        except Exception as e:
            raise DatabaseError(f"Failed to list estimates with pagination: {str(e)}")
    
    def _estimate_to_dict(self, estimate: Estimate) -> dict:
        """Convert Estimate entity to database dictionary."""
        return {
            "id": str(estimate.id),
            "business_id": str(estimate.business_id),
            "estimate_number": estimate.estimate_number,
            "title": estimate.title,
            "description": estimate.description,
            "po_number": estimate.po_number,
            "status": estimate.status.value if hasattr(estimate.status, 'value') else str(estimate.status),
            "contact_id": str(estimate.contact_id) if estimate.contact_id else None,
            "project_id": str(estimate.project_id) if estimate.project_id else None,
            "job_id": str(estimate.job_id) if estimate.job_id else None,
            "template_id": str(estimate.template_id) if estimate.template_id else None,
            "assigned_to": estimate.created_by,  # Map to assigned_to field
            "currency": estimate.currency.value if hasattr(estimate.currency, 'value') else str(estimate.currency),
            "subtotal": float(estimate.get_line_items_subtotal()),
            "discount_type": estimate.overall_discount_type.value if hasattr(estimate.overall_discount_type, 'value') else str(estimate.overall_discount_type),
            "discount_value": float(estimate.overall_discount_value),
            "discount_amount": float(estimate.get_overall_discount_amount()),
            "tax_type": estimate.tax_type.value if hasattr(estimate.tax_type, 'value') else str(estimate.tax_type),
            "tax_rate": float(estimate.tax_rate),
            "tax_amount": float(estimate.get_tax_amount()),
            "total_amount": float(estimate.get_total_amount()),
            "advance_payment_type": estimate.advance_payment.type.value if hasattr(estimate.advance_payment.type, 'value') else str(estimate.advance_payment.type),
            "advance_payment_value": float(estimate.advance_payment.value),
            "advance_payment_amount": float(estimate.advance_payment.get_required_amount(estimate.get_total_amount())),
            "advance_payment_due_date": estimate.advance_payment.due_date.isoformat() if estimate.advance_payment.due_date else None,
            "advance_payment_received": estimate.advance_payment.collected_amount > 0,
            "advance_payment_received_date": estimate.advance_payment.collected_date.isoformat() if estimate.advance_payment.collected_date else None,
            "valid_until": estimate.terms.get_expiry_date(estimate.created_date.date()).isoformat() if estimate.terms else None,
            "terms_and_conditions": estimate.terms.terms_and_conditions if estimate.terms else None,
            "notes": estimate.internal_notes,
            "issue_date": estimate.issue_date.isoformat() if estimate.issue_date else None,
            "email_tracking": [self._email_tracking_to_dict(email) for email in estimate.email_history],
            "status_history": [self._status_history_to_dict(entry) for entry in estimate.status_history],
            "converted_to_invoice_id": str(estimate.converted_to_invoice_id) if estimate.converted_to_invoice_id else None,
            "created_by": estimate.created_by,
            "created_date": estimate.created_date.isoformat(),
            "last_modified": estimate.last_modified.isoformat()
        }
    
    def _line_item_to_dict(self, line_item: EstimateLineItem, estimate_id: uuid.UUID, sort_order: int = 0) -> dict:
        """Convert EstimateLineItem to dictionary for database storage."""
        return {
            "id": str(line_item.id),
            "estimate_id": str(estimate_id),
            "sort_order": sort_order,
            "name": line_item.description,  # Map description to name field
            "description": line_item.notes,  # Map notes to description field  
            "quantity": float(line_item.quantity),
            "unit": line_item.unit or "each",
            "unit_price": float(line_item.unit_price),
            "discount_type": line_item.discount_type.value if hasattr(line_item.discount_type, 'value') else str(line_item.discount_type),
            "discount_value": float(line_item.discount_value),
            "discount_amount": float(line_item.get_discount_amount()),
            "tax_type": "percentage",  # Map tax_rate to tax_type
            "tax_rate": float(line_item.tax_rate),
            "tax_amount": float(line_item.get_tax_amount()),
            "total_amount": float(line_item.get_total()),
            "is_taxable": line_item.tax_rate > 0,
            "notes": line_item.notes
        }
    
    def _advance_payment_to_dict(self, advance_payment: AdvancePayment) -> dict:
        """Convert AdvancePayment to dictionary."""
        return {
            "required": advance_payment.required,
            "type": advance_payment.type.value if hasattr(advance_payment.type, 'value') else str(advance_payment.type),
            "value": float(advance_payment.value),
            "due_date": advance_payment.due_date.isoformat() if advance_payment.due_date else None,
            "collected_amount": float(advance_payment.collected_amount),
            "collected_date": advance_payment.collected_date.isoformat() if advance_payment.collected_date else None,
            "collection_method": advance_payment.collection_method,
            "reference": advance_payment.reference,
            "notes": advance_payment.notes
        }
    
    def _terms_to_dict(self, terms: EstimateTerms) -> dict:
        """Convert EstimateTerms to dictionary."""
        return {
            "payment_terms": terms.payment_terms,
            "validity_days": terms.validity_days,
            "warranty_period": terms.warranty_period,
            "terms_and_conditions": terms.terms_and_conditions,
            "notes": terms.notes
        }
    
    def _email_tracking_to_dict(self, email_tracking: EmailTracking) -> dict:
        """Convert EmailTracking to dictionary."""
        return {
            "id": str(email_tracking.id),
            "sent_date": email_tracking.sent_date.isoformat() if email_tracking.sent_date else None,
            "delivered_date": email_tracking.delivered_date.isoformat() if email_tracking.delivered_date else None,
            "opened_date": email_tracking.opened_date.isoformat() if email_tracking.opened_date else None,
            "clicked_date": email_tracking.clicked_date.isoformat() if email_tracking.clicked_date else None,
            "status": email_tracking.status.value if hasattr(email_tracking.status, 'value') else str(email_tracking.status),
            "recipient_email": email_tracking.recipient_email,
            "subject": email_tracking.subject,
            "message_id": email_tracking.message_id,
            "error_message": email_tracking.error_message,
            "tracking_data": email_tracking.tracking_data
        }
    
    def _status_history_to_dict(self, status_entry: StatusHistoryEntry) -> dict:
        """Convert StatusHistoryEntry to dictionary."""
        return {
            "id": str(status_entry.id),
            "from_status": status_entry.from_status.value if status_entry.from_status and hasattr(status_entry.from_status, 'value') else str(status_entry.from_status) if status_entry.from_status else None,
            "to_status": status_entry.to_status.value if hasattr(status_entry.to_status, 'value') else str(status_entry.to_status),
            "timestamp": status_entry.timestamp.isoformat(),
            "changed_by": status_entry.changed_by,
            "reason": status_entry.reason,
            "notes": status_entry.notes
        }
    
    def _dict_to_estimate(self, data: dict) -> Estimate:
        """Convert database dictionary to Estimate entity."""
        
        def safe_json_parse(value, default=None):
            if value is None:
                return default or []
            if isinstance(value, (list, dict)):
                return value
            try:
                return json.loads(value) if isinstance(value, str) else value
            except (json.JSONDecodeError, TypeError):
                return default or []
        
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
        
        # Parse line items from separate table data
        line_items_data = data.get("_line_items", [])
        line_items = []
        for item_data in line_items_data:
            try:
                line_item = EstimateLineItem(
                    id=uuid.UUID(item_data["id"]),
                    description=item_data.get("name", ""),  # Schema uses 'name' not 'description'
                    quantity=Decimal(str(item_data.get("quantity", "1"))),
                    unit_price=Decimal(str(item_data.get("unit_price", "0"))),
                    unit=item_data.get("unit"),
                    category=None,  # Not in current schema
                    discount_type=DiscountType(item_data.get("discount_type", "none")),
                    discount_value=Decimal(str(item_data.get("discount_value", "0"))),
                    tax_rate=Decimal(str(item_data.get("tax_rate", "0"))),
                    notes=item_data.get("notes")
                )
                line_items.append(line_item)
            except Exception as e:
                logger.warning(f"Failed to parse line item: {e}")
                continue
        
        # Parse advance payment
        advance_payment_data = safe_json_parse(data.get("advance_payment", {}))
        advance_payment = AdvancePayment(
            required=advance_payment_data.get("required", False),
            type=AdvancePaymentType(advance_payment_data.get("type", "none")),
            value=Decimal(str(advance_payment_data.get("value", "0"))),
            due_date=safe_date_parse(advance_payment_data.get("due_date")),
            collected_amount=Decimal(str(advance_payment_data.get("collected_amount", "0"))),
            collected_date=safe_datetime_parse(advance_payment_data.get("collected_date")),
            collection_method=advance_payment_data.get("collection_method"),
            reference=advance_payment_data.get("reference"),
            notes=advance_payment_data.get("notes")
        )
        
        # Parse terms
        terms_data = safe_json_parse(data.get("terms", {}))
        terms = EstimateTerms(
            payment_terms=terms_data.get("payment_terms"),
            validity_days=terms_data.get("validity_days", 30),
            warranty_period=terms_data.get("warranty_period"),
            terms_and_conditions=terms_data.get("terms_and_conditions"),
            notes=terms_data.get("notes")
        )
        
        # Parse email history
        email_history_data = safe_json_parse(data.get("email_history", []))
        email_history = []
        for email_data in email_history_data:
            try:
                email_tracking = EmailTracking(
                    id=uuid.UUID(email_data["id"]),
                    sent_date=safe_datetime_parse(email_data.get("sent_date")),
                    delivered_date=safe_datetime_parse(email_data.get("delivered_date")),
                    opened_date=safe_datetime_parse(email_data.get("opened_date")),
                    clicked_date=safe_datetime_parse(email_data.get("clicked_date")),
                    status=EmailStatus(email_data.get("status", "pending")),
                    recipient_email=email_data.get("recipient_email"),
                    subject=email_data.get("subject"),
                    message_id=email_data.get("message_id"),
                    error_message=email_data.get("error_message"),
                    tracking_data=email_data.get("tracking_data", {})
                )
                email_history.append(email_tracking)
            except Exception as e:
                logger.warning(f"Failed to parse email tracking: {e}")
                continue
        
        # Parse status history
        status_history_data = safe_json_parse(data.get("status_history", []))
        status_history = []
        for status_data in status_history_data:
            try:
                # Use safe_uuid_parse for status history ID and generate fallback if needed
                status_id = safe_uuid_parse(status_data.get("id")) or uuid.uuid4()
                
                # Convert status strings to enums properly
                from_status_str = status_data.get("from_status")
                from_status = EstimateStatus.parse_from_string(from_status_str) if from_status_str else None
                to_status_str = status_data.get("to_status", "draft")
                to_status = EstimateStatus.parse_from_string(to_status_str) or EstimateStatus.DRAFT
                
                status_entry = StatusHistoryEntry(
                    id=status_id,
                    from_status=from_status,
                    to_status=to_status,
                    timestamp=safe_datetime_parse(status_data["timestamp"]),
                    changed_by=status_data.get("changed_by"),
                    reason=status_data.get("reason"),
                    notes=status_data.get("notes")
                )
                status_history.append(status_entry)
            except Exception as e:
                logger.warning(f"Failed to parse status history: {e}")
                continue
        
        # Parse client address
        client_address = None
        if data.get("client_address"):
            try:
                address_data = safe_json_parse(data["client_address"])
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
                logger.warning(f"Failed to parse client address: {e}")
        
        # Use model_validate to ensure all Pydantic validation is triggered
        # Explicitly convert status string to enum to prevent conversion issues
        status_str = data.get("status", "draft")
        status_enum = EstimateStatus.parse_from_string(status_str) or EstimateStatus.DRAFT
        
        estimate_data = {
            "id": uuid.UUID(data["id"]),
            "business_id": uuid.UUID(data["business_id"]),
            "estimate_number": data.get("estimate_number"),
            "document_type": data.get("document_type", "estimate"),
            "status": status_enum,
            "status_history": status_history,
            "contact_id": safe_uuid_parse(data.get("contact_id")),
            "client_name": data.get("client_name"),
            "client_email": data.get("client_email"),
            "client_phone": data.get("client_phone"),
            "client_address": client_address,
            "title": data.get("title", ""),
            "description": data.get("description"),
            "po_number": data.get("po_number"),
            "line_items": line_items,
            "currency": data.get("currency", "USD"),
            "tax_rate": Decimal(str(data.get("tax_rate", "0"))),
            "tax_type": data.get("tax_type", "percentage"),
            "overall_discount_type": data.get("overall_discount_type", "none"),
            "overall_discount_value": Decimal(str(data.get("overall_discount_value", "0"))),
            "advance_payment": advance_payment,
            "terms": terms,
            "template_id": safe_uuid_parse(data.get("template_id")),
            "template_data": safe_json_parse(data.get("template_data", {})),
            "email_history": email_history,
            "project_id": safe_uuid_parse(data.get("project_id")),
            "job_id": safe_uuid_parse(data.get("job_id")),
            "converted_to_invoice_id": safe_uuid_parse(data.get("converted_to_invoice_id")),
            "conversion_date": safe_datetime_parse(data.get("conversion_date")),
            "tags": safe_json_parse(data.get("tags", [])),
            "custom_fields": safe_json_parse(data.get("custom_fields", {})),
            "internal_notes": data.get("internal_notes"),
            "issue_date": safe_date_parse(data.get("issue_date")),
            "created_by": data.get("created_by"),
            "created_date": safe_datetime_parse(data["created_date"]) or datetime.now(),
            "last_modified": safe_datetime_parse(data["last_modified"]) or datetime.now(),
            "sent_date": safe_datetime_parse(data.get("sent_date")),
            "viewed_date": safe_datetime_parse(data.get("viewed_date")),
            "responded_date": safe_datetime_parse(data.get("responded_date"))
        }
        
        return Estimate.model_validate(estimate_data) 

    async def list_with_filters(self, business_id: uuid.UUID, filters: Dict[str, Any], 
                              sort_by: str = "created_date", sort_desc: bool = True,
                              skip: int = 0, limit: int = 100) -> Tuple[List[Estimate], int]:
        """List estimates with flexible filtering."""
        logger.info(f"list_with_filters() called for business: {business_id}, filters: {filters}")
        
        try:
            # Start with base query
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            # Apply filters
            for field, value in filters.items():
                if value is None:
                    continue
                    
                if field == "status":
                    query = query.eq("status", value)
                elif field == "status_list":
                    if value:
                        status_values = [s.value if hasattr(s, 'value') else str(s) for s in value]
                        query = query.in_("status", status_values)
                elif field == "contact_id":
                    query = query.eq("contact_id", str(value))
                elif field == "project_id":
                    query = query.eq("project_id", str(value))
                elif field == "job_id":
                    query = query.eq("job_id", str(value))
                elif field == "template_id":
                    query = query.eq("template_id", str(value))
                elif field == "date_from":
                    query = query.gte("created_date", value.isoformat())
                elif field == "date_to":
                    query = query.lte("created_date", value.isoformat())
                elif field == "min_value":
                    # This would need a calculated field for total_amount
                    pass
                elif field == "max_value":
                    # This would need a calculated field for total_amount
                    pass
                elif field == "currency":
                    query = query.eq("currency", value)
                elif field == "client_name_contains":
                    query = query.ilike("client_name", f"%{value}%")
                elif field == "client_email":
                    query = query.eq("client_email", value)
                elif field == "title_contains":
                    query = query.ilike("title", f"%{value}%")
                elif field == "description_contains":
                    query = query.ilike("description", f"%{value}%")
                elif field == "estimate_number_contains":
                    query = query.ilike("estimate_number", f"%{value}%")
                elif field == "search_term":
                    # Full text search across multiple fields
                    query = query.or_(f"title.ilike.%{value}%,description.ilike.%{value}%,client_name.ilike.%{value}%,estimate_number.ilike.%{value}%")
                elif field == "tags":
                    if value:
                        # Search for any tag in the list
                        for tag in value:
                            query = query.contains("tags", [tag])
            
            # Apply sorting
            sort_column = sort_by
            if sort_column == "client_display_name":
                sort_column = "client_name"
            elif sort_column == "total_amount":
                # For now, sort by created_date if total_amount is requested since it's calculated
                sort_column = "created_date"
            
            if sort_desc:
                query = query.order(sort_column, desc=True)
            else:
                query = query.order(sort_column)
            
            # Get total count first (without pagination)
            count_query = self.client.table(self.table_name).select("id", count="exact").eq("business_id", str(business_id))
            
            # Apply same filters to count query
            for field, value in filters.items():
                if value is None:
                    continue
                    
                if field == "status":
                    count_query = count_query.eq("status", value)
                elif field == "status_list":
                    if value:
                        count_query = count_query.in_("status", value)
                elif field == "contact_id":
                    count_query = count_query.eq("contact_id", str(value))
                elif field == "project_id":
                    count_query = count_query.eq("project_id", str(value))
                elif field == "job_id":
                    count_query = count_query.eq("job_id", str(value))
                elif field == "template_id":
                    count_query = count_query.eq("template_id", str(value))
                elif field == "date_from":
                    count_query = count_query.gte("created_date", value.isoformat())
                elif field == "date_to":
                    count_query = count_query.lte("created_date", value.isoformat())
                elif field == "currency":
                    count_query = count_query.eq("currency", value)
                elif field == "client_name_contains":
                    count_query = count_query.ilike("client_name", f"%{value}%")
                elif field == "client_email":
                    count_query = count_query.eq("client_email", value)
                elif field == "title_contains":
                    count_query = count_query.ilike("title", f"%{value}%")
                elif field == "description_contains":
                    count_query = count_query.ilike("description", f"%{value}%")
                elif field == "estimate_number_contains":
                    count_query = count_query.ilike("estimate_number", f"%{value}%")
                elif field == "search_term":
                    count_query = count_query.or_(f"title.ilike.%{value}%,description.ilike.%{value}%,client_name.ilike.%{value}%,estimate_number.ilike.%{value}%")
                elif field == "tags":
                    if value:
                        for tag in value:
                            count_query = count_query.contains("tags", [tag])
            
            # Execute count query
            count_response = count_query.execute()
            total_count = count_response.count if count_response.count is not None else 0
            
            # Apply pagination to main query
            query = query.range(skip, skip + limit - 1)
            
            # Execute main query
            response = query.execute()
            
            if not response.data:
                logger.info(f"No estimates found for business: {business_id}")
                return [], total_count
            
            # Fetch line items for all estimates in one query
            estimate_ids = [item["id"] for item in response.data]
            line_items_by_estimate = {}
            
            if estimate_ids:
                try:
                    line_items_response = self.client.table("estimate_line_items").select("*").in_(
                        "estimate_id", estimate_ids
                    ).order("estimate_id, sort_order").execute()
                    
                    # Group line items by estimate_id
                    for item in line_items_response.data:
                        estimate_id = item["estimate_id"]
                        if estimate_id not in line_items_by_estimate:
                            line_items_by_estimate[estimate_id] = []
                        line_items_by_estimate[estimate_id].append(item)
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch line items: {e}")
                    line_items_by_estimate = {}
            
            # Convert to domain entities
            estimates = []
            for data in response.data:
                try:
                    # Add line items to estimate data
                    data["_line_items"] = line_items_by_estimate.get(data["id"], [])
                    estimate = self._dict_to_estimate(data)
                    estimates.append(estimate)
                except Exception as e:
                    logger.error(f"Failed to convert estimate data to entity: {e}, data: {data}")
                    continue
            
            logger.info(f"Retrieved {len(estimates)} estimates with filters (total: {total_count})")
            return estimates, total_count
            
        except Exception as e:
            logger.error(f"Error retrieving estimates with filters: {e}")
            raise DatabaseError(f"Failed to retrieve estimates: {str(e)}")
    
    async def count_with_filters(self, business_id: uuid.UUID, filters: Dict[str, Any]) -> int:
        """Count estimates with flexible filtering."""
        logger.info(f"count_with_filters() called for business: {business_id}, filters: {filters}")
        
        try:
            # Start with base query
            query = self.client.table(self.table_name).select("id", count="exact").eq("business_id", str(business_id))
            
            # Apply the same filters as list_with_filters
            for field, value in filters.items():
                if value is None:
                    continue
                    
                if field == "status":
                    query = query.eq("status", value)
                elif field == "status_list":
                    if value:
                        # Convert EstimateStatus enum objects to string values
                        status_values = [s.value if hasattr(s, 'value') else str(s) for s in value]
                        query = query.in_("status", status_values)
                elif field == "contact_id":
                    query = query.eq("contact_id", str(value))
                elif field == "project_id":
                    query = query.eq("project_id", str(value))
                elif field == "job_id":
                    query = query.eq("job_id", str(value))
                elif field == "template_id":
                    query = query.eq("template_id", str(value))
                elif field == "date_from":
                    query = query.gte("created_date", value.isoformat())
                elif field == "date_to":
                    query = query.lte("created_date", value.isoformat())
                elif field == "currency":
                    query = query.eq("currency", value)
                elif field == "client_name_contains":
                    query = query.ilike("client_name", f"%{value}%")
                elif field == "client_email":
                    query = query.eq("client_email", value)
                elif field == "title_contains":
                    query = query.ilike("title", f"%{value}%")
                elif field == "description_contains":
                    query = query.ilike("description", f"%{value}%")
                elif field == "estimate_number_contains":
                    query = query.ilike("estimate_number", f"%{value}%")
                elif field == "search_term":
                    # Full text search across multiple fields
                    query = query.or_(f"title.ilike.%{value}%,description.ilike.%{value}%,client_name.ilike.%{value}%,estimate_number.ilike.%{value}%")
                elif field == "tags":
                    if value:
                        for tag in value:
                            query = query.contains("tags", [tag])
            
            # Execute count query
            response = query.execute()
            count = response.count if response.count is not None else 0
            
            logger.info(f"Count with filters: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Error counting estimates with filters: {e}")
            raise DatabaseError(f"Failed to count estimates: {str(e)}") 

    def query(self):
        """Return EstimateQueryBuilder for fluent query building."""
        from app.domain.repositories.estimate_repository import EstimateQueryBuilder
        return EstimateQueryBuilder()
    
    async def execute_query(self, business_id: uuid.UUID, query_builder) -> Tuple[List[Estimate], int]:
        """Execute a query built by EstimateQueryBuilder."""
        filters = query_builder.build_filters()
        sort_by, sort_desc = query_builder.build_sort()
        skip, limit = query_builder.build_pagination()
        
        return await self.list_with_filters(
            business_id=business_id,
            filters=filters,
            sort_by=sort_by,
            sort_desc=sort_desc,
            skip=skip,
            limit=limit
        ) 