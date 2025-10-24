"""Newsletter service for managing newsletter generation and storage."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from discord_bot.core.config import settings
from discord_bot.core.logging import get_logger
from discord_bot.services.database import db_service
from discord_bot.services.engagement_service import engagement_service
from discord_bot.agents.newsletter_workflow import newsletter_workflow
from discord_bot.agents.state import DiscussionData
from discord_bot.models.newsletter_models import (
    Newsletter, NewsletterType, NewsletterStatus, NewsletterSection,
    NewsletterDiscussion, NewsletterGenerationLog
)
from discord_bot.models.discord_models import DiscordMessage, EngagementMetrics

logger = get_logger(__name__)


class NewsletterService:
    """Service for managing newsletter generation and storage."""
    
    def __init__(self):
        self._generation_locks: Dict[str, asyncio.Lock] = {}
    
    async def generate_newsletter(
        self,
        newsletter_type: NewsletterType = NewsletterType.DAILY,
        force: bool = False,
        target_date: Optional[str] = None
    ) -> Optional[Newsletter]:
        """Generate a newsletter of the specified type."""
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        # Create a lock key for this generation request
        lock_key = f"{newsletter_type}_{target_date}"
        if lock_key not in self._generation_locks:
            self._generation_locks[lock_key] = asyncio.Lock()
        
        async with self._generation_locks[lock_key]:
            return await self._generate_newsletter_locked(newsletter_type, force, target_date)
    
    async def _generate_newsletter_locked(
        self,
        newsletter_type: NewsletterType,
        force: bool,
        target_date: str
    ) -> Optional[Newsletter]:
        """Generate newsletter with exclusive lock."""
        logger.info("Starting newsletter generation", extra={
            "type": newsletter_type,
            "target_date": target_date,
            "force": force
        })
        
        # Check if newsletter already exists
        if not force:
            existing = await self._check_existing_newsletter(newsletter_type, target_date)
            if existing:
                logger.info("Newsletter already exists for date", extra={
                    "newsletter_id": str(existing.id),
                    "status": existing.status
                })
                return existing
        
        # Create newsletter record
        newsletter = await self._create_newsletter_record(newsletter_type, target_date)
        
        try:
            # Update status to generating
            await self._update_newsletter_status(newsletter.id, NewsletterStatus.GENERATING)
            
            # Get discussions for newsletter
            discussions = await self._get_discussions_for_newsletter(newsletter_type)
            
            if not discussions:
                logger.warning("No discussions found for newsletter generation")
                await self._update_newsletter_status(newsletter.id, NewsletterStatus.FAILED, "No discussions found")
                return None
            
            # Log generation start
            await self._log_generation_step(
                newsletter.id,
                "generation_start",
                "started",
                {"discussion_count": len(discussions)}
            )
            
            # Convert to DiscussionData objects
            discussion_data = []
            for d in discussions:
                discussion_obj = DiscussionData(
                    message_id=d[0].message_id,
                    content=d[0].content,
                    author=d[0].author.username if d[0].author else "Unknown",
                    channel=d[0].channel.name if d[0].channel else "Unknown",
                    channel_id=d[0].channel.channel_id if d[0].channel else "",
                    engagement_score=d[1].engagement_score,
                    reply_count=d[1].reply_count,
                    reaction_count=d[1].reaction_count,
                    participants=d[1].discussion_participants,
                    keywords=d[1].extracted_keywords or [],
                    category=d[1].topic_categories or ["general"],
                    created_at=d[0].created_at
                )
                discussion_data.append(discussion_obj)
            
            # Generate newsletter using workflow
            workflow_result = await newsletter_workflow.generate_newsletter(
                discussions=discussion_data,
                newsletter_type=newsletter_type.value,
                target_date=target_date
            )
            
            # Store newsletter content
            await self._store_newsletter_content(newsletter.id, workflow_result)
            
            # Update status to generated
            await self._update_newsletter_status(newsletter.id, NewsletterStatus.GENERATED)
            
            # Log generation completion
            await self._log_generation_step(
                newsletter.id,
                "generation_complete",
                "completed",
                {
                    "word_count": workflow_result.get("quality_metrics", {}).get("total_word_count", 0),
                    "section_count": len(workflow_result.get("draft_sections", [])),
                    "errors": workflow_result.get("errors", [])
                }
            )
            
            logger.info("Newsletter generation completed", extra={
                "newsletter_id": str(newsletter.id),
                "word_count": workflow_result.get("quality_metrics", {}).get("total_word_count", 0)
            })
            
            # Reload with updated data
            return await self._get_newsletter_by_id(newsletter.id)
            
        except Exception as e:
            logger.error("Newsletter generation failed", extra={
                "newsletter_id": str(newsletter.id),
                "error": str(e)
            })
            
            await self._update_newsletter_status(
                newsletter.id, 
                NewsletterStatus.FAILED, 
                f"Generation failed: {str(e)}"
            )
            
            await self._log_generation_step(
                newsletter.id,
                "generation_error",
                "failed",
                {"error": str(e), "error_type": type(e).__name__}
            )
            
            return None
    
    async def _check_existing_newsletter(
        self, 
        newsletter_type: NewsletterType, 
        target_date: str
    ) -> Optional[Newsletter]:
        """Check if newsletter already exists for the given date."""
        async with db_service.get_session() as session:
            date_obj = datetime.fromisoformat(target_date).date()
            
            result = await session.execute(
                select(Newsletter)
                .where(and_(
                    Newsletter.newsletter_type == newsletter_type,
                    Newsletter.created_at >= datetime.combine(date_obj, datetime.min.time()),
                    Newsletter.created_at < datetime.combine(date_obj, datetime.max.time())
                ))
                .order_by(Newsletter.created_at.desc())
                .limit(1)
            )
            
            return result.scalar_one_or_none()
    
    async def _create_newsletter_record(
        self, 
        newsletter_type: NewsletterType, 
        target_date: str
    ) -> Newsletter:
        """Create a new newsletter record."""
        async with db_service.get_session() as session:
            # Generate title based on type and date
            date_obj = datetime.fromisoformat(target_date)

            if newsletter_type == NewsletterType.DAILY:
                title = f"AIMUG Daily - {date_obj.strftime('%B %d, %Y')}"
                subtitle = "Today's highlights from the Austin AI/ML User Group community"
            elif newsletter_type == NewsletterType.WEEKLY:
                title = f"AIMUG Weekly - Week of {date_obj.strftime('%B %d, %Y')}"
                subtitle = "This week's top discussions and insights from the Austin AI/ML community"
            elif newsletter_type == NewsletterType.MONTHLY:
                title = f"AIMUG Monthly - {date_obj.strftime('%B %Y')}"
                subtitle = "This month's top discussions and insights from the Austin AI/ML community"
            else:
                title = f"AIMUG Newsletter - {date_obj.strftime('%B %d, %Y')}"
                subtitle = "Community highlights and technical insights from Austin AI/ML User Group"
            
            newsletter = Newsletter(
                title=title,
                subtitle=subtitle,
                newsletter_type=newsletter_type,
                status=NewsletterStatus.PENDING,
                scheduled_for=date_obj
            )
            
            session.add(newsletter)
            await session.commit()
            
            logger.info("Created newsletter record", extra={
                "newsletter_id": str(newsletter.id),
                "title": title
            })
            
            return newsletter
    
    async def _get_discussions_for_newsletter(
        self,
        newsletter_type: NewsletterType
    ) -> List[tuple]:
        """Get discussions for newsletter generation."""
        # Determine time period and parameters based on newsletter type
        if newsletter_type == NewsletterType.DAILY:
            days = 1
            min_score = settings.min_engagement_score
            limit = 10  # Fewer for daily
        elif newsletter_type == NewsletterType.WEEKLY:
            days = 7
            min_score = settings.min_engagement_score
            limit = 20  # Moderate for weekly
        elif newsletter_type == NewsletterType.MONTHLY:
            days = 30
            min_score = 1.5  # Higher threshold for monthly
            limit = 50  # More discussions for monthly
        else:
            days = 7
            min_score = settings.min_engagement_score
            limit = 20

        # Get top discussions from engagement service
        discussions = await engagement_service.get_top_discussions(
            days=days,
            min_score=min_score,
            limit=limit
        )

        return discussions
    
    async def _store_newsletter_content(self, newsletter_id: str, workflow_result: Dict[str, Any]) -> None:
        """Store newsletter content and sections."""
        async with db_service.get_session() as session:
            # Get newsletter
            result = await session.execute(
                select(Newsletter).where(Newsletter.id == newsletter_id)
            )
            newsletter = result.scalar_one()

            # Store main content
            draft = workflow_result.get("newsletter_draft")
            # Check if formatted_content exists in workflow result, if not generate it
            formatted_content = workflow_result.get("formatted_content")
            quality_metrics = workflow_result.get("quality_metrics", {})

            if draft:
                # If formatted_content is not in workflow result, we need to generate it from draft
                if not formatted_content:
                    from discord_bot.agents.formatter_agent import FormatterAgent
                    formatter = FormatterAgent()
                    # Generate formatted content from the draft
                    from discord_bot.agents.state import NewsletterDraft, NewsletterSection

                    # Reconstruct sections with all required fields
                    sections = []
                    for section_data in draft.get("sections", []):
                        section = NewsletterSection(
                            section_type=section_data.get("section_type", "general"),
                            title=section_data.get("title", "Untitled"),
                            content=section_data.get("content", ""),
                            discussions=section_data.get("discussions", []),
                            word_count=section_data.get("word_count", 0)
                        )
                        sections.append(section)

                    draft_obj = NewsletterDraft(
                        title=draft.get("title", ""),
                        subtitle=draft.get("subtitle", ""),
                        sections=sections,
                        total_word_count=draft.get("total_word_count", 0),
                        estimated_read_time=draft.get("estimated_read_time", 1),
                        featured_discussions=draft.get("featured_discussions", []),
                        generation_metadata=draft.get("generation_metadata", {})
                    )

                    html_content = formatter._format_as_html(draft_obj)
                    markdown_content = formatter._format_as_markdown(draft_obj)
                    text_content = formatter._format_as_text(draft_obj)

                    newsletter.content_html = html_content
                    newsletter.content_markdown = markdown_content
                    newsletter.content_text = text_content
                else:
                    newsletter.content_html = formatted_content.get("html")
                    newsletter.content_markdown = formatted_content.get("markdown")
                    newsletter.content_text = formatted_content.get("text")

                newsletter.word_count = draft.get("total_word_count", 0)
                newsletter.estimated_read_time = draft.get("estimated_read_time", 1)

                # Update generation metadata
                newsletter.generated_at = datetime.now(timezone.utc)
                newsletter.quality_score = quality_metrics.get("overall_score", 0.8)
            
            # Store sections - use sections from the draft object which is correctly structured
            if draft and "sections" in draft:
                from discord_bot.models.newsletter_models import NewsletterSection as DBNewsletterSection
                sections = draft["sections"]
                for i, section_data in enumerate(sections):
                    # Sections from draft are dictionaries with section_type, title, content, discussions, word_count
                    section = DBNewsletterSection(
                        newsletter_id=newsletter.id,
                        section_type=section_data.get("section_type", "general"),
                        title=section_data.get("title", f"Section {i+1}"),
                        order_index=i,
                        content_html=f"<p>{section_data.get('content', '')}</p>",
                        content_markdown=section_data.get("content", ""),
                        summary=section_data.get("content", "")[:200] + "..." if len(section_data.get("content", "")) > 200 else section_data.get("content", ""),
                        generated_by_agent="NewsletterWorkflow"
                    )
                    session.add(section)
            
            # TODO: Store featured discussions
            # Skipping for now - message_id is Discord snowflake (string) not UUID
            # technical_analysis = workflow_result.get("technical_analysis", {})
            # for message_id, analysis in technical_analysis.items():
            #     ...
            
            await session.commit()
    
    async def _update_newsletter_status(
        self, 
        newsletter_id: str, 
        status: NewsletterStatus,
        error_message: Optional[str] = None
    ) -> None:
        """Update newsletter status."""
        async with db_service.get_session() as session:
            result = await session.execute(
                select(Newsletter).where(Newsletter.id == newsletter_id)
            )
            newsletter = result.scalar_one()
            
            newsletter.status = status
            if error_message:
                newsletter.error_message = error_message
            
            await session.commit()
    
    async def _get_newsletter_by_id(self, newsletter_id: str) -> Optional[Newsletter]:
        """Get newsletter by ID with all relationships."""
        async with db_service.get_session() as session:
            result = await session.execute(
                select(Newsletter)
                .options(
                    selectinload(Newsletter.sections),
                    selectinload(Newsletter.featured_discussions),
                    selectinload(Newsletter.generation_logs)
                )
                .where(Newsletter.id == newsletter_id)
            )
            return result.scalar_one_or_none()
    
    async def _log_generation_step(
        self,
        newsletter_id: str,
        step_name: str,
        status: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Log a generation step."""
        async with db_service.get_session() as session:
            log_entry = NewsletterGenerationLog(
                newsletter_id=newsletter_id,
                step_name=step_name,
                status=status,
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc) if status in ["completed", "failed"] else None,
                metadata=metadata or {}
            )
            session.add(log_entry)
            await session.commit()
    
    async def get_recent_newsletters(
        self,
        days: int = 30,
        newsletter_type: Optional[NewsletterType] = None,
        limit: int = 20
    ) -> List[Newsletter]:
        """Get recent newsletters."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        async with db_service.get_session() as session:
            query = (
                select(Newsletter)
                .where(Newsletter.created_at >= cutoff_date)
                .order_by(Newsletter.created_at.desc())
                .limit(limit)
            )
            
            if newsletter_type:
                query = query.where(Newsletter.newsletter_type == newsletter_type)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_newsletter_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get newsletter generation statistics."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        async with db_service.get_session() as session:
            # Total newsletters
            total_result = await session.execute(
                select(Newsletter).where(Newsletter.created_at >= cutoff_date)
            )
            newsletters = total_result.scalars().all()
            
            # Group by status
            status_counts = {}
            total_word_count = 0
            
            for newsletter in newsletters:
                status = newsletter.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
                if newsletter.word_count:
                    total_word_count += newsletter.word_count
            
            return {
                "period_days": days,
                "total_newsletters": len(newsletters),
                "status_breakdown": status_counts,
                "total_word_count": total_word_count,
                "average_word_count": total_word_count / len(newsletters) if newsletters else 0,
                "success_rate": status_counts.get("generated", 0) / len(newsletters) if newsletters else 0
            }


# Global newsletter service instance
newsletter_service = NewsletterService()