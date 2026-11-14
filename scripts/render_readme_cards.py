"""Render animated SVG cards for the GitHub profile README.

Reads data/github.json (written by fetch_github_data.py) and writes cards/*.svg.
The cards are self-contained: inline CSS keyframes, no external fonts or images.

  python scripts/render_readme_cards.py           # animated
  STATIC=1 python scripts/render_readme_cards.py  # final frame only (for previews)
"""
import json
import os
from datetime import date
from html import escape

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data", "github.json")
OUT = os.path.join(ROOT, "cards")
STATIC = os.environ.get("STATIC") == "1"

BG, BORDER = "#0f1115", "#262a33"
TEXT, MUTED = "#e8e6e3", "#9a968f"
AMBER, TEAL = "#f4a443", "#4ab197"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"

NAME = "Arunlal PP"
ROLE = "Frontend Developer · Kerala, India"
TAGLINES = [
    "Building fast, responsive interfaces with React & Next.js",
    "Shipping Nuxt / Vue apps at Softius Technologies",
    "TypeScript · Tailwind · React Native · GSAP",
]
STACK = ["React", "Next.js", "Vue", "Nuxt", "TypeScript", "Tailwind", "React Native"]


def style(css):
    """Wrap CSS; in STATIC mode drop all animation so the final frame shows."""
    if STATIC:
        css += "\n* { animation: none !important; }"
    return f"<style>{css}</style>"


def card(width, height, body, css=""):
    base = f"""
    text {{ font-family: {FONT}; }}
    .fade {{ animation: fade .7s ease-out both; }}
    @keyframes fade {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
    """
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
        f"{style(base + css)}"
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" '
        f'fill="{BG}" stroke="{BORDER}"/>'
        f"{body}</svg>"
    )


def header():
    w, h = 840, 218
    n = len(TAGLINES)
    cycle = 3.2 * n
    css = f"""
    .tag {{ opacity: 0; animation: cycle {cycle}s infinite; }}
    @keyframes cycle {{
      0% {{ opacity: 0; transform: translateY(8px); }}
      4%, {100 / n - 4:.1f}% {{ opacity: 1; transform: none; }}
      {100 / n:.1f}%, 100% {{ opacity: 0; transform: translateY(-8px); }}
    }}
    .bar {{ transform-origin: 40px 0; animation: grow 1.2s cubic-bezier(.2,.8,.2,1) .3s both; }}
    @keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
    .chip {{ animation: fade .5s ease-out both; }}
    .glow {{ animation: pulse 4s ease-in-out infinite; }}
    @keyframes pulse {{ 0%,100% {{ opacity: .35; }} 50% {{ opacity: .7; }} }}
    """
    tags = "".join(
        f'<text class="tag" x="40" y="118" font-size="17" fill="{MUTED}" '
        f'style="animation-delay:{i * 3.2}s{";opacity:1" if STATIC and i == 0 else ""}">{escape(t)}</text>'
        for i, t in enumerate(TAGLINES)
    )
    chips, x = [], 40
    for i, s in enumerate(STACK):
        cw = 16 + 7.6 * len(s)
        chips.append(
            f'<g class="chip" style="animation-delay:{0.6 + i * 0.12:.2f}s">'
            f'<rect x="{x}" y="154" width="{cw:.0f}" height="28" rx="14" fill="#1a1d24" stroke="{BORDER}"/>'
            f'<text x="{x + cw / 2:.0f}" y="173" font-size="13" fill="{TEXT}" text-anchor="middle">{escape(s)}</text></g>'
        )
        x += cw + 8
    body = f"""
    <defs><radialGradient id="g" cx="85%" cy="100%" r="60%">
      <stop offset="0" stop-color="{AMBER}" stop-opacity=".35"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/>
    </radialGradient></defs>
    <rect class="glow" x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="url(#g)"/>
    <text class="fade" x="40" y="62" font-size="15" font-weight="700" letter-spacing="2" fill="{AMBER}">HI, I'M</text>
    <text class="fade" x="40" y="96" font-size="34" font-weight="800" fill="{TEXT}" style="animation-delay:.15s">{NAME}</text>
    <text class="fade" x="{40 + 21 * len(NAME)}" y="96" font-size="16" fill="{MUTED}" style="animation-delay:.3s">{escape(ROLE)}</text>
    <rect class="bar" x="40" y="128" width="120" height="3" rx="1.5" fill="{AMBER}"/>
    {tags}
    {''.join(chips)}
    """
    # taglines sit above the bar; nudge bar below them
    body = body.replace('y="128" width="120"', 'y="136" width="120"').replace('y="118"', 'y="120"')
    return card(w, h, body, css)


