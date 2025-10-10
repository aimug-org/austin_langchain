"""Editor agent for reviewing and refining newsletter content."""

from typing import Dict, Any, List, Optional
import re

from discord_bot.agents.base_agent import BaseNewsletterAgent
from discord_bot.agents.state import NewsletterState, AgentResponse, WriterFeedback
from discord_bot.core.logging import get_logger

logger = get_logger(__name__)


class EditorAgent(BaseNewsletterAgent):
    """Agent responsible for editing and quality control."""
    
    def __init__(self, model=None):
        super().__init__(
            name="EditorAgent",
            role="Senior Editor",
            model=model,
            temperature=0.3,  # Low temperature for consistent editing
            max_tokens=3000
        )
    
    def _create_system_prompt(self) -> str:
        return """You are a senior editor for the Austin LangChain community newsletter.

Your responsibilities:
1. Review all content for clarity, accuracy, and tone
2. Ensure consistent style and formatting
3. Check for technical accuracy and appropriate language
4. Verify content is respectful and constructive
5. Optimize for readability and engagement

Editorial guidelines:
- Maintain professional yet approachable tone
- Ensure technical accuracy without being overly complex
- Keep content concise and valuable
- Remove any potentially offensive or overly critical content
- Preserve the collaborative spirit of the community

Quality criteria:
- Clear and concise writing
- Appropriate technical depth
- Engaging and informative content
- Proper grammar and structure
- Consistent formatting"""
    
    async def process(self, state: NewsletterState) -> AgentResponse:
        """Review and edit newsletter content."""
        draft_sections = state.get("draft_sections", [])
        technical_analysis = state.get("technical_analysis", {})
        
        if not draft_sections:
            return AgentResponse(
                agent_name=self.name,
                action="skip",
                output=None,
                reasoning="No draft sections to edit"
            )
        
        # Review each section
        edited_sections = []
        feedback_items = []
        
        for section in draft_sections:
            edited_section, feedback = await self._edit_section(section)
            edited_sections.append(edited_section)
            if feedback:
                feedback_items.append(feedback)
        
        # Perform quality checks
        quality_metrics = self._perform_quality_checks(edited_sections)
        
        # Generate editorial summary
        editorial_summary = await self._generate_editorial_summary(
            edited_sections,
            feedback_items,
            quality_metrics
        )
        
        return AgentResponse(
            agent_name=self.name,
            action="editing_complete",
            output={
                "edited_sections": edited_sections,
                "writer_feedback": [f.dict() for f in feedback_items],
                "quality_metrics": quality_metrics,
                "editorial_summary": editorial_summary
            },
            confidence=quality_metrics.get("overall_score", 0.8),
            reasoning=f"Edited {len(edited_sections)} sections with {len(feedback_items)} feedback items",
            next_steps=["final_formatting", "publication_prep"]
        )
    
    async def _edit_section(self, section: Dict) -> tuple[Dict, Optional[WriterFeedback]]:
        """Edit a single section."""
        original_content = section.get("content", "")
        
        if not self.model:
            # Basic editing without LLM
            edited_content = self._basic_edit(original_content)
        else:
            edited_content = await self._llm_edit(section)
        
        # Check if significant changes were made
        changes_made = self._calculate_edit_distance(original_content, edited_content)
        
        feedback = None
        if changes_made > 0.1:  # More than 10% change
            feedback = WriterFeedback(
                agent_name=self.name,
                section=section.get("title", "Unknown"),
                feedback="Significant edits made for clarity and tone",
                suggestions=[
                    "Consider more concise technical explanations",
                    "Maintain consistent voice throughout"
                ],
                quality_score=0.85
            )
        
        edited_section = section.copy()
        edited_section["content"] = edited_content
        edited_section["edited"] = True
        edited_section["word_count"] = len(edited_content.split())
        
        return edited_section, feedback
    
    def _basic_edit(self, content: str) -> str:
        """Perform basic editing without LLM."""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Fix common issues
        content = content.replace("  ", " ")
        content = re.sub(r'([.!?])\s*([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), content)
        
        # Ensure proper sentence endings
        if content and not content[-1] in '.!?':
            content += '.'
        
        return content
    
    async def _llm_edit(self, section: Dict) -> str:
        """Edit content using LLM."""
        prompt = f"""
        Edit this newsletter section for the Austin LangChain community:
        
        Section Type: {section.get('section_type', 'general')}
        Title: {section.get('title', 'Untitled')}
        
        Content:
        {section.get('content', '')}
        
        Edit for:
        1. Clarity and conciseness
        2. Technical accuracy
        3. Professional yet approachable tone
        4. Grammar and style
        5. Community-friendly language
        
        Preserve the core message and technical details.
        Keep the collaborative spirit of the community.
        """
        
        messages = self._create_messages(prompt)
        response = await self._call_llm(messages)
        
        return response.strip()
    
    def _calculate_edit_distance(self, original: str, edited: str) -> float:
        """Calculate the percentage of content changed."""
        if not original:
            return 1.0
        
        original_words = set(original.lower().split())
        edited_words = set(edited.lower().split())
        
        if not original_words:
            return 1.0
        
        common_words = original_words.intersection(edited_words)
        change_ratio = 1 - (len(common_words) / len(original_words))
        
        return change_ratio
    
    def _perform_quality_checks(self, sections: List[Dict]) -> Dict[str, Any]:
        """Perform quality checks on edited content."""
        metrics = {
            "total_word_count": 0,
            "average_section_length": 0,
            "readability_score": 0,
            "technical_terms_count": 0,
            "sections_edited": len(sections),
            "quality_issues": []
        }
        
        total_words = 0
        technical_terms = [
            "langchain", "langgraph", "agent", "llm", "rag", "vector",
            "embedding", "api", "python", "javascript", "ai", "ml"
        ]
        
        for section in sections:
            content = section.get("content", "")
            words = content.split()
            total_words += len(words)
            
            # Count technical terms
            content_lower = content.lower()
            for term in technical_terms:
                metrics["technical_terms_count"] += content_lower.count(term)
            
            # Check for quality issues
            if len(words) < 50:
                metrics["quality_issues"].append(f"Section '{section.get('title')}' is too short")
            elif len(words) > 500:
                metrics["quality_issues"].append(f"Section '{section.get('title')}' is too long")
            
            # Simple readability check (sentence length)
            sentences = re.split(r'[.!?]+', content)
            avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            if avg_sentence_length > 25:
                metrics["quality_issues"].append(f"Section '{section.get('title')}' has long sentences")
        
        metrics["total_word_count"] = total_words
        metrics["average_section_length"] = total_words / max(len(sections), 1)
        
        # Calculate overall readability score (simplified)
        if total_words > 0:
            metrics["readability_score"] = min(100, 100 - (metrics["technical_terms_count"] / total_words * 100))
        
        # Overall quality score
        quality_score = 1.0
        quality_score -= len(metrics["quality_issues"]) * 0.1
        quality_score = max(0.5, min(1.0, quality_score))
        metrics["overall_score"] = quality_score
        
        return metrics
    
    async def _generate_editorial_summary(
        self, 
        sections: List[Dict],
        feedback_items: List[WriterFeedback],
        quality_metrics: Dict
    ) -> Dict[str, Any]:
        """Generate an editorial summary."""
        summary = {
            "sections_reviewed": len(sections),
            "total_feedback_items": len(feedback_items),
            "overall_quality": quality_metrics.get("overall_score", 0),
            "word_count": quality_metrics.get("total_word_count", 0),
            "estimated_read_time": max(1, quality_metrics.get("total_word_count", 0) // 200),
            "key_improvements": [],
            "recommendations": []
        }
        
        # Summarize improvements
        if feedback_items:
            summary["key_improvements"] = [
                "Enhanced clarity and readability",
                "Improved technical accuracy",
                "Consistent tone and style"
            ]
        
        # Add recommendations based on metrics
        if quality_metrics.get("quality_issues"):
            summary["recommendations"].extend([
                "Address identified quality issues",
                "Review section lengths for optimal reading"
            ])
        
        if quality_metrics.get("readability_score", 100) < 70:
            summary["recommendations"].append(
                "Consider simplifying technical language for broader accessibility"
            )
        
        return summary