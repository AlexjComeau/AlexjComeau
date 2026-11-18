#!/usr/bin/env python3
"""Render README.md the way GitHub does, in light and dark, for a local preview.

Uses GitHub's own Markdown API (via the authenticated `gh` CLI) so the HTML and the
sanitisation match github.com, then wraps it in github-markdown-css inside a mock
profile-README card.

Usage:  python3 preview/render.py            # writes preview/light.html + preview/dark.html
        python3 preview/render.py --serve    # also serves the repo root on :8787
"""
import argparse, html, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREVIEW = ROOT / "preview"
MAP = PREVIEW / "placeholders.json"   # {"github-metrics.svg": "preview/placeholders/x.svg"}

CSS = {
    "light": "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.8.1/github-markdown-light.min.css",
    "dark":  "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.8.1/github-markdown-dark.min.css",
}
BG = {"light": "#ffffff", "dark": "#0d1117"}
BORDER = {"light": "#d1d9e0", "dark": "#3d444d"}
FG = {"light": "#1f2328", "dark": "#f0f6fc"}

def gh_markdown(md: str) -> str:
    out = subprocess.run(
        ["gh", "api", "markdown", "-f", "mode=gfm", "-f", "context=AlexjComeau/AlexjComeau", "-F", "text=@-"],
        input=md, text=True, capture_output=True, check=True)
    return out.stdout

def pick_theme(body: str, theme: str) -> str:
    """Resolve <picture> blocks to the one <img> the chosen theme would show."""
    def repl(m):
        block = m.group(0)
        srcs = dict(re.findall(r'<source[^>]*media="\(prefers-color-scheme:\s*(\w+)\)"[^>]*srcset="([^"]+)"', block))
        img = re.search(r'<img[^>]*>', block)
        if not img:
            return block
        tag = img.group(0)
        if theme in srcs:
            tag = re.sub(r'src="[^"]*"', f'src="{srcs[theme]}"', tag)
        return tag
    body = re.sub(r'<themed-picture[^>]*>', '', body).replace('</themed-picture>', '')
    return re.sub(r'<picture>.*?</picture>', repl, body, flags=re.S)

def map_placeholders(body: str, mapping: dict) -> str:
    """Point not-yet-generated SVGs at example placeholders (relative to repo root)."""
    for src, dst in mapping.items():
        body = body.replace(f'src="{src}"', f'src="{dst}"').replace(f'src="/{src}"', f'src="{dst}"')
    return body

def root_paths(body: str) -> str:
    """Serve relative image paths from the repo root (the preview pages live in preview/)."""
    return re.sub(r'(src|srcset)="(?!https?://|/)', r'\1="/', body)

def page(body: str, theme: str) -> str:
    return f"""<!doctype html>
<html lang="en" data-color-mode="{theme}" data-theme="{theme}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AlexjComeau profile preview ({theme})</title>
<link rel="stylesheet" href="{CSS[theme]}">
<style>
  html,body{{margin:0;background:{BG[theme]};color:{FG[theme]};color-scheme:{theme};
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif}}
  .page{{max-width:1280px;margin:0 auto;padding:32px 24px;display:grid;grid-template-columns:296px 1fr;gap:24px}}
  .side{{font-size:14px}}
  .side img{{width:296px;height:296px;border-radius:50%;border:1px solid {BORDER[theme]}}}
  .side h1{{font-size:24px;margin:16px 0 0;font-weight:600}}
  .side .login{{font-size:20px;opacity:.65;font-weight:300}}
  .side p{{margin:16px 0 0;line-height:1.5}}
  .card{{border:1px solid {BORDER[theme]};border-radius:6px;padding:24px;min-width:0}}
  .card .fname{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;opacity:.7;margin:-8px 0 16px}}
  .markdown-body{{background:transparent}}
  .markdown-body img{{max-width:100%}}
  @media (max-width:900px){{.page{{grid-template-columns:1fr}}.side img{{width:96px;height:96px}}}}
</style>
</head>
<body>
<div class="page">
  <aside class="side">
    <img src="https://avatars.githubusercontent.com/u/54641856?v=4" alt="avatar">
    <h1>Alexander Comeau</h1><div class="login">AlexjComeau</div>
    <p>Two truths and a lie: 1. Fought in the underground fightclubs of Bangkok 2. I make 1000+ bottles of maple syrup a year 3. Surfed Jaws on a huge northwest swell</p>
    <p>📍 Ottawa &nbsp;·&nbsp; 🔗 acomeau.com</p>
  </aside>
  <main class="card">
    <div class="fname">AlexjComeau / README.md</div>
    <article class="markdown-body">
{body}
    </article>
  </main>
</div>
</body></html>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default=str(ROOT / "README.md"))
    ap.add_argument("--serve", action="store_true")
    a = ap.parse_args()
    md = Path(a.readme).read_text()
    mapping = json.loads(MAP.read_text()) if MAP.exists() else {}
    body = gh_markdown(md)
    for theme in ("light", "dark"):
        themed = pick_theme(body, theme)
        b = root_paths(map_placeholders(themed, mapping))
        (PREVIEW / f"{theme}.html").write_text(page(b, theme))
        # still variant for screenshots: the banner's finished frame instead of the animation
        still = dict(mapping, **{f"assets/header-{theme}.svg": f"preview/header-still-{theme}.svg"})
        if (PREVIEW / f"header-still-{theme}.svg").exists():
            (PREVIEW / f"{theme}-still.html").write_text(page(root_paths(map_placeholders(themed, still)), theme))
        print("wrote", PREVIEW / f"{theme}.html")
    if a.serve:
        os.chdir(ROOT)
        subprocess.run([sys.executable, "-m", "http.server", "8787", "--bind", "127.0.0.1"])

if __name__ == "__main__":
    main()
