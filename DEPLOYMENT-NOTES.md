# FamilyDoc9 deployment notes

Live preview:
- https://vowful-oasis-rjzq.here.now/

Why here.now for the first pass:
- fastest way to get a real public preview
- works well for a static HTML/CSS/JS site
- no app framework or CMS migration needed right now

Why not WordPress for this build:
- the site was rebuilt as a clean static surface
- WordPress would reintroduce CMS overhead before the design is settled
- the goal right now is a tangible launchable shell, not a full content workflow migration

Why Vercel is the best next permanent host:
- excellent fit for static multi-page sites
- easy Git-based deploys and preview URLs
- easy to move this exact folder into a repo later

What is already deployment-ready:
- homepage
- cornerstone pages
- topic hubs
- article pages
- responsive layout
- dark/light toggle
- newsletter form stub

Next deployment step if you want permanence:
1. put this folder in git
2. push to GitHub
3. import the repo into Vercel
4. point the domain later if needed
