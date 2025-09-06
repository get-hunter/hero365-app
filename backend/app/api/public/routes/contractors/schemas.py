"""
Shared Pydantic schemas for contractor public API endpoints.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal


class ProfessionalProfile(BaseModel):
    """Professional profile information."""
    
    business_id: str = Field(..., description="Business ID")
    business_name: str = Field(..., description="Business name")
    trade_type: str = Field(..., description="Primary trade type")
    description: str = Field(..., description="Business description")
    
    # Contact information
    phone: str = Field(..., description="Business phone")
    email: str = Field(..., description="Business email")
    address: str = Field(..., description="Business address")
    city: str = Field(..., description="Business city")
    state: str = Field(..., description="Business state")
    postal_code: str = Field(..., description="Business postal code")
    website: Optional[HttpUrl] = Field(None, description="Business website")
    
    # Service information
    service_areas: List[str] = Field(default_factory=list, description="Service areas")
    emergency_service: bool = Field(False, description="24/7 emergency service available")
    
    # Business details
    years_in_business: Optional[int] = Field(None, description="Years in business")
    license_number: Optional[str] = Field(None, description="License number")
    insurance_verified: bool = Field(False, description="Insurance verified")
    
    # Ratings and reviews
    average_rating: Optional[float] = Field(None, description="Average customer rating")
    total_reviews: Optional[int] = Field(None, description="Total number of reviews")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")


class ServiceItem(BaseModel):
    """Professional service information."""
    
    id: str = Field(..., description="Service ID")
    name: str = Field(..., description="Service name")
    description: str = Field(..., description="Service description")
    category: str = Field(..., description="Service category")
    
    # Pricing information
    base_price: Optional[float] = Field(None, description="Base price")
    price_range_min: Optional[float] = Field(None, description="Minimum price")
    price_range_max: Optional[float] = Field(None, description="Maximum price")
    pricing_unit: str = Field("service", description="Pricing unit")
    
    # Service details
    duration_minutes: Optional[int] = Field(None, description="Estimated duration")
    is_emergency: bool = Field(False, description="Emergency service available")
    requires_quote: bool = Field(False, description="Requires custom quote")
    available: bool = Field(True, description="Currently available")
    
    # Service areas and keywords
    service_areas: List[str] = Field(default_factory=list, description="Service areas")
    keywords: List[str] = Field(default_factory=list, description="SEO keywords")


class ServiceCategory(BaseModel):
    """Service category with services."""
    
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="Category slug")
    description: Optional[str] = Field(None, description="Category description")
    services: List[ServiceItem] = Field(default_factory=list, description="Services in this category")


class ProductItem(BaseModel):
    """Professional product information."""
    
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    category: str = Field(..., description="Product category")
    
    # Product details
    brand: Optional[str] = Field(None, description="Product brand")
    model: Optional[str] = Field(None, description="Product model")
    sku: Optional[str] = Field(None, description="Product SKU")
    
    # Pricing and availability
    price: float = Field(..., description="Product price")
    msrp: Optional[float] = Field(None, description="Manufacturer suggested retail price")
    in_stock: bool = Field(True, description="Product in stock")
    stock_quantity: int = Field(0, description="Current stock quantity")
    
    # Additional information
    specifications: Dict[str, str] = Field(default_factory=dict, description="Product specifications")
    warranty_years: Optional[int] = Field(None, description="Warranty period in years")
    energy_rating: Optional[str] = Field(None, description="Energy efficiency rating")


class ProductCategory(BaseModel):
    """Product category with products."""
    
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    product_count: int = Field(0, description="Number of products in category")
    sort_order: int = Field(0, description="Display order")


class ProductInstallationOption(BaseModel):
    """Product installation option with pricing."""
    
    id: str = Field(..., description="Installation option ID")
    option_name: str = Field(..., description="Installation option name")
    description: Optional[str] = Field(None, description="Installation description")
    base_install_price: float = Field(..., description="Base installation price")
    
    # Membership pricing
    residential_install_price: Optional[float] = Field(None, description="Residential member price")
    commercial_install_price: Optional[float] = Field(None, description="Commercial member price")
    premium_install_price: Optional[float] = Field(None, description="Premium member price")
    
    # Installation details
    estimated_duration_hours: Optional[float] = Field(None, description="Estimated installation time")
    complexity_multiplier: float = Field(1.0, description="Complexity multiplier")
    is_default: bool = Field(False, description="Default installation option")
    
    # Requirements and inclusions
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Installation requirements")
    included_in_install: List[str] = Field(default_factory=list, description="What's included")


class ProductCatalogItem(BaseModel):
    """Product catalog item with installation options."""
    
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    sku: str = Field(..., description="Product SKU")
    description: Optional[str] = Field(None, description="Product description")
    long_description: Optional[str] = Field(None, description="Detailed product description")
    
    # Pricing
    unit_price: float = Field(..., description="Product unit price")
    price_display: str = Field("fixed", description="Price display type")
    
    # Product details
    category_name: Optional[str] = Field(None, description="Product category")
    brand: Optional[str] = Field(None, description="Product brand")
    warranty_years: Optional[int] = Field(None, description="Warranty period")
    energy_efficiency_rating: Optional[str] = Field(None, description="Energy efficiency rating")
    
    # Installation
    requires_professional_install: bool = Field(False, description="Requires professional installation")
    install_complexity: str = Field("standard", description="Installation complexity level")
    installation_time_estimate: Optional[str] = Field(None, description="Installation time estimate")
    
    # E-commerce
    featured_image_url: Optional[str] = Field(None, description="Main product image")
    gallery_images: List[str] = Field(default_factory=list, description="Product gallery images")
    product_highlights: List[str] = Field(default_factory=list, description="Key product features")
    technical_specs: Dict[str, Any] = Field(default_factory=dict, description="Technical specifications")
    
    # SEO
    meta_title: Optional[str] = Field(None, description="SEO title")
    meta_description: Optional[str] = Field(None, description="SEO description")
    slug: Optional[str] = Field(None, description="URL slug")
    
    # Availability
    is_active: bool = Field(True, description="Product is active")
    is_featured: bool = Field(False, description="Product is featured")
    current_stock: Optional[float] = Field(None, description="Current stock level")
    
    # Installation options
    installation_options: List[ProductInstallationOption] = Field(default_factory=list, description="Available installation options")


class PricingBreakdown(BaseModel):
    """Detailed pricing breakdown for product + installation."""
    
    # Base pricing
    product_unit_price: float = Field(..., description="Product unit price")
    installation_base_price: float = Field(..., description="Installation base price") 
    quantity: int = Field(1, description="Quantity")
    
    # Subtotals
    product_subtotal: float = Field(..., description="Product subtotal")
    installation_subtotal: float = Field(..., description="Installation subtotal")
    subtotal_before_discounts: float = Field(..., description="Subtotal before discounts")
    
    # Discounts
    membership_type: Optional[str] = Field(None, description="Applied membership type")
    product_discount_amount: float = Field(0, description="Product discount amount")
    installation_discount_amount: float = Field(0, description="Installation discount amount")
    total_discount_amount: float = Field(0, description="Total discount amount")
    bundle_savings: float = Field(0, description="Bundle discount savings")
    
    # Final pricing
    subtotal_after_discounts: float = Field(..., description="Subtotal after discounts")
    tax_rate: float = Field(0, description="Tax rate applied")
    tax_amount: float = Field(0, description="Tax amount")
    total_amount: float = Field(..., description="Final total amount")
    
    # Savings summary
    total_savings: float = Field(0, description="Total amount saved")
    savings_percentage: float = Field(0, description="Percentage saved")
    
    # Display
    formatted_display_price: str = Field(..., description="Formatted display price")
    price_display_type: str = Field("fixed", description="Price display type")


class MembershipBenefit(BaseModel):
    """Membership plan benefit."""
    
    id: str = Field(..., description="Benefit ID")
    title: str = Field(..., description="Benefit title")
    description: str = Field(..., description="Benefit description")
    icon: Optional[str] = Field(None, description="Icon name for UI")
    value: Optional[str] = Field(None, description="Benefit value (e.g., '15%', '$69 value')")
    is_highlighted: bool = Field(False, description="Whether this benefit should be highlighted")
    sort_order: int = Field(0, description="Display order")


class MembershipPlan(BaseModel):
    """Customer membership plan."""
    
    id: str = Field(..., description="Plan ID")
    name: str = Field(..., description="Plan name")
    plan_type: str = Field(..., description="Plan type (residential, commercial, premium)")
    description: str = Field(..., description="Plan description")
    tagline: Optional[str] = Field(None, description="Marketing tagline")
    
    # Pricing
    price_monthly: Optional[float] = Field(None, description="Monthly price")
    price_yearly: Optional[float] = Field(None, description="Yearly price")
    yearly_savings: Optional[float] = Field(None, description="Annual savings amount")
    setup_fee: Optional[float] = Field(None, description="One-time setup fee")
    
    # Service benefits
    discount_percentage: int = Field(0, description="Service discount percentage")
    priority_service: bool = Field(False, description="Priority scheduling")
    extended_warranty: bool = Field(False, description="Extended warranty coverage")
    maintenance_included: bool = Field(False, description="Maintenance visits included")
    emergency_response: bool = Field(False, description="24/7 emergency response")
    free_diagnostics: bool = Field(False, description="Free diagnostic calls")
    annual_tune_ups: int = Field(0, description="Number of annual tune-ups")
    
    # Display
    is_active: bool = Field(True, description="Plan is active")
    is_featured: bool = Field(False, description="Plan is featured/popular")
    popular_badge: Optional[str] = Field(None, description="Popular badge text")
    color_scheme: Optional[str] = Field(None, description="UI color scheme")
    sort_order: int = Field(0, description="Display order")
    
    # Terms
    contract_length_months: Optional[int] = Field(None, description="Contract length in months")
    cancellation_policy: Optional[str] = Field(None, description="Cancellation policy")
    
    # Benefits list
    benefits: List[MembershipBenefit] = Field(default_factory=list, description="Plan benefits")


class ServicePricing(BaseModel):
    """Service pricing with membership discounts."""
    
    id: str = Field(..., description="Pricing ID")
    service_name: str = Field(..., description="Service name")
    service_category: str = Field(..., description="Service category")
    
    # Base pricing
    base_price: float = Field(..., description="Base service price")
    price_display: str = Field("fixed", description="Price display type (from, fixed, quote_required, free)")
    
    # Member pricing
    residential_member_price: Optional[float] = Field(None, description="Residential member price")
    commercial_member_price: Optional[float] = Field(None, description="Commercial member price")
    premium_member_price: Optional[float] = Field(None, description="Premium member price")
    
    # Service details
    description: Optional[str] = Field(None, description="Service description")
    includes: List[str] = Field(default_factory=list, description="What's included in service")
    duration_estimate: Optional[str] = Field(None, description="Estimated duration")
    minimum_labor_fee: Optional[float] = Field(None, description="Minimum labor charge")
    
    # Service conditions
    height_surcharge: bool = Field(False, description="Height surcharge may apply")
    additional_tech_fee: bool = Field(False, description="Additional technician fee may apply")
    parts_separate: bool = Field(False, description="Parts are charged separately")
    
    # Display
    is_active: bool = Field(True, description="Service pricing is active")
    sort_order: int = Field(0, description="Display order")


class ServicePricingCategory(BaseModel):
    """Service pricing grouped by category."""
    
    category: str = Field(..., description="Category name")
    services: List[ServicePricing] = Field(default_factory=list, description="Services in this category")


class AvailabilitySlot(BaseModel):
    """Available time slot."""
    
    slot_date: date = Field(..., description="Available date")
    start_time: str = Field(..., description="Start time (HH:MM format)")
    end_time: str = Field(..., description="End time (HH:MM format)")
    slot_type: str = Field(..., description="Slot type (regular, emergency, consultation)")
    duration_minutes: int = Field(..., description="Slot duration in minutes")
    available: bool = Field(True, description="Slot is available")


# Shopping Cart Models
class CartItemRequest(BaseModel):
    product_id: str
    installation_option_id: Optional[str] = None
    quantity: int = Field(ge=1, le=100)
    membership_type: Optional[str] = None


class CartItem(BaseModel):
    id: str
    product_id: str
    product_name: str
    product_sku: str
    unit_price: float
    installation_option_id: Optional[str] = None
    installation_option_name: Optional[str] = None
    installation_price: float = 0.0
    quantity: int
    item_total: float
    discount_amount: float = 0.0
    membership_discount: float = 0.0
    bundle_savings: float = 0.0


class ShoppingCart(BaseModel):
    id: str
    business_id: Optional[str] = None
    session_id: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    cart_status: str = "active"
    currency_code: str = "USD"
    items: List[CartItem] = []
    membership_type: Optional[str] = None
    membership_verified: bool = False
    subtotal: float = 0.0
    total_savings: float = 0.0
    tax_amount: float = 0.0
    total_amount: float = 0.0
    item_count: int = 0
    last_activity_at: Optional[str] = None
    created_at: str
    updated_at: str


class CartSummary(BaseModel):
    item_count: int
    subtotal: float
    total_savings: float
    tax_amount: float
    total_amount: float
    savings_percentage: float = 0.0


# Checkout Models
class CheckoutCustomer(BaseModel):
    """Customer information for checkout."""
    
    name: str = Field(..., description="Customer full name")
    email: str = Field(..., description="Customer email address")
    phone: str = Field(..., description="Customer phone number")
    address: str = Field(..., description="Service address")
    city: str = Field(..., description="Service city")
    state: str = Field(..., description="Service state")
    postal_code: str = Field(..., description="Service postal code")


class InstallationPreferences(BaseModel):
    """Installation scheduling preferences."""
    
    preferred_date: str = Field(..., description="Preferred installation date (YYYY-MM-DD)")
    preferred_time: str = Field(..., description="Preferred time slot (morning/afternoon/evening)")
    special_instructions: Optional[str] = Field(None, description="Special installation instructions")
    access_instructions: Optional[str] = Field(None, description="Property access instructions")


class CheckoutRequest(BaseModel):
    """Complete checkout request."""
    
    cart_id: str = Field(..., description="Shopping cart ID")
    customer: CheckoutCustomer
    installation: InstallationPreferences
    membership_type: str = Field(default="none", description="Customer membership type")
    payment_method: str = Field(default="card", description="Payment method (card/check/cash)")
    notes: Optional[str] = Field(None, description="Additional order notes")


class CheckoutResponse(BaseModel):
    """Checkout response with estimate and booking information."""
    
    success: bool
    estimate_id: str
    booking_id: str
    estimate_number: str
    booking_number: str
    total_amount: float
    message: str


# Featured Projects Models
class FeaturedProject(BaseModel):
    """Featured project information."""
    
    id: str = Field(..., description="Project ID")
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Project description")
    trade: str = Field(..., description="Trade type")
    service_category: str = Field(..., description="Service category")
    location: str = Field(..., description="Project location")
    completion_date: Optional[date] = Field(None, description="Project completion date")
    project_duration: str = Field(..., description="Project duration")
    project_value: Optional[float] = Field(None, description="Project value")
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_testimonial: Optional[str] = Field(None, description="Customer testimonial")
    before_images: List[str] = Field(default_factory=list, description="Before images")
    after_images: List[str] = Field(default_factory=list, description="After images")
    gallery_images: List[str] = Field(default_factory=list, description="Gallery images")
    video_url: Optional[str] = Field(None, description="Project video URL")
    challenges_faced: List[str] = Field(default_factory=list, description="Challenges faced")
    solutions_provided: List[str] = Field(default_factory=list, description="Solutions provided")
    equipment_installed: List[str] = Field(default_factory=list, description="Equipment installed")
    warranty_info: Optional[str] = Field(None, description="Warranty information")
    is_featured: bool = Field(False, description="Is featured project")
    seo_slug: str = Field(..., description="SEO slug")
    tags: List[str] = Field(default_factory=list, description="Project tags")
    display_order: int = Field(0, description="Display order")



class ProjectCategory(BaseModel):
    """Project category information."""
    
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="Category slug")
    description: Optional[str] = Field(None, description="Category description")
    icon: Optional[str] = Field(None, description="Category icon")
    project_count: int = Field(0, description="Number of projects in category")
    display_order: int = Field(0, description="Display order")


class MembershipPlan(BaseModel):
    """Customer membership plan information."""
    
    id: str = Field(..., description="Plan ID")
    name: str = Field(..., description="Plan name")
    plan_type: str = Field(..., description="Plan type (residential, commercial, premium)")
    description: str = Field(..., description="Plan description")
    tagline: str = Field(..., description="Plan tagline")
    price_monthly: float = Field(..., description="Monthly price")
    price_yearly: float = Field(..., description="Yearly price")
    yearly_savings: float = Field(..., description="Yearly savings amount")
    setup_fee: float = Field(..., description="Setup fee")
    discount_percentage: int = Field(..., description="Discount percentage")
    priority_service: bool = Field(..., description="Priority service included")
    extended_warranty: bool = Field(..., description="Extended warranty included")
    maintenance_included: bool = Field(..., description="Maintenance included")
    emergency_response: bool = Field(..., description="Emergency response included")
    free_diagnostics: bool = Field(..., description="Free diagnostics included")
    annual_tune_ups: int = Field(..., description="Number of annual tune-ups")
    is_active: bool = Field(..., description="Plan is active")
    is_featured: bool = Field(..., description="Plan is featured")
    popular_badge: Optional[str] = Field(None, description="Popular badge text")
    color_scheme: str = Field(..., description="Plan color scheme")
    sort_order: int = Field(..., description="Sort order")
    contract_length_months: int = Field(..., description="Contract length in months")
    cancellation_policy: str = Field(..., description="Cancellation policy")
