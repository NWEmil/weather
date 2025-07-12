#!/usr/bin/env python3
"""
Discord Weather Bot Entry Point
Starts the Discord bot and handles graceful shutdown.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from weather_bot_simple import run_bot

def main():
    """Main entry point for the Discord weather bot."""
    # Load environment variables
    load_dotenv()
    
    # Get Discord bot token from environment
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not bot_token:
        print("Error: DISCORD_BOT_TOKEN environment variable is required")
        print("Please set your Discord bot token in the environment or .env file")
        sys.exit(1)
    
    try:
        print("Starting Discord Weather Bot...")
        run_bot(bot_token)
    except KeyboardInterrupt:
        print("\nBot shutdown requested by user")
    except Exception as e:
        print(f"Error running bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
