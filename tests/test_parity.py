#!/usr/bin/env python3
"""
Print and screen must draw the same field. This checks that generator/alg0_field.py
and player/alg0_field.js produce identical cells for the same seed and grid, and
agree on which programme colours read on a paper ground (the INVERT rule).

usage:  python3 tests/test_parity.py        (needs node on PATH)
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'generator'))
import alg0_field as G  # noqa: E402

CASES = [(211126, 45, 57), (211126, 46, 65), (120327, 30, 30), (300427, 30, 30), (51226, 80, 45), (140127, 45, 57)]

js = r"""
const A = require(process.argv[1]);
const cases = JSON.parse(process.argv[2]);
const out = {};
for (const [seed, cols, rows] of cases)
  out[`${seed}_${cols}_${rows}`] = A.field(seed, cols, rows, '#8A00FF').map(e => [e.r, e.c, e.shape, e.col, e.L]);
out.paper = Object.fromEntries(Object.entries(A.PROGRAMMES).map(([k, v]) => [k, A.readsOnPaper(v)]));
console.log(JSON.stringify(out));
"""
res = subprocess.run(['node', '-e', js, str(ROOT / 'player' / 'alg0_field.js'), json.dumps(CASES)],
                     capture_output=True, text=True, check=True)
got = json.loads(res.stdout)

fails = 0
for seed, cols, rows in CASES:
    key = f'{seed}_{cols}_{rows}'
    py = [list(c) for c in G.field(seed, cols, rows)]
    ok = py == got[key]
    fails += not ok
    print(f'{"ok  " if ok else "FAIL"} field {key}: {len(py)} cells')

for k, v in G.PROGRAMMES.items():
    ok = G.reads_on_paper(v) == got['paper'][k]
    fails += not ok
    print(f'{"ok  " if ok else "FAIL"} reads-on-paper {k}: {G.reads_on_paper(v)}')

missing = set(G.PROGRAMMES) ^ set(got['paper'])
if missing:
    fails += 1
    print('FAIL programmes differ:', missing)

print('\nall checks passed' if not fails else f'\n{fails} check(s) failed')
sys.exit(1 if fails else 0)
