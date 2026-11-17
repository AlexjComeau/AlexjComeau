#!/usr/bin/env python3
"""Generate assets/header-light.svg and header-dark.svg.

Hand-made banner: name, a blinking prompt with rotating lines, a growth curve that draws
itself, and a quiet contribution-grid texture. SMIL and CSS keyframes both run inside
<img> on github.com; fonts are system fonts because web fonts never load in SVG-as-image.
Edit LINES below and re-run:  python3 assets/make_header.py
"""
import random
from pathlib import Path

LINES = [
    "go-to-market engineer.",
    "I build systems that grow.",
    "software, video pipelines, AI agents.",
    "Sundays go to whatever looks interesting.",
]
THEMES = {
    "light": dict(bg="#ffffff", bg2="#f6f8fa", border="#d1d9e0", fg="#1f2328", muted="#59636e",
                  accent="#1f883d", accent2="#8250df", dot="#d8e8dc", dot2="#9be9a8", grid="#eaeef2"),
    "dark":  dict(bg="#0d1117", bg2="#161b22", border="#30363d", fg="#f0f6fc", muted="#9198a1",
                  accent="#3fb950", accent2="#a371f7", dot="#143b23", dot2="#0e4429", grid="#21262d"),
}
W, H = 1280, 200
PER, N = 3.4, len(LINES)          # seconds per rotating line
CYCLE = PER * N

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

def svg(theme):
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
    rot = []
    for i, line in enumerate(LINES):
        b = i * PER
        rot.append(f'<text x="76" y="150" font-size="22" fill="{c["muted"]}" opacity="0">{line}'
                   f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.06;0.92;1" dur="{PER}s" begin="{b}s" repeatCount="indefinite" calcMode="linear" '
                   f'end="indefinite"/></text>')
    # SMIL note: begin offsets with repeatCount restart every PER seconds; stagger by using one
    # <animate> per line whose dur is the full cycle so lines do not overlap.
    rot = []
    for i, line in enumerate(LINES):
        k0 = i / N; k1 = k0 + 0.02; k2 = (i + 1) / N - 0.02; k3 = (i + 1) / N
        rot.append(f'<text x="76" y="150" font-size="22" fill="{c["muted"]}" opacity="0">{line}'
                   f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{k0:.4f};{k1:.4f};{k2:.4f};{k3:.4f};1" dur="{CYCLE}s" repeatCount="indefinite" calcMode="linear"/></text>')
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
  <text class="caret" x="48" y="150" font-size="22" fill="{c["accent"]}" font-weight="700">&gt;</text>
  {"".join(rot)}
</g>
</svg>'''

if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    for t in THEMES:
        (here / f"header-{t}.svg").write_text(svg(t))
        print("wrote", here / f"header-{t}.svg")
