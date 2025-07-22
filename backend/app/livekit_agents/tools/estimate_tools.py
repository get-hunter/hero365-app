"""
Estimate Management Tools for Hero365 LiveKit Agents

Refactored to use EstimateService for unified business logic.
"""

import logging
import uuid
from typing import Dict, Any, Optional
from livekit.agents import function_tool

logger = logging.getLogger(__name__)


class EstimateTools:
    """Estimate management tools for the Hero365 agent"""
    
    def __init__(self, session_context: Dict[str, Any], context_intelligence: Optional[Any] = None):
        self.session_context = session_context
        self.context_intelligence = context_intelligence
        self._container = None
        self._estimate_service = None
        
    def _get_container(self):
        """Get dependency injection container"""
        if not self._container:
            try:
                from app.infrastructure.config.dependency_injection import get_container
                self._container = get_container()
                logger.info("✅ Retrieved container for EstimateTools")
            except Exception as e:
                logger.error(f"❌ Error getting container: {e}")
                return None
        return self._container
    
    def _get_estimate_service(self):
        """Get estimate service with caching"""
        if not self._estimate_service:
            container = self._get_container()
            if container:
                try:
                    # Try to get estimate service from container
                    # If not available, create with repository
                    try:
                        self._estimate_service = container.get_estimate_service()
                    except:
                        # Fallback: create service manually
                        from app.application.services.estimate_service import EstimateService
                        estimate_repo = container.get_estimate_repository()
                        self._estimate_service = EstimateService(estimate_repo)
                    
                    logger.info("✅ Estimate service retrieved successfully")
                except Exception as e:
                    logger.error(f"❌ Error getting estimate service: {e}")
                    return None
        return self._estimate_service
    
    def _get_business_id(self) -> Optional[uuid.UUID]:
        """Get business ID from context"""
        business_id = self.session_context.get('business_id')
        if business_id:
            if isinstance(business_id, str):
                return uuid.UUID(business_id)
            return business_id
        return None
    
    def _get_user_id(self) -> str:
        """Get user ID from context (for voice agent, this is typically 'voice_agent')"""
        return self.session_context.get('user_id', 'voice_agent')

    @function_tool
    async def create_estimate(
        self,
        title: str,
        description: str,
        contact_id: Optional[str] = None,
        total_amount: Optional[float] = None,
        valid_until: Optional[str] = None,
        client_name: Optional[str] = None,
        client_email: Optional[str] = None
    ) -> str:
        """Create a new estimate with context-aware assistance.
        
        Args:
            title: Estimate title/summary
            description: Detailed estimate description
            contact_id: ID of the contact for this estimate
            total_amount: Total estimated amount
            valid_until: Estimate validity date (YYYY-MM-DD format)
            client_name: Client name (if no contact_id provided)
            client_email: Client email (if no contact_id provided)
        """
        try:
            logger.info(f"📊 Creating estimate: {title}")
            
            # Get business context
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            user_id = self._get_user_id()
            
            # Get estimate service
            estimate_service = self._get_estimate_service()
            if not estimate_service:
                return "Estimate service not available"
            
            # Create quick estimate using service
            result = await estimate_service.create_quick_estimate(
                business_id=business_id,
                user_id=user_id,
                title=title,
                client_name=client_name,
                client_email=client_email,
                total_amount=total_amount,
                description=description
            )
            
            response = f"Successfully created estimate '{title}' with number {result.estimate_number}"
            if total_amount:
                response += f" for ${total_amount:,.2f}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error creating estimate: {e}")
            return f"Error creating estimate: {str(e)}"

    @function_tool
    async def get_recent_estimates(self, limit: int = 10, days: int = 30) -> str:
        """Get recent estimates with service layer integration.
        
        Args:
            limit: Maximum number of estimates to return
            days: Number of days to look back (default 30, use 365 for all estimates)
        """
        try:
            logger.info(f"📋 Getting recent estimates (limit: {limit}, days: {days})")
            
            # Get business context
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available - no business ID found"
            
            user_id = self._get_user_id()
            
            # Get estimate service
            estimate_service = self._get_estimate_service()
            if not estimate_service:
                return "Estimate service not available"
            
            # Use service to get recent estimates
            if days >= 365:
                # Get all estimates using list method
                result = await estimate_service.list_estimates(
                    business_id=business_id,
                    user_id=user_id,
                    limit=limit
                )
                estimates = result["estimates"]
            else:
                # Get recent estimates
                result = await estimate_service.get_recent_estimates(
                    business_id=business_id,
                    user_id=user_id,
                    days=days,
                    limit=limit
                )
                estimates = result["estimates"]
            
            if estimates:
                logger.info(f"✅ Found {len(estimates)} estimates")
                
                response = f"Here are your {len(estimates)} most recent estimates"
                if days < 365:
                    response += f" from the last {days} days"
                response += ": "
                
                estimate_list = []
                for i, estimate in enumerate(estimates, 1):
                    estimate_info = f"{i}. {estimate.title}, status {estimate.status_display}"
                    if estimate.total_amount and estimate.total_amount > 0:
                        estimate_info += f" for ${float(estimate.total_amount):,.2f}"
                    estimate_info += f", for {estimate.client_display_name}"
                    estimate_list.append(estimate_info)
                
                response += ". ".join(estimate_list)
                return response
            else:
                if days == 30:
                    return "No estimates found in the last 30 days. Would you like me to check older estimates or create a new estimate?"
                else:
                    return f"No estimates found in the last {days} days. Would you like to create a new estimate?"
                
        except Exception as e:
            logger.error(f"❌ Error getting recent estimates: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return f"Error getting recent estimates: {str(e)}"

    @function_tool
    async def get_pending_estimates(self, limit: int = 10) -> str:
        """Get all pending estimates regardless of age.
        
        Args:
            limit: Maximum number of estimates to return
        """
        try:
            logger.info(f"📋 Getting pending estimates (limit: {limit})")
            
            # Get business context
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            user_id = self._get_user_id()
            
            # Get estimate service
            estimate_service = self._get_estimate_service()
            if not estimate_service:
                return "Estimate service not available"
            
            # Get pending estimates using service
            result = await estimate_service.get_pending_estimates(
                business_id=business_id,
                user_id=user_id,
                limit=limit
            )
            
            estimates = result["estimates"]
            
            if estimates:
                response = f"Here are your {len(estimates)} pending estimates: "
                estimate_list = []
                
                for i, estimate in enumerate(estimates, 1):
                    estimate_info = f"{i}. {estimate.title}, status {estimate.status_display}"
                    if estimate.total_amount and estimate.total_amount > 0:
                        estimate_info += f" for ${float(estimate.total_amount):,.2f}"
                    estimate_info += f", for {estimate.client_display_name}"
                    estimate_list.append(estimate_info)
                
                response += ". ".join(estimate_list)
                return response
            else:
                return "No pending estimates found. All your estimates may be completed or you may need to create new ones."
                
        except Exception as e:
            logger.error(f"❌ Error getting pending estimates: {e}")
            return f"Error getting pending estimates: {str(e)}"

    @function_tool
    async def get_suggested_estimates(self, limit: int = 5) -> str:
        """Get suggested estimates based on draft status.
        
        Args:
            limit: Maximum number of suggestions to return
        """
        try:
            logger.info("💡 Getting suggested estimates")
            
            # Get business context
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            user_id = self._get_user_id()
            
            # Get estimate service
            estimate_service = self._get_estimate_service()
            if not estimate_service:
                return "Estimate service not available"
            
            # Get suggestions using service
            result = await estimate_service.get_estimate_suggestions(
                business_id=business_id,
                user_id=user_id,
                limit=limit
            )
            
            estimates = result["estimates"]
            
            if estimates:
                response = f"Here are {len(estimates)} draft estimates that need attention: "
                estimate_list = []
                for i, estimate in enumerate(estimates, 1):
                    estimate_info = f"{i}. {estimate.title} for {estimate.client_display_name}"
                    if estimate.total_amount and estimate.total_amount > 0:
                        estimate_info += f" worth ${float(estimate.total_amount):,.2f}"
                    estimate_list.append(estimate_info)
                
                response += ". ".join(estimate_list)
                return response
            else:
                return "No draft estimates found. All estimates are up to date!"
                
        except Exception as e:
            logger.error(f"❌ Error getting estimate suggestions: {e}")
            return f"Error getting estimate suggestions: {str(e)}"

    @function_tool
    async def search_estimates(self, query: str, limit: int = 10) -> str:
        """Search for estimates using the service layer.
        
        Args:
            query: Search query (title, description, contact name, etc.)
            limit: Maximum number of results to return
        """
        try:
            logger.info(f"🔍 Searching estimates for: {query}")
            
            # Get business context
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            user_id = self._get_user_id()
            
            # Get estimate service
            estimate_service = self._get_estimate_service()
            if not estimate_service:
                return "Estimate service not available"
            
            # Search using service
            result = await estimate_service.search_estimates(
                business_id=business_id,
                user_id=user_id,
                search_term=query,
                limit=limit
            )
            
            estimates = result["estimates"]
            
            if estimates:
                response = f"Found {len(estimates)} estimates matching '{query}': "
                estimate_list = []
                for i, estimate in enumerate(estimates, 1):
                    estimate_info = f"{i}. {estimate.title}, status {estimate.status_display}"
                    if estimate.total_amount and estimate.total_amount > 0:
                        estimate_info += f" for ${float(estimate.total_amount):,.2f}"
                    estimate_info += f", for {estimate.client_display_name}"
                    estimate_list.append(estimate_info)
                
                response += ". ".join(estimate_list)
                return response
            else:
                return f"No estimates found matching '{query}'. Would you like to create a new estimate?"
                
        except Exception as e:
            logger.error(f"❌ Error searching estimates: {e}")
            return f"Error searching estimates: {str(e)}"

    @function_tool
    async def update_estimate_status(self, estimate_id: str, status: str) -> str:
        """Update the status of a specific estimate using service layer"""
        try:
            logger.info(f"📊 Updating estimate {estimate_id} status to {status}")
            
            # Get business context
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            user_id = self._get_user_id()
            
            # Get estimate service
            estimate_service = self._get_estimate_service()
            if not estimate_service:
                return "Estimate service not available"
            
            # Parse status using service helper
            parsed_status = estimate_service.parse_status_from_string(status)
            if not parsed_status:
                available_statuses = ["draft", "sent", "approved", "rejected", "cancelled"]
                return f"Invalid status '{status}'. Valid options are: {', '.join(available_statuses)}"
            
            # Update status using service
            result = await estimate_service.change_estimate_status(
                estimate_id=uuid.UUID(estimate_id),
                new_status=parsed_status,
                business_id=business_id,
                user_id=user_id,
                reason=f"Status changed via voice agent to {status}"
            )
            
            return f"Successfully updated estimate '{result.title}' status to {result.status_display.lower()}"
                
        except ValueError as e:
            return f"Invalid estimate ID format: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Error updating estimate status: {e}")
            return f"Error updating estimate status: {str(e)}"

    @function_tool
    async def send_estimate(self, estimate_id: str, client_email: Optional[str] = None) -> str:
        """Send an estimate to client using service layer"""
        try:
            logger.info(f"📧 Sending estimate {estimate_id} to client")
            
            # Get business context
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            user_id = self._get_user_id()
            
            # Get estimate service
            estimate_service = self._get_estimate_service()
            if not estimate_service:
                return "Estimate service not available"
            
            # Send estimate using service
            result = await estimate_service.send_estimate(
                estimate_id=uuid.UUID(estimate_id),
                business_id=business_id,
                user_id=user_id,
                client_email=client_email
            )
            
            return f"Successfully sent estimate '{result.title}' to {result.client_display_name}"
                
        except ValueError as e:
            return f"Invalid estimate ID format: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Error sending estimate: {e}")
            return f"Error sending estimate: {str(e)}"

    @function_tool
    async def get_estimate_stats(self, period_days: int = 30) -> str:
        """Get estimate statistics using service layer"""
        try:
            logger.info(f"📈 Getting estimate statistics for {period_days} days")
            
            # Get business context
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            user_id = self._get_user_id()
            
            # Get estimate service
            estimate_service = self._get_estimate_service()
            if not estimate_service:
                return "Estimate service not available"
            
            # Get stats using service
            stats = await estimate_service.get_estimate_stats(
                business_id=business_id,
                user_id=user_id,
                period_days=period_days
            )
            
            response_parts = [
                f"Here are your estimate statistics for the last {period_days} days:",
                f"• {stats['total_recent']} total estimates",
                f"• {stats['total_pending']} pending approval",
                f"• {stats['total_drafts']} drafts need attention",
                f"• {stats['total_expiring']} expiring soon",
                f"• ${stats['total_value']:,.2f} total value",
                f"• ${stats['average_value']:,.2f} average value per estimate"
            ]
            
            return " ".join(response_parts)
                
        except Exception as e:
            logger.error(f"❌ Error getting estimate stats: {e}")
            return f"Error getting estimate stats: {str(e)}"

    @function_tool
    async def convert_estimate_to_invoice(self, estimate_id: str) -> str:
        """Convert an approved estimate to an invoice using service layer"""
        try:
            logger.info(f"💰 Converting estimate {estimate_id} to invoice")
            
            # Get business context
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            user_id = self._get_user_id()
            
            # Get estimate service
            estimate_service = self._get_estimate_service()
            if not estimate_service:
                return "Estimate service not available"
            
            # Get the estimate first to check status
            estimate = await estimate_service.get_estimate(
                estimate_id=uuid.UUID(estimate_id),
                business_id=business_id,
                user_id=user_id
            )
            
            # Check if estimate is approved
            if estimate.status.value != "approved":
                return f"Only approved estimates can be converted to invoices. Current status is {estimate.status_display.lower()}"
            
            # Mark as converted (actual invoice creation would be handled by invoice service)
            result = await estimate_service.change_estimate_status(
                estimate_id=uuid.UUID(estimate_id),
                new_status="converted",
                business_id=business_id,
                user_id=user_id,
                reason="Converted to invoice via voice agent"
            )
            
            return f"Estimate '{result.title}' has been marked as converted to invoice. Invoice creation functionality will be implemented in the next phase."
                
        except ValueError as e:
            return f"Invalid estimate ID format: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Error converting estimate to invoice: {e}")
            return f"Error converting estimate to invoice: {str(e)}" 