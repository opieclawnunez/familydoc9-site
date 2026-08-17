#!/usr/bin/env python3
"""Convert article-draft.md to blog HTML using stdlib only — no external deps."""
import pathlib
import html

repo = pathlib.Path("/opt/fleet/workspace/repos/familydoc9-site")
slug = "summer-heat-safety-west-valley-families"
draft_dir = repo / "content-pipeline/output/drafts"
draft_dir.mkdir(parents=True, exist_ok=True)

md_path = repo / "content-pipeline/output/2026-W34/article-draft.md"
html_path = draft_dir / f"{slug}.html"

md_text = md_path.read_text()

def md_to_html(text):
    """Minimal markdown to HTML: headings, paragraphs, lists, bold, italic."""
    lines = text.split('\n')
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith('## '):
            out.append('<h2>' + html.escape(stripped[3:]) + '</h2>')
        elif stripped.startswith('### '):
            out.append('<h3>' + html.escape(stripped[4:]) + '</h3>')
        elif stripped.startswith('***') and stripped.endswith('***'):
            content = stripped[3:-3].strip()
            out.append('<p><em><strong>' + html.escape(content) + '</strong></em></p>')
        elif stripped.startswith('*') and stripped.endswith('*') and len(stripped) > 2:
            content = stripped[1:-1].strip()
            out.append('<p><em>' + html.escape(content) + '</em></p>')
        elif stripped.startswith('- ') or stripped.startswith('* '):
            items = []
            while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                item = lines[i].strip()[2:]
                items.append('<li>' + html.escape(item) + '</li>')
                i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')
            continue
        elif not stripped:
            if out and out[-1] != '</p>':
                out.append('<p></p>')
        i += 1

    # Join consecutive non-structural lines into paragraphs
    paragraphs = []
    current = []
    for line in out:
        if line == '<p></p>' or line.startswith('<h') or line.startswith('<ul'):
            if current:
                paragraphs.append('<p>' + ''.join(current) + '</p>')
                current = []
            paragraphs.append(line)
        else:
            current.append(line)
    if current:
        paragraphs.append('<p>' + ''.join(current) + '</p>')

    # Join consecutive <p> tags that have no blank between them
    result = '\n'.join(paragraphs)
    # Merge adjacent <p> blocks
    result = re.sub(r'(</p>)\n(<p>)', r'\1\n\2', result)
    return result


import re
html_body = md_to_html(md_text)

slug_title = slug.replace('-', ' ').title()
canonical = 'https://docnunez.com/' + slug + '/'
og_url = canonical

parts = [
    '<!doctype html>',
    '<html lang="en">',
    '<head>',
    '  <meta charset="utf-8">',
    '  <meta name="viewport" content="width=device-width, initial-scale=1">',
    '  <title>' + slug_title + ' | The Family Doc Blog</title>',
    '  <meta name="description" content="Summer heat safety for West Valley families and outdoor workers - practical guidance from Dr. Nunez.">',
    '  <link rel="canonical" href="' + canonical + '">',
    '  <meta property="og:title" content="Summer Heat Safety: What It Means for You and Your Family in the West Valley">',
    '  <meta property="og:description" content="Practical heat-safety habits for West Valley families, outdoor workers, and anyone facing another August in the Arizona sun.">',
    '  <meta property="og:url" content="' + og_url + '">',
    '  <meta property="og:type" content="article">',
    '  <link rel="stylesheet" href="assets/style.css">',
    '</head>',
    '<body>',
    '  <header class="site-header"><a class="brand" href="index.html">FD <span>The Family Doc Blog</span></a><nav><a href="articles.html">Articles</a><a href="newsletter.html">Newsletter</a><a href="disclaimer.html">Disclaimer</a></nav></header>',
    '  <main id="content" class="article-page">',
    '    <article class="article">',
    '      <p class="eyebrow">Preventive Health &amp; Wellness - Peoria, AZ</p>',
    '      <h1>Summer Heat Safety: What It Means for You and Your Family in the West Valley</h1>',
    '      <p class="lede">Practical heat-safety habits for West Valley families, outdoor workers, and anyone facing another August in the Arizona sun.</p>',
    html_body,
    '    </article>',
    '  </main>',
    '  <footer class="site-footer"><p>Schedule your next appointment with Dr. Nunez and the Prosano Health Team - prosanohealth.com</p></footer>',
    '</body>',
    '</html>',
]
html_page = '\n'.join(parts) + '\n'

html_path.write_text(html_page)
print('Wrote ' + str(html_path) + ' (' + str(len(html_page)) + ' bytes)')
