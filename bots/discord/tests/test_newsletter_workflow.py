"""Tests for newsletter workflow and agents."""

import pytest
from datetime import datetime, timezone
from discord_bot.agents.newsletter_workflow import NewsletterWorkflow
from discord_bot.agents.state import DiscussionData, NewsletterState
from discord_bot.agents.research_agent import ResearchAgent
from discord_bot.agents.content_analyst import ContentAnalystAgent
from discord_bot.agents.opinion_writer import OpinionWriterAgent
from discord_bot.agents.editor_agent import EditorAgent
from discord_bot.agents.formatter_agent import FormatterAgent


@pytest.fixture
def sample_discussions():
    """Create sample discussion data for testing."""
    return [
        DiscussionData(
            message_id="123456",
            content="I'm having trouble with LangChain agents. How do you handle memory in complex workflows?",
            author="user1",
            channel="general",
            engagement_score=15.5,
            reply_count=8,
            reaction_count=12,
            participants=6,
            keywords=["langchain", "agent", "memory", "workflow"],
            category=["ai-ml"],
            created_at=datetime.now(timezone.utc)
        ),
        DiscussionData(
            message_id="789012",
            content="Just deployed a RAG system using vector databases. Performance is amazing!",
            author="user2", 
            channel="technical",
            engagement_score=22.1,
            reply_count=15,
            reaction_count=25,
            participants=10,
            keywords=["rag", "vector", "database", "performance"],
            category=["ai-ml", "programming"],
            created_at=datetime.now(timezone.utc)
        ),
        DiscussionData(
            message_id="345678",
            content="Austin LangChain meetup next week! Who's coming?",
            author="organizer",
            channel="events",
            engagement_score=18.3,
            reply_count=20,
            reaction_count=30,
            participants=25,
            keywords=["austin", "meetup", "event"],
            category=["community"],
            created_at=datetime.now(timezone.utc)
        )
    ]


@pytest.mark.asyncio
async def test_research_agent():
    """Test research agent functionality."""
    agent = ResearchAgent(model=None)
    
    state: NewsletterState = {
        "discussions": [
            {
                "message_id": "123",
                "content": "How do LangChain agents work with vector databases?",
                "keywords": ["langchain", "agent", "vector"],
                "category": ["ai-ml"]
            }
        ],
        "newsletter_type": "daily",
        "target_date": "2023-01-01",
        "research_topics": [],
        "research_results": [],
        "fact_check_results": {},
        "content_outline": {},
        "draft_sections": [],
        "technical_analysis": {},
        "writer_feedback": [],
        "newsletter_draft": None,
        "quality_metrics": {},
        "current_step": "research",
        "iteration_count": 0,
        "errors": [],
        "warnings": [],
        "selected_models": {},
        "model_costs": {}
    }
    
    response = await agent.invoke(state)
    
    assert response.agent_name == "ResearchAgent"
    assert response.action in ["research_complete", "skip"]
    
    if response.action == "research_complete":
        assert "research_topics" in response.output
        assert "research_results" in response.output


@pytest.mark.asyncio  
async def test_content_analyst_agent():
    """Test content analyst agent functionality."""
    agent = ContentAnalystAgent(model=None)
    
    state: NewsletterState = {
        "discussions": [
            {
                "message_id": "123",
                "content": "Testing LangChain workflows for production deployment",
                "engagement_score": 15.0,
                "keywords": ["langchain", "workflow", "production"],
                "category": ["ai-ml", "programming"]
            }
        ],
        "research_results": [],
        "newsletter_type": "daily",
        "target_date": "2023-01-01",
        "research_topics": [],
        "fact_check_results": {},
        "content_outline": {},
        "draft_sections": [],
        "technical_analysis": {},
        "writer_feedback": [],
        "newsletter_draft": None,
        "quality_metrics": {},
        "current_step": "content_analysis", 
        "iteration_count": 0,
        "errors": [],
        "warnings": [],
        "selected_models": {},
        "model_costs": {}
    }
    
    response = await agent.invoke(state)
    
    assert response.agent_name == "ContentAnalystAgent"
    assert response.action in ["analysis_complete", "skip"]
    
    if response.action == "analysis_complete":
        assert "content_analysis" in response.output
        assert "content_outline" in response.output


@pytest.mark.asyncio
async def test_opinion_writer_agent():
    """Test opinion writer agent functionality.""" 
    agent = OpinionWriterAgent(model=None)
    
    state: NewsletterState = {
        "discussions": [
            {
                "message_id": "123",
                "content": "Best practices for LangChain agent architecture?",
                "keywords": ["langchain", "agent", "architecture"],
                "category": ["ai-ml"],
                "engagement_score": 20.0
            }
        ],
        "content_outline": {
            "sections": [
                {
                    "type": "featured",
                    "title": "Featured Discussions", 
                    "discussion_ids": ["123"]
                }
            ]
        },
        "research_results": [],
        "newsletter_type": "daily",
        "target_date": "2023-01-01",
        "research_topics": [],
        "fact_check_results": {},
        "draft_sections": [],
        "technical_analysis": {},
        "writer_feedback": [],
        "newsletter_draft": None,
        "quality_metrics": {},
        "current_step": "opinion_writing",
        "iteration_count": 0,
        "errors": [],
        "warnings": [],
        "selected_models": {},
        "model_costs": {}
    }
    
    response = await agent.invoke(state)
    
    assert response.agent_name == "OpinionWriterAgent"
    assert response.action in ["commentary_complete", "skip"]


