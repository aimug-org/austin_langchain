"""Tests for DiscussionWriterAgent."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from discord_bot.agents.discussion_writer import DiscussionWriterAgent
from discord_bot.agents.state import NewsletterState, AgentResponse


@pytest.fixture
def sample_discussions():
    """Sample discussions for testing."""
    return [
        {
            "message_id": "1234567890",
            "content": "I've been working on implementing the SALOON stack (Sqlite, Astro, Langgraph, Ollama, OpenAI, NixOS) for a self-hosted AI knowledge system. The key challenge is managing state across LangGraph agents while keeping everything local.",
            "author": "colinmcnamara",
            "channel": "technical-discussions",
            "engagement_score": 3.5,
            "reply_count": 15,
            "reaction_count": 23,
            "participants": 8,
            "keywords": ["saloon", "langgraph", "self-hosted", "ai"],
            "category": ["ai-ml"],
            "created_at": datetime(2025, 9, 15, 10, 30, tzinfo=timezone.utc)
        },
        {
            "message_id": "1234567891",
            "content": "Has anyone integrated Cursor with Slack for AI-assisted development? I built a bot that shares code snippets and suggestions directly in Slack channels.",
            "author": "josephflu",
            "channel": "showcase",
            "engagement_score": 2.8,
            "reply_count": 8,
            "reaction_count": 12,
            "participants": 5,
            "keywords": ["cursor", "slack", "integration", "ai-development"],
            "category": ["programming"],
            "created_at": datetime(2025, 9, 16, 14, 15, tzinfo=timezone.utc)
        },
        {
            "message_id": "1234567892",
            "content": "Question about LangGraph: how do you handle error recovery in multi-agent workflows? My agents keep failing when external APIs are down.",
            "author": "developer123",
            "channel": "help",
            "engagement_score": 2.5,
            "reply_count": 10,
            "reaction_count": 8,
            "participants": 6,
            "keywords": ["langgraph", "error-handling", "multi-agent"],
            "category": ["ai-ml"],
            "created_at": datetime(2025, 9, 17, 9, 0, tzinfo=timezone.utc)
        }
    ]


@pytest.fixture
def discussion_writer_agent():
    """Create DiscussionWriterAgent instance."""
    mock_model = AsyncMock()
    mock_model.ainvoke = AsyncMock(return_value=Mock(content="**SALOON Stack for Self-Hosted AI**\n@colinmcnamara shared implementation details for the SALOON stack (Sqlite, Astro, Langgraph, Ollama, OpenAI, NixOS) for building self-hosted AI knowledge systems. The discussion focused on managing state across LangGraph agents while maintaining local deployment."))

    agent = DiscussionWriterAgent(model=mock_model)
    return agent


class TestDiscussionWriterAgent:
    """Test suite for DiscussionWriterAgent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = DiscussionWriterAgent()

        assert agent.name == "DiscussionWriterAgent"
        assert agent.role == "Technical Discussion Writer"
        assert agent.temperature == 0.4
        assert agent.max_tokens == 4000

    @pytest.mark.asyncio
    async def test_process_with_no_discussions(self, discussion_writer_agent):
        """Test process returns skip when no discussions."""
        state: NewsletterState = {
            "discussions": [],
            "newsletter_type": "weekly",
            "target_date": "2025-09-20",
            "research_topics": [],
            "research_results": [],
            "fact_check_results": {},
            "content_outline": {},
            "draft_sections": [],
            "technical_analysis": {},
            "writer_feedback": [],
            "newsletter_draft": None,
            "quality_metrics": {},
            "current_step": "discussion_writing",
            "iteration_count": 0,
            "errors": [],
            "warnings": [],
            "selected_models": {},
            "model_costs": {}
        }

        response = await discussion_writer_agent.process(state)

        assert response.action == "skip"
        assert response.output is None

    @pytest.mark.asyncio
    async def test_process_generates_discussion_summaries(self, discussion_writer_agent, sample_discussions):
        """Test that process generates discussion summaries."""
        state: NewsletterState = {
            "discussions": sample_discussions,
            "newsletter_type": "weekly",
            "target_date": "2025-09-20",
            "content_outline": {},
            "research_topics": [],
            "research_results": [],
            "fact_check_results": {},
            "draft_sections": [],
            "technical_analysis": {},
            "writer_feedback": [],
            "newsletter_draft": None,
            "quality_metrics": {},
            "current_step": "discussion_writing",
            "iteration_count": 0,
            "errors": [],
            "warnings": [],
            "selected_models": {},
            "model_costs": {}
        }

        response = await discussion_writer_agent.process(state)

        assert response.action == "discussion_writing_complete"
        assert response.output is not None
        assert "discussion_summaries" in response.output
        assert "grouped_discussions" in response.output
        assert response.output["total_discussions_written"] > 0

    @pytest.mark.asyncio
    async def test_group_discussions_by_topic(self, discussion_writer_agent, sample_discussions):
        """Test discussions are grouped correctly by topic."""
        grouped = discussion_writer_agent._group_discussions_by_topic(sample_discussions)

        # Should have at least one section
        assert len(grouped) > 0

        # Check that discussions are in sections
        total_discussions = sum(len(discussions) for discussions in grouped.values())
        assert total_discussions == len(sample_discussions)

    @pytest.mark.asyncio
    async def test_detect_cross_channel_topics(self, discussion_writer_agent):
        """Test detection of topics discussed across multiple channels."""
        # Create discussions with same keyword in different channels
        cross_channel_discussions = [
            {
                "message_id": "001",
                "content": "LangGraph agents are powerful",
                "channel": "technical-discussions",
                "keywords": ["langgraph", "agents"],
                "category": ["ai-ml"],
                "engagement_score": 3.0,
                "reply_count": 5,
                "reaction_count": 10,
                "author": "user1",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "message_id": "002",
                "content": "Help with LangGraph setup",
                "channel": "help",
                "keywords": ["langgraph", "setup"],
                "category": ["ai-ml"],
                "engagement_score": 2.5,
                "reply_count": 3,
                "reaction_count": 5,
                "author": "user2",
                "created_at": datetime.now(timezone.utc)
            }
        ]

        grouped = discussion_writer_agent._group_discussions_by_topic(cross_channel_discussions)

        # Should detect cross-channel topic
        assert any("Cross-Channel" in section for section in grouped.keys())

    @pytest.mark.asyncio
    async def test_generate_discussion_summary_structure(self, discussion_writer_agent, sample_discussions):
        """Test that generated summaries have required structure."""
        summary = await discussion_writer_agent._generate_single_discussion_summary(
            sample_discussions[0],
            "AI & Machine Learning"
        )

        # Check required fields
        assert "summary" in summary
        assert "channel" in summary
        assert "message_id" in summary
        assert "discord_link" in summary or summary.get("discord_link") is None
        assert "engagement" in summary
        assert "score" in summary["engagement"]
        assert "replies" in summary["engagement"]
        assert "reactions" in summary["engagement"]

    @pytest.mark.asyncio
    async def test_summary_includes_specific_details(self, discussion_writer_agent, sample_discussions):
        """Test that summaries include specific technical details."""
        summary = await discussion_writer_agent._generate_single_discussion_summary(
            sample_discussions[0],
            "AI & Machine Learning"
        )

        summary_text = summary["summary"].lower()

        # Should include specific tools/technologies
        assert any(keyword in summary_text for keyword in ["saloon", "langgraph", "ollama", "sqlite"])

        # Should include username
        assert "@" in summary["summary"] or "colin" in summary_text

    @pytest.mark.asyncio
    async def test_summary_word_count_range(self, discussion_writer_agent, sample_discussions):
        """Test that summaries are in 50-100 word range."""
        summary = await discussion_writer_agent._generate_single_discussion_summary(
            sample_discussions[0],
            "AI & Machine Learning"
        )

        word_count = len(summary["summary"].split())

        # Should be reasonable length (allowing some flexibility)
        assert 30 <= word_count <= 150, f"Word count {word_count} outside expected range"

    @pytest.mark.asyncio
    async def test_fallback_summary_without_model(self, sample_discussions):
        """Test that fallback summaries work without LLM."""
        agent = DiscussionWriterAgent(model=None)

        summary = agent._create_fallback_summary(sample_discussions[0])

        assert "summary" in summary
        assert "channel" in summary
        assert len(summary["summary"]) > 0

    @pytest.mark.asyncio
    async def test_discussion_summaries_sorted_by_engagement(self, discussion_writer_agent, sample_discussions):
        """Test that discussions are sorted by engagement score."""
        grouped = discussion_writer_agent._group_discussions_by_topic(sample_discussions)

        for section, discussions in grouped.items():
            # Check that discussions are sorted by engagement (descending)
            scores = [d.get("engagement_score", 0) for d in discussions]
            assert scores == sorted(scores, reverse=True), f"Section {section} not sorted by engagement"

    @pytest.mark.asyncio
    async def test_limits_discussions_per_section(self, discussion_writer_agent):
        """Test that each section limits discussions to top 10."""
        # Create 15 discussions in same category
        many_discussions = [
            {
                "message_id": f"msg_{i}",
                "content": f"Discussion {i}",
                "channel": "technical-discussions",
                "keywords": ["test"],
                "category": ["ai-ml"],
                "engagement_score": float(i),
                "reply_count": i,
                "reaction_count": i,
                "author": f"user{i}",
                "created_at": datetime.now(timezone.utc)
            }
            for i in range(15)
        ]

        grouped = discussion_writer_agent._group_discussions_by_topic(many_discussions)

        for section, discussions in grouped.items():
            assert len(discussions) <= 10, f"Section {section} has {len(discussions)} discussions, max should be 10"
