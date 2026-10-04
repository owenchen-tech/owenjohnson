"""Generate a dependency-free portfolio: python3 build.py."""
import json
import re
import shutil
from html import escape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
profile = json.loads((ROOT / 'data/profile.json').read_text())
projects = json.loads((ROOT / 'data/projects.json').read_text())
built_files = []

def e(value):
    return escape(str(value), quote=True)

def safe_url(value):
    return urlparse(value).scheme in ('http', 'https') and bool(urlparse(value).netloc)

def asset(value):
    if not value:
        return ''
    path = (ROOT / value.lstrip('/')).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f'Configured asset does not exist: {value}')
    return '/' + path.relative_to(ROOT).as_posix()

portrait = asset(profile['portrait'])
pdf = asset(profile['resumePdf'])
for key in ('linkedin', 'github', 'siteUrl'):
    if profile[key] and not safe_url(profile[key]):
        raise ValueError(f'{key} must be an absolute HTTP(S) URL')
if profile['email'] and not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+', profile['email']):
    raise ValueError('Please configure a valid email address')

def contact(label, key, cls='button secondary'):
    value = profile[key]
    if not value:
        return f'<span class="{cls} unavailable" aria-disabled="true">{e(label)} <span class="availability">Pending</span></span>'
    href = 'mailto:' + value if key == 'email' else value
    return f'<a class="{cls}" href="{e(href)}">{e(label)} <span aria-hidden="true">↗</span></a>'

def download():
    return f'<a class="button secondary" href="{e(pdf)}" download>Download Resume PDF ↓</a>' if pdf else '<span class="button secondary unavailable" aria-disabled="true">Download Resume PDF <span class="availability">Pending</span></span>'

def diagram():
    steps = ['Chip Design', 'Wafer Fabrication', 'Packaging & Testing', 'Electronics Manufacturing', 'End Customer']
    inputs = ['Equipment', 'Materials', 'Silicon wafers', 'Chemicals', 'Specialty gases', 'Photomasks']
    return '<figure class="chain-figure"><div class="diagram-label">UPSTREAM INPUTS <span>· framework to expand</span></div><ul class="input-chips">' + ''.join(f'<li>{x}</li>' for x in inputs) + '</ul><div class="input-connector" aria-hidden="true">↓</div><ol class="chain">' + ''.join(f'<li><span class="step-number">0{i+1}</span><span>{x}</span></li>' for i, x in enumerate(steps)) + '</ol><figcaption>Conceptual sequence for organizing research. Upstream relationships and product-specific paths will be detailed as the project develops.</figcaption></figure>'

def card(p, i):
    visual = '<div class="mini-chain" aria-hidden="true"><span>DESIGN</span><b>→</b><span>FABRICATION</span><b>→</b><span>TEST</span></div>' if p['visual'] == 'supply-chain' else '<div class="mini-score" aria-hidden="true"><span>Cost</span><span>Quality</span><span>Lead time</span><span>Capacity</span><span>Delivery</span><span>Risk</span></div>'
    return f'''<article class="project-card"><div class="project-art"><span class="art-index">STUDY / 0{i+1}</span>{visual}<span class="art-caption">{'THE SEMICONDUCTOR VALUE CHAIN' if i == 0 else 'SOURCING × PLANNING'}</span></div><div class="project-body"><div class="card-meta"><span>CASE STUDY</span><span class="status"><i></i>{e(p['status'])}</span></div><h3>{e(p['title'])}</h3><p class="project-question">{e(p['question'])}</p><p>{e(p['description'])}</p><div class="tags">{''.join(f'<span>{e(t)}</span>' for t in p['topics'])}</div><a class="text-link" href="/projects/{e(p['slug'])}/">View Case Study <span aria-hidden="true">↗</span></a></div></article>'''

def header(active):
    links = [('Home', '/'), ('Projects', '/#projects'), ('About', '/#about'), ('Experience', '/#experience'), ('Contact', '/#contact')]
    return '<header class="site-header"><div class="container header-inner"><a href="/" class="wordmark" aria-label="Owen Johnson home">OWEN JOHNSON<span class="brand-dot"></span></a><button class="menu-toggle" aria-controls="main-nav" aria-expanded="false">Menu <span aria-hidden="true">☰</span></button><nav id="main-nav" aria-label="Main navigation">' + ''.join(f'<a href="{url}"' + (' aria-current="page"' if label == active else '') + f'>{label}</a>' for label, url in links) + '<a class="nav-resume" href="/resume/">Resume <span aria-hidden="true">↗</span></a></nav></div></header>'

