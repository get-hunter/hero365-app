"""
Centralized Enums Module

Single source of truth for all enums used across the application.
These enums work with both domain entities and API schemas.
"""

from enum import Enum


class ContactType(str, Enum):
    """Contact type enumeration."""
    PROSPECT = "prospect"
    LEAD = "lead"
    CUSTOMER = "customer"
    PARTNER = "partner"
    VENDOR = "vendor"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PROSPECT: "Prospect",
            self.LEAD: "Lead", 
            self.CUSTOMER: "Customer",
            self.PARTNER: "Partner",
            self.VENDOR: "Vendor"
        }
        return display_map.get(self, self.value.title())


class ContactStatus(str, Enum):
    """Contact status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    BLOCKED = "blocked"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.ACTIVE: "Active",
            self.INACTIVE: "Inactive",
            self.ARCHIVED: "Archived", 
            self.BLOCKED: "Blocked"
        }
        return display_map.get(self, self.value.title())


class ContactPriority(str, Enum):
    """Contact priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.LOW: "Low",
            self.MEDIUM: "Medium",
            self.HIGH: "High",
            self.URGENT: "Urgent"
        }
        return display_map.get(self, self.value.title())


class ContactSource(str, Enum):
    """Contact source enumeration."""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    PHONE_CALL = "phone_call"
    WALK_IN = "walk_in"
    TRADE_SHOW = "trade_show"
    ADVERTISING = "advertising"
    ONLINE = "online"
    OTHER = "other"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.WEBSITE: "Website",
            self.REFERRAL: "Referral",
            self.SOCIAL_MEDIA: "Social Media",
            self.EMAIL_CAMPAIGN: "Email Campaign",
            self.PHONE_CALL: "Phone Call",
            self.WALK_IN: "Walk-in",
            self.TRADE_SHOW: "Trade Show",
            self.ADVERTISING: "Advertising",
            self.ONLINE: "Online",
            self.OTHER: "Other"
        }
        return display_map.get(self, self.value.title())


class RelationshipStatus(str, Enum):
    """Relationship status enumeration."""
    PROSPECT = "prospect"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    DORMANT = "dormant"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PROSPECT: "Prospect",
            self.QUALIFIED: "Qualified",
            self.PROPOSAL: "Proposal",
            self.NEGOTIATION: "Negotiation",
            self.CLOSED_WON: "Closed Won",
            self.CLOSED_LOST: "Closed Lost",
            self.DORMANT: "Dormant"
        }
        return display_map.get(self, self.value.title())


class LifecycleStage(str, Enum):
    """Lifecycle stage enumeration."""
    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    INTENT = "intent"
    EVALUATION = "evaluation"
    PURCHASE = "purchase"
    RETENTION = "retention"
    ADVOCACY = "advocacy"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.AWARENESS: "Awareness",
            self.INTEREST: "Interest", 
            self.CONSIDERATION: "Consideration",
            self.INTENT: "Intent",
            self.EVALUATION: "Evaluation",
            self.PURCHASE: "Purchase",
            self.RETENTION: "Retention",
            self.ADVOCACY: "Advocacy"
        }
        return display_map.get(self, self.value.title())


class JobType(str, Enum):
    """Job type enumeration."""
    SERVICE = "service"
    PROJECT = "project"
    MAINTENANCE = "maintenance"
    INSTALLATION = "installation"
    REPAIR = "repair"
    INSPECTION = "inspection"
    CONSULTATION = "consultation"
    QUOTE = "quote"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.SERVICE: "Service",
            self.PROJECT: "Project",
            self.MAINTENANCE: "Maintenance",
            self.INSTALLATION: "Installation",
            self.REPAIR: "Repair",
            self.INSPECTION: "Inspection",
            self.CONSULTATION: "Consultation",
            self.QUOTE: "Quote",
            self.FOLLOW_UP: "Follow Up",
            self.EMERGENCY: "Emergency"
        }
        return display_map.get(self, self.value.title())


class JobStatus(str, Enum):
    """Job status enumeration."""
    DRAFT = "draft"
    QUOTED = "quoted"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    INVOICED = "invoiced"
    PAID = "paid"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.DRAFT: "Draft",
            self.QUOTED: "Quoted",
            self.SCHEDULED: "Scheduled",
            self.IN_PROGRESS: "In Progress",
            self.ON_HOLD: "On Hold",
            self.COMPLETED: "Completed",
            self.CANCELLED: "Cancelled",
            self.INVOICED: "Invoiced",
            self.PAID: "Paid"
        }
        return display_map.get(self, self.value.title())


