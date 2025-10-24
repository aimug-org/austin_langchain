# Newsletter Output Directory

This directory contains all generated AIMUG newsletters.

## File Naming Convention

Generated newsletters follow this naming pattern:
```
newsletter_{timeframe}_{YYYYMMDD}.md
```

### Examples:
- `newsletter_daily_20251011.md` - Daily newsletter for October 11, 2025
- `newsletter_weekly_20251011.md` - Weekly newsletter for the week of October 11, 2025
- `newsletter_biweekly_20251011.md` - Bi-weekly newsletter for the period ending October 11, 2025
- `newsletter_monthly_20251011.md` - Monthly newsletter for October 2025

## Newsletter Formats

All newsletters are saved in **Markdown format** (`.md`) and include:

- **Title** with AIMUG branding
- **Subtitle** describing the timeframe
- **Reading time** estimate
- **Featured Discussions** section
- **Technical Discussions** by category
- **Trends & Insights** section
- **Community links** (Discord, Meetup, Website)
- **Generation metadata** (word count, section count)

## Viewing Newsletters

You can view newsletters using any Markdown viewer or editor:

```bash
# View in terminal with glow (if installed)
glow newsletter_weekly_20251011.md

# View in VS Code
code newsletter_weekly_20251011.md

# View in your browser (convert to HTML first)
pandoc newsletter_weekly_20251011.md -o newsletter_weekly_20251011.html
open newsletter_weekly_20251011.html
```

## Automated Publishing

Newsletters in this directory are for **local preview and backup**.

The automated publishing flow is:
1. Newsletter generated and saved here
2. Content stored in database
3. Published to Buttondown via API (if enabled)
4. Distributed to email subscribers

## Storage Notes

- This directory is **gitignored** by default
- Files are safe to delete (original content is stored in the database)
- Newsletters can be regenerated using `generate_newsletter.py`
- Consider archiving old newsletters periodically

## See Also

- [NEWSLETTER_GENERATION.md](../docs/NEWSLETTER_GENERATION.md) - Complete generation guide
- [README.md](../README.md) - Main project documentation
