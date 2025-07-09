"""
Hero365 Voice Agent Launcher

This script provides a simple way to launch different types of voice agent workers
based on configuration or command-line arguments.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / "environments" / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description='Hero365 Voice Agent Launcher')
    parser.add_argument(
        '--mode', 
        choices=['standard', 'reasoning'], 
        default='standard',
        help='Choose the type of voice agent worker to run (default: standard)'
    )
    parser.add_argument(
        '--max-iterations', 
        type=int, 
        default=3,
        help='Maximum reasoning iterations (only for reasoning mode, default: 3)'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set environment variables based on mode
    if args.mode == 'reasoning':
        os.environ['MAX_REASONING_ITERATIONS'] = str(args.max_iterations)
    
    # Display startup info
    logger.info("="*60)
    logger.info("🚀 Hero365 Voice Agent Launcher")
    logger.info("="*60)
    logger.info(f"Mode: {args.mode.upper()}")
    
    if args.mode == 'reasoning':
        logger.info(f"Max reasoning iterations: {args.max_iterations}")
    
    logger.info("="*60)
    
    # Import and run the appropriate worker
    try:
        if args.mode == 'standard':
            from app.voice_agents.worker import main as worker_main
            logger.info("Starting standard voice agent worker...")
            worker_main()
            
        elif args.mode == 'reasoning':
            from app.voice_agents.reasoning_worker import main as reasoning_worker_main
            logger.info("Starting reasoning voice agent worker...")
            reasoning_worker_main()
            
    except KeyboardInterrupt:
        logger.info("Shutting down voice agent worker...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start worker: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 