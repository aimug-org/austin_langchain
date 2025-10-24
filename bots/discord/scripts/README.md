# Scripts Directory

This directory contains utility and maintenance scripts for the AIMUG Discord bot.

## Script Categories

### Message Synchronization

#### `sync_messages.py`
Synchronizes Discord messages from the server to the local database.

**Usage:**
```bash
poetry run python scripts/sync_messages.py
```

**Purpose:**
- Fetches historical messages from Discord channels
- Stores messages in PostgreSQL database
- Updates existing messages if edited
- Handles rate limiting automatically

**Configuration:**
- Monitors channels specified in `DISCORD_CHANNEL_IDS` env var
- Respects Discord API rate limits
- Logs progress to console and log files

---

### Engagement Metrics

#### `calculate_engagement.py`
Calculates engagement metrics for Discord messages.

**Usage:**
```bash
poetry run python scripts/calculate_engagement.py
```

**Purpose:**
- Calculates engagement scores based on:
  - Reply count (40% weight)
  - Reaction count (20% weight)
  - Unique participants (30% weight)
  - Recency factor (10% weight)
- Identifies trending discussions
- Extracts keywords from content
- Categorizes messages by topic

**Metrics Calculated:**
- `engagement_score`: Overall engagement rating
- `trending_score`: Time-weighted trending score
- `discussion_participants`: Unique user count
- `extracted_keywords`: Important terms
- `topic_categories`: Content classification

---

#### `recalculate_engagement.py`
Recalculates engagement metrics for all existing messages.

**Usage:**
```bash
poetry run python scripts/recalculate_engagement.py
```

**Purpose:**
- Refreshes engagement scores for all messages
- Useful after algorithm changes
- Updates historical data
- Fixes incorrect scores

**When to Use:**
- After modifying engagement scoring algorithm
- When introducing new metrics
- To backfill missing engagement data
- To correct scoring errors

---

#### `show_top_messages.py`
Displays top-engaged messages from the database.

**Usage:**
```bash
poetry run python scripts/show_top_messages.py
```

**Purpose:**
- Shows highest-scoring discussions
- Displays engagement metrics
- Previews message content
- Helps validate engagement scoring

**Output:**
```
Top 20 Messages by Engagement Score
====================================
1. [#general] Score: 8.52
   Author: username
   Content: Message preview...
   Replies: 5, Reactions: 12, Participants: 8
```

---

### Newsletter Management

#### `display_newsletter.py`
Displays a generated newsletter from the database.

**Usage:**
```bash
poetry run python scripts/display_newsletter.py
```

**Purpose:**
- Retrieves recent newsletters from database
- Displays newsletter content in terminal
- Shows metadata (word count, sections, etc.)
- Useful for preview before publishing

**Example:**
```bash
# Display most recent newsletter
poetry run python scripts/display_newsletter.py

# Display specific newsletter by ID
poetry run python scripts/display_newsletter.py --id UUID
```

---

#### `newsletter_with_fetch.py`
Generates a newsletter with live data fetching.

**Usage:**
```bash
poetry run python scripts/newsletter_with_fetch.py
```

**Purpose:**
- Fetches latest discussions from database
- Generates newsletter using current data
- Includes Perplexity research integration
- Testing alternative generation approaches

**Note:** This is an experimental script. Use `../generate_newsletter.py` for production.

---

#### `publish_newsletter_to_buttondown.py`
Publishes a generated newsletter to Buttondown email service.

**Usage:**
```bash
poetry run python scripts/publish_newsletter_to_buttondown.py
```

**Purpose:**
- Fetches newsletter from database
- Converts to Buttondown-compatible format
- Creates draft in Buttondown
- Optionally publishes immediately

**Requirements:**
- `BUTTONDOWN_API_KEY` in environment
- Newsletter must be in `GENERATED` status
- Buttondown account configured

**Configuration:**
```python
# Publish as draft (default)
poetry run python scripts/publish_newsletter_to_buttondown.py

# Publish immediately (use with caution)
poetry run python scripts/publish_newsletter_to_buttondown.py --publish-now
```

---

### Scheduling & Validation

#### `verify_schedules.py`
Verifies scheduled job configuration and timing.

**Usage:**
```bash
poetry run python scripts/verify_schedules.py
```

**Purpose:**
- Validates cron schedule syntax
- Shows next scheduled execution times
- Verifies timezone configuration
- Lists all scheduled jobs

**Output:**
```
Newsletter Schedules (America/Chicago)
======================================
Daily Newsletter:
  Schedule: 0 6 * * * (6:00 AM daily)
  Next run: 2025-10-12 06:00:00 CST

Weekly Newsletter:
  Schedule: 0 20 * * 6 (8:00 PM Saturday)
  Next run: 2025-10-12 20:00:00 CST

Monthly Newsletter:
  Schedule: 0 20 1 * * (8:00 PM 1st of month)
  Next run: 2025-11-01 20:00:00 CST
```

