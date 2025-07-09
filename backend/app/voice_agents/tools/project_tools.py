"""
Voice agent tools for project management.
Provides voice-activated project operations for Hero365.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from contextvars import ContextVar
from decimal import Decimal

from livekit.agents import function_tool

from app.infrastructure.config.dependency_injection import DependencyContainer
from app.application.use_cases.project.create_project_use_case import CreateProjectUseCase
from app.application.use_cases.project.get_project_use_case import GetProjectUseCase
from app.application.use_cases.project.update_project_use_case import UpdateProjectUseCase
from app.application.use_cases.project.delete_project_use_case import DeleteProjectUseCase
from app.application.use_cases.project.project_search_use_case import ProjectSearchUseCase
from app.application.dto.project_dto import (
    ProjectResponseDTO,
    ProjectCreateDTO,
    ProjectUpdateDTO,
    ProjectSearchDTO,
)
from app.application.dto.contact_dto import ContactSearchDTO
from app.domain.enums import ProjectStatus, ProjectType, ProjectPriority

logger = logging.getLogger(__name__)

# Context variable to store the current agent context
_current_context: ContextVar[Dict[str, Any]] = ContextVar('current_context', default={})

def set_current_context(context: Dict[str, Any]) -> None:
    """Set the current agent context."""
    _current_context.set(context)

def get_current_context() -> Dict[str, Any]:
    """Get the current agent context."""
    context = _current_context.get()
    if not context.get("business_id") or not context.get("user_id"):
        logger.warning("Agent context not available for project tools")
        return {"business_id": None, "user_id": None}
    return context


@function_tool
async def create_project(
    name: str,
    description: str,
    client_contact_id: str,
    project_type: str = "service",
    priority: str = "medium",
    start_date: Optional[str] = None,
    estimated_budget: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create a new project for the business.
    
    Args:
        name: Project name or title
        description: Detailed project description
        client_contact_id: ID of the client contact
        project_type: Type of project (service, maintenance, installation, renovation)
        priority: Project priority (low, medium, high, urgent)
        start_date: Planned start date (YYYY-MM-DD format)
        estimated_budget: Estimated project budget
    
    Returns:
        Dictionary with project creation result
    """
    try:
        container = DependencyContainer()
        create_project_use_case = CreateProjectUseCase(container)
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to create project. Please try again."
            }
        
        # Convert string enums
        try:
            project_type_enum = ProjectType(project_type.upper())
        except ValueError:
            project_type_enum = ProjectType.SERVICE
            
        try:
            priority_enum = ProjectPriority(priority.upper())
        except ValueError:
            priority_enum = ProjectPriority.MEDIUM
        
        # Parse start date
        parsed_start_date = None
        if start_date:
            try:
                parsed_start_date = datetime.fromisoformat(start_date)
            except ValueError:
                logger.warning(f"Invalid start date format: {start_date}")
        
        project_dto = ProjectCreateDTO(
            business_id=uuid.UUID(business_id),
            contact_id=uuid.UUID(client_contact_id) if client_contact_id else None,
            name=name,
            description=description,
            project_type=project_type_enum,
            priority=priority_enum,
            start_date=parsed_start_date,
            estimated_budget=estimated_budget
        )
        
        result = await create_project_use_case.execute(project_dto, business_id, user_id)
        
        logger.info(f"Created project via voice agent: {result.id}")
        
        return {
            "success": True,
            "project_id": str(result.id),
            "name": result.name,
            "project_number": result.project_number,
            "start_date": result.start_date.isoformat() if result.start_date else None,
            "message": f"Project '{name}' created successfully with number {result.project_number}"
        }
        
    except Exception as e:
        logger.error(f"Error creating project via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create project. Please try again or contact support."
        }


@function_tool
async def get_active_projects(limit: int = 10) -> Dict[str, Any]:
    """
    Get active projects for the business.
    
    Args:
        limit: Maximum number of projects to return (default: 10)
    
    Returns:
        Dictionary with active projects list
    """
    try:
        container = DependencyContainer()
        project_repository = container.get_project_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve projects. Please try again."
            }
        
        # Get active projects directly from repository
        projects = await project_repository.get_active_projects(
            business_id=uuid.UUID(business_id),
            skip=0,
            limit=limit
        )
        
        active_projects = []
        for project in projects:
            active_projects.append({
                "id": str(project.id),
                "name": project.name,
                "project_number": project.project_number,
                "status": project.status.value,
                "priority": project.priority.value,
                "start_date": project.start_date.date() if project.start_date else None,
                "estimated_budget": float(project.estimated_budget) if project.estimated_budget else None,
                "progress_percentage": project.progress_percentage
            })
        
        logger.info(f"Retrieved {len(active_projects)} active projects via voice agent")
        
        return {
            "success": True,
            "projects": active_projects,
            "total_count": len(active_projects),
            "message": f"Found {len(active_projects)} active projects"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving active projects via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve active projects. Please try again."
        }


