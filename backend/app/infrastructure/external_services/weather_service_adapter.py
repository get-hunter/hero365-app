"""
Weather Service Adapter

External service adapter for weather API integration providing
weather impact analysis for intelligent job scheduling.
"""

import asyncio
import aiohttp
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
import logging
from pydantic import BaseModel, Field

from ...application.ports.external_services import WeatherServicePort
from ...domain.exceptions.domain_exceptions import DomainValidationError
from ...core.config import settings

logger = logging.getLogger(__name__)


class WeatherCondition(Enum):
    """Weather condition categories."""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    LIGHT_RAIN = "light_rain"
    HEAVY_RAIN = "heavy_rain"
    SNOW = "snow"
    STORM = "storm"
    FOG = "fog"
    EXTREME_HEAT = "extreme_heat"
    EXTREME_COLD = "extreme_cold"


class WeatherImpactLevel(Enum):
    """Impact levels of weather on job scheduling."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class WeatherData(BaseModel):
    """Weather data for a specific location and time."""
    temperature_celsius: float
    humidity_percent: float
    wind_speed_kmh: float
    precipitation_mm: float
    condition: WeatherCondition
    visibility_km: float
    uv_index: Optional[float] = None
    air_quality_index: Optional[int] = None


class WeatherImpact(BaseModel):
    """Weather impact analysis for job scheduling."""
    impact_level: WeatherImpactLevel
    affected_job_types: List[str]
    recommended_actions: List[str]
    safety_concerns: List[str]
    schedule_adjustment_minutes: int
    work_feasibility_score: Decimal  # 0-1 scale
    
    def is_work_safe(self) -> bool:
        """Check if weather conditions are safe for work."""
        return self.impact_level not in [WeatherImpactLevel.HIGH, WeatherImpactLevel.SEVERE]
    
    def requires_rescheduling(self) -> bool:
        """Check if weather requires job rescheduling."""
        return self.impact_level == WeatherImpactLevel.SEVERE


class WeatherForecast(BaseModel):
    """Weather forecast for scheduling optimization."""
    location_lat: float
    location_lng: float
    forecast_time: datetime
    weather_data: WeatherData
    impact_analysis: WeatherImpact


class WeatherServiceAdapter:
    """
    Weather service adapter for job scheduling optimization.
    
    Provides weather data and impact analysis to help optimize
    job scheduling based on weather conditions and forecasts.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.WEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("Weather API key not configured. Weather-based optimization will be limited.")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_current_weather(self, latitude: float, longitude: float) -> WeatherData:
        """
        Get current weather conditions for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            WeatherData with current conditions
        """
        try:
            if not self.api_key:
                return self._get_default_weather()
            
            url = f"{self.base_url}/weather"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Weather API error: {response.status}")
                    return self._get_default_weather()
                
                data = await response.json()
                return self._parse_current_weather(data)
                
        except Exception as e:
            logger.error(f"Error getting current weather: {str(e)}")
            return self._get_default_weather()
    
    async def get_weather_forecast(self, 
                                 latitude: float, 
                                 longitude: float,
                                 hours_ahead: int = 24) -> List[WeatherForecast]:
        """
        Get weather forecast for scheduling optimization.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            hours_ahead: Hours to forecast ahead
            
        Returns:
            List of WeatherForecast objects
        """
        try:
            if not self.api_key:
                return self._get_default_forecast(latitude, longitude, hours_ahead)
            
            url = f"{self.base_url}/forecast"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Weather forecast API error: {response.status}")
                    return self._get_default_forecast(latitude, longitude, hours_ahead)
                
                data = await response.json()
                return self._parse_weather_forecast(data, latitude, longitude, hours_ahead)
                
        except Exception as e:
            logger.error(f"Error getting weather forecast: {str(e)}")
            return self._get_default_forecast(latitude, longitude, hours_ahead)
    
    async def get_weather_impact(self, 
                               latitude: float, 
                               longitude: float,
                               job_type: str,
                               scheduled_time: datetime) -> WeatherImpact:
        """
        Analyze weather impact on a specific job.
        
        Args:
            latitude: Job location latitude
            longitude: Job location longitude
            job_type: Type of job being scheduled
            scheduled_time: When the job is scheduled
            
        Returns:
            WeatherImpact analysis
        """
        try:
            # Get weather data for the scheduled time
            if scheduled_time <= datetime.utcnow() + timedelta(hours=1):
                # Current weather
                weather_data = await self.get_current_weather(latitude, longitude)
            else:
                # Forecast weather
                forecasts = await self.get_weather_forecast(latitude, longitude, 48)
                weather_data = self._find_closest_forecast(forecasts, scheduled_time)
            
            # Analyze impact based on job type and weather
            return self._analyze_weather_impact(weather_data, job_type)
            
        except Exception as e:
            logger.error(f"Error analyzing weather impact: {str(e)}")
            return self._get_default_impact()
    
    async def get_optimal_weather_window(self,
                                       latitude: float,
                                       longitude: float,
                                       job_type: str,
                                       start_time: datetime,
                                       end_time: datetime) -> Optional[datetime]:
        """
        Find the optimal time window with best weather conditions.
        
        Args:
            latitude: Job location latitude
            longitude: Job location longitude
            job_type: Type of job
            start_time: Earliest possible start time
            end_time: Latest possible end time
            
        Returns:
            Optimal start time or None if no good window exists
        """
        try:
            # Get forecast for the time range
            hours_ahead = int((end_time - datetime.utcnow()).total_seconds() / 3600)
            forecasts = await self.get_weather_forecast(latitude, longitude, hours_ahead)
            
            best_time = None
            best_score = Decimal("0")
            
            # Evaluate each forecast window
            for forecast in forecasts:
                if start_time <= forecast.forecast_time <= end_time:
                    if forecast.impact_analysis.work_feasibility_score > best_score:
                        best_score = forecast.impact_analysis.work_feasibility_score
                        best_time = forecast.forecast_time
            
            return best_time
            
        except Exception as e:
            logger.error(f"Error finding optimal weather window: {str(e)}")
            return start_time  # Fallback to original time
    
    def _parse_current_weather(self, data: Dict) -> WeatherData:
        """Parse OpenWeatherMap current weather response."""
        main = data["main"]
        weather = data["weather"][0]
        wind = data.get("wind", {})
        
        # Map weather condition
        condition = self._map_weather_condition(weather["main"], weather["description"])
        
        return WeatherData(
            temperature_celsius=main["temp"],
            humidity_percent=main["humidity"],
            wind_speed_kmh=wind.get("speed", 0) * 3.6,  # Convert m/s to km/h
            precipitation_mm=data.get("rain", {}).get("1h", 0) + data.get("snow", {}).get("1h", 0),
            condition=condition,
            visibility_km=data.get("visibility", 10000) / 1000,  # Convert m to km
            uv_index=data.get("uvi"),
        )
    
    def _parse_weather_forecast(self, 
                              data: Dict, 
                              latitude: float, 
                              longitude: float,
                              hours_ahead: int) -> List[WeatherForecast]:
        """Parse OpenWeatherMap forecast response."""
        forecasts = []
        
        for item in data["list"]:
            forecast_time = datetime.fromtimestamp(item["dt"])
            
            # Only include forecasts within our time window
            if forecast_time <= datetime.utcnow() + timedelta(hours=hours_ahead):
                weather_data = self._parse_forecast_item(item)
                impact_analysis = self._analyze_weather_impact(weather_data, "general")
                
                forecasts.append(WeatherForecast(
                    location_lat=latitude,
                    location_lng=longitude,
                    forecast_time=forecast_time,
                    weather_data=weather_data,
                    impact_analysis=impact_analysis
                ))
        
        return forecasts
    
    def _parse_forecast_item(self, item: Dict) -> WeatherData:
        """Parse individual forecast item."""
        main = item["main"]
        weather = item["weather"][0]
        wind = item.get("wind", {})
        
        condition = self._map_weather_condition(weather["main"], weather["description"])
        
        return WeatherData(
            temperature_celsius=main["temp"],
            humidity_percent=main["humidity"],
            wind_speed_kmh=wind.get("speed", 0) * 3.6,
            precipitation_mm=item.get("rain", {}).get("3h", 0) + item.get("snow", {}).get("3h", 0),
            condition=condition,
            visibility_km=item.get("visibility", 10000) / 1000,
        )
    
    def _map_weather_condition(self, main: str, description: str) -> WeatherCondition:
        """Map OpenWeatherMap conditions to our enum."""
        main = main.lower()
        description = description.lower()
        
        if main == "clear":
            return WeatherCondition.CLEAR
        elif main == "clouds":
            return WeatherCondition.CLOUDY
        elif main == "rain":
            if "light" in description:
                return WeatherCondition.LIGHT_RAIN
            else:
                return WeatherCondition.HEAVY_RAIN
        elif main == "snow":
            return WeatherCondition.SNOW
        elif main == "thunderstorm":
            return WeatherCondition.STORM
        elif main in ["mist", "fog", "haze"]:
            return WeatherCondition.FOG
        else:
            return WeatherCondition.CLOUDY
    
    def _analyze_weather_impact(self, weather_data: WeatherData, job_type: str) -> WeatherImpact:
        """Analyze weather impact on job scheduling."""
        impact_level = WeatherImpactLevel.NONE
        affected_job_types = []
        recommended_actions = []
        safety_concerns = []
        schedule_adjustment = 0
        feasibility_score = Decimal("1.0")
        
        # Temperature impact
        if weather_data.temperature_celsius < -10:
            impact_level = WeatherImpactLevel.HIGH
            safety_concerns.append("Extreme cold conditions")
            schedule_adjustment += 30
            feasibility_score -= Decimal("0.3")
        elif weather_data.temperature_celsius > 35:
            impact_level = WeatherImpactLevel.MODERATE
            safety_concerns.append("High temperature - ensure hydration")
            schedule_adjustment += 15
            feasibility_score -= Decimal("0.2")
        
        # Precipitation impact
        if weather_data.condition == WeatherCondition.HEAVY_RAIN:
            impact_level = WeatherImpactLevel.HIGH
            affected_job_types.extend(["electrical", "roofing", "painting"])
            recommended_actions.append("Consider rescheduling outdoor work")
            schedule_adjustment += 45
            feasibility_score -= Decimal("0.4")
        elif weather_data.condition == WeatherCondition.LIGHT_RAIN:
            impact_level = max(impact_level, WeatherImpactLevel.LOW)
            affected_job_types.extend(["painting", "roofing"])
            recommended_actions.append("Bring weather protection equipment")
            schedule_adjustment += 15
            feasibility_score -= Decimal("0.1")
        
        # Snow impact
        if weather_data.condition == WeatherCondition.SNOW:
            impact_level = WeatherImpactLevel.HIGH
            affected_job_types.extend(["roofing", "electrical", "plumbing"])
            safety_concerns.append("Slippery conditions - use caution")
            recommended_actions.append("Allow extra travel time")
            schedule_adjustment += 60
            feasibility_score -= Decimal("0.5")
        
        # Storm impact
        if weather_data.condition == WeatherCondition.STORM:
            impact_level = WeatherImpactLevel.SEVERE
            affected_job_types = ["all"]
            safety_concerns.append("Dangerous weather conditions")
            recommended_actions.append("Reschedule all outdoor work")
            schedule_adjustment += 120
            feasibility_score = Decimal("0.1")
        
        # Wind impact
        if weather_data.wind_speed_kmh > 50:
            impact_level = max(impact_level, WeatherImpactLevel.HIGH)
            affected_job_types.extend(["roofing", "tree_service"])
            safety_concerns.append("High wind conditions")
            schedule_adjustment += 30
            feasibility_score -= Decimal("0.3")
        
        # Visibility impact
        if weather_data.visibility_km < 1:
            impact_level = max(impact_level, WeatherImpactLevel.MODERATE)
            safety_concerns.append("Poor visibility conditions")
            recommended_actions.append("Use extra lighting and caution")
            schedule_adjustment += 20
            feasibility_score -= Decimal("0.2")
        
        # Job-specific adjustments
        if job_type in ["electrical", "roofing"] and weather_data.precipitation_mm > 0:
            impact_level = max(impact_level, WeatherImpactLevel.MODERATE)
        
        # Ensure feasibility score is within bounds
        feasibility_score = max(Decimal("0"), min(Decimal("1"), feasibility_score))
        
        return WeatherImpact(
            impact_level=impact_level,
            affected_job_types=list(set(affected_job_types)),
            recommended_actions=recommended_actions,
            safety_concerns=safety_concerns,
            schedule_adjustment_minutes=schedule_adjustment,
            work_feasibility_score=feasibility_score
        )
    
    def _find_closest_forecast(self, forecasts: List[WeatherForecast], target_time: datetime) -> WeatherData:
        """Find the forecast closest to the target time."""
        if not forecasts:
            return self._get_default_weather()
        
        closest_forecast = min(
            forecasts,
            key=lambda f: abs((f.forecast_time - target_time).total_seconds())
        )
        
        return closest_forecast.weather_data
    
    def _get_default_weather(self) -> WeatherData:
        """Get default weather data when API is unavailable."""
        return WeatherData(
            temperature_celsius=20.0,
            humidity_percent=50.0,
            wind_speed_kmh=10.0,
            precipitation_mm=0.0,
            condition=WeatherCondition.CLEAR,
            visibility_km=10.0
        )
    
    def _get_default_forecast(self, 
                            latitude: float, 
                            longitude: float, 
                            hours_ahead: int) -> List[WeatherForecast]:
        """Get default forecast when API is unavailable."""
        forecasts = []
        base_time = datetime.utcnow()
        
        for i in range(0, hours_ahead, 3):  # 3-hour intervals
            forecast_time = base_time + timedelta(hours=i)
            weather_data = self._get_default_weather()
            impact_analysis = self._get_default_impact()
            
            forecasts.append(WeatherForecast(
                location_lat=latitude,
                location_lng=longitude,
                forecast_time=forecast_time,
                weather_data=weather_data,
                impact_analysis=impact_analysis
            ))
        
        return forecasts
    
    def _get_default_impact(self) -> WeatherImpact:
        """Get default weather impact when analysis is unavailable."""
        return WeatherImpact(
            impact_level=WeatherImpactLevel.NONE,
            affected_job_types=[],
            recommended_actions=[],
            safety_concerns=[],
            schedule_adjustment_minutes=0,
            work_feasibility_score=Decimal("1.0")
        )


# Factory function for dependency injection
def create_weather_service_adapter() -> WeatherServiceAdapter:
    """Create weather service adapter instance."""
    return WeatherServiceAdapter() 