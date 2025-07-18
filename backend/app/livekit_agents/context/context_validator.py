"""
Context Validator for Hero365 LiveKit Agents
Validates business context data for completeness and correctness
"""

from typing import Dict, Any, List, Tuple
import logging
from datetime import datetime

from ..models import BusinessContext, UserContext

logger = logging.getLogger(__name__)


class ContextValidator:
    """
    Validates business context data for completeness and correctness
    Simplified version using Pydantic models for validation
    """
    
    def validate_preloaded_context(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate preloaded context data"""
        errors = []
        
        # Check for required fields
        required_fields = ['business_id', 'user_id']
        for field in required_fields:
            if not context.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Check for business context
        if not context.get('business_name'):
            errors.append("Missing business name")
        
        # Check for user context
        if not context.get('user_name') and not context.get('user_email'):
            errors.append("Missing user identification (name or email)")
        
        return len(errors) == 0, errors
    
    def validate_agent_context(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate agent context data"""
        errors = []
        
        # Use Pydantic models for validation
        try:
            # Try to create BusinessContext from the data
            business_data = {
                'business_id': context.get('business_id', ''),
                'business_name': context.get('business_name', ''),
                'business_type': context.get('business_type', ''),
                'owner_name': context.get('owner_name', 'Owner'),
                'phone': context.get('phone'),
                'email': context.get('email'),
                'address': context.get('address'),
                'timezone': context.get('timezone', 'UTC'),
            }
            
            # Validate using Pydantic model
            BusinessContext(**business_data)
            
        except Exception as e:
            errors.append(f"Invalid business context: {str(e)}")
        
        try:
            # Try to create UserContext from the data
            user_data = {
                'user_id': context.get('user_id', ''),
                'name': context.get('user_name', 'User'),
                'email': context.get('user_email', 'user@example.com'),
                'role': context.get('user_role', 'user'),
                'permissions': context.get('user_permissions', []),
                'preferences': context.get('user_preferences', {}),
                'recent_actions': [],
            }
            
            # Validate using Pydantic model
            UserContext(**user_data)
            
        except Exception as e:
            errors.append(f"Invalid user context: {str(e)}")
        
        return len(errors) == 0, errors
    
    def log_context_status(self, context: Dict[str, Any], context_type: str):
        """Log context status for debugging"""
        logger.info(f"📊 {context_type} Context Status:")
        logger.info(f"  Business: {context.get('business_name', 'Unknown')}")
        logger.info(f"  User: {context.get('user_name', 'Unknown')}")
        logger.info(f"  Active Jobs: {context.get('active_jobs', 0)}")
        logger.info(f"  Pending Estimates: {context.get('pending_estimates', 0)}")
    
    def generate_context_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a context validation report"""
        is_valid, errors = self.validate_agent_context(context)
        
        # Calculate completeness score
        total_fields = 15  # Total expected fields
        present_fields = 0
        
        check_fields = [
            'business_id', 'business_name', 'business_type', 'owner_name',
            'phone', 'email', 'address', 'timezone',
            'user_id', 'user_name', 'user_email', 'user_role',
            'active_jobs', 'pending_estimates', 'recent_contacts_count'
        ]
        
        for field in check_fields:
            if context.get(field):
                present_fields += 1
        
        completeness = present_fields / total_fields
        
        return {
            'validation_status': 'Valid' if is_valid else 'Invalid',
            'completeness': completeness,
            'errors': errors,
            'warnings': [],
            'fields_present': present_fields,
            'total_fields': total_fields,
            'generated_at': datetime.now().isoformat()
        } 