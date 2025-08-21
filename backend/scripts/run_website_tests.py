#!/usr/bin/env python3
"""
Hero365 Website Builder Test Runner

Simple CLI script to run various tests for the website builder system.
Provides easy commands for testing and deployment.
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from scripts.test_website_deployment import WebsiteBuilderTester, run_quick_demo, run_comprehensive_test


def print_banner():
    """Print Hero365 banner."""
    
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    Hero365 Website Builder                   ║
    ║                        Test Runner                           ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """Print available commands."""
    
    help_text = """
Available Commands:

🚀 QUICK TESTS:
  quick-demo          - Run quick demo with 3 sample websites
  quick-test <trade>  - Test specific trade (e.g., plumbing, hvac)
  
🧪 COMPREHENSIVE TESTS:
  test-all-trades     - Test all 20 trade templates
  integration-test    - Run full integration test suite
  performance-test    - Run performance tests on deployed sites
  
🌐 SUBDOMAIN MANAGEMENT:
  list-subdomains     - List all active test subdomains
  deploy-subdomain    - Deploy website to hero365.ai subdomain
  delete-subdomain    - Delete a test subdomain
  
📊 UTILITIES:
  validate-templates  - Validate all template structures
  export-results      - Export test results to JSON
  cleanup-tests       - Clean up old test deployments

