/*
 * ALG0RIDDIMS — alg0_field.js  v3
 * The pattern field as a live, animated sequencer. The still field is identical,
 * bit-for-bit, to alg0_field.py for the same seed / size / cell.
 *
 * Every frame is a pure function of (seed, size, cell, programme, params, step).
 * Nothing reads the clock while rendering, so exports are identical every time.
 *
 *   const f = ALG0.create({ seed: 211126, W: 1080, H: 1350, u: 24, programme: 'NIGHT' });
 *   f.frame(ctx, step, params)   // step = linear 16th-note count from the transport; null = still poster
 *   f.loopFor(params)            // steps in one seamless loop for these params
 *   f.code(step, params, n)      // the "source" lines for the code layer
 *
 * params (all optional, defaults in ALG0.DEFAULTS):
 *   mode   'sweep' | 'poly' | 'drift' | 'rain' | 'auto'   (auto = scene change every sceneBars)
 *   rate   0.5 | 1 | 2          half / normal / double time against the BPM
 *   swing  0..0.6               delays every second 16th
 *   decay  steps a hit takes to fade (1..8)
 *   pulse  0..1                 how much a hit grows
 *   ripple 0..1                 rings that spread from hits
 *   density 0..1                share of hits drawn (deterministic thinning: build-ups)
 *   mutes  { KICK, SNARE, HAT, FX }   true = muted
 *   depth  0..1                 two echo layers of the same seed at 2x and 3x cell, swaying
 *   zoom   0..1                 push on every downbeat (field only: type never moves)
 *   shift  bool                 every 4 bars, a few rows jump sideways and snap back
 *   flash  bool                 downbeat flash on the grid, once per bar (photosensitive-safe rate)
 *   evolve bool                 one row rewritten every editBars bars (live only: never loops)
 */
