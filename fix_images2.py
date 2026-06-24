#!/usr/bin/env python3
"""Fix remaining image issues across all docnunez.com articles."""
import re, os

REPO = "/opt/fleet/workspace/repos/familydoc9-site"

def read_file(path):
    with open(path) as f:
        return f.read()

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)

# 1. Articles that got figure added but need og:image (og:type exists but pattern didn't match)
# These have: <meta property="og:type" content="article">
# Need to add: <meta property="og:image" content="..."> after it
articles_needing_og = {
    "mental-health-policy-overhaul-2024.html": "hero-mental-health-2.jpg",
    "future-of-telehealth-post-pandemic.html": "hero-telehealth.jpg",
    "mental-health-policy-overhaul-bridging-gaps-in-care-and-what-it-means-for-you.html": "hero-mental-health.jpg",
    "hypertension-101-how-to-keep-your-blood-pressure-in-check.html": "hero-blood-pressure.jpg",
    "the-future-of-telehealth-post-pandemic-a-professional-perspective.html": "hero-telehealth.jpg",
}

print("=== Adding og:image to articles that got figures ===")
for filename, img in articles_needing_og.items():
    filepath = os.path.join(REPO, filename)
    content = read_file(filepath)
    og_url = f"https://docnunez.com/assets/media/{img}"
    og_tag = f'  <meta property="og:image" content="{og_url}" />'
    
    # Match both "article"> and "article" />
    pattern = r'(<meta property="og:type" content="article")([\s]*>)'
    replacement = rf'\1\n{og_tag}\2'
    new_content = re.sub(pattern, replacement, content, count=1)
    
    if new_content != content:
        write_file(filepath, new_content)
        print(f"  OK: {filename}")
    else:
        print(f"  FAIL: {filename}")

# 2. Articles with NO hero image at all - need to add figure block
# These have <p class="lede"> but no <img> anywhere
articles_no_hero = {
    "mental-health.html": ("hero-mental-health-2.jpg", "Two hands reaching toward each other — a visual metaphor for mental health support and connection"),
    "family-support-guide.html": ("hero-family-support.jpg", "A multi-generational family holding hands on a beach at sunset — representing family support and togetherness"),
    "family-support.html": ("hero-family-support.jpg", "A multi-generational family holding hands on a beach at sunset — representing family support and togetherness"),
    "healthy-aging-guide.html": ("hero-healthy-aging.jpg", "Medical professionals in an operating room — representing the advanced care available for healthy aging"),
    "healthy-aging.html": ("hero-healthy-aging.jpg", "Medical professionals in an operating room — representing the advanced care available for healthy aging"),
    "prevention-screening.html": ("hero-prevention.jpg", "A stethoscope on a desk next to a laptop — representing the behind-the-scenes work of preventive care"),
}

print("\n=== Adding hero figures to articles with no image ===")
for filename, (img, alt) in articles_no_hero.items():
    filepath = os.path.join(REPO, filename)
    content = read_file(filepath)
    
    figure_block = f'''\n        <figure>\n          <img src="assets/media/{img}" alt="{alt}" />\n          <figcaption class="figure-caption">{alt}.</figcaption>\n        </figure>'''
    
    # Find the lede paragraph and add figure after its closing </p>
    lede_pattern = r'(<p class="lede">.*?</p>)'
    match = re.search(lede_pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.end()
        new_content = content[:insert_pos] + figure_block + content[insert_pos:]
        
        # Also add og:image
        og_url = f"https://docnunez.com/assets/media/{img}"
        og_tag = f'  <meta property="og:image" content="{og_url}" />'
        og_pattern = r'(<meta property="og:type" content="article")([\s]*>)'
        new_content = re.sub(og_pattern, rf'\1\n{og_tag}\2', new_content, count=1)
        
        write_file(filepath, new_content)
        print(f"  OK: {filename}")
    else:
        print(f"  FAIL: {filename} - no lede found")

# 3. Articles with JPG heroes but missing og:image (older articles with different og:type format)
articles_missing_og_jpg = {
    "blood-pressure.html": "hero-home-4.jpg",
    "childhood-immunizations.html": "hero-home-1.jpg",
    "delaying-healthcare.html": "hero-home-5.jpg",
    "global-health-evaluation.html": "hero-home-2.jpg",
    "self-care.html": "hero-home-6.jpg",
    "turmeric.html": "hero-design.html",
}

print("\n=== Adding og:image to older articles ===")
for filename, img in articles_missing_og_jpg.items():
    filepath = os.path.join(REPO, filename)
    content = read_file(filepath)
    
    # Check if og:image already exists
    if 'og:image' in content:
        print(f"  SKIP: {filename} (already has og:image)")
        continue
    
    og_url = f"https://docnunez.com/assets/media/{img}"
    og_tag = f'  <meta property="og:image" content="{og_url}" />'
    
    # Try to add after og:type
    og_pattern = r'(<meta property="og:type" content="article")([\s]*>)'
    new_content = re.sub(og_pattern, rf'\1\n{og_tag}\2', content, count=1)
    
    if new_content != content:
        write_file(filepath, new_content)
        print(f"  OK: {filename}")
    else:
        # No og:type - add after og:url
        url_pattern = r'(<meta property="og:url"[^>]*>)'
        new_content = re.sub(url_pattern, rf'\1\n{og_tag}', content, count=1)
        if new_content != content:
            write_file(filepath, new_content)
            print(f"  OK (after og:url): {filename}")
        else:
            print(f"  FAIL: {filename}")

print("\n=== Done ===")
