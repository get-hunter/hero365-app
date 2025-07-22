"""
Project API Routes

FastAPI routes for project management operations.
Handles all project-related HTTP endpoints with proper validation and error handling.
"""

import uuid
from typing import List, Optional
from datetime import datetime, date
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..deps import get_current_user, get_business_context
from ..schemas.project_schemas import (
    ProjectCreateRequest, ProjectUpdateRequest, ProjectSearchRequest,
    ProjectAssignmentRequest, ProjectTemplateCreateRequest, ProjectTemplateUpdateRequest,
    ProjectCreateFromTemplateRequest, ProjectResponse, ProjectListResponse,
    ProjectStatisticsResponse, ProjectBudgetSummaryResponse, ProjectProgressReportResponse,
    ProjectTemplateResponse, ProjectListPaginatedResponse, ProjectActionResponse,
    ProjectErrorResponse, ProjectJobAssignmentResponse, ProjectJobAssignmentRequest
)
from ...application.use_cases.project.create_project_use_case import CreateProjectUseCase
from ...application.use_cases.project.get_project_use_case import GetProjectUseCase
from ...application.use_cases.project.update_project_use_case import UpdateProjectUseCase
from ...application.use_cases.project.delete_project_use_case import DeleteProjectUseCase
from ...application.use_cases.project.project_search_use_case import ProjectSearchUseCase
from ...application.use_cases.project.project_analytics_use_case import ProjectAnalyticsUseCase
from ...application.use_cases.project.project_assignment_use_case import ProjectAssignmentUseCase
from ...application.use_cases.project.project_template_use_case import ProjectTemplateUseCase
from ...application.dto.project_dto import (
    ProjectCreateDTO, ProjectUpdateDTO, ProjectSearchDTO, ProjectAssignmentDTO,
    ProjectTemplateCreateDTO, ProjectTemplateUpdateDTO, ProjectCreateFromTemplateDTO,
    ContactAddressDTO
)
from ...application.exceptions.application_exceptions import (
    ValidationError, NotFoundError, PermissionDeniedError, BusinessRuleViolationError
)
from ...infrastructure.config.dependency_injection import (
    get_create_project_use_case, get_get_project_use_case, get_update_project_use_case,
    get_delete_project_use_case, get_project_search_use_case, get_project_analytics_use_case,
    get_project_assignment_use_case, get_project_template_use_case
)
from ...domain.entities.project_enums.enums import ProjectType, ProjectStatus, ProjectPriority


