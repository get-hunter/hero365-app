"""
External Services Ports

Port interfaces for external services following the ports and adapters pattern.
These define contracts for external integrations without implementation details.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal


class RouteOptimizationPort(ABC):
    """Port interface for route optimization services."""
    
    @abstractmethod
    async def get_optimal_route(self, 
                               start_location: Dict[str, float],
                               end_location: Dict[str, float],
                               waypoints: List[Dict[str, float]],
                               optimize_waypoints: bool = True) -> Dict[str, Any]:
        """Get optimized route through multiple waypoints."""
        pass
    
    @abstractmethod
    async def get_travel_time_matrix(self,
                                   origins: List[Dict[str, float]],
                                   destinations: List[Dict[str, float]],
                                   departure_time: Optional[datetime] = None) -> Dict[Tuple[int, int], Dict[str, Any]]:
        """Get travel times between multiple origins and destinations."""
        pass


class TravelTimePort(ABC):
    """Port interface for travel time calculation services."""
    
    @abstractmethod
    async def get_travel_time(self,
                             origin: Dict[str, float],
                             destination: Dict[str, float],
                             departure_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get travel time between two locations."""
        pass
    
    @abstractmethod
    async def get_traffic_conditions(self,
                                   location: Dict[str, float],
                                   radius_km: float = 5.0) -> Dict[str, Any]:
        """Get current traffic conditions around a location."""
        pass


class WeatherServicePort(ABC):
    """Port interface for weather services."""
    
    @abstractmethod
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get current weather conditions for a location."""
        pass
    
    @abstractmethod
    async def get_weather_forecast(self,
                                 latitude: float,
                                 longitude: float,
                                 hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """Get weather forecast for scheduling optimization."""
        pass
    
    @abstractmethod
    async def get_weather_impact(self,
                               latitude: float,
                               longitude: float,
                               job_type: str,
                               scheduled_time: datetime) -> Dict[str, Any]:
        """Analyze weather impact on a specific job."""
        pass


class NotificationServicePort(ABC):
    """Port interface for notification services."""
    
    @abstractmethod
    async def send_schedule_notification(self,
                                       user_id: str,
                                       message: str,
                                       notification_type: str = "schedule_update") -> bool:
        """Send schedule update notification to user."""
        pass
    
    @abstractmethod
    async def send_bulk_notifications(self,
                                    notifications: List[Dict[str, Any]]) -> Dict[str, int]:
        """Send multiple notifications efficiently."""
        pass


class GeolocationServicePort(ABC):
    """Port interface for geolocation services."""
    
    @abstractmethod
    async def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """Convert address to coordinates."""
        pass
    
    @abstractmethod
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """Convert coordinates to address."""
        pass 