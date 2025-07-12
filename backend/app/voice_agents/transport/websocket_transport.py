"""
WebSocket Voice Transport

WebSocket transport layer for real-time voice communication with OpenAI voice agents.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, AsyncIterator
from datetime import datetime
import websockets
from websockets.exceptions import ConnectionClosed
from agents import Runner
from agents.voice import VoicePipeline, SingleAgentVoiceWorkflow, AudioInput
from ..personal.openai_personal_agent import OpenAIPersonalAgent


logger = logging.getLogger(__name__)


class WebSocketVoiceTransport:
    """WebSocket transport for voice agent communication"""
    
    def __init__(self, 
                 business_context: Dict[str, Any],
                 user_context: Dict[str, Any]):
        """
        Initialize WebSocket voice transport
        
        Args:
            business_context: Business information and context
            user_context: User information and preferences
        """
        self.business_context = business_context
        self.user_context = user_context
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.agent: Optional[OpenAIPersonalAgent] = None
        self.pipeline: Optional[VoicePipeline] = None
        self.session_id: Optional[str] = None
        self.is_connected = False
        self.audio_buffer = []
        
    async def handle_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """
        Handle new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        self.websocket = websocket
        self.session_id = f"session_{self.user_context['id']}_{datetime.now().isoformat()}"
        self.is_connected = True
        
        logger.info(f"New voice agent connection: {self.session_id}")
        
        try:
            # Initialize voice agent
            await self._initialize_agent()
            
            # Send connection confirmation
            await self._send_message({
                "type": "connection_established",
                "session_id": self.session_id,
                "agent_name": self.agent.get_agent_name(),
                "greeting": self.agent.get_personalized_greeting(),
                "capabilities": self.agent.get_available_capabilities()
            })
            
            # Handle messages
            async for message in websocket:
                await self._handle_message(message)
                
        except ConnectionClosed:
            logger.info(f"Voice agent connection closed: {self.session_id}")
        except Exception as e:
            logger.error(f"Error in voice agent connection: {e}")
            await self._send_error("Connection error", str(e))
        finally:
            self.is_connected = False
            await self._cleanup()
    
    async def _initialize_agent(self):
        """Initialize the voice agent and pipeline"""
        try:
            # Create personal agent
            self.agent = OpenAIPersonalAgent(
                business_context=self.business_context,
                user_context=self.user_context
            )
            
            # Create voice pipeline
            agent_instance = self.agent.create_voice_optimized_agent()
            workflow = SingleAgentVoiceWorkflow(agent_instance)
            self.pipeline = VoicePipeline(workflow=workflow)
            
            logger.info(f"Voice agent initialized: {self.agent.get_agent_name()}")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice agent: {e}")
            raise
    
    async def _handle_message(self, message: str):
        """
        Handle incoming WebSocket message
        
        Args:
            message: JSON message from client
        """
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "audio_chunk":
                await self._handle_audio_chunk(data)
            elif message_type == "audio_end":
                await self._handle_audio_end(data)
            elif message_type == "text_message":
                await self._handle_text_message(data)
            elif message_type == "config_update":
                await self._handle_config_update(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON message received")
            await self._send_error("invalid_json", "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self._send_error("message_error", str(e))
    
    async def _handle_audio_chunk(self, data: Dict[str, Any]):
        """Handle incoming audio chunk"""
        try:
            audio_data = data.get("audio_data")
            if audio_data:
                # Decode base64 audio data
                import base64
                import numpy as np
                
                audio_bytes = base64.b64decode(audio_data)
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                
                # Add to buffer
                self.audio_buffer.append(audio_array)
                
                # Send acknowledgment
                await self._send_message({
                    "type": "audio_chunk_received",
                    "chunk_id": data.get("chunk_id"),
                    "buffer_size": len(self.audio_buffer)
                })
                
        except Exception as e:
            logger.error(f"Error handling audio chunk: {e}")
            await self._send_error("audio_error", str(e))
    
    async def _handle_audio_end(self, data: Dict[str, Any]):
        """Handle end of audio input and process with agent"""
        try:
            if not self.audio_buffer:
                await self._send_error("no_audio", "No audio data received")
                return
            
            # Concatenate audio buffer
            import numpy as np
            audio_input = np.concatenate(self.audio_buffer, axis=0)
            self.audio_buffer = []  # Clear buffer
            
            # Process with voice pipeline
            audio_input_obj = AudioInput(buffer=audio_input)
            result = await self.pipeline.run(audio_input_obj)
            
            # Stream response back to client
            await self._stream_voice_response(result)
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            await self._send_error("processing_error", str(e))
    
    async def _handle_text_message(self, data: Dict[str, Any]):
        """Handle text message input"""
        try:
            text = data.get("text", "")
            if not text:
                await self._send_error("empty_text", "Empty text message")
                return
            
            # Process with agent (text-only mode)
            agent_instance = self.agent.create_agent()
            result = await Runner.run(agent_instance, text)
            
            # Send text response
            await self._send_message({
                "type": "text_response",
                "text": result.final_output,
                "message_id": data.get("message_id")
            })
            
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await self._send_error("text_error", str(e))
    
    async def _handle_config_update(self, data: Dict[str, Any]):
        """Handle configuration update"""
        try:
            config = data.get("config", {})
            
            # Update user context
            if "is_driving" in config:
                self.user_context["is_driving"] = config["is_driving"]
            if "safety_mode" in config:
                self.user_context["safety_mode"] = config["safety_mode"]
            
            # Reinitialize agent with new config
            await self._initialize_agent()
            
            await self._send_message({
                "type": "config_updated",
                "config": config
            })
            
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            await self._send_error("config_error", str(e))
    
    async def _stream_voice_response(self, result):
        """Stream voice response back to client"""
        try:
            await self._send_message({
                "type": "voice_response_start",
                "session_id": self.session_id
            })
            
            # Stream audio chunks
            async for event in result.stream():
                if event.type == "voice_stream_event_audio":
                    # Encode audio data
                    import base64
                    import numpy as np
                    
                    audio_data = base64.b64encode(event.data.tobytes()).decode()
                    
                    await self._send_message({
                        "type": "audio_chunk",
                        "audio_data": audio_data,
                        "chunk_id": f"chunk_{datetime.now().timestamp()}"
                    })
                
                elif event.type == "voice_stream_event_text":
                    # Send text transcript
                    await self._send_message({
                        "type": "text_transcript",
                        "text": event.text
                    })
            
            await self._send_message({
                "type": "voice_response_end",
                "session_id": self.session_id
            })
            
        except Exception as e:
            logger.error(f"Error streaming voice response: {e}")
            await self._send_error("streaming_error", str(e))
    
    async def _send_message(self, message: Dict[str, Any]):
        """Send message to client"""
        if self.websocket and self.is_connected:
            try:
                await self.websocket.send(json.dumps(message))
            except ConnectionClosed:
                logger.warning("Cannot send message - connection closed")
                self.is_connected = False
            except Exception as e:
                logger.error(f"Error sending message: {e}")
    
    async def _send_error(self, error_type: str, error_message: str):
        """Send error message to client"""
        await self._send_message({
            "type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "session_id": self.session_id
        })
    
    async def _cleanup(self):
        """Clean up resources"""
        try:
            if self.pipeline:
                # Clean up pipeline resources
                pass
            
            self.audio_buffer = []
            logger.info(f"Voice agent session cleaned up: {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


class VoiceAgentWebSocketServer:
    """WebSocket server for voice agents"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize WebSocket server
        
        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self.server = None
        self.active_connections: Dict[str, WebSocketVoiceTransport] = {}
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting voice agent WebSocket server on {self.host}:{self.port}")
        
        self.server = await websockets.serve(
            self._handle_connection,
            self.host,
            self.port
        )
        
        logger.info("Voice agent WebSocket server started")
    
    async def stop_server(self):
        """Stop the WebSocket server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Voice agent WebSocket server stopped")
    
    async def _handle_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection"""
        # Extract business and user context from path or headers
        # This is a simplified implementation - in production, you'd extract from JWT token
        business_context = {
            "id": "business_123",
            "name": "Sample Business",
            "type": "home_services"
        }
        
        user_context = {
            "id": "user_456",
            "name": "John Doe",
            "is_driving": False,
            "safety_mode": True
        }
        
        transport = WebSocketVoiceTransport(business_context, user_context)
        await transport.handle_connection(websocket, path) 