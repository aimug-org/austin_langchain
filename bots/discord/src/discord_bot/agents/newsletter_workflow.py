"""LangGraph workflow for newsletter generation."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from discord_bot.agents.state import NewsletterState, DiscussionData
from discord_bot.agents.research_agent import ResearchAgent
from discord_bot.agents.content_analyst import ContentAnalystAgent
from discord_bot.agents.discussion_writer import DiscussionWriterAgent
from discord_bot.agents.opinion_writer import OpinionWriterAgent
from discord_bot.agents.editor_agent import EditorAgent
from discord_bot.agents.content_enrichment_agent import ContentEnrichmentAgent
from discord_bot.agents.formatter_agent import FormatterAgent
from discord_bot.core.logging import get_logger
from discord_bot.core.config import settings
from discord_bot.services.model_router import model_router, ModelCapability

logger = get_logger(__name__)


class NewsletterWorkflow:
    """LangGraph workflow for newsletter generation."""
    
    def __init__(self):
        self.graph: Optional[StateGraph] = None
        self.compiled_graph = None
        self.agents = {}
        self._initialize_agents()
        self._build_graph()
    
    def _initialize_agents(self):
        """Initialize all workflow agents."""
        # Initialize LangChain chat models directly
        from langchain_openai import ChatOpenAI

        # Use OpenAI models since we have the API key
        try:
            if settings.openai_api_key:
                writing_model = ChatOpenAI(
                    model="gpt-4o-mini",  # Use gpt-4o-mini for cost efficiency
                    api_key=settings.openai_api_key,
                    temperature=0.7
                )
                editing_model = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=settings.openai_api_key,
                    temperature=0.3
                )
                logger.info("Initialized OpenAI models for agents")
            else:
                # No API keys available, use None (will trigger fallbacks)
                writing_model = None
                editing_model = None
                logger.warning("No API keys configured for LLM models")

        except Exception as e:
            logger.error(f"Failed to initialize LLM models: {e}")
            writing_model = None
            editing_model = None

        # Initialize agents with models
        self.agents = {
            "research": ResearchAgent(model=writing_model),
            "content_analyst": ContentAnalystAgent(model=writing_model),
            "discussion_writer": DiscussionWriterAgent(model=writing_model),  # NEW: Generate detailed summaries
            "opinion_writer": OpinionWriterAgent(model=writing_model),
            "content_enrichment": ContentEnrichmentAgent(model=writing_model),  # NEW: Add news, events, memes
            "editor": EditorAgent(model=editing_model),
            "formatter": FormatterAgent(model=editing_model)
        }

        logger.info("Initialized newsletter workflow agents", extra={
            "agents": list(self.agents.keys()),
            "writing_model": writing_model.__class__.__name__ if writing_model else "None",
            "editing_model": editing_model.__class__.__name__ if editing_model else "None"
        })
    
    def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(NewsletterState)

        # Add nodes for each agent
        workflow.add_node("research", self._research_node)
        workflow.add_node("content_analysis", self._content_analysis_node)
        workflow.add_node("discussion_writing", self._discussion_writing_node)  # NEW: Generate detailed summaries
        workflow.add_node("opinion_writing", self._opinion_writing_node)
        workflow.add_node("content_enrichment", self._content_enrichment_node)  # NEW: Add news, events, memes
        workflow.add_node("editing", self._editing_node)
        workflow.add_node("formatting", self._formatting_node)
        workflow.add_node("quality_check", self._quality_check_node)

        # Define the workflow edges
        workflow.set_entry_point("research")

        workflow.add_edge("research", "content_analysis")
        workflow.add_edge("content_analysis", "discussion_writing")  # NEW: Write detailed summaries
        workflow.add_edge("discussion_writing", "content_enrichment")  # NEW: Enrich with news, events, memes
        workflow.add_edge("content_enrichment", "opinion_writing")
        workflow.add_edge("opinion_writing", "editing")
        workflow.add_edge("editing", "formatting")
        workflow.add_edge("formatting", "quality_check")
        
        # Conditional edge for quality check
        workflow.add_conditional_edges(
            "quality_check",
            self._should_iterate,
            {
                "iterate": "content_analysis",  # Go back to content analysis for iteration
                "complete": END
            }
        )
        
        self.graph = workflow
        self.compiled_graph = workflow.compile()
        
        logger.info("Built newsletter generation workflow")
    
    async def generate_newsletter(
        self,
        discussions: List[DiscussionData],
        newsletter_type: str = "daily",
        target_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a newsletter from discussions."""
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        # Prepare initial state
        initial_state: NewsletterState = {
            "newsletter_type": newsletter_type,
            "target_date": target_date,
            "discussions": [d.dict() if hasattr(d, 'dict') else d for d in discussions],
            "research_topics": [],
            "research_results": [],
            "fact_check_results": {},
            "content_outline": {},
            "draft_sections": [],
            "discussion_summaries": {},
            "grouped_discussions": {},
            "enriched_content": {},  # NEW: news, events, memes
            "technical_analysis": {},
            "writer_feedback": [],
            "newsletter_draft": None,
            "quality_metrics": {},
            "current_step": "research",
            "iteration_count": 0,
            "errors": [],
            "warnings": [],
            "selected_models": {},
            "model_costs": {}
        }
        
        logger.info("Starting newsletter generation", extra={
            "newsletter_type": newsletter_type,
            "discussion_count": len(discussions),
            "target_date": target_date
        })
        
        try:
            # Run the workflow
            config = RunnableConfig(
                configurable={
                    "thread_id": f"newsletter_{newsletter_type}_{target_date}",
                    "checkpoint_ns": "newsletter_generation"
                }
            )
            
            result = await self.compiled_graph.ainvoke(initial_state, config)
            
            logger.info("Newsletter generation completed", extra={
                "final_step": result.get("current_step"),
                "iterations": result.get("iteration_count"),
                "total_word_count": result.get("quality_metrics", {}).get("total_word_count", 0)
            })
            
            return result
            
        except Exception as e:
            logger.error("Newsletter generation failed", extra={
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    async def _research_node(self, state: NewsletterState) -> NewsletterState:
        """Research node in the workflow."""
        state["current_step"] = "research"
        
        try:
            # Get model for research capability
            model_info = await model_router.get_model_for_capability(ModelCapability.RESEARCH)
            if model_info:
                state["selected_models"]["research"] = model_info.id
            
            response = await self.agents["research"].invoke(state)
            
            if response.output:
                state["research_topics"] = response.output.get("research_topics", [])
                state["research_results"] = response.output.get("research_results", [])
            
        except Exception as e:
            state["errors"].append(f"Research step failed: {str(e)}")
            logger.error("Research step failed", extra={"error": str(e)})
        
        return state
    
    async def _content_analysis_node(self, state: NewsletterState) -> NewsletterState:
        """Content analysis node in the workflow."""
        state["current_step"] = "content_analysis"
        
        try:
            # Get model for content analysis
            model_info = await model_router.get_model_for_capability(ModelCapability.TECHNICAL_ANALYSIS)
            if model_info:
                state["selected_models"]["content_analysis"] = model_info.id
            
            response = await self.agents["content_analyst"].invoke(state)
            
            if response.output:
                state["content_outline"] = response.output.get("content_outline", {})
                # Initialize draft sections based on content outline
                outline = state["content_outline"]
                draft_sections = []
                
                for section in outline.get("sections", []):
                    draft_sections.append({
                        "section_type": section.get("type", "general"),
                        "title": section.get("title", "Untitled"),
                        "content": f"Content for {section.get('title')} section will be generated...",
                        "discussion_ids": section.get("discussion_ids", []),
                        "word_count": 0
                    })
                
                state["draft_sections"] = draft_sections
        
        except Exception as e:
            state["errors"].append(f"Content analysis step failed: {str(e)}")
            logger.error("Content analysis step failed", extra={"error": str(e)})
        
        return state

    async def _discussion_writing_node(self, state: NewsletterState) -> NewsletterState:
        """Discussion writing node - generates detailed discussion summaries."""
        state["current_step"] = "discussion_writing"

        try:
            # Get model for discussion writing
            model_info = await model_router.get_model_for_capability(ModelCapability.CONTENT_WRITING)
            if model_info:
                state["selected_models"]["discussion_writing"] = model_info.id

            response = await self.agents["discussion_writer"].invoke(state)

            if response.output:
                # Store discussion summaries and grouped discussions
                state["discussion_summaries"] = response.output.get("discussion_summaries", {})
                state["grouped_discussions"] = response.output.get("grouped_discussions", {})

                # Collect ALL discussions across all sections
                all_summaries = []
                for section_name, summaries in state["discussion_summaries"].items():
                    for summary_data in summaries:
                        all_summaries.append({
                            **summary_data,
                            "original_section": section_name
                        })

                # Sort by engagement score to get top discussions
                all_summaries.sort(key=lambda x: x["engagement"]["score"], reverse=True)

                # Separate top 3 as featured
                featured_summaries = all_summaries[:3]
                remaining_summaries = all_summaries[3:]

                # Build draft sections with new layout
                draft_sections = []

                # 1. Top 3 Featured Discussions
                if featured_summaries:
                    featured_content = []
                    for idx, summary_data in enumerate(featured_summaries, 1):
                        disc_summary = summary_data["summary"]
                        channel = summary_data["channel"]
                        discord_link = summary_data.get("discord_link")
                        engagement = summary_data["engagement"]
                        cross_channel = summary_data.get("cross_channel_info", "")

                        # Format featured item with ranking
                        item = f"### {idx}. Featured Discussion\n\n"
                        item += f"{disc_summary}\n\n"
                        item += f"*Channel: #{channel}"
                        if discord_link:
                            item += f" | [View Discussion]({discord_link})"
                        item += f" | 💬 {engagement['replies']} replies | 👍 {engagement['reactions']} reactions*"
                        if cross_channel:
                            item += cross_channel
                        item += "\n"

                        featured_content.append(item)

                    draft_sections.append({
                        "section_type": "featured",
                        "title": "🔥 Top Discussions This Week",
                        "content": "\n".join(featured_content),
                        "discussion_ids": [s["message_id"] for s in featured_summaries],
                        "word_count": sum(len(item.split()) for item in featured_content)
                    })

                # 2. Remaining discussions organized by original sections
                section_groups = {}
                for summary_data in remaining_summaries:
                    section_name = summary_data["original_section"]
                    if section_name not in section_groups:
                        section_groups[section_name] = []
                    section_groups[section_name].append(summary_data)

                for section_name, summaries in section_groups.items():
                    if summaries:
                        section_content = []
                        for summary_data in summaries:
                            disc_summary = summary_data["summary"]
                            channel = summary_data["channel"]
                            discord_link = summary_data.get("discord_link")
                            engagement = summary_data["engagement"]
                            cross_channel = summary_data.get("cross_channel_info", "")

                            # Format discussion item
                            item = f"{disc_summary}\n"
                            item += f"*Channel: #{channel}"
                            if discord_link:
                                item += f" | [View Discussion]({discord_link})"
                            item += f" | 💬 {engagement['replies']} replies | 👍 {engagement['reactions']} reactions*"
                            if cross_channel:
                                item += cross_channel
                            item += "\n"

                            section_content.append(item)

                        draft_sections.append({
                            "section_type": "category",
                            "title": section_name,
                            "content": "\n".join(section_content),
                            "discussion_ids": [s["message_id"] for s in summaries],
                            "word_count": sum(len(item.split()) for item in section_content)
                        })

                state["draft_sections"] = draft_sections

        except Exception as e:
            state["errors"].append(f"Discussion writing step failed: {str(e)}")
            logger.error("Discussion writing step failed", extra={"error": str(e)})

        return state

    async def _content_enrichment_node(self, state: NewsletterState) -> NewsletterState:
        """Content enrichment node - adds news, events, memes, and t-shirt ideas."""
        state["current_step"] = "content_enrichment"

        try:
            response = await self.agents["content_enrichment"].invoke(state)

            if response.output:
                # Store enriched content
                state["enriched_content"] = response.output

                # Add enriched content to draft sections
                newsletter_type = state.get("newsletter_type", "weekly")
                draft_sections = state.get("draft_sections", [])

                # Insert news section after featured discussions
                news_article = response.output.get("news_article")
                if news_article:
                    news_content = f"**{news_article['title']}**\n\n"
                    news_content += f"{news_article['summary']}\n\n"
                    if news_article.get('url'):
                        news_content += f"[Read Full Article]({news_article['url']})"
                    if news_article.get('discord_link'):
                        news_content += f" | [Discussion]({news_article['discord_link']})"

                    # Insert after featured (index 1)
                    draft_sections.insert(1, {
                        "section_type": "news",
                        "title": "📰 Community News",
                        "content": news_content,
                        "discussion_ids": [],
                        "word_count": len(news_content.split())
                    })

                # Add events section for monthly newsletters
                if newsletter_type == "monthly":
                    events = response.output.get("events", [])
                    if events:
                        events_content = []
                        for event in events:
                            event_item = f"**{event['title']}**  \n"
                            event_item += f"{event['description']}  \n"
                            event_item += f"📅 {event['date']}  \n"
                            if event.get('location'):
                                event_item += f"📍 {event['location']}  \n"
                            if event.get('url'):
                                event_item += f"[Learn More]({event['url']})\n"
                            events_content.append(event_item)

                        draft_sections.append({
                            "section_type": "events",
                            "title": "📅 Upcoming Events",
                            "content": "\n".join(events_content),
                            "discussion_ids": [],
                            "word_count": sum(len(e.split()) for e in events_content)
                        })

                # Add meme section
                meme = response.output.get("meme_image")
                if meme:
                    meme_content = f"![Top Community Meme]({meme['image_url']})\n\n"
                    if meme.get('caption'):
                        meme_content += f"*{meme['caption']}*\n\n"
                    if meme.get('discord_link'):
                        meme_content += f"[View in Discord]({meme['discord_link']})"

                    draft_sections.append({
                        "section_type": "meme",
                        "title": "😂 Top Community Meme",
                        "content": meme_content,
                        "discussion_ids": [],
                        "word_count": len(meme_content.split())
                    })

                # Add t-shirt ideas section
                tshirt_ideas = response.output.get("tshirt_ideas", [])
                if tshirt_ideas:
                    tshirt_content = "Community members have shared these creative design ideas! Images tagged with 👕 are considered for future AIMUG merchandise.\n\n"
                    for idx, idea in enumerate(tshirt_ideas, 1):
                        tshirt_content += f"**Idea {idx}**  \n"
                        tshirt_content += f"![T-Shirt Idea {idx}]({idea['image_url']})  \n"
                        if idea.get('description'):
                            tshirt_content += f"*{idea['description']}*  \n"
                        if idea.get('discord_link'):
                            tshirt_content += f"[View in Discord]({idea['discord_link']})  \n"
                        tshirt_content += "\n"

                    draft_sections.append({
                        "section_type": "tshirt",
                        "title": "👕 T-Shirt Design Ideas",
                        "content": tshirt_content,
                        "discussion_ids": [],
                        "word_count": len(tshirt_content.split())
                    })

                state["draft_sections"] = draft_sections

        except Exception as e:
            state["errors"].append(f"Content enrichment step failed: {str(e)}")
            logger.error("Content enrichment step failed", extra={"error": str(e)})

        return state

    async def _opinion_writing_node(self, state: NewsletterState) -> NewsletterState:
        """Opinion writing node in the workflow."""
        state["current_step"] = "opinion_writing"
        
        try:
            # Get model for opinion writing
            model_info = await model_router.get_model_for_capability(ModelCapability.CONTENT_WRITING)
            if model_info:
                state["selected_models"]["opinion_writing"] = model_info.id
            
            response = await self.agents["opinion_writer"].invoke(state)
            
            if response.output:
                state["technical_analysis"] = response.output.get("technical_analysis", {})
                
                # Update draft sections with generated content
                section_intros = response.output.get("section_intros", {})
                for section in state["draft_sections"]:
                    title = section["title"]
                    if title in section_intros:
                        section["content"] = section_intros[title]
                        section["word_count"] = len(section["content"].split())
        
        except Exception as e:
            state["errors"].append(f"Opinion writing step failed: {str(e)}")
            logger.error("Opinion writing step failed", extra={"error": str(e)})
        
        return state
    
    async def _editing_node(self, state: NewsletterState) -> NewsletterState:
        """Editing node in the workflow."""
        state["current_step"] = "editing"
        
        try:
            # Get model for editing
            model_info = await model_router.get_model_for_capability(ModelCapability.EDITING)
            if model_info:
                state["selected_models"]["editing"] = model_info.id
            
            response = await self.agents["editor"].invoke(state)
            
            if response.output:
                state["draft_sections"] = response.output.get("edited_sections", state["draft_sections"])
                state["writer_feedback"] = response.output.get("writer_feedback", [])
                state["quality_metrics"] = response.output.get("quality_metrics", {})
        
        except Exception as e:
            state["errors"].append(f"Editing step failed: {str(e)}")
            logger.error("Editing step failed", extra={"error": str(e)})
        
        return state
    
    async def _formatting_node(self, state: NewsletterState) -> NewsletterState:
        """Formatting node in the workflow."""
        state["current_step"] = "formatting"
        
        try:
            # Get model for formatting (usually simpler model is fine)
            model_info = await model_router.get_model_for_capability(ModelCapability.FORMATTING)
            if model_info:
                state["selected_models"]["formatting"] = model_info.id
            
            response = await self.agents["formatter"].invoke(state)
            
            if response.output:
                state["newsletter_draft"] = response.output.get("newsletter_draft")
                # Store formatted content for later use
                state["formatted_content"] = {
                    "html": response.output.get("html_content"),
                    "markdown": response.output.get("markdown_content"),
                    "text": response.output.get("text_content")
                }
        
        except Exception as e:
            state["errors"].append(f"Formatting step failed: {str(e)}")
            logger.error("Formatting step failed", extra={"error": str(e)})
        
        return state
    
    async def _quality_check_node(self, state: NewsletterState) -> NewsletterState:
        """Quality check node in the workflow."""
        state["current_step"] = "quality_check"
        
        quality_score = state.get("quality_metrics", {}).get("overall_score", 0.8)
        error_count = len(state.get("errors", []))
        
        # Check if quality meets standards
        if quality_score < 0.7 or error_count > 2:
            if state.get("iteration_count", 0) < 2:  # Max 2 iterations
                state["warnings"].append("Quality below threshold, initiating revision")
                state["iteration_count"] = state.get("iteration_count", 0) + 1
                logger.warning("Quality check failed, initiating revision", extra={
                    "quality_score": quality_score,
                    "error_count": error_count,
                    "iteration": state["iteration_count"]
                })
            else:
                state["warnings"].append("Max iterations reached, proceeding with current quality")
        
        return state
    
    def _should_iterate(self, state: NewsletterState) -> str:
        """Determine if workflow should iterate or complete."""
        quality_score = state.get("quality_metrics", {}).get("overall_score", 0.8)
        error_count = len(state.get("errors", []))
        iteration_count = state.get("iteration_count", 0)
        
        # Iterate if quality is low and we haven't exceeded max iterations
        if (quality_score < 0.7 or error_count > 2) and iteration_count < 2:
            return "iterate"
        else:
            return "complete"
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            "agents_initialized": len(self.agents),
            "graph_built": self.graph is not None,
            "compiled": self.compiled_graph is not None,
            "agent_names": list(self.agents.keys()),
            "model_router_available": model_router is not None
        }


# Global workflow instance
newsletter_workflow = NewsletterWorkflow()