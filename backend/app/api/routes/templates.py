"""
Templates API Routes

Unified template management endpoints using the flexible Template system.
Supports all document types, websites, and more with JSONB configuration.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field

from ..deps import get_current_user, get_business_context
from ..middleware.permissions import require_view_projects_dep, require_edit_projects_dep
from ...domain.entities.template import TemplateType, TemplateCategory
from ...application.use_cases.template.manage_templates_use_case import ManageTemplatesUseCase
from ...application.exceptions.application_exceptions import NotFoundError, PermissionDeniedError
from ...infrastructure.config.dependency_injection import get_manage_templates_use_case

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["templates"])


# Response Models
class TemplateResponse(BaseModel):
    """Template response model."""
    id: uuid.UUID
    business_id: Optional[uuid.UUID]
    branding_id: Optional[uuid.UUID]
    template_type: str
    category: Optional[str]
    name: str
    description: Optional[str]
    version: int
    is_active: bool
    is_default: bool
    is_system: bool
    config: dict
    usage_count: int
    last_used_at: Optional[str]
    tags: List[str]
    metadata: dict
    created_by: Optional[str]
    created_at: str
    updated_at: str
    updated_by: Optional[str]


class MobileTemplateResponse(BaseModel):
    """Enhanced template response for mobile app with visual parameters."""
    id: str
    name: str
    template_type: str
    category: Optional[str]
    layout_style: str
    description: Optional[str]
    is_active: bool
    is_default: bool
    is_system: bool
    colors: Dict[str, str]
    header_style: Dict[str, Any]
    layout_elements: Dict[str, Any]
    visual_theme: Dict[str, Any]
    typography: Dict[str, Any]
    created_at: str
    updated_at: str


class CreateTemplateRequest(BaseModel):
    """Create template request model."""
    name: str = Field(..., min_length=1, max_length=200)
    template_type: str = Field(..., description="Template type (invoice, estimate, website, etc.)")
    category: Optional[str] = Field(None, description="Template category")
    description: Optional[str] = Field(None)
    config: dict = Field(default_factory=dict, description="Template configuration (JSONB)")
    tags: List[str] = Field(default_factory=list)
    branding_id: Optional[uuid.UUID] = Field(None)


class UpdateTemplateRequest(BaseModel):
    """Update template request model."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    is_default: Optional[bool] = Field(None)
    config: Optional[dict] = Field(None, description="Template configuration updates")
    tags: Optional[List[str]] = Field(None)


class SetDefaultTemplateRequest(BaseModel):
    """Set default template request model."""
    template_type: str = Field(..., description="Template type to set as default")


