"""
Data Transfer Objects (DTOs)

Objects that carry data between application layers and processes.
"""

from .activity_dto import (
    ActivityResponseDTO,
    ActivityCreateDTO,
    ActivityUpdateDTO,
    ActivitySearchDTO,
    ActivityListDTO,
    ActivityTemplateResponseDTO,
    ActivityTemplateCreateDTO,
    TimelineResponseDTO,
    ActivityStatisticsDTO,
)
from .auth_dto import (
    RegisterDTO,
    LoginDTO,
    AuthUserDTO,
    ResetPasswordTokenDTO,
    AuthTokenDTO,
    SocialAuthDTO,
    SupabaseAuthDTO,
)
from .business_dto import (
    BusinessResponseDTO,
    BusinessCreateDTO,
    BusinessUpdateDTO,
    BusinessSummaryDTO,
    BusinessSearchDTO,
    BusinessMembershipResponseDTO,
    BusinessInvitationResponseDTO,
    BusinessInvitationCreateDTO,
    BusinessStatsDTO,
)
from .contact_dto import (
    ContactResponseDTO,
    ContactCreateDTO,
    ContactUpdateDTO,
    ContactSearchDTO,
    ContactListDTO,
    ContactStatisticsDTO,
)
from .job_dto import (
    JobResponseDTO,
    JobCreateDTO,
    JobUpdateDTO,
    JobSearchDTO,
    JobListDTO,
    JobStatisticsDTO,
    JobAssignmentDTO,
    JobStatusUpdateDTO,
    JobBulkUpdateDTO,
)
from .project_dto import (
    ProjectResponseDTO,
    ProjectCreateDTO,
    ProjectUpdateDTO,
    ProjectSearchDTO,
    ProjectListDTO,
    ProjectStatisticsDTO,
    ProjectAssignmentDTO,
    ProjectTemplateResponseDTO,
    ProjectTemplateCreateDTO,
)
from .estimate_dto import (
    EstimateDTO,
    EstimateCreateDTO,
    EstimateUpdateDTO,
    EstimateFilters,
    # Legacy EstimateTemplate DTOs removed - using unified DocumentTemplate system
)
from .invoice_dto import (
    InvoiceDTO,
    CreateInvoiceDTO,
    CreateInvoiceFromEstimateDTO,
    ProcessPaymentDTO,
    InvoiceLineItemDTO,
    PaymentDTO,
)
from .product_dto import (
    ProductItemDTO,
    ProductCatalogDTO,
    PricingBreakdownDTO,
    ProductInstallationOptionDTO,
    ProductCategoryDTO,
    CreateProductDTO,
    ProductDTO,
    StockAdjustmentDTO,
    ProductSearchCriteria,
    ProductListDTO,
    ProductSummaryDTO,
)
from .service_dto import (
    ServiceItemDTO,
    ServiceCategoryDTO,
    ServicePricingDTO,
)
from .cart_dto import (
    CartDTO,
    CartItemDTO,
    CartSummaryDTO,
    AddToCartDTO,
    UpdateCartItemDTO,
)
from .profile_dto import (
    BusinessProfileDTO,
    ProfileSummaryDTO,
)
from .project_portfolio_dto import (
    FeaturedProjectDTO,
    ProjectCategoryDTO,
    ProjectTagDTO,
    ProjectSearchCriteria,
)
from .availability_dto import (
    AvailabilitySlotDTO,
    BusinessHoursDTO,
    AvailabilitySearchCriteria,
    CalendarEventDTO,
)

__all__ = [
    # Activity DTOs
    "ActivityResponseDTO",
    "ActivityCreateDTO",
    "ActivityUpdateDTO",
    "ActivitySearchDTO",
    "ActivityListDTO",
    "ActivityTemplateResponseDTO",
    "ActivityTemplateCreateDTO",
    "TimelineResponseDTO",
    "ActivityStatisticsDTO",
    # Auth DTOs
    "RegisterDTO",
    "LoginDTO",
    "AuthUserDTO",
    "ResetPasswordTokenDTO",
    "AuthTokenDTO",
    "SocialAuthDTO",
    "SupabaseAuthDTO",
    # Business DTOs
    "BusinessResponseDTO",
    "BusinessCreateDTO",
    "BusinessUpdateDTO",
    "BusinessSummaryDTO",
    "BusinessSearchDTO",
    "BusinessMembershipResponseDTO",
    "BusinessInvitationResponseDTO",
    "BusinessInvitationCreateDTO",
    "BusinessStatsDTO",
    # Contact DTOs
    "ContactResponseDTO",
    "ContactCreateDTO",
    "ContactUpdateDTO",
    "ContactSearchDTO",
    "ContactListDTO",
    "ContactStatisticsDTO",
    # Job DTOs
    "JobResponseDTO",
    "JobCreateDTO",
    "JobUpdateDTO",
    "JobSearchDTO",
    "JobListDTO",
    "JobStatisticsDTO",
    "JobAssignmentDTO",
    "JobStatusUpdateDTO",
    "JobBulkUpdateDTO",
    # Project DTOs
    "ProjectResponseDTO",
    "ProjectCreateDTO",
    "ProjectUpdateDTO",
    "ProjectSearchDTO",
    "ProjectListDTO",
    "ProjectStatisticsDTO",
    "ProjectAssignmentDTO",
    "ProjectTemplateResponseDTO",
    "ProjectTemplateCreateDTO",
    # Estimate DTOs
    "EstimateDTO",
    "EstimateCreateDTO",
    "EstimateUpdateDTO", 
    "EstimateFilters",
    # Legacy EstimateTemplate DTOs removed
    # Invoice DTOs
    "InvoiceDTO",
    "CreateInvoiceDTO",
    "CreateInvoiceFromEstimateDTO",
    "ProcessPaymentDTO",
    "InvoiceLineItemDTO",
    "PaymentDTO",
    # Product DTOs
    "ProductItemDTO",
    "ProductCatalogDTO",
    "PricingBreakdownDTO",
    "ProductInstallationOptionDTO",
    "ProductCategoryDTO",
    "CreateProductDTO",
    "ProductDTO",
    "StockAdjustmentDTO",
    "ProductSearchCriteria",
    "ProductListDTO",
    "ProductSummaryDTO",
    # Service DTOs
    "ServiceItemDTO",
    "ServiceCategoryDTO",
    "ServicePricingDTO",
    # Cart DTOs
    "CartDTO",
    "CartItemDTO",
    "CartSummaryDTO",
    "AddToCartDTO",
    "UpdateCartItemDTO",
    # Profile DTOs
    "BusinessProfileDTO",
    "ProfileSummaryDTO",
    # Project Portfolio DTOs
    "FeaturedProjectDTO",
    "ProjectCategoryDTO",
    "ProjectTagDTO",
    "ProjectSearchCriteria",
    # Availability DTOs
    "AvailabilitySlotDTO",
    "BusinessHoursDTO",
    "AvailabilitySearchCriteria",
    "CalendarEventDTO",
] 