"""
Update Project Use Case

Business logic for project update operations in Hero365.
Handles project updates with validation and business rules.
"""

import uuid
from datetime import datetime

from ...dto.project_dto import ProjectUpdateDTO, ProjectResponseDTO
from ...exceptions.application_exceptions import NotFoundError
from app.domain.repositories.project_repository import ProjectRepository
from .project_helper_service import ProjectHelperService


class UpdateProjectUseCase:
    """
    Use case for updating existing projects within Hero365.
    
    Handles project updates with proper validation, permission checks,
    and business rule enforcement.
    """
    
    def __init__(
        self,
        project_repository: ProjectRepository,
        project_helper_service: ProjectHelperService
    ):
        self.project_repository = project_repository
        self.project_helper_service = project_helper_service
    
    async def execute(self, project_id: uuid.UUID, business_id: uuid.UUID, project_data: ProjectUpdateDTO, 
                     user_id: str) -> ProjectResponseDTO:
        """Update an existing project."""
        
        # Check permission first
        await self.project_helper_service.check_permission(business_id, user_id, "edit_projects")
        
        project = await self.project_repository.get_by_id(project_id, business_id)
        if not project:
            raise NotFoundError("Project not found")
        
        # Validate contact if provided
        if project_data.contact_id is not None:
            if project_data.contact_id:  # Not None and not empty
                await self.project_helper_service.validate_contact(business_id, project_data.contact_id)
        
        # Validate team members if provided
        if project_data.team_members is not None:
            await self.project_helper_service.validate_assigned_users(business_id, project_data.team_members)
        
        # Update project fields using model_copy to maintain Pydantic validation
        update_data = {}
        if project_data.name is not None:
            update_data["name"] = project_data.name
        if project_data.description is not None:
            update_data["description"] = project_data.description
        if project_data.project_type is not None:
            update_data["project_type"] = project_data.project_type
        if project_data.status is not None:
            update_data["status"] = project_data.status
        if project_data.priority is not None:
            update_data["priority"] = project_data.priority
        if project_data.contact_id is not None:
            update_data["contact_id"] = project_data.contact_id
        if project_data.client_name is not None:
            update_data["client_name"] = project_data.client_name
        if project_data.client_email is not None:
            update_data["client_email"] = project_data.client_email
        if project_data.client_phone is not None:
            update_data["client_phone"] = project_data.client_phone
        if project_data.address is not None:
            update_data["address"] = project_data.address
        if project_data.start_date is not None:
            update_data["start_date"] = project_data.start_date
        if project_data.end_date is not None:
            update_data["end_date"] = project_data.end_date
        if project_data.estimated_hours is not None:
            update_data["estimated_hours"] = project_data.estimated_hours
        if project_data.actual_hours is not None:
            update_data["actual_hours"] = project_data.actual_hours
        if project_data.budget_amount is not None:
            update_data["budget_amount"] = project_data.budget_amount
        if project_data.actual_cost is not None:
            update_data["actual_cost"] = project_data.actual_cost
        if project_data.team_members is not None:
            update_data["team_members"] = project_data.team_members
        if project_data.tags is not None:
            update_data["tags"] = project_data.tags
        if project_data.notes is not None:
            update_data["notes"] = project_data.notes
        
        # Add updated timestamp
        update_data["updated_date"] = datetime.now()
        
        # Apply updates using Pydantic model_copy for validation
        updated_project = project.model_copy(update=update_data)
        
        # Save updated project
        saved_project = await self.project_repository.update(updated_project)
        
        return await self.project_helper_service.convert_to_response_dto(saved_project) 