@router.get("", response_model=List[TemplateResponse])
async def get_templates(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_system: Optional[bool] = Query(None, description="Show only system templates"),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get all templates for the business.
    
    Returns both business-specific and system templates.
    Can be filtered by template type, category, and status.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"Getting templates for business {business_id}")
    
    try:
        # Parse template type if provided
        t_type = None
        if template_type:
            try:
                t_type = TemplateType(template_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid template type: {template_type}"
                )
        
        # Parse category if provided
        t_category = None
        if category:
            try:
                t_category = TemplateCategory(category.lower())
            except ValueError:
                # Allow custom categories
                pass
        
        # Get templates based on filters
        if is_system:
            templates = await use_case.get_system_templates(
                template_type=t_type,
                category=t_category,
                is_active=is_active
            )
        else:
            templates = await use_case.get_business_templates(
                business_id=business_id,
                template_type=t_type,
                is_active=is_active
            )
        
        logger.info(f"Found {len(templates)} templates")
        
        # Convert to API response
        response_templates = [
            TemplateResponse(
                id=template.id,
                business_id=template.business_id,
                branding_id=template.branding_id,
                template_type=template.template_type,
                category=template.category,
                name=template.name,
                description=template.description,
                version=template.version,
                is_active=template.is_active,
                is_default=template.is_default,
                is_system=template.is_system,
                config=template.config,
                usage_count=template.usage_count,
                last_used_at=template.last_used_at.isoformat() if template.last_used_at else None,
                tags=template.tags,
                metadata=template.metadata,
                created_by=template.created_by,
                created_at=template.created_at.isoformat(),
                updated_at=template.updated_at.isoformat(),
                updated_by=template.updated_by
            ) for template in templates
        ]
        
        return response_templates
        
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/invoices", response_model=List[TemplateResponse])
async def get_invoice_templates(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_system: Optional[bool] = Query(None, description="Show only system templates"),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """Get all invoice templates."""
    return await _get_templates_by_type("invoice", business_context, current_user, is_active, is_system, use_case)


@router.get("/estimates", response_model=List[TemplateResponse])
async def get_estimate_templates(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_system: Optional[bool] = Query(None, description="Show only system templates"),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """Get all estimate templates."""
    return await _get_templates_by_type("estimate", business_context, current_user, is_active, is_system, use_case)


@router.get("/contracts", response_model=List[TemplateResponse])
async def get_contract_templates(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_system: Optional[bool] = Query(None, description="Show only system templates"),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """Get all contract templates."""
    return await _get_templates_by_type("contract", business_context, current_user, is_active, is_system, use_case)


async def _get_templates_by_type(
    template_type: str, 
    business_context: dict, 
    current_user: dict, 
    is_active: Optional[bool], 
    is_system: Optional[bool], 
    use_case: ManageTemplatesUseCase
) -> List[TemplateResponse]:
    """Helper function to get templates by type."""
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"Getting {template_type} templates for business {business_id}")
    
    try:
        # Parse template type
        try:
            t_type = TemplateType(template_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid template type: {template_type}"
            )
        
        # Get templates based on filters
        if is_system:
            templates = await use_case.get_system_templates(
                template_type=t_type,
                is_active=is_active
            )
        else:
            templates = await use_case.get_business_templates(
                business_id=business_id,
                template_type=t_type,
                is_active=is_active
            )
        
        logger.info(f"Found {len(templates)} {template_type} templates")
        
        # Convert to API response
        return [
            TemplateResponse(
                id=template.id,
                business_id=template.business_id,
                branding_id=template.branding_id,
                template_type=template.template_type,
                category=template.category,
                name=template.name,
                description=template.description,
                version=template.version,
                is_active=template.is_active,
                is_default=template.is_default,
                is_system=template.is_system,
                config=template.config,
                usage_count=template.usage_count,
                last_used_at=template.last_used_at.isoformat() if template.last_used_at else None,
                tags=template.tags,
                metadata=template.metadata,
                created_by=template.created_by,
                created_at=template.created_at.isoformat(),
                updated_at=template.updated_at.isoformat(),
                updated_by=template.updated_by
            ) for template in templates
        ]
        
    except Exception as e:
        logger.error(f"Error getting {template_type} templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/type/{template_type}", response_model=List[TemplateResponse])
async def get_templates_by_type(
    template_type: str,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_system: Optional[bool] = Query(None, description="Show only system templates"),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get all templates for a specific type (e.g., /templates/type/invoice).
    
    This is a convenience endpoint for mobile apps.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Parse template type
        try:
            t_type = TemplateType(template_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid template type: {template_type}"
            )
        
        # Get templates based on filters
        if is_system:
            templates = await use_case.get_system_templates(
                template_type=t_type,
                is_active=is_active
            )
        else:
            templates = await use_case.get_business_templates(
                business_id=business_id,
                template_type=t_type,
                is_active=is_active
            )
        
        logger.info(f"Found {len(templates)} {template_type} templates")
        
        # Convert to API response
        return [
            TemplateResponse(
                id=template.id,
                business_id=template.business_id,
                branding_id=template.branding_id,
                template_type=template.template_type,
                category=template.category,
                name=template.name,
                description=template.description,
                version=template.version,
                is_active=template.is_active,
                is_default=template.is_default,
                is_system=template.is_system,
                config=template.config,
                usage_count=template.usage_count,
                last_used_at=template.last_used_at.isoformat() if template.last_used_at else None,
                tags=template.tags,
                metadata=template.metadata,
                created_by=template.created_by,
                created_at=template.created_at.isoformat(),
                updated_at=template.updated_at.isoformat(),
                updated_by=template.updated_by
            ) for template in templates
        ]
        
    except Exception as e:
        logger.error(f"Error getting {template_type} templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/default/{template_type}", response_model=Optional[TemplateResponse])
async def get_default_template(
    template_type: str,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get the default template for a specific type.
    
    Returns the business default or falls back to system default.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Parse template type
        try:
            t_type = TemplateType(template_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid template type: {template_type}"
            )
        
        template = await use_case.get_default_template(
            business_id=business_id,
            template_type=t_type
        )
        
        if not template:
            return None
        
        return TemplateResponse(
            id=template.id,
            business_id=template.business_id,
            branding_id=template.branding_id,
            template_type=template.template_type,
            category=template.category,
            name=template.name,
            description=template.description,
            version=template.version,
            is_active=template.is_active,
            is_default=template.is_default,
            is_system=template.is_system,
            config=template.config,
            usage_count=template.usage_count,
            last_used_at=template.last_used_at.isoformat() if template.last_used_at else None,
            tags=template.tags,
            metadata=template.metadata,
            created_by=template.created_by,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat(),
            updated_by=template.updated_by
        )
        
    except Exception as e:
        logger.error(f"Error getting default template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/validate", response_model=Dict[str, Any])
async def validate_template_access(
    template_ids: List[uuid.UUID] = Body(..., description="List of template IDs to validate"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Validate if templates exist and are accessible for the current business.
    
    Helps prevent template validation errors by checking accessibility upfront.
    Returns validation status for each template ID.
    """
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        validation_results = {}
        
        for template_id in template_ids:
            try:
                template = await use_case.get_template(template_id)
                
                # Check if template is accessible (system or belongs to business)
                if template.is_system or template.business_id == business_id:
                    validation_results[str(template_id)] = {
                        "valid": True,
                        "accessible": True,
                        "name": template.name,
                        "template_type": template.template_type,
                        "is_system": template.is_system,
                        "is_active": template.is_active
                    }
                else:
                    validation_results[str(template_id)] = {
                        "valid": True,
                        "accessible": False,
                        "error": "Template belongs to a different business",
                        "name": template.name,
                        "template_type": template.template_type
                    }
            except Exception:
                validation_results[str(template_id)] = {
                    "valid": False,
                    "accessible": False,
                    "error": "Template not found"
                }
        
        return {
            "validation_results": validation_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error validating template access: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """Get a specific template by ID."""
    try:
        template = await use_case.get_template(template_id)
        
        # Check access permissions
        business_id = uuid.UUID(business_context["business_id"])
        if template.business_id and template.business_id != business_id and not template.is_system:
            raise PermissionDeniedError("Cannot access template from another business")
        
        return TemplateResponse(
            id=template.id,
            business_id=template.business_id,
            branding_id=template.branding_id,
            template_type=template.template_type,
            category=template.category,
            name=template.name,
            description=template.description,
            version=template.version,
            is_active=template.is_active,
            is_default=template.is_default,
            is_system=template.is_system,
            config=template.config,
            usage_count=template.usage_count,
            last_used_at=template.last_used_at.isoformat() if template.last_used_at else None,
            tags=template.tags,
            metadata=template.metadata,
            created_by=template.created_by,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat(),
            updated_by=template.updated_by
        )
        
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/mobile/{template_type}", response_model=List[MobileTemplateResponse])
async def get_mobile_templates(
    template_type: str,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    is_system: Optional[bool] = Query(None, description="Show only system templates"),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get templates optimized for mobile app with enhanced visual parameters.
    
    This endpoint returns templates with all visual configuration data needed
    for mobile app thumbnail generation and template differentiation.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"Getting mobile templates for {template_type} - business {business_id}")
    
    try:
        # Parse template type
        try:
            t_type = TemplateType(template_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid template type: {template_type}"
            )
        
        # Get templates based on filters
        if is_system:
            templates = await use_case.get_system_templates(
                template_type=t_type,
                is_active=is_active
            )
        else:
            templates = await use_case.get_business_templates(
                business_id=business_id,
                template_type=t_type,
                is_active=is_active
            )
        
        logger.info(f"Found {len(templates)} {template_type} templates for mobile")
        
        # Convert to mobile-optimized response
        mobile_templates = []
        for template in templates:
            mobile_data = template.get_mobile_template_data()
            mobile_templates.append(MobileTemplateResponse(**mobile_data))
        
        return mobile_templates
        
    except NotFoundError as e:
        logger.warning(f"Templates not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionDeniedError as e:
        logger.warning(f"Permission denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting mobile templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    request: CreateTemplateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """Create a new template."""
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Parse template type
        try:
            t_type = TemplateType(request.template_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid template type: {request.template_type}"
            )
        
        # Parse category if provided
        t_category = None
        if request.category:
            try:
                t_category = TemplateCategory(request.category.lower())
            except ValueError:
                # Allow custom categories
                t_category = None
        
        template = await use_case.create_template(
            business_id=business_id,
            name=request.name,
            template_type=t_type,
            branding_id=request.branding_id,
            description=request.description,
            category=t_category,
            config=request.config,
            created_by=current_user["sub"],
            tags=request.tags
        )
        
        logger.info(f"Created template {template.id}")
        
        return TemplateResponse(
            id=template.id,
            business_id=template.business_id,
            branding_id=template.branding_id,
            template_type=template.template_type,
            category=template.category,
            name=template.name,
            description=template.description,
            version=template.version,
            is_active=template.is_active,
            is_default=template.is_default,
            is_system=template.is_system,
            config=template.config,
            usage_count=template.usage_count,
            last_used_at=template.last_used_at.isoformat() if template.last_used_at else None,
            tags=template.tags,
            metadata=template.metadata,
            created_by=template.created_by,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat(),
            updated_by=template.updated_by
        )
        
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    request: UpdateTemplateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """Update an existing template."""
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Get existing template to check permissions
        template = await use_case.get_template(template_id)
        
        # Check permissions
        if template.is_system:
            raise PermissionDeniedError("Cannot modify system templates")
        if template.business_id != business_id:
            raise PermissionDeniedError("Cannot modify template from another business")
        
        # Build updates dict
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.description is not None:
            updates['description'] = request.description
        if request.category is not None:
            updates['category'] = request.category
        if request.is_active is not None:
            updates['is_active'] = request.is_active
        if request.config is not None:
            updates['config'] = request.config
        if request.tags is not None:
            updates['tags'] = request.tags
        
        # Update template
        if updates:
            template = await use_case.update_template(
                template_id=template_id,
                updates=updates,
                updated_by=current_user["sub"]
            )
        
        # Handle setting as default
        if request.is_default is True:
            template = await use_case.set_default_template(
                template_id=template_id,
                business_id=business_id,
                template_type=template.template_type,
                set_by=current_user["sub"]
            )
        
        logger.info(f"Updated template {template_id}")
        
        return TemplateResponse(
            id=template.id,
            business_id=template.business_id,
            branding_id=template.branding_id,
            template_type=template.template_type,
            category=template.category,
            name=template.name,
            description=template.description,
            version=template.version,
            is_active=template.is_active,
            is_default=template.is_default,
            is_system=template.is_system,
            config=template.config,
            usage_count=template.usage_count,
            last_used_at=template.last_used_at.isoformat() if template.last_used_at else None,
            tags=template.tags,
            metadata=template.metadata,
            created_by=template.created_by,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat(),
            updated_by=template.updated_by
        )
        
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{template_id}/set-default", response_model=TemplateResponse)
async def set_default_template(
    template_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """Set a template as the default for its type."""
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        # Get template to determine its type
        template = await use_case.get_template(template_id)
        
        # Set as default
        template = await use_case.set_default_template(
            template_id=template_id,
            business_id=business_id,
            template_type=template.template_type,
            set_by=current_user["sub"]
        )
        
        logger.info(f"Set template {template_id} as default for type {template.template_type}")
        
        return TemplateResponse(
            id=template.id,
            business_id=template.business_id,
            branding_id=template.branding_id,
            template_type=template.template_type,
            category=template.category,
            name=template.name,
            description=template.description,
            version=template.version,
            is_active=template.is_active,
            is_default=template.is_default,
            is_system=template.is_system,
            config=template.config,
            usage_count=template.usage_count,
            last_used_at=template.last_used_at.isoformat() if template.last_used_at else None,
            tags=template.tags,
            metadata=template.metadata,
            created_by=template.created_by,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat(),
            updated_by=template.updated_by
        )
        
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    except Exception as e:
        logger.error(f"Error setting default template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{template_id}/clone", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def clone_template(
    template_id: uuid.UUID,
    new_name: str = Body(..., description="Name for the cloned template"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """Clone an existing template."""
    business_id = uuid.UUID(business_context["business_id"])
    
    try:
        template = await use_case.clone_template(
            template_id=template_id,
            new_name=new_name,
            business_id=business_id,
            cloned_by=current_user["sub"]
        )
        
        logger.info(f"Cloned template {template_id} to {template.id}")
        
        return TemplateResponse(
            id=template.id,
            business_id=template.business_id,
            branding_id=template.branding_id,
            template_type=template.template_type,
            category=template.category,
            name=template.name,
            description=template.description,
            version=template.version,
            is_active=template.is_active,
            is_default=template.is_default,
            is_system=template.is_system,
            config=template.config,
            usage_count=template.usage_count,
            last_used_at=template.last_used_at.isoformat() if template.last_used_at else None,
            tags=template.tags,
            metadata=template.metadata,
            created_by=template.created_by,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat(),
            updated_by=template.updated_by
        )
        
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    except Exception as e:
        logger.error(f"Error cloning template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageTemplatesUseCase = Depends(get_manage_templates_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """Delete a template."""
    try:
        await use_case.delete_template(template_id)
        logger.info(f"Deleted template {template_id}")
        
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
