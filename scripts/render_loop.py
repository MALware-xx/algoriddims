#!/usr/bin/env python3
"""
ALG0RIDDIMS — render a seamless video loop from the field player.
Frames are rendered by step number (not recorded in real time), so every export
is identical and the last frame joins the first.

setup (once):  pip3 install playwright && python3 -m playwright install chromium
               brew install ffmpeg
usage:         python3 render_loop.py [SEED] [PROGRAMME] [BPM] [FORMAT] [LOOPS] [out.mp4] ['PARAMS JSON']
example:       python3 render_loop.py 211126 NIGHT 140 poster 1 alg0_001_poster.mp4
               python3 render_loop.py 211126 NIGHT 140 vj 1 vj_3A7F.mp4 '{"look":"3A7F"}'
               python3 render_loop.py 211126 NIGHT 140 poster 0 poster_001.png '{"setlist":["19:00 NAME ONE","20:00 NAME TWO"]}'
The player can now export PNG, PDF and MP4 itself (Export panel). Use this script for batches.
In the player: Export → Command line instead → Copy, then run it from the repo root.
FORMAT: poster | square | story | vj      LOOPS: how many seamless loops to render (0 = still PNG)
PARAMS: "look": "3A7F" (a look code) and/or any look setting (colourway, mode, rate, swing,
        decay, pulse, ripple, density, mutes, depth, zoom, shift, flash, sceneBars); event text
        "text": {sub, time, p1, p2, entry}, "setlist": [...], "strap": [...]; "type": false hides type.
        The loop length is worked out from the settings so the file always joins up.
Renders with dist/alg0_player.html (run scripts/build_player.py first).
"""
import sys, os, subprocess, tempfile, shutil, pathlib
from playwright.sync_api import sync_playwright

import json
a = sys.argv[1:] + [None] * 7
seed = int(a[0] or 211126); prog = (a[1] or 'NIGHT').upper(); bpm = int(a[2] or 140)
fmt = a[3] or 'poster'; loops = int(a[4] or 1); out = a[5] or f'alg0_{seed}_{prog}_{fmt}.mp4'
params = json.loads(a[6]) if a[6] else {}
FPS = 30
here = pathlib.Path(__file__).resolve().parent
tmp = tempfile.mkdtemp()
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto((here.parent / 'dist' / 'alg0_player.html').as_uri()); pg.wait_for_timeout(600)
    info = pg.evaluate("o => ALG0PLAYER.setup(o)", {'seed': seed, 'programme': prog, 'bpm': bpm, 'format': fmt, 'params': params})
    W, H, L = info['W'], info['H'], info['loopSteps']
    pg.set_viewport_size({'width': W, 'height': H}); pg.wait_for_timeout(300)
    if loops == 0:                                   # still poster, no motion
        pg.evaluate('ALG0PLAYER.still()'); pg.wait_for_timeout(100)
        pg.locator('#stage').screenshot(path=out); b.close()
        print(f'{out}  {W}x{H}  still  seed {seed} {prog}'); sys.exit(0)
    seconds = L * 60 / (bpm * 4) * loops
    n = round(seconds * FPS)
    stage = pg.locator('#stage')
    for i in range(n):
        pg.evaluate(f'ALG0PLAYER.frame({i * L * loops / n})')
        stage.screenshot(path=f'{tmp}/f{i:05d}.png')
    b.close()
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{tmp}/f%05d.png',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-movflags', '+faststart', out], check=True)
shutil.rmtree(tmp)
print(f'{out}  {W}x{H}  {n} frames  {seconds:.2f}s  seed {seed} {prog} {bpm} BPM')
