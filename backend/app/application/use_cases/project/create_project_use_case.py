"""
Create Project Use Case

Business logic for project creation operations in Hero365.
Handles new project creation with validation and business rules.
"""

import uuid
from datetime import datetime
import logging

from ...dto.project_dto import ProjectCreateDTO, ProjectResponseDTO
from ...exceptions.application_exceptions import ValidationError
from app.domain.entities.project import Project
from app.domain.value_objects.address import Address
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.contact_repository import ContactRepository
from .project_helper_service import ProjectHelperService

logger = logging.getLogger(__name__)


class CreateProjectUseCase:
    """
    Use case for creating new projects within Hero365.
    
    Handles project creation with proper validation, permission checks,
    and business rule enforcement.
    """
    
    def __init__(
        self,
        project_repository: ProjectRepository,
        contact_repository: ContactRepository,
        project_helper_service: ProjectHelperService
    ):
        self.project_repository = project_repository
        self.contact_repository = contact_repository
        self.project_helper_service = project_helper_service
    
    async def execute(self, business_id: uuid.UUID, project_data: ProjectCreateDTO, 
                     created_by: str) -> ProjectResponseDTO:
        """Create a new project."""
        
        try:
            logger.info(f"Starting project creation for business {business_id} by user {created_by}")
            
            # Verify user has permission to create projects
            logger.info("Checking create_projects permission...")
            await self.project_helper_service.check_permission(business_id, created_by, "create_projects")
            logger.info("Permission check passed")
            
            # Validate contact exists if provided
            if project_data.contact_id:
                logger.info(f"Validating contact {project_data.contact_id}...")
                await self.project_helper_service.validate_contact(business_id, project_data.contact_id)
                logger.info("Contact validation passed")
            
            # Generate project number if not provided
            logger.info("Generating project number...")
            project_number = project_data.project_number
            if not project_number:
                project_number = await self.project_repository.get_next_project_number(business_id)
            else:
                # Check for duplicate project number
                if await self.project_repository.has_duplicate_project_number(business_id, project_number):
                    raise ValidationError(f"Project number '{project_number}' already exists")
            logger.info(f"Project number: {project_number}")
            
            # Validate team members exist in business
            if project_data.team_members:
                logger.info("Validating team members...")
                await self.project_helper_service.validate_assigned_users(business_id, project_data.team_members)
                logger.info("Team members validation passed")
            
            # Convert address DTO to Address value object
            project_address = None
            if project_data.address:
                logger.info("Converting address DTO to Address value object...")
                project_address = Address(
                    street_address=project_data.address.street_address or "",
                    city=project_data.address.city or "",
                    state=project_data.address.state or "",
                    postal_code=project_data.address.postal_code or "",
                    country=project_data.address.country or "US",
                    latitude=project_data.address.latitude,
                    longitude=project_data.address.longitude,
                    access_notes=project_data.address.access_notes,
                    place_id=project_data.address.place_id,
                    formatted_address=project_data.address.formatted_address,
                    address_type=project_data.address.address_type
                )
                logger.info("Address conversion completed")
            
            # Create project entity using Pydantic validation
            logger.info("Creating project entity...")
            project = Project.create_project(
                business_id=business_id,
                name=project_data.name,
                description=project_data.description,
                created_by=created_by,
                client_id=project_data.contact_id or uuid.uuid4(),  # Use contact_id or generate UUID
                client_name=project_data.client_name or "",
                address=project_address,
                project_type=project_data.project_type,
                priority=project_data.priority,
                start_date=project_data.start_date,
                project_number=project_number,
                end_date=project_data.end_date,
                estimated_budget=project_data.budget_amount,
                manager_id=project_data.manager_id,
                team_members=project_data.team_members or [],
                tags=project_data.tags or [],
                notes=project_data.notes
            )
            logger.info("Project entity created")
            
            # Save project
            logger.info("Saving project to repository...")
            created_project = await self.project_repository.create(project)
            logger.info(f"Project saved with ID: {created_project.id}")
            
            # Convert to response DTO
            logger.info("Converting to response DTO...")
            result = await self.project_helper_service.convert_to_response_dto(created_project)
            logger.info("Project creation completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}", exc_info=True)
            raise 