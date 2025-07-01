"""
Domain Entities

Business entities that encapsulate the most general and high-level rules.
"""

# Core business entities
from .business import Business
from .business_membership import BusinessMembership
from .business_invitation import BusinessInvitation
from .user_capabilities import UserCapabilities
from .contact import Contact
from .project import Project, ProjectTemplate
from .job import Job
from .activity import Activity
from .calendar import CalendarEvent, TimeOffRequest, WorkingHoursTemplate, CalendarPreferences
from .availability import AvailabilityWindow, WorkloadCapacity
from .skills import Skill, Certification
from .scheduling_engine import IntelligentSchedulingEngine

# Financial entities
from .estimate import Estimate
from .estimate_template import EstimateTemplate
from .invoice import Invoice

# Inventory management entities
from .product import Product, ProductPricingTier, ProductLocation, ProductSupplier
from .product_category import ProductCategory, CategoryDefaults
from .stock_movement import StockMovement, StockMovementContext
from .supplier import Supplier, SupplierContact, PaymentTerms, SupplierPerformance
from .purchase_order import PurchaseOrder, PurchaseOrderLineItem

__all__ = [
    # Core business entities
    "Business",
    "BusinessMembership", 
    "BusinessInvitation",
    "UserCapabilities",
    "Contact",
    "Project",
    "ProjectTemplate",
    "Job",
    "Activity",
    "CalendarEvent",
    "TimeOffRequest",
    "WorkingHoursTemplate",
    "CalendarPreferences",
    "AvailabilityWindow",
    "WorkloadCapacity",
    "Skill",
    "Certification",
    "IntelligentSchedulingEngine",
    
    # Financial entities
    "Estimate",
    "EstimateTemplate",
    "Invoice",
    
    # Inventory management entities
    "Product",
    "ProductPricingTier",
    "ProductLocation", 
    "ProductSupplier",
    "ProductCategory",
    "CategoryDefaults",
    "StockMovement",
    "StockMovementContext",
    "Supplier",
    "SupplierContact",
    "PaymentTerms",
    "SupplierPerformance",
    "PurchaseOrder",
    "PurchaseOrderLineItem",
] 