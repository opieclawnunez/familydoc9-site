#!/usr/bin/env python3
"""Analyze the bulk-exported WordPress articles for repurposing priority."""
import json, sys
from pathlib import Path

# Ensure content-pipeline/scripts is on the path so pipeline module is importable
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'content-pipeline' / 'scripts'))

from pipeline import score_post, clean

RAW = REPO / 'content-pipeline/data/raw/wp-posts.json'
posts = json.loads(RAW.read_text())

print(f'Total articles: {len(posts)}')
print()

local_rel, recent, thin = 0, 0, 0
scores = []
for p in posts:
    s, _, _ = score_post(p)
    scores.append(s)
    low = (clean(p.get('title',{}).get('rendered','')) + ' ' + clean(p.get('content',{}).get('rendered',''))).lower()
    if any(x in low for x in ['west valley', 'phoenix', 'arizona', 'heat', 'air quality']):
        local_rel += 1
    date = p.get('date','')[:10]
    try:
        if int(date[:4]) >= 2025:
            recent += 1
    except: pass
    if len(clean(p.get('content',{}).get('rendered','')).split()) < 500:
        thin += 1

print(f'Local relevance (West Valley/Phoenix/AZ/heat/air quality): {local_rel}')
print(f'Recent (2025+): {recent}')
print(f'Thin (<500 words): {thin}')
print(f'Score range: {min(scores)} to {max(scores)}, mean: {sum(scores)/len(scores):.1f}')
print()

rows = []
for p in posts:
    s, _, words = score_post(p)
    rows.append((s, p.get('date','')[:10], p.get('slug',''), clean(p.get('title',{}).get('rendered',''))[:90]))
rows.sort(key=lambda r: r[0], reverse=True)

print('=== TOP 20 BY SCORE (repurposing priority) ===')
for s, date, slug, title in rows[:20]:
    print(f'  {s:>4} | {date} | {slug:<50} | {title}')

print()
print('=== BOTTOM 10 BY SCORE (likely skip) ===')
for s, date, slug, title in rows[-10:]:
    print(f'  {s:>4} | {date} | {slug:<50} | {title}')

# Categories present
cats = {}
for p in posts:
    for c in p.get('categories', []):
        if isinstance(c, dict) and c.get('name'):
            name = c['name']
            cats[name] = cats.get(name, 0) + 1
print()
print('=== CATEGORY DISTRIBUTION ===')
for name, count in sorted(cats.items(), key=lambda x: -x[1]):
    print(f'  {count:>4}  {name}')
