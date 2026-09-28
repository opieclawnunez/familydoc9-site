#!/usr/bin/env python3
"""Prepare three reviewable site files from final, reviewed article JSON. No git operations."""
import argparse
import datetime
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://docnunez.com/'
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
MARKER = '<div class="article-grid">'


def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be non-empty text')
    return value.strip()


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Input must be an object')
    for field in ('title', 'slug', 'summary', 'category', 'date'):
        text(data.get(field), field)
    slug = data['slug']
    if not SLUG.fullmatch(slug):
        raise ValueError('slug must be lowercase letters, numbers, and single hyphens')
    datetime.date.fromisoformat(data['date'])
    source = data.get('source_url')
    if source is not None and (not isinstance(source, str) or urlparse(source).scheme not in ('https', 'http') or not urlparse(source).netloc):
        raise ValueError('source_url must be an absolute http(s) URL')
    blocks = data.get('blocks')
    if not isinstance(blocks, list) or not blocks:
        raise ValueError('blocks must be a nonempty list')
    for block in blocks:
        if not isinstance(block, dict) or block.get('type') not in ('paragraph', 'heading', 'list'):
            raise ValueError('Each block needs type paragraph, heading, or list')
        if block['type'] == 'list':
            if not isinstance(block.get('items'), list) or not block['items']:
                raise ValueError('List blocks need nonempty items')
            for item in block['items']:
                text(item, 'list item')
        else:
            text(block.get('text'), 'block text')
    return data


def escape(value):
    return html.escape(value, quote=True)


def render_article(data):
    title, summary, category, slug = (escape(data[k]) for k in ('title', 'summary', 'category', 'slug'))
    url = BASE + slug + '.html'
    body = []
    for block in data['blocks']:
        kind = block['type']
        if kind == 'list':
            body.append('        <ul>\n' + '\n'.join(f'          <li>{escape(item)}</li>' for item in block['items']) + '\n        </ul>')
        else:
            tag = 'h2' if kind == 'heading' else 'p'
            body.append(f'        <{tag}>{escape(block["text"])}</{tag}>')
    source = f'        <p class="source-note">Source: <a href="{escape(data["source_url"])}">Original article</a></p>' if data.get('source_url') else ''
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} | The Family Doc Blog</title>
  <link rel="canonical" href="{url}" />
  <meta name="description" content="{summary}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{summary}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:type" content="article" />
  <meta name="color-scheme" content="light dark" />
  <link rel="icon" href="assets/logo.svg" type="image/svg+xml" />
  <link rel="stylesheet" href="assets/styles.css" />
</head>
<body>
  <a class="skip-link" href="#content">Skip to content</a>
  <header class="site-header"><div class="header-inner"><a class="brand" href="index.html"><span class="brand-mark">FD</span><span class="brand-text"><span class="brand-name">The Family Doc Blog</span><span class="brand-tag">Health tips and insights from a family physician.</span></span></a><div class="nav-wrap"><button class="icon-button menu-button" data-menu-button aria-expanded="false" aria-controls="primary-nav">Menu</button><nav id="primary-nav" class="primary-nav"><a href="index.html">Home</a><a href="site-purpose.html">Purpose</a><a href="about.html">About</a><a href="articles.html" aria-current="page">Articles</a><a href="resources.html">Resources</a><a href="newsletter.html">Newsletter</a><a href="disclaimer.html">Disclaimer</a></nav><button class="icon-button" data-theme-button type="button" aria-label="Toggle color theme">Dark mode</button></div></div></header>
  <main id="content" class="site-shell">
    <section class="article-hero"><div class="article"><span class="eyebrow">{category}</span><h1 class="page-title tight">{title}</h1><p class="page-intro">{summary}</p><div class="kicker-row"><span class="meta-chip">{escape(data['date'])}</span></div></div></section>
    <section class="article-layout"><article class="article article-body">
{chr(10).join(body)}
{source}
        <aside class="callout" aria-label="Follow-up and appointments">
          <h3>Questions about your result?</h3>
          <p>Make an appointment with your primary care provider. If you'd like to see Dr. M. Nunez at Prosano Health, call <a href="tel:+18557767266">(855) 776-7266</a> or visit <a href="https://www.prosanohealth.com/">Prosano Health</a> to ask about eligibility and availability.</p>
        </aside>
        <p class="source-note">This is a general discussion, not medical advice for your particular situation. Your own care needs an assessment with your clinician in person.</p>
    </article></section>
  </main>
  <footer class="footer"><div class="site-shell footer-inner"><small><strong>The Family Doc Blog</strong> &mdash; educational information only. Not a substitute for individualized medical advice.</small></div></footer>
  <script src="assets/site.js" defer></script>
</body>
</html>
'''


def prepare(data, root, dry_run=False):
    validate(data)
    slug = data['slug']
    article = root / (slug + '.html')
    if article.exists():
        raise ValueError(f'duplicate slug: {slug}.html already exists')
    listing = root / 'articles.html'
    sitemap = root / 'sitemap.xml'
    listing_text = listing.read_text(encoding='utf-8')
    sitemap_text = sitemap.read_text(encoding='utf-8')
    url = BASE + slug + '.html'
    if listing_text.count(MARKER) != 1 or f'href="{slug}.html"' in listing_text:
        raise ValueError('article listing marker missing/ambiguous or slug already listed')
    if url in sitemap_text:
        raise ValueError('slug already present in sitemap')
    ET.fromstring(sitemap_text)
    card = f'''\n        <article class="media-card">
          <div class="media-copy">
            <div class="meta"><span class="category-chip">{escape(data['category'])}</span> · {escape(data['date'])}</div>
            <h3><a href="{escape(slug)}.html">{escape(data['title'])}</a></h3>
            <p>{escape(data['summary'])}</p>
          </div>
        </article>'''
    revised_listing = listing_text.replace(MARKER, MARKER + card, 1)
    new_url = f'  <url><loc>{escape(url)}</loc></url>\n'
    revised_sitemap = sitemap_text.replace('</urlset>', new_url + '</urlset>', 1)
    ET.fromstring(revised_sitemap)
    changes = {article: render_article(data), listing: revised_listing, sitemap: revised_sitemap}
    if not dry_run:
        for path, content in changes.items():
            path.write_text(content, encoding='utf-8')
    return list(changes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='reviewed JSON file')
    parser.add_argument('--dry-run', action='store_true', help='validate and preview paths; write nothing')
    args = parser.parse_args()
    try:
        paths = prepare(json.loads(args.input.read_text(encoding='utf-8')), ROOT, args.dry_run)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        parser.exit(1, f'Preparation refused: {error}\n')
    print(('Would prepare: ' if args.dry_run else 'Prepared: ') + ', '.join(str(path) for path in paths))
    print('No commit, push, deploy, or cross-post was performed.')
