"""
Project Helper Service

Common utilities and validation logic for project use cases.
Provides shared functionality across all project-related operations.
"""

import uuid
from typing import List, Dict, Any

from ...dto.project_dto import ProjectResponseDTO, ProjectListDTO
from ...exceptions.application_exceptions import ValidationError, PermissionDeniedError, NotFoundError
from app.domain.entities.project import Project
from app.domain.repositories.business_membership_repository import BusinessMembershipRepository
from app.domain.repositories.contact_repository import ContactRepository


class ProjectHelperService:
    """
    Helper service providing common functionality for project use cases.
    
    Handles permission checks, user validation, and data transformations
    shared across multiple project operations.
    """
    
    def __init__(
        self,
        business_membership_repository: BusinessMembershipRepository,
        contact_repository: ContactRepository
    ):
        self.business_membership_repository = business_membership_repository
        self.contact_repository = contact_repository
    
    async def check_permission(self, business_id: uuid.UUID, user_id: str, permission: str) -> None:
        """Check if user has the required permission for a business."""
        membership = await self.business_membership_repository.get_by_user_and_business(
            user_id, business_id
        )
        
        if not membership:
            raise PermissionDeniedError("User is not a member of this business")
        
        if not membership.is_active:
            raise PermissionDeniedError("User membership is not active")
        
        # Check if user has the required permission
        if not membership.has_permission(permission):
            raise PermissionDeniedError(f"User does not have permission: {permission}")
    
    async def validate_assigned_users(self, business_id: uuid.UUID, user_ids: List[str]) -> None:
        """Validate that all users are members of the business."""
        for user_id in user_ids:
            membership = await self.business_membership_repository.get_by_user_and_business(
                user_id, business_id
            )
            if not membership or not membership.is_active:
                raise ValidationError(f"User {user_id} is not an active member of this business")
    
    async def validate_contact(self, business_id: uuid.UUID, contact_id: uuid.UUID) -> None:
        """Validate that contact exists and belongs to the business."""
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise ValidationError("Contact not found")
        
        if str(contact.business_id) != str(business_id):
            raise ValidationError("Contact does not belong to this business")
    
    async def convert_to_response_dto(self, project: Project) -> ProjectResponseDTO:
        """Convert Project entity to response DTO."""
        return ProjectResponseDTO(
            id=project.id,
            business_id=project.business_id,
            project_number=project.project_number,
            name=project.name,
            description=project.description,
            project_type=project.project_type,
            status=project.status,
            priority=project.priority,
            contact_id=project.contact_id,
            client_name=project.client_name,
            client_email=project.client_email,
            client_phone=project.client_phone,
            address=project.address,
            start_date=project.start_date,
            end_date=project.end_date,
            estimated_hours=project.estimated_hours,
            actual_hours=project.actual_hours,
            budget_amount=project.budget_amount,
            actual_cost=project.actual_cost,
            team_members=project.team_members,
            tags=project.tags,
            notes=project.notes,
            created_by=project.created_by,
            created_date=project.created_date,
            updated_date=project.updated_date
        )
    
    async def convert_to_list_dto(self, project: Project) -> ProjectListDTO:
        """Convert Project entity to list DTO (optimized for lists)."""
        return ProjectListDTO(
            id=project.id,
            business_id=project.business_id,
            project_number=project.project_number,
            name=project.name,
            description=project.description,
            project_type=project.project_type,
            status=project.status,
            priority=project.priority,
            client_name=project.client_name,
            start_date=project.start_date,
            end_date=project.end_date,
            budget_amount=project.budget_amount,
            actual_cost=project.actual_cost,
            team_members=project.team_members,
            tags=project.tags,
            created_date=project.created_date
        )
    
    def calculate_project_progress(self, project: Project) -> Dict[str, Any]:
        """Calculate project progress metrics."""
        progress = {
            "completion_percentage": 0.0,
            "budget_utilization": 0.0,
            "time_utilization": 0.0,
            "is_overdue": False,
            "is_over_budget": False
        }
        
        # Calculate completion percentage based on status
        status_completion_map = {
            "planning": 10.0,
            "active": 50.0,
            "on_hold": 50.0,
            "completed": 100.0,
            "cancelled": 0.0
        }
        progress["completion_percentage"] = status_completion_map.get(project.status.value, 0.0)
        
        # Calculate budget utilization
        if project.budget_amount and project.budget_amount > 0:
            progress["budget_utilization"] = float(
                (project.actual_cost or 0) / project.budget_amount * 100
            )
            progress["is_over_budget"] = progress["budget_utilization"] > 100
        
        # Calculate time utilization
        if project.estimated_hours and project.estimated_hours > 0:
            progress["time_utilization"] = float(
                (project.actual_hours or 0) / project.estimated_hours * 100
            )
        
        # Check if overdue
        if project.end_date:
            from datetime import date
            progress["is_overdue"] = (
                project.end_date < date.today() and 
                project.status.value not in ["completed", "cancelled"]
            )
        
        return progress 