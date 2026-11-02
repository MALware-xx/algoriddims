from pathlib import Path
import re, json, hashlib, html
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

ROOT = Path(__file__).parent
SRC = ROOT / 'original'
OUT = ROOT / 'dist'
ORIGIN = 'https://ready-resilience-store.vercel.app'
NAV = [('/start-here.html', '12 TOPICS'), ('/free-tools.html', 'FREE TOOLS'), ('/journal/', 'FIELD NOTES'), ('/home/', 'HOME SYSTEMS'), ('/sources.html', 'SOURCES'), ('/#catalogue', 'PLANS + PRICES')]

def navlinks(path):
    active = '/journal/' if path.startswith('/journal/') else '/free-tools.html' if path.startswith('/tools/') else '/home/' if path.startswith('/home/') else '/start-here.html' if path.startswith('/topics/') else path
    return ''.join(f'<a href="{url}"'+(' aria-current="page"' if url == active else '')+f'>{label}</a>' for url,label in NAV)

def header(path):
    links = navlinks(path)
    return f'''<a class="ready-skip" href="#main">Skip to main content</a><header class="ready-header"><div class="ready-container ready-header-inner"><a class="ready-brand" href="/" aria-label="READY home">READY<span>/</span></a><nav class="ready-desktop-nav" aria-label="Main">{links}</nav><details class="ready-mobile-menu"><summary>MENU <span aria-hidden="true">＋</span></summary><nav aria-label="Main mobile">{links}</nav></details></div></header>'''

FOOTER = '''<footer class="ready-footer"><div class="ready-container ready-footer-inner"><div><a class="ready-brand" href="/" aria-label="READY home">READY<span>/</span></a><p>Independent practical resilience tools.<br>Not an official government publication.</p></div><nav aria-label="Footer"><a href="/">Home</a><a href="/start-here.html">12 topics</a><a href="/free-tools.html">Free tools</a><a href="/journal/">Field notes</a><a href="/home/">Home systems</a><a href="/sources.html">Sources</a><a href="/terms.html">Terms</a><a href="/privacy.html">Privacy</a></nav></div><div class="ready-container ready-footer-note">During a live incident, follow current instructions from emergency services, utilities, relevant professionals and public authorities.</div></footer>'''

