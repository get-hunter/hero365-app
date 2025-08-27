"""
Repository Interfaces

Abstract interfaces for data access that the domain layer needs.
These will be implemented in the infrastructure layer.
"""

from .activity_repository import ActivityRepository
from .business_invitation_repository import BusinessInvitationRepository
from .business_repository import BusinessRepository
from .business_membership_repository import BusinessMembershipRepository
from .contact_repository import ContactRepository
from .job_repository import JobRepository
from .project_repository import ProjectRepository
from .base_repository import BaseRepository
from .estimate_repository import EstimateRepository
from .invoice_repository import InvoiceRepository
from .template_repository import TemplateRepository
from .user_capabilities_repository import UserCapabilitiesRepository
from .product_repository import ProductRepository
from .product_category_repository import ProductCategoryRepository
from .stock_movement_repository import StockMovementRepository
from .supplier_repository import SupplierRepository
from .purchase_order_repository import PurchaseOrderRepository
from .hybrid_search_repository import HybridSearchRepository, SearchResult, EmbeddingRecord, SearchQuery
from .customer_membership_repository import CustomerMembershipRepository

__all__ = [
    "ActivityRepository",
    "BaseRepository",
    "BusinessInvitationRepository",
    "BusinessRepository",
    "BusinessMembershipRepository",
    "ContactRepository",
    "JobRepository",
    "ProjectRepository",
    "EstimateRepository",
    "InvoiceRepository",
    "TemplateRepository",
    "UserCapabilitiesRepository",
    "ProductRepository",
    "ProductCategoryRepository",
    "StockMovementRepository",
    "SupplierRepository",
    "PurchaseOrderRepository",
    "HybridSearchRepository",
    "SearchResult",
    "EmbeddingRecord",
    "SearchQuery",
    "CustomerMembershipRepository",
] 