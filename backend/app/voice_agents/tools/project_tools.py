"""
Voice agent tools for project management.
Provides voice-activated project operations for Hero365.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
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

# Global context storage for the worker environment
_current_context: Dict[str, Any] = {}

def set_current_context(context: Dict[str, Any]) -> None:
    """Set the current agent context."""
    global _current_context
    _current_context = context

def get_current_context() -> Dict[str, Any]:
    """Get the current agent context."""
    global _current_context
    if not _current_context.get("business_id") or not _current_context.get("user_id"):
        logger.warning("Agent context not available for project tools")
        return {"business_id": None, "user_id": None}
    return _current_context


@function_tool
async def create_project(
    name: str,
    description: str,
    client_contact_id: str,
    project_type: str = "service",
    priority: str = "medium",
    start_date: Optional[str] = None,
    estimated_budget: Optional[float] = None
) -> str:
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
        String describing the project creation result
    """
    try:
        container = DependencyContainer()
        create_project_use_case = container.get_create_project_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return "I'm sorry, I can't create a project right now. Please try again."
        
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
        
        # Create a conversational response
        response = f"I've successfully created the project '{name}' with project number {result.project_number}."
        
        if result.start_date:
            response += f" The project is scheduled to start on {result.start_date.strftime('%B %d, %Y')}."
            
        if estimated_budget:
            response += f" The estimated budget is ${estimated_budget:,.0f}."
            
        response += " Is there anything else you'd like me to help you with for this project?"
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating project via voice agent: {str(e)}")
        return "I'm sorry, I wasn't able to create the project. Please try again or let me know if you need help with the project details."


@function_tool
async def get_active_projects(limit: int = 10) -> str:
    """
    Get active projects for the business.
    
    Args:
        limit: Maximum number of projects to return (default: 10)
    
    Returns:
        String describing the active projects
    """
    try:
        container = DependencyContainer()
        project_repository = container.get_project_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return "I'm sorry, I can't access your project information right now. Please try again."
        
        # Get active projects directly from repository
        projects = await project_repository.get_active_projects(
            business_id=uuid.UUID(business_id),
            skip=0,
            limit=limit
        )
        
        if not projects:
            return "You don't have any active projects at the moment. Would you like me to help you create a new project?"
        
        # Create a conversational response about the projects
        project_summaries = []
        for project in projects:
            status = project.status.value if hasattr(project.status, 'value') else str(project.status)
            priority = project.priority.value if hasattr(project.priority, 'value') else str(project.priority)
            
            summary = f"{project.name} - {status} priority"
            if project.start_date:
                summary += f", started {project.start_date.strftime('%B %d')}"
            if project.estimated_budget:
                summary += f", budget ${project.estimated_budget:,.0f}"
            
            project_summaries.append(summary)
        
        logger.info(f"Retrieved {len(projects)} active projects via voice agent")
        
        # Format the response for voice output
        if len(projects) == 1:
            return f"You have 1 active project: {project_summaries[0]}"
        elif len(projects) <= 3:
            return f"You have {len(projects)} active projects: {', '.join(project_summaries[:-1])}, and {project_summaries[-1]}"
        else:
            return f"You have {len(projects)} active projects. Here are the first 3: {', '.join(project_summaries[:3])}. Would you like me to continue with the rest?"
        
    except Exception as e:
        logger.error(f"Error retrieving active projects via voice agent: {str(e)}")
        return "I'm having trouble accessing your project information right now. Please try again in a moment."


