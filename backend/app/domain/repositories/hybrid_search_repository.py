"""
Hybrid Search Repository Interface

Domain repository interface for hybrid search operations combining
traditional text search with vector similarity search.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

# BaseEntity import removed as it's not needed for this interface


@dataclass
class SearchResult:
    """Result object for hybrid search operations."""
    
    entity_id: UUID
    entity_type: str
    business_id: UUID
    similarity_score: float
    content_preview: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    # Relationship information
    relationship_type: Optional[str] = None
    relationship_strength: Optional[int] = None
    relationship_details: Optional[Dict[str, Any]] = None


@dataclass
class EmbeddingRecord:
    """Record object for embedding storage operations."""
    
    entity_id: UUID
    entity_type: str
    business_id: UUID
    embedding: List[float]
    content_hash: str
    content_preview: str
    embedding_model: str
    created_at: datetime
    updated_at: datetime


@dataclass
class SearchQuery:
    """Query object for hybrid search operations."""
    
    query_text: str
    query_embedding: List[float]
    business_id: UUID
    entity_types: List[str]
    limit: int = 10
    similarity_threshold: float = 0.5
    include_relationships: bool = True
    text_search_weight: float = 0.3
    vector_search_weight: float = 0.7


class HybridSearchRepository(ABC):
    """
    Repository interface for hybrid search operations.
    
    Combines traditional text search with vector similarity search
    to provide intelligent entity discovery and relationship verification.
    """
    
    @abstractmethod
    async def store_embedding(self, 
                            entity_type: str, 
                            entity_id: UUID, 
                            business_id: UUID,
                            content: str,
                            embedding: List[float],
                            content_hash: str,
                            embedding_model: str = "text-embedding-3-small") -> bool:
        """
        Store or update an embedding for an entity.
        
        Args:
            entity_type: Type of entity (contact, job, estimate, etc.)
            entity_id: Unique identifier of the entity
            business_id: Business identifier for multi-tenancy
            content: Original content that was embedded
            embedding: Vector embedding of the content
            content_hash: SHA256 hash of the content for change detection
            embedding_model: Model used to generate embedding
            
        Returns:
            True if successfully stored, False otherwise
        """
        pass
    
    @abstractmethod
    async def update_embedding(self, 
                             entity_type: str, 
                             entity_id: UUID, 
                             business_id: UUID,
                             content: str,
                             embedding: List[float],
                             content_hash: str,
                             embedding_model: str = "text-embedding-3-small") -> bool:
        """
        Update an existing embedding for an entity.
        
        Args:
            entity_type: Type of entity
            entity_id: Unique identifier of the entity
            business_id: Business identifier for multi-tenancy
            content: Updated content that was embedded
            embedding: New vector embedding
            content_hash: New SHA256 hash of the content
            embedding_model: Model used to generate embedding
            
        Returns:
            True if successfully updated, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_embedding(self, 
                          entity_type: str, 
                          entity_id: UUID, 
                          business_id: UUID) -> Optional[EmbeddingRecord]:
        """
        Get embedding record for a specific entity.
        
        Args:
            entity_type: Type of entity
            entity_id: Unique identifier of the entity
            business_id: Business identifier for multi-tenancy
            
        Returns:
            EmbeddingRecord if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete_embedding(self, 
                             entity_type: str, 
                             entity_id: UUID, 
                             business_id: UUID) -> bool:
        """
        Delete an embedding record.
        
        Args:
            entity_type: Type of entity
            entity_id: Unique identifier of the entity
            business_id: Business identifier for multi-tenancy
            
        Returns:
            True if successfully deleted, False otherwise
        """
        pass
    
    @abstractmethod
    async def search_similar(self, 
                           query_embedding: List[float],
                           business_id: UUID,
                           entity_types: List[str],
                           limit: int = 10,
                           similarity_threshold: float = 0.5) -> List[SearchResult]:
        """
        Search for similar entities using vector similarity.
        
        Args:
            query_embedding: Vector embedding of the search query
            business_id: Business identifier for multi-tenancy
            entity_types: List of entity types to search
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of SearchResult objects sorted by similarity
        """
        pass
    
    @abstractmethod
    async def search_text(self, 
                        query_text: str,
                        business_id: UUID,
                        entity_types: List[str],
                        limit: int = 10) -> List[SearchResult]:
        """
        Search for entities using traditional text search.
        
        Args:
            query_text: Text query string
            business_id: Business identifier for multi-tenancy
            entity_types: List of entity types to search
            limit: Maximum number of results
            
        Returns:
            List of SearchResult objects sorted by relevance
        """
        pass
    
    @abstractmethod
    async def search_hybrid(self, query: SearchQuery) -> List[SearchResult]:
        """
        Perform hybrid search combining text and vector similarity.
        
        Args:
            query: SearchQuery object containing all search parameters
            
        Returns:
            List of SearchResult objects with combined scoring
        """
        pass
    
    @abstractmethod
    async def verify_relationships(self, 
                                 entity_type: str, 
                                 entity_id: UUID, 
                                 business_id: UUID,
                                 related_entity_ids: List[UUID]) -> List[SearchResult]:
        """
        Verify business relationships between entities.
        
        Args:
            entity_type: Type of the primary entity
            entity_id: ID of the primary entity
            business_id: Business identifier for multi-tenancy
            related_entity_ids: List of potentially related entity IDs
            
        Returns:
            List of SearchResult objects with relationship information
        """
        pass
    
    @abstractmethod
    async def get_entity_embeddings(self, 
                                  business_id: UUID,
                                  entity_type: Optional[str] = None,
                                  limit: int = 100,
                                  offset: int = 0) -> List[EmbeddingRecord]:
        """
        Get embedding records for a business.
        
        Args:
            business_id: Business identifier for multi-tenancy
            entity_type: Optional entity type filter
            limit: Maximum number of records
            offset: Number of records to skip
            
        Returns:
            List of EmbeddingRecord objects
        """
        pass
    
    @abstractmethod
    async def get_embedding_stats(self, business_id: UUID) -> Dict[str, Any]:
        """
        Get statistics about embeddings for a business.
        
        Args:
            business_id: Business identifier for multi-tenancy
            
        Returns:
            Dictionary containing embedding statistics
        """
        pass
    
    @abstractmethod
    async def bulk_store_embeddings(self, 
                                  embeddings: List[Dict[str, Any]]) -> int:
        """
        Store multiple embeddings in a single operation.
        
        Args:
            embeddings: List of embedding dictionaries
            
        Returns:
            Number of successfully stored embeddings
        """
        pass
    
    @abstractmethod
    async def cleanup_orphaned_embeddings(self, business_id: UUID) -> int:
        """
        Remove embeddings for entities that no longer exist.
        
        Args:
            business_id: Business identifier for multi-tenancy
            
        Returns:
            Number of orphaned embeddings removed
        """
        pass
    
    @abstractmethod
    async def get_stale_embeddings(self, 
                                 business_id: UUID,
                                 hours_threshold: int = 24) -> List[EmbeddingRecord]:
        """
        Get embeddings that haven't been updated recently.
        
        Args:
            business_id: Business identifier for multi-tenancy
            hours_threshold: Number of hours to consider as stale
            
        Returns:
            List of EmbeddingRecord objects that are stale
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the repository.
        
        Returns:
            Dictionary containing health status information
        """
        pass 