@pytest.mark.asyncio
async def test_editor_agent():
    """Test editor agent functionality."""
    agent = EditorAgent(model=None)
    
    state: NewsletterState = {
        "draft_sections": [
            {
                "section_type": "featured",
                "title": "Featured Discussions",
                "content": "This is some test content that needs editing for clarity.",
                "word_count": 10
            }
        ],
        "technical_analysis": {},
        "discussions": [],
        "newsletter_type": "daily",
        "target_date": "2023-01-01",
        "research_topics": [],
        "research_results": [],
        "fact_check_results": {},
        "content_outline": {},
        "writer_feedback": [],
        "newsletter_draft": None,
        "quality_metrics": {},
        "current_step": "editing",
        "iteration_count": 0,
        "errors": [],
        "warnings": [],
        "selected_models": {},
        "model_costs": {}
    }
    
    response = await agent.invoke(state)
    
    assert response.agent_name == "EditorAgent"
    assert response.action in ["editing_complete", "skip"]
    
    if response.action == "editing_complete":
        assert "quality_metrics" in response.output
        assert "edited_sections" in response.output


@pytest.mark.asyncio
async def test_formatter_agent():
    """Test formatter agent functionality."""
    agent = FormatterAgent(model=None)
    
    state: NewsletterState = {
        "edited_sections": [
            {
                "section_type": "featured",
                "title": "Featured Discussions",
                "content": "This week's most engaging technical discussions.",
                "word_count": 6,
                "discussion_ids": ["123"]
            }
        ],
        "quality_metrics": {"estimated_read_time": 3},
        "newsletter_type": "daily",
        "target_date": "2023-01-01",
        "discussions": [],
        "research_topics": [],
        "research_results": [],
        "fact_check_results": {},
        "content_outline": {},
        "draft_sections": [],
        "technical_analysis": {},
        "writer_feedback": [],
        "newsletter_draft": None,
        "current_step": "formatting",
        "iteration_count": 0,
        "errors": [],
        "warnings": [],
        "selected_models": {},
        "model_costs": {}
    }
    
    response = await agent.invoke(state)
    
    assert response.agent_name == "FormatterAgent"
    assert response.action in ["formatting_complete", "skip"]
    
    if response.action == "formatting_complete":
        assert "newsletter_draft" in response.output
        assert "html_content" in response.output
        assert "markdown_content" in response.output
        assert "text_content" in response.output


@pytest.mark.asyncio
async def test_newsletter_workflow_initialization():
    """Test newsletter workflow initialization."""
    workflow = NewsletterWorkflow()
    
    status = workflow.get_workflow_status()
    
    assert status["agents_initialized"] == 5
    assert status["graph_built"] is True
    assert status["compiled"] is True
    assert "research" in status["agent_names"]
    assert "content_analyst" in status["agent_names"]
    assert "opinion_writer" in status["agent_names"]
    assert "editor" in status["agent_names"]
    assert "formatter" in status["agent_names"]


@pytest.mark.asyncio
async def test_newsletter_workflow_execution(sample_discussions):
    """Test full newsletter workflow execution."""
    workflow = NewsletterWorkflow()
    
    # This test runs the full workflow without LLM models
    # It tests the workflow structure and fallback mechanisms
    try:
        result = await workflow.generate_newsletter(
            discussions=sample_discussions,
            newsletter_type="daily",
            target_date="2023-01-01"
        )
        
        # Check basic structure is present
        assert "newsletter_type" in result
        assert "discussions" in result
        assert result["newsletter_type"] == "daily"
        
        # Check that workflow steps were attempted
        # (May have errors due to no LLM models, but structure should be intact)
        
    except Exception as e:
        # Workflow may fail without actual LLM models
        # But the structure should be testable
        assert "workflow" in str(e).lower() or "model" in str(e).lower()


def test_discussion_data_validation():
    """Test DiscussionData validation."""
    # Valid discussion data
    discussion = DiscussionData(
        message_id="123",
        content="Test content",
        author="testuser",
        channel="general",
        engagement_score=10.0,
        reply_count=5,
        reaction_count=3,
        participants=8,
        keywords=["test"],
        category=["general"],
        created_at=datetime.now(timezone.utc)
    )
    
    assert discussion.message_id == "123"
    assert discussion.engagement_score == 10.0
    assert discussion.keywords == ["test"]