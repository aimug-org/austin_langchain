#!/usr/bin/env python3
"""Publish a generated newsletter to Buttondown."""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from discord_bot.services.buttondown_service import buttondown_service
from discord_bot.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def publish_newsletter():
    """Publish the monthly newsletter to Buttondown."""
    print("\n" + "="*80)
    print("PUBLISHING NEWSLETTER TO BUTTONDOWN")
    print("="*80 + "\n")

    # Initialize Buttondown service
    await buttondown_service.initialize()

    # Check health
    health = await buttondown_service.health_check()
    print(f"Buttondown Status: {health.get('status')}")
    print(f"API Key Configured: {health.get('api_key_configured')}")
    print(f"Subscriber Count: {health.get('subscriber_count', 'N/A')}")
    print()

    if health.get('status') != 'healthy':
        print(f"❌ Buttondown service is not healthy: {health.get('error', 'Unknown error')}")
        await buttondown_service.close()
        return

    # Read the generated newsletter markdown
    newsletter_file = "newsletter_monthly_october_2025.md"

    try:
        with open(newsletter_file, 'r') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print(f"❌ Newsletter file not found: {newsletter_file}")
        await buttondown_service.close()
        return

    print(f"✅ Read newsletter from {newsletter_file}")
    print(f"   Content length: {len(markdown_content)} characters")
    print()

    # Extract title from markdown
    lines = markdown_content.split('\n')
    title = lines[0].replace('#', '').strip() if lines else "Austin LangChain Monthly - October 2025"

    # Create newsletter draft
    print("📝 Creating draft in Buttondown...")

    tags = ["austin-langchain", "monthly", "october-2025"]
    metadata = {
        "newsletter_type": "monthly",
        "source": "austin-langchain-discord-bot",
        "generated_at": datetime.now().isoformat(),
        "subscriber_category": "newsletter-monthly",
        "content_source": "discord-community",
        "month": "2025-10"
    }

    # Convert markdown to HTML for email
    # For now, we'll use simple conversion - Buttondown can handle markdown
    # But we'll wrap it in basic HTML structure
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 650px; margin: 0 auto; padding: 20px;">
    {markdown_content.replace('# ', '<h1>').replace('## ', '<h2>').replace('### ', '<h3>')}
</body>
</html>
"""

    draft_data = await buttondown_service.create_draft(
        subject=title,
        body=markdown_content,  # Buttondown handles markdown natively
        tags=tags,
        metadata=metadata
    )

    if not draft_data:
        print("❌ Failed to create draft")
        await buttondown_service.close()
        return

    draft_id = draft_data.get('id')
    print(f"✅ Draft created successfully!")
    print(f"   Draft ID: {draft_id}")
    print(f"   Subject: {title}")
    print()

    # Ask user if they want to publish now or later
    print("Draft created in Buttondown!")
    print()
    print("Options:")
    print("1. Keep as draft (you can review and publish from Buttondown dashboard)")
    print("2. Publish immediately to all subscribers")
    print("3. Schedule for later")
    print()

    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "2":
        print("\n📧 Publishing newsletter...")
        publish_result = await buttondown_service.publish_draft(draft_id)

        if publish_result:
            print("✅ Newsletter published successfully!")
            print(f"   Sent to all subscribers")
        else:
            print("❌ Failed to publish newsletter")

    elif choice == "3":
        scheduled_date = input("Enter publish date/time (YYYY-MM-DD HH:MM): ").strip()
        try:
            scheduled_datetime = datetime.strptime(scheduled_date, "%Y-%m-%d %H:%M")
            print(f"\n📅 Scheduling newsletter for {scheduled_datetime}...")

            publish_result = await buttondown_service.publish_draft(
                draft_id,
                scheduled_time=scheduled_datetime
            )

            if publish_result:
                print(f"✅ Newsletter scheduled for {scheduled_datetime}")
            else:
                print("❌ Failed to schedule newsletter")
        except ValueError:
            print("❌ Invalid date format")

    else:
        print("\n✅ Draft saved! You can review and publish from:")
        print(f"   https://buttondown.email/emails/{draft_id}")

    print()
    print("="*80)
    print("BUTTONDOWN PUBLISHING COMPLETE")
    print("="*80)

    await buttondown_service.close()


if __name__ == "__main__":
    asyncio.run(publish_newsletter())