---

## Common Workflows

### Initial Setup Workflow
```bash
# 1. Sync historical messages
poetry run python scripts/sync_messages.py

# 2. Calculate engagement metrics
poetry run python scripts/calculate_engagement.py

# 3. Verify top messages
poetry run python scripts/show_top_messages.py
```

### Newsletter Generation Workflow
```bash
# 1. Verify schedules
poetry run python scripts/verify_schedules.py

# 2. Generate newsletter (use main script)
poetry run python generate_newsletter.py weekly

# 3. Display for review
poetry run python scripts/display_newsletter.py

# 4. Publish to Buttondown
poetry run python scripts/publish_newsletter_to_buttondown.py
```

### Maintenance Workflow
```bash
# 1. Sync new messages
poetry run python scripts/sync_messages.py

# 2. Recalculate engagement
poetry run python scripts/recalculate_engagement.py

# 3. Check top messages
poetry run python scripts/show_top_messages.py
```

---

## Environment Requirements

All scripts require:

### Database Connection:
```env
DATABASE_URL=postgresql://discord_bot:dev_password@localhost:5433/austin_langchain_bot
```

### Discord API (for sync scripts):
```env
DISCORD_TOKEN=your_bot_token
DISCORD_GUILD_ID=your_guild_id
DISCORD_CHANNEL_IDS=ALL
```

### Newsletter Publishing:
```env
BUTTONDOWN_API_KEY=your_buttondown_key
BUTTONDOWN_BASE_URL=https://api.buttondown.email/v1
```

### LangSmith (optional, for tracing):
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=AIMUG-discord-bot
```

---

## Script Development

### Adding New Scripts

1. **Create script file:**
   ```bash
   touch scripts/new_script.py
   chmod +x scripts/new_script.py
   ```

2. **Add shebang and docstring:**
   ```python
   #!/usr/bin/env python3
   """Brief description of what the script does.

   Usage:
       poetry run python scripts/new_script.py
   """
   ```

3. **Import required dependencies:**
   ```python
   import asyncio
   from discord_bot.services.database import db_service
   from discord_bot.core.logging import setup_logging, get_logger

   setup_logging()
   logger = get_logger(__name__)
   ```

4. **Follow async/await patterns:**
   ```python
   async def main():
       await db_service.initialize()
       try:
           # Script logic here
           pass
       finally:
           await db_service.close()

   if __name__ == "__main__":
       asyncio.run(main())
   ```

5. **Update this README** with script documentation

---

## Performance Tips

### Database Optimization
- Use batch operations for bulk updates
- Add indexes for frequently queried fields
- Use connection pooling (already configured)

### Discord API
- Respect rate limits (automatic with discord.py)
- Use bulk operations when available
- Cache channel/user data when possible

### Engagement Calculation
- Calculate incrementally rather than full recalc
- Use background tasks for large datasets
- Cache keyword extraction results

---

## Troubleshooting

### Script Won't Run
```bash
# Check Python path
echo $PYTHONPATH

# Verify poetry environment
poetry env info

# Run with explicit path
PYTHONPATH=/Users/that1guy15/austin_langchain/bots/discord/src poetry run python scripts/script_name.py
```

### Database Connection Issues
```bash
# Test database connection
poetry run python -c "from discord_bot.services.database import db_service; import asyncio; asyncio.run(db_service.initialize()); print('Connected')"

# Check database is running
docker ps | grep postgres

# Restart database
docker-compose -f docker-compose.dev.yml restart postgres
```

### Discord API Errors
- Check bot token is valid
- Verify bot has required permissions
- Check rate limit headers in logs
- Ensure guild ID is correct

---

## Scheduled Execution

Some scripts run automatically via APScheduler:

| Script | Schedule | Cron | Timezone |
|--------|----------|------|----------|
| sync_messages.py | Every 5 minutes | */5 * * * * | UTC |
| calculate_engagement.py | Every 15 minutes | */15 * * * * | UTC |
| Newsletter generation | See schedule | Various | America/Chicago |

**Note:** Manual execution of these scripts is safe and won't conflict with scheduled runs.

---

## See Also

- [../tests/README.md](../tests/README.md) - Test documentation
- [../README.md](../README.md) - Main project documentation
- [../NEWSLETTER_GENERATION.md](../docs/NEWSLETTER_GENERATION.md) - Newsletter generation guide
- [../output/README.md](../output/README.md) - Generated newsletters
