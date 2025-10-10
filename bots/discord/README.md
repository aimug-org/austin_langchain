# Austin LangChain Discord Newsletter Bot

An AI-powered Discord bot that monitors community discussions, analyzes engagement, and automatically generates professional newsletters for the Austin LangChain community.

## Features

- 🤖 **Automated Discord Monitoring**: Real-time tracking of community discussions
- 📊 **Intelligent Engagement Analysis**: Advanced algorithms to identify trending conversations
- ✍️ **AI-Powered Newsletter Generation**: Multi-agent technical writing workflow
- 🔍 **Research Integration**: Perplexity API for fact-checking and context enhancement
- 📧 **Automated Publishing**: Seamless integration with Buttondown for email distribution
- 🕐 **Smart Scheduling**: Daily, weekly, and monthly newsletter generation
- 📅 **Flexible Timeframes**: Support for daily, weekly, bi-weekly, and monthly newsletters
- 📈 **Comprehensive Monitoring**: LangSmith integration for workflow visibility

## Architecture

The bot uses a sophisticated multi-agent workflow:

```
Discord Monitoring → Engagement Analysis → Multi-Agent Writing → Newsletter Publishing
       ↓                     ↓                      ↓                    ↓
   Message Store    Engagement Metrics      Technical Content      Buttondown API
```

### Core Components

- **Discord Integration**: Real-time message monitoring with engagement tracking
- **LangGraph Workflows**: Multi-agent technical writing team simulation
- **Requesty.ai Router**: Flexible AI model selection and routing  
- **Perplexity Research**: Advanced fact-checking and context gathering
- **Database Layer**: PostgreSQL with comprehensive data modeling

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose
- Discord Bot Token
- API Keys: LangSmith, Perplexity, Buttondown, Requesty.ai

### Development Setup

1. **Clone and setup environment:**
   ```bash
   git clone <repository>
   cd austin-langchain-discord-bot
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

2. **Start development environment:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. **Initialize database:**
   ```bash
   poetry install
   poetry run alembic upgrade head
   ```

4. **Run the bot:**
   ```bash
   poetry run python -m discord_bot.main
   ```

### Configuration

**Environment File Location**: `/Users/that1guy15/austin_langchain/bots/discord/.env`

This `.env` file is shared across multiple services including:
- Discord bot newsletter generation
- Portfolio website newsletter scripts
- Other automation tools

Key environment variables in `.env`:

```env
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_guild_id
DISCORD_CHANNEL_IDS=channel1,channel2,channel3

# Database
DATABASE_URL=postgresql://discord_bot:password@localhost:5432/austin_langchain_bot

# AI Services
LANGCHAIN_API_KEY=your_langsmith_key
REQUESTY_API_KEY=your_requesty_key
PERPLEXITY_API_KEY=your_perplexity_key

# Buttondown Newsletter API
BUTTONDOWN_API_KEY=your_buttondown_key
BUTTONDOWN_BASE_URL=https://api.buttondown.com  # Optional, defaults to this

# Newsletter Schedule
NEWSLETTER_SCHEDULE_DAILY=0 6 * * *  # 6 AM CST daily
NEWSLETTER_SCHEDULE_WEEKLY=0 6 * * 1  # 6 AM CST Monday
```

**Note**: Scripts in other repositories (like the portfolio website at `/Users/that1guy15/abstractRyanPortfolio`) reference this centralized `.env` file for Buttondown API credentials.

## Usage

### Make Commands

The project uses a Makefile for simplified command execution. Run `make help` to see all available commands:

```bash
# Show all available commands
make help

# Newsletter generation
make newsletter-daily      # Generate daily newsletter
make newsletter-weekly     # Generate weekly newsletter
make newsletter-monthly    # Generate monthly newsletter
make newsletter-draft      # Publish to Buttondown as draft

# Data management
make sync                  # Sync Discord messages
make engagement            # Calculate engagement metrics
make show-top              # Show top discussions

# Testing
make test                  # Run all tests
make test-coverage         # Run tests with coverage