(function (root) {
  'use strict';
  var INK = '#121212', PAPER = '#F2F1EC', RED = '#FF0033', CYAN = '#00E5FF', GHOST = '#262626';
  var PROGRAMMES = { NIGHT: '#8A00FF', WORKSHOP: '#33FF66', TALK: '#FFB000', STREAM: '#2F5BFF', JAM: '#C8FF00', ARCHIVE: '#B4B1A8' };
  var SHADE = '#DCD9CF';
  // Colourways re-assign the locked palette to the voices. They never add a colour.
  function colourway(name, snare) {
    switch (name) {
      case 'DUO':    return { ground: INK, ghost: GHOST, play: '242,241,236', KICK: RED, SNARE: snare, HAT: snare, FX: RED };
      case 'ACCENT': return { ground: INK, ghost: GHOST, play: '242,241,236', KICK: PAPER, SNARE: snare, HAT: PAPER, FX: PAPER };
      case 'MONO':   return { ground: INK, ghost: GHOST, play: '242,241,236', KICK: PAPER, SNARE: PAPER, HAT: PAPER, FX: PAPER };
      case 'INVERT': return { ground: PAPER, ghost: SHADE, play: '18,18,18', KICK: RED, SNARE: readsOnPaper(snare) ? snare : INK, HAT: INK, FX: INK };
      default:       return { ground: INK, ghost: GHOST, play: '242,241,236', KICK: RED, SNARE: snare, HAT: PAPER, FX: CYAN };
    }
  }
  var COLOURWAYS = ['STANDARD', 'DUO', 'ACCENT', 'MONO', 'INVERT'];
  function lum(h) {
    var c = [1, 3, 5].map(function (i) { var x = parseInt(h.substr(i, 2), 16) / 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); });
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  }
  // a programme colour only stays on a paper ground if it reaches 3:1 against it
  function readsOnPaper(h) { return (lum(PAPER) + 0.05) / (lum(h) + 0.05) >= 3; }
  var VOICES = [
    ['KICK', 0.30, 3, 6, 'dot', RED],
    ['SNARE', 0.30, 3, 5, 'dot', null],
    ['HAT', 0.40, 5, 9, 'bar', PAPER]
  ];
  var LENGTHS = [16, 16, 12, 8];
  var MODES = ['sweep', 'poly', 'drift', 'rain'];
  var DEFAULTS = { colourway: 'STANDARD', mode: 'sweep', rate: 1, swing: 0, decay: 3, pulse: 0.32, ripple: 0, density: 1,
    mutes: {}, depth: 0, zoom: 0, shift: false, flash: false, evolve: false, sceneBars: 8, editBars: 4 };
  var TAU = 6.283185307179586;

  function mulberry32(seed) {
    var s = seed >>> 0;
    return function () {
      s = (s + 0x6D2B79F5) >>> 0;
      var t = s;
      t = Math.imul(t ^ (t >>> 15), t | 1) >>> 0;
      t = (t ^ ((t + (Math.imul(t ^ (t >>> 7), t | 61) >>> 0)) >>> 0)) >>> 0;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function hash3(a, b, c) {
    return mulberry32((a ^ Math.imul(b + 1, 73856093) ^ Math.imul(c + 1, 19349663)) >>> 0)();
  }
  function euclid(k, n) {
    var p = [];
    for (var i = 0; i < n; i++) p.push((i * k) % n < k ? 1 : 0);
    return p;
  }
  function gcd(a, b) { while (b) { var t = b; b = a % b; a = t; } return a; }
  function lcm(a, b) { return a / gcd(a, b) * b; }
  function mod(a, n) { return ((a % n) + n) % n; }

  // The field. Do not change the order of rnd() calls: it is the poster.
  function field(seed, cols, rows, snare) {
    var rnd = mulberry32(seed), out = [], meta = [];
    for (var r = 0; r < rows; r++) {
      var x = rnd(), acc = 0, v = VOICES[0];
      for (var i = 0; i < VOICES.length; i++) {
        v = VOICES[i]; acc += v[1];
        if (x < acc) break;
      }
      var shape = v[4], col = v[0] === 'SNARE' ? snare : v[5];
      var n = LENGTHS[Math.floor(rnd() * LENGTHS.length)];
      var k = Math.min(v[2] + Math.floor(rnd() * (v[3] - v[2] + 1)), n - 1);
      var rot = Math.floor(rnd() * n) + Math.floor(r / 8);
      var pat = euclid(k, n), rr = rot % n;
      if (rr) pat = pat.slice(n - rr).concat(pat.slice(0, n - rr));
      meta.push({ voice: v[0], col: col, k: k, n: n, rot: rr, pat: pat });
      var c = 0;
      while (c < cols) {
        if (pat[c % n]) {
          if (rnd() < 0.035) {
            out.push({ r: r, c: c, shape: 'dot', col: CYAN, L: 1, voice: 'FX' });
          } else if (shape === 'bar') {
            var L = 1 + Math.floor(rnd() * 3), nxt = L + 1;
            for (var j = 1; j <= L; j++) { if (pat[(c + j) % n]) { nxt = j; break; } }
            L = Math.max(1, Math.min(L, nxt, cols - c));
            out.push({ r: r, c: c, shape: 'bar', col: col, L: L, voice: v[0] });
            c += L;
            continue;
          } else {
            out.push({ r: r, c: c, shape: 'dot', col: col, L: 1, voice: v[0] });
          }
        }
        c += 1;
      }
    }
    out.rowsMeta = meta;
    return out;
  }

  function stepAt(seconds, bpm) { return seconds * bpm / 60 * 4; }

  // swing: first 16th of each pair is longer, second shorter
  function swung(t, s) {
    if (!s) return t;
    var pair = Math.floor(t / 2), f = t - pair * 2;
    return f < 1 + s ? pair * 2 + f / (1 + s) : pair * 2 + 1 + (f - 1 - s) / (1 - s);
  }

  function create(o) {
    var W = o.W, H = o.H, u = o.u, seed = o.seed | 0;
    var snare = PROGRAMMES[(o.programme || 'NIGHT').toUpperCase()] || o.programme;

    function layer(cell) {
      var cols = Math.ceil(W / cell), rows = Math.ceil(H / cell);
      var cells = field(seed, cols, rows, snare);
      cells.forEach(function (e) { e.h = hash3(seed, e.r, e.c); });
      return { u: cell, cols: cols, rows: rows, ox: (W - cols * cell) / 2, oy: (H - rows * cell) / 2,
        cells: cells, meta: cells.rowsMeta, loop: Math.ceil(cols / 16) * 16 };
    }
    var front = layer(u), echoes = null;
    function getEchoes() {
      if (!echoes) echoes = [
        { L: layer(u * 3), alpha: 0.16, sway: 0.6 },
        { L: layer(u * 2), alpha: 0.30, sway: 1.2 }
      ];
      return echoes;
    }
    var L0 = front.loop;
    var polyLoop = front.meta.reduce(function (a, m) { return lcm(a, m.n); }, 1);

    function P(p) {
      var q = {}, k;
      for (k in DEFAULTS) q[k] = DEFAULTS[k];
      for (k in (p || {})) if (p[k] !== undefined) q[k] = p[k];
      q.mutes = q.mutes || {};
      return q;
    }
    function modeAt(pos, p) {
      if (p.mode !== 'auto') return p.mode;
      return MODES[Math.floor(pos / (16 * p.sceneBars)) % MODES.length];
    }
    function loopFor(params) {
      var p = P(params), steps;
      if (p.mode === 'auto') steps = 16 * p.sceneBars * MODES.length;
      else steps = p.mode === 'poly' ? lcm(L0, polyLoop) : L0;
      if (p.shift) steps = lcm(steps, 64);
      if (p.zoom || p.flash) steps = lcm(steps, 16);
      if (p.swing) steps = lcm(steps, 2);
      return steps / p.rate;                     // transport steps (before rate)
    }

    // live edit (never in exports)
    var cache = {};
    function frontAt(edit, p) {
      if (!p.evolve || edit <= 0) return front.cells;
      if (cache[edit]) return cache[edit];
      var prev = frontAt(edit - 1, p);
      var pick = Math.floor(mulberry32(seed ^ Math.imul(edit, 2654435761))() * front.rows);
      var fresh = field(seed + edit, front.cols, front.rows, snare).filter(function (e) { return e.r === pick; });
      fresh.forEach(function (e) { e.h = hash3(seed, e.r, e.c); });
      var next = prev.filter(function (e) { return e.r !== pick; }).concat(fresh);
      cache[edit] = next;
      var keys = Object.keys(cache);
      if (keys.length > 8) delete cache[keys[0]];
      return next;
    }

    function hitPhase(mode, Lr, e, pos, meta) {
      var Ls = Lr.loop, cols = Lr.cols;
      if (mode === 'poly') { var n = meta[e.r].n; return { ph: mod(pos - (e.c % n), n) }; }
      if (mode === 'rain') return { ph: mod(pos - e.r * Ls / Lr.rows, Ls) };
      if (mode === 'drift') { var kc = cols / Ls, pc = Math.floor(cols / 2); return { ph: mod(pos - (e.c - pc) / kc, Ls) }; }
      return { ph: mod(pos - e.c, Ls) };
    }

    function roundRect(ctx, x, y, w, h, r) {
      ctx.beginPath();
      ctx.moveTo(x + r, y); ctx.lineTo(x + w - r, y); ctx.arc(x + w - r, y + r, r, -1.5708, 1.5708);
      ctx.lineTo(x + r, y + h); ctx.arc(x + r, y + r, r, 1.5708, 4.7124); ctx.closePath();
    }

    function drawCells(ctx, Lr, cells, pos, mode, p, opt) {
      var map = opt.map;
      var cu = Lr.u, cols = Lr.cols, bar = Math.floor(pos / 16), barPh = mod(pos, 16);
      var kc = cols / Lr.loop;
      var shiftEnv = (p.shift && bar % 4 === 0 && barPh < 4) ? Math.pow(1 - barPh / 4, 2) : 0;
      cells.forEach(function (e) {
        if (p.mutes[e.voice] || e.h > p.density) return;
        var cx = e.c;
        if (pos != null && mode === 'drift') cx = mod(e.c - pos * kc, cols);
        if (shiftEnv && opt.front) {
          var hr = hash3(seed + bar, e.r, 7);
          if (hr < 0.14) cx += Math.round((hash3(seed + bar, e.r, 9) - 0.5) * 10) * shiftEnv;
        }
        var x = Lr.ox + cx * cu + opt.dx, y = Lr.oy + e.r * cu + opt.dy, f = 0;
        if (pos != null) {
          var ph = hitPhase(mode, Lr, e, pos, Lr.meta).ph;
          f = ph < p.decay ? Math.pow(1 - ph / p.decay, 2) : 0;
        }
        var g = p.pulse * f, col = map[e.voice];
        ctx.fillStyle = col;
        if (e.shape === 'dot') {
          var rad = cu * 0.39 * (1 + g);
          ctx.beginPath(); ctx.arc(x + cu / 2, y + cu / 2, rad, 0, TAU); ctx.fill();
          if (p.ripple && f > 0 && opt.front) {
            ctx.save();
            ctx.globalAlpha = opt.alpha * f * 0.8;
            ctx.strokeStyle = col; ctx.lineWidth = cu * 0.06;
            ctx.beginPath(); ctx.arc(x + cu / 2, y + cu / 2, cu * 0.39 * (1 + (1 - f) * 2.4 * p.ripple), 0, TAU); ctx.stroke();
            ctx.restore();
          }
        } else {
          var hgt = cu * (0.36 + 0.81 * g), w = e.L * cu - cu * 0.18;
          roundRect(ctx, x + cu * 0.09, y + (cu - hgt) / 2, w, hgt, hgt / 2); ctx.fill();
        }
      });
    }

    // step: linear transport steps (null = still poster)
    function frame(ctx, step, params) {
      var p = P(params);
      var pos = step == null ? null : swung(step * p.rate, p.swing);
      var mode = pos == null ? 'sweep' : modeAt(pos, p);
      var barPh = pos == null ? 99 : mod(pos, 16);
      var map = colourway(p.colourway, snare);
      ctx.save();
      ctx.fillStyle = map.ground; ctx.fillRect(0, 0, W, H);

      var zk = pos == null ? 0 : p.zoom * 0.035 * Math.pow(Math.max(0, 1 - barPh / 4), 2);
      if (zk) { ctx.translate(W / 2, H / 2); ctx.scale(1 + zk, 1 + zk); ctx.translate(-W / 2, -H / 2); }

      // depth: echo layers behind, same seed at bigger cells, swaying on a loop-length sine
      if (p.depth > 0) {
        var Lp = loopFor(p) * p.rate, ang = pos == null ? 0 : TAU * pos / Lp;
        getEchoes().forEach(function (E) {
          ctx.save(); ctx.globalAlpha = E.alpha * p.depth;
          drawCells(ctx, E.L, E.L.cells, pos == null ? null : pos * E.L.loop / front.loop, 'sweep', p,
            { dx: Math.sin(ang) * E.sway * u, dy: Math.cos(ang) * E.sway * u * 0.5, front: false, alpha: 1, map: map });
          ctx.restore();
        });
      }

      var cells = pos == null ? front.cells : frontAt(Math.floor(pos / (16 * p.editBars)), p);
      var cols = front.cols, rows = front.rows;
      // ghost grid (skipped under hits)
      var filled = {};
      cells.forEach(function (e) {
        if (p.mutes[e.voice] || e.h > p.density) return;
        for (var i = 0; i < e.L; i++) filled[e.r * 4096 + e.c + i] = 1;
      });
      var flashA = (p.flash && pos != null && barPh < 2) ? 0.45 * Math.pow(1 - barPh / 2, 2) : 0;
      var still = pos == null || mode !== 'drift';
      for (var r = 0; r < rows; r++) for (var c = 0; c < cols; c++) {
        if (still && filled[r * 4096 + c]) continue;
        var gx = front.ox + c * u + u / 2, gy = front.oy + r * u + u / 2;
        ctx.fillStyle = map.ghost; ctx.beginPath(); ctx.arc(gx, gy, u * 0.12, 0, TAU); ctx.fill();
        if (flashA) { ctx.globalAlpha = flashA; ctx.fillStyle = map.ground === PAPER ? INK : PAPER; ctx.beginPath(); ctx.arc(gx, gy, u * 0.12, 0, TAU); ctx.fill(); ctx.globalAlpha = 1; }
      }

      // playheads
      if (pos != null) {
        ctx.fillStyle = 'rgba(' + map.play + ',0.07)';
        if (mode === 'sweep') ctx.fillRect(front.ox + Math.floor(mod(pos, front.loop)) * u, 0, u, H);
        else if (mode === 'drift') ctx.fillRect(front.ox + Math.floor(cols / 2) * u, 0, u, H);
        else if (mode === 'rain') ctx.fillRect(0, front.oy + Math.floor(mod(pos, front.loop) / front.loop * rows) * u, W, u);
        else if (mode === 'poly') {
          ctx.fillStyle = 'rgba(' + map.play + ',0.35)';
          front.meta.forEach(function (m, rr) {
            var s = Math.floor(mod(pos, m.n));
            for (var cc = s; cc < cols; cc += m.n) ctx.fillRect(front.ox + cc * u + u * 0.2, front.oy + rr * u + u * 0.9, u * 0.6, u * 0.06);
          });
        }
      }

      drawCells(ctx, front, cells, pos, mode, p, { dx: 0, dy: 0, front: true, alpha: 1, map: map });
      ctx.restore();
      return { mode: mode, pos: pos, ground: map.ground };
    }

    return { frame: frame, draw: function (ctx, step) { return frame(ctx, step, {}); }, loopFor: loopFor,
      cells: front.cells, meta: front.meta, cols: front.cols, rows: front.rows, ox: front.ox, oy: front.oy,
      loopSteps: front.loop, snare: snare };
  }

  // A "look" is every non-locked variable, derived from a 16-bit look code.
  // Same code, same look, on any machine. Never touches seed, programme, text, palette or layout.
  // Never switches flash or live edit on, and never picks INVERT (print/daytime only).
  function deriveLook(code) {
    var rnd = mulberry32((code & 0xFFFF) * 2654435761 >>> 0);
    var pick = function (xs) { return xs[Math.floor(rnd() * xs.length)]; };
    var range = function (a, b, step) { var v = a + rnd() * (b - a); return Math.round(v / step) * step; };
    var maybe = function (p, f, off) { return rnd() < p ? f() : off; };
    var look = {
      colourway: pick(['STANDARD', 'STANDARD', 'STANDARD', 'STANDARD', 'DUO', 'ACCENT', 'MONO']),
      mode: pick(['sweep', 'poly', 'poly', 'drift', 'rain', 'auto']),
      rate: pick([0.5, 1, 1, 1, 2]),
      swing: maybe(0.35, function () { return range(0.1, 0.5, 0.01); }, 0),
      decay: range(1.5, 6, 0.5),
      pulse: range(0.15, 0.8, 0.01),
      ripple: maybe(0.5, function () { return range(0.3, 1, 0.01); }, 0),
      density: maybe(0.4, function () { return range(0.55, 0.95, 0.01); }, 1),
      depth: maybe(0.6, function () { return range(0.3, 1, 0.01); }, 0),
      zoom: maybe(0.5, function () { return range(0.2, 0.8, 0.01); }, 0),
      shift: rnd() < 0.3,
      sceneBars: pick([4, 8, 8, 16]),
      mutes: {}, flash: false, evolve: false
    };
    ['HAT', 'FX'].forEach(function (v) { if (rnd() < 0.12) look.mutes[v] = true; });
    return look;
  }
  function lookHex(code) { return ('000' + (code & 0xFFFF).toString(16).toUpperCase()).slice(-4); }

  var api = { create: create, deriveLook: deriveLook, lookHex: lookHex, COLOURWAYS: COLOURWAYS, colourway: colourway, readsOnPaper: readsOnPaper, field: field, mulberry32: mulberry32, euclid: euclid, stepAt: stepAt, swung: swung,
    PROGRAMMES: PROGRAMMES, DEFAULTS: DEFAULTS, MODES: MODES };
  root.ALG0 = api;                                   // always: pages read window.ALG0
  if (typeof module !== 'undefined' && module.exports) module.exports = api;   // node: tests, scripts
})(typeof window !== 'undefined' ? window : this);
