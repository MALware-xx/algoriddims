#!/usr/bin/env python3
"""
Build dist/ALG0RIDDIMS_Identity_v0.5.pdf from identity/identity.src.html.

Every image in the guidelines is made fresh from the generator and the player,
so the PDF always shows what the tools actually produce.

usage:  python3 scripts/build_identity.py
needs:  pip install playwright && python3 -m playwright install chromium
        run scripts/build_player.py and scripts/make_marks.py first
"""
import pathlib, sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'identity' / 'assets'
PLAYER = ROOT / 'dist' / 'alg0_player.html'
OUT = ROOT / 'dist' / 'ALG0RIDDIMS_Identity_v0.5.pdf'
sys.path.insert(0, str(ROOT / 'generator'))
import alg0_field as G  # noqa: E402

ASSETS.mkdir(parents=True, exist_ok=True)
if not PLAYER.exists():
    sys.exit('dist/alg0_player.html missing: run scripts/build_player.py first')


def tile(name, seed, prog='NIGHT', cway='STANDARD'):
    svg, _ = G.svg(seed, 480, 480, 16, G.PROGRAMMES[prog], cway)
    (ASSETS / name).write_text(svg)


for p in G.PROGRAMMES:
    tile(f'prog_{p}.svg', 211126, p)
for c in ('STANDARD', 'DUO', 'ACCENT', 'MONO', 'INVERT'):
    tile(f'cw_{c}.svg', 211126, 'NIGHT', c)
for s in (211126, 120327, 300427):
    tile(f'seed_{s}.svg', s)

PLACEHOLDER_SETLIST = ['19:00 [PERFORMER]', '20:00 [PERFORMER]', '21:00 [PERFORMER]', '22:00 [PERFORMER]']

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width': 1080, 'height': 1080})
    pg.goto(PLAYER.as_uri())
    pg.wait_for_timeout(800)

    def shot(path, fmt, params, step=None):
        info = pg.evaluate('o => ALG0PLAYER.setup(o)', {'seed': 211126, 'programme': 'NIGHT', 'bpm': 140,
                                                        'format': fmt, 'params': params})
        pg.set_viewport_size({'width': info['W'], 'height': info['H']})
        pg.evaluate('ALG0PLAYER.still()' if step is None else f'ALG0PLAYER.frame({step})')
        pg.wait_for_timeout(80)
        pg.locator('#stage').screenshot(path=str(ASSETS / path))

    for f in ('poster', 'square', 'story', 'vj'):
        shot(f'lay_{f}.png', f, {'setlist': PLACEHOLDER_SETLIST})
    for m in ('sweep', 'poly', 'drift', 'rain'):
        shot(f'mode_{m}.png', 'square', {'type': False, 'mode': m, 'ripple': 0.6, 'pulse': 0.5, 'decay': 4}, 21.5)
    for code in ('1000', '1061', '12A7', '14ED'):
        shot(f'look_{code}.png', 'square', {'look': code}, 26.5)
    shot('cover_vj.png', 'vj', {'type': False, 'depth': 0.8, 'ripple': 0.5}, 18.5)

    # the failure case for the minimum-size panel: the micro mark typed at 16 px
    font = (ROOT / 'fonts' / 'IBMPlexMono-Bold.woff2').as_uri()
    pg.set_viewport_size({'width': 16, 'height': 16})
    pg.set_content(f"""<style>@font-face{{font-family:P;src:url({font})}}body{{margin:0}}
      div{{width:16px;height:16px;background:#121212;color:#F2F1EC;font:700 8.5px/16px P;text-align:center}}</style><div>0_</div>""")
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(ASSETS / 'micro_typed16.png'))

    doc = b.new_page()
    doc.goto((ROOT / 'identity' / 'identity.src.html').as_uri())
    doc.wait_for_timeout(1500)
    doc.pdf(path=str(OUT), prefer_css_page_size=True, print_background=True)
    b.close()

print(OUT.relative_to(ROOT))