def stats(d):
    w, h = 410, 190
    items = [
        ("Public repos", d["repos"]),
        (f"Contributions ({date.today().year - 1}–{date.today().year % 100:02d})", d["contributions_year"]),
        ("Current streak", f'{d["current_streak"]} days'),
        ("Followers", d["followers"]),
    ]
    rows = []
    for i, (label, value) in enumerate(items):
        cx = 30 + (i % 2) * 190
        cy = 78 + (i // 2) * 62
        rows.append(
            f'<g class="fade" style="animation-delay:{0.2 + i * 0.15:.2f}s">'
            f'<text x="{cx}" y="{cy}" font-size="28" font-weight="800" fill="{TEXT}">{escape(str(value))}</text>'
            f'<text x="{cx}" y="{cy + 20}" font-size="12.5" fill="{MUTED}">{escape(label)}</text></g>'
        )
    body = (
        f'<text class="fade" x="30" y="38" font-size="14" font-weight="700" letter-spacing="1.5" fill="{AMBER}">GITHUB AT A GLANCE</text>'
        + "".join(rows)
    )
    return card(w, h, body)


def languages(d):
    w, h = 410, 190
    langs = d["languages"][:5]
    total = sum(l["bytes"] for l in langs) or 1
    css = """
    .grow { transform-box: fill-box; transform-origin: left; animation: grow 1s cubic-bezier(.2,.8,.2,1) both; }
    @keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
    """
    rows = []
    for i, l in enumerate(langs):
        pct = l["bytes"] / total * 100
        y = 66 + i * 24
        bw = max(4, 230 * pct / 100)
        rows.append(
            f'<g class="fade" style="animation-delay:{0.15 * i:.2f}s">'
            f'<text x="30" y="{y + 9}" font-size="13" fill="{TEXT}">{escape(l["name"])}</text>'
            f'<rect x="130" y="{y}" width="230" height="10" rx="5" fill="#1a1d24"/>'
            f'<rect class="grow" x="130" y="{y}" width="{bw:.1f}" height="10" rx="5" fill="{l["color"]}" '
            f'style="animation-delay:{0.3 + 0.15 * i:.2f}s"/>'
            f'<text x="370" y="{y + 9}" font-size="12" fill="{MUTED}">{pct:.0f}%</text></g>'
        )
    body = (
        f'<text class="fade" x="30" y="38" font-size="14" font-weight="700" letter-spacing="1.5" fill="{AMBER}">TOP LANGUAGES</text>'
        + "".join(rows)
    )
    return card(w, h, body, css)


def activity(d):
    w, h = 840, 175
    days = d["days"][-371:]
    peak = max((x["count"] for x in days), default=0) or 1
    shades = ["#1b1f27", "#5a3d1c", "#8a5a22", "#c27f2e", AMBER]
    css = """
    .cell { transform-box: fill-box; transform-origin: center; animation: pop .35s ease-out both; }
    @keyframes pop { from { opacity: 0; transform: scale(.2); } to { opacity: 1; transform: scale(1); } }
    """
    cells = []
    first = date.fromisoformat(days[0]["date"]) if days else date.today()
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    for i, x in enumerate(days):
        idx = i + offset
        col, row = idx // 7, idx % 7
        c = x["count"]
        lvl = 0 if c == 0 else min(4, 1 + int(3 * c / peak))
        cells.append(
            f'<rect class="cell" x="{30 + col * 14.6:.1f}" y="{52 + row * 14}" width="11" height="11" rx="2.5" '
            f'fill="{shades[lvl]}" style="animation-delay:{col * 0.025:.3f}s"/>'
        )
    body = (
        f'<text class="fade" x="30" y="36" font-size="14" font-weight="700" letter-spacing="1.5" fill="{AMBER}">LAST 12 MONTHS</text>'
        f'<text class="fade" x="810" y="36" font-size="13" fill="{MUTED}" text-anchor="end">'
        f'{d["contributions_year"]} contributions · updated {d["generated_at"]}</text>'
        + "".join(cells)
    )
    return card(w, h, body, css)


def main():
    os.makedirs(OUT, exist_ok=True)
    cards = [("header", header())]
    if os.path.exists(DATA):
        with open(DATA) as fh:
            d = json.load(fh)
        cards += [("stats", stats(d)), ("languages", languages(d)), ("activity", activity(d))]
    else:
        print("data/github.json not found; run fetch_github_data.py first. Rendering header only.")
    for name, svg in cards:
        path = os.path.join(OUT, f"{name}.svg")
        with open(path, "w") as fh:
            fh.write(svg)
        print("wrote", path)


if __name__ == "__main__":
    main()
