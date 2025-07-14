"""
Cache manager for voice agent responses to optimize performance.
"""

import asyncio
import json
import hashlib
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from ...core.config import settings

logger = logging.getLogger(__name__)


class VoiceAgentCacheManager:
    """Cache manager for voice agent responses using Redis"""
    
    def __init__(self):
        """Initialize cache manager with Redis connection"""
        self.redis_client = None
        self.fallback_cache = {}  # In-memory fallback
        self.cache_ttl = {
            "transcription": 300,  # 5 minutes
            "tts_response": 1800,  # 30 minutes
            "agent_response": 600,  # 10 minutes
            "common_queries": 3600  # 1 hour
        }
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            if settings.REDIS_URL:
                self.redis_client = AsyncRedis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                logger.info("✅ Voice agent cache initialized with Redis")
            else:
                logger.warning("⚠️ Redis URL not configured, using in-memory cache")
                
        except ImportError as e:
            logger.error(f"❌ Redis package not available: {e}")
            logger.info("📝 Using in-memory cache only")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis: {e}")
            logger.info("📝 Falling back to in-memory cache")
    
    def _generate_cache_key(self, prefix: str, data: str, user_id: str = None) -> str:
        """Generate cache key with hash for consistent lookup"""
        # Create hash of the data for consistent key generation
        data_hash = hashlib.sha256(data.encode()).hexdigest()[:16]
        
        if user_id:
            return f"voice_agent:{prefix}:{user_id}:{data_hash}"
        else:
            return f"voice_agent:{prefix}:{data_hash}"
    
    async def get_cached_response(self, 
                                 cache_type: str, 
                                 key_data: str, 
                                 user_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get cached response from Redis or fallback cache.
        
        Args:
            cache_type: Type of cache (transcription, tts_response, agent_response, common_queries)
            key_data: Data to generate cache key from
            user_id: Optional user ID for user-specific caching
            
        Returns:
            Cached response data or None if not found
        """
        try:
            cache_key = self._generate_cache_key(cache_type, key_data, user_id)
            
            if self.redis_client:
                # Try Redis first
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    logger.info(f"✅ Cache hit for {cache_type}: {cache_key}")
                    return json.loads(cached_data)
            
            # Fallback to in-memory cache
            if cache_key in self.fallback_cache:
                cached_item = self.fallback_cache[cache_key]
                
                # Check if expired
                if datetime.now() < cached_item["expires_at"]:
                    logger.info(f"✅ In-memory cache hit for {cache_type}: {cache_key}")
                    return cached_item["data"]
                else:
                    # Remove expired item
                    del self.fallback_cache[cache_key]
            
            logger.debug(f"❌ Cache miss for {cache_type}: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting cached response: {e}")
            return None
    
    async def set_cached_response(self, 
                                 cache_type: str, 
                                 key_data: str, 
                                 response_data: Dict[str, Any], 
                                 user_id: str = None,
                                 custom_ttl: int = None) -> bool:
        """
        Set cached response in Redis and fallback cache.
        
        Args:
            cache_type: Type of cache
            key_data: Data to generate cache key from
            response_data: Response data to cache
            user_id: Optional user ID for user-specific caching
            custom_ttl: Custom TTL in seconds
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(cache_type, key_data, user_id)
            ttl = custom_ttl or self.cache_ttl.get(cache_type, 600)
            
            # Add metadata to cached response
            cached_item = {
                "data": response_data,
                "cached_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat(),
                "cache_type": cache_type
            }
            
            if self.redis_client:
                # Set in Redis with TTL
                await self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(cached_item, ensure_ascii=False)
                )
                logger.info(f"✅ Cached response in Redis for {cache_type}: {cache_key}")
            
            # Also set in fallback cache
            self.fallback_cache[cache_key] = {
                "data": response_data,
                "expires_at": datetime.now() + timedelta(seconds=ttl)
            }
            
            # Clean up old entries in fallback cache
            await self._cleanup_fallback_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting cached response: {e}")
            return False
    
    async def cache_transcription(self, audio_hash: str, transcription: str) -> bool:
        """Cache audio transcription result"""
        response_data = {
            "transcription": transcription,
            "audio_hash": audio_hash
        }
        return await self.set_cached_response("transcription", audio_hash, response_data)
    
    async def get_cached_transcription(self, audio_hash: str) -> Optional[str]:
        """Get cached transcription"""
        cached_data = await self.get_cached_response("transcription", audio_hash)
        return cached_data["data"]["transcription"] if cached_data else None
    
    async def cache_tts_response(self, text: str, voice: str, audio_data: bytes) -> bool:
        """Cache TTS response"""
        response_data = {
            "text": text,
            "voice": voice,
            "audio_size": len(audio_data),
            "audio_data": audio_data.hex()  # Store as hex string to avoid encoding issues
        }
        cache_key = f"{text}:{voice}"
        return await self.set_cached_response("tts_response", cache_key, response_data)
    
    async def get_cached_tts_response(self, text: str, voice: str) -> Optional[bytes]:
        """Get cached TTS response"""
        cache_key = f"{text}:{voice}"
        cached_data = await self.get_cached_response("tts_response", cache_key)
        if cached_data:
            return bytes.fromhex(cached_data["data"]["audio_data"])
        return None
    
    async def cache_agent_response(self, query: str, response: str, user_id: str) -> bool:
        """Cache agent response for user-specific queries"""
        response_data = {
            "query": query,
            "response": response,
            "user_id": user_id
        }
        return await self.set_cached_response("agent_response", query, response_data, user_id)
    
    async def get_cached_agent_response(self, query: str, user_id: str) -> Optional[str]:
        """Get cached agent response"""
        cached_data = await self.get_cached_response("agent_response", query, user_id)
        return cached_data["data"]["response"] if cached_data else None
    
    async def cache_common_query(self, query: str, response: str) -> bool:
        """Cache response for common queries that don't require user context"""
        response_data = {
            "query": query,
            "response": response
        }
        return await self.set_cached_response("common_queries", query, response_data)
    
    async def get_cached_common_query(self, query: str) -> Optional[str]:
        """Get cached common query response"""
        cached_data = await self.get_cached_response("common_queries", query)
        return cached_data["data"]["response"] if cached_data else None
    
    async def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate all cached responses for a specific user"""
        try:
            if self.redis_client:
                # Find all keys for this user
                pattern = f"voice_agent:*:{user_id}:*"
                keys = await self.redis_client.keys(pattern)
                
                if keys:
                    await self.redis_client.delete(*keys)
                    logger.info(f"✅ Invalidated {len(keys)} cached responses for user {user_id}")
                
            # Also clear from fallback cache
            keys_to_remove = [
                key for key in self.fallback_cache.keys()
                if f":{user_id}:" in key
            ]
            
            for key in keys_to_remove:
                del self.fallback_cache[key]
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Error invalidating user cache: {e}")
            return False
    
    async def _cleanup_fallback_cache(self):
        """Clean up expired entries from fallback cache"""
        try:
            now = datetime.now()
            expired_keys = [
                key for key, item in self.fallback_cache.items()
                if now >= item["expires_at"]
            ]
            
            for key in expired_keys:
                del self.fallback_cache[key]
                
            if expired_keys:
                logger.debug(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            logger.error(f"❌ Error cleaning up fallback cache: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "fallback_cache_size": len(self.fallback_cache),
            "redis_connected": bool(self.redis_client),
            "cache_ttl": self.cache_ttl
        }
        
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                stats["redis_info"] = {
                    "used_memory": info.get("used_memory_human", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                }
            except Exception as e:
                stats["redis_error"] = str(e)
        
        return stats
    
    async def clear_all_cache(self) -> bool:
        """Clear all cached responses (use with caution)"""
        try:
            if self.redis_client:
                # Clear all voice agent keys
                pattern = "voice_agent:*"
                keys = await self.redis_client.keys(pattern)
                
                if keys:
                    await self.redis_client.delete(*keys)
                    logger.info(f"✅ Cleared {len(keys)} cached responses from Redis")
            
            # Clear fallback cache
            self.fallback_cache.clear()
            logger.info("✅ Cleared all fallback cache entries")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error clearing cache: {e}")
            return False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("✅ Voice agent cache manager closed")


# Global cache manager instance
cache_manager = VoiceAgentCacheManager() 