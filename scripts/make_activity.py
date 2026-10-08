#!/usr/bin/env python3
"""Generates assets/activity.svg: an animated "productivity" card built from your GitHub contributions.

Usage:
  GITHUB_TOKEN=... GH_LOGIN=Badis-J python3 scripts/make_activity.py      # real data (used by the workflow)
  python3 scripts/make_activity.py --demo                                  # fake data, for local preview

Counts come from GitHub's contribution calendar, so private contributions are included only if
"Include private contributions on my profile" is enabled in your GitHub profile settings.
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "activity.svg"
FONT = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
GREEN, CYAN, MUTED, TEXT = "#00ff9c", "#58a6ff", "#6e7681", "#e6edf3"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-activity"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload or not payload.get("data", {}).get("user"):
        raise SystemExit(f"GraphQL error: {payload}")
    return payload["data"]["user"]["contributionsCollection"]


def demo() -> dict:
    random.seed(7)
    today = dt.date.today()
    start = today - dt.timedelta(days=370)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    weeks, d = [], start
    while d <= today:
        days = []
        for _ in range(7):
            n = 0 if d > today else max(0, int(random.gauss(2.2, 3.2))) if random.random() > 0.35 else 0
            days.append({"date": d.isoformat(), "contributionCount": n})
            d += dt.timedelta(days=1)
        weeks.append({"contributionDays": days})
    total = sum(x["contributionCount"] for w in weeks for x in w["contributionDays"])
    return {
        "totalCommitContributions": int(total * 0.8),
        "totalPullRequestContributions": 12,
        "totalPullRequestReviewContributions": 3,
        "totalIssueContributions": 4,
        "restrictedContributionsCount": 0,
        "contributionCalendar": {"totalContributions": total, "weeks": weeks},
    }


def stats(col: dict):
    days = [x for w in col["contributionCalendar"]["weeks"] for x in w["contributionDays"]]
    days = [x for x in days if x["date"] <= dt.date.today().isoformat()]
    counts = [x["contributionCount"] for x in days]
    # current streak (today may still be 0)
    cur = 0
    for c in reversed(counts[:-1] if counts and counts[-1] == 0 else counts):
        if c > 0:
            cur += 1
        else:
            break
    best = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        best = max(best, run)
    weekly = [sum(x["contributionCount"] for x in w["contributionDays"]) for w in col["contributionCalendar"]["weeks"]]
    busiest = max(days, key=lambda x: x["contributionCount"]) if days else {"date": "-", "contributionCount": 0}
    return cur, best, weekly, busiest


def render(col: dict) -> str:
    total = col["contributionCalendar"]["totalContributions"]
    cur, best, weekly, busiest = stats(col)
    weekly = weekly[-26:]
    W, H = 1000, 330
    peak = max(weekly) if weekly and max(weekly) > 0 else 1

    # stat tiles
    tiles = [
        ("contributions", f"{total}", "last 12 months"),
        ("commits", f"{col['totalCommitContributions']}", "pushed"),
        ("current streak", f"{cur}", "days"),
        ("longest streak", f"{best}", "days"),
    ]
    tile_svg = ""
    tw, gap, x0, y0 = 218, 16, 30, 66
    for i, (label, value, sub) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        d = 0.15 * i
        tile_svg += f"""
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{d}s" dur="0.5s" fill="freeze"/>
    <rect x="{x}" y="{y0}" width="{tw}" height="86" rx="10" fill="#ffffff" fill-opacity="0.04" stroke="{GREEN}" stroke-opacity="0.22"/>
    <text x="{x + 18}" y="{y0 + 26}" font-family="{FONT}" font-size="12" fill="{MUTED}">{label}</text>
    <text x="{x + 18}" y="{y0 + 62}" font-family="{FONT}" font-size="34" font-weight="700" fill="{GREEN}">{value}<tspan font-size="13" font-weight="400" fill="{MUTED}"> {sub}</tspan></text>
  </g>"""

    # weekly bars
    cx0, cy_base, ch = 30, 292, 100
    n = len(weekly)
    bw = (W - 60) / max(n, 1)
    bars = ""
    for i, v in enumerate(weekly):
        h = max(3, round(v / peak * ch, 1)) if v else 3
        x = round(cx0 + i * bw + 3, 1)
        w = round(bw - 6, 1)
        op = 0.35 + 0.65 * (v / peak) if v else 0.18
        bars += f"""
  <rect x="{x}" y="{cy_base}" width="{w}" height="0" rx="3" fill="{GREEN}" fill-opacity="{round(op, 2)}">
    <animate attributeName="height" from="0" to="{h}" begin="{round(0.35 + i * 0.045, 3)}s" dur="0.6s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>
    <animate attributeName="y" from="{cy_base}" to="{round(cy_base - h, 1)}" begin="{round(0.35 + i * 0.045, 3)}s" dur="0.6s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>
  </rect>"""

    busiest_txt = f"busiest day: {busiest['date']} · {busiest['contributionCount']} contributions"
    updated = dt.date.today().isoformat()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub activity: {total} contributions in the last 12 months">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0d1117"/>
      <stop offset="1" stop-color="#0b1f1a"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{GREEN}" stroke-opacity="0.25"/>

  <text x="30" y="38" font-family="{FONT}" font-size="15" fill="{GREEN}">$ <tspan fill="{TEXT}">git log --author="Badis-J" --since="12 months ago" --stat</tspan></text>
{tile_svg}

  <text x="30" y="{cy_base - ch - 16}" font-family="{FONT}" font-size="12" fill="{MUTED}">contributions per week · last {n} weeks</text>
  <text x="{W - 30}" y="{cy_base - ch - 16}" text-anchor="end" font-family="{FONT}" font-size="12" fill="{MUTED}">{busiest_txt}</text>
  <line x1="30" y1="{cy_base + 0.5}" x2="{W - 30}" y2="{cy_base + 0.5}" stroke="#ffffff" stroke-opacity="0.12"/>
{bars}
  <text x="{W - 30}" y="{H - 8}" text-anchor="end" font-family="{FONT}" font-size="10" fill="{MUTED}" fill-opacity="0.7">updated {updated}</text>
</svg>
"""


if __name__ == "__main__":
    if "--demo" in sys.argv:
        data = demo()
    else:
        token, login = os.environ.get("GITHUB_TOKEN"), os.environ.get("GH_LOGIN", "Badis-J")
        if not token:
            raise SystemExit("GITHUB_TOKEN is missing (or run with --demo)")
        data = fetch(login, token)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(data), encoding="utf-8")
    print("wrote", OUT)
