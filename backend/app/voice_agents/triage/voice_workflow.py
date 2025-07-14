"""
Voice Workflow for Triage Agent System

Voice workflow implementation that integrates with OpenAI Agents SDK VoicePipeline.
Provides proper STT -> LLM -> TTS chain using the triage agent system.
"""

from typing import AsyncIterator, Dict, Any, List, Optional
from collections.abc import AsyncIterator as AsyncIteratorABC
import logging

from agents import Agent, Runner, TResponseInputItem
from agents.voice import VoiceWorkflowBase, VoiceWorkflowHelper
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

from .triage_agent import TriageAgent
from .context_manager import ContextManager

logger = logging.getLogger(__name__)


class Hero365VoiceWorkflow(VoiceWorkflowBase):
    """
    Voice workflow for Hero365 triage agent system.
    
    This workflow integrates with the OpenAI Agents SDK VoicePipeline to provide
    proper STT -> LLM -> TTS processing using the Hero365 triage agent system.
    """
    
    def __init__(
        self, 
        business_context: Dict[str, Any],
        user_context: Dict[str, Any],
        context_manager: Optional[ContextManager] = None
    ):
        """
        Initialize the voice workflow.
        
        Args:
            business_context: Business information and context
            user_context: User information and preferences
            context_manager: Optional context manager for enhanced context handling
        """
        super().__init__()
        
        self.business_context = business_context
        self.user_context = user_context
        self.context_manager = context_manager or ContextManager(business_context, user_context)
        
        # Initialize the triage agent
        self.triage_agent = TriageAgent(
            business_context=business_context,
            user_context=user_context,
            context_manager=self.context_manager
        )
        
        # Conversation history for the OpenAI Agents SDK
        self._conversation_history: List[TResponseInputItem] = []
        
        # Current active agent (starts with triage)
        self._current_agent: Agent = self.triage_agent.create_agent()
        
        logger.info(f"🎯 Initialized Hero365VoiceWorkflow for business: {business_context.get('name')}")
    
    async def run(self, transcription: str) -> AsyncIteratorABC[str]:
        """
        Process a transcribed user message and generate a response.
        
        This method is called by the VoicePipeline after STT processing.
        It uses the OpenAI Agents SDK to process the text and returns
        streaming text chunks for TTS processing.
        
        Args:
            transcription: The transcribed text from the user's speech
            
        Yields:
            str: Text chunks for TTS processing
        """
        try:
            logger.info(f"🎤 Processing transcription: '{transcription}'")
            
            # Add user input to conversation history
            self._conversation_history.append({
                "role": "user", 
                "content": transcription
            })
            
            # Check for empty transcription
            if not transcription.strip():
                logger.warning("⚠️ Empty transcription received")
                yield "I didn't catch that. Could you please repeat?"
                return
            
            # Use the OpenAI Agents SDK Runner to process the request
            logger.info("🤖 Running agent with OpenAI Agents SDK...")
            
            # Run the agent with streaming support
            result = Runner.run_streamed(
                self._current_agent,
                self._conversation_history,
                max_turns=20  # Allow for proper handoffs
            )
            
            # Stream text chunks as they come in for faster TTS processing
            response_chunks = []
            async for chunk in VoiceWorkflowHelper.stream_text_from(result):
                response_chunks.append(chunk)
                yield chunk
            
            # Update conversation history with the full response
            full_response = ''.join(response_chunks)
            if full_response.strip():
                self._conversation_history.append({
                    "role": "assistant",
                    "content": full_response
                })
            
            # Update the current agent if a handoff occurred
            if hasattr(result, 'last_agent') and result.last_agent:
                self._current_agent = result.last_agent
                logger.info(f"🔄 Agent handoff occurred, now using: {self._current_agent.name}")
            
            # Update conversation history from the result
            if hasattr(result, 'to_input_list'):
                self._conversation_history = result.to_input_list()
            
            logger.info(f"✅ Successfully processed transcription, generated {len(full_response)} characters")
            
        except Exception as e:
            logger.error(f"❌ Error processing transcription: {str(e)}")
            
            # Provide appropriate error response based on the error type
            if "Max turns" in str(e):
                error_response = "I'm working on your request. Let me help you more directly - could you rephrase your question?"
            elif "handoff" in str(e).lower():
                error_response = "I'm connecting you with the right specialist. Please try again."
            else:
                error_response = "I'm having trouble processing that request. Could you please try again?"
            
            yield error_response
            
            # Add error response to history
            self._conversation_history.append({
                "role": "assistant",
                "content": error_response
            })
    
    def get_conversation_history(self) -> List[TResponseInputItem]:
        """Get the current conversation history."""
        return self._conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self._conversation_history.clear()
        logger.info("🗑️ Conversation history cleared")
    
    def get_current_agent_name(self) -> str:
        """Get the name of the currently active agent."""
        return self._current_agent.name if self._current_agent else "Unknown"
    
    def reset_to_triage_agent(self):
        """Reset the workflow to use the triage agent."""
        self._current_agent = self.triage_agent.create_agent()
        logger.info("🔄 Reset to triage agent")
    
    def get_personalized_greeting(self) -> str:
        """Get a personalized greeting for the user."""
        return self.triage_agent.get_personalized_greeting()
    
    def get_available_capabilities(self) -> Dict[str, List[str]]:
        """Get the available capabilities for the current session."""
        return self.triage_agent.get_available_capabilities()
    
    def update_context(self, updates: Dict[str, Any]):
        """Update the context manager with new information."""
        self.triage_agent.update_context(updates)
        if self.context_manager:
            self.context_manager.refresh_context()
        logger.info("📝 Context updated")
    
    def is_driving_mode(self) -> bool:
        """Check if the user is in driving mode."""
        return self.user_context.get('is_driving', False)
    
    def get_safety_mode(self) -> bool:
        """Check if safety mode is enabled."""
        return self.user_context.get('safety_mode', True)
    
    def get_context_summary(self) -> str:
        """Get summary of current context for debugging."""
        return self.context_manager.get_context_summary() if self.context_manager else "No context available" 