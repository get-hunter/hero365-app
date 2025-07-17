"""
Voice pipeline for Hero365 using OpenAI agents SDK with TTS-LLM-STT processing.
"""

from typing import AsyncGenerator, Dict, Any, Optional
# from openai_agents.voice import VoiceAgent, VoiceWorkflow, AudioInput, AudioOutput
# from openai_agents import Runner
from datetime import datetime
import asyncio
import logging
from .context_manager import ContextManager
from ...core.config import settings

logger = logging.getLogger(__name__)


class Hero365VoicePipeline:
    """Voice pipeline using OpenAI agents SDK with TTS-LLM-STT"""
    
    def __init__(self, triage_agent):
        """
        Initialize voice pipeline with triage agent.
        
        Args:
            triage_agent: Main triage agent that routes to specialists
        """
        self.triage_agent = triage_agent
        self.context_manager: ContextManager = triage_agent.context_manager
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def start_voice_session(self, 
                                 user_id: str, 
                                 business_id: str,
                                 session_metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new voice session.
        
        Args:
            user_id: User ID
            business_id: Business ID  
            session_metadata: Optional metadata for the session
            
        Returns:
            Session ID for the new session
        """
        try:
            # Generate session ID
            session_id = f"voice_session_{user_id}_{int(datetime.now().timestamp())}"
            
            # Initialize context
            context = await self.context_manager.initialize_context(
                user_id=user_id,
                business_id=business_id,
                session_id=session_id
            )
            
            # Store session info
            self.active_sessions[session_id] = {
                "user_id": user_id,
                "business_id": business_id,
                "triage_agent": self.triage_agent,
                "context": context,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "metadata": session_metadata or {}
            }
            
            # Update context with session start
            await self.context_manager.update_context({
                "conversation": {
                    "agent": "system",
                    "action": "session_start",
                    "message": f"Voice session started for {context.user_info.get('name', 'user')}"
                }
            })
            
            logger.info(f"Started voice session {session_id} for user {user_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting voice session: {e}")
            raise
    
    async def create_session_with_id(self, 
                                   session_id: str,
                                   user_id: str, 
                                   business_id: str,
                                   session_metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a voice session with a specific session ID (for real-time streaming).
        
        Args:
            session_id: Custom session ID to use
            user_id: User ID
            business_id: Business ID  
            session_metadata: Optional metadata for the session
            
        Returns:
            Session ID that was created
        """
        try:
            # Check if session already exists
            if session_id in self.active_sessions:
                logger.warning(f"⚠️ Voice pipeline session {session_id} already exists")
                return session_id
            
            # Initialize context
            context = await self.context_manager.initialize_context(
                user_id=user_id,
                business_id=business_id,
                session_id=session_id
            )
            
            # Store session info
            self.active_sessions[session_id] = {
                "user_id": user_id,
                "business_id": business_id,
                "triage_agent": self.triage_agent,
                "context": context,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "metadata": session_metadata or {}
            }
            
            # Update context with session start
            await self.context_manager.update_context({
                "conversation": {
                    "agent": "system",
                    "action": "session_start",
                    "message": f"Voice session started for {context.user_info.get('name', 'user')}"
                }
            })
            
            logger.info(f"Created voice pipeline session {session_id} for user {user_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating voice pipeline session {session_id}: {e}")
            raise
    
    async def process_audio_stream(self, 
                                  session_id: str, 
                                  audio_input) -> AsyncGenerator:
        """
        Process audio input through the OpenAI Agents SDK multi-agent system.
        
        Args:
            session_id: Session ID
            audio_input: Audio input data
            
        Yields:
            Audio output from the agents
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"No active session found: {session_id}")
        
        try:
            session = self.active_sessions[session_id]
            triage_agent = session["triage_agent"]
            
            # For now, audio processing will be handled through the text pathway
            # This is a placeholder for future audio streaming implementation
            
            # Convert audio to text first
            text_input = await self.audio_processor.process_audio_to_text(audio_input)
            
            # Process through OpenAI Agents SDK
            response = await triage_agent.process_user_request(text_input)
            
            # Convert response back to audio
            audio_response = await self.audio_processor.convert_text_to_speech(response)
            
            yield audio_response
            
        except Exception as e:
            logger.error(f"❌ Error processing audio stream: {e}")
            raise
    
    async def process_text_input(self, 
                               session_id: str, 
                               text_input: str) -> str:
        """
        Process text input through the OpenAI Agents SDK multi-agent system.
        
        Args:
            session_id: Session ID
            text_input: Text input from user
            
        Returns:
            Text response from agent
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"No active session found: {session_id}")
        
        try:
            session = self.active_sessions[session_id]
            triage_agent = session["triage_agent"]
            
            # Update context with user input using context manager
            await self.context_manager.update_context({
                "conversation": {
                    "agent": "user",
                    "action": "text_input",
                    "message": text_input
                }
            })
            
            logger.info(f"🎯 Processing text input with OpenAI Agents SDK: {text_input}")
            
            # Use the OpenAI Agents SDK through the triage agent
            response = await triage_agent.process_user_request(text_input)
            
            logger.info(f"✅ OpenAI Agents SDK response: {response}")
            
            # Update context with response using context manager
            await self.context_manager.update_context({
                "conversation": {
                    "agent": "assistant",
                    "action": "text_response",
                    "message": response
                }
            })
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing text input: {e}")
            raise
    
    async def end_voice_session(self, session_id: str):
        """
        End voice session and cleanup.
        
        Args:
            session_id: Session ID to end
        """
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                
                # Update context with session end
                await self.context_manager.update_context({
                    "conversation": {
                        "agent": "system",
                        "action": "session_end",
                        "message": "Voice session ended"
                    }
                })
                
                # Cleanup session
                del self.active_sessions[session_id]
                
                logger.info(f"Ended voice session {session_id}")
            
            # End context manager session
            await self.context_manager.end_session(session_id)
            
        except Exception as e:
            logger.error(f"Error ending voice session: {e}")
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get status of a voice session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session status information
        """
        if session_id not in self.active_sessions:
            return {"status": "not_found", "session_id": session_id}
        
        session = self.active_sessions[session_id]
        context = await self.context_manager.get_current_context()
        
        return {
            "status": session["status"],
            "session_id": session_id,
            "user_id": session["user_id"],
            "business_id": session["business_id"],
            "created_at": session["created_at"],
            "current_agent": context.get("current_agent"),
            "active_tasks": context.get("active_tasks", []),
            "conversation_count": len(context.get("recent_conversation", [])),
            "metadata": session.get("metadata", {})
        }
    
    async def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active voice sessions.
        
        Returns:
            Dictionary of active sessions
        """
        return {
            session_id: {
                "user_id": session["user_id"],
                "business_id": session["business_id"],
                "created_at": session["created_at"],
                "status": session["status"],
                "metadata": session.get("metadata", {})
            }
            for session_id, session in self.active_sessions.items()
        }
    
    async def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """
        Clean up expired voice sessions.
        
        Args:
            max_age_hours: Maximum age in hours before session is considered expired
        """
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session in self.active_sessions.items():
                created_at = datetime.fromisoformat(session["created_at"])
                age = current_time - created_at
                
                if age.total_seconds() > (max_age_hours * 3600):
                    expired_sessions.append(session_id)
            
            # Clean up expired sessions
            for session_id in expired_sessions:
                await self.end_voice_session(session_id)
                logger.info(f"Cleaned up expired session: {session_id}")
            
            return len(expired_sessions)
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    async def handle_agent_handoff(self, 
                                  session_id: str, 
                                  from_agent: str, 
                                  to_agent: str,
                                  context: Dict[str, Any] = None):
        """
        Handle agent handoff during conversation.
        
        Args:
            session_id: Session ID
            from_agent: Source agent name
            to_agent: Target agent name
            context: Additional context for handoff
        """
        try:
            # Update context with handoff information
            await self.context_manager.update_context({
                "conversation": {
                    "agent": "system",
                    "action": "agent_handoff",
                    "from_agent": from_agent,
                    "to_agent": to_agent,
                    "context": context or {}
                },
                "current_agent": to_agent
            })
            
            logger.info(f"Agent handoff in session {session_id}: {from_agent} → {to_agent}")
            
        except Exception as e:
            logger.error(f"Error handling agent handoff: {e}")
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        Get pipeline statistics.
        
        Returns:
            Pipeline statistics
        """
        return {
            "active_sessions": len(self.active_sessions),
            "total_sessions_created": len(self.active_sessions),  # This would be tracked in production
            "pipeline_status": "active",
            "supported_models": {
                "voice": settings.OPENAI_VOICE_MODEL,
                "speech": settings.OPENAI_SPEECH_MODEL,
                "tts": settings.OPENAI_TTS_MODEL,
                "tts_voice": settings.OPENAI_TTS_VOICE
            }
        } 