class JobPriority(str, Enum):
    """Job priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.LOW: "Low",
            self.MEDIUM: "Medium",
            self.HIGH: "High",
            self.URGENT: "Urgent",
            self.EMERGENCY: "Emergency"
        }
        return display_map.get(self, self.value.title())


class JobSource(str, Enum):
    """Job source enumeration."""
    PHONE = "phone"
    EMAIL = "email"
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    ADVERTISEMENT = "advertisement"
    WALK_IN = "walk_in"
    REPEAT_CUSTOMER = "repeat_customer"
    PARTNERSHIP = "partnership"
    OTHER = "other"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PHONE: "Phone",
            self.EMAIL: "Email",
            self.WEBSITE: "Website",
            self.REFERRAL: "Referral",
            self.SOCIAL_MEDIA: "Social Media",
            self.ADVERTISEMENT: "Advertisement",
            self.WALK_IN: "Walk-in",
            self.REPEAT_CUSTOMER: "Repeat Customer",
            self.PARTNERSHIP: "Partnership",
            self.OTHER: "Other"
        }
        return display_map.get(self, self.value.title())


# Project-related enums
class ProjectType(str, Enum):
    """Project type enumeration."""
    MAINTENANCE = "maintenance"
    INSTALLATION = "installation"
    RENOVATION = "renovation"
    EMERGENCY = "emergency"
    CONSULTATION = "consultation"
    INSPECTION = "inspection"
    REPAIR = "repair"
    CONSTRUCTION = "construction"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.MAINTENANCE: "Maintenance",
            self.INSTALLATION: "Installation",
            self.RENOVATION: "Renovation",
            self.EMERGENCY: "Emergency",
            self.CONSULTATION: "Consultation",
            self.INSPECTION: "Inspection",
            self.REPAIR: "Repair",
            self.CONSTRUCTION: "Construction"
        }
        return display_map.get(self, self.value.title())


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PLANNING: "Planning",
            self.ACTIVE: "Active",
            self.ON_HOLD: "On Hold",
            self.COMPLETED: "Completed",
            self.CANCELLED: "Cancelled"
        }
        return display_map.get(self, self.value.title())


class ProjectPriority(str, Enum):
    """Project priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.LOW: "Low",
            self.MEDIUM: "Medium",
            self.HIGH: "High",
            self.CRITICAL: "Critical"
        }
        return display_map.get(self, self.value.title())


# Estimates and Invoices enums
class EstimateStatus(str, Enum):
    """Estimate status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED = "converted"
    CANCELLED = "cancelled"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.DRAFT: "Draft",
            self.SENT: "Sent",
            self.VIEWED: "Viewed",
            self.APPROVED: "Approved",
            self.REJECTED: "Rejected",
            self.EXPIRED: "Expired",
            self.CONVERTED: "Converted",
            self.CANCELLED: "Cancelled"
        }
        return display_map.get(self, self.value.title())


class InvoiceStatus(str, Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"  
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.DRAFT: "Draft",
            self.SENT: "Sent",
            self.VIEWED: "Viewed",
            self.PAID: "Paid",
            self.PARTIALLY_PAID: "Partially Paid",
            self.OVERDUE: "Overdue",
            self.CANCELLED: "Cancelled",
            self.REFUNDED: "Refunded"
        }
        return display_map.get(self, self.value.title())


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PENDING: "Pending",
            self.PROCESSING: "Processing",
            self.COMPLETED: "Completed",
            self.FAILED: "Failed",
            self.CANCELLED: "Cancelled",
            self.REFUNDED: "Refunded",
            self.PARTIALLY_REFUNDED: "Partially Refunded"
        }
        return display_map.get(self, self.value.title())


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    ACH = "ach"
    WIRE_TRANSFER = "wire_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    SQUARE = "square"
    VENMO = "venmo"
    ZELLE = "zelle"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.CASH: "Cash",
            self.CHECK: "Check",
            self.CREDIT_CARD: "Credit Card",
            self.DEBIT_CARD: "Debit Card",
            self.ACH: "ACH Transfer",
            self.WIRE_TRANSFER: "Wire Transfer",
            self.PAYPAL: "PayPal",
            self.STRIPE: "Stripe",
            self.SQUARE: "Square",
            self.VENMO: "Venmo",
            self.ZELLE: "Zelle",
            self.BANK_TRANSFER: "Bank Transfer",
            self.OTHER: "Other"
        }
        return display_map.get(self, self.value.title())


class TemplateType(str, Enum):
    """Template type enumeration."""
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    MINIMAL = "minimal"
    CORPORATE = "corporate"
    MODERN = "modern"
    CLASSIC = "classic"
    INDUSTRIAL = "industrial"
    SERVICE_FOCUSED = "service_focused"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PROFESSIONAL: "Professional",
            self.CREATIVE: "Creative",
            self.MINIMAL: "Minimal",
            self.CORPORATE: "Corporate",
            self.MODERN: "Modern",
            self.CLASSIC: "Classic",
            self.INDUSTRIAL: "Industrial",
            self.SERVICE_FOCUSED: "Service Focused"
        }
        return display_map.get(self, self.value.title())


class CurrencyCode(str, Enum):
    """Currency code enumeration (ISO 4217)."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    CNY = "CNY"
    MXN = "MXN"
    BRL = "BRL"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.USD: "US Dollar",
            self.EUR: "Euro",
            self.GBP: "British Pound",
            self.CAD: "Canadian Dollar", 
            self.AUD: "Australian Dollar",
            self.JPY: "Japanese Yen",
            self.CHF: "Swiss Franc",
            self.CNY: "Chinese Yuan",
            self.MXN: "Mexican Peso",
            self.BRL: "Brazilian Real"
        }
        return display_map.get(self, self.value)