# Development
make dev-setup             # Full development setup
make run                   # Start the bot
```

**Or use direct commands:**

```bash
# Generate newsletter manually (daily, weekly, biweekly, or monthly)
poetry run python generate_newsletter.py daily
poetry run python generate_newsletter.py weekly
poetry run python generate_newsletter.py monthly

# See detailed usage guide
cat NEWSLETTER_GENERATION.md
```

### Newsletter Generation Process

1. **Data Collection**: Bot monitors Discord channels continuously
2. **Engagement Analysis**: Algorithms identify high-engagement discussions  
3. **Multi-Agent Workflow**: 
   - Research Agent: Gathers context via Perplexity
   - Content Analyst: Summarizes discussions
   - Opinion Writer: Provides technical commentary  
   - Editor: Reviews quality and tone
   - Formatter: Prepares final newsletter
4. **Publishing**: Creates Buttondown draft for review

### Engagement Scoring

The bot uses sophisticated engagement metrics:

```python
engagement_score = (
    reply_count * 0.4 +
    reaction_count * 0.2 +
    unique_participants * 0.3 +
    recency_factor * 0.1
)
```

## Development

### Project Structure

```
discord/
├── src/discord_bot/       # Main application code
│   ├── core/             # Configuration and logging
│   ├── models/           # Database models
│   ├── services/         # Business logic services
│   ├── agents/           # LangGraph agent workflows
│   ├── utils/            # Utility functions
│   └── main.py           # Application entry point
├── tests/                # Test files (see tests/README.md)
├── scripts/              # Utility scripts (see scripts/README.md)
├── output/               # Generated newsletters
├── generate_newsletter.py  # Newsletter generation CLI
└── run_bot.py            # Bot startup script
```

### Database Models

- **Discord Models**: Messages, users, channels, engagement metrics
- **Newsletter Models**: Newsletters, sections, generation logs, publications

### Testing

```bash
# Run all tests
poetry run pytest tests/

# Run with coverage
poetry run pytest tests/ --cov=discord_bot

# Run specific test
poetry run pytest tests/test_engagement.py

# See tests/README.md for detailed test documentation
```

### Utility Scripts

Common maintenance and validation scripts (see `scripts/README.md` for details):

```bash
# Sync Discord messages to database
poetry run python scripts/sync_messages.py

# Calculate engagement metrics
poetry run python scripts/calculate_engagement.py

# Show top engaged discussions
poetry run python scripts/show_top_messages.py

# Verify schedule configuration
poetry run python scripts/verify_schedules.py

# Display generated newsletter
poetry run python scripts/display_newsletter.py

# Publish newsletter to Buttondown
poetry run python scripts/publish_newsletter_to_buttondown.py
```

### Code Quality

```bash
# Format code
poetry run black src tests scripts

# Sort imports
poetry run isort src tests scripts

# Type checking
poetry run mypy src

# Lint
poetry run flake8 src tests scripts
```

## Deployment

### Production Setup

1. **Environment Configuration:**
   ```bash
   export ENVIRONMENT=production
   export DATABASE_URL=your_production_db_url
   # Set all required API keys
   ```

2. **Database Migration:**
   ```bash
   alembic upgrade head
   ```

3. **Docker Deployment:**
   ```bash
   docker-compose up -d
   ```

### Monitoring

- **LangSmith**: Workflow execution and performance monitoring
- **Application Logs**: Structured JSON logging with loguru
- **Database Metrics**: PostgreSQL monitoring via standard tools
- **Discord API**: Rate limiting and error tracking

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run quality checks: `poetry run black . && poetry run pytest`
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive tests
- Update documentation
- Use conventional commit messages

## API Documentation

### Newsletter Generation API

The bot exposes internal APIs for newsletter management:

```python
# Generate newsletter
newsletter = await newsletter_service.generate_newsletter(
    type=NewsletterType.DAILY,
    force=False
)

# Get engagement metrics  
metrics = await engagement_service.get_top_discussions(
    days=7,
    min_score=5.0
)
```

## Support & Community

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join Austin LangChain Discord community
- **Documentation**: Full docs at `/docs` (when available)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Austin LangChain community for requirements and feedback  
- LangChain team for excellent framework and tools
- Discord.py contributors for robust Discord API library

---

**Developed by Austin LangChain Team** | **Version 0.1.0**