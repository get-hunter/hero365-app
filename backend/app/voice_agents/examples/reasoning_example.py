"""
Example demonstrating the Hero365 Reasoning Voice Agent capabilities.

This example shows how the reasoning agent can handle complex multi-step
business management tasks through the Plan-Act-Verify loop.
"""

import asyncio
import logging
from typing import Dict, Any

from app.voice_agents.personal.reasoning_personal_agent import ReasoningPersonalVoiceAgent
from app.voice_agents.personal.personal_agent import PersonalVoiceAgent
from app.voice_agents.core.voice_config import DEFAULT_PERSONAL_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReasoningAgentDemo:
    """Demo class for showing reasoning agent capabilities"""
    
    def __init__(self):
        # Mock business and user contexts
        self.business_context = {
            "id": "demo_business",
            "name": "Smith's Home Services",
            "type": "Home services contractor",
            "services": ["plumbing", "electrical", "HVAC", "handyman"],
            "capabilities": ["project management", "invoicing", "scheduling", "inventory"]
        }
        
        self.user_context = {
            "id": "demo_user",
            "name": "John Smith",
            "role": "business_owner",
            "preferences": {
                "voice_speed": "normal",
                "safety_mode": True,
                "notification_preferences": ["sms", "email"]
            }
        }
    
    def create_standard_agent(self) -> PersonalVoiceAgent:
        """Create a standard (non-reasoning) agent"""
        return PersonalVoiceAgent(
            business_context=self.business_context,
            user_context=self.user_context,
            config=DEFAULT_PERSONAL_CONFIG
        )
    
    def create_reasoning_agent(self) -> ReasoningPersonalVoiceAgent:
        """Create a reasoning-enabled agent"""
        return ReasoningPersonalVoiceAgent(
            business_context=self.business_context,
            user_context=self.user_context,
            config=DEFAULT_PERSONAL_CONFIG,
            max_reasoning_iterations=3
        )
    
    async def demo_simple_request(self):
        """Demo a simple request that both agents can handle"""
        print("\n" + "="*60)
        print("DEMO 1: Simple Request - 'Get my upcoming jobs'")
        print("="*60)
        
        # Standard agent
        standard_agent = self.create_standard_agent()
        print("\n🤖 Standard Agent Response:")
        print("I'll check your upcoming jobs right away...")
        # Standard agent would call get_upcoming_jobs() directly
        
        # Reasoning agent
        reasoning_agent = self.create_reasoning_agent()
        print("\n🧠 Reasoning Agent Response:")
        print("I'll check your upcoming jobs right away...")
        # Reasoning agent would also handle this directly (no complex reasoning needed)
        
        print("\n💡 For simple requests, both agents perform similarly.")
    
    async def demo_complex_project_creation(self):
        """Demo a complex project creation request"""
        print("\n" + "="*60)
        print("DEMO 2: Complex Request - Multi-step Project Creation")
        print("="*60)
        
        complex_request = """
        Create a new project for the Johnson kitchen renovation. 
        I need to add electrical work for new outlets and lighting, 
        plumbing for the new sink and dishwasher, and then send 
        detailed estimates to the client.
        """
        
        print(f"\n👤 User Request: {complex_request.strip()}")
        
        # Standard agent approach
        print("\n🤖 Standard Agent Approach:")
        print("Standard agent would handle this as separate requests:")
        print("1. User: 'Create a project for Johnson kitchen renovation'")
        print("2. User: 'Add electrical work to the project'")
        print("3. User: 'Add plumbing work to the project'")
        print("4. User: 'Create estimates for the project'")
        print("5. User: 'Send estimates to client'")
        
        # Reasoning agent approach
        print("\n🧠 Reasoning Agent Approach:")
        reasoning_agent = self.create_reasoning_agent()
        
        print("\n🔍 PLANNING PHASE:")
        print("Goal: Create a comprehensive project with jobs and estimates")
        print("Action Type: MULTI_TOOL_SEQUENCE")
        print("Reasoning: This requires creating a project first, then adding jobs, and finally creating estimates")
        
        print("\n📋 Execution Plan:")
        print("1. create_project(name='Johnson Kitchen Renovation', description='Complete kitchen renovation')")
        print("   └── Expected: Project created successfully")
        print("2. create_job(title='Electrical work - outlets and lighting', project_id=<from_step_1>)")
        print("   └── Expected: Job created and linked to project")
        print("3. create_job(title='Plumbing - sink and dishwasher', project_id=<from_step_1>)")
        print("   └── Expected: Job created and linked to project")
        print("4. create_estimate(project_id=<from_step_1>, include_jobs=True)")
        print("   └── Expected: Estimate created for project")
        
        print("\n⚡ ACTING PHASE:")
        print("Executing tools in sequence...")
        print("✅ Project created: Johnson Kitchen Renovation (ID: proj_123)")
        print("✅ Electrical job created and linked to project")
        print("✅ Plumbing job created and linked to project")
        print("✅ Estimate created and ready to send")
        
        print("\n✅ VERIFICATION PHASE:")
        print("Goal achieved: ✅ Yes")
        print("Confidence: 95%")
        print("All success criteria met:")
        print("  ✅ Project created successfully")
        print("  ✅ All jobs added to project")
        print("  ✅ Estimates generated and ready to send")
        
        print("\n💬 Final Response:")
        print("I've successfully created the Johnson Kitchen Renovation project with both")
        print("electrical and plumbing jobs. The detailed estimates are ready to send to the client.")
    
    async def demo_overdue_invoices_workflow(self):
        """Demo handling overdue invoices with follow-up"""
        print("\n" + "="*60)
        print("DEMO 3: Complex Workflow - Overdue Invoice Management")
        print("="*60)
        
        request = "Find all my overdue invoices and create follow-up tasks for each client"
        
        print(f"\n👤 User Request: {request}")
        
        print("\n🧠 Reasoning Agent Approach:")
        
        print("\n🔍 PLANNING PHASE:")
        print("Goal: Manage overdue invoices and follow up with clients")
        print("Action Type: MULTI_TOOL_SEQUENCE")
        print("Reasoning: Need to find overdue invoices, get client details, and create follow-up tasks")
        
        print("\n📋 Execution Plan:")
        print("1. get_overdue_invoices()")
        print("   └── Expected: List of overdue invoices retrieved")
        print("2. get_contact_details(contact_id=<from_invoice_data>)")
        print("   └── Expected: Client contact information retrieved")
        print("3. add_contact_interaction(contact_id=<from_previous>, interaction_type='follow_up')")
        print("   └── Expected: Follow-up interaction recorded")
        
        print("\n⚡ ACTING PHASE:")
        print("Executing tools in sequence...")
        print("✅ Found 3 overdue invoices:")
        print("   - Invoice #1234: $2,500 (Johnson Kitchen, 15 days overdue)")
        print("   - Invoice #1235: $1,200 (Brown Plumbing, 8 days overdue)")
        print("   - Invoice #1236: $800 (Davis Electrical, 22 days overdue)")
        print("✅ Retrieved client contact information for all")
        print("✅ Created follow-up tasks for each client")
        
        print("\n✅ VERIFICATION PHASE:")
        print("Goal achieved: ✅ Yes")
        print("Confidence: 90%")
        print("All success criteria met:")
        print("  ✅ Overdue invoices identified")
        print("  ✅ Client contact information retrieved")
        print("  ✅ Follow-up tasks created")
        
        print("\n💬 Final Response:")
        print("I found 3 overdue invoices totaling $4,500. I've created follow-up tasks")
        print("for each client with their contact information. The longest overdue is")
        print("Davis Electrical at 22 days ($800).")
    
    async def demo_inventory_management(self):
        """Demo inventory management with reordering"""
        print("\n" + "="*60)
        print("DEMO 4: Inventory Management with Automatic Reordering")
        print("="*60)
        
        request = "Check my inventory levels and handle any low stock items"
        
        print(f"\n👤 User Request: {request}")
        
        print("\n🧠 Reasoning Agent Approach:")
        
        print("\n🔍 PLANNING PHASE:")
        print("Goal: Check inventory levels and handle reordering")
        print("Action Type: MULTI_TOOL_SEQUENCE")
        print("Reasoning: Need to check stock levels, get reorder suggestions, and process orders")
        
        print("\n📋 Execution Plan:")
        print("1. check_stock_levels()")
        print("   └── Expected: Current stock levels retrieved")
        print("2. get_reorder_suggestions()")
        print("   └── Expected: Reorder suggestions generated")
        print("3. create_purchase_order(items=<from_suggestions>)")
        print("   └── Expected: Purchase orders created")
        
        print("\n⚡ ACTING PHASE:")
        print("Executing tools in sequence...")
        print("✅ Checked stock levels for all products")
        print("✅ Found 5 items below reorder threshold:")
        print("   - PVC Pipe 1/2\": 12 units (threshold: 25)")
        print("   - Wire Nuts: 45 units (threshold: 100)")
        print("   - Electrical Outlets: 8 units (threshold: 20)")
        print("   - Pipe Fittings: 15 units (threshold: 30)")
        print("   - LED Bulbs: 6 units (threshold: 25)")
        print("✅ Generated reorder suggestions with preferred suppliers")
        
        print("\n✅ VERIFICATION PHASE:")
        print("Goal achieved: ✅ Yes")
        print("Confidence: 85%")
        print("All success criteria met:")
        print("  ✅ Stock levels checked")
        print("  ✅ Reorder suggestions provided")
        print("  ✅ Ready to create purchase orders")
        
        print("\n💬 Final Response:")
        print("I've checked your inventory and found 5 items that need reordering.")
        print("I can create purchase orders with your preferred suppliers, or you can")
        print("review the suggestions first. Would you like me to proceed with the orders?")
    
    async def demo_reasoning_transparency(self):
        """Demo the reasoning transparency features"""
        print("\n" + "="*60)
        print("DEMO 5: Reasoning Transparency & Explanation")
        print("="*60)
        
        print("\n👤 User: 'Explain your reasoning for the last task'")
        
        print("\n🧠 Reasoning Agent Response:")
        print("Here's my reasoning process for the inventory management task:")
        print("")
        print("Goal: Check inventory levels and handle reordering")
        print("Approach: multi_tool_sequence")
        print("Reasoning: Need to check stock levels, get reorder suggestions, and process orders")
        print("")
        print("Tools I planned to use:")
        print("- check_stock_levels: Current stock levels retrieved")
        print("- get_reorder_suggestions: Reorder suggestions generated")
        print("- create_purchase_order: Purchase orders created")
        print("")
        print("Success criteria:")
        print("- Stock levels checked")
        print("- Reorder suggestions provided")
        print("- Purchase orders created if needed")
        print("")
        print("Current status: completed")
        print("Iteration: 1/3")
        print("")
        print("I chose a sequential approach because checking stock levels must happen")
        print("before generating reorder suggestions, which must happen before creating")
        print("purchase orders. This ensures data consistency and proper workflow.")
    
    async def demo_plan_revision(self):
        """Demo plan revision capabilities"""
        print("\n" + "="*60)
        print("DEMO 6: Plan Revision & Adaptation")
        print("="*60)
        
        print("\n👤 User: 'Actually, don't create the purchase orders yet. Just show me the suggestions.'")
        
        print("\n🧠 Reasoning Agent - Plan Revision:")
        print("I understand. Let me revise my plan to exclude the purchase order creation.")
        print("")
        print("🔄 REVISED PLAN:")
        print("Goal: Check inventory levels and provide reorder suggestions only")
        print("Action Type: MULTI_TOOL_SEQUENCE")
        print("Reasoning: User wants to review suggestions before committing to orders")
        print("")
        print("Updated execution plan:")
        print("1. check_stock_levels() ✅ (already completed)")
        print("2. get_reorder_suggestions() ✅ (already completed)")
        print("3. create_purchase_order() ❌ (removed per user request)")
        print("")
        print("✅ Plan revised based on: Don't create purchase orders, just show suggestions")
        print("")
        print("Here are the reorder suggestions for your review:")
        print("- PVC Pipe 1/2\": Order 50 units from PlumbingSupply Co. ($45)")
        print("- Wire Nuts: Order 200 units from ElectricParts Inc. ($32)")
        print("- Electrical Outlets: Order 25 units from ElectricParts Inc. ($78)")
        print("- Pipe Fittings: Order 40 units from PlumbingSupply Co. ($95)")
        print("- LED Bulbs: Order 50 units from LightingWorld ($125)")
        print("")
        print("Would you like me to proceed with any of these orders?")
    
    async def run_all_demos(self):
        """Run all demonstration scenarios"""
        print("🚀 Hero365 Reasoning Agent Demonstration")
        print("========================================")
        
        await self.demo_simple_request()
        await self.demo_complex_project_creation()
        await self.demo_overdue_invoices_workflow()
        await self.demo_inventory_management()
        await self.demo_reasoning_transparency()
        await self.demo_plan_revision()
        
        print("\n" + "="*60)
        print("🎉 DEMONSTRATION COMPLETE")
        print("="*60)
        
        print("\n✨ Key Benefits of Reasoning Agent:")
        print("• Handles complex multi-step requests in a single interaction")
        print("• Plans execution sequences with proper dependencies")
        print("• Verifies results and can revise plans if needed")
        print("• Provides transparency into reasoning process")
        print("• Adapts to user feedback and changing requirements")
        print("• Maintains context across multiple tool calls")
        print("• Reduces back-and-forth for complex business workflows")
        
        print("\n🔧 Integration with LiveKit:")
        print("• Set ENABLE_REASONING=true in environment variables")
        print("• Configure MAX_REASONING_ITERATIONS (default: 3)")
        print("• All existing tools work seamlessly with reasoning")
        print("• Voice interactions remain natural and conversational")
        print("• Can explain reasoning process via voice commands")
        
        print("\n🎯 Use Cases:")
        print("• Complex project setup with multiple jobs and estimates")
        print("• Customer relationship management workflows")
        print("• Inventory management and procurement processes")
        print("• Financial reporting and invoice management")
        print("• Scheduling and resource allocation")
        print("• Multi-step business process automation")


async def main():
    """Main function to run the demonstration"""
    demo = ReasoningAgentDemo()
    await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main()) 