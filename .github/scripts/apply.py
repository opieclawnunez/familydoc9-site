import re, glob, html, sys
GC = '  <script data-goatcounter="https://docnunez.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>\n'
ML = """  <script>
    (function(w,d,e,u,f,l,n){w[f]=w[f]||function(){(w[f].q=w[f].q||[]).push(arguments);},l=d.createElement(e),l.async=1,l.src=u,n=d.getElementsByTagName(e)[0],n.parentNode.insertBefore(l,n);})
    (window,document,'script','https://assets.mailerlite.com/js/universal.js','ml');
    ml('account','2375228');
  </script>
"""
BOX = """    <section class="article subscribe-box"><div class="info-box"><h3>Want the next one in your inbox?</h3><p>A short note when a new article goes up, a couple of times a month at most. Unsubscribe any time.</p><div class="ml-embedded" data-form="X08N3j"></div><p class="small-meta">Run by MailerLite. Please don&#x27;t put personal health details in the form.</p></div></section>
"""
SUF = ' | Dr. Nunez, Family Doctor'
T = {
 'index.html': ('Dr. Nunez, Family Doctor | Plain-English Health Guidance, Phoenix West Valley', 'Straight answers from a family doctor in the Phoenix West Valley: blood pressure, prediabetes, cough, aging and prevention, explained the way I would in the exam room.'),
 'chronic-cough-when-to-call.html': ('Chronic Cough: When to Call Your Doctor'+SUF, 'A cough that lingers after a cold deserves a plan. What a chronic cough can mean, what to track, red flags, and what to bring to the visit.'),
 'prediabetes-without-panic.html': ('Prediabetes: What Your A1c Result Means'+SUF, 'An unexpected A1c is a reason to make a plan, not to panic. What prediabetes means, what helps, and when to follow up with your doctor.'),
 'blood-pressure.html': ('Home Blood Pressure Monitoring: How to Do It Right'+SUF, 'How to measure blood pressure at home, understand the numbers, and know when high readings need follow-up with your doctor.'),
 'hypertension-101-how-to-keep-your-blood-pressure-in-check.html': ('Hypertension 101: Keeping Blood Pressure in Check'+SUF, 'High blood pressure basics from a family doctor: risk factors, everyday habits that help, and when medication comes into the picture.'),
 'delaying-healthcare.html': ('Why Delaying Healthcare Costs More Than Time'+SUF, 'Why people put off care, what waiting can cost, and how to tell when it is time to act sooner. A practical guide to making the next step easier.'),
 'healthy-aging-guide.html': ('Healthy Aging Starts with Strength'+SUF, 'A practical primer on strength and mobility for healthy aging, from a family doctor.'),
 'self-care.html': ('Self-Care for Busy Moms and Caregivers'+SUF, 'Low-friction self-care for busy moms and caregivers: rest, boundaries, movement, sleep, and asking for help.'),
 'intensive-lifestyle-modification.html': ('Intensive Lifestyle Modification for Obesity: Not a Boot Camp'+SUF, 'What intensive lifestyle care for obesity actually means, when it fits, and who can help, explained by a family doctor.'),
 'why-does-your-stomach-hurt-decode-the-mystery-and-find-relief.html': ('Stomach Pain: Causes, Red Flags, and When to Get Help'+SUF, 'Stomach pain explained by a family doctor: common causes, what location can tell you, home care, red flags, and when to get urgent care.'),
 'telehealth-after-pandemic.html': ('Telehealth After the Pandemic: When Virtual Care Works'+SUF, 'When a virtual visit works, when in-person care is safer, and how to prepare, from a family doctor.'),
 'childhood-immunizations.html': ('Childhood Immunizations: Why They Matter'+SUF, 'A plain-language guide to childhood vaccines: how they work, what they prevent, why timing matters, and how they protect the community.'),
 'articles.html': ('Health Articles from a Family Doctor'+SUF, 'Plain-English articles from a family doctor on blood pressure, prediabetes, cough, aging, mental health and prevention.'),
}
IMG = {
 'hypertension-101-how-to-keep-your-blood-pressure-in-check.html': 'hero-blood-pressure.jpg',
 'summer-heat-safety-west-valley-families.html': 'heat-safety-families.jpg',
 'summer-heat-safety-west-valley-families-outdoor-workers.html': 'heat-safety-families.jpg',
 'mental-health-policy-overhaul-bridging-gaps-in-care-and-what-it-means-for-you.html': 'hero-mental-health.jpg',
 'the-future-of-telehealth-post-pandemic-a-professional-perspective.html': 'future-of-telehealth-post-pandemic.jpg',
}
DEF = 'hero-design.jpg'
SKIP = {'ig.html','disclaimer.html'}
log = []
def esc(s): return html.escape(s, quote=True)
def setmeta(h, attr, key, val):
    pat = re.compile(r'(<meta %s="%s" content=")[^"]*(")' % (attr, re.escape(key)))
    if pat.search(h): return pat.sub(lambda m: m.group(1)+esc(val)+m.group(2), h)
    return h.replace('</head>', '  <meta %s="%s" content="%s" />\n</head>' % (attr, key, esc(val)), 1)
for f in sorted(glob.glob('*.html')):
    h = open(f, encoding='utf-8').read(); o = h
    if f in T:
        t, d = T[f]
        h = re.sub(r'<title>[^<]*</title>', lambda m: '<title>%s</title>' % esc(t), h, 1)
        h = setmeta(h, 'name', 'description', d)
        h = setmeta(h, 'property', 'og:title', t.replace(SUF, ''))
        h = setmeta(h, 'property', 'og:description', d)
        if 'twitter:card' in h:
            pass
    if f not in SKIP:
        if 'og:image' not in h:
            h = h.replace('</head>', '  <meta property="og:image" content="https://docnunez.com/assets/media/%s" />\n</head>' % IMG.get(f, DEF), 1)
        if 'twitter:card' not in h:
            h = h.replace('</head>', '  <meta name="twitter:card" content="summary_large_image" />\n</head>', 1)
        if 'og:title' not in h:
            m = re.search(r'<title>([^<]*)</title>', h)
            h = h.replace('</head>', '  <meta property="og:title" content="%s" />\n</head>' % m.group(1).split(' | ')[0].split(' · ')[0], 1)
    if f == 'newsletter.html':
        h = h.replace('Join the existing docnunez newsletter for occasional article updates.', 'Get a short note from Dr. Nunez when a new health article goes up. A couple of times a month at most. Unsubscribe any time.')
        h = h.replace('<p>A short note when there is something useful to share. You can unsubscribe any time.</p>', '<p>A short note from Dr. Nunez when a new article goes up, a couple of times a month at most. Plain-English health notes, no daily emails. You can unsubscribe any time.</p>')
        h = h.replace('<p class="small-meta">This form is run by MailerLite and adds confirmed readers to the docnunez mailing list. No diagnosis or personal health information belongs in it.</p>', '<p class="small-meta">This form is run by MailerLite. No diagnosis or personal health information belongs in it.</p>')
        h = setmeta(h, 'property', 'og:title', 'Get new articles by email | Dr. Nunez')
    # subscribe box on article pages
    if 'og:type" content="article"' in h and 'subscribe-box' not in h and f not in SKIP:
        h = h.replace('</main>', BOX + '  </main>', 1)
        if "ml('account'" not in h:
            h = h.replace('</head>', ML + '</head>', 1)
    if 'goatcounter' not in h:
        h = h.replace('</head>', GC + '</head>', 1)
    if h != o:
        open(f, 'w', encoding='utf-8').write(h); log.append(f)
print(len(log), 'files changed')
