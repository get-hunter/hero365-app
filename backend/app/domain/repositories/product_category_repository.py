"""
Product Category Repository Interface

Repository interface for product category management with hierarchical structure support,
category defaults, and product organization capabilities.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import uuid

from ..entities.product_category import ProductCategory


class ProductCategoryRepository(ABC):
    """Repository interface for product category management operations."""
    
    # Basic CRUD operations
    @abstractmethod
    async def create(self, category: ProductCategory) -> ProductCategory:
        """Create a new product category."""
        pass
    
    @abstractmethod
    async def get_by_id(self, business_id: uuid.UUID, category_id: uuid.UUID) -> Optional[ProductCategory]:
        """Get category by ID."""
        pass
    
    @abstractmethod
    async def get_by_name(self, business_id: uuid.UUID, name: str, parent_id: Optional[uuid.UUID] = None) -> Optional[ProductCategory]:
        """Get category by name within the same parent."""
        pass
    
    @abstractmethod
    async def update(self, category: ProductCategory) -> ProductCategory:
        """Update an existing category."""
        pass
    
    @abstractmethod
    async def delete(self, business_id: uuid.UUID, category_id: uuid.UUID) -> bool:
        """Delete a category (only if empty)."""
        pass
    
    # Hierarchy management
    @abstractmethod
    async def get_root_categories(self, business_id: uuid.UUID, active_only: bool = True) -> List[ProductCategory]:
        """Get all root categories (no parent)."""
        pass
    
    @abstractmethod
    async def get_children(self, business_id: uuid.UUID, parent_id: uuid.UUID, active_only: bool = True) -> List[ProductCategory]:
        """Get direct children of a category."""
        pass
    
    @abstractmethod
    async def get_descendants(self, business_id: uuid.UUID, parent_id: uuid.UUID, active_only: bool = True) -> List[ProductCategory]:
        """Get all descendants of a category (recursive)."""
        pass
    
    @abstractmethod
    async def get_ancestors(self, business_id: uuid.UUID, category_id: uuid.UUID) -> List[ProductCategory]:
        """Get all ancestors of a category up to root."""
        pass
    
    @abstractmethod
    async def get_hierarchy_tree(self, business_id: uuid.UUID, root_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Get the complete category hierarchy as a tree structure."""
        pass
    
    @abstractmethod
    async def get_category_path(self, business_id: uuid.UUID, category_id: uuid.UUID) -> List[ProductCategory]:
        """Get the complete path from root to category."""
        pass
    
    @abstractmethod
    async def move_category(self, business_id: uuid.UUID, category_id: uuid.UUID, new_parent_id: Optional[uuid.UUID]) -> bool:
        """Move a category to a new parent."""
        pass
    
    @abstractmethod
    async def get_max_level(self, business_id: uuid.UUID) -> int:
        """Get the maximum hierarchy level in the business."""
        pass
    
    # Category validation
    @abstractmethod
    async def can_move_to_parent(self, business_id: uuid.UUID, category_id: uuid.UUID, new_parent_id: Optional[uuid.UUID]) -> bool:
        """Check if a category can be moved to a new parent without creating cycles."""
        pass
    
    @abstractmethod
    async def can_delete_category(self, business_id: uuid.UUID, category_id: uuid.UUID) -> bool:
        """Check if a category can be deleted (no products, no subcategories)."""
        pass
    
    @abstractmethod
    async def exists_by_name(self, business_id: uuid.UUID, name: str, parent_id: Optional[uuid.UUID] = None, exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if a category with the given name exists in the same parent."""
        pass
    
    # Product association management
    @abstractmethod
    async def update_product_counts(self, business_id: uuid.UUID, category_id: uuid.UUID) -> bool:
        """Recalculate and update product counts for a category."""
        pass
    
    @abstractmethod
    async def increment_product_count(self, business_id: uuid.UUID, category_id: uuid.UUID, active_product: bool = True) -> bool:
        """Increment product count when a product is added."""
        pass
    
    @abstractmethod
    async def decrement_product_count(self, business_id: uuid.UUID, category_id: uuid.UUID, was_active: bool = True) -> bool:
        """Decrement product count when a product is removed."""
        pass
    
    @abstractmethod
    async def update_product_active_status(self, business_id: uuid.UUID, category_id: uuid.UUID, is_now_active: bool, was_active: bool) -> bool:
        """Update active product count when a product's status changes."""
        pass
    
    # Subcategory management
    @abstractmethod
    async def increment_subcategory_count(self, business_id: uuid.UUID, parent_id: uuid.UUID) -> bool:
        """Increment subcategory count when a subcategory is added."""
        pass
    
    @abstractmethod
    async def decrement_subcategory_count(self, business_id: uuid.UUID, parent_id: uuid.UUID) -> bool:
        """Decrement subcategory count when a subcategory is removed."""
        pass
    
    @abstractmethod
    async def update_subcategory_counts(self, business_id: uuid.UUID, category_id: uuid.UUID) -> bool:
        """Recalculate subcategory counts for a category."""
        pass
    
    # List and search operations
    @abstractmethod
    async def list_by_business(self, business_id: uuid.UUID, active_only: bool = True, include_empty: bool = True) -> List[ProductCategory]:
        """List all categories for a business."""
        pass
    
    @abstractmethod
    async def search_categories(self, business_id: uuid.UUID, query: str, limit: int = 50) -> List[ProductCategory]:
        """Search categories by name or description."""
        pass
    
    @abstractmethod
    async def get_categories_by_level(self, business_id: uuid.UUID, level: int, active_only: bool = True) -> List[ProductCategory]:
        """Get all categories at a specific hierarchy level."""
        pass
    
    @abstractmethod
    async def get_leaf_categories(self, business_id: uuid.UUID, active_only: bool = True) -> List[ProductCategory]:
        """Get all leaf categories (no subcategories)."""
        pass
    
    @abstractmethod
    async def get_categories_with_products(self, business_id: uuid.UUID, active_only: bool = True) -> List[ProductCategory]:
        """Get categories that have products."""
        pass
    
    @abstractmethod
    async def get_empty_categories(self, business_id: uuid.UUID) -> List[ProductCategory]:
        """Get categories with no products and no subcategories."""
        pass
    
    # Category defaults and configuration
    @abstractmethod
    async def apply_defaults_to_products(self, business_id: uuid.UUID, category_id: uuid.UUID) -> int:
        """Apply category defaults to all products in the category."""
        pass
    
    @abstractmethod
    async def get_inherited_defaults(self, business_id: uuid.UUID, category_id: uuid.UUID) -> Dict[str, Any]:
        """Get inherited defaults from parent categories."""
        pass
    
    @abstractmethod
    async def update_category_defaults(self, business_id: uuid.UUID, category_id: uuid.UUID, defaults: Dict[str, Any]) -> bool:
        """Update category defaults."""
        pass
    
    # Bulk operations
    @abstractmethod
    async def bulk_update_status(self, business_id: uuid.UUID, category_ids: List[uuid.UUID], is_active: bool) -> int:
        """Bulk update category status."""
        pass
    
    @abstractmethod
    async def bulk_move_categories(self, business_id: uuid.UUID, moves: List[Dict[str, uuid.UUID]]) -> int:
        """Bulk move categories to new parents."""
        pass
    
    @abstractmethod
    async def rebuild_hierarchy_paths(self, business_id: uuid.UUID) -> bool:
        """Rebuild all category paths and levels."""
        pass
    
    # Sort order management
    @abstractmethod
    async def update_sort_order(self, business_id: uuid.UUID, category_id: uuid.UUID, sort_order: int) -> bool:
        """Update category sort order within its parent."""
        pass
    
    @abstractmethod
    async def reorder_siblings(self, business_id: uuid.UUID, parent_id: Optional[uuid.UUID], category_orders: List[Dict[str, Any]]) -> bool:
        """Reorder categories within the same parent."""
        pass
    
    @abstractmethod
    async def get_next_sort_order(self, business_id: uuid.UUID, parent_id: Optional[uuid.UUID]) -> int:
        """Get the next available sort order for a new category."""
        pass
    
    # Mobile app optimization
    @abstractmethod
    async def get_categories_for_mobile(self, business_id: uuid.UUID, parent_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Get categories optimized for mobile app consumption."""
        pass
    
    @abstractmethod
    async def get_category_breadcrumb(self, business_id: uuid.UUID, category_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get category breadcrumb for mobile navigation."""
        pass
    
    @abstractmethod
    async def get_category_tree_for_selection(self, business_id: uuid.UUID, max_depth: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get flattened category tree for product category selection."""
        pass
    
    # Analytics and reporting
    @abstractmethod
    async def get_category_analytics(self, business_id: uuid.UUID, category_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Get category analytics including product counts, sales data, etc."""
        pass
    
    @abstractmethod
    async def get_category_distribution(self, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get distribution of products across categories."""
        pass
    
    @abstractmethod
    async def get_unused_categories(self, business_id: uuid.UUID, days_threshold: int = 90) -> List[ProductCategory]:
        """Get categories with no recent product activity."""
        pass
    
    # Count operations
    @abstractmethod
    async def count_categories(self, business_id: uuid.UUID, parent_id: Optional[uuid.UUID] = None, active_only: bool = True) -> int:
        """Count categories with optional parent filtering."""
        pass
    
    @abstractmethod
    async def count_total_products_in_hierarchy(self, business_id: uuid.UUID, category_id: uuid.UUID) -> int:
        """Count total products in category and all its descendants."""
        pass 