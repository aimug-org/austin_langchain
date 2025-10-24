"""Test script to validate new newsletter branding and formatting."""

from discord_bot.agents.formatter_agent import FormatterAgent
from discord_bot.agents.state import NewsletterDraft, NewsletterSection

def test_formatting():
    """Test the new formatting with branding."""
    # Create sample newsletter data
    sections = [
        NewsletterSection(
            section_type="featured",
            title="🔥 Top Discussions This Week",
            content="""### 1. Featured Discussion

**LangGraph Project Update and Insights**
@h0rizons provided an update on their project focused on generating LangGraph graphs with an agentic flow. The project has pivoted to writing complete LangGraph code for success.

*Channel: #🧠〡langgraph | [View Discussion](https://discord.com/channels/123/456/789) | 💬 5 replies | 👍 12 reactions*

### 2. Featured Discussion

**Building the SALOON Stack for AI Knowledge Management**
@c0lli3r proposed creating the SALOON stack (SQLite, fastAPI, LangGraph, Ollama, Obsidian, NextJS) for a self-hostable AI knowledge management system.

*Channel: #💡〡ai-development-general | [View Discussion](https://discord.com/channels/123/456/790) | 💬 8 replies | 👍 15 reactions*

### 3. Featured Discussion

**Excitement for Collaborative Learning in AI/ML**
@ravichandu.ummadisetti expressed enthusiasm for learning from the AIMUG community, showcasing commitment to knowledge sharing.

*Channel: #💭〡general | [View Discussion](https://discord.com/channels/123/456/791) | 💬 3 replies | 👍 10 reactions*""",
            discussions=["789", "790", "791"],
            word_count=150
        ),
        NewsletterSection(
            section_type="category",
            title="💻 Development & Tools",
            content="""**Discord Bot Development Update**
@that1guy15 shared progress on a Discord bot that analyzes conversations to identify popular posts, summarizing them into weekly blog posts.

*Channel: #cloudflare | [View Discussion](https://discord.com/channels/123/456/792) | 💬 4 replies | 👍 6 reactions*

**Dynamic Graph Generation in AI Systems**
@rpirruccio highlighted innovative use of self-modifying graph generation inspired by Toyota's MLOps practices using Kaizen principles.

*Channel: #🧑‍💻〡aimug-org | [View Discussion](https://discord.com/channels/123/456/793) | 💬 2 replies | 👍 8 reactions*""",
            discussions=["792", "793"],
            word_count=75
        )
    ]

    draft = NewsletterDraft(
        title="Austin LangChain Weekly - Week of October 12, 2025",
        subtitle="This week's top discussions and insights from the Austin AI/ML community",
        sections=sections,
        total_word_count=225,
        estimated_read_time=2,
        featured_discussions=["789", "790", "791"],
        generation_metadata={"test": True}
    )

    formatter = FormatterAgent()

    # Generate both formats
    markdown_content = formatter._format_as_markdown(draft)
    html_content = formatter._format_as_html(draft)

    # Save outputs
    with open('test_newsletter_branded.md', 'w') as f:
        f.write(markdown_content)

    with open('test_newsletter_branded.html', 'w') as f:
        f.write(html_content)

    print("✅ Test newsletter generated successfully!")
    print("Files created:")
    print("  - test_newsletter_branded.md")
    print("  - test_newsletter_branded.html")
    print(f"\nFeatures included:")
    print("  ✓ AIMUG logo and branding colors")
    print("  ✓ Community links (Discord, Twitter, YouTube, etc.)")
    print("  ✓ Subscribe button")
    print("  ✓ Top 3 featured discussions")
    print("  ✓ Categorized remaining discussions")
    print("  ✓ Random motivational quote")
    print("  ✓ Responsive design")

if __name__ == "__main__":
    test_formatting()
