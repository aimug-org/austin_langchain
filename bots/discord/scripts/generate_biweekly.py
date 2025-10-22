"""Generate a bi-weekly newsletter for a specific date range."""

import asyncio
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from discord_bot.services.database import db_service
from discord_bot.services.newsletter_service import newsletter_service
from discord_bot.models.newsletter_models import NewsletterType
from rich.console import Console

console = Console()


async def main():
    """Generate bi-weekly newsletter for Oct 4-19."""
    console.print("📰 Generating bi-weekly newsletter for Oct 4-19, 2025", style="blue")

    try:
        # Initialize database
        console.print("🔄 Initializing services...", style="blue")
        await db_service.initialize()

        from discord_bot.services.engagement_service import engagement_service
        from datetime import datetime, timedelta

        # Get discussions from Oct 4-19 (14 days)
        console.print("📊 Fetching discussions from Oct 4-19...", style="blue")

        # Manually fetch discussions for the bi-weekly period
        async with db_service.get_session() as session:
            from sqlalchemy import select
            from discord_bot.models.discord_models import DiscordMessage, DiscordChannel, DiscordUser, EngagementMetrics
            from sqlalchemy.orm import selectinload

            start_date = datetime.fromisoformat("2025-10-04T00:00:00+00:00")
            end_date = datetime.fromisoformat("2025-10-19T23:59:59+00:00")

            result = await session.execute(
                select(DiscordMessage, EngagementMetrics)
                .join(EngagementMetrics)
                .options(
                    selectinload(DiscordMessage.author),
                    selectinload(DiscordMessage.channel)
                )
                .where(DiscordMessage.created_at >= start_date)
                .where(DiscordMessage.created_at <= end_date)
                .where(EngagementMetrics.engagement_score >= 1.0)
                .order_by(EngagementMetrics.engagement_score.desc())
                .limit(30)  # Get top 30 for bi-weekly
            )

            discussions = result.all()
            console.print(f"✅ Found {len(discussions)} discussions with high engagement", style="green")

        if not discussions:
            console.print("❌ No discussions found in date range", style="red")
            return None

        # Convert to DiscussionData format
        from discord_bot.agents.state import DiscussionData
        discussion_data = []
        for msg, metrics in discussions:
            discussion_obj = DiscussionData(
                message_id=msg.message_id,
                content=msg.content,
                author=msg.author.username if msg.author else "Unknown",
                channel=msg.channel.name if msg.channel else "Unknown",
                channel_id=msg.channel.channel_id if msg.channel else "",
                engagement_score=metrics.engagement_score,
                reply_count=metrics.reply_count,
                reaction_count=metrics.reaction_count,
                participants=metrics.discussion_participants,
                keywords=metrics.extracted_keywords or [],
                category=metrics.topic_categories or ["general"],
                created_at=msg.created_at
            )
            discussion_data.append(discussion_obj)

        # Generate newsletter using the workflow directly
        from discord_bot.agents.newsletter_workflow import newsletter_workflow

        target_date = "2025-10-19"
        console.print(f"📅 Target date: {target_date}", style="blue")
        console.print("⏳ Generating newsletter (this may take a few minutes)...", style="yellow")

        workflow_result = await newsletter_workflow.generate_newsletter(
            discussions=discussion_data,
            newsletter_type="weekly",
            target_date=target_date
        )

        if workflow_result:
            console.print("✅ Newsletter generated successfully!", style="green")

            # Extract newsletter draft
            newsletter_draft = workflow_result.get("newsletter_draft")
            formatted_content = workflow_result.get("formatted_content", {})

            console.print(f"DEBUG: workflow_result keys: {list(workflow_result.keys())}", style="dim")
            console.print(f"DEBUG: formatted_content keys: {list(formatted_content.keys())}", style="dim")

            if newsletter_draft:
                console.print(f"\n📰 {newsletter_draft.get('title')}", style="bold cyan")
                console.print(f"📝 Subtitle: {newsletter_draft.get('subtitle')}", style="cyan")
                console.print(f"📊 Word count: {newsletter_draft.get('total_word_count', 0)}", style="blue")
                console.print(f"⏱️  Read time: {newsletter_draft.get('estimated_read_time', 0)} minutes", style="blue")
                console.print(f"📅 Sections: {len(newsletter_draft.get('sections', []))}", style="blue")

            # Save to files
            markdown_content = formatted_content.get("markdown")
            html_content = formatted_content.get("html")

            console.print(f"DEBUG: markdown_content exists: {markdown_content is not None}", style="dim")
            console.print(f"DEBUG: html_content exists: {html_content is not None}", style="dim")

            if markdown_content:
                md_file = "/Users/that1guy15/austin_langchain/bots/discord/newsletter_oct4-19.md"
                with open(md_file, 'w') as f:
                    f.write(markdown_content)
                console.print(f"✅ Markdown saved to: {md_file}", style="green")

            if html_content:
                html_file = "/Users/that1guy15/austin_langchain/bots/discord/newsletter_oct4-19.html"
                with open(html_file, 'w') as f:
                    f.write(html_content)
                console.print(f"✅ HTML saved to: {html_file}", style="green")

            # Display markdown content
            if markdown_content:
                console.print("\n" + "="*80, style="dim")
                console.print("📄 MARKDOWN CONTENT PREVIEW:", style="bold yellow")
                console.print("="*80, style="dim")
                # Show first 100 lines
                lines = markdown_content.split('\n')
                console.print('\n'.join(lines[:100]))
                if len(lines) > 100:
                    console.print(f"\n... ({len(lines) - 100} more lines)")
                console.print("="*80 + "\n", style="dim")

            return workflow_result
        else:
            console.print("❌ Newsletter generation failed", style="red")
            return None

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(main())
