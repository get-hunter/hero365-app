#!/usr/bin/env python3
"""
Mobile Website Deployment Test Script

This script simulates a mobile app calling the deployment API to test the entire flow:
1. Submit deployment request
2. Poll deployment status
3. Display progress updates
4. Show final result

Usage:
    python test_mobile_deployment.py
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any

import httpx
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Mock JWT token for testing (you'll need a real one)
TEST_TOKEN = "your-test-jwt-token-here"

# Test business data
TEST_DEPLOYMENT_DATA = {
    "subdomain": f"test-{uuid.uuid4().hex[:8]}",
    "service_areas": [
        {
            "postal_code": "78701",
            "country_code": "US",
            "city": "Austin",
            "region": "TX",
            "emergency_services_available": True,
            "regular_services_available": True
        },
        {
            "postal_code": "78702",
            "country_code": "US",
            "city": "Austin",
            "region": "TX",
            "emergency_services_available": False,
            "regular_services_available": True
        }
    ],
    "services": [
        {
            "name": "HVAC Repair",
            "description": "Professional HVAC repair and maintenance services",
            "pricing_model": "hourly",
            "unit_price": 125.0,
            "estimated_duration_hours": 2.0,
            "is_emergency": True,
            "is_featured": True
        },
        {
            "name": "AC Installation",
            "description": "Complete air conditioning system installation",
            "pricing_model": "fixed",
            "unit_price": 3500.0,
            "estimated_duration_hours": 8.0,
            "is_emergency": False,
            "is_featured": True
        },
        {
            "name": "Maintenance Check",
            "description": "Routine HVAC system maintenance and inspection",
            "pricing_model": "fixed",
            "unit_price": 89.0,
            "estimated_duration_hours": 1.0,
            "is_emergency": False,
            "is_featured": False
        }
    ],
    "products": [
        {
            "name": "High-Efficiency Air Filter",
            "sku": "AF-HEPA-001",
            "description": "HEPA air filter for improved indoor air quality",
            "unit_price": 29.99,
            "is_featured": True
        },
        {
            "name": "Thermostat - Smart WiFi",
            "sku": "THERM-WIFI-001",
            "description": "Smart WiFi-enabled programmable thermostat",
            "unit_price": 199.99,
            "is_featured": True
        },
        {
            "name": "Refrigerant R-410A",
            "sku": "REF-410A-001",
            "description": "R-410A refrigerant for modern AC systems",
            "unit_price": 45.00,
            "is_featured": False
        }
    ],
    "locations": [
        {
            "name": "Main Office",
            "address": "123 Business Park Dr",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "is_primary": True
        }
    ],
    "hours": [
        {
            "day_of_week": 1,  # Monday
            "is_open": True,
            "open_time": "08:00:00",
            "close_time": "17:00:00",
            "lunch_start": "12:00:00",
            "lunch_end": "13:00:00",
            "is_emergency_only": False
        },
        {
            "day_of_week": 2,  # Tuesday
            "is_open": True,
            "open_time": "08:00:00",
            "close_time": "17:00:00",
            "lunch_start": "12:00:00",
            "lunch_end": "13:00:00",
            "is_emergency_only": False
        },
        {
            "day_of_week": 3,  # Wednesday
            "is_open": True,
            "open_time": "08:00:00",
            "close_time": "17:00:00",
            "lunch_start": "12:00:00",
            "lunch_end": "13:00:00",
            "is_emergency_only": False
        },
        {
            "day_of_week": 4,  # Thursday
            "is_open": True,
            "open_time": "08:00:00",
            "close_time": "17:00:00",
            "lunch_start": "12:00:00",
            "lunch_end": "13:00:00",
            "is_emergency_only": False
        },
        {
            "day_of_week": 5,  # Friday
            "is_open": True,
            "open_time": "08:00:00",
            "close_time": "17:00:00",
            "lunch_start": "12:00:00",
            "lunch_end": "13:00:00",
            "is_emergency_only": False
        },
        {
            "day_of_week": 6,  # Saturday
            "is_open": True,
            "open_time": "09:00:00",
            "close_time": "15:00:00",
            "is_emergency_only": True
        },
        {
            "day_of_week": 7,  # Sunday
            "is_open": False,
            "is_emergency_only": True
        }
    ],
    "branding": {
        "primary_color": "#2563EB",
        "secondary_color": "#059669",
        "logo_url": "https://via.placeholder.com/200x100/2563EB/FFFFFF?text=HVAC+Pro"
    },
    "idempotency_key": str(uuid.uuid4())
}


class MobileDeploymentTester:
    """Test client for mobile website deployment API."""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def submit_deployment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a deployment request."""
        console.print("\n🚀 [bold blue]Submitting deployment request...[/bold blue]")
        
        # Display request summary
        table = Table(title="Deployment Request Summary")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Subdomain", data["subdomain"])
        table.add_row("Service Areas", str(len(data["service_areas"])))
        table.add_row("Services", str(len(data["services"])))
        table.add_row("Products", str(len(data["products"])))
        table.add_row("Locations", str(len(data["locations"])))
        table.add_row("Business Hours", str(len(data["hours"])))
        table.add_row("Idempotency Key", data["idempotency_key"][:8] + "...")
        
        console.print(table)
        
        try:
            response = await self.client.post(
                f"{self.base_url}/mobile/website/deploy",
                json=data
            )
            
            if response.status_code == 201:
                result = response.json()
                console.print(f"✅ [bold green]Deployment submitted successfully![/bold green]")
                console.print(f"📋 Deployment ID: [bold]{result['deployment_id']}[/bold]")
                console.print(f"⏱️  Estimated completion: {result['estimated_completion_minutes']} minutes")
                return result
            else:
                console.print(f"❌ [bold red]Deployment failed![/bold red]")
                console.print(f"Status: {response.status_code}")
                console.print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            console.print(f"❌ [bold red]Request failed: {str(e)}[/bold red]")
            return None
    
    async def poll_deployment_status(self, deployment_id: str, max_polls: int = 60) -> Dict[str, Any]:
        """Poll deployment status until completion."""
        console.print(f"\n📊 [bold blue]Polling deployment status...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Deploying website...", total=100)
            
            for poll_count in range(max_polls):
                try:
                    response = await self.client.get(
                        f"{self.base_url}/mobile/website/deployments/{deployment_id}"
                    )
                    
                    if response.status_code == 200:
                        status_data = response.json()
                        
                        # Update progress
                        progress.update(
                            task,
                            completed=status_data["progress"],
                            description=f"[cyan]{status_data['current_step']}[/cyan]"
                        )
                        
                        # Check if deployment is complete
                        if status_data["status"] in ["completed", "failed", "cancelled"]:
                            return status_data
                        
                        # Wait before next poll
                        await asyncio.sleep(2)
                    else:
                        console.print(f"❌ Status check failed: {response.status_code}")
                        break
                        
                except Exception as e:
                    console.print(f"❌ Status check error: {str(e)}")
                    break
            
            console.print("⏰ [yellow]Polling timeout reached[/yellow]")
            return None
    
    async def get_deployment_list(self) -> Dict[str, Any]:
        """Get list of recent deployments."""
        try:
            response = await self.client.get(f"{self.base_url}/mobile/website/deployments")
            
            if response.status_code == 200:
                return response.json()
            else:
                console.print(f"❌ Failed to get deployment list: {response.status_code}")
                return None
                
        except Exception as e:
            console.print(f"❌ Error getting deployment list: {str(e)}")
            return None
    
    async def cancel_deployment(self, deployment_id: str) -> bool:
        """Cancel a deployment."""
        try:
            response = await self.client.post(
                f"{self.base_url}/mobile/website/deployments/{deployment_id}/cancel"
            )
            
            if response.status_code == 200:
                console.print("✅ [bold green]Deployment cancelled successfully![/bold green]")
                return True
            else:
                console.print(f"❌ Failed to cancel deployment: {response.status_code}")
                return False
                
        except Exception as e:
            console.print(f"❌ Error cancelling deployment: {str(e)}")
            return False


