"""
generate_pdf.py — Compile REVIEW_DOCUMENT.md into a styled, self-contained HTML
with embedded figures, MathJax-rendered LaTeX, and Appendix A data tables.

Strategy:
  1. Read REVIEW_DOCUMENT.md as raw text
  2. Convert Markdown → HTML using a lightweight built-in parser
  3. Embed Fig1 and Fig2 as base64-encoded inline images
  4. Render LaTeX via MathJax CDN
  5. Dynamically load all 7 CSVs into formatted HTML tables for Appendix A
  6. Attempt PDF via weasyprint/pdfkit; fallback to .html
"""
import os
import re
import base64
import pandas as pd

# Ensure we're running from the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
MD_FILE = "REVIEW_DOCUMENT.md"
OUTPUT_HTML = "Version_2_Research_Report.html"
OUTPUT_PDF  = "Version_2_Research_Report.pdf"

FIGURE_DIR = "."  # figures are in Version_2/

CSV_FILES = [
    ("Euler (Pericenter) Summary",        "Euler_p/Data/euler_summary.csv"),
    ("Euler (Apocenter) Summary",         "Euler_Apo/Data/euler_apo_summary.csv"),
    ("RK4 (Pericenter) Summary",          "RK4_p/Data/rk4_summary.csv"),
    ("RK4 (Apocenter) Summary",           "RK4_Apo/Data/rk4_apo_summary.csv"),
    ("Verlet (Pericenter) Summary",       "Verlet/Data/verlet_summary.csv"),
    ("Verlet (Apocenter) Summary",        "Verlet_Apo/Data/verlet_apo_summary.csv"),
    ("Consolidated k-Values",             "k_values_summary.csv"),
]

# ─────────────────────────────────────────────
# HELPER: Encode image as base64 data URI
# ─────────────────────────────────────────────
def img_to_base64(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(path)[1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext.strip("."), "image/png")
    return f"data:{mime};base64,{data}"


# ─────────────────────────────────────────────
# HELPER: Lightweight Markdown → HTML converter
# ─────────────────────────────────────────────
def md_to_html(md_text):
    """Convert Markdown to HTML using regex-based transformation.
    Handles: headers, bold, italic, code blocks, tables, images,
    blockquotes, horizontal rules, lists, paragraphs."""

    html = md_text

    # Fenced code blocks (```...```)
    def code_block_repl(m):
        lang = m.group(1) or ""
        code = m.group(2).strip()
        code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<pre><code class="language-{lang}">{code}</code></pre>'

    html = re.sub(r'```(\w*)\n(.*?)```', code_block_repl, html, flags=re.DOTALL)

    # Display math ($$...$$)
    html = re.sub(r'\$\$(.*?)\$\$', r'<div class="math-display">\\[\1\\]</div>', html, flags=re.DOTALL)

    # Inline math ($...$) — careful not to match $$
    html = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', r'\\(\1\\)', html)

    # Images ![alt](src)
    def img_repl(m):
        alt = m.group(1)
        src = m.group(2)
        # Resolve local paths and embed as base64
        local_candidates = [
            src,
            os.path.join(FIGURE_DIR, os.path.basename(src)),
            os.path.basename(src),
        ]
        for path in local_candidates:
            if os.path.isfile(path):
                data_uri = img_to_base64(path)
                return f'<figure><img src="{data_uri}" alt="{alt}" style="max-width:100%;height:auto;"><figcaption>{alt}</figcaption></figure>'
        # If file not found, try the path with forward slashes
        clean = src.replace("\\", "/")
        if os.path.isfile(clean):
            data_uri = img_to_base64(clean)
            return f'<figure><img src="{data_uri}" alt="{alt}" style="max-width:100%;height:auto;"><figcaption>{alt}</figcaption></figure>'
        return f'<figure><img src="{src}" alt="{alt}" style="max-width:100%;height:auto;"><figcaption>{alt}</figcaption></figure>'

    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', img_repl, html)

    # Headers
    html = re.sub(r'^######\s+(.*?)$',  r'<h6>\1</h6>',  html, flags=re.MULTILINE)
    html = re.sub(r'^#####\s+(.*?)$',   r'<h5>\1</h5>',  html, flags=re.MULTILINE)
    html = re.sub(r'^####\s+(.*?)$',    r'<h4>\1</h4>',  html, flags=re.MULTILINE)
    html = re.sub(r'^###\s+(.*?)$',     r'<h3>\1</h3>',  html, flags=re.MULTILINE)
    html = re.sub(r'^##\s+(.*?)$',      r'<h2>\1</h2>',  html, flags=re.MULTILINE)
    html = re.sub(r'^#\s+(.*?)$',       r'<h1>\1</h1>',  html, flags=re.MULTILINE)

    # Horizontal rules
    html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*',     r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*',         r'<em>\1</em>', html)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Blockquotes (multi-line)
    def blockquote_repl(m):
        content = re.sub(r'^>\s?', '', m.group(0), flags=re.MULTILINE)
        return f'<blockquote>{content}</blockquote>'

    html = re.sub(r'(^>.*\n?)+', blockquote_repl, html, flags=re.MULTILINE)

    # Tables
    def table_repl(m):
        lines = m.group(0).strip().split('\n')
        if len(lines) < 2:
            return m.group(0)

        # Parse header
        headers = [c.strip() for c in lines[0].strip('|').split('|')]

        # Skip separator line (index 1)
        rows = []
        for line in lines[2:]:
            cells = [c.strip() for c in line.strip('|').split('|')]
            rows.append(cells)

        th = ''.join(f'<th>{h}</th>' for h in headers)
        tbody = ''
        for row in rows:
            td = ''.join(f'<td>{c}</td>' for c in row)
            tbody += f'<tr>{td}</tr>\n'

        return f'<table>\n<thead><tr>{th}</tr></thead>\n<tbody>\n{tbody}</tbody>\n</table>'

    html = re.sub(r'(\|.*\|.*\n\|[-:\s|]+\|\n(\|.*\|.*\n)*)', table_repl, html)

    # Unordered lists
    def ul_repl(m):
        items = re.findall(r'^[-*]\s+(.*?)$', m.group(0), re.MULTILINE)
        li = ''.join(f'<li>{item}</li>' for item in items)
        return f'<ul>{li}</ul>'

    html = re.sub(r'(^[-*]\s+.*\n?)+', ul_repl, html, flags=re.MULTILINE)

    # Ordered lists
    def ol_repl(m):
        items = re.findall(r'^\d+\.\s+(.*?)$', m.group(0), re.MULTILINE)
        li = ''.join(f'<li>{item}</li>' for item in items)
        return f'<ol>{li}</ol>'

    html = re.sub(r'(^\d+\.\s+.*\n?)+', ol_repl, html, flags=re.MULTILINE)

    # Paragraphs — wrap loose text blocks
    lines = html.split('\n')
    result = []
    in_para = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_para:
                result.append('</p>')
                in_para = False
            result.append('')
        elif stripped.startswith('<') and not stripped.startswith('<em') and not stripped.startswith('<strong') and not stripped.startswith('<code'):
            if in_para:
                result.append('</p>')
                in_para = False
            result.append(line)
        else:
            if not in_para:
                result.append('<p>')
                in_para = True
            result.append(line)
    if in_para:
        result.append('</p>')

    return '\n'.join(result)


