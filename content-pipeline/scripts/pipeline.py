#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, html, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / 'content-pipeline/config.json').read_text())
API = CONFIG['wordpress_api'].rstrip('/')
RAW = ROOT / CONFIG['raw_dir'] / 'wp-posts.json'
REPORTS = ROOT / 'content-pipeline/reports'
DRAFTS = ROOT / CONFIG['draft_dir']
PROMOS = ROOT / CONFIG['promotion_dir']
TAG_RE = re.compile(r'<[^>]+>')


def clean(s: str) -> str:
    return re.sub(r'\s+', ' ', html.unescape(TAG_RE.sub(' ', s or ''))).strip()


def slugify(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:80] or 'article'


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={'User-Agent': 'docnunez-content-pipeline/1.0'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode()), r.headers


def inventory(args):
    RAW.parent.mkdir(parents=True, exist_ok=True)
    posts = []
    for page in range(1, args.max_pages + 1):
        qs = urllib.parse.urlencode({
            'per_page': args.per_page,
            'page': page,
            '_fields': 'id,date,modified,slug,link,title,excerpt,content,categories,tags'
        })
        try:
            batch, headers = fetch_json(f'{API}/posts?{qs}')
        except urllib.error.HTTPError as e:
            if e.code == 400 and page > 1:
                break
            raise
        posts.extend(batch)
        print(f'fetched page={page} count={len(batch)} total={len(posts)}')
        if page >= int(headers.get('X-WP-TotalPages') or page):
            break
        time.sleep(0.15)
    RAW.write_text(json.dumps(posts, indent=2, ensure_ascii=False))
    print(f'saved {len(posts)} posts to {RAW}')


def score_post(p):
    title = clean(p.get('title', {}).get('rendered', ''))
    body = clean(p.get('content', {}).get('rendered', ''))
    low = (title + ' ' + body).lower()
    words = len(body.split())
    score, reasons = 0, []
    if 700 <= words <= 2200:
        score += 15; reasons.append('good length')
    elif words < 500:
        score -= 10; reasons.append('thin')
    else:
        score += 5; reasons.append('long/rework')
    for kw in CONFIG['topic_priority_keywords']:
        if kw in low:
            score += 6; reasons.append('priority:' + kw)
    for kw in CONFIG['medical_review_keywords']:
        if kw.lower() in low:
            score -= 2; reasons.append('review:' + kw)
    date = p.get('date', '')[:10]
    try:
        year = int(date[:4])
        if year >= 2025:
            score += 8; reasons.append('recent')
        elif year <= 2023:
            score -= 4; reasons.append('needs freshness update')
    except Exception:
        pass
    if any(x in low for x in ['west valley', 'phoenix', 'arizona', 'heat', 'air quality']):
        score += 20; reasons.append('local relevance')
    return score, reasons, words


def candidates(args):
    if not RAW.exists():
        inventory(argparse.Namespace(per_page=100, max_pages=20))
    posts = json.loads(RAW.read_text())
    rows = []
    for p in posts:
        score, reasons, words = score_post(p)
        rows.append({'score': score, 'date': p.get('date', '')[:10], 'slug': p.get('slug'), 'title': clean(p.get('title', {}).get('rendered', '')), 'words': words, 'link': p.get('link'), 'reasons': '; '.join(reasons[:10])})
    rows.sort(key=lambda r: r['score'], reverse=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / 'modernization-candidates.csv'
    with out.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f'saved {out}')
    for r in rows[:args.limit]:
        print(f"{r['score']:>4} {r['date']} {r['slug']} - {r['title'][:90]} [{r['reasons']}]")


def meta(text: str) -> str:
    text = clean(text)
    return text if len(text) <= 155 else text[:155].rsplit(' ', 1)[0] + '...'


