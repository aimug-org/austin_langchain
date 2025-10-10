#!/usr/bin/env python3
"""Test the newsletter workflow directly."""

import asyncio
import json
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Set LangSmith environment variables explicitly for tracing
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "AIMUG-discord-bot")

from discord_bot.agents.newsletter_workflow import newsletter_workflow
from discord_bot.agents.state import DiscussionData
from discord_bot.core.logging import setup_logging, get_logger
from discord_bot.services.database import db_service
from discord_bot.services.engagement_service import engagement_service

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def test_workflow():
    """Test newsletter workflow."""
    print("\n" + "="*80)
    print("TESTING NEWSLETTER WORKFLOW")
    print("="*80 + "\n")

    # Verify LangSmith configuration
    print("LangSmith Configuration:")
    print(f"  Tracing Enabled: {os.getenv('LANGCHAIN_TRACING_V2')}")
    print(f"  API Key Set: {'Yes' if os.getenv('LANGCHAIN_API_KEY') else 'No'}")
    print(f"  Project: {os.getenv('LANGCHAIN_PROJECT')}")
    print()

    # Initialize database
    await db_service.initialize()

    # Get discussions
    discussions = await engagement_service.get_top_discussions(
        days=7,
        min_score=1.0,
        limit=5  # Just test with 5
    )

    print(f"Found {len(discussions)} discussions for testing\n")

    # Convert to DiscussionData
    discussion_data = []
    for d in discussions[:3]:  # Use only 3 for faster testing
        msg, metrics = d
        discussion_obj = DiscussionData(
            message_id=msg.message_id,
            content=msg.content[:200] if msg.content else "",  # Truncate for testing
            author=msg.author.username if msg.author else "Unknown",
            channel=msg.channel.name if msg.channel else "Unknown",
            engagement_score=metrics.engagement_score,
            reply_count=metrics.reply_count,
            reaction_count=metrics.reaction_count,
            participants=metrics.discussion_participants,
            keywords=metrics.extracted_keywords or [],
            category=metrics.topic_categories or ["general"],
            created_at=msg.created_at
        )
        discussion_data.append(discussion_obj)
        print(f"Discussion: {discussion_obj.author} in #{discussion_obj.channel}")
        print(f"  Score: {discussion_obj.engagement_score}")
        print(f"  Content: {discussion_obj.content[:80]}...\n")

    print("\nRunning workflow...\n")

    # Run workflow
    result = await newsletter_workflow.generate_newsletter(
        discussions=discussion_data,
        newsletter_type="weekly",
        target_date=datetime.now().strftime("%Y-%m-%d")
    )

    print("\n" + "="*80)
    print("WORKFLOW RESULT")
    print("="*80 + "\n")

    print(f"Current Step: {result.get('current_step')}")
    print(f"Iteration Count: {result.get('iteration_count')}")
    print(f"Errors: {result.get('errors')}")
    print(f"Warnings: {result.get('warnings')}")
    print()

    print(f"Draft Sections Count: {len(result.get('draft_sections', []))}")
    for i, section in enumerate(result.get('draft_sections', []), 1):
        print(f"\nSection {i}:")
        print(f"  Type: {section.get('section_type')}")
        print(f"  Title: {section.get('title')}")
        print(f"  Content Length: {len(section.get('content', ''))}")
        print(f"  Content Preview: {section.get('content', '')[:150]}...")

    print(f"\n\nNewsletter Draft: {result.get('newsletter_draft') is not None}")
    if result.get('newsletter_draft'):
        draft = result.get('newsletter_draft')
        print(f"  Title: {draft.get('title')}")
        print(f"  Word Count: {draft.get('total_word_count')}")
        print(f"  Sections: {len(draft.get('sections', []))}")

    print(f"\n\nFormatted Content Keys: {list(result.get('formatted_content', {}).keys())}")
    if result.get('formatted_content', {}).get('markdown'):
        markdown = result['formatted_content']['markdown']
        print(f"Markdown Content Length: {len(markdown)}")
        print(f"Markdown Preview:\n{markdown[:500]}...")

    print(f"\n\nQuality Metrics: {result.get('quality_metrics')}")

    await db_service.close()


if __name__ == "__main__":
    asyncio.run(test_workflow())
