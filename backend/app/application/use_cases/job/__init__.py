"""
Job Use Cases Module

This module contains all job-related use cases following clean architecture principles.
Each use case handles a specific aspect of job management operations.
"""

# Individual CRUD use cases
from .create_job_use_case import CreateJobUseCase
from .get_job_use_case import GetJobUseCase
from .update_job_use_case import UpdateJobUseCase
from .delete_job_use_case import DeleteJobUseCase

# Other specialized use cases
from .job_status_management_use_case import JobStatusManagementUseCase
from .job_assignment_use_case import JobAssignmentUseCase
from .job_search_use_case import JobSearchUseCase
from .job_analytics_use_case import JobAnalyticsUseCase
from .job_scheduling_use_case import JobSchedulingUseCase
from .job_bulk_operations_use_case import JobBulkOperationsUseCase

# Helper service
from .job_helper_service import JobHelperService

# Keep the original combined use cases for backward compatibility during transition
from .job_crud_use_case import JobCRUDUseCase
from .manage_jobs import ManageJobsUseCase

__all__ = [
    # Individual CRUD use cases
    "CreateJobUseCase",
    "GetJobUseCase",
    "UpdateJobUseCase",
    "DeleteJobUseCase",
    
    # Specialized use cases
    "JobStatusManagementUseCase", 
    "JobAssignmentUseCase",
    "JobSearchUseCase",
    "JobAnalyticsUseCase",
    "JobSchedulingUseCase",
    "JobBulkOperationsUseCase",
    
    # Helper service
    "JobHelperService",
    
    # For backward compatibility
    "JobCRUDUseCase",
    "ManageJobsUseCase",
] 