def pillar(title: str, body: str) -> str:
    low = (title + ' ' + body).lower()
    rules = [
        ('Heart & Circulatory', ['blood pressure', 'hypertension', 'heart', 'stroke', 'cholesterol']),
        ('Respiratory & Lung', ['cough', 'asthma', 'lung', 'respiratory', 'air quality']),
        ('Mental & Emotional Health', ['stress', 'anxiety', 'mental', 'emotional', 'burnout']),
        ("Women's & Family Health", ['mom', 'mother', 'family', 'caregiver', 'children', 'pregnancy']),
        ('Public Health & Policy', ['vaccine', 'immunization', 'public health', 'policy', 'community']),
        ('Healthcare Innovation', ['technology', 'ai', 'innovation', 'study', 'research', 'global health']),
    ]
    for name, kws in rules:
        if any(k in low for k in kws):
            return name
    return 'Preventive Health & Wellness'


def modernize(args):
    if not RAW.exists():
        inventory(argparse.Namespace(per_page=100, max_pages=20))
    posts = json.loads(RAW.read_text())
    p = next((x for x in posts if x.get('slug') == args.slug), None)
    if not p:
        raise SystemExit(f'slug not found: {args.slug}')
    title = clean(p.get('title', {}).get('rendered', ''))
    body = clean(p.get('content', {}).get('rendered', ''))
    new_slug = slugify(title)
    desc = meta(p.get('excerpt', {}).get('rendered') or body)
    pil = pillar(title, body)
    flags = [kw for kw in CONFIG['medical_review_keywords'] if kw.lower() in body.lower()]
    paras = [x.strip() for x in re.split(r'(?<=[.!?])\s+(?=[A-Z])', body) if len(x.strip()) > 80][:14]
    article_url = f"{CONFIG['site_url']}/{new_slug}.html"
    DRAFTS.mkdir(parents=True, exist_ok=True); PROMOS.mkdir(parents=True, exist_ok=True)
    html_body = '\n'.join(f'      <p>{html.escape(x)}</p>' for x in paras)
    review_items = '\n'.join(f'        <li>{html.escape(x)}</li>' for x in flags) or '        <li>No high-risk medical terms detected automatically.</li>'
    article = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} | The Family Doc Blog</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="{article_url}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{article_url}">
  <meta property="og:type" content="article">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <header class="site-header"><a class="brand" href="index.html">FD <span>The Family Doc Blog</span></a><nav><a href="articles.html">Articles</a><a href="newsletter.html">Newsletter</a><a href="disclaimer.html">Disclaimer</a></nav></header>
  <main id="content" class="article-page">
    <article class="article">
      <p class="eyebrow">{html.escape(pil)}</p>
      <h1>{html.escape(title)}</h1>
      <p class="lede">{html.escape(desc)}</p>
{html_body}
      <section class="callout"><h2>What to do next</h2><p>Use this as general education, then bring specific questions to your own clinician, especially if symptoms are severe, changing, or persistent.</p></section>
      <section class="editor-note"><h2>Editorial review notes</h2><p>Legacy source: <a href="{html.escape(p.get('link',''))}">WordPress original</a>. Physician review required before publication if clinical recommendations changed.</p><ul>
{review_items}
      </ul></section>
    </article>
  </main>
  <footer class="site-footer"><p>Educational information only; not medical advice.</p></footer>
</body>
</html>
'''
    (DRAFTS / f'{new_slug}.html').write_text(article)
    def utm(source, content):
        return article_url + '?' + urllib.parse.urlencode({'utm_source': source, 'utm_medium': 'email' if source == 'newsletter' else 'social', 'utm_campaign': new_slug, 'utm_content': content})
    promo = f'''# Promotion Package: {title}

Canonical: {article_url}

## Tracking URLs
- Newsletter: {utm('newsletter','main_cta')}
- Facebook: {utm('facebook','hook_1')}
- Threads: {utm('threads','hook_1')}
- X/Twitter: {utm('x','weekly_batch_1')}
- LinkedIn: {utm('linkedin','expert_commentary')}

## Newsletter draft
Subject options:
1. {title}
2. A practical guide: {title}
3. What your family doctor wants you to know

Preview text: {desc}

Body intro: {desc}

CTA: Read the full article

