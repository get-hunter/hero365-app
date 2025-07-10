#!/usr/bin/env python3

"""
Hero365 Voice Agent Worker
Starting from simple worker base and adding business features incrementally.

Following LiveKit Agents framework patterns:
- GitHub: https://github.com/livekit/agents
- Docs: https://docs.livekit.io/agents/

SDK Version: 1.1.5
"""

import logging
import os
import sys
from pathlib import Path

# Add parent directory for app imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment configuration
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent.parent / "environments" / ".env")

# LiveKit Agents SDK imports
import livekit.agents as agents
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents import Agent, AgentSession
from livekit.plugins import silero, openai, deepgram, cartesia

# Business imports - core application features
from app.voice_agents.personal.personal_agent import PersonalVoiceAgent
from app.voice_agents.core.voice_config import PersonalAgentConfig, AgentType, VoiceProfile, VoiceModel
from app.infrastructure.config.dependency_injection import get_business_repository
from app.core.auth_facade import auth_facade

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """
    Agent entrypoint - called when user joins a room.
    Starts simple and adds business features when available.
    """
    logger.info("🎯 HERO365 AGENT ENTRYPOINT CALLED!")
    logger.info(f"🚀 Agent starting for room: {ctx.room.name}")
    logger.info(f"🔍 Room participants: {len(ctx.room.remote_participants)}")
    
    # Connect to room with audio subscription
    logger.info("🔌 Connecting to LiveKit room...")
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)
    logger.info("✅ Connected to LiveKit room")
    
    # Wait for participant to join (critical for working!)
    participant = await ctx.wait_for_participant()
    logger.info(f"👤 Participant joined: {participant.identity}")
    
    # Try to get business context if available
    agent_context = None
    use_business_features = False
    
    if ctx.room.name.startswith("voice-session-"):
        # Parse room name: voice-session-{user_id}-{business_id}
        room_suffix = ctx.room.name.replace("voice-session-", "")
        
        # Split by dashes and try to identify the business_id (last UUID)
        # Format: voice-session-{user_id}-{business_id}
        # Both are UUIDs with format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        parts = room_suffix.split("-")
        
        if len(parts) >= 10:  # At least 2 UUIDs (5 parts each)
            # Take the last 5 parts as business_id, everything else as user_id
            business_id_parts = parts[-5:]
            user_id_parts = parts[:-5]
            
            business_id = "-".join(business_id_parts)
            user_id = "-".join(user_id_parts)
            
            logger.info(f"🆔 Parsed room name: user_id={user_id}, business_id={business_id}")
            
            try:
                # Fetch business data from database
                business_repository = get_business_repository()
                business_entity = await business_repository.get_by_id(business_id)
                
                if business_entity:
                    business_context = {
                        "id": str(business_entity.id),
                        "name": business_entity.name,
                        "type": business_entity.industry or "Home Services",
                        "industry": business_entity.industry or "home_services",
                        "company_size": business_entity.company_size.value if business_entity.company_size else "small",
                        "description": business_entity.description,
                        "phone": business_entity.phone_number,
                        "email": business_entity.business_email,
                        "website": business_entity.website
                    }
                    
                    # Fetch user data from auth system
                    user_data = await auth_facade.get_user_by_id(user_id)
                    
                    if user_data:
                        user_context = {
                            "id": user_id,
                            "name": user_data.get("name") or user_data.get("email", "User"),
                            "email": user_data.get("email", ""),
                            "preferred_language": "en",
                            "timezone": "UTC"
                        }
                        
                        # Create agent context
                        agent_context = {
                            "business_context": business_context,
                            "user_context": user_context,
                            "agent_config": {
                                "temperature": 0.7,
                                "max_duration": 3600
                            }
                        }
                        
                        logger.info(f"📋 Business context loaded from database!")
                        logger.info(f"🏢 Business: {business_context['name']}")
                        logger.info(f"👤 User: {user_context['name']} ({user_context['email']})")
                        use_business_features = True
                        
                    else:
                        logger.warning(f"⚠️ User not found in auth system: {user_id}")
                        
                else:
                    logger.warning(f"⚠️ Business not found in database: {business_id}")
                    
            except Exception as e:
                logger.error(f"❌ Error fetching business/user data: {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
        else:
            logger.warning(f"⚠️ Invalid room name format: {ctx.room.name}")
            logger.warning("Expected format: voice-session-{user_id}-{business_id}")
            logger.warning(f"Got {len(parts)} parts, expected at least 10")
    else:
        logger.info(f"🔍 Room name '{ctx.room.name}' doesn't match expected format 'voice-session-*'")
        logger.info("🔄 Using simple mode for this room")
    
    # Create agent based on available features
    if use_business_features and agent_context:
        agent = await create_business_agent(agent_context)
        greeting_msg = create_business_greeting(agent_context)
    else:
        agent = create_simple_agent()
        greeting_msg = "Greet the user warmly and introduce yourself as Hero365 AI assistant. Ask how you can help them today."
    
    # Create AgentSession (same as simple worker)
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(
            model="sonic-2",
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22"
        )
    )
    
    # Start the session
    logger.info("🎙️ Starting agent session...")
    await session.start(agent=agent, room=ctx.room)
    logger.info("✅ Agent session started successfully")
    
    # Generate greeting
    await session.generate_reply(instructions=greeting_msg)
    
    if use_business_features:
        logger.info("💬 Business agent ready with tools")
    else:
        logger.info("💬 Simple agent ready")