@function_tool
async def get_projects_by_status(status: str, limit: int = 10) -> str:
    """
    Get projects filtered by status.
    
    Args:
        status: Project status (planning, active, on_hold, completed, cancelled)
        limit: Maximum number of projects to return (default: 10)
    
    Returns:
        String describing the projects with the specified status
    """
    try:
        container = DependencyContainer()
        project_repository = container.get_project_repository()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return "I'm sorry, I can't access your project information right now. Please try again."
        
        # Convert status string to enum
        try:
            status_enum = ProjectStatus(status.upper())
        except ValueError:
            return f"I don't recognize the status '{status}'. Valid statuses are: planning, active, on hold, completed, or cancelled."
        
        # Get projects by status directly from repository
        projects = await project_repository.get_by_status(
            business_id=uuid.UUID(business_id),
            status=status_enum,
            skip=0,
            limit=limit
        )
        
        if not projects:
            return f"You don't have any projects with status '{status}' at the moment."
        
        # Create conversational summaries
        project_summaries = []
        for project in projects:
            priority = project.priority.value if hasattr(project.priority, 'value') else str(project.priority)
            summary = f"{project.name} - {priority} priority"
            if project.start_date:
                summary += f", started {project.start_date.strftime('%B %d')}"
            if project.estimated_budget:
                summary += f", budget ${project.estimated_budget:,.0f}"
            project_summaries.append(summary)
        
        logger.info(f"Retrieved {len(projects)} projects with status {status} via voice agent")
        
        # Format the response for voice output
        if len(projects) == 1:
            return f"You have 1 project with status '{status}': {project_summaries[0]}"
        elif len(projects) <= 3:
            return f"You have {len(projects)} projects with status '{status}': {', '.join(project_summaries[:-1])}, and {project_summaries[-1]}"
        else:
            return f"You have {len(projects)} projects with status '{status}'. Here are the first 3: {', '.join(project_summaries[:3])}. Would you like me to continue with the rest?"
        
    except Exception as e:
        logger.error(f"Error retrieving projects by status via voice agent: {str(e)}")
        return "I'm having trouble accessing your project information right now. Please try again in a moment."


@function_tool
async def update_project_status(project_id: str, new_status: str, notes: Optional[str] = None) -> str:
    """
    Update project status with optional notes.
    
    Args:
        project_id: ID of the project to update
        new_status: New status (planning, active, on_hold, completed, cancelled)
        notes: Optional notes about the status change
    
    Returns:
        String confirming the status update
    """
    try:
        container = DependencyContainer()
        update_project_use_case = container.get_update_project_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return "I'm sorry, I can't update the project status right now. Please try again."
        
        # Convert status string to enum
        try:
            status_enum = ProjectStatus(new_status.upper())
        except ValueError:
            return f"I don't recognize the status '{new_status}'. Valid statuses are: planning, active, on hold, completed, or cancelled."
        
        # Create update DTO
        update_dto = ProjectUpdateDTO(
            status=status_enum,
            notes=notes
        )
        
        result = await update_project_use_case.execute(
            project_id=uuid.UUID(project_id),
            business_id=uuid.UUID(business_id),
            project_data=update_dto,
            user_id=user_id
        )
        
        logger.info(f"Updated project {project_id} status to {new_status} via voice agent")
        
        response = f"Project status has been updated to {new_status}."
        if notes:
            response += f" Notes added: {notes}"
        
        return response
        
    except Exception as e:
        logger.error(f"Error updating project status via voice agent: {str(e)}")
        return "I'm having trouble updating the project status. Please check the project ID and try again."


