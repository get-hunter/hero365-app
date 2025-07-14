"""
Contact Management Agent

Specialized voice agent for contact management and customer relationship operations.
Optimized for OpenAI Realtime API with natural voice interactions.
"""

from typing import Dict, Any, List
from agents import Agent, function_tool
from ..core.base_agent import BaseVoiceAgent
from ..tools.contact_tools import ContactTools


class ContactAgent(BaseVoiceAgent):
    """
    Specialized agent for contact management and customer relationships.
    Optimized for OpenAI Realtime API with natural voice interactions.
    
    Handles:
    - Contact information management
    - Customer relationship tracking
    - Lead qualification and nurturing
    - Contact interaction logging
    - Follow-up scheduling
    - Contact search and organization
    """
    
    def __init__(self, business_context: Dict[str, Any], user_context: Dict[str, Any]):
        """
        Initialize contact agent
        
        Args:
            business_context: Business information and context
            user_context: User information and preferences
        """
        super().__init__(business_context, user_context)
        self.contact_tools = ContactTools(
            business_id=self.get_business_id(),
            user_id=self.get_user_id()
        )
    
    def get_instructions(self) -> str:
        """Get system instructions for the contact agent optimized for voice"""
        
        business_name = self.business_context.get('name', 'Hero365')
        user_name = self.user_context.get('name', 'User')
        is_driving = self.is_driving_mode()
        
        instructions = f"""You are the Hero365 Contact Management Assistant for {business_name}.

IDENTITY & ROLE:
You are a specialized contact management expert focused on customer relationship management, lead tracking, and client communication. Your expertise includes contact organization, relationship building, interaction tracking, and customer lifecycle management.

VOICE INTERACTION EXCELLENCE:
- Speak naturally and conversationally about contacts and relationships
- Use customer-friendly language: "Let me find that contact for you" instead of "Executing search function"
- Ask clarifying questions when contact information is incomplete
- Provide helpful context: "I found John Smith, the one from ABC Company" 
- Always confirm important details before making changes
- Offer related actions: "Would you like me to add their email too?"

CORE CAPABILITIES:
- **Contact Management**: Create, update, and organize customer contacts
- **Relationship Tracking**: Monitor customer relationships and lifecycle stages
- **Lead Qualification**: Assess and qualify potential leads
- **Interaction Logging**: Record all customer interactions and touchpoints
- **Follow-up Management**: Schedule and track customer follow-ups
- **Contact Search**: Find and filter contacts by various criteria
- **Customer Insights**: Provide insights on customer behavior and preferences
- **Communication History**: Track all communication channels and history

BUSINESS CONTEXT:
- Business: {business_name}
- User: {user_name}
- Driving Mode: {'ACTIVE - Keep responses brief and voice-friendly' if is_driving else 'INACTIVE'}

CONTACT EXPERTISE:
You have access to Hero365's comprehensive contact management system that includes:
- Complete contact information management
- Customer relationship lifecycle tracking
- Lead qualification and nurturing processes
- Interaction logging and communication history
- Follow-up scheduling and task management
- Advanced contact search and filtering
- Customer insights and analytics

VOICE COMMUNICATION STYLE:
- Be professional and relationship-focused
- Speak in terms of customer relationships and value
- Provide clear contact information and next steps
- Always confirm important contact details before saving
- Be proactive about follow-up opportunities
- Focus on building and maintaining customer relationships
- Use conversational transitions: "Great! I've added that contact. Now, would you like to..."

SAFETY PROTOCOLS:
{self._get_safety_protocols()}

VOICE RESPONSE GUIDELINES:
- Always prioritize customer relationship quality over quantity
- Suggest appropriate follow-up actions based on customer type
- Provide context about customer history when relevant
- Be proactive about identifying relationship opportunities
- Focus on long-term customer value and relationship building
- When driving mode is active, keep responses under 50 words

Remember: You are the expert in customer relationships and contact management. Your goal is to help build strong, lasting relationships with customers while maintaining organized, actionable contact information through natural voice interaction."""
        
        return instructions
    
    def get_tools(self) -> List[Any]:
        """Return list of contact management tools"""
        return [
            self._create_contact_tool(),
            self._get_contact_info_tool(),
            self._update_contact_tool(),
            self._search_contacts_tool(),
            self._get_recent_contacts_tool(),
            self._add_contact_interaction_tool(),
            self._schedule_follow_up_tool(),
            self._get_contact_interactions_tool()
        ]
    
    def _create_contact_tool(self):
        """Create contact tool wrapper"""
        @function_tool
        async def create_contact(first_name: str = None, 
                               last_name: str = None,
                               company_name: str = None,
                               email: str = None,
                               phone: str = None,
                               contact_type: str = "customer",
                               notes: str = None) -> str:
            """Create a new contact in the system.
            
            Args:
                first_name: Contact's first name
                last_name: Contact's last name
                company_name: Company name (if business contact)
                email: Email address
                phone: Phone number
                contact_type: Type of contact (customer, lead, prospect, vendor)
                notes: Additional notes about the contact
            
            Returns:
                Success message with contact details
            """
            result = await self.contact_tools.create_contact(
                first_name=first_name,
                last_name=last_name,
                company_name=company_name,
                email=email,
                phone=phone,
                contact_type=contact_type,
                notes=notes
            )
            
            if result["success"]:
                contact = result['contact']
                name = contact.get('name', 'New contact')
                company = contact.get('company', '')
                response = f"Perfect! I've added {name} to your contacts"
                if company:
                    response += f" from {company}"
                response += f" as a {contact.get('type', 'customer')}."
                
                # Suggest follow-up actions
                if not contact.get('email') and not contact.get('phone'):
                    response += " Would you like to add their email or phone number?"
                elif contact.get('type') == 'lead':
                    response += " Should I schedule a follow-up reminder for this lead?"
                
                return response
            else:
                return f"I had trouble creating that contact. {result['message']} Could you try again with the contact information?"
        
        return create_contact
    
    def _get_contact_info_tool(self):
        """Get contact info tool wrapper"""
        @function_tool
        async def get_contact_info(contact_id: str) -> str:
            """Get detailed information about a specific contact.
            
            Args:
                contact_id: Unique identifier for the contact
            
            Returns:
                Detailed contact information
            """
            result = await self.contact_tools.get_contact_info(contact_id)
            
            if result["success"]:
                contact = result["contact"]
                name = contact.get('name', 'Unknown contact')
                response = f"Here's the information for {name}:"
                
                # Add contact details conversationally
                if contact.get('company'):
                    response += f" They work at {contact['company']}."
                
                if contact.get('email'):
                    response += f" Their email is {contact['email']}."
                
                if contact.get('phone'):
                    response += f" Their phone number is {contact['phone']}."
                
                if contact.get('relationship_status'):
                    response += f" They're currently a {contact['relationship_status']}."
                
                response += " Would you like me to look up their interaction history or schedule a follow-up?"
                
                return response
            else:
                return f"I couldn't find that contact. {result['message']} Could you try searching by name or company instead?"
        
        return get_contact_info
    
    def _update_contact_tool(self):
        """Update contact tool wrapper"""
        @function_tool
        async def update_contact(contact_id: str,
                               first_name: str = None,
                               last_name: str = None,
                               company_name: str = None,
                               email: str = None,
                               phone: str = None,
                               notes: str = None) -> str:
            """Update an existing contact's information.
            
            Args:
                contact_id: Unique identifier for the contact
                first_name: Updated first name
                last_name: Updated last name
                company_name: Updated company name
                email: Updated email address
                phone: Updated phone number
                notes: Updated notes
            
            Returns:
                Success message with updated details
            """
            result = await self.contact_tools.update_contact(
                contact_id=contact_id,
                first_name=first_name,
                last_name=last_name,
                company_name=company_name,
                email=email,
                phone=phone,
                notes=notes
            )
            
            if result["success"]:
                contact = result['contact']
                name = contact.get('name', 'Contact')
                
                # Build update confirmation
                updates = []
                if first_name or last_name:
                    updates.append("name")
                if company_name:
                    updates.append("company")
                if email:
                    updates.append("email")
                if phone:
                    updates.append("phone")
                if notes:
                    updates.append("notes")
                
                if updates:
                    update_text = ", ".join(updates)
                    response = f"Great! I've updated {name}'s {update_text}."
                else:
                    response = f"I've updated {name}'s information."
                
                response += " Is there anything else you'd like to update for this contact?"
                
                return response
            else:
                return f"I couldn't update that contact. {result['message']} Would you like to try again?"
        
        return update_contact
    
    def _search_contacts_tool(self):
        """Search contacts tool wrapper"""
        @function_tool
        async def search_contacts(query: str,
                                contact_type: str = None,
                                relationship_status: str = None,
                                limit: int = 10) -> str:
            """Search for contacts based on various criteria.
            
            Args:
                query: Search query (name, email, phone, company)
                contact_type: Filter by contact type (customer, lead, prospect, vendor)
                relationship_status: Filter by relationship status
                limit: Maximum number of results to return
            
            Returns:
                List of matching contacts
            """
            try:
                result = await self.contact_tools.search_contacts(
                    query=query,
                    contact_type=contact_type,
                    relationship_status=relationship_status,
                    limit=limit
                )
                
                if result["success"]:
                    contacts = result["contacts"]
                    if not contacts:
                        return f"I didn't find any contacts matching '{query}'. Would you like me to search for something else or help you add a new contact?"
                    
                    # Format results for voice
                    if len(contacts) == 1:
                        contact = contacts[0]
                        name = contact.get('name', 'Unknown')
                        company = contact.get('company', '')
                        response = f"I found {name}"
                        if company:
                            response += f" from {company}"
                        response += f". They're a {contact.get('type', 'contact')}."
                        response += " Would you like to see their details or interaction history?"
                    else:
                        response = f"I found {len(contacts)} contacts matching '{query}': "
                        contact_names = []
                        for contact in contacts[:5]:  # Limit to 5 for voice
                            name = contact.get('name', 'Unknown')
                            company = contact.get('company', '')
                            if company:
                                contact_names.append(f"{name} from {company}")
                            else:
                                contact_names.append(name)
                        
                        response += ", ".join(contact_names)
                        
                        if len(contacts) > 5:
                            response += f" and {len(contacts) - 5} more"
                        
                        response += ". Which one would you like to know more about?"
                    
                    return response
                else:
                    return f"I had trouble searching for contacts. {result['message']} Could you try a different search term?"
            except Exception as e:
                return f"I encountered an error searching for contacts. Let me try a different approach - what specific contact are you looking for?"
        
        return search_contacts
    
    def _get_recent_contacts_tool(self):
        """Get recent contacts tool wrapper"""
        @function_tool
        async def get_recent_contacts(limit: int = 10) -> str:
            """Get the most recently created or updated contacts.
            
            Args:
                limit: Maximum number of contacts to return
            
            Returns:
                List of recent contacts
            """
            try:
                result = await self.contact_tools.get_recent_contacts(limit=limit)
                
                if result["success"]:
                    contacts = result["contacts"]
                    if not contacts:
                        return "You don't have any recent contacts yet. Would you like me to help you add some contacts?"
                    
                    # Format for voice response
                    if len(contacts) == 1:
                        contact = contacts[0]
                        name = contact.get('name', 'Unknown')
                        company = contact.get('company', '')
                        response = f"Your most recent contact is {name}"
                        if company:
                            response += f" from {company}"
                        response += f", added as a {contact.get('type', 'contact')}."
                    else:
                        response = f"Here are your {len(contacts)} most recent contacts: "
                        contact_names = []
                        for contact in contacts:
                            name = contact.get('name', 'Unknown')
                            company = contact.get('company', '')
                            if company:
                                contact_names.append(f"{name} from {company}")
                            else:
                                contact_names.append(name)
                        
                        response += ", ".join(contact_names)
                    
                    response += ". Would you like more details about any of them?"
                    return response
                else:
                    return f"I had trouble getting your recent contacts. {result['message']}"
            except Exception as e:
                return f"I encountered an error getting your recent contacts. Let me try to help you in another way."
        
        return get_recent_contacts
    
    def _add_contact_interaction_tool(self):
        """Add contact interaction tool wrapper"""
        @function_tool
        async def add_contact_interaction(contact_id: str,
                                        interaction_type: str,
                                        notes: str,
                                        outcome: str = None) -> str:
            """Log an interaction with a contact.
            
            Args:
                contact_id: Unique identifier for the contact
                interaction_type: Type of interaction (call, email, meeting, etc.)
                notes: Detailed notes about the interaction
                outcome: Outcome of the interaction
            
            Returns:
                Confirmation message
            """
            result = await self.contact_tools.add_contact_interaction(
                contact_id=contact_id,
                interaction_type=interaction_type,
                notes=notes,
                outcome=outcome
            )
            
            if result["success"]:
                contact_name = result.get('contact_name', 'contact')
                response = f"Perfect! I've logged that {interaction_type} with {contact_name}."
                
                if outcome:
                    response += f" The outcome was: {outcome}."
                
                # Suggest follow-up actions
                if outcome and any(word in outcome.lower() for word in ['follow', 'call back', 'reschedule']):
                    response += " Should I schedule a follow-up reminder for this?"
                elif interaction_type.lower() == 'meeting':
                    response += " Would you like me to schedule a follow-up meeting?"
                
                return response
            else:
                return f"I couldn't log that interaction. {result['message']} Could you try again?"
        
        return add_contact_interaction
    
    def _schedule_follow_up_tool(self):
        """Schedule follow-up tool wrapper"""
        @function_tool
        async def schedule_follow_up(contact_id: str,
                                   follow_up_date: str,
                                   notes: str,
                                   priority: str = "medium") -> str:
            """Schedule a follow-up task for a contact.
            
            Args:
                contact_id: Unique identifier for the contact
                follow_up_date: Date for the follow-up (YYYY-MM-DD format)
                notes: Notes about what to follow up on
                priority: Priority level (low, medium, high)
            
            Returns:
                Confirmation message
            """
            result = await self.contact_tools.schedule_follow_up(
                contact_id=contact_id,
                follow_up_date=follow_up_date,
                notes=notes,
                priority=priority
            )
            
            if result["success"]:
                contact_name = result.get('contact_name', 'contact')
                response = f"Great! I've scheduled a follow-up with {contact_name} for {follow_up_date}."
                
                if priority == "high":
                    response += " I've marked this as high priority."
                
                response += f" The reminder is set for: {notes}."
                
                # Suggest additional actions
                response += " Would you like me to set up any other reminders or add this to your calendar?"
                
                return response
            else:
                return f"I couldn't schedule that follow-up. {result['message']} Could you try again with a different date?"
        
        return schedule_follow_up
    
    def _get_contact_interactions_tool(self):
        """Get contact interactions tool wrapper"""
        @function_tool
        async def get_contact_interactions(contact_id: str, limit: int = 10) -> str:
            """Get interaction history for a contact.
            
            Args:
                contact_id: Unique identifier for the contact
                limit: Maximum number of interactions to return
            
            Returns:
                List of contact interactions
            """
            result = await self.contact_tools.get_contact_interactions(
                contact_id=contact_id,
                limit=limit
            )
            
            if result["success"]:
                interactions = result["interactions"]
                contact_name = result.get('contact_name', 'contact')
                
                if not interactions:
                    return f"I don't have any recorded interactions with {contact_name} yet. Would you like to log a recent interaction?"
                
                # Format for voice
                if len(interactions) == 1:
                    interaction = interactions[0]
                    response = f"The most recent interaction with {contact_name} was a {interaction.get('type', 'interaction')}: {interaction.get('notes', 'No details recorded')[:50]}..."
                else:
                    response = f"Here are the recent interactions with {contact_name}: "
                    interaction_list = []
                    for interaction in interactions[:5]:  # Limit for voice
                        interaction_type = interaction.get('type', 'interaction')
                        interaction_list.append(f"a {interaction_type}")
                    
                    response += ", ".join(interaction_list)
                    
                    if len(interactions) > 5:
                        response += f" and {len(interactions) - 5} more"
                
                response += ". Would you like details about any specific interaction?"
                
                return response
            else:
                return f"I couldn't retrieve the interaction history. {result['message']}"
        
        return get_contact_interactions
    
    def _get_safety_protocols(self) -> str:
        """Get safety protocols based on user context"""
        if self.is_driving_mode():
            return """
DRIVING MODE SAFETY:
- Keep all responses under 50 words
- Avoid complex multi-step processes
- Prioritize hands-free, voice-only interactions
- Limit data entry to essential information only
- Focus on essential contact information only
- Use simple confirmation patterns
"""
        else:
            return """
STANDARD SAFETY:
- Always confirm important contact details before saving
- Protect customer privacy and data confidentiality
- Follow proper data handling procedures
- Maintain professional communication standards
- Verify contact information accuracy
"""
    
    def get_handoffs(self) -> List[Agent]:
        """Get agents this agent can hand off to"""
        # Contact agent can hand off to related agents
        return []
    
    def get_agent_name(self) -> str:
        """Get agent name for identification"""
        business_name = self.business_context.get('name', 'Hero365')
        return f"{business_name} Contact Management Assistant"
    
    def get_personalized_greeting(self) -> str:
        """Generate personalized greeting based on context"""
        user_name = self.user_context.get('name', 'there')
        business_name = self.business_context.get('name', 'Hero365')
        
        if self.is_driving_mode():
            return f"Hi {user_name}! I'm your {business_name} contact assistant. I'll keep responses brief since you're driving. How can I help with your contacts?"
        else:
            return f"Hi {user_name}! I'm your {business_name} contact management assistant. I can help you manage customer relationships, track leads, log interactions, and more. What would you like to do with your contacts?"
    
    def get_contact_capabilities(self) -> Dict[str, List[str]]:
        """Get summary of contact management capabilities"""
        return {
            "contact_management": [
                "Add new contacts",
                "Update contact information",
                "Search and filter contacts",
                "Organize contact records"
            ],
            "relationship_tracking": [
                "Track relationship status",
                "Monitor customer lifecycle",
                "Qualify leads",
                "Segment customers"
            ],
            "interaction_management": [
                "Log customer interactions",
                "Track communication history",
                "Record meeting notes",
                "Monitor touchpoints"
            ],
            "follow_up_management": [
                "Schedule follow-ups",
                "Set reminders",
                "Track pending actions",
                "Manage customer outreach"
            ]
        }
    
    def get_safety_mode_instructions(self) -> str:
        """Get safety mode instructions for driving"""
        if self.is_driving_mode():
            return """
DRIVING MODE ACTIVE:
- Keep responses brief and clear
- Provide essential contact information only
- Avoid complex contact operations
- Focus on simple queries like "Who called today?"
- Offer to handle complex contact management when user is not driving
"""
        return ""
    
    def can_handle_request(self, request: str) -> bool:
        """Check if this agent can handle the request"""
        contact_keywords = [
            "contact", "customer", "client", "lead", "prospect", "call", "email",
            "phone", "address", "follow", "interaction", "relationship", "CRM",
            "customer management", "client management", "contact management",
            "add contact", "find contact", "search contact", "update contact"
        ]
        
        request_lower = request.lower()
        return any(keyword in request_lower for keyword in contact_keywords)
    
    def get_quick_actions(self) -> List[Dict[str, str]]:
        """Get quick contact management actions"""
        return [
            {
                "action": "search_contacts",
                "description": "Search contacts",
                "command": "Find contacts matching..."
            },
            {
                "action": "recent_interactions",
                "description": "Recent interactions",
                "command": "Show recent customer interactions"
            },
            {
                "action": "add_contact",
                "description": "Add new contact",
                "command": "Add a new customer contact"
            },
            {
                "action": "pending_followups",
                "description": "Pending follow-ups",
                "command": "Show pending follow-ups"
            }
        ]
    
    def get_voice_pipeline(self):
        """Get voice pipeline for realtime audio processing"""
        return self.create_voice_pipeline() 