CSS = '''/* READY/ shared public site shell. Edit here, then build every public page. */
@font-face{font-family:Inter;src:url('/journal-assets/Inter-Regular.ttf') format('truetype');font-style:normal;font-weight:400;font-display:swap}
:root{--ready-max:1240px;--ready-gutter:32px;--ready-ink:#111;--ready-paper:#f2efe8;--ready-line:#cfc9bd;--ready-red:#d62d20;--ready-muted:#67635c;--ready-blue:#2e6fae}
html{scroll-padding-top:100px;scrollbar-gutter:stable}body.ready-site{margin:0;background:#fff!important;color:var(--ready-ink)!important;font-family:Inter,sans-serif!important;min-width:320px;line-height:1.65}body.ready-site *{box-sizing:border-box}.ready-site button,.ready-site input,.ready-site select,.ready-site textarea{font-family:Inter,sans-serif!important}.ready-site a{color:inherit;text-underline-offset:4px}.ready-site :is(a,button,input,select,textarea,summary):focus-visible{outline:3px solid var(--ready-blue);outline-offset:4px}
.ready-site .ready-container,.ready-site :is(.w,.wrap,.shell,.site-shell){width:100%;max-width:var(--ready-max)!important;margin-left:auto!important;margin-right:auto!important;padding-left:var(--ready-gutter)!important;padding-right:var(--ready-gutter)!important}
.ready-site .ready-skip{position:fixed;left:16px;top:-100px;z-index:100;background:#fff;border:1px solid #111;padding:12px 16px;font-size:14px;font-weight:700}.ready-site .ready-skip:focus{top:12px}
.ready-site .ready-header{position:sticky!important;top:0;z-index:50!important;height:78px!important;min-height:78px!important;margin:0!important;padding:0!important;background:#fff!important;border:0!important;border-bottom:1px solid var(--ready-line)!important;display:block!important}.ready-site .ready-header-inner{height:100%;display:flex;align-items:center;justify-content:space-between;gap:32px}.ready-site .ready-brand{display:inline-block;font-family:Inter,sans-serif;font-size:30px!important;line-height:1!important;letter-spacing:-.06em!important;font-weight:800!important;text-decoration:none!important;white-space:nowrap}.ready-site .ready-brand span{color:var(--ready-red)}
.ready-site .ready-desktop-nav{display:flex;align-items:center;gap:22px;margin:0;padding:0;font-size:11px;line-height:1.3;font-weight:800;letter-spacing:.065em}.ready-site .ready-desktop-nav a,.ready-site .ready-mobile-menu nav a{padding:10px 0;text-decoration:none;white-space:nowrap}.ready-site .ready-desktop-nav a:hover,.ready-site .ready-desktop-nav a[aria-current],.ready-site .ready-mobile-menu nav a[aria-current]{color:var(--ready-red)}.ready-site .ready-mobile-menu{display:none;margin:0;padding:0;border:0;background:transparent}.ready-site .ready-mobile-menu summary{display:flex;gap:18px;align-items:center;list-style:none;cursor:pointer;font-size:12px;font-weight:800;letter-spacing:.08em}.ready-site .ready-mobile-menu summary::-webkit-details-marker{display:none}.ready-site .ready-mobile-menu summary span{font-size:22px;font-weight:400}.ready-site .ready-mobile-menu[open] summary span{transform:rotate(45deg)}
.ready-site h1,.ready-site .hero h1,.ready-site .piece h1{font-family:Inter,sans-serif!important;font-size:clamp(38px,5.2vw,72px)!important;line-height:1.02!important;letter-spacing:-.055em!important;font-weight:800!important;margin:16px 0 24px!important;max-width:1040px}.ready-site h2{font-family:Inter,sans-serif!important;font-size:clamp(26px,3vw,38px);line-height:1.15;letter-spacing:-.04em;font-weight:800}.ready-site h3{font-family:Inter,sans-serif!important;line-height:1.25;letter-spacing:-.025em}.ready-site p,.ready-site li{line-height:1.7}.ready-site :is(.ey,.k,.eyebrow,.code){font-size:11px!important;line-height:1.5;letter-spacing:.12em!important;text-transform:uppercase;font-weight:800;color:var(--ready-muted)}
.ready-site section.hero{background:var(--ready-paper)!important;border-bottom:1px solid var(--ready-line);margin:0;padding:0}.ready-site section.hero>:is(.w,.wrap,.shell,.ready-container){padding-top:52px!important;padding-bottom:52px!important}.ready-site .hero :is(.lead,.lede),.ready-site .ready-page-hero .lead{font-size:18px!important;line-height:1.65!important;color:#393631;max-width:740px;margin:0 0 12px}.ready-site .hero .meta{font-size:12px;color:var(--ready-muted);margin-top:20px}.ready-site .hero h1 br{display:initial}.ready-site :is(.lede,.lead){font-size:18px;line-height:1.65;color:#393631}
.ready-site :is(.btn,.button,.cta){display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:46px;max-width:100%;padding:12px 17px!important;border:1px solid var(--ready-ink)!important;border-radius:0!important;background:#fff;color:var(--ready-ink);font-size:12px!important;font-weight:800!important;line-height:1.4!important;letter-spacing:.025em;text-decoration:none!important;cursor:pointer;white-space:normal;text-align:center}.ready-site :is(.btn.red,.button-red,.cta,.button.primary){background:var(--ready-red)!important;border-color:var(--ready-red)!important;color:#fff!important}.ready-site :is(.btn,.button,.cta):hover{filter:brightness(.94)}.ready-site :is(.buttons,.actions):not(ol){gap:12px}.ready-site button:disabled{cursor:wait;opacity:.6}
.ready-site :is(main.guide,main.tool){padding:44px 0 64px}.ready-site main.guide h2,.ready-site .body h2{margin:36px 0 16px}.ready-site :is(.callout,.box,.form,.result,.buybox){border-color:var(--ready-line)!important;border-radius:0}.ready-site .callout,.ready-site .box{background:var(--ready-paper)!important;padding:22px!important;border:1px solid var(--ready-line)}.ready-site :is(.form,.buybox){padding:24px!important;background:#fff}.ready-site .buybox{border-top:3px solid var(--ready-red)!important;top:102px}.ready-site [hidden]{display:none!important}.ready-site .checks label{cursor:pointer}.ready-site input[type=checkbox]{accent-color:var(--ready-red);width:18px;height:18px;flex:none}.ready-site input[type=number]{min-height:46px;max-width:100%;padding:10px 12px;border:1px solid var(--ready-line);border-radius:0}.ready-site .source,.ready-site .sources{overflow-wrap:anywhere;font-size:13px;color:var(--ready-muted)}
.ready-site .ready-article{max-width:var(--ready-max);padding:44px var(--ready-gutter) 64px;margin:auto}.ready-site .ready-article .piece{max-width:920px;border:0;padding:0;margin:0}.ready-site .ready-article figure{margin:0 0 30px}.ready-site .ready-article figure img{width:100%;height:auto;display:block}.ready-site .ready-article .body{max-width:780px}.ready-site .ready-article .body p,.ready-site .ready-article .body li{font-size:16px}.ready-site .ready-article figcaption{font-size:12px;color:var(--ready-muted);line-height:1.5;margin-top:10px}.ready-site .ready-article table{border-collapse:collapse;width:100%;font-size:14px}.ready-site .ready-article th,.ready-site .ready-article td{padding:12px;border-bottom:1px solid var(--ready-line);vertical-align:top;text-align:left}.ready-site .ready-article th{background:var(--ready-paper)}.ready-site .table-wrap{max-width:100%;overflow-x:auto}.ready-site .ready-journal-main{padding:44px 0 64px}.ready-site .ready-journal-main .grid{max-width:var(--ready-max);padding:0 var(--ready-gutter);margin:auto;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}.ready-site .ready-journal-main .card,.ready-site .ready-feature-card{background:#fff;border:1px solid var(--ready-line);border-top:3px solid var(--ready-ink);padding:0 0 22px;text-decoration:none;display:block;min-width:0}.ready-site .ready-journal-main .card img,.ready-site .ready-feature-card img{display:block;width:100%;height:auto!important;aspect-ratio:3/2;object-fit:cover}.ready-site .ready-journal-main .card .copy,.ready-site .ready-feature-card .copy{padding:0 20px}.ready-site .ready-journal-main .card h2,.ready-site .ready-feature-card h3{font-size:23px;line-height:1.2;margin:20px 0 14px}.ready-site .ready-journal-main .card p,.ready-site .ready-feature-card p{font-size:14px;line-height:1.65;color:var(--ready-muted)}.ready-site .ready-journal-main .card:hover h2,.ready-site .ready-feature-card:hover h3{text-decoration:underline;text-decoration-color:var(--ready-red)}.ready-site .ready-featured{padding:44px 0;background:var(--ready-paper);border-bottom:1px solid var(--ready-line)}.ready-site .ready-section-heading{display:flex;align-items:end;justify-content:space-between;gap:24px;margin-bottom:24px}.ready-site .ready-section-heading h2{margin:0 0 12px}.ready-site .ready-section-heading p{margin:0;max-width:68ch}.ready-site .ready-featured-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}.ready-site .ready-feature-card .ready-read{display:block;margin-top:16px;font-size:11px;font-weight:800;letter-spacing:.08em}
.ready-site .ready-footer{margin:0!important;padding:36px 0 28px!important;background:var(--ready-paper)!important;border:0!important;border-top:1px solid var(--ready-line)!important;color:var(--ready-muted);font-size:12px!important}.ready-site .ready-footer-inner{display:grid!important;grid-template-columns:1fr 1fr;gap:40px;align-items:start}.ready-site .ready-footer p{font-size:12px;line-height:1.6;margin:16px 0 0}.ready-site .ready-footer nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 24px;font-size:12px;letter-spacing:0;line-height:1.5;text-transform:none}.ready-site .ready-footer nav a{margin:0!important;padding:0!important;text-decoration:none}.ready-site .ready-footer nav a:hover{text-decoration:underline}.ready-site .ready-footer-note{font-size:11px;line-height:1.6;padding-top:28px!important;margin-top:28px!important;border-top:1px solid var(--ready-line)}.ready-site .page-shell{max-width:var(--ready-max);margin:auto;padding:44px var(--ready-gutter)}.ready-site .page-shell .hero-grid{display:block!important;min-height:40vh!important}
@media(max-width:1000px){.ready-site .ready-desktop-nav{gap:14px;font-size:10px}.ready-site .ready-header-inner{gap:24px}}
@media(max-width:900px){:root{--ready-gutter:24px}.ready-site .ready-desktop-nav{display:none}.ready-site .ready-mobile-menu{display:block}.ready-site .ready-mobile-menu nav{position:absolute;left:0;right:0;top:77px;display:grid;grid-template-columns:1fr 1fr;gap:0 24px;padding:18px var(--ready-gutter) 24px;background:#fff;border-bottom:1px solid var(--ready-line);box-shadow:0 12px 18px #00000012;font-size:12px;font-weight:800;letter-spacing:.04em}.ready-site .ready-mobile-menu nav a{padding:14px 0;border-bottom:1px solid var(--ready-line)}.ready-site .ready-journal-main .grid,.ready-site .ready-featured-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.ready-site .ready-footer-inner{grid-template-columns:1fr 1fr}.ready-site .buybox{position:static}}
@media(max-width:600px){:root{--ready-gutter:18px}.ready-site .ready-header{height:70px!important;min-height:70px!important}.ready-site .ready-brand{font-size:28px!important}.ready-site .ready-mobile-menu nav{top:69px}.ready-site section.hero>:is(.w,.wrap,.shell,.ready-container){padding-top:34px!important;padding-bottom:34px!important}.ready-site h1,.ready-site .hero h1,.ready-site .piece h1{font-size:38px!important;letter-spacing:-.05em!important;overflow-wrap:anywhere}.ready-site .hero :is(.lead,.lede){font-size:17px!important}.ready-site .ready-journal-main .grid,.ready-site .ready-featured-grid{grid-template-columns:1fr}.ready-site .ready-section-heading{display:block}.ready-site .ready-section-heading>.button{margin-top:20px}.ready-site .ready-footer-inner{grid-template-columns:1fr;gap:28px}.ready-site .ready-article{padding-top:30px}.ready-site .ready-article table{min-width:430px}.ready-site .ready-page-hero .meta{font-size:11px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}.ready-site *{scroll-behavior:auto!important}}
@media print{.ready-header,.ready-footer,.ready-skip,.ready-mobile-menu{display:none!important}.ready-site .ready-article{padding:0}.ready-site .hero{background:#fff!important}.ready-site h1,.ready-site .hero h1{font-size:32px!important}.ready-site .table-wrap{overflow:visible}.ready-site a{color:#111!important}}
 .ready-site .chooser h2{font-size:20px;line-height:1.25;letter-spacing:-.025em}.ready-site .pc h2,.ready-site .card h2,.ready-site .buybox h2{font-size:24px;line-height:1.2}
.ready-site .fresh-status{border-bottom:1px solid var(--ready-line);padding:10px var(--ready-gutter);font-size:12px;background:#fff}.ready-site .fresh-index{padding-top:30px}.ready-site .fresh-card img{aspect-ratio:1!important;object-fit:contain!important}.ready-site .fresh-card .copy p{padding-top:6px}.ready-site details.fresh-reddit{margin:32px 0;padding:22px;background:var(--ready-paper);border:1px solid var(--ready-line);max-width:920px}.ready-site .fresh-reddit summary{cursor:pointer;font-weight:700}.ready-site .fresh-reddit h2{font-size:25px}.ready-site .fresh-article{padding-bottom:52px;border-bottom:1px solid var(--ready-line)}.ready-site .fresh-article figure{max-width:780px}.ready-site .fresh-article p{overflow-wrap:anywhere}.ready-site .fresh-top{margin-top:30px;font-size:13px}.ready-site .fresh-sources{margin-top:36px;border-top:1px solid var(--ready-line);padding-top:12px}.ready-site .fresh-sources h2{font-size:25px}.ready-site .fresh-sources li{font-size:13px}.ready-site .fresh-reddit p,.ready-site .fresh-reddit li{font-size:15px}.ready-site .fresh-meta{font-size:12px;color:var(--ready-muted)}.ready-site .fresh-count{font-size:11px;letter-spacing:.08em}.ready-site .ready-article h2{break-after:avoid}@media print{details.fresh-reddit{display:none}.fresh-article{break-before:page}.fresh-article figure{max-width:400px}}

'''

