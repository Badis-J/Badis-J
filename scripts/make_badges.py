#!/usr/bin/env python3
"""Generates the README badges as self-contained SVG files (rounded rectangles, larger sans-serif font).

Run: python3 scripts/make_badges.py   then commit the files written in assets/.
Needs Pillow only to measure text width (pip install pillow). Change the PALETTE below to recolor everything.
"""
from pathlib import Path

from PIL import ImageFont

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

PALETTE = {
    "base": "#1f2937",      # pill background (slate)
    "border": "#374151",
    "label": "#aeb8c6",     # secondary text
    "value": "#ffffff",     # main text
    "accent": "#34d399",    # icons (soft emerald)
    "linkedin": "#0a66c2",
    "status": "#047857",    # emerald-700, white text reaches 5.5:1 contrast
}
FONT_STACK = "Inter,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
_MEASURE = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"


def tw(text: str, size: int) -> float:
    try:
        return ImageFont.truetype(_MEASURE, size).getlength(text)
    except OSError:  # fallback if Inter is missing: rough average width
        return len(text) * size * 0.58


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def icon(kind: str, x: float, cy: float, color: str) -> str:
    """16x16 icons drawn around (x, cy)."""
    y = cy - 8
    if kind == "mail":
        return (f'<g transform="translate({x} {y})" fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round">'
                f'<rect x="1" y="2.5" width="14" height="11" rx="2.5"/><path d="M2 4.5l6 4.5 6-4.5"/></g>')
    if kind == "pin":
        return (f'<g transform="translate({x} {y})"><path fill="{color}" d="M8 0.5C4.9 0.5 2.5 2.9 2.5 5.9c0 4 5.5 9.6 5.5 9.6s5.5-5.6 5.5-9.6C13.5 2.9 11.1 0.5 8 0.5z"/>'
                f'<circle cx="8" cy="5.9" r="2.1" fill="{PALETTE["base"]}"/></g>')
    if kind == "dot":
        return (f'<circle cx="{x + 8}" cy="{cy}" r="4.5" fill="#a7f3d0"><animate attributeName="opacity" values="1;0.35;1" dur="1.8s" repeatCount="indefinite"/></circle>')
    if kind == "in":
        return (f'<g transform="translate({x} {y})"><rect width="16" height="16" rx="3.5" fill="#ffffff"/>'
                f'<text x="8" y="12.4" text-anchor="middle" font-family="{FONT_STACK}" font-size="11.5" font-weight="800" fill="{PALETTE["linkedin"]}">in</text></g>')
    return ""


def pill(name: str, kind: str, label: str, value: str, *, fill=None, stroke=None, h=40, fs=16, lfs=14,
         icon_color=None, label_color=None):
    fill = fill or PALETTE["base"]
    stroke = stroke or PALETTE["border"]
    icon_color = icon_color or PALETTE["accent"]
    label_color = label_color or PALETTE["label"]
    pad, gap = 16, 10
    lw = tw(label, lfs) * 0.97 if label else 0
    vw = tw(value, fs) * 0.97
    w = pad + 16 + gap + (lw + 8 if label else 0) + vw + pad + 6
    cy = h / 2
    x = pad + 16 + gap
    parts = [icon(kind, pad, cy, icon_color)]
    if label:
        parts.append(f'<text x="{x:.1f}" y="{cy + lfs * 0.35:.1f}" font-family="{FONT_STACK}" font-size="{lfs}" font-weight="500" fill="{label_color}" '
                     f'textLength="{lw:.1f}" lengthAdjust="spacingAndGlyphs">{esc(label)}</text>')
        x += lw + 8
    parts.append(f'<text x="{x:.1f}" y="{cy + fs * 0.35:.1f}" font-family="{FONT_STACK}" font-size="{fs}" font-weight="600" fill="{PALETTE["value"]}" '
                 f'textLength="{vw:.1f}" lengthAdjust="spacingAndGlyphs">{esc(value)}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h}" viewBox="0 0 {w:.0f} {h}" role="img" aria-label="{esc(label + " " + value).strip()}">'
           f'<rect x="0.5" y="0.5" width="{w - 1:.0f}" height="{h - 1}" rx="10" fill="{fill}" stroke="{stroke}"/>'
           + "".join(parts) + "</svg>\n")
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
    return name


def chip(name: str, label: str, dot: str):
    h, fs, pad = 34, 14, 14
    vw = tw(label, fs) * 0.97
    w = pad + 10 + 8 + vw + pad + 4
    cy = h / 2
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h}" viewBox="0 0 {w:.0f} {h}" role="img" aria-label="{esc(label)}">'
           f'<rect x="0.5" y="0.5" width="{w - 1:.0f}" height="{h - 1}" rx="9" fill="{PALETTE["base"]}" stroke="{PALETTE["border"]}"/>'
           f'<circle cx="{pad + 5}" cy="{cy}" r="5" fill="{dot}"/>'
           f'<text x="{pad + 18}" y="{cy + fs * 0.35:.1f}" font-family="{FONT_STACK}" font-size="{fs}" font-weight="600" fill="{PALETTE["value"]}" '
           f'textLength="{vw:.1f}" lengthAdjust="spacingAndGlyphs">{esc(label)}</text></svg>\n')
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


def button(name: str, kind: str, text: str, fill: str, stroke: str, icon_color: str):
    h, fs, pad = 52, 17, 24
    vw = tw(text, fs) * 0.97
    w = pad + 18 + 12 + vw + pad + 6
    cy = h / 2
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h}" viewBox="0 0 {w:.0f} {h}" role="img" aria-label="{esc(text)}">'
           f'<rect x="0.5" y="0.5" width="{w - 1:.0f}" height="{h - 1}" rx="12" fill="{fill}" stroke="{stroke}"/>'
           + icon(kind, pad, cy, icon_color) +
           f'<text x="{pad + 28}" y="{cy + fs * 0.35:.1f}" font-family="{FONT_STACK}" font-size="{fs}" font-weight="600" fill="#ffffff" '
           f'textLength="{vw:.1f}" lengthAdjust="spacingAndGlyphs">{esc(text)}</text></svg>\n')
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    # top row
    pill("badge-linkedin", "in", "LinkedIn", "badis-jilani", fill=PALETTE["linkedin"], stroke=PALETTE["linkedin"], label_color="#d6e6f8")
    pill("badge-mail", "mail", "Mail", "badis.jilani@gmail.com")
    pill("badge-location", "pin", "Location", "Paris, FR")
    pill("badge-status", "dot", "", "Open to internship · Summer 2027", fill=PALETTE["status"], stroke=PALETTE["status"])

    # contact buttons
    button("btn-linkedin", "in", "Connect on LinkedIn", PALETTE["linkedin"], PALETTE["linkedin"], "#ffffff")
    button("btn-email", "mail", "Send an email", PALETTE["base"], PALETTE["accent"], PALETTE["accent"])

    # stack chips
    for slug, label, dot in [
        ("claude-code", "Claude Code", "#D97757"),
        ("copilot", "GitHub Copilot", "#a371f7"),
        ("cursor", "Cursor", "#e6edf3"),
        ("n8n", "n8n", "#EA4B71"),
        ("azure-ai", "Azure AI Foundry", "#2f9bff"),
        ("power-automate", "Power Automate", "#3b82f6"),
        ("mcp", "MCP", "#34d399"),
        ("knime", "KNIME", "#FFD300"),
    ]:
        chip(f"chip-{slug}", label, dot)
    print("badges written to", OUT)
