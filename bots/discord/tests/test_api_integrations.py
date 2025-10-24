"""Tests for API integration services."""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock
from discord_bot.services.perplexity_service import PerplexityService
from discord_bot.services.model_router import ModelRouter, ModelCapability, ModelProvider
from discord_bot.services.buttondown_service import ButtondownService
from discord_bot.services.scheduler_service import SchedulerService
from discord_bot.models.newsletter_models import Newsletter, NewsletterType, NewsletterStatus


@pytest.mark.asyncio
async def test_perplexity_service_initialization():
    """Test Perplexity service initialization."""
    service = PerplexityService()
    
    # Test without API key
    service.api_key = None
    await service.initialize()
    assert service.client is None
    
    # Test with API key
    service.api_key = "test_key"
    await service.initialize()
    assert service.client is not None
    
    await service.close()


@pytest.mark.asyncio
async def test_perplexity_research_fallback():
    """Test Perplexity research with fallback."""
    service = PerplexityService()
    service.api_key = None  # Force fallback
    
    result = await service.research_topic("LangChain updates", "AI development")
    
    assert result is not None
    assert result.topic == "LangChain updates"
    assert result.query == "LangChain updates"
    assert len(result.findings) > 0
    assert len(result.sources) > 0
    assert 0 <= result.relevance_score <= 1


@pytest.mark.asyncio 
async def test_perplexity_fact_check_fallback():
    """Test Perplexity fact-checking with fallback."""
    service = PerplexityService()
    service.api_key = None  # Force fallback
    
    result = await service.fact_check("LangChain is a Python framework", "AI development")
    
    assert result["claim"] == "LangChain is a Python framework"
    assert result["status"] == "unverified"
    assert "explanation" in result
    assert "sources" in result
    assert "confidence" in result


@pytest.mark.asyncio
async def test_perplexity_health_check():
    """Test Perplexity service health check."""
    service = PerplexityService()
    
    health = await service.health_check()
    
    assert health["service"] == "perplexity"
    assert "status" in health
    assert "api_key_configured" in health


@pytest.mark.asyncio
async def test_model_router_initialization():
    """Test model router initialization."""
    router = ModelRouter()
    
    # Test without API key (should initialize fallback models)
    router.api_key = None
    await router.initialize()
    
    assert len(router.available_models) > 0
    assert "claude-3-sonnet-20240229" in router.available_models
    
    await router.close()


@pytest.mark.asyncio
async def test_model_router_capability_selection():
    """Test model selection by capability."""
    router = ModelRouter()
    await router.initialize()
    
    # Test getting model for research capability
    model = await router.get_model_for_capability(ModelCapability.RESEARCH)
    assert model is not None
    assert ModelCapability.RESEARCH in model.capabilities
    
    # Test getting model for editing capability
    model = await router.get_model_for_capability(ModelCapability.EDITING)
    assert model is not None
    assert ModelCapability.EDITING in model.capabilities


@pytest.mark.asyncio
async def test_model_router_fallback_response():
    """Test model router fallback response."""
    router = ModelRouter()
    router.api_key = None
    await router.initialize()
    
    messages = [{"role": "user", "content": "Test message"}]
    response = await router.invoke_model("claude-3-sonnet-20240229", messages)
    
    assert response is not None
    assert "choices" in response
    assert "fallback" in response
    assert response["fallback"] is True


@pytest.mark.asyncio
async def test_model_router_user_preferences():
    """Test model router user preferences."""
    router = ModelRouter()
    await router.initialize()
    
    # Set user preference
    router.set_user_preference(ModelCapability.RESEARCH, "claude-3-sonnet-20240229")
    
    # Check preference is applied
    model = await router.get_model_for_capability(ModelCapability.RESEARCH)
    assert model is not None
    assert model.id == "claude-3-sonnet-20240229"


@pytest.mark.asyncio
async def test_buttondown_service_initialization():
    """Test Buttondown service initialization."""
    service = ButtondownService()
    
    # Test without API key
    service.api_key = None
    await service.initialize()
    assert service.client is None
    
    # Test with API key
    service.api_key = "test_key"
    await service.initialize()
    assert service.client is not None
    
    await service.close()


@pytest.mark.asyncio
async def test_buttondown_create_draft_fallback():
    """Test Buttondown draft creation with fallback."""
    service = ButtondownService()
    service.api_key = None  # Force fallback
    
    draft = await service.create_draft(
        subject="Test Newsletter",
        body="<h1>Test Content</h1>"
    )
    
    assert draft is not None
    assert draft["subject"] == "Test Newsletter"
    assert draft["fallback"] is True
    assert "id" in draft


