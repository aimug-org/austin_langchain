#!/usr/bin/env python3
"""
Simple script to run the bot and let it sync via the built-in on_ready handler.
"""

import asyncio
import sys

from discord_bot.core.config import settings
from discord_bot.core.logging import setup_logging, get_logger
from discord_bot.services.database import db_service, create_tables
from discord_bot.services.discord_service import discord_service

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def run_bot():
    """Run the bot."""
    logger.info("Starting Discord bot with automatic message sync")

    try:
        # Initialize database
        logger.info("Initializing database")
        await db_service.initialize()
        await create_tables()

        if not await db_service.health_check():
            raise RuntimeError("Database health check failed")

        # Initialize Discord service
        logger.info("Initializing Discord service")
        await discord_service.initialize()

        # Start bot (this blocks until bot stops)
        logger.info("Starting bot - will sync recent messages automatically")
        await discord_service.start()

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot failed: {e}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down...")
        await discord_service.stop()
        await db_service.close()
        logger.info("Shutdown complete")


async def main():
    """Main entry point."""
    if not settings.discord_token:
        logger.error("DISCORD_TOKEN not set")
        sys.exit(1)

    if not settings.database_url:
        logger.error("DATABASE_URL not set")
        sys.exit(1)

    await run_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
