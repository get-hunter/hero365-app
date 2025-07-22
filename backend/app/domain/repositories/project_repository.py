"""
Project Repository Interface

Defines the contract for project data access operations.
This interface follows the Repository pattern from clean architecture.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from ..entities.project import Project, ProjectTemplate
from ..entities.project_enums.enums import ProjectType, ProjectStatus, ProjectPriority


class ProjectRepository(ABC):
    """Abstract repository interface for Project entity operations."""
    
    @abstractmethod
    async def create(self, project: Project) -> Project:
        """Create a new project."""
        pass
    
    @abstractmethod
    async def get_by_id(self, project_id: UUID, business_id: UUID) -> Optional[Project]:
        """Get a project by ID within business context."""
        pass
    
    @abstractmethod
    async def update(self, project: Project) -> Project:
        """Update an existing project."""
        pass
    
    @abstractmethod
    async def delete(self, project_id: UUID, business_id: UUID) -> bool:
        """Delete a project by ID within business context."""
        pass
    
    @abstractmethod
    async def get_by_business(
        self,
        business_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProjectStatus] = None,
        project_type: Optional[ProjectType] = None,
        priority: Optional[ProjectPriority] = None,
        client_id: Optional[UUID] = None,
        manager_id: Optional[UUID] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Project], int]:
        """
        Get projects by business with filtering, pagination and search.
        Returns tuple of (projects, total_count).
        """
        pass
    
    @abstractmethod
    async def get_by_client(self, client_id: UUID, business_id: UUID) -> List[Project]:
        """Get all projects for a specific client."""
        pass
    
    @abstractmethod
    async def get_by_manager(self, manager_id: UUID, business_id: UUID) -> List[Project]:
        """Get all projects managed by a specific user."""
        pass
    
    @abstractmethod
    async def get_by_status(self, status: ProjectStatus, business_id: UUID) -> List[Project]:
        """Get all projects with a specific status."""
        pass
    
    @abstractmethod
    async def get_overdue_projects(self, business_id: UUID) -> List[Project]:
        """Get all overdue projects for a business."""
        pass
    
    @abstractmethod
    async def get_project_analytics(
        self,
        business_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[ProjectStatus] = None,
        project_type: Optional[ProjectType] = None
    ) -> Dict[str, Any]:
        """Get project analytics data for a business."""
        pass
    
    @abstractmethod
    async def count_by_business(self, business_id: UUID) -> int:
        """Count total projects for a business."""
        pass
    
    @abstractmethod
    async def exists(self, project_id: UUID, business_id: UUID) -> bool:
        """Check if a project exists within business context."""
        pass


class ProjectTemplateRepository(ABC):
    """Abstract repository interface for ProjectTemplate entity operations."""
    
    @abstractmethod
    async def create(self, template: ProjectTemplate) -> ProjectTemplate:
        """Create a new project template."""
        pass
    
    @abstractmethod
    async def get_by_id(self, template_id: UUID, business_id: Optional[UUID] = None) -> Optional[ProjectTemplate]:
        """Get a template by ID. If business_id is None, only system templates are considered."""
        pass
    
    @abstractmethod
    async def update(self, template: ProjectTemplate) -> ProjectTemplate:
        """Update an existing project template."""
        pass
    
    @abstractmethod
    async def delete(self, template_id: UUID, business_id: UUID) -> bool:
        """Delete a business template by ID."""
        pass
    
    @abstractmethod
    async def get_by_business(
        self,
        business_id: UUID,
        include_system: bool = True,
        project_type: Optional[ProjectType] = None
    ) -> List[ProjectTemplate]:
        """Get templates accessible by a business (business templates + system templates)."""
        pass
    
    @abstractmethod
    async def get_system_templates(
        self,
        project_type: Optional[ProjectType] = None
    ) -> List[ProjectTemplate]:
        """Get all system templates."""
        pass
    
    @abstractmethod
    async def get_business_templates(
        self,
        business_id: UUID,
        project_type: Optional[ProjectType] = None
    ) -> List[ProjectTemplate]:
        """Get templates created by a specific business."""
        pass
    
    @abstractmethod
    async def exists(self, template_id: UUID, business_id: Optional[UUID] = None) -> bool:
        """Check if a template exists and is accessible by the business."""
        pass 