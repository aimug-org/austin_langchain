"""Formatter agent for creating the final newsletter format."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import random

from discord_bot.agents.base_agent import BaseNewsletterAgent
from discord_bot.agents.state import NewsletterState, AgentResponse, NewsletterDraft, NewsletterSection
from discord_bot.core.logging import get_logger

logger = get_logger(__name__)

# AIMUG branding constants
AIMUG_LOGO_URL = "https://aimug.org/img/alc-docs-social-card.jpg"
AIMUG_PRIMARY_COLOR = "#2C5F9E"  # Blue from AIMUG branding
AIMUG_SECONDARY_COLOR = "#1B3A5C"  # Darker blue
AIMUG_ACCENT_COLOR = "#4A90E2"  # Light blue for accents

# Community links
COMMUNITY_LINKS = {
    "website": "https://aimug.org",
    "discord": "https://discord.gg/JzWgadPFQd",
    "twitter": "https://twitter.com/AustinLangChain",
    "youtube": "https://www.youtube.com/@austinlangchain",
    "meetup": "https://www.meetup.com/austin-langchain-ai-group/",
    "subscribe": "https://buttondown.com/aimug"
}

# Motivational quotes pool
MOTIVATIONAL_QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
    ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("Artificial intelligence is the new electricity.", "Andrew Ng"),
    ("Technology is best when it brings people together.", "Matt Mullenweg"),
    ("The science of today is the technology of tomorrow.", "Edward Teller"),
    ("Learning never exhausts the mind.", "Leonardo da Vinci"),
    ("Stay curious, stay humble, stay hungry for knowledge.", "Anonymous"),
    ("The only impossible journey is the one you never begin.", "Tony Robbins"),
    ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("The advance of technology is based on making it fit in so that you don't really even notice it.", "Bill Gates"),
    ("AI is the new UI.", "Mustafa Suleyman")
]


class FormatterAgent(BaseNewsletterAgent):
    """Agent responsible for final newsletter formatting and layout."""
    
    def __init__(self, model=None):
        super().__init__(
            name="FormatterAgent",
            role="Newsletter Formatter",
            model=model,
            temperature=0.1,  # Very low temperature for consistent formatting
            max_tokens=4000
        )
    
    def _create_system_prompt(self) -> str:
        return """You are a newsletter formatter for the Austin LangChain community newsletter.

Your role is to:
1. Create the final newsletter layout and structure
2. Format content for multiple output formats (HTML, Markdown, Text)
3. Ensure consistent styling and branding
4. Add proper headers, footers, and navigation
5. Optimize for email delivery and web viewing

