"""Database models for newsletter generation and management."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Text, Integer, Float, Boolean, JSON, DateTime,
    ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from discord_bot.models.base import BaseModel


class NewsletterType(str, Enum):
    """Newsletter type enumeration."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SPECIAL = "special"


class NewsletterStatus(str, Enum):
    """Newsletter status enumeration."""
    PENDING = "pending"
    GENERATING = "generating" 
    GENERATED = "generated"
    REVIEWING = "reviewing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PublishStatus(str, Enum):
    """Publication status enumeration."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"


class Newsletter(BaseModel):
    """Newsletter generation and tracking."""
    
    __tablename__ = "newsletters"
    
    # Basic information
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Newsletter title"
    )
    subtitle: Mapped[Optional[str]] = mapped_column(
        String(500),
        doc="Newsletter subtitle"
    )
    newsletter_type: Mapped[NewsletterType] = mapped_column(
        SQLEnum(NewsletterType),
        nullable=False,
        doc="Type of newsletter"
    )
    status: Mapped[NewsletterStatus] = mapped_column(
        SQLEnum(NewsletterStatus),
        default=NewsletterStatus.PENDING,
        doc="Current status of newsletter"
    )
    
    # Content
    content_html: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Newsletter content in HTML format"
    )
    content_markdown: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Newsletter content in Markdown format"
    )
    content_text: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Newsletter content in plain text"
    )
    
    # Metadata
    word_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Word count of newsletter content"
    )
    estimated_read_time: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Estimated reading time in minutes"
    )
    
    # Scheduling
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(
        doc="When the newsletter was scheduled to be generated"
    )
    generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="When the newsletter was actually generated"
    )
    
    # Generation metadata
    generation_duration: Mapped[Optional[float]] = mapped_column(
        Float,
        doc="Time taken to generate newsletter in seconds"
    )
    model_used: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="AI model used for generation"
    )
    generation_cost: Mapped[Optional[float]] = mapped_column(
        Float,
        doc="Cost of generation in USD"
    )
    
    # Quality metrics
    quality_score: Mapped[Optional[float]] = mapped_column(
        Float,
        doc="Automated quality assessment score"
    )
    human_review_score: Mapped[Optional[float]] = mapped_column(
        Float,
        doc="Human reviewer quality score"
    )
    review_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Review notes from human reviewer"
    )
    
    # External service integration
    buttondown_draft_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Buttondown draft ID"
    )
    buttondown_email_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Buttondown email ID after publishing"
    )
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Error message if generation failed"
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Number of retry attempts"
    )
    
    # Relationships
    sections: Mapped[List["NewsletterSection"]] = relationship(
        back_populates="newsletter",
        cascade="all, delete-orphan"
    )
    featured_discussions: Mapped[List["NewsletterDiscussion"]] = relationship(
        back_populates="newsletter",
        cascade="all, delete-orphan"
    )
    generation_logs: Mapped[List["NewsletterGenerationLog"]] = relationship(
        back_populates="newsletter",
        cascade="all, delete-orphan"
    )
    publication_record: Mapped[Optional["NewsletterPublication"]] = relationship(
        back_populates="newsletter",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    __table_args__ = (
        Index("ix_newsletters_type", "newsletter_type"),
        Index("ix_newsletters_status", "status"),
        Index("ix_newsletters_scheduled_for", "scheduled_for"),
        Index("ix_newsletters_created_at", "created_at"),
    )


class NewsletterSection(BaseModel):
    """Individual sections within a newsletter."""
    
    __tablename__ = "newsletter_sections"
    
    newsletter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("newsletters.id"),
        nullable=False,
        doc="Reference to the newsletter"
    )
    
    # Section metadata
    section_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Type of section (featured, trending, community, etc.)"
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Section title"
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Order of section in newsletter"
    )
    
    # Content
    content_html: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Section content in HTML"
    )
    content_markdown: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Section content in Markdown"
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Brief summary of section content"
    )
    
    # Generation metadata
    generated_by_agent: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Which agent generated this section"
    )
    generation_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Prompt used to generate this section"
    )
    
    # Relationships
    newsletter: Mapped["Newsletter"] = relationship(back_populates="sections")
    
    __table_args__ = (
        Index("ix_newsletter_sections_newsletter_id", "newsletter_id"),
        Index("ix_newsletter_sections_type", "section_type"),
        Index("ix_newsletter_sections_order", "order_index"),
    )


class NewsletterDiscussion(BaseModel):
    """Featured discussions in newsletters."""
    
    __tablename__ = "newsletter_discussions"
    
    newsletter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("newsletters.id"),
        nullable=False,
        doc="Reference to the newsletter"
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("discord_messages.id"),
        nullable=False,
        doc="Reference to the Discord message"
    )
    
    # Discussion metadata
    discussion_title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Title/summary of the discussion"
    )
    discussion_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="AI-generated summary of the discussion"
    )
    key_points: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        doc="Key points extracted from discussion"
    )
    
    # Technical commentary
    technical_analysis: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Technical writing team analysis"
    )
    expert_opinion: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Expert opinion on the topic discussed"
    )
    
    # Engagement data at time of inclusion
    engagement_score_snapshot: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Engagement score when included in newsletter"
    )
    participant_count_snapshot: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Number of participants when included"
    )
    
    # Research and fact-checking
    fact_check_results: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        doc="Results from fact-checking process"
    )
    additional_research: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Additional research context from Perplexity"
    )
    research_sources: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        doc="Sources used for additional research"
    )
    
    # Inclusion metadata
    inclusion_reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Why this discussion was included"
    )
    priority_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        doc="Priority score for ordering in newsletter"
    )
    
    # Relationships
    newsletter: Mapped["Newsletter"] = relationship(back_populates="featured_discussions")
    
    __table_args__ = (
        Index("ix_newsletter_discussions_newsletter_id", "newsletter_id"),
        Index("ix_newsletter_discussions_message_id", "message_id"),
        Index("ix_newsletter_discussions_priority", "priority_score"),
    )


class NewsletterGenerationLog(BaseModel):
    """Detailed logs of newsletter generation process."""
    
    __tablename__ = "newsletter_generation_logs"
    
    newsletter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("newsletters.id"),
        nullable=False,
        doc="Reference to the newsletter"
    )
    
    # Log entry details
    step_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Name of the generation step"
    )
    agent_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="Name of the agent that performed this step"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Status of this step (started, completed, failed)"
    )
    
    # Timing information
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="When this step started"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        doc="When this step completed"
    )
    duration: Mapped[Optional[float]] = mapped_column(
        Float,
        doc="Duration of step in seconds"
    )
    
    # Input/Output data
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        doc="Input data for this step"
    )
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        doc="Output data from this step"
    )
    
    # Model and API information
    model_used: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="AI model used for this step"
    )
    api_calls: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of API calls made"
    )
    tokens_used: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of tokens used"
    )
    cost: Mapped[Optional[float]] = mapped_column(
        Float,
        doc="Cost of this step in USD"
    )
    
    # Error information
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Error message if step failed"
    )
    error_traceback: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Full error traceback"
    )
    
    # Additional metadata
    step_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        doc="Additional metadata for this step"
    )
    
    # Relationships
    newsletter: Mapped["Newsletter"] = relationship(back_populates="generation_logs")
    
    __table_args__ = (
        Index("ix_newsletter_logs_newsletter_id", "newsletter_id"),
        Index("ix_newsletter_logs_step", "step_name"),
        Index("ix_newsletter_logs_status", "status"),
        Index("ix_newsletter_logs_started_at", "started_at"),
    )


class NewsletterPublication(BaseModel):
    """Newsletter publication tracking for external services."""
    
    __tablename__ = "newsletter_publications"
    
    newsletter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("newsletters.id"),
        unique=True,
        nullable=False,
        doc="Reference to the newsletter"
    )
    
    # Publication details
    service_name: Mapped[str] = mapped_column(
        String(50),
        default="buttondown",
        doc="Service used for publication"
    )
    status: Mapped[PublishStatus] = mapped_column(
        SQLEnum(PublishStatus),
        default=PublishStatus.DRAFT,
        doc="Publication status"
    )
    
    # External service IDs
    external_draft_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External service draft ID"
    )
    external_email_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        doc="External service email ID"
    )
    
    # Publication timing
    published_at: Mapped[Optional[datetime]] = mapped_column(
        doc="When the newsletter was published"
    )
    scheduled_send_time: Mapped[Optional[datetime]] = mapped_column(
        doc="Scheduled send time"
    )
    actual_send_time: Mapped[Optional[datetime]] = mapped_column(
        doc="Actual send time"
    )
    
    # Delivery metrics
    subscriber_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of subscribers at time of send"
    )
    delivered_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of emails delivered"
    )
    open_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of emails opened"
    )
    click_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of clicks"
    )
    unsubscribe_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        doc="Number of unsubscribes"
    )
    
    # Rates (calculated)
    delivery_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        doc="Delivery rate percentage"
    )
    open_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        doc="Open rate percentage"
    )
    click_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        doc="Click rate percentage"
    )
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        doc="Error message if publication failed"
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Number of retry attempts"
    )
    
    # Relationships
    newsletter: Mapped["Newsletter"] = relationship(back_populates="publication_record")
    
    __table_args__ = (
        Index("ix_newsletter_publications_status", "status"),
        Index("ix_newsletter_publications_published_at", "published_at"),
        Index("ix_newsletter_publications_service", "service_name"),
    )