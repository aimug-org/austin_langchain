"""Discord service for bot integration and message processing."""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set
import discord
from discord.ext import commands
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from discord_bot.core.config import settings
from discord_bot.core.logging import get_logger
from discord_bot.services.database import db_service
from discord_bot.models.discord_models import (
    DiscordGuild, DiscordChannel, DiscordUser, DiscordMessage, 
    MessageReaction, EngagementMetrics
)

logger = get_logger(__name__)


class DiscordBot(commands.Bot):
    """Custom Discord bot with message monitoring capabilities."""
    
    def __init__(self, discord_service: 'DiscordService'):
        # Configure intents for message content access
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.guild_reactions = True
        # Don't request members intent - it's privileged and not needed
        # intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.discord_service = discord_service
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Discord bot logged in as {self.user}")

        # Signal ready event if waiting
        if self.discord_service._ready_event:
            self.discord_service._ready_event.set()

        # Initialize guilds and channels
        await self.discord_service.sync_guilds()

        # Start monitoring existing messages if needed
        # Sync 14 days = 336 hours
        await self.discord_service.sync_recent_messages(hours=720)  # 30 days
    
    async def on_message(self, message: discord.Message):
        """Handle new messages."""
        if message.author.bot and not settings.debug:
            return  # Skip bot messages in production
        
        await self.discord_service.process_message(message)
        await self.process_commands(message)
    
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Handle message edits."""
        await self.discord_service.process_message_edit(before, after)
    
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Handle reaction additions."""
        await self.discord_service.process_reaction(reaction, user, is_add=True)
    
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        """Handle reaction removals."""
        await self.discord_service.process_reaction(reaction, user, is_add=False)


