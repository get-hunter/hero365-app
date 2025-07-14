"""
Health check system for voice agents infrastructure.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import aiohttp
import json
from enum import Enum

from ...core.config import settings
from .voice_metrics import voice_metrics

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheck:
    """Base class for health checks."""
    
    def __init__(self, name: str, timeout: int = 30):
        self.name = name
        self.timeout = timeout
        self.last_check = None
        self.last_status = HealthStatus.UNKNOWN
        self.last_error = None
    
    async def check(self) -> Dict[str, Any]:
        """Perform health check. Should be implemented by subclasses."""
        raise NotImplementedError
    
    async def run_check(self) -> Dict[str, Any]:
        """Run the health check with timeout and error handling."""
        try:
            result = await asyncio.wait_for(self.check(), timeout=self.timeout)
            self.last_check = datetime.now()
            self.last_status = HealthStatus(result.get("status", "unknown"))
            self.last_error = None
            return result
        except asyncio.TimeoutError:
            error_result = {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Health check timed out after {self.timeout} seconds",
                "timestamp": datetime.now().isoformat()
            }
            self.last_status = HealthStatus.UNHEALTHY
            self.last_error = "timeout"
            return error_result
        except Exception as e:
            error_result = {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            self.last_status = HealthStatus.UNHEALTHY
            self.last_error = str(e)
            return error_result


class RedisHealthCheck(HealthCheck):
    """Health check for Redis connection."""
    
    def __init__(self):
        super().__init__("redis", timeout=10)
    
    async def check(self) -> Dict[str, Any]:
        """Check Redis connection and basic functionality."""
        try:
            import redis.asyncio as redis
            
            # Create Redis client
            redis_client = redis.from_url(settings.REDIS_URL)
            
            # Test basic operations
            test_key = "health_check_test"
            test_value = "ok"
            
            # Set a test value
            await redis_client.set(test_key, test_value, ex=60)
            
            # Get the test value
            result = await redis_client.get(test_key)
            
            # Clean up
            await redis_client.delete(test_key)
            await redis_client.close()
            
            if result and result.decode() == test_value:
                return {
                    "status": HealthStatus.HEALTHY.value,
                    "message": "Redis connection successful",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": "Redis test operation failed",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Redis connection failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


class OpenAIHealthCheck(HealthCheck):
    """Health check for OpenAI API."""
    
    def __init__(self):
        super().__init__("openai", timeout=30)
    
    async def check(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity."""
        try:
            if not settings.OPENAI_API_KEY:
                return {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": "OpenAI API key not configured",
                    "timestamp": datetime.now().isoformat()
                }
            
            import openai
            
            # Test a simple API call
            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Test with a minimal completion
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            if response.choices and response.choices[0].message:
                return {
                    "status": HealthStatus.HEALTHY.value,
                    "message": "OpenAI API connection successful",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": HealthStatus.DEGRADED.value,
                    "message": "OpenAI API responded but with unexpected format",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"OpenAI API connection failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


class SupabaseHealthCheck(HealthCheck):
    """Health check for Supabase connection."""
    
    def __init__(self):
        super().__init__("supabase", timeout=15)
    
    async def check(self) -> Dict[str, Any]:
        """Check Supabase connection."""
        try:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                return {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": "Supabase configuration missing",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Test Supabase connection with a simple query
            async with aiohttp.ClientSession() as session:
                headers = {
                    "apikey": settings.SUPABASE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_KEY}"
                }
                
                url = f"{settings.SUPABASE_URL}/rest/v1/businesses?select=count"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return {
                            "status": HealthStatus.HEALTHY.value,
                            "message": "Supabase connection successful",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": HealthStatus.UNHEALTHY.value,
                            "message": f"Supabase returned status {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Supabase connection failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


class WorldContextHealthCheck(HealthCheck):
    """Health check for world context tools (weather, maps, search)."""
    
    def __init__(self):
        super().__init__("world_context", timeout=20)
    
    async def check(self) -> Dict[str, Any]:
        """Check world context tools availability."""
        try:
            services = {
                "weather": settings.OPENWEATHER_API_KEY,
                "maps": settings.GOOGLE_MAPS_API_KEY,
                "search": settings.SERPAPI_KEY
            }
            
            available_services = []
            for service, api_key in services.items():
                if api_key:
                    available_services.append(service)
            
            if len(available_services) == 0:
                return {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": "No world context services configured",
                    "services": available_services,
                    "timestamp": datetime.now().isoformat()
                }
            elif len(available_services) < len(services):
                return {
                    "status": HealthStatus.DEGRADED.value,
                    "message": f"Some world context services unavailable",
                    "services": available_services,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": HealthStatus.HEALTHY.value,
                    "message": "All world context services configured",
                    "services": available_services,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"World context check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


class VoiceSystemHealthCheck(HealthCheck):
    """Health check for voice system overall health."""
    
    def __init__(self):
        super().__init__("voice_system", timeout=5)
    
    async def check(self) -> Dict[str, Any]:
        """Check voice system health based on metrics."""
        try:
            # Get current metrics from voice metrics collector
            metrics = voice_metrics.get_health_status()
            
            return {
                "status": metrics["status"],
                "message": f"Voice system is {metrics['status']}",
                "details": {
                    "active_sessions": metrics["active_sessions"],
                    "recent_errors": metrics["recent_errors"],
                    "error_rate": metrics["error_rate_percent"],
                    "avg_response_time": metrics["avg_response_time_seconds"],
                    "uptime": metrics["uptime_seconds"]
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Voice system health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }


class VoiceAgentHealthMonitor:
    """Main health monitor for voice agent system."""
    
    def __init__(self):
        self.checks = {
            "redis": RedisHealthCheck(),
            "openai": OpenAIHealthCheck(),
            "supabase": SupabaseHealthCheck(),
            "world_context": WorldContextHealthCheck(),
            "voice_system": VoiceSystemHealthCheck()
        }
        self.last_full_check = None
    
    async def run_single_check(self, check_name: str) -> Dict[str, Any]:
        """Run a single health check."""
        if check_name not in self.checks:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": f"Unknown health check: {check_name}",
                "timestamp": datetime.now().isoformat()
            }
        
        return await self.checks[check_name].run_check()
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        overall_status = HealthStatus.HEALTHY
        
        # Run all checks in parallel
        tasks = {
            name: asyncio.create_task(check.run_check())
            for name, check in self.checks.items()
        }
        
        for name, task in tasks.items():
            try:
                result = await task
                results[name] = result
                
                # Update overall status
                check_status = HealthStatus(result.get("status", "unknown"))
                if check_status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif check_status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            except Exception as e:
                results[name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": f"Health check failed: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                overall_status = HealthStatus.UNHEALTHY
        
        self.last_full_check = datetime.now()
        
        return {
            "overall_status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "checks": results,
            "summary": {
                "total_checks": len(self.checks),
                "healthy": len([r for r in results.values() if r.get("status") == HealthStatus.HEALTHY.value]),
                "degraded": len([r for r in results.values() if r.get("status") == HealthStatus.DEGRADED.value]),
                "unhealthy": len([r for r in results.values() if r.get("status") == HealthStatus.UNHEALTHY.value])
            }
        }
    
    async def get_quick_status(self) -> Dict[str, Any]:
        """Get a quick status without running all checks."""
        return {
            "overall_status": "unknown",
            "message": "Run full health check for detailed status",
            "last_full_check": self.last_full_check.isoformat() if self.last_full_check else None,
            "timestamp": datetime.now().isoformat()
        }


# Global health monitor instance
health_monitor = VoiceAgentHealthMonitor() 