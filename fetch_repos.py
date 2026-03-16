"""
fetch_repos.py
--------------
Fetches public repos for GITHUB_USERNAME via the GitHub API
and writes a curated repos.json used by projects.html.

Run by GitHub Actions on every push to main.
Can also be run locally:
    GITHUB_USERNAME=Aboagye-Kwame-Appiah python scripts/fetch_repos.py
"""

import os
import json
import requests
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────────────────────

USERNAME = os.environ.get("GITHUB_USERNAME", "Aboagye-Kwame-Appiah")
TOKEN    = os.environ.get("GITHUB_TOKEN", "")   # injected by Actions; optional locally

# Repos to always pin at the top of the grid (by repo name, exact match)
PINNED = [
    "E-Commerce-Dashboard-Excel-",
    "Data_Driven_Production_Optimization",
    "E-commerce-Sales-Performance-Dashboard-Power-BI-",
    "Active-Product-Sales-Analysis",
    "Ghana_Adventures_Project",
    "TechSolutions_Ghana_Project",
]

# Repos to exclude entirely (e.g. the portfolio repo itself, forks, test repos)
EXCLUDE = [
    "KwameTheDataAnalyst.github.io",
    "Aboagye-Kwame-Appiah",          # profile README repo
]

# Map repo names → emoji icon used in the project cards
ICONS = {
    "E-Commerce-Dashboard-Excel-":                         "📊",
    "Data_Driven_Production_Optimization":                 "🏭",
    "E-commerce-Sales-Performance-Dashboard-Power-BI-":    "📈",
    "Active-Product-Sales-Analysis":                       "🐍",
    "Ghana_Adventures_Project":                            "🌍",
    "TechSolutions_Ghana_Project":                         "💼",
}
DEFAULT_ICON = "🔗"

# Map repo names → human-readable category label
CATEGORIES = {
    "E-Commerce-Dashboard-Excel-":                         "E-Commerce · Excel · BI",
    "Data_Driven_Production_Optimization":                 "Manufacturing · Python · Operations",
    "E-commerce-Sales-Performance-Dashboard-Power-BI-":    "E-Commerce · Power BI · Revenue",
    "Active-Product-Sales-Analysis":                       "Python · EDA · Sales",
    "Ghana_Adventures_Project":                            "Tourism · Power BI · Ghana",
    "TechSolutions_Ghana_Project":                         "B2B · Client Retention · BI",
}
DEFAULT_CATEGORY = "Data Analytics"

# ── Fetch ─────────────────────────────────────────────────────────────────────

headers = {"Accept": "application/vnd.github+json"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

all_repos = []
page = 1
while True:
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&sort=updated"
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    batch = resp.json()
    if not batch:
        break
    all_repos.extend(batch)
    page += 1

print(f"Fetched {len(all_repos)} repos for {USERNAME}")

# ── Filter ────────────────────────────────────────────────────────────────────

def clean_description(desc):
    """Return empty string instead of None."""
    return (desc or "").strip()

def format_date(iso_str):
    """2025-03-15T10:00:00Z  →  March 2025"""
    if not iso_str:
        return ""
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.strftime("%B %Y")

projects = []
for repo in all_repos:
    name = repo["name"]

    # Skip excluded, forked, or archived repos
    if name in EXCLUDE:
        continue
    if repo.get("fork"):
        continue
    if repo.get("archived"):
        continue

    projects.append({
        "name":        name,
        "display":     name.replace("-", " ").replace("_", " ").title(),
        "description": clean_description(repo.get("description")),
        "url":         repo["html_url"],
        "homepage":    repo.get("homepage") or "",
        "language":    repo.get("language") or "",
        "topics":      repo.get("topics") or [],
        "stars":       repo.get("stargazers_count", 0),
        "updated":     format_date(repo.get("updated_at")),
        "icon":        ICONS.get(name, DEFAULT_ICON),
        "category":    CATEGORIES.get(name, DEFAULT_CATEGORY),
        "pinned":      name in PINNED,
    })

# ── Sort: pinned first (in PINNED order), then by updated desc ────────────────

pinned_order = {name: i for i, name in enumerate(PINNED)}

def sort_key(p):
    if p["pinned"]:
        return (0, pinned_order.get(p["name"], 99))
    return (1, 0)   # non-pinned float below; JS will sort by date

projects.sort(key=sort_key)

# ── Write ─────────────────────────────────────────────────────────────────────

output = {
    "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "username":   USERNAME,
    "count":      len(projects),
    "projects":   projects,
}

out_path = os.path.join(os.path.dirname(__file__), "..", "repos.json")
out_path = os.path.normpath(out_path)

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(projects)} projects to {out_path}")
for p in projects:
    pin = "📌" if p["pinned"] else "  "
    print(f"  {pin} {p['name']}")