# ─────────────────────────────────────────────
# HELPER: Build Appendix A HTML from CSVs
# ─────────────────────────────────────────────
def build_appendix():
    sections = ['<h2>7. Appendix A: Raw Numerical Summaries</h2>']

    for title, csv_path in CSV_FILES:
        if not os.path.isfile(csv_path):
            sections.append(f'<h3>{title}</h3><p><em>File not found: {csv_path}</em></p>')
            continue

        df = pd.read_csv(csv_path)
        df = df.round(10)  # Clean trailing noise

        sections.append(f'<h3>{title}</h3>')
        sections.append(f'<p class="csv-path"><code>{csv_path}</code></p>')
        sections.append(df.to_html(index=False, classes='data-table', border=0))

    return '\n'.join(sections)


# ─────────────────────────────────────────────
# CSS STYLES
# ─────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400&display=swap');

:root {
    --text: #1a1a2e;
    --bg: #ffffff;
    --accent: #16213e;
    --muted: #6c757d;
    --border: #dee2e6;
    --table-head: #16213e;
    --table-head-text: #ffffff;
    --table-stripe: #f8f9fa;
    --fig-bg: #fafafa;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Crimson Pro', 'Georgia', serif;
    font-size: 11.5pt;
    line-height: 1.72;
    color: var(--text);
    background: var(--bg);
    max-width: 820px;
    margin: 0 auto;
    padding: 48px 40px 80px;
}

h1 {
    font-size: 1.6em;
    font-weight: 700;
    color: var(--accent);
    text-align: center;
    margin: 0 0 8px;
    line-height: 1.35;
    letter-spacing: -0.3px;
}

h2 {
    font-size: 1.25em;
    font-weight: 700;
    color: var(--accent);
    border-bottom: 2px solid var(--accent);
    padding-bottom: 4px;
    margin: 36px 0 14px;
}

h3 {
    font-size: 1.08em;
    font-weight: 600;
    color: #2c3e50;
    margin: 24px 0 10px;
}

h4 { font-size: 1em; font-weight: 600; margin: 18px 0 8px; }

p { margin: 0 0 12px; text-align: justify; }

hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 28px 0;
}

strong { font-weight: 700; }
em { font-style: italic; }

code {
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 0.88em;
    background: #f0f0f5;
    padding: 1px 5px;
    border-radius: 3px;
}

pre {
    background: #1a1a2e;
    color: #e0e0e0;
    padding: 14px 18px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 12px 0 18px;
    font-size: 0.85em;
    line-height: 1.55;
}

