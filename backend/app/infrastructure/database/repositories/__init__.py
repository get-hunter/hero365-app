"""
Database Repository Implementations

Concrete implementations of repository interfaces using Supabase client SDK.
"""

from .supabase_activity_repository import SupabaseActivityRepository
from .supabase_business_invitation_repository import SupabaseBusinessInvitationRepository
from .supabase_business_repository import SupabaseBusinessRepository
from .supabase_contact_repository import SupabaseContactRepository
from .supabase_job_repository import SupabaseJobRepository
from .supabase_project_repository import SupabaseProjectRepository
from .supabase_user_capabilities_repository import SupabaseUserCapabilitiesRepository
from .supabase_estimate_repository import SupabaseEstimateRepository
from .supabase_invoice_repository import SupabaseInvoiceRepository
from .supabase_estimate_template_repository import SupabaseEstimateTemplateRepository
from .supabase_product_repository import SupabaseProductRepository
from .supabase_product_category_repository import SupabaseProductCategoryRepository
from .supabase_stock_movement_repository import SupabaseStockMovementRepository
from .supabase_supplier_repository import SupabaseSupplierRepository
from .supabase_purchase_order_repository import SupabasePurchaseOrderRepository
from .supabase_hybrid_search_repository import SupabaseHybridSearchRepository

__all__ = [
    "SupabaseActivityRepository",
    "SupabaseBusinessInvitationRepository",
    "SupabaseBusinessRepository",
    "SupabaseContactRepository", 
    "SupabaseJobRepository",
    "SupabaseProjectRepository",
    "SupabaseUserCapabilitiesRepository",
    "SupabaseEstimateRepository",
    "SupabaseInvoiceRepository",
    "SupabaseEstimateTemplateRepository",
    "SupabaseProductRepository",
    "SupabaseProductCategoryRepository",
    "SupabaseStockMovementRepository",
    "SupabaseSupplierRepository",
    "SupabasePurchaseOrderRepository",
    "SupabaseHybridSearchRepository",
] 