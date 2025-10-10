"""Research agent for fact-checking and gathering additional context."""

from typing import Dict, Any, List, Optional
from datetime import datetime

from discord_bot.agents.base_agent import BaseNewsletterAgent
from discord_bot.agents.state import NewsletterState, AgentResponse, ResearchResult
from discord_bot.core.logging import get_logger
from discord_bot.services.perplexity_service import perplexity_service

logger = get_logger(__name__)


class ResearchAgent(BaseNewsletterAgent):
    """Agent responsible for researching topics and fact-checking."""
    
    def __init__(self, model=None):
        super().__init__(
            name="ResearchAgent",
            role="Technical Research Specialist",
            model=model,
            temperature=0.3,  # Lower temperature for factual research
            max_tokens=2000
        )
    
    def _create_system_prompt(self) -> str:
        return """You are a technical research specialist for the Austin LangChain community newsletter.
Your role is to:
1. Identify topics that need additional research or fact-checking
2. Formulate precise research queries
3. Verify technical claims and provide accurate context
4. Find relevant industry updates and trends
5. Ensure all information is current and accurate

You have access to web search capabilities through Perplexity API.
Focus on LangChain, AI/ML, and Austin tech community topics.
Always prioritize accuracy and cite sources when possible."""
    
    async def process(self, state: NewsletterState) -> AgentResponse:
        """Process discussions and identify research needs."""
        discussions = state.get("discussions", [])
        
        if not discussions:
            return AgentResponse(
                agent_name=self.name,
                action="skip",
                output=None,
                reasoning="No discussions provided for research"
            )
        
        # Extract research topics from discussions
        research_topics = await self._identify_research_topics(discussions)
        
        # Perform research for each topic
        research_results = []
        for topic in research_topics[:5]:  # Limit to top 5 topics
            result = await self._research_topic(topic, discussions)
            if result:
                research_results.append(result)
        
        return AgentResponse(
            agent_name=self.name,
            action="research_complete",
            output={
                "research_topics": research_topics,
                "research_results": [r.dict() for r in research_results]
            },
            confidence=0.9 if research_results else 0.5,
            reasoning=f"Researched {len(research_results)} topics from {len(discussions)} discussions",
            next_steps=["content_analysis", "fact_verification"]
        )
    
    async def _identify_research_topics(self, discussions: List[Dict]) -> List[str]:
        """Identify topics that need research."""
        # Analyze discussions for technical topics
        topics_to_research = []
        
        for discussion in discussions:
            keywords = discussion.get("keywords", [])
            content = discussion.get("content", "")
            
            # Look for technical terms that might need clarification
            if any(keyword in ["langchain", "langgraph", "agent", "rag"] for keyword in keywords):
                # Extract potential research topics
                if "langchain" in content.lower() and "update" in content.lower():
                    topics_to_research.append("Latest LangChain updates and releases")
                
                if "langgraph" in content.lower():
                    topics_to_research.append("LangGraph best practices and patterns")
                
                if "agent" in content.lower() and any(word in content.lower() for word in ["build", "create", "implement"]):
                    topics_to_research.append("AI agent implementation techniques")
                
                if "rag" in content.lower() or "retrieval" in content.lower():
                    topics_to_research.append("RAG (Retrieval Augmented Generation) advancements")
        
        # Also add general topics
        topics_to_research.extend([
            "Austin tech community events this week",
            "AI/ML industry news and trends"
        ])
        
        # Remove duplicates and return
        return list(set(topics_to_research))
    
    async def _research_topic(self, topic: str, discussions: List[Dict]) -> Optional[ResearchResult]:
        """Research a specific topic."""
        # Create research query
        query = self._create_research_query(topic, discussions)
        
        # Use Perplexity service for research
        research_result = await perplexity_service.research_topic(
            query=query,
            topic_context=topic
        )
        
        if research_result:
            logger.info(f"Researched topic: {topic}", extra={
                "topic": topic,
                "relevance_score": research_result.relevance_score
            })
        
        return research_result
    
    def _create_research_query(self, topic: str, discussions: List[Dict]) -> str:
        """Create an optimized research query."""
        # Add context from discussions
        discussion_context = []
        for d in discussions[:3]:  # Use top 3 discussions for context
            if any(keyword in topic.lower() for keyword in d.get("keywords", [])):
                discussion_context.append(d.get("content", "")[:100])
        
        # Build query
        query_parts = [topic]
        
        # Add temporal context
        if "update" in topic.lower() or "latest" in topic.lower():
            query_parts.append("2024 2025")
        
        # Add location context for community topics
        if "austin" in topic.lower() or "community" in topic.lower():
            query_parts.append("Austin Texas tech community")
        
        # Add technical context
        if "langchain" in topic.lower():
            query_parts.append("LangChain LangGraph LangSmith")
        
        return " ".join(query_parts)
    
    async def fact_check(self, claim: str, context: str = "") -> Dict[str, Any]:
        """Fact-check a specific claim."""
        # Use Perplexity service for fact-checking
        return await perplexity_service.fact_check(claim, context)