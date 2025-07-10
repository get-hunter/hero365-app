"""
Hero365 Tools

Main tools class that aggregates all business functionality for voice agents.
"""

from typing import List, Any, Dict, Optional
from app.infrastructure.config.dependency_injection import get_container
from .job_tools import JobTools
from .project_tools import ProjectTools
from .invoice_tools import InvoiceTools
from .estimate_tools import EstimateTools
from .contact_tools import ContactTools


class Hero365Tools:
    """Main tools class that provides all Hero365 business functionality"""
    
    def __init__(self, business_id: str, user_id: str):
        """
        Initialize Hero365 tools with business and user context
        
        Args:
            business_id: Current business ID
            user_id: Current user ID
        """
        self.business_id = business_id
        self.user_id = user_id
        self.container = get_container()
        
        # Initialize specialized tool classes
        self.job_tools = JobTools(business_id, user_id)
        self.project_tools = ProjectTools(business_id, user_id)
        self.invoice_tools = InvoiceTools(business_id, user_id)
        self.estimate_tools = EstimateTools(business_id, user_id)
        self.contact_tools = ContactTools(business_id, user_id)
    
    def get_all_tools(self) -> List[Any]:
        """Get all available tools for voice agents"""
        tools = []
        
        # Job management tools
        tools.extend(self.job_tools.get_tools())
        
        # Project management tools
        tools.extend(self.project_tools.get_tools())
        
        # Invoice management tools
        tools.extend(self.invoice_tools.get_tools())
        
        # Estimate management tools
        tools.extend(self.estimate_tools.get_tools())
        
        # Contact management tools
        tools.extend(self.contact_tools.get_tools())
        
        # General business tools
        tools.extend(self.get_general_tools())
        
        return tools
    
    def get_general_tools(self) -> List[Any]:
        """Get general business tools"""
        return [
            self.get_business_summary,
            self.get_current_time,
            self.set_reminder,
            self.get_weather_info
        ]
    
    def get_business_summary(self) -> Dict[str, Any]:
        """Get summary of current business information"""
        try:
            business_repository = self.container.get_business_repository()
            business = business_repository.get_by_id(self.business_id)
            
            if not business:
                return {
                    "success": False,
                    "message": "Business not found"
                }
            
            return {
                "success": True,
                "business": {
                    "name": business.name,
                    "industry": business.industry,
                    "company_size": business.company_size.value if business.company_size else "unknown",
                    "phone": business.phone_number,
                    "email": business.business_email,
                    "website": business.website
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting business summary: {str(e)}"
            }
    
    def get_current_time(self) -> Dict[str, Any]:
        """Get current date and time"""
        from datetime import datetime
        
        now = datetime.now()
        return {
            "success": True,
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%A, %B %d, %Y"),
            "time": now.strftime("%I:%M %p")
        }
    
    def set_reminder(self, message: str, reminder_time: str) -> Dict[str, Any]:
        """Set a reminder for the user"""
        # This would integrate with a reminder system
        # For now, return a confirmation
        return {
            "success": True,
            "message": f"Reminder set: '{message}' for {reminder_time}",
            "reminder_id": f"reminder_{self.user_id}_{reminder_time}"
        }
    
    def get_weather_info(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get weather information for a location"""
        # This would integrate with a weather service
        # For now, return mock data
        location = location or "current location"
        return {
            "success": True,
            "location": location,
            "weather": "Partly cloudy, 72°F",
            "conditions": "Good conditions for outdoor work",
            "forecast": "Clear skies expected for the rest of the day"
        } 