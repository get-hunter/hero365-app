"""
Product-Service Association Repository

Handles data access for product-service associations using Supabase.
"""

import logging
from typing import List, Optional
from uuid import UUID

from supabase import Client

from ...domain.entities.product_service_association import (
    ProductServiceAssociation,
    ProductServiceAssociationCreate,
    ProductServiceAssociationUpdate,
    AssociationType
)
from ...application.exceptions.application_exceptions import EntityNotFoundError, ApplicationError as RepositoryError

logger = logging.getLogger(__name__)


class SupabaseProductServiceAssociationRepository:
    """Supabase implementation of product-service association repository."""
    
    def __init__(self, client: Client):
        self.client = client
        self.table = "product_service_associations"
    
    async def create(
        self, 
        business_id: UUID, 
        association: ProductServiceAssociationCreate
    ) -> ProductServiceAssociation:
        """Create a new product-service association."""
        try:
            data = {
                "business_id": str(business_id),
                "product_id": str(association.product_id),
                "service_id": str(association.service_id),
                "association_type": association.association_type.value,
                "display_order": association.display_order,
                "is_featured": association.is_featured,
                "service_discount_percentage": association.service_discount_percentage,
                "bundle_price": float(association.bundle_price) if association.bundle_price else None,
                "notes": association.notes
            }
            
            result = self.client.table(self.table).insert(data).execute()
            
            if not result.data:
                raise RepositoryError("Failed to create product-service association")
            
            return ProductServiceAssociation(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error creating product-service association: {str(e)}")
            raise RepositoryError(f"Failed to create association: {str(e)}")
    
    async def get_by_id(self, association_id: UUID) -> Optional[ProductServiceAssociation]:
        """Get association by ID."""
        try:
            result = self.client.table(self.table).select("*").eq("id", str(association_id)).execute()
            
            if not result.data:
                return None
            
            return ProductServiceAssociation(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error getting association {association_id}: {str(e)}")
            raise RepositoryError(f"Failed to get association: {str(e)}")
    
    async def get_by_service(
        self, 
        business_id: UUID, 
        service_id: UUID,
        association_type: Optional[AssociationType] = None,
        featured_only: bool = False
    ) -> List[ProductServiceAssociation]:
        """Get associations for a service."""
        try:
            query = (
                self.client.table(self.table)
                .select("*")
                .eq("business_id", str(business_id))
                .eq("service_id", str(service_id))
                .order("display_order", desc=False)
                .order("created_at", desc=False)
            )
            
            if association_type:
                query = query.eq("association_type", association_type.value)
            
            if featured_only:
                query = query.eq("is_featured", True)
            
            result = query.execute()
            
            return [ProductServiceAssociation(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error getting associations for service {service_id}: {str(e)}")
            raise RepositoryError(f"Failed to get service associations: {str(e)}")
    
    async def get_by_product(
        self, 
        business_id: UUID, 
        product_id: UUID
    ) -> List[ProductServiceAssociation]:
        """Get associations for a product."""
        try:
            result = (
                self.client.table(self.table)
                .select("*")
                .eq("business_id", str(business_id))
                .eq("product_id", str(product_id))
                .order("display_order", desc=False)
                .execute()
            )
            
            return [ProductServiceAssociation(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error getting associations for product {product_id}: {str(e)}")
            raise RepositoryError(f"Failed to get product associations: {str(e)}")
    
    async def update(
        self, 
        association_id: UUID, 
        updates: ProductServiceAssociationUpdate
    ) -> ProductServiceAssociation:
        """Update an association."""
        try:
            # Build update data
            update_data = {}
            if updates.association_type is not None:
                update_data["association_type"] = updates.association_type.value
            if updates.display_order is not None:
                update_data["display_order"] = updates.display_order
            if updates.is_featured is not None:
                update_data["is_featured"] = updates.is_featured
            if updates.service_discount_percentage is not None:
                update_data["service_discount_percentage"] = updates.service_discount_percentage
            if updates.bundle_price is not None:
                update_data["bundle_price"] = float(updates.bundle_price)
            if updates.notes is not None:
                update_data["notes"] = updates.notes
            
            if not update_data:
                # No updates provided, return current
                current = await self.get_by_id(association_id)
                if not current:
                    raise EntityNotFoundError("ProductServiceAssociation", str(association_id))
                return current
            
            result = (
                self.client.table(self.table)
                .update(update_data)
                .eq("id", str(association_id))
                .execute()
            )
            
            if not result.data:
                raise EntityNotFoundError("ProductServiceAssociation", str(association_id))
            
            return ProductServiceAssociation(**result.data[0])
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating association {association_id}: {str(e)}")
            raise RepositoryError(f"Failed to update association: {str(e)}")
    
    async def delete(self, association_id: UUID) -> bool:
        """Delete an association."""
        try:
            result = (
                self.client.table(self.table)
                .delete()
                .eq("id", str(association_id))
                .execute()
            )
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting association {association_id}: {str(e)}")
            raise RepositoryError(f"Failed to delete association: {str(e)}")
    
    async def get_products_for_service(
        self, 
        business_id: UUID, 
        service_id: UUID,
        association_type: Optional[AssociationType] = None
    ) -> List[dict]:
        """Get products associated with a service with product details."""
        try:
            query = """
            SELECT 
                psa.*,
                p.name as product_name,
                p.description as product_description,
                p.unit_price,
                p.featured_image_url,
                p.is_active as product_is_active,
                p.category as product_category
            FROM product_service_associations psa
            JOIN products p ON psa.product_id = p.id
            WHERE psa.business_id = %s 
            AND psa.service_id = %s
            AND p.is_active = true
            """
            
            params = [str(business_id), str(service_id)]
            
            if association_type:
                query += " AND psa.association_type = %s"
                params.append(association_type.value)
            
            query += " ORDER BY psa.display_order, psa.created_at"
            
            # Note: Using raw SQL for join - in production you'd want proper join support
            # For now, we'll do separate queries
            associations = await self.get_by_service(business_id, service_id, association_type)
            
            results = []
            for assoc in associations:
                # Get product details
                product_result = (
                    self.client.table("products")
                    .select("*")
                    .eq("id", str(assoc.product_id))
                    .eq("is_active", True)
                    .execute()
                )
                
                if product_result.data:
                    product = product_result.data[0]
                    results.append({
                        "association": assoc,
                        "product": product
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting products for service {service_id}: {str(e)}")
            raise RepositoryError(f"Failed to get service products: {str(e)}")
