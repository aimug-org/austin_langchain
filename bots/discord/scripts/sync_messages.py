#!/usr/bin/env python3
"""
Script to sync historical messages from Discord.
Runs the bot, syncs messages from the past 2 weeks, then exits.
"""

import asyncio
import sys
from datetime import datetime, timezone, timedelta

from discord_bot.core.config import settings
from discord_bot.core.logging import setup_logging, get_logger
from discord_bot.services.database import db_service, create_tables
from discord_bot.services.discord_service import discord_service

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def sync_historical_messages(days: int = 14):
    """Sync historical messages and exit."""
    logger.info(f"Starting historical message sync for last {days} days")

    try:
        # Initialize database
        logger.info("Initializing database connection")
        await db_service.initialize()

        # Create tables if needed
        await create_tables()

        # Check database health
        if not await db_service.health_check():
            raise RuntimeError("Database health check failed")

        # Initialize Discord service
        logger.info("Initializing Discord service")
        await discord_service.initialize()

        # Start bot connection with a ready event
        logger.info("Connecting to Discord...")

        # Create ready event in the service
        discord_service._ready_event = asyncio.Event()

        # Start bot in background task
        bot_task = asyncio.create_task(discord_service.bot.start(settings.discord_token))

        # Wait for ready event with timeout
        try:
            await asyncio.wait_for(discord_service._ready_event.wait(), timeout=60.0)
            logger.info(f"Bot connected as: {discord_service.bot.user}")
        except asyncio.TimeoutError:
            bot_task.cancel()
            raise RuntimeError("Bot failed to connect within 60 seconds")

        # Guild sync already happens in on_ready, so we can proceed directly to message sync

        # Sync messages from the past N days
        hours = days * 24
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)

        logger.info(f"Syncing messages since {cutoff_time}")

        message_count = 0
        channel_count = 0

        for guild in discord_service.bot.guilds:
            logger.info(f"Processing guild: {guild.name}")

            for channel in guild.text_channels:
                # Skip if not monitored
                if not discord_service._monitor_all_channels and str(channel.id) not in discord_service._monitored_channels:
                    continue

                try:
                    channel_messages = 0
                    logger.info(f"  Syncing #{channel.name}...")

                    async for message in channel.history(after=cutoff_time, limit=None):
                        await discord_service.process_message(message, is_historical=True)
                        message_count += 1
                        channel_messages += 1

                        # Rate limiting
                        if message_count % 100 == 0:
                            logger.info(f"    Processed {message_count} total messages so far...")
                            await asyncio.sleep(1)

                    if channel_messages > 0:
                        logger.info(f"    ✅ Synced {channel_messages} messages from #{channel.name}")
                        channel_count += 1

                except Exception as e:
                    logger.error(f"    ❌ Error syncing #{channel.name}: {e}")

        logger.info(f"\n📊 Sync Summary:")
        logger.info(f"   Channels processed: {channel_count}")
        logger.info(f"   Total messages synced: {message_count}")
        logger.info(f"   Time period: Last {days} days")

    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        raise

    finally:
        # Cleanup
        logger.info("Shutting down...")

        # Cancel bot task if it exists
        if 'bot_task' in locals() and not bot_task.done():
            bot_task.cancel()
            try:
                await bot_task
            except asyncio.CancelledError:
                pass

        if discord_service.bot and not discord_service.bot.is_closed():
            await discord_service.bot.close()

        await db_service.close()
        logger.info("Shutdown complete")


async def main():
    """Main entry point."""
    if not settings.discord_token:
        logger.error("DISCORD_TOKEN not set in environment")
        sys.exit(1)

    if not settings.database_url:
        logger.error("DATABASE_URL not set in environment")
        sys.exit(1)

    # Default to 14 days (2 weeks)
    days = 14
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid days argument: {sys.argv[1]}")
            sys.exit(1)

    await sync_historical_messages(days=days)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Sync interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        sys.exit(1)