def page(title, description, body, route='/', active=''):
    canonical = profile['siteUrl'].rstrip('/') + route if profile['siteUrl'] else ''
    meta = f'<link rel="canonical" href="{e(canonical)}"><meta property="og:url" content="{e(canonical)}">' if canonical else ''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(description)}">{meta}<meta name="theme-color" content="#193f3b"><link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"><link rel="stylesheet" href="/style.css"><script src="/script.js" defer></script></head><body><a class="skip-link" href="#main">Skip to content</a>{header(active)}<main id="main">{body}</main><footer class="site-footer container"><a class="footer-name" href="/">Owen Johnson</a><span>Technology foundation. International perspective.</span><span>Based in Taiwan · © 2026</span></footer></body></html>'''

def experience():
    return '''<div class="experience-list"><article class="experience-row"><div><span class="eyebrow">2024–2025</span><h3>Space Dynamics Laboratory</h3><span class="role">IT Service Desk</span></div><div><p>Provided technical support in a secure defense R&D environment, supporting enterprise users, systems, hardware, software, networking, identity/access technologies, workstation deployment, asset management, and technical documentation.</p><div class="tags"><span>Technical problem solving</span><span>Secure technology environment</span><span>Cross-functional support</span><span>Enterprise systems</span><span>Documentation</span><span>Operational reliability</span></div></div></article><article class="experience-row"><div><span class="eyebrow">TECHNOLOGY & CUSTOMER EXPERIENCE</span><h3>Expercom</h3><span class="role">Sales Technician</span></div><div><p>Customer-facing technology sales and technical support, including customer communication, B2B outreach, e-commerce, and technology products.</p><div class="tags"><span>Customer communication</span><span>Technology sales</span><span>B2B outreach</span><span>Problem solving</span></div></div></article></div><div class="credentials"><div><span class="eyebrow">EDUCATION</span><h3>Utah State University</h3><p>B.S. Technology Systems — Cybersecurity</p><span class="muted">Magna Cum Laude · 2025</span></div><div><span class="eyebrow">CERTIFICATIONS</span><h3>CompTIA Security+ <span class="muted">/</span> CompTIA A+</h3><p>A foundation in secure, reliable technology.</p></div></div>'''

