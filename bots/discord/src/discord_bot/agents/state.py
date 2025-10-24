"""State definitions for the newsletter generation workflow."""

from typing import List, Dict, Optional, Any, TypedDict
from datetime import datetime
from pydantic import BaseModel, Field


class DiscussionData(BaseModel):
    """Data for a single discussion."""
    message_id: str
    content: str
    author: str
    channel: str
    channel_id: str
    engagement_score: float
    reply_count: int
    reaction_count: int
    participants: int
    keywords: List[str]
    category: List[str]
    thread_summary: Optional[str] = None
    created_at: datetime


class ResearchResult(BaseModel):
    """Research result from Perplexity API."""
    topic: str
    query: str
    findings: str
    sources: List[str]
    relevance_score: float
    timestamp: datetime


class NewsletterSection(BaseModel):
    """A section of the newsletter."""
    section_type: str  # featured, trending, community, technical
    title: str
    content: str
    discussions: List[str]  # message_ids
    word_count: int
    
    
class WriterFeedback(BaseModel):
    """Feedback from writer agents."""
    agent_name: str
    section: str
    feedback: str
    suggestions: List[str]
    quality_score: float


class NewsletterDraft(BaseModel):
    """Complete newsletter draft."""
    title: str
    subtitle: str
    sections: List[NewsletterSection]
    total_word_count: int
    estimated_read_time: int
    featured_discussions: List[str]
    generation_metadata: Dict[str, Any]


class NewsletterState(TypedDict):
    """State for the newsletter generation workflow."""
    # Input data
    newsletter_type: str  # daily, weekly, monthly
    target_date: str
    discussions: List[DiscussionData]

    # Research phase
    research_topics: List[str]
    research_results: List[ResearchResult]
    fact_check_results: Dict[str, Any]

    # Content generation phase
    content_outline: Dict[str, Any]
    draft_sections: List[NewsletterSection]
    discussion_summaries: Dict[str, List[Dict[str, Any]]]  # section_name -> [summary_data]
    grouped_discussions: Dict[str, List[Dict[str, Any]]]  # section_name -> [discussion_data]
    enriched_content: Dict[str, Any]  # NEW: news, events, memes, t-shirt ideas
    technical_analysis: Dict[str, str]
    writer_feedback: List[WriterFeedback]

    # Final output
    newsletter_draft: Optional[NewsletterDraft]
    formatted_content: Dict[str, str]  # html, markdown, text
    quality_metrics: Dict[str, float]

    # Workflow control
    current_step: str
    iteration_count: int
    errors: List[str]
    warnings: List[str]

    # Model selection
    selected_models: Dict[str, str]  # agent_name -> model_id
    model_costs: Dict[str, float]  # agent_name -> cost


class AgentResponse(BaseModel):
    """Standard response from an agent."""
    agent_name: str
    action: str
    output: Any
    confidence: float = 1.0
    reasoning: Optional[str] = None
    next_steps: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)