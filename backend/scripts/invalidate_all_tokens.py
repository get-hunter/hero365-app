#!/usr/bin/env python3
"""
Emergency Token Invalidation Script

This script immediately invalidates ALL JWT tokens by rotating the secret key.
Use this in emergency situations when you need to force all users to re-authenticate immediately.

⚠️  WARNING: This will log out ALL users and they will need to sign in again.

Usage:
    python scripts/invalidate_all_tokens.py --confirm
"""

import os
import sys
import argparse
import secrets
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_new_secret_key() -> str:
    """Generate a new secure secret key."""
    return secrets.token_urlsafe(64)


def update_env_file(env_file_path: str, new_secret: str) -> bool:
    """
    Update the SECRET_KEY in the environment file.
    
    Args:
        env_file_path: Path to the .env file
        new_secret: New secret key to set
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read current env file
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Find and update SECRET_KEY line
        secret_key_updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith('SECRET_KEY='):
                lines[i] = f'SECRET_KEY={new_secret}\n'
                secret_key_updated = True
                break
        
        # If SECRET_KEY not found, add it
        if not secret_key_updated:
            lines.append(f'SECRET_KEY={new_secret}\n')
        
        # Write back to file
        with open(env_file_path, 'w') as f:
            f.writelines(lines)
        
        logger.info(f"Updated SECRET_KEY in {env_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update {env_file_path}: {str(e)}")
        return False


def backup_current_secret(env_file_path: str) -> str:
    """
    Backup the current secret key.
    
    Args:
        env_file_path: Path to the .env file
        
    Returns:
        Current secret key or empty string if not found
    """
    try:
        if not os.path.exists(env_file_path):
            return ""
        
        with open(env_file_path, 'r') as f:
            for line in f:
                if line.strip().startswith('SECRET_KEY='):
                    return line.strip().split('=', 1)[1]
        
        return ""
        
    except Exception as e:
        logger.error(f"Failed to read current secret from {env_file_path}: {str(e)}")
        return ""


def main():
    """Main function to handle emergency token invalidation."""
    parser = argparse.ArgumentParser(
        description="Emergency Token Invalidation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
⚠️  WARNING: This will immediately invalidate ALL JWT tokens!
All users will be logged out and need to sign in again.

Use this only in emergency situations like:
- Security breach
- Compromised secret key
- Need to force all users to re-authenticate

Examples:
  python scripts/invalidate_all_tokens.py --confirm
  python scripts/invalidate_all_tokens.py --confirm --env-file custom.env
        """
    )
    
    parser.add_argument('--confirm', action='store_true', required=True,
                       help='Confirm that you want to invalidate ALL tokens')
    parser.add_argument('--env-file', default='.env',
                       help='Path to environment file (default: .env)')
    parser.add_argument('--backup-secret', action='store_true',
                       help='Backup current secret to invalidated_secrets.log')
    
    args = parser.parse_args()
    
    # Double confirmation for safety
    print("🚨 EMERGENCY TOKEN INVALIDATION")
    print("=" * 50)
    print("⚠️  This will IMMEDIATELY invalidate ALL JWT tokens!")
    print("⚠️  ALL users will be logged out!")
    print("⚠️  Users will need to sign in again!")
    print("=" * 50)
    
    confirmation = input("Type 'INVALIDATE ALL TOKENS' to confirm: ")
    if confirmation != 'INVALIDATE ALL TOKENS':
        print("❌ Operation cancelled.")
        return
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    env_file_path = os.path.join(backend_dir, args.env_file)
    
    try:
        # Backup current secret if requested
        if args.backup_secret:
            current_secret = backup_current_secret(env_file_path)
            if current_secret:
                backup_file = os.path.join(backend_dir, 'invalidated_secrets.log')
                with open(backup_file, 'a') as f:
                    timestamp = datetime.utcnow().isoformat()
                    f.write(f"{timestamp}: {current_secret}\n")
                logger.info(f"Current secret backed up to {backup_file}")
        
        # Generate new secret key
        new_secret = generate_new_secret_key()
        logger.info("Generated new secret key")
        
        # Update .env file
        if update_env_file(env_file_path, new_secret):
            print("✅ SECRET_KEY updated successfully!")
            print("🔄 You need to restart your application servers for this to take effect.")
            print("")
            print("Next steps:")
            print("1. Restart your backend server")
            print("2. Inform users they need to sign in again")
            print("3. Monitor for any issues")
            
            logger.info("Emergency token invalidation completed successfully")
            
        else:
            print("❌ Failed to update SECRET_KEY")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Emergency token invalidation failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 