def home():
    photo = f'<img src="{e(portrait)}" alt="{e(profile["portraitAlt"])}" width="480" height="560">' if portrait else '<div class="portrait-placeholder" role="img" aria-label="Reserved space for Owen Johnson’s professional portrait"><div class="portrait-monogram">OJ<span></span></div><div class="portrait-label"><span>OWEN JOHNSON</span><span>Professional portrait to be added</span></div></div>'
    learn = [('01', 'Semiconductor supply chains', 'Foundries, fabless companies, OSATs, equipment suppliers, semiconductor manufacturing, and the relationships connecting them.'), ('02', 'Procurement & strategic sourcing', 'Supplier selection, negotiation, total cost of ownership, supplier performance, and sourcing risk.'), ('03', 'Supply & demand planning', 'Forecasting, inventory, lead times, safety stock, replenishment, and capacity.'), ('04', 'Business Mandarin', 'Professional vocabulary for supply chain, technology, procurement, and international business.')]
    return f'''<section class="hero container"><div class="hero-content"><div class="eyebrow location"><span class="live-dot"></span> AMERICAN PROFESSIONAL · BASED IN TAIWAN</div><h1>Owen<br>Johnson<span class="accent">.</span></h1><p class="hero-fields">International Business · Supply Chain · Technology</p><p class="hero-description">American technology professional based in Taiwan, developing expertise in semiconductor supply chains, procurement, and international business.</p><div class="actions"><a class="button primary" href="#projects">View Projects <span aria-hidden="true">↗</span></a>{contact('LinkedIn', 'linkedin')}<a class="text-link" href="#contact">Contact Me <span aria-hidden="true">↗</span></a></div></div><div class="hero-portrait">{photo}<div class="portrait-foot"><span>U.S. FOUNDATION</span><span>TAIWAN PERSPECTIVE ↗</span></div></div></section><div class="foundation-strip"><div class="container"><span>TECHNICAL FOUNDATION</span><span>Secure R&D experience</span><span>Customer-facing technology</span><span>International outlook</span></div></div>
<section id="projects" class="section container"><div class="section-top"><div><span class="eyebrow">01 / APPLIED LEARNING</span><h2>Featured Projects</h2></div><p>Turning industry curiosity into structured analysis.<br>Two case studies currently in development.</p></div><div class="project-grid">{''.join(card(p, i) for i,p in enumerate(projects))}</div></section>
<section id="about" class="section about-section"><div class="container about-grid"><div><span class="eyebrow">02 / THE THROUGH LINE</span><h2>A technical foundation.<br>An international direction.</h2><div class="story-path">Technology <span>→</span> Cybersecurity <span>→</span> Professional IT <span>→</span> Customer & Sales Experience <span>→</span> Taiwan <span>→</span> Supply Chain & International Business</div></div><div class="about-copy"><h3>About Me</h3><p>I'm an American technology professional based in Taiwan with a B.S. in Technology Systems (Cybersecurity) from Utah State University and professional experience in technology support, secure R&D environments, and customer-facing sales.</p><p>I'm currently developing expertise in supply chain management, procurement, and international business, with a particular interest in Taiwan's semiconductor and electronics industries.</p><p class="about-emphasis">I'm especially interested in roles connecting technology, suppliers, customers, and international markets.</p></div></div></section>
<section class="section container" id="learning"><div class="section-top"><div><span class="eyebrow">03 / PROFESSIONAL DEVELOPMENT</span><h2>Currently Learning</h2></div><p>Building practical understanding,<br>one question at a time.</p></div><div class="learning-grid">{''.join(f'<article class="learning-item"><span class="learn-index">{i}</span><h3>{title}</h3><p>{text}</p></article>' for i,title,text in learn)}</div><div class="tools-line"><span class="eyebrow">TOOLS I'M DEVELOPING</span><span>Excel <b>·</b> PowerPoint <b>·</b> SAP / ERP Fundamentals</span></div></section>
<section id="experience" class="section experience-section"><div class="container"><div class="section-top"><div><span class="eyebrow">04 / PROFESSIONAL FOUNDATION</span><h2>Experience & Education</h2></div><a class="text-link" href="/resume/">View Resume <span aria-hidden="true">↗</span></a></div>{experience()}</div></section>
<section class="taiwan-section container"><span class="eyebrow">05 / INTERNATIONAL PERSPECTIVE</span><div class="taiwan-grid"><h2>Based in Taiwan.<br>International Perspective<span class="accent">.</span></h2><p>I'm a U.S. professional currently based in Taiwan, where I'm developing Mandarin proficiency and building expertise in Taiwan's technology and semiconductor ecosystem. I'm particularly interested in work connecting Taiwan with international suppliers, customers, and markets.</p></div><div class="taiwan-caption"><span>UNITED STATES</span><span class="connection-line" aria-hidden="true"></span><span>TAIWAN</span></div></section>
<section id="contact" class="contact-section"><div class="container contact-grid"><div><span class="eyebrow">06 / START A CONVERSATION</span><h2>Let's Connect<span>.</span></h2></div><div><p>I'm interested in opportunities involving supply chain, procurement, customer operations, international sales, and international business within Taiwan's technology industry.</p><div class="actions">{contact('Email', 'email')}{contact('LinkedIn', 'linkedin')}{contact('GitHub', 'github')}{download()}</div>{'<p class="contact-note">Contact links and the PDF résumé will be available when added.</p>' if any(not profile[k] for k in ('email','linkedin','github','resumePdf')) else ''}</div></div></section>'''

def project_page(p):
    sections = []
    for s in p['sections']:
        sid = re.sub(r'[^a-z0-9]+', '-', s['title'].lower()).strip('-')
        extra = diagram() if s['title'] == 'Supply Chain Map' else ''
        table = s.get('table')
        if table:
            extra += '<div class="table-scroll" role="region" tabindex="0" aria-label="' + e(s['title']) + ' data table"><table><caption>' + e(table.get('caption', s['title'])) + '</caption><thead><tr>' + ''.join('<th scope="col">' + e(h) + '</th>' for h in table['headers']) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + e(c) + '</td>' for c in row) + '</tr>' for row in table['rows']) + '</tbody></table></div>'
        sections.append(f'<section id="{sid}" class="report-section"><h2>{e(s["title"])}</h2><p>{e(s["text"])}</p>{extra}</section>')
    images = ''.join(f'<figure><img class="report-image" src="{e(asset(im["src"]))}" alt="{e(im["alt"])}" loading="lazy"><figcaption>{e(im.get("caption", ""))}</figcaption></figure>' for im in p['images'])
    sources = '<ol class="sources-list">' + ''.join(f'<li><a href="{e(s["url"])}">{e(s["title"])}</a>{" — " + e(s["note"]) if s.get("note") else ""}</li>' for s in p['sources'] if safe_url(s['url'])) + '</ol>' if p['sources'] else '<p>Sources will be listed here as the research is documented. No research citations have been added yet.</p>'
    toc = ''.join(f'<a href="{re.sub(r"[^a-z0-9]+", "-", s["title"].lower()).strip("-") and "#" + re.sub(r"[^a-z0-9]+", "-", s["title"].lower()).strip("-")}">{e(s["title"])}</a>' for s in p['sections'])
    return f'''<div class="container report"><a class="text-link back-link" href="/#projects">← All Projects</a><header class="report-header"><div class="card-meta"><span>RESEARCH CASE STUDY</span><span class="status"><i></i>{e(p['status'])}</span>{f'<span>{e(p["date"])}</span>' if p['date'] else ''}</div><h1>{e(p['title'])}</h1><p class="report-question">{e(p['question'])}</p><div class="tags">{''.join(f'<span>{e(t)}</span>' for t in p['topics'])}</div></header><div class="research-note"><strong>Work in progress</strong><p>This page establishes the research scope and report structure. Completed analysis, findings, and recommendations will be added as the work develops.</p></div><div class="report-layout"><aside class="report-toc"><nav aria-label="Case study contents"><span class="eyebrow">IN THIS REPORT</span>{toc}<a href="#sources">Sources</a></nav></aside><div class="report-content">{''.join(sections)}{images}<section id="sources" class="report-section"><h2>Sources</h2>{sources}</section></div></div><div class="report-bottom"><a class="text-link" href="/#projects">← Explore Projects</a><a class="text-link" href="/#contact">Let's Connect ↗</a></div></div>'''