def display_final_result(status_data: Dict[str, Any]):
    """Display the final deployment result."""
    console.print("\n" + "="*60)
    
    if status_data["status"] == "completed":
        panel = Panel(
            f"🎉 [bold green]Deployment Completed Successfully![/bold green]\n\n"
            f"🌐 Website URL: [link]{status_data['website_url']}[/link]\n"
            f"⏱️  Total Time: {_calculate_duration(status_data)}\n"
            f"📋 Deployment ID: {status_data['deployment_id']}\n"
            f"✨ Status: {status_data['status'].upper()}",
            title="🚀 Deployment Result",
            border_style="green"
        )
    elif status_data["status"] == "failed":
        panel = Panel(
            f"❌ [bold red]Deployment Failed![/bold red]\n\n"
            f"💥 Error: {status_data.get('error_message', 'Unknown error')}\n"
            f"📋 Deployment ID: {status_data['deployment_id']}\n"
            f"⏱️  Duration: {_calculate_duration(status_data)}",
            title="💥 Deployment Failed",
            border_style="red"
        )
    else:
        panel = Panel(
            f"⚠️  [bold yellow]Deployment Status: {status_data['status'].upper()}[/bold yellow]\n\n"
            f"📋 Deployment ID: {status_data['deployment_id']}\n"
            f"📊 Progress: {status_data['progress']}%\n"
            f"🔄 Current Step: {status_data['current_step']}",
            title="⚠️  Deployment Status",
            border_style="yellow"
        )
    
    console.print(panel)
    
    # Show build logs if available
    if status_data.get("build_logs"):
        console.print("\n📝 [bold]Recent Build Logs:[/bold]")
        for log in status_data["build_logs"][-5:]:  # Show last 5 logs
            console.print(f"  • {log}")


