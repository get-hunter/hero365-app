"""
Project Search Use Case

Business logic for project search and filtering operations in Hero365.
Handles project listing, searching, and filtering with various criteria.
"""

import uuid
from typing import List

from ...dto.project_dto import ProjectListDTO, ProjectSearchDTO
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.enums import ProjectStatus, ProjectType, ProjectPriority
from .project_helper_service import ProjectHelperService


class ProjectSearchUseCase:
    """
    Use case for searching and listing projects within Hero365.
    
    Handles project listing, search with filters, and various
    query operations with proper permission validation.
    """
    
    def __init__(
        self,
        project_repository: ProjectRepository,
        project_helper_service: ProjectHelperService
    ):
        self.project_repository = project_repository
        self.project_helper_service = project_helper_service
    
    async def list_projects(self, business_id: uuid.UUID, user_id: str,
                           skip: int = 0, limit: int = 100) -> List[ProjectListDTO]:
        """List projects for a business."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        projects = await self.project_repository.get_by_business_id(business_id, skip, limit)
        
        return [await self.project_helper_service.convert_to_list_dto(project) for project in projects]
    
    async def search_projects(self, business_id: uuid.UUID, search_criteria: ProjectSearchDTO,
                             user_id: str, skip: int = 0, limit: int = 100) -> List[ProjectListDTO]:
        """Search projects with various criteria."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        # Start with all projects if no specific criteria
        if search_criteria.search:
            projects = await self.project_repository.search_projects(
                business_id, search_criteria.search, skip, limit
            )
        else:
            projects = await self.project_repository.get_by_business_id(business_id, skip, limit)
        
        # Apply additional filters
        filtered_projects = []
        for project in projects:
            if self._matches_criteria(project, search_criteria):
                filtered_projects.append(project)
        
        return [await self.project_helper_service.convert_to_list_dto(project) for project in filtered_projects]
    
    async def get_by_status(self, business_id: uuid.UUID, status: ProjectStatus, user_id: str,
                           skip: int = 0, limit: int = 100) -> List[ProjectListDTO]:
        """Get projects by status."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        projects = await self.project_repository.get_by_status(business_id, status, skip, limit)
        
        return [await self.project_helper_service.convert_to_list_dto(project) for project in projects]
    
    async def get_by_type(self, business_id: uuid.UUID, project_type: ProjectType, user_id: str,
                         skip: int = 0, limit: int = 100) -> List[ProjectListDTO]:
        """Get projects by type."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        projects = await self.project_repository.get_by_type(business_id, project_type, skip, limit)
        
        return [await self.project_helper_service.convert_to_list_dto(project) for project in projects]
    
    async def get_by_priority(self, business_id: uuid.UUID, priority: ProjectPriority, user_id: str,
                             skip: int = 0, limit: int = 100) -> List[ProjectListDTO]:
        """Get projects by priority."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        projects = await self.project_repository.get_by_priority(business_id, priority, skip, limit)
        
        return [await self.project_helper_service.convert_to_list_dto(project) for project in projects]
    
    async def get_active_projects(self, business_id: uuid.UUID, user_id: str,
                                 skip: int = 0, limit: int = 100) -> List[ProjectListDTO]:
        """Get active projects."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        projects = await self.project_repository.get_active_projects(business_id, skip, limit)
        
        return [await self.project_helper_service.convert_to_list_dto(project) for project in projects]
    
    async def get_overdue_projects(self, business_id: uuid.UUID, user_id: str,
                                  skip: int = 0, limit: int = 100) -> List[ProjectListDTO]:
        """Get overdue projects."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        projects = await self.project_repository.get_overdue_projects(business_id, skip, limit)
        
        return [await self.project_helper_service.convert_to_list_dto(project) for project in projects]
    
    async def get_projects_by_tag(self, business_id: uuid.UUID, tag: str, user_id: str,
                                 skip: int = 0, limit: int = 100) -> List[ProjectListDTO]:
        """Get projects by tag."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        projects = await self.project_repository.get_projects_by_tag(business_id, tag, skip, limit)
        
        return [await self.project_helper_service.convert_to_list_dto(project) for project in projects]
    
    def _matches_criteria(self, project, criteria: ProjectSearchDTO) -> bool:
        """Check if project matches search criteria."""
        
        # Filter by status
        if criteria.status and project.status != criteria.status:
            return False
        
        # Filter by type
        if criteria.project_type and project.project_type != criteria.project_type:
            return False
        
        # Filter by priority
        if criteria.priority and project.priority != criteria.priority:
            return False
        
        # Filter by start date range
        if criteria.start_date_from and project.start_date and project.start_date < criteria.start_date_from:
            return False
        
        if criteria.start_date_to and project.start_date and project.start_date > criteria.start_date_to:
            return False
        
        # Filter by end date range
        if criteria.end_date_from and project.end_date and project.end_date < criteria.end_date_from:
            return False
        
        if criteria.end_date_to and project.end_date and project.end_date > criteria.end_date_to:
            return False
        
        # Filter by tags
        if criteria.tags:
            project_tags = set(project.tags or [])
            search_tags = set(criteria.tags)
            if not search_tags.intersection(project_tags):
                return False
        
        return True 