@pytest.mark.asyncio
async def test_buttondown_newsletter_from_model():
    """Test creating newsletter from model."""
    service = ButtondownService()
    service.api_key = None  # Force fallback
    
    # Create mock newsletter
    newsletter = Mock(spec=Newsletter)
    newsletter.id = "test-id"
    newsletter.title = "Test Newsletter"
    newsletter.content_html = "<h1>Test Content</h1>"
    newsletter.newsletter_type = NewsletterType.DAILY
    
    draft_id = await service.create_newsletter_from_model(newsletter)
    
    assert draft_id is not None


@pytest.mark.asyncio
async def test_buttondown_health_check():
    """Test Buttondown service health check."""
    service = ButtondownService()
    
    health = await service.health_check()
    
    assert health["service"] == "buttondown"
    assert "status" in health
    assert "api_key_configured" in health


@pytest.mark.asyncio
async def test_scheduler_service_initialization():
    """Test scheduler service initialization."""
    scheduler = SchedulerService()
    
    await scheduler.initialize()
    assert scheduler.scheduler is not None
    assert scheduler.timezone is not None
    
    await scheduler.stop()


@pytest.mark.asyncio
async def test_scheduler_newsletter_scheduling():
    """Test newsletter scheduling."""
    scheduler = SchedulerService()
    await scheduler.initialize()
    await scheduler.start()
    
    try:
        # Schedule a newsletter
        await scheduler.schedule_newsletter_generation(
            newsletter_type=NewsletterType.DAILY,
            cron_expression="0 6 * * *",
            job_id="test_daily"
        )
        
        # Check job was created
        jobs = scheduler.get_scheduled_jobs()
        job_ids = [job["id"] for job in jobs]
        assert "test_daily" in job_ids
        
        # Check job status
        status = scheduler.get_job_status("test_daily")
        assert status is not None
        assert status["id"] == "test_daily"
        
    finally:
        await scheduler.stop()


@pytest.mark.asyncio
async def test_scheduler_one_time_newsletter():
    """Test one-time newsletter scheduling."""
    scheduler = SchedulerService()
    await scheduler.initialize()
    await scheduler.start()
    
    try:
        # Schedule one-time newsletter
        future_time = datetime.now(timezone.utc).replace(microsecond=0)
        job_id = await scheduler.schedule_one_time_newsletter(
            newsletter_type=NewsletterType.WEEKLY,
            scheduled_time=future_time
        )
        
        assert job_id is not None
        assert job_id.startswith("onetime_weekly_")
        
        # Check job exists
        status = scheduler.get_job_status(job_id)
        assert status is not None
        
    finally:
        await scheduler.stop()


@pytest.mark.asyncio
async def test_scheduler_job_management():
    """Test scheduler job management operations."""
    scheduler = SchedulerService()
    await scheduler.initialize()
    await scheduler.start()
    
    try:
        # Create test job
        await scheduler.schedule_newsletter_generation(
            newsletter_type=NewsletterType.DAILY,
            cron_expression="0 8 * * *",
            job_id="test_management"
        )
        
        # Test pause
        result = await scheduler.pause_job("test_management")
        assert result is True
        
        # Test resume
        result = await scheduler.resume_job("test_management")
        assert result is True
        
        # Test reschedule
        result = await scheduler.reschedule_job("test_management", "0 9 * * *")
        assert result is True
        
        # Test cancel
        result = await scheduler.cancel_job("test_management")
        assert result is True
        
        # Check job is gone
        status = scheduler.get_job_status("test_management")
        assert status is None
        
    finally:
        await scheduler.stop()


@pytest.mark.asyncio
async def test_scheduler_status():
    """Test scheduler status reporting."""
    scheduler = SchedulerService()
    
    # Test uninitialized status
    status = scheduler.get_scheduler_status()
    assert status["is_running"] is False
    assert status["scheduler_initialized"] is False
    
    # Test initialized status
    await scheduler.initialize()
    await scheduler.start()
    
    try:
        status = scheduler.get_scheduler_status()
        assert status["is_running"] is True
        assert status["scheduler_initialized"] is True
        assert status["jobs_count"] >= 0
        
    finally:
        await scheduler.stop()


def test_model_info_creation():
    """Test ModelInfo class creation."""
    from discord_bot.services.model_router import ModelInfo
    
    model = ModelInfo(
        id="test-model",
        name="Test Model",
        provider=ModelProvider.ANTHROPIC,
        capabilities=[ModelCapability.RESEARCH, ModelCapability.CONTENT_WRITING],
        input_cost_per_token=0.001,
        output_cost_per_token=0.002,
        max_tokens=2000,
        context_window=8000
    )
    
    assert model.id == "test-model"
    assert model.provider == ModelProvider.ANTHROPIC
    assert ModelCapability.RESEARCH in model.capabilities
    assert model.input_cost_per_token == 0.001


def test_model_capability_enum():
    """Test ModelCapability enumeration."""
    assert ModelCapability.RESEARCH.value == "research"
    assert ModelCapability.CONTENT_WRITING.value == "content_writing"
    assert ModelCapability.TECHNICAL_ANALYSIS.value == "technical_analysis"