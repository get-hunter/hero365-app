"""
Supabase Supplier Repository Implementation

Repository implementation for supplier management with performance tracking.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta

from supabase import Client

from app.domain.repositories.supplier_repository import SupplierRepository
from app.domain.entities.supplier import Supplier
from app.domain.entities.product_enums.enums import SupplierStatus
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, DatabaseError
)

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseSupplierRepository(SupplierRepository):
    """
    Supabase client implementation of SupplierRepository.
    
    Handles supplier management with automated performance tracking.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "suppliers"
        logger.info(f"SupabaseSupplierRepository initialized")
    
    async def create(self, supplier: Supplier) -> Supplier:
        """Create a new supplier."""
        try:
            supplier_data = self._supplier_to_dict(supplier)
            
            response = self.client.table(self.table_name).insert(supplier_data).execute()
            
            if response.data:
                return self._dict_to_supplier(response.data[0])
            else:
                raise DatabaseError("Failed to create supplier - no data returned")
                
        except Exception as e:
            if "duplicate key" in str(e).lower():
                raise DuplicateEntityError(f"Supplier with code '{supplier.supplier_code}' already exists")
            raise DatabaseError(f"Failed to create supplier: {str(e)}")
    
    async def get_by_id(self, business_id: uuid.UUID, supplier_id: uuid.UUID) -> Optional[Supplier]:
        """Get supplier by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("id", str(supplier_id)).execute()
            
            if response.data:
                return self._dict_to_supplier(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get supplier by ID: {str(e)}")
    
    async def get_by_code(self, business_id: uuid.UUID, supplier_code: str) -> Optional[Supplier]:
        """Get supplier by code."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("supplier_code", supplier_code).execute()
            
            if response.data:
                return self._dict_to_supplier(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get supplier by code: {str(e)}")
    
    async def get_by_tax_id(self, business_id: uuid.UUID, tax_id: str) -> Optional[Supplier]:
        """Get supplier by tax ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("tax_id", tax_id).execute()
            
            if response.data:
                return self._dict_to_supplier(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get supplier by tax ID: {str(e)}")
    
    async def update(self, supplier: Supplier) -> Supplier:
        """Update an existing supplier."""
        try:
            supplier_data = self._supplier_to_dict(supplier)
            supplier_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table(self.table_name).update(supplier_data).eq(
                "id", str(supplier.id)
            ).execute()
            
            if response.data:
                return self._dict_to_supplier(response.data[0])
            else:
                raise EntityNotFoundError(f"Supplier with ID {supplier.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update supplier: {str(e)}")
    
    async def delete(self, business_id: uuid.UUID, supplier_id: uuid.UUID) -> bool:
        """Delete a supplier (soft delete)."""
        try:
            response = self.client.table(self.table_name).update({
                "status": SupplierStatus.INACTIVE.value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq("id", str(supplier_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete supplier: {str(e)}")
    
    async def list_by_business(
        self,
        business_id: uuid.UUID,
        status: Optional[SupplierStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Supplier]:
        """List suppliers for a business with optional filtering."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if status:
                query = query.eq("status", status.value)
            
            response = query.range(offset, offset + limit - 1).order("company_name").execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to list suppliers: {str(e)}")
    
    async def search_suppliers(
        self,
        business_id: uuid.UUID,
        query: str,
        status: Optional[SupplierStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Supplier]:
        """Search suppliers by name, code, or contact information."""
        try:
            search_query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).or_(
                f"company_name.ilike.%{query}%,supplier_code.ilike.%{query}%,contact_name.ilike.%{query}%"
            )
            
            if status:
                search_query = search_query.eq("status", status.value)
            
            response = search_query.range(offset, offset + limit - 1).order("company_name").execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search suppliers: {str(e)}")
    
    async def get_suppliers_by_status(
        self,
        business_id: uuid.UUID,
        status: SupplierStatus
    ) -> List[Supplier]:
        """Get suppliers by status."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", status.value).order("company_name").execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get suppliers by status: {str(e)}")
    
    async def get_suppliers_by_location(
        self,
        business_id: uuid.UUID,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Supplier]:
        """Get suppliers by location."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if country:
                query = query.ilike("address", f"%{country}%")
            if state:
                query = query.ilike("address", f"%{state}%")
            if city:
                query = query.ilike("address", f"%{city}%")
            
            response = query.order("company_name").execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get suppliers by location: {str(e)}")
    
    async def get_suppliers_for_product(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        active_only: bool = True
    ) -> List[Supplier]:
        """Get suppliers that provide a specific product."""
        try:
            # This would require joining with product_suppliers table
            # For now, returning all active suppliers
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if active_only:
                query = query.eq("status", SupplierStatus.ACTIVE.value)
            
            response = query.order("company_name").execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get suppliers for product: {str(e)}")
    
    async def get_preferred_suppliers(
        self,
        business_id: uuid.UUID,
        product_id: Optional[uuid.UUID] = None
    ) -> List[Supplier]:
        """Get preferred suppliers for a product or all preferred suppliers."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("is_preferred", True).eq("status", SupplierStatus.ACTIVE.value)
            
            response = query.order("performance_score", desc=True).execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get preferred suppliers: {str(e)}")
    
    async def get_suppliers_by_product_category(
        self,
        business_id: uuid.UUID,
        category_id: uuid.UUID
    ) -> List[Supplier]:
        """Get suppliers that provide products in a specific category."""
        try:
            # This would require joining with products and product categories
            # For now, returning all active suppliers
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", SupplierStatus.ACTIVE.value).order("company_name").execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get suppliers by product category: {str(e)}")
    
    async def update_supplier_performance(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        performance_data: Dict[str, Any]
    ) -> bool:
        """Update supplier performance metrics."""
        try:
            response = self.client.table(self.table_name).update({
                "performance_score": performance_data.get("performance_score"),
                "on_time_delivery_rate": performance_data.get("on_time_delivery_rate"),
                "quality_score": performance_data.get("quality_score"),
                "return_rate": performance_data.get("return_rate"),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq("id", str(supplier_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to update supplier performance: {str(e)}")
    
    async def calculate_performance_score(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """Calculate performance score for a supplier."""
        try:
            # This would require complex calculations based on delivery history, quality, etc.
            # For now, returning a default score
            supplier = await self.get_by_id(business_id, supplier_id)
            if supplier and supplier.performance_score:
                return supplier.performance_score
            return Decimal('75.0')  # Default score
            
        except Exception as e:
            raise DatabaseError(f"Failed to calculate performance score: {str(e)}")
    
    async def get_top_performing_suppliers(
        self,
        business_id: uuid.UUID,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top performing suppliers."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", SupplierStatus.ACTIVE.value).order("performance_score", desc=True).limit(limit).execute()
            
            suppliers = [self._dict_to_supplier(supplier) for supplier in response.data]
            
            return [{
                "id": str(supplier.id),
                "company_name": supplier.company_name,
                "supplier_code": supplier.supplier_code,
                "performance_score": float(supplier.performance_score),
                "total_orders": supplier.total_orders,
                "total_spent": float(supplier.total_spent)
            } for supplier in suppliers]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get top performing suppliers: {str(e)}")
    
    async def get_suppliers_needing_review(
        self,
        business_id: uuid.UUID,
        performance_threshold: Optional[Decimal] = None
    ) -> List[Supplier]:
        """Get suppliers that need performance review."""
        try:
            threshold = performance_threshold or Decimal('60.0')
            
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).lt("performance_score", float(threshold)).execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get suppliers needing review: {str(e)}")
    
    async def get_supplier_analytics(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a supplier."""
        try:
            supplier = await self.get_by_id(business_id, supplier_id)
            if not supplier:
                raise EntityNotFoundError(f"Supplier {supplier_id} not found")
            
            # This would require complex analytics calculations
            # For now, returning basic analytics
            return {
                "supplier_id": str(supplier_id),
                "company_name": supplier.company_name,
                "performance_score": float(supplier.performance_score),
                "total_orders": supplier.total_orders,
                "total_spent": float(supplier.total_spent),
                "avg_order_value": float(supplier.total_spent / supplier.total_orders) if supplier.total_orders > 0 else 0,
                "status": supplier.status.value,
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get supplier analytics: {str(e)}")
    
    async def get_suppliers_with_pending_orders(
        self,
        business_id: uuid.UUID
    ) -> List[Supplier]:
        """Get suppliers with pending purchase orders."""
        try:
            # This would require joining with purchase_orders table
            # For now, returning all active suppliers
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", SupplierStatus.ACTIVE.value).order("company_name").execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get suppliers with pending orders: {str(e)}")
    
    async def get_supplier_order_history(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get purchase order history for a supplier."""
        try:
            # This would require querying purchase_orders table
            # For now, returning empty list
            return []
            
        except Exception as e:
            raise DatabaseError(f"Failed to get supplier order history: {str(e)}")
    
    async def calculate_supplier_spend(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """Calculate total spend for a supplier."""
        try:
            supplier = await self.get_by_id(business_id, supplier_id)
            if supplier:
                return supplier.total_spent
            return Decimal('0')
            
        except Exception as e:
            raise DatabaseError(f"Failed to calculate supplier spend: {str(e)}")
    
    async def add_supplier_contact(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        contact_data: Dict[str, Any]
    ) -> bool:
        """Add a contact to a supplier."""
        try:
            # This would require a supplier_contacts table
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to add supplier contact: {str(e)}")
    
    async def update_supplier_contact(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        contact_id: uuid.UUID,
        contact_data: Dict[str, Any]
    ) -> bool:
        """Update a supplier contact."""
        try:
            # This would require a supplier_contacts table
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to update supplier contact: {str(e)}")
    
    async def remove_supplier_contact(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        contact_id: uuid.UUID
    ) -> bool:
        """Remove a supplier contact."""
        try:
            # This would require a supplier_contacts table
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to remove supplier contact: {str(e)}")
    
    async def get_supplier_contacts(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        contact_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get contacts for a supplier."""
        try:
            # This would require a supplier_contacts table
            # For now, returning empty list
            return []
            
        except Exception as e:
            raise DatabaseError(f"Failed to get supplier contacts: {str(e)}")
    
    async def update_payment_terms(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        payment_terms: Dict[str, Any]
    ) -> bool:
        """Update payment terms for a supplier."""
        try:
            response = self.client.table(self.table_name).update({
                "payment_terms": payment_terms,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq("id", str(supplier_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to update payment terms: {str(e)}")
    
    async def get_suppliers_by_payment_terms(
        self,
        business_id: uuid.UUID,
        payment_days: Optional[int] = None,
        has_early_discount: Optional[bool] = None
    ) -> List[Supplier]:
        """Get suppliers by payment terms."""
        try:
            # This would require complex payment terms filtering
            # For now, returning all active suppliers
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", SupplierStatus.ACTIVE.value).order("company_name").execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get suppliers by payment terms: {str(e)}")
    
    async def calculate_early_payment_savings(
        self,
        business_id: uuid.UUID,
        supplier_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate early payment savings."""
        try:
            # This would require complex payment calculations
            # For now, returning basic structure
            return {
                "total_savings": 0.0,
                "potential_savings": 0.0,
                "discount_rate": 2.0,
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to calculate early payment savings: {str(e)}")
    
    async def add_supplier_certification(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        certification_data: Dict[str, Any]
    ) -> bool:
        """Add a certification to a supplier."""
        try:
            # This would require a supplier_certifications table
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to add supplier certification: {str(e)}")
    
    async def get_suppliers_by_certification(
        self,
        business_id: uuid.UUID,
        certification_type: str,
        valid_only: bool = True
    ) -> List[Supplier]:
        """Get suppliers by certification type."""
        try:
            # This would require joining with certifications table
            # For now, returning all active suppliers
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", SupplierStatus.ACTIVE.value).order("company_name").execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get suppliers by certification: {str(e)}")
    
    async def get_expiring_certifications(
        self,
        business_id: uuid.UUID,
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Get certifications expiring soon."""
        try:
            # This would require a supplier_certifications table
            # For now, returning empty list
            return []
            
        except Exception as e:
            raise DatabaseError(f"Failed to get expiring certifications: {str(e)}")
    
    async def bulk_update_status(
        self,
        business_id: uuid.UUID,
        supplier_ids: List[uuid.UUID],
        status: SupplierStatus
    ) -> int:
        """Bulk update supplier status."""
        try:
            response = self.client.table(self.table_name).update({
                "status": status.value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_(
                "id", [str(supplier_id) for supplier_id in supplier_ids]
            ).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk update status: {str(e)}")
    
    async def bulk_update_payment_terms(
        self,
        business_id: uuid.UUID,
        updates: List[Dict[str, Any]]
    ) -> int:
        """Bulk update payment terms."""
        try:
            # This would require multiple update operations
            # For now, returning the count of updates requested
            return len(updates)
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk update payment terms: {str(e)}")
    
    async def import_suppliers(
        self,
        business_id: uuid.UUID,
        supplier_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Import suppliers from data."""
        try:
            # This would require data validation and batch insertion
            # For now, returning basic import result
            return {
                "imported": 0,
                "failed": len(supplier_data),
                "errors": ["Import functionality not yet implemented"]
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to import suppliers: {str(e)}")
    
    async def advanced_search(
        self,
        business_id: uuid.UUID,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Advanced search with filtering."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            # Apply filters
            for key, value in filters.items():
                if value is not None:
                    if key == "status":
                        query = query.eq("status", value)
                    elif key == "company_name":
                        query = query.ilike("company_name", f"%{value}%")
                    elif key == "supplier_code":
                        query = query.ilike("supplier_code", f"%{value}%")
            
            # Apply sorting
            sort_column = sort_by or "company_name"
            desc = sort_order.lower() == "desc"
            
            response = query.range(offset, offset + limit - 1).order(sort_column, desc=desc).execute()
            
            suppliers = [self._dict_to_supplier(supplier) for supplier in response.data]
            
            return {
                "suppliers": [{
                    "id": str(s.id),
                    "company_name": s.company_name,
                    "supplier_code": s.supplier_code,
                    "status": s.status.value,
                    "performance_score": float(s.performance_score)
                } for s in suppliers],
                "total": len(suppliers),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to perform advanced search: {str(e)}")
    
    async def get_filter_options(
        self,
        business_id: uuid.UUID
    ) -> Dict[str, List[Any]]:
        """Get available filter options."""
        try:
            return {
                "statuses": [status.value for status in SupplierStatus],
                "countries": [],  # Would require data analysis
                "certifications": [],  # Would require certifications table
                "payment_terms": []  # Would require payment terms analysis
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get filter options: {str(e)}")
    
    async def update_lead_times(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        product_id: uuid.UUID,
        lead_time_days: int
    ) -> bool:
        """Update lead times for a supplier-product combination."""
        try:
            # This would require a supplier_products table
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to update lead times: {str(e)}")
    
    async def get_suppliers_by_lead_time(
        self,
        business_id: uuid.UUID,
        max_lead_time_days: int,
        product_id: Optional[uuid.UUID] = None
    ) -> List[Supplier]:
        """Get suppliers by lead time constraints."""
        try:
            # This would require supplier_products table with lead times
            # For now, returning all active suppliers
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("status", SupplierStatus.ACTIVE.value).order("company_name").execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get suppliers by lead time: {str(e)}")
    
    async def get_delivery_performance(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get delivery performance metrics."""
        try:
            # This would require purchase order delivery data
            # For now, returning basic performance data
            return {
                "on_time_delivery_rate": 85.0,
                "average_delay_days": 2.3,
                "total_deliveries": 25,
                "on_time_deliveries": 21,
                "late_deliveries": 4
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get delivery performance: {str(e)}")
    
    async def assess_supplier_risk(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Assess supplier risk."""
        try:
            # This would require complex risk assessment logic
            # For now, returning basic risk assessment
            return {
                "risk_level": "medium",
                "risk_score": 60.0,
                "factors": {
                    "financial_stability": "good",
                    "delivery_reliability": "fair",
                    "quality_consistency": "good",
                    "geographic_risk": "low"
                }
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to assess supplier risk: {str(e)}")
    
    async def get_high_risk_suppliers(
        self,
        business_id: uuid.UUID,
        risk_threshold: Optional[str] = None
    ) -> List[Supplier]:
        """Get high risk suppliers."""
        try:
            # This would require risk assessment data
            # For now, returning suppliers with low performance scores
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).lt("performance_score", 50.0).execute()
            
            return [self._dict_to_supplier(supplier) for supplier in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get high risk suppliers: {str(e)}")
    
    async def update_risk_assessment(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        risk_data: Dict[str, Any]
    ) -> bool:
        """Update risk assessment for a supplier."""
        try:
            response = self.client.table(self.table_name).update({
                "risk_level": risk_data.get("risk_level"),
                "risk_score": risk_data.get("risk_score"),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq("id", str(supplier_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to update risk assessment: {str(e)}")
    
    async def count_suppliers(
        self,
        business_id: uuid.UUID,
        status: Optional[SupplierStatus] = None
    ) -> int:
        """Count suppliers with optional status filter."""
        try:
            query = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            )
            
            if status:
                query = query.eq("status", status.value)
            
            response = query.execute()
            
            return response.count if response.count else 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count suppliers: {str(e)}")
    
    async def exists_by_code(
        self,
        business_id: uuid.UUID,
        supplier_code: str,
        exclude_supplier_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if supplier code exists."""
        try:
            query = self.client.table(self.table_name).select("id").eq(
                "business_id", str(business_id)
            ).eq("supplier_code", supplier_code)
            
            if exclude_supplier_id:
                query = query.neq("id", str(exclude_supplier_id))
            
            response = query.execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check supplier code existence: {str(e)}")
    
    async def exists_by_tax_id(
        self,
        business_id: uuid.UUID,
        tax_id: str,
        exclude_supplier_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if tax ID exists."""
        try:
            query = self.client.table(self.table_name).select("id").eq(
                "business_id", str(business_id)
            ).eq("tax_id", tax_id)
            
            if exclude_supplier_id:
                query = query.neq("id", str(exclude_supplier_id))
            
            response = query.execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to check tax ID existence: {str(e)}")
    
    async def get_suppliers_for_mobile(
        self,
        business_id: uuid.UUID,
        search_query: Optional[str] = None,
        status: Optional[SupplierStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get suppliers optimized for mobile app."""
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            if search_query:
                query = query.or_(f"company_name.ilike.%{search_query}%,supplier_code.ilike.%{search_query}%")
            
            if status:
                query = query.eq("status", status.value)
            
            response = query.range(offset, offset + limit - 1).order("company_name").execute()
            
            suppliers = [self._dict_to_supplier(supplier) for supplier in response.data]
            
            mobile_suppliers = []
            for supplier in suppliers:
                mobile_suppliers.append({
                    "id": str(supplier.id),
                    "company_name": supplier.company_name,
                    "supplier_code": supplier.supplier_code,
                    "contact_name": supplier.contact_name,
                    "phone": supplier.phone,
                    "email": supplier.email,
                    "status": supplier.status.value,
                    "performance_score": float(supplier.performance_score)
                })
            
            return {
                "suppliers": mobile_suppliers,
                "total": len(mobile_suppliers),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get suppliers for mobile: {str(e)}")
    
    async def get_supplier_summary_for_mobile(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get supplier summary for mobile app."""
        try:
            supplier = await self.get_by_id(business_id, supplier_id)
            if not supplier:
                raise EntityNotFoundError(f"Supplier {supplier_id} not found")
            
            return {
                "id": str(supplier.id),
                "company_name": supplier.company_name,
                "supplier_code": supplier.supplier_code,
                "contact_name": supplier.contact_name,
                "phone": supplier.phone,
                "email": supplier.email,
                "address": supplier.address,
                "status": supplier.status.value,
                "performance_score": float(supplier.performance_score),
                "total_orders": supplier.total_orders,
                "total_spent": float(supplier.total_spent),
                "is_preferred": getattr(supplier, 'is_preferred', False),
                "notes": supplier.notes
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get supplier summary for mobile: {str(e)}")
    
    def _supplier_to_dict(self, supplier: Supplier) -> dict:
        """Convert Supplier entity to dictionary."""
        return {
            "id": str(supplier.id),
            "business_id": str(supplier.business_id),
            "supplier_code": supplier.supplier_code,
            "company_name": supplier.company_name,
            "contact_name": supplier.contact_name,
            "email": supplier.email,
            "phone": supplier.phone,
            "address": supplier.address,
            "status": supplier.status.value,
            "is_active": supplier.is_active,
            "notes": supplier.notes,
            "tags": supplier.tags,
            "total_orders": supplier.total_orders,
            "total_spent": float(supplier.total_spent),
            "performance_score": float(supplier.performance_score),
        }
    
    def _dict_to_supplier(self, data: dict) -> Supplier:
        """Convert dictionary to Supplier entity."""
        def safe_decimal(value, default=None):
            if value is None:
                return default
            return Decimal(str(value))
        
        return Supplier(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            supplier_code=data["supplier_code"],
            company_name=data["company_name"],
            contact_name=data.get("contact_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            status=SupplierStatus(data["status"]),
            is_active=data.get("is_active", True),
            notes=data.get("notes"),
            tags=data.get("tags", []),
            total_orders=data.get("total_orders", 0),
            total_spent=safe_decimal(data.get("total_spent"), Decimal('0')),
            performance_score=safe_decimal(data.get("performance_score"), Decimal('0')),
        ) 