Formatting guidelines:
- Clean, professional layout
- Consistent typography and spacing
- Proper use of headers (H1, H2, H3)
- Readable font sizes and line spacing
- Mobile-friendly design
- Clear section divisions
- Call-to-action elements"""
    
    async def process(self, state: NewsletterState) -> AgentResponse:
        """Format the final newsletter."""
        # Try edited_sections first (from EditorAgent), fall back to draft_sections (from DiscussionWriter)
        sections_to_format = state.get("edited_sections") or state.get("draft_sections", [])
        quality_metrics = state.get("quality_metrics", {})
        newsletter_type = state.get("newsletter_type", "daily")
        target_date = state.get("target_date", datetime.now().strftime("%Y-%m-%d"))

        if not sections_to_format:
            return AgentResponse(
                agent_name=self.name,
                action="skip",
                output=None,
                reasoning="No sections to format"
            )

        edited_sections = sections_to_format
        
        # Create newsletter sections
        newsletter_sections = []
        for section in edited_sections:
            ns = NewsletterSection(
                section_type=section.get("section_type", "general"),
                title=section.get("title", "Untitled"),
                content=section.get("content", ""),
                discussions=section.get("discussion_ids", []),
                word_count=section.get("word_count", 0)
            )
            newsletter_sections.append(ns)
        
        # Generate title and subtitle
        title, subtitle = self._generate_title_and_subtitle(newsletter_type, target_date)
        
        # Create newsletter draft
        newsletter_draft = NewsletterDraft(
            title=title,
            subtitle=subtitle,
            sections=newsletter_sections,
            total_word_count=sum(s.word_count for s in newsletter_sections),
            estimated_read_time=quality_metrics.get("estimated_read_time", 3),
            featured_discussions=[
                msg_id for section in newsletter_sections 
                for msg_id in section.discussions
            ],
            generation_metadata={
                "formatted_at": datetime.now().isoformat(),
                "formatter_version": "1.0",
                "section_count": len(newsletter_sections)
            }
        )
        
        # Generate different formats
        html_content = self._format_as_html(newsletter_draft)
        markdown_content = self._format_as_markdown(newsletter_draft)
        text_content = self._format_as_text(newsletter_draft)
        
        return AgentResponse(
            agent_name=self.name,
            action="formatting_complete",
            output={
                "newsletter_draft": newsletter_draft.dict(),
                "html_content": html_content,
                "markdown_content": markdown_content,
                "text_content": text_content,
                "formats_generated": ["html", "markdown", "text"]
            },
            confidence=0.95,
            reasoning=f"Formatted newsletter with {len(newsletter_sections)} sections in 3 formats",
            next_steps=["quality_review", "publication"]
        )
    
    def _generate_title_and_subtitle(self, newsletter_type: str, target_date: str) -> tuple[str, str]:
        """Generate title and subtitle for the newsletter."""
        date_obj = datetime.fromisoformat(target_date)
        
        if newsletter_type == "daily":
            title = f"Austin LangChain Daily - {date_obj.strftime('%B %d, %Y')}"
            subtitle = "Today's highlights from the Austin LangChain community"
        elif newsletter_type == "weekly":
            title = f"Austin LangChain Weekly - Week of {date_obj.strftime('%B %d, %Y')}"
            subtitle = "This week's top discussions and insights from the Austin tech community"
        else:
            title = f"Austin LangChain Newsletter - {date_obj.strftime('%B %d, %Y')}"
            subtitle = "Community highlights and technical insights"
        
        return title, subtitle
    
    def _format_as_html(self, draft: NewsletterDraft) -> str:
        """Format newsletter as HTML with AIMUG branding."""
        # Get random motivational quote
        quote, author = random.choice(MOTIVATIONAL_QUOTES)

        html_sections = []

        for section in draft.sections:
            # Convert content to HTML paragraphs
            paragraphs = section.content.split('\n\n')
            content_html = '\n'.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())

            section_html = f"""
            <section class="newsletter-section">
                <h2>{section.title}</h2>
                {content_html}
            </section>
            """
            html_sections.append(section_html)

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{draft.title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .logo {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid {AIMUG_PRIMARY_COLOR};
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: {AIMUG_PRIMARY_COLOR};
            margin-bottom: 10px;
            font-size: 2em;
        }}
        .subtitle {{
            color: #666;
            font-style: italic;
            font-size: 1.1em;
        }}
        .community-links {{
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
        }}
        .community-links a {{
            display: inline-block;
            margin: 5px 10px;
            padding: 8px 16px;
            background-color: {AIMUG_PRIMARY_COLOR};
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
            transition: background-color 0.3s;
        }}
        .community-links a:hover {{
            background-color: {AIMUG_SECONDARY_COLOR};
        }}
        .subscribe-btn {{
            background-color: {AIMUG_ACCENT_COLOR} !important;
            font-weight: bold;
        }}
        .newsletter-section {{
            margin-bottom: 30px;
            padding: 20px;
            border-left: 4px solid {AIMUG_PRIMARY_COLOR};
            background-color: #f9f9f9;
            border-radius: 4px;
        }}
        .newsletter-section h2 {{
            color: {AIMUG_PRIMARY_COLOR};
            margin-top: 0;
        }}
        .quote-section {{
            margin: 40px 0;
            padding: 25px;
            background: linear-gradient(135deg, {AIMUG_PRIMARY_COLOR}15, {AIMUG_ACCENT_COLOR}15);
            border-left: 4px solid {AIMUG_PRIMARY_COLOR};
            border-radius: 6px;
            font-style: italic;
            text-align: center;
        }}
        .quote-text {{
            font-size: 1.2em;
            color: {AIMUG_SECONDARY_COLOR};
            margin-bottom: 10px;
        }}
        .quote-author {{
            font-size: 0.9em;
            color: #666;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid {AIMUG_PRIMARY_COLOR};
            font-size: 0.9em;
            color: #666;
        }}
        .footer-logo {{
            color: {AIMUG_PRIMARY_COLOR};
            font-weight: bold;
            font-size: 1.1em;
        }}
        .read-time {{
            text-align: center;
            color: #888;
            font-size: 0.9em;
            margin-bottom: 30px;
        }}
        p {{
            margin-bottom: 15px;
        }}
        a {{
            color: {AIMUG_PRIMARY_COLOR};
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="{AIMUG_LOGO_URL}" alt="Austin LangChain User Group">
        </div>

        <div class="header">
            <h1>{draft.title}</h1>
            <p class="subtitle">{draft.subtitle}</p>
        </div>

        <div class="community-links">
            <a href="{COMMUNITY_LINKS['subscribe']}" class="subscribe-btn">📧 Subscribe</a>
            <a href="{COMMUNITY_LINKS['discord']}">💬 Discord</a>
            <a href="{COMMUNITY_LINKS['meetup']}">📅 Meetup</a>
            <a href="{COMMUNITY_LINKS['twitter']}">🐦 Twitter</a>
            <a href="{COMMUNITY_LINKS['youtube']}">▶️ YouTube</a>
            <a href="{COMMUNITY_LINKS['website']}">🌐 Website</a>
        </div>

        <div class="read-time">
            📖 Estimated reading time: {draft.estimated_read_time} minute{'s' if draft.estimated_read_time != 1 else ''}
        </div>

        {''.join(html_sections)}

        <div class="quote-section">
            <div class="quote-text">"{quote}"</div>
            <div class="quote-author">— {author}</div>
        </div>

        <div class="footer">
            <p class="footer-logo">🤖 Austin LangChain User Group (AIMUG)</p>
            <p>Generated with ❤️ by our AI-powered newsletter system</p>
            <p><small>Word count: {draft.total_word_count} | Sections: {len(draft.sections)}</small></p>
            <p><small><a href="{COMMUNITY_LINKS['website']}">Visit AIMUG.org</a></small></p>
        </div>
    </div>
</body>
</html>
        """.strip()

        return html_content
    
    def _format_as_markdown(self, draft: NewsletterDraft) -> str:
        """Format newsletter as Markdown with AIMUG branding."""
        # Get random motivational quote
        quote, author = random.choice(MOTIVATIONAL_QUOTES)

        markdown_sections = []

        for section in draft.sections:
            section_md = f"""
## {section.title}

{section.content}

---
            """.strip()
            markdown_sections.append(section_md)

        markdown_content = f"""
# {draft.title}

*{draft.subtitle}*

📖 **Reading time:** {draft.estimated_read_time} minute{'s' if draft.estimated_read_time != 1 else ''}

---

## 🔗 Connect with AIMUG

**[📧 Subscribe to Newsletter]({COMMUNITY_LINKS['subscribe']})** | **[💬 Join Discord]({COMMUNITY_LINKS['discord']})** | **[📅 Meetup]({COMMUNITY_LINKS['meetup']})** | **[🐦 Twitter]({COMMUNITY_LINKS['twitter']})** | **[▶️ YouTube]({COMMUNITY_LINKS['youtube']})** | **[🌐 Website]({COMMUNITY_LINKS['website']})**

---

{chr(10).join(markdown_sections)}

---

## 💭 Thought of the Day

> *"{quote}"*
> — {author}

---

**🤖 Austin LangChain User Group (AIMUG)**
Generated with ❤️ by our AI-powered newsletter system

*Word count: {draft.total_word_count} | Sections: {len(draft.sections)}*

[Visit AIMUG.org]({COMMUNITY_LINKS['website']})
        """.strip()

        return markdown_content
    
    def _format_as_text(self, draft: NewsletterDraft) -> str:
        """Format newsletter as plain text."""
        text_sections = []
        
        for section in draft.sections:
            section_text = f"""
{section.title.upper()}
{'=' * len(section.title)}

{section.content}

{'-' * 50}
            """.strip()
            text_sections.append(section_text)
        
        text_content = f"""
{draft.title.upper()}
{'=' * len(draft.title)}

{draft.subtitle}

Reading time: {draft.estimated_read_time} minute{'s' if draft.estimated_read_time != 1 else ''}

{'=' * 60}

{chr(10).join(text_sections)}

{'=' * 60}

AUSTIN LANGCHAIN COMMUNITY NEWSLETTER
Generated with love by our AI-powered newsletter system

Word count: {draft.total_word_count} | Sections: {len(draft.sections)}
        """.strip()
        
        return text_content