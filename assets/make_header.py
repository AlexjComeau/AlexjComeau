#!/usr/bin/env python3
"""Generate assets/header-light.svg and header-dark.svg.

Hand-made banner: name, a blinking prompt with rotating lines, a growth curve that draws
itself, and a quiet contribution-grid texture. SMIL and CSS keyframes both run inside
<img> on github.com; fonts are system fonts because web fonts never load in SVG-as-image.
Edit TIMELINE below and re-run:  python3 assets/make_header.py
"""
import random
import re
import sys
from pathlib import Path

# The rotating line: a year, then what I was doing that year. Shown in a shuffled order
# (fixed seed, so every render is the same) that opens on the current year.
TIMELINE = [
    (1991, "Birth year"),
    (2007, "First pro points at an MLG event"),
    (2009, "Graduated high school"),
    (2013, "Graduated college"),
    (2015, "Lived in a van surfing in Australia"),
    (2017, "Founded my first company"),
    (2019, "Opened a nightclub"),
    (2022, "250,000 vodka sodas sold"),
    (2023, "Sold my first company"),
    (2023, "Joined Airstack (first onchain AI)"),
    (2026, "Building Senpi"),
]
TAGLINE = "distribution is an engineering problem."   # used on the share image only
SEED = 7
PER = 5.0                         # seconds each entry stays up
ROLL_STEPS, ROLL_STEP = 4, 0.08   # the year "rolls" through a few others before it lands
THEMES = {
    "light": dict(bg="#ffffff", bg2="#f6f8fa", border="#d1d9e0", fg="#1f2328", muted="#59636e",
                  accent="#1f883d", accent2="#8250df", dot="#d8e8dc", dot2="#9be9a8", grid="#eaeef2"),
    "dark":  dict(bg="#0d1117", bg2="#161b22", border="#30363d", fg="#f0f6fc", muted="#9198a1",
                  accent="#3fb950", accent2="#a371f7", dot="#143b23", dot2="#0e4429", grid="#21262d"),
}
W, H = 1280, 200

# Growth curve: control points in banner space (x 720..1232, y 40..168), rising left to right
PTS = [(720, 158), (790, 150), (850, 154), (910, 136), (960, 140), (1010, 112), (1060, 118),
       (1110, 84), (1150, 90), (1190, 56), (1232, 44)]

def smooth_path(pts):
    """Catmull-Rom through pts as cubic beziers."""
    d = f"M{pts[0][0]},{pts[0][1]}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]},{p2[1]}"
    return d

def approx_length(pts, steps=40):
    """Numeric length of the same Catmull-Rom spline (for the dash animation)."""
    import math
    total = 0.0
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        prev = p1
        for s in range(1, steps + 1):
            t = s / steps
            x = (1-t)**3*p1[0] + 3*(1-t)**2*t*c1[0] + 3*(1-t)*t**2*c2[0] + t**3*p2[0]
            y = (1-t)**3*p1[1] + 3*(1-t)**2*t*c1[1] + 3*(1-t)*t**2*c2[1] + t**3*p2[1]
            total += math.hypot(x - prev[0], y - prev[1]); prev = (x, y)
    return total

def order():
    """Indexes into TIMELINE: the latest year first, the rest shuffled, same year never back to back."""
    first = max(range(len(TIMELINE)), key=lambda i: TIMELINE[i][0])
    rest = [i for i in range(len(TIMELINE)) if i != first]
    seed = SEED
    while True:
        cand = rest[:]
        random.Random(seed).shuffle(cand)
        seq = [first] + cand
        if all(TIMELINE[a][0] != TIMELINE[b][0] for a, b in zip(seq, seq[1:] + seq[:1])):
            return seq
        seed += 1


