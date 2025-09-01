"""
Project Portfolio Data Transfer Objects

DTOs for project portfolio-related data transfer between application layers.
"""

from typing import Optional, List
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class FeaturedProjectDTO(BaseModel):
    """DTO for featured project information."""
    
    id: str = Field(..., description="Project ID")
    business_id: str = Field(..., description="Business ID")
    title: str = Field(..., description="Project title")
    description: Optional[str] = Field(None, description="Project description")
    trade: str = Field("", description="Trade type")
    service_category: str = Field("", description="Service category")
    location: str = Field("", description="Project location")
    completion_date: Optional[date] = Field(None, description="Project completion date")
    project_duration: Optional[str] = Field(None, description="Project duration")
    project_value: Optional[Decimal] = Field(None, description="Project value")
    
    # Customer information
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_testimonial: Optional[str] = Field(None, description="Customer testimonial")
    
    # Media
    before_images: List[str] = Field(default_factory=list, description="Before images URLs")
    after_images: List[str] = Field(default_factory=list, description="After images URLs")
    gallery_images: List[str] = Field(default_factory=list, description="Gallery images URLs")
    video_url: Optional[str] = Field(None, description="Project video URL")
    
    # Project details
    challenges_faced: List[str] = Field(default_factory=list, description="Challenges faced")
    solutions_provided: List[str] = Field(default_factory=list, description="Solutions provided")
    equipment_installed: List[str] = Field(default_factory=list, description="Equipment installed")
    warranty_info: Optional[str] = Field(None, description="Warranty information")
    
    # SEO and organization
    is_featured: bool = Field(False, description="Is featured project")
    seo_slug: str = Field(..., description="SEO slug")
    tags: List[str] = Field(default_factory=list, description="Project tags")
    display_order: int = Field(0, description="Display order")


class ProjectCategoryDTO(BaseModel):
    """DTO for project category information."""
    
    id: str = Field(..., description="Category ID")
    business_id: str = Field(..., description="Business ID")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="Category slug")
    description: Optional[str] = Field(None, description="Category description")
    icon: Optional[str] = Field(None, description="Category icon")
    project_count: int = Field(0, description="Number of projects in category")
    display_order: int = Field(0, description="Display order")
    is_active: bool = Field(True, description="Category is active")


class ProjectTagDTO(BaseModel):
    """DTO for project tag information."""
    
    id: str = Field(..., description="Tag ID")
    business_id: str = Field(..., description="Business ID")
    name: str = Field(..., description="Tag name")
    slug: str = Field(..., description="Tag slug")
    color: str = Field("#3B82F6", description="Tag color")
    usage_count: int = Field(0, description="Number of times tag is used")
    is_active: bool = Field(True, description="Tag is active")


class ProjectSearchCriteria(BaseModel):
    """DTO for project search criteria."""
    
    trade: Optional[str] = Field(None, description="Filter by trade type")
    category: Optional[str] = Field(None, description="Filter by service category")
    featured_only: bool = Field(False, description="Show only featured projects")
    tags: List[str] = Field(default_factory=list, description="Filter by tags")
    limit: int = Field(12, ge=1, le=50, description="Maximum number of projects")
    offset: int = Field(0, ge=0, description="Pagination offset")