def featured():
    items=json.loads((ROOT/'featured.json').read_text())
    cards=[]
    for item in items:
        cards.append(f'<a class="ready-feature-card fresh-card" href="/journal/{item["slug"]}/"><img src="/journal-assets/fresh/{item["id"]}.jpg" alt="{html.escape(item["alt"],quote=True)}" width="1254" height="1254" loading="lazy"><div class="copy"><h3>{html.escape(item["title"])}</h3><p>{html.escape(item["description"])}</p><span class="ready-read">READ THE FIELD NOTE →</span></div></a>')
    return '<section class="ready-featured" aria-labelledby="field-notes-title"><div class="ready-container"><div class="ready-section-heading"><div><p class="ey">FREE READING / PRACTICAL NEXT STEPS</p><h2 id="field-notes-title">READY/ FIELD NOTES</h2><p>Useful answers for the home and business systems you depend on. Read an article, then try the matching free check.</p></div><a class="button button-red" href="/journal/">READ ALL FIELD NOTES →</a></div><div class="ready-featured-grid">'+''.join(cards)+'</div></div></section>'

inventory=json.loads((ROOT/'inventory.json').read_text())
if not any(i['path']=='/access.html' for i in inventory):
    inventory.append({'path':'/access.html','type':'text/html'})
PUBLIC_PATHS={i['path'] for i in inventory if i.get('type')=='text/html' and i['path']!='/access.html'}

