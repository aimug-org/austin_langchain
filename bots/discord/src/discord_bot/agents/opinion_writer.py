"""Opinion writer agent for providing technical commentary."""

from typing import Dict, Any, List
import random

from discord_bot.agents.base_agent import BaseNewsletterAgent
from discord_bot.agents.state import NewsletterState, AgentResponse
from discord_bot.core.logging import get_logger

logger = get_logger(__name__)


class OpinionWriterAgent(BaseNewsletterAgent):
    """Agent responsible for providing professional technical commentary."""
    
    def __init__(self, model=None):
        super().__init__(
            name="OpinionWriterAgent",
            role="Senior Technical Writer",
            model=model,
            temperature=0.7,  # Higher temperature for more creative writing
            max_tokens=2500
        )
    
    def _create_system_prompt(self) -> str:
        return """You are a senior technical writer providing expert commentary for the Austin LangChain community newsletter.

Your role is to:
1. Provide thoughtful, professional commentary on technical discussions
2. Offer balanced perspectives on implementation approaches
3. Highlight best practices and potential pitfalls
4. Encourage community learning and collaboration
5. Maintain a respectful, constructive tone

Guidelines:
- Focus on ideas and technical merit, never criticize individuals
- Provide actionable insights and recommendations
- Reference industry best practices and standards
- Acknowledge multiple valid approaches when applicable
- Encourage experimentation and learning

Your commentary should be:
- Professional yet approachable
- Technically accurate and well-reasoned
- Constructive and forward-looking
- Supportive of the community's growth"""
    
    async def process(self, state: NewsletterState) -> AgentResponse:
        """Generate technical commentary for selected discussions."""
        content_analysis = state.get("content_outline", {})
        research_results = state.get("research_results", [])
        discussions = state.get("discussions", [])
        
        if not content_analysis or not discussions:
            return AgentResponse(
                agent_name=self.name,
                action="skip",
                output=None,
                reasoning="No content outline or discussions for commentary"
            )
        
        # Select discussions for commentary
        featured_discussions = self._select_featured_discussions(
            discussions, 
            content_analysis
        )
        
        # Generate commentary for each featured discussion
        technical_analysis = {}
        for discussion in featured_discussions:
            commentary = await self._generate_commentary(
                discussion,
                research_results
            )
            technical_analysis[discussion["message_id"]] = commentary
        
        # Generate section introductions
        section_intros = await self._generate_section_intros(content_analysis)
        
        return AgentResponse(
            agent_name=self.name,
            action="commentary_complete",
            output={
                "technical_analysis": technical_analysis,
                "section_intros": section_intros,
                "featured_count": len(featured_discussions)
            },
            confidence=0.85,
            reasoning=f"Generated commentary for {len(featured_discussions)} discussions",
            next_steps=["content_editing", "final_review"]
        )
    
    def _select_featured_discussions(
        self, 
        discussions: List[Dict], 
        content_outline: Dict
    ) -> List[Dict]:
        """Select discussions for detailed commentary."""
        featured_ids = []
        
        # Get featured discussion IDs from outline
        for section in content_outline.get("sections", []):
            if section.get("type") == "featured":
                featured_ids.extend(section.get("discussion_ids", []))
        
        # Find the actual discussion objects
        featured_discussions = []
        for discussion in discussions:
            if discussion.get("message_id") in featured_ids:
                featured_discussions.append(discussion)
        
        # If no featured discussions, select top 3 by engagement
        if not featured_discussions:
            sorted_discussions = sorted(
                discussions, 
                key=lambda x: x.get("engagement_score", 0),
                reverse=True
            )
            featured_discussions = sorted_discussions[:3]
        
        return featured_discussions
    
    async def _generate_commentary(
        self, 
        discussion: Dict,
        research_results: List[Dict]
    ) -> Dict[str, str]:
        """Generate technical commentary for a discussion."""
        if not self.model:
            return self._create_fallback_commentary(discussion)
        
        # Find relevant research
        keywords = discussion.get("keywords", [])
        relevant_research = [
            r for r in research_results
            if any(kw.lower() in r.get("topic", "").lower() for kw in keywords)
        ]
        
        prompt = f"""
        Provide technical commentary on this community discussion:
        
        Content: {discussion.get('content', '')}
        Keywords: {', '.join(keywords)}
        Category: {', '.join(discussion.get('category', ['general']))}
        Engagement: {discussion.get('engagement_score', 0)} score with {discussion.get('reply_count', 0)} replies
        
        Research Context:
        {chr(10).join([r.get('findings', '') for r in relevant_research[:1]])}
        
        Provide:
        1. Technical perspective on the approach/question discussed
        2. Best practices or recommendations
        3. Potential considerations or alternatives
        4. Encouragement for community learning
        
        Keep it professional, constructive, and under 200 words.
        Focus on the technical aspects, not individuals.
        """
        
        messages = self._create_messages(prompt)
        response = await self._call_llm(messages)
        
        return {
            "commentary": response,
            "focus_areas": keywords[:3],
            "discussion_type": discussion.get("category", ["general"])[0]
        }
    
    def _create_fallback_commentary(self, discussion: Dict) -> Dict[str, str]:
        """Create commentary without LLM."""
        keywords = discussion.get("keywords", [])
        category = discussion.get("category", ["general"])[0]
        
        # Template-based commentary
        templates = {
            "ai-ml": [
                f"This discussion about {keywords[0] if keywords else 'AI/ML'} highlights the community's growing interest in practical AI implementations. "
                "The engagement shows that many developers are actively exploring these technologies. "
                "Consider experimenting with different approaches and sharing your findings with the community."
            ],
            "programming": [
                f"The technical discussion around {keywords[0] if keywords else 'development'} demonstrates the community's commitment to best practices. "
                "High engagement on this topic suggests it's a common challenge many developers face. "
                "Remember that there are often multiple valid approaches to solving technical problems."
            ],
            "community": [
                "Community discussions like this are vital for the growth of Austin's tech ecosystem. "
                "The engagement here shows the strength of our local developer community. "
                "Keep these conversations going—they benefit everyone involved."
            ]
        }
        
        commentary = templates.get(category, templates["community"])[0]
        
        return {
            "commentary": commentary,
            "focus_areas": keywords[:3],
            "discussion_type": category
        }
    
    async def _generate_section_intros(self, content_outline: Dict) -> Dict[str, str]:
        """Generate introductions for each newsletter section."""
        section_intros = {}
        
        for section in content_outline.get("sections", []):
            section_type = section.get("type")
            title = section.get("title")
            
            if section_type == "featured":
                section_intros[title] = (
                    "This week's most engaging discussions showcase the depth and breadth "
                    "of technical exploration happening in our community. From cutting-edge "
                    "AI implementations to practical development tips, these conversations "
                    "represent the best of Austin LangChain."
                )
            elif section_type == "category":
                themes = section.get("themes", [])
                theme_text = f"focusing on {', '.join(themes[:2])}" if themes else ""
                section_intros[title] = (
                    f"The {title} section highlights important discussions {theme_text}. "
                    "These conversations demonstrate our community's commitment to "
                    "continuous learning and technical excellence."
                )
            elif section_type == "trends":
                section_intros[title] = (
                    "This week's trends reveal the evolving interests and challenges "
                    "facing our developer community. From emerging technologies to "
                    "time-tested best practices, these insights help us stay ahead "
                    "in the rapidly changing tech landscape."
                )
        
        return section_intros