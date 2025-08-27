"""
Contractor Featured Projects API Routes

Public endpoints for retrieving featured projects and portfolio information.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List, Dict, Any
from datetime import date
import logging

from .schemas import FeaturedProject, ProjectCategory

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/featured-projects/{business_id}", response_model=List[FeaturedProject])
async def get_featured_projects(
    business_id: str = Path(..., description="Business ID"),
    trade: Optional[str] = Query(None, description="Filter by trade type"),
    category: Optional[str] = Query(None, description="Filter by service category"),
    featured_only: bool = Query(False, description="Show only featured projects"),
    limit: int = Query(12, ge=1, le=50, description="Maximum number of projects to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get featured projects for a contractor.
    
    Returns list of projects with images, testimonials, and project details.
    """
    
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Build query
        query = supabase.table("featured_projects").select(
            """
            id, title, description, trade, service_category, location,
            completion_date, project_duration, project_value, customer_name,
            customer_testimonial, before_images, after_images, gallery_images,
            video_url, challenges_faced, solutions_provided, equipment_installed,
            warranty_info, is_featured, seo_slug, tags, display_order
            """
        ).eq("business_id", business_id)
        
        # Apply filters
        if trade:
            query = query.eq("trade", trade)
        if category:
            query = query.eq("service_category", category)
        if featured_only:
            query = query.eq("is_featured", True)
        
        # Apply pagination and ordering
        query = query.order("display_order").order("completion_date", desc=True)
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        
        if not result.data:
            return []
        
        # Convert to response models
        projects = []
        for project in result.data:
            project_data = FeaturedProject(
                id=str(project["id"]),
                title=project["title"],
                description=project.get("description", ""),
                trade=project["trade"],
                service_category=project["service_category"],
                location=project["location"],
                completion_date=project["completion_date"],
                project_duration=project.get("project_duration", ""),
                project_value=float(project["project_value"]) if project.get("project_value") else None,
                customer_name=project.get("customer_name"),
                customer_testimonial=project.get("customer_testimonial"),
                before_images=project.get("before_images", []),
                after_images=project.get("after_images", []),
                gallery_images=project.get("gallery_images", []),
                video_url=project.get("video_url"),
                challenges_faced=project.get("challenges_faced", []),
                solutions_provided=project.get("solutions_provided", []),
                equipment_installed=project.get("equipment_installed", []),
                warranty_info=project.get("warranty_info"),
                is_featured=project.get("is_featured", False),
                seo_slug=project["seo_slug"],
                tags=project.get("tags", []),
                display_order=project.get("display_order", 0)
            )
            projects.append(project_data)
        
        return projects
        
    except Exception as e:
        logger.error(f"Error fetching featured projects for {business_id}: {str(e)}")
        return []


@router.get("/featured-projects/{business_id}/{project_slug}", response_model=FeaturedProject)
async def get_project_details(
    business_id: str = Path(..., description="Business ID"),
    project_slug: str = Path(..., description="Project SEO slug")
):
    """
    Get detailed information for a specific project.
    
    Returns complete project details including all images and testimonials.
    """
    
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Get project details
        result = supabase.table("featured_projects").select(
            """
            id, title, description, trade, service_category, location,
            completion_date, project_duration, project_value, customer_name,
            customer_testimonial, before_images, after_images, gallery_images,
            video_url, challenges_faced, solutions_provided, equipment_installed,
            warranty_info, is_featured, seo_slug, tags, display_order
            """
        ).eq("business_id", business_id).eq("seo_slug", project_slug).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = result.data[0]
        
        return FeaturedProject(
            id=str(project["id"]),
            title=project["title"],
            description=project.get("description", ""),
            trade=project["trade"],
            service_category=project["service_category"],
            location=project["location"],
            completion_date=project["completion_date"],
            project_duration=project.get("project_duration", ""),
            project_value=float(project["project_value"]) if project.get("project_value") else None,
            customer_name=project.get("customer_name"),
            customer_testimonial=project.get("customer_testimonial"),
            before_images=project.get("before_images", []),
            after_images=project.get("after_images", []),
            gallery_images=project.get("gallery_images", []),
            video_url=project.get("video_url"),
            challenges_faced=project.get("challenges_faced", []),
            solutions_provided=project.get("solutions_provided", []),
            equipment_installed=project.get("equipment_installed", []),
            warranty_info=project.get("warranty_info"),
            is_featured=project.get("is_featured", False),
            seo_slug=project["seo_slug"],
            tags=project.get("tags", []),
            display_order=project.get("display_order", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project details for {business_id}/{project_slug}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch project details")



@router.get("/project-categories/{business_id}", response_model=List[ProjectCategory])
async def get_project_categories(
    business_id: str = Path(..., description="Business ID")
):
    """
    Get project categories for filtering and navigation.
    
    Returns list of project categories with counts.
    """
    
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Get categories with project counts
        categories_result = supabase.table("project_categories").select(
            "id, name, slug, description, icon, display_order"
        ).eq("business_id", business_id).eq("is_active", True).order("display_order").execute()
        
        if not categories_result.data:
            return []
        
        categories = []
        for category in categories_result.data:
            # Count projects in this category
            count_result = supabase.table("featured_projects").select(
                "id", count="exact"
            ).eq("business_id", business_id).eq("service_category", category["name"]).execute()
            
            project_count = count_result.count or 0
            
            categories.append(ProjectCategory(
                id=str(category["id"]),
                name=category["name"],
                slug=category["slug"],
                description=category.get("description"),
                icon=category.get("icon"),
                project_count=project_count,
                display_order=category.get("display_order", 0)
            ))
        
        return categories
        
    except Exception as e:
        logger.error(f"Error fetching project categories for {business_id}: {str(e)}")
        return []


@router.get("/project-tags/{business_id}")
async def get_project_tags(
    business_id: str = Path(..., description="Business ID")
):
    """
    Get available project tags for filtering.
    
    Returns list of tags with usage counts.
    """
    
    try:
        from .....core.db import get_supabase_client
        supabase = get_supabase_client()
        
        # Get tags with usage counts
        result = supabase.table("project_tags").select(
            "id, name, slug, color, usage_count"
        ).eq("business_id", business_id).eq("is_active", True).order("usage_count", desc=True).execute()
        
        if not result.data:
            return []
        
        tags = []
        for tag in result.data:
            tags.append({
                "id": str(tag["id"]),
                "name": tag["name"],
                "slug": tag["slug"],
                "color": tag.get("color", "#3B82F6"),
                "usage_count": tag.get("usage_count", 0)
            })
        
        return tags
        
    except Exception as e:
        logger.error(f"Error fetching project tags for {business_id}: {str(e)}")
        return []
