#!/usr/bin/env python3
"""Generate assets/card-video.svg and assets/card-search.svg.

Two animated 2:1 cards for the README's "Systems that grow" grid, drawn in the banner's
language: mono prompt line, GitHub dark palette, the green-to-purple line along the bottom.
Dark only, like the two site cards they sit beside. SMIL runs inside <img> on github.com.
No figures on either card: they show how each system works, not what it scored.

    python3 assets/make_cards.py            # the two animated cards
    python3 assets/make_cards.py --stills   # also finished frames in preview/, for screenshots
"""
import math
import random
import sys
from pathlib import Path

C = dict(bg="#0d1117", bg2="#161b22", lane="#131820", border="#30363d", line="#21262d",
         fg="#f0f6fc", muted="#9198a1", faint="#6e7681", accent="#3fb950", accent2="#a371f7")
W, H = 1280, 640
T = 10.0            # seconds per loop, same as the banner's curve
OUT = 9.2           # everything fades together from here to T
STATIC = False      # True draws the finished frame with no animation


def k(t):
    return f"{max(0.0, min(1.0, t / T)):.4f}"


def appear(t, dur=0.25):
    return (f'<animate attributeName="opacity" values="0;0;1;1;0" '
            f'keyTimes="0;{k(t)};{k(t + dur)};{k(OUT)};1" dur="{T:g}s" repeatCount="indefinite"/>')


def el(tag, attrs, t=None, inner="", dur=0.25):
    """One element that fades in at second t of the loop (or is simply there in a still).

    The element itself is drawn finished and the animation takes it down to nothing first, so
    anything that shows the file without running it still gets the complete picture.
    """
    if t is None or STATIC:
        return f"<{tag} {attrs}>{inner}</{tag}>"
    return f'<{tag} {attrs}>{inner}{appear(t, dur)}</{tag}>'


def grow(attr, full, t0, t1):
    """Animate a length from 0 to full between t0 and t1, then hold."""
    if STATIC:
        return ""
    return (f'<animate attributeName="{attr}" values="0;0;{full};{full};0" '
            f'keyTimes="0;{k(t0)};{k(t1)};{k(OUT)};1" dur="{T:g}s" repeatCount="indefinite"/>')


