"""
Estimate Repository Interface

Defines the contract for estimate data access operations.
Follows the Repository pattern for clean architecture.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from ..entities.estimate import Estimate
from ..enums import EstimateStatus, CurrencyCode


class EstimateRepository(ABC):
    """
    Abstract repository interface for estimate data access operations.
    
    Defines all methods needed for estimate management without
    specifying implementation details.
    """
    
    @abstractmethod
    async def create(self, estimate: Estimate) -> Estimate:
        """Create a new estimate."""
        pass
    
    @abstractmethod
    async def get_by_id(self, estimate_id: uuid.UUID) -> Optional[Estimate]:
        """Get estimate by ID."""
        pass
    
    @abstractmethod
    async def get_by_estimate_number(self, business_id: uuid.UUID, estimate_number: str) -> Optional[Estimate]:
        """Get estimate by estimate number within a business."""
        pass
    
    @abstractmethod
    async def get_by_business_id(self, business_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates by business ID with pagination."""
        pass
    
    @abstractmethod
    async def get_by_contact_id(self, contact_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates by contact ID with pagination."""
        pass
    
    @abstractmethod
    async def get_by_project_id(self, project_id: uuid.UUID, business_id: uuid.UUID,
                               skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates associated with a specific project."""
        pass
    
    @abstractmethod
    async def get_by_job_id(self, job_id: uuid.UUID, business_id: uuid.UUID,
                           skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates associated with a specific job."""
        pass
    
    @abstractmethod
    async def get_by_status(self, business_id: uuid.UUID, status: EstimateStatus,
                           skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates by status within a business."""
        pass
    
    @abstractmethod
    async def get_by_assigned_user(self, business_id: uuid.UUID, user_id: str,
                                  skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates assigned to a specific user within a business."""
        pass
    
    @abstractmethod
    async def get_by_template_id(self, business_id: uuid.UUID, template_id: uuid.UUID,
                                skip: int = 0, limit: int = 100) -> List[Estimate]:
        """
        Get estimates using a specific template within a business.
        
        Args:
            business_id: ID of the business
            template_id: ID of the template
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Estimate entities using the template
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_date_range(self, business_id: uuid.UUID, start_date: datetime,
                               end_date: datetime, skip: int = 0, limit: int = 100) -> List[Estimate]:
        """
        Get estimates within a date range.
        
        Args:
            business_id: ID of the business
            start_date: Start date of the range
            end_date: End date of the range
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Estimate entities within the date range
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_expired_estimates(self, business_id: uuid.UUID,
                                   skip: int = 0, limit: int = 100) -> List[Estimate]:
        """
        Get estimates that have expired but not yet marked as expired.
        
        Args:
            business_id: ID of the business
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of expired Estimate entities
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_expiring_soon(self, business_id: uuid.UUID, days: int = 7,
                               skip: int = 0, limit: int = 100) -> List[Estimate]:
        """
        Get estimates expiring within the specified number of days.
        
        Args:
            business_id: ID of the business
            days: Number of days from now to check for expiration
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Estimate entities expiring soon
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_pending_approval(self, business_id: uuid.UUID,
                                  skip: int = 0, limit: int = 100) -> List[Estimate]:
        """
        Get estimates pending client approval (sent but not approved/rejected).
        
        Args:
            business_id: ID of the business
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Estimate entities pending approval
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_value_range(self, business_id: uuid.UUID, min_value: Decimal,
                                max_value: Decimal, skip: int = 0, limit: int = 100) -> List[Estimate]:
        """
        Get estimates within a value range.
        
        Args:
            business_id: ID of the business
            min_value: Minimum estimate value
            max_value: Maximum estimate value
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Estimate entities within the value range
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def search_estimates(self, business_id: uuid.UUID, search_term: str,
                              skip: int = 0, limit: int = 100) -> List[Estimate]:
        """
        Search estimates within a business by title, description, or estimate number.
        
        Args:
            business_id: ID of the business
            search_term: Term to search for
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Estimate entities matching the search term
            
        Raises:
            DatabaseError: If search fails
        """
        pass
    
    @abstractmethod
    async def get_by_currency(self, business_id: uuid.UUID, currency: CurrencyCode,
                             skip: int = 0, limit: int = 100) -> List[Estimate]:
        """
        Get estimates by currency within a business.
        
        Args:
            business_id: ID of the business
            currency: Currency code to filter by
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of Estimate entities in the specified currency
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def update(self, estimate: Estimate) -> Estimate:
        """Update an existing estimate."""
        pass
    
    @abstractmethod
    async def delete(self, estimate_id: uuid.UUID) -> bool:
        """Delete an estimate by ID."""
        pass
    
    @abstractmethod
    async def bulk_update_status(self, business_id: uuid.UUID, estimate_ids: List[uuid.UUID],
                                status: EstimateStatus) -> int:
        """
        Bulk update estimate status.
        
        Args:
            business_id: ID of the business
            estimate_ids: List of estimate IDs to update
            status: New status to set
            
        Returns:
            Number of estimates updated
            
        Raises:
            DatabaseError: If bulk update fails
        """
        pass
    
    @abstractmethod
    async def bulk_assign_estimates(self, business_id: uuid.UUID, estimate_ids: List[uuid.UUID],
                                   user_id: str) -> int:
        """
        Bulk assign estimates to a user.
        
        Args:
            business_id: ID of the business
            estimate_ids: List of estimate IDs to assign
            user_id: ID of the user to assign to
            
        Returns:
            Number of estimates assigned
            
        Raises:
            DatabaseError: If bulk assignment fails
        """
        pass
    
    @abstractmethod
    async def bulk_expire_estimates(self, business_id: uuid.UUID, estimate_ids: List[uuid.UUID]) -> int:
        """
        Bulk expire estimates.
        
        Args:
            business_id: ID of the business
            estimate_ids: List of estimate IDs to expire
            
        Returns:
            Number of estimates expired
            
        Raises:
            DatabaseError: If bulk expiration fails
        """
        pass
    
    @abstractmethod
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """
        Count total estimates for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            Total number of estimates
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def count_by_status(self, business_id: uuid.UUID, status: EstimateStatus) -> int:
        """
        Count estimates by status within a business.
        
        Args:
            business_id: ID of the business
            status: Status to count
            
        Returns:
            Number of estimates with the specified status
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def count_by_contact(self, contact_id: uuid.UUID) -> int:
        """
        Count estimates for a specific contact.
        
        Args:
            contact_id: ID of the contact
            
        Returns:
            Number of estimates for the contact
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    

    
    @abstractmethod
    async def exists(self, estimate_id: uuid.UUID) -> bool:
        """Check if an estimate exists."""
        pass

    @abstractmethod
    async def get_by_template_id(self, business_id: uuid.UUID, template_id: uuid.UUID,
                                skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates using a specific template within a business."""
        pass

    @abstractmethod
    async def get_by_date_range(self, business_id: uuid.UUID, start_date: datetime,
                               end_date: datetime, skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates within a date range."""
        pass

    @abstractmethod
    async def get_expired_estimates(self, business_id: uuid.UUID,
                                   skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates that have expired but not yet marked as expired."""
        pass

    @abstractmethod
    async def get_expiring_soon(self, business_id: uuid.UUID, days: int = 7,
                               skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates expiring within the specified number of days."""
        pass

    @abstractmethod
    async def get_pending_approval(self, business_id: uuid.UUID,
                                  skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Get estimates pending client approval (sent but not approved/rejected)."""
        pass

    @abstractmethod
    async def search_estimates(self, business_id: uuid.UUID, search_term: str,
                              skip: int = 0, limit: int = 100) -> List[Estimate]:
        """Search estimates within a business by title, description, or estimate number."""
        pass

    @abstractmethod
    async def bulk_update_status(self, business_id: uuid.UUID, estimate_ids: List[uuid.UUID],
                                status: EstimateStatus) -> int:
        """Bulk update estimate status."""
        pass

    @abstractmethod
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """Count total estimates for a business."""
        pass

    @abstractmethod
    async def count_by_status(self, business_id: uuid.UUID, status: EstimateStatus) -> int:
        """Count estimates by status within a business."""
        pass



    @abstractmethod
    async def has_duplicate_estimate_number(self, business_id: uuid.UUID, estimate_number: str,
                                           exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Check if estimate number already exists within business."""
        pass

    @abstractmethod
    async def get_next_estimate_number(self, business_id: uuid.UUID, prefix: str = "EST") -> str:
        """Generate next available estimate number for a business."""
        pass 