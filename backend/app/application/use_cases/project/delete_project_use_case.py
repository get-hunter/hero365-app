"""
Delete Project Use Case

Business logic for project deletion operations in Hero365.
Handles project deletion with validation and business rules.
"""

import uuid

from ...exceptions.application_exceptions import (
    NotFoundError, BusinessRuleViolationError
)
from app.domain.entities.project_enums.enums import ProjectStatus
from app.domain.repositories.project_repository import ProjectRepository
from .project_helper_service import ProjectHelperService


class DeleteProjectUseCase:
    """
    Use case for deleting projects within Hero365.
    
    Handles project deletion with proper permission checks
    and business rule validation.
    """
    
    def __init__(
        self,
        project_repository: ProjectRepository,
        project_helper_service: ProjectHelperService
    ):
        self.project_repository = project_repository
        self.project_helper_service = project_helper_service
    
    async def execute(self, project_id: uuid.UUID, business_id: uuid.UUID, user_id: str) -> bool:
        """Delete a project."""
        
        # Check permission first
        await self.project_helper_service.check_permission(business_id, user_id, "delete_projects")
        
        project = await self.project_repository.get_by_id(project_id, business_id)
        if not project:
            raise NotFoundError("Project not found")
        
        # Business rule: Cannot delete completed projects that may have financial records
        if project.status == ProjectStatus.COMPLETED:
            raise BusinessRuleViolationError("Cannot delete completed projects")
        
        return await self.project_repository.delete(project_id, business_id) 