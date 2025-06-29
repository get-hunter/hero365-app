"""
Get Project Use Case

Business logic for project retrieval operations in Hero365.
Handles project fetching by ID with permission validation.
"""

import uuid

from ...dto.project_dto import ProjectResponseDTO
from ...exceptions.application_exceptions import NotFoundError
from app.domain.repositories.project_repository import ProjectRepository
from .project_helper_service import ProjectHelperService


class GetProjectUseCase:
    """
    Use case for retrieving projects within Hero365.
    
    Handles project retrieval by ID with proper permission checks
    and data transformation to response DTOs.
    """
    
    def __init__(
        self,
        project_repository: ProjectRepository,
        project_helper_service: ProjectHelperService
    ):
        self.project_repository = project_repository
        self.project_helper_service = project_helper_service
    
    async def execute(self, project_id: uuid.UUID, business_id: uuid.UUID, user_id: str) -> ProjectResponseDTO:
        """Get a project by ID."""
        
        # Check permission first
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        project = await self.project_repository.get_by_id(project_id, business_id)
        if not project:
            raise NotFoundError("Project not found")
        
        return await self.project_helper_service.convert_to_response_dto(project) 