def create_simple_agent() -> Agent:
    """Create a simple agent without business features."""
    logger.info("🔄 Creating simple Hero365 agent")
    
    return Agent(
        instructions=(
            "You are Hero365 AI, a helpful assistant for home services businesses. "
            "You can help with general questions, business planning, and provide guidance. "
            "Be friendly, professional, and concise in your responses."
        )
    )


async def create_business_agent(agent_context: dict) -> Agent:
    """Create a business agent with full context and tools."""
    logger.info("🏢 Creating business agent with context")
    
    try:
        # Extract context components
        business_context = agent_context.get("business_context", {})
        user_context = agent_context.get("user_context", {})
        agent_config_data = agent_context.get("agent_config", {})
        
        # Log context details
        business_name = business_context.get("name", "Hero365")
        user_name = user_context.get("name", "Unknown")
        business_type = business_context.get("type", "Home Services")
        
        logger.info(f"📋 Business context loaded:")
        logger.info(f"   🏢 Business: {business_name} ({business_type})")
        logger.info(f"   👤 User: {user_name}")
        logger.info(f"   📧 Email: {user_context.get('email', 'N/A')}")
        
        # Create agent configuration
        agent_config = PersonalAgentConfig(
            agent_type=AgentType.PERSONAL,
            agent_name=f"{business_name} AI Assistant",
            voice_profile=VoiceProfile.PROFESSIONAL,
            voice_model=VoiceModel.SONIC_2,
            temperature=agent_config_data.get("temperature", 0.7),
            max_conversation_duration=agent_config_data.get("max_duration", 3600)
        )
        
        # Create PersonalVoiceAgent
        personal_agent = PersonalVoiceAgent(
            business_context=business_context,
            user_context=user_context,
            agent_config=agent_config
        )
        
        # Create LiveKit Agent with business capabilities
        agent = Agent(
            instructions=personal_agent.get_system_prompt(),
            tools=personal_agent.get_tools()
        )
        
        logger.info(f"🏢 Business agent created with {len(personal_agent.get_tools())} tools")
        return agent
        
    except Exception as e:
        logger.error(f"❌ Error creating business agent: {e}")
        logger.info("🔄 Falling back to simple agent")
        return create_simple_agent()


def create_business_greeting(agent_context: dict) -> str:
    """Create a personalized greeting for business agent."""
    business_context = agent_context.get("business_context", {})
    user_context = agent_context.get("user_context", {})
    
    business_name = business_context.get("name", "Hero365")
    user_name = user_context.get("name", "there")
    business_type = business_context.get("type", "Home Services")
    
    greeting = f"Greet {user_name} warmly and introduce yourself as the AI assistant for {business_name}"
    
    if business_type and business_type != "Home Services":
        greeting += f", a {business_type} business"
    
    greeting += ". Mention that you can help with scheduling, estimates, invoices, project management, and general business inquiries. Ask how you can assist them today."
    
    return greeting


def main():
    """Main worker entry point."""
    logger.info("🚀 Starting Hero365 Voice Agent Worker")
    
    # Verify required environment variables
    required_vars = [
        "LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY", "DEEPGRAM_API_KEY", "CARTESIA_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    logger.info("✅ Environment variables validated")
    
    # Debug connection info
    logger.info(f"🔍 LIVEKIT_URL: {os.getenv('LIVEKIT_URL')}")
    logger.info(f"🔍 LIVEKIT_API_KEY: {os.getenv('LIVEKIT_API_KEY', 'NOT_SET')[:10]}...")
    
    # Configure worker with automatic dispatch
    worker_options = WorkerOptions(entrypoint_fnc=entrypoint)
    
    logger.info("🎯 Worker configured for automatic room dispatch")
    logger.info("⏳ Waiting for room assignments...")
    
    # Start the worker
    cli.run_app(worker_options)


if __name__ == "__main__":
    main() 