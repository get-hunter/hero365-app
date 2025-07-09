"""
LiveKit service for managing rooms and tokens
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global variables for graceful degradation
livekit_available = False
AccessToken = None
VideoGrants = None
RoomServiceClient = None

try:
    from livekit.api import AccessToken, VideoGrants, LiveKitAPI
    livekit_available = True
    logger.info("LiveKit API imported successfully")
except ImportError as e:
    logger.warning(f"LiveKit API not available: {e}")
    livekit_available = False


class LiveKitService:
    """Service for managing LiveKit rooms and tokens"""
    
    def __init__(self):
        self.settings = settings
        self.api_client = None
        
        if livekit_available and self.settings.livekit_enabled:
            try:
                self.api_client = LiveKitAPI(
                    url=self.settings.LIVEKIT_URL,
                    api_key=self.settings.LIVEKIT_API_KEY,
                    api_secret=self.settings.LIVEKIT_API_SECRET
                )
                logger.info("LiveKit API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize LiveKit API client: {e}")
                self.api_client = None
    
    def is_available(self) -> bool:
        """Check if LiveKit is available and properly configured"""
        return livekit_available and self.api_client is not None
    
    def get_connection_url(self) -> str:
        """Get the LiveKit connection URL"""
        return self.settings.LIVEKIT_URL or ""
    
    async def create_voice_session_room(self, session_id: str, user_id: str, room_name: str = None) -> Optional[Dict[str, Any]]:
        """Create a new room for a voice session"""
        if not self.is_available():
            logger.warning("LiveKit not available, cannot create room")
            return None
        
        try:
            if room_name is None:
                room_name = f"voice-session-{session_id}"
            
            # Import CreateRoomRequest
            from livekit.api.room_service import CreateRoomRequest
            
            # Create room request
            request = CreateRoomRequest()
            request.name = room_name
            request.metadata = f"voice_session:{session_id}:user:{user_id}"
            
            # Create room using the room service
            room_info = await self.api_client.room.create_room(request)
            
            logger.info(f"Created LiveKit room: {room_name}")
            logger.info(f"Room info: name={room_info.name}, sid={room_info.sid}, num_participants={room_info.num_participants}")
            
            return {
                "room_name": room_name,
                "room_sid": room_info.sid,
                "creation_time": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to create LiveKit room: {e}")
            return None
    
    def generate_user_token(self, room_name: str, user_id: str) -> Optional[str]:
        """Generate a user token for joining a room"""
        if not livekit_available:
            logger.warning("LiveKit not available, cannot generate token")
            return None
        
        try:
            # Create video grants with proper permissions
            grants = VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
                can_update_own_metadata=True
            )
            
            # Create access token with grants
            token = AccessToken(
                api_key=self.settings.LIVEKIT_API_KEY,
                api_secret=self.settings.LIVEKIT_API_SECRET
            ).with_identity(user_id).with_grants(grants)
            
            jwt_token = token.to_jwt()
            logger.info(f"Generated user token for room {room_name}")
            
            # Debug: decode and log token contents
            import json
            import base64
            try:
                # Split the JWT to get the payload
                header, payload, signature = jwt_token.split('.')
                # Add padding if needed
                payload += '=' * (4 - len(payload) % 4)
                decoded_payload = base64.b64decode(payload)
                token_data = json.loads(decoded_payload)
                logger.info(f"Token payload: {json.dumps(token_data, indent=2)}")
            except Exception as e:
                logger.error(f"Failed to decode token for debugging: {e}")
            
            return jwt_token
        except Exception as e:
            logger.error(f"Failed to generate user token: {e}")
            return None
    
    def generate_agent_token(self, room_name: str, agent_id: str) -> Optional[str]:
        """Generate an agent token for joining a room"""
        if not livekit_available:
            logger.warning("LiveKit not available, cannot generate token")
            return None
        
        try:
            # Create video grants with admin permissions for the agent
            grants = VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
                can_update_own_metadata=True,
                room_admin=True
            )
            
            # Create access token with grants
            token = AccessToken(
                api_key=self.settings.LIVEKIT_API_KEY,
                api_secret=self.settings.LIVEKIT_API_SECRET
            ).with_identity(f"agent-{agent_id}").with_grants(grants)
            
            jwt_token = token.to_jwt()
            logger.info(f"Generated agent token for room {room_name}")
            
            # Debug: decode and log token contents
            import json
            import base64
            try:
                # Split the JWT to get the payload
                header, payload, signature = jwt_token.split('.')
                # Add padding if needed
                payload += '=' * (4 - len(payload) % 4)
                decoded_payload = base64.b64decode(payload)
                token_data = json.loads(decoded_payload)
                logger.info(f"Agent token payload: {json.dumps(token_data, indent=2)}")
            except Exception as e:
                logger.error(f"Failed to decode agent token for debugging: {e}")
            
            return jwt_token
        except Exception as e:
            logger.error(f"Failed to generate agent token: {e}")
            return None
    
    async def get_room_info(self, room_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a room"""
        if not self.is_available():
            return None
        
        try:
            room_info = await self.api_client.room.list_rooms(names=[room_name])
            if room_info and len(room_info.rooms) > 0:
                room = room_info.rooms[0]
                return {
                    "name": room.name,
                    "sid": room.sid,
                    "num_participants": room.num_participants,
                    "creation_time": room.creation_time,
                    "metadata": room.metadata
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get room info: {e}")
            return None
    
    async def list_participants(self, room_name: str) -> List[Dict[str, Any]]:
        """List participants in a room"""
        if not self.is_available():
            return []
        
        try:
            participants = await self.api_client.room.list_participants(room=room_name)
            return [
                {
                    "identity": p.identity,
                    "joined_at": p.joined_at,
                    "metadata": p.metadata
                }
                for p in participants.participants
            ]
        except Exception as e:
            logger.error(f"Failed to list participants: {e}")
            return []
    
    async def close_room(self, room_name: str) -> bool:
        """Close a room"""
        if not self.is_available():
            return False
        
        try:
            await self.api_client.room.delete_room(room_name)
            logger.info(f"Closed LiveKit room: {room_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to close room: {e}")
            return False
    
    async def update_room_metadata(self, room_name: str, metadata: str) -> bool:
        """Update room metadata"""
        if not self.is_available():
            return False
        
        try:
            await self.api_client.room.update_room_metadata(
                room=room_name,
                metadata=metadata
            )
            logger.info(f"Updated room metadata for: {room_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to update room metadata: {e}")
            return False
    
    async def disconnect_participant(self, room_name: str, participant_identity: str) -> bool:
        """Disconnect a participant from a room"""
        if not self.is_available():
            return False
        
        try:
            await self.api_client.room.remove_participant(
                room=room_name,
                identity=participant_identity
            )
            logger.info(f"Disconnected participant {participant_identity} from room {room_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect participant: {e}")
            return False


# Global service instance
livekit_service = LiveKitService() if livekit_available else None

if livekit_service and livekit_service.is_available():
    logger.info("LiveKit service initialized and available")
else:
    logger.warning("LiveKit service not available") 