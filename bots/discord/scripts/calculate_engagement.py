#!/usr/bin/env python3
"""Calculate engagement metrics for all messages in the database."""

import asyncio
import sys
from datetime import datetime, timezone

from discord_bot.core.config import settings
from discord_bot.core.logging import setup_logging, get_logger
from discord_bot.services.database import db_service
from discord_bot.services.discord_service import discord_service
from discord_bot.services.engagement_service import engagement_service

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def calculate_all_engagement():
    """Calculate engagement metrics for all messages."""
    logger.info("Starting engagement calculation for all messages")

    try:
        # Initialize database
        logger.info("Initializing database")
        await db_service.initialize()

        if not await db_service.health_check():
            raise RuntimeError("Database health check failed")

        # Initialize Discord service
        logger.info("Initializing Discord service")
        await discord_service.initialize()

        # Start bot to get Discord API access
        logger.info("Starting Discord bot")

        # Create bot startup task
        bot_task = asyncio.create_task(discord_service.start())

        # Wait for bot to be ready (with timeout)
        try:
            await asyncio.wait_for(discord_service._ready_event.wait(), timeout=30)
            logger.info("Discord bot is ready")
        except asyncio.TimeoutError:
            logger.error("Discord bot failed to start within 30 seconds")
            bot_task.cancel()
            return

        # Get all messages that need engagement updates
        from discord_bot.models.discord_models import DiscordMessage, EngagementMetrics
        from sqlalchemy import select

        async with db_service.get_session() as session:
            result = await session.execute(
                select(DiscordMessage)
                .order_by(DiscordMessage.created_at.desc())
            )
            messages = result.scalars().all()

        total = len(messages)
        logger.info(f"Found {total} messages to process")
        print(f"\nProcessing {total} messages...")

        updated = 0
        errors = 0

        for i, message in enumerate(messages, 1):
            try:
                # Update engagement metrics for this message
                score = await engagement_service.update_message_engagement(message.message_id)

                if score is not None:
                    updated += 1

                if i % 50 == 0:
                    print(f"Processed {i}/{total} messages ({updated} updated, {errors} errors)")
                    logger.info(f"Progress: {i}/{total} messages processed")

            except Exception as e:
                errors += 1
                logger.error(f"Error processing message {message.message_id}: {e}")

        print(f"\n✅ Engagement calculation completed!")
        print(f"   Total messages: {total}")
        print(f"   Successfully updated: {updated}")
        print(f"   Errors: {errors}")

        # Show top messages by engagement score
        print("\n" + "="*80)
        print("TOP 10 MESSAGES BY ENGAGEMENT SCORE")
        print("="*80 + "\n")

        from sqlalchemy.orm import selectinload

        async with db_service.get_session() as session:
            result = await session.execute(
                select(DiscordMessage, EngagementMetrics)
                .join(EngagementMetrics)
                .options(
                    selectinload(DiscordMessage.author),
                    selectinload(DiscordMessage.channel)
                )
                .where(EngagementMetrics.engagement_score > 0)
                .order_by(EngagementMetrics.engagement_score.desc())
                .limit(10)
            )
            top_messages = result.all()

        for i, (msg, metrics) in enumerate(top_messages, 1):
            print(f"{i}. Score: {metrics.engagement_score:.2f} | #{msg.channel.name if msg.channel else 'Unknown'}")
            print(f"   By: @{msg.author.username if msg.author else 'Unknown'}")
            print(f"   Engagement: {metrics.reaction_count} reactions, {metrics.reply_count} replies, {metrics.discussion_participants} participants")
            content = (msg.content or "[No content]")[:100]
            print(f"   Content: {content}...")
            print()

        # Stop the bot
        logger.info("Stopping Discord bot")
        await discord_service.stop()
        bot_task.cancel()

        try:
            await bot_task
        except asyncio.CancelledError:
            pass

    except Exception as e:
        logger.error(f"Failed to calculate engagement: {e}", exc_info=True)
        raise
    finally:
        await db_service.close()
        logger.info("Database connection closed")


async def main():
    """Main entry point."""
    if not settings.discord_token:
        logger.error("DISCORD_TOKEN not set")
        sys.exit(1)

    if not settings.database_url:
        logger.error("DATABASE_URL not set")
        sys.exit(1)

    await calculate_all_engagement()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
