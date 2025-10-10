# Makefile Usage Guide

This document provides detailed information about using the Makefile for the AIMUG Discord Bot project.

## Quick Start

View all available commands:
```bash
make help
```

## Command Categories

### Setup & Installation

#### `make install`
Install all project dependencies using Poetry.
```bash
make install
```

#### `make db-init`
Initialize the database and apply all migrations.
```bash
make db-init
```

#### `make dev-setup`
Complete development environment setup:
- Installs dependencies
- Starts Docker containers
- Initializes database
- Applies migrations

```bash
make dev-setup
```

---

### Running the Bot

#### `make run`
Start the Discord bot using the main application entry point.
```bash
make run
```

#### `make run-bot`
Alternative method to start the bot via `run_bot.py`.
```bash
make run-bot
```

---

### Newsletter Generation

#### `make newsletter-daily`
Generate a daily newsletter (past 24 hours).
```bash
make newsletter-daily
```
- Fetches discussions from past day
- Min engagement score: 0.5
- Limit: 10 discussions

#### `make newsletter-weekly`
Generate a weekly newsletter (past 7 days).
```bash
make newsletter-weekly
```
- Fetches discussions from past week
- Min engagement score: 1.0
- Limit: 20 discussions

#### `make newsletter-biweekly`
Generate a bi-weekly newsletter (past 14 days).
```bash
make newsletter-biweekly
```
- Fetches discussions from past 2 weeks
- Min engagement score: 1.0
- Limit: 30 discussions

#### `make newsletter-monthly`
Generate a monthly newsletter (past 30 days).
```bash
make newsletter-monthly
```
- Fetches discussions from past month
- Min engagement score: 1.5
- Limit: 50 discussions

#### `make newsletter-draft`
Publish the most recent newsletter to Buttondown as a DRAFT (no sending).
```bash
make newsletter-draft
```
- Fetches latest generated newsletter from database
- Creates draft in Buttondown
- Updates database with draft ID
- **Does NOT send emails** - draft only

---

### Data Management

#### `make sync`
Synchronize Discord messages from server to local database.
```bash
make sync
```
- Fetches messages from all monitored channels
- Updates existing messages if edited
- Handles rate limiting automatically

#### `make engagement`
Calculate engagement metrics for all messages.
```bash
make engagement
```
- Calculates engagement scores
- Identifies trending discussions
- Extracts keywords and categories

#### `make recalculate`
Recalculate all engagement scores from scratch.
```bash
make recalculate
```
Use this when:
- Engagement algorithm changes
- Need to backfill missing data
- Correcting scoring errors

#### `make show-top`
Display the top-engaged discussions.
```bash
make show-top
```
Shows:
- Engagement scores
- Reply/reaction counts
- Message content preview
- Channel and author info

---

### Validation & Scripts

#### `make verify-schedules`
Verify newsletter schedule configuration and show next run times.
```bash
make verify-schedules
```
Displays:
- Cron schedule expressions
- Next execution times
- Timezone configuration
- All scheduled jobs

#### `make display-newsletter`
Display the most recent generated newsletter.
```bash
make display-newsletter
```

---

### Testing

#### `make test`
Run all pytest tests.
```bash
make test
```

#### `make test-coverage`
Run tests with coverage report.
```bash
make test-coverage
```
Generates:
- Terminal coverage report
- HTML coverage report in `htmlcov/`

#### `make test-bot`
Quick bot connectivity test.
```bash
make test-bot
```
Tests:
- Bot authentication
- Guild connection
- Basic API access

#### `make test-permissions`
Test Discord bot permissions.
```bash
make test-permissions
```
Tests:
- Channel access permissions
- Message reading permissions
- Permission breakdown by channel

#### `make test-workflow`
Test newsletter generation workflow end-to-end.
```bash
make test-workflow
```

#### `make test-all-channels`
Test bot access across all Discord channels.
```bash
make test-all-channels
```

---

### Code Quality

#### `make lint`
Run linting with flake8.
```bash
make lint
```
Checks:
- Code style violations
- Syntax errors
- Best practice violations

#### `make format`
Format code with black and isort.
```bash
make format
```
- Formats Python code (black)
- Sorts imports (isort)
- Auto-fixes style issues

#### `make typecheck`
Run type checking with mypy.
```bash
make typecheck
```

#### `make quality`
Run all quality checks: format + lint + typecheck.
```bash
make quality
```

---

### Database

#### `make db-start`
Start the PostgreSQL Docker container.
```bash
make db-start
```

#### `make db-stop`
Stop the PostgreSQL Docker container.
```bash
make db-stop
```

#### `make db-shell`
Open a PostgreSQL shell.
```bash
make db-shell
```
Connects to: `austin_langchain_bot` database