## Social copy
Facebook/Threads: New article from The Family Doc Blog: {title}\n\n{desc}\n\n{utm('facebook','hook_1')}

X/Twitter batch 1: {title}\n\n{utm('x','title_link')}

LinkedIn: New from The Family Doc Blog: {title}\n\n{desc}\n\n{utm('linkedin','expert_commentary')}

## Manual checklist
- [ ] Physician/editorial review complete
- [ ] SEO audit passes
- [ ] Publish article
- [ ] Create/review MailerLite campaign draft
- [ ] Post/schedule X batch manually
- [ ] Post LinkedIn manually
- [ ] Share Facebook/Threads manually or via Meta automation
- [ ] Check UTM performance after 48 hours
'''
    (PROMOS / f'{new_slug}.md').write_text(promo)
    print(f"draft: {DRAFTS / (new_slug + '.html')}")
    print(f"promo: {PROMOS / (new_slug + '.md')}")
    print(f"pillar: {pil}; review flags: {', '.join(flags) if flags else 'none'}")


def seo(args):
    title_re = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)
    desc_re = re.compile(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', re.I | re.S)
    canon_re = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']', re.I | re.S)
    total = 0
    for p in sorted(ROOT.glob('*.html')):
        s = p.read_text(errors='ignore')
        issues = []
        if not title_re.search(s): issues.append('missing title')
        if not desc_re.search(s): issues.append('missing meta description')
        if not canon_re.search(s): issues.append('missing canonical')
        h1 = len(re.findall(r'<h1\b', s, re.I))
        if h1 != 1: issues.append(f'h1 count {h1}')
        if issues:
            total += len(issues); print(f'{p.name}: ' + '; '.join(issues))
    print(f'SEO audit complete: {total} issues')
    raise SystemExit(1 if total else 0)


def sitemap(args):
    base = CONFIG['site_url'].rstrip('/')
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in sorted(ROOT.glob('*.html')):
        loc = base + ('/' if p.name == 'index.html' else '/' + p.name)
        lines.append(f'  <url><loc>{html.escape(loc)}</loc></url>')
    lines.append('</urlset>')
    (ROOT / 'sitemap.xml').write_text('\n'.join(lines) + '\n')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n')
    print('wrote sitemap.xml and robots.txt')


def publish(args):
    """Copy draft HTML files to repo root, commit, and push to main."""
    import shutil
    draft_dir = ROOT / CONFIG["draft_dir"]
    if not draft_dir.exists():
        print("No drafts to publish")
        return
    html_files = list(draft_dir.glob("*.html"))
    if not html_files:
        print("No draft HTML files found")
        return
    for src in html_files:
        dst = ROOT / src.name
        shutil.copy2(src, dst)
        print(f"published {src.name} -> {dst}")
    # Commit and push
    import subprocess
    try:
        subprocess.run(["git", "add", "."], cwd=ROOT, check=True)
        # Check if there's anything staged to commit
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
        if diff.returncode == 0:
            print("No new changes to publish (already up to date)")
        else:
            subprocess.run(["git", "commit", "-m", f"Auto-publish: {len(html_files)} article(s)"], cwd=ROOT, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)
            print("pushed to main - GitHub Pages will deploy automatically")
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}")
        raise SystemExit(1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    inv = sub.add_parser('inventory'); inv.add_argument('--per-page', type=int, default=100); inv.add_argument('--max-pages', type=int, default=20); inv.set_defaults(func=inventory)
    cand = sub.add_parser('candidates'); cand.add_argument('--limit', type=int, default=25); cand.set_defaults(func=candidates)
    mod = sub.add_parser('modernize'); mod.add_argument('--slug', required=True); mod.set_defaults(func=modernize)
    sub.add_parser('seo').set_defaults(func=seo)
    sub.add_parser('sitemap').set_defaults(func=sitemap)
    pub = sub.add_parser('publish'); pub.set_defaults(func=publish)
    args = ap.parse_args(); args.func(args)

if __name__ == '__main__':
    main()
