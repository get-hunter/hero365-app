"""
OpenAI Embedding Service Adapter

Implementation of EmbeddingServicePort interface using OpenAI API.
"""

import os
import openai
from typing import List, Dict, Any, Optional
import logging
import math
from decimal import Decimal
import asyncio
from datetime import datetime, timedelta
import hashlib

from ...application.ports.embedding_service import (
    EmbeddingServicePort, EmbeddingServiceError, EmbeddingServiceRateLimitError,
    EmbeddingServiceQuotaError, EmbeddingServiceModelError
)

logger = logging.getLogger(__name__)


class OpenAIEmbeddingAdapter(EmbeddingServicePort):
    """
    OpenAI implementation of EmbeddingServicePort.
    
    This adapter handles text embedding generation using OpenAI's embedding API.
    """
    
    # Model configurations
    MODEL_CONFIG = {
        "text-embedding-3-small": {
            "dimensions": 1536,
            "max_tokens": 8192,
            "cost_per_1k_tokens": 0.00002,  # $0.02 per 1M tokens
            "description": "New and improved embedding model with better performance"
        },
        "text-embedding-3-large": {
            "dimensions": 3072,
            "max_tokens": 8192,
            "cost_per_1k_tokens": 0.00013,  # $0.13 per 1M tokens
            "description": "Most capable embedding model with highest accuracy"
        },
        "text-embedding-ada-002": {
            "dimensions": 1536,
            "max_tokens": 8192,
            "cost_per_1k_tokens": 0.0001,  # $0.10 per 1M tokens
            "description": "Legacy embedding model (deprecated)"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None, 
                 organization: Optional[str] = None,
                 max_retries: int = 3,
                 timeout: int = 30):
        """
        Initialize the OpenAI embedding adapter.
        
        Args:
            api_key: OpenAI API key (optional, can be set via environment)
            organization: OpenAI organization ID (optional)
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.organization = organization or os.getenv("OPENAI_ORGANIZATION")
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Initialize OpenAI client
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            organization=self.organization,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
        
        # Rate limiting tracking
        self.rate_limit_tracker = {}
        
    async def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """Generate embedding for a single text string."""
        try:
            # Validate model
            if model not in self.MODEL_CONFIG:
                raise EmbeddingServiceModelError(f"Model '{model}' is not supported", model)
            
            # Check rate limits
            await self._check_rate_limits()
            
            # Prepare text (truncate if too long)
            processed_text = self._prepare_text(text, model)
            
            # Generate embedding
            response = await self.client.embeddings.create(
                model=model,
                input=processed_text
            )
            
            # Update rate limit tracking
            self._update_rate_limit_tracker(response)
            
            # Extract embedding
            embedding = response.data[0].embedding
            
            logger.debug(f"Generated embedding for text (length: {len(text)}) using model {model}")
            return embedding
            
        except openai.RateLimitError as e:
            logger.warning(f"Rate limit exceeded for model {model}: {e}")
            raise EmbeddingServiceRateLimitError(
                f"Rate limit exceeded for model {model}",
                retry_after=getattr(e, 'retry_after', None)
            )
        except openai.APIError as e:
            logger.error(f"OpenAI API error during embedding generation: {e}")
            raise EmbeddingServiceError(
                f"OpenAI API error: {e}",
                error_code="OPENAI_API_ERROR",
                details={"model": model, "text_length": len(text)}
            )
        except Exception as e:
            logger.error(f"Unexpected error during embedding generation: {e}")
            raise EmbeddingServiceError(
                f"Unexpected error: {e}",
                error_code="UNEXPECTED_ERROR"
            )
    
    async def generate_embeddings_batch(self, 
                                      texts: List[str], 
                                      model: str = "text-embedding-3-small") -> List[List[float]]:
        """Generate embeddings for multiple texts in a batch."""
        try:
            # Validate model
            if model not in self.MODEL_CONFIG:
                raise EmbeddingServiceModelError(f"Model '{model}' is not supported", model)
            
            if not texts:
                return []
            
            # Check rate limits
            await self._check_rate_limits()
            
            # Prepare texts
            processed_texts = [self._prepare_text(text, model) for text in texts]
            
            # Generate embeddings in batches (OpenAI has limits)
            batch_size = 100  # OpenAI limit
            embeddings = []
            
            for i in range(0, len(processed_texts), batch_size):
                batch = processed_texts[i:i + batch_size]
                
                response = await self.client.embeddings.create(
                    model=model,
                    input=batch
                )
                
                # Update rate limit tracking
                self._update_rate_limit_tracker(response)
                
                # Extract embeddings
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                
                # Small delay between batches to avoid rate limits
                if i + batch_size < len(processed_texts):
                    await asyncio.sleep(0.1)
            
            logger.debug(f"Generated {len(embeddings)} embeddings using model {model}")
            return embeddings
            
        except openai.RateLimitError as e:
            logger.warning(f"Rate limit exceeded for batch embedding with model {model}: {e}")
            raise EmbeddingServiceRateLimitError(
                f"Rate limit exceeded for batch embedding with model {model}",
                retry_after=getattr(e, 'retry_after', None)
            )
        except openai.APIError as e:
            logger.error(f"OpenAI API error during batch embedding generation: {e}")
            raise EmbeddingServiceError(
                f"OpenAI API error: {e}",
                error_code="OPENAI_API_ERROR",
                details={"model": model, "batch_size": len(texts)}
            )
        except Exception as e:
            logger.error(f"Unexpected error during batch embedding generation: {e}")
            raise EmbeddingServiceError(
                f"Unexpected error: {e}",
                error_code="UNEXPECTED_ERROR"
            )
    
    async def get_embedding_dimensions(self, model: str = "text-embedding-3-small") -> int:
        """Get the dimensions of embeddings for a specific model."""
        if model not in self.MODEL_CONFIG:
            raise EmbeddingServiceModelError(f"Model '{model}' is not supported", model)
        
        return self.MODEL_CONFIG[model]["dimensions"]
    
    async def calculate_similarity(self, 
                                 embedding1: List[float], 
                                 embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            if len(embedding1) != len(embedding2):
                raise EmbeddingServiceError(
                    "Embeddings must have the same dimensions",
                    error_code="DIMENSION_MISMATCH"
                )
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            
            # Calculate magnitudes
            magnitude1 = math.sqrt(sum(a * a for a in embedding1))
            magnitude2 = math.sqrt(sum(b * b for b in embedding2))
            
            # Calculate cosine similarity
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            raise EmbeddingServiceError(
                f"Error calculating similarity: {e}",
                error_code="SIMILARITY_CALCULATION_ERROR"
            )
    
    async def is_model_available(self, model: str) -> bool:
        """Check if a specific embedding model is available."""
        return model in self.MODEL_CONFIG
    
    async def get_available_models(self) -> List[str]:
        """Get list of available embedding models."""
        return list(self.MODEL_CONFIG.keys())
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific embedding model."""
        if model not in self.MODEL_CONFIG:
            raise EmbeddingServiceModelError(f"Model '{model}' is not supported", model)
        
        return self.MODEL_CONFIG[model].copy()
    
    async def estimate_cost(self, 
                          texts: List[str], 
                          model: str = "text-embedding-3-small") -> Decimal:
        """Estimate the cost of embedding generation for given texts."""
        if model not in self.MODEL_CONFIG:
            raise EmbeddingServiceModelError(f"Model '{model}' is not supported", model)
        
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        total_chars = sum(len(text) for text in texts)
        estimated_tokens = total_chars / 4
        
        # Get cost per 1k tokens
        cost_per_1k = self.MODEL_CONFIG[model]["cost_per_1k_tokens"]
        
        # Calculate total cost
        total_cost = Decimal(str(estimated_tokens * cost_per_1k / 1000))
        
        return total_cost
    
    def _prepare_text(self, text: str, model: str) -> str:
        """Prepare text for embedding generation."""
        # Basic text cleaning
        text = text.strip()
        if not text:
            return " "  # OpenAI doesn't like empty strings
        
        # Get max tokens for model
        max_tokens = self.MODEL_CONFIG[model]["max_tokens"]
        
        # Rough truncation (1 token ≈ 4 characters)
        max_chars = max_tokens * 4
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            logger.warning(f"Text truncated to {max_chars} characters for model {model}")
        
        return text
    
    async def _check_rate_limits(self):
        """Check if we're within rate limits."""
        # Simple rate limiting check
        # In a production environment, you might want more sophisticated rate limiting
        current_time = datetime.now()
        
        # Clean old entries
        cutoff_time = current_time - timedelta(minutes=1)
        self.rate_limit_tracker = {
            k: v for k, v in self.rate_limit_tracker.items() 
            if v > cutoff_time
        }
        
        # Check if we're making too many requests
        if len(self.rate_limit_tracker) > 100:  # Conservative limit
            logger.warning("Rate limit protection: delaying request")
            await asyncio.sleep(1)
    
    def _update_rate_limit_tracker(self, response):
        """Update rate limit tracking with response information."""
        # Generate a unique ID for this request
        request_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()
        self.rate_limit_tracker[request_id] = datetime.now()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the OpenAI service."""
        try:
            # Try to get available models
            models = await self.get_available_models()
            
            # Test with a simple embedding
            test_embedding = await self.generate_embedding("test", "text-embedding-3-small")
            
            return {
                "status": "healthy",
                "available_models": models,
                "test_embedding_dimensions": len(test_embedding),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 