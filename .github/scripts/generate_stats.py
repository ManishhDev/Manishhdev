import json
import os
import urllib.request
from html import escape
from pathlib import Path


TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ["GITHUB_USERNAME"]
API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get(path):
    request = urllib.request.Request(API + path, headers=HEADERS)
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def text(value):
    return escape(str(value))


def card(title, rows):
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="495" height="165" viewBox="0 0 495 165">',
        '<rect width="495" height="165" rx="8" fill="#0D1117"/>',
        '<rect x="0.5" y="0.5" width="494" height="164" rx="8" fill="none" stroke="#30363D"/>',
        f'<text x="24" y="35" fill="#60A5FA" font-family="Arial,sans-serif" font-size="18" font-weight="700">{text(title)}</text>',
    ]
    for index, (label, value) in enumerate(rows):
        x = 24 + (index % 3) * 157
        y = 82 + (index // 3) * 55
        lines.append(f'<text x="{x}" y="{y}" fill="#C9D1D9" font-family="Arial,sans-serif" font-size="24" font-weight="700">{text(value)}</text>')
        lines.append(f'<text x="{x}" y="{y + 22}" fill="#8B949E" font-family="Arial,sans-serif" font-size="12">{text(label)}</text>')
    lines.append("</svg>")
    return "\n".join(lines)


repos = get(f"/users/{USERNAME}/repos?per_page=100&type=owner")
languages = {}
stars = 0
for repo in repos:
    if not repo["fork"]:
        stars += repo["stargazers_count"]
        for language, amount in get(repo["languages_url"].replace(API, "")).items():
            languages[language] = languages.get(language, 0) + amount

top_languages = sorted(languages.items(), key=lambda item: item[1], reverse=True)[:5]
total_bytes = sum(amount for _, amount in top_languages) or 1
language_rows = [
    (language, f"{round(amount * 100 / total_bytes)}%")
    for language, amount in top_languages
]
while len(language_rows) < 6:
    language_rows.append(("", ""))

stats_rows = [
    ("Public repositories", len(repos)),
    ("Followers", get(f"/users/{USERNAME}")["followers"]),
    ("Stars earned", stars),
]

output = Path("assets")
output.mkdir(exist_ok=True)
(output / "github-stats.svg").write_text(card("GitHub Statistics", stats_rows), encoding="utf-8")
(output / "top-languages.svg").write_text(card("Most Used Languages", language_rows[:6]), encoding="utf-8")
