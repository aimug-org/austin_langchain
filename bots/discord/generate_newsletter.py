#!/usr/bin/env python3
"""Generate a newsletter for a specified timeframe.

Usage:
    python generate_newsletter.py daily
    python generate_newsletter.py weekly
    python generate_newsletter.py biweekly
    python generate_newsletter.py monthly
"""

import asyncio
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Tuple

from discord_bot.core.config import settings
from discord_bot.core.logging import setup_logging, get_logger
from discord_bot.services.database import db_service
from discord_bot.services.newsletter_service import newsletter_service
from discord_bot.services.engagement_service import engagement_service
from discord_bot.services.model_router import model_router
from discord_bot.models.newsletter_models import NewsletterType

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Output directory for generated newsletters
OUTPUT_DIR = Path(__file__).parent / "output"

# Timeframe configurations
TIMEFRAME_CONFIG = {
    "daily": {
        "days": 1,
        "min_score": 0.5,
        "limit": 10,
        "newsletter_type": NewsletterType.DAILY,
        "display_name": "Daily"
    },
    "weekly": {
        "days": 7,
        "min_score": 1.0,
        "limit": 20,
        "newsletter_type": NewsletterType.WEEKLY,
        "display_name": "Weekly"
    },
    "biweekly": {
        "days": 14,
        "min_score": 1.0,
        "limit": 30,
        "newsletter_type": NewsletterType.WEEKLY,  # Use WEEKLY type for bi-weekly
        "display_name": "Bi-Weekly"
    },
    "monthly": {
        "days": 30,
        "min_score": 1.5,
        "limit": 50,
        "newsletter_type": NewsletterType.MONTHLY,
        "display_name": "Monthly"
    }
}


def parse_arguments() -> str:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate AIMUG newsletter for a specified timeframe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s daily      Generate a daily newsletter (past 24 hours)
  %(prog)s weekly     Generate a weekly newsletter (past 7 days)
  %(prog)s biweekly   Generate a bi-weekly newsletter (past 14 days)
  %(prog)s monthly    Generate a monthly newsletter (past 30 days)
        """
    )

    parser.add_argument(
        "timeframe",
        choices=["daily", "weekly", "biweekly", "monthly"],
        help="Timeframe for the newsletter"
    )

    args = parser.parse_args()
    return args.timeframe


async def generate_newsletter(timeframe: str):
    """Generate newsletter for the specified timeframe.

    Args:
        timeframe: One of 'daily', 'weekly', 'biweekly', or 'monthly'
    """
    config = TIMEFRAME_CONFIG[timeframe]
    display_name = config["display_name"]

    logger.info(f"Starting {display_name.lower()} newsletter generation")
    print("\n" + "="*80)
    print(f"GENERATING {display_name.upper()} NEWSLETTER")
    print("="*80 + "\n")

    try:
        # Initialize database
        logger.info("Initializing database")
        await db_service.initialize()

        if not await db_service.health_check():
            raise RuntimeError("Database health check failed")

        # Initialize model router
        logger.info("Initializing model router")
        await model_router.initialize()

        # Get top discussions for the timeframe
        logger.info(f"Fetching top discussions from past {config['days']} days")
        print(f"Fetching discussions from past {config['days']} days...")
        print(f"  Min engagement score: {config['min_score']}")
        print(f"  Limit: {config['limit']} discussions\n")

        discussions = await engagement_service.get_top_discussions(
            days=config["days"],
            min_score=config["min_score"],
            limit=config["limit"]
        )

        logger.info(f"Found {len(discussions)} discussions for {display_name.lower()} newsletter")
        print(f"Found {len(discussions)} discussions\n")

        if not discussions:
            logger.warning("No discussions found for newsletter generation")
            print("❌ No discussions found with sufficient engagement for the timeframe")
            return

        # Print discussion summary
        print("="*80)
        print(f"TOP DISCUSSIONS FROM PAST {config['days']} DAYS")
        print("="*80 + "\n")

        for i, (message, metrics) in enumerate(discussions, 1):
            print(f"{i}. [{message.channel.name}] Score: {metrics.engagement_score:.2f}")
            print(f"   Author: {message.author.username}")
            print(f"   Engagement: {metrics.reply_count} replies, {metrics.reaction_count} reactions, {metrics.discussion_participants} participants")
            print(f"   Content: {message.content[:100]}...")
            print(f"   Created: {message.created_at}")
            if metrics.extracted_keywords:
                print(f"   Keywords: {', '.join(metrics.extracted_keywords[:5])}")
            print()

        # Generate newsletter
        print("\n" + "="*80)
        print(f"GENERATING {display_name.upper()} NEWSLETTER")
        print("="*80 + "\n")

        newsletter = await newsletter_service.generate_newsletter(
            newsletter_type=config["newsletter_type"],
            force=True,
            target_date=datetime.now().strftime("%Y-%m-%d")
        )

        if newsletter:
            print(f"\n✅ Newsletter generated successfully!")
            print(f"   ID: {newsletter.id}")
            print(f"   Title: {newsletter.title}")
            print(f"   Status: {newsletter.status.value}")
            print(f"   Word Count: {newsletter.word_count}")
            print(f"   Sections: {len(newsletter.sections) if newsletter.sections else 0}")
            print(f"   Reading Time: {newsletter.estimated_read_time} min")

            # Save to file
            if newsletter.content_markdown:
                # Create output directory if it doesn't exist
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

                output_file = OUTPUT_DIR / f"newsletter_{timeframe}_{datetime.now().strftime('%Y%m%d')}.md"
                with open(output_file, 'w') as f:
                    f.write(newsletter.content_markdown)
                print(f"\n📄 Newsletter saved to: {output_file}")

            # Display content
            if newsletter.content_markdown:
                print("\n" + "="*80)
                print("NEWSLETTER CONTENT (Markdown)")
                print("="*80 + "\n")
                print(newsletter.content_markdown)
            elif newsletter.content_text:
                print("\n" + "="*80)
                print("NEWSLETTER CONTENT (Text)")
                print("="*80 + "\n")
                print(newsletter.content_text)
        else:
            print("\n❌ Newsletter generation failed")
            logger.error("Newsletter generation returned None")

    except Exception as e:
        logger.error(f"Failed to generate {display_name.lower()} newsletter: {e}", exc_info=True)
        print(f"\n❌ Error generating newsletter: {e}")
        raise
    finally:
        await model_router.close()
        await db_service.close()
        logger.info("Database connection closed")


async def main():
    """Main entry point."""
    if not settings.database_url:
        logger.error("DATABASE_URL not set")
        print("❌ Error: DATABASE_URL not set in environment")
        sys.exit(1)

    timeframe = parse_arguments()
    await generate_newsletter(timeframe)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
        print("\n\n⚠️  Stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed: {e}")
        print(f"\n❌ Failed: {e}")
        sys.exit(1)
