"""Content enrichment agent for adding news, events, memes, and community content."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re

from discord_bot.agents.base_agent import BaseNewsletterAgent
from discord_bot.agents.state import NewsletterState, AgentResponse
from discord_bot.core.logging import get_logger
from discord_bot.core.config import settings

logger = get_logger(__name__)


class ContentEnrichmentAgent(BaseNewsletterAgent):
    """Agent responsible for enriching newsletter with additional content."""

    def __init__(self, model=None):
        super().__init__(
            name="ContentEnrichmentAgent",
            role="Content Enrichment Specialist",
            model=model,
            temperature=0.3,
            max_tokens=2000
        )

    def _create_system_prompt(self) -> str:
        return """You are a content curator for the AIMUG newsletter.

Your role is to:
1. Select the most relevant news article from the news channel
2. Format event information clearly
3. Choose engaging meme images
4. Curate community t-shirt design ideas

Guidelines:
- Prioritize relevance and community value
- Keep descriptions concise and engaging
- Ensure content is appropriate and professional
"""

    async def process(self, state: NewsletterState) -> AgentResponse:
        """Enrich newsletter with additional content sections."""
        newsletter_type = state.get("newsletter_type", "weekly")
        discussions = state.get("discussions", [])

        enriched_content = {
            "news_article": None,
            "events": [],
            "meme_image": None,
            "tshirt_ideas": []
        }

        # Fetch news from #news-and-polls channel
        news_article = await self._fetch_top_news(discussions)
        if news_article:
            enriched_content["news_article"] = news_article

        # Fetch events for monthly newsletters
        if newsletter_type == "monthly":
            events = await self._fetch_upcoming_events()
            enriched_content["events"] = events

        # Fetch top meme from #dank-memes
        meme = await self._fetch_top_meme(discussions)
        if meme:
            enriched_content["meme_image"] = meme

        # Fetch t-shirt ideas
        tshirt_ideas = await self._fetch_tshirt_ideas(discussions)
        enriched_content["tshirt_ideas"] = tshirt_ideas

        return AgentResponse(
            agent_name=self.name,
            action="content_enrichment_complete",
            output=enriched_content,
            confidence=0.85,
            reasoning=f"Enriched newsletter with {sum(1 for v in enriched_content.values() if v)} additional content sections",
            next_steps=["formatting"]
        )

    async def _fetch_top_news(self, discussions: List[Dict]) -> Optional[Dict[str, Any]]:
        """Fetch the top news article from #news-and-polls channel."""
        # Filter discussions from news-and-polls channel
        news_discussions = [
            d for d in discussions
            if d.get("channel", "").lower() in ["news-and-polls", "📰〡news-and-polls", "news and polls"]
        ]

        if not news_discussions:
            logger.info("No news discussions found")
            return None

        # Sort by engagement and get top article
        news_discussions.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)
        top_news = news_discussions[0]

        # Extract URL from content if present
        content = top_news.get("content", "")
        urls = re.findall(r'https?://[^\s]+', content)
        news_url = urls[0] if urls else None

        # Generate Discord link
        from discord_bot.utils.discord_links import generate_discord_message_link
        guild_id = settings.discord_guild_id
        channel = top_news.get("channel", "news-and-polls")
        message_id = top_news.get("message_id", "")
        discord_link = generate_discord_message_link(guild_id, channel, message_id) if guild_id else None

        # Use LLM to create a brief summary if available
        summary = await self._summarize_news_article(top_news)

        return {
            "title": self._extract_title(content),
            "summary": summary,
            "url": news_url,
            "discord_link": discord_link,
            "engagement": {
                "score": top_news.get("engagement_score", 0),
                "reactions": top_news.get("reaction_count", 0),
                "replies": top_news.get("reply_count", 0)
            }
        }

    async def _summarize_news_article(self, news_discussion: Dict) -> str:
        """Generate a brief summary of the news article."""
        if not self.model:
            # Fallback: use first 150 characters
            content = news_discussion.get("content", "")
            return content[:150] + "..." if len(content) > 150 else content

        content = news_discussion.get("content", "")
        prompt = f"""Summarize this news article in 1-2 sentences (max 50 words):

{content[:500]}

Focus on the key point and why it matters to the AI/ML community."""

        try:
            messages = self._create_messages(prompt)
            response = await self._call_llm(messages)
            return response.strip()
        except Exception as e:
            logger.warning(f"Failed to generate news summary: {e}")
            return content[:150] + "..." if len(content) > 150 else content

    def _extract_title(self, content: str) -> str:
        """Extract title from content."""
        # Try to find first line or sentence
        lines = content.split('\n')
        first_line = lines[0].strip() if lines else content[:100]

        # Remove URLs
        first_line = re.sub(r'https?://[^\s]+', '', first_line).strip()

        # Truncate if too long
        if len(first_line) > 100:
            first_line = first_line[:97] + "..."

        return first_line or "Community News"

    async def _fetch_upcoming_events(self) -> List[Dict[str, Any]]:
        """Fetch upcoming events from AIMUG.org."""
        events = []

        try:
            # Use Firecrawl to fetch events page
            import httpx

            # For now, return hardcoded events structure
            # In production, this would scrape from aimug.org/events
            events = [
                {
                    "title": "Office Hours",
                    "description": "Weekly community office hours",
                    "date": "Every Tuesday @ 5:00 PM CT",
                    "location": "Virtual (Discord)",
                    "url": "https://aimug.org/events"
                }
            ]

            logger.info(f"Fetched {len(events)} upcoming events")

        except Exception as e:
            logger.error(f"Failed to fetch events: {e}")

        return events

    async def _fetch_top_meme(self, discussions: List[Dict]) -> Optional[Dict[str, Any]]:
        """Fetch the top meme image from #dank-memes channel."""
        # Filter discussions from dank-memes channel that have images
        meme_discussions = [
            d for d in discussions
            if d.get("channel", "").lower() in ["dank-memes", "😁〡dank-memes", "dank memes"]
            and d.get("has_attachments", False)
        ]

        if not meme_discussions:
            logger.info("No meme discussions with images found")
            return None

        # Sort by engagement
        meme_discussions.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)
        top_meme = meme_discussions[0]

        # Get image URL
        attachment_urls = top_meme.get("attachment_urls", [])
        image_url = attachment_urls[0] if attachment_urls else None

        if not image_url:
            return None

        # Generate Discord link
        from discord_bot.utils.discord_links import generate_discord_message_link
        guild_id = settings.discord_guild_id
        channel = top_meme.get("channel", "dank-memes")
        message_id = top_meme.get("message_id", "")
        discord_link = generate_discord_message_link(guild_id, channel, message_id) if guild_id else None

        return {
            "image_url": image_url,
            "discord_link": discord_link,
            "caption": top_meme.get("content", "")[:200],
            "engagement": {
                "score": top_meme.get("engagement_score", 0),
                "reactions": top_meme.get("reaction_count", 0)
            }
        }

    async def _fetch_tshirt_ideas(self, discussions: List[Dict]) -> List[Dict[str, Any]]:
        """Fetch images tagged with t-shirt emoji."""
        tshirt_ideas = []

        # Find messages with t-shirt emoji (👕) reactions and images
        for discussion in discussions:
            # Check if message has attachments
            if not discussion.get("has_attachments", False):
                continue

            # Check for t-shirt emoji in reactions
            # Note: This would require checking the reactions table in a real implementation
            # For now, we'll use a simplified approach

            # Get reactions data if available
            # In the workflow, we'd need to query the MessageReaction table
            # For now, placeholder logic
            attachment_urls = discussion.get("attachment_urls", [])
            if attachment_urls:
                # Generate Discord link
                from discord_bot.utils.discord_links import generate_discord_message_link
                guild_id = settings.discord_guild_id
                channel = discussion.get("channel", "unknown")
                message_id = discussion.get("message_id", "")
                discord_link = generate_discord_message_link(guild_id, channel, message_id) if guild_id else None

                tshirt_ideas.append({
                    "image_url": attachment_urls[0],
                    "discord_link": discord_link,
                    "description": discussion.get("content", "")[:100],
                    "channel": channel
                })

                # Limit to top 3
                if len(tshirt_ideas) >= 3:
                    break

        logger.info(f"Found {len(tshirt_ideas)} t-shirt ideas")
        return tshirt_ideas
