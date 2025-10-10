#!/usr/bin/env python3
"""Show top messages from the past 7 days to review for newsletter generation."""

import asyncio
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from discord_bot.core.config import settings
from discord_bot.core.logging import setup_logging, get_logger
from discord_bot.services.database import db_service
from discord_bot.models.discord_models import DiscordMessage, DiscordChannel, DiscordUser, EngagementMetrics

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def show_top_messages():
    """Show top messages from past 7 days."""
    logger.info("Fetching top messages from past 7 days")

    try:
        # Initialize database
        await db_service.initialize()

        if not await db_service.health_check():
            raise RuntimeError("Database health check failed")

        # Get messages from past 7 days with engagement metrics
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)

        async with db_service.get_session() as session:
            # Get top messages by reaction + reply count
            result = await session.execute(
                select(DiscordMessage, EngagementMetrics)
                .join(EngagementMetrics)
                .options(
                    selectinload(DiscordMessage.author),
                    selectinload(DiscordMessage.channel)
                )
                .where(DiscordMessage.created_at >= cutoff_date)
                .order_by(
                    desc(EngagementMetrics.reaction_count + EngagementMetrics.reply_count)
                )
                .limit(20)
            )

            messages = result.all()

        print("\n" + "="*80)
        print(f"TOP 20 MESSAGES FROM PAST 7 DAYS")
        print(f"Date Range: {cutoff_date.strftime('%Y-%m-%d %H:%M')} - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}")
        print("="*80 + "\n")

        if not messages:
            print("No messages found in the past 7 days.")
            return

        for i, (message, metrics) in enumerate(messages, 1):
            print(f"\n{i}. Channel: #{message.channel.name if message.channel else 'Unknown'}")
            print(f"   Author: @{message.author.username if message.author else 'Unknown'}")
            print(f"   Created: {message.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"   Engagement: {metrics.reaction_count} reactions, {metrics.reply_count} replies, {metrics.discussion_participants} participants")

            # Show content (truncated)
            content = message.content or "[No text content]"
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"   Content: {content}")

            if metrics.extracted_keywords:
                print(f"   Keywords: {', '.join(metrics.extracted_keywords[:5])}")

            print(f"   Message ID: {message.message_id}")
            print(f"   Score: {metrics.engagement_score}")

        # Show channel breakdown
        print("\n" + "="*80)
        print("CHANNEL BREAKDOWN")
        print("="*80 + "\n")

        async with db_service.get_session() as session:
            channel_stats = await session.execute(
                select(
                    DiscordChannel.name,
                    func.count(DiscordMessage.id).label('msg_count'),
                    func.sum(EngagementMetrics.reaction_count).label('total_reactions'),
                    func.sum(EngagementMetrics.reply_count).label('total_replies')
                )
                .join(DiscordMessage, DiscordChannel.id == DiscordMessage.channel_id)
                .join(EngagementMetrics, DiscordMessage.id == EngagementMetrics.message_id)
                .where(DiscordMessage.created_at >= cutoff_date)
                .group_by(DiscordChannel.name)
                .order_by(desc('total_reactions'))
            )

            channels = channel_stats.all()

        for channel_name, msg_count, reactions, replies in channels:
            print(f"#{channel_name:30} {msg_count:3} msgs, {reactions or 0:3} reactions, {replies or 0:3} replies")

    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        raise
    finally:
        await db_service.close()


async def main():
    """Main entry point."""
    if not settings.database_url:
        logger.error("DATABASE_URL not set")
        sys.exit(1)

    await show_top_messages()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
