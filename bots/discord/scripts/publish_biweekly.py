#!/usr/bin/env python3
"""Publish the bi-weekly newsletter (Oct 4-19) to Buttondown."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from discord_bot.services.buttondown_service import buttondown_service
from discord_bot.core.logging import get_logger
from rich.console import Console

console = Console()
logger = get_logger(__name__)


async def publish_newsletter():
    """Publish the bi-weekly newsletter to Buttondown."""
    console.print("\n" + "="*80, style="cyan")
    console.print("📧 PUBLISHING NEWSLETTER TO BUTTONDOWN", style="bold cyan")
    console.print("="*80 + "\n", style="cyan")

    # Initialize Buttondown service
    console.print("🔄 Initializing Buttondown service...", style="blue")
    await buttondown_service.initialize()

    # Check health
    health = await buttondown_service.health_check()
    console.print(f"Buttondown Status: {health.get('status')}", style="green" if health.get('status') == 'healthy' else "red")
    console.print(f"API Key Configured: {health.get('api_key_configured')}", style="green" if health.get('api_key_configured') else "red")
    console.print(f"Subscriber Count: {health.get('subscriber_count', 'N/A')}", style="blue")
    console.print()

    if health.get('status') != 'healthy':
        console.print(f"❌ Buttondown service is not healthy: {health.get('error', 'Unknown error')}", style="red")
        await buttondown_service.close()
        return

    # Read the generated newsletter
    newsletter_file = "/Users/that1guy15/austin_langchain/bots/discord/newsletter_oct4-19.html"

    try:
        with open(newsletter_file, 'r') as f:
            html_content = f.read()
    except FileNotFoundError:
        console.print(f"❌ Newsletter file not found: {newsletter_file}", style="red")
        await buttondown_service.close()
        return

    console.print(f"✅ Read newsletter from {newsletter_file}", style="green")
    console.print(f"   Content length: {len(html_content)} characters", style="blue")
    console.print()

    # Title for the newsletter
    title = "Austin LangChain Weekly - Week of October 19, 2025"

    # Create newsletter draft
    console.print("📝 Creating draft in Buttondown...", style="blue")

    tags = ["austin-langchain", "bi-weekly", "oct-2025"]
    metadata = {
        "newsletter_type": "bi-weekly",
        "source": "austin-langchain-discord-bot",
        "date_range": "2025-10-04 to 2025-10-19",
        "discussion_count": "10",
        "word_count": "893"
    }

    draft_data = await buttondown_service.create_draft(
        subject=title,
        body=html_content,  # Use HTML content
        tags=tags,
        metadata=metadata
    )

    if not draft_data:
        console.print("❌ Failed to create draft", style="red")
        await buttondown_service.close()
        return

    draft_id = draft_data.get('id')
    console.print(f"✅ Draft created successfully!", style="green")
    console.print(f"   Draft ID: {draft_id}", style="cyan")
    console.print(f"   Subject: {title}", style="cyan")
    console.print()

    # Show draft link
    console.print(f"🔗 Review draft at: https://buttondown.email/emails/{draft_id}", style="blue")
    console.print()

    console.print("="*80, style="cyan")
    console.print("✅ NEWSLETTER PUBLISHED TO BUTTONDOWN AS DRAFT", style="bold green")
    console.print("="*80, style="cyan")
    console.print()
    console.print("Next steps:", style="bold yellow")
    console.print("1. Review the draft in your Buttondown dashboard", style="yellow")
    console.print("2. Make any final edits if needed", style="yellow")
    console.print("3. Click 'Publish' when ready to send to subscribers", style="yellow")

    await buttondown_service.close()


if __name__ == "__main__":
    asyncio.run(publish_newsletter())
