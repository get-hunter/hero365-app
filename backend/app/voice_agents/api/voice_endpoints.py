"""
Voice agent API endpoints for Hero365 mobile integration.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel
import asyncio
import json
import logging
from datetime import datetime

from ...api.deps import get_current_user, get_business_context
from ..core.voice_pipeline import Hero365VoicePipeline
from ..core.context_manager import ContextManager
from ..triage.triage_agent import TriageAgent
from ..specialists.contact_agent import ContactAgent
from ..specialists.job_agent import JobAgent
from ..specialists.estimate_agent import EstimateAgent
from ..specialists.scheduling_agent import SchedulingAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

# Global voice system components
context_manager = ContextManager()
voice_pipeline = None


def initialize_voice_system():
    """Initialize the voice agent system"""
    global voice_pipeline, context_manager
    
    try:
        # Create specialist agents
        specialist_agents = {
            "contact": ContactAgent(context_manager),
            "job": JobAgent(context_manager),
            "estimate": EstimateAgent(context_manager),
            "scheduling": SchedulingAgent(context_manager)
        }
        
        # Create triage agent
        triage_agent = TriageAgent(context_manager, specialist_agents)
        
        # Create voice pipeline
        voice_pipeline = Hero365VoicePipeline(triage_agent)
        
        logger.info("Voice agent system initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize voice system: {e}")
        raise


# Initialize on module load
initialize_voice_system()


# Request/Response Models
class VoiceSessionRequest(BaseModel):
    session_metadata: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    device_info: Optional[Dict[str, Any]] = None


class VoiceSessionResponse(BaseModel):
    session_id: str
    status: str
    message: str
    user_context: Dict[str, Any]


class TextInputRequest(BaseModel):
    message: str
    session_id: str


class TextInputResponse(BaseModel):
    response: str
    session_id: str
    current_agent: Optional[str] = None


class VoiceCommandRequest(BaseModel):
    command: str
    session_id: str
    context: Optional[Dict[str, Any]] = None


# WebSocket connection manager
class VoiceWebSocketManager:
    """Manage WebSocket connections for real-time voice interaction"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str, business_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        
        # Initialize session metadata
        self.session_metadata[session_id] = {
            "user_id": user_id,
            "business_id": business_id,
            "connected_at": datetime.now().isoformat(),
            "status": "connected"
        }
        
        # Send initial context
        try:
            context = await context_manager.get_current_context()
            await websocket.send_json({
                "type": "context_update",
                "data": context,
                "session_id": session_id
            })
        except Exception as e:
            logger.error(f"Error sending initial context: {e}")
    
    async def disconnect(self, session_id: str):
        """Disconnect a WebSocket client"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        if session_id in self.session_metadata:
            del self.session_metadata[session_id]
        
        # End voice session
        if voice_pipeline:
            await voice_pipeline.end_voice_session(session_id)
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to a specific session"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to session {session_id}: {e}")
                await self.disconnect(session_id)
    
    async def handle_voice_message(self, session_id: str, message: Dict[str, Any]):
        """Handle incoming voice messages"""
        try:
            message_type = message.get("type")
            
            if message_type == "text_input":
                # Process text input through voice pipeline
                response = await voice_pipeline.process_text_input(
                    session_id, 
                    message.get("text", "")
                )
                
                await self.send_message(session_id, {
                    "type": "agent_response",
                    "session_id": session_id,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "audio_data":
                # This would handle audio processing
                # For now, return acknowledgment
                await self.send_message(session_id, {
                    "type": "audio_processing",
                    "session_id": session_id,
                    "status": "processing",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "context_update":
                # Update context
                await context_manager.update_context(message.get("data", {}))
                
                # Broadcast context update
                await self.send_message(session_id, {
                    "type": "context_updated",
                    "session_id": session_id,
                    "data": await context_manager.get_current_context(),
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "session_status":
                # Get session status
                status = await voice_pipeline.get_session_status(session_id)
                
                await self.send_message(session_id, {
                    "type": "session_status",
                    "session_id": session_id,
                    "data": status,
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            logger.error(f"Error handling voice message: {e}")
            await self.send_message(session_id, {
                "type": "error",
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })


# Initialize WebSocket manager
websocket_manager = VoiceWebSocketManager()


# API Endpoints
@router.post("/start-session", response_model=VoiceSessionResponse)
async def start_voice_session(
    request: VoiceSessionRequest,
    current_user=Depends(get_current_user),
    business_context=Depends(get_business_context)
):
    """Start a new voice session"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        user_id = current_user["sub"]
        business_id = business_context.get("business_id", current_user.get("business_id"))
        
        # Start voice session
        session_id = await voice_pipeline.start_voice_session(
            user_id=user_id,
            business_id=business_id,
            session_metadata=request.session_metadata
        )
        
        # Update context with location if provided
        if request.location:
            await context_manager.update_context({
                "location": request.location
            })
        
        # Get current context for response
        context = await context_manager.get_current_context()
        
        return VoiceSessionResponse(
            session_id=session_id,
            status="active",
            message="Voice session started successfully",
            user_context=context
        )
        
    except Exception as e:
        logger.error(f"Error starting voice session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text-input", response_model=TextInputResponse)