@function_tool
async def get_projects_by_status(status: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get projects filtered by status.
    
    Args:
        status: Project status (planning, active, on_hold, completed, cancelled)
        limit: Maximum number of projects to return (default: 10)
    
    Returns:
        Dictionary with filtered projects
    """
    try:
        container = DependencyContainer()
        project_repository = container.get_project_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve projects by status. Please try again."
            }
        
        # Convert status string to enum
        try:
            status_enum = ProjectStatus(status.upper())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid status: {status}",
                "message": "Valid statuses are: planning, active, on_hold, completed, cancelled"
            }
        
        # Get projects by status directly from repository
        projects = await project_repository.get_by_status(
            business_id=uuid.UUID(business_id),
            status=status_enum,
            skip=0,
            limit=limit
        )
        
        project_list = []
        for project in projects:
            project_list.append({
                "id": str(project.id),
                "name": project.name,
                "project_number": project.project_number,
                "priority": project.priority.value,
                "start_date": project.start_date.date() if project.start_date else None,
                "estimated_budget": float(project.estimated_budget) if project.estimated_budget else None
            })
        
        logger.info(f"Retrieved {len(project_list)} projects with status {status} via voice agent")
        
        return {
            "success": True,
            "projects": project_list,
            "status_filter": status,
            "total_count": len(project_list),
            "message": f"Found {len(project_list)} projects with status: {status}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving projects by status via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve projects by status. Please try again."
        }


@function_tool
async def update_project_status(project_id: str, new_status: str, notes: Optional[str] = None) -> Dict[str, Any]:
    """
    Update project status with optional notes.
    
    Args:
        project_id: ID of the project to update
        new_status: New status (planning, active, on_hold, completed, cancelled)
        notes: Optional notes about the status change
    
    Returns:
        Dictionary with update result
    """
    try:
        container = DependencyContainer()
        update_project_use_case = UpdateProjectUseCase(container)
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to update project status. Please try again."
            }
        
        # Convert status string to enum
        try:
            status_enum = ProjectStatus(new_status.upper())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid status: {new_status}",
                "message": "Valid statuses are: planning, active, on_hold, completed, cancelled"
            }
        
        # Create update DTO
        update_dto = ProjectUpdateDTO(
            status=status_enum,
            notes=notes
        )
        
        result = await update_project_use_case.execute(
            project_id=uuid.UUID(project_id),
            project_data=update_dto,
            user_id=user_id
        )
        
        logger.info(f"Updated project {project_id} status to {new_status} via voice agent")
        
        return {
            "success": True,
            "project_id": project_id,
            "new_status": new_status,
            "notes": notes,
            "message": f"Project status updated to {new_status}"
        }
        
    except Exception as e:
        logger.error(f"Error updating project status via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to update project status. Please try again."
        }


@function_tool
async def get_project_details(project_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific project.
    
    Args:
        project_id: ID of the project to retrieve
    
    Returns:
        Dictionary with project details
    """
    try:
        container = DependencyContainer()
        get_project_use_case = GetProjectUseCase(container)
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to retrieve project details. Please try again."
            }
        
        result = await get_project_use_case.execute(
            project_id=uuid.UUID(project_id),
            user_id=user_id
        )
        
        logger.info(f"Retrieved project details for {project_id} via voice agent")
        
        return {
            "success": True,
            "project": {
                "id": str(result.id),
                "name": result.name,
                "project_number": result.project_number,
                "description": result.description,
                "status": result.status.value,
                "priority": result.priority.value,
                "project_type": result.project_type.value,
                "start_date": result.start_date.date() if result.start_date else None,
                "end_date": result.end_date.date() if result.end_date else None,
                "estimated_budget": float(result.estimated_budget) if result.estimated_budget else None,
                "actual_cost": float(result.actual_cost) if result.actual_cost else None,
                "progress_percentage": result.progress_percentage,
                "team_members": result.team_members
            },
            "message": f"Retrieved details for project {result.name}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving project details via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve project details. Please try again."
        }


@function_tool
async def search_projects(search_term: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search projects by name, description, or project number.
    
    Args:
        search_term: Text to search for in project names, descriptions, or numbers
        limit: Maximum number of projects to return (default: 10)
    
    Returns:
        Dictionary with search results
    """
    try:
        container = DependencyContainer()
        project_search_use_case = ProjectSearchUseCase(container)
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return {
                "success": False,
                "error": "Agent context not available",
                "message": "Unable to search projects. Please try again."
            }
        
        search_dto = ProjectSearchDTO(
            search=search_term,
            limit=limit
        )
        
        results = await project_search_use_case.search_projects(
            business_id=business_id,
            search_params=search_dto,
            user_id=user_id
        )
        
        projects = []
        for project in results:
            projects.append({
                "id": str(project.id),
                "name": project.name,
                "project_number": project.project_number,
                "status": project.status.value,
                "priority": project.priority.value,
                "start_date": project.start_date.date() if project.start_date else None
            })
        
        logger.info(f"Found {len(projects)} projects matching '{search_term}' via voice agent")
        
        return {
            "success": True,
            "projects": projects,
            "search_term": search_term,
            "total_count": len(projects),
            "message": f"Found {len(projects)} projects matching '{search_term}'"
        }
        
    except Exception as e:
        logger.error(f"Error searching projects via voice agent: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to search projects. Please try again."
        } 