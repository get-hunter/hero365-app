#!/usr/bin/env python3
"""
Interactive Business Website Deployer

This script presents all businesses from the database in an interactive menu,
allows you to select one, and then builds and deploys their website to Cloudflare Workers.

Usage:
    python scripts/interactive-website-deployer.py [--env staging|production] [--build-only]

Examples:
    # Interactive deployment to staging
    python scripts/interactive-website-deployer.py --env staging
    
    # Build only (no deployment)
    python scripts/interactive-website-deployer.py --build-only
    
    # Production deployment
    python scripts/interactive-website-deployer.py --env production
"""

import os
import sys
import subprocess
import argparse
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Add the backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from supabase import create_client, Client
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("Please install: pip install supabase rich")
    sys.exit(1)

@dataclass
class Business:
    """Business data structure"""
    id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    state: Optional[str]
    primary_trade: Optional[str]
    is_active: bool
    owner_id: Optional[str]

class InteractiveWebsiteDeployer:
    """Interactive website deployer for Hero365 businesses"""
    
    def __init__(self, environment: str = "staging", build_only: bool = False):
        self.environment = environment
        self.build_only = build_only
        self.console = Console()
        self.supabase_client: Optional[Client] = None
        
        # Paths
        self.root_dir = Path(__file__).parent.parent
        self.website_builder_dir = self.root_dir / "website-builder"
        self.deploy_script = self.website_builder_dir / "scripts" / "deploy-with-business.js"
        
        # Load environment variables
        self._load_environment()
        
    def _load_environment(self):
        """Load environment variables from .env file"""
        env_file = self.root_dir / "environments" / ".env"
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key, value)
        
        # Validate required environment variables
        required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            self.console.print(f"❌ Missing required environment variables: {', '.join(missing_vars)}", style="red")
            self.console.print("Please check your environments/.env file", style="yellow")
            sys.exit(1)
    
    def _get_supabase_client(self) -> Client:
        """Get Supabase client"""
        if not self.supabase_client:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
            
            self.supabase_client = create_client(supabase_url, supabase_key)
        
        return self.supabase_client
    
    def fetch_businesses(self) -> List[Business]:
        """Fetch all active businesses from the database"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Fetching businesses from database...", total=None)
                
                client = self._get_supabase_client()
                
                # Query businesses with essential information
                response = client.table('businesses').select(
                    'id, name, email, phone, city, state, primary_trade, is_active, owner_id'
                ).eq('is_active', True).order('name').execute()
                
                progress.update(task, completed=True)
            
            if not response.data:
                self.console.print("⚠️ No active businesses found in the database", style="yellow")
                return []
            
            businesses = []
            for row in response.data:
                businesses.append(Business(
                    id=row['id'],
                    name=row['name'] or 'Unnamed Business',
                    email=row.get('email'),
                    phone=row.get('phone'),
                    city=row.get('city'),
                    state=row.get('state'),
                    primary_trade=row.get('primary_trade'),
                    is_active=row.get('is_active', True),
                    owner_id=row.get('owner_id')
                ))
            
            return businesses
            
        except Exception as e:
            self.console.print(f"❌ Error fetching businesses: {str(e)}", style="red")
            return []
    
    def display_businesses(self, businesses: List[Business]) -> None:
        """Display businesses in a formatted table"""
        if not businesses:
            return
        
        table = Table(title="🏢 Available Businesses", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Business Name", style="bold blue", min_width=20)
        table.add_column("Trade", style="green", width=15)
        table.add_column("Location", style="cyan", width=20)
        table.add_column("Contact", style="yellow", width=25)
        
        for i, business in enumerate(businesses, 1):
            location = ""
            if business.city and business.state:
                location = f"{business.city}, {business.state}"
            elif business.city:
                location = business.city
            elif business.state:
                location = business.state
            
            contact = ""
            if business.email and business.phone:
                contact = f"{business.email}\n{business.phone}"
            elif business.email:
                contact = business.email
            elif business.phone:
                contact = business.phone
            
            table.add_row(
                str(i),
                business.name,
                business.primary_trade or "N/A",
                location or "N/A",
                contact or "N/A"
            )
        
        self.console.print(table)
    
    def select_business(self, businesses: List[Business]) -> Optional[Business]:
        """Interactive business selection"""
        if not businesses:
            self.console.print("❌ No businesses available for selection", style="red")
            return None
        
        self.console.print()
        self.console.print("📋 Select a business to deploy:", style="bold")
        
        while True:
            try:
                choice = Prompt.ask(
                    f"Enter business number (1-{len(businesses)}) or 'q' to quit",
                    default="1"
                )
                
                if choice.lower() == 'q':
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(businesses):
                    selected = businesses[index]
                    
                    # Confirm selection
                    self.console.print()
                    panel = Panel(
                        f"[bold blue]{selected.name}[/bold blue]\n"
                        f"Trade: {selected.primary_trade or 'N/A'}\n"
                        f"Location: {selected.city or 'N/A'}, {selected.state or 'N/A'}\n"
                        f"Email: {selected.email or 'N/A'}\n"
                        f"Phone: {selected.phone or 'N/A'}",
                        title="Selected Business",
                        border_style="green"
                    )
                    self.console.print(panel)
                    
                    if Confirm.ask("Deploy website for this business?", default=True):
                        return selected
                    else:
                        self.console.print("Selection cancelled. Choose another business or 'q' to quit.")
                        continue
                else:
                    self.console.print(f"❌ Invalid choice. Please enter a number between 1 and {len(businesses)}", style="red")
                    
            except ValueError:
                self.console.print("❌ Invalid input. Please enter a number or 'q' to quit", style="red")
            except KeyboardInterrupt:
                self.console.print("\n👋 Deployment cancelled by user", style="yellow")
                return None
    
    def deploy_business_website(self, business: Business) -> bool:
        """Deploy website for the selected business"""
        try:
            self.console.print()
            self.console.print(f"🚀 Starting website deployment for [bold blue]{business.name}[/bold blue]", style="green")
            self.console.print(f"Environment: [bold]{self.environment}[/bold]")
            self.console.print(f"Build Only: [bold]{self.build_only}[/bold]")
            
            # Prepare deployment command
            cmd = [
                "node",
                str(self.deploy_script),
                f"--businessId={business.id}",
                f"--env={self.environment}",
                "--verbose"
            ]
            
            if self.build_only:
                cmd.append("--build-only")
            
            # Add business overrides for better deployment
            if business.name:
                cmd.append(f"--businessName={business.name}")
            if business.phone:
                cmd.append(f"--businessPhone={business.phone}")
            if business.email:
                cmd.append(f"--businessEmail={business.email}")
            
            self.console.print(f"Executing: {' '.join(cmd)}", style="dim")
            self.console.print()
            
            # Change to website-builder directory
            original_cwd = os.getcwd()
            os.chdir(self.website_builder_dir)
            
            try:
                # Run deployment
                result = subprocess.run(
                    cmd,
                    capture_output=False,  # Show real-time output
                    text=True,
                    check=True
                )
                
                self.console.print()
                self.console.print("✅ Website deployment completed successfully!", style="bold green")
                return True
                
            finally:
                os.chdir(original_cwd)
                
        except subprocess.CalledProcessError as e:
            self.console.print(f"❌ Deployment failed with exit code {e.returncode}", style="red")
            return False
        except Exception as e:
            self.console.print(f"❌ Deployment error: {str(e)}", style="red")
            return False
    
    def run(self):
        """Main execution flow"""
        # Display header
        self.console.print()
        panel = Panel(
            "[bold blue]Hero365 Interactive Website Deployer[/bold blue]\n"
            f"Environment: [yellow]{self.environment}[/yellow]\n"
            f"Mode: [cyan]{'Build Only' if self.build_only else 'Build & Deploy'}[/cyan]",
            title="🚀 Website Deployment Tool",
            border_style="blue"
        )
        self.console.print(panel)
        
        # Fetch businesses
        businesses = self.fetch_businesses()
        if not businesses:
            self.console.print("❌ No businesses found. Exiting.", style="red")
            return
        
        self.console.print(f"✅ Found {len(businesses)} active businesses", style="green")
        
        # Display businesses
        self.display_businesses(businesses)
        
        # Select business
        selected_business = self.select_business(businesses)
        if not selected_business:
            self.console.print("👋 No business selected. Exiting.", style="yellow")
            return
        
        # Deploy website
        success = self.deploy_business_website(selected_business)
        
        if success:
            self.console.print()
            self.console.print("🎉 Deployment process completed successfully!", style="bold green")
            if not self.build_only:
                self.console.print("🌐 Your website should be available shortly on Cloudflare Workers", style="cyan")
        else:
            self.console.print()
            self.console.print("❌ Deployment process failed. Check the logs above for details.", style="red")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Interactive Business Website Deployer for Hero365",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/interactive-website-deployer.py --env staging
  python scripts/interactive-website-deployer.py --env production --build-only
  python scripts/interactive-website-deployer.py
        """
    )
    
    parser.add_argument(
        '--env',
        choices=['development', 'staging', 'production'],
        default='staging',
        help='Target environment (default: staging)'
    )
    
    parser.add_argument(
        '--build-only',
        action='store_true',
        help='Only build the website, do not deploy'
    )
    
    args = parser.parse_args()
    
    # Validate deployment script exists
    deployer = InteractiveWebsiteDeployer(args.env, args.build_only)
    
    if not deployer.deploy_script.exists():
        print(f"❌ Deployment script not found: {deployer.deploy_script}")
        print("Please ensure you're running this from the project root directory")
        sys.exit(1)
    
    try:
        deployer.run()
    except KeyboardInterrupt:
        print("\n👋 Deployment cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