class TaxType(str, Enum):
    """Tax type enumeration."""
    NONE = "none"
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    INCLUSIVE = "inclusive"
    EXCLUSIVE = "exclusive"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.NONE: "No Tax",
            self.PERCENTAGE: "Percentage",
            self.FIXED_AMOUNT: "Fixed Amount",
            self.INCLUSIVE: "Tax Inclusive",
            self.EXCLUSIVE: "Tax Exclusive"
        }
        return display_map.get(self, self.value.title())


class DiscountType(str, Enum):
    """Discount type enumeration."""
    NONE = "none"
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.NONE: "No Discount",
            self.PERCENTAGE: "Percentage",
            self.FIXED_AMOUNT: "Fixed Amount"
        }
        return display_map.get(self, self.value.title())


class AdvancePaymentType(str, Enum):
    """Advance payment type enumeration."""
    NONE = "none"
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.NONE: "No Advance Payment",
            self.PERCENTAGE: "Percentage",
            self.FIXED_AMOUNT: "Fixed Amount"
        }
        return display_map.get(self, self.value.title())


class DocumentType(str, Enum):
    """Document type enumeration for estimates and quotes."""
    ESTIMATE = "estimate"
    QUOTE = "quote"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.ESTIMATE: "Estimate",
            self.QUOTE: "Quote"
        }
        return display_map.get(self, self.value.title())


class EmailStatus(str, Enum):
    """Email delivery status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"
    UNSUBSCRIBED = "unsubscribed"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.PENDING: "Pending",
            self.SENT: "Sent",
            self.DELIVERED: "Delivered",
            self.OPENED: "Opened", 
            self.CLICKED: "Clicked",
            self.BOUNCED: "Bounced",
            self.FAILED: "Failed",
            self.UNSUBSCRIBED: "Unsubscribed"
        }
        return display_map.get(self, self.value.title())


# Inventory Management Enums
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


class PricingModel(str, Enum):
    """Pricing model enumeration."""
    FIXED = "fixed"
    HOURLY = "hourly"
    PER_UNIT = "per_unit"
    TIERED = "tiered"
    CUSTOM = "custom"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.FIXED: "Fixed Price",
            self.HOURLY: "Hourly Rate",
            self.PER_UNIT: "Per Unit",
            self.TIERED: "Tiered Pricing",
            self.CUSTOM: "Custom Pricing"
        }
        return display_map.get(self, self.value.title())


class UnitOfMeasure(str, Enum):
    """Unit of measure enumeration."""
    EACH = "each"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    SQUARE_FOOT = "square_foot"
    LINEAR_FOOT = "linear_foot"
    CUBIC_FOOT = "cubic_foot"
    POUND = "pound"
    KILOGRAM = "kilogram"
    GALLON = "gallon"
    LITER = "liter"
    METER = "meter"
    YARD = "yard"
    PIECE = "piece"
    SET = "set"
    LOT = "lot"
    CASE = "case"
    BOX = "box"
    
    def get_display(self) -> str:
        """Get human-readable display name."""
        display_map = {
            self.EACH: "Each",
            self.HOUR: "Hour",
            self.DAY: "Day",
            self.WEEK: "Week",
            self.MONTH: "Month",
            self.SQUARE_FOOT: "Square Foot",
            self.LINEAR_FOOT: "Linear Foot",
            self.CUBIC_FOOT: "Cubic Foot",
            self.POUND: "Pound",
            self.KILOGRAM: "Kilogram",
            self.GALLON: "Gallon",
            self.LITER: "Liter",
            self.METER: "Meter",
            self.YARD: "Yard",
            self.PIECE: "Piece",
            self.SET: "Set",
            self.LOT: "Lot",
            self.CASE: "Case",
            self.BOX: "Box"
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