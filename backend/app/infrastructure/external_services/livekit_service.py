"""
LiveKit service for managing rooms and tokens
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os
import json

from livekit import api
from livekit.api import CreateRoomRequest, AccessToken, VideoGrants
from app.core.config import settings

logger = logging.getLogger(__name__)


class LiveKitService:
    def __init__(self):
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self.ws_url = settings.LIVEKIT_URL
        
        if not all([self.api_key, self.api_secret, self.ws_url]):
            raise ValueError("Missing required LiveKit configuration")
        
        self._livekit_api = None
        logger.info("LiveKit service initialized")
    
    @property
    def livekit_api(self):
        """Lazy initialization of LiveKit API to avoid event loop issues"""
        if self._livekit_api is None:
            self._livekit_api = api.LiveKitAPI(
                url=self.ws_url,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
        return self._livekit_api

    def is_available(self) -> bool:
        """Check if LiveKit service is available"""
        try:
            return all([self.api_key, self.api_secret, self.ws_url])
        except Exception as e:
            logger.error(f"LiveKit service availability check failed: {e}")
            return False

    async def create_room(self, room_name: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a LiveKit room"""
        try:
            request = CreateRoomRequest(
                name=room_name,
                metadata=json.dumps(metadata) if metadata else ""
            )
            
            room = await self.livekit_api.room.create_room(request)
            
            logger.info(f"Created LiveKit room: {room_name}")
            
            return {
                "room_name": room.name,
                "room_sid": room.sid,
                "creation_time": datetime.now().isoformat(),
                "num_participants": room.num_participants
            }
            
        except Exception as e:
            logger.error(f"Failed to create LiveKit room: {e}")
            raise

    async def create_voice_session_room(self, session_id: str, user_id: str, room_name: str, agent_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a voice session room with metadata for the voice agent"""
        try:
            # Prepare metadata for the voice agent worker
            metadata = {
                "session_id": session_id,
                "user_id": user_id,
                "session_type": "voice_agent",
                "created_at": datetime.now().isoformat()
            }
            
            # Add agent context if provided
            if agent_context:
                metadata["agent_context"] = agent_context
            
            # Create the room
            room_info = await self.create_room(room_name, metadata)
            
            logger.info(f"Created voice session room: {room_name} for user: {user_id}")
            return room_info
            
        except Exception as e:
            logger.error(f"Failed to create voice session room: {e}")
            raise

    def generate_user_token(self, room_name: str, user_id: str, user_name: str = "") -> str:
        """Generate a user token for joining a LiveKit room"""
        try:
            # Create token with user permissions
            token = AccessToken(self.api_key, self.api_secret)
            
            # Set user identity and room
            token.with_identity(user_id)
            token.with_name(user_name or user_id)
            
            # Grant permissions for user to join room and publish/subscribe
            grants = VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
                can_update_own_metadata=True
            )
            
            token.with_grants(grants)
            
            # Set token expiration (6 hours)
            token.with_ttl(timedelta(hours=6))
            
            jwt_token = token.to_jwt()
            
            logger.info(f"Generated user token for room: {room_name}")
            
            return jwt_token
            
        except Exception as e:
            logger.error(f"Failed to generate user token: {e}")
            raise

    def get_connection_url(self) -> str:
        """Get the WebSocket connection URL for LiveKit"""
        return self.ws_url 