class DiscordService:
    """Service for managing Discord bot operations and data processing."""

    def __init__(self):
        self.bot: Optional[DiscordBot] = None
        self._monitored_channels: Set[str] = set()
        self._monitor_all_channels: bool = False
        self._message_cache: Dict[str, datetime] = {}  # Cache for rate limiting
        self._is_running = False
        self._ready_event: Optional[asyncio.Event] = None
    
    async def initialize(self) -> None:
        """Initialize the Discord service."""
        logger.info("Initializing Discord service")
        
        # Initialize monitored channels
        channel_ids = settings.channel_ids
        if channel_ids and channel_ids[0] == "ALL":
            # Special case: monitor all channels
            self._monitor_all_channels = True
            self._monitored_channels = set()
            logger.info("Configured to monitor ALL channels")
        else:
            self._monitor_all_channels = False
            self._monitored_channels = set(channel_ids)
        
        # Create bot instance
        self.bot = DiscordBot(self)
        
        logger.info("Discord service initialized", extra={
            "monitor_all_channels": self._monitor_all_channels,
            "monitored_channels": len(self._monitored_channels) if not self._monitor_all_channels else "ALL",
            "guild_id": settings.discord_guild_id
        })
    
    async def start(self) -> None:
        """Start the Discord bot."""
        if not self.bot:
            await self.initialize()
        
        logger.info("Starting Discord bot")
        self._is_running = True
        
        try:
            await self.bot.start(settings.discord_token)
        except Exception as e:
            logger.error("Failed to start Discord bot", extra={
                "error": str(e),
                "error_type": type(e).__name__
            })
            self._is_running = False
            raise
    
    async def stop(self) -> None:
        """Stop the Discord bot."""
        if self.bot and self._is_running:
            logger.info("Stopping Discord bot")
            await self.bot.close()
            self._is_running = False
            logger.info("Discord bot stopped")
    
    async def sync_guilds(self) -> None:
        """Sync guild information with database."""
        if not self.bot:
            return
        
        logger.info("Syncing guild information")
        
        for guild in self.bot.guilds:
            await self._store_guild(guild)
            
            # Sync channels
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    await self._store_channel(channel, guild)
        
        logger.info("Guild sync completed", extra={
            "guilds_synced": len(self.bot.guilds)
        })
    
    async def sync_recent_messages(self, hours: int = 24) -> None:
        """Sync recent messages from monitored channels."""
        if not self.bot:
            return
        
        logger.info(f"Syncing recent messages from last {hours} hours")

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        message_count = 0
        
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if not self._monitor_all_channels and str(channel.id) not in self._monitored_channels:
                    continue
                
                try:
                    async for message in channel.history(after=cutoff_time, limit=None):
                        await self.process_message(message, is_historical=True)
                        message_count += 1
                        
                        # Rate limiting for bulk processing
                        if message_count % 100 == 0:
                            await asyncio.sleep(1)
                            logger.debug(f"Processed {message_count} historical messages")
                
                except discord.Forbidden:
                    logger.warning(f"No access to channel {channel.name}")
                except Exception as e:
                    logger.error(f"Error syncing messages from {channel.name}", extra={
                        "error": str(e),
                        "channel_id": channel.id
                    })
        
        logger.info("Recent message sync completed", extra={
            "messages_processed": message_count
        })
    
    async def process_message(self, message: discord.Message, is_historical: bool = False) -> None:
        """Process a Discord message and store in database."""
        # Skip messages from non-monitored channels
        if not self._monitor_all_channels and str(message.channel.id) not in self._monitored_channels:
            return
        
        # Rate limiting check
        if not is_historical and self._should_rate_limit(message.id):
            return
        
        try:
            async with db_service.get_session() as session:
                # Store/update user
                user_record = await self._store_user(message.author, session)
                
                # Store/update guild and channel
                if isinstance(message.channel, discord.TextChannel):
                    guild_record = await self._store_guild(message.guild, session)
                    channel_record = await self._store_channel(message.channel, message.guild, session)
                    
                    # Store message
                    message_record = await self._store_message(
                        message, user_record, guild_record, channel_record, session
                    )
                    
                    # Process reactions
                    for reaction in message.reactions:
                        await self._store_reactions(reaction, message_record, session)

                    # Initialize engagement metrics
                    await self._initialize_engagement_metrics(message_record, session)

                    # Update engagement metrics with reaction/reply counts
                    await self._update_engagement_metrics(message_record, session)

                    await session.commit()

                    if not is_historical:
                        logger.debug("Processed new message", extra={
                            "message_id": message.id,
                            "channel": message.channel.name,
                            "author": message.author.name
                        })
        
        except Exception as e:
            logger.error("Error processing message", extra={
                "error": str(e),
                "message_id": message.id,
                "channel_id": message.channel.id
            })
    
    async def process_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        """Process message edit."""
        try:
            async with db_service.get_session() as session:
                # Find existing message
                result = await session.execute(
                    select(DiscordMessage).where(DiscordMessage.message_id == str(after.id))
                )
                message_record = result.scalar_one_or_none()
                
                if message_record:
                    message_record.content = after.content
                    message_record.clean_content = after.clean_content
                    message_record.is_edited = True
                    message_record.edit_timestamp = after.edited_at or datetime.now(timezone.utc)
                    
                    logger.debug("Updated edited message", extra={
                        "message_id": after.id
                    })
        
        except Exception as e:
            logger.error("Error processing message edit", extra={
                "error": str(e),
                "message_id": after.id
            })
    
    async def process_reaction(self, reaction: discord.Reaction, user: discord.User, is_add: bool) -> None:
        """Process reaction addition or removal."""
        try:
            async with db_service.get_session() as session:
                # Store/update user
                user_record = await self._store_user(user, session)
                
                # Find message
                result = await session.execute(
                    select(DiscordMessage).where(DiscordMessage.message_id == str(reaction.message.id))
                )
                message_record = result.scalar_one_or_none()
                
                if not message_record:
                    # Process the message first if we don't have it
                    await self.process_message(reaction.message)
                    return
                
                if is_add:
                    await self._store_reaction(reaction, message_record, user_record, session)
                else:
                    await self._remove_reaction(reaction, message_record, user_record, session)
                
                # Update engagement metrics
                await self._update_engagement_metrics(message_record, session)
        
        except Exception as e:
            logger.error("Error processing reaction", extra={
                "error": str(e),
                "message_id": reaction.message.id,
                "user_id": user.id
            })
    
    def _should_rate_limit(self, message_id: str) -> bool:
        """Check if message processing should be rate limited."""
        now = datetime.now(timezone.utc)
        
        # Clean old entries
        cutoff = now - timedelta(minutes=5)
        self._message_cache = {
            k: v for k, v in self._message_cache.items() 
            if v > cutoff
        }
        
        # Check if we've seen this message recently
        if message_id in self._message_cache:
            return True
        
        self._message_cache[message_id] = now
        return False
    
    async def _store_guild(self, guild: discord.Guild, session=None) -> DiscordGuild:
        """Store or update guild information."""
        if session is None:
            async with db_service.get_session() as session:
                return await self._store_guild(guild, session)
        
        # Check if guild exists
        result = await session.execute(
            select(DiscordGuild).where(DiscordGuild.guild_id == str(guild.id))
        )
        guild_record = result.scalar_one_or_none()
        
        if not guild_record:
            guild_record = DiscordGuild(
                guild_id=str(guild.id),
                name=guild.name,
                description=guild.description,
                member_count=guild.member_count,
                is_active=True
            )
            session.add(guild_record)
        else:
            # Update existing record
            guild_record.name = guild.name
            guild_record.description = guild.description
            guild_record.member_count = guild.member_count
        
        await session.flush()
        return guild_record
    
    async def _store_channel(self, channel: discord.TextChannel, guild: discord.Guild, session=None) -> DiscordChannel:
        """Store or update channel information."""
        if session is None:
            async with db_service.get_session() as session:
                return await self._store_channel(channel, guild, session)
        
        # Get guild record
        guild_result = await session.execute(
            select(DiscordGuild).where(DiscordGuild.guild_id == str(guild.id))
        )
        guild_record = guild_result.scalar_one()
        
        # Check if channel exists
        result = await session.execute(
            select(DiscordChannel).where(DiscordChannel.channel_id == str(channel.id))
        )
        channel_record = result.scalar_one_or_none()
        
        if not channel_record:
            channel_record = DiscordChannel(
                channel_id=str(channel.id),
                guild_id=guild_record.id,
                name=channel.name,
                channel_type=str(channel.type),
                topic=channel.topic,
                is_monitored=self._monitor_all_channels or str(channel.id) in self._monitored_channels
            )
            session.add(channel_record)
        else:
            # Update existing record
            channel_record.name = channel.name
            channel_record.topic = channel.topic
            channel_record.is_monitored = self._monitor_all_channels or str(channel.id) in self._monitored_channels
        
        await session.flush()
        return channel_record
    
    async def _store_user(self, user: discord.User, session=None) -> DiscordUser:
        """Store or update user information."""
        if session is None:
            async with db_service.get_session() as session:
                return await self._store_user(user, session)
        
        # Check if user exists
        result = await session.execute(
            select(DiscordUser).where(DiscordUser.user_id == str(user.id))
        )
        user_record = result.scalar_one_or_none()
        
        if not user_record:
            user_record = DiscordUser(
                user_id=str(user.id),
                username=user.name,
                display_name=user.display_name,
                avatar_url=str(user.avatar.url) if user.avatar else None,
                is_bot=user.bot
            )
            session.add(user_record)
        else:
            # Update existing record
            user_record.username = user.name
            user_record.display_name = user.display_name
            user_record.avatar_url = str(user.avatar.url) if user.avatar else None
        
        await session.flush()
        return user_record
    
    async def _store_message(
        self, 
        message: discord.Message, 
        user_record: DiscordUser,
        guild_record: DiscordGuild,
        channel_record: DiscordChannel,
        session
    ) -> DiscordMessage:
        """Store message information."""
        # Check if message already exists
        result = await session.execute(
            select(DiscordMessage).where(DiscordMessage.message_id == str(message.id))
        )
        existing_message = result.scalar_one_or_none()
        
        if existing_message:
            return existing_message
        
        # Determine parent message for replies
        parent_message_id = None
        if message.reference and message.reference.message_id:
            parent_message_id = str(message.reference.message_id)
        
        # Create message record
        message_record = DiscordMessage(
            message_id=str(message.id),
            guild_id=guild_record.id,
            channel_id=channel_record.id,
            author_id=user_record.id,
            content=message.content,
            clean_content=message.clean_content,
            message_type=str(message.type),
            thread_id=str(message.thread.id) if hasattr(message, 'thread') and message.thread else None,
            parent_message_id=parent_message_id,
            is_edited=message.edited_at is not None,
            edit_timestamp=message.edited_at,
            is_pinned=message.pinned,
            has_attachments=len(message.attachments) > 0,
            attachment_urls=[str(att.url) for att in message.attachments] if message.attachments else None,
            has_embeds=len(message.embeds) > 0,
            embed_data=[embed.to_dict() for embed in message.embeds] if message.embeds else None,
            created_at=message.created_at
        )
        
        session.add(message_record)
        await session.flush()
        return message_record
    
    async def _store_reactions(self, reaction: discord.Reaction, message_record: DiscordMessage, session) -> None:
        """Store reaction information."""
        # Get all users who reacted
        try:
            async for user in reaction.users():
                user_record = await self._store_user(user, session)
                await self._store_reaction(reaction, message_record, user_record, session)
        except Exception as e:
            logger.warning("Could not fetch reaction users", extra={
                "error": str(e),
                "message_id": message_record.message_id
            })
    
    async def _store_reaction(
        self, 
        reaction: discord.Reaction, 
        message_record: DiscordMessage, 
        user_record: DiscordUser, 
        session
    ) -> None:
        """Store individual reaction."""
        emoji_str = str(reaction.emoji)
        emoji_id = None
        is_custom = False
        
        if hasattr(reaction.emoji, 'id') and reaction.emoji.id:
            emoji_id = str(reaction.emoji.id)
            is_custom = True
        
        # Check if reaction already exists
        result = await session.execute(
            select(MessageReaction).where(
                MessageReaction.message_id == message_record.id,
                MessageReaction.user_id == user_record.id,
                MessageReaction.emoji == emoji_str
            )
        )
        existing_reaction = result.scalar_one_or_none()
        
        if not existing_reaction:
            reaction_record = MessageReaction(
                message_id=message_record.id,
                user_id=user_record.id,
                emoji=emoji_str,
                emoji_id=emoji_id,
                is_custom=is_custom
            )
            session.add(reaction_record)
    
    async def _remove_reaction(
        self,
        reaction: discord.Reaction,
        message_record: DiscordMessage,
        user_record: DiscordUser,
        session
    ) -> None:
        """Remove reaction from database."""
        emoji_str = str(reaction.emoji)
        
        result = await session.execute(
            select(MessageReaction).where(
                MessageReaction.message_id == message_record.id,
                MessageReaction.user_id == user_record.id,
                MessageReaction.emoji == emoji_str
            )
        )
        reaction_record = result.scalar_one_or_none()
        
        if reaction_record:
            await session.delete(reaction_record)
    
    async def _initialize_engagement_metrics(self, message_record: DiscordMessage, session) -> None:
        """Initialize engagement metrics for a message."""
        # Check if metrics already exist
        result = await session.execute(
            select(EngagementMetrics).where(EngagementMetrics.message_id == message_record.id)
        )
        existing_metrics = result.scalar_one_or_none()
        
        if not existing_metrics:
            metrics = EngagementMetrics(
                message_id=message_record.id,
                reply_count=0,
                reaction_count=0,
                unique_reactors=0,
                thread_depth=0,
                engagement_score=0.0,
                trending_score=0.0,
                discussion_participants=1,  # At least the author
                last_activity=message_record.created_at
            )
            session.add(metrics)
    
    async def _update_engagement_metrics(self, message_record: DiscordMessage, session) -> None:
        """Update engagement metrics for a message."""
        # Get current metrics
        result = await session.execute(
            select(EngagementMetrics).where(EngagementMetrics.message_id == message_record.id)
        )
        metrics = result.scalar_one_or_none()

        if not metrics:
            await self._initialize_engagement_metrics(message_record, session)
            return

        # Count reactions
        reaction_result = await session.execute(
            select(MessageReaction).where(MessageReaction.message_id == message_record.id)
        )
        reactions = reaction_result.scalars().all()

        metrics.reaction_count = len(reactions)
        metrics.unique_reactors = len(set(r.user_id for r in reactions))

        # Count replies (messages that reference this message as parent)
        from sqlalchemy import func
        reply_result = await session.execute(
            select(func.count(DiscordMessage.id))
            .where(DiscordMessage.parent_message_id == message_record.message_id)
        )
        metrics.reply_count = reply_result.scalar() or 0

        # Count unique participants in discussion
        participant_result = await session.execute(
            select(func.count(func.distinct(DiscordMessage.author_id)))
            .where(
                (DiscordMessage.message_id == message_record.message_id) |
                (DiscordMessage.parent_message_id == message_record.message_id)
            )
        )
        metrics.discussion_participants = participant_result.scalar() or 1

        metrics.last_activity = datetime.now(timezone.utc)

        # Calculate basic engagement score
        metrics.engagement_score = self._calculate_engagement_score(
            reply_count=metrics.reply_count,
            reaction_count=metrics.reaction_count,
            unique_reactors=metrics.unique_reactors,
            discussion_participants=metrics.discussion_participants,
            message_age_hours=(datetime.now(timezone.utc) - message_record.created_at).total_seconds() / 3600
        )
    
    def _calculate_engagement_score(
        self, 
        reply_count: int, 
        reaction_count: int, 
        unique_reactors: int,
        discussion_participants: int,
        message_age_hours: float
    ) -> float:
        """Calculate engagement score for a message."""
        # Weight factors
        reply_weight = 0.4
        reaction_weight = 0.2
        participant_weight = 0.3
        recency_weight = 0.1
        
        # Recency multiplier (decay over time)
        recency_multiplier = max(0.1, 1.0 - (message_age_hours / 168))  # Decay over 7 days
        
        score = (
            reply_count * reply_weight +
            reaction_count * reaction_weight +
            unique_reactors * participant_weight +
            recency_multiplier * recency_weight * 10  # Base recency score
        )
        
        return round(score, 2)
    
    @property
    def is_running(self) -> bool:
        """Check if the Discord service is running."""
        return self._is_running and self.bot is not None
    
    @property 
    def monitored_channels(self) -> Set[str]:
        """Get the set of monitored channel IDs.
        
        Returns:
            Set containing channel IDs, or a set with 'ALL' if monitoring all channels.
        """
        if self._monitor_all_channels:
            return {"ALL"}
        return self._monitored_channels.copy()


# Global Discord service instance
discord_service = DiscordService()