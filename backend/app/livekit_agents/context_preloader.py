"""
Context Preloading Service for Voice Agents
Loads and serializes business context during session creation
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from .business_context_manager import BusinessContextManager
from ..infrastructure.config.dependency_injection import get_container

logger = logging.getLogger(__name__)


class ContextPreloader:
    """Preloads and serializes business context for voice agent sessions"""
    
    def __init__(self):
        self.container = None
        
    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert any object to JSON-serializable format"""
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif hasattr(obj, '__dict__'):
            # For objects with attributes, try to serialize their dict representation
            return {key: self._make_json_serializable(value) for key, value in obj.__dict__.items()}
        else:
            return obj
    
    async def preload_context(self, user_id: str, business_id: str) -> Dict[str, Any]:
        """
        Preload business context for a voice session
        
        Args:
            user_id: The user ID
            business_id: The business ID
            
        Returns:
            Dict containing serialized business context
        """
        try:
            logger.info(f"🔄 Preloading context for user {user_id}, business {business_id}")
            
            # Initialize container if not available
            if not self.container:
                self.container = get_container()
            
            # Initialize business context manager
            context_manager = BusinessContextManager()
            await context_manager.initialize(user_id, business_id, self.container)
            
            # Get loaded context
            business_context = context_manager.get_business_context()
            user_context = context_manager.get_user_context()
            recent_contacts = context_manager.get_recent_contacts()
            recent_jobs = context_manager.get_recent_jobs()
            recent_estimates = context_manager.get_recent_estimates()
            business_summary = context_manager.get_business_summary()
            
            # Serialize context for metadata
            serialized_context = {
                'preloaded_at': datetime.now().isoformat(),
                'user_id': user_id,
                'business_id': business_id,
                'business_context': self._serialize_business_context(business_context),
                'user_context': self._serialize_user_context(user_context),
                'recent_contacts': self._serialize_recent_contacts(recent_contacts),
                'recent_jobs': self._serialize_recent_jobs(recent_jobs),
                'recent_estimates': self._serialize_recent_estimates(recent_estimates),
                'business_summary': self._serialize_business_summary(business_summary),
                'context_version': '1.0'
            }
            
            # Ensure everything is JSON-serializable
            serialized_context = self._make_json_serializable(serialized_context)
            
            logger.info(f"✅ Context preloaded successfully for user {user_id}")
            return serialized_context
            
        except Exception as e:
            logger.error(f"❌ Error preloading context for user {user_id}, business {business_id}: {e}")
            # Return minimal context to prevent total failure
            minimal_context = {
                'preloaded_at': datetime.now().isoformat(),
                'user_id': user_id,
                'business_id': business_id,
                'error': str(e),
                'context_version': '1.0'
            }
            return self._make_json_serializable(minimal_context)
    
    def _serialize_business_context(self, business_context) -> Dict[str, Any]:
        """Serialize business context for metadata"""
        if not business_context:
            return {}
            
        return {
            'business_id': str(business_context.business_id),
            'business_name': business_context.business_name,
            'business_type': business_context.business_type,
            'owner_name': business_context.owner_name,
            'phone': business_context.phone,
            'email': business_context.email,
            'address': business_context.address,
            'timezone': business_context.timezone,
            'recent_contacts_count': business_context.recent_contacts_count,
            'recent_jobs_count': business_context.recent_jobs_count,
            'recent_estimates_count': business_context.recent_estimates_count,
            'active_jobs': business_context.active_jobs,
            'pending_estimates': business_context.pending_estimates,
            'last_refresh': business_context.last_refresh.isoformat() if business_context.last_refresh else None
        }
    
    def _serialize_user_context(self, user_context) -> Dict[str, Any]:
        """Serialize user context for metadata"""
        if not user_context:
            return {}
            
        return {
            'user_id': str(user_context.user_id),
            'name': user_context.name,
            'email': user_context.email,
            'role': user_context.role,
            'permissions': user_context.permissions,
            'last_active': user_context.last_active.isoformat() if user_context.last_active else None,
            'preferences': user_context.preferences
        }
    
    def _serialize_recent_contacts(self, recent_contacts) -> List[Dict[str, Any]]:
        """Serialize recent contacts for metadata"""
        if not recent_contacts:
            return []
            
        return [
            {
                'id': str(contact.id),
                'name': contact.name,
                'phone': contact.phone,
                'email': contact.email,
                'contact_type': contact.contact_type,
                'last_interaction': contact.last_interaction.isoformat() if contact.last_interaction else None,
                'recent_jobs': [str(job_id) for job_id in contact.recent_jobs] if contact.recent_jobs else [],
                'recent_estimates': [str(est_id) for est_id in contact.recent_estimates] if contact.recent_estimates else [],
                'priority': contact.priority.value if contact.priority else 'medium'
            }
            for contact in recent_contacts[:10]  # Limit to 10 most recent
        ]
    
    def _serialize_recent_jobs(self, recent_jobs) -> List[Dict[str, Any]]:
        """Serialize recent jobs for metadata"""
        if not recent_jobs:
            return []
            
        return [
            {
                'id': str(job.id),
                'title': job.title,
                'contact_id': str(job.contact_id),
                'contact_name': job.contact_name,
                'status': job.status,
                'scheduled_date': job.scheduled_date.isoformat() if job.scheduled_date else None,
                'estimated_duration': job.estimated_duration,
                'priority': job.priority,
                'description': job.description,
                'location': job.location
            }
            for job in recent_jobs[:10]  # Limit to 10 most recent
        ]
    
    def _serialize_recent_estimates(self, recent_estimates) -> List[Dict[str, Any]]:
        """Serialize recent estimates for metadata"""
        if not recent_estimates:
            return []
            
        return [
            {
                'id': str(estimate.id),
                'title': estimate.title,
                'contact_id': str(estimate.contact_id),
                'contact_name': estimate.contact_name,
                'status': estimate.status,
                'total_amount': float(estimate.total_amount) if estimate.total_amount else None,
                'created_date': estimate.created_date.isoformat() if estimate.created_date else None,
                'valid_until': estimate.valid_until.isoformat() if estimate.valid_until else None,
                'line_items_count': estimate.line_items_count
            }
            for estimate in recent_estimates[:10]  # Limit to 10 most recent
        ]
    
    def _serialize_business_summary(self, business_summary) -> Dict[str, Any]:
        """Serialize business summary for metadata"""
        if not business_summary:
            return {}
            
        return {
            'total_contacts': business_summary.total_contacts,
            'active_jobs': business_summary.active_jobs,
            'pending_estimates': business_summary.pending_estimates,
            'overdue_invoices': business_summary.overdue_invoices,
            'revenue_this_month': float(business_summary.revenue_this_month) if business_summary.revenue_this_month else 0.0,
            'jobs_this_week': business_summary.jobs_this_week,
            'upcoming_appointments': business_summary.upcoming_appointments
        }
    
    def deserialize_context(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deserialize context from room metadata
        
        Args:
            metadata: Room metadata containing serialized context
            
        Returns:
            Dict containing deserialized context ready for agent use
        """
        try:
            if not metadata or 'business_context' not in metadata:
                logger.warning("No business context found in metadata")
                return {}
            
            # Create agent-ready context
            agent_context = {
                'user_id': metadata.get('user_id'),
                'business_id': metadata.get('business_id'),
                'preloaded_at': metadata.get('preloaded_at'),
                'context_version': metadata.get('context_version', '1.0')
            }
            
            # Deserialize business context
            business_context = metadata.get('business_context', {})
            if business_context:
                agent_context.update({
                    'business_name': business_context.get('business_name'),
                    'business_type': business_context.get('business_type'),
                    'owner_name': business_context.get('owner_name'),
                    'phone': business_context.get('phone'),
                    'email': business_context.get('email'),
                    'address': business_context.get('address'),
                    'timezone': business_context.get('timezone'),
                    'recent_contacts_count': business_context.get('recent_contacts_count', 0),
                    'recent_jobs_count': business_context.get('recent_jobs_count', 0),
                    'recent_estimates_count': business_context.get('recent_estimates_count', 0),
                    'active_jobs': business_context.get('active_jobs', 0),
                    'pending_estimates': business_context.get('pending_estimates', 0),
                    'last_refresh': business_context.get('last_refresh')
                })
            
            # Deserialize user context
            user_context = metadata.get('user_context', {})
            if user_context:
                agent_context.update({
                    'user_name': user_context.get('name'),
                    'user_email': user_context.get('email'),
                    'user_role': user_context.get('role'),
                    'user_permissions': user_context.get('permissions', []),
                    'user_preferences': user_context.get('preferences', {})
                })
            
            # Add summary data
            business_summary = metadata.get('business_summary', {})
            if business_summary:
                agent_context.update({
                    'total_contacts': business_summary.get('total_contacts', 0),
                    'revenue_this_month': business_summary.get('revenue_this_month', 0),
                    'jobs_this_week': business_summary.get('jobs_this_week', 0),
                    'upcoming_appointments': business_summary.get('upcoming_appointments', 0)
                })
            
            # Add recent activity data
            agent_context.update({
                'recent_contacts': metadata.get('recent_contacts', []),
                'recent_jobs': metadata.get('recent_jobs', []),
                'recent_estimates': metadata.get('recent_estimates', [])
            })
            
            logger.info(f"✅ Context deserialized successfully for user {agent_context.get('user_id')}")
            return agent_context
            
        except Exception as e:
            logger.error(f"❌ Error deserializing context: {e}")
            return {} 