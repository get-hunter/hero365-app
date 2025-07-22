"""
Product Domain Enums

Enums specific to the product and inventory domain including product types,
statuses, inventory tracking, stock movements, and supplier management.
"""

from enum import Enum


class ProductType(str, Enum):
    """Product type enumeration for inventory management."""
    PRODUCT = "product"           # Physical inventory item
    SERVICE = "service"           # Labor/time-based service  
    BUNDLE = "bundle"            # Product + service packages
    SUBSCRIPTION = "subscription" # Recurring services
    MAINTENANCE_PLAN = "maintenance_plan"
    DIGITAL = "digital"          # Software, licenses, etc.
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PRODUCT: "Product",
            self.SERVICE: "Service",
            self.BUNDLE: "Bundle",
            self.SUBSCRIPTION: "Subscription",
            self.MAINTENANCE_PLAN: "Maintenance Plan",
            self.DIGITAL: "Digital"
        }
        return display_map.get(self, self.value.title())


class ProductStatus(str, Enum):
    """Product status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    DRAFT = "draft"
    OUT_OF_STOCK = "out_of_stock"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.ACTIVE: "Active",
            self.INACTIVE: "Inactive",
            self.DISCONTINUED: "Discontinued",
            self.DRAFT: "Draft",
            self.OUT_OF_STOCK: "Out of Stock"
        }
        return display_map.get(self, self.value.title())


class InventoryMethod(str, Enum):
    """Inventory tracking method enumeration."""
    PERPETUAL = "perpetual"      # Real-time tracking
    PERIODIC = "periodic"        # Period-end counting
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PERPETUAL: "Perpetual",
            self.PERIODIC: "Periodic"
        }
        return display_map.get(self, self.value.title())


class CostingMethod(str, Enum):
    """Inventory costing method enumeration."""
    FIFO = "fifo"               # First In, First Out
    LIFO = "lifo"               # Last In, First Out  
    WEIGHTED_AVERAGE = "weighted_average"
    SPECIFIC_IDENTIFICATION = "specific_identification"
    STANDARD_COST = "standard_cost"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.FIFO: "First In, First Out (FIFO)",
            self.LIFO: "Last In, First Out (LIFO)",
            self.WEIGHTED_AVERAGE: "Weighted Average",
            self.SPECIFIC_IDENTIFICATION: "Specific Identification",
            self.STANDARD_COST: "Standard Cost"
        }
        return display_map.get(self, self.value.title())


class StockMovementType(str, Enum):
    """Stock movement type enumeration."""
    PURCHASE = "purchase"        # Receiving inventory
    SALE = "sale"               # Selling inventory
    ADJUSTMENT = "adjustment"    # Manual corrections
    TRANSFER = "transfer"        # Between locations
    RETURN = "return"           # Customer returns
    DAMAGE = "damage"           # Damaged goods write-off
    SHRINKAGE = "shrinkage"     # Inventory shrinkage
    INITIAL = "initial"         # Initial stock entry
    RECOUNT = "recount"         # Physical count adjustment
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PURCHASE: "Purchase",
            self.SALE: "Sale",
            self.ADJUSTMENT: "Adjustment",
            self.TRANSFER: "Transfer",
            self.RETURN: "Return",
            self.DAMAGE: "Damage",
            self.SHRINKAGE: "Shrinkage",
            self.INITIAL: "Initial Stock",
            self.RECOUNT: "Recount"
        }
        return display_map.get(self, self.value.title())


class StockStatus(str, Enum):
    """Stock status enumeration."""
    AVAILABLE = "available"      # Ready for sale
    RESERVED = "reserved"        # Reserved for orders
    ON_ORDER = "on_order"       # Purchase order placed
    BACKORDERED = "backordered" # Out of stock, on backorder
    DAMAGED = "damaged"         # Damaged inventory
    QUARANTINE = "quarantine"   # Quality control hold
    IN_TRANSIT = "in_transit"   # Being transferred
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.AVAILABLE: "Available",
            self.RESERVED: "Reserved",
            self.ON_ORDER: "On Order",
            self.BACKORDERED: "Backordered",
            self.DAMAGED: "Damaged",
            self.QUARANTINE: "Quarantine",
            self.IN_TRANSIT: "In Transit"
        }
        return display_map.get(self, self.value.title())


class PurchaseOrderStatus(str, Enum):
    """Purchase order status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"
    CLOSED = "closed"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.DRAFT: "Draft",
            self.SENT: "Sent",
            self.CONFIRMED: "Confirmed",
            self.PARTIALLY_RECEIVED: "Partially Received",
            self.RECEIVED: "Received",
            self.CANCELLED: "Cancelled",
            self.CLOSED: "Closed"
        }
        return display_map.get(self, self.value.title())


class SupplierStatus(str, Enum):
    """Supplier status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.ACTIVE: "Active",
            self.INACTIVE: "Inactive",
            self.PENDING: "Pending",
            self.SUSPENDED: "Suspended"
        }
        return display_map.get(self, self.value.title()) 