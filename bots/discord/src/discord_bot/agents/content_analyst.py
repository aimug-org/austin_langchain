"""Content analyst agent for summarizing and analyzing discussions."""

from typing import Dict, Any, List, Optional
from collections import defaultdict

from discord_bot.agents.base_agent import BaseNewsletterAgent
from discord_bot.agents.state import NewsletterState, AgentResponse, DiscussionData
from discord_bot.core.logging import get_logger

logger = get_logger(__name__)


class ContentAnalystAgent(BaseNewsletterAgent):
    """Agent responsible for analyzing and summarizing discussion content."""
    
    def __init__(self, model=None):
        super().__init__(
            name="ContentAnalystAgent",
            role="Technical Content Analyst",
            model=model,
            temperature=0.5,
            max_tokens=3000
        )
    
    def _create_system_prompt(self) -> str:
        return """You are a technical content analyst for the Austin LangChain community newsletter.
Your role is to:
1. Analyze Discord discussions for key insights and technical value
2. Summarize complex technical conversations clearly and concisely
3. Identify the main points, questions, and solutions discussed
4. Extract actionable insights and learning opportunities
5. Categorize discussions by topic and importance

Focus on:
- Technical accuracy and clarity
- Community value and relevance
- Educational opportunities
- Practical applications

Maintain a professional but approachable tone that reflects the collaborative spirit of the Austin tech community."""
    
    async def process(self, state: NewsletterState) -> AgentResponse:
        """Analyze discussions and create summaries."""
        discussions = state.get("discussions", [])
        research_results = state.get("research_results", [])
        
        if not discussions:
            return AgentResponse(
                agent_name=self.name,
                action="skip",
                output=None,
                reasoning="No discussions to analyze"
            )
        
        # Group discussions by category
        categorized_discussions = self._categorize_discussions(discussions)
        
        # Analyze each category
        content_analysis = {}
        for category, category_discussions in categorized_discussions.items():
            analysis = await self._analyze_category(
                category, 
                category_discussions,
                research_results
            )
            content_analysis[category] = analysis
        
        # Create content outline
        content_outline = await self._create_content_outline(
            content_analysis,
            state.get("newsletter_type", "daily")
        )
        
        return AgentResponse(
            agent_name=self.name,
            action="analysis_complete",
            output={
                "content_analysis": content_analysis,
                "content_outline": content_outline,
                "total_discussions": len(discussions),
                "categories_found": list(categorized_discussions.keys())
            },
            confidence=0.9,
            reasoning=f"Analyzed {len(discussions)} discussions across {len(categorized_discussions)} categories",
            next_steps=["technical_writing", "opinion_generation"]
        )
    
    def _categorize_discussions(self, discussions: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize discussions by topic."""
        categories = defaultdict(list)
        
        for discussion in discussions:
            discussion_categories = discussion.get("category", ["general"])
            primary_category = discussion_categories[0] if discussion_categories else "general"
            
            # Map to newsletter sections
            if primary_category == "ai-ml":
                categories["AI & Machine Learning"].append(discussion)
            elif primary_category == "programming":
                categories["Development & Tools"].append(discussion)
            elif primary_category == "community":
                categories["Community Updates"].append(discussion)
            elif primary_category == "learning":
                categories["Learning Resources"].append(discussion)
            else:
                categories["Technical Discussions"].append(discussion)
        
        # Sort discussions within each category by engagement score
        for category in categories:
            categories[category].sort(
                key=lambda x: x.get("engagement_score", 0),
                reverse=True
            )
        
        return dict(categories)
    
    async def _analyze_category(
        self, 
        category: str, 
        discussions: List[Dict],
        research_results: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze discussions in a specific category."""
        if not self.model:
            # Fallback analysis without LLM
            return self._create_fallback_analysis(category, discussions)
        
        # Prepare discussion summaries
        discussion_texts = []
        for d in discussions[:5]:  # Limit to top 5 discussions
            text = f"""
            Content: {d.get('content', '')}
            Engagement Score: {d.get('engagement_score', 0)}
            Replies: {d.get('reply_count', 0)}
            Keywords: {', '.join(d.get('keywords', []))}
            """
            discussion_texts.append(text)
        
        # Add relevant research
        relevant_research = [
            r for r in research_results 
            if category.lower() in r.get('topic', '').lower()
        ]
        
        prompt = f"""
        Analyze these {category} discussions from the Austin LangChain community:
        
        {chr(10).join(discussion_texts)}
        
        Research Context:
        {chr(10).join([r.get('findings', '') for r in relevant_research[:2]])}
        
        Provide:
        1. Key themes and insights
        2. Technical highlights
        3. Community questions or challenges
        4. Actionable takeaways
        5. Brief summary (2-3 sentences)
        
        Format as JSON with keys: themes, highlights, challenges, takeaways, summary
        """
        
        messages = self._create_messages(prompt)
        response = await self._call_llm(messages)
        analysis = self._extract_json_from_response(response)
        
        return {
            "category": category,
            "discussion_count": len(discussions),
            "top_discussions": [d.get("message_id") for d in discussions[:3]],
            **analysis
        }
    
    def _create_fallback_analysis(self, category: str, discussions: List[Dict]) -> Dict[str, Any]:
        """Create analysis without LLM."""
        # Extract common themes from keywords
        all_keywords = []
        for d in discussions:
            all_keywords.extend(d.get("keywords", []))
        
        keyword_counts = defaultdict(int)
        for keyword in all_keywords:
            keyword_counts[keyword] += 1
        
        top_themes = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "category": category,
            "discussion_count": len(discussions),
            "top_discussions": [d.get("message_id") for d in discussions[:3]],
            "themes": [theme[0] for theme in top_themes],
            "highlights": [f"High engagement discussion about {discussions[0].get('keywords', ['topics'])[0]}" if discussions else ""],
            "challenges": ["Community seeking solutions for common implementation patterns"],
            "takeaways": ["Active community engagement on technical topics"],
            "summary": f"{len(discussions)} discussions in {category} with focus on {top_themes[0][0] if top_themes else 'various topics'}"
        }
    
    async def _create_content_outline(
        self, 
        content_analysis: Dict[str, Dict],
        newsletter_type: str
    ) -> Dict[str, Any]:
        """Create a content outline for the newsletter."""
        outline = {
            "newsletter_type": newsletter_type,
            "sections": []
        }
        
        # Featured section (top discussions across all categories)
        all_discussions = []
        for analysis in content_analysis.values():
            all_discussions.extend(analysis.get("top_discussions", []))
        
        outline["sections"].append({
            "type": "featured",
            "title": "Featured Discussions",
            "content_source": "top_engaged",
            "discussion_ids": all_discussions[:3]
        })
        
        # Category sections
        for category, analysis in content_analysis.items():
            if analysis["discussion_count"] > 0:
                outline["sections"].append({
                    "type": "category",
                    "title": category,
                    "content_source": "category_analysis",
                    "discussion_ids": analysis.get("top_discussions", []),
                    "summary": analysis.get("summary", ""),
                    "themes": analysis.get("themes", [])
                })
        
        # Add special sections based on content
        if newsletter_type == "weekly":
            outline["sections"].append({
                "type": "trends",
                "title": "Weekly Trends & Insights",
                "content_source": "trend_analysis"
            })
        
        return outline