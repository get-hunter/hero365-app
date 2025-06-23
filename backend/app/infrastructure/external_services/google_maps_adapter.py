"""
Google Maps API Adapter

External service adapter for Google Maps API integration providing
real-time travel time calculations and route optimization.
"""

import asyncio
import aiohttp
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
import json
import logging

from ...application.ports.external_services import RouteOptimizationPort, TravelTimePort
from ...domain.exceptions.domain_exceptions import DomainValidationError
from ...core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class Location:
    """Location value object for coordinates."""
    latitude: float
    longitude: float
    address: Optional[str] = None
    
    def to_string(self) -> str:
        """Convert to Google Maps API format."""
        return f"{self.latitude},{self.longitude}"


@dataclass
class TravelTimeResult:
    """Result of travel time calculation."""
    distance_km: Decimal
    duration_minutes: Decimal
    duration_in_traffic_minutes: Optional[Decimal] = None
    route_polyline: Optional[str] = None
    traffic_conditions: Optional[str] = None
    alternative_routes_count: int = 0


@dataclass
class OptimizedRoute:
    """Optimized route with waypoints."""
    total_distance_km: Decimal
    total_duration_minutes: Decimal
    waypoints_order: List[int]  # Optimized order of waypoints
    route_legs: List[Dict[str, Any]]
    estimated_fuel_cost: Optional[Decimal] = None
    traffic_warnings: List[str] = None


