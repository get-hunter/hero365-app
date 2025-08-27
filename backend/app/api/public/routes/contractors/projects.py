"""
Contractor Featured Projects API Routes

Public endpoints for retrieving featured projects and portfolio information.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional, List, Dict, Any
from datetime import date
import logging

from .schemas import FeaturedProject, ProjectCategory
from app.application.services.project_portfolio_service import ProjectPortfolioService
from app.application.dto.project_portfolio_dto import ProjectSearchCriteria
from app.application.exceptions.application_exceptions import (
    ApplicationError, ValidationError, EntityNotFoundError
)
from app.infrastructure.config.dependency_injection import get_business_repository

logger = logging.getLogger(__name__)

router = APIRouter()


def get_project_portfolio_service():
    """Dependency injection for ProjectPortfolioService."""
    business_repo = get_business_repository()
    return ProjectPortfolioService(business_repo)


@router.get("/featured-projects/{business_id}", response_model=List[FeaturedProject])
async def get_featured_projects(
    business_id: str = Path(..., description="Business ID"),
    trade: Optional[str] = Query(None, description="Filter by trade type"),
    category: Optional[str] = Query(None, description="Filter by service category"),
    featured_only: bool = Query(False, description="Show only featured projects"),
    limit: int = Query(12, ge=1, le=50, description="Maximum number of projects to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    project_service: ProjectPortfolioService = Depends(get_project_portfolio_service)
):
    """
    Get featured projects for a contractor.
    
    Returns list of projects with images, testimonials, and project details.
    
    Args:
        business_id: The unique identifier of the business
        trade: Optional trade filter
        category: Optional category filter
        featured_only: Show only featured projects
        limit: Maximum number of projects to return
        offset: Pagination offset
        project_service: Injected project portfolio service
        
    Returns:
        List[FeaturedProject]: List of featured projects
        
    Raises:
        HTTPException: If business not found or retrieval fails
    """
    
    try:
        # Create search criteria
        search_criteria = ProjectSearchCriteria(
            trade=trade,
            category=category,
            featured_only=featured_only,
            limit=limit,
            offset=offset
        )
        
        # Get projects from service layer
        project_dtos = await project_service.get_featured_projects(business_id, search_criteria)
        
        # Convert DTOs to API response models
        projects = []
        for project_dto in project_dtos:
            project_data = FeaturedProject(
                id=project_dto.id,
                title=project_dto.title,
                description=project_dto.description or "",
                trade=project_dto.trade,
                service_category=project_dto.service_category,
                location=project_dto.location,
                completion_date=project_dto.completion_date,
                project_duration=project_dto.project_duration or "",
                project_value=float(project_dto.project_value) if project_dto.project_value else None,
                customer_name=project_dto.customer_name,
                customer_testimonial=project_dto.customer_testimonial,
                before_images=project_dto.before_images,
                after_images=project_dto.after_images,
                gallery_images=project_dto.gallery_images,
                video_url=project_dto.video_url,
                challenges_faced=project_dto.challenges_faced,
                solutions_provided=project_dto.solutions_provided,
                equipment_installed=project_dto.equipment_installed,
                warranty_info=project_dto.warranty_info,
                is_featured=project_dto.is_featured,
                seo_slug=project_dto.seo_slug,
                tags=project_dto.tags,
                display_order=project_dto.display_order
            )
            projects.append(project_data)
        
        return projects
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error for business {business_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving projects for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve projects")
    except Exception as e:
        logger.error(f"Unexpected error retrieving projects for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/featured-projects/{business_id}/{project_slug}", response_model=FeaturedProject)
async def get_project_details(
    business_id: str = Path(..., description="Business ID"),
    project_slug: str = Path(..., description="Project SEO slug"),
    project_service: ProjectPortfolioService = Depends(get_project_portfolio_service)
):
    """
    Get detailed information for a specific project.
    
    Returns complete project details including all images and testimonials.
    
    Args:
        business_id: The unique identifier of the business
        project_slug: Project SEO slug
        project_service: Injected project portfolio service
        
    Returns:
        FeaturedProject: Complete project details
        
    Raises:
        HTTPException: If business or project not found or retrieval fails
    """
    
    try:
        # Get project from service layer
        project_dto = await project_service.get_project_by_slug(business_id, project_slug)
        
        # Convert DTO to API response model
        return FeaturedProject(
            id=project_dto.id,
            title=project_dto.title,
            description=project_dto.description or "",
            trade=project_dto.trade,
            service_category=project_dto.service_category,
            location=project_dto.location,
            completion_date=project_dto.completion_date,
            project_duration=project_dto.project_duration or "",
            project_value=float(project_dto.project_value) if project_dto.project_value else None,
            customer_name=project_dto.customer_name,
            customer_testimonial=project_dto.customer_testimonial,
            before_images=project_dto.before_images,
            after_images=project_dto.after_images,
            gallery_images=project_dto.gallery_images,
            video_url=project_dto.video_url,
            challenges_faced=project_dto.challenges_faced,
            solutions_provided=project_dto.solutions_provided,
            equipment_installed=project_dto.equipment_installed,
            warranty_info=project_dto.warranty_info,
            is_featured=project_dto.is_featured,
            seo_slug=project_dto.seo_slug,
            tags=project_dto.tags,
            display_order=project_dto.display_order
        )
        
    except EntityNotFoundError as e:
        logger.warning(f"Project not found: {business_id}/{project_slug}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error for project {business_id}/{project_slug}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving project {business_id}/{project_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve project")
    except Exception as e:
        logger.error(f"Unexpected error retrieving project {business_id}/{project_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/project-categories/{business_id}", response_model=List[ProjectCategory])
async def get_project_categories(
    business_id: str = Path(..., description="Business ID"),
    project_service: ProjectPortfolioService = Depends(get_project_portfolio_service)
):
    """
    Get project categories for filtering and navigation.
    
    Returns list of project categories with counts.
    
    Args:
        business_id: The unique identifier of the business
        project_service: Injected project portfolio service
        
    Returns:
        List[ProjectCategory]: List of project categories
        
    Raises:
        HTTPException: If business not found or retrieval fails
    """
    
    try:
        # Get categories from service layer
        category_dtos = await project_service.get_project_categories(business_id)
        
        # Convert DTOs to API response models
        categories = []
        for category_dto in category_dtos:
            category_data = ProjectCategory(
                id=category_dto.id,
                name=category_dto.name,
                slug=category_dto.slug,
                description=category_dto.description,
                icon=category_dto.icon,
                project_count=category_dto.project_count,
                display_order=category_dto.display_order
            )
            categories.append(category_data)
        
        return categories
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error for business {business_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving categories for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")
    except Exception as e:
        logger.error(f"Unexpected error retrieving categories for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/project-tags/{business_id}")
async def get_project_tags(
    business_id: str = Path(..., description="Business ID"),
    project_service: ProjectPortfolioService = Depends(get_project_portfolio_service)
):
    """
    Get available project tags for filtering.
    
    Returns list of tags with usage counts.
    
    Args:
        business_id: The unique identifier of the business
        project_service: Injected project portfolio service
        
    Returns:
        List[Dict]: List of project tags
        
    Raises:
        HTTPException: If business not found or retrieval fails
    """
    
    try:
        # Get tags from service layer
        tag_dtos = await project_service.get_project_tags(business_id)
        
        # Convert DTOs to API response format
        tags = []
        for tag_dto in tag_dtos:
            tag_data = {
                "id": tag_dto.id,
                "name": tag_dto.name,
                "slug": tag_dto.slug,
                "color": tag_dto.color,
                "usage_count": tag_dto.usage_count
            }
            tags.append(tag_data)
        
        return tags
        
    except EntityNotFoundError as e:
        logger.warning(f"Business not found: {business_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error for business {business_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ApplicationError as e:
        logger.error(f"Application error retrieving tags for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tags")
    except Exception as e:
        logger.error(f"Unexpected error retrieving tags for business {business_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")