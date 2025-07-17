"""
Enhanced context management system for Hero365 LiveKit agents.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of context data"""
    USER_SESSION = "user_session"
    CONVERSATION_HISTORY = "conversation_history"
    BUSINESS_DATA = "business_data"
    AGENT_STATE = "agent_state"
    VOICE_PREFERENCES = "voice_preferences"


@dataclass
class ConversationEntry:
    """Single conversation entry"""
    timestamp: datetime
    participant_type: str  # "user" or "agent"
    content: str
    agent_name: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UserSession:
    """User session information"""
    user_id: str
    business_id: str
    session_id: str
    started_at: datetime
    last_activity: datetime
    preferences: Dict[str, Any]
    context_data: Dict[str, Any]


@dataclass
class AgentState:
    """Agent state information"""
    current_agent: str
    last_action: str
    pending_tasks: List[str]
    collected_data: Dict[str, Any]
    conversation_flow: str


class LiveKitContextManager:
    """Enhanced context manager for LiveKit agents"""
    
    def __init__(self, max_history_length: int = 100, session_timeout: int = 3600):
        """
        Initialize the context manager.
        
        Args:
            max_history_length: Maximum number of conversation entries to keep
            session_timeout: Session timeout in seconds
        """
        self.max_history_length = max_history_length
        self.session_timeout = session_timeout
        self._contexts: Dict[str, Dict[str, Any]] = {}
        self._session_locks: Dict[str, asyncio.Lock] = {}
        
    async def get_context_lock(self, session_id: str) -> asyncio.Lock:
        """Get or create a lock for a session"""
        if session_id not in self._session_locks:
            self._session_locks[session_id] = asyncio.Lock()
        return self._session_locks[session_id]
    
    async def initialize_session(self, session_id: str, user_id: str, business_id: str) -> None:
        """Initialize a new session context"""
        async with await self.get_context_lock(session_id):
            now = datetime.now()
            
            user_session = UserSession(
                user_id=user_id,
                business_id=business_id,
                session_id=session_id,
                started_at=now,
                last_activity=now,
                preferences={},
                context_data={}
            )
            
            # Convert UserSession to dict and serialize datetime fields to ISO format
            user_session_dict = asdict(user_session)
            user_session_dict['started_at'] = now.isoformat()
            user_session_dict['last_activity'] = now.isoformat()
            
            self._contexts[session_id] = {
                ContextType.USER_SESSION.value: user_session_dict,
                ContextType.CONVERSATION_HISTORY.value: [],
                ContextType.BUSINESS_DATA.value: {},
                ContextType.AGENT_STATE.value: asdict(AgentState(
                    current_agent="triage",
                    last_action="initialize",
                    pending_tasks=[],
                    collected_data={},
                    conversation_flow="initial"
                )),
                ContextType.VOICE_PREFERENCES.value: {
                    "voice_model": "cartesia",
                    "voice_speed": 1.0,
                    "voice_style": "professional",
                    "noise_cancellation": True,
                    "echo_cancellation": True
                }
            }
            
            logger.info(f"Initialized session context for {session_id}")
    
    async def get_context(self, session_id: str, context_type: ContextType) -> Optional[Dict[str, Any]]:
        """Get context data for a session"""
        async with await self.get_context_lock(session_id):
            if session_id not in self._contexts:
                return None
                
            context_data = self._contexts[session_id].get(context_type.value)
            if context_data and context_type == ContextType.USER_SESSION:
                # Update last activity
                context_data['last_activity'] = datetime.now().isoformat()
                
            return context_data
    
    async def set_context(self, session_id: str, context_type: ContextType, data: Dict[str, Any]) -> None:
        """Set context data for a session"""
        async with await self.get_context_lock(session_id):
            if session_id not in self._contexts:
                logger.warning(f"Session {session_id} not initialized")
                return
                
            self._contexts[session_id][context_type.value] = data
            
            # Update session activity
            if context_type != ContextType.USER_SESSION:
                session_data = self._contexts[session_id][ContextType.USER_SESSION.value]
                session_data['last_activity'] = datetime.now().isoformat()
    
    async def add_conversation_entry(self, session_id: str, participant_type: str, 
                                   content: str, agent_name: Optional[str] = None,
                                   confidence: Optional[float] = None,
                                   metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a conversation entry"""
        async with await self.get_context_lock(session_id):
            if session_id not in self._contexts:
                logger.warning(f"Session {session_id} not initialized")
                return
                
            entry = ConversationEntry(
                timestamp=datetime.now(),
                participant_type=participant_type,
                content=content,
                agent_name=agent_name,
                confidence=confidence,
                metadata=metadata
            )
            
            history = self._contexts[session_id][ContextType.CONVERSATION_HISTORY.value]
            history.append(asdict(entry))
            
            # Trim history if too long
            if len(history) > self.max_history_length:
                history[:] = history[-self.max_history_length:]
                
            logger.debug(f"Added conversation entry for {session_id}: {participant_type} - {content[:50]}...")
    
    async def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        async with await self.get_context_lock(session_id):
            if session_id not in self._contexts:
                return []
                
            history = self._contexts[session_id][ContextType.CONVERSATION_HISTORY.value]
            
            if limit:
                return history[-limit:]
            return history
    
    async def update_agent_state(self, session_id: str, current_agent: str, 
                               last_action: str, collected_data: Optional[Dict[str, Any]] = None) -> None:
        """Update agent state"""
        async with await self.get_context_lock(session_id):
            if session_id not in self._contexts:
                logger.warning(f"Session {session_id} not initialized")
                return
                
            agent_state = self._contexts[session_id][ContextType.AGENT_STATE.value]
            agent_state.update({
                'current_agent': current_agent,
                'last_action': last_action,
                'collected_data': collected_data or agent_state.get('collected_data', {})
            })
    
    async def get_user_session(self, session_id: str) -> Optional[UserSession]:
        """Get user session information"""
        session_data = await self.get_context(session_id, ContextType.USER_SESSION)
        if session_data:
            # Convert datetime fields safely
            for field in ['started_at', 'last_activity']:
                if field in session_data:
                    value = session_data[field]
                    if isinstance(value, str):
                        try:
                            session_data[field] = datetime.fromisoformat(value)
                        except ValueError:
                            # Try parsing as a different format or use current time as fallback
                            try:
                                session_data[field] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            except ValueError:
                                logger.warning(f"Could not parse datetime field {field}: {value}, using current time")
                                session_data[field] = datetime.now()
                    elif isinstance(value, datetime):
                        # Already a datetime object
                        session_data[field] = value
                    else:
                        # Fallback to current time
                        logger.warning(f"Invalid datetime field {field}: {value}, using current time")
                        session_data[field] = datetime.now()
            
            return UserSession(**session_data)
        return None
    
    async def get_business_context(self, session_id: str) -> Dict[str, Any]:
        """Get business context data"""
        return await self.get_context(session_id, ContextType.BUSINESS_DATA) or {}
    
    async def set_business_context(self, session_id: str, data: Dict[str, Any]) -> None:
        """Set business context data"""
        await self.set_context(session_id, ContextType.BUSINESS_DATA, data)
    
    async def get_voice_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get voice preferences"""
        return await self.get_context(session_id, ContextType.VOICE_PREFERENCES) or {}
    
    async def update_voice_preferences(self, session_id: str, preferences: Dict[str, Any]) -> None:
        """Update voice preferences"""
        current_prefs = await self.get_voice_preferences(session_id)
        current_prefs.update(preferences)
        await self.set_context(session_id, ContextType.VOICE_PREFERENCES, current_prefs)
    
    async def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        expired_sessions = []
        current_time = datetime.now()
        
        for session_id in list(self._contexts.keys()):
            async with await self.get_context_lock(session_id):
                session_data = self._contexts[session_id].get(ContextType.USER_SESSION.value)
                if session_data:
                    last_activity = datetime.fromisoformat(session_data['last_activity'])
                    if current_time - last_activity > timedelta(seconds=self.session_timeout):
                        expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.cleanup_session(session_id)
            
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    async def cleanup_session(self, session_id: str) -> None:
        """Clean up a specific session"""
        async with await self.get_context_lock(session_id):
            if session_id in self._contexts:
                del self._contexts[session_id]
            if session_id in self._session_locks:
                del self._session_locks[session_id]
                
        logger.info(f"Cleaned up session {session_id}")
    
    async def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the session context"""
        async with await self.get_context_lock(session_id):
            if session_id not in self._contexts:
                return {}
                
            context = self._contexts[session_id]
            history = context.get(ContextType.CONVERSATION_HISTORY.value, [])
            
            return {
                'session_id': session_id,
                'user_id': context.get(ContextType.USER_SESSION.value, {}).get('user_id'),
                'business_id': context.get(ContextType.USER_SESSION.value, {}).get('business_id'),
                'current_agent': context.get(ContextType.AGENT_STATE.value, {}).get('current_agent'),
                'conversation_length': len(history),
                'last_activity': context.get(ContextType.USER_SESSION.value, {}).get('last_activity'),
                'collected_data_keys': list(context.get(ContextType.AGENT_STATE.value, {}).get('collected_data', {}).keys())
            }
    
    def get_active_sessions_count(self) -> int:
        """Get the number of active sessions"""
        return len(self._contexts)
    
    async def export_session_data(self, session_id: str) -> Optional[str]:
        """Export session data as JSON"""
        async with await self.get_context_lock(session_id):
            if session_id not in self._contexts:
                return None
                
            # Convert datetime objects to ISO strings for JSON serialization
            context_copy = {}
            for key, value in self._contexts[session_id].items():
                if key == ContextType.CONVERSATION_HISTORY.value:
                    # Convert datetime objects in conversation history
                    history_copy = []
                    for entry in value:
                        entry_copy = entry.copy()
                        if isinstance(entry_copy.get('timestamp'), datetime):
                            entry_copy['timestamp'] = entry_copy['timestamp'].isoformat()
                        history_copy.append(entry_copy)
                    context_copy[key] = history_copy
                else:
                    context_copy[key] = value
                    
            return json.dumps(context_copy, indent=2, default=str)


# Global context manager instance
context_manager = LiveKitContextManager()


async def get_context_manager() -> LiveKitContextManager:
    """Get the global context manager instance"""
    return context_manager 