#!/usr/bin/env python3
"""Generate assets/skyline-light.svg and assets/skyline-dark.svg.

A full-year contribution skyline drawn from the public contribution calendar: one block per
day, 53 weeks left to right, Sunday at the back, height = that day's contributions. Built for
full README width, so the type stays readable; GitHub's own greens, one file per theme.

Needs a token in GH_TOKEN (any token that can read public data). Standard library only.
    GH_TOKEN=$(gh auth token) python3 assets/make_skyline.py
"""
import datetime, json, math, os, sys, urllib.request
from pathlib import Path

LOGIN = "AlexjComeau"
QUERY = """query($login:String!){ user(login:$login){ contributionsCollection{ contributionCalendar{
  totalContributions weeks{ contributionDays{ date weekday contributionCount contributionLevel } } } } } }"""

THEMES = {
    "light": dict(levels=["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
                  fg="#1f2328", muted="#59636e", faint="#8c959f"),
    "dark":  dict(levels=["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
                  fg="#f0f6fc", muted="#9198a1", faint="#6e7681"),
}
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

W = 1120                      # viewBox width; README shows it at about 0.77x
WEEKS = int(os.environ.get("SKYLINE_WEEKS", "53"))   # how many trailing weeks to draw
VXR, VYR, UYR = -0.414, 0.373, 0.130   # day step and weekly drop, as fractions of one week's width
CELL = 0.84                   # block footprint, the rest is gap
MINH = 5.0                    # shortest non-empty block, px
LEFT, RIGHT = 22, 14

def fetch():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GH_TOKEN is not set")
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-skyline"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors"):
        sys.exit(f"GraphQL error: {data['errors'][0].get('message')}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]

def shade(hex_color, k):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c * k))) for c in (r, g, b))

def stats(weeks):
    days = [d for w in weeks for d in w["contributionDays"]]
    best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        best = max(best, run)
    top = max(days, key=lambda d: d["contributionCount"])
    total = sum(d["contributionCount"] for d in days)
    return dict(total=total, best_streak=best, busiest=top["contributionCount"],
                busiest_date=top["date"], average=total / max(1, len(days)), days=len(days))

def svg(cal, theme):
    c = THEMES[theme]
    weeks = cal["weeks"][-WEEKS:]
    n = len(weeks)
    ux = (W - LEFT - RIGHT) / (n - 7 * VXR)         # one week's width; the day axis leans left
    VX, VY, UY = VXR * ux, VYR * ux, UYR * ux
    MAXH = min(92.0, 3.2 * ux)
    x0, y0 = LEFT - 7 * VX, MAXH + 12
    maxc = max(d["contributionCount"] for w in weeks for d in w["contributionDays"]) or 1
    P = lambda w, d, h=0.0: (x0 + w * ux + d * VX, y0 + w * UY + d * VY - h)
    pts = lambda *ps: " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)

    blocks = []
    for dayi in range(7):                           # back row first
        for wi, week in enumerate(weeks):           # then left to right
            day = next((d for d in week["contributionDays"] if d["weekday"] == dayi), None)
            if day is None:
                continue
            lv = LEVEL.get(day["contributionLevel"], 0)
            col = c["levels"][lv]
            cnt = day["contributionCount"]
            h = 0.0 if cnt == 0 else MINH + (MAXH - MINH) * math.sqrt(cnt / maxc)
            a, b = (wi, dayi), (wi + CELL, dayi)
            cc, dd = (wi + CELL, dayi + CELL), (wi, dayi + CELL)
            if h:
                blocks.append(f'<polygon points="{pts(P(*dd), P(*cc), P(*cc, h), P(*dd, h))}" fill="{shade(col, 0.80)}"/>')
                blocks.append(f'<polygon points="{pts(P(*cc), P(*b), P(*b, h), P(*cc, h))}" fill="{shade(col, 0.62)}"/>')
            blocks.append(f'<polygon points="{pts(P(*a, h), P(*b, h), P(*cc, h), P(*dd, h))}" fill="{col}"/>')

    # month labels along the front edge, tilted to the slope
    marks, seen = [], None
    for wi, week in enumerate(weeks):
        first = week["contributionDays"][0]["date"]
        if first[:7] != seen and wi < n - 1:
            seen = first[:7]
            marks.append((wi, datetime.date.fromisoformat(first).strftime("%b")))
    marks = [m for i, m in enumerate(marks) if i == len(marks) - 1 or marks[i + 1][0] - m[0] >= 3]
    tilt = math.degrees(math.atan2(UY, ux))
    labels = []
    for wi, name in marks:
        lx, ly = P(wi, 7.0)
        labels.append(f'<text x="{lx + 2:.1f}" y="{ly + 15:.1f}" transform="rotate({tilt:.2f} {lx + 2:.1f} {ly + 15:.1f})" font-size="12" fill="{c["faint"]}" class="mono">{name}</text>')

    s = stats(weeks)
    H = int(P(n, 7)[1] + 30)
    ty = H - 58                                       # text block: bottom-left, under the high end of the strip
    busiest = datetime.date.fromisoformat(s["busiest_date"]).strftime("%-d %b")
    span = "the last year" if n >= 52 else f"the last {n} weeks"
    facts = f'{s["best_streak"]}-day best streak  /  {s["busiest"]:,} on {busiest}  /  {s["average"]:.0f} a day'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{s["total"]:,} contributions in {span}, drawn as a skyline: one block per day.">
<style>
  text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
  .mono{{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace}}
</style>
<g>{"".join(blocks)}</g>
<g>{"".join(labels)}</g>
<text x="{LEFT}" y="{ty}" font-size="46" font-weight="700" letter-spacing="-1" fill="{c["fg"]}">{s["total"]:,}</text>
<text x="{LEFT}" y="{ty + 24}" font-size="16" fill="{c["muted"]}">contributions in {span}, one block per day</text>
<text x="{LEFT}" y="{ty + 46}" font-size="13" fill="{c["faint"]}" class="mono">{facts}</text>
</svg>'''

if __name__ == "__main__":
    cal = fetch()
    prefix = os.environ.get("SKYLINE_OUT") or str(Path(__file__).resolve().parent / "skyline")
    for theme in THEMES:
        out = Path(f"{prefix}-{theme}.svg")
        out.write_text(svg(cal, theme))
        print("wrote", out.name, out.stat().st_size // 1024, "KB")
    print(json.dumps(stats(cal["weeks"][-WEEKS:])))
