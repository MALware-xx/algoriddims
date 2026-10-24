#!/usr/bin/env python3
"""
ALG0RIDDIMS — pattern field generator  (alg0.field)
The artwork is made by the same process as the event: a seeded step sequencer.

  seed   = event date as DDMMYY (001 = 211126). Same seed -> same artwork, always.
  rows   = sequencer tracks. Each row is a Euclidean rhythm E(k, n), rotated.
  voices = KICK (red dots) · SNARE (violet dots) · HAT (paper bars) · FX (cyan, rare)
  drift  = every 8 rows the rotation steps on by one: the pattern is "edited live"
           as you read down the page.

PRNG is mulberry32 so a JS port reproduces the same field bit-for-bit.

usage:  python3 alg0_field.py SEED WIDTH HEIGHT CELL out.svg [PROGRAMME] [COLOURWAY]
        python3 alg0_field.py 211126 1080 1350 24 field_001.svg
        python3 alg0_field.py 140127 1080 1350 24 workshop.svg WORKSHOP

PROGRAMME sets the snare voice (the programme colour): NIGHT (default) ·
WORKSHOP · TALK · STREAM · JAM · ARCHIVE, or a 6-digit hex for a guest/collab colour.
COLOURWAY re-assigns the locked palette: STANDARD (default) · DUO · ACCENT · MONO · INVERT
(INVERT = paper ground for riso and daytime print).
KICK red, HAT paper and FX cyan never change: they are the series.
"""
import sys

INK, PAPER = '#121212', '#F2F1EC'
RED, VIOLET, CYAN = '#FF0033', '#8A00FF', '#00E5FF'
GHOST = '#262626'          # empty step: the grid you can just about see
PROGRAMMES = {'NIGHT': '#8A00FF', 'WORKSHOP': '#33FF66', 'TALK': '#FFB000', 'STREAM': '#2F5BFF',
              'JAM': '#C8FF00', 'ARCHIVE': '#B4B1A8'}
SHADE = '#DCD9CF'


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def reads_on_paper(h):  # programme colour stays on a paper ground only at 3:1 or better
    return (lum(PAPER) + 0.05) / (lum(h) + 0.05) >= 3


def colourway(name, snare):
    # ground, ghost, KICK, SNARE, HAT, FX
    return {
        'DUO':    (INK, GHOST, RED, snare, snare, RED),
        'ACCENT': (INK, GHOST, PAPER, snare, PAPER, PAPER),
        'MONO':   (INK, GHOST, PAPER, PAPER, PAPER, PAPER),
        'INVERT': (PAPER, SHADE, RED, snare if reads_on_paper(snare) else INK, INK, INK),
    }.get(name, (INK, GHOST, RED, snare, PAPER, CYAN))


def mulberry32(seed):
    s = seed & 0xFFFFFFFF
    def rnd():
        nonlocal s
        s = (s + 0x6D2B79F5) & 0xFFFFFFFF
        t = s
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return rnd


def euclid(k, n):
    """Bjorklund via the bresenham form: k onsets spread over n steps."""
    return [1 if (i * k) % n < k else 0 for i in range(n)]


VOICES = [  # name, weight, (kmin, kmax), shape, colour
    ('KICK',  0.30, (3, 6), 'dot', RED),
    ('SNARE', 0.30, (3, 5), 'dot', VIOLET),
    ('HAT',   0.40, (5, 9), 'bar', PAPER),
]
LENGTHS = [16, 16, 12, 8]       # polymeter: rows drift against each other


def field(seed, cols, rows, snare=VIOLET):
    rnd = mulberry32(seed)
    pick = lambda xs: xs[int(rnd() * len(xs))]
    grid = []      # (row, col, shape, colour, length)
    for r in range(rows):
        x = rnd()
        acc = 0
        for name, w, (kmin, kmax), shape, col in VOICES:
            acc += w
            if x < acc:
                break
        if name == 'SNARE':
            col = snare
        n = pick(LENGTHS)
        k = min(kmin + int(rnd() * (kmax - kmin + 1)), n - 1)
        rot = int(rnd() * n) + r // 8                 # drift
        pat = euclid(k, n)
        pat = pat[-(rot % n):] + pat[:-(rot % n)] if rot % n else pat
        c = 0
        while c < cols:
            if pat[c % n]:
                if rnd() < 0.035:                     # FX: rare cyan hit
                    grid.append((r, c, 'dot', CYAN, 1))
                elif shape == 'bar':
                    L = 1 + int(rnd() * 3)
                    nxt = next((j for j in range(1, L + 1) if pat[(c + j) % n]), L + 1)
                    L = max(1, min(L, nxt, cols - c))
                    grid.append((r, c, 'bar', col, L))
                    c += L
                    continue
                else:
                    grid.append((r, c, 'dot', col, 1))
            c += 1
    return grid


def svg(seed, W, H, u, snare=VIOLET, cway='STANDARD'):
    cols, rows = -(-W // u), -(-H // u)
    ox, oy = (W - cols * u) / 2, (H - rows * u) / 2
    g = field(seed, cols, rows, snare)
    filled = {(r, c + i) for r, c, s, col, L in g for i in range(L)}
    ground, ghost, ck, cs, ch, cf = colourway(cway, snare)
    remap = {RED: ck, snare: cs, PAPER: ch, CYAN: cf}
    g = [(r, c, s, remap[col], L) for r, c, s, col, L in g]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="{ground}"/>']
    gr = u * 0.12
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in filled:
                out.append(f'<circle cx="{ox+c*u+u/2:.1f}" cy="{oy+r*u+u/2:.1f}" r="{gr:.1f}" fill="{ghost}"/>')
    area = {}
    for r, c, shape, col, L in g:
        x, y = ox + c * u, oy + r * u
        if shape == 'dot':
            out.append(f'<circle cx="{x+u/2:.1f}" cy="{y+u/2:.1f}" r="{u*0.39:.1f}" fill="{col}"/>')
            area[col] = area.get(col, 0) + 3.14159 * (u * 0.39) ** 2
        else:
            h = u * 0.36
            w = L * u - u * 0.18
            out.append(f'<rect x="{x+u*0.09:.1f}" y="{y+(u-h)/2:.1f}" width="{w:.1f}" height="{h:.1f}" '
                       f'rx="{h/2:.1f}" fill="{col}"/>')
            area[col] = area.get(col, 0) + w * h
    out.append('</svg>')
    tot = W * H
    share = {k: round(100 * v / tot, 1) for k, v in area.items()}
    share['GROUND'] = round(100 - sum(share.values()), 1)
    return '\n'.join(out), share


if __name__ == '__main__':
    seed, W, H, u, path = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    prog = sys.argv[6].upper() if len(sys.argv) > 6 else 'NIGHT'
    snare = PROGRAMMES.get(prog) or ('#' + prog.lstrip('#'))
    cway = sys.argv[7].upper() if len(sys.argv) > 7 else 'STANDARD'
    s, share = svg(seed, W, H, u, snare, cway)
    open(path, 'w').write(s)
    print(path, cway, share)