router = APIRouter(prefix="/projects", tags=["Projects"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Create a new project with the provided details. Project number will be auto-generated if not provided."
)
async def create_project(
    project_data: ProjectCreateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: CreateProjectUseCase = Depends(get_create_project_use_case)
) -> ProjectResponse:
    """Create a new project."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        # Convert address if provided
        address_dto = None
        if project_data.address:
            logger.info(f"🔧 ProjectAPI: Converting address: {project_data.address}")
            address_dto = ContactAddressDTO(
                street_address=project_data.address.street_address,
                city=project_data.address.city,
                state=project_data.address.state,
                postal_code=project_data.address.postal_code,
                country=project_data.address.country,
                latitude=project_data.address.latitude,
                longitude=project_data.address.longitude,
                access_notes=project_data.address.access_notes,
                place_id=project_data.address.place_id,
                formatted_address=project_data.address.formatted_address,
                address_type=project_data.address.address_type
            )
        
        # Convert request to DTO
        create_dto = ProjectCreateDTO(
            business_id=business_id,
            project_number=project_data.project_number,
            name=project_data.name,
            description=project_data.description,
            project_type=project_data.project_type,
            status=project_data.status,
            priority=project_data.priority,
            contact_id=project_data.contact_id,
            client_name=project_data.client_name,
            client_email=project_data.client_email,
            client_phone=project_data.client_phone,
            address=address_dto,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            estimated_hours=project_data.estimated_hours,
            actual_hours=project_data.actual_hours,
            budget_amount=project_data.budget_amount,
            actual_cost=project_data.actual_cost,
            team_members=project_data.team_members,
            tags=project_data.tags,
            notes=project_data.notes
        )
        
        result = await use_case.execute(business_id, create_dto, user_id)
        
        # Convert DTO to API response schema
        # Convert ContactAddressDTO to dict if present
        address_dict = None
        if result.client_address:
            address_dict = {
                "street_address": result.client_address.street_address,
                "city": result.client_address.city,
                "state": result.client_address.state,
                "postal_code": result.client_address.postal_code,
                "country": result.client_address.country,
                "latitude": result.client_address.latitude,
                "longitude": result.client_address.longitude,
                "access_notes": result.client_address.access_notes,
                "place_id": result.client_address.place_id,
                "formatted_address": result.client_address.formatted_address,
                "address_type": result.client_address.address_type
            }
        
        return ProjectResponse(
            id=result.id,
            business_id=result.business_id,
            project_number=result.project_number,
            name=result.name,
            description=result.description,
            created_by=result.created_by,
            client_id=result.client_id,
            client_name=result.client_name,
            address=address_dict,
            project_type=result.project_type,
            status=result.status,
            priority=result.priority,
            start_date=result.start_date,
            end_date=result.end_date,
            estimated_budget=result.estimated_budget,
            actual_cost=result.actual_cost,
            manager=result.manager,
            manager_id=result.manager_id,
            team_members=result.team_members,
            tags=result.tags,
            notes=result.notes,
            created_date=result.created_date,
            last_modified=result.last_modified,
            is_overdue=result.is_overdue,
            is_over_budget=result.is_over_budget,
            budget_variance=result.budget_variance,
            budget_variance_percentage=result.budget_variance_percentage,
            duration_days=result.duration_days,
            status_display=result.status_display,
            priority_display=result.priority_display,
            type_display=result.type_display
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
    description="Retrieve a specific project by its ID."
)
async def get_project(
    project_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: GetProjectUseCase = Depends(get_get_project_use_case)
) -> ProjectResponse:
    """Get a project by ID."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        result = await use_case.execute(project_id, business_id, user_id)
        
        # Convert DTO to API response schema
        # Convert ContactAddressDTO to dict if present
        address_dict = None
        if result.client_address:
            address_dict = {
                "street_address": result.client_address.street_address,
                "city": result.client_address.city,
                "state": result.client_address.state,
                "postal_code": result.client_address.postal_code,
                "country": result.client_address.country,
                "latitude": result.client_address.latitude,
                "longitude": result.client_address.longitude,
                "access_notes": result.client_address.access_notes,
                "place_id": result.client_address.place_id,
                "formatted_address": result.client_address.formatted_address,
                "address_type": result.client_address.address_type
            }
        
        return ProjectResponse(
            id=result.id,
            business_id=result.business_id,
            project_number=result.project_number,
            name=result.name,
            description=result.description,
            created_by=result.created_by,
            client_id=result.client_id,
            client_name=result.client_name,
            address=address_dict,
            project_type=result.project_type,
            status=result.status,
            priority=result.priority,
            start_date=result.start_date,
            end_date=result.end_date,
            estimated_budget=result.estimated_budget,
            actual_cost=result.actual_cost,
            manager=result.manager,
            manager_id=result.manager_id,
            team_members=result.team_members,
            tags=result.tags,
            notes=result.notes,
            created_date=result.created_date,
            last_modified=result.last_modified,
            is_overdue=result.is_overdue,
            is_over_budget=result.is_over_budget,
            budget_variance=result.budget_variance,
            budget_variance_percentage=result.budget_variance_percentage,
            duration_days=result.duration_days,
            status_display=result.status_display,
            priority_display=result.priority_display,
            type_display=result.type_display
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Update an existing project with the provided details."
)
async def update_project(
    project_id: uuid.UUID,
    project_data: ProjectUpdateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: UpdateProjectUseCase = Depends(get_update_project_use_case)
) -> ProjectResponse:
    """Update an existing project."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        # Convert address if provided
        address_dto = None
        if project_data.address:
            logger.info(f"🔧 ProjectAPI: Converting address: {project_data.address}")
            address_dto = ContactAddressDTO(
                street_address=project_data.address.street_address,
                city=project_data.address.city,
                state=project_data.address.state,
                postal_code=project_data.address.postal_code,
                country=project_data.address.country,
                latitude=project_data.address.latitude,
                longitude=project_data.address.longitude,
                access_notes=project_data.address.access_notes,
                place_id=project_data.address.place_id,
                formatted_address=project_data.address.formatted_address,
                address_type=project_data.address.address_type
            )
        
        # Convert request to DTO
        update_dto = ProjectUpdateDTO(
            project_id=project_id,
            name=project_data.name,
            description=project_data.description,
            project_type=project_data.project_type,
            status=project_data.status,
            priority=project_data.priority,
            contact_id=project_data.contact_id,
            client_name=project_data.client_name,
            client_email=project_data.client_email,
            client_phone=project_data.client_phone,
            address=address_dto,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            estimated_hours=project_data.estimated_hours,
            actual_hours=project_data.actual_hours,
            budget_amount=project_data.budget_amount,
            actual_cost=project_data.actual_cost,
            team_members=project_data.team_members,
            tags=project_data.tags,
            notes=project_data.notes
        )
        
        result = await use_case.execute(business_id, update_dto, user_id)
        
        # Convert DTO to API response schema
        # Convert ContactAddressDTO to dict if present
        address_dict = None
        if result.client_address:
            address_dict = {
                "street_address": result.client_address.street_address,
                "city": result.client_address.city,
                "state": result.client_address.state,
                "postal_code": result.client_address.postal_code,
                "country": result.client_address.country,
                "latitude": result.client_address.latitude,
                "longitude": result.client_address.longitude,
                "access_notes": result.client_address.access_notes,
                "place_id": result.client_address.place_id,
                "formatted_address": result.client_address.formatted_address,
                "address_type": result.client_address.address_type
            }
        
        return ProjectResponse(
            id=result.id,
            business_id=result.business_id,
            project_number=result.project_number,
            name=result.name,
            description=result.description,
            created_by=result.created_by,
            client_id=result.client_id,
            client_name=result.client_name,
            address=address_dict,
            project_type=result.project_type,
            status=result.status,
            priority=result.priority,
            start_date=result.start_date,
            end_date=result.end_date,
            estimated_budget=result.estimated_budget,
            actual_cost=result.actual_cost,
            manager=result.manager,
            manager_id=result.manager_id,
            team_members=result.team_members,
            tags=result.tags,
            notes=result.notes,
            created_date=result.created_date,
            last_modified=result.last_modified,
            is_overdue=result.is_overdue,
            is_over_budget=result.is_over_budget,
            budget_variance=result.budget_variance,
            budget_variance_percentage=result.budget_variance_percentage,
            duration_days=result.duration_days,
            status_display=result.status_display,
            priority_display=result.priority_display,
            type_display=result.type_display
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/{project_id}",
    response_model=ProjectActionResponse,
    summary="Delete project",
    description="Delete a project by its ID."
)
async def delete_project(
    project_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: DeleteProjectUseCase = Depends(get_delete_project_use_case)
) -> ProjectActionResponse:
    """Delete a project."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        success = await use_case.execute(project_id, business_id, user_id)
        
        return ProjectActionResponse(
            success=success,
            message="Project deleted successfully" if success else "Failed to delete project"
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except BusinessRuleViolationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "",
    response_model=ProjectListPaginatedResponse,
    summary="List projects",
    description="Get a paginated list of projects for the business."
)
async def list_projects(
    skip: int = Query(0, ge=0, description="Number of projects to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of projects to return"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ProjectSearchUseCase = Depends(get_project_search_use_case)
) -> ProjectListPaginatedResponse:
    """List projects for a business."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        projects = await use_case.list_projects(business_id, user_id, skip, limit)
        
        return ProjectListPaginatedResponse(
            projects=projects,
            pagination={
                "total": len(projects),
                "skip": skip,
                "limit": limit,
                "has_next": len(projects) == limit,
                "has_previous": skip > 0
            }
        )
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/search",
    response_model=ProjectListPaginatedResponse,
    summary="Search projects",
    description="Search projects with various criteria and filters."
)
async def search_projects(
    search_request: ProjectSearchRequest,
    skip: int = Query(0, ge=0, description="Number of projects to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of projects to return"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ProjectSearchUseCase = Depends(get_project_search_use_case)
) -> ProjectListPaginatedResponse:
    """Search projects with criteria."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        # Convert request to DTO
        search_dto = ProjectSearchDTO(
            search=search_request.search,
            status=search_request.status,
            project_type=search_request.project_type,
            priority=search_request.priority,
            start_date_from=search_request.start_date_from,
            start_date_to=search_request.start_date_to,
            end_date_from=search_request.end_date_from,
            end_date_to=search_request.end_date_to,
            tags=search_request.tags
        )
        
        projects = await use_case.search_projects(business_id, search_dto, user_id, skip, limit)
        
        return ProjectListPaginatedResponse(
            projects=projects,
            pagination={
                "total": len(projects),
                "skip": skip,
                "limit": limit,
                "has_next": len(projects) == limit,
                "has_previous": skip > 0
            }
        )
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching projects: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/status/{status}",
    response_model=List[ProjectListResponse],
    summary="Get projects by status",
    description="Get all projects with a specific status."
)
async def get_projects_by_status(
    status: ProjectStatus,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ProjectSearchUseCase = Depends(get_project_search_use_case)
) -> List[ProjectListResponse]:
    """Get projects by status."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        projects = await use_case.get_by_status(business_id, status, user_id, skip, limit)
        return projects
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting projects by status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/analytics/statistics",
    response_model=ProjectStatisticsResponse,
    summary="Get project statistics",
    description="Get comprehensive project statistics for the business."
)
async def get_project_statistics(
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ProjectAnalyticsUseCase = Depends(get_project_analytics_use_case)
) -> ProjectStatisticsResponse:
    """Get project statistics."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        stats = await use_case.get_project_statistics(business_id, user_id)
        return stats
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting project statistics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/analytics/budget-summary",
    response_model=ProjectBudgetSummaryResponse,
    summary="Get budget summary",
    description="Get budget summary for projects within a date range."
)
async def get_budget_summary(
    start_date: date = Query(description="Start date for budget summary"),
    end_date: date = Query(description="End date for budget summary"),
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ProjectAnalyticsUseCase = Depends(get_project_analytics_use_case)
) -> ProjectBudgetSummaryResponse:
    """Get budget summary."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        summary = await use_case.get_budget_summary(
            business_id, user_id, 
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        )
        return summary
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting budget summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/{project_id}/assign",
    response_model=ProjectResponse,
    summary="Assign team members to project",
    description="Assign team members to a project."
)
async def assign_team_members(
    project_id: uuid.UUID,
    assignment_data: ProjectAssignmentRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ProjectAssignmentUseCase = Depends(get_project_assignment_use_case)
) -> ProjectResponse:
    """Assign team members to a project."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        assignment_dto = ProjectAssignmentDTO(
            user_ids=assignment_data.user_ids,
            replace_existing=assignment_data.replace_existing
        )
        
        result = await use_case.assign_team_members(project_id, business_id, assignment_dto, user_id)
        
        # Convert DTO to API response schema
        # Convert ContactAddressDTO to dict if present
        address_dict = None
        if result.client_address:
            address_dict = {
                "street_address": result.client_address.street_address,
                "city": result.client_address.city,
                "state": result.client_address.state,
                "postal_code": result.client_address.postal_code,
                "country": result.client_address.country,
                "latitude": result.client_address.latitude,
                "longitude": result.client_address.longitude,
                "access_notes": result.client_address.access_notes,
                "place_id": result.client_address.place_id,
                "formatted_address": result.client_address.formatted_address,
                "address_type": result.client_address.address_type
            }
        
        return ProjectResponse(
            id=result.id,
            business_id=result.business_id,
            project_number=result.project_number,
            name=result.name,
            description=result.description,
            created_by=result.created_by,
            client_id=result.client_id,
            client_name=result.client_name,
            address=address_dict,
            project_type=result.project_type,
            status=result.status,
            priority=result.priority,
            start_date=result.start_date,
            end_date=result.end_date,
            estimated_budget=result.estimated_budget,
            actual_cost=result.actual_cost,
            manager=result.manager,
            manager_id=result.manager_id,
            team_members=result.team_members,
            tags=result.tags,
            notes=result.notes,
            created_date=result.created_date,
            last_modified=result.last_modified,
            is_overdue=result.is_overdue,
            is_over_budget=result.is_over_budget,
            budget_variance=result.budget_variance,
            budget_variance_percentage=result.budget_variance_percentage,
            duration_days=result.duration_days,
            status_display=result.status_display,
            priority_display=result.priority_display,
            type_display=result.type_display
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error assigning team members: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# Project Templates endpoints
@router.post(
    "/templates",
    response_model=ProjectTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project template",
    description="Create a new project template."
)
async def create_project_template(
    template_data: ProjectTemplateCreateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ProjectTemplateUseCase = Depends(get_project_template_use_case)
) -> ProjectTemplateResponse:
    """Create a project template."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        create_dto = ProjectTemplateCreateDTO(
            name=template_data.name,
            description=template_data.description,
            project_type=template_data.project_type,
            default_priority=template_data.default_priority,
            estimated_hours=template_data.estimated_hours,
            budget_template=template_data.budget_template,
            default_tags=template_data.default_tags,
            checklist_items=template_data.checklist_items,
            required_skills=template_data.required_skills
        )
        
        result = await use_case.create_template(business_id, create_dto, user_id)
        return result
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating project template: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/templates/{template_id}/create-project",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project from template",
    description="Create a new project using a template."
)
async def create_project_from_template(
    template_id: uuid.UUID,
    project_data: ProjectCreateFromTemplateRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user),
    use_case: ProjectTemplateUseCase = Depends(get_project_template_use_case)
) -> ProjectResponse:
    """Create a project from a template."""
    try:
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        # Convert address if provided
        address_dto = None
        if project_data.address:
            logger.info(f"🔧 ProjectAPI: Converting address: {project_data.address}")
            address_dto = ContactAddressDTO(
                street_address=project_data.address.street_address,
                city=project_data.address.city,
                state=project_data.address.state,
                postal_code=project_data.address.postal_code,
                country=project_data.address.country,
                latitude=project_data.address.latitude,
                longitude=project_data.address.longitude,
                access_notes=project_data.address.access_notes,
                place_id=project_data.address.place_id,
                formatted_address=project_data.address.formatted_address,
                address_type=project_data.address.address_type
            )
        
        create_dto = ProjectCreateFromTemplateDTO(
            project_number=project_data.project_number,
            name=project_data.name,
            description=project_data.description,
            status=project_data.status,
            priority=project_data.priority,
            contact_id=project_data.contact_id,
            client_name=project_data.client_name,
            client_email=project_data.client_email,
            client_phone=project_data.client_phone,
            address=address_dto,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            estimated_hours=project_data.estimated_hours,
            budget_amount=project_data.budget_amount,
            team_members=project_data.team_members,
            tags=project_data.tags,
            notes=project_data.notes
        )
        
        result = await use_case.create_project_from_template(business_id, template_id, create_dto, user_id)
        
        # Convert DTO to API response schema
        # Convert ContactAddressDTO to dict if present
        address_dict = None
        if result.client_address:
            address_dict = {
                "street_address": result.client_address.street_address,
                "city": result.client_address.city,
                "state": result.client_address.state,
                "postal_code": result.client_address.postal_code,
                "country": result.client_address.country,
                "latitude": result.client_address.latitude,
                "longitude": result.client_address.longitude,
                "access_notes": result.client_address.access_notes,
                "place_id": result.client_address.place_id,
                "formatted_address": result.client_address.formatted_address,
                "address_type": result.client_address.address_type
            }
        
        return ProjectResponse(
            id=result.id,
            business_id=result.business_id,
            project_number=result.project_number,
            name=result.name,
            description=result.description,
            created_by=result.created_by,
            client_id=result.client_id,
            client_name=result.client_name,
            address=address_dict,
            project_type=result.project_type,
            status=result.status,
            priority=result.priority,
            start_date=result.start_date,
            end_date=result.end_date,
            estimated_budget=result.estimated_budget,
            actual_cost=result.actual_cost,
            manager=result.manager,
            manager_id=result.manager_id,
            team_members=result.team_members,
            tags=result.tags,
            notes=result.notes,
            created_date=result.created_date,
            last_modified=result.last_modified,
            is_overdue=result.is_overdue,
            is_over_budget=result.is_over_budget,
            budget_variance=result.budget_variance,
            budget_variance_percentage=result.budget_variance_percentage,
            duration_days=result.duration_days,
            status_display=result.status_display,
            priority_display=result.priority_display,
            type_display=result.type_display
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating project from template: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# Project-Job Management Endpoints
@router.post(
    "/{project_id}/jobs",
    response_model=ProjectJobAssignmentResponse,
    summary="Assign jobs to project",
    description="Assign multiple jobs to a project."
)
async def assign_jobs_to_project(
    project_id: uuid.UUID,
    assignment_data: ProjectJobAssignmentRequest,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user)
) -> ProjectJobAssignmentResponse:
    """Assign jobs to a project."""
    try:
        from ...infrastructure.config.dependency_injection import get_job_repository, get_project_repository
        
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        # Get repositories
        job_repository = get_job_repository()
        project_repository = get_project_repository()
        
        # Validate project exists and user has permission
        project = await project_repository.get_by_id(project_id, business_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        job_ids = assignment_data.job_ids
        if not job_ids:
            raise HTTPException(status_code=400, detail="At least one job ID required")
        
        updated_count = 0
        for job_id in job_ids:
            job = await job_repository.get_by_id(job_id)
            if job and job.business_id == business_id:
                job.project_id = project_id
                await job_repository.update(job)
                updated_count += 1
        
        return ProjectJobAssignmentResponse(
            project_id=project_id,
            job_ids=job_ids,
            message=f"Successfully assigned {updated_count} jobs to project"
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error assigning jobs to project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{project_id}/jobs",
    response_model=List[dict],  # Will be JobListResponse when imported
    summary="Get project jobs",
    description="Get all jobs associated with a project."
)
async def get_project_jobs(
    project_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user)
) -> List[dict]:
    """Get all jobs for a project."""
    try:
        from ...infrastructure.config.dependency_injection import get_job_repository, get_project_repository
        
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        # Get repositories
        job_repository = get_job_repository()
        project_repository = get_project_repository()
        
        # Validate project exists and user has permission
        project = await project_repository.get_by_id(project_id, business_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get jobs for this project
        jobs = await job_repository.get_by_project_id(project_id, business_id)
        
        # Convert to response format
        return [
            {
                "id": str(job.id),
                "job_number": job.job_number,
                "title": job.title,
                "job_type": job.job_type.value,
                "status": job.status.value,
                "priority": job.priority.value,
                "assigned_to": job.assigned_to,
                "scheduled_start": job.scheduled_start.isoformat() if job.scheduled_start else None,
                "scheduled_end": job.scheduled_end.isoformat() if job.scheduled_end else None,
                "created_date": job.created_date.isoformat(),
                "last_modified": job.last_modified.isoformat()
            }
            for job in jobs
        ]
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting project jobs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/{project_id}/jobs/{job_id}",
    response_model=ProjectActionResponse,
    summary="Remove job from project",
    description="Remove a job from a project (sets project_id to NULL)."
)
async def remove_job_from_project(
    project_id: uuid.UUID,
    job_id: uuid.UUID,
    business_context: dict = Depends(get_business_context),
    current_user: dict = Depends(get_current_user)
) -> ProjectActionResponse:
    """Remove a job from a project."""
    try:
        from ...infrastructure.config.dependency_injection import get_job_repository
        
        user_id = current_user["sub"]
        business_id = business_context["business_id"]
        
        # Get repository
        job_repository = get_job_repository()
        
        # Get and validate job
        job = await job_repository.get_by_id(job_id)
        if not job or job.business_id != business_id:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.project_id != project_id:
            raise HTTPException(status_code=400, detail="Job is not assigned to this project")
        
        # Remove project association
        job.project_id = None
        await job_repository.update(job)
        
        return ProjectActionResponse(
            success=True,
            message="Job successfully removed from project",
            project_id=project_id
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error removing job from project: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") 