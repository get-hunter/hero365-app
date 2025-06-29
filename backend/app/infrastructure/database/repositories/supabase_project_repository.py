"""
Supabase Project Repository Implementation

Implements project data access operations using Supabase.
Handles all project-related database operations with proper error handling.
"""

import uuid
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from supabase import Client

from app.domain.repositories.project_repository import ProjectRepository, ProjectTemplateRepository
from app.domain.entities.project import Project, ProjectTemplate
from app.domain.enums import ProjectType, ProjectStatus, ProjectPriority
from app.domain.exceptions.domain_exceptions import (
    EntityNotFoundError, DuplicateEntityError, DatabaseError, DomainValidationError
)

logger = logging.getLogger(__name__)


class SupabaseProjectRepository(ProjectRepository):
    """
    Supabase implementation of the Project repository.
    
    Handles all project data access operations using Supabase client.
    """
    
    def __init__(self, client: Client):
        self.client = client
        self.table_name = "projects"
    
    async def create(self, project: Project) -> Project:
        """Create a new project."""
        try:
            project_data = self._project_to_dict(project)
            
            result = self.client.table(self.table_name).insert(project_data).execute()
            
            if not result.data:
                raise DatabaseError("Failed to create project")
            
            logger.info(f"Created project {project.id}")
            return self._dict_to_project(result.data[0])
        
        except Exception as e:
            if "duplicate key" in str(e).lower():
                raise DuplicateEntityError("Project with this name already exists for this business")
            logger.error(f"Failed to create project: {str(e)}")
            raise DatabaseError(f"Failed to create project: {str(e)}")
    
    async def get_by_id(self, project_id: uuid.UUID, business_id: uuid.UUID) -> Optional[Project]:
        """Get project by ID within business context."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("id", str(project_id))
                     .eq("business_id", str(business_id))
                     .execute())
            
            if not result.data:
                return None
            
            return self._dict_to_project(result.data[0])
        
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {str(e)}")
            raise DatabaseError(f"Failed to get project: {str(e)}")
    
    async def get_by_project_number(self, business_id: uuid.UUID, project_number: str) -> Optional[Project]:
        """Get project by project number within a business."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("project_number", project_number)
                     .execute())
            
            if not result.data:
                return None
            
            return self._dict_to_project(result.data[0])
        
        except Exception as e:
            logger.error(f"Failed to get project by number: {str(e)}")
            raise DatabaseError(f"Failed to get project by number: {str(e)}")
    
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get projects by business ID with pagination."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_project(project_data) for project_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get projects by business: {str(e)}")
            raise DatabaseError(f"Failed to get projects by business: {str(e)}")
    
    async def get_by_contact_id(self, contact_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get projects by contact ID with pagination."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("contact_id", str(contact_id))
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_project(project_data) for project_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get projects by contact: {str(e)}")
            raise DatabaseError(f"Failed to get projects by contact: {str(e)}")
    
    async def get_by_status(self, business_id: uuid.UUID, status: ProjectStatus,
                           skip: int = 0, limit: int = 100) -> List[Project]:
        """Get projects by status within a business."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("status", status.value)
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_project(project_data) for project_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get projects by status: {str(e)}")
            raise DatabaseError(f"Failed to get projects by status: {str(e)}")
    
    async def get_by_type(self, business_id: uuid.UUID, project_type: ProjectType,
                         skip: int = 0, limit: int = 100) -> List[Project]:
        """Get projects by type within a business."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("project_type", project_type.value)
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_project(project_data) for project_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get projects by type: {str(e)}")
            raise DatabaseError(f"Failed to get projects by type: {str(e)}")
    
    async def get_by_priority(self, business_id: uuid.UUID, priority: ProjectPriority,
                             skip: int = 0, limit: int = 100) -> List[Project]:
        """Get projects by priority within a business."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("priority", priority.value)
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_project(project_data) for project_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get projects by priority: {str(e)}")
            raise DatabaseError(f"Failed to get projects by priority: {str(e)}")
    
    async def get_active_projects(self, business_id: uuid.UUID,
                                 skip: int = 0, limit: int = 100) -> List[Project]:
        """Get active projects within a business."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .in_("status", [ProjectStatus.PLANNING.value, ProjectStatus.ACTIVE.value])
                     .order("priority", desc=True)
                     .order("start_date", desc=False)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_project(project_data) for project_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get active projects: {str(e)}")
            raise DatabaseError(f"Failed to get active projects: {str(e)}")
    
    async def get_overdue_projects(self, business_id: uuid.UUID,
                                  skip: int = 0, limit: int = 100) -> List[Project]:
        """Get overdue projects within a business."""
        try:
            today = datetime.now().date()
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .in_("status", [ProjectStatus.PLANNING.value, ProjectStatus.ACTIVE.value])
                     .lt("end_date", today.isoformat())
                     .order("end_date", desc=False)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_project(project_data) for project_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get overdue projects: {str(e)}")
            raise DatabaseError(f"Failed to get overdue projects: {str(e)}")
    
    async def get_projects_by_tag(self, business_id: uuid.UUID, tag: str,
                                 skip: int = 0, limit: int = 100) -> List[Project]:
        """Get projects by tag within a business."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .contains("tags", [tag])
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_project(project_data) for project_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get projects by tag: {str(e)}")
            raise DatabaseError(f"Failed to get projects by tag: {str(e)}")
    
    async def search_projects(self, business_id: uuid.UUID, search_term: str,
                             skip: int = 0, limit: int = 100) -> List[Project]:
        """Search projects by name, description, or tags within a business."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .or_(
                         f"name.ilike.%{search_term}%,"
                         f"description.ilike.%{search_term}%,"
                         f"client_name.ilike.%{search_term}%"
                     )
                     .order("created_date", desc=True)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_project(project_data) for project_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to search projects: {str(e)}")
            raise DatabaseError(f"Failed to search projects: {str(e)}")
    
    async def get_budget_summary(self, business_id: uuid.UUID, 
                                start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get budget summary for projects within a date range."""
        try:
            result = (self.client.table(self.table_name)
                     .select("budget_amount, actual_cost, status")
                     .eq("business_id", str(business_id))
                     .gte("start_date", start_date.date().isoformat())
                     .lte("end_date", end_date.date().isoformat())
                     .execute())
            
            if not result.data:
                return {
                    "total_budget": Decimal("0.00"),
                    "total_actual": Decimal("0.00"),
                    "variance": Decimal("0.00"),
                    "project_count": 0
                }
            
            total_budget = sum(Decimal(str(p.get("budget_amount", 0))) for p in result.data)
            total_actual = sum(Decimal(str(p.get("actual_cost", 0))) for p in result.data)
            
            return {
                "total_budget": total_budget,
                "total_actual": total_actual,
                "variance": total_budget - total_actual,
                "project_count": len(result.data)
            }
        
        except Exception as e:
            logger.error(f"Failed to get budget summary: {str(e)}")
            raise DatabaseError(f"Failed to get budget summary: {str(e)}")
    
    async def update(self, project: Project) -> Project:
        """Update an existing project."""
        try:
            project_data = self._project_to_dict(project)
            project_data["updated_date"] = datetime.now().isoformat()
            
            result = (self.client.table(self.table_name)
                     .update(project_data)
                     .eq("id", str(project.id))
                     .execute())
            
            if not result.data:
                raise EntityNotFoundError(f"Project {project.id} not found")
            
            logger.info(f"Updated project {project.id}")
            return self._dict_to_project(result.data[0])
        
        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update project {project.id}: {str(e)}")
            raise DatabaseError(f"Failed to update project: {str(e)}")
    
    async def delete(self, project_id: uuid.UUID, business_id: uuid.UUID) -> bool:
        """Delete a project by ID within business context."""
        try:
            result = (self.client.table(self.table_name)
                     .delete()
                     .eq("id", str(project_id))
                     .eq("business_id", str(business_id))
                     .execute())
            
            success = result.data is not None and len(result.data) > 0
            if success:
                logger.info(f"Deleted project {project_id}")
            
            return success
        
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete project: {str(e)}")
    
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Count projects in a business."""
        try:
            result = (self.client.table(self.table_name)
                     .select("id", count="exact")
                     .eq("business_id", str(business_id))
                     .execute())
            
            return result.count or 0
        
        except Exception as e:
            logger.error(f"Failed to count projects: {str(e)}")
            raise DatabaseError(f"Failed to count projects: {str(e)}")
    
    async def count_by_status(self, business_id: uuid.UUID, status: ProjectStatus) -> int:
        """Count projects by status within a business."""
        try:
            result = (self.client.table(self.table_name)
                     .select("id", count="exact")
                     .eq("business_id", str(business_id))
                     .eq("status", status.value)
                     .execute())
            
            return result.count or 0
        
        except Exception as e:
            logger.error(f"Failed to count projects by status: {str(e)}")
            raise DatabaseError(f"Failed to count projects by status: {str(e)}")
    
    async def exists(self, project_id: uuid.UUID, business_id: uuid.UUID) -> bool:
        """Check if a project exists within business context."""
        try:
            result = (self.client.table(self.table_name)
                     .select("id")
                     .eq("id", str(project_id))
                     .eq("business_id", str(business_id))
                     .execute())
            
            return len(result.data) > 0
        
        except Exception as e:
            logger.error(f"Failed to check project existence: {str(e)}")
            raise DatabaseError(f"Failed to check project existence: {str(e)}")
    
    async def has_duplicate_project_number(self, business_id: uuid.UUID, project_number: str,
                                          exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if project number is unique within a business."""
        try:
            query = (self.client.table(self.table_name)
                    .select("id")
                    .eq("business_id", str(business_id))
                    .eq("project_number", project_number))
            
            if exclude_id:
                query = query.neq("id", str(exclude_id))
            
            result = query.execute()
            return len(result.data) > 0
        
        except Exception as e:
            logger.error(f"Failed to check project number uniqueness: {str(e)}")
            raise DatabaseError(f"Failed to check project number uniqueness: {str(e)}")
    
    async def get_next_project_number(self, business_id: uuid.UUID, prefix: str = "PROJ") -> str:
        """Generate the next project number for a business."""
        try:
            result = (self.client.table(self.table_name)
                     .select("project_number")
                     .eq("business_id", str(business_id))
                     .like("project_number", f"{prefix}%")
                     .order("project_number", desc=True)
                     .limit(1)
                     .execute())
            
            if not result.data:
                return f"{prefix}-001"
            
            last_number = result.data[0]["project_number"]
            try:
                # Extract number part and increment
                number_part = int(last_number.split('-')[-1])
                return f"{prefix}-{(number_part + 1):03d}"
            except (ValueError, IndexError):
                # Fallback if parsing fails
                return f"{prefix}-001"
        
        except Exception as e:
            logger.error(f"Failed to generate project number: {str(e)}")
            raise DatabaseError(f"Failed to generate project number: {str(e)}")
    
    async def get_project_statistics(self, business_id: uuid.UUID) -> Dict[str, Any]:
        """Get project statistics for a business."""
        try:
            result = (self.client.table(self.table_name)
                     .select("status, priority, budget_amount, actual_cost")
                     .eq("business_id", str(business_id))
                     .execute())
            
            if not result.data:
                return {
                    "total_projects": 0,
                    "by_status": {},
                    "by_priority": {},
                    "budget_totals": {
                        "total_budget": Decimal("0.00"),
                        "total_actual": Decimal("0.00"),
                        "variance": Decimal("0.00")
                    }
                }
            
            stats = {
                "total_projects": len(result.data),
                "by_status": {},
                "by_priority": {},
                "budget_totals": {
                    "total_budget": Decimal("0.00"),
                    "total_actual": Decimal("0.00"),
                    "variance": Decimal("0.00")
                }
            }
            
            # Count by status and priority
            for project in result.data:
                status = project.get("status", "unknown")
                priority = project.get("priority", "unknown")
                
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
                
                # Budget calculations
                budget = Decimal(str(project.get("budget_amount", 0)))
                actual = Decimal(str(project.get("actual_cost", 0)))
                
                stats["budget_totals"]["total_budget"] += budget
                stats["budget_totals"]["total_actual"] += actual
            
            stats["budget_totals"]["variance"] = (
                stats["budget_totals"]["total_budget"] - stats["budget_totals"]["total_actual"]
            )
            
            return stats
        
        except Exception as e:
            logger.error(f"Failed to get project statistics: {str(e)}")
            raise DatabaseError(f"Failed to get project statistics: {str(e)}")
    
    # Abstract method implementations required by the interface
    
    async def get_by_business(
        self,
        business_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProjectStatus] = None,
        project_type: Optional[ProjectType] = None,
        priority: Optional[ProjectPriority] = None,
        client_id: Optional[uuid.UUID] = None,
        manager_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Project], int]:
        """Get projects by business with filtering, pagination and search."""
        try:
            # Build query with filters
            query = self.client.table(self.table_name).select("*", count="exact")
            query = query.eq("business_id", str(business_id))
            
            if status:
                query = query.eq("status", status.value)
            if project_type:
                query = query.eq("project_type", project_type.value)
            if priority:
                query = query.eq("priority", priority.value)
            if client_id:
                query = query.eq("contact_id", str(client_id))
            if manager_id:
                query = query.contains("team_members", [str(manager_id)])
            if search:
                query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%,project_number.ilike.%{search}%")
            
            # Add sorting
            if sort_by:
                desc = sort_order.lower() == "desc"
                query = query.order(sort_by, desc=desc)
            else:
                query = query.order("created_date", desc=True)
            
            # Add pagination
            query = query.range(skip, skip + limit - 1)
            
            result = query.execute()
            
            projects = [self._dict_to_project(project_data) for project_data in result.data]
            total_count = result.count or 0
            
            return projects, total_count
            
        except Exception as e:
            logger.error(f"Failed to get projects with filters: {str(e)}")
            raise DatabaseError(f"Failed to get projects with filters: {str(e)}")
    
    async def get_by_client(self, client_id: uuid.UUID, business_id: uuid.UUID) -> List[Project]:
        """Get all projects for a specific client."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("contact_id", str(client_id))
                     .order("created_date", desc=True)
                     .execute())
            
            return [self._dict_to_project(project_data) for project_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get projects by client: {str(e)}")
            raise DatabaseError(f"Failed to get projects by client: {str(e)}")
    
    async def get_by_manager(self, manager_id: uuid.UUID, business_id: uuid.UUID) -> List[Project]:
        """Get all projects managed by a specific user."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .contains("team_members", [str(manager_id)])
                     .order("created_date", desc=True)
                     .execute())
            
            return [self._dict_to_project(project_data) for project_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get projects by manager: {str(e)}")
            raise DatabaseError(f"Failed to get projects by manager: {str(e)}")
    
    async def get_project_analytics(
        self,
        business_id: uuid.UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[ProjectStatus] = None,
        project_type: Optional[ProjectType] = None
    ) -> Dict[str, Any]:
        """Get project analytics data for a business."""
        try:
            # Build query with filters
            query = self.client.table(self.table_name).select("*")
            query = query.eq("business_id", str(business_id))
            
            if date_from:
                query = query.gte("created_date", date_from.isoformat())
            if date_to:
                query = query.lte("created_date", date_to.isoformat())
            if status:
                query = query.eq("status", status.value)
            if project_type:
                query = query.eq("project_type", project_type.value)
            
            result = query.execute()
            
            if not result.data:
                return {
                    "total_projects": 0,
                    "by_status": {},
                    "by_priority": {},
                    "by_type": {},
                    "budget_totals": {
                        "total_budget": Decimal("0.00"),
                        "total_actual": Decimal("0.00"),
                        "variance": Decimal("0.00")
                    },
                    "overdue_count": 0,
                    "active_count": 0
                }
            
            analytics = {
                "total_projects": len(result.data),
                "by_status": {},
                "by_priority": {},
                "by_type": {},
                "budget_totals": {
                    "total_budget": Decimal("0.00"),
                    "total_actual": Decimal("0.00"),
                    "variance": Decimal("0.00")
                },
                "overdue_count": 0,
                "active_count": 0
            }
            
            today = datetime.now().date()
            
            # Analyze projects
            for project_data in result.data:
                status_val = project_data.get("status", "unknown")
                priority_val = project_data.get("priority", "unknown")
                type_val = project_data.get("project_type", "unknown")
                
                analytics["by_status"][status_val] = analytics["by_status"].get(status_val, 0) + 1
                analytics["by_priority"][priority_val] = analytics["by_priority"].get(priority_val, 0) + 1
                analytics["by_type"][type_val] = analytics["by_type"].get(type_val, 0) + 1
                
                # Budget calculations
                budget = Decimal(str(project_data.get("budget_amount", 0)))
                actual = Decimal(str(project_data.get("actual_cost", 0)))
                
                analytics["budget_totals"]["total_budget"] += budget
                analytics["budget_totals"]["total_actual"] += actual
                
                # Count overdue and active projects
                if project_data.get("end_date"):
                    end_date = datetime.fromisoformat(project_data["end_date"]).date()
                    if end_date < today and status_val in ["planning", "active"]:
                        analytics["overdue_count"] += 1
                
                if status_val in ["planning", "active"]:
                    analytics["active_count"] += 1
            
            analytics["budget_totals"]["variance"] = (
                analytics["budget_totals"]["total_budget"] - analytics["budget_totals"]["total_actual"]
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get project analytics: {str(e)}")
            raise DatabaseError(f"Failed to get project analytics: {str(e)}")
    
    def _project_to_dict(self, project: Project) -> Dict[str, Any]:
        """Convert Project entity to dictionary for database storage."""
        return {
            "id": str(project.id),
            "business_id": str(project.business_id),
            "project_number": project.project_number,
            "name": project.name,
            "description": project.description,
            "project_type": project.project_type.value,
            "status": project.status.value,
            "priority": project.priority.value,
            "contact_id": str(project.contact_id) if project.contact_id else None,
            "client_name": project.client_name,
            "client_email": project.client_email,
            "client_phone": project.client_phone,
            "address": project.address.model_dump() if project.address else None,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "end_date": project.end_date.isoformat() if project.end_date else None,
            "estimated_hours": float(project.estimated_hours) if project.estimated_hours else None,
            "actual_hours": float(project.actual_hours) if project.actual_hours else None,
            "budget_amount": float(project.budget_amount) if project.budget_amount else None,
            "actual_cost": float(project.actual_cost) if project.actual_cost else None,
            "team_members": project.team_members,
            "tags": project.tags,
            "notes": project.notes,
            "created_by": project.created_by,
            "created_date": project.created_date.isoformat(),
            "updated_date": project.updated_date.isoformat() if project.updated_date else None
        }
    
    def _dict_to_project(self, data: Dict[str, Any]) -> Project:
        """Convert database dictionary to Project entity."""
        from app.domain.value_objects.address import Address
        
        # Handle address conversion
        address = None
        if data.get("address"):
            if isinstance(data["address"], dict):
                address = Address(**data["address"])
            elif isinstance(data["address"], str):
                address_data = json.loads(data["address"])
                address = Address(**address_data)
        
        return Project(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]),
            project_number=data["project_number"],
            name=data["name"],
            description=data.get("description"),
            project_type=ProjectType(data["project_type"]),
            status=ProjectStatus(data["status"]),
            priority=ProjectPriority(data["priority"]),
            contact_id=uuid.UUID(data["contact_id"]) if data.get("contact_id") else None,
            client_name=data.get("client_name"),
            client_email=data.get("client_email"),
            client_phone=data.get("client_phone"),
            address=address,
            start_date=datetime.fromisoformat(data["start_date"]).date() if data.get("start_date") else None,
            end_date=datetime.fromisoformat(data["end_date"]).date() if data.get("end_date") else None,
            estimated_hours=Decimal(str(data["estimated_hours"])) if data.get("estimated_hours") else None,
            actual_hours=Decimal(str(data["actual_hours"])) if data.get("actual_hours") else None,
            budget_amount=Decimal(str(data["budget_amount"])) if data.get("budget_amount") else None,
            actual_cost=Decimal(str(data["actual_cost"])) if data.get("actual_cost") else None,
            team_members=data.get("team_members", []),
            tags=data.get("tags", []),
            notes=data.get("notes"),
            created_by=data["created_by"],
            created_date=datetime.fromisoformat(data["created_date"]),
            updated_date=datetime.fromisoformat(data["updated_date"]) if data.get("updated_date") else None
        )


class SupabaseProjectTemplateRepository(ProjectTemplateRepository):
    """
    Supabase implementation of the Project Template repository.
    
    Handles all project template data access operations using Supabase client.
    """
    
    def __init__(self, client: Client):
        self.client = client
        self.table_name = "project_templates"
    
    async def create(self, template: ProjectTemplate) -> ProjectTemplate:
        """Create a new project template."""
        try:
            template_data = self._template_to_dict(template)
            
            result = self.client.table(self.table_name).insert(template_data).execute()
            
            if not result.data:
                raise DatabaseError("Failed to create project template")
            
            logger.info(f"Created project template {template.id}")
            return self._dict_to_template(result.data[0])
        
        except Exception as e:
            if "duplicate key" in str(e).lower():
                raise DuplicateEntityError("Project template with this name already exists")
            logger.error(f"Failed to create project template: {str(e)}")
            raise DatabaseError(f"Failed to create project template: {str(e)}")
    
    async def get_by_id(self, template_id: uuid.UUID, business_id: Optional[uuid.UUID] = None) -> Optional[ProjectTemplate]:
        """Get a template by ID. If business_id is None, only system templates are considered."""
        try:
            query = self.client.table(self.table_name).select("*").eq("id", str(template_id))
            
            if business_id is not None:
                # Allow both business templates and system templates for this business
                query = query.or_(f"business_id.eq.{str(business_id)},business_id.is.null")
            else:
                # Only system templates
                query = query.is_("business_id", "null")
            
            result = query.execute()
            
            if not result.data:
                return None
            
            return self._dict_to_template(result.data[0])
        
        except Exception as e:
            logger.error(f"Failed to get project template {template_id}: {str(e)}")
            raise DatabaseError(f"Failed to get project template: {str(e)}")
    
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[ProjectTemplate]:
        """Get project templates by business ID with pagination."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .eq("business_id", str(business_id))
                     .eq("is_active", True)
                     .order("name", desc=False)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_template(template_data) for template_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get project templates by business: {str(e)}")
            raise DatabaseError(f"Failed to get project templates by business: {str(e)}")
    
    async def get_system_templates(self, skip: int = 0, limit: int = 100) -> List[ProjectTemplate]:
        """Get system-wide project templates."""
        try:
            result = (self.client.table(self.table_name)
                     .select("*")
                     .is_("business_id", "null")
                     .eq("is_active", True)
                     .order("name", desc=False)
                     .range(skip, skip + limit - 1)
                     .execute())
            
            return [self._dict_to_template(template_data) for template_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get system project templates: {str(e)}")
            raise DatabaseError(f"Failed to get system project templates: {str(e)}")
    
    async def get_by_project_type(self, project_type: ProjectType, business_id: Optional[uuid.UUID] = None,
                                 skip: int = 0, limit: int = 100) -> List[ProjectTemplate]:
        """Get project templates by project type."""
        try:
            query = (self.client.table(self.table_name)
                    .select("*")
                    .eq("project_type", project_type.value)
                    .eq("is_active", True))
            
            if business_id:
                query = query.or_(f"business_id.eq.{str(business_id)},business_id.is.null")
            else:
                query = query.is_("business_id", "null")
            
            result = query.order("name", desc=False).range(skip, skip + limit - 1).execute()
            
            return [self._dict_to_template(template_data) for template_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get project templates by type: {str(e)}")
            raise DatabaseError(f"Failed to get project templates by type: {str(e)}")
    
    async def update(self, template: ProjectTemplate) -> ProjectTemplate:
        """Update an existing project template."""
        try:
            template_data = self._template_to_dict(template)
            template_data["updated_date"] = datetime.now().isoformat()
            
            result = (self.client.table(self.table_name)
                     .update(template_data)
                     .eq("id", str(template.id))
                     .execute())
            
            if not result.data:
                raise EntityNotFoundError(f"Project template {template.id} not found")
            
            logger.info(f"Updated project template {template.id}")
            return self._dict_to_template(result.data[0])
        
        except EntityNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update project template {template.id}: {str(e)}")
            raise DatabaseError(f"Failed to update project template: {str(e)}")
    
    async def delete(self, template_id: uuid.UUID, business_id: uuid.UUID) -> bool:
        """Delete a business template by ID."""
        try:
            result = (self.client.table(self.table_name)
                     .delete()
                     .eq("id", str(template_id))
                     .eq("business_id", str(business_id))
                     .execute())
            
            success = result.data is not None and len(result.data) > 0
            if success:
                logger.info(f"Deleted project template {template_id}")
            
            return success
        
        except Exception as e:
            logger.error(f"Failed to delete project template {template_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete project template: {str(e)}")
    
    async def exists(self, template_id: uuid.UUID, business_id: Optional[uuid.UUID] = None) -> bool:
        """Check if a template exists and is accessible by the business."""
        try:
            query = self.client.table(self.table_name).select("id").eq("id", str(template_id))
            
            if business_id is not None:
                # Allow both business templates and system templates for this business
                query = query.or_(f"business_id.eq.{str(business_id)},business_id.is.null")
            else:
                # Only system templates
                query = query.is_("business_id", "null")
            
            result = query.execute()
            
            return len(result.data) > 0
        
        except Exception as e:
            logger.error(f"Failed to check project template existence: {str(e)}")
            raise DatabaseError(f"Failed to check project template existence: {str(e)}")
    
    # Abstract method implementations required by the interface
    
    async def get_by_business(
        self,
        business_id: uuid.UUID,
        include_system: bool = True,
        project_type: Optional[ProjectType] = None
    ) -> List[ProjectTemplate]:
        """Get templates accessible by a business (business templates + system templates)."""
        try:
            # Build query for business templates
            business_query = (self.client.table(self.table_name)
                             .select("*")
                             .eq("business_id", str(business_id))
                             .eq("is_active", True))
            
            if project_type:
                business_query = business_query.eq("project_type", project_type.value)
            
            business_result = business_query.execute()
            templates = [self._dict_to_template(template_data) for template_data in business_result.data]
            
            # Add system templates if requested
            if include_system:
                system_query = (self.client.table(self.table_name)
                               .select("*")
                               .is_("business_id", "null")
                               .eq("is_active", True))
                
                if project_type:
                    system_query = system_query.eq("project_type", project_type.value)
                
                system_result = system_query.execute()
                system_templates = [self._dict_to_template(template_data) for template_data in system_result.data]
                templates.extend(system_templates)
            
            # Sort by name
            templates.sort(key=lambda t: t.name)
            
            return templates
        
        except Exception as e:
            logger.error(f"Failed to get templates by business: {str(e)}")
            raise DatabaseError(f"Failed to get templates by business: {str(e)}")
    
    async def get_business_templates(
        self,
        business_id: uuid.UUID,
        project_type: Optional[ProjectType] = None
    ) -> List[ProjectTemplate]:
        """Get templates created by a specific business."""
        try:
            query = (self.client.table(self.table_name)
                    .select("*")
                    .eq("business_id", str(business_id))
                    .eq("is_active", True))
            
            if project_type:
                query = query.eq("project_type", project_type.value)
            
            result = query.order("name", desc=False).execute()
            
            return [self._dict_to_template(template_data) for template_data in result.data]
        
        except Exception as e:
            logger.error(f"Failed to get business templates: {str(e)}")
            raise DatabaseError(f"Failed to get business templates: {str(e)}")
    
    def _template_to_dict(self, template: ProjectTemplate) -> Dict[str, Any]:
        """Convert ProjectTemplate entity to dictionary for database storage."""
        return {
            "id": str(template.id),
            "business_id": str(template.business_id) if template.business_id else None,
            "name": template.name,
            "description": template.description,
            "project_type": template.project_type.value,
            "default_priority": template.default_priority.value,
            "estimated_hours": float(template.estimated_hours) if template.estimated_hours else None,
            "budget_template": float(template.budget_template) if template.budget_template else None,
            "default_tags": template.default_tags,
            "checklist_items": template.checklist_items,
            "required_skills": template.required_skills,
            "is_active": template.is_active,
            "created_by": template.created_by,
            "created_date": template.created_date.isoformat(),
            "updated_date": template.updated_date.isoformat() if template.updated_date else None
        }
    
    def _dict_to_template(self, data: Dict[str, Any]) -> ProjectTemplate:
        """Convert database dictionary to ProjectTemplate entity."""
        return ProjectTemplate(
            id=uuid.UUID(data["id"]),
            business_id=uuid.UUID(data["business_id"]) if data.get("business_id") else None,
            name=data["name"],
            description=data.get("description"),
            project_type=ProjectType(data["project_type"]),
            default_priority=ProjectPriority(data["default_priority"]),
            estimated_hours=Decimal(str(data["estimated_hours"])) if data.get("estimated_hours") else None,
            budget_template=Decimal(str(data["budget_template"])) if data.get("budget_template") else None,
            default_tags=data.get("default_tags", []),
            checklist_items=data.get("checklist_items", []),
            required_skills=data.get("required_skills", []),
            is_active=data.get("is_active", True),
            created_by=data["created_by"],
            created_date=datetime.fromisoformat(data["created_date"]),
            updated_date=datetime.fromisoformat(data["updated_date"]) if data.get("updated_date") else None
        ) 