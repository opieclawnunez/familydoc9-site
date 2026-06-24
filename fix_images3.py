#!/usr/bin/env python3
"""Add og:image meta tags to articles that have no OG tags at all."""
import os, re

REPO = "/opt/fleet/workspace/repos/familydoc9-site"

articles = {
    "blood-pressure.html": "hero-home-4.jpg",
    "childhood-immunizations.html": "hero-home-1.jpg",
    "delaying-healthcare.html": "hero-home-5.jpg",
    "global-health-evaluation.html": "hero-home-2.jpg",
    "self-care.html": "hero-home-6.jpg",
    "turmeric.html": "hero-design.jpg",
}

for filename, img in articles.items():
    filepath = os.path.join(REPO, filename)
    with open(filepath) as f:
        content = f.read()
    
    og_url = f"https://docnunez.com/assets/media/{img}"
    og_block = f'  <meta property="og:image" content="{og_url}" />'
    
    # Add after the description meta tag
    pattern = r'(<meta name="description"[^>]*>)'
    replacement = rf'\1\n{og_block}'
    new_content = re.sub(pattern, replacement, content, count=1)
    
    if new_content != content:
        with open(filepath, "w") as f:
            f.write(new_content)
        print(f"OK: {filename}")
    else:
        print(f"FAIL: {filename}")
