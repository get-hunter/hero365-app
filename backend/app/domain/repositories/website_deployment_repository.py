"""
Website Deployment Repository Interface

Defines the contract for website deployment data access operations.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..entities.website_deployment import WebsiteDeployment, BusinessWebsite, DeploymentStatus


class WebsiteDeploymentRepository(ABC):
    """
    Repository interface for WebsiteDeployment entity operations.
    
    This interface defines the contract for all website deployment data access operations,
    following the Repository pattern to abstract database implementation details.
    """
    
    @abstractmethod
    async def create(self, deployment: WebsiteDeployment) -> WebsiteDeployment:
        """
        Create a new website deployment.
        
        Args:
            deployment: WebsiteDeployment entity to create
            
        Returns:
            Created deployment entity with generated ID and timestamps
            
        Raises:
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, deployment_id: uuid.UUID) -> Optional[WebsiteDeployment]:
        """
        Get deployment by ID.
        
        Args:
            deployment_id: Unique identifier of the deployment
            
        Returns:
            WebsiteDeployment entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_business_id(
        self, 
        business_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[WebsiteDeployment]:
        """
        Get deployments for a specific business.
        
        Args:
            business_id: ID of the business
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of deployment entities for the business
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_active_deployment(self, business_id: uuid.UUID) -> Optional[WebsiteDeployment]:
        """
        Get the currently active (non-terminal) deployment for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            Active deployment if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_current_deployment(self, business_id: uuid.UUID) -> Optional[WebsiteDeployment]:
        """
        Get the current live deployment for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            Current deployment if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_idempotency_key(
        self, 
        business_id: uuid.UUID, 
        idempotency_key: str
    ) -> Optional[WebsiteDeployment]:
        """
        Get deployment by idempotency key for a business.
        
        Args:
            business_id: ID of the business
            idempotency_key: Idempotency key to search for
            
        Returns:
            Deployment with matching idempotency key if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def update(self, deployment: WebsiteDeployment) -> WebsiteDeployment:
        """
        Update an existing deployment.
        
        Args:
            deployment: Deployment entity with updated information
            
        Returns:
            Updated deployment entity
            
        Raises:
            EntityNotFoundError: If deployment doesn't exist
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def update_status(
        self, 
        deployment_id: uuid.UUID, 
        status: DeploymentStatus,
        progress: Optional[int] = None,
        current_step: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update deployment status and progress.
        
        Args:
            deployment_id: ID of the deployment
            status: New deployment status
            progress: Progress percentage (0-100)
            current_step: Current deployment step description
            error_message: Error message if status is failed
            
        Returns:
            True if update was successful, False otherwise
            
        Raises:
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def set_current_deployment(
        self, 
        business_id: uuid.UUID, 
        deployment_id: uuid.UUID
    ) -> bool:
        """
        Set a deployment as the current live deployment for a business.
        
        This will unset any previous current deployment and set the specified
        deployment as current.
        
        Args:
            business_id: ID of the business
            deployment_id: ID of the deployment to set as current
            
        Returns:
            True if update was successful, False otherwise
            
        Raises:
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def cancel_deployment(self, deployment_id: uuid.UUID) -> bool:
        """
        Cancel a pending or in-progress deployment.
        
        Args:
            deployment_id: ID of the deployment to cancel
            
        Returns:
            True if cancellation was successful, False otherwise
            
        Raises:
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def get_deployments_by_status(
        self, 
        status: DeploymentStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[WebsiteDeployment]:
        """
        Get deployments by status across all businesses.
        
        Args:
            status: Deployment status to filter by
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of deployments with the specified status
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def count_by_business(self, business_id: uuid.UUID) -> int:
        """
        Get count of deployments for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            Number of deployments for the business
            
        Raises:
            DatabaseError: If count fails
        """
        pass
    
    @abstractmethod
    async def delete(self, deployment_id: uuid.UUID) -> bool:
        """
        Delete a deployment record.
        
        Args:
            deployment_id: ID of the deployment to delete
            
        Returns:
            True if deletion was successful, False if deployment wasn't found
            
        Raises:
            DatabaseError: If deletion fails
        """
        pass


class BusinessWebsiteRepository(ABC):
    """
    Repository interface for BusinessWebsite entity operations.
    
    This interface defines the contract for business website configuration
    data access operations.
    """
    
    @abstractmethod
    async def create(self, website: BusinessWebsite) -> BusinessWebsite:
        """
        Create a new business website configuration.
        
        Args:
            website: BusinessWebsite entity to create
            
        Returns:
            Created website entity with generated ID and timestamps
            
        Raises:
            DuplicateEntityError: If subdomain already exists
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_by_business_id(self, business_id: uuid.UUID) -> Optional[BusinessWebsite]:
        """
        Get website configuration for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            BusinessWebsite entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_by_subdomain(self, subdomain: str) -> Optional[BusinessWebsite]:
        """
        Get website by subdomain.
        
        Args:
            subdomain: Subdomain to search for
            
        Returns:
            BusinessWebsite entity if found, None otherwise
            
        Raises:
            DatabaseError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def update(self, website: BusinessWebsite) -> BusinessWebsite:
        """
        Update an existing website configuration.
        
        Args:
            website: Website entity with updated information
            
        Returns:
            Updated website entity
            
        Raises:
            EntityNotFoundError: If website doesn't exist
            DuplicateEntityError: If subdomain conflicts
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    async def upsert_by_business_id(self, website: BusinessWebsite) -> BusinessWebsite:
        """
        Create or update website configuration for a business.
        
        Args:
            website: Website entity to create or update
            
        Returns:
            Created or updated website entity
            
        Raises:
            DuplicateEntityError: If subdomain conflicts with another business
            DatabaseError: If operation fails
        """
        pass
    
    @abstractmethod
    async def is_subdomain_available(
        self, 
        subdomain: str, 
        exclude_business_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if a subdomain is available.
        
        Args:
            subdomain: Subdomain to check
            exclude_business_id: Business ID to exclude from check (for updates)
            
        Returns:
            True if subdomain is available, False otherwise
            
        Raises:
            DatabaseError: If check fails
        """
        pass
    
    @abstractmethod
    async def delete(self, business_id: uuid.UUID) -> bool:
        """
        Delete website configuration for a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            True if deletion was successful, False if website wasn't found
            
        Raises:
            DatabaseError: If deletion fails
        """
        pass
