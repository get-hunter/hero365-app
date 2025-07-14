"""
Context manager for maintaining shared context across all voice agents.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import redis
import asyncio
import logging
from ...core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Shared context across all voice agents"""
    user_id: str
    business_id: str
    session_id: str
    user_info: Dict[str, Any] = field(default_factory=dict)
    business_info: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    world_context: Dict[str, Any] = field(default_factory=dict)
    current_location: Optional[Dict[str, Any]] = None
    active_tasks: List[Dict[str, Any]] = field(default_factory=list)
    current_agent: Optional[str] = None
    # Add conversation state tracking
    conversation_state: Dict[str, Any] = field(default_factory=dict)
    ongoing_operation: Optional[Dict[str, Any]] = None
    # Add OpenAI Agents SDK conversation management
    last_agent_result: Optional[Dict[str, Any]] = None
    sdk_conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "user_id": self.user_id,
            "business_id": self.business_id,
            "session_id": self.session_id,
            "user_info": self.user_info,
            "business_info": self.business_info,
            "conversation_history": self.conversation_history,
            "world_context": self.world_context,
            "current_location": self.current_location,
            "active_tasks": self.active_tasks,
            "current_agent": self.current_agent,
            "conversation_state": self.conversation_state,
            "ongoing_operation": self.ongoing_operation,
            "last_agent_result": self.last_agent_result,
            "sdk_conversation_history": self.sdk_conversation_history,
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentContext":
        """Create from dictionary"""
        return cls(
            user_id=data["user_id"],
            business_id=data["business_id"],
            session_id=data["session_id"],
            user_info=data.get("user_info", {}),
            business_info=data.get("business_info", {}),
            conversation_history=data.get("conversation_history", []),
            world_context=data.get("world_context", {}),
            current_location=data.get("current_location"),
            active_tasks=data.get("active_tasks", []),
            current_agent=data.get("current_agent"),
            conversation_state=data.get("conversation_state", {}),
            ongoing_operation=data.get("ongoing_operation"),
            last_agent_result=data.get("last_agent_result"),
            sdk_conversation_history=data.get("sdk_conversation_history", []),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        )


