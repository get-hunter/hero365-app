"""
Templates API Routes

Global template management endpoints for different document types.
"""

import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ..deps import get_current_user, get_business_context
from ..middleware.permissions import require_view_projects_dep, require_edit_projects_dep
from ..schemas.estimate_schemas import EstimateTemplateResponse
from ...application.use_cases.estimate.get_estimate_templates_use_case import GetEstimateTemplatesUseCase
from ...application.dto.estimate_dto import EstimateTemplateListFilters
from ...application.exceptions.application_exceptions import NotFoundError, PermissionDeniedError
from ...infrastructure.config.dependency_injection import get_get_estimate_templates_use_case

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/invoices", response_model=List[EstimateTemplateResponse])
async def get_invoice_templates(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    is_active: bool = Query(True, description="Filter by active status"),
    use_case: GetEstimateTemplatesUseCase = Depends(get_get_estimate_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get invoice templates for the business.
    
    Returns estimate templates that are suitable for invoice creation.
    Since invoices and estimates share the same template system,
    this endpoint returns estimate templates filtered for invoice use.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 TemplatesAPI: Getting invoice templates for business {business_id}")
    
    try:
        # Create filters for template search
        filters = EstimateTemplateListFilters(
            business_id=business_id,
            template_type=template_type,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        
        # Get templates using the estimate templates use case
        # since invoices use the same template system as estimates
        templates_response = await use_case.execute(filters, current_user["sub"])
        
        logger.info(f"🔧 TemplatesAPI: Found {len(templates_response.templates)} invoice templates")
        
        # Convert DTOs to API response schemas
        return [
            EstimateTemplateResponse(
                id=template.id,
                business_id=template.business_id,
                name=template.name,
                description=template.description,
                template_type=template.template_type,
                is_active=template.is_active,
                is_default=template.is_default,
                is_system_template=template.is_system_template,
                usage_count=template.usage_count,
                last_used_date=template.last_used_date,
                created_by=template.created_by,
                created_date=template.created_date,
                last_modified=template.last_modified,
                tags=template.tags,
                category=template.category,
                version=template.version
            ) for template in templates_response.templates
        ]
        
    except PermissionDeniedError as e:
        logger.error(f"❌ TemplatesAPI: Permission denied: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"❌ TemplatesAPI: Error getting invoice templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/estimates", response_model=List[EstimateTemplateResponse])
async def get_estimate_templates(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    is_active: bool = Query(True, description="Filter by active status"),
    use_case: GetEstimateTemplatesUseCase = Depends(get_get_estimate_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get estimate templates for the business.
    
    Returns estimate templates available for estimate creation.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 TemplatesAPI: Getting estimate templates for business {business_id}")
    
    try:
        # Create filters for template search
        filters = EstimateTemplateListFilters(
            business_id=business_id,
            template_type=template_type,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        
        templates_response = await use_case.execute(filters, current_user["sub"])
        
        logger.info(f"🔧 TemplatesAPI: Found {len(templates_response.templates)} estimate templates")
        
        # Convert DTOs to API response schemas
        return [
            EstimateTemplateResponse(
                id=template.id,
                business_id=template.business_id,
                name=template.name,
                description=template.description,
                template_type=template.template_type,
                is_active=template.is_active,
                is_default=template.is_default,
                is_system_template=template.is_system_template,
                usage_count=template.usage_count,
                last_used_date=template.last_used_date,
                created_by=template.created_by,
                created_date=template.created_date,
                last_modified=template.last_modified,
                tags=template.tags,
                category=template.category,
                version=template.version
            ) for template in templates_response.templates
        ]
        
    except PermissionDeniedError as e:
        logger.error(f"❌ TemplatesAPI: Permission denied: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"❌ TemplatesAPI: Error getting estimate templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        ) 