def timeline(c, freeze=None):
    """The rotating year line. freeze=k returns entry k of the shuffled order with no animation."""
    seq = order()
    n = len(seq)
    cycle = PER * n
    x_year, x_text, y = 78, 138, 149
    base = f'class="mono" y="{y}" font-size="20"'
    if freeze is not None:
        year, text = TIMELINE[seq[freeze % n]]
        return (f'<text {base} x="{x_year}" font-weight="600" fill="{c["fg"]}">{year}</text>'
                f'<text {base} x="{x_text}" fill="{c["muted"]}">- {text}</text>')
    k = lambda t: f"{min(1.0, max(0.0, t / cycle)):.5f}"
    def fade(start, full, hold, end):
        """opacity keyframes: 0 until start, up by full, held until hold, 0 by end."""
        vals, kts = ["0", "0", "1", "1", "0"], ["0", k(start), k(full), k(hold), k(end)]
        if end < cycle - 1e-6:
            vals.append("0"); kts.append("1")
        return f'<animate attributeName="opacity" values="{";".join(vals)}" keyTimes="{";".join(kts)}" dur="{cycle:g}s" repeatCount="indefinite" calcMode="linear"/>'
    rnd = random.Random(SEED)
    out = []
    for slot, idx in enumerate(seq):
        year, text = TIMELINE[idx]
        t0, end = slot * PER, (slot + 1) * PER
        others = sorted({yr for yr, _ in TIMELINE if yr != year})
        for j in range(ROLL_STEPS):
            a, b = t0 + j * ROLL_STEP, t0 + (j + 1) * ROLL_STEP
            vals, kts = ("1;0", f"0;{k(b)}") if a <= 0 else ("0;1;0", f"0;{k(a)};{k(b)}")
            out.append(f'<text {base} x="{x_year}" fill="{c["muted"]}" opacity="0">{rnd.choice(others)}'
                       f'<animate attributeName="opacity" values="{vals}" keyTimes="{kts}" dur="{cycle:g}s" repeatCount="indefinite" calcMode="discrete"/></text>')
        land = t0 + ROLL_STEPS * ROLL_STEP
        out.append(f'<text {base} x="{x_year}" font-weight="600" fill="{c["fg"]}" opacity="0">{year}{fade(land, land + 0.02, end - 0.35, end)}</text>')
        out.append(f'<text {base} x="{x_text}" fill="{c["muted"]}" opacity="0">- {text}{fade(land, land + 0.30, end - 0.35, end)}</text>')
    return "".join(out)


def svg(theme, freeze=None):
    c = THEMES[theme]
    rnd = random.Random(11)
    cells = []
    for col in range(44):
        for row in range(10):
            v = rnd.random()
            if v < 0.62:
                continue
            fill = c["dot"] if v < 0.9 else c["dot2"]
            delay = (col * 0.09 + row * 0.13) % 4
            cells.append(f'<rect x="{716 + col * 12}" y="{40 + row * 13}" width="9" height="9" rx="2" fill="{fill}" opacity="0.35">'
                         f'<animate attributeName="opacity" values="0.35;0.9;0.35" dur="5s" begin="{delay:.2f}s" repeatCount="indefinite"/></rect>')
    path = smooth_path(PTS)
    L = int(approx_length(PTS)) + 8
    area = path + f" L{PTS[-1][0]},176 L{PTS[0][0]},176 Z"
    rot = timeline(c, freeze)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Alex Comeau, go-to-market engineer. I build systems that grow.">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c["bg"]}"/><stop offset="1" stop-color="{c["bg2"]}"/></linearGradient>
  <linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["accent2"]}"/></linearGradient>
  <linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["accent"]}" stop-opacity="0.28"/><stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"/></linearGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["bg"]}" stop-opacity="1"/><stop offset="0.25" stop-color="{c["bg"]}" stop-opacity="0"/></linearGradient>
  <clipPath id="r"><rect width="{W}" height="{H}" rx="12"/></clipPath>
  <style>
    text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-weight:500}}
    .name{{font-weight:700;letter-spacing:-0.5px}}
    .mono{{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;font-weight:400;letter-spacing:-0.2px}}
    .caret{{animation:blink 1.1s steps(2,start) infinite}}
    @keyframes blink{{to{{visibility:hidden}}}}
    .sweep{{animation:sweep 8s ease-in-out infinite}}
    @keyframes sweep{{0%{{transform:translateX(-220px)}}100%{{transform:translateX({W + 240}px)}}}}
  </style>
