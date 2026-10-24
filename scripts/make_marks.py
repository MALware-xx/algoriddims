#!/usr/bin/env python3
"""
Build the ALG0RIDDIMS logo files in brand/.

The wordmark is typed, never drawn: these SVGs are IBM Plex Mono Bold's own glyph
outlines, set at tracking 0 with Plex's default (dotted) zero. Nothing is redrawn.
The one exception is the 16 px favicon, which is hand-set in pixels because no
typeface keeps the zero's dot at 16 px.

usage:  python3 scripts/make_marks.py          (needs: pip install fonttools brotli)
"""
import pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'brand'
INK, PAPER = '#121212', '#F2F1EC'

font = TTFont(ROOT / 'fonts' / 'IBMPlexMono-Bold.woff2')
gs, cmap = font.getGlyphSet(), font.getBestCmap()
UPM = font['head'].unitsPerEm                     # 1000
ADV = font['hmtx']['A'][0]                        # 600: one cell
CAP = font['OS/2'].sCapHeight                     # 698


def path_for(text, size, x0, baseline):
    """SVG path data for `text` set at `size` px, left edge x0, on `baseline`."""
    k = size / UPM
    pen = SVGPathPen(gs)
    for i, ch in enumerate(text):
        g = cmap[ord(ch)]
        tp = TransformPen(pen, (k, 0, 0, -k, x0 + i * ADV * k, baseline))
        gs[g].draw(tp)
    return pen.getCommands()


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n')


def wordmark(fg, bg=None, size=100):
    """One cell of padding on every side, as in the poster boxes (cell = 0.6 em)."""
    text = 'ALG0RIDDIMS_'
    cell = ADV / UPM * size
    w = len(text) * cell + 2 * cell
    h = size * 1.2 + cell                    # line of 1.2 em plus half a cell top and bottom
    base = h / 2 + CAP / UPM * size / 2      # cap height centred
    body = f'<rect width="{w:g}" height="{h:g}" fill="{bg}"/>' if bg else ''
    body += f'<path fill="{fg}" d="{path_for(text, size, cell, base)}"/>'
    return svg(round(w, 2), round(h, 2), body, 'ALG0RIDDIMS')


def micro(fg, bg, side=512):
    size = side * 0.53
    cell = ADV / UPM * size
    x0 = (side - 2 * cell) / 2
    base = side / 2 + CAP / UPM * size / 2
    body = f'<rect width="{side}" height="{side}" fill="{bg}"/><path fill="{fg}" d="{path_for("0_", size, x0, base)}"/>'
    return svg(side, side, body, 'ALG0RIDDIMS')


FAVICON_16 = [  # hand-set ('#' = paper, '.' = ink): zero 7 x 11, 2 px strokes, 1 x 3 dot in a 3 px counter, cursor on the base
    '................',
    '................',
    '................',
    '...#####........',
    '..#######.......',
    '..##...##.......',
    '..##...##.......',
    '..##.#.##.......',
    '..##.#.##.......',
    '..##.#.##.......',
    '..##...##.......',
    '..##...##.......',
    '..#######.#####.',
    '...#####..#####.',
    '................',
    '................',
]


def favicon16():
    rows = [list(r) for r in FAVICON_16]
    body = f'<rect width="16" height="16" fill="{INK}"/>'
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c == '#':
                body += f'<rect x="{x}" y="{y}" width="1" height="1" fill="{PAPER}"/>'
    return svg(16, 16, body, 'ALG0RIDDIMS'), rows


files = {
    'ALG0RIDDIMS_wordmark_paper-on-ink.svg': wordmark(PAPER, INK),
    'ALG0RIDDIMS_wordmark_ink-on-paper.svg': wordmark(INK, PAPER),
    'ALG0RIDDIMS_wordmark_ink.svg': wordmark(INK),
    'ALG0RIDDIMS_wordmark_paper.svg': wordmark(PAPER),
    'ALG0RIDDIMS_micro.svg': micro(PAPER, INK),
    'ALG0RIDDIMS_favicon-16.svg': favicon16()[0],
}
OUT.mkdir(exist_ok=True)
for name, data in files.items():
    (OUT / name).write_text(data)
    print('brand/' + name)

# PNGs (needs Pillow): favicon-16 pixel-exact, micro at app-icon sizes rendered from the SVG via Chromium if present
try:
    from PIL import Image
    _, rows = favicon16()
    im = Image.new('RGB', (16, 16), INK)
    px = im.load()
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c == '#':
                px[x, y] = (0xF2, 0xF1, 0xEC)
    im.save(OUT / 'ALG0RIDDIMS_favicon-16.png')
    print('brand/ALG0RIDDIMS_favicon-16.png')
except ImportError:
    pass
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        for side in (32, 180, 512):
            pg = b.new_page(viewport={'width': side, 'height': side})
            pg.set_content(f'<body style="margin:0">{micro(PAPER, INK, side)}</body>')
            pg.screenshot(path=str(OUT / f'ALG0RIDDIMS_micro-{side}.png'))
            print(f'brand/ALG0RIDDIMS_micro-{side}.png')
        for name in ('paper-on-ink', 'ink-on-paper'):
            data = (OUT / f'ALG0RIDDIMS_wordmark_{name}.svg').read_text()
            pg = b.new_page(viewport={'width': 2400, 'height': 400})
            pg.set_content(f'<body style="margin:0">{data.replace("<svg ", "<svg style=\"display:block;width:2400px;height:auto\" ", 1)}</body>')
            pg.locator('svg').screenshot(path=str(OUT / f'ALG0RIDDIMS_wordmark_{name}.png'))
            print(f'brand/ALG0RIDDIMS_wordmark_{name}.png')
        b.close()
except ImportError:
    print('(playwright not installed: PNG app icons and wordmark PNGs skipped)')
