#!/usr/bin/env python3
"""Build dist/alg0_player.html: inline the Plex Mono fonts and the field engine into player/alg0_player.html.in.

usage:  python3 scripts/build_player.py
"""
import base64, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def b64(name):
    return base64.b64encode((ROOT / 'fonts' / name).read_bytes()).decode()


src = (ROOT / 'player' / 'alg0_player.html.in').read_text()
out = (src.replace('__FONT_BOLD__', b64('IBMPlexMono-Bold.woff2'))
          .replace('__FONT_REG__', b64('IBMPlexMono-Regular.woff2'))
          .replace('__ALG0JS__', (ROOT / 'player' / 'alg0_field.js').read_text()))
assert '__' + 'FONT' not in out and '__ALG0JS__' not in out
dest = ROOT / 'dist' / 'alg0_player.html'
dest.write_text(out)
print(f'{dest.relative_to(ROOT)}  {len(out) // 1024} KB')
