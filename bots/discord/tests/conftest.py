"""Pytest configuration and fixtures."""

import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from discord_bot.models.base import Base
from discord_bot.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db_engine():
    """Create test database engine."""
    # Use in-memory SQLite for testing
    test_database_url = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(
        test_database_url,
        echo=False,
        future=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_db_engine):
    """Create test database session."""
    session_factory = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_discord_message():
    """Mock Discord message for testing."""
    from unittest.mock import Mock
    
    message = Mock()
    message.id = "123456789"
    message.content = "Test message content"
    message.clean_content = "Test message content"
    message.created_at = "2023-01-01T00:00:00+00:00"
    message.edited_at = None
    message.pinned = False
    message.attachments = []
    message.embeds = []
    message.reactions = []
    message.reference = None
    message.type = "default"
    
    # Mock author
    message.author = Mock()
    message.author.id = "987654321"
    message.author.name = "testuser"
    message.author.display_name = "Test User"
    message.author.avatar = None
    message.author.bot = False
    
    # Mock channel
    message.channel = Mock()
    message.channel.id = "555666777"
    message.channel.name = "test-channel"
    message.channel.topic = "Test channel"
    message.channel.type = "text"
    
    # Mock guild
    message.guild = Mock()
    message.guild.id = "111222333"
    message.guild.name = "Test Guild"
    message.guild.description = "Test guild description"
    message.guild.member_count = 100
    
    return message