def _calculate_duration(status_data: Dict[str, Any]) -> str:
    """Calculate deployment duration."""
    if status_data.get("created_at") and status_data.get("completed_at"):
        try:
            start = datetime.fromisoformat(status_data["created_at"].replace('Z', '+00:00'))
            end = datetime.fromisoformat(status_data["completed_at"].replace('Z', '+00:00'))
            duration = end - start
            return f"{duration.total_seconds():.1f} seconds"
        except:
            pass
    return "Unknown"


@click.command()
@click.option('--token', '-t', help='JWT authentication token', required=True)
@click.option('--base-url', '-u', default=API_BASE, help='API base URL')
@click.option('--subdomain', '-s', help='Custom subdomain (optional)')
@click.option('--list-only', '-l', is_flag=True, help='Only list existing deployments')
@click.option('--cancel', '-c', help='Cancel deployment by ID')
@click.option('--mock-token', is_flag=True, help='Use mock token for testing')
async def main(token: str, base_url: str, subdomain: str, list_only: bool, cancel: str, mock_token: bool):
    """Test the mobile website deployment API."""
    
    console.print(Panel(
        "[bold blue]Mobile Website Deployment Tester[/bold blue]\n"
        "This tool simulates a mobile app calling the deployment API",
        title="🧪 Test Suite"
    ))
    
    # Use mock token if requested
    if mock_token:
        token = "mock-jwt-token-for-testing"
        console.print("⚠️  [yellow]Using mock token - API calls may fail without proper authentication[/yellow]")
    
    async with MobileDeploymentTester(base_url, token) as tester:
        
        # Handle list-only mode
        if list_only:
            console.print("\n📋 [bold]Fetching deployment list...[/bold]")
            deployments = await tester.get_deployment_list()
            
            if deployments:
                table = Table(title="Recent Deployments")
                table.add_column("ID", style="cyan")
                table.add_column("Status", style="white")
                table.add_column("Progress", style="green")
                table.add_column("Created", style="blue")
                
                for deployment in deployments["deployments"]:
                    table.add_row(
                        deployment["deployment_id"][:8] + "...",
                        deployment["status"],
                        f"{deployment['progress']}%",
                        deployment["created_at"][:19]
                    )
                
                console.print(table)
                console.print(f"\nTotal deployments: {deployments['total_count']}")
            
            return
        
        # Handle cancel mode
        if cancel:
            console.print(f"\n🛑 [bold]Cancelling deployment {cancel}...[/bold]")
            success = await tester.cancel_deployment(cancel)
            return
        
        # Customize test data if subdomain provided
        if subdomain:
            TEST_DEPLOYMENT_DATA["subdomain"] = subdomain
        
        # Run full deployment test
        console.print(f"\n🎯 [bold]Starting deployment test...[/bold]")
        console.print(f"🌐 Target subdomain: [bold]{TEST_DEPLOYMENT_DATA['subdomain']}[/bold]")
        
        # Step 1: Submit deployment
        deployment_result = await tester.submit_deployment(TEST_DEPLOYMENT_DATA)
        
        if not deployment_result:
            console.print("❌ [bold red]Test failed - could not submit deployment[/bold red]")
            return
        
        deployment_id = deployment_result["deployment_id"]
        
        # Step 2: Poll status
        final_status = await tester.poll_deployment_status(deployment_id)
        
        if final_status:
            display_final_result(final_status)
        else:
            console.print("❌ [bold red]Test incomplete - status polling failed[/bold red]")
        
        # Step 3: Show deployment list
        console.print("\n📋 [bold]Fetching updated deployment list...[/bold]")
        deployments = await tester.get_deployment_list()
        
        if deployments and deployments["deployments"]:
            console.print(f"📊 Total deployments: {deployments['total_count']}")
            console.print(f"🆕 Latest deployment: {deployments['deployments'][0]['deployment_id'][:8]}...")


if __name__ == "__main__":
    # Install required packages if not available
    try:
        import httpx
        import click
        from rich.console import Console
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "httpx", "click", "rich"])
        import httpx
        import click
        from rich.console import Console
    
    asyncio.run(main())
