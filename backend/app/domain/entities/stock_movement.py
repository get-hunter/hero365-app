"""
Stock Movement Domain Entity

Represents a stock movement transaction for comprehensive inventory tracking
and audit trail maintenance.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, Field, validator, computed_field

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError
from .product_enums.enums import StockMovementType
from ..shared.enums import CurrencyCode

# Configure logging
logger = logging.getLogger(__name__)


class StockMovementContext(BaseModel):
    """Additional context information for the stock movement."""
    reference_type: Optional[str] = Field(None, max_length=50, description="Type of reference document")
    reference_id: Optional[uuid.UUID] = Field(None, description="Reference document ID")
    reference_number: Optional[str] = Field(None, max_length=100, description="Reference document number")
    batch_number: Optional[str] = Field(None, max_length=100, description="Batch or lot number")
    serial_numbers: Optional[list[str]] = Field(None, description="Serial numbers for tracked items")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date for perishable items")
    
    class Config:
        use_enum_values = True


class StockMovement(BaseModel):
    """
    Stock Movement domain entity.
    
    Represents an inventory movement transaction with complete audit trail
    and business logic for cost tracking and validation.
    """
    
    # Basic movement information
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Movement unique identifier")
    business_id: uuid.UUID = Field(..., description="Business identifier")
    product_id: uuid.UUID = Field(..., description="Product identifier")
    location_id: Optional[uuid.UUID] = Field(None, description="Location identifier")
    
    # Movement details
    movement_type: StockMovementType = Field(..., description="Type of stock movement")
    quantity: Decimal = Field(..., description="Quantity moved (positive for increases, negative for decreases)")
    unit_cost: Decimal = Field(default=Decimal('0'), ge=0, description="Unit cost at time of movement")
    total_cost: Decimal = Field(default=Decimal('0'), description="Total cost of movement")
    currency: CurrencyCode = Field(default=CurrencyCode.USD, description="Currency code")
    
    # Before and after snapshots
    quantity_before: Decimal = Field(default=Decimal('0'), ge=0, description="Quantity before movement")
    quantity_after: Decimal = Field(default=Decimal('0'), ge=0, description="Quantity after movement")
    cost_before: Decimal = Field(default=Decimal('0'), ge=0, description="Unit cost before movement")
    cost_after: Decimal = Field(default=Decimal('0'), ge=0, description="Unit cost after movement")
    
    # Context and references
    context: StockMovementContext = Field(default_factory=StockMovementContext, description="Movement context")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for movement")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    # Location details
    from_location_id: Optional[uuid.UUID] = Field(None, description="Source location for transfers")
    to_location_id: Optional[uuid.UUID] = Field(None, description="Destination location for transfers")
    from_location_name: Optional[str] = Field(None, max_length=200, description="Source location name")
    to_location_name: Optional[str] = Field(None, max_length=200, description="Destination location name")
    
    # Supplier information (for purchases)
    supplier_id: Optional[uuid.UUID] = Field(None, description="Supplier identifier")
    supplier_name: Optional[str] = Field(None, max_length=200, description="Supplier name")
    supplier_invoice_number: Optional[str] = Field(None, max_length=100, description="Supplier invoice number")
    
    # Customer information (for sales)
    customer_id: Optional[uuid.UUID] = Field(None, description="Customer identifier")
    customer_name: Optional[str] = Field(None, max_length=200, description="Customer name")
    
    # Financial tracking
    landed_cost: Optional[Decimal] = Field(None, ge=0, description="Total landed cost including shipping, duties")
    shipping_cost: Optional[Decimal] = Field(None, ge=0, description="Shipping cost")
    duty_cost: Optional[Decimal] = Field(None, ge=0, description="Duty/customs cost")
    other_costs: Optional[Decimal] = Field(None, ge=0, description="Other associated costs")
    
    # Metadata
    movement_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Date of movement")
    created_by: str = Field(..., description="User who created the movement")
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    approved_by: Optional[str] = Field(None, description="User who approved the movement")
    approved_date: Optional[datetime] = Field(None, description="Approval timestamp")
    is_approved: bool = Field(default=True, description="Whether movement is approved")
    
    # Business rules validation
    @validator('quantity')
    def validate_quantity(cls, v):
        if v == 0:
            raise ValueError('Movement quantity cannot be zero')
        return v
    
    @validator('total_cost')
    def validate_total_cost(cls, v, values):
        if 'unit_cost' in values and 'quantity' in values:
            expected_cost = abs(values['quantity']) * values['unit_cost']
            if v != 0 and abs(v - expected_cost) > Decimal('0.01'):
                logger.warning(f"Total cost {v} doesn't match quantity * unit_cost {expected_cost}")
        return v
    
    @validator('quantity_after')
    def validate_quantity_after(cls, v, values):
        if 'quantity_before' in values and 'quantity' in values:
            expected_after = values['quantity_before'] + values['quantity']
            if v != expected_after:
                raise ValueError(f"Quantity after ({v}) must equal quantity before + movement quantity")
        return v
    
    @validator('movement_type')
    def validate_movement_type_context(cls, v, values):
        # Validate that movement type matches context
        if v == StockMovementType.TRANSFER:
            # Transfers should have both from and to locations
            pass  # Will be validated in post_init if needed
        elif v == StockMovementType.PURCHASE:
            # Purchases should have supplier information
            pass  # Will be validated in post_init if needed
        elif v == StockMovementType.SALE:
            # Sales should have customer information
            pass  # Will be validated in post_init if needed
        return v
    
    class Config:
        validate_assignment = True
        use_enum_values = True
        json_encoders = {
            uuid.UUID: str,
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
    
    # Computed fields
    @computed_field
    @property
    def is_increase(self) -> bool:
        """Check if this movement increases inventory."""
        return self.quantity > 0
    
    @computed_field
    @property
    def is_decrease(self) -> bool:
        """Check if this movement decreases inventory."""
        return self.quantity < 0
    
    @computed_field
    @property
    def absolute_quantity(self) -> Decimal:
        """Get absolute quantity value."""
        return abs(self.quantity)
    
    @computed_field
    @property
    def is_cost_relevant(self) -> bool:
        """Check if this movement affects cost calculations."""
        return self.movement_type in [
            StockMovementType.PURCHASE,
            StockMovementType.ADJUSTMENT,
            StockMovementType.INITIAL,
            StockMovementType.RETURN
        ]
    
    @computed_field
    @property
    def effective_unit_cost(self) -> Decimal:
        """Get effective unit cost including all additional costs."""
        if self.landed_cost and self.absolute_quantity > 0:
            return self.landed_cost / self.absolute_quantity
        return self.unit_cost
    
    @computed_field
    @property
    def movement_value(self) -> Decimal:
        """Calculate total value of the movement."""
        return self.absolute_quantity * self.effective_unit_cost
    
    # Business logic methods
    def calculate_total_cost(self) -> Decimal:
        """Calculate total cost based on quantity and unit cost."""
        return self.absolute_quantity * self.unit_cost
    
    def calculate_landed_cost(self) -> Decimal:
        """Calculate total landed cost including all additional costs."""
        base_cost = self.calculate_total_cost()
        additional_costs = (
            (self.shipping_cost or Decimal('0')) +
            (self.duty_cost or Decimal('0')) +
            (self.other_costs or Decimal('0'))
        )
        return base_cost + additional_costs
    
    def update_costs(self):
        """Update calculated cost fields."""
        self.total_cost = self.calculate_total_cost()
        self.landed_cost = self.calculate_landed_cost()
    
    def is_valid_movement(self) -> bool:
        """Validate that the movement is properly configured."""
        try:
            # Check quantity after calculation
            expected_after = self.quantity_before + self.quantity
            if self.quantity_after != expected_after:
                return False
            
            # Check that decrease movements don't result in negative inventory
            if self.is_decrease and self.quantity_after < 0:
                return False
            
            # Check movement type specific validations
            if self.movement_type == StockMovementType.TRANSFER:
                if not self.from_location_id or not self.to_location_id:
                    return False
                if self.from_location_id == self.to_location_id:
                    return False
            
            return True
        except Exception:
            return False
    
    def get_impact_description(self) -> str:
        """Get human-readable description of the movement impact."""
        action = "increased" if self.is_increase else "decreased"
        return f"Inventory {action} by {self.absolute_quantity} units"
    
    def get_movement_description(self) -> str:
        """Get detailed description of the movement."""
        type_display = self.movement_type.get_display()
        quantity_str = f"{self.absolute_quantity}"
        
        if self.movement_type == StockMovementType.PURCHASE:
            supplier = self.supplier_name or "Unknown Supplier"
            return f"{type_display}: {quantity_str} units from {supplier}"
        elif self.movement_type == StockMovementType.SALE:
            customer = self.customer_name or "Customer"
            return f"{type_display}: {quantity_str} units to {customer}"
        elif self.movement_type == StockMovementType.TRANSFER:
            from_loc = self.from_location_name or "Unknown Location"
            to_loc = self.to_location_name or "Unknown Location"
            return f"{type_display}: {quantity_str} units from {from_loc} to {to_loc}"
        elif self.movement_type == StockMovementType.ADJUSTMENT:
            direction = "increase" if self.is_increase else "decrease"
            reason = self.reason or "Manual adjustment"
            return f"{type_display}: {direction} of {quantity_str} units - {reason}"
        else:
            return f"{type_display}: {quantity_str} units"
    
    def can_be_reversed(self) -> bool:
        """Check if this movement can be reversed."""
        # Generally, most movements can be reversed with an opposite movement
        # Some business rules might prevent reversals
        if not self.is_approved:
            return False
        
        # Check if reversing would cause negative inventory
        if self.is_increase:
            # To reverse an increase, we need enough current inventory
            # This would need to be checked against current stock levels
            return True
        else:
            # Reversing a decrease is generally safe
            return True
    
    def create_reversal(self, reason: str, created_by: str) -> 'StockMovement':
        """
        Create a reversal movement for this movement.
        
        Args:
            reason: Reason for the reversal
            created_by: User creating the reversal
            
        Returns:
            New StockMovement that reverses this one
        """
        if not self.can_be_reversed():
            raise BusinessRuleViolationError("This movement cannot be reversed")
        
        reversal = StockMovement(
            business_id=self.business_id,
            product_id=self.product_id,
            location_id=self.location_id,
            movement_type=self.movement_type,
            quantity=-self.quantity,  # Opposite quantity
            unit_cost=self.unit_cost,
            currency=self.currency,
            reason=f"Reversal of movement {self.id}: {reason}",
            notes=f"Reversal of original movement on {self.movement_date.isoformat()}",
            created_by=created_by,
            context=StockMovementContext(
                reference_type="stock_movement_reversal",
                reference_id=self.id,
                reference_number=str(self.id)
            )
        )
        
        return reversal
    
    def approve(self, approved_by: str):
        """Approve the movement."""
        if self.is_approved:
            raise BusinessRuleViolationError("Movement is already approved")
        
        self.is_approved = True
        self.approved_by = approved_by
        self.approved_date = datetime.now(timezone.utc)
        
        logger.info(f"Stock movement {self.id} approved by {approved_by}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert movement to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "product_id": str(self.product_id),
            "location_id": str(self.location_id) if self.location_id else None,
            "movement_type": self.movement_type.value,
            "movement_type_display": self.movement_type.get_display(),
            "quantity": float(self.quantity),
            "absolute_quantity": float(self.absolute_quantity),
            "unit_cost": float(self.unit_cost),
            "total_cost": float(self.total_cost),
            "landed_cost": float(self.landed_cost) if self.landed_cost else None,
            "effective_unit_cost": float(self.effective_unit_cost),
            "movement_value": float(self.movement_value),
            "currency": self.currency.value,
            "quantity_before": float(self.quantity_before),
            "quantity_after": float(self.quantity_after),
            "cost_before": float(self.cost_before),
            "cost_after": float(self.cost_after),
            "is_increase": self.is_increase,
            "is_decrease": self.is_decrease,
            "is_cost_relevant": self.is_cost_relevant,
            "context": {
                "reference_type": self.context.reference_type,
                "reference_id": str(self.context.reference_id) if self.context.reference_id else None,
                "reference_number": self.context.reference_number,
                "batch_number": self.context.batch_number,
                "serial_numbers": self.context.serial_numbers,
                "expiry_date": self.context.expiry_date.isoformat() if self.context.expiry_date else None
            },
            "reason": self.reason,
            "notes": self.notes,
            "from_location_id": str(self.from_location_id) if self.from_location_id else None,
            "to_location_id": str(self.to_location_id) if self.to_location_id else None,
            "from_location_name": self.from_location_name,
            "to_location_name": self.to_location_name,
            "supplier_id": str(self.supplier_id) if self.supplier_id else None,
            "supplier_name": self.supplier_name,
            "supplier_invoice_number": self.supplier_invoice_number,
            "customer_id": str(self.customer_id) if self.customer_id else None,
            "customer_name": self.customer_name,
            "shipping_cost": float(self.shipping_cost) if self.shipping_cost else None,
            "duty_cost": float(self.duty_cost) if self.duty_cost else None,
            "other_costs": float(self.other_costs) if self.other_costs else None,
            "movement_date": self.movement_date.isoformat(),
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat(),
            "approved_by": self.approved_by,
            "approved_date": self.approved_date.isoformat() if self.approved_date else None,
            "is_approved": self.is_approved,
            "can_be_reversed": self.can_be_reversed(),
            "impact_description": self.get_impact_description(),
            "movement_description": self.get_movement_description()
        }
    
    def __str__(self) -> str:
        return f"StockMovement({self.movement_type.value}: {self.quantity} units)"
    
    def __repr__(self) -> str:
        return f"StockMovement(id={self.id}, type={self.movement_type.value}, quantity={self.quantity})" 