#### `make db-migrate`
Create a new database migration.
```bash
make db-migrate
```
Interactive: prompts for migration message

#### `make db-upgrade`
Apply all pending migrations.
```bash
make db-upgrade
```

#### `make db-downgrade`
Rollback the last migration.
```bash
make db-downgrade
```

---

### Cleanup

#### `make clean`
Remove generated files and caches.
```bash
make clean
```
Removes:
- `__pycache__` directories
- `*.pyc` files
- `.pytest_cache`
- `.mypy_cache`
- `htmlcov/`
- `.coverage`

#### `make clean-output`
Remove all generated newsletters.
```bash
make clean-output
```
⚠️ **Interactive**: Asks for confirmation before deleting

---

### Docker Operations

#### `make docker-build`
Build Docker containers.
```bash
make docker-build
```

#### `make docker-up`
Start all Docker containers.
```bash
make docker-up
```

#### `make docker-down`
Stop all Docker containers.
```bash
make docker-down
```

#### `make docker-logs`
Follow Docker container logs.
```bash
make docker-logs
```

#### `make docker-restart`
Restart Docker containers.
```bash
make docker-restart
```

---

### Combined Workflows

#### `make workflow-daily`
Complete daily newsletter workflow:
1. Sync Discord messages
2. Calculate engagement
3. Generate daily newsletter
4. Publish as Buttondown draft

```bash
make workflow-daily
```

#### `make workflow-weekly`
Complete weekly newsletter workflow:
1. Sync Discord messages
2. Calculate engagement
3. Generate weekly newsletter
4. Publish as Buttondown draft

```bash
make workflow-weekly
```

#### `make workflow-monthly`
Complete monthly newsletter workflow:
1. Sync Discord messages
2. Calculate engagement
3. Generate monthly newsletter
4. Publish as Buttondown draft

```bash
make workflow-monthly
```

---

### Development Workflows

#### `make dev-start`
Start development environment (database + bot).
```bash
make dev-start
```

#### `make dev-stop`
Stop development environment.
```bash
make dev-stop
```

---

### Quick Commands

#### `make quick-test`
Run quick bot connectivity test.
```bash
make quick-test
```

#### `make quick-newsletter`
Generate a quick weekly newsletter.
```bash
make quick-newsletter
```

---

## Common Use Cases

### Initial Setup
```bash
# Clone repository
git clone <repo-url>
cd bots/discord

# Setup everything
make dev-setup

# Verify setup
make verify-schedules
```

### Daily Development
```bash
# Start database
make db-start

# Run the bot
make run

# In another terminal: sync messages
make sync

# Calculate engagement
make engagement
```

### Newsletter Generation
```bash
# Generate monthly newsletter
make newsletter-monthly

# Publish as draft to Buttondown
make newsletter-draft

# Review draft at: https://buttondown.email/emails/{draft_id}
```

### Testing Changes
```bash
# Format code
make format

# Run quality checks
make quality

# Run tests
make test-coverage
```

### Database Management
```bash
# Start database
make db-start

# Create migration
make db-migrate

# Apply migration
make db-upgrade

# Access database shell
make db-shell
```

---

## Environment Variables

The Makefile automatically sets:
- `PYTHONPATH=$(pwd)/src` - Python module path

Ensure `.env` file contains:
```env
DATABASE_URL=postgresql://discord_bot:dev_password@localhost:5433/austin_langchain_bot
DISCORD_TOKEN=your_token
DISCORD_GUILD_ID=your_guild_id
LANGCHAIN_API_KEY=your_key
BUTTONDOWN_API_KEY=your_key
```

---

## Troubleshooting

### Command Not Found
```bash
# Install make if not available
# macOS (via Xcode Command Line Tools)
xcode-select --install

# Or via Homebrew
brew install make
```

### Permission Denied
```bash
# Make Makefile executable
chmod +x Makefile
```

### Poetry Not Found
```bash
# Install poetry
curl -sSL https://install.python-poetry.org | python3 -
```

### Database Connection Failed
```bash
# Check database is running
make db-start

# Verify connection
make db-shell
```

---

## Tips

1. **Tab Completion**: Most shells support tab completion for make targets
2. **Chaining Commands**: You can run multiple commands: `make format && make test`
3. **Background Tasks**: Run bot in background: `make run &`
4. **Verbose Output**: Add `-d` flag: `make -d test` for debug output
5. **Dry Run**: Use `-n` flag: `make -n newsletter-monthly` to see what would run

---

## See Also

- [README.md](../README.md) - Main project documentation
- [NEWSLETTER_GENERATION.md](NEWSLETTER_GENERATION.md) - Newsletter generation guide
- [scripts/README.md](../scripts/README.md) - Scripts documentation
- [tests/README.md](../tests/README.md) - Testing guide
