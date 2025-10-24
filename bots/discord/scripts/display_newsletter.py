#!/usr/bin/env python3
"""Display the generated newsletter in a readable format."""

# Sample data from the generated newsletter
title = "Austin LangChain Monthly - October 2025"
subtitle = "Top discussions and insights from the past month"

sections = [
    {
        "title": "Featured Discussions",
        "content": """This month's most engaging discussions highlight the diverse technical explorations within our community. From innovative AI implementations to practical development tips, these conversations exemplify the spirit of collaboration at Austin LangChain:

**LangGraph Development**: @.h0rizons shared exciting updates on generating LangGraph graphs with AI, pushing the boundaries of what's possible with self-modifying AI systems.

**The SALOON Stack**: @c0lli3r introduced a new tech stack concept (SQLite, Astro, Ollama/OpenAI, Nix/NixOS) that's gaining traction for local-first AI development.

**Self-Hosted Solutions**: @ibby.xd shared Aegra, a framework for self-hosting LangGraph agents, providing the community with practical tools for deployment.

**Community Growth**: The monthly showcase event was a huge success with @colinmcnamara sharing all talks and slides, and @ravichandu.ummadisetti joining our growing community of AI enthusiasts."""
    },
    {
        "title": "Technical Highlights",
        "content": """**Factory Recursion in LangGraph**
@rpirruccio led fascinating discussions about factory recursion and building self-improving AI systems. The community explored how LangGraph can handle dynamic graph generation and recursive patterns.

**Claude Code Plugins Now Official**
@facelessman shared exciting news about Claude Code plugins becoming official, opening new possibilities for AI-assisted development workflows.

**Graph Registry Concept**
Discussions emerged about creating a graph registry similar to Smithery for MCPs, but specifically for LangGraph components - potentially revolutionizing how we share and reuse AI agent architectures.

**Cloudflare AISearch Integration**
@c0lli3r highlighted opportunities for indexing aimug.org with Cloudflare's AISearch, improving discoverability of community resources."""
    },
    {
        "title": "Community Updates",
        "content": """**Upcoming Events**: Join us for our next community meetup where we'll dive deeper into advanced LangGraph patterns and share real-world implementations.

**New Members**: Welcome to all our new community members! We're excited to have you join our journey in exploring the frontiers of AI development.

**Social Boost**: @james.francis.coffey launched a community initiative to spread the word about AIMUG Episode 1 across social platforms.

**Off-Topic Fun**: @colinmcnamara shared news about a smoothie line launch under the Sprouts brand - showing that our community members are innovators in all areas!"""
    },
    {
        "title": "Learning Resources",
        "content": """**Development Tips**: @.h0rizons shared valuable Claude Code commands for better documentation-first development practices.

**MLOps Insights**: @rpirruccio provided notes from MLOps World, highlighting how rapidly AI technology is evolving.

**Tech Stack Discussions**: Active conversations around NixOS, Astro, and other modern development tools continue to shape our community's technology choices."""
    },
    {
        "title": "Monthly Trends & Insights",
        "content": """This month showcased several key trends in our community:

1. **Self-Hosted AI**: Growing interest in deploying and managing AI agents locally
2. **LangGraph Innovation**: Continuous exploration of advanced graph patterns and recursive architectures
3. **Tool Integration**: Focus on practical integrations with Claude Code, MCPs, and other developer tools
4. **Stack Modernization**: Community members experimenting with cutting-edge tech stacks
5. **Knowledge Sharing**: Strong emphasis on documentation and sharing learnings

The discussions reflect our community's commitment to pushing boundaries while maintaining practical, production-ready solutions."""
    }
]

# Generate markdown
markdown = f"""# {title}

*{subtitle}*

📖 **Reading time:** 5 minutes

---

"""

for section in sections:
    markdown += f"""
## {section['title']}

{section['content']}

---

"""

markdown += """

**Austin LangChain Community Newsletter**
Generated with ❤️ by our AI-powered newsletter system

---

## Get Involved

- **Join our Discord**: Connect with fellow AI developers and enthusiasts
- **Attend Meetups**: Monthly events featuring talks, demos, and networking
- **Contribute**: Share your projects, insights, and questions
- **Follow Us**: Stay updated on the latest AI/ML developments in Austin

*This newsletter was generated using OpenAI GPT-4o and traced with LangSmith for quality assurance.*

---

**Stats for this edition:**
- 📊 50 discussions analyzed from the past 30 days
- 🎯 20 top discussions featured
- ⭐ Engagement score threshold: 1.5+
- 💬 Topics covered: 13 channels
- Word count: ~600 words
"""

print(markdown)

# Also save to file
output_file = "newsletter_monthly_october_2025.md"
with open(output_file, 'w') as f:
    f.write(markdown)

print(f"\n\n✅ Newsletter saved to: {output_file}")
