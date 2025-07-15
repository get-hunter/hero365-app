"""
Embedding Service Port

Port interface for text embedding generation services following the ports and adapters pattern.
This defines contracts for embedding generation without implementation details.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from decimal import Decimal


class EmbeddingServicePort(ABC):
    """Port interface for text embedding generation services."""
    
    @abstractmethod
    async def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """
        Generate embedding for a single text string.
        
        Args:
            text: The input text to embed
            model: The embedding model to use (default: text-embedding-3-small)
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            EmbeddingServiceError: If embedding generation fails
        """
        pass
    
    @abstractmethod
    async def generate_embeddings_batch(self, 
                                      texts: List[str], 
                                      model: str = "text-embedding-3-small") -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a batch.
        
        Args:
            texts: List of input texts to embed
            model: The embedding model to use (default: text-embedding-3-small)
            
        Returns:
            List of embedding vectors, one for each input text
            
        Raises:
            EmbeddingServiceError: If batch embedding generation fails
        """
        pass
    
    @abstractmethod
    async def get_embedding_dimensions(self, model: str = "text-embedding-3-small") -> int:
        """
        Get the dimensions of embeddings for a specific model.
        
        Args:
            model: The embedding model name
            
        Returns:
            Number of dimensions in the embedding vector
            
        Raises:
            EmbeddingServiceError: If model info cannot be retrieved
        """
        pass
    
    @abstractmethod
    async def calculate_similarity(self, 
                                 embedding1: List[float], 
                                 embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
            
        Raises:
            EmbeddingServiceError: If similarity calculation fails
        """
        pass
    
    @abstractmethod
    async def is_model_available(self, model: str) -> bool:
        """
        Check if a specific embedding model is available.
        
        Args:
            model: The embedding model name to check
            
        Returns:
            True if model is available, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """
        Get list of available embedding models.
        
        Returns:
            List of available model names
        """
        pass
    
    @abstractmethod
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific embedding model.
        
        Args:
            model: The embedding model name
            
        Returns:
            Dictionary containing model information (dimensions, description, etc.)
            
        Raises:
            EmbeddingServiceError: If model info cannot be retrieved
        """
        pass
    
    @abstractmethod
    async def estimate_cost(self, 
                          texts: List[str], 
                          model: str = "text-embedding-3-small") -> Decimal:
        """
        Estimate the cost of embedding generation for given texts.
        
        Args:
            texts: List of texts to estimate cost for
            model: The embedding model to use
            
        Returns:
            Estimated cost in USD
            
        Raises:
            EmbeddingServiceError: If cost estimation fails
        """
        pass


class EmbeddingServiceError(Exception):
    """Exception raised by embedding service operations."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class EmbeddingServiceRateLimitError(EmbeddingServiceError):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, "RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after


class EmbeddingServiceQuotaError(EmbeddingServiceError):
    """Exception raised when quota is exceeded."""
    
    def __init__(self, message: str, quota_type: str):
        super().__init__(message, "QUOTA_EXCEEDED")
        self.quota_type = quota_type


class EmbeddingServiceModelError(EmbeddingServiceError):
    """Exception raised when model is not available or invalid."""
    
    def __init__(self, message: str, model_name: str):
        super().__init__(message, "MODEL_ERROR")
        self.model_name = model_name 