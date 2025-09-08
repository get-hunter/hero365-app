"""
Product-Service Association Application Service

Handles business logic for product-service associations.
"""

import logging
from typing import List, Optional
from uuid import UUID

from ...domain.entities.product_service_association import (
    ProductServiceAssociation,
    ProductServiceAssociationCreate,
    ProductServiceAssociationUpdate,
    AssociationType
)
from ...infrastructure.repositories.product_service_association_repository import (
    SupabaseProductServiceAssociationRepository
)
from ...application.exceptions.application_exceptions import EntityNotFoundError, ValidationError, ApplicationError

logger = logging.getLogger(__name__)


class ProductServiceAssociationService:
    """Application service for product-service associations."""
    
    def __init__(self, repository: SupabaseProductServiceAssociationRepository):
        self.repository = repository
    
    async def create_association(
        self,
        business_id: UUID,
        association: ProductServiceAssociationCreate
    ) -> ProductServiceAssociation:
        """Create a new product-service association."""
        try:
            # Validate business owns both product and service
            # TODO: Add validation that business owns the product and service
            
            return await self.repository.create(business_id, association)
            
        except Exception as e:
            logger.error(f"Error creating association: {str(e)}")
            raise ApplicationError(f"Failed to create association: {str(e)}")
    
    async def get_service_products(
        self,
        business_id: UUID,
        service_id: UUID,
        association_type: Optional[AssociationType] = None,
        featured_only: bool = False
    ) -> List[dict]:
        """Get products associated with a service."""
        try:
            if featured_only:
                associations = await self.repository.get_by_service(
                    business_id, service_id, association_type, featured_only=True
                )
                # Convert to dict format for consistency
                results = []
                for assoc in associations:
                    # Get product details - simplified for now
                    results.append({
                        "association": assoc,
                        "product": None  # Would fetch product details
                    })
                return results
            else:
                return await self.repository.get_products_for_service(
                    business_id, service_id, association_type
                )
                
        except Exception as e:
            logger.error(f"Error getting service products: {str(e)}")
            raise ApplicationError(f"Failed to get service products: {str(e)}")
    
    async def get_product_services(
        self,
        business_id: UUID,
        product_id: UUID
    ) -> List[ProductServiceAssociation]:
        """Get services associated with a product."""
        try:
            return await self.repository.get_by_product(business_id, product_id)
            
        except Exception as e:
            logger.error(f"Error getting product services: {str(e)}")
            raise ApplicationError(f"Failed to get product services: {str(e)}")
    
    async def update_association(
        self,
        association_id: UUID,
        updates: ProductServiceAssociationUpdate
    ) -> ProductServiceAssociation:
        """Update an association."""
        try:
            return await self.repository.update(association_id, updates)
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating association: {str(e)}")
            raise ApplicationError(f"Failed to update association: {str(e)}")
    
    async def delete_association(self, association_id: UUID) -> bool:
        """Delete an association."""
        try:
            return await self.repository.delete(association_id)
            
        except Exception as e:
            logger.error(f"Error deleting association: {str(e)}")
            raise ApplicationError(f"Failed to delete association: {str(e)}")
    
    async def get_recommended_products(
        self,
        business_id: UUID,
        service_id: UUID,
        limit: int = 10
    ) -> List[dict]:
        """Get recommended products for a service."""
        try:
            # Get required and recommended products
            required = await self.repository.get_products_for_service(
                business_id, service_id, AssociationType.REQUIRED
            )
            recommended = await self.repository.get_products_for_service(
                business_id, service_id, AssociationType.RECOMMENDED
            )
            
            # Combine and limit
            all_products = required + recommended
            return all_products[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recommended products: {str(e)}")
            raise ApplicationError(f"Failed to get recommended products: {str(e)}")
    
    async def get_upsell_products(
        self,
        business_id: UUID,
        service_id: UUID,
        limit: int = 5
    ) -> List[dict]:
        """Get upsell products for a service."""
        try:
            return await self.repository.get_products_for_service(
                business_id, service_id, AssociationType.UPSELL
            )[:limit]
            
        except Exception as e:
            logger.error(f"Error getting upsell products: {str(e)}")
            raise ApplicationError(f"Failed to get upsell products: {str(e)}")
