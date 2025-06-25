#!/usr/bin/env python3
"""
Token Revocation Script for Hero365

This script provides functionality to revoke authentication tokens for users.
Useful for security incidents, maintenance, or testing scenarios.

Usage:
    python scripts/revoke_tokens.py --all                    # Revoke all user tokens
    python scripts/revoke_tokens.py --user user-uuid         # Revoke specific user
    python scripts/revoke_tokens.py --business business-uuid # Revoke all users in business
    python scripts/revoke_tokens.py --inactive               # Revoke inactive users only
    python scripts/revoke_tokens.py --dry-run --all          # Preview what would be revoked
"""

import asyncio
import argparse
import sys
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uuid

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.infrastructure.config.dependency_injection import get_container
from app.core.auth_facade import auth_facade

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('token_revocation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TokenRevocationManager:
    """Manager for token revocation operations."""
    
    def __init__(self):
        self.container = get_container()
        self.revoked_count = 0
        self.failed_count = 0
        self.total_count = 0
    
    async def revoke_all_tokens(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Revoke tokens for all users in the system.
        
        Args:
            dry_run: If True, only simulate the operation
            
        Returns:
            Dictionary with operation results
        """
        logger.info("Starting token revocation for ALL users")
        
        if dry_run:
            logger.info("DRY RUN MODE - No actual tokens will be revoked")
        
        try:
            # Get all users from Supabase
            users_data = await auth_facade.list_users(page=1, per_page=1000)
            users = users_data.get('users', [])
            
            if not users:
                logger.warning("No users found in the system")
                return {"success": True, "revoked": 0, "failed": 0, "total": 0}
            
            self.total_count = len(users)
            logger.info(f"Found {self.total_count} users to process")
            
            # Process users in batches to avoid overwhelming the system
            batch_size = 10
            for i in range(0, len(users), batch_size):
                batch = users[i:i + batch_size]
                await self._process_user_batch(batch, dry_run)
                
                # Small delay between batches to be respectful to the API
                await asyncio.sleep(0.5)
            
            logger.info(f"Token revocation completed: {self.revoked_count} revoked, {self.failed_count} failed, {self.total_count} total")
            
            return {
                "success": True,
                "revoked": self.revoked_count,
                "failed": self.failed_count,
                "total": self.total_count,
                "dry_run": dry_run
            }
            
        except Exception as e:
            logger.error(f"Failed to revoke all tokens: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "revoked": self.revoked_count,
                "failed": self.failed_count,
                "total": self.total_count
            }
    
    async def revoke_user_token(self, user_id: str, dry_run: bool = False) -> bool:
        """
        Revoke tokens for a specific user.
        
        Args:
            user_id: UUID of the user
            dry_run: If True, only simulate the operation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate UUID format
            uuid.UUID(user_id)
        except ValueError:
            logger.error(f"Invalid user ID format: {user_id}")
            return False
        
        logger.info(f"Revoking tokens for user: {user_id}")
        
        if dry_run:
            logger.info("DRY RUN MODE - No actual tokens will be revoked")
            return True
        
        try:
            success = await auth_facade.revoke_user_tokens(user_id)
            
            if success:
                logger.info(f"Successfully revoked tokens for user: {user_id}")
                return True
            else:
                logger.error(f"Failed to revoke tokens for user: {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error revoking tokens for user {user_id}: {str(e)}")
            return False
    
    async def revoke_business_user_tokens(self, business_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Revoke tokens for all users in a specific business.
        
        Args:
            business_id: UUID of the business
            dry_run: If True, only simulate the operation
            
        Returns:
            Dictionary with operation results
        """
        try:
            # Validate UUID format
            uuid.UUID(business_id)
        except ValueError:
            logger.error(f"Invalid business ID format: {business_id}")
            return {"success": False, "error": "Invalid business ID format"}
        
        logger.info(f"Revoking tokens for all users in business: {business_id}")
        
        if dry_run:
            logger.info("DRY RUN MODE - No actual tokens will be revoked")
        
        try:
            # Get business membership repository
            membership_repo = self.container.get_business_membership_repository()
            memberships = await membership_repo.get_business_memberships(uuid.UUID(business_id))
            
            if not memberships:
                logger.warning(f"No users found in business: {business_id}")
                return {"success": True, "revoked": 0, "failed": 0, "total": 0}
            
            user_ids = [str(membership.user_id) for membership in memberships if membership.is_active]
            self.total_count = len(user_ids)
            
            logger.info(f"Found {self.total_count} active users in business {business_id}")
            
            # Process users
            for user_id in user_ids:
                if await self.revoke_user_token(user_id, dry_run):
                    self.revoked_count += 1
                else:
                    self.failed_count += 1
                
                # Small delay between operations
                await asyncio.sleep(0.1)
            
            logger.info(f"Business token revocation completed: {self.revoked_count} revoked, {self.failed_count} failed")
            
            return {
                "success": True,
                "business_id": business_id,
                "revoked": self.revoked_count,
                "failed": self.failed_count,
                "total": self.total_count,
                "dry_run": dry_run
            }
            
        except Exception as e:
            logger.error(f"Failed to revoke business user tokens: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "business_id": business_id,
                "revoked": self.revoked_count,
                "failed": self.failed_count
            }
    
    async def revoke_inactive_user_tokens(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Revoke tokens for inactive users (users who haven't signed in recently).
        
        Args:
            dry_run: If True, only simulate the operation
            
        Returns:
            Dictionary with operation results
        """
        logger.info("Revoking tokens for inactive users")
        
        if dry_run:
            logger.info("DRY RUN MODE - No actual tokens will be revoked")
        
        try:
            # Get users repository
            user_repo = self.container.get_user_repository()
            
            # Define inactive period (30 days)
            inactive_since = datetime.utcnow() - timedelta(days=30)
            
            # Get inactive users from public.users table
            # Note: This assumes you have a method to get inactive users
            # You might need to implement this method in your user repository
            
            # For now, we'll get all users and filter them
            users_data = await auth_facade.list_users(page=1, per_page=1000)
            users = users_data.get('users', [])
            
            inactive_users = []
            for user in users:
                last_sign_in = user.last_sign_in
                if last_sign_in:
                    try:
                        last_sign_in_date = datetime.fromisoformat(last_sign_in.replace('Z', '+00:00'))
                        if last_sign_in_date < inactive_since:
                            inactive_users.append(user)
                    except (ValueError, AttributeError):
                        # If we can't parse the date, consider the user inactive
                        inactive_users.append(user)
                else:
                    # No last sign in date means they've never signed in or are very old
                    inactive_users.append(user)
            
            self.total_count = len(inactive_users)
            logger.info(f"Found {self.total_count} inactive users (no activity since {inactive_since})")
            
            if self.total_count == 0:
                return {"success": True, "revoked": 0, "failed": 0, "total": 0}
            
            # Process inactive users
            for user in inactive_users:
                if await self.revoke_user_token(user.id, dry_run):
                    self.revoked_count += 1
                else:
                    self.failed_count += 1
                
                await asyncio.sleep(0.1)
            
            logger.info(f"Inactive user token revocation completed: {self.revoked_count} revoked, {self.failed_count} failed")
            
            return {
                "success": True,
                "revoked": self.revoked_count,
                "failed": self.failed_count,
                "total": self.total_count,
                "inactive_since": inactive_since.isoformat(),
                "dry_run": dry_run
            }
            
        except Exception as e:
            logger.error(f"Failed to revoke inactive user tokens: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "revoked": self.revoked_count,
                "failed": self.failed_count
            }
    
    async def _process_user_batch(self, users: List[Any], dry_run: bool):
        """Process a batch of users for token revocation."""
        tasks = []
        
        for user in users:
            task = self._revoke_user_token_with_count(user.id, dry_run)
            tasks.append(task)
        
        # Process batch concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _revoke_user_token_with_count(self, user_id: str, dry_run: bool):
        """Revoke user token and update counters."""
        try:
            if await self.revoke_user_token(user_id, dry_run):
                self.revoked_count += 1
            else:
                self.failed_count += 1
        except Exception as e:
            logger.error(f"Error processing user {user_id}: {str(e)}")
            self.failed_count += 1


async def main():
    """Main function to handle command line arguments and execute token revocation."""
    parser = argparse.ArgumentParser(
        description="Token Revocation Script for Hero365",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/revoke_tokens.py --all                    # Revoke all user tokens
  python scripts/revoke_tokens.py --user user-uuid         # Revoke specific user
  python scripts/revoke_tokens.py --business business-uuid # Revoke all users in business
  python scripts/revoke_tokens.py --inactive               # Revoke inactive users only
  python scripts/revoke_tokens.py --dry-run --all          # Preview what would be revoked
        """
    )
    
    # Operation type (mutually exclusive)
    operation_group = parser.add_mutually_exclusive_group(required=True)
    operation_group.add_argument('--all', action='store_true', help='Revoke tokens for all users')
    operation_group.add_argument('--user', metavar='USER_ID', help='Revoke tokens for specific user (UUID)')
    operation_group.add_argument('--business', metavar='BUSINESS_ID', help='Revoke tokens for all users in business (UUID)')
    operation_group.add_argument('--inactive', action='store_true', help='Revoke tokens for inactive users only')
    
    # Options
    parser.add_argument('--dry-run', action='store_true', help='Preview operation without actually revoking tokens')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt (use with caution)')
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Confirmation for non-dry-run operations
    if not args.dry_run and not args.confirm:
        if args.all:
            confirmation = input("⚠️  This will revoke tokens for ALL users. Are you sure? (type 'YES' to confirm): ")
        elif args.business:
            confirmation = input(f"⚠️  This will revoke tokens for all users in business {args.business}. Are you sure? (type 'YES' to confirm): ")
        elif args.inactive:
            confirmation = input("⚠️  This will revoke tokens for all inactive users. Are you sure? (type 'YES' to confirm): ")
        else:
            confirmation = input(f"⚠️  This will revoke tokens for user {args.user}. Are you sure? (type 'YES' to confirm): ")
        
        if confirmation != 'YES':
            print("Operation cancelled.")
            return
    
    # Initialize manager
    manager = TokenRevocationManager()
    
    # Execute operation
    try:
        if args.all:
            result = await manager.revoke_all_tokens(dry_run=args.dry_run)
        elif args.user:
            success = await manager.revoke_user_token(args.user, dry_run=args.dry_run)
            result = {"success": success, "user_id": args.user, "dry_run": args.dry_run}
        elif args.business:
            result = await manager.revoke_business_user_tokens(args.business, dry_run=args.dry_run)
        elif args.inactive:
            result = await manager.revoke_inactive_user_tokens(dry_run=args.dry_run)
        
        # Print results
        print("\n" + "="*50)
        print("TOKEN REVOCATION RESULTS")
        print("="*50)
        
        if args.dry_run:
            print("🔍 DRY RUN MODE - No actual changes were made")
        
        if result.get("success"):
            print("✅ Operation completed successfully")
            
            if "revoked" in result:
                print(f"📊 Revoked: {result['revoked']}")
                print(f"📊 Failed: {result['failed']}")
                print(f"📊 Total: {result['total']}")
            
            if args.user:
                print(f"👤 User: {result['user_id']}")
            elif args.business:
                print(f"🏢 Business: {result['business_id']}")
            elif args.inactive:
                print(f"⏰ Inactive since: {result.get('inactive_since', 'N/A')}")
                
        else:
            print("❌ Operation failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 