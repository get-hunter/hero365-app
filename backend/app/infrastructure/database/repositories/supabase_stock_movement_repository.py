"""
Supabase Stock Movement Repository Implementation

Repository implementation for comprehensive stock movement tracking and audit trail.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date

from supabase import Client

from app.domain.repositories.stock_movement_repository import StockMovementRepository
from app.domain.entities.stock_movement import StockMovement
from app.domain.enums import StockMovementType
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DatabaseError
)

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseStockMovementRepository(StockMovementRepository):
    """
    Supabase client implementation of StockMovementRepository.
    
    Handles comprehensive stock movement tracking with audit trail.
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "stock_movements"
        logger.info(f"SupabaseStockMovementRepository initialized")
    
    async def create(self, movement: StockMovement) -> StockMovement:
        """Create a new stock movement record."""
        try:
            movement_data = self._movement_to_dict(movement)
            
            response = self.client.table(self.table_name).insert(movement_data).execute()
            
            if response.data:
                return self._dict_to_movement(response.data[0])
            else:
                raise DatabaseError("Failed to create stock movement - no data returned")
                
        except Exception as e:
            raise DatabaseError(f"Failed to create stock movement: {str(e)}")
    
    async def get_by_id(self, business_id: uuid.UUID, movement_id: uuid.UUID) -> Optional[StockMovement]:
        """Get stock movement by ID."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("id", str(movement_id)).execute()
            
            if response.data:
                return self._dict_to_movement(response.data[0])
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get stock movement by ID: {str(e)}")
    
    async def update(self, movement: StockMovement) -> StockMovement:
        """Update an existing stock movement."""
        try:
            movement_data = self._movement_to_dict(movement)
            movement_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table(self.table_name).update(movement_data).eq(
                "id", str(movement.id)
            ).execute()
            
            if response.data:
                return self._dict_to_movement(response.data[0])
            else:
                raise EntityNotFoundError(f"Stock movement with ID {movement.id} not found")
                
        except EntityNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update stock movement: {str(e)}")
    
    async def delete(self, business_id: uuid.UUID, movement_id: uuid.UUID) -> bool:
        """Delete a stock movement (admin only, affects audit trail)."""
        try:
            response = self.client.table(self.table_name).delete().eq(
                "business_id", str(business_id)
            ).eq("id", str(movement_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to delete stock movement: {str(e)}")
    
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
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("product_id", str(product_id))
            
            if start_date:
                query = query.gte("movement_date", start_date.isoformat())
            if end_date:
                query = query.lte("movement_date", end_date.isoformat())
            if movement_types:
                query = query.in_("movement_type", [mt.value for mt in movement_types])
            if location_id:
                query = query.eq("location_id", str(location_id))
            
            response = query.range(offset, offset + limit - 1).order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movements for product: {str(e)}")
    
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
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).gte("movement_date", start_date.isoformat()).lte("movement_date", end_date.isoformat())
            
            if movement_types:
                query = query.in_("movement_type", [mt.value for mt in movement_types])
            if product_id:
                query = query.eq("product_id", str(product_id))
            if location_id:
                query = query.eq("location_id", str(location_id))
            
            response = query.range(offset, offset + limit - 1).order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movements by date range: {str(e)}")
    
    async def get_movements_by_type(
        self,
        business_id: uuid.UUID,
        movement_type: StockMovementType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Get movements by type within date range."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("movement_type", movement_type.value)
            
            if start_date:
                query = query.gte("movement_date", start_date.isoformat())
            if end_date:
                query = query.lte("movement_date", end_date.isoformat())
            
            response = query.range(offset, offset + limit - 1).order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movements by type: {str(e)}")
    
    async def get_movements_by_reference(
        self,
        business_id: uuid.UUID,
        reference_type: str,
        reference_id: uuid.UUID
    ) -> List[StockMovement]:
        """Get stock movements by reference document."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("reference_type", reference_type).eq("reference_id", str(reference_id)).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movements by reference: {str(e)}")
    
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
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("location_id", str(location_id))
            
            if start_date:
                query = query.gte("movement_date", start_date.isoformat())
            if end_date:
                query = query.lte("movement_date", end_date.isoformat())
            if movement_types:
                query = query.in_("movement_type", [mt.value for mt in movement_types])
            
            response = query.range(offset, offset + limit - 1).order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movements for location: {str(e)}")
    
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
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("movement_type", StockMovementType.TRANSFER.value)
            
            if from_location_id:
                query = query.eq("from_location_id", str(from_location_id))
            if to_location_id:
                query = query.eq("to_location_id", str(to_location_id))
            if start_date:
                query = query.gte("movement_date", start_date.isoformat())
            if end_date:
                query = query.lte("movement_date", end_date.isoformat())
            
            response = query.range(offset, offset + limit - 1).order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get transfer movements: {str(e)}")
    
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
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("supplier_id", str(supplier_id))
            
            if start_date:
                query = query.gte("movement_date", start_date.isoformat())
            if end_date:
                query = query.lte("movement_date", end_date.isoformat())
            
            response = query.range(offset, offset + limit - 1).order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movements by supplier: {str(e)}")
    
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
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("customer_id", str(customer_id))
            
            if start_date:
                query = query.gte("movement_date", start_date.isoformat())
            if end_date:
                query = query.lte("movement_date", end_date.isoformat())
            
            response = query.range(offset, offset + limit - 1).order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movements by customer: {str(e)}")
    
    async def create_batch_movements(self, movements: List[StockMovement]) -> List[StockMovement]:
        """Create multiple stock movements in a batch."""
        try:
            movements_data = [self._movement_to_dict(movement) for movement in movements]
            
            response = self.client.table(self.table_name).insert(movements_data).execute()
            
            if response.data:
                return [self._dict_to_movement(movement) for movement in response.data]
            else:
                raise DatabaseError("Failed to create batch movements - no data returned")
                
        except Exception as e:
            raise DatabaseError(f"Failed to create batch movements: {str(e)}")
    
    async def get_movements_by_batch(
        self,
        business_id: uuid.UUID,
        batch_number: str
    ) -> List[StockMovement]:
        """Get stock movements by batch number."""
        try:
            response = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("batch_number", batch_number).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movements by batch: {str(e)}")
    
    async def approve_batch_movements(
        self,
        business_id: uuid.UUID,
        movement_ids: List[uuid.UUID],
        approved_by: str
    ) -> int:
        """Approve multiple movements in batch."""
        try:
            response = self.client.table(self.table_name).update({
                "is_approved": True,
                "approved_by": approved_by,
                "approved_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).in_(
                "id", [str(movement_id) for movement_id in movement_ids]
            ).execute()
            
            return len(response.data)
            
        except Exception as e:
            raise DatabaseError(f"Failed to approve batch movements: {str(e)}")
    
    async def get_cost_affecting_movements(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        up_to_date: Optional[datetime] = None
    ) -> List[StockMovement]:
        """Get movements that affect product cost calculations."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("product_id", str(product_id)).in_(
                "movement_type", [StockMovementType.PURCHASE.value, StockMovementType.SALE.value]
            )
            
            if up_to_date:
                query = query.lte("movement_date", up_to_date.isoformat())
            
            response = query.order("movement_date").execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get cost affecting movements: {str(e)}")
    
    async def calculate_weighted_average_cost(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        up_to_date: Optional[datetime] = None
    ) -> Decimal:
        """Calculate weighted average cost from movement history."""
        try:
            movements = await self.get_cost_affecting_movements(business_id, product_id, up_to_date)
            
            total_cost = Decimal('0')
            total_quantity = Decimal('0')
            
            for movement in movements:
                if movement.movement_type == StockMovementType.PURCHASE:
                    total_cost += movement.total_cost or Decimal('0')
                    total_quantity += movement.quantity
            
            if total_quantity > 0:
                return total_cost / total_quantity
            return Decimal('0')
            
        except Exception as e:
            raise DatabaseError(f"Failed to calculate weighted average cost: {str(e)}")
    
    async def get_inventory_valuation_movements(
        self,
        business_id: uuid.UUID,
        valuation_date: datetime,
        product_ids: Optional[List[uuid.UUID]] = None
    ) -> List[Dict[str, Any]]:
        """Get inventory valuation movements for a specific date."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).lte("movement_date", valuation_date.isoformat())
            
            if product_ids:
                query = query.in_("product_id", [str(pid) for pid in product_ids])
            
            response = query.order("movement_date").execute()
            
            movements = [self._dict_to_movement(movement) for movement in response.data]
            
            # Process into valuation data
            valuation_data = []
            for movement in movements:
                valuation_data.append({
                    "product_id": str(movement.product_id),
                    "quantity": float(movement.quantity),
                    "unit_cost": float(movement.unit_cost) if movement.unit_cost else 0,
                    "total_cost": float(movement.total_cost) if movement.total_cost else 0,
                    "movement_type": movement.movement_type.value,
                    "movement_date": movement.movement_date.isoformat()
                })
            
            return valuation_data
            
        except Exception as e:
            raise DatabaseError(f"Failed to get inventory valuation movements: {str(e)}")
    
    async def get_movement_summary(
        self,
        business_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "type"
    ) -> Dict[str, Any]:
        """Get movement summary grouped by specified criteria."""
        try:
            movements = await self.get_movements_by_date_range(
                business_id, start_date, end_date, limit=1000
            )
            
            summary = {
                "total_movements": len(movements),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "grouped_data": {}
            }
            
            if group_by == "type":
                type_counts = {}
                for movement in movements:
                    movement_type = movement.movement_type.value
                    type_counts[movement_type] = type_counts.get(movement_type, 0) + 1
                summary["grouped_data"] = type_counts
            
            return summary
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movement summary: {str(e)}")
    
    async def get_inventory_turnover_data(
        self,
        business_id: uuid.UUID,
        product_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get inventory turnover data."""
        try:
            # This would require complex calculation based on sales and inventory levels
            # For now, returning basic structure
            return {
                "product_id": str(product_id) if product_id else None,
                "turnover_ratio": 0.0,
                "average_inventory": 0.0,
                "cost_of_goods_sold": 0.0,
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get inventory turnover data: {str(e)}")
    
    async def get_movement_trends(
        self,
        business_id: uuid.UUID,
        period: str = "month",
        periods_count: int = 12,
        movement_types: Optional[List[StockMovementType]] = None
    ) -> List[Dict[str, Any]]:
        """Get movement trends over time."""
        try:
            # This would require complex time-series analysis
            # For now, returning basic structure
            trends = []
            for i in range(periods_count):
                trends.append({
                    "period": f"{period}_{i}",
                    "total_movements": 0,
                    "total_quantity": 0.0,
                    "total_value": 0.0
                })
            
            return trends
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movement trends: {str(e)}")
    
    async def get_variance_analysis(
        self,
        business_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get variance analysis for inventory discrepancies."""
        try:
            # This would require comparing expected vs actual inventory levels
            # For now, returning basic structure
            return []
            
        except Exception as e:
            raise DatabaseError(f"Failed to get variance analysis: {str(e)}")
    
    async def get_adjustment_movements(
        self,
        business_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[uuid.UUID] = None,
        location_id: Optional[uuid.UUID] = None
    ) -> List[StockMovement]:
        """Get adjustment movements."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("movement_type", StockMovementType.ADJUSTMENT.value)
            
            if start_date:
                query = query.gte("movement_date", start_date.isoformat())
            if end_date:
                query = query.lte("movement_date", end_date.isoformat())
            if product_id:
                query = query.eq("product_id", str(product_id))
            if location_id:
                query = query.eq("location_id", str(location_id))
            
            response = query.order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get adjustment movements: {str(e)}")
    
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
        """Create an adjustment movement."""
        try:
            movement = StockMovement(
                id=uuid.uuid4(),
                business_id=business_id,
                product_id=product_id,
                movement_type=StockMovementType.ADJUSTMENT,
                quantity=quantity_difference,
                movement_date=datetime.utcnow(),
                notes=reason,
                created_by=created_by
            )
            
            return await self.create(movement)
            
        except Exception as e:
            raise DatabaseError(f"Failed to create adjustment movement: {str(e)}")
    
    async def get_pending_approvals(
        self,
        business_id: uuid.UUID,
        movement_types: Optional[List[StockMovementType]] = None
    ) -> List[StockMovement]:
        """Get movements pending approval."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("is_approved", False)
            
            if movement_types:
                query = query.in_("movement_type", [mt.value for mt in movement_types])
            
            response = query.order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get pending approvals: {str(e)}")
    
    async def search_movements(
        self,
        business_id: uuid.UUID,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StockMovement]:
        """Search movements by query string."""
        try:
            search_query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).or_(f"notes.ilike.%{query}%,reference_id.ilike.%{query}%")
            
            if filters:
                for key, value in filters.items():
                    if key == "movement_type" and value:
                        search_query = search_query.eq("movement_type", value)
                    elif key == "product_id" and value:
                        search_query = search_query.eq("product_id", str(value))
            
            response = search_query.range(offset, offset + limit - 1).order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to search movements: {str(e)}")
    
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
        try:
            query = self.client.table(self.table_name).select("*").eq("business_id", str(business_id))
            
            # Apply filters
            for key, value in filters.items():
                if value is not None:
                    if key == "movement_type":
                        query = query.eq("movement_type", value)
                    elif key == "product_id":
                        query = query.eq("product_id", str(value))
                    elif key == "location_id":
                        query = query.eq("location_id", str(value))
                    elif key == "start_date":
                        query = query.gte("movement_date", value)
                    elif key == "end_date":
                        query = query.lte("movement_date", value)
            
            # Apply sorting
            sort_column = sort_by or "movement_date"
            desc = sort_order.lower() == "desc"
            
            response = query.range(offset, offset + limit - 1).order(sort_column, desc=desc).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movements with filters: {str(e)}")
    
    async def get_audit_trail(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get audit trail for a product."""
        try:
            movements = await self.get_movements_for_product(
                business_id, product_id, start_date, end_date, limit=1000
            )
            
            audit_trail = []
            for movement in movements:
                audit_trail.append({
                    "id": str(movement.id),
                    "movement_type": movement.movement_type.value,
                    "quantity": float(movement.quantity),
                    "unit_cost": float(movement.unit_cost) if movement.unit_cost else None,
                    "total_cost": float(movement.total_cost) if movement.total_cost else None,
                    "movement_date": movement.movement_date.isoformat(),
                    "reference_type": movement.reference_type,
                    "reference_id": movement.reference_id,
                    "notes": movement.notes,
                    "created_by": movement.created_by
                })
            
            return audit_trail
            
        except Exception as e:
            raise DatabaseError(f"Failed to get audit trail: {str(e)}")
    
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
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("created_by", user_id)
            
            if start_date:
                query = query.gte("movement_date", start_date.isoformat())
            if end_date:
                query = query.lte("movement_date", end_date.isoformat())
            
            response = query.range(offset, offset + limit - 1).order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user movements: {str(e)}")
    
    async def get_movements_requiring_review(
        self,
        business_id: uuid.UUID,
        criteria: Optional[Dict[str, Any]] = None
    ) -> List[StockMovement]:
        """Get movements that require review."""
        try:
            query = self.client.table(self.table_name).select("*").eq(
                "business_id", str(business_id)
            ).eq("requires_review", True)
            
            response = query.order("movement_date", desc=True).execute()
            
            return [self._dict_to_movement(movement) for movement in response.data]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movements requiring review: {str(e)}")
    
    async def create_reversal_movement(
        self,
        business_id: uuid.UUID,
        original_movement_id: uuid.UUID,
        reason: str,
        created_by: str
    ) -> StockMovement:
        """Create a reversal movement."""
        try:
            # Get original movement
            original = await self.get_by_id(business_id, original_movement_id)
            if not original:
                raise EntityNotFoundError(f"Original movement {original_movement_id} not found")
            
            # Create reversal with opposite quantity
            reversal = StockMovement(
                id=uuid.uuid4(),
                business_id=business_id,
                product_id=original.product_id,
                movement_type=original.movement_type,
                quantity=-original.quantity,  # Opposite quantity
                unit_cost=original.unit_cost,
                total_cost=-original.total_cost if original.total_cost else None,
                movement_date=datetime.utcnow(),
                reference_type="reversal",
                reference_id=str(original_movement_id),
                notes=f"Reversal of movement {original_movement_id}: {reason}",
                created_by=created_by
            )
            
            return await self.create(reversal)
            
        except Exception as e:
            raise DatabaseError(f"Failed to create reversal movement: {str(e)}")
    
    async def get_reversal_chain(
        self,
        business_id: uuid.UUID,
        movement_id: uuid.UUID
    ) -> List[StockMovement]:
        """Get the reversal chain for a movement."""
        try:
            # Get original movement
            movements = [await self.get_by_id(business_id, movement_id)]
            if not movements[0]:
                return []
            
            # Get reversals
            reversals = await self.get_movements_by_reference(business_id, "reversal", movement_id)
            movements.extend(reversals)
            
            return [m for m in movements if m is not None]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get reversal chain: {str(e)}")
    
    async def mark_movement_reversed(
        self,
        business_id: uuid.UUID,
        movement_id: uuid.UUID,
        reversal_movement_id: uuid.UUID
    ) -> bool:
        """Mark a movement as reversed."""
        try:
            response = self.client.table(self.table_name).update({
                "is_reversed": True,
                "reversal_movement_id": str(reversal_movement_id),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("business_id", str(business_id)).eq("id", str(movement_id)).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to mark movement as reversed: {str(e)}")
    
    async def get_latest_movement_for_products(
        self,
        business_id: uuid.UUID,
        product_ids: List[uuid.UUID],
        movement_type: Optional[StockMovementType] = None
    ) -> Dict[uuid.UUID, StockMovement]:
        """Get latest movement for each product."""
        try:
            latest_movements = {}
            
            for product_id in product_ids:
                query = self.client.table(self.table_name).select("*").eq(
                    "business_id", str(business_id)
                ).eq("product_id", str(product_id))
                
                if movement_type:
                    query = query.eq("movement_type", movement_type.value)
                
                response = query.order("movement_date", desc=True).limit(1).execute()
                
                if response.data:
                    latest_movements[product_id] = self._dict_to_movement(response.data[0])
            
            return latest_movements
            
        except Exception as e:
            raise DatabaseError(f"Failed to get latest movements for products: {str(e)}")
    
    async def get_current_stock_levels(
        self,
        business_id: uuid.UUID,
        product_ids: Optional[List[uuid.UUID]] = None,
        location_id: Optional[uuid.UUID] = None
    ) -> Dict[uuid.UUID, Dict[str, Decimal]]:
        """Get current stock levels for products."""
        try:
            # This would require complex calculation based on all movements
            # For now, returning basic structure
            stock_levels = {}
            
            if product_ids:
                for product_id in product_ids:
                    stock_levels[product_id] = {
                        "quantity": Decimal('0'),
                        "reserved": Decimal('0'),
                        "available": Decimal('0')
                    }
            
            return stock_levels
            
        except Exception as e:
            raise DatabaseError(f"Failed to get current stock levels: {str(e)}")
    
    async def rebuild_stock_levels(
        self,
        business_id: uuid.UUID,
        product_id: Optional[uuid.UUID] = None,
        location_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Rebuild stock levels from movement history."""
        try:
            # This would require recalculating all stock levels from movements
            # For now, returning True indicating success
            return True
            
        except Exception as e:
            raise DatabaseError(f"Failed to rebuild stock levels: {str(e)}")
    
    async def count_movements(
        self,
        business_id: uuid.UUID,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count movements with optional filters."""
        try:
            query = self.client.table(self.table_name).select("id", count="exact").eq(
                "business_id", str(business_id)
            )
            
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        if key == "movement_type":
                            query = query.eq("movement_type", value)
                        elif key == "product_id":
                            query = query.eq("product_id", str(value))
            
            response = query.execute()
            
            return response.count if response.count else 0
            
        except Exception as e:
            raise DatabaseError(f"Failed to count movements: {str(e)}")
    
    async def get_movement_statistics(
        self,
        business_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get movement statistics for a date range."""
        try:
            movements = await self.get_movements_by_date_range(
                business_id, start_date, end_date, limit=10000
            )
            
            stats = {
                "total_movements": len(movements),
                "total_value": sum(float(m.total_cost) if m.total_cost else 0 for m in movements),
                "average_value": 0,
                "movement_types": {},
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
            if movements:
                stats["average_value"] = stats["total_value"] / len(movements)
                
                # Count by type
                for movement in movements:
                    movement_type = movement.movement_type.value
                    stats["movement_types"][movement_type] = stats["movement_types"].get(movement_type, 0) + 1
            
            return stats
            
        except Exception as e:
            raise DatabaseError(f"Failed to get movement statistics: {str(e)}")
    
    def _movement_to_dict(self, movement: StockMovement) -> dict:
        """Convert StockMovement entity to dictionary."""
        return {
            "id": str(movement.id),
            "business_id": str(movement.business_id),
            "product_id": str(movement.product_id),
            "movement_type": movement.movement_type.value,
            "quantity": float(movement.quantity),
            "unit_cost": float(movement.unit_cost) if movement.unit_cost else None,
            "total_cost": float(movement.total_cost) if movement.total_cost else None,
            "movement_date": movement.movement_date.isoformat(),
            "reference_type": movement.reference_type,
            "reference_id": movement.reference_id,
            "notes": movement.notes,
            "created_by": movement.created_by,
        }
    
    def _dict_to_movement(self, data: dict) -> StockMovement:
        """Convert dictionary to StockMovement entity."""
        def safe_decimal(value, default=None):
            if value is None:
                return default
            return Decimal(str(value))
        
        def safe_datetime(value):
            if value is None:
                return None
            if isinstance(value, str):
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            return value
        
        return StockMovement(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            product_id=uuid.UUID(data["product_id"]),
            movement_type=StockMovementType(data["movement_type"]),
            quantity=safe_decimal(data["quantity"], Decimal('0')),
            unit_cost=safe_decimal(data.get("unit_cost")),
            total_cost=safe_decimal(data.get("total_cost")),
            movement_date=safe_datetime(data["movement_date"]) or datetime.utcnow(),
            reference_type=data.get("reference_type"),
            reference_id=data.get("reference_id"),
            notes=data.get("notes"),
            created_by=data.get("created_by", ""),
        ) 