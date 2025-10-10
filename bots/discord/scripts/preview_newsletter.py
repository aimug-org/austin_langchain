#!/usr/bin/env python3
"""Preview newsletter in browser with HTML rendering.

Usage:
    python scripts/preview_newsletter.py [newsletter_file.md]

If no file specified, opens the most recent newsletter.
"""

import sys
import argparse
from pathlib import Path
import webbrowser
import tempfile
import markdown
from datetime import datetime


def markdown_to_html(markdown_content: str, title: str = "AIMUG Newsletter") -> str:
    """Convert markdown to styled HTML."""
    # Convert markdown to HTML
    html_body = markdown.markdown(
        markdown_content,
        extensions=['extra', 'codehilite', 'toc']
    )

    # Create full HTML with styling
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #555;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin-left: 0;
            padding-left: 20px;
            color: #666;
            font-style: italic;
        }}
        hr {{
            border: none;
            border-top: 2px solid #eee;
            margin: 30px 0;
        }}
        ul, ol {{
            padding-left: 30px;
        }}
        li {{
            margin: 8px 0;
        }}
        .metadata {{
            color: #777;
            font-size: 0.9em;
            font-style: italic;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            text-align: center;
            color: #999;
            font-size: 0.9em;
        }}
        strong {{
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def find_latest_newsletter(output_dir: Path) -> Path:
    """Find the most recent newsletter file."""
    newsletters = list(output_dir.glob("newsletter_*.md"))
    if not newsletters:
        raise FileNotFoundError(f"No newsletters found in {output_dir}")

    # Sort by modification time, most recent first
    newsletters.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return newsletters[0]


def preview_newsletter(newsletter_path: Path):
    """Convert newsletter to HTML and open in browser."""
    if not newsletter_path.exists():
        raise FileNotFoundError(f"Newsletter not found: {newsletter_path}")

    print(f"📰 Opening newsletter: {newsletter_path.name}")

    # Read markdown content
    markdown_content = newsletter_path.read_text()

    # Extract title from first line if it's a heading
    title = "AIMUG Newsletter"
    if markdown_content.startswith("# "):
        title = markdown_content.split("\n")[0].replace("# ", "")

    # Convert to HTML
    html_content = markdown_to_html(markdown_content, title)

    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_html = f.name

    # Open in browser
    print(f"🌐 Opening in browser: {temp_html}")
    webbrowser.open(f"file://{temp_html}")

    print(f"✅ Newsletter preview opened successfully")
    print(f"📄 Source: {newsletter_path}")
    print(f"💾 HTML preview: {temp_html}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Preview AIMUG newsletter in browser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                          # Preview latest newsletter
  %(prog)s output/newsletter_monthly_202509.md     # Preview specific newsletter
        """
    )

    parser.add_argument(
        "newsletter",
        nargs="?",
        help="Path to newsletter markdown file (default: latest)"
    )

    args = parser.parse_args()

    # Determine newsletter path
    if args.newsletter:
        newsletter_path = Path(args.newsletter)
    else:
        # Find latest newsletter
        output_dir = Path(__file__).parent.parent / "output"
        try:
            newsletter_path = find_latest_newsletter(output_dir)
            print(f"📋 Using latest newsletter: {newsletter_path.name}")
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    # Preview the newsletter
    try:
        preview_newsletter(newsletter_path)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to preview newsletter: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
