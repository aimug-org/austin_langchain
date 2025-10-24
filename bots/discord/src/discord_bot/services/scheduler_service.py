"""Scheduler service for automated newsletter generation."""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, time, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.job import Job
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
import pytz

from discord_bot.core.config import settings
from discord_bot.core.logging import get_logger
from discord_bot.services.newsletter_service import newsletter_service
from discord_bot.services.buttondown_service import buttondown_service
from discord_bot.models.newsletter_models import NewsletterType

logger = get_logger(__name__)


class SchedulerService:
    """Service for scheduling automated newsletter generation and publishing."""
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.timezone = pytz.timezone(settings.timezone)
        self.is_running = False
        self._job_callbacks: Dict[str, Callable] = {}
    
    async def initialize(self):
        """Initialize the scheduler service."""
        # Configure scheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=self.timezone
        )
        
        # Add event listeners - import event constants
        from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self._job_missed, EVENT_JOB_MISSED)
        
        logger.info("Scheduler service initialized", extra={
            "timezone": settings.timezone
        })
    
    async def start(self):
        """Start the scheduler service."""
        if not self.scheduler:
            await self.initialize()
        
        self.scheduler.start()
        self.is_running = True
        
        # Schedule default newsletter jobs
        await self._schedule_default_jobs()
        
        logger.info("Scheduler service started", extra={
            "jobs_count": len(self.scheduler.get_jobs())
        })
    
    async def stop(self):
        """Stop the scheduler service."""
        if self.scheduler and self.is_running:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Scheduler service stopped")
    
    async def _schedule_default_jobs(self):
        """Schedule default newsletter generation jobs."""
        # Daily newsletter - 6 AM CST
        await self.schedule_newsletter_generation(
            newsletter_type=NewsletterType.DAILY,
            cron_expression=settings.newsletter_schedule_daily,
            job_id="daily_newsletter",
            auto_publish=False  # Don't auto-publish daily
        )

        # Weekly newsletter - Saturday 8 PM CST
        await self.schedule_newsletter_generation(
            newsletter_type=NewsletterType.WEEKLY,
            cron_expression=settings.newsletter_schedule_weekly,
            job_id="weekly_newsletter",
            auto_publish=True  # Auto-publish weekly to Buttondown
        )

        # Monthly newsletter - 1st day of month 8 PM CST
        await self.schedule_newsletter_generation(
            newsletter_type=NewsletterType.MONTHLY,
            cron_expression=settings.newsletter_schedule_monthly,
            job_id="monthly_newsletter",
            auto_publish=True  # Auto-publish monthly to Buttondown
        )

        # Maintenance job - daily cleanup at 2 AM
        await self.schedule_maintenance_job()
    
    async def schedule_newsletter_generation(
        self,
        newsletter_type: NewsletterType,
        cron_expression: str,
        job_id: str,
        auto_publish: bool = False
    ):
        """Schedule newsletter generation job."""
        try:
            # Parse cron expression (format: minute hour day month day_of_week)
            cron_parts = cron_expression.split()
            if len(cron_parts) != 5:
                raise ValueError(f"Invalid cron expression: {cron_expression}")
            
            minute, hour, day, month, day_of_week = cron_parts
            
            # Create cron trigger
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day if day != '*' else None,
                month=month if month != '*' else None,
                day_of_week=day_of_week if day_of_week != '*' else None,
                timezone=self.timezone
            )
            
            # Add job
            job = self.scheduler.add_job(
                func=self._generate_newsletter_job,
                trigger=trigger,
                args=[newsletter_type, auto_publish],
                id=job_id,
                name=f"Generate {newsletter_type.value} newsletter",
                replace_existing=True
            )
            
            logger.info(f"Scheduled {newsletter_type.value} newsletter generation", extra={
                "job_id": job_id,
                "cron": cron_expression,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            })
            
        except Exception as e:
            logger.error(f"Failed to schedule newsletter generation: {e}")
            raise
    
    async def schedule_one_time_newsletter(
        self,
        newsletter_type: NewsletterType,
        scheduled_time: datetime,
        auto_publish: bool = False
    ) -> str:
        """Schedule a one-time newsletter generation."""
        job_id = f"onetime_{newsletter_type.value}_{int(scheduled_time.timestamp())}"
        
        try:
            trigger = DateTrigger(run_date=scheduled_time, timezone=self.timezone)
            
            job = self.scheduler.add_job(
                func=self._generate_newsletter_job,
                trigger=trigger,
                args=[newsletter_type, auto_publish],
                id=job_id,
                name=f"One-time {newsletter_type.value} newsletter",
                replace_existing=True
            )
            
            logger.info(f"Scheduled one-time newsletter", extra={
                "job_id": job_id,
                "scheduled_time": scheduled_time.isoformat(),
                "type": newsletter_type.value
            })
            
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to schedule one-time newsletter: {e}")
            raise
    
    async def schedule_maintenance_job(self):
        """Schedule daily maintenance job."""
        try:
            trigger = CronTrigger(
                hour=2,
                minute=0,
                timezone=self.timezone
            )
            
            self.scheduler.add_job(
                func=self._maintenance_job,
                trigger=trigger,
                id="daily_maintenance",
                name="Daily maintenance",
                replace_existing=True
            )
            
            logger.info("Scheduled daily maintenance job")
            
        except Exception as e:
            logger.error(f"Failed to schedule maintenance job: {e}")
    
    async def _generate_newsletter_job(
        self,
        newsletter_type: NewsletterType,
        auto_publish: bool = False
    ):
        """Execute newsletter generation job."""
        logger.info(f"Starting scheduled {newsletter_type.value} newsletter generation")
        
        try:
            # Generate newsletter
            newsletter = await newsletter_service.generate_newsletter(
                newsletter_type=newsletter_type,
                force=False  # Don't force if one already exists for today
            )
            
            if not newsletter:
                logger.warning(f"Failed to generate {newsletter_type.value} newsletter")
                return
            
            logger.info(f"Successfully generated {newsletter_type.value} newsletter", extra={
                "newsletter_id": str(newsletter.id),
                "title": newsletter.title
            })
            
            # Auto-publish if requested
            if auto_publish:
                try:
                    draft_id = await buttondown_service.create_newsletter_from_model(
                        newsletter=newsletter,
                        publish_immediately=True
                    )
                    
                    if draft_id:
                        logger.info(f"Auto-published newsletter", extra={
                            "newsletter_id": str(newsletter.id),
                            "buttondown_draft_id": draft_id
                        })
                    else:
                        logger.warning(f"Failed to auto-publish newsletter {newsletter.id}")
                        
                except Exception as e:
                    logger.error(f"Error auto-publishing newsletter: {e}")
            
        except Exception as e:
            logger.error(f"Error in newsletter generation job: {e}")
            # Could add notification/alerting here
    
    async def _maintenance_job(self):
        """Execute daily maintenance tasks."""
        logger.info("Starting daily maintenance")
        
        try:
            # Clean up old newsletter generation logs
            # This would involve database cleanup operations
            logger.info("Maintenance completed successfully")
            
        except Exception as e:
            logger.error(f"Error in maintenance job: {e}")
    
    def _job_executed(self, event):
        """Handle job executed event."""
        logger.info("Job executed successfully", extra={
            "job_id": event.job_id,
            "scheduled_run_time": event.scheduled_run_time.isoformat() if event.scheduled_run_time else None
        })
    
    def _job_error(self, event):
        """Handle job error event."""
        logger.error("Job execution failed", extra={
            "job_id": event.job_id,
            "error": str(event.exception),
            "traceback": event.traceback
        })
    
    def _job_missed(self, event):
        """Handle job missed event."""
        logger.warning("Job execution missed", extra={
            "job_id": event.job_id,
            "scheduled_run_time": event.scheduled_run_time.isoformat() if event.scheduled_run_time else None
        })
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get list of all scheduled jobs."""
        if not self.scheduler:
            return []
        
        jobs = []
        for job in self.scheduler.get_jobs():
            job_info = {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
                "func_name": job.func.__name__ if hasattr(job.func, '__name__') else str(job.func)
            }
            jobs.append(job_info)
        
        return jobs
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job."""
        if not self.scheduler:
            return None
        
        job = self.scheduler.get_job(job_id)
        if not job:
            return None
        
        return {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
            "func_name": job.func.__name__ if hasattr(job.func, '__name__') else str(job.func),
            "max_instances": job.max_instances,
            "misfire_grace_time": job.misfire_grace_time
        }
    
    async def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job."""
        if not self.scheduler:
            return False
        
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}")
            return False
    
    async def resume_job(self, job_id: str) -> bool:
        """Resume a paused job."""
        if not self.scheduler:
            return False
        
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
            return False
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job."""
        if not self.scheduler:
            return False
        
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Cancelled job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
    
    async def reschedule_job(
        self,
        job_id: str,
        new_cron_expression: str
    ) -> bool:
        """Reschedule a job with new cron expression."""
        if not self.scheduler:
            return False
        
        try:
            # Parse new cron expression
            cron_parts = new_cron_expression.split()
            if len(cron_parts) != 5:
                raise ValueError(f"Invalid cron expression: {new_cron_expression}")
            
            minute, hour, day, month, day_of_week = cron_parts
            
            # Create new trigger
            new_trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day if day != '*' else None,
                month=month if month != '*' else None,
                day_of_week=day_of_week if day_of_week != '*' else None,
                timezone=self.timezone
            )
            
            # Reschedule job
            self.scheduler.reschedule_job(job_id, trigger=new_trigger)
            
            logger.info(f"Rescheduled job {job_id}", extra={
                "new_cron": new_cron_expression
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to reschedule job {job_id}: {e}")
            return False
    
    async def trigger_job_now(self, job_id: str) -> bool:
        """Manually trigger a job to run now."""
        if not self.scheduler:
            return False
        
        try:
            job = self.scheduler.get_job(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return False
            
            # Create a one-time job with the same function
            immediate_job_id = f"{job_id}_immediate_{int(datetime.now().timestamp())}"
            
            self.scheduler.add_job(
                func=job.func,
                args=job.args,
                kwargs=job.kwargs,
                id=immediate_job_id,
                name=f"Immediate: {job.name}",
            )
            
            logger.info(f"Triggered job {job_id} to run immediately")
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger job {job_id}: {e}")
            return False
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        return {
            "is_running": self.is_running,
            "scheduler_initialized": bool(self.scheduler),
            "timezone": settings.timezone,
            "jobs_count": len(self.scheduler.get_jobs()) if self.scheduler else 0,
            "scheduler_state": self.scheduler.state if self.scheduler else None
        }


# Global scheduler service instance
scheduler_service = SchedulerService()