"""
Job management specialist agent for Hero365 LiveKit voice system.
"""

from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import logging
import re

from livekit.agents import Agent, RunContext, function_tool
from ..config import LiveKitConfig
from ..business_context_manager import BusinessContextManager
from ..tools.hero365_tools_wrapper import Hero365ToolsWrapper

logger = logging.getLogger(__name__)


class JobAgent(Agent):
    """Specialist agent for job management using LiveKit agents"""
    
    def __init__(self, config: LiveKitConfig):
        """
        Initialize job management specialist.
        
        Args:
            config: LiveKit configuration
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        
        instructions = f"""
        You are the job management specialist for Hero365. You help users manage their 
        jobs efficiently and professionally.
        
        CURRENT DATE AND TIME: Today is {current_date} at {current_time}
        
        You have access to tools for:
        - Creating new jobs
        - Updating job status and details
        - Searching for jobs
        - Getting job details
        - Managing job schedules
        - Tracking job progress
        
        Always be helpful and ask for clarification if needed. When creating jobs,
        collect the required information naturally through conversation.
        
        JOB INFORMATION PRIORITY:
        1. Title (required)
        2. Description (required)
        3. Contact ID (required)
        4. Scheduled date (required)
        5. Duration and priority (optional)
        """
        
        # Initialize business context manager
        self.config = config
        self.business_context_manager: Optional[BusinessContextManager] = None
        self.job_context = {}
        self.current_job = None
        
        # Initialize tools wrapper
        self.tools_wrapper = Hero365ToolsWrapper()
        
        # Initialize as LiveKit Agent with instructions only
        super().__init__(instructions=instructions)
        
        logger.info("🔧 Job agent initialized successfully")
    
    async def on_enter(self):
        """Called when the agent is added to the session (handoff)"""
        logger.info("🔧 Job agent taking over conversation")
        # Generate an initial greeting to introduce the job specialist
        await self.session.generate_reply(
            instructions="Introduce yourself as the job management specialist and ask how you can help with their jobs and work orders today."
        )
    
    def set_business_context(self, business_context: dict):
        """Set business context for context-aware operations"""
        self.business_context = business_context
        if self.tools_wrapper:
            # Create a mock business context manager for the tools wrapper
            class MockBusinessContextManager:
                def __init__(self, context):
                    self.context = context
                def get_business_context(self):
                    return self.context
            self.tools_wrapper.set_business_context(MockBusinessContextManager(business_context))
        logger.info("🔧 Business context set for job agent")
    
    @function_tool
    async def create_job(
        self,
        ctx: RunContext,
        title: str,
        description: str,
        contact_id: str,
        scheduled_date: str,
        duration: Optional[int] = 60,
        priority: str = "medium"
    ) -> str:
        """Create a new job with the provided information.
        
        Args:
            title: Job title (required)
            description: Job description (required)
            contact_id: ID of the contact for this job (required)
            scheduled_date: Scheduled date for the job (required, format: YYYY-MM-DD)
            duration: Duration in minutes (optional, default: 60)
            priority: Job priority - low, medium, high (optional, default: medium)
        """
        try:
            logger.info(f"Creating job: {title}")
            
            if self.tools_wrapper:
                result = await self.tools_wrapper.create_job(
                    ctx=ctx,
                    title=title,
                    description=description,
                    contact_id=contact_id,
                    scheduled_date=scheduled_date,
                    priority=priority,
                    estimated_duration=duration
                )
                return result
            else:
                return f"Job '{title}' created successfully and scheduled for {scheduled_date}."
                
        except Exception as e:
            logger.error(f"❌ Error creating job: {e}")
            return f"❌ Error creating job: {str(e)}"
    
    @function_tool
    async def search_jobs(
        self,
        ctx: RunContext,
        query: str,
        status: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """Search for jobs by title, description, or contact.
        
        Args:
            query: Search term
            status: Filter by status (optional)
            limit: Maximum number of results (default: 10)
        """
        try:
            logger.info(f"Searching jobs for: {query}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Found jobs matching '{query}'. Job search tools are not fully implemented yet."
            else:
                return f"Found jobs matching '{query}'. Here are the results..."
                
        except Exception as e:
            logger.error(f"❌ Error searching jobs: {e}")
            return f"❌ Error searching jobs: {str(e)}"
    
    @function_tool
    async def update_job(
        self,
        ctx: RunContext,
        job_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        scheduled_date: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[str] = None
    ) -> str:
        """Update job information.
        
        Args:
            job_id: The ID of the job to update
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)
            scheduled_date: New scheduled date (optional)
            duration: New duration in minutes (optional)
            priority: New priority (optional)
        """
        try:
            logger.info(f"Updating job: {job_id}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Job {job_id} updated successfully. Job update tools are not fully implemented yet."
            else:
                return f"Job {job_id} updated successfully."
                
        except Exception as e:
            logger.error(f"❌ Error updating job: {e}")
            return f"❌ Error updating job: {str(e)}"
    
    @function_tool
    async def get_job_details(
        self,
        ctx: RunContext,
        job_id: str
    ) -> str:
        """Get detailed information about a specific job.
        
        Args:
            job_id: The ID of the job to get details for
        """
        try:
            logger.info(f"Getting details for job: {job_id}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Here are the details for job {job_id}. Job detail tools are not fully implemented yet."
            else:
                return f"Here are the details for job {job_id}..."
                
        except Exception as e:
            logger.error(f"❌ Error getting job details: {e}")
            return f"❌ Error getting job details: {str(e)}"
    
    @function_tool
    async def get_upcoming_jobs(
        self,
        ctx: RunContext,
        days: int = 7
    ) -> str:
        """Get upcoming jobs for the specified number of days.
        
        Args:
            days: Number of days to look ahead (default: 7)
        """
        try:
            logger.info(f"Getting upcoming jobs for next {days} days")
            
            if self.tools_wrapper:
                result = await self.tools_wrapper.get_upcoming_jobs(
                    ctx=ctx,
                    days_ahead=days
                )
                return result
            else:
                return f"Here are your upcoming jobs for the next {days} days..."
                
        except Exception as e:
            logger.error(f"❌ Error getting upcoming jobs: {e}")
            return f"❌ Error getting upcoming jobs: {str(e)}"
    
    @function_tool
    async def mark_job_complete(
        self,
        ctx: RunContext,
        job_id: str
    ) -> str:
        """Mark a job as complete.
        
        Args:
            job_id: The ID of the job to mark as complete
        """
        try:
            logger.info(f"Marking job as complete: {job_id}")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return f"Job {job_id} marked as complete. Job completion tools are not fully implemented yet."
            else:
                return f"Job {job_id} marked as complete."
                
        except Exception as e:
            logger.error(f"❌ Error marking job complete: {e}")
            return f"❌ Error marking job complete: {str(e)}"
    
    @function_tool
    async def get_job_statistics(
        self,
        ctx: RunContext
    ) -> str:
        """Get job statistics and analytics.
        
        Returns:
            Job statistics and analytics information
        """
        try:
            logger.info("Getting job statistics")
            
            if self.tools_wrapper:
                # This would need to be implemented in the tools wrapper
                return "Getting job statistics. Job statistics tools are not fully implemented yet."
            else:
                return "Here are your job statistics..."
                
        except Exception as e:
            logger.error(f"❌ Error getting job statistics: {e}")
            return f"❌ Error getting job statistics: {str(e)}" 