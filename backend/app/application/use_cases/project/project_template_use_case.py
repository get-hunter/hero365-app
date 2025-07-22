"""
Project Template Use Case

Business logic for project template management operations in Hero365.
Handles project template creation, updates, and usage.
"""

import uuid
from typing import List, Optional

from ...dto.project_dto import (
    ProjectTemplateCreateDTO, ProjectTemplateUpdateDTO, ProjectTemplateResponseDTO,
    ProjectCreateFromTemplateDTO, ProjectResponseDTO
)
from ...exceptions.application_exceptions import NotFoundError, ValidationError
from app.domain.entities.project import ProjectTemplate, Project
from app.domain.repositories.project_repository import ProjectTemplateRepository, ProjectRepository
from app.domain.entities.project_enums.enums import ProjectType
from .project_helper_service import ProjectHelperService


class ProjectTemplateUseCase:
    """
    Use case for managing project templates within Hero365.
    
    Handles template creation, updates, and project creation from templates.
    """
    
    def __init__(
        self,
        project_template_repository: ProjectTemplateRepository,
        project_repository: ProjectRepository,
        project_helper_service: ProjectHelperService
    ):
        self.project_template_repository = project_template_repository
        self.project_repository = project_repository
        self.project_helper_service = project_helper_service
    
    async def create_template(self, business_id: uuid.UUID, template_data: ProjectTemplateCreateDTO, 
                             created_by: str) -> ProjectTemplateResponseDTO:
        """Create a new project template."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, created_by, "manage_templates")
        
        # Create template entity
        template = ProjectTemplate.create(
            business_id=business_id,
            name=template_data.name,
            description=template_data.description,
            project_type=template_data.project_type,
            default_priority=template_data.default_priority,
            estimated_hours=template_data.estimated_hours,
            budget_template=template_data.budget_template,
            default_tags=template_data.default_tags or [],
            checklist_items=template_data.checklist_items or [],
            required_skills=template_data.required_skills or [],
            created_by=created_by
        )
        
        # Save template
        created_template = await self.project_template_repository.create(template)
        
        return self._convert_template_to_response_dto(created_template)
    
    async def get_template(self, template_id: uuid.UUID, user_id: str) -> ProjectTemplateResponseDTO:
        """Get a project template by ID."""
        
        template = await self.project_template_repository.get_by_id(template_id)
        if not template:
            raise NotFoundError("Project template not found")
        
        # Check permission (for business templates)
        if template.business_id:
            await self.project_helper_service.check_permission(template.business_id, user_id, "view_templates")
        
        return self._convert_template_to_response_dto(template)
    
    async def update_template(self, template_id: uuid.UUID, template_data: ProjectTemplateUpdateDTO,
                             user_id: str) -> ProjectTemplateResponseDTO:
        """Update a project template."""
        
        template = await self.project_template_repository.get_by_id(template_id)
        if not template:
            raise NotFoundError("Project template not found")
        
        # Check permission
        if template.business_id:
            await self.project_helper_service.check_permission(template.business_id, user_id, "manage_templates")
        else:
            # System templates can only be updated by system administrators
            raise ValidationError("Cannot update system templates")
        
        # Update template fields
        update_data = {}
        if template_data.name is not None:
            update_data["name"] = template_data.name
        if template_data.description is not None:
            update_data["description"] = template_data.description
        if template_data.project_type is not None:
            update_data["project_type"] = template_data.project_type
        if template_data.default_priority is not None:
            update_data["default_priority"] = template_data.default_priority
        if template_data.estimated_hours is not None:
            update_data["estimated_hours"] = template_data.estimated_hours
        if template_data.budget_template is not None:
            update_data["budget_template"] = template_data.budget_template
        if template_data.default_tags is not None:
            update_data["default_tags"] = template_data.default_tags
        if template_data.checklist_items is not None:
            update_data["checklist_items"] = template_data.checklist_items
        if template_data.required_skills is not None:
            update_data["required_skills"] = template_data.required_skills
        if template_data.is_active is not None:
            update_data["is_active"] = template_data.is_active
        
        # Apply updates
        updated_template = template.model_copy(update=update_data)
        
        # Save updated template
        saved_template = await self.project_template_repository.update(updated_template)
        
        return self._convert_template_to_response_dto(saved_template)
    
    async def delete_template(self, template_id: uuid.UUID, user_id: str) -> bool:
        """Delete a project template."""
        
        template = await self.project_template_repository.get_by_id(template_id)
        if not template:
            raise NotFoundError("Project template not found")
        
        # Check permission
        if template.business_id:
            await self.project_helper_service.check_permission(template.business_id, user_id, "manage_templates")
        else:
            # System templates cannot be deleted
            raise ValidationError("Cannot delete system templates")
        
        return await self.project_template_repository.delete(template_id)
    
    async def list_business_templates(self, business_id: uuid.UUID, user_id: str,
                                     skip: int = 0, limit: int = 100) -> List[ProjectTemplateResponseDTO]:
        """List project templates for a business."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_templates")
        
        templates = await self.project_template_repository.get_by_business_id(business_id, skip, limit)
        
        return [self._convert_template_to_response_dto(template) for template in templates]
    
    async def list_system_templates(self, skip: int = 0, limit: int = 100) -> List[ProjectTemplateResponseDTO]:
        """List system-wide project templates."""
        
        templates = await self.project_template_repository.get_system_templates(skip, limit)
        
        return [self._convert_template_to_response_dto(template) for template in templates]
    
    async def get_templates_by_type(self, project_type: ProjectType, business_id: Optional[uuid.UUID] = None,
                                   user_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[ProjectTemplateResponseDTO]:
        """Get project templates by project type."""
        
        # Check permission if business-specific
        if business_id and user_id:
            await self.project_helper_service.check_permission(business_id, user_id, "view_templates")
        
        templates = await self.project_template_repository.get_by_project_type(
            project_type, business_id, skip, limit
        )
        
        return [self._convert_template_to_response_dto(template) for template in templates]
    
    async def create_project_from_template(self, business_id: uuid.UUID, template_id: uuid.UUID,
                                          project_data: ProjectCreateFromTemplateDTO, 
                                          created_by: str) -> ProjectResponseDTO:
        """Create a new project from a template."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, created_by, "create_projects")
        
        # Get template
        template = await self.project_template_repository.get_by_id(template_id)
        if not template:
            raise NotFoundError("Project template not found")
        
        # Validate template can be used by this business
        if template.business_id and template.business_id != business_id:
            raise ValidationError("Template not available for this business")
        
        # Generate project number
        project_number = project_data.project_number
        if not project_number:
            project_number = await self.project_repository.get_next_project_number(business_id)
        
        # Create project from template
        project = Project.create(
            business_id=business_id,
            project_number=project_number,
            name=project_data.name,
            description=project_data.description or template.description,
            project_type=template.project_type,
            status=project_data.status,
            priority=project_data.priority or template.default_priority,
            contact_id=project_data.contact_id,
            client_name=project_data.client_name,
            client_email=project_data.client_email,
            client_phone=project_data.client_phone,
            address=project_data.address,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            estimated_hours=project_data.estimated_hours or template.estimated_hours,
            budget_amount=project_data.budget_amount or template.budget_template,
            team_members=project_data.team_members or [],
            tags=(project_data.tags or []) + (template.default_tags or []),
            notes=project_data.notes,
            created_by=created_by
        )
        
        # Save project
        created_project = await self.project_repository.create(project)
        
        return await self.project_helper_service.convert_to_response_dto(created_project)
    
    def _convert_template_to_response_dto(self, template: ProjectTemplate) -> ProjectTemplateResponseDTO:
        """Convert ProjectTemplate entity to response DTO."""
        return ProjectTemplateResponseDTO(
            id=template.id,
            business_id=template.business_id,
            name=template.name,
            description=template.description,
            project_type=template.project_type,
            default_priority=template.default_priority,
            estimated_hours=template.estimated_hours,
            budget_template=template.budget_template,
            default_tags=template.default_tags,
            checklist_items=template.checklist_items,
            required_skills=template.required_skills,
            is_active=template.is_active,
            created_by=template.created_by,
            created_date=template.created_date,
            updated_date=template.updated_date
        ) 