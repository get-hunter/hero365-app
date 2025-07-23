"""
Estimate Management Tools for Hero365 LiveKit Agents

Refactored to use EstimateService for unified business logic.
"""

import logging
import uuid
from typing import Dict, Any, Optional
from livekit.agents import function_tool

from app.domain.entities.estimate_enums.enums import EstimateStatus

logger = logging.getLogger(__name__)


class EstimateTools:
    """
    Estimate management tools for the Hero365 agent.
    
    Features context-aware position referencing: when users say "estimate 1", 
    it refers to position 1 from the most recently shown estimate list 
    (pending, recent, search results, etc.), not from a different list.
    """
    
    def __init__(self, session_context: Dict[str, Any], context_intelligence: Optional[Any] = None):
        self.session_context = session_context
        self.context_intelligence = context_intelligence
        self._container = None
        self._estimate_service = None
        # Conversation context for position-based references
        self._last_shown_estimates = []  # Cache of last estimates shown to user
        self._last_list_type = None      # Type of last list shown (pending, recent, search, etc.)
        
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
    
    async def _resolve_estimate_id(self, estimate_id: str, business_id: uuid.UUID, user_id: str, estimate_service) -> Optional[uuid.UUID]:
        """
        Intelligently resolve estimate ID from various formats with context awareness:
        - UUID string: "123e4567-e89b-12d3-a456-426614174000" 
        - Estimate number: "EST-001"
        - Position number: "1", "2", "3" - refers to position from most recently shown list
          (pending estimates, recent estimates, search results, etc.)
        
        Context-aware behavior: When user says "estimate 1" after seeing a list,
        it refers to position 1 from that specific list, not from a different list.
        """
        try:
            # Try parsing as UUID first
            try:
                return uuid.UUID(estimate_id)
            except ValueError:
                pass
            
            # Try as estimate number (EST-001, QUO-001, etc.)
            if estimate_id.upper().startswith(('EST', 'QUO')):
                try:
                    # Search for estimate by number
                    result = await estimate_service.search_estimates(
                        business_id=business_id,
                        user_id=user_id,
                        search_term=estimate_id.upper(),
                        limit=1
                    )
                    if result.get("estimates"):
                        return result["estimates"][0].id
                except Exception as e:
                    logger.warning(f"Error searching by estimate number: {e}")
            
            # Try as position number (1, 2, 3, etc.)
            try:
                position = int(estimate_id)
                if 1 <= position <= 20:  # Reasonable limit
                    # Use cached estimates from last shown list if available
                    if self._last_shown_estimates and len(self._last_shown_estimates) >= position:
                        cached_estimate = self._last_shown_estimates[position - 1]  # Convert 1-based to 0-based
                        logger.info(f"✅ Using position {position} from cached {self._last_list_type} estimates: {cached_estimate.title}")
                        return cached_estimate.id
                    else:
                        logger.warning(f"❌ Position {position} requested but only {len(self._last_shown_estimates) if self._last_shown_estimates else 0} cached estimates available from {self._last_list_type or 'none'}")
                        return None
                        
            except ValueError:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error resolving estimate ID '{estimate_id}': {e}")
            return None

    def _clear_estimate_cache(self):
        """Clear cached estimates when context changes."""
        self._last_shown_estimates = []
        self._last_list_type = None

    def _get_estimate_not_found_message(self, estimate_id: str) -> str:
        """Generate a helpful error message when estimate ID resolution fails."""
        if estimate_id.isdigit():
            cache_info = f" (cached: {len(self._last_shown_estimates) if self._last_shown_estimates else 0} {self._last_list_type or 'none'} estimates)"
            return f"❌ Position {estimate_id} not found{cache_info}. Try asking for a list of estimates first, then use the position number from that list."
        else:
            return f"❌ Could not find estimate '{estimate_id}'. Please check the estimate number (EST-001) or UUID."

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
            
            # Clear cache since list context has changed
            self._clear_estimate_cache()
            
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
                
                # Cache estimates for position-based references
                self._last_shown_estimates = estimates
                self._last_list_type = "recent"
                
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
                # Cache estimates for position-based references
                self._last_shown_estimates = estimates
                self._last_list_type = "pending"
                
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
                # Cache estimates for position-based references
                self._last_shown_estimates = estimates
                self._last_list_type = "suggestions"
                
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
                # Cache estimates for position-based references
                self._last_shown_estimates = estimates
                self._last_list_type = "search"
                
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
        """Update the status of a specific estimate using service layer
        
        Args:
            estimate_id: Can be a UUID, estimate number (EST-001), or position number (1, 2, 3)
            status: New status for the estimate
        """
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
            
            # Parse target status using domain enum method
            parsed_status = EstimateStatus.parse_from_string(status)
            if not parsed_status:
                available_statuses = [s.value for s in EstimateStatus]
                return f"Invalid status '{status}'. Valid options are: {', '.join(available_statuses)}"
            
            # Smart estimate ID resolution
            actual_estimate_id = await self._resolve_estimate_id(estimate_id, business_id, user_id, estimate_service)
            if not actual_estimate_id:
                return self._get_estimate_not_found_message(estimate_id)
            
            # STEP 1: Get current estimate details first for validation
            logger.info(f"🔍 Fetching current estimate details for validation...")
            try:
                current_estimate = await estimate_service.get_estimate(
                    estimate_id=actual_estimate_id,
                    business_id=business_id,
                    user_id=user_id
                )
            except Exception as e:
                logger.error(f"Failed to fetch estimate details: {e}")
                return f"Could not fetch estimate details: {str(e)}"
            
            # STEP 2: Show current status and validate transition
            current_status = current_estimate.status
            logger.info(f"📋 Current status: {current_status.value if hasattr(current_status, 'value') else current_status} → Target status: {parsed_status.value}")
            
            # Ensure current_status is an enum (defensive programming)
            if isinstance(current_status, str):
                logger.warning(f"⚠️ Current status is string '{current_status}', converting to enum")
                current_status = EstimateStatus.parse_from_string(current_status) or EstimateStatus.DRAFT
            
            # Check if already at target status
            if current_status == parsed_status:
                status_display = current_status.value if hasattr(current_status, 'value') else str(current_status)
                return f"Estimate '{current_estimate.title}' is already in {status_display} status."
            
            # Get available transitions
            available_transitions = estimate_service.get_available_status_transitions(current_status)
            available_status_names = [s.value for s in available_transitions]
            
            # STEP 3: Pre-validate the transition before attempting
            if parsed_status not in available_transitions:
                current_status_display = current_status.value if hasattr(current_status, 'value') else str(current_status)
                if available_status_names:
                    return (f"❌ Cannot change estimate '{current_estimate.title}' from {current_status_display} to {parsed_status.value}. "
                           f"Valid transitions from {current_status_display} are: {', '.join(available_status_names)}")
                else:
                    return (f"❌ Cannot change estimate '{current_estimate.title}' from {current_status_display} to {parsed_status.value}. "
                           f"Status '{current_status_display}' is a terminal state with no allowed transitions.")
            
            # STEP 4: Attempt the status update
            logger.info(f"✅ Transition valid. Updating status...")
            current_status_display = current_status.value if hasattr(current_status, 'value') else str(current_status)
            result = await estimate_service.change_estimate_status(
                estimate_id=actual_estimate_id,
                new_status=parsed_status,
                business_id=business_id,
                user_id=user_id,
                reason=f"Status changed via voice agent from {current_status_display} to {parsed_status.value}"
            )
            
            # Clear cache since estimate status changed
            self._clear_estimate_cache()
            
            return f"✅ Successfully updated estimate '{result.title}' (#{result.estimate_number}) from {current_status_display} to {result.status_display.lower()}"
                
        except Exception as e:
            logger.error(f"❌ Error updating estimate status: {e}")
            # Provide more specific error feedback
            if "Cannot change status from" in str(e):
                return f"❌ Status transition not allowed: {str(e)}"
            elif "not found" in str(e).lower():
                return f"❌ Estimate not found: {str(e)}"
            else:
                return f"❌ Error updating estimate status: {str(e)}"

    @function_tool
    async def send_estimate(self, estimate_id: str, client_email: Optional[str] = None) -> str:
        """Send an estimate to client using service layer
        
        Args:
            estimate_id: Can be a UUID, estimate number (EST-001), or position number (1, 2, 3)
            client_email: Optional client email override
        """
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
            
            # Smart estimate ID resolution
            actual_estimate_id = await self._resolve_estimate_id(estimate_id, business_id, user_id, estimate_service)
            if not actual_estimate_id:
                return self._get_estimate_not_found_message(estimate_id)
            
            # Send estimate using service
            result = await estimate_service.send_estimate(
                estimate_id=actual_estimate_id,
                business_id=business_id,
                user_id=user_id,
                client_email=client_email
            )
            
            # Clear cache since estimate status changed to sent
            self._clear_estimate_cache()
            
            return f"Successfully sent estimate '{result.title}' (#{result.estimate_number}) to {result.client_display_name}"
                
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
        """Convert an approved estimate to an invoice using service layer
        
        Args:
            estimate_id: Can be a UUID, estimate number (EST-001), or position number (1, 2, 3)
        """
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
            
            # Smart estimate ID resolution
            actual_estimate_id = await self._resolve_estimate_id(estimate_id, business_id, user_id, estimate_service)
            if not actual_estimate_id:
                return self._get_estimate_not_found_message(estimate_id)
            
            # Get the estimate first to check status
            estimate = await estimate_service.get_estimate(
                estimate_id=actual_estimate_id,
                business_id=business_id,
                user_id=user_id
            )
            
            # Check if estimate is approved
            if estimate.status.value != "approved":
                return f"Only approved estimates can be converted to invoices. Current status is {estimate.status_display.lower()}"
            
            # Mark as converted (actual invoice creation would be handled by invoice service)
            result = await estimate_service.change_estimate_status(
                estimate_id=actual_estimate_id,
                new_status="converted",
                business_id=business_id,
                user_id=user_id,
                reason="Converted to invoice via voice agent"
            )
            
            # Clear cache since estimate status changed to converted
            self._clear_estimate_cache()
            
            return f"Estimate '{result.title}' (#{result.estimate_number}) has been marked as converted to invoice. Invoice creation functionality will be implemented in the next phase."
                
        except Exception as e:
            logger.error(f"❌ Error converting estimate to invoice: {e}")
            return f"Error converting estimate to invoice: {str(e)}" 

    @function_tool
    async def get_estimate_details(self, estimate_id: str) -> str:
        """Get detailed information about a specific estimate including current status
        
        Args:
            estimate_id: Can be a UUID, estimate number (EST-001), or position number (1, 2, 3)
        """
        try:
            logger.info(f"📋 Getting details for estimate: {estimate_id}")
            
            # Get business context
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            user_id = self._get_user_id()
            
            # Get estimate service
            estimate_service = self._get_estimate_service()
            if not estimate_service:
                return "Estimate service not available"
            
            # Smart estimate ID resolution
            actual_estimate_id = await self._resolve_estimate_id(estimate_id, business_id, user_id, estimate_service)
            if not actual_estimate_id:
                return self._get_estimate_not_found_message(estimate_id)
            
            # Get estimate details
            estimate = await estimate_service.get_estimate(
                estimate_id=actual_estimate_id,
                business_id=business_id,
                user_id=user_id
            )
            
            # Get available transitions for current status
            available_transitions = estimate_service.get_available_status_transitions(estimate.status)
            available_status_names = [status.value for status in available_transitions]
            
            response_parts = [
                f"Estimate Details:",
                f"• Number: {estimate.estimate_number}",
                f"• Title: {estimate.title}",
                f"• Client: {estimate.client_display_name}",
                f"• Current Status: {estimate.status_display}",
                f"• Total Amount: ${float(estimate.total_amount):,.2f}",
                f"• Created: {estimate.created_date.strftime('%Y-%m-%d')}",
            ]
            
            if available_status_names:
                response_parts.append(f"• Available Status Changes: {', '.join(available_status_names)}")
            else:
                response_parts.append("• Available Status Changes: None (terminal status)")
            
            if hasattr(estimate, 'conversion_date') and estimate.conversion_date:
                response_parts.append(f"• Converted Date: {estimate.conversion_date.strftime('%Y-%m-%d')}")
                
            return " ".join(response_parts)
                
        except Exception as e:
            logger.error(f"❌ Error getting estimate details: {e}")
            return f"Error getting estimate details: {str(e)}" 