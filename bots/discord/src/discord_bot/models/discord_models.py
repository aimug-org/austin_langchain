"""Database models for Discord-related data."""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Text, BigInteger, Integer, Float, Boolean,
    JSON, ForeignKey, Index, UniqueConstraint, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from discord_bot.models.base import BaseModel


class DiscordGuild(BaseModel):
    """Discord guild/server information."""
    
    __tablename__ = "discord_guilds"
    
    guild_id: Mapped[str] = mapped_column(
        String(20), 
        unique=True, 
        nullable=False,
        doc="Discord guild ID"
    )
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        doc="Guild name"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Guild description"
    )
    member_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of members"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        doc="Whether the guild is actively monitored"
    )
    
    # Relationships
    channels: Mapped[List["DiscordChannel"]] = relationship(
        back_populates="guild",
        cascade="all, delete-orphan"
    )
    messages: Mapped[List["DiscordMessage"]] = relationship(
        back_populates="guild",
        cascade="all, delete-orphan"
    )


class DiscordChannel(BaseModel):
    """Discord channel information."""
    
    __tablename__ = "discord_channels"
    
    channel_id: Mapped[str] = mapped_column(
        String(20), 
        unique=True, 
        nullable=False,
        doc="Discord channel ID"
    )
    guild_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("discord_guilds.id"),
        nullable=False,
        doc="Reference to the guild"
    )
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        doc="Channel name"
    )
    channel_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Channel type (text, voice, etc.)"
    )
    topic: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Channel topic/description"
    )
    is_monitored: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        doc="Whether this channel is monitored for messages"
    )
    
    # Relationships
    guild: Mapped["DiscordGuild"] = relationship(back_populates="channels")
    messages: Mapped[List["DiscordMessage"]] = relationship(
        back_populates="channel",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("ix_discord_channels_guild_id", "guild_id"),
    )


class DiscordUser(BaseModel):
    """Discord user information."""
    
    __tablename__ = "discord_users"
    
    user_id: Mapped[str] = mapped_column(
        String(20), 
        unique=True, 
        nullable=False,
        doc="Discord user ID"
    )
    username: Mapped[str] = mapped_column(
        String(32), 
        nullable=False,
        doc="Discord username"
    )
    display_name: Mapped[Optional[str]] = mapped_column(
        String(32),
        doc="User display name"
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="User avatar URL"
    )
    is_bot: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Whether the user is a bot"
    )
    join_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="When the user joined the guild"
    )
    
    # Relationships
    messages: Mapped[List["DiscordMessage"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )
    reactions: Mapped[List["MessageReaction"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class DiscordMessage(BaseModel):
    """Discord message data."""
    
    __tablename__ = "discord_messages"
    
    message_id: Mapped[str] = mapped_column(
        String(20), 
        unique=True, 
        nullable=False,
        doc="Discord message ID"
    )
    guild_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("discord_guilds.id"),
        nullable=False,
        doc="Reference to the guild"
    )
    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("discord_channels.id"),
        nullable=False,
        doc="Reference to the channel"
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("discord_users.id"),
        nullable=False,
        doc="Reference to the message author"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Message content"
    )
    clean_content: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Message content with mentions resolved"
    )
    message_type: Mapped[str] = mapped_column(
        String(20),
        default="default",
        doc="Type of message (default, reply, etc.)"
    )
    
    # Thread information
    thread_id: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Thread ID if message is in a thread"
    )
    parent_message_id: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Parent message ID if this is a reply"
    )
    
    # Message metadata
    is_edited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Whether the message has been edited"
    )
    edit_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="When the message was last edited"
    )
    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Whether the message is pinned"
    )
    
    # Attachments and embeds
    has_attachments: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Whether the message has attachments"
    )
    attachment_urls: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        doc="List of attachment URLs"
    )
    has_embeds: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Whether the message has embeds"
    )
    embed_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        doc="Embed data"
    )
    
    # Relationships
    guild: Mapped["DiscordGuild"] = relationship(back_populates="messages")
    channel: Mapped["DiscordChannel"] = relationship(back_populates="messages")
    author: Mapped["DiscordUser"] = relationship(back_populates="messages")
    reactions: Mapped[List["MessageReaction"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan"
    )
    engagement_metrics: Mapped[Optional["EngagementMetrics"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    __table_args__ = (
        Index("ix_discord_messages_channel_id", "channel_id"),
        Index("ix_discord_messages_author_id", "author_id"),
        Index("ix_discord_messages_created_at", "created_at"),
        Index("ix_discord_messages_thread_id", "thread_id"),
    )


class MessageReaction(BaseModel):
    """Message reaction data."""
    
    __tablename__ = "message_reactions"
    
    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("discord_messages.id"),
        nullable=False,
        doc="Reference to the message"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("discord_users.id"),
        nullable=False,
        doc="Reference to the user who reacted"
    )
    emoji: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Emoji used for reaction"
    )
    emoji_id: Mapped[Optional[str]] = mapped_column(
        String(20),
        doc="Custom emoji ID if applicable"
    )
    is_custom: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Whether the emoji is a custom emoji"
    )
    
    # Relationships
    message: Mapped["DiscordMessage"] = relationship(back_populates="reactions")
    user: Mapped["DiscordUser"] = relationship(back_populates="reactions")
    
    __table_args__ = (
        UniqueConstraint("message_id", "user_id", "emoji", name="unique_reaction"),
        Index("ix_message_reactions_message_id", "message_id"),
        Index("ix_message_reactions_user_id", "user_id"),
    )


class EngagementMetrics(BaseModel):
    """Engagement metrics for messages and discussions."""
    
    __tablename__ = "engagement_metrics"
    
    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("discord_messages.id"),
        unique=True,
        nullable=False,
        doc="Reference to the message"
    )
    
    # Basic engagement counts
    reply_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Number of direct replies"
    )
    reaction_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Total number of reactions"
    )
    unique_reactors: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Number of unique users who reacted"
    )
    thread_depth: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Depth of thread conversation"
    )
    
    # Advanced metrics
    engagement_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        doc="Calculated engagement score"
    )
    trending_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        doc="Trending score based on recent activity"
    )
    discussion_participants: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Number of unique participants in discussion"
    )
    
    # Time-based metrics
    last_activity: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="Timestamp of last activity on this message"
    )
    peak_activity_hour: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Hour of day with peak activity"
    )
    
    # Content analysis
    sentiment_score: Mapped[Optional[float]] = mapped_column(
        Float,
        doc="Sentiment analysis score"
    )
    toxicity_score: Mapped[Optional[float]] = mapped_column(
        Float,
        doc="Toxicity detection score"
    )
    
    # Keywords and topics
    extracted_keywords: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        doc="Extracted keywords from message and replies"
    )
    topic_categories: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        doc="Categorized topics"
    )
    
    # Relationships
    message: Mapped["DiscordMessage"] = relationship(back_populates="engagement_metrics")
    
    __table_args__ = (
        Index("ix_engagement_metrics_score", "engagement_score"),
        Index("ix_engagement_metrics_trending", "trending_score"),
        Index("ix_engagement_metrics_last_activity", "last_activity"),
    )