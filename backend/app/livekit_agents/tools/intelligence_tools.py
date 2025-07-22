"""
Business Intelligence Tools for Hero365 LiveKit Agents
"""

import logging
from typing import Dict, Any, Optional
from livekit.agents import function_tool

from ..context import BusinessContextManager

logger = logging.getLogger(__name__)

# SerpAPI for web search
try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False
    logger.warning("SerpAPI not available. Web search will use fallback responses.")

# Configuration
from ..config import LiveKitConfig


class IntelligenceTools:
    """Business intelligence tools for the Hero365 agent"""
    
    def __init__(self, business_context: Dict[str, Any], business_context_manager: Optional[BusinessContextManager] = None):
        self.business_context = business_context
        self.business_context_manager = business_context_manager
    
    @function_tool
    async def get_weather(self, location: Optional[str] = None) -> str:
        """Get current weather information with business context awareness.
        
        Args:
            location: Location to get weather for (if not provided, uses business location)
        """
        try:
            # Use business location as default if available
            if not location and self.business_context_manager:
                business_context = self.business_context_manager.get_business_context()
                if business_context and business_context.address:
                    location = business_context.address
            
            logger.info(f"🌤️ Getting weather for: {location or 'current location'}")
            
            # Simulate weather info (replace with actual API call)
            response = f"Current weather in {location or 'your area'}: 72°F, partly cloudy with light winds."
            
            # Add context-aware suggestions for outdoor jobs
            if self.business_context_manager:
                upcoming_jobs = self.business_context_manager.get_recent_jobs(5)
                outdoor_jobs = [j for j in upcoming_jobs if any(word in j.title.lower() for word in ["exterior", "outdoor", "roof", "siding", "landscape"])]
                
                if outdoor_jobs:
                    response += f"\n🔧 Weather impact: {len(outdoor_jobs)} outdoor jobs might be affected"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error getting weather: {e}")
            return f"❌ Error getting weather: {str(e)}"

    @function_tool
    async def search_places(
        self,
        query: str,
        location: Optional[str] = None,
        radius: int = 5000
    ) -> str:
        """Search for places nearby with business context awareness.
        
        Args:
            query: What to search for (e.g., "hardware store", "restaurant")
            location: Location to search near (if not provided, uses business location)
            radius: Search radius in meters
        """
        try:
            # Use business location as default if available
            if not location and self.business_context_manager:
                business_context = self.business_context_manager.get_business_context()
                if business_context and business_context.address:
                    location = business_context.address
            
            logger.info(f"🔍 Searching for {query} near {location or 'current location'}")
            
            # Simulate places search (replace with actual API call)
            response = f"Found several {query} locations within {radius} meters of {location or 'your area'}."
            
            # Add context-aware suggestions
            if "supply" in query.lower() or "hardware" in query.lower():
                if self.business_context_manager:
                    suggestions = self.business_context_manager.get_contextual_suggestions()
                    if suggestions and suggestions.quick_actions:
                        response += f"\n💡 For current jobs: {suggestions.quick_actions[0]}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error searching places: {e}")
            return f"❌ Error searching places: {str(e)}"

    @function_tool
    async def get_directions(
        self,
        destination: str,
        origin: Optional[str] = None,
        mode: str = "driving"
    ) -> str:
        """Get directions with business context awareness.
        
        Args:
            destination: Where to go
            origin: Starting point (if not provided, uses business location)
            mode: Travel mode (driving, walking, transit)
        """
        try:
            # Use business location as default origin if available
            if not origin and self.business_context_manager:
                business_context = self.business_context_manager.get_business_context()
                if business_context and business_context.address:
                    origin = business_context.address
            
            logger.info(f"🗺️ Getting directions from {origin or 'current location'} to {destination}")
            
            # Simulate directions (replace with actual API call)
            response = f"Directions from {origin or 'your location'} to {destination}: Take the main route, approximately 15 minutes by {mode}."
            
            # Add context-aware job suggestions
            if self.business_context_manager:
                # Check if destination matches any job locations
                recent_jobs = self.business_context_manager.get_recent_jobs(10)
                matching_jobs = [j for j in recent_jobs if j.location and destination.lower() in j.location.lower()]
                
                if matching_jobs:
                    response += f"\n🔧 Related jobs at this location: {matching_jobs[0].title}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error getting directions: {e}")
            return f"❌ Error getting directions: {str(e)}"

    @function_tool
    async def universal_search(self, query: str, limit: int = 10) -> str:
        """Context-aware universal search across all Hero365 data.
        
        Args:
            query: Search query
            limit: Maximum number of results per category
        """
        try:
            logger.info(f"🔍 Universal search for: {query}")
            
            # Check business context for quick matches
            context_results = []
            if self.business_context_manager:
                contact_match = self.business_context_manager.find_contact_by_name(query)
                if contact_match:
                    context_results.append(f"📞 Recent contact: {contact_match.name}")
                
                job_match = self.business_context_manager.find_job_by_title(query)
                if job_match:
                    context_results.append(f"🔧 Recent job: {job_match.title}")
                
                estimate_match = self.business_context_manager.find_estimate_by_title(query)
                if estimate_match:
                    context_results.append(f"📊 Recent estimate: {estimate_match.title}")
            
            # Simulate universal search results (replace with actual API call)
            total_count = 3
            contacts = [{"name": f"Contact {query}", "phone": "555-0001"}]
            jobs = [{"title": f"Job {query}", "status": "active"}]
            estimates = [{"title": f"Estimate {query}", "status": "draft"}]
            
            response = ""
            
            # Add context results first
            if context_results:
                response += f"🎯 Quick matches from recent activity:\n"
                for context_result in context_results:
                    response += f"• {context_result}\n"
                response += "\n"
            
            if total_count > 0:
                response += f"🔍 Found {total_count} total results for '{query}':\n"
                
                # Contacts
                if contacts:
                    response += f"\n📞 Contacts ({len(contacts)}):\n"
                    for contact in contacts:
                        response += f"• {contact['name']}\n"
                
                # Jobs
                if jobs:
                    response += f"\n🔧 Jobs ({len(jobs)}):\n"
                    for job in jobs:
                        response += f"• {job['title']}\n"
                
                # Estimates
                if estimates:
                    response += f"\n📋 Estimates ({len(estimates)}):\n"
                    for estimate in estimates:
                        response += f"• {estimate['title']}\n"
                
                return response
            else:
                if context_results:
                    return response + f"No additional results found for '{query}'"
                else:
                    return f"🔍 No results found for '{query}'"
                
        except Exception as e:
            logger.error(f"❌ Error in universal search: {e}")
            return f"❌ Error in search: {str(e)}"

    @function_tool
    async def get_business_analytics(self, period: str = "month") -> str:
        """Get business analytics with contextual insights.
        
        Args:
            period: Time period for analytics (day, week, month, year)
        """
        try:
            logger.info(f"📊 Getting business analytics for: {period}")
            
            # Add business context summary
            context_summary = ""
            if self.business_context_manager:
                business_summary = self.business_context_manager.get_business_summary()
                if business_summary:
                    context_summary = f"Current snapshot: {business_summary.active_jobs} active jobs, {business_summary.pending_estimates} pending estimates. "
            
            # Simulate analytics data (replace with actual API call)
            response = context_summary + f"Business analytics for {period}: "
            analytics_parts = []
            analytics_parts.append("total jobs fifteen")
            analytics_parts.append("completed jobs ten") 
            analytics_parts.append("total revenue twenty five thousand dollars")
            analytics_parts.append("pending estimates five")
            analytics_parts.append("overdue invoices two")
            
            response += ", ".join(analytics_parts)
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.urgent_items:
                    response += f". Urgent attention needed: {suggestions.urgent_items[0]}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")
            return f"Error getting analytics: {str(e)}"

    @function_tool
    async def get_contextual_insights(self) -> str:
        """Get contextual business insights and suggestions based on current state."""
        try:
            logger.info("🔍 Getting contextual insights")
            
            if not self.business_context_manager:
                return "Business context not available for insights"
            
            business_summary = self.business_context_manager.get_business_summary()
            suggestions = self.business_context_manager.get_contextual_suggestions()
            
            if not business_summary:
                return "No business data available for insights"
            
            response = f"Business insights: "
            insight_parts = []
            insight_parts.append(f"overview shows {business_summary.active_jobs} active jobs and {business_summary.pending_estimates} pending estimates")
            insight_parts.append(f"this week you have {business_summary.jobs_this_week} jobs scheduled")
            
            if suggestions:
                if suggestions.urgent_items:
                    urgent_list = []
                    for item in suggestions.urgent_items[:3]:
                        urgent_list.append(item)
                    insight_parts.append(f"urgent items include {', '.join(urgent_list)}")
                
                if suggestions.quick_actions:
                    action_list = []
                    for action in suggestions.quick_actions[:3]:
                        action_list.append(action)
                    insight_parts.append(f"quick actions you can take are {', '.join(action_list)}")
                
                if suggestions.opportunities:
                    opp_list = []
                    for opportunity in suggestions.opportunities[:3]:
                        opp_list.append(opportunity)
                    insight_parts.append(f"opportunities available are {', '.join(opp_list)}")
            
            response += ". ".join(insight_parts)
            return response
            
        except Exception as e:
            logger.error(f"❌ Error getting contextual insights: {e}")
            return f"Error getting contextual insights: {str(e)}"

    @function_tool
    async def web_search(self, query: str, num_results: int = 5) -> str:
        """Perform real web search using SerpAPI with business context awareness.
        
        Args:
            query: Search query
            num_results: Number of results to return (max 10)
        """
        try:
            logger.info(f"🌐 Web search for: {query}")
            
            if not SERPAPI_AVAILABLE or not LiveKitConfig.SERPAPI_KEY:
                logger.warning("SerpAPI not available or API key missing")
                return f"I searched the web for {query} but I'm having trouble accessing search results right now. The information might include recent updates, industry news, or current market trends related to your query."
            
            # Perform actual web search using SerpAPI
            search_params = {
                "q": query,
                "api_key": LiveKitConfig.SERPAPI_KEY,
                "num": min(num_results, 10),  # Limit to 10 results max
                "hl": "en",
                "gl": "us"
            }
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            if "error" in results:
                logger.error(f"SerpAPI error: {results['error']}")
                return f"I searched for {query} but encountered an issue with the search service. Please try again in a moment."
            
            organic_results = results.get("organic_results", [])
            
            if not organic_results:
                return f"I searched the web for {query} but didn't find specific results. You might want to try different search terms."
            
            # Format results for voice in a natural, conversational way
            response_parts = []
            response_parts.append(f"I found information about {query}")
            
            # Add top results in a voice-friendly format
            for i, result in enumerate(organic_results[:3], 1):
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                
                if snippet:
                    # Clean up snippet for better voice readability
                    clean_snippet = snippet.replace("...", "").strip()
                    if clean_snippet:
                        if i == 1:
                            response_parts.append(f"According to {title}, {clean_snippet}")
                        else:
                            response_parts.append(f"Also, {clean_snippet}")
            
            # Add business context awareness
            business_keywords = ["contractor", "service", "repair", "installation", "home", "business", "plumbing", "electrical", "HVAC"]
            if any(keyword in query.lower() for keyword in business_keywords):
                if self.business_context_manager:
                    suggestions = self.business_context_manager.get_contextual_suggestions()
                    if suggestions and suggestions.quick_actions:
                        response_parts.append(f"This might be relevant for {suggestions.quick_actions[0]}")
            
            response = ". ".join(response_parts)
            
            # Ensure response is not too long for voice
            if len(response) > 500:
                # Truncate but maintain natural speech flow
                response = response[:450] + "... and more details are available if you need them"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error in web search: {e}")
            return f"I tried to search for {query} but encountered an issue. Please let me know if you'd like me to try again."

    @function_tool
    async def get_business_recommendations(self) -> str:
        """Get AI-powered business recommendations based on current context"""
        try:
            logger.info("💡 Getting business recommendations")
            
            if not self.business_context_manager:
                return "Business context not available for recommendations"
            
            business_summary = self.business_context_manager.get_business_summary()
            if not business_summary:
                return "No business data available for recommendations"
            
            recommendations = []
            
            # Basic recommendations based on business state
            if business_summary.pending_estimates > 5:
                recommendations.append("consider following up on your pending estimates to improve conversion rates")
            
            if business_summary.active_jobs > 10:
                recommendations.append("with your current workload, you might want to consider hiring additional help")
            
            if not recommendations:
                recommendations.append("your business metrics look good, keep up the great work")
            
            response = f"Based on your current business status, I recommend you {', and '.join(recommendations)}"
            return response
            
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {e}")
            return f"Error getting business recommendations: {str(e)}" 