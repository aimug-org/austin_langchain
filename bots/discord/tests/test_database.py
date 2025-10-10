"""Tests for database service."""

import pytest
import uuid
from datetime import datetime, timezone
from discord_bot.models.discord_models import DiscordGuild, DiscordChannel, DiscordUser, DiscordMessage
from discord_bot.models.newsletter_models import Newsletter, NewsletterType, NewsletterStatus


@pytest.mark.asyncio
async def test_discord_guild_creation(test_db_session):
    """Test creating a Discord guild record."""
    guild = DiscordGuild(
        guild_id="123456789",
        name="Test Guild",
        description="A test guild",
        member_count=100,
        is_active=True
    )
    
    test_db_session.add(guild)
    await test_db_session.commit()
    
    assert guild.id is not None
    assert guild.guild_id == "123456789"
    assert guild.name == "Test Guild"
    assert guild.created_at is not None


@pytest.mark.asyncio
async def test_discord_user_creation(test_db_session):
    """Test creating a Discord user record."""
    user = DiscordUser(
        user_id="987654321",
        username="testuser",
        display_name="Test User",
        avatar_url="https://example.com/avatar.png",
        is_bot=False
    )
    
    test_db_session.add(user)
    await test_db_session.commit()
    
    assert user.id is not None
    assert user.user_id == "987654321"
    assert user.username == "testuser"
    assert not user.is_bot


@pytest.mark.asyncio
async def test_discord_message_with_relationships(test_db_session):
    """Test creating a message with all relationships."""
    # Create guild
    guild = DiscordGuild(
        guild_id="123456789",
        name="Test Guild",
        is_active=True
    )
    test_db_session.add(guild)
    await test_db_session.flush()
    
    # Create channel
    channel = DiscordChannel(
        channel_id="555666777",
        guild_id=guild.id,
        name="test-channel",
        channel_type="text",
        is_monitored=True
    )
    test_db_session.add(channel)
    await test_db_session.flush()
    
    # Create user
    user = DiscordUser(
        user_id="987654321",
        username="testuser",
        display_name="Test User",
        is_bot=False
    )
    test_db_session.add(user)
    await test_db_session.flush()
    
    # Create message
    message = DiscordMessage(
        message_id="111222333",
        guild_id=guild.id,
        channel_id=channel.id,
        author_id=user.id,
        content="Test message content",
        clean_content="Test message content",
        message_type="default",
        has_attachments=False,
        has_embeds=False
    )
    test_db_session.add(message)
    await test_db_session.commit()
    
    # Verify relationships
    assert message.guild.name == "Test Guild"
    assert message.channel.name == "test-channel"
    assert message.author.username == "testuser"


@pytest.mark.asyncio
async def test_newsletter_creation(test_db_session):
    """Test creating a newsletter record."""
    newsletter = Newsletter(
        title="Daily Newsletter - Test",
        subtitle="Test newsletter",
        newsletter_type=NewsletterType.DAILY,
        status=NewsletterStatus.PENDING,
        content_html="<h1>Test Newsletter</h1>",
        content_markdown="# Test Newsletter",
        word_count=50,
        estimated_read_time=1
    )
    
    test_db_session.add(newsletter)
    await test_db_session.commit()
    
    assert newsletter.id is not None
    assert newsletter.title == "Daily Newsletter - Test"
    assert newsletter.newsletter_type == NewsletterType.DAILY
    assert newsletter.status == NewsletterStatus.PENDING


@pytest.mark.asyncio
async def test_base_model_methods(test_db_session):
    """Test base model methods."""
    guild = DiscordGuild(
        guild_id="123456789",
        name="Test Guild",
        is_active=True
    )
    
    test_db_session.add(guild)
    await test_db_session.commit()
    
    # Test to_dict method
    guild_dict = guild.to_dict()
    assert isinstance(guild_dict, dict)
    assert guild_dict['guild_id'] == "123456789"
    assert guild_dict['name'] == "Test Guild"
    assert 'created_at' in guild_dict
    
    # Test __repr__ method
    repr_str = repr(guild)
    assert "DiscordGuild" in repr_str
    assert str(guild.id) in repr_str