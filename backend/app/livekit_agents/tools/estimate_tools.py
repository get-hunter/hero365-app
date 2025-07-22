"""
Estimate Management Tools for Hero365 LiveKit Agents
"""

import logging
import uuid
from typing import Dict, Any, Optional
from livekit.agents import function_tool

logger = logging.getLogger(__name__)


class EstimateTools:
    """Estimate management tools for the Hero365 agent"""
    
    def __init__(self, business_context: Dict[str, Any], business_context_manager: Optional[Any] = None):
        self.business_context = business_context
        self.business_context_manager = business_context_manager
        self._container = None
        self._estimate_repo = None
        self._contact_repo = None
        
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
    
    def _get_estimate_repository(self):
        """Get estimate repository with caching"""
        if not self._estimate_repo:
            container = self._get_container()
            if container:
                try:
                    self._estimate_repo = container.get_estimate_repository()
                    logger.info("✅ Estimate repository retrieved successfully")
                except Exception as e:
                    logger.error(f"❌ Error getting estimate repository: {e}")
                    return None
        return self._estimate_repo
    
    def _get_contact_repository(self):
        """Get contact repository with caching"""
        if not self._contact_repo:
            container = self._get_container()
            if container:
                try:
                    self._contact_repo = container.get_contact_repository()
                    logger.info("✅ Contact repository retrieved successfully")
                except Exception as e:
                    logger.error(f"❌ Error getting contact repository: {e}")
                    return None
        return self._contact_repo
    
    def _get_business_id(self) -> Optional[uuid.UUID]:
        """Get business ID from context"""
        business_id = self.business_context.get('business_id')
        if business_id:
            if isinstance(business_id, str):
                return uuid.UUID(business_id)
            return business_id
        return None
    
    @function_tool
    async def create_estimate(
        self,
        title: str,
        description: str,
        contact_id: Optional[str] = None,
        total_amount: Optional[float] = None,
        valid_until: Optional[str] = None
    ) -> str:
        """Create a new estimate with context-aware assistance.
        
        Args:
            title: Estimate title/summary
            description: Detailed estimate description
            contact_id: ID of the contact for this estimate
            total_amount: Total estimated amount
            valid_until: Estimate validity date (YYYY-MM-DD format)
        """
        try:
            logger.info(f"📊 Creating estimate: {title}")
            
            # Get business ID
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            # Get repositories
            estimate_repo = self._get_estimate_repository()
            if not estimate_repo:
                return "Estimate repository not available"
            
            # If no contact_id provided, try to find a recent contact
            if not contact_id:
                contact_repo = self._get_contact_repository()
                if contact_repo:
                    recent_contacts = await contact_repo.get_recent_by_business(business_id, limit=5)
                    if recent_contacts:
                        # Use the most recent contact
                        contact_id = str(recent_contacts[0].id)
                        logger.info(f"🎯 Using recent contact: {recent_contacts[0].get_display_name()}")
            
            # Import estimate entity
            from app.domain.entities.estimate import Estimate
            from datetime import datetime, timedelta
            
            # Parse valid_until date
            valid_until_date = None
            if valid_until:
                try:
                    valid_until_date = datetime.strptime(valid_until, "%Y-%m-%d")
                except ValueError:
                    logger.warning(f"⚠️ Invalid date format for valid_until: {valid_until}")
            
            # Default validity period: 30 days
            if not valid_until_date:
                valid_until_date = datetime.now() + timedelta(days=30)
            
            # Generate next estimate number
            estimate_number = await estimate_repo.get_next_estimate_number(business_id)
            
            # Create new estimate
            new_estimate = Estimate(
                business_id=business_id,
                contact_id=uuid.UUID(contact_id) if contact_id else None,
                title=title,
                description=description,
                estimate_number=estimate_number,
                total_amount=total_amount or 0.0,
                valid_until_date=valid_until_date,
                notes=f"Created via voice agent"
            )
            
            # Save to repository
            created_estimate = await estimate_repo.create(new_estimate)
            
            response = f"Successfully created estimate '{title}' with number {estimate_number}"
            if total_amount:
                response += f" for ${total_amount:,.2f}"
            if valid_until_date:
                response += f", valid until {valid_until_date.strftime('%B %d, %Y')}"
            
            return response
                
        except Exception as e:
            logger.error(f"❌ Error creating estimate: {e}")
            return f"Error creating estimate: {str(e)}"

    @function_tool
    async def get_recent_estimates(self, limit: int = 10, days: int = 30) -> str:
        """Get recent estimates with direct repository access.
        
        Args:
            limit: Maximum number of estimates to return
            days: Number of days to look back (default 30, use 365 for all estimates)
        """
        try:
            logger.info(f"📋 Getting recent estimates (limit: {limit}, days: {days})")
            
            # Debug: Log business context
            logger.info(f"🔍 Debug - Business context keys: {list(self.business_context.keys())}")
            logger.info(f"🔍 Debug - Business context: {self.business_context}")
            
            # Get business ID
            business_id = self._get_business_id()
            logger.info(f"🔍 Debug - Business ID: {business_id} (type: {type(business_id)})")
            
            if not business_id:
                logger.error("❌ No business_id found in context")
                return "Business context not available - no business ID found"
            
            # Get estimate repository
            estimate_repo = self._get_estimate_repository()
            if not estimate_repo:
                logger.error("❌ Estimate repository not available")
                return "Estimate repository not available"
            
            logger.info(f"🔍 Debug - Calling estimate_repo.get_recent_by_business with business_id={business_id}, limit={limit}, days={days}")
            
            # Get recent estimates from repository
            if days >= 365:
                # Get all estimates regardless of age
                recent_estimates = await estimate_repo.get_by_business_id(business_id, limit=limit)
                logger.info(f"🔍 Debug - Using get_by_business_id (all estimates)")
            else:
                # Get estimates from specific time period
                recent_estimates = await estimate_repo.get_recent_by_business(business_id, days=days, limit=limit)
                logger.info(f"🔍 Debug - Using get_recent_by_business (last {days} days)")
            
            logger.info(f"🔍 Debug - Repository returned {len(recent_estimates) if recent_estimates else 0} estimates")
            
            if recent_estimates:
                logger.info(f"✅ Found {len(recent_estimates)} estimates")
                for i, est in enumerate(recent_estimates):
                    logger.info(f"  Estimate {i+1}: {est.title} - Status: {est.status.value if hasattr(est, 'status') else 'No status'}")
                
                response = f"Here are your {len(recent_estimates)} most recent estimates"
                if days < 365:
                    response += f" from the last {days} days"
                response += ": "
                
                estimate_list = []
                for i, estimate in enumerate(recent_estimates, 1):
                    # Get contact name
                    contact_name = "Unknown Contact"
                    if estimate.contact_id:
                        contact_repo = self._get_contact_repository()
                        if contact_repo:
                            try:
                                contact = await contact_repo.get_by_id(estimate.contact_id)
                                if contact:
                                    contact_name = contact.get_display_name()
                            except Exception as e:
                                logger.warning(f"⚠️ Could not get contact name: {e}")
                    
                    estimate_info = f"{i}. {estimate.title}, status {estimate.status.value}"
                    if hasattr(estimate, 'get_total_amount'):
                        total = estimate.get_total_amount()
                        if total and total > 0:
                            estimate_info += f" for ${float(total):,.2f}"
                    estimate_info += f", for {contact_name}"
                    estimate_list.append(estimate_info)
                
                response += ". ".join(estimate_list)
                return response
            else:
                logger.warning(f"⚠️ No estimates found in repository (last {days} days)")
                
                if days == 30:
                    # If no estimates in last 30 days, check if there are any older ones
                    try:
                        logger.info("🔍 Debug - Checking for older estimates...")
                        all_estimates = await estimate_repo.get_by_business_id(business_id, limit=5)
                        logger.info(f"🔍 Debug - Found {len(all_estimates) if all_estimates else 0} total estimates")
                        
                        if all_estimates:
                            response = f"No estimates found in the last {days} days, but you have {len(all_estimates)} total estimates. Would you like me to show all your estimates?"
                            return response
                    except Exception as debug_e:
                        logger.error(f"🔍 Debug query failed: {debug_e}")
                
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
            
            # Get business ID
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            # Get estimate repository
            estimate_repo = self._get_estimate_repository()
            if not estimate_repo:
                return "Estimate repository not available"
            
            # Get all estimates and filter for pending ones
            all_estimates = await estimate_repo.get_by_business_id(business_id, limit=limit * 2)  # Get extra in case many are not pending
            
            # Filter for pending estimates
            pending_estimates = []
            for estimate in all_estimates:
                if hasattr(estimate, 'status') and estimate.status.value in ['draft', 'pending', 'sent', 'viewed']:
                    pending_estimates.append(estimate)
                    if len(pending_estimates) >= limit:
                        break
            
            logger.info(f"🔍 Found {len(pending_estimates)} pending estimates out of {len(all_estimates)} total")
            
            if pending_estimates:
                response = f"Here are your {len(pending_estimates)} pending estimates: "
                estimate_list = []
                
                for i, estimate in enumerate(pending_estimates, 1):
                    # Get contact name
                    contact_name = "Unknown Contact"
                    if estimate.contact_id:
                        contact_repo = self._get_contact_repository()
                        if contact_repo:
                            try:
                                contact = await contact_repo.get_by_id(estimate.contact_id)
                                if contact:
                                    contact_name = contact.get_display_name()
                            except Exception as e:
                                logger.warning(f"⚠️ Could not get contact name: {e}")
                    
                    estimate_info = f"{i}. {estimate.title}, status {estimate.status.value}"
                    if hasattr(estimate, 'get_total_amount'):
                        total = estimate.get_total_amount()
                        if total and total > 0:
                            estimate_info += f" for ${float(total):,.2f}"
                    estimate_info += f", for {contact_name}"
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
            
            # Get business ID
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            # Get estimate repository
            estimate_repo = self._get_estimate_repository()
            if not estimate_repo:
                return "Estimate repository not available"
            
            # Get draft estimates
            from app.domain.enums import EstimateStatus
            draft_estimates = await estimate_repo.get_by_status(business_id, EstimateStatus.DRAFT, limit=limit)
            
            if draft_estimates:
                response = f"Here are {len(draft_estimates)} draft estimates that need attention: "
                estimate_list = []
                for i, estimate in enumerate(draft_estimates, 1):
                    # Get contact name
                    contact_name = "Unknown Contact"
                    if estimate.contact_id:
                        contact_repo = self._get_contact_repository()
                        if contact_repo:
                            try:
                                contact = await contact_repo.get_by_id(estimate.contact_id)
                                if contact:
                                    contact_name = contact.get_display_name()
                            except Exception as e:
                                logger.warning(f"⚠️ Could not get contact name: {e}")
                    
                    estimate_info = f"{i}. {estimate.title} for {contact_name}"
                    if hasattr(estimate, 'get_total_amount'):
                        total = estimate.get_total_amount()
                        if total and total > 0:
                            estimate_info += f" worth ${float(total):,.2f}"
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
        """Search for estimates with direct repository access.
        
        Args:
            query: Search query (title, description, contact name, etc.)
            limit: Maximum number of results to return
        """
        try:
            logger.info(f"🔍 Searching estimates for: {query}")
            
            # Get business ID
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            # Get repositories
            estimate_repo = self._get_estimate_repository()
            if not estimate_repo:
                return "Estimate repository not available"
            
            # Get all estimates and filter by query (basic implementation)
            all_estimates = await estimate_repo.get_by_business_id(business_id, limit=limit*2)
            
            # Filter estimates that match the query
            matching_estimates = []
            query_lower = query.lower()
            
            for estimate in all_estimates:
                if (query_lower in estimate.title.lower() or 
                    query_lower in (estimate.description or "").lower() or 
                    query_lower in (estimate.estimate_number or "").lower()):
                    matching_estimates.append(estimate)
                    if len(matching_estimates) >= limit:
                        break
            
            if matching_estimates:
                response = f"Found {len(matching_estimates)} estimates matching '{query}': "
                estimate_list = []
                for i, estimate in enumerate(matching_estimates, 1):
                    # Get contact name
                    contact_name = "Unknown Contact"
                    if estimate.contact_id:
                        contact_repo = self._get_contact_repository()
                        if contact_repo:
                            try:
                                contact = await contact_repo.get_by_id(estimate.contact_id)
                                if contact:
                                    contact_name = contact.get_display_name()
                            except Exception as e:
                                logger.warning(f"⚠️ Could not get contact name: {e}")
                    
                    estimate_info = f"{i}. {estimate.title}, status {estimate.status.value}"
                    if hasattr(estimate, 'get_total_amount'):
                        total = estimate.get_total_amount()
                        if total and total > 0:
                            estimate_info += f" for ${float(total):,.2f}"
                    estimate_info += f", for {contact_name}"
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
        """Update the status of a specific estimate"""
        try:
            logger.info(f"📊 Updating estimate {estimate_id} status to {status}")
            
            # Get business ID
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            # Get estimate repository
            estimate_repo = self._get_estimate_repository()
            if not estimate_repo:
                return "Estimate repository not available"
            
            # Get the estimate
            estimate = await estimate_repo.get_by_id(uuid.UUID(estimate_id))
            if not estimate:
                return f"Estimate with ID {estimate_id} not found"
            
            # Verify it belongs to the business
            if estimate.business_id != business_id:
                return "You don't have permission to update this estimate"
            
            # Update status
            from app.domain.enums import EstimateStatus
            try:
                new_status = EstimateStatus(status.lower())
                estimate.status = new_status
                updated_estimate = await estimate_repo.update(estimate)
                
                return f"Successfully updated estimate '{updated_estimate.title}' status to {new_status.value}"
            except ValueError:
                valid_statuses = [status.value for status in EstimateStatus]
                return f"Invalid status '{status}'. Valid options are: {', '.join(valid_statuses)}"
                
        except Exception as e:
            logger.error(f"❌ Error updating estimate status: {e}")
            return f"Error updating estimate status: {str(e)}"

    @function_tool
    async def convert_estimate_to_invoice(self, estimate_id: str) -> str:
        """Convert an approved estimate to an invoice"""
        try:
            logger.info(f"💰 Converting estimate {estimate_id} to invoice")
            
            # Get business ID
            business_id = self._get_business_id()
            if not business_id:
                return "Business context not available"
            
            # Get estimate repository
            estimate_repo = self._get_estimate_repository()
            if not estimate_repo:
                return "Estimate repository not available"
            
            # Get the estimate
            estimate = await estimate_repo.get_by_id(uuid.UUID(estimate_id))
            if not estimate:
                return f"Estimate with ID {estimate_id} not found"
            
            # Verify it belongs to the business
            if estimate.business_id != business_id:
                return "You don't have permission to convert this estimate"
            
            # Check if estimate is approved
            from app.domain.enums import EstimateStatus
            if estimate.status != EstimateStatus.APPROVED:
                return f"Only approved estimates can be converted to invoices. Current status is {estimate.status.value}"
            
            # For now, return a success message - actual invoice creation would need invoice repository
            return f"Estimate '{estimate.title}' is ready for invoice conversion. Invoice creation functionality will be implemented in the next phase."
                
        except Exception as e:
            logger.error(f"❌ Error converting estimate to invoice: {e}")
            return f"Error converting estimate to invoice: {str(e)}" 