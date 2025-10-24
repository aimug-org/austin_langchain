# Newsletter Generation Guide

This document describes how to manually generate AIMUG newsletters for different timeframes.

## Quick Start

Generate a newsletter using the unified `generate_newsletter.py` script:

```bash
# Generate a daily newsletter (past 24 hours)
poetry run python generate_newsletter.py daily

# Generate a weekly newsletter (past 7 days)
poetry run python generate_newsletter.py weekly

# Generate a bi-weekly newsletter (past 14 days)
poetry run python generate_newsletter.py biweekly

# Generate a monthly newsletter (past 30 days)
poetry run python generate_newsletter.py monthly
```

## Timeframe Configurations

Each timeframe has different parameters optimized for content quality:

| Timeframe | Days | Min Score | Limit | Newsletter Type | Description |
|-----------|------|-----------|-------|-----------------|-------------|
| **daily** | 1 | 0.5 | 10 | DAILY | Best discussions from past 24 hours |
| **weekly** | 7 | 1.0 | 20 | WEEKLY | Top discussions from past week |
| **biweekly** | 14 | 1.0 | 30 | WEEKLY | Top discussions from past 2 weeks |
| **monthly** | 30 | 1.5 | 50 | MONTHLY | Best discussions from past month |

### Parameters Explained

- **Days**: Number of days to look back for discussions
- **Min Score**: Minimum engagement score threshold (filters out low-quality discussions)
- **Limit**: Maximum number of discussions to consider
- **Newsletter Type**: Database enum type (DAILY, WEEKLY, MONTHLY)

## Output

The script will:

1. **Fetch discussions** from the database based on timeframe
2. **Display discussion summary** with engagement metrics
3. **Generate newsletter** using the LangGraph workflow
4. **Save to file**: `output/newsletter_{timeframe}_{YYYYMMDD}.md`
5. **Display full content** in Markdown format

**Note**: All generated newsletters are saved to the `output/` directory, which is automatically created if it doesn't exist.

### Example Output

```
================================================================================
GENERATING WEEKLY NEWSLETTER
================================================================================

Fetching discussions from past 7 days...
  Min engagement score: 1.0
  Limit: 20 discussions

Found 20 discussions

================================================================================
TOP DISCUSSIONS FROM PAST 7 DAYS
================================================================================

1. [💭〡general] Score: 3.66
   Author: username
   Engagement: 1 replies, 7 reactions, 2 participants
   Content: Discussion preview...
   Created: 2025-10-09 13:37:25
   Keywords: ai, machine-learning, python

[... more discussions ...]

================================================================================
GENERATING WEEKLY NEWSLETTER
================================================================================

✅ Newsletter generated successfully!
   ID: 0f058be5-0572-4ccd-abcc-5d2989d2ad04
   Title: AIMUG Weekly - Week of October 11, 2025
   Status: GENERATED
   Word Count: 151
   Sections: 3
   Reading Time: 3 min

📄 Newsletter saved to: output/newsletter_weekly_20251011.md

================================================================================
NEWSLETTER CONTENT (Markdown)
================================================================================

# AIMUG Weekly - Week of October 11, 2025

[... full newsletter content ...]
```

## Newsletter Structure

All newsletters include:

### Header
- Title with branding (e.g., "AIMUG Weekly - Week of October 11, 2025")
- Subtitle describing the timeframe
- Estimated reading time

### Sections
- **Featured Discussions**: Highlights of top conversations
- **Technical Discussions**: Category-based technical content
- **Weekly/Monthly Trends & Insights**: Emerging themes and patterns

### Footer
- **Join the AIMUG Community** section with links:
  - 🌐 Website: https://aimug.org
  - 💬 Discord: https://aimug.org/community
  - 📅 Meetup: https://www.meetup.com/austin-langchain-ai-group/
- Generation metadata (word count, section count)

## Environment Requirements

Ensure you have:

1. **Database connection** configured in `.env`:
   ```
   DATABASE_URL=postgresql://discord_bot:dev_password@localhost:5433/austin_langchain_bot
   ```

