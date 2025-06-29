"""
Project Use Cases Module

This module contains all project-related use cases following clean architecture principles.
Each use case handles a specific aspect of project management operations.
"""

# Individual CRUD use cases
from .create_project_use_case import CreateProjectUseCase
from .get_project_use_case import GetProjectUseCase
from .update_project_use_case import UpdateProjectUseCase
from .delete_project_use_case import DeleteProjectUseCase

# Template management use cases
from .project_template_use_case import ProjectTemplateUseCase

# Other specialized use cases
from .project_search_use_case import ProjectSearchUseCase
from .project_analytics_use_case import ProjectAnalyticsUseCase
from .project_assignment_use_case import ProjectAssignmentUseCase

# Helper service
from .project_helper_service import ProjectHelperService

__all__ = [
    # Individual CRUD use cases
    "CreateProjectUseCase",
    "GetProjectUseCase",
    "UpdateProjectUseCase",
    "DeleteProjectUseCase",
    
    # Template management
    "ProjectTemplateUseCase",
    
    # Specialized use cases
    "ProjectSearchUseCase",
    "ProjectAnalyticsUseCase",
    "ProjectAssignmentUseCase",
    
    # Helper service
    "ProjectHelperService",
] 