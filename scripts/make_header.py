#!/usr/bin/env python3
"""Generates assets/header.svg and assets/footer.svg (self-contained, animated, dark card).

Run once locally (python3 scripts/make_header.py) and commit the resulting SVG files.
No external service is used, so the banner never breaks and looks the same in light and dark mode.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

W, H = 1000, 240
FONT = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
GREEN = "#00ff9c"
CYAN = "#58a6ff"

LINES = [
    ("whoami", "CS engineering student @ CESI"),
    ("role", "Digital Innovation & Emerging Tech @ TDF"),
    ("stack", "LLMs · agents · automation · Kotlin"),
    ("status", "open to international internship 2027"),
]
SLOT = 4.5            # seconds per line
CYCLE = SLOT * len(LINES)
CHAR_W = 13.2         # px per char at font-size 22 (textLength forces this exactly)
FS = 22
X0 = 70
Y_LINE = 186


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def typed_line(i: int, key: str, value: str) -> str:
    prefix = f"> {key} → "
    text = prefix + value
    full = len(text) * CHAR_W
    # timeline over the whole cycle (keyTimes in 0..1)
    t0 = i * SLOT / CYCLE                 # starts typing
    t1 = t0 + (SLOT * 0.40) / CYCLE       # fully typed
    t2 = t0 + (SLOT * 0.93) / CYCLE       # starts disappearing (hold)
    t3 = (i + 1) * SLOT / CYCLE           # gone
    kt = [0, t0, t1, t2, t3, 1]
    kt = sorted(set(round(k, 5) for k in kt))
    # build values aligned with keyTimes
    def width_at(k):
        if k <= t0:
            return 0
        if k >= t3:
            return 0
        if k >= t1 and k <= t2:
            return full + 4
        if k < t1:
            return full + 4
        return 0
    vals = []
    for k in kt:
        if k <= t0 or k >= t3:
            vals.append(0)
        else:
            vals.append(round(full + 4, 1))
    # first line must be at 0 at time 0 and type from t0; ensure linear growth t0->t1
    kt_s = ";".join(str(k) for k in kt)
    v_s = ";".join(str(v) for v in vals)
    cid = f"clip{i}"
    cur_vals = ";".join(str(round(X0 + (v if v else 0), 1)) for v in vals)
    return f"""
  <clipPath id="{cid}"><rect x="{X0 - 2}" y="{Y_LINE - 30}" width="0" height="42">
    <animate attributeName="width" dur="{CYCLE}s" repeatCount="indefinite" calcMode="linear"
      keyTimes="{kt_s}" values="{v_s}"/>
  </rect></clipPath>
  <g clip-path="url(#{cid})">
    <text x="{X0}" y="{Y_LINE}" font-family="{FONT}" font-size="{FS}" textLength="{round(full, 1)}" lengthAdjust="spacing">
      <tspan fill="{GREEN}">&gt; {esc(key)} </tspan><tspan fill="#6e7681">→ </tspan><tspan fill="#e6edf3">{esc(value)}</tspan>
    </text>
  </g>
  <rect x="{X0}" y="{Y_LINE - 22}" width="11" height="26" fill="{GREEN}" opacity="0">
    <animate attributeName="x" dur="{CYCLE}s" repeatCount="indefinite" calcMode="linear"
      keyTimes="{kt_s}" values="{cur_vals}"/>
    <animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" calcMode="discrete"
      keyTimes="0;{round(t0, 5)};{round(t3, 5)};1" values="0;0.9;0;0"/>
  </rect>"""


def header() -> str:
    lines = "".join(typed_line(i, k, v) for i, (k, v) in enumerate(LINES))
    # fix: first line keyTimes must start at 0 – handled by set/sorted above
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Badis JILANI — augmented developer, AI and emerging tech">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0d1117"/>
      <stop offset="0.6" stop-color="#0b1f1a"/>
      <stop offset="1" stop-color="#0b3d2e"/>
    </linearGradient>
    <linearGradient id="title" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="1" stop-color="{GREEN}"/>
    </linearGradient>
    <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M28 0H0V28" fill="none" stroke="#ffffff" stroke-opacity="0.045" stroke-width="1"/>
    </pattern>
    <radialGradient id="glow" cx="0.9" cy="0.1" r="0.7">
      <stop offset="0" stop-color="{GREEN}" stop-opacity="0.22"/>
      <stop offset="1" stop-color="{GREEN}" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" rx="14" fill="url(#grid)"/>
  <rect width="{W}" height="{H}" rx="14" fill="url(#glow)"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{GREEN}" stroke-opacity="0.25"/>

  <!-- window chrome -->
  <circle cx="34" cy="30" r="6" fill="#ff5f56"/>
  <circle cx="56" cy="30" r="6" fill="#ffbd2e"/>
  <circle cx="78" cy="30" r="6" fill="#27c93f"/>
  <text x="{W - 30}" y="35" text-anchor="end" font-family="{FONT}" font-size="13" fill="#6e7681">badis@cesi: ~/profile</text>

  <!-- title -->
  <text x="{X0 - 4}" y="105" font-family="{FONT}" font-size="58" font-weight="700" fill="url(#title)" letter-spacing="1">BADIS JILANI</text>
  <text x="{X0}" y="136" font-family="{FONT}" font-size="16" fill="{CYAN}" fill-opacity="0.9">augmented_developer<tspan fill="#6e7681"> // </tspan>ai &amp; emerging tech</text>
{lines}
</svg>
"""


def footer() -> str:
    w, h = 1000, 70
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="footer">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#0d1117"/>
      <stop offset="1" stop-color="#0b3d2e"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" rx="12" fill="url(#bg)"/>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="{GREEN}" stroke-opacity="0.25"/>
  <text x="30" y="42" font-family="{FONT}" font-size="16" fill="{GREEN}">$ <tspan fill="#e6edf3">exit 0</tspan><tspan fill="#6e7681">   # thanks for stopping by</tspan></text>
  <rect x="{w - 40}" y="26" width="10" height="20" fill="{GREEN}">
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/>
  </rect>
</svg>
"""


if __name__ == "__main__":
    (OUT / "header.svg").write_text(header(), encoding="utf-8")
    (OUT / "footer.svg").write_text(footer(), encoding="utf-8")
    print("wrote", OUT / "header.svg", OUT / "footer.svg")
