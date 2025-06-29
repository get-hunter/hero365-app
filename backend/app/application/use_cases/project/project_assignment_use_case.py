"""
Project Assignment Use Case

Business logic for project assignment and team management operations in Hero365.
Handles project assignments to team members and team management.
"""

import uuid
from typing import List

from ...dto.project_dto import ProjectAssignmentDTO, ProjectResponseDTO
from ...exceptions.application_exceptions import NotFoundError
from app.domain.repositories.project_repository import ProjectRepository
from .project_helper_service import ProjectHelperService


class ProjectAssignmentUseCase:
    """
    Use case for managing project assignments within Hero365.
    
    Handles project assignments to team members and validates
    user permissions and business membership.
    """
    
    def __init__(
        self,
        project_repository: ProjectRepository,
        project_helper_service: ProjectHelperService
    ):
        self.project_repository = project_repository
        self.project_helper_service = project_helper_service
    
    async def assign_team_members(self, project_id: uuid.UUID, business_id: uuid.UUID, assignment_data: ProjectAssignmentDTO,
                                 user_id: str) -> ProjectResponseDTO:
        """Assign team members to a project."""
        
        # Check permission first
        await self.project_helper_service.check_permission(business_id, user_id, "edit_projects")
        
        project = await self.project_repository.get_by_id(project_id, business_id)
        if not project:
            raise NotFoundError("Project not found")
        
        # Validate assigned users
        await self.project_helper_service.validate_assigned_users(business_id, assignment_data.user_ids)
        
        # Update team members
        if assignment_data.replace_existing:
            # Replace all existing team members
            updated_project = project.model_copy(update={"team_members": assignment_data.user_ids})
        else:
            # Add to existing team members (avoiding duplicates)
            current_team = set(project.team_members or [])
            new_team = current_team.union(set(assignment_data.user_ids))
            updated_project = project.model_copy(update={"team_members": list(new_team)})
        
        # Save updated project
        saved_project = await self.project_repository.update(updated_project)
        
        return await self.project_helper_service.convert_to_response_dto(saved_project)
    
    async def remove_team_members(self, project_id: uuid.UUID, business_id: uuid.UUID, user_ids: List[str],
                                 requester_user_id: str) -> ProjectResponseDTO:
        """Remove team members from a project."""
        
        # Check permission first
        await self.project_helper_service.check_permission(business_id, requester_user_id, "edit_projects")
        
        project = await self.project_repository.get_by_id(project_id, business_id)
        if not project:
            raise NotFoundError("Project not found")
        
        # Remove users from team members
        current_team = set(project.team_members or [])
        users_to_remove = set(user_ids)
        new_team = current_team - users_to_remove
        
        # Update project
        updated_project = project.model_copy(update={"team_members": list(new_team)})
        
        # Save updated project
        saved_project = await self.project_repository.update(updated_project)
        
        return await self.project_helper_service.convert_to_response_dto(saved_project)
    
    async def get_user_projects(self, business_id: uuid.UUID, assigned_user_id: str,
                               requester_user_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get projects assigned to a specific user."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, requester_user_id, "view_projects")
        
        # Get all projects for the business and filter by assigned user
        all_projects = await self.project_repository.get_by_business_id(business_id, 0, 1000)  # Get more for filtering
        
        # Filter projects where user is assigned
        user_projects = [
            project for project in all_projects 
            if assigned_user_id in (project.team_members or [])
        ]
        
        # Apply pagination
        paginated_projects = user_projects[skip:skip + limit]
        
        # Convert to list DTOs
        return [await self.project_helper_service.convert_to_list_dto(project) for project in paginated_projects] 