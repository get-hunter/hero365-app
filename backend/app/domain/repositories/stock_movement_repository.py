"""
Stock Movement Repository Interface

Repository interface for stock movement management with comprehensive audit trail,
inventory tracking, and analytics capabilities.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime, date

from ..entities.stock_movement import StockMovement
from ..entities.product_enums.enums import StockMovementType


class StockMovementRepository(ABC):
    """Repository interface for stock movement management operations."""
    
    # Basic CRUD operations
    @abstractmethod
    async def create(self, movement: StockMovement) -> StockMovement:
        """Create a new stock movement."""
        pass
    
    @abstractmethod
    async def get_by_id(self, business_id: uuid.UUID, movement_id: uuid.UUID) -> Optional[StockMovement]:
        """Get stock movement by ID."""
        pass
    
    @abstractmethod
    async def update(self, movement: StockMovement) -> StockMovement:
        """Update an existing stock movement."""
        pass
    
    @abstractmethod
    async def delete(self, business_id: uuid.UUID, movement_id: uuid.UUID) -> bool:
        """Delete a stock movement (admin only, affects audit trail)."""
        pass
    
    # Movement tracking and audit trail
    @abstractmethod
    async def get_movements_for_product(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        movement_types: Optional[List[StockMovementType]] = None,
        location_id: Optional[uuid.UUID] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Get stock movements for a specific product."""
        pass
    
    @abstractmethod
    async def get_movements_by_date_range(
        self,
        business_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
        movement_types: Optional[List[StockMovementType]] = None,
        product_id: Optional[uuid.UUID] = None,
        location_id: Optional[uuid.UUID] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Get stock movements within a date range."""
        pass
    
    @abstractmethod
    async def get_movements_by_type(
        self,
        business_id: uuid.UUID,
        movement_type: StockMovementType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Get stock movements by type."""
        pass
    
    @abstractmethod
    async def get_movements_by_reference(
        self,
        business_id: uuid.UUID,
        reference_type: str,
        reference_id: uuid.UUID
    ) -> List[StockMovement]:
        """Get stock movements by reference document."""
        pass
    
    # Location-based tracking
    @abstractmethod
    async def get_movements_for_location(
        self,
        business_id: uuid.UUID,
        location_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        movement_types: Optional[List[StockMovementType]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Get stock movements for a specific location."""
        pass
    
    @abstractmethod
    async def get_transfer_movements(
        self,
        business_id: uuid.UUID,
        from_location_id: Optional[uuid.UUID] = None,
        to_location_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Get transfer movements between locations."""
        pass
    
    # Supplier and customer tracking
    @abstractmethod
    async def get_movements_by_supplier(
        self,
        business_id: uuid.UUID,
        supplier_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Get stock movements from a specific supplier."""
        pass
    
    @abstractmethod
    async def get_movements_by_customer(
        self,
        business_id: uuid.UUID,
        customer_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Get stock movements to a specific customer."""
        pass
    
    # Batch processing and bulk operations
    @abstractmethod
    async def create_batch_movements(self, movements: List[StockMovement]) -> List[StockMovement]:
        """Create multiple stock movements in a batch."""
        pass
    
    @abstractmethod
    async def get_movements_by_batch(
        self,
        business_id: uuid.UUID,
        batch_number: str
    ) -> List[StockMovement]:
        """Get stock movements by batch number."""
        pass
    
    @abstractmethod
    async def approve_batch_movements(
        self,
        business_id: uuid.UUID,
        movement_ids: List[uuid.UUID],
        approved_by: str
    ) -> int:
        """Approve multiple movements in batch."""
        pass
    
    # Cost tracking and valuation
    @abstractmethod
    async def get_cost_affecting_movements(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        up_to_date: Optional[datetime] = None
    ) -> List[StockMovement]:
        """Get movements that affect product cost calculations."""
        pass
    
    @abstractmethod
    async def calculate_weighted_average_cost(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        up_to_date: Optional[datetime] = None
    ) -> Decimal:
        """Calculate weighted average cost from movement history."""
        pass
    
    @abstractmethod
    async def get_inventory_valuation_movements(
        self,
        business_id: uuid.UUID,
        valuation_date: datetime,
        product_ids: Optional[List[uuid.UUID]] = None
    ) -> List[Dict[str, Any]]:
        """Get movements for inventory valuation at a specific date."""
        pass
    
    # Analytics and reporting
    @abstractmethod
    async def get_movement_summary(
        self,
        business_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "type"  # type, product, location, date
    ) -> Dict[str, Any]:
        """Get movement summary analytics."""
        pass
    
    @abstractmethod
    async def get_inventory_turnover_data(
        self,
        business_id: uuid.UUID,
        product_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get inventory turnover analytics."""
        pass
    
    @abstractmethod
    async def get_movement_trends(
        self,
        business_id: uuid.UUID,
        period: str = "month",  # day, week, month, quarter
        periods_count: int = 12,
        movement_types: Optional[List[StockMovementType]] = None
    ) -> List[Dict[str, Any]]:
        """Get movement trends over time."""
        pass
    
    @abstractmethod
    async def get_variance_analysis(
        self,
        business_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get inventory variance analysis."""
        pass
    
    # Reconciliation and adjustments
    @abstractmethod
    async def get_adjustment_movements(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[uuid.UUID] = None,
        location_id: Optional[uuid.UUID] = None
    ) -> List[StockMovement]:
        """Get inventory adjustment movements."""
        pass
    
    @abstractmethod
    async def create_adjustment_movement(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity_difference: Decimal,
        reason: str,
        location_id: Optional[uuid.UUID] = None,
        created_by: str = "",
        reference_data: Optional[Dict[str, Any]] = None
    ) -> StockMovement:
        """Create an inventory adjustment movement."""
        pass
    
    @abstractmethod
    async def get_pending_approvals(
        self,
        business_id: uuid.UUID,
        movement_types: Optional[List[StockMovementType]] = None
    ) -> List[StockMovement]:
        """Get movements pending approval."""
        pass
    
    # Search and filtering
    @abstractmethod
    async def search_movements(
        self,
        business_id: uuid.UUID,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Search stock movements by various criteria."""
        pass
    
    @abstractmethod
    async def get_movements_with_filters(
        self,
        business_id: uuid.UUID,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Get movements with advanced filtering."""
        pass
    
    # Audit and compliance
    @abstractmethod
    async def get_audit_trail(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get complete audit trail for a product."""
        pass
    
    @abstractmethod
    async def get_user_movements(
        self,
        business_id: uuid.UUID,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Get movements created by a specific user."""
        pass
    
    @abstractmethod
    async def get_movements_requiring_review(
        self,
        business_id: uuid.UUID,
        criteria: Optional[Dict[str, Any]] = None
    ) -> List[StockMovement]:
        """Get movements that require review based on business rules."""
        pass
    
    # Reversal and correction
    @abstractmethod
    async def create_reversal_movement(
        self,
        business_id: uuid.UUID,
        original_movement_id: uuid.UUID,
        reason: str,
        created_by: str
    ) -> StockMovement:
        """Create a reversal movement for an existing movement."""
        pass
    
    @abstractmethod
    async def get_reversal_chain(
        self,
        business_id: uuid.UUID,
        movement_id: uuid.UUID
    ) -> List[StockMovement]:
        """Get the complete reversal chain for a movement."""
        pass
    
    @abstractmethod
    async def mark_movement_reversed(
        self,
        business_id: uuid.UUID,
        movement_id: uuid.UUID,
        reversal_movement_id: uuid.UUID
    ) -> bool:
        """Mark a movement as reversed."""
        pass
    
    # Performance and optimization
    @abstractmethod
    async def get_latest_movement_for_products(
        self,
        business_id: uuid.UUID,
        product_ids: List[uuid.UUID],
        movement_type: Optional[StockMovementType] = None
    ) -> Dict[uuid.UUID, StockMovement]:
        """Get latest movement for each product."""
        pass
    
    @abstractmethod
    async def get_current_stock_levels(
        self,
        business_id: uuid.UUID,
        product_ids: Optional[List[uuid.UUID]] = None,
        location_id: Optional[uuid.UUID] = None
    ) -> Dict[uuid.UUID, Dict[str, Decimal]]:
        """Get current stock levels calculated from movements."""
        pass
    
    @abstractmethod
    async def rebuild_stock_levels(
        self,
        business_id: uuid.UUID,
        product_id: Optional[uuid.UUID] = None,
        location_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Rebuild stock levels from movement history."""
        pass
    
    # Count operations
    @abstractmethod
    async def count_movements(
        self,
        business_id: uuid.UUID,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count movements with optional filtering."""
        pass
    
    @abstractmethod
    async def get_movement_statistics(
        self,
        business_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get movement statistics for a date range."""
        pass 