</defs>
<g clip-path="url(#r)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{c["border"]}"/>
  <g>{"".join(cells)}</g>
  <rect x="700" y="0" width="200" height="{H}" fill="url(#fade)"/>
  <path d="{area}" fill="url(#area)" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.06;0.22;0.92;1" dur="10s" repeatCount="indefinite"/></path>
  <path d="{path}" fill="none" stroke="url(#line)" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" opacity="0.16" stroke-dasharray="{L}" stroke-dashoffset="{L}">
    <animate attributeName="stroke-dashoffset" values="{L};0;0;{L}" keyTimes="0;0.18;0.92;1" dur="10s" repeatCount="indefinite" calcMode="spline" keySplines="0.2 0.8 0.2 1;0 0 1 1;0.4 0 0.6 1"/>
  </path>
  <path d="{path}" fill="none" stroke="url(#line)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{L}" stroke-dashoffset="{L}">
    <animate attributeName="stroke-dashoffset" values="{L};0;0;{L}" keyTimes="0;0.18;0.92;1" dur="10s" repeatCount="indefinite" calcMode="spline" keySplines="0.2 0.8 0.2 1;0 0 1 1;0.4 0 0.6 1"/>
  </path>
  <circle cx="{PTS[-1][0]}" cy="{PTS[-1][1]}" r="5" fill="{c["accent2"]}" opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.17;0.21;0.92;1" dur="10s" repeatCount="indefinite"/></circle>
  <rect x="0" y="{H - 4}" width="{W}" height="4" fill="url(#line)" opacity="0.9"/>
  <rect class="sweep" x="0" y="{H - 4}" width="220" height="4" fill="{c["bg"]}" opacity="0.55"/>
  <text class="name" x="48" y="96" font-size="54" fill="{c["fg"]}">Alex Comeau</text>
  <text class="caret mono" x="48" y="149" font-size="20" fill="{c["accent"]}" style="font-weight:700">&gt;</text>
  {rot}
</g>
</svg>'''

def still(theme, line=0):
    """The banner's finished frame with no animation: for screenshots and the share image."""
    out = svg(theme, freeze=line)
    out = re.sub(r"<animate\b[^>]*/>", "", out)
    out = out.replace('fill="url(#area)" opacity="0"', 'fill="url(#area)" opacity="1"')
    out = re.sub(r'stroke-dashoffset="\d+"', 'stroke-dashoffset="0"', out)
    out = re.sub(r'(<circle[^>]*?)opacity="0"', r'\1opacity="1"', out)
    out = re.sub(r'<rect class="sweep"[^>]*/>', "", out)
    return out.replace('class="caret mono"', 'class="mono"')


def social():
    """1280x640 share image (GitHub's social preview size): dark, static."""
    c = THEMES["dark"]
    rnd = random.Random(11)
    cells = []
    for col in range(86):
        for row in range(30):
            v = rnd.random()
            if v < 0.74:
                continue
            fill = c["dot"] if v < 0.93 else c["dot2"]
            cells.append(f'<rect x="{250 + col * 12}" y="{150 + row * 13}" width="9" height="9" rx="2" fill="{fill}" opacity="0.55"/>')
    path = smooth_path(PTS)
    area = path + f" L{PTS[-1][0]},176 L{PTS[0][0]},176 Z"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c["bg"]}"/><stop offset="1" stop-color="{c["bg2"]}"/></linearGradient>
  <linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["accent2"]}"/></linearGradient>
  <linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["accent"]}" stop-opacity="0.30"/><stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"/></linearGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["bg"]}" stop-opacity="1"/><stop offset="0.55" stop-color="{c["bg"]}" stop-opacity="0"/></linearGradient>
  <style>
    text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
    .mono{{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}}
  </style>
</defs>
<rect width="1280" height="640" fill="url(#bg)"/>
<g>{"".join(cells)}</g>
<rect x="240" y="0" width="520" height="640" fill="url(#fade)"/>
<g transform="translate(-1036,146) scale(1.85)">
  <path d="{area}" fill="url(#area)"/>
  <path d="{path}" fill="none" stroke="url(#line)" stroke-width="9" stroke-linecap="round" opacity="0.16"/>
  <path d="{path}" fill="none" stroke="url(#line)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="{PTS[-1][0]}" cy="{PTS[-1][1]}" r="4.5" fill="{c["accent2"]}"/>
</g>
<text x="72" y="176" font-size="96" font-weight="700" letter-spacing="-2" fill="{c["fg"]}">Alex Comeau</text>
<text x="74" y="240" font-size="30" class="mono" fill="{c["muted"]}"><tspan fill="{c["accent"]}" font-weight="700">&gt;</tspan> {TAGLINE}</text>
<text x="74" y="572" font-size="24" class="mono" fill="{c["muted"]}">github.com/AlexjComeau</text>
<rect x="0" y="632" width="1280" height="8" fill="url(#line)"/>
</svg>"""


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    for t in THEMES:
        (here / f"header-{t}.svg").write_text(svg(t))
        print("wrote", here / f"header-{t}.svg")
    if "--stills" in sys.argv:        # preview-only files; the README does not reference them
        prev = here.parent / "preview"
        for t in THEMES:
            (prev / f"header-still-{t}.svg").write_text(still(t))
        (prev / "social-preview.svg").write_text(social())
        print("wrote preview stills and social-preview.svg")
