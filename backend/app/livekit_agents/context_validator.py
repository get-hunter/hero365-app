"""
Context Validation Service for Voice Agents
Validates business context and provides comprehensive logging
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextValidationError(Exception):
    """Raised when context validation fails"""
    pass


class ContextValidator:
    """Validates business context for voice agent sessions"""
    
    def __init__(self):
        self.validation_rules = {
            'business_context': {
                'required_fields': ['business_id', 'business_name'],
                'optional_fields': ['business_type', 'phone', 'email', 'address', 'timezone'],
                'metrics_fields': ['active_jobs', 'pending_estimates', 'recent_contacts_count']
            },
            'user_context': {
                'required_fields': ['user_id', 'name'],
                'optional_fields': ['email', 'role', 'permissions', 'preferences']
            }
        }
    
    def validate_preloaded_context(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate preloaded context structure and content
        
        Args:
            context: The preloaded context dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            errors = []
            
            # Check basic structure
            if not isinstance(context, dict):
                errors.append("Context must be a dictionary")
                return False, errors
            
            # Check for required top-level fields
            required_top_level = ['user_id', 'business_id', 'preloaded_at', 'context_version']
            for field in required_top_level:
                if field not in context:
                    errors.append(f"Missing required field: {field}")
            
            # Validate business context
            business_context = context.get('business_context', {})
            if business_context:
                business_errors = self._validate_business_context(business_context)
                errors.extend(business_errors)
            else:
                errors.append("Missing business_context")
            
            # Validate user context
            user_context = context.get('user_context', {})
            if user_context:
                user_errors = self._validate_user_context(user_context)
                errors.extend(user_errors)
            else:
                errors.append("Missing user_context")
            
            # Validate timestamps
            preloaded_at = context.get('preloaded_at')
            if preloaded_at:
                try:
                    datetime.fromisoformat(preloaded_at.replace('Z', '+00:00'))
                except ValueError:
                    errors.append("Invalid preloaded_at timestamp format")
            
            # Check context freshness (warn if older than 1 hour)
            if preloaded_at:
                try:
                    preload_time = datetime.fromisoformat(preloaded_at.replace('Z', '+00:00'))
                    age_hours = (datetime.now() - preload_time.replace(tzinfo=None)).total_seconds() / 3600
                    if age_hours > 1:
                        logger.warning(f"⚠️ Context is {age_hours:.1f} hours old")
                except Exception:
                    pass
            
            is_valid = len(errors) == 0
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"❌ Error validating context: {e}")
            return False, [f"Validation error: {str(e)}"]
    
    def _validate_business_context(self, business_context: Dict[str, Any]) -> List[str]:
        """Validate business context structure"""
        errors = []
        
        # Check required fields
        for field in self.validation_rules['business_context']['required_fields']:
            if field not in business_context or not business_context[field]:
                errors.append(f"Business context missing required field: {field}")
        
        # Validate business_id format (should be UUID)
        business_id = business_context.get('business_id')
        if business_id and not self._is_valid_uuid(business_id):
            errors.append("Invalid business_id format")
        
        # Validate business_name (should be non-empty string)
        business_name = business_context.get('business_name')
        if business_name and not isinstance(business_name, str):
            errors.append("business_name must be a string")
        
        # Validate phone number format if present
        phone = business_context.get('phone')
        if phone and not self._is_valid_phone(phone):
            errors.append("Invalid phone number format")
        
        # Validate email format if present
        email = business_context.get('email')
        if email and not self._is_valid_email(email):
            errors.append("Invalid email format")
        
        # Validate numeric fields
        numeric_fields = ['active_jobs', 'pending_estimates', 'recent_contacts_count']
        for field in numeric_fields:
            value = business_context.get(field)
            if value is not None and not isinstance(value, (int, float)):
                errors.append(f"{field} must be a number")
            elif value is not None and value < 0:
                errors.append(f"{field} must be non-negative")
        
        return errors
    
    def _validate_user_context(self, user_context: Dict[str, Any]) -> List[str]:
        """Validate user context structure"""
        errors = []
        
        # Check required fields
        for field in self.validation_rules['user_context']['required_fields']:
            if field not in user_context or not user_context[field]:
                errors.append(f"User context missing required field: {field}")
        
        # Validate user_id format (should be UUID)
        user_id = user_context.get('user_id')
        if user_id and not self._is_valid_uuid(user_id):
            errors.append("Invalid user_id format")
        
        # Validate name (should be non-empty string)
        name = user_context.get('name')
        if name and not isinstance(name, str):
            errors.append("User name must be a string")
        
        # Validate email format if present
        email = user_context.get('email')
        if email and not self._is_valid_email(email):
            errors.append("Invalid user email format")
        
        # Validate permissions (should be a list)
        permissions = user_context.get('permissions')
        if permissions is not None and not isinstance(permissions, list):
            errors.append("User permissions must be a list")
        
        # Validate preferences (should be a dict)
        preferences = user_context.get('preferences')
        if preferences is not None and not isinstance(preferences, dict):
            errors.append("User preferences must be a dictionary")
        
        return errors
    
    def validate_agent_context(self, agent_context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate agent context (deserialized from preloaded context)
        
        Args:
            agent_context: The agent context dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            errors = []
            
            # Check basic structure
            if not isinstance(agent_context, dict):
                errors.append("Agent context must be a dictionary")
                return False, errors
            
            # Check for essential fields
            essential_fields = ['user_id', 'business_id']
            for field in essential_fields:
                if field not in agent_context or not agent_context[field]:
                    errors.append(f"Agent context missing essential field: {field}")
            
            # Validate business information
            business_fields = ['business_name', 'business_type']
            for field in business_fields:
                value = agent_context.get(field)
                if value and not isinstance(value, str):
                    errors.append(f"{field} must be a string")
            
            # Validate user information
            user_name = agent_context.get('user_name')
            if user_name and not isinstance(user_name, str):
                errors.append("user_name must be a string")
            
            # Validate metrics
            metric_fields = ['active_jobs', 'pending_estimates', 'total_contacts']
            for field in metric_fields:
                value = agent_context.get(field)
                if value is not None:
                    if not isinstance(value, (int, float)):
                        errors.append(f"{field} must be a number")
                    elif value < 0:
                        errors.append(f"{field} must be non-negative")
            
            # Validate lists
            list_fields = ['recent_contacts', 'recent_jobs', 'recent_estimates']
            for field in list_fields:
                value = agent_context.get(field)
                if value is not None and not isinstance(value, list):
                    errors.append(f"{field} must be a list")
            
            is_valid = len(errors) == 0
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"❌ Error validating agent context: {e}")
            return False, [f"Agent context validation error: {str(e)}"]
    
    def log_context_status(self, context: Dict[str, Any], context_type: str = "unknown"):
        """
        Log comprehensive context status for debugging
        
        Args:
            context: The context to log
            context_type: Type of context being logged
        """
        try:
            if not context:
                logger.warning(f"⚠️ {context_type} context is empty or None")
                return
            
            logger.info(f"📊 {context_type} Context Status:")
            
            # Log basic info
            user_id = context.get('user_id', 'Unknown')
            business_id = context.get('business_id', 'Unknown')
            logger.info(f"  User ID: {user_id}")
            logger.info(f"  Business ID: {business_id}")
            
            # Log business info
            business_name = context.get('business_name', 'Unknown')
            business_type = context.get('business_type', 'Unknown')
            logger.info(f"  Business: {business_name} ({business_type})")
            
            # Log user info
            user_name = context.get('user_name', 'Unknown')
            logger.info(f"  User: {user_name}")
            
            # Log metrics
            active_jobs = context.get('active_jobs', 0)
            pending_estimates = context.get('pending_estimates', 0)
            total_contacts = context.get('total_contacts', 0)
            logger.info(f"  Metrics: {active_jobs} active jobs, {pending_estimates} pending estimates, {total_contacts} total contacts")
            
            # Log recent activity
            recent_contacts = context.get('recent_contacts', [])
            recent_jobs = context.get('recent_jobs', [])
            recent_estimates = context.get('recent_estimates', [])
            logger.info(f"  Recent Activity: {len(recent_contacts)} contacts, {len(recent_jobs)} jobs, {len(recent_estimates)} estimates")
            
            # Log timestamps
            preloaded_at = context.get('preloaded_at')
            if preloaded_at:
                logger.info(f"  Preloaded: {preloaded_at}")
            
            last_refresh = context.get('last_refresh')
            if last_refresh:
                logger.info(f"  Last Refresh: {last_refresh}")
            
        except Exception as e:
            logger.error(f"❌ Error logging context status: {e}")
    
    def _is_valid_uuid(self, value: str) -> bool:
        """Check if string is a valid UUID"""
        try:
            import uuid
            uuid.UUID(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        if not isinstance(email, str):
            return False
        return '@' in email and '.' in email.split('@')[-1]
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Basic phone validation"""
        if not isinstance(phone, str):
            return False
        # Remove common phone number characters
        cleaned = ''.join(c for c in phone if c.isdigit())
        return 10 <= len(cleaned) <= 15
    
    def generate_context_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive context report
        
        Args:
            context: The context to analyze
            
        Returns:
            Dict containing context analysis report
        """
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'context_available': bool(context),
                'validation_status': 'unknown',
                'errors': [],
                'warnings': [],
                'metrics': {},
                'completeness': 0.0
            }
            
            if not context:
                report['validation_status'] = 'missing'
                return report
            
            # Validate context
            is_valid, errors = self.validate_agent_context(context)
            report['validation_status'] = 'valid' if is_valid else 'invalid'
            report['errors'] = errors
            
            # Calculate completeness
            expected_fields = [
                'user_id', 'business_id', 'business_name', 'business_type',
                'user_name', 'phone', 'email', 'address'
            ]
            present_fields = sum(1 for field in expected_fields if context.get(field))
            report['completeness'] = present_fields / len(expected_fields)
            
            # Extract metrics
            report['metrics'] = {
                'active_jobs': context.get('active_jobs', 0),
                'pending_estimates': context.get('pending_estimates', 0),
                'total_contacts': context.get('total_contacts', 0),
                'recent_contacts_count': len(context.get('recent_contacts', [])),
                'recent_jobs_count': len(context.get('recent_jobs', [])),
                'recent_estimates_count': len(context.get('recent_estimates', []))
            }
            
            # Check for warnings
            if report['completeness'] < 0.7:
                report['warnings'].append(f"Context completeness is low: {report['completeness']:.1%}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating context report: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'context_available': False,
                'validation_status': 'error',
                'errors': [str(e)],
                'warnings': [],
                'metrics': {},
                'completeness': 0.0
            } 