@function_tool
async def get_project_details(project_id: str) -> str:
    """
    Get detailed information about a specific project.
    
    Args:
        project_id: ID or name of the project to retrieve
    
    Returns:
        String describing the project details
    """
    try:
        container = DependencyContainer()
        get_project_use_case = container.get_project_search_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return "I'm sorry, I can't access your project information right now. Please try again."
        
        # Check if project_id is a valid UUID
        project_uuid = None
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            # If not a valid UUID, search for project by name
            logger.info(f"Searching for project by name: {project_id}")
            search_dto = ProjectSearchDTO(
                search=project_id,
                limit=1
            )
            
            search_results = await get_project_use_case.search_projects(
                business_id=uuid.UUID(business_id),
                search_criteria=search_dto,
                user_id=user_id
            )
            
            if not search_results:
                return f"I couldn't find a project with the name '{project_id}'. Please check the project name and try again."
            
            # Use the first search result
            project = search_results[0]
            project_uuid = project.id
        
        # Now get the project details using the correct use case
        project_detail_use_case = container.get_get_project_use_case()
        result = await project_detail_use_case.execute(
            project_id=project_uuid,
            business_id=uuid.UUID(business_id),
            user_id=user_id
        )
        
        logger.info(f"Retrieved project details for {project_id} via voice agent")
        
        # Build a conversational response
        status = result.status.value if hasattr(result.status, 'value') else str(result.status)
        priority = result.priority.value if hasattr(result.priority, 'value') else str(result.priority)
        project_type = result.project_type.value if hasattr(result.project_type, 'value') else str(result.project_type)
        
        response = f"Here are the details for project {result.name}: "
        response += f"It's a {project_type} project with {priority} priority and {status} status. "
        
        if result.description:
            response += f"Description: {result.description}. "
        
        if result.start_date:
            response += f"Started on {result.start_date.strftime('%B %d, %Y')}. "
        
        if result.end_date:
            response += f"Expected completion date is {result.end_date.strftime('%B %d, %Y')}. "
        
        if result.estimated_budget:
            response += f"Estimated budget is ${result.estimated_budget:,.0f}. "
        
        if result.actual_cost:
            response += f"Actual cost so far is ${result.actual_cost:,.0f}. "
        
        progress = getattr(result, 'progress_percentage', 0)
        if progress > 0:
            response += f"Project is {progress}% complete. "
        
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving project details via voice agent: {str(e)}")
        return "I'm having trouble accessing the details for that project. Please check the project name or ID and try again."


@function_tool
async def search_projects(search_term: str, limit: int = 10) -> str:
    """
    Search projects by name, description, or project number.
    
    Args:
        search_term: Text to search for in project names, descriptions, or numbers
        limit: Maximum number of projects to return (default: 10)
    
    Returns:
        String describing the search results
    """
    try:
        container = DependencyContainer()
        project_search_use_case = container.get_project_search_use_case()
        
        context = get_current_context()
        business_id = context["business_id"]
        user_id = context["user_id"]
        
        if not business_id or not user_id:
            return "I'm sorry, I can't search your projects right now. Please try again."
        
        search_dto = ProjectSearchDTO(
            search=search_term,
            limit=limit
        )
        
        results = await project_search_use_case.search_projects(
            business_id=uuid.UUID(business_id),
            search_criteria=search_dto,
            user_id=user_id
        )
        
        if not results:
            return f"I didn't find any projects matching '{search_term}'. Would you like to try a different search term?"
        
        # Create conversational summaries
        project_summaries = []
        for project in results:
            status = project.status.value if hasattr(project.status, 'value') else str(project.status)
            priority = project.priority.value if hasattr(project.priority, 'value') else str(project.priority)
            
            summary = f"{project.name} - {status} status, {priority} priority"
            if project.start_date:
                summary += f", started {project.start_date.strftime('%B %d')}"
            
            project_summaries.append(summary)
        
        logger.info(f"Found {len(results)} projects matching '{search_term}' via voice agent")
        
        # Format the response for voice output
        if len(results) == 1:
            return f"I found 1 project matching '{search_term}': {project_summaries[0]}"
        elif len(results) <= 3:
            return f"I found {len(results)} projects matching '{search_term}': {', '.join(project_summaries[:-1])}, and {project_summaries[-1]}"
        else:
            return f"I found {len(results)} projects matching '{search_term}'. Here are the first 3: {', '.join(project_summaries[:3])}. Would you like me to continue with the rest?"
        
    except Exception as e:
        logger.error(f"Error searching projects via voice agent: {str(e)}")
        return f"I'm having trouble searching for projects with '{search_term}'. Please try again in a moment." 