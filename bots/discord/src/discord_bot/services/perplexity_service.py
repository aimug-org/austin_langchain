"""Perplexity API service for research and fact-checking."""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx
import json

from discord_bot.core.config import settings
from discord_bot.core.logging import get_logger
from discord_bot.agents.state import ResearchResult

logger = get_logger(__name__)


class PerplexityService:
    """Service for interacting with Perplexity API for research and fact-checking."""
    
    def __init__(self):
        self.base_url = settings.perplexity_base_url
        self.api_key = settings.perplexity_api_key
        self.client: Optional[httpx.AsyncClient] = None
        self._rate_limit_remaining = 100  # Default rate limit
        self._rate_limit_reset = datetime.now(timezone.utc)
    
    async def initialize(self):
        """Initialize the Perplexity service."""
        if not self.api_key:
            logger.warning("Perplexity API key not configured")
            return
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        logger.info("Perplexity service initialized")
    
    async def close(self):
        """Close the Perplexity service."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Perplexity service closed")
    
    async def research_topic(
        self,
        query: str,
        topic_context: str = "",
        max_tokens: int = 500
    ) -> Optional[ResearchResult]:
        """Research a topic using Perplexity API."""
        if not self.client:
            await self.initialize()
        
        if not self.client or not self.api_key:
            logger.warning("Perplexity API not available, using fallback research")
            return self._fallback_research(query, topic_context)
        
        # Check rate limits
        if not await self._check_rate_limit():
            logger.warning("Perplexity API rate limit exceeded")
            return self._fallback_research(query, topic_context)
        
        try:
            # Prepare the research prompt
            research_prompt = self._create_research_prompt(query, topic_context)
            
            # Make API request
            response = await self._make_api_request(
                "/chat/completions",
                {
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a technical research assistant. Provide accurate, up-to-date information with sources."
                        },
                        {
                            "role": "user",
                            "content": research_prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.2,
                    "return_citations": True,
                    "search_domain_filter": ["github.com", "docs.python.org", "langchain.com", "python.langchain.com"]
                }
            )
            
            if response:
                return self._parse_research_response(query, response)
            
        except Exception as e:
            logger.error(f"Perplexity API research failed: {e}")
        
        # Fallback to local research
        return self._fallback_research(query, topic_context)
    
    async def fact_check(
        self,
        claim: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """Fact-check a claim using Perplexity API."""
        if not self.client:
            await self.initialize()
        
        if not self.client or not self.api_key:
            return self._fallback_fact_check(claim)
        
        # Check rate limits
        if not await self._check_rate_limit():
            return self._fallback_fact_check(claim)
        
        try:
            fact_check_prompt = f"""
            Fact-check this claim: "{claim}"
            
            Context: {context}
            
            Please verify:
            1. Is this claim accurate?
            2. What evidence supports or contradicts it?
            3. Are there any important caveats or nuances?
            4. What are the most reliable sources on this topic?
            
            Provide a clear assessment with citations.
            """
            
            response = await self._make_api_request(
                "/chat/completions",
                {
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a fact-checking expert. Provide accurate assessments with reliable sources."
                        },
                        {
                            "role": "user",
                            "content": fact_check_prompt
                        }
                    ],
                    "max_tokens": 400,
                    "temperature": 0.1,
                    "return_citations": True
                }
            )
            
            if response:
                return self._parse_fact_check_response(claim, response)
            
        except Exception as e:
            logger.error(f"Perplexity fact-check failed: {e}")
        
        return self._fallback_fact_check(claim)
    
    async def get_latest_updates(
        self,
        topics: List[str],
        time_range: str = "1 week"
    ) -> List[Dict[str, Any]]:
        """Get latest updates on specified topics."""
        if not self.client:
            await self.initialize()
        
        updates = []
        
        for topic in topics[:3]:  # Limit to 3 topics to avoid rate limits
            try:
                query = f"latest {topic} updates news {time_range} 2024 2025"
                
                if not self.client or not self.api_key:
                    # Fallback update
                    updates.append(self._fallback_update(topic))
                    continue
                
                if not await self._check_rate_limit():
                    updates.append(self._fallback_update(topic))
                    continue
                
                response = await self._make_api_request(
                    "/chat/completions",
                    {
                        "model": "sonar",
                        "messages": [
                            {
                                "role": "user",
                                "content": f"What are the latest developments in {topic}? Focus on recent updates, releases, or important news in the past {time_range}."
                            }
                        ],
                        "max_tokens": 300,
                        "temperature": 0.2,
                        "return_citations": True
                    }
                )
                
                if response:
                    update = self._parse_update_response(topic, response)
                    updates.append(update)
                else:
                    updates.append(self._fallback_update(topic))
                
                # Rate limiting between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to get updates for {topic}: {e}")
                updates.append(self._fallback_update(topic))
        
        return updates
    
    async def _make_api_request(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API request to Perplexity."""
        try:
            response = await self.client.post(endpoint, json=payload)
            
            # Update rate limit info
            self._update_rate_limits(response.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Perplexity API rate limit exceeded")
                return None
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return None
                
        except httpx.TimeoutException:
            logger.error("Perplexity API request timeout")
            return None
        except Exception as e:
            logger.error(f"Perplexity API request failed: {e}")
            return None
    
    def _create_research_prompt(self, query: str, context: str) -> str:
        """Create an optimized research prompt."""
        prompt = f"Research: {query}"
        
        if context:
            prompt += f"\n\nContext: {context}"
        
        prompt += """
        
        Please provide:
        1. Key findings and current information
        2. Recent developments or updates
        3. Best practices or recommendations
        4. Reliable sources for further reading
        
        Focus on accurate, up-to-date technical information.
        """
        
        return prompt
    
    def _parse_research_response(self, query: str, response: Dict[str, Any]) -> ResearchResult:
        """Parse research response from Perplexity API."""
        content = ""
        sources = []
        
        if "choices" in response and response["choices"]:
            choice = response["choices"][0]
            content = choice.get("message", {}).get("content", "")
            
            # Extract citations if present
            if "citations" in choice:
                sources = [cite.get("url", "") for cite in choice["citations"] if cite.get("url")]
        
        # Calculate relevance score based on content quality
        relevance_score = self._calculate_relevance_score(content, query)
        
        return ResearchResult(
            topic=query,
            query=query,
            findings=content,
            sources=sources[:5],  # Limit to top 5 sources
            relevance_score=relevance_score,
            timestamp=datetime.now(timezone.utc)
        )
    
    def _parse_fact_check_response(self, claim: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse fact-check response from Perplexity API."""
        result = {
            "claim": claim,
            "status": "unverified",
            "explanation": "",
            "sources": [],
            "confidence": 0.5
        }
        
        if "choices" in response and response["choices"]:
            choice = response["choices"][0]
            content = choice.get("message", {}).get("content", "")
            
            result["explanation"] = content
            
            # Extract sources
            if "citations" in choice:
                result["sources"] = [cite.get("url", "") for cite in choice["citations"] if cite.get("url")][:3]
            
            # Simple status extraction (could be improved with NLP)
            content_lower = content.lower()
            if any(word in content_lower for word in ["accurate", "correct", "true", "verified"]):
                result["status"] = "verified"
                result["confidence"] = 0.8
            elif any(word in content_lower for word in ["inaccurate", "incorrect", "false", "disputed"]):
                result["status"] = "disputed"
                result["confidence"] = 0.8
            elif any(word in content_lower for word in ["partially", "somewhat", "limited"]):
                result["status"] = "partially_verified"
                result["confidence"] = 0.6
        
        return result
    
    def _parse_update_response(self, topic: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse update response from Perplexity API."""
        update = {
            "topic": topic,
            "content": "",
            "sources": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if "choices" in response and response["choices"]:
            choice = response["choices"][0]
            update["content"] = choice.get("message", {}).get("content", "")
            
            if "citations" in choice:
                update["sources"] = [cite.get("url", "") for cite in choice["citations"] if cite.get("url")][:3]
        
        return update
    
    def _calculate_relevance_score(self, content: str, query: str) -> float:
        """Calculate relevance score for research content."""
        if not content:
            return 0.0
        
        # Simple relevance scoring based on query terms
        query_terms = query.lower().split()
        content_lower = content.lower()
        
        matches = sum(1 for term in query_terms if term in content_lower)
        base_score = matches / len(query_terms) if query_terms else 0
        
        # Boost score for longer, more detailed content
        length_bonus = min(0.3, len(content) / 1000)
        
        # Boost score for technical terms
        technical_terms = ["api", "framework", "library", "implementation", "documentation"]
        tech_bonus = sum(0.05 for term in technical_terms if term in content_lower)
        
        return min(1.0, base_score + length_bonus + tech_bonus)
    
    async def _check_rate_limit(self) -> bool:
        """Check if we can make an API request based on rate limits."""
        now = datetime.now(timezone.utc)
        
        # Reset rate limit if time has passed
        if now >= self._rate_limit_reset:
            self._rate_limit_remaining = 100  # Reset to default
        
        return self._rate_limit_remaining > 0
    
    def _update_rate_limits(self, headers: Dict[str, str]):
        """Update rate limit tracking from API response headers."""
        if "x-ratelimit-remaining" in headers:
            self._rate_limit_remaining = int(headers["x-ratelimit-remaining"])
        
        if "x-ratelimit-reset" in headers:
            reset_timestamp = int(headers["x-ratelimit-reset"])
            self._rate_limit_reset = datetime.fromtimestamp(reset_timestamp, tz=timezone.utc)
    
    def _fallback_research(self, query: str, context: str = "") -> ResearchResult:
        """Fallback research when Perplexity API is not available."""
        # Simulate research based on common Austin LangChain topics
        fallback_content = {
            "langchain": "LangChain is a framework for developing applications powered by language models. Recent updates include improved agent capabilities and better integration with vector databases.",
            "langgraph": "LangGraph is LangChain's library for building stateful, multi-actor applications with LLMs. It provides a graph-based approach to workflow orchestration.",
            "rag": "Retrieval Augmented Generation (RAG) combines language models with external knowledge sources. Best practices include proper chunking, embedding optimization, and retrieval scoring.",
            "agent": "AI agents are autonomous systems that can perform tasks and make decisions. Current trends focus on multi-agent workflows and tool integration.",
            "austin": "Austin has a vibrant tech community with regular meetups, conferences, and networking events focused on AI/ML and software development."
        }
        
        # Find relevant fallback content
        query_lower = query.lower()
        findings = "Research not available without Perplexity API. "
        
        for keyword, content in fallback_content.items():
            if keyword in query_lower:
                findings += content
                break
        else:
            findings += "Please check the latest documentation and community resources for current information."
        
        return ResearchResult(
            topic=query,
            query=query,
            findings=findings,
            sources=["https://langchain.com/docs", "https://github.com/langchain-ai"],
            relevance_score=0.6,
            timestamp=datetime.now(timezone.utc)
        )
    
    def _fallback_fact_check(self, claim: str) -> Dict[str, Any]:
        """Fallback fact-check when API is not available."""
        return {
            "claim": claim,
            "status": "unverified",
            "explanation": "Fact-checking not available without Perplexity API. Please verify information manually.",
            "sources": [],
            "confidence": 0.3
        }
    
    def _fallback_update(self, topic: str) -> Dict[str, Any]:
        """Fallback update when API is not available."""
        return {
            "topic": topic,
            "content": f"Latest updates for {topic} are not available without Perplexity API. Check official documentation and community channels.",
            "sources": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of Perplexity service."""
        health = {
            "service": "perplexity",
            "status": "unknown",
            "api_key_configured": bool(self.api_key),
            "client_initialized": bool(self.client),
            "rate_limit_remaining": self._rate_limit_remaining,
            "last_reset": self._rate_limit_reset.isoformat() if self._rate_limit_reset else None
        }
        
        if not self.api_key:
            health["status"] = "disabled"
            return health
        
        if not self.client:
            try:
                await self.initialize()
            except Exception as e:
                health["status"] = "error"
                health["error"] = str(e)
                return health
        
        # Try a simple test request
        try:
            test_response = await self._make_api_request(
                "/chat/completions",
                {
                    "model": "sonar",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
            )
            
            if test_response:
                health["status"] = "healthy"
            else:
                health["status"] = "error"
                health["error"] = "API request failed"
                
        except Exception as e:
            health["status"] = "error"
            health["error"] = str(e)
        
        return health


# Global Perplexity service instance
perplexity_service = PerplexityService()