class ContextManager:
    """Manages shared context across all voice agents"""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.current_context: Optional[AgentContext] = None
        self.session_timeout = timedelta(hours=24)  # 24 hour session timeout
        
    async def initialize_context(self, 
                                user_id: str, 
                                business_id: str,
                                session_id: str) -> AgentContext:
        """Initialize context for a new voice session"""
        try:
            # Check if context already exists
            existing_context = await self._load_context_from_redis(session_id)
            if existing_context:
                self.current_context = existing_context
                return existing_context
            
            # Get user and business info from database
            user_info = await self._get_user_info(user_id)
            business_info = await self._get_business_info(business_id)
            
            # Get world context
            world_context = await self._get_world_context()
            
            # Create new context
            context = AgentContext(
                user_id=user_id,
                business_id=business_id,
                session_id=session_id,
                user_info=user_info,
                business_info=business_info,
                world_context=world_context,
                conversation_history=[],
                active_tasks=[]
            )
            
            # Store in Redis
            await self._store_context_in_redis(context)
            self.current_context = context
            
            return context
            
        except Exception as e:
            logger.error(f"Error initializing context: {e}")
            # Return minimal context on error
            return AgentContext(
                user_id=user_id,
                business_id=business_id,
                session_id=session_id
            )
    
    async def get_current_context(self) -> Dict[str, Any]:
        """Get current context formatted for agent prompts"""
        if not self.current_context:
            return {}
        
        try:
            # Refresh context from Redis if needed
            if self._should_refresh_context():
                await self._refresh_context_from_redis()
            
            return {
                "user_id": self.current_context.user_id,
                "business_id": self.current_context.business_id,
                "session_id": self.current_context.session_id,
                "user_name": self.current_context.user_info.get("name", ""),
                "user_email": self.current_context.user_info.get("email", ""),
                "user_role": self.current_context.user_info.get("role", ""),
                "business_name": self.current_context.business_info.get("name", ""),
                "business_type": self.current_context.business_info.get("type", ""),
                "current_date": self.current_context.world_context.get("date", datetime.now().strftime("%Y-%m-%d")),
                "current_time": self.current_context.world_context.get("time", datetime.now().strftime("%H:%M")),
                "location": self.current_context.current_location,
                "weather": self.current_context.world_context.get("weather", {}),
                "recent_conversation": self.current_context.conversation_history[-5:] if self.current_context.conversation_history else [],
                "active_tasks": self.current_context.active_tasks,
                "current_agent": self.current_context.current_agent,
                "conversation_state": self.current_context.conversation_state,
                "ongoing_operation": self.current_context.ongoing_operation,
                # Add OpenAI Agents SDK conversation management
                "conversation_history": self.current_context.sdk_conversation_history,
                "last_agent_result": self.current_context.last_agent_result
            }
            
        except Exception as e:
            logger.error(f"Error getting current context: {e}")
            return {}
    
    async def update_context(self, updates: Dict[str, Any]):
        """Update context with new information"""
        if not self.current_context:
            return
        
        try:
            # Update specific fields
            if "conversation" in updates:
                self.current_context.conversation_history.append({
                    **updates["conversation"],
                    "timestamp": datetime.now().isoformat()
                })
                
                # Keep only last 20 conversations
                if len(self.current_context.conversation_history) > 20:
                    self.current_context.conversation_history = self.current_context.conversation_history[-20:]
            
            if "location" in updates:
                self.current_context.current_location = updates["location"]
                
            if "active_task" in updates:
                self.current_context.active_tasks.append({
                    **updates["active_task"],
                    "timestamp": datetime.now().isoformat()
                })
                
            if "current_agent" in updates:
                self.current_context.current_agent = updates["current_agent"]
                
            if "user_info" in updates:
                self.current_context.user_info.update(updates["user_info"])
                
            if "business_info" in updates:
                self.current_context.business_info.update(updates["business_info"])
                
            if "world_context" in updates:
                self.current_context.world_context.update(updates["world_context"])
                
            if "conversation_state" in updates:
                self.current_context.conversation_state.update(updates["conversation_state"])
                
            if "ongoing_operation" in updates:
                self.current_context.ongoing_operation = updates["ongoing_operation"]
                
            # Handle OpenAI Agents SDK conversation management
            if "conversation_history" in updates:
                self.current_context.sdk_conversation_history = updates["conversation_history"]
                
            if "last_agent_result" in updates:
                self.current_context.last_agent_result = updates["last_agent_result"]
            
            # Update timestamp
            self.current_context.last_updated = datetime.now()
            
            # Store updated context
            await self._store_context_in_redis(self.current_context)
            
        except Exception as e:
            logger.error(f"Error updating context: {e}")
    
    async def end_session(self, session_id: str):
        """End voice session and cleanup"""
        try:
            # Remove from Redis
            self.redis_client.delete(f"voice_session:{session_id}")
            
            # Clear current context if it matches
            if self.current_context and self.current_context.session_id == session_id:
                self.current_context = None
                
        except Exception as e:
            logger.error(f"Error ending session: {e}")
    
    async def _load_context_from_redis(self, session_id: str) -> Optional[AgentContext]:
        """Load context from Redis"""
        try:
            data = self.redis_client.get(f"voice_session:{session_id}")
            if data:
                return AgentContext.from_dict(json.loads(data))
            return None
        except Exception as e:
            logger.error(f"Error loading context from Redis: {e}")
            return None
    
    async def _store_context_in_redis(self, context: AgentContext):
        """Store context in Redis"""
        try:
            key = f"voice_session:{context.session_id}"
            data = json.dumps(context.to_dict())
            self.redis_client.setex(key, self.session_timeout, data)
        except Exception as e:
            logger.error(f"Error storing context in Redis: {e}")
    
    async def _refresh_context_from_redis(self):
        """Refresh context from Redis"""
        if self.current_context:
            updated_context = await self._load_context_from_redis(self.current_context.session_id)
            if updated_context:
                self.current_context = updated_context
    
    def _should_refresh_context(self) -> bool:
        """Check if context should be refreshed from Redis"""
        if not self.current_context:
            return False
        
        # Refresh if context is older than 5 minutes
        time_since_update = datetime.now() - self.current_context.last_updated
        return time_since_update > timedelta(minutes=5)
    
    async def _get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information from database"""
        try:
            from ...infrastructure.config.dependency_injection import get_container
            container = get_container()
            
            # This would need to be implemented as a specific use case
            # For now, return basic info
            return {
                "id": user_id,
                "name": "User",
                "email": "user@example.com",
                "role": "contractor"
            }
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {}
    
    async def _get_business_info(self, business_id: str) -> Dict[str, Any]:
        """Get business information from database"""
        try:
            from ...infrastructure.config.dependency_injection import get_container
            container = get_container()
            
            # This would need to be implemented as a specific use case
            # For now, return basic info
            return {
                "id": business_id,
                "name": "Business",
                "type": "home_services",
                "address": "",
                "phone": ""
            }
        except Exception as e:
            logger.error(f"Error getting business info: {e}")
            return {}
    
    async def _get_world_context(self) -> Dict[str, Any]:
        """Get world context information"""
        try:
            now = datetime.now()
            return {
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M"),
                "day_of_week": now.strftime("%A"),
                "weather": {},  # Would be populated by weather service
                "timezone": "UTC"
            }
        except Exception as e:
            logger.error(f"Error getting world context: {e}")
            return {} 