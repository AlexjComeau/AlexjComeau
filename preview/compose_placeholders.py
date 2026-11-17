#!/usr/bin/env python3
"""Stack several lowlighter/metrics example SVGs into one tall SVG so the preview
shows roughly what a composed column will look like before the action has run.
Example SVGs come from https://github.com/lowlighter/metrics/tree/examples ."""
import re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent / "placeholders"

def load(name):
    s = (HERE / f"metrics.{name}.svg").read_text()
    s = re.sub(r"<\?xml[^>]*\?>", "", s).strip()
    h = int(re.search(r'height="(\d+)"', s[:400]).group(1))
    return s, h

def compose(names, out):
    parts, y = [], 0
    for n in names:
        s, h = load(n)
        s = re.sub(r"<svg\b", f'<svg y="{y}"', s, count=1)
        parts.append(s); y += h
    (HERE / out).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="{y}" viewBox="0 0 480 {y}">{"".join(parts)}</svg>')
    print("wrote", HERE / out, y, "px tall")

compose(["plugin.isocalendar", "plugin.languages.indepth", "plugin.achievements.compact"], "left-composite.svg")
compose(["classic", "plugin.habits.facts", "plugin.habits.charts", "plugin.lines"], "right-composite.svg")
