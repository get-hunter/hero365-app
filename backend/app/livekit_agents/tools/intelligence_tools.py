"""
Business Intelligence Tools for Hero365 LiveKit Agents
"""

import logging
from typing import Dict, Any, Optional
from livekit.agents import function_tool

from ..context import BusinessContextManager

logger = logging.getLogger(__name__)


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
                    context_summary = f"📊 Current snapshot: {business_summary.active_jobs} active jobs, {business_summary.pending_estimates} pending estimates\n\n"
            
            # Simulate analytics data (replace with actual API call)
            response = context_summary + f"📊 Business Analytics for {period}:\n"
            response += f"• Total Jobs: 15\n"
            response += f"• Completed Jobs: 10\n"
            response += f"• Total Revenue: $25,000.00\n"
            response += f"• Pending Estimates: 5\n"
            response += f"• Overdue Invoices: 2\n"
            
            # Add contextual suggestions
            if self.business_context_manager:
                suggestions = self.business_context_manager.get_contextual_suggestions()
                if suggestions and suggestions.urgent_items:
                    response += f"\n🔥 Urgent attention needed: {suggestions.urgent_items[0]}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")
            return f"❌ Error getting analytics: {str(e)}"

    @function_tool
    async def get_contextual_insights(self) -> str:
        """Get contextual business insights and suggestions based on current state."""
        try:
            logger.info("🔍 Getting contextual insights")
            
            if not self.business_context_manager:
                return "🔍 Business context not available for insights"
            
            business_summary = self.business_context_manager.get_business_summary()
            suggestions = self.business_context_manager.get_contextual_suggestions()
            
            if not business_summary:
                return "🔍 No business data available for insights"
            
            response = f"🔍 Business Insights:\n"
            response += f"📊 Overview: {business_summary.active_jobs} active jobs, {business_summary.pending_estimates} pending estimates\n"
            response += f"📅 This week: {business_summary.jobs_this_week} jobs scheduled\n"
            
            if suggestions:
                if suggestions.urgent_items:
                    response += f"\n🔥 Urgent items:\n"
                    for item in suggestions.urgent_items[:3]:
                        response += f"• {item}\n"
                
                if suggestions.quick_actions:
                    response += f"\n⚡ Quick actions:\n"
                    for action in suggestions.quick_actions[:3]:
                        response += f"• {action}\n"
                
                if suggestions.opportunities:
                    response += f"\n💡 Opportunities:\n"
                    for opportunity in suggestions.opportunities[:3]:
                        response += f"• {opportunity}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error getting contextual insights: {e}")
            return f"❌ Error getting contextual insights: {str(e)}"

    @function_tool
    async def web_search(self, query: str, num_results: int = 5) -> str:
        """Perform web search with business context awareness.
        
        Args:
            query: Search query
            num_results: Number of results to return
        """
        try:
            logger.info(f"🌐 Web search for: {query}")
            
            # Simulate web search (replace with actual API call)
            response = f"I found information about {query}. Here are the key details from my search results."
            
            # Add context-aware suggestions for business-related searches
            if any(word in query.lower() for word in ["contractor", "service", "repair", "installation"]):
                if self.business_context_manager:
                    suggestions = self.business_context_manager.get_contextual_suggestions()
                    if suggestions and suggestions.quick_actions:
                        response += f"\n💡 Related to your business: {suggestions.quick_actions[0]}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error searching web: {e}")
            return f"❌ Error searching web: {str(e)}"

    @function_tool
    async def get_business_recommendations(self) -> str:
        """Get AI-powered business recommendations based on current context."""
        try:
            logger.info("🤖 Getting business recommendations")
            
            if not self.business_context_manager:
                return "🤖 Business context not available for recommendations"
            
            business_summary = self.business_context_manager.get_business_summary()
            suggestions = self.business_context_manager.get_contextual_suggestions()
            
            if not business_summary:
                return "🤖 No business data available for recommendations"
            
            response = f"🤖 AI Business Recommendations:\n"
            
            # Performance recommendations
            if business_summary.active_jobs > 10:
                response += f"📈 High job volume detected. Consider hiring additional staff or optimizing scheduling.\n"
            
            if business_summary.pending_estimates > 5:
                response += f"📊 Multiple pending estimates. Focus on follow-up calls to convert them.\n"
            
            # Efficiency recommendations
            if suggestions and suggestions.urgent_items:
                response += f"\n🔥 Priority actions:\n"
                for item in suggestions.urgent_items[:2]:
                    response += f"• {item}\n"
            
            # Growth opportunities
            if suggestions and suggestions.opportunities:
                response += f"\n💡 Growth opportunities:\n"
                for opportunity in suggestions.opportunities[:2]:
                    response += f"• {opportunity}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error getting business recommendations: {e}")
            return f"❌ Error getting business recommendations: {str(e)}" 