2. **LLM API keys** configured:
   ```
   OPENAI_API_KEY=sk-...
   LANGCHAIN_API_KEY=lsv2_pt_...
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=AIMUG-discord-bot
   ```

3. **Dependencies installed**:
   ```bash
   poetry install
   ```

## Troubleshooting

### No discussions found
```
❌ No discussions found with sufficient engagement for the timeframe
```

**Solutions**:
- Lower the `min_score` threshold in the `TIMEFRAME_CONFIG` dictionary
- Increase the `days` parameter to look further back
- Check that messages have been synced from Discord
- Verify engagement metrics have been calculated

### Database connection failed
```
❌ Error: DATABASE_URL not set in environment
```

**Solutions**:
- Ensure `.env` file exists and is loaded
- Verify database is running: `docker-compose up -d postgres`
- Test connection: `poetry run python -m discord_bot.services.database`

### Newsletter generation takes too long
- Generation typically takes 1-2 minutes due to multiple LLM API calls
- The script has a 5-minute timeout
- Check LangSmith for tracing if issues occur

## Automated Scheduling

Newsletters are automatically generated via APScheduler:

| Type | Schedule | Cron Expression |
|------|----------|-----------------|
| Daily | 6:00 AM CST | `0 6 * * *` |
| Weekly | Saturday 8:00 PM CST | `0 20 * * 6` |
| Monthly | 1st day 8:00 PM CST | `0 20 1 * *` |

Configure schedules in `.env`:
```
NEWSLETTER_SCHEDULE_DAILY=0 6 * * *
NEWSLETTER_SCHEDULE_WEEKLY=0 20 * * 6
NEWSLETTER_SCHEDULE_MONTHLY=0 20 1 * *
TIMEZONE=America/Chicago
```

## Advanced Usage

### Custom Timeframe Parameters

You can modify `generate_newsletter.py` to add custom timeframes:

```python
TIMEFRAME_CONFIG = {
    "custom": {
        "days": 3,
        "min_score": 0.8,
        "limit": 15,
        "newsletter_type": NewsletterType.WEEKLY,
        "display_name": "Custom"
    }
}
```

Then add `"custom"` to the argparse choices.

### Testing Newsletter Workflow

To test the newsletter workflow without database storage:

```bash
cd discord/src
PYTHONPATH=/Users/that1guy15/austin_langchain/bots/discord/src poetry run python -c "
from discord_bot.agents.newsletter_workflow import newsletter_workflow
from discord_bot.agents.state import DiscussionData
from datetime import datetime
import asyncio

async def test():
    discussions = [
        DiscussionData(
            message_id='123',
            content='Test discussion',
            author='test_user',
            channel='general',
            engagement_score=5.0,
            reply_count=3,
            reaction_count=5,
            participants=3,
            keywords=['test'],
            category=['technical'],
            created_at=datetime.now()
        )
    ]

    result = await newsletter_workflow.generate_newsletter(
        discussions=discussions,
        newsletter_type='weekly',
        target_date=datetime.now().strftime('%Y-%m-%d')
    )

    print(result.get('formatted_content', {}).get('markdown', 'No markdown'))

asyncio.run(test())
"
```

## Related Documentation

- [CLOUDFLARE_DEPLOYMENT_ANALYSIS.md](../CLOUDFLARE_DEPLOYMENT_ANALYSIS.md) - Deployment options
- [README.md](../README.md) - Main project documentation
- [src/discord_bot/agents/newsletter_workflow.py](../src/discord_bot/agents/newsletter_workflow.py) - LangGraph workflow
- [src/discord_bot/services/newsletter_service.py](../src/discord_bot/services/newsletter_service.py) - Newsletter service

## Support

For issues or questions:
- GitHub Issues: https://github.com/aimug-org/austin_langchain
- Discord: https://aimug.org/community
- Meetup: https://www.meetup.com/austin-langchain-ai-group/
