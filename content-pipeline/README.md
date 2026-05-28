# docnunez.com Content Modernization Pipeline

This pipeline turns legacy WordPress content from `familydoc9.wordpress.com` into review-ready, SEO-aware article drafts for `docnunez.com`, then generates social/newsletter promotion packages for each publication.

## Commands

```bash
cd /opt/fleet/workspace/repos/familydoc9-site
python3 content-pipeline/scripts/pipeline.py inventory
python3 content-pipeline/scripts/pipeline.py candidates --limit 25
python3 content-pipeline/scripts/pipeline.py modernize --slug <wordpress-slug>
python3 content-pipeline/scripts/pipeline.py seo
python3 content-pipeline/scripts/pipeline.py sitemap
```

## Operating model

1. Ingest WordPress posts from the public API and keep raw snapshots.
2. Score candidates by evergreen value, local relevance, SEO potential, and medical-review risk.
3. Modernize one article at a time into a static HTML draft with canonical URL, meta description, H1/H2 structure, disclaimer, internal links, and review checklist.
4. Generate a promotion package with UTM URLs, newsletter copy, X/Twitter batch copy, Facebook/Threads/LinkedIn copy, and manual checklist.
5. Audit SEO before publication.
6. Publish only after human/physician review when medical content has changed materially.

## Current constraints

- GitHub push/auth is not available on this VPS yet, so generated changes are local until a GitHub token or SSH deploy key is installed.
- X/Twitter free API is read-only; the pipeline generates weekly/manual copy instead of auto-posting.
- Meta/Instagram/Threads can be automated later once credentials are supplied.
