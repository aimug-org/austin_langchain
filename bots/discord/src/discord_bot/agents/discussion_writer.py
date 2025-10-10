"""Discussion writer agent for creating detailed discussion summaries."""

from typing import Dict, Any, List
from collections import defaultdict

from discord_bot.agents.base_agent import BaseNewsletterAgent
from discord_bot.agents.state import NewsletterState, AgentResponse
from discord_bot.core.logging import get_logger
from discord_bot.core.config import settings

logger = get_logger(__name__)


class DiscussionWriterAgent(BaseNewsletterAgent):
    """Agent responsible for writing detailed discussion summaries."""

    def __init__(self, model=None):
        super().__init__(
            name="DiscussionWriterAgent",
            role="Technical Discussion Writer",
            model=model,
            temperature=0.4,  # Balance between factual and engaging
            max_tokens=4000
        )

    def _create_system_prompt(self) -> str:
        return """You are a technical writer creating detailed summaries of Discord discussions for the AIMUG (Austin AI/ML User Group) newsletter.

Your role is to:
1. Create engaging, specific summaries of individual discussions
2. Highlight the key technical points, questions, and solutions
3. Include relevant usernames and contributions
4. Reference specific tools, technologies, and projects mentioned
5. Make it easy for readers to understand what was discussed and why it matters

Guidelines:
- Start with a clear topic headline
- Summarize the main technical question or discussion point
- Include specific tool/technology names (e.g., "LangGraph", "SALOON stack", "Ollama")
- Mention key contributors by username
- Highlight actionable insights or resources shared
- Keep each discussion summary to 50-100 words
- Use clear, accessible technical language

Format:
**[Topic Name]**
[Summary of 2-3 sentences covering: what was discussed, key technical details, and main takeaways]
"""

    async def process(self, state: NewsletterState) -> AgentResponse:
        """Generate detailed discussion summaries."""
        discussions = state.get("discussions", [])
        content_analysis = state.get("content_outline", {})

        if not discussions:
            return AgentResponse(
                agent_name=self.name,
                action="skip",
                output=None,
                reasoning="No discussions to write about"
            )

        # Group discussions by topic/category
        grouped_discussions = self._group_discussions_by_topic(discussions)

        # Generate detailed summaries for each discussion
        discussion_summaries = {}
        for group_name, group_discussions in grouped_discussions.items():
            summaries = await self._generate_discussion_summaries(
                group_name,
                group_discussions
            )
            discussion_summaries[group_name] = summaries

        return AgentResponse(
            agent_name=self.name,
            action="discussion_writing_complete",
            output={
                "discussion_summaries": discussion_summaries,
                "grouped_discussions": grouped_discussions,
                "total_discussions_written": sum(len(v) for v in discussion_summaries.values())
            },
            confidence=0.9,
            reasoning=f"Generated summaries for {len(discussions)} discussions across {len(grouped_discussions)} topics",
            next_steps=["editing", "formatting"]
        )

    def _group_discussions_by_topic(self, discussions: List[Dict]) -> Dict[str, List[Dict]]:
        """Group discussions by topic/category and detect cross-channel topics."""
        # First, group by keywords to find cross-channel topics
        keyword_discussions = defaultdict(list)
        for discussion in discussions:
            keywords = discussion.get("keywords", [])
            for keyword in keywords[:3]:  # Use top 3 keywords
                keyword_discussions[keyword.lower()].append(discussion)

        # Find topics that appear in multiple channels
        cross_channel_topics = {}
        for keyword, disc_list in keyword_discussions.items():
            if len(disc_list) >= 2:  # Topic appears in at least 2 discussions
                channels = set(d.get("channel", "unknown") for d in disc_list)
                if len(channels) >= 2:  # Across different channels
                    cross_channel_topics[keyword] = {
                        "discussions": disc_list,
                        "channels": list(channels)
                    }

        # Group remaining discussions by category
        categorized = defaultdict(list)
        categorized["🔥 Trending Topics (Cross-Channel)"] = []

        # Add cross-channel discussions first
        processed_ids = set()
        for keyword, topic_data in cross_channel_topics.items():
            for disc in topic_data["discussions"]:
                disc_id = disc.get("message_id")
                if disc_id not in processed_ids:
                    categorized["🔥 Trending Topics (Cross-Channel)"].append({
                        **disc,
                        "cross_channel_topic": keyword,
                        "appears_in_channels": topic_data["channels"]
                    })
                    processed_ids.add(disc_id)

        # Add remaining discussions by category
        for discussion in discussions:
            disc_id = discussion.get("message_id")
            if disc_id not in processed_ids:
                categories = discussion.get("category", ["general"])
                primary_category = categories[0] if categories else "general"

                # Map to readable section names
                if primary_category == "ai-ml":
                    section = "🤖 AI & Machine Learning"
                elif primary_category == "programming":
                    section = "💻 Development & Tools"
                elif primary_category == "community":
                    section = "👥 Community & Events"
                elif primary_category == "learning":
                    section = "📚 Learning Resources"
                else:
                    section = "💡 Technical Discussions"

                categorized[section].append(discussion)

        # Remove empty sections and sort by engagement
        result = {}
        for section, disc_list in categorized.items():
            if disc_list:
                disc_list.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)
                result[section] = disc_list[:10]  # Top 10 per section

        return result

    async def _generate_discussion_summaries(
        self,
        group_name: str,
        discussions: List[Dict]
    ) -> List[Dict[str, str]]:
        """Generate detailed summaries for a group of discussions."""
        if not self.model:
            return self._create_fallback_summaries(discussions)

        summaries = []

        for disc in discussions:
            try:
                summary = await self._generate_single_discussion_summary(disc, group_name)
                summaries.append(summary)
            except Exception as e:
                logger.warning(f"Failed to generate summary for discussion {disc.get('message_id')}: {e}")
                summaries.append(self._create_fallback_summary(disc))

        return summaries

    async def _generate_single_discussion_summary(
        self,
        discussion: Dict,
        group_name: str
    ) -> Dict[str, str]:
        """Generate a detailed summary for a single discussion."""
        content = discussion.get("content", "")
        keywords = discussion.get("keywords", [])
        channel = discussion.get("channel", "unknown")
        author = discussion.get("author", "Unknown")
        engagement = discussion.get("engagement_score", 0)
        replies = discussion.get("reply_count", 0)
        reactions = discussion.get("reaction_count", 0)
        message_id = discussion.get("message_id", "")

        # Check if cross-channel
        cross_channel_info = ""
        if discussion.get("cross_channel_topic"):
            channels = discussion.get("appears_in_channels", [])
            cross_channel_info = f"\n🌐 Also discussed in: {', '.join(f'#{c}' for c in channels if c != channel)}"

        prompt = f"""
Create a detailed, engaging summary of this Discord discussion for a newsletter.

Discussion Content:
{content[:1000]}

Keywords: {', '.join(keywords)}
Channel: #{channel}
Author: @{author}
Engagement: {engagement:.1f} score, {replies} replies, {reactions} reactions

Write a summary that includes:
1. A clear, specific topic headline (4-8 words)
2. What was discussed (specific technical details, not generic)
3. Key tools/technologies mentioned BY NAME
4. Main insights or questions raised
5. Why this matters to the AIMUG community

Format:
**[Specific Topic Headline]**
[2-3 sentences with specific details - tools, technologies, problems, solutions]

Rules:
- Use ACTUAL tool/technology names from the content
- Include @username for key contributors
- Be specific, not generic
- Focus on actionable insights
- 50-100 words total

Return ONLY the formatted summary, nothing else.
"""

        messages = self._create_messages(prompt)
        response = await self._call_llm(messages)

        # Generate Discord link
        from discord_bot.utils.discord_links import generate_discord_message_link
        guild_id = settings.discord_guild_id
        discord_link = generate_discord_message_link(guild_id, channel, message_id) if guild_id else None

        return {
            "summary": response.strip(),
            "channel": channel,
            "message_id": message_id,
            "discord_link": discord_link,
            "engagement": {
                "score": engagement,
                "replies": replies,
                "reactions": reactions
            },
            "cross_channel_info": cross_channel_info
        }

    def _create_fallback_summary(self, discussion: Dict) -> Dict[str, str]:
        """Create a basic summary without LLM."""
        keywords = discussion.get("keywords", [])
        channel = discussion.get("channel", "unknown")
        author = discussion.get("author", "Unknown")
        content = discussion.get("content", "")[:150]
        message_id = discussion.get("message_id", "")
        engagement = discussion.get("engagement_score", 0)
        replies = discussion.get("reply_count", 0)
        reactions = discussion.get("reaction_count", 0)

        topic = keywords[0].title() if keywords else "Technical Discussion"

        summary = f"**{topic}**\n"
        summary += f"@{author} initiated a discussion about {topic.lower()}. "
        summary += f"The conversation covered {', '.join(keywords[:3])}. "

        from discord_bot.utils.discord_links import generate_discord_message_link
        guild_id = settings.discord_guild_id
        discord_link = generate_discord_message_link(guild_id, channel, message_id) if guild_id else None

        return {
            "summary": summary,
            "channel": channel,
            "message_id": message_id,
            "discord_link": discord_link,
            "engagement": {
                "score": engagement,
                "replies": replies,
                "reactions": reactions
            },
            "cross_channel_info": ""
        }

    def _create_fallback_summaries(self, discussions: List[Dict]) -> List[Dict[str, str]]:
        """Create fallback summaries for all discussions."""
        return [self._create_fallback_summary(d) for d in discussions]