def frame(body, label):
    cells, rnd = [], random.Random(5)
    for col in range(100):
        for row in range(46):
            if rnd.random() < 0.93:
                continue
            cells.append(f'<rect x="{34 + col * 12.2:.1f}" y="{28 + row * 13}" width="8" height="8" rx="2" fill="{C["line"]}"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["bg"]}"/><stop offset="1" stop-color="{C["bg2"]}"/></linearGradient>
  <linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["accent"]}"/><stop offset="1" stop-color="{C["accent2"]}"/></linearGradient>
  <style>
    text{{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;letter-spacing:-0.3px}}
    @media (max-width:240px){{ .lbl{{display:none}} }}
  </style>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<g>{"".join(cells)}</g>
{body}
<rect x="0" y="{H - 7}" width="{W}" height="7" fill="url(#line)"/>
</svg>'''


def caption(text):
    return (f'<text class="lbl" x="64" y="106" font-size="40" fill="{C["fg"]}">'
            f'<tspan fill="{C["accent"]}" font-weight="700">&gt;</tspan> {text}</text>')


def check(x, y, t):
    return el("path", f'd="M{x},{y} l8,8 l15,-17" fill="none" stroke="{C["accent"]}" stroke-width="5.5" '
                      f'stroke-linecap="round" stroke-linejoin="round"', t)


# ---------------------------------------------------------------------------- video pipeline
def video():
    """A brief becomes a timeline; the playhead renders it; both aspect ratios fill and tick."""
    X0, X1 = 262, 794                      # clip area inside the lanes
    lanes = [("script", 176), ("voice", 264), ("picture", 352), ("captions", 440)]
    LH = 64
    T_PLAY0, T_PLAY1 = 3.4, 7.0
    out = [caption("one brief in, every cut out")]

    for name, y in lanes:
        out.append(f'<rect x="250" y="{y}" width="556" height="{LH}" rx="10" fill="{C["lane"]}" stroke="{C["line"]}" stroke-width="2"/>')
        out.append(f'<text class="lbl" x="64" y="{y + 43}" font-size="32" fill="{C["muted"]}">{name}</text>')

    # script: three blocks of text
    y = lanes[0][1] + 10
    for i, (x, w) in enumerate([(262, 150), (424, 196), (632, 128)]):
        inner = (f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="8" fill="{C["line"]}" stroke="{C["border"]}" stroke-width="2"/>'
                 f'<rect x="{x + 14}" y="{y + 13}" width="{w * 0.62:.0f}" height="5" rx="2.5" fill="{C["faint"]}"/>'
                 f'<rect x="{x + 14}" y="{y + 26}" width="{w * 0.40:.0f}" height="5" rx="2.5" fill="{C["faint"]}"/>')
        out.append(el("g", "", 0.4 + i * 0.22, inner))

    # voice: a waveform that arrives left to right
    cy, rnd, bars = lanes[1][1] + LH / 2, random.Random(3), []
    n = (X1 - X0) // 12
    for i in range(n):
        env = 0.35 + 0.65 * abs(math.sin(i * 0.37 + 0.6)) * abs(math.sin(i * 0.11 + 1.1))
        h = max(6.0, 50 * env * rnd.uniform(0.55, 1.0))
        bars.append(el("rect", f'x="{X0 + i * 12}" y="{cy - h / 2:.1f}" width="6" height="{h:.1f}" rx="3" fill="{C["accent"]}"',
                       1.2 + i * 0.016, dur=0.12))
    out.append(f'<g>{"".join(bars)}</g>')

    # picture: four shots
    y = lanes[2][1] + 8
    for i, (x, w) in enumerate([(262, 118), (388, 150), (546, 104), (658, 136)]):
        inner = (f'<rect x="{x}" y="{y}" width="{w}" height="48" rx="8" fill="{C["accent2"]}" fill-opacity="{0.20 + 0.07 * (i % 2):.2f}" stroke="{C["accent2"]}" stroke-opacity="0.75" stroke-width="2"/>'
                 f'<path d="M{x + 14},{y + 36} l{w * 0.22:.0f},-16 l{w * 0.16:.0f},10 l{w * 0.2:.0f},-18 l{w * 0.24:.0f},24" fill="none" stroke="{C["accent2"]}" stroke-opacity="0.9" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
        out.append(el("g", "", 2.1 + i * 0.2, inner))

    # captions: short pills
    y, x, rnd, i = lanes[3][1] + 22, X0, random.Random(8), 0
    while True:
        w = rnd.choice([30, 44, 58, 36, 66])
        if x + w > X1:
            break
        out.append(el("rect", f'x="{x}" y="{y}" width="{w}" height="20" rx="10" fill="{C["muted"]}" fill-opacity="0.6"', 2.9 + i * 0.035, dur=0.12))
        x += w + 10
        i += 1

    # playhead
    travel = X1 - X0
    head = (f'<line x1="{X0}" y1="158" x2="{X0}" y2="522" stroke="{C["fg"]}" stroke-width="3"/>'
            f'<path d="M{X0 - 10},146 h20 v8 l-10,10 l-10,-10 z" fill="{C["fg"]}"/>')
    if STATIC:
        out.append(f'<g transform="translate({travel} 0)">{head}</g>')
    else:
        out.append(f'<g transform="translate({travel} 0)">{head}'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{travel} 0;{travel} 0" keyTimes="0;{k(T_PLAY0)};{k(T_PLAY1)};1" dur="{T:g}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{k(T_PLAY0 - 0.25)};{k(T_PLAY0)};{k(OUT)};1" dur="{T:g}s" repeatCount="indefinite"/></g>')

    # the two cuts, filling as the playhead moves
    def cut(cid, x, y, w, h, t_done):
        stroke = "" if STATIC else (f'<animate attributeName="stroke" values="{C["border"]};{C["border"]};{C["accent"]};{C["accent"]};{C["border"]}" '
                                    f'keyTimes="0;{k(T_PLAY1)};{k(t_done)};{k(OUT)};1" dur="{T:g}s" repeatCount="indefinite"/>')
        px, py, s = x + w / 2, y + h / 2, min(w, h) * 0.17
        return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/></clipPath>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{C["lane"]}"/>'
                f'<rect clip-path="url(#{cid})" x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#line)" fill-opacity="0.30">{grow("width", w, T_PLAY0, T_PLAY1)}</rect>'
                f'<path d="M{px - s * 0.8:.1f},{py - s:.1f} L{px + s:.1f},{py:.1f} L{px - s * 0.8:.1f},{py + s:.1f} Z" fill="{C["fg"]}" fill-opacity="0.55"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{C["accent"]}" stroke-width="3">{stroke}</rect>')
    out.append(cut("c169", 872, 176, 344, 193.5, 7.25))
    out.append(cut("c916", 872, 398, 106, 188.5, 7.55))
    for i, ratio in enumerate(["16:9", "9:16"]):
        yy = 474 + i * 62
        out.append(f'<text class="lbl" x="1020" y="{yy}" font-size="32" fill="{C["muted"]}">{ratio}</text>')
        out.append(check(1122, yy - 12, 7.25 + i * 0.3))
    return frame("\n".join(out), "A brief becomes a timeline of script, voice, picture and captions, then renders to 16:9 and 9:16 cuts.")


# ---------------------------------------------------------------------------- AI search tracker
def search():
    """Questions down the side, assistants across the top; each cell is one answer checked."""
    cols = [("ChatGPT", 520), ("Perplexity", 725), ("Gemini", 930), ("Claude", 1135)]
    rows = [262, 340, 418, 496]
    asked = [(190, 96), (150, 132), (222, 72), (132, 118)]      # question lengths, as redacted bars
    named = ["1011", "0101", "1110", "0111"]                    # a pattern for the picture, not data
    T0, STEP = 0.7, 0.2
    out = [caption("who gets named?")]

    for name, x in cols:
        out.append(f'<text class="lbl" x="{x}" y="198" font-size="30" text-anchor="middle" fill="{C["muted"]}">{name}</text>')
    for r, y in enumerate(rows):
        a, b = asked[r]
        out.append(f'<rect x="64" y="{y - 10}" width="{a}" height="20" rx="10" fill="{C["border"]}"/>'
                   f'<rect x="{64 + a + 14}" y="{y - 10}" width="{b}" height="20" rx="10" fill="{C["border"]}"/>'
                   f'<text class="lbl" x="{64 + a + 14 + b + 12}" y="{y + 11}" font-size="32" fill="{C["faint"]}">?</text>'
                   f'<line x1="{64 + a + b + 62}" y1="{y}" x2="{cols[-1][1] + 44}" y2="{y}" stroke="{C["line"]}" stroke-width="2" stroke-dasharray="3 9"/>')

    order = [(r, c) for r in range(len(rows)) for c in range(len(cols))]
    for i, (r, c) in enumerate(order):
        x, y, t = cols[c][1], rows[r], T0 + i * STEP
        if named[r][c] == "1":
            inner = (f'<circle cx="{x}" cy="{y}" r="31" fill="{C["accent"]}" fill-opacity="0.16"/>'
                     f'<circle cx="{x}" cy="{y}" r="21" fill="{C["accent"]}"/>')
        else:
            inner = f'<circle cx="{x}" cy="{y}" r="19" fill="{C["bg"]}" stroke="{C["border"]}" stroke-width="3"/>'
        out.append(el("g", "", t, inner, dur=0.15))

    # the scanner: a ring that hops from cell to cell just ahead of each answer
    if not STATIC:
        n = len(order)
        kts = ";".join(["0"] + [k(T0 - 0.12 + i * STEP) for i in range(n)])
        xs = ";".join([str(cols[0][1])] + [str(cols[c][1]) for _, c in order])
        ys = ";".join([str(rows[0])] + [str(rows[r]) for r, _ in order])
        t_end = T0 + n * STEP
        out.append(f'<circle cx="{cols[0][1]}" cy="{rows[0]}" r="33" fill="none" stroke="{C["accent2"]}" stroke-width="3.5" opacity="0">'
                   f'<animate attributeName="cx" calcMode="discrete" values="{xs}" keyTimes="{kts}" dur="{T:g}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="cy" calcMode="discrete" values="{ys}" keyTimes="{kts}" dur="{T:g}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{k(T0 - 0.3)};{k(T0 - 0.12)};{k(t_end)};{k(t_end + 0.25)};1" dur="{T:g}s" repeatCount="indefinite"/></circle>')

    # share of voice: the line the daily runs add up to
    pts = [(372, 598), (455, 593), (540, 596), (628, 585), (716, 588), (806, 573), (896, 577),
           (986, 560), (1070, 563), (1142, 548), (1196, 541)]
    d = f"M{pts[0][0]},{pts[0][1]}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        d += (f" C{p1[0] + (p2[0] - p0[0]) / 6:.1f},{p1[1] + (p2[1] - p0[1]) / 6:.1f}"
              f" {p2[0] - (p3[0] - p1[0]) / 6:.1f},{p2[1] - (p3[1] - p1[1]) / 6:.1f} {p2[0]},{p2[1]}")
    L = 860
    t_a, t_b = T0 + len(order) * STEP + 0.4, T0 + len(order) * STEP + 2.2
    if STATIC:
        dash_attr = dash_anim = ""
    else:
        dash_attr = f' stroke-dasharray="{L}" stroke-dashoffset="0"'
        dash_anim = (f'<animate attributeName="stroke-dashoffset" values="{L};{L};0;0;{L}" keyTimes="0;{k(t_a)};{k(t_b)};{k(OUT)};1" '
                     f'dur="{T:g}s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;0.3 0 0.2 1;0 0 1 1;0.4 0 0.6 1"/>')
    out.append(f'<text class="lbl" x="64" y="592" font-size="30" fill="{C["muted"]}">share of voice</text>')
    out.append(f'<path d="{d}" fill="none" stroke="url(#line)" stroke-width="13" stroke-linecap="round" opacity="0.16"{dash_attr}>{dash_anim}</path>')
    out.append(f'<path d="{d}" fill="none" stroke="url(#line)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"{dash_attr}>{dash_anim}</path>')
    out.append(el("circle", f'cx="{pts[-1][0]}" cy="{pts[-1][1]}" r="8" fill="{C["accent2"]}"', t_b - 0.1))
    return frame("\n".join(out), "A grid of buyer questions against AI assistants, each answer checked for who gets named, with share of voice charted underneath.")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    for name, fn in (("video", video), ("search", search)):
        (here / f"card-{name}.svg").write_text(fn())
        print("wrote", here / f"card-{name}.svg")
    if "--stills" in sys.argv:        # preview-only files; the README does not reference them
        STATIC = True
        for name, fn in (("video", video), ("search", search)):
            (here.parent / "preview" / f"card-still-{name}.svg").write_text(fn())
        print("wrote preview stills")
