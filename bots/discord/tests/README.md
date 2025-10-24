# Tests Directory

This directory contains test files for validating Discord bot functionality, permissions, and workflows.

## Test Files

### Discord Bot Tests

#### `test_bot_quick.py`
Quick validation test for basic bot connectivity and setup.

**Usage:**
```bash
poetry run python tests/test_bot_quick.py
```

**Tests:**
- Bot authentication
- Guild connection
- Basic API access

---

#### `test_all_channels.py`
Tests bot access across all Discord channels in the guild.

**Usage:**
```bash
poetry run python tests/test_all_channels.py
```

**Tests:**
- Channel enumeration
- Read permissions per channel
- Message fetching capability

---

### Permission Tests

#### `test_basic_permissions.py`
Basic permission validation for the Discord bot.

**Usage:**
```bash
poetry run python tests/test_basic_permissions.py
```

**Tests:**
- Read message permissions
- Channel access permissions
- Guild member permissions

---

#### `test_discord_permissions.py`
Comprehensive Discord permission testing.

**Usage:**
```bash
poetry run python tests/test_discord_permissions.py
```

**Tests:**
- Detailed permission breakdown by channel
- Role-based permission checks
- Bot permission validation

---

### Message Access Tests

#### `test_message_access.py`
Tests bot's ability to access and read Discord messages.

**Usage:**
```bash
poetry run python tests/test_message_access.py
```

**Tests:**
- Message reading across channels
- Historical message access
- Message metadata retrieval

---

#### `test_fetch_history.py`
Tests fetching message history from Discord channels.

**Usage:**
```bash
poetry run python tests/test_fetch_history.py
```

**Tests:**
- Historical message fetching
- Message pagination
- Time-based message filtering

---

### Workflow Tests

#### `test_workflow.py`
Tests the newsletter generation workflow end-to-end.

**Usage:**
```bash
PYTHONPATH=/Users/that1guy15/austin_langchain/bots/discord/src python tests/test_workflow.py
```

**Tests:**
- Complete newsletter workflow
- Agent pipeline execution
- Newsletter content generation

---

## Pytest Tests

These tests are designed to run with pytest and include fixtures.

#### `test_database.py`
Database connectivity and operations tests.

**Usage:**
```bash
poetry run pytest tests/test_database.py -v
```

**Tests:**
- Database connection
- Model creation and retrieval
- Transaction handling

---

#### `test_engagement.py`
Engagement metrics calculation and scoring tests.

**Usage:**
```bash
poetry run pytest tests/test_engagement.py -v
```

**Tests:**
- Engagement score calculation
- Metric aggregation
- Top discussion retrieval

---

#### `test_newsletter_workflow.py`
Newsletter workflow unit tests with mocked dependencies.

**Usage:**
```bash
poetry run pytest tests/test_newsletter_workflow.py -v
```

**Tests:**
- Individual agent behavior
- Workflow state management
- Newsletter generation pipeline

---

#### `test_api_integrations.py`
API integration tests for external services.

**Usage:**
```bash
poetry run pytest tests/test_api_integrations.py -v
```

**Tests:**
- Perplexity API integration
- Buttondown API integration
- LangSmith tracing

---

## Test Configuration

### `conftest.py`
Pytest configuration and shared fixtures.

**Includes:**
- Database fixtures
- Mock services
- Test data factories
- Cleanup utilities

### `__init__.py`
Package initialization for the tests module.

---

## Running All Tests

### Run all pytest tests:
```bash
poetry run pytest tests/ -v
```

### Run tests with coverage:
```bash
poetry run pytest tests/ --cov=discord_bot --cov-report=html
```

### Run specific test file:
```bash
poetry run pytest tests/test_engagement.py -v
```

### Run tests matching a pattern:
```bash
poetry run pytest tests/ -k "engagement" -v
```

---

## Test Environment

Tests require the following environment setup:

### Required Environment Variables:
```env
DATABASE_URL=postgresql://discord_bot:dev_password@localhost:5433/austin_langchain_bot
DISCORD_TOKEN=your_test_bot_token
DISCORD_GUILD_ID=your_test_guild_id
```

### Database Setup:
```bash
# Start test database
docker-compose -f docker-compose.dev.yml up -d postgres

# Run migrations
poetry run alembic upgrade head
```

### Discord Bot Setup:
- Create a test bot in Discord Developer Portal
- Add bot to test guild
- Ensure bot has required permissions:
  - Read Messages/View Channels
  - Read Message History
  - Add Reactions (optional)

---

## Writing New Tests

### Test Naming Convention:
- Pytest tests: `test_*.py` in tests directory
- Standalone validation: `test_*.py` can be run directly
- Test functions: `def test_description():`

### Example Test Structure:
```python
import pytest
from discord_bot.services.engagement_service import engagement_service

@pytest.mark.asyncio
async def test_engagement_calculation(db_session):
    """Test engagement score calculation."""
    # Arrange
    message = create_test_message()

    # Act
    score = await engagement_service.calculate_score(message)

    # Assert
    assert score > 0
    assert score < 10
```

---

## Continuous Integration

Tests are run automatically on:
- Pull requests
- Commits to main branch
- Scheduled daily runs

See `.github/workflows/tests.yml` for CI configuration.

---

## Troubleshooting

### Database Connection Errors
```bash
# Check database is running
docker ps | grep postgres

# Verify connection
poetry run python -c "from discord_bot.services.database import db_service; import asyncio; asyncio.run(db_service.initialize())"
```

### Discord API Errors
- Verify bot token is valid
- Check bot is in the test guild
- Ensure bot has required permissions

### Import Errors
```bash
# Set PYTHONPATH
export PYTHONPATH=/Users/that1guy15/austin_langchain/bots/discord/src

# Or use poetry run
poetry run python tests/test_workflow.py
```

---

## See Also

- [../scripts/README.md](../scripts/README.md) - Utility scripts
- [../README.md](../README.md) - Main project documentation
- [../NEWSLETTER_GENERATION.md](../docs/NEWSLETTER_GENERATION.md) - Newsletter generation guide
