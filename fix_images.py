#!/usr/bin/env python3
"""Replace SVG and missing hero images with real stock photos across all docnunez.com articles."""
import re, os

REPO = "/opt/fleet/workspace/repos/familydoc9-site"

# Map: article_filename -> (new_image_filename, alt_text)
# For articles that currently have NO hero image, we need to add the full <figure> block
# For articles that have an SVG, we just swap the src and alt

replacements = {
    # Articles with SVG hero images - just swap
    "achieving-healthy-appetite-suppression-like-glp1.html": (
        "hero-healthy-eating-2.jpg",
        "A healthy low-carb meal with zucchini noodles, eggs, avocado, and greens — the kind of nutrition that supports appetite control"
    ),
    "summer-heat-safety-west-valley-families.html": (
        "hero-summer-heat.jpg",
        "A person outdoors in hot desert conditions, illustrating the importance of heat safety and hydration"
    ),
    # Articles with NO hero image - need to add <figure> block after <p class="lede">
    "mental-health-policy-overhaul-2024.html": (
        "hero-mental-health-2.jpg",
        "Two hands reaching toward each other — a visual metaphor for mental health support and connection"
    ),
    "future-of-telehealth-post-pandemic.html": (
        "hero-telehealth.jpg",
        "A doctor in a white coat holding a smartphone, representing modern telehealth and virtual care"
    ),
    "mental-health-policy-overhaul-bridging-gaps-in-care-and-what-it-means-for-you.html": (
        "hero-mental-health.jpg",
        "A warm, approachable healthcare professional — representing the human side of mental health care"
    ),
    "mental-health.html": (
        "hero-mental-health-2.jpg",
        "Two hands reaching toward each other — a visual metaphor for mental health support and connection"
    ),
    "hypertension-101-how-to-keep-your-blood-pressure-in-check.html": (
        "hero-blood-pressure.jpg",
        "A medical model of the brain and nervous system — the command center that regulates blood pressure and heart health"
    ),
    "the-future-of-telehealth-post-pandemic-a-professional-perspective.html": (
        "hero-telehealth.jpg",
        "A doctor in a white coat holding a smartphone, representing modern telehealth and virtual care"
    ),
    "family-support-guide.html": (
        "hero-family-support.jpg",
        "A multi-generational family holding hands on a beach at sunset — representing family support and togetherness"
    ),
    "family-support.html": (
        "hero-family-support.jpg",
        "A multi-generational family holding hands on a beach at sunset — representing family support and togetherness"
    ),
    "healthy-aging-guide.html": (
        "hero-healthy-aging.jpg",
        "Medical professionals in an operating room — representing the advanced care available for healthy aging"
    ),
    "healthy-aging.html": (
        "hero-healthy-aging.jpg",
        "Medical professionals in an operating room — representing the advanced care available for healthy aging"
    ),
    "prevention-screening.html": (
        "hero-prevention.jpg",
        "A stethoscope on a desk next to a laptop — representing the behind-the-scenes work of preventive care"
    ),
}

# Articles that already have JPG heroes but are missing og:image meta tag
missing_og = {
    "blood-pressure.html": "hero-home-4.jpg",
    "childhood-immunizations.html": "hero-home-1.jpg",
    "delaying-healthcare.html": "hero-home-5.jpg",
    "global-health-evaluation.html": "hero-home-2.jpg",
    "self-care.html": "hero-home-6.jpg",
    "telehealth-after-pandemic.html": "hero-home-3.jpg",
    "turmeric.html": "hero-design.jpg",
}

def swap_svg_in_article(filepath, new_img, new_alt):
    """Swap SVG img src with new JPG in an article's <figure> block."""
    with open(filepath, "r") as f:
        content = f.read()
    
    # Replace the <img> tag inside the <figure> in the article body
    # Pattern: <img src="assets/media/..." alt="..." />
    old_pattern = r'(<img\s+src="assets/media/)[^"]*("[^>]*alt=")[^"]*("[^>]*/>)'
    new_replacement = rf'\1{new_img}\2{new_alt}\3'
    
    new_content = re.sub(old_pattern, new_replacement, content, count=1)
    
    if new_content == content:
        print(f"  WARNING: No <img> tag found in {filepath}")
        return False
    
    with open(filepath, "w") as f:
        f.write(new_content)
    print(f"  Updated img in {filepath}")
    return True

def add_figure_to_article(filepath, new_img, new_alt):
    """Add a <figure> block after the <p class="lede"> tag."""
    with open(filepath, "r") as f:
        content = f.read()
    
    figure_block = f'''
        <figure>
          <img src="assets/media/{new_img}" alt="{new_alt}" />
          <figcaption class="figure-caption">Figure: {new_alt}.</figcaption>
        </figure>'''
    
    # Insert after <p class="lede">...</p>
    # Find the closing </p> of the lede paragraph
    lede_pattern = r'(<p class="lede">.*?</p>)'
    match = re.search(lede_pattern, content, re.DOTALL)
    
    if not match:
        print(f"  WARNING: No <p class='lede'> found in {filepath}")
        return False
    
    insert_pos = match.end()
    new_content = content[:insert_pos] + figure_block + content[insert_pos:]
    
    with open(filepath, "w") as f:
        f.write(new_content)
    print(f"  Added figure to {filepath}")
    return True

def add_og_image(filepath, img_filename):
    """Add og:image meta tag after og:type."""
    with open(filepath, "r") as f:
        content = f.read()
    
    og_url = f"https://docnunez.com/assets/media/{img_filename}"
    og_tag = f'  <meta property="og:image" content="{og_url}" />'
    
    # Insert after og:type line
    pattern = r'(<meta property="og:type" content="article" />)'
    replacement = rf'\1\n{og_tag}'
    
    new_content = re.sub(pattern, replacement, content, count=1)
    
    if new_content == content:
        print(f"  WARNING: No og:type found in {filepath}")
        return False
    
    with open(filepath, "w") as f:
        f.write(new_content)
    print(f"  Added og:image to {filepath}")
    return True

# Process articles with SVG swaps
print("=== Replacing SVG images ===")
for filename, (new_img, new_alt) in replacements.items():
    filepath = os.path.join(REPO, filename)
    if not os.path.exists(filepath):
        print(f"  SKIP: {filename} not found")
        continue
    
    has_svg = False
    with open(filepath) as f:
        if ".svg" in f.read():
            has_svg = True
    
    if has_svg:
        swap_svg_in_article(filepath, new_img, new_alt)
    else:
        add_figure_to_article(filepath, new_img, new_alt)
    
    # Also update og:image
    add_og_image(filepath, new_img)

# Process articles missing og:image
print("\n=== Adding missing og:image tags ===")
for filename, img_filename in missing_og.items():
    filepath = os.path.join(REPO, filename)
    if not os.path.exists(filepath):
        print(f"  SKIP: {filename} not found")
        continue
    add_og_image(filepath, img_filename)

print("\n=== Done ===")
