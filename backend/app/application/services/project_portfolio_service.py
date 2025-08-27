"""
Project Portfolio Application Service

Service layer for project portfolio management operations.
"""

import uuid
import logging
from typing import Optional, List
from decimal import Decimal

from ..dto.project_portfolio_dto import (
    FeaturedProjectDTO, ProjectCategoryDTO, ProjectTagDTO, ProjectSearchCriteria
)
from ...domain.repositories.business_repository import BusinessRepository
from ..exceptions.application_exceptions import (
    ApplicationError, ValidationError, EntityNotFoundError
)
from ...core.db import get_supabase_client

logger = logging.getLogger(__name__)


class ProjectPortfolioService:
    """
    Application service for project portfolio management.
    
    Encapsulates business logic for project operations and coordinates
    between the domain and infrastructure layers.
    """
    
    def __init__(self, business_repository: BusinessRepository):
        self.business_repository = business_repository
        self.supabase = get_supabase_client()
        logger.info("ProjectPortfolioService initialized")
    
    async def get_featured_projects(
        self, 
        business_id: str, 
        search_criteria: ProjectSearchCriteria
    ) -> List[FeaturedProjectDTO]:
        """
        Get featured projects for a business.
        
        Args:
            business_id: Business identifier
            search_criteria: Search and filter criteria
            
        Returns:
            List of featured projects as DTOs
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # Build query
            query = self.supabase.table("featured_projects").select(
                """
                id, title, description, trade, service_category, location,
                completion_date, project_duration, project_value, customer_name,
                customer_testimonial, before_images, after_images, gallery_images,
                video_url, challenges_faced, solutions_provided, equipment_installed,
                warranty_info, is_featured, seo_slug, tags, display_order
                """
            ).eq("business_id", business_id)
            
            # Apply filters
            if search_criteria.trade:
                query = query.eq("trade", search_criteria.trade)
            if search_criteria.category:
                query = query.eq("service_category", search_criteria.category)
            if search_criteria.featured_only:
                query = query.eq("is_featured", True)
            
            # Apply pagination and ordering
            query = query.order("display_order").order("completion_date", desc=True)
            query = query.range(search_criteria.offset, search_criteria.offset + search_criteria.limit - 1)
            
            result = query.execute()
            
            # Convert to DTOs
            project_dtos = []
            for project_data in result.data:
                project_dto = self._convert_to_project_dto(project_data, business_id)
                project_dtos.append(project_dto)
            
            logger.info(f"Retrieved {len(project_dtos)} featured projects for business {business_id}")
            return project_dtos
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error retrieving featured projects for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve featured projects: {str(e)}")
    
    async def get_project_by_slug(self, business_id: str, project_slug: str) -> FeaturedProjectDTO:
        """
        Get project details by SEO slug.
        
        Args:
            business_id: Business identifier
            project_slug: Project SEO slug
            
        Returns:
            Project details as DTO
            
        Raises:
            EntityNotFoundError: If business or project doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # Get project details
            result = self.supabase.table("featured_projects").select(
                """
                id, title, description, trade, service_category, location,
                completion_date, project_duration, project_value, customer_name,
                customer_testimonial, before_images, after_images, gallery_images,
                video_url, challenges_faced, solutions_provided, equipment_installed,
                warranty_info, is_featured, seo_slug, tags, display_order
                """
            ).eq("business_id", business_id).eq("seo_slug", project_slug).execute()
            
            if not result.data:
                raise EntityNotFoundError(f"Project not found: {project_slug}")
            
            project_data = result.data[0]
            project_dto = self._convert_to_project_dto(project_data, business_id)
            
            logger.info(f"Retrieved project {project_slug} for business {business_id}")
            return project_dto
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving project {project_slug} for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve project: {str(e)}")
    
    async def get_project_categories(self, business_id: str) -> List[ProjectCategoryDTO]:
        """
        Get project categories for a business.
        
        Args:
            business_id: Business identifier
            
        Returns:
            List of project categories as DTOs
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # Get categories with project counts
            categories_result = self.supabase.table("project_categories").select(
                "id, name, slug, description, icon, display_order"
            ).eq("business_id", business_id).eq("is_active", True).order("display_order").execute()
            
            category_dtos = []
            for category_data in categories_result.data:
                # Count projects in this category
                count_result = self.supabase.table("featured_projects").select(
                    "id", count="exact"
                ).eq("business_id", business_id).eq("service_category", category_data["name"]).execute()
                
                project_count = count_result.count or 0
                
                category_dto = ProjectCategoryDTO(
                    id=str(category_data["id"]),
                    business_id=business_id,
                    name=category_data["name"],
                    slug=category_data["slug"],
                    description=category_data.get("description"),
                    icon=category_data.get("icon"),
                    project_count=project_count,
                    display_order=category_data.get("display_order", 0)
                )
                category_dtos.append(category_dto)
            
            logger.info(f"Retrieved {len(category_dtos)} project categories for business {business_id}")
            return category_dtos
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error retrieving project categories for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve project categories: {str(e)}")
    
    async def get_project_tags(self, business_id: str) -> List[ProjectTagDTO]:
        """
        Get project tags for a business.
        
        Args:
            business_id: Business identifier
            
        Returns:
            List of project tags as DTOs
            
        Raises:
            EntityNotFoundError: If business doesn't exist
            ValidationError: If parameters are invalid
            ApplicationError: If retrieval fails
        """
        try:
            business_uuid = uuid.UUID(business_id)
            
            # Verify business exists
            business = await self.business_repository.get_by_id(business_uuid)
            if not business:
                raise EntityNotFoundError(f"Business not found: {business_id}")
            
            # Get tags with usage counts
            result = self.supabase.table("project_tags").select(
                "id, name, slug, color, usage_count"
            ).eq("business_id", business_id).eq("is_active", True).order("usage_count", desc=True).execute()
            
            tag_dtos = []
            for tag_data in result.data:
                tag_dto = ProjectTagDTO(
                    id=str(tag_data["id"]),
                    business_id=business_id,
                    name=tag_data["name"],
                    slug=tag_data["slug"],
                    color=tag_data.get("color", "#3B82F6"),
                    usage_count=tag_data.get("usage_count", 0)
                )
                tag_dtos.append(tag_dto)
            
            logger.info(f"Retrieved {len(tag_dtos)} project tags for business {business_id}")
            return tag_dtos
            
        except ValueError as e:
            raise ValidationError(f"Invalid business ID format: {business_id}")
        except Exception as e:
            logger.error(f"Error retrieving project tags for business {business_id}: {str(e)}")
            raise ApplicationError(f"Failed to retrieve project tags: {str(e)}")
    
    def _convert_to_project_dto(self, project_data: dict, business_id: str) -> FeaturedProjectDTO:
        """Convert database project data to DTO."""
        return FeaturedProjectDTO(
            id=str(project_data["id"]),
            business_id=business_id,
            title=project_data["title"],
            description=project_data.get("description", ""),
            trade=project_data["trade"],
            service_category=project_data["service_category"],
            location=project_data["location"],
            completion_date=project_data["completion_date"],
            project_duration=project_data.get("project_duration", ""),
            project_value=Decimal(str(project_data["project_value"])) if project_data.get("project_value") else None,
            customer_name=project_data.get("customer_name"),
            customer_testimonial=project_data.get("customer_testimonial"),
            before_images=project_data.get("before_images", []),
            after_images=project_data.get("after_images", []),
            gallery_images=project_data.get("gallery_images", []),
            video_url=project_data.get("video_url"),
            challenges_faced=project_data.get("challenges_faced", []),
            solutions_provided=project_data.get("solutions_provided", []),
            equipment_installed=project_data.get("equipment_installed", []),
            warranty_info=project_data.get("warranty_info"),
            is_featured=project_data.get("is_featured", False),
            seo_slug=project_data["seo_slug"],
            tags=project_data.get("tags", []),
            display_order=project_data.get("display_order", 0)
        )
