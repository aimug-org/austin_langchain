#!/usr/bin/env python3
"""Publish a generated newsletter to Buttondown as DRAFT ONLY (no sending)."""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from discord_bot.services.buttondown_service import buttondown_service
from discord_bot.services.database import db_service
from discord_bot.models.newsletter_models import Newsletter
from discord_bot.core.logging import setup_logging, get_logger
from sqlalchemy import select, desc

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def publish_newsletter_as_draft():
    """Publish the most recent newsletter to Buttondown as a DRAFT ONLY."""
    print("\n" + "="*80)
    print("PUBLISHING NEWSLETTER TO BUTTONDOWN (DRAFT ONLY)")
    print("="*80 + "\n")

    try:
        # Initialize services
        await db_service.initialize()
        await buttondown_service.initialize()

        # Check Buttondown health
        health = await buttondown_service.health_check()
        print(f"Buttondown Status: {health.get('status')}")
        print(f"API Key Configured: {health.get('api_key_configured')}")
        print(f"Subscriber Count: {health.get('subscriber_count', 'N/A')}")
        print()

        if health.get('status') != 'healthy':
            print(f"❌ Buttondown service is not healthy: {health.get('error', 'Unknown error')}")
            return False

        # Get the most recent monthly newsletter from database
        async with db_service.get_session() as session:
            result = await session.execute(
                select(Newsletter)
                .where(Newsletter.newsletter_type == 'MONTHLY')
                .where(Newsletter.status == 'GENERATED')
                .order_by(desc(Newsletter.created_at))
                .limit(1)
            )
            newsletter = result.scalar_one_or_none()

        if not newsletter:
            print("❌ No generated monthly newsletter found in database")
            return False

        print(f"✅ Found newsletter: {newsletter.title}")
        print(f"   ID: {newsletter.id}")
        print(f"   Status: {newsletter.status.value}")
        print(f"   Word Count: {newsletter.word_count}")
        print(f"   Created: {newsletter.created_at}")
        print()

        # Check if already published to Buttondown
        if newsletter.buttondown_draft_id:
            print(f"⚠️  Newsletter already has Buttondown draft ID: {newsletter.buttondown_draft_id}")
            print(f"   Draft URL: https://buttondown.email/emails/{newsletter.buttondown_draft_id}")

            choice = input("\nCreate a new draft anyway? (y/N): ").strip().lower()
            if choice != 'y':
                print("Cancelled.")
                return True

        # Use markdown content for Buttondown (it handles markdown natively)
        if not newsletter.content_markdown:
            print("❌ Newsletter has no markdown content")
            return False

        markdown_content = newsletter.content_markdown
        print(f"✅ Using markdown content ({len(markdown_content)} characters)")
        print()

        # Extract metadata
        newsletter_date = newsletter.scheduled_for or newsletter.created_at
        month_year = newsletter_date.strftime("%Y-%m")

        tags = ["aimug", "monthly", f"month-{month_year}"]
        metadata = {
            "newsletter_id": str(newsletter.id),
            "newsletter_type": newsletter.newsletter_type.value,
            "source": "aimug-discord-bot",
            "generated_at": newsletter.generated_at.isoformat() if newsletter.generated_at else None,
            "word_count": newsletter.word_count,
            "month": month_year
        }

        # Create draft in Buttondown
        print("📝 Creating draft in Buttondown...")
        print("   ⚠️  THIS WILL CREATE A DRAFT ONLY - NO EMAIL WILL BE SENT")
        print()

        draft_data = await buttondown_service.create_draft(
            subject=newsletter.title,
            body=markdown_content,
            tags=tags,
            metadata=metadata
        )

        if not draft_data:
            print("❌ Failed to create draft in Buttondown")
            return False

        draft_id = draft_data.get('id')
        print(f"✅ Draft created successfully in Buttondown!")
        print(f"   Draft ID: {draft_id}")
        print(f"   Subject: {newsletter.title}")
        print(f"   Tags: {', '.join(tags)}")
        print()

        # Update newsletter record with Buttondown draft ID
        async with db_service.get_session() as session:
            result = await session.execute(
                select(Newsletter).where(Newsletter.id == newsletter.id)
            )
            nl = result.scalar_one()
            nl.buttondown_draft_id = draft_id
            await session.commit()

        print(f"✅ Updated newsletter record with draft ID")
        print()
        print("="*80)
        print("DRAFT CREATION COMPLETE")
        print("="*80)
        print()
        print(f"📝 Review and publish the draft at:")
        print(f"   https://buttondown.email/emails/{draft_id}")
        print()
        print("⚠️  IMPORTANT: The draft is NOT published. You must manually")
        print("   publish it from the Buttondown dashboard when ready.")
        print()

        return True

    except Exception as e:
        logger.error(f"Failed to publish newsletter: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return False

    finally:
        await buttondown_service.close()
        await db_service.close()


async def main():
    """Main entry point."""
    success = await publish_newsletter_as_draft()
    sys.exit(0 if success else 1)


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
