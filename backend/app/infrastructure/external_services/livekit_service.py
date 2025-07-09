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
        logger.info("🔧 LiveKit service initialized")
        logger.debug(f"🌐 LiveKit URL: {self.ws_url}")
        logger.debug(f"🔑 API Key: {self.api_key[:10]}..." if self.api_key else "None")
    
    @property
    def livekit_api(self):
        """Lazy initialization of LiveKit API to avoid event loop issues"""
        if self._livekit_api is None:
            logger.debug("🔧 Initializing LiveKit API client...")
            self._livekit_api = api.LiveKitAPI(
                url=self.ws_url,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            logger.debug("✅ LiveKit API client initialized")
        return self._livekit_api

    def is_available(self) -> bool:
        """Check if LiveKit service is available"""
        try:
            result = all([self.api_key, self.api_secret, self.ws_url])
            logger.debug(f"🔍 LiveKit availability check: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ LiveKit service availability check failed: {e}")
            return False

    async def create_room(self, room_name: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a LiveKit room"""
        try:
            logger.info(f"🏠 Creating LiveKit room: {room_name}")
            logger.debug(f"📋 Room metadata: {metadata}")
            
            # Convert metadata to JSON string
            metadata_json = json.dumps(metadata) if metadata else ""
            logger.debug(f"📋 Metadata JSON: {metadata_json}")
            
            request = CreateRoomRequest(
                name=room_name,
                metadata=metadata_json
            )
            
            logger.debug(f"📤 Sending room creation request: {request}")
            room = await self.livekit_api.room.create_room(request)
            logger.info(f"✅ LiveKit room created successfully: {room_name}")
            logger.debug(f"🏠 Room details: name={room.name}, sid={room.sid}, participants={room.num_participants}")
            
            result = {
                "room_name": room.name,
                "room_sid": room.sid,
                "creation_time": datetime.now().isoformat(),
                "num_participants": room.num_participants
            }
            
            logger.debug(f"📤 Returning room info: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to create LiveKit room '{room_name}': {e}")
            import traceback
            logger.debug(f"🐛 Room creation traceback: {traceback.format_exc()}")
            raise

    async def create_voice_session_room(self, session_id: str, user_id: str, room_name: str, agent_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a voice session room with metadata for the voice agent"""
        try:
            logger.info(f"🎙️ Creating voice session room: {room_name}")
            logger.info(f"👤 Session ID: {session_id}, User ID: {user_id}")
            logger.debug(f"🤖 Agent context: {agent_context}")
            
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
                logger.info("✅ Agent context added to room metadata")
            else:
                logger.warning("⚠️ No agent context provided - worker may not have business/user info")
            
            logger.debug(f"📋 Complete metadata for worker: {metadata}")
            
            # Create the room
            room_info = await self.create_room(room_name, metadata)
            
            logger.info(f"✅ Voice session room created: {room_name} for user: {user_id}")
            logger.info("🎯 Room is ready for automatic worker dispatch")
            
            return room_info
            
        except Exception as e:
            logger.error(f"❌ Failed to create voice session room '{room_name}': {e}")
            import traceback
            logger.debug(f"🐛 Voice session room creation traceback: {traceback.format_exc()}")
            raise

    def generate_user_token(self, room_name: str, user_id: str, user_name: str = "") -> str:
        """Generate a user token for joining a LiveKit room"""
        try:
            logger.info(f"🎫 Generating user token for room: {room_name}")
            logger.debug(f"👤 User: {user_id} ({user_name})")
            
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
            
            logger.info(f"✅ User token generated for room: {room_name}")
            logger.debug(f"🎫 Token (first 20 chars): {jwt_token[:20]}...")
            
            return jwt_token
            
        except Exception as e:
            logger.error(f"❌ Failed to generate user token for room '{room_name}': {e}")
            import traceback
            logger.debug(f"🐛 Token generation traceback: {traceback.format_exc()}")
            raise

    def get_connection_url(self) -> str:
        """Get the WebSocket connection URL for LiveKit"""
        logger.debug(f"🌐 Returning connection URL: {self.ws_url}")
        return self.ws_url 