def write(path, content):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    built_files.append(path)

write('index.html', page('Owen Johnson | International Business, Supply Chain & Technology', 'American technology professional based in Taiwan. Explore Owen Johnson’s background and developing work in semiconductor supply chains, procurement, and international business.', home(), active='Home'))
for p in projects:
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', p['slug']):
        raise ValueError('Project slugs must use lowercase letters, numbers and hyphens')
    write(f'projects/{p["slug"]}/index.html', page(f'{p["title"]} | Owen Johnson', p['description'], project_page(p), f'/projects/{p["slug"]}/', 'Projects'))
resume = f'''<div class="container resume-page"><a class="text-link back-link" href="/">← Back Home</a><header class="resume-header"><div><span class="eyebrow">PROFESSIONAL RESUME</span><h1>Owen Johnson</h1><p>International Business · Supply Chain · Technology</p><span class="muted">American professional based in Taiwan</span></div>{download()}</header><section class="resume-summary"><h2>Profile</h2><p>Technology professional with experience in secure R&D IT support and customer-facing technology sales. B.S. in Technology Systems (Cybersecurity), Utah State University. Currently developing expertise in semiconductor supply chains, procurement, and international business in Taiwan.</p></section><section><h2>Experience & Education</h2>{experience()}</section><section class="resume-summary"><h2>Current Professional Development</h2><p>Semiconductor supply chains · Procurement & strategic sourcing · Supply & demand planning · Business Mandarin</p><p>Tools: Excel · PowerPoint · SAP / ERP Fundamentals</p><a class="text-link" href="/#projects">View research in progress ↗</a></section><section class="resume-summary"><h2>Contact</h2><div class="actions">{contact('Email','email')}{contact('LinkedIn','linkedin')}</div></section></div>'''
write('resume/index.html', page('Resume | Owen Johnson', 'Owen Johnson’s professional experience, education, certifications, and current development in Taiwan’s technology industry.', resume, '/resume/'))
write('404.html', page('Page Not Found | Owen Johnson', 'Return to Owen Johnson’s portfolio.', '<section class="container error-page"><span class="eyebrow">404 / PAGE NOT FOUND</span><h1>Let’s get you back on track.</h1><a class="button primary" href="/">Return Home ↗</a></section>'))
if profile['siteUrl']:
    origin = profile['siteUrl'].rstrip('/')
    routes = ['/', '/resume/'] + [f'/projects/{p["slug"]}/' for p in projects]
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{e(origin+r)}</loc></url>' for r in routes) + '</urlset>')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {origin}/sitemap.xml\n')
else:
    write('robots.txt', 'User-agent: *\nAllow: /\n')
for path in built_files + ['style.css', 'script.js']:
    output = ROOT / 'dist' / path
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / path, output)
shutil.copytree(ROOT / 'assets', ROOT / 'dist/assets', dirs_exist_ok=True)
# The configured PDF or portrait may live outside assets; include it explicitly.
for path in (portrait, pdf):
    if path:
        relative = path.lstrip('/')
        output = ROOT / 'dist' / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, output)
print(f'Generated homepage, {len(projects)} case studies, resume, and 404 page. Deployable files: dist/')