async def process_text_input(
    request: TextInputRequest,
    current_user=Depends(get_current_user)
):
    """Process text input through the voice agent system"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        # Process text input
        response = await voice_pipeline.process_text_input(
            request.session_id,
            request.message
        )
        
        # Get current context
        context = await context_manager.get_current_context()
        
        return TextInputResponse(
            response=response,
            session_id=request.session_id,
            current_agent=context.get("current_agent")
        )
        
    except Exception as e:
        logger.error(f"Error processing text input: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-command")
async def process_voice_command(
    request: VoiceCommandRequest,
    current_user=Depends(get_current_user)
):
    """Process a voice command"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        # Update context if provided
        if request.context:
            await context_manager.update_context(request.context)
        
        # Process command
        response = await voice_pipeline.process_text_input(
            request.session_id,
            request.command
        )
        
        return {
            "success": True,
            "response": response,
            "session_id": request.session_id
        }
        
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/status")
async def get_session_status(
    session_id: str,
    current_user=Depends(get_current_user)
):
    """Get status of a voice session"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        status = await voice_pipeline.get_session_status(session_id)
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/end")
async def end_voice_session(
    session_id: str,
    current_user=Depends(get_current_user)
):
    """End a voice session"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        await voice_pipeline.end_voice_session(session_id)
        
        return {
            "success": True,
            "message": "Voice session ended successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error ending voice session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/active")
async def get_active_sessions(
    current_user=Depends(get_current_user)
):
    """Get all active voice sessions"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        sessions = await voice_pipeline.get_active_sessions()
        
        return {
            "success": True,
            "data": sessions
        }
        
    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/status")
async def get_voice_system_status(
    current_user=Depends(get_current_user)
):
    """Get voice system status"""
    try:
        if not voice_pipeline:
            return {
                "success": False,
                "error": "Voice system not initialized"
            }
        
        stats = voice_pipeline.get_pipeline_stats()
        
        return {
            "success": True,
            "data": {
                "system_initialized": True,
                "pipeline_stats": stats,
                "active_connections": len(websocket_manager.active_connections),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting voice system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-audio/{session_id}")
async def upload_audio(
    session_id: str,
    audio_file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Upload audio file for processing"""
    try:
        if not voice_pipeline:
            raise HTTPException(status_code=500, detail="Voice system not initialized")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # This would process the audio through the voice pipeline
        # For now, return acknowledgment
        
        return {
            "success": True,
            "message": "Audio uploaded successfully",
            "session_id": session_id,
            "file_size": len(audio_data)
        }
        
    except Exception as e:
        logger.error(f"Error uploading audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    user_id: str,
    business_id: str
):
    """WebSocket endpoint for real-time voice interaction"""
    try:
        await websocket_manager.connect(websocket, session_id, user_id, business_id)
        
        # Start voice session if not already started
        if voice_pipeline:
            await voice_pipeline.start_voice_session(
                user_id=user_id,
                business_id=business_id,
                session_metadata={"websocket": True}
            )
        
        try:
            while True:
                # Receive message from client
                message = await websocket.receive_json()
                
                # Handle the message
                await websocket_manager.handle_voice_message(session_id, message)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for session {session_id}")
        except Exception as e:
            logger.error(f"WebSocket error for session {session_id}: {e}")
        finally:
            await websocket_manager.disconnect(session_id)
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close()


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        system_healthy = voice_pipeline is not None
        
        return {
            "status": "healthy" if system_healthy else "unhealthy",
            "voice_system_initialized": system_healthy,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        } 