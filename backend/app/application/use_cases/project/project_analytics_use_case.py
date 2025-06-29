"""
Project Analytics Use Case

Business logic for project analytics and statistics in Hero365.
Handles project statistics, budget analysis, and reporting operations.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any

from ...dto.project_dto import ProjectStatisticsDTO, ProjectBudgetSummaryDTO
from app.domain.repositories.project_repository import ProjectRepository
from .project_helper_service import ProjectHelperService


class ProjectAnalyticsUseCase:
    """
    Use case for project analytics and statistics within Hero365.
    
    Handles project statistics, budget analysis, performance metrics,
    and reporting operations with proper permission validation.
    """
    
    def __init__(
        self,
        project_repository: ProjectRepository,
        project_helper_service: ProjectHelperService
    ):
        self.project_repository = project_repository
        self.project_helper_service = project_helper_service
    
    async def get_project_statistics(self, business_id: uuid.UUID, user_id: str) -> ProjectStatisticsDTO:
        """Get comprehensive project statistics for a business."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        stats = await self.project_repository.get_project_statistics(business_id)
        
        return ProjectStatisticsDTO(
            total_projects=stats["total_projects"],
            by_status=stats["by_status"],
            by_priority=stats["by_priority"],
            by_type=stats.get("by_type", {}),
            budget_totals=ProjectBudgetSummaryDTO(
                total_budget=stats["budget_totals"]["total_budget"],
                total_actual=stats["budget_totals"]["total_actual"],
                variance=stats["budget_totals"]["variance"],
                project_count=stats["total_projects"]
            )
        )
    
    async def get_budget_summary(self, business_id: uuid.UUID, user_id: str,
                                start_date: datetime, end_date: datetime) -> ProjectBudgetSummaryDTO:
        """Get budget summary for projects within a date range."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        summary = await self.project_repository.get_budget_summary(business_id, start_date, end_date)
        
        return ProjectBudgetSummaryDTO(
            total_budget=summary["total_budget"],
            total_actual=summary["total_actual"],
            variance=summary["variance"],
            project_count=summary["project_count"]
        )
    
    async def get_project_progress_report(self, business_id: uuid.UUID, user_id: str) -> Dict[str, Any]:
        """Get detailed project progress report."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        # Get active projects
        active_projects = await self.project_repository.get_active_projects(business_id)
        overdue_projects = await self.project_repository.get_overdue_projects(business_id)
        
        # Calculate aggregated metrics
        total_active = len(active_projects)
        total_overdue = len(overdue_projects)
        
        # Calculate progress for each project
        project_progress = []
        for project in active_projects:
            progress = self.project_helper_service.calculate_project_progress(project)
            project_progress.append({
                "project_id": str(project.id),
                "project_name": project.name,
                "project_number": project.project_number,
                "progress": progress
            })
        
        return {
            "summary": {
                "total_active_projects": total_active,
                "total_overdue_projects": total_overdue,
                "overdue_percentage": (total_overdue / total_active * 100) if total_active > 0 else 0
            },
            "projects": project_progress,
            "overdue_projects": [
                {
                    "project_id": str(p.id),
                    "project_name": p.name,
                    "project_number": p.project_number,
                    "end_date": p.end_date,
                    "days_overdue": (datetime.now().date() - p.end_date).days if p.end_date else 0
                }
                for p in overdue_projects
            ]
        }
    
    async def get_monthly_project_metrics(self, business_id: uuid.UUID, user_id: str, 
                                         year: int, month: int) -> Dict[str, Any]:
        """Get project metrics for a specific month."""
        
        # Check permission
        await self.project_helper_service.check_permission(business_id, user_id, "view_projects")
        
        # Create date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Get budget summary for the month
        budget_summary = await self.project_repository.get_budget_summary(
            business_id, start_date, end_date
        )
        
        # Get project counts by status
        project_stats = await self.project_repository.get_project_statistics(business_id)
        
        return {
            "month": month,
            "year": year,
            "budget_summary": {
                "total_budget": float(budget_summary["total_budget"]),
                "total_actual": float(budget_summary["total_actual"]),
                "variance": float(budget_summary["variance"]),
                "project_count": budget_summary["project_count"]
            },
            "project_counts": project_stats["by_status"]
        } 