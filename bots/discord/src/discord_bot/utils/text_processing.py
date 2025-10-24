"""Text processing utilities for newsletter generation."""

import re
import html
from typing import List, Dict, Optional
from datetime import datetime


class TextProcessor:
    """Utility class for text processing operations."""
    
    @staticmethod
    def clean_discord_content(content: str) -> str:
        """Clean Discord message content for newsletter use."""
        if not content:
            return ""
        
        # Remove Discord-specific formatting
        content = re.sub(r'<@!?(\d+)>', r'@user', content)  # Mentions
        content = re.sub(r'<#(\d+)>', r'#channel', content)  # Channel links
        content = re.sub(r'<:(\w+):(\d+)>', r':\1:', content)  # Custom emojis
        content = re.sub(r'<a?:(\w+):(\d+)>', r':\1:', content)  # Animated emojis
        
        # Clean up code blocks for readability
        content = re.sub(r'```(\w+)?\n(.*?)\n```', r'`\2`', content, flags=re.DOTALL)
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'  +', ' ', content)
        
        return content.strip()
    
    @staticmethod
    def extract_code_snippets(content: str) -> List[Dict[str, str]]:
        """Extract code snippets from Discord messages."""
        snippets = []
        
        # Multi-line code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        for lang, code in code_blocks:
            snippets.append({
                'type': 'block',
                'language': lang or 'text',
                'code': code.strip()
            })
        
        # Inline code
        inline_code = re.findall(r'`([^`]+)`', content)
        for code in inline_code:
            if len(code.strip()) > 0:
                snippets.append({
                    'type': 'inline',
                    'language': 'text',
                    'code': code.strip()
                })
        
        return snippets
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
        """Truncate text to a maximum length."""
        if len(text) <= max_length:
            return text
        
        # Try to truncate at word boundary
        truncated = text[:max_length - len(suffix)]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.7:  # Don't cut too much
            truncated = truncated[:last_space]
        
        return truncated + suffix
    
    @staticmethod
    def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
        """Calculate estimated reading time in minutes."""
        if not text:
            return 1
        
        word_count = len(text.split())
        reading_time = max(1, round(word_count / words_per_minute))
        
        return reading_time
    
    @staticmethod
    def format_for_html(text: str) -> str:
        """Format text for HTML display."""
        if not text:
            return ""
        
        # Escape HTML
        text = html.escape(text)
        
        # Convert line breaks to HTML
        text = text.replace('\n', '<br>')
        
        # Convert **bold** to <strong>
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Convert *italic* to <em>
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Convert `code` to <code>
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # Convert links
        text = re.sub(
            r'https?://[^\s]+',
            r'<a href="\g<0>" target="_blank">\g<0></a>',
            text
        )
        
        return text
    
    @staticmethod
    def format_for_markdown(text: str) -> str:
        """Format text for Markdown display."""
        if not text:
            return ""
        
        # Clean up existing markdown
        text = text.strip()
        
        # Ensure proper paragraph spacing
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'https?://[^\s<>"{}|^`[\]\\]+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def highlight_keywords(text: str, keywords: List[str]) -> str:
        """Highlight keywords in text for display."""
        if not keywords:
            return text
        
        highlighted = text
        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted = pattern.sub(f'**{keyword}**', highlighted)
        
        return highlighted
    
    @staticmethod
    def generate_summary(text: str, max_sentences: int = 2) -> str:
        """Generate a simple summary by taking first few sentences."""
        if not text:
            return ""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Take first few sentences
        summary_sentences = sentences[:max_sentences]
        summary = '. '.join(summary_sentences)
        
        if len(sentences) > max_sentences:
            summary += '.'
        
        return summary


class NewsletterFormatter:
    """Specialized formatter for newsletter content."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def format_discussion_summary(
        self, 
        content: str, 
        author: str, 
        engagement_score: float,
        max_length: int = 300
    ) -> Dict[str, str]:
        """Format a discussion summary for newsletter inclusion."""
        clean_content = self.text_processor.clean_discord_content(content)
        summary = self.text_processor.generate_summary(clean_content, max_sentences=2)
        
        if len(summary) > max_length:
            summary = self.text_processor.truncate_text(summary, max_length)
        
        return {
            'summary': summary,
            'author': author,
            'engagement_score': f"{engagement_score:.1f}",
            'formatted_for_html': self.text_processor.format_for_html(summary),
            'formatted_for_markdown': self.text_processor.format_for_markdown(summary)
        }
    
    def format_section_header(self, title: str, emoji: str = "📝") -> Dict[str, str]:
        """Format a section header for different output formats."""
        return {
            'html': f'<h2>{emoji} {title}</h2>',
            'markdown': f'## {emoji} {title}',
            'text': f'{emoji} {title.upper()}\n{"=" * len(title)}'
        }
    
    def format_newsletter_footer(self, stats: Dict[str, Any]) -> Dict[str, str]:
        """Format newsletter footer with stats."""
        word_count = stats.get('word_count', 0)
        discussion_count = stats.get('discussion_count', 0)
        read_time = stats.get('read_time', 1)
        
        footer_text = f"📊 {discussion_count} discussions • {word_count} words • {read_time} min read"
        
        return {
            'html': f'<div class="newsletter-footer">{footer_text}</div>',
            'markdown': f'*{footer_text}*',
            'text': footer_text
        }


# Global instances
text_processor = TextProcessor()
newsletter_formatter = NewsletterFormatter()