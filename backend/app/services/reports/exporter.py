"""
Report Exporter Service.
Generates styled standalone HTML and Markdown downloadable files.
"""

import html
import re


class ReportExporter:
    @staticmethod
    def to_markdown(title: str, markdown_content: str, version_number: int) -> str:
        header = f"<!-- DeepResearch Report: {title} (v{version_number}) -->\n\n"
        return header + markdown_content

    @staticmethod
    def to_html(title: str, markdown_content: str, version_number: int) -> str:
        # Basic markdown-to-HTML conversion with clean styling
        escaped = html.escape(markdown_content)

        # Convert simple markdown headers
        html_body = re.sub(r"^### (.*)$", r"<h3>\1</h3>", escaped, flags=re.MULTILINE)
        html_body = re.sub(r"^## (.*)$", r"<h2>\1</h2>", html_body, flags=re.MULTILINE)
        html_body = re.sub(r"^# (.*)$", r"<h1>\1</h1>", html_body, flags=re.MULTILINE)
        html_body = re.sub(r"^- (.*)$", r"<li>\1</li>", html_body, flags=re.MULTILINE)
        html_body = re.sub(
            r"\[(\d+)\]",
            r'<span class="citation">[\1]</span>',
            html_body,
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{html.escape(title)} - v{version_number}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            max-width: 850px;
            margin: 40px auto;
            padding: 0 20px;
        }}
        h1 {{ font-size: 2.2rem; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
        h2 {{
            font-size: 1.5rem;
            margin-top: 2rem;
            color: #1e3a8a;
            border-bottom: 1px solid #e5e7eb;
        }}

        h3 {{ font-size: 1.2rem; margin-top: 1.5rem; }}
        .citation {{
            font-size: 0.85em;
            color: #2563eb;
            font-weight: 600;
            cursor: pointer;
        }}
        .meta {{
            color: #6b7280;
            font-size: 0.9rem;
            margin-bottom: 2rem;
        }}
        li {{ margin-bottom: 0.4rem; }}
    </style>
</head>
<body>
    <div class="meta">DeepResearch Synthesis • Version {version_number}</div>
    {html_body}
</body>
</html>"""
