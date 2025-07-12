"""
Context Manager for Triage-Based Voice Agent System

Enhanced context management for intelligent routing and specialized agent execution.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, time
from app.domain.entities.business import Business


class ContextManager:
    """Enhanced context management for triage-based routing"""
    
    def __init__(self, business_context: Dict[str, Any], user_context: Dict[str, Any]):
        """
        Initialize context manager
        
        Args:
            business_context: Business information and context
            user_context: User information and preferences
        """
        self.business_context = business_context
        self.user_context = user_context
        
    def get_routing_context(self) -> Dict[str, Any]:
        """Get comprehensive context for intelligent routing"""
        return {
            "business": self._get_business_context(),
            "user": self._get_user_context(),
            "session": self._get_session_context(),
            "temporal": self._get_temporal_context()
        }
    
    def _get_business_context(self) -> Dict[str, Any]:
        """Get business-specific context"""
        return {
            "id": self.business_context.get("id"),
            "name": self.business_context.get("name"),
            "type": self.business_context.get("type"),
            "size": self.business_context.get("size"),
            "industry": self.business_context.get("industry"),
            "services": self.business_context.get("services", []),
            "business_hours": self.get_business_hours(),
            "timezone": self.business_context.get("timezone", "UTC")
        }
    
    def _get_user_context(self) -> Dict[str, Any]:
        """Get user-specific context"""
        return {
            "id": self.user_context.get("id"),
            "name": self.user_context.get("name"),
            "email": self.user_context.get("email"),
            "role": self.user_context.get("role"),
            "permissions": self.user_context.get("permissions", []),
            "preferences": self.user_context.get("preferences", {}),
            "language": self.user_context.get("language", "en"),
            "expertise_level": self.user_context.get("expertise_level", "beginner")
        }
    
    def _get_session_context(self) -> Dict[str, Any]:
        """Get session-specific context"""
        return {
            "location": self.user_context.get("location"),
            "coordinates": self.user_context.get("coordinates"),
            "time_zone": self.user_context.get("time_zone"),
            "is_driving": self.user_context.get("is_driving", False),
            "device_type": self.user_context.get("device_type"),
            "connection_type": self.user_context.get("connection_type"),
            "safety_mode": self.user_context.get("safety_mode", True)
        }
    
    def _get_temporal_context(self) -> Dict[str, Any]:
        """Get time-based context"""
        now = datetime.now()
        return {
            "current_time": now.isoformat(),
            "current_hour": now.hour,
            "day_of_week": now.strftime("%A"),
            "day_of_month": now.day,
            "month": now.strftime("%B"),
            "year": now.year,
            "is_business_hours": self.is_business_hours(now),
            "is_weekend": now.weekday() >= 5,
            "quarter": self._get_quarter(now)
        }
    
    def get_business_hours(self) -> Dict[str, Any]:
        """Get business operating hours"""
        # Default business hours - would be pulled from business settings
        return {
            "monday": {"start": "09:00", "end": "17:00"},
            "tuesday": {"start": "09:00", "end": "17:00"},
            "wednesday": {"start": "09:00", "end": "17:00"},
            "thursday": {"start": "09:00", "end": "17:00"},
            "friday": {"start": "09:00", "end": "17:00"},
            "saturday": {"start": "10:00", "end": "14:00"},
            "sunday": {"closed": True}
        }
    
    def is_business_hours(self, dt: datetime) -> bool:
        """Check if current time is within business hours"""
        day_name = dt.strftime("%A").lower()
        business_hours = self.get_business_hours()
        
        if day_name not in business_hours:
            return False
            
        day_hours = business_hours[day_name]
        if day_hours.get("closed", False):
            return False
            
        current_time = dt.time()
        start_time = time.fromisoformat(day_hours["start"])
        end_time = time.fromisoformat(day_hours["end"])
        
        return start_time <= current_time <= end_time
    
    def _get_quarter(self, dt: datetime) -> int:
        """Get current quarter (1-4)"""
        return (dt.month - 1) // 3 + 1
    
    def get_user_permissions(self) -> List[str]:
        """Get user permissions for authorization"""
        return self.user_context.get("permissions", [])
    
    def can_access_function(self, function_name: str) -> bool:
        """Check if user can access a specific function"""
        permissions = self.get_user_permissions()
        
        # Map functions to required permissions
        permission_map = {
            "create_job": ["job_management", "admin"],
            "create_invoice": ["invoice_management", "finance", "admin"],
            "process_payment": ["payment_processing", "finance", "admin"],
            "manage_inventory": ["inventory_management", "admin"],
            "access_financial_reports": ["finance", "admin"],
            "manage_users": ["admin"],
            "escalate_to_human": ["customer_service", "admin"]
        }
        
        required_permissions = permission_map.get(function_name, [])
        return any(perm in permissions for perm in required_permissions)
    
    def get_safety_constraints(self) -> Dict[str, Any]:
        """Get safety constraints based on current context"""
        constraints = {
            "max_response_length": 500,
            "avoid_complex_instructions": False,
            "require_confirmations": False,
            "limit_financial_actions": False
        }
        
        # Adjust constraints based on driving mode
        if self.user_context.get("is_driving", False):
            constraints.update({
                "max_response_length": 150,
                "avoid_complex_instructions": True,
                "require_confirmations": True,
                "limit_financial_actions": True
            })
        
        # Adjust constraints based on safety mode
        if self.user_context.get("safety_mode", True):
            constraints.update({
                "require_confirmations": True,
                "limit_financial_actions": True
            })
        
        return constraints
    
    def get_context_summary(self) -> str:
        """Get a formatted summary of current context"""
        ctx = self.get_routing_context()
        
        return f"""
CONTEXT SUMMARY:
Business: {ctx['business']['name']} ({ctx['business']['type']})
User: {ctx['user']['name']} ({ctx['user']['role']})
Time: {ctx['temporal']['current_time']} ({ctx['temporal']['day_of_week']})
Location: {ctx['session']['location'] or 'Unknown'}
Driving: {'Yes' if ctx['session']['is_driving'] else 'No'}
Business Hours: {'Yes' if ctx['temporal']['is_business_hours'] else 'No'}
        """.strip()
    
    def should_route_to_specialist(self, specialist_name: str, user_request: str) -> bool:
        """
        Determine if a request should be routed to a specific specialist
        
        Args:
            specialist_name: Name of the specialist agent
            user_request: User's request text
            
        Returns:
            Boolean indicating if routing is appropriate
        """
        # This would contain routing logic based on context and request analysis
        # For now, return True - actual implementation would use NLU
        return True
    
    def get_routing_confidence(self, specialist_name: str, user_request: str) -> float:
        """
        Get confidence score for routing to a specific specialist
        
        Args:
            specialist_name: Name of the specialist agent
            user_request: User's request text
            
        Returns:
            Confidence score between 0 and 1
        """
        # This would contain ML-based confidence scoring
        # For now, return default confidence
        return 0.8 