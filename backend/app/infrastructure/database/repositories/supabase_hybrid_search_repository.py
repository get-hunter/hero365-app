"""
Supabase Hybrid Search Repository Implementation

Implementation of HybridSearchRepository interface using Supabase with pgvector.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
import json

from supabase import Client
from postgrest.exceptions import APIError

from ....domain.repositories.hybrid_search_repository import (
    HybridSearchRepository, SearchResult, EmbeddingRecord, SearchQuery
)
from ....application.exceptions.application_exceptions import (
    ApplicationError, NotFoundError
)

logger = logging.getLogger(__name__)


class SupabaseHybridSearchRepository(HybridSearchRepository):
    """
    Supabase implementation of HybridSearchRepository.
    
    Uses Supabase PostgreSQL with pgvector extension for vector similarity search
    and traditional text search capabilities.
    """
    
    def __init__(self, supabase_client: Client):
        """
        Initialize the Supabase hybrid search repository.
        
        Args:
            supabase_client: Authenticated Supabase client
        """
        self.client = supabase_client
    
    async def store_embedding(self, 
                            entity_type: str, 
                            entity_id: UUID, 
                            business_id: UUID,
                            content: str,
                            embedding: List[float],
                            content_hash: str,
                            embedding_model: str = "text-embedding-3-small") -> bool:
        """Store or update an embedding for an entity."""
        try:
            # Prepare embedding data
            embedding_data = {
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "business_id": str(business_id),
                "embedding": embedding,
                "content_hash": content_hash,
                "content_preview": content[:200] if len(content) > 200 else content,
                "embedding_model": embedding_model
            }
            
            # Use upsert to handle both insert and update
            response = self.client.table("entity_embeddings").upsert(
                embedding_data,
                on_conflict="business_id,entity_type,entity_id"
            ).execute()
            
            if response.data:
                logger.debug(f"Successfully stored embedding for {entity_type}:{entity_id}")
                return True
            else:
                logger.error(f"Failed to store embedding for {entity_type}:{entity_id}")
                return False
                
        except APIError as e:
            logger.error(f"API error storing embedding: {e}")
            raise ApplicationError(f"Failed to store embedding: {e}")
        except Exception as e:
            logger.error(f"Unexpected error storing embedding: {e}")
            raise ApplicationError(f"Unexpected error storing embedding: {e}")
    
    async def update_embedding(self, 
                             entity_type: str, 
                             entity_id: UUID, 
                             business_id: UUID,
                             content: str,
                             embedding: List[float],
                             content_hash: str,
                             embedding_model: str = "text-embedding-3-small") -> bool:
        """Update an existing embedding for an entity."""
        # For this implementation, update is the same as store since we use upsert
        return await self.store_embedding(
            entity_type, entity_id, business_id, content, 
            embedding, content_hash, embedding_model
        )
    
    async def get_embedding(self, 
                          entity_type: str, 
                          entity_id: UUID, 
                          business_id: UUID) -> Optional[EmbeddingRecord]:
        """Get embedding record for a specific entity."""
        try:
            response = self.client.table("entity_embeddings").select("*").eq(
                "business_id", str(business_id)
            ).eq(
                "entity_type", entity_type
            ).eq(
                "entity_id", str(entity_id)
            ).execute()
            
            if response.data:
                data = response.data[0]
                return EmbeddingRecord(
                    entity_id=UUID(data["entity_id"]),
                    entity_type=data["entity_type"],
                    business_id=UUID(data["business_id"]),
                    embedding=data["embedding"],
                    content_hash=data["content_hash"],
                    content_preview=data["content_preview"],
                    embedding_model=data["embedding_model"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    updated_at=datetime.fromisoformat(data["updated_at"])
                )
            else:
                return None
                
        except APIError as e:
            logger.error(f"API error getting embedding: {e}")
            raise ApplicationError(f"Failed to get embedding: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting embedding: {e}")
            raise ApplicationError(f"Unexpected error getting embedding: {e}")
    
    async def delete_embedding(self, 
                             entity_type: str, 
                             entity_id: UUID, 
                             business_id: UUID) -> bool:
        """Delete an embedding record."""
        try:
            response = self.client.table("entity_embeddings").delete().eq(
                "business_id", str(business_id)
            ).eq(
                "entity_type", entity_type
            ).eq(
                "entity_id", str(entity_id)
            ).execute()
            
            return len(response.data) > 0
            
        except APIError as e:
            logger.error(f"API error deleting embedding: {e}")
            raise ApplicationError(f"Failed to delete embedding: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deleting embedding: {e}")
            raise ApplicationError(f"Unexpected error deleting embedding: {e}")
    
    async def search_similar(self, 
                           query_embedding: List[float],
                           business_id: UUID,
                           entity_types: List[str],
                           limit: int = 10,
                           similarity_threshold: float = 0.5) -> List[SearchResult]:
        """Search for similar entities using vector similarity."""
        try:
            # Use the RPC function for vector similarity search
            response = self.client.rpc(
                "search_similar_embeddings",
                {
                    "query_embedding": query_embedding,
                    "business_id": str(business_id),
                    "entity_types": entity_types,
                    "similarity_threshold": similarity_threshold,
                    "max_results": limit
                }
            ).execute()
            
            results = []
            for item in response.data:
                # Convert similarity distance to similarity score (1 - distance)
                similarity_score = 1 - item["similarity_distance"]
                
                results.append(SearchResult(
                    entity_id=UUID(item["entity_id"]),
                    entity_type=item["entity_type"],
                    business_id=UUID(item["business_id"]),
                    similarity_score=similarity_score,
                    content_preview=item["content_preview"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"]),
                    metadata={"embedding_model": item["embedding_model"]}
                ))
            
            return results
            
        except APIError as e:
            logger.error(f"API error in similarity search: {e}")
            raise ApplicationError(f"Failed to perform similarity search: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in similarity search: {e}")
            raise ApplicationError(f"Unexpected error in similarity search: {e}")
    
    async def search_text(self, 
                        query_text: str,
                        business_id: UUID,
                        entity_types: List[str],
                        limit: int = 10) -> List[SearchResult]:
        """Search for entities using traditional text search."""
        try:
            # Use the RPC function for text search
            response = self.client.rpc(
                "search_text_embeddings",
                {
                    "query_text": query_text,
                    "business_id": str(business_id),
                    "entity_types": entity_types,
                    "max_results": limit
                }
            ).execute()
            
            results = []
            for item in response.data:
                results.append(SearchResult(
                    entity_id=UUID(item["entity_id"]),
                    entity_type=item["entity_type"],
                    business_id=UUID(item["business_id"]),
                    similarity_score=item.get("text_rank", 0.5),  # Text relevance score
                    content_preview=item["content_preview"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"]),
                    metadata={"search_type": "text", "embedding_model": item["embedding_model"]}
                ))
            
            return results
            
        except APIError as e:
            logger.error(f"API error in text search: {e}")
            raise ApplicationError(f"Failed to perform text search: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in text search: {e}")
            raise ApplicationError(f"Unexpected error in text search: {e}")
    
    async def search_hybrid(self, query: SearchQuery) -> List[SearchResult]:
        """Perform hybrid search combining text and vector similarity."""
        try:
            # Use the RPC function for hybrid search
            response = self.client.rpc(
                "search_hybrid_embeddings",
                {
                    "query_text": query.query_text,
                    "query_embedding": query.query_embedding,
                    "business_id": str(query.business_id),
                    "entity_types": query.entity_types,
                    "similarity_threshold": query.similarity_threshold,
                    "max_results": query.limit,
                    "text_weight": query.text_search_weight,
                    "vector_weight": query.vector_search_weight
                }
            ).execute()
            
            results = []
            for item in response.data:
                result = SearchResult(
                    entity_id=UUID(item["entity_id"]),
                    entity_type=item["entity_type"],
                    business_id=UUID(item["business_id"]),
                    similarity_score=item["combined_score"],
                    content_preview=item["content_preview"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"]),
                    metadata={
                        "search_type": "hybrid",
                        "text_score": item.get("text_score", 0),
                        "vector_score": item.get("vector_score", 0),
                        "embedding_model": item["embedding_model"]
                    }
                )
                
                # Add relationship information if requested
                if query.include_relationships:
                    # This would be populated by the relationship verification
                    result.relationship_type = item.get("relationship_type")
                    result.relationship_strength = item.get("relationship_strength")
                    result.relationship_details = item.get("relationship_details")
                
                results.append(result)
            
            return results
            
        except APIError as e:
            logger.error(f"API error in hybrid search: {e}")
            raise ApplicationError(f"Failed to perform hybrid search: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in hybrid search: {e}")
            raise ApplicationError(f"Unexpected error in hybrid search: {e}")
    
    async def verify_relationships(self, 
                                 entity_type: str, 
                                 entity_id: UUID, 
                                 business_id: UUID,
                                 related_entity_ids: List[UUID]) -> List[SearchResult]:
        """Verify business relationships between entities."""
        try:
            # Use the relationship verification function
            response = self.client.rpc(
                "verify_entity_relationships",
                {
                    "p_entity_type": entity_type,
                    "p_entity_id": str(entity_id),
                    "p_business_id": str(business_id),
                    "p_related_entity_ids": [str(id) for id in related_entity_ids]
                }
            ).execute()
            
            results = []
            for item in response.data:
                # Get the embedding record for this related entity
                embedding_record = await self.get_embedding(
                    item["entity_type"], UUID(item["entity_id"]), business_id
                )
                
                if embedding_record:
                    result = SearchResult(
                        entity_id=UUID(item["entity_id"]),
                        entity_type=item["entity_type"],
                        business_id=business_id,
                        similarity_score=0.0,  # Not applicable for relationship verification
                        content_preview=embedding_record.content_preview,
                        created_at=embedding_record.created_at,
                        updated_at=embedding_record.updated_at,
                        metadata={"verified_relationship": True},
                        relationship_type=item["relationship_type"],
                        relationship_strength=item["relationship_strength"],
                        relationship_details=item.get("relationship_details", {})
                    )
                    results.append(result)
            
            return results
            
        except APIError as e:
            logger.error(f"API error in relationship verification: {e}")
            raise ApplicationError(f"Failed to verify relationships: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in relationship verification: {e}")
            raise ApplicationError(f"Unexpected error in relationship verification: {e}")
    
    async def get_entity_embeddings(self, 
                                  business_id: UUID,
                                  entity_type: Optional[str] = None,
                                  limit: int = 100,
                                  offset: int = 0) -> List[EmbeddingRecord]:
        """Get embedding records for a business."""
        try:
            query = self.client.table("entity_embeddings").select("*").eq(
                "business_id", str(business_id)
            )
            
            if entity_type:
                query = query.eq("entity_type", entity_type)
            
            response = query.range(offset, offset + limit - 1).execute()
            
            records = []
            for item in response.data:
                records.append(EmbeddingRecord(
                    entity_id=UUID(item["entity_id"]),
                    entity_type=item["entity_type"],
                    business_id=UUID(item["business_id"]),
                    embedding=item["embedding"],
                    content_hash=item["content_hash"],
                    content_preview=item["content_preview"],
                    embedding_model=item["embedding_model"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"])
                ))
            
            return records
            
        except APIError as e:
            logger.error(f"API error getting entity embeddings: {e}")
            raise ApplicationError(f"Failed to get entity embeddings: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting entity embeddings: {e}")
            raise ApplicationError(f"Unexpected error getting entity embeddings: {e}")
    
    async def get_embedding_stats(self, business_id: UUID) -> Dict[str, Any]:
        """Get statistics about embeddings for a business."""
        try:
            response = self.client.rpc(
                "get_embedding_stats",
                {"p_business_id": str(business_id)}
            ).execute()
            
            if response.data:
                stats = {}
                for item in response.data:
                    stats[item["entity_type"]] = {
                        "total_embeddings": item["total_embeddings"],
                        "avg_content_length": float(item["avg_content_length"]) if item["avg_content_length"] else 0,
                        "last_updated": item["last_updated"]
                    }
                return stats
            else:
                return {}
                
        except APIError as e:
            logger.error(f"API error getting embedding stats: {e}")
            raise ApplicationError(f"Failed to get embedding stats: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting embedding stats: {e}")
            raise ApplicationError(f"Unexpected error getting embedding stats: {e}")
    
    async def bulk_store_embeddings(self, 
                                  embeddings: List[Dict[str, Any]]) -> int:
        """Store multiple embeddings in a single operation."""
        try:
            if not embeddings:
                return 0
            
            # Prepare data for bulk insert
            bulk_data = []
            for embedding in embeddings:
                bulk_data.append({
                    "entity_type": embedding["entity_type"],
                    "entity_id": str(embedding["entity_id"]),
                    "business_id": str(embedding["business_id"]),
                    "embedding": embedding["embedding"],
                    "content_hash": embedding["content_hash"],
                    "content_preview": embedding.get("content_preview", ""),
                    "embedding_model": embedding.get("embedding_model", "text-embedding-3-small")
                })
            
            response = self.client.table("entity_embeddings").upsert(
                bulk_data,
                on_conflict="business_id,entity_type,entity_id"
            ).execute()
            
            return len(response.data) if response.data else 0
            
        except APIError as e:
            logger.error(f"API error in bulk store: {e}")
            raise ApplicationError(f"Failed to bulk store embeddings: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in bulk store: {e}")
            raise ApplicationError(f"Unexpected error in bulk store: {e}")
    
    async def cleanup_orphaned_embeddings(self, business_id: UUID) -> int:
        """Remove embeddings for entities that no longer exist."""
        try:
            response = self.client.rpc(
                "cleanup_orphaned_embeddings",
                {"p_business_id": str(business_id)}
            ).execute()
            
            return response.data if response.data else 0
            
        except APIError as e:
            logger.error(f"API error in cleanup: {e}")
            raise ApplicationError(f"Failed to cleanup orphaned embeddings: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in cleanup: {e}")
            raise ApplicationError(f"Unexpected error in cleanup: {e}")
    
    async def get_stale_embeddings(self, 
                                 business_id: UUID,
                                 hours_threshold: int = 24) -> List[EmbeddingRecord]:
        """Get embeddings that haven't been updated recently."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_threshold)
            
            response = self.client.table("entity_embeddings").select("*").eq(
                "business_id", str(business_id)
            ).lt(
                "updated_at", cutoff_time.isoformat()
            ).execute()
            
            records = []
            for item in response.data:
                records.append(EmbeddingRecord(
                    entity_id=UUID(item["entity_id"]),
                    entity_type=item["entity_type"],
                    business_id=UUID(item["business_id"]),
                    embedding=item["embedding"],
                    content_hash=item["content_hash"],
                    content_preview=item["content_preview"],
                    embedding_model=item["embedding_model"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"])
                ))
            
            return records
            
        except APIError as e:
            logger.error(f"API error getting stale embeddings: {e}")
            raise ApplicationError(f"Failed to get stale embeddings: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting stale embeddings: {e}")
            raise ApplicationError(f"Unexpected error getting stale embeddings: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the repository."""
        try:
            # Test basic connectivity
            response = self.client.table("entity_embeddings").select("count", count="exact").limit(1).execute()
            
            # Test pgvector extension
            vector_test = self.client.rpc("test_vector_operations").execute()
            
            return {
                "status": "healthy",
                "total_embeddings": response.count,
                "vector_extension": "available" if vector_test.data else "unavailable",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 