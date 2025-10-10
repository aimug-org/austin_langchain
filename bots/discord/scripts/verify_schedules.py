#!/usr/bin/env python3
"""Verify newsletter schedules are configured correctly."""

import asyncio
from datetime import datetime
from discord_bot.services.scheduler_service import scheduler_service
from discord_bot.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def verify_schedules():
    """Verify all newsletter schedules."""
    print("\n" + "="*80)
    print("NEWSLETTER SCHEDULE VERIFICATION")
    print("="*80 + "\n")

    # Initialize and start scheduler
    await scheduler_service.initialize()
    await scheduler_service.start()

    # Get scheduler status
    status = scheduler_service.get_scheduler_status()
    print("Scheduler Status:")
    print(f"  Running: {status['is_running']}")
    print(f"  Initialized: {status['scheduler_initialized']}")
    print(f"  Timezone: {status['timezone']}")
    print(f"  Total Jobs: {status['jobs_count']}")
    print()

    # Get all scheduled jobs
    jobs = scheduler_service.get_scheduled_jobs()

    print(f"Scheduled Newsletter Jobs: {len([j for j in jobs if 'newsletter' in j['id']])}")
    print("="*80)
    print()

    # Display each newsletter job
    newsletter_jobs = [j for j in jobs if 'newsletter' in j['id']]

    for job in newsletter_jobs:
        print(f"📧 {job['name']}")
        print(f"   ID: {job['id']}")
        print(f"   Trigger: {job['trigger']}")

        if job['next_run_time']:
            next_run = datetime.fromisoformat(job['next_run_time'])
            print(f"   Next Run: {next_run.strftime('%A, %B %d, %Y at %I:%M %p %Z')}")
            print(f"             ({job['next_run_time']})")
        else:
            print(f"   Next Run: Not scheduled")

        print()

    # Display expected schedules
    print("="*80)
    print("Expected Schedules:")
    print("="*80)
    print()

    print("📅 Weekly Newsletter:")
    print("   Every Saturday at 8:00 PM CST")
    print("   Cron: 0 20 * * 6")
    print("   Auto-Publish: YES")
    print()

    print("📅 Monthly Newsletter:")
    print("   First day of every month at 8:00 PM CST")
    print("   Cron: 0 20 1 * *")
    print("   Auto-Publish: YES")
    print()

    print("📅 Daily Newsletter:")
    print("   Every day at 6:00 AM CST")
    print("   Cron: 0 6 * * *")
    print("   Auto-Publish: NO (draft only)")
    print()

    # Verify correct jobs exist
    print("="*80)
    print("Verification Results:")
    print("="*80)
    print()

    job_ids = [j['id'] for j in jobs]

    checks = [
        ('weekly_newsletter', 'Weekly Newsletter'),
        ('monthly_newsletter', 'Monthly Newsletter'),
        ('daily_newsletter', 'Daily Newsletter (optional)'),
    ]

    all_passed = True
    for job_id, name in checks:
        if job_id in job_ids:
            print(f"✅ {name} - Configured")
        else:
            print(f"❌ {name} - Missing")
            all_passed = False

    print()

    if all_passed:
        print("="*80)
        print("✅ ALL SCHEDULES VERIFIED SUCCESSFULLY")
        print("="*80)
    else:
        print("="*80)
        print("⚠️  SOME SCHEDULES ARE MISSING")
        print("="*80)

    print()
    print("To start the scheduler in production, run:")
    print("  poetry run python -m discord_bot.main")
    print()

    # Stop scheduler
    await scheduler_service.stop()


if __name__ == "__main__":
    asyncio.run(verify_schedules())
