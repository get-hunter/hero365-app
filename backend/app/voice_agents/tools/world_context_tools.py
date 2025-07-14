"""
World context tools for voice agents - weather, maps, web search functionality.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp
from urllib.parse import quote

from ...core.config import settings

logger = logging.getLogger(__name__)


class WorldContextTools:
    """World context tools providing weather, maps, and web search capabilities."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.weather_api_key = settings.OPENWEATHER_API_KEY
        self.google_maps_api_key = settings.GOOGLE_MAPS_API_KEY
        self.serpapi_key = settings.SERPAPI_KEY
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_weather(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get current weather information for a location.
        
        Args:
            location: City name or coordinates
            units: Temperature units (metric, imperial, kelvin)
            
        Returns:
            Weather information dict
        """
        try:
            if not self.weather_api_key:
                return {
                    "error": "Weather API key not configured",
                    "voice_response": "I'm sorry, weather information is not available right now. The weather service needs to be configured."
                }
            
            session = await self._get_session()
            
            # Get current weather
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": self.weather_api_key,
                "units": units
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse weather data
                    weather_info = {
                        "location": data["name"],
                        "country": data["sys"]["country"],
                        "temperature": data["main"]["temp"],
                        "feels_like": data["main"]["feels_like"],
                        "humidity": data["main"]["humidity"],
                        "pressure": data["main"]["pressure"],
                        "description": data["weather"][0]["description"],
                        "wind_speed": data["wind"]["speed"],
                        "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                        "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
                        "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M"),
                        "units": units
                    }
                    
                    # Create voice-friendly response
                    temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
                    voice_response = (
                        f"The current weather in {weather_info['location']} is "
                        f"{weather_info['temperature']}{temp_unit} with {weather_info['description']}. "
                        f"It feels like {weather_info['feels_like']}{temp_unit}. "
                        f"Humidity is {weather_info['humidity']}% and wind speed is {weather_info['wind_speed']} meters per second."
                    )
                    
                    return {
                        "success": True,
                        "data": weather_info,
                        "voice_response": voice_response
                    }
                else:
                    error_data = await response.json()
                    return {
                        "error": f"Weather API error: {error_data.get('message', 'Unknown error')}",
                        "voice_response": f"I couldn't get weather information for {location}. Please check the location name and try again."
                    }
                    
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return {
                "error": f"Weather service error: {str(e)}",
                "voice_response": "I'm having trouble getting weather information right now. Please try again later."
            }
    
    async def get_weather_forecast(self, location: str, days: int = 5, units: str = "metric") -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            location: City name or coordinates
            days: Number of days for forecast (1-5)
            units: Temperature units (metric, imperial, kelvin)
            
        Returns:
            Weather forecast dict
        """
        try:
            if not self.weather_api_key:
                return {
                    "error": "Weather API key not configured",
                    "voice_response": "Weather forecast is not available right now."
                }
            
            session = await self._get_session()
            
            # Get forecast
            url = f"https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": location,
                "appid": self.weather_api_key,
                "units": units,
                "cnt": days * 8  # 8 forecasts per day (every 3 hours)
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Group forecasts by day
                    daily_forecasts = {}
                    for forecast in data["list"]:
                        date = datetime.fromtimestamp(forecast["dt"]).date()
                        if date not in daily_forecasts:
                            daily_forecasts[date] = []
                        daily_forecasts[date].append(forecast)
                    
                    # Create summary for each day
                    forecast_summary = []
                    for date, forecasts in list(daily_forecasts.items())[:days]:
                        temps = [f["main"]["temp"] for f in forecasts]
                        descriptions = [f["weather"][0]["description"] for f in forecasts]
                        
                        day_summary = {
                            "date": date.strftime("%Y-%m-%d"),
                            "day_name": date.strftime("%A"),
                            "min_temp": min(temps),
                            "max_temp": max(temps),
                            "description": max(set(descriptions), key=descriptions.count),
                            "humidity": sum(f["main"]["humidity"] for f in forecasts) // len(forecasts)
                        }
                        forecast_summary.append(day_summary)
                    
                    # Create voice response
                    temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
                    voice_parts = [f"Here's the weather forecast for {location}:"]
                    
                    for day in forecast_summary:
                        voice_parts.append(
                            f"{day['day_name']}: {day['description']}, "
                            f"high {day['max_temp']}{temp_unit}, low {day['min_temp']}{temp_unit}"
                        )
                    
                    return {
                        "success": True,
                        "data": {
                            "location": data["city"]["name"],
                            "country": data["city"]["country"],
                            "forecast": forecast_summary,
                            "units": units
                        },
                        "voice_response": ". ".join(voice_parts)
                    }
                else:
                    error_data = await response.json()
                    return {
                        "error": f"Weather API error: {error_data.get('message', 'Unknown error')}",
                        "voice_response": f"I couldn't get the weather forecast for {location}."
                    }
                    
        except Exception as e:
            logger.error(f"Error getting weather forecast: {e}")
            return {
                "error": f"Weather forecast error: {str(e)}",
                "voice_response": "I'm having trouble getting the weather forecast right now."
            }
    
    async def get_directions(self, origin: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
        """
        Get directions between two locations.
        
        Args:
            origin: Starting location
            destination: Ending location
            mode: Travel mode (driving, walking, bicycling, transit)
            
        Returns:
            Directions information dict
        """
        try:
            if not self.google_maps_api_key:
                return {
                    "error": "Google Maps API key not configured",
                    "voice_response": "Directions are not available right now. The maps service needs to be configured."
                }
            
            session = await self._get_session()
            
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "key": self.google_maps_api_key
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data["status"] == "OK" and data["routes"]:
                        route = data["routes"][0]
                        leg = route["legs"][0]
                        
                        directions_info = {
                            "origin": leg["start_address"],
                            "destination": leg["end_address"],
                            "distance": leg["distance"]["text"],
                            "duration": leg["duration"]["text"],
                            "mode": mode,
                            "steps": []
                        }
                        
                        # Extract key steps
                        for step in leg["steps"]:
                            directions_info["steps"].append({
                                "instruction": step["html_instructions"],
                                "distance": step["distance"]["text"],
                                "duration": step["duration"]["text"]
                            })
                        
                        voice_response = (
                            f"The route from {directions_info['origin']} to {directions_info['destination']} "
                            f"is {directions_info['distance']} and takes about {directions_info['duration']} "
                            f"by {mode}."
                        )
                        
                        return {
                            "success": True,
                            "data": directions_info,
                            "voice_response": voice_response
                        }
                    else:
                        return {
                            "error": f"Directions error: {data.get('status', 'Unknown error')}",
                            "voice_response": f"I couldn't find directions from {origin} to {destination}. Please check the locations and try again."
                        }
                else:
                    return {
                        "error": f"Google Maps API error: {response.status}",
                        "voice_response": "I'm having trouble getting directions right now."
                    }
                    
        except Exception as e:
            logger.error(f"Error getting directions: {e}")
            return {
                "error": f"Directions error: {str(e)}",
                "voice_response": "I'm having trouble getting directions right now. Please try again later."
            }
    
    async def search_places(self, query: str, location: str = None, radius: int = 5000) -> Dict[str, Any]:
        """
        Search for places near a location.
        
        Args:
            query: Search query (e.g., "restaurants", "gas stations")
            location: Location to search near
            radius: Search radius in meters
            
        Returns:
            Places search results dict
        """
        try:
            if not self.google_maps_api_key:
                return {
                    "error": "Google Maps API key not configured",
                    "voice_response": "Place search is not available right now."
                }
            
            session = await self._get_session()
            
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query,
                "key": self.google_maps_api_key
            }
            
            if location:
                params["location"] = location
                params["radius"] = radius
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data["status"] == "OK":
                        places = []
                        for place in data["results"][:5]:  # Limit to top 5 results
                            place_info = {
                                "name": place["name"],
                                "address": place.get("formatted_address", ""),
                                "rating": place.get("rating", 0),
                                "price_level": place.get("price_level", 0),
                                "types": place.get("types", [])
                            }
                            places.append(place_info)
                        
                        voice_response = f"I found {len(places)} places for '{query}'"
                        if location:
                            voice_response += f" near {location}"
                        voice_response += ". "
                        
                        if places:
                            voice_response += "Here are the top results: "
                            for i, place in enumerate(places[:3], 1):
                                voice_response += f"{i}. {place['name']}"
                                if place['rating'] > 0:
                                    voice_response += f" with {place['rating']} stars"
                                voice_response += ". "
                        
                        return {
                            "success": True,
                            "data": {
                                "query": query,
                                "location": location,
                                "places": places
                            },
                            "voice_response": voice_response
                        }
                    else:
                        return {
                            "error": f"Places API error: {data.get('status', 'Unknown error')}",
                            "voice_response": f"I couldn't find any places for '{query}'. Please try a different search."
                        }
                else:
                    return {
                        "error": f"Google Places API error: {response.status}",
                        "voice_response": "I'm having trouble searching for places right now."
                    }
                    
        except Exception as e:
            logger.error(f"Error searching places: {e}")
            return {
                "error": f"Places search error: {str(e)}",
                "voice_response": "I'm having trouble searching for places right now. Please try again later."
            }
    
    async def web_search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Perform web search using SerpAPI.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Web search results dict
        """
        try:
            if not self.serpapi_key:
                return {
                    "error": "SerpAPI key not configured",
                    "voice_response": "Web search is not available right now. The search service needs to be configured."
                }
            
            session = await self._get_session()
            
            url = "https://serpapi.com/search.json"
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "engine": "google",
                "num": num_results
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "organic_results" in data:
                        results = []
                        for result in data["organic_results"]:
                            result_info = {
                                "title": result.get("title", ""),
                                "link": result.get("link", ""),
                                "snippet": result.get("snippet", ""),
                                "displayed_link": result.get("displayed_link", "")
                            }
                            results.append(result_info)
                        
                        voice_response = f"I found {len(results)} search results for '{query}'. "
                        if results:
                            voice_response += "Here are the top results: "
                            for i, result in enumerate(results[:3], 1):
                                voice_response += f"{i}. {result['title']}. {result['snippet'][:100]}... "
                        
                        return {
                            "success": True,
                            "data": {
                                "query": query,
                                "results": results,
                                "total_results": len(results)
                            },
                            "voice_response": voice_response
                        }
                    else:
                        return {
                            "error": "No search results found",
                            "voice_response": f"I couldn't find any search results for '{query}'. Please try a different search term."
                        }
                else:
                    return {
                        "error": f"Search API error: {response.status}",
                        "voice_response": "I'm having trouble searching the web right now."
                    }
                    
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return {
                "error": f"Web search error: {str(e)}",
                "voice_response": "I'm having trouble searching the web right now. Please try again later."
            }
    
    async def get_business_hours(self, business_name: str, location: str = None) -> Dict[str, Any]:
        """
        Get business hours for a specific business.
        
        Args:
            business_name: Name of the business
            location: Location to search in
            
        Returns:
            Business hours information dict
        """
        try:
            if not self.google_maps_api_key:
                return {
                    "error": "Google Maps API key not configured",
                    "voice_response": "Business hours information is not available right now."
                }
            
            session = await self._get_session()
            
            # Search for the business
            query = business_name
            if location:
                query += f" {location}"
            
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query,
                "key": self.google_maps_api_key
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data["status"] == "OK" and data["results"]:
                        place = data["results"][0]
                        place_id = place["place_id"]
                        
                        # Get detailed place information
                        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                        details_params = {
                            "place_id": place_id,
                            "fields": "name,formatted_address,opening_hours,formatted_phone_number",
                            "key": self.google_maps_api_key
                        }
                        
                        async with session.get(details_url, params=details_params) as details_response:
                            if details_response.status == 200:
                                details_data = await details_response.json()
                                
                                if details_data["status"] == "OK":
                                    result = details_data["result"]
                                    
                                    business_info = {
                                        "name": result.get("name", business_name),
                                        "address": result.get("formatted_address", ""),
                                        "phone": result.get("formatted_phone_number", ""),
                                        "hours": result.get("opening_hours", {}).get("weekday_text", []),
                                        "open_now": result.get("opening_hours", {}).get("open_now", False)
                                    }
                                    
                                    # Create voice response
                                    voice_response = f"I found information for {business_info['name']}. "
                                    if business_info['open_now']:
                                        voice_response += "They are currently open. "
                                    else:
                                        voice_response += "They are currently closed. "
                                    
                                    if business_info['hours']:
                                        voice_response += "Their hours are: "
                                        for hour in business_info['hours']:
                                            voice_response += f"{hour}. "
                                    
                                    return {
                                        "success": True,
                                        "data": business_info,
                                        "voice_response": voice_response
                                    }
                    
                    return {
                        "error": f"Business not found: {business_name}",
                        "voice_response": f"I couldn't find information for {business_name}. Please check the business name and try again."
                    }
                else:
                    return {
                        "error": f"Google Places API error: {response.status}",
                        "voice_response": "I'm having trouble getting business information right now."
                    }
                    
        except Exception as e:
            logger.error(f"Error getting business hours: {e}")
            return {
                "error": f"Business hours error: {str(e)}",
                "voice_response": "I'm having trouble getting business hours right now. Please try again later."
            }


# Global instance
world_context_tools = WorldContextTools() 