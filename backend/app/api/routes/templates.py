"""
Templates API Routes

Unified template management endpoints for different document types (estimates, invoices, contracts, etc.)
"""

import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ..deps import get_current_user, get_business_context
from ..middleware.permissions import require_view_projects_dep, require_edit_projects_dep
from ..schemas.document_template_schemas import DocumentTemplateResponse, CreateDocumentTemplateRequest, UpdateDocumentTemplateRequest
from ...domain.entities.document_template import DocumentType
from ...application.use_cases.document_template.manage_document_templates_use_case import ManageDocumentTemplatesUseCase
from ...application.exceptions.application_exceptions import NotFoundError, PermissionDeniedError
from ...infrastructure.config.dependency_injection import get_manage_document_templates_use_case

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=List[DocumentTemplateResponse])
async def get_templates(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    document_type: Optional[str] = Query(None, description="Filter by document type (estimate, invoice, contract, etc.)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    use_case: ManageDocumentTemplatesUseCase = Depends(get_manage_document_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get all document templates for the business.
    
    Can be filtered by document type and active status.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 TemplatesAPI: Getting templates for business {business_id}")
    
    try:
        # Parse document type if provided
        doc_type = None
        if document_type:
            try:
                doc_type = DocumentType(document_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid document type: {document_type}. Valid types: {[dt.value for dt in DocumentType]}"
                )
        
        # Get templates
        templates = await use_case.get_business_templates(
            business_id=business_id,
            document_type=doc_type,
            is_active=is_active
        )
        
        logger.info(f"🔧 TemplatesAPI: Found {len(templates)} templates")
        
        # Convert to API response
        return [
            DocumentTemplateResponse(
                id=template.id,
                business_id=template.business_id,
                branding_id=template.branding_id,
                name=template.name,
                description=template.description,
                document_type=template.document_type,
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
            ) for template in templates
        ]
        
    except PermissionDeniedError as e:
        logger.error(f"❌ TemplatesAPI: Permission denied: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"❌ TemplatesAPI: Error getting templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/estimates", response_model=List[DocumentTemplateResponse])
async def get_estimate_templates(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    use_case: ManageDocumentTemplatesUseCase = Depends(get_manage_document_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get estimate templates for the business.
    
    Returns templates specifically designed for estimates.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 TemplatesAPI: Getting estimate templates for business {business_id}")
    
    try:
        templates = await use_case.get_business_templates(
            business_id=business_id,
            document_type=DocumentType.ESTIMATE,
            is_active=is_active
        )
        
        logger.info(f"🔧 TemplatesAPI: Found {len(templates)} estimate templates")
        
        return [
            DocumentTemplateResponse(
                id=template.id,
                business_id=template.business_id,
                branding_id=template.branding_id,
                name=template.name,
                description=template.description,
                document_type=template.document_type,
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
            ) for template in templates
        ]
        
    except Exception as e:
        logger.error(f"❌ TemplatesAPI: Error getting estimate templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/invoices", response_model=List[DocumentTemplateResponse])
async def get_invoice_templates(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    use_case: ManageDocumentTemplatesUseCase = Depends(get_manage_document_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get invoice templates for the business.
    
    Returns templates specifically designed for invoices.
    Requires 'view_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 TemplatesAPI: Getting invoice templates for business {business_id}")
    
    try:
        templates = await use_case.get_business_templates(
            business_id=business_id,
            document_type=DocumentType.INVOICE,
            is_active=is_active
        )
        
        logger.info(f"🔧 TemplatesAPI: Found {len(templates)} invoice templates")
        
        return [
            DocumentTemplateResponse(
                id=template.id,
                business_id=template.business_id,
                branding_id=template.branding_id,
                name=template.name,
                description=template.description,
                document_type=template.document_type,
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
            ) for template in templates
        ]
        
    except Exception as e:
        logger.error(f"❌ TemplatesAPI: Error getting invoice templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/", response_model=DocumentTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    request: CreateDocumentTemplateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageDocumentTemplatesUseCase = Depends(get_manage_document_templates_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Create a new document template.
    
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 TemplatesAPI: Creating template {request.name} for business {business_id}")
    
    try:
        # Parse document type
        try:
            doc_type = DocumentType(request.document_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type: {request.document_type}. Valid types: {[dt.value for dt in DocumentType]}"
            )
        
        # Create template
        template = await use_case.create_template(
            business_id=business_id,
            name=request.name,
            document_type=doc_type,
            branding_id=request.branding_id,
            description=request.description,
            created_by=current_user["sub"]
        )
        
        logger.info(f"🔧 TemplatesAPI: Created template {template.id}")
        
        return DocumentTemplateResponse(
            id=template.id,
            business_id=template.business_id,
            branding_id=template.branding_id,
            name=template.name,
            description=template.description,
            document_type=template.document_type,
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
        )
        
    except PermissionDeniedError as e:
        logger.error(f"❌ TemplatesAPI: Permission denied: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"❌ TemplatesAPI: Error creating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{template_id}", response_model=DocumentTemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageDocumentTemplatesUseCase = Depends(get_manage_document_templates_use_case),
    _: bool = Depends(require_view_projects_dep)
):
    """
    Get a specific template by ID.
    
    Requires 'view_projects' permission.
    """
    logger.info(f"🔧 TemplatesAPI: Getting template {template_id}")
    
    try:
        template = await use_case.get_template(template_id)
        
        # Check if template belongs to the user's business (or is a system template)
        if template.business_id and template.business_id != uuid.UUID(business_context["business_id"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        
        return DocumentTemplateResponse(
            id=template.id,
            business_id=template.business_id,
            branding_id=template.branding_id,
            name=template.name,
            description=template.description,
            document_type=template.document_type,
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
        )
        
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    except Exception as e:
        logger.error(f"❌ TemplatesAPI: Error getting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{template_id}", response_model=DocumentTemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    request: UpdateDocumentTemplateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageDocumentTemplatesUseCase = Depends(get_manage_document_templates_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Update a template.
    
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 TemplatesAPI: Updating template {template_id}")
    
    try:
        # First get the template to verify ownership
        template = await use_case.get_template(template_id)
        
        if template.business_id != business_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        
        # Build updates dict from request
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.description is not None:
            updates['description'] = request.description
        if request.is_active is not None:
            updates['is_active'] = request.is_active
        if request.branding_id is not None:
            updates['branding_id'] = request.branding_id
        
        # Apply regular updates first (if any)
        if updates:
            updated_template = await use_case.update_template(
                template_id=template_id,
                updates=updates,
                updated_by=current_user["sub"]
            )
        else:
            updated_template = template
        
        # Handle setting as default template (if requested)
        if request.is_default is not None and request.is_default:
            updated_template = await use_case.set_default_template(
                template_id=template_id,
                business_id=business_id,
                document_type=template.document_type,
                set_by=current_user["sub"]
            )
        
        logger.info(f"🔧 TemplatesAPI: Updated template {template_id}")
        
        return DocumentTemplateResponse(
            id=updated_template.id,
            business_id=updated_template.business_id,
            branding_id=updated_template.branding_id,
            name=updated_template.name,
            description=updated_template.description,
            document_type=updated_template.document_type,
            template_type=updated_template.template_type,
            is_active=updated_template.is_active,
            is_default=updated_template.is_default,
            is_system_template=updated_template.is_system_template,
            usage_count=updated_template.usage_count,
            last_used_date=updated_template.last_used_date,
            created_by=updated_template.created_by,
            created_date=updated_template.created_date,
            last_modified=updated_template.last_modified,
            tags=updated_template.tags,
            category=updated_template.category,
            version=updated_template.version
        )
        
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    except PermissionDeniedError as e:
        logger.error(f"❌ TemplatesAPI: Permission denied: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"❌ TemplatesAPI: Error updating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ManageDocumentTemplatesUseCase = Depends(get_manage_document_templates_use_case),
    _: bool = Depends(require_edit_projects_dep)
):
    """
    Delete a template.
    
    Cannot delete default templates.
    Requires 'edit_projects' permission.
    """
    business_id = uuid.UUID(business_context["business_id"])
    logger.info(f"🔧 TemplatesAPI: Deleting template {template_id}")
    
    try:
        # Verify ownership
        template = await use_case.get_template(template_id)
        
        if template.business_id != business_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        
        # Delete template
        success = await use_case.delete_template(template_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete template"
            )
        
        logger.info(f"🔧 TemplatesAPI: Deleted template {template_id}")
        
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    except PermissionDeniedError as e:
        logger.error(f"❌ TemplatesAPI: Permission denied: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"❌ TemplatesAPI: Error deleting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )