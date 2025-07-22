"""
Product Category Domain Entity

Represents a product category for organizing products in a hierarchical structure
with business rules and category-level settings.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, validator, computed_field

from ..exceptions.domain_exceptions import DomainValidationError, BusinessRuleViolationError
from ..shared.enums import TaxType, CurrencyCode

# Configure logging
logger = logging.getLogger(__name__)


class CategoryDefaults(BaseModel):
    """Default settings for products in this category."""
    default_tax_type: Optional[TaxType] = Field(None, description="Default tax type for products")
    default_tax_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Default tax rate percentage")
    default_markup_percentage: Optional[Decimal] = Field(None, ge=0, description="Default markup percentage")
    default_unit_of_measure: Optional[str] = Field(None, max_length=50, description="Default unit of measure")
    track_inventory_default: bool = Field(default=True, description="Default inventory tracking setting")
    
    class Config:
        use_enum_values = True


class ProductCategory(BaseModel):
    """
    Product Category domain entity.
    
    Represents a hierarchical category system for organizing products
    with category-level defaults and business rules.
    """
    
    # Basic category information
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Category unique identifier")
    business_id: uuid.UUID = Field(..., description="Business identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Category name")
    description: Optional[str] = Field(None, max_length=1000, description="Category description")
    
    # Hierarchical structure
    parent_id: Optional[uuid.UUID] = Field(None, description="Parent category identifier")
    parent_name: Optional[str] = Field(None, max_length=200, description="Parent category name")
    level: int = Field(default=0, ge=0, le=10, description="Category level in hierarchy")
    path: str = Field(..., max_length=500, description="Full category path")
    
    # Category settings
    is_active: bool = Field(default=True, description="Whether category is active")
    sort_order: int = Field(default=0, description="Sort order within parent category")
    
    # Category defaults for products
    defaults: CategoryDefaults = Field(default_factory=CategoryDefaults, description="Default settings for products")
    
    # Images and branding
    image_url: Optional[str] = Field(None, description="Category image URL")
    icon: Optional[str] = Field(None, max_length=100, description="Category icon identifier")
    color: Optional[str] = Field(None, max_length=7, description="Category color (hex code)")
    
    # Analytics
    product_count: int = Field(default=0, ge=0, description="Number of products in category")
    active_product_count: int = Field(default=0, ge=0, description="Number of active products")
    subcategory_count: int = Field(default=0, ge=0, description="Number of subcategories")
    
    # Metadata
    created_by: str = Field(..., description="User who created the category")
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation date")
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last modification date")
    
    # Business rules validation
    @validator('name')
    def validate_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Category name cannot be empty')
        return v.strip()
    
    @validator('path')
    def validate_path(cls, v, values):
        if not v or v.strip() == "":
            if 'name' in values:
                return values['name'].strip()
            raise ValueError('Category path cannot be empty')
        return v.strip()
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None:
            import re
            if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
                raise ValueError('Color must be a valid hex code (e.g., #FF0000)')
        return v
    
    @validator('level')
    def validate_level(cls, v, values):
        if v < 0:
            raise ValueError('Category level cannot be negative')
        if v > 10:
            raise ValueError('Category hierarchy cannot exceed 10 levels')
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
    def full_name(self) -> str:
        """Get full category name including parent path."""
        return self.path
    
    @computed_field
    @property
    def has_products(self) -> bool:
        """Check if category has any products."""
        return self.product_count > 0
    
    @computed_field
    @property
    def has_subcategories(self) -> bool:
        """Check if category has subcategories."""
        return self.subcategory_count > 0
    
    @computed_field
    @property
    def is_root_category(self) -> bool:
        """Check if this is a root category."""
        return self.parent_id is None
    
    @computed_field
    @property
    def is_leaf_category(self) -> bool:
        """Check if this is a leaf category (no subcategories)."""
        return self.subcategory_count == 0
    
    # Business logic methods
    def can_be_deleted(self) -> bool:
        """
        Check if category can be deleted.
        Categories can only be deleted if they have no products and no subcategories.
        """
        return self.product_count == 0 and self.subcategory_count == 0
    
    def can_add_subcategory(self) -> bool:
        """Check if subcategories can be added to this category."""
        return self.level < 10  # Maximum hierarchy depth
    
    def update_path(self, parent_path: Optional[str] = None):
        """
        Update the category path based on parent path and current name.
        
        Args:
            parent_path: Path of the parent category
        """
        if parent_path:
            self.path = f"{parent_path} > {self.name}"
        else:
            self.path = self.name
        
        self.last_modified = datetime.now(timezone.utc)
    
    def update_level(self, parent_level: Optional[int] = None):
        """
        Update the category level based on parent level.
        
        Args:
            parent_level: Level of the parent category
        """
        if parent_level is not None:
            self.level = parent_level + 1
        else:
            self.level = 0
        
        self.last_modified = datetime.now(timezone.utc)
    
    def increment_product_count(self, active_product: bool = True):
        """
        Increment product count when a product is added to this category.
        
        Args:
            active_product: Whether the product is active
        """
        self.product_count += 1
        if active_product:
            self.active_product_count += 1
        self.last_modified = datetime.now(timezone.utc)
    
    def decrement_product_count(self, was_active: bool = True):
        """
        Decrement product count when a product is removed from this category.
        
        Args:
            was_active: Whether the product was active
        """
        self.product_count = max(0, self.product_count - 1)
        if was_active:
            self.active_product_count = max(0, self.active_product_count - 1)
        self.last_modified = datetime.now(timezone.utc)
    
    def update_product_active_status(self, is_now_active: bool, was_active: bool):
        """
        Update active product count when a product's status changes.
        
        Args:
            is_now_active: Whether the product is now active
            was_active: Whether the product was previously active
        """
        if is_now_active and not was_active:
            self.active_product_count += 1
        elif not is_now_active and was_active:
            self.active_product_count = max(0, self.active_product_count - 1)
        
        if is_now_active != was_active:
            self.last_modified = datetime.now(timezone.utc)
    
    def increment_subcategory_count(self):
        """Increment subcategory count when a subcategory is added."""
        self.subcategory_count += 1
        self.last_modified = datetime.now(timezone.utc)
    
    def decrement_subcategory_count(self):
        """Decrement subcategory count when a subcategory is removed."""
        self.subcategory_count = max(0, self.subcategory_count - 1)
        self.last_modified = datetime.now(timezone.utc)
    
    def activate(self):
        """Activate the category."""
        if not self.is_active:
            self.is_active = True
            self.last_modified = datetime.now(timezone.utc)
            logger.info(f"Category {self.name} activated")
    
    def deactivate(self):
        """
        Deactivate the category.
        Note: This should be validated at the service level to ensure
        no active products are in this category.
        """
        if self.is_active:
            self.is_active = False
            self.last_modified = datetime.now(timezone.utc)
            logger.info(f"Category {self.name} deactivated")
    
    def get_hierarchy_level_display(self) -> str:
        """Get display string for hierarchy level."""
        if self.level == 0:
            return "Root Category"
        elif self.level == 1:
            return "Main Category"
        elif self.level == 2:
            return "Subcategory"
        else:
            return f"Level {self.level} Category"
    
    def get_breadcrumb(self) -> List[str]:
        """Get breadcrumb trail as list of category names."""
        return self.path.split(" > ")
    
    def apply_defaults_to_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply category defaults to product data if not already specified.
        
        Args:
            product_data: Product data dictionary
            
        Returns:
            Updated product data with category defaults applied
        """
        updated_data = product_data.copy()
        
        # Apply tax defaults
        if self.defaults.default_tax_type and 'tax_type' not in updated_data:
            updated_data['tax_type'] = self.defaults.default_tax_type
        
        if self.defaults.default_tax_rate and 'tax_rate' not in updated_data:
            updated_data['tax_rate'] = self.defaults.default_tax_rate
        
        # Apply markup default
        if self.defaults.default_markup_percentage and 'markup_percentage' not in updated_data:
            updated_data['markup_percentage'] = self.defaults.default_markup_percentage
        
        # Apply unit of measure default
        if self.defaults.default_unit_of_measure and 'unit_of_measure' not in updated_data:
            updated_data['unit_of_measure'] = self.defaults.default_unit_of_measure
        
        # Apply inventory tracking default
        if 'track_inventory' not in updated_data:
            updated_data['track_inventory'] = self.defaults.track_inventory_default
        
        return updated_data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert category to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": str(self.business_id),
            "name": self.name,
            "description": self.description,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "parent_name": self.parent_name,
            "level": self.level,
            "level_display": self.get_hierarchy_level_display(),
            "path": self.path,
            "full_name": self.full_name,
            "breadcrumb": self.get_breadcrumb(),
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "is_root_category": self.is_root_category,
            "is_leaf_category": self.is_leaf_category,
            "has_products": self.has_products,
            "has_subcategories": self.has_subcategories,
            "product_count": self.product_count,
            "active_product_count": self.active_product_count,
            "subcategory_count": self.subcategory_count,
            "can_be_deleted": self.can_be_deleted(),
            "can_add_subcategory": self.can_add_subcategory(),
            "defaults": {
                "default_tax_type": self.defaults.default_tax_type.value if self.defaults.default_tax_type else None,
                "default_tax_rate": float(self.defaults.default_tax_rate) if self.defaults.default_tax_rate else None,
                "default_markup_percentage": float(self.defaults.default_markup_percentage) if self.defaults.default_markup_percentage else None,
                "default_unit_of_measure": self.defaults.default_unit_of_measure,
                "track_inventory_default": self.defaults.track_inventory_default
            },
            "image_url": self.image_url,
            "icon": self.icon,
            "color": self.color,
            "created_by": self.created_by,
            "created_date": self.created_date.isoformat(),
            "last_modified": self.last_modified.isoformat()
        }
    
    def __str__(self) -> str:
        return f"ProductCategory({self.path})"
    
    def __repr__(self) -> str:
        return f"ProductCategory(id={self.id}, name='{self.name}', level={self.level})" 