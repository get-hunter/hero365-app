"""
Supplier Repository Interface

Repository interface for supplier management with performance tracking,
relationship management, and analytics capabilities.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime

from ..entities.supplier import Supplier
from ..entities.product_enums.enums import SupplierStatus


class SupplierRepository(ABC):
    """Repository interface for supplier management operations."""
    
    # Basic CRUD operations
    @abstractmethod
    async def create(self, supplier: Supplier) -> Supplier:
        """Create a new supplier."""
        pass
    
    @abstractmethod
    async def get_by_id(self, business_id: uuid.UUID, supplier_id: uuid.UUID) -> Optional[Supplier]:
        """Get supplier by ID."""
        pass
    
    @abstractmethod
    async def get_by_code(self, business_id: uuid.UUID, supplier_code: str) -> Optional[Supplier]:
        """Get supplier by supplier code."""
        pass
    
    @abstractmethod
    async def get_by_tax_id(self, business_id: uuid.UUID, tax_id: str) -> Optional[Supplier]:
        """Get supplier by tax ID."""
        pass
    
    @abstractmethod
    async def update(self, supplier: Supplier) -> Supplier:
        """Update an existing supplier."""
        pass
    
    @abstractmethod
    async def delete(self, business_id: uuid.UUID, supplier_id: uuid.UUID) -> bool:
        """Delete a supplier (only if no active relationships)."""
        pass
    
    # List and search operations
    @abstractmethod
    async def list_by_business(
        self,
        business_id: uuid.UUID,
        status: Optional[SupplierStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Supplier]:
        """List suppliers for a business with optional filtering."""
        pass
    
    @abstractmethod
    async def search_suppliers(
        self,
        business_id: uuid.UUID,
        query: str,
        status: Optional[SupplierStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Supplier]:
        """Search suppliers by name, code, or contact information."""
        pass
    
    @abstractmethod
    async def get_suppliers_by_status(
        self,
        business_id: uuid.UUID,
        status: SupplierStatus
    ) -> List[Supplier]:
        """Get suppliers by status."""
        pass
    
    @abstractmethod
    async def get_suppliers_by_location(
        self,
        business_id: uuid.UUID,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Supplier]:
        """Get suppliers by location."""
        pass
    
    # Product relationship management
    @abstractmethod
    async def get_suppliers_for_product(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        active_only: bool = True
    ) -> List[Supplier]:
        """Get suppliers that provide a specific product."""
        pass
    
    @abstractmethod
    async def get_preferred_suppliers(
        self,
        business_id: uuid.UUID,
        product_id: Optional[uuid.UUID] = None
    ) -> List[Supplier]:
        """Get preferred suppliers for a product or all preferred suppliers."""
        pass
    
    @abstractmethod
    async def get_suppliers_by_product_category(
        self,
        business_id: uuid.UUID,
        category_id: uuid.UUID
    ) -> List[Supplier]:
        """Get suppliers that provide products in a specific category."""
        pass
    
    # Performance tracking and analytics
    @abstractmethod
    async def update_supplier_performance(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        performance_data: Dict[str, Any]
    ) -> bool:
        """Update supplier performance metrics."""
        pass
    
    @abstractmethod
    async def calculate_performance_score(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """Calculate performance score for a supplier."""
        pass
    
    @abstractmethod
    async def get_top_performing_suppliers(
        self,
        business_id: uuid.UUID,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top performing suppliers."""
        pass
    
    @abstractmethod
    async def get_suppliers_needing_review(
        self,
        business_id: uuid.UUID,
        performance_threshold: Optional[Decimal] = None
    ) -> List[Supplier]:
        """Get suppliers that need performance review."""
        pass
    
    @abstractmethod
    async def get_supplier_analytics(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a supplier."""
        pass
    
    # Purchase order integration
    @abstractmethod
    async def get_suppliers_with_pending_orders(
        self,
        business_id: uuid.UUID
    ) -> List[Supplier]:
        """Get suppliers with pending purchase orders."""
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def calculate_supplier_spend(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """Calculate total spend with a supplier."""
        pass
    
    # Contact management
    @abstractmethod
    async def add_supplier_contact(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        contact_data: Dict[str, Any]
    ) -> bool:
        """Add a contact to a supplier."""
        pass
    
    @abstractmethod
    async def update_supplier_contact(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        contact_id: uuid.UUID,
        contact_data: Dict[str, Any]
    ) -> bool:
        """Update a supplier contact."""
        pass
    
    @abstractmethod
    async def remove_supplier_contact(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        contact_id: uuid.UUID
    ) -> bool:
        """Remove a contact from a supplier."""
        pass
    
    @abstractmethod
    async def get_supplier_contacts(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        contact_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get contacts for a supplier."""
        pass
    
    # Payment terms and financial management
    @abstractmethod
    async def update_payment_terms(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        payment_terms: Dict[str, Any]
    ) -> bool:
        """Update payment terms for a supplier."""
        pass
    
    @abstractmethod
    async def get_suppliers_by_payment_terms(
        self,
        business_id: uuid.UUID,
        payment_days: Optional[int] = None,
        has_early_discount: Optional[bool] = None
    ) -> List[Supplier]:
        """Get suppliers by payment terms criteria."""
        pass
    
    @abstractmethod
    async def calculate_early_payment_savings(
        self,
        business_id: uuid.UUID,
        supplier_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate potential early payment savings."""
        pass
    
    # Certification and compliance
    @abstractmethod
    async def add_supplier_certification(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        certification_data: Dict[str, Any]
    ) -> bool:
        """Add a certification to a supplier."""
        pass
    
    @abstractmethod
    async def get_suppliers_by_certification(
        self,
        business_id: uuid.UUID,
        certification_type: str,
        valid_only: bool = True
    ) -> List[Supplier]:
        """Get suppliers with specific certifications."""
        pass
    
    @abstractmethod
    async def get_expiring_certifications(
        self,
        business_id: uuid.UUID,
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Get supplier certifications expiring soon."""
        pass
    
    # Bulk operations
    @abstractmethod
    async def bulk_update_status(
        self,
        business_id: uuid.UUID,
        supplier_ids: List[uuid.UUID],
        status: SupplierStatus
    ) -> int:
        """Bulk update supplier status."""
        pass
    
    @abstractmethod
    async def bulk_update_payment_terms(
        self,
        business_id: uuid.UUID,
        updates: List[Dict[str, Any]]
    ) -> int:
        """Bulk update supplier payment terms."""
        pass
    
    @abstractmethod
    async def import_suppliers(
        self,
        business_id: uuid.UUID,
        supplier_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Import suppliers from external data."""
        pass
    
    # Advanced search and filtering
    @abstractmethod
    async def advanced_search(
        self,
        business_id: uuid.UUID,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Advanced supplier search with multiple filters."""
        pass
    
    @abstractmethod
    async def get_filter_options(
        self,
        business_id: uuid.UUID
    ) -> Dict[str, List[Any]]:
        """Get available filter options for supplier search."""
        pass
    
    # Lead time and delivery management
    @abstractmethod
    async def update_lead_times(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        product_id: uuid.UUID,
        lead_time_days: int
    ) -> bool:
        """Update lead time for a product from a supplier."""
        pass
    
    @abstractmethod
    async def get_suppliers_by_lead_time(
        self,
        business_id: uuid.UUID,
        max_lead_time_days: int,
        product_id: Optional[uuid.UUID] = None
    ) -> List[Supplier]:
        """Get suppliers with lead times within specified range."""
        pass
    
    @abstractmethod
    async def get_delivery_performance(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get delivery performance metrics for a supplier."""
        pass
    
    # Risk management
    @abstractmethod
    async def assess_supplier_risk(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Assess risk factors for a supplier."""
        pass
    
    @abstractmethod
    async def get_high_risk_suppliers(
        self,
        business_id: uuid.UUID,
        risk_threshold: Optional[str] = None
    ) -> List[Supplier]:
        """Get suppliers with high risk factors."""
        pass
    
    @abstractmethod
    async def update_risk_assessment(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        risk_data: Dict[str, Any]
    ) -> bool:
        """Update risk assessment for a supplier."""
        pass
    
    # Count operations
    @abstractmethod
    async def count_suppliers(
        self,
        business_id: uuid.UUID,
        status: Optional[SupplierStatus] = None
    ) -> int:
        """Count suppliers with optional filtering."""
        pass
    
    @abstractmethod
    async def exists_by_code(
        self,
        business_id: uuid.UUID,
        supplier_code: str,
        exclude_supplier_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if a supplier with the given code exists."""
        pass
    
    @abstractmethod
    async def exists_by_tax_id(
        self,
        business_id: uuid.UUID,
        tax_id: str,
        exclude_supplier_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if a supplier with the given tax ID exists."""
        pass
    
    # Mobile app optimization
    @abstractmethod
    async def get_suppliers_for_mobile(
        self,
        business_id: uuid.UUID,
        search_query: Optional[str] = None,
        status: Optional[SupplierStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get suppliers optimized for mobile app consumption."""
        pass
    
    @abstractmethod
    async def get_supplier_summary_for_mobile(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get supplier summary optimized for mobile display."""
        pass 