def version_navigation(s):
    # Older releases cached public HTML for a year. Navigation opts into the new
    # layout once; canonical URLs remain clean and no purchaser URLs are changed.
    def update(match):
        quote,value=match[1],html.unescape(match[2]);url=urlsplit(value)
        if url.netloc or url.path not in PUBLIC_PATHS:return match[0]
        query=dict(parse_qsl(url.query));query['ui']='1'
        value=urlunsplit(('', '', url.path, urlencode(query),url.fragment))
        return 'href='+quote+html.escape(value,quote=True)+quote
    parts=re.split(r'(<script\b[^>]*>.*?</script>)',s,flags=re.S|re.I)
    return ''.join(part if part.lower().startswith('<script') else re.sub(r'href=([\"\'])(/[^\"\']*)\1',update,part) for part in parts)

NAV_JS='''/* Keep dynamically generated internal links on the current READY layout. */
const readyPublicPaths=new Set(PATHS);
document.addEventListener('click',event=>{const link=event.target.closest?.('a[href]');if(!link||link.hasAttribute('download'))return;const url=new URL(link.href,location.href);if(url.origin!==location.origin||!readyPublicPaths.has(url.pathname))return;url.searchParams.set('ui','1');link.href=url.pathname+url.search+url.hash;});
'''.replace('PATHS',json.dumps(sorted(PUBLIC_PATHS)))
manifest=[]
for item in inventory:
    if item.get('type')!='text/html':continue
    path=item['path'];relative='index.html' if path=='/' else path.lstrip('/')+('index.html' if path.endswith('/') else '')
    original=(SRC/relative).read_text();s=original
    # Keep page content and all inline application scripts; replace the common shell.
    s=re.sub(r'<header\b[^>]*>.*?</header>','',s,flags=re.S|re.I)
    s=re.sub(r'<footer\b[^>]*>.*?</footer>','',s,flags=re.S|re.I)
    s=re.sub(r'<a\b[^>]*class="(?:skip|ready-skip)"[^>]*>.*?</a>','',s,flags=re.S|re.I)
    s=re.sub(r'<body([^>]*)>',lambda m:'<body'+m[1]+' class="ready-site">'+header(path),s,count=1,flags=re.I)
    s=s.replace('</body>',FOOTER+'</body>')
    s=s.replace('</head>','<link rel="stylesheet" href="/assets/ready-shell-v2.css"></head>')
    if 'fonts.googleapis.com/css2?family=Inter' not in s:
        s=s.replace('</head>','<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;display=swap"></head>')
    if '<main' in s:
        s=re.sub(r'<main\b([^>]*)>',lambda m:'<main'+(m[1] if re.search(r'\bid=',m[1]) else m[1]+' id="main"')+'>',s,count=1)
    # Put the journal and tools on the same page-introduction pattern as the store.
    if path.startswith('/journal/') and path!='/journal/':
        pattern=r'(<article\b[^>]*>)(<p class="eyebrow">.*?</p><h1>.*?</h1><p class="lead">.*?</p><p class="meta">.*?</p>)'
        found=re.search(pattern,s,flags=re.S)
        if not found:raise ValueError('Journal intro missing: '+path)
        intro=found[2];s=s[:found.start()]+'<section class="hero ready-page-hero"><div class="ready-container">'+intro+'</div></section><main id="main" class="ready-article">'+found[1]+s[found.end():]
        s=s.replace('</article></body>','</article></main></body>') if '</article></body>' in s else s.replace('</article>'+FOOTER,'</article></main>'+FOOTER)
    elif path=='/journal/':
        s=s.replace('<main id="main"><section class="intro">','<section class="hero ready-page-hero"><div class="ready-container">')
        s=s.replace('</section><div class="grid">','</div></section><main id="main" class="ready-journal-main"><div class="grid">',1)
    elif re.search(r'<main class="(?:guide|tool)" id="main"><div class="shell">',s):
        pattern=r'(<main class="(?:guide|tool)" id="main"><div class="shell">)(<div class="ey">.*?</div><h1>.*?</h1><p class="lede">.*?</p>)'
        found=re.search(pattern,s,flags=re.S)
        if found:s=s[:found.start()]+'<section class="hero ready-page-hero"><div class="ready-container">'+found[2]+'</div></section>'+found[1]+s[found.end():]
    if path=='/':
        s=s.replace('<main class="w" id="main">',featured()+'<main class="w" id="main">',1)
    if path=='/home/':s=s.replace('READY/09 / EVERGREEN ACQUISITION','READY/09 / HOME SYSTEMS')
    # Accessible live results on the four free tools; application selectors remain identical.
    s=s.replace('class="result" id="result" hidden','class="result" id="result" role="status" aria-live="polite" hidden')
    s=version_navigation(s)
    if path!='/access.html' and not re.search(r'<link\b[^>]*rel=[\"\']canonical[\"\']',s):
        s=s.replace('</head>','<link rel="canonical" href="'+ORIGIN+path+'"></head>')
    old_scripts=re.findall(r'<script\b[^>]*>(.*?)</script>',original,re.S)
    new_scripts=re.findall(r'<script\b[^>]*>(.*?)</script>',s,re.S)
    if old_scripts!=new_scripts:raise ValueError('Application script changed: '+path)
    s=s.replace('</body>','<script src="/assets/ready-navigation-v1.js" defer></script></body>')
    if s.count('id="main"')!=1 or s.count('<main')!=1 or s.count('</main>')!=1:raise ValueError('Main landmark invalid: '+path)
    file=OUT/('index.html' if path=='/' else path.lstrip('/')+('index.html' if path.endswith('/') else ''))
    file.parent.mkdir(parents=True,exist_ok=True);file.write_text(s)
    manifest.append({'path':path,'file':str(file),'scripts_unchanged':True,'sha256':hashlib.sha256(s.encode()).hexdigest()})
(OUT/'assets').mkdir(exist_ok=True)
(OUT/'assets/ready-shell-v2.css').write_text(CSS)
(OUT/'assets/ready-navigation-v1.js').write_text(NAV_JS)
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+ORIGIN+path+'</loc><lastmod>2026-11-02</lastmod></url>' for path in sorted(PUBLIC_PATHS))+'</urlset>')
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'public_pages':len(manifest),'shared_header':True,'shared_footer':True,'shared_stylesheet':True,'application_scripts_preserved':True}))