Examples:
  python run_website_tests.py quick-demo
  python run_website_tests.py quick-test plumbing
  python run_website_tests.py test-all-trades
  python run_website_tests.py deploy-subdomain --trade hvac --name "Test HVAC Co"
    """
    print(help_text)


async def quick_test_trade(trade_type: str, business_name: str = None, location: str = "New York"):
    """Run quick test for specific trade."""
    
    print(f"🧪 Testing {trade_type} trade...")
    
    tester = WebsiteBuilderTester()
    
    # Determine trade category
    commercial_trades = [
        "mechanical", "refrigeration", "security_systems", "landscaping",
        "kitchen_equipment", "water_treatment", "pool_spa"
    ]
    
    from app.domain.entities.business import TradeCategory
    category = TradeCategory.COMMERCIAL if trade_type in commercial_trades else TradeCategory.RESIDENTIAL
    
    # Use provided name or generate one
    if not business_name:
        business_name = f"{trade_type.title()} Pro Services"
    
    result = await tester.quick_test_deployment(
        trade_type=trade_type,
        trade_category=category,
        business_name=business_name,
        location=location
    )
    
    if result["success"]:
        print(f"✅ SUCCESS!")
        print(f"   Preview URL: {result['preview_url']}")
        print(f"   Build Time: {result['build_time_seconds']:.1f}s")
        print(f"   Lighthouse Score: {result['lighthouse_score']}")
        print(f"   Pages Generated: {result['pages_generated']}")
    else:
        print(f"❌ FAILED: {result.get('error')}")
    
    return result


async def deploy_to_subdomain(trade_type: str, business_name: str, location: str = "New York", subdomain: str = None):
    """Deploy a test website to hero365.ai subdomain."""
    
    print(f"🚀 Deploying {business_name} to subdomain...")
    
    # Run quick test which includes subdomain deployment
    result = await quick_test_trade(trade_type, business_name, location)
    
    if result["success"]:
        print(f"\n🌐 Website deployed successfully!")
        print(f"   Subdomain: {result['subdomain']}")
        print(f"   Full URL: {result['preview_url']}")
        print(f"   You can now test the website in your browser!")
        
        # Save deployment info
        deployment_info = {
            "subdomain": result["subdomain"],
            "url": result["preview_url"],
            "trade_type": trade_type,
            "business_name": business_name,
            "deployed_at": datetime.utcnow().isoformat(),
            "build_time": result["build_time_seconds"],
            "lighthouse_score": result["lighthouse_score"]
        }
        
        # Save to file
        deployments_file = Path("test_deployments.json")
        deployments = []
        
        if deployments_file.exists():
            with open(deployments_file, 'r') as f:
                deployments = json.load(f)
        
        deployments.append(deployment_info)
        
        with open(deployments_file, 'w') as f:
            json.dump(deployments, f, indent=2)
        
        print(f"   Deployment info saved to {deployments_file}")
    
    return result


async def list_deployments():
    """List recent test deployments."""
    
    deployments_file = Path("test_deployments.json")
    
    if not deployments_file.exists():
        print("No test deployments found.")
        return
    
    with open(deployments_file, 'r') as f:
        deployments = json.load(f)
    
    if not deployments:
        print("No test deployments found.")
        return
    
    print(f"📋 Recent Test Deployments ({len(deployments)} total):")
    print("=" * 60)
    
    for i, deployment in enumerate(deployments[-10:], 1):  # Show last 10
        print(f"{i}. {deployment['business_name']} ({deployment['trade_type']})")
        print(f"   URL: {deployment['url']}")
        print(f"   Deployed: {deployment['deployed_at'][:19]}")
        print(f"   Build Time: {deployment['build_time']:.1f}s")
        print(f"   Lighthouse: {deployment['lighthouse_score']}")
        print()


async def validate_all_templates():
    """Validate all website templates."""
    
    print("🔍 Validating all website templates...")
    
    from scripts.seed_website_templates import validate_all_templates
    
    results = await validate_all_templates()
    
    print(f"📊 Validation Results:")
    print(f"   Total Templates: {results['total_templates']}")
    print(f"   Valid: {results['valid_templates']}")
    print(f"   Invalid: {results['invalid_templates']}")
    
    if results['invalid_templates'] > 0:
        print(f"\n❌ Invalid Templates:")
        for result in results['results']:
            if not result['is_valid']:
                print(f"   • {result['template_name']}: {', '.join(result['issues'])}")
    else:
        print(f"\n✅ All templates are valid!")
    
    return results


async def cleanup_old_deployments():
    """Clean up old test deployments."""
    
    print("🧹 Cleaning up old test deployments...")
    
    deployments_file = Path("test_deployments.json")
    
    if not deployments_file.exists():
        print("No deployments file found.")
        return
    
    with open(deployments_file, 'r') as f:
        deployments = json.load(f)
    
    # Keep only last 20 deployments
    if len(deployments) > 20:
        deployments = deployments[-20:]
        
        with open(deployments_file, 'w') as f:
            json.dump(deployments, f, indent=2)
        
        print(f"✅ Cleaned up old deployments, kept last 20")
    else:
        print(f"No cleanup needed, {len(deployments)} deployments found")


async def main():
    """Main CLI function."""
    
    parser = argparse.ArgumentParser(
        description="Hero365 Website Builder Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        help='Command to run (use "help" for list of commands)'
    )
    
    parser.add_argument(
        '--trade',
        help='Trade type for testing (e.g., plumbing, hvac, electrical)'
    )
    
    parser.add_argument(
        '--name',
        help='Business name for testing'
    )
    
    parser.add_argument(
        '--location',
        default='New York',
        help='Business location for testing'
    )
    
    parser.add_argument(
        '--subdomain',
        help='Custom subdomain for deployment'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if not args.command or args.command == 'help':
        print_help()
        return
    
    try:
        if args.command == 'quick-demo':
            await run_quick_demo()
        
        elif args.command == 'quick-test':
            if not args.trade:
                print("❌ Error: --trade parameter required for quick-test")
                return
            await quick_test_trade(args.trade, args.name, args.location)
        
        elif args.command == 'test-all-trades':
            await run_comprehensive_test()
        
        elif args.command == 'deploy-subdomain':
            if not args.trade or not args.name:
                print("❌ Error: --trade and --name parameters required for deploy-subdomain")
                return
            await deploy_to_subdomain(args.trade, args.name, args.location, args.subdomain)
        
        elif args.command == 'list-deployments':
            await list_deployments()
        
        elif args.command == 'validate-templates':
            await validate_all_templates()
        
        elif args.command == 'cleanup-tests':
            await cleanup_old_deployments()
        
        elif args.command == 'integration-test':
            tester = WebsiteBuilderTester()
            results = await tester.integration_test_suite()
            print(f"Integration Test Status: {results['overall_status']}")
        
        elif args.command == 'performance-test':
            if not args.subdomain:
                print("❌ Error: --subdomain parameter required for performance-test")
                return
            
            tester = WebsiteBuilderTester()
            website_url = f"https://{args.subdomain}.hero365.ai"
            results = await tester.performance_test(website_url)
            print(f"Performance Score: {results['overall_score']:.1f}")
        
        else:
            print(f"❌ Unknown command: {args.command}")
            print("Use 'help' to see available commands")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
