"""Integration tests for newsletter generation workflow."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from discord_bot.agents.newsletter_workflow import newsletter_workflow
from discord_bot.agents.state import DiscussionData


@pytest.fixture
def sample_discussions_for_newsletter():
    """Sample discussions for integration testing."""
    return [
        DiscussionData(
            message_id="1234567890",
            content="I've been working on implementing the SALOON stack (Sqlite, Astro, Langgraph, Ollama, OpenAI, NixOS) for a self-hosted AI knowledge system. The key challenge is managing state across LangGraph agents while keeping everything local.",
            author="colinmcnamara",
            channel="technical-discussions",
            engagement_score=3.5,
            reply_count=15,
            reaction_count=23,
            participants=8,
            keywords=["saloon", "langgraph", "self-hosted", "ai"],
            category=["ai-ml"],
            created_at=datetime(2025, 9, 15, 10, 30, tzinfo=timezone.utc)
        ),
        DiscussionData(
            message_id="1234567891",
            content="Has anyone integrated Cursor with Slack for AI-assisted development? I built a bot that shares code snippets and suggestions directly in Slack channels.",
            author="josephflu",
            channel="showcase",
            engagement_score=2.8,
            reply_count=8,
            reaction_count=12,
            participants=5,
            keywords=["cursor", "slack", "integration", "ai-development"],
            category=["programming"],
            created_at=datetime(2025, 9, 16, 14, 15, tzinfo=timezone.utc)
        ),
        DiscussionData(
            message_id="1234567892",
            content="Question about LangGraph: how do you handle error recovery in multi-agent workflows? My agents keep failing when external APIs are down.",
            author="developer123",
            channel="help",
            engagement_score=2.5,
            reply_count=10,
            reaction_count=8,
            participants=6,
            keywords=["langgraph", "error-handling", "multi-agent"],
            category=["ai-ml"],
            created_at=datetime(2025, 9, 17, 9, 0, tzinfo=timezone.utc)
        )
    ]


class TestNewsletterIntegration:
    """Integration tests for the full newsletter generation workflow."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_generates_newsletter_with_discussion_summaries(self, sample_discussions_for_newsletter):
        """Test that the workflow generates a newsletter with detailed discussion summaries."""
        # This is an integration test - it will actually call LLMs if configured
        # For CI/CD, this test should be skipped or mocked

        result = await newsletter_workflow.generate_newsletter(
            discussions=sample_discussions_for_newsletter,
            newsletter_type="weekly",
            target_date="2025-09-20"
        )

        # Verify workflow completed
        assert result["current_step"] == "quality_check"
        assert len(result["errors"]) == 0

        # Verify discussion summaries were generated
        assert "discussion_summaries" in result
        assert len(result["discussion_summaries"]) > 0

        # Verify sections contain actual content
        assert "draft_sections" in result
        assert len(result["draft_sections"]) > 0

        for section in result["draft_sections"]:
            assert section["content"]
            assert len(section["content"]) > 50  # Should have substantial content
            assert section["word_count"] > 0

        # Verify newsletter draft was created
        assert result["newsletter_draft"] is not None

        # Verify formatted content
        assert "formatted_content" in result
        assert result["formatted_content"]["markdown"]
        assert len(result["formatted_content"]["markdown"]) > 500  # Should be substantial

    @pytest.mark.asyncio
    async def test_discussion_summaries_include_discord_links(self, sample_discussions_for_newsletter):
        """Test that discussion summaries include Discord links."""
        with patch('discord_bot.core.config.settings.discord_guild_id', '123456789'):
            result = await newsletter_workflow.generate_newsletter(
                discussions=sample_discussions_for_newsletter,
                newsletter_type="weekly",
                target_date="2025-09-20"
            )

            # Check that discussion summaries have Discord links
            for section_summaries in result["discussion_summaries"].values():
                for summary in section_summaries:
                    assert "discord_link" in summary
                    if summary["discord_link"]:
                        assert "discord.com/channels/" in summary["discord_link"]

    @pytest.mark.asyncio
    async def test_cross_channel_topics_detected(self):
        """Test that cross-channel topics are properly detected."""
        # Create discussions with same keyword in different channels
        cross_channel_discussions = [
            DiscussionData(
                message_id="001",
                content="LangGraph agents are powerful for building AI systems",
                channel="technical-discussions",
                keywords=["langgraph", "agents", "ai"],
                category=["ai-ml"],
                engagement_score=3.0,
                reply_count=5,
                reaction_count=10,
                author="user1",
                participants=4,
                created_at=datetime.now(timezone.utc)
            ),
            DiscussionData(
                message_id="002",
                content="Help! How do I set up LangGraph for the first time?",
                channel="help",
                keywords=["langgraph", "setup", "beginner"],
                category=["ai-ml"],
                engagement_score=2.5,
                reply_count=3,
                reaction_count=5,
                author="user2",
                participants=3,
                created_at=datetime.now(timezone.utc)
            ),
            DiscussionData(
                message_id="003",
                content="Check out my LangGraph project for document processing",
                channel="showcase",
                keywords=["langgraph", "project", "documents"],
                category=["ai-ml"],
                engagement_score=2.8,
                reply_count=4,
                reaction_count=8,
                author="user3",
                participants=5,
                created_at=datetime.now(timezone.utc)
            )
        ]

        result = await newsletter_workflow.generate_newsletter(
            discussions=cross_channel_discussions,
            newsletter_type="weekly",
            target_date="2025-09-20"
        )

        # Check that cross-channel section exists
        grouped = result.get("grouped_discussions", {})
        assert any("Cross-Channel" in section for section in grouped.keys())

    @pytest.mark.asyncio
    async def test_newsletter_markdown_contains_required_elements(self, sample_discussions_for_newsletter):
        """Test that generated markdown contains all required elements."""
        result = await newsletter_workflow.generate_newsletter(
            discussions=sample_discussions_for_newsletter,
            newsletter_type="weekly",
            target_date="2025-09-20"
        )

        markdown = result["formatted_content"]["markdown"]

        # Should have title
        assert "# AIMUG" in markdown or "# Austin" in markdown

        # Should have reading time
        assert "Reading time" in markdown or "reading time" in markdown

        # Should have section headers
        assert "##" in markdown

        # Should have channel information
        assert "#" in markdown  # Channel names like #technical-discussions

        # Should have engagement metrics
        assert "replies" in markdown.lower() or "reactions" in markdown.lower()

        # Should have community links
        assert "aimug.org" in markdown.lower()

    @pytest.mark.asyncio
    async def test_workflow_handles_empty_discussions(self):
        """Test workflow handles empty discussion list gracefully."""
        result = await newsletter_workflow.generate_newsletter(
            discussions=[],
            newsletter_type="weekly",
            target_date="2025-09-20"
        )

        # Should complete without crashing
        assert result is not None
        assert "errors" in result

    @pytest.mark.asyncio
    async def test_workflow_populates_all_state_fields(self, sample_discussions_for_newsletter):
        """Test that workflow populates all expected state fields."""
        result = await newsletter_workflow.generate_newsletter(
            discussions=sample_discussions_for_newsletter,
            newsletter_type="monthly",
            target_date="2025-09-01"
        )

        # Verify all expected fields are present
        expected_fields = [
            "newsletter_type",
            "target_date",
            "discussions",
            "research_topics",
            "content_outline",
            "draft_sections",
            "discussion_summaries",  # NEW
            "grouped_discussions",  # NEW
            "newsletter_draft",
            "quality_metrics",
            "current_step",
            "errors",
            "warnings"
        ]

        for field in expected_fields:
            assert field in result, f"Missing field: {field}"
