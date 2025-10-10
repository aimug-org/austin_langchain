"""Engagement analysis service for Discord discussions."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import selectinload

from discord_bot.core.config import settings
from discord_bot.core.logging import get_logger
from discord_bot.services.database import db_service
from discord_bot.models.discord_models import (
    DiscordMessage, DiscordUser, DiscordChannel, EngagementMetrics, MessageReaction
)

logger = get_logger(__name__)


class EngagementAnalyzer:
    """Analyzes engagement metrics for Discord discussions."""
    
    def __init__(self):
        self._keywords_cache: Dict[str, List[str]] = {}
    
    async def calculate_engagement_score(
        self,
        message_id: str,
        reply_count: int = 0,
        reaction_count: int = 0,
        unique_reactors: int = 0,
        discussion_participants: int = 1,
        thread_depth: int = 0,
        message_age_hours: float = 0,
        content_keywords: List[str] = None
    ) -> float:
        """Calculate comprehensive engagement score for a message."""
        
        # Base weights for different engagement factors
        weights = {
            'reply': 0.35,
            'reaction': 0.20,
            'unique_reactors': 0.25,
            'thread_depth': 0.10,
            'recency': 0.10,
            'keyword_bonus': 0.05  # Bonus for technical keywords
        }
        
        # Recency decay factor (messages lose engagement value over time)
        max_age_hours = 168  # 7 days
        recency_multiplier = max(0.1, 1.0 - (message_age_hours / max_age_hours))
        
        # Calculate base score components
        reply_score = reply_count * weights['reply']
        reaction_score = reaction_count * weights['reaction']
        reactor_score = unique_reactors * weights['unique_reactors']
        thread_score = min(thread_depth, 10) * weights['thread_depth']  # Cap thread depth
        recency_score = recency_multiplier * weights['recency'] * 10
        
        # Keyword bonus for technical discussions
        keyword_bonus = 0
        if content_keywords:
            technical_keywords = self._get_technical_keywords()
            matching_keywords = set(content_keywords) & set(technical_keywords)
            keyword_bonus = len(matching_keywords) * weights['keyword_bonus']
        
        # Calculate final score
        total_score = (
            reply_score + 
            reaction_score + 
            reactor_score + 
            thread_score + 
            recency_score + 
            keyword_bonus
        )
        
        # Apply discussion size multiplier
        if discussion_participants > 3:
            total_score *= min(1.5, 1.0 + (discussion_participants - 3) * 0.1)
        
        return round(total_score, 2)
    
    async def calculate_trending_score(
        self,
        engagement_score: float,
        recent_activity_hours: float,
        velocity_factor: float = 1.0
    ) -> float:
        """Calculate trending score based on recent activity velocity."""
        
        # Trending is based on recent engagement and velocity
        if recent_activity_hours > 24:
            return 0.0  # Not trending if no recent activity
        
        # Higher score for more recent activity
        recency_boost = max(0.1, 1.0 - (recent_activity_hours / 24))
        
        # Calculate trending score
        trending_score = engagement_score * recency_boost * velocity_factor
        
        return round(trending_score, 2)
    
    async def update_message_engagement(self, message_id: str) -> Optional[float]:
        """Update engagement metrics for a specific message."""
        async with db_service.get_session() as session:
            try:
                # Get message with relationships
                result = await session.execute(
                    select(DiscordMessage)
                    .options(
                        selectinload(DiscordMessage.reactions),
                        selectinload(DiscordMessage.engagement_metrics)
                    )
                    .where(DiscordMessage.message_id == message_id)
                )
                message = result.scalar_one_or_none()
                
                if not message:
                    logger.warning(f"Message {message_id} not found for engagement update")
                    return None
                
                # Count direct replies
                reply_result = await session.execute(
                    select(func.count(DiscordMessage.id))
                    .where(DiscordMessage.parent_message_id == message_id)
                )
                reply_count = reply_result.scalar() or 0
                
                # Count thread messages
                thread_result = await session.execute(
                    select(func.count(DiscordMessage.id))
                    .where(and_(
                        DiscordMessage.thread_id.isnot(None),
                        or_(
                            DiscordMessage.message_id == message_id,
                            DiscordMessage.parent_message_id == message_id
                        )
                    ))
                )
                thread_depth = thread_result.scalar() or 0
                
                # Analyze reactions
                reaction_count = len(message.reactions)
                unique_reactors = len(set(r.user_id for r in message.reactions))
                
                # Count unique participants in discussion
                participant_result = await session.execute(
                    select(func.count(func.distinct(DiscordMessage.author_id)))
                    .where(or_(
                        DiscordMessage.message_id == message_id,
                        DiscordMessage.parent_message_id == message_id,
                        and_(
                            DiscordMessage.thread_id.isnot(None),
                            DiscordMessage.thread_id == message.thread_id
                        )
                    ))
                )
                discussion_participants = participant_result.scalar() or 1
                
                # Calculate message age
                message_age = datetime.now(timezone.utc) - message.created_at
                message_age_hours = message_age.total_seconds() / 3600
                
                # Extract keywords from content
                content_keywords = self._extract_keywords(message.content)
                
                # Calculate engagement score
                engagement_score = await self.calculate_engagement_score(
                    message_id=message_id,
                    reply_count=reply_count,
                    reaction_count=reaction_count,
                    unique_reactors=unique_reactors,
                    discussion_participants=discussion_participants,
                    thread_depth=thread_depth,
                    message_age_hours=message_age_hours,
                    content_keywords=content_keywords
                )
                
                # Find most recent activity
                last_activity_result = await session.execute(
                    select(func.max(DiscordMessage.created_at))
                    .where(or_(
                        DiscordMessage.message_id == message_id,
                        DiscordMessage.parent_message_id == message_id
                    ))
                )
                last_activity = last_activity_result.scalar() or message.created_at
                
                # Calculate trending score
                recent_activity_hours = (datetime.now(timezone.utc) - last_activity).total_seconds() / 3600
                trending_score = await self.calculate_trending_score(
                    engagement_score=engagement_score,
                    recent_activity_hours=recent_activity_hours
                )
                
                # Update or create engagement metrics
                if message.engagement_metrics:
                    metrics = message.engagement_metrics
                else:
                    metrics = EngagementMetrics(message_id=message.id)
                    session.add(metrics)
                
                # Update metrics
                metrics.reply_count = reply_count
                metrics.reaction_count = reaction_count
                metrics.unique_reactors = unique_reactors
                metrics.thread_depth = thread_depth
                metrics.discussion_participants = discussion_participants
                metrics.engagement_score = engagement_score
                metrics.trending_score = trending_score
                metrics.last_activity = last_activity
                metrics.extracted_keywords = content_keywords
                metrics.topic_categories = self._categorize_content(message.content, content_keywords)
                
                await session.commit()
                
                logger.debug(f"Updated engagement for message {message_id}: score={engagement_score}")
                return engagement_score
                
            except Exception as e:
                logger.error(f"Error updating engagement for message {message_id}: {e}")
                await session.rollback()
                return None
    
    async def get_top_discussions(
        self,
        days: int = 7,
        min_score: float = None,
        limit: int = 20,
        channel_ids: List[str] = None
    ) -> List[Tuple[DiscordMessage, EngagementMetrics]]:
        """Get top discussions based on engagement score."""
        if min_score is None:
            min_score = settings.min_engagement_score
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        async with db_service.get_session() as session:
            query = (
                select(DiscordMessage, EngagementMetrics)
                .join(EngagementMetrics)
                .options(
                    selectinload(DiscordMessage.author),
                    selectinload(DiscordMessage.channel)
                )
                .where(DiscordMessage.created_at >= cutoff_date)
                .where(EngagementMetrics.engagement_score >= min_score)
                .order_by(EngagementMetrics.engagement_score.desc())
                .limit(limit)
            )
            
            if channel_ids:
                # Join with channel to filter by channel IDs
                query = query.join(DiscordChannel).where(DiscordChannel.channel_id.in_(channel_ids))
            
            result = await session.execute(query)
            return result.all()
    
    async def get_trending_discussions(
        self,
        hours: int = 24,
        min_trending_score: float = 5.0,
        limit: int = 10
    ) -> List[Tuple[DiscordMessage, EngagementMetrics]]:
        """Get currently trending discussions."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        async with db_service.get_session() as session:
            result = await session.execute(
                select(DiscordMessage, EngagementMetrics)
                .join(EngagementMetrics)
                .options(
                    selectinload(DiscordMessage.author),
                    selectinload(DiscordMessage.channel)
                )
                .where(EngagementMetrics.last_activity >= cutoff_date)
                .where(EngagementMetrics.trending_score >= min_trending_score)
                .order_by(EngagementMetrics.trending_score.desc())
                .limit(limit)
            )
            return result.all()
    
    async def get_engagement_summary(self, days: int = 7) -> Dict:
        """Get engagement summary statistics."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        async with db_service.get_session() as session:
            # Total messages
            total_messages_result = await session.execute(
                select(func.count(DiscordMessage.id))
                .where(DiscordMessage.created_at >= cutoff_date)
            )
            total_messages = total_messages_result.scalar() or 0
            
            # Messages with high engagement
            high_engagement_result = await session.execute(
                select(func.count(EngagementMetrics.id))
                .join(DiscordMessage)
                .where(DiscordMessage.created_at >= cutoff_date)
                .where(EngagementMetrics.engagement_score >= settings.min_engagement_score)
            )
            high_engagement_count = high_engagement_result.scalar() or 0
            
            # Average engagement score
            avg_score_result = await session.execute(
                select(func.avg(EngagementMetrics.engagement_score))
                .join(DiscordMessage)
                .where(DiscordMessage.created_at >= cutoff_date)
            )
            avg_engagement_score = avg_score_result.scalar() or 0.0
            
            # Top keywords
            keyword_result = await session.execute(
                text("""
                SELECT keyword, COUNT(*) as frequency
                FROM (
                    SELECT jsonb_array_elements_text(extracted_keywords) as keyword
                    FROM engagement_metrics em
                    JOIN discord_messages dm ON em.message_id = dm.id
                    WHERE dm.created_at >= :cutoff_date
                    AND em.extracted_keywords IS NOT NULL
                ) keywords
                GROUP BY keyword
                ORDER BY frequency DESC
                LIMIT 10
                """),
                {"cutoff_date": cutoff_date}
            )
            top_keywords = [(row[0], row[1]) for row in keyword_result.fetchall()]
            
            return {
                "period_days": days,
                "total_messages": total_messages,
                "high_engagement_count": high_engagement_count,
                "high_engagement_rate": high_engagement_count / total_messages if total_messages > 0 else 0,
                "average_engagement_score": round(float(avg_engagement_score), 2),
                "top_keywords": top_keywords
            }
    
    async def bulk_update_engagement(self, message_ids: List[str] = None, batch_size: int = 100) -> int:
        """Bulk update engagement metrics for multiple messages."""
        async with db_service.get_session() as session:
            # Get messages to update
            if message_ids:
                query = select(DiscordMessage.message_id).where(DiscordMessage.message_id.in_(message_ids))
            else:
                # Update messages from last 7 days
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
                query = select(DiscordMessage.message_id).where(DiscordMessage.created_at >= cutoff_date)
            
            result = await session.execute(query)
            all_message_ids = [row[0] for row in result.fetchall()]
        
        # Process in batches
        updated_count = 0
        total_messages = len(all_message_ids)
        
        logger.info(f"Bulk updating engagement for {total_messages} messages")
        
        for i in range(0, total_messages, batch_size):
            batch = all_message_ids[i:i + batch_size]
            
            # Update each message in the batch
            for message_id in batch:
                score = await self.update_message_engagement(message_id)
                if score is not None:
                    updated_count += 1
            
            # Rate limiting between batches
            if i + batch_size < total_messages:
                await asyncio.sleep(1)
            
            logger.info(f"Updated engagement for {min(i + batch_size, total_messages)}/{total_messages} messages")
        
        logger.info(f"Bulk engagement update completed: {updated_count}/{total_messages} messages updated")
        return updated_count
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract technical keywords from message content."""
        if not content:
            return []
        
        # Simple keyword extraction (can be enhanced with NLP)
        technical_terms = self._get_technical_keywords()
        content_lower = content.lower()
        
        keywords = []
        for term in technical_terms:
            if term.lower() in content_lower:
                keywords.append(term)
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def _get_technical_keywords(self) -> List[str]:
        """Get list of technical keywords to look for."""
        return [
            # AI/ML Terms
            "langchain", "langgraph", "llm", "gpt", "claude", "openai", "anthropic",
            "vector", "embedding", "rag", "retrieval", "agent", "workflow", "chain",
            "prompt", "fine-tune", "model", "inference", "training", "dataset",
            
            # Programming Terms
            "python", "javascript", "typescript", "react", "node", "api", "rest",
            "graphql", "database", "sql", "nosql", "mongodb", "postgres", "redis",
            "docker", "kubernetes", "aws", "azure", "gcp", "serverless", "microservices",
            
            # Austin/Local Terms
            "austin", "texas", "meetup", "conference", "sxsw", "local", "atx",
            
            # General Tech Terms
            "startup", "venture", "funding", "saas", "platform", "framework",
            "library", "tool", "integration", "automation", "deployment", "ci/cd"
        ]
    
    def _categorize_content(self, content: str, keywords: List[str]) -> List[str]:
        """Categorize content based on keywords and content analysis."""
        if not content or not keywords:
            return ["general"]
        
        categories = []
        content_lower = content.lower()
        
        # AI/ML category
        ai_terms = ["langchain", "langgraph", "llm", "gpt", "claude", "ai", "ml", "model", "agent"]
        if any(term in keywords for term in ai_terms):
            categories.append("ai-ml")
        
        # Programming category
        prog_terms = ["python", "javascript", "api", "code", "programming", "development"]
        if any(term in keywords for term in prog_terms):
            categories.append("programming")
        
        # Infrastructure category
        infra_terms = ["docker", "kubernetes", "aws", "cloud", "deployment", "devops"]
        if any(term in keywords for term in infra_terms):
            categories.append("infrastructure")
        
        # Community category
        community_terms = ["meetup", "event", "conference", "presentation", "talk"]
        if any(term in content_lower for term in community_terms):
            categories.append("community")
        
        # Learning category
        learning_terms = ["tutorial", "learn", "course", "guide", "documentation", "how to"]
        if any(term in content_lower for term in learning_terms):
            categories.append("learning")
        
        return categories if categories else ["general"]


# Global engagement service instance
engagement_service = EngagementAnalyzer()