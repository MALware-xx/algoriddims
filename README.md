# ALG0RIDDIMS_

Identity and visual tools for **ALGORIDDIMS**, Bristol live-code: music and visuals written live.
**001** · Sat 21 Nov 2026 · 19:00–23:00 · Hamilton House, above the Canteen.

The artwork is made the way the night is made, with code. Every pattern is a step sequencer drawn
as a grid, grown from the event date. The poster, the projector and the print all draw the same field.

## Start here

| You want to | Use |
| --- | --- |
| Make a poster, story or projector loop | Open `dist/alg0_player.html` in Chrome, set the event, then Export (PNG, PDF or MP4) |
| The logo | `brand/` (outlined SVG and PNG wordmarks, micro mark, favicons) |
| The rules | `dist/ALG0RIDDIMS_Identity_v0.5.pdf` |
| A vector field for print | `python3 generator/alg0_field.py 211126 1240 1754 27 field.svg NIGHT STANDARD` |
| The field in VJinA | `player/alg0_field.js` (see below) |

## Layout

```
generator/   alg0_field.py: the field as vector SVG (print). Programme and colourway arguments.
player/      alg0_field.js: the same field, animated, with colourways and look codes.
             player.src.html: the player template.
dist/        Built files: alg0_player.html (fonts and engine inlined) and the identity PDF.
brand/       Logo files, made from Plex Mono Bold's own outlines.
identity/    identity.src.html: source of the guidelines PDF.
scripts/     build_player.py, make_marks.py, build_identity.py, render_loop.py
tests/       test_parity.py: Python and JavaScript must draw the same field, cell for cell.
fonts/       IBM Plex Mono Bold and Regular, Plex Sans Regular, and their licence.
```

## Build

```sh
pip3 install -r requirements.txt
python3 -m playwright install chromium
brew install ffmpeg                    # only for scripts/render_loop.py

python3 scripts/build_player.py        # -> dist/alg0_player.html
python3 scripts/make_marks.py          # -> brand/
python3 scripts/build_identity.py      # -> dist/ALG0RIDDIMS_Identity_v0.5.pdf
python3 tests/test_parity.py           # needs node
```

Edit `player/player.src.html` or `player/alg0_field.js`, never `dist/alg0_player.html`: it is rebuilt.
If you change the field logic, change it in both `generator/alg0_field.py` and `player/alg0_field.js`
and run the parity test. The order of random-number calls in `field()` is the artwork; changing it
changes every poster.

## The rules that keep it one system

- **Seed = event date, DDMMYY.** 001 is `211126`. Same seed, size and cell always give the same field.
- **One cell per format.** Poster 1080×1350 and square 1080×1080: 24 px. Story 1080×1920: 24 px.
  VJ 1920×1080: 40 px. A-ratio print 1240×1754: 27 px. Render each format; never resize one into another.
- **The mark is typed:** `ALG0RIDDIMS_` in IBM Plex Mono Bold, tracking 0, Plex's own dotted zero.
  Minimum 20 px type on screen, 30 mm wide in print; micro mark `0_` at least 32 px.
- **Locked:** seed, programme, event text, palette, layout. **Variable:** the look, by hand or with
  Randomise. A look is a four-character code (for example `12A7`) that gives the same look anywhere.
- **Palette:** Ink `#121212`, Paper `#F2F1EC`, Kick Red `#FF0033`, FX Cyan `#00E5FF`, plus one
  programme colour in the snare slot: NIGHT `#8A00FF`, WORKSHOP `#33FF66`, TALK `#FFB000`,
  STREAM `#2F5BFF`, JAM `#C8FF00`, ARCHIVE `#B4B1A8`.

## Batch exports

The player exports by itself. For batches, from the repo folder:

```sh
python3 scripts/render_loop.py 211126 NIGHT 140 poster 1 poster.mp4 '{"look":"12A7"}'
python3 scripts/render_loop.py 211126 NIGHT 140 poster 0 poster.png '{"setlist":["19:00 NAME","20:00 NAME"]}'
```

In the player, Export → Command line instead → Copy gives the exact command for what is on screen.

## Using the field in VJinA

`player/alg0_field.js` has no dependencies. Every frame is a pure function of the step number,
so drive it from VJinA's own BPM clock:

```js
const f = ALG0.create({ seed: 211126, W: 1920, H: 1080, u: 40, programme: 'NIGHT' });
// each frame:
f.frame(ctx, ALG0.stepAt(seconds, bpm), { ...ALG0.deriveLook(0x12A7) });
```

## Licences

Fonts: IBM Plex, SIL Open Font License 1.1 (`fonts/OFL.txt`). "Plex" is a reserved font name, so
the fonts here are unmodified. Code and artwork: no licence chosen yet, so all rights are reserved
until one is added.
