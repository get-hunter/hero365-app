"""
Base Repository Interface

Abstract base class defining common repository operations.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

# Generic type for entities
T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository providing common CRUD operations.
    
    This interface defines the contract that all repositories must implement
    following the Repository pattern.
    """
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Create a new entity.
        
        Args:
            entity: Entity to create
            
        Returns:
            The created entity
            
        Raises:
            DuplicateEntityError: If entity already exists
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: uuid.UUID) -> Optional[T]:
        """
        Get an entity by its ID.
        
        Args:
            entity_id: ID of the entity to retrieve
            
        Returns:
            The entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        Update an existing entity.
        
        Args:
            entity: Entity to update
            
        Returns:
            The updated entity
            
        Raises:
            EntityNotFoundError: If entity doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: uuid.UUID) -> bool:
        """
        Delete an entity by its ID.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            True if entity was deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def exists(self, entity_id: uuid.UUID) -> bool:
        """
        Check if an entity exists.
        
        Args:
            entity_id: ID of the entity to check
            
        Returns:
            True if entity exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get all entities with pagination.
        
        Args:
            skip: Number of entities to skip
            limit: Maximum number of entities to return
            
        Returns:
            List of entities
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Get the total count of entities.
        
        Returns:
            Total number of entities
        """
        pass 