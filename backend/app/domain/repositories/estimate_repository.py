"""
Estimate Repository Interface

Defines the contract for estimate data access operations.
Follows the Repository pattern for clean architecture.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal

from ..entities.estimate import Estimate
from ..enums import EstimateStatus, CurrencyCode


class EstimateQueryBuilder:
    """
    Query builder for flexible estimate filtering and sorting.
    
    Provides a fluent interface for building complex queries without
    method explosion in the repository interface.
    """
    
    def __init__(self):
        self.filters = {}
        self.sort_by = "created_date"
        self.sort_desc = True
        self.skip = 0
        self.limit = 100
    
    def filter_by_status(self, status: EstimateStatus) -> "EstimateQueryBuilder":
        """Filter by single status."""
        self.filters["status"] = status
        return self
    
    def filter_by_statuses(self, statuses: List[EstimateStatus]) -> "EstimateQueryBuilder":
        """Filter by multiple statuses."""
        self.filters["status_list"] = statuses
        return self
    
    def filter_by_contact(self, contact_id: uuid.UUID) -> "EstimateQueryBuilder":
        """Filter by contact ID."""
        self.filters["contact_id"] = contact_id
        return self
    
    def filter_by_project(self, project_id: uuid.UUID) -> "EstimateQueryBuilder":
        """Filter by project ID."""
        self.filters["project_id"] = project_id
        return self
    
    def filter_by_job(self, job_id: uuid.UUID) -> "EstimateQueryBuilder":
        """Filter by job ID."""
        self.filters["job_id"] = job_id
        return self
    
    def filter_by_date_range(self, date_from: datetime, date_to: datetime) -> "EstimateQueryBuilder":
        """Filter by date range."""
        self.filters["date_from"] = date_from
        self.filters["date_to"] = date_to
        return self
    
    def filter_by_value_range(self, min_value: Decimal, max_value: Decimal) -> "EstimateQueryBuilder":
        """Filter by value range."""
        self.filters["min_value"] = min_value
        self.filters["max_value"] = max_value
        return self
    
    def filter_by_currency(self, currency: CurrencyCode) -> "EstimateQueryBuilder":
        """Filter by currency."""
        self.filters["currency"] = currency
        return self
    
    def filter_expired(self, is_expired: bool = True) -> "EstimateQueryBuilder":
        """Filter expired estimates."""
        self.filters["is_expired"] = is_expired
        return self
    
    def filter_expiring_soon(self, days: int = 7) -> "EstimateQueryBuilder":
        """Filter estimates expiring soon."""
        self.filters["is_expiring_soon"] = True
        self.filters["expiring_days"] = days
        return self
    
    def filter_pending_approval(self) -> "EstimateQueryBuilder":
        """Filter estimates pending approval (sent/viewed but not approved/rejected)."""
        self.filters["status_list"] = [EstimateStatus.SENT, EstimateStatus.VIEWED]
        return self
    
    def filter_by_template(self, template_id: uuid.UUID) -> "EstimateQueryBuilder":
        """Filter by template ID."""
        self.filters["template_id"] = template_id
        return self
    
    def search(self, search_term: str) -> "EstimateQueryBuilder":
        """Search across title, description, and estimate number."""
        self.filters["search_term"] = search_term
        return self
    
    def filter_by_tags(self, tags: List[str]) -> "EstimateQueryBuilder":
        """Filter by tags."""
        self.filters["tags"] = tags
        return self
    
    def sort_by_field(self, field: str, descending: bool = True) -> "EstimateQueryBuilder":
        """Sort by specific field."""
        valid_fields = [
            "created_date", "last_modified", "title", "status", 
            "total_amount", "client_name", "estimate_number"
        ]
        if field not in valid_fields:
            raise ValueError(f"Invalid sort field: {field}. Valid fields: {valid_fields}")
        
        self.sort_by = field
        self.sort_desc = descending
        return self
    
    def paginate(self, skip: int, limit: int) -> "EstimateQueryBuilder":
        """Set pagination parameters."""
        if skip < 0:
            raise ValueError("Skip must be non-negative")
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")
        
        self.skip = skip
        self.limit = limit
        return self
    
    def build_filters(self) -> Dict[str, Any]:
        """Build filters dictionary for repository."""
        return self.filters.copy()
    
    def build_sort(self) -> Tuple[str, bool]:
        """Build sort parameters."""
        return self.sort_by, self.sort_desc
    
    def build_pagination(self) -> Tuple[int, int]:
        """Build pagination parameters."""
        return self.skip, self.limit


class EstimateRepository(ABC):
    """
    Abstract repository interface for estimate data access operations.
    
    Simplified interface using flexible filtering instead of method explosion.
    """
    
    # Core CRUD Operations
    @abstractmethod
    async def create(self, estimate: Estimate) -> Estimate:
        """
        Create a new estimate.
        
        Args:
            estimate: Estimate entity to create
            
        Returns:
            Created Estimate entity with generated ID
            
        Raises:
            DatabaseError: If creation fails
            ValidationError: If estimate data is invalid
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, estimate_id: uuid.UUID) -> Optional[Estimate]:
        """
        Get estimate by ID.
        
        Args:
            estimate_id: ID of the estimate
            
        Returns:
            Estimate entity or None if not found
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def update(self, estimate: Estimate) -> Estimate:
        """
        Update an existing estimate.
        
        Args:
            estimate: Estimate entity with updated data
            
        Returns:
            Updated Estimate entity
            
        Raises:
            DatabaseError: If update fails
            NotFoundError: If estimate doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, estimate_id: uuid.UUID) -> bool:
        """
        Delete an estimate by ID.
        
        Args:
            estimate_id: ID of the estimate to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            DatabaseError: If deletion fails
        """
        pass
    
    # Flexible Query Operations
    @abstractmethod
    async def list_with_filters(
        self,
        business_id: uuid.UUID,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_date",
        sort_desc: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Estimate], int]:
        """
        List estimates with flexible filtering and pagination.
        
        This method replaces 15+ specific query methods with a single flexible interface.
        
        Args:
            business_id: ID of the business
            filters: Dictionary of filters to apply (see EstimateFilters for options)
            sort_by: Field to sort by
            sort_desc: Sort in descending order
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (List of Estimate entities, Total count)
            
        Raises:
            DatabaseError: If query fails
            ValidationError: If filter parameters are invalid
            
        Example filters:
            {
                "status": EstimateStatus.SENT,
                "contact_id": uuid.UUID("..."),
                "date_from": datetime(...),
                "date_to": datetime(...),
                "min_value": Decimal("1000"),
                "search_term": "kitchen renovation"
            }
        """
        pass
    
    @abstractmethod
    async def exists(self, estimate_id: uuid.UUID) -> bool:
        """
        Check if an estimate exists.
        
        Args:
            estimate_id: ID of the estimate
            
        Returns:
            True if estimate exists, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    @abstractmethod
    async def count_with_filters(
        self,
        business_id: uuid.UUID,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count estimates matching filters.
        
        Args:
            business_id: ID of the business
            filters: Dictionary of filters to apply
            
        Returns:
            Number of estimates matching filters
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    # Business Logic Helpers
    @abstractmethod
    async def get_next_estimate_number(self, business_id: uuid.UUID, prefix: str = "EST") -> str:
        """
        Generate next available estimate number for a business.
        
        Args:
            business_id: ID of the business
            prefix: Prefix for estimate number
            
        Returns:
            Next available estimate number
            
        Raises:
            DatabaseError: If generation fails
        """
        pass
    
    @abstractmethod
    async def has_duplicate_estimate_number(
        self, 
        business_id: uuid.UUID, 
        estimate_number: str,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if estimate number already exists within business.
        
        Args:
            business_id: ID of the business
            estimate_number: Estimate number to check
            exclude_id: Optional estimate ID to exclude from check
            
        Returns:
            True if duplicate exists, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    # Bulk Operations
    @abstractmethod
    async def bulk_update_status(
        self, 
        business_id: uuid.UUID, 
        estimate_ids: List[uuid.UUID],
        status: EstimateStatus,
        changed_by: Optional[str] = None
    ) -> int:
        """
        Bulk update estimate status.
        
        Args:
            business_id: ID of the business
            estimate_ids: List of estimate IDs to update
            status: New status to set
            changed_by: User making the change
            
        Returns:
            Number of estimates updated
            
        Raises:
            DatabaseError: If bulk update fails
        """
        pass
    
    # Query Builder Support
    def query(self) -> EstimateQueryBuilder:
        """
        Create a new query builder for complex queries.
        
        Returns:
            EstimateQueryBuilder instance
            
        Example:
            estimates, total = await repo.execute_query(
                business_id,
                repo.query()
                    .filter_by_status(EstimateStatus.SENT)
                    .filter_expiring_soon(7)
                    .sort_by_field("created_date", descending=True)
                    .paginate(0, 50)
            )
        """
        return EstimateQueryBuilder()
    
    async def execute_query(
        self, 
        business_id: uuid.UUID, 
        query_builder: EstimateQueryBuilder
    ) -> Tuple[List[Estimate], int]:
        """
        Execute a query built with EstimateQueryBuilder.
        
        Args:
            business_id: ID of the business
            query_builder: Configured query builder
            
        Returns:
            Tuple of (List of Estimate entities, Total count)
            
        Raises:
            DatabaseError: If query execution fails
        """
        filters = query_builder.build_filters()
        sort_by, sort_desc = query_builder.build_sort()
        skip, limit = query_builder.build_pagination()
        
        return await self.list_with_filters(
            business_id=business_id,
            filters=filters,
            sort_by=sort_by,
            sort_desc=sort_desc,
            skip=skip,
            limit=limit
        )


# Convenience query builders for common patterns
class CommonEstimateQueries:
    """Common estimate query patterns using the query builder."""
    
    @staticmethod
    def recent_estimates(days: int = 30) -> EstimateQueryBuilder:
        """Get estimates created in the last N days."""
        from datetime import datetime, timedelta
        date_from = datetime.now() - timedelta(days=days)
        return EstimateQueryBuilder().filter_by_date_range(date_from, datetime.now())
    
    @staticmethod
    def pending_estimates() -> EstimateQueryBuilder:
        """Get estimates pending approval."""
        return EstimateQueryBuilder().filter_pending_approval()
    
    @staticmethod
    def draft_estimates() -> EstimateQueryBuilder:
        """Get draft estimates."""
        return EstimateQueryBuilder().filter_by_status(EstimateStatus.DRAFT)
    
    @staticmethod
    def expired_estimates() -> EstimateQueryBuilder:
        """Get expired estimates."""
        return EstimateQueryBuilder().filter_expired(True)
    
    @staticmethod
    def expiring_soon_estimates(days: int = 7) -> EstimateQueryBuilder:
        """Get estimates expiring in N days."""
        return EstimateQueryBuilder().filter_expiring_soon(days)
    
    @staticmethod
    def high_value_estimates(min_value: Decimal) -> EstimateQueryBuilder:
        """Get estimates above certain value."""
        return EstimateQueryBuilder().filter_by_value_range(min_value, Decimal("999999999"))
    
    @staticmethod
    def contact_estimates(contact_id: uuid.UUID) -> EstimateQueryBuilder:
        """Get all estimates for a contact."""
        return EstimateQueryBuilder().filter_by_contact(contact_id)
    
    @staticmethod
    def project_estimates(project_id: uuid.UUID) -> EstimateQueryBuilder:
        """Get all estimates for a project."""
        return EstimateQueryBuilder().filter_by_project(project_id) 