pre code {
    background: none;
    padding: 0;
    color: inherit;
}

blockquote {
    border-left: 3px solid var(--accent);
    padding: 10px 18px;
    margin: 14px 0;
    background: #f5f6fa;
    color: #444;
    font-style: italic;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0 20px;
    font-size: 0.92em;
}

thead tr {
    background: var(--table-head);
    color: var(--table-head-text);
}

th {
    padding: 8px 12px;
    text-align: left;
    font-weight: 600;
    font-size: 0.9em;
    letter-spacing: 0.3px;
}

td {
    padding: 7px 12px;
    border-bottom: 1px solid var(--border);
}

tbody tr:nth-child(even) { background: var(--table-stripe); }
tbody tr:hover { background: #eef1f7; }

.data-table {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82em;
}

.data-table th {
    font-family: 'Crimson Pro', serif;
    text-transform: capitalize;
}

figure {
    margin: 24px 0;
    text-align: center;
    background: var(--fig-bg);
    padding: 16px;
    border-radius: 6px;
    border: 1px solid var(--border);
    page-break-inside: avoid;
}

figure img {
    max-width: 95%;
    height: auto;
    border-radius: 3px;
}

figcaption {
    margin-top: 10px;
    font-size: 0.88em;
    color: var(--muted);
    font-style: italic;
    line-height: 1.5;
    text-align: center;
}

.csv-path {
    font-size: 0.85em;
    color: var(--muted);
    margin-bottom: 6px;
}

ul, ol { margin: 8px 0 12px 28px; }
li { margin-bottom: 4px; }

.math-display {
    margin: 16px 0;
    text-align: center;
    font-size: 1.1em;
}

@media print {
    body { padding: 24px; max-width: none; font-size: 10.5pt; }
    h1 { font-size: 1.5em; }
    figure { page-break-inside: avoid; }
    h2 { page-break-after: avoid; }
    table { page-break-inside: avoid; }
    pre { background: #f0f0f0 !important; color: #333 !important; }
}
"""

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("Reading REVIEW_DOCUMENT.md...")
    with open(MD_FILE, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Remove the placeholder Appendix A (we'll generate it dynamically)
    # Find the section starting with "> **Note**:" or "## 7. Appendix"
    # and strip everything from there to the end of the document metadata
    appendix_marker = "## 7. Appendix A: Raw Numerical Summaries"
    idx = md_text.find(appendix_marker)
    if idx != -1:
        md_text = md_text[:idx].rstrip()

    # Also remove the trailing metadata line
    for marker in ["*Document compiled", "*Computational environment"]:
        end_idx = md_text.find(marker)
        if end_idx != -1:
            md_text = md_text[:end_idx].rstrip()

    print("Converting Markdown → HTML...")
    body_html = md_to_html(md_text)

    print("Building Appendix A from CSVs...")
    appendix_html = build_appendix()

    # Footer
    footer_html = """
    <hr>
    <p style="text-align:center; color:#888; font-size:0.85em; margin-top:30px;">
        <em>Document compiled from Version_2 data (64-bit, e ∈ [0.1, 0.7], Δt = 0.00625, N<sub>orb</sub> = 100).<br>
        Computational environment: Python 3 / NumPy (float64). Date: 2 March 2026.</em>
    </p>
    """

    # Assemble full HTML
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Empirical Analysis of Eccentricity-Driven Secular Energy Drift</title>
    <style>{CSS}</style>
    <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['\\\\(', '\\\\)']],
                displayMath: [['\\\\[', '\\\\]']],
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'code', 'pre']
            }}
        }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
</head>
<body>
{body_html}

{appendix_html}

{footer_html}
</body>
</html>"""

    # ── Try PDF first, fallback to HTML ──
    pdf_saved = False

    # Attempt 1: weasyprint
    try:
        from weasyprint import HTML as WHTML
        print("Generating PDF via weasyprint...")
        WHTML(string=full_html, base_url=".").write_pdf(OUTPUT_PDF)
        print(f"✓ PDF saved: {OUTPUT_PDF}")
        pdf_saved = True
    except Exception as e:
        print(f"  weasyprint unavailable: {e}")

    # Attempt 2: pdfkit
    if not pdf_saved:
        try:
            import pdfkit
            print("Generating PDF via pdfkit...")
            pdfkit.from_string(full_html, OUTPUT_PDF)
            print(f"✓ PDF saved: {OUTPUT_PDF}")
            pdf_saved = True
        except Exception as e:
            print(f"  pdfkit unavailable: {e}")

    # Fallback: save as HTML
    if not pdf_saved:
        print(f"PDF libraries not available. Saving self-contained HTML instead...")

    # Always save HTML (useful as standalone artifact)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"✓ HTML saved: {OUTPUT_HTML}")

    if not pdf_saved:
        print(f"\n→ Open {OUTPUT_HTML} in your browser and press Ctrl+P to print to PDF.")
    
    print("\nCompilation complete.")


if __name__ == "__main__":
    main()
