#!/usr/bin/env python3
"""Recalculate engagement metrics for all existing messages in the database."""

import asyncio
import sys
from datetime import datetime, timezone

from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from discord_bot.core.config import settings
from discord_bot.core.logging import setup_logging, get_logger
from discord_bot.services.database import db_service
from discord_bot.models.discord_models import DiscordMessage, EngagementMetrics, MessageReaction

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def recalculate_engagement():
    """Recalculate engagement metrics for all messages."""
    logger.info("Starting engagement recalculation for all messages")

    try:
        # Initialize database
        logger.info("Initializing database")
        await db_service.initialize()

        if not await db_service.health_check():
            raise RuntimeError("Database health check failed")

        # Get all messages
        async with db_service.get_session() as session:
            result = await session.execute(
                select(DiscordMessage)
                .options(selectinload(DiscordMessage.engagement_metrics))
                .order_by(DiscordMessage.created_at.desc())
            )
            messages = result.scalars().all()

        total = len(messages)
        logger.info(f"Found {total} messages to process")
        print(f"\nRecalculating engagement for {total} messages...")

        updated = 0

        for i, message in enumerate(messages, 1):
            async with db_service.get_session() as session:
                # Get engagement metrics
                metrics_result = await session.execute(
                    select(EngagementMetrics).where(EngagementMetrics.message_id == message.id)
                )
                metrics = metrics_result.scalar_one_or_none()

                if not metrics:
                    continue

                # Count reactions
                reaction_result = await session.execute(
                    select(MessageReaction).where(MessageReaction.message_id == message.id)
                )
                reactions = reaction_result.scalars().all()

                metrics.reaction_count = len(reactions)
                metrics.unique_reactors = len(set(r.user_id for r in reactions))

                # Count replies
                reply_result = await session.execute(
                    select(func.count(DiscordMessage.id))
                    .where(DiscordMessage.parent_message_id == message.message_id)
                )
                metrics.reply_count = reply_result.scalar() or 0

                # Count unique participants
                participant_result = await session.execute(
                    select(func.count(func.distinct(DiscordMessage.author_id)))
                    .where(
                        or_(
                            DiscordMessage.message_id == message.message_id,
                            DiscordMessage.parent_message_id == message.message_id
                        )
                    )
                )
                metrics.discussion_participants = participant_result.scalar() or 1

                # Calculate engagement score
                message_age_hours = (datetime.now(timezone.utc) - message.created_at).total_seconds() / 3600

                # Weight factors
                reply_weight = 0.4
                reaction_weight = 0.2
                participant_weight = 0.3
                recency_weight = 0.1

                # Recency decay
                max_age_hours = 168  # 7 days
                recency_multiplier = max(0.1, 1.0 - (message_age_hours / max_age_hours))

                # Calculate score
                metrics.engagement_score = (
                    (metrics.reply_count * reply_weight) +
                    (metrics.reaction_count * reaction_weight) +
                    (metrics.unique_reactors * 0.1) +
                    (metrics.discussion_participants * participant_weight) +
                    (recency_multiplier * recency_weight * 10)
                )

                await session.commit()
                updated += 1

            if i % 50 == 0:
                print(f"Processed {i}/{total} messages")

        print(f"\n✅ Engagement recalculation completed!")
        print(f"   Total messages: {total}")
        print(f"   Successfully updated: {updated}")

        # Show top messages by engagement score
        print("\n" + "="*80)
        print("TOP 20 MESSAGES BY ENGAGEMENT SCORE")
        print("="*80 + "\n")

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
                .limit(20)
            )
            top_messages = result.all()

        if not top_messages:
            print("No messages with engagement > 0 found.")
        else:
            for i, (msg, metrics) in enumerate(top_messages, 1):
                print(f"{i}. Score: {metrics.engagement_score:.2f} | #{msg.channel.name if msg.channel else 'Unknown'}")
                print(f"   @{msg.author.username if msg.author else 'Unknown'} | {msg.created_at.strftime('%Y-%m-%d')}")
                print(f"   {metrics.reaction_count} reactions, {metrics.reply_count} replies, {metrics.discussion_participants} participants")
                content = (msg.content or "[No content]")[:100]
                print(f"   {content}...")
                print()

    except Exception as e:
        logger.error(f"Failed to recalculate engagement: {e}", exc_info=True)
        raise
    finally:
        await db_service.close()
        logger.info("Database connection closed")


async def main():
    """Main entry point."""
    if not settings.database_url:
        logger.error("DATABASE_URL not set")
        sys.exit(1)

    await recalculate_engagement()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
