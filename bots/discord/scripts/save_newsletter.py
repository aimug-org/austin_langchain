"""Save the generated newsletter to a file for review."""

import asyncio
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from discord_bot.services.database import db_service
from sqlalchemy import select
from discord_bot.models.newsletter_models import Newsletter
from rich.console import Console

console = Console()


async def main():
    """Save the most recent newsletter to markdown file."""
    try:
        await db_service.initialize()

        async with db_service.get_session() as session:
            # Get the most recent newsletter
            result = await session.execute(
                select(Newsletter)
                .order_by(Newsletter.created_at.desc())
                .limit(1)
            )
            newsletter = result.scalar_one_or_none()

            if not newsletter:
                console.print("❌ No newsletter found in database", style="red")
                return

            console.print(f"📰 Found newsletter: {newsletter.title}", style="green")

            # Save to file
            output_file = "/Users/that1guy15/austin_langchain/bots/discord/newsletter_oct4-19.md"

            # Use the formatted content from the workflow if available
            # Otherwise fall back to the newsletter content_markdown
            content = newsletter.content_markdown

            if content:
                with open(output_file, 'w') as f:
                    f.write(content)
                console.print(f"✅ Newsletter saved to: {output_file}", style="green")
                console.print(f"📊 Word count: {newsletter.word_count}", style="blue")
                console.print(f"⏱️  Read time: {newsletter.estimated_read_time} minutes", style="blue")

                # Also save HTML version
                if newsletter.content_html:
                    html_file = "/Users/that1guy15/austin_langchain/bots/discord/newsletter_oct4-19.html"
                    with open(html_file, 'w') as f:
                        f.write(newsletter.content_html)
                    console.print(f"✅ HTML version saved to: {html_file}", style="green")

            else:
                console.print("❌ Newsletter content is empty", style="red")

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