class GoogleMapsAdapter:
    """
    Google Maps API adapter for travel time and route optimization.
    
    Provides real-time travel data, route optimization, and traffic-aware
    scheduling capabilities for Hero365's intelligent scheduling system.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("Google Maps API key not configured. Real-time optimization will be limited.")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_travel_time(self, 
                             origin: Location, 
                             destination: Location,
                             departure_time: Optional[datetime] = None,
                             traffic_model: str = "best_guess") -> TravelTimeResult:
        """
        Get travel time between two locations with real-time traffic data.
        
        Args:
            origin: Starting location
            destination: End location
            departure_time: When the trip will start (for traffic prediction)
            traffic_model: Traffic prediction model (best_guess, pessimistic, optimistic)
            
        Returns:
            TravelTimeResult with distance, duration, and traffic info
        """
        try:
            if not self.api_key:
                # Fallback to Haversine calculation
                return await self._fallback_travel_time(origin, destination)
            
            # Prepare API request
            url = f"{self.base_url}/distancematrix/json"
            params = {
                "origins": origin.to_string(),
                "destinations": destination.to_string(),
                "key": self.api_key,
                "units": "metric",
                "traffic_model": traffic_model,
                "departure_time": self._format_departure_time(departure_time)
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Google Maps API error: {response.status}")
                    return await self._fallback_travel_time(origin, destination)
                
                data = await response.json()
                return self._parse_distance_matrix_response(data)
                
        except Exception as e:
            logger.error(f"Error getting travel time: {str(e)}")
            return await self._fallback_travel_time(origin, destination)
    
    async def get_optimal_route(self, 
                               start: Location,
                               end: Location,
                               waypoints: List[Location],
                               optimize_waypoints: bool = True) -> OptimizedRoute:
        """
        Get optimized route through multiple waypoints.
        
        Args:
            start: Starting location
            end: Ending location  
            waypoints: Intermediate locations to visit
            optimize_waypoints: Whether to optimize waypoint order
            
        Returns:
            OptimizedRoute with optimized waypoint order and route details
        """
        try:
            if not self.api_key or not waypoints:
                return await self._fallback_route_optimization(start, end, waypoints)
            
            # Prepare waypoints string
            waypoints_str = "|".join([wp.to_string() for wp in waypoints])
            if optimize_waypoints:
                waypoints_str = f"optimize:true|{waypoints_str}"
            
            url = f"{self.base_url}/directions/json"
            params = {
                "origin": start.to_string(),
                "destination": end.to_string(),
                "waypoints": waypoints_str,
                "key": self.api_key,
                "traffic_model": "best_guess",
                "departure_time": "now"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Google Directions API error: {response.status}")
                    return await self._fallback_route_optimization(start, end, waypoints)
                
                data = await response.json()
                return self._parse_directions_response(data, len(waypoints))
                
        except Exception as e:
            logger.error(f"Error optimizing route: {str(e)}")
            return await self._fallback_route_optimization(start, end, waypoints)
    
    async def get_travel_time_matrix(self, 
                                   origins: List[Location],
                                   destinations: List[Location],
                                   departure_time: Optional[datetime] = None) -> Dict[Tuple[int, int], TravelTimeResult]:
        """
        Get travel times between multiple origins and destinations.
        
        Args:
            origins: List of starting locations
            destinations: List of destination locations
            departure_time: When trips will start
            
        Returns:
            Dictionary mapping (origin_index, destination_index) to TravelTimeResult
        """
        try:
            if not self.api_key:
                return await self._fallback_travel_matrix(origins, destinations)
            
            # Google Maps API has limits, so batch if necessary
            results = {}
            batch_size = 10  # API limit per request
            
            for i in range(0, len(origins), batch_size):
                origin_batch = origins[i:i + batch_size]
                
                for j in range(0, len(destinations), batch_size):
                    dest_batch = destinations[j:j + batch_size]
                    
                    batch_results = await self._get_matrix_batch(
                        origin_batch, dest_batch, departure_time, i, j
                    )
                    results.update(batch_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting travel time matrix: {str(e)}")
            return await self._fallback_travel_matrix(origins, destinations)
    
    async def get_traffic_conditions(self, 
                                   location: Location,
                                   radius_km: float = 5.0) -> Dict[str, Any]:
        """
        Get current traffic conditions around a location.
        
        Args:
            location: Center location for traffic check
            radius_km: Radius to check for traffic conditions
            
        Returns:
            Traffic conditions data
        """
        try:
            # This would use Google Maps Roads API or Traffic API
            # For now, return basic traffic simulation
            return {
                "traffic_level": "moderate",
                "incidents": [],
                "average_speed_kmh": 35,
                "congestion_areas": []
            }
            
        except Exception as e:
            logger.error(f"Error getting traffic conditions: {str(e)}")
            return {"traffic_level": "unknown", "incidents": []}
    
    def _format_departure_time(self, departure_time: Optional[datetime]) -> str:
        """Format departure time for Google Maps API."""
        if departure_time is None:
            return "now"
        
        # Convert to Unix timestamp
        timestamp = int(departure_time.timestamp())
        return str(timestamp)
    
    def _parse_distance_matrix_response(self, data: Dict) -> TravelTimeResult:
        """Parse Google Distance Matrix API response."""
        try:
            if data["status"] != "OK":
                raise DomainValidationError(f"Google Maps API error: {data['status']}")
            
            element = data["rows"][0]["elements"][0]
            
            if element["status"] != "OK":
                raise DomainValidationError(f"Route calculation failed: {element['status']}")
            
            distance_km = Decimal(str(element["distance"]["value"] / 1000))
            duration_minutes = Decimal(str(element["duration"]["value"] / 60))
            
            # Check for traffic data
            duration_in_traffic = None
            if "duration_in_traffic" in element:
                duration_in_traffic = Decimal(str(element["duration_in_traffic"]["value"] / 60))
            
            return TravelTimeResult(
                distance_km=distance_km,
                duration_minutes=duration_minutes,
                duration_in_traffic_minutes=duration_in_traffic,
                traffic_conditions="moderate" if duration_in_traffic else None
            )
            
        except Exception as e:
            logger.error(f"Error parsing distance matrix response: {str(e)}")
            raise DomainValidationError("Failed to parse travel time data")
    
    def _parse_directions_response(self, data: Dict, waypoint_count: int) -> OptimizedRoute:
        """Parse Google Directions API response."""
        try:
            if data["status"] != "OK":
                raise DomainValidationError(f"Google Directions API error: {data['status']}")
            
            route = data["routes"][0]
            
            # Extract optimized waypoint order
            waypoints_order = []
            if "waypoint_order" in route:
                waypoints_order = route["waypoint_order"]
            else:
                waypoints_order = list(range(waypoint_count))
            
            # Calculate totals
            total_distance = sum(leg["distance"]["value"] for leg in route["legs"])
            total_duration = sum(leg["duration"]["value"] for leg in route["legs"])
            
            # Extract route legs
            route_legs = []
            for leg in route["legs"]:
                route_legs.append({
                    "distance_km": leg["distance"]["value"] / 1000,
                    "duration_minutes": leg["duration"]["value"] / 60,
                    "start_address": leg["start_address"],
                    "end_address": leg["end_address"]
                })
            
            return OptimizedRoute(
                total_distance_km=Decimal(str(total_distance / 1000)),
                total_duration_minutes=Decimal(str(total_duration / 60)),
                waypoints_order=waypoints_order,
                route_legs=route_legs
            )
            
        except Exception as e:
            logger.error(f"Error parsing directions response: {str(e)}")
            raise DomainValidationError("Failed to parse route optimization data")
    
    async def _get_matrix_batch(self, 
                               origins: List[Location],
                               destinations: List[Location],
                               departure_time: Optional[datetime],
                               origin_offset: int,
                               dest_offset: int) -> Dict[Tuple[int, int], TravelTimeResult]:
        """Get travel time matrix for a batch of origins and destinations."""
        origins_str = "|".join([loc.to_string() for loc in origins])
        destinations_str = "|".join([loc.to_string() for loc in destinations])
        
        url = f"{self.base_url}/distancematrix/json"
        params = {
            "origins": origins_str,
            "destinations": destinations_str,
            "key": self.api_key,
            "units": "metric",
            "departure_time": self._format_departure_time(departure_time)
        }
        
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            
            results = {}
            for i, row in enumerate(data["rows"]):
                for j, element in enumerate(row["elements"]):
                    if element["status"] == "OK":
                        distance_km = Decimal(str(element["distance"]["value"] / 1000))
                        duration_minutes = Decimal(str(element["duration"]["value"] / 60))
                        
                        results[(origin_offset + i, dest_offset + j)] = TravelTimeResult(
                            distance_km=distance_km,
                            duration_minutes=duration_minutes
                        )
            
            return results
    
    async def _fallback_travel_time(self, origin: Location, destination: Location) -> TravelTimeResult:
        """Fallback travel time calculation using Haversine formula."""
        from ...domain.entities.scheduling_engine import TravelTimeCalculation
        
        distance_km = TravelTimeCalculation.calculate_haversine_distance(
            origin.latitude, origin.longitude,
            destination.latitude, destination.longitude
        )
        
        # Estimate travel time (assuming 30 km/h average speed)
        duration_minutes = TravelTimeCalculation.estimate_travel_time(distance_km)
        
        return TravelTimeResult(
            distance_km=distance_km,
            duration_minutes=duration_minutes
        )
    
    async def _fallback_route_optimization(self, 
                                         start: Location,
                                         end: Location,
                                         waypoints: List[Location]) -> OptimizedRoute:
        """Fallback route optimization using simple nearest neighbor."""
        if not waypoints:
            travel_result = await self._fallback_travel_time(start, end)
            return OptimizedRoute(
                total_distance_km=travel_result.distance_km,
                total_duration_minutes=travel_result.duration_minutes,
                waypoints_order=[],
                route_legs=[]
            )
        
        # Simple nearest neighbor optimization
        current_location = start
        remaining_waypoints = list(enumerate(waypoints))
        optimized_order = []
        total_distance = Decimal("0")
        total_duration = Decimal("0")
        route_legs = []
        
        while remaining_waypoints:
            # Find nearest waypoint
            nearest_idx = 0
            nearest_distance = float('inf')
            
            for i, (orig_idx, waypoint) in enumerate(remaining_waypoints):
                dist_result = await self._fallback_travel_time(current_location, waypoint)
                if float(dist_result.distance_km) < nearest_distance:
                    nearest_distance = float(dist_result.distance_km)
                    nearest_idx = i
            
            # Move to nearest waypoint
            orig_idx, nearest_waypoint = remaining_waypoints.pop(nearest_idx)
            optimized_order.append(orig_idx)
            
            travel_result = await self._fallback_travel_time(current_location, nearest_waypoint)
            total_distance += travel_result.distance_km
            total_duration += travel_result.duration_minutes
            
            route_legs.append({
                "distance_km": float(travel_result.distance_km),
                "duration_minutes": float(travel_result.duration_minutes),
                "start_address": f"{current_location.latitude},{current_location.longitude}",
                "end_address": f"{nearest_waypoint.latitude},{nearest_waypoint.longitude}"
            })
            
            current_location = nearest_waypoint
        
        # Final leg to destination
        final_travel = await self._fallback_travel_time(current_location, end)
        total_distance += final_travel.distance_km
        total_duration += final_travel.duration_minutes
        
        route_legs.append({
            "distance_km": float(final_travel.distance_km),
            "duration_minutes": float(final_travel.duration_minutes),
            "start_address": f"{current_location.latitude},{current_location.longitude}",
            "end_address": f"{end.latitude},{end.longitude}"
        })
        
        return OptimizedRoute(
            total_distance_km=total_distance,
            total_duration_minutes=total_duration,
            waypoints_order=optimized_order,
            route_legs=route_legs
        )
    
    async def _fallback_travel_matrix(self, 
                                    origins: List[Location],
                                    destinations: List[Location]) -> Dict[Tuple[int, int], TravelTimeResult]:
        """Fallback travel matrix using Haversine calculations."""
        results = {}
        
        for i, origin in enumerate(origins):
            for j, destination in enumerate(destinations):
                travel_result = await self._fallback_travel_time(origin, destination)
                results[(i, j)] = travel_result
        
        return results


# Factory function for dependency injection
def create_google_maps_adapter() -> GoogleMapsAdapter:
    """Create Google Maps adapter instance."""
    return GoogleMapsAdapter() 