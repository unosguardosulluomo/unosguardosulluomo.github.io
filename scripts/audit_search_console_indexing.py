#!/usr/bin/env python3
"""Compare the latest saved Search Console snapshot with the static HTML.

The source CSV files are exports saved under docs/search-console. This script
does not query Search Console and must be updated to point to each new monthly
snapshot.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://unosguardosulluomo.github.io/"
SNAPSHOT_DATE = "2026-11-22"
INDEX_REPORT_DATE = "2026-11-16"
PERFORMANCE_END_DATE = "2026-11-20"
SNAPSHOT = ROOT / "docs" / "search-console" / SNAPSHOT_DATE


def csv_names(path: Path, column: str) -> list[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            Path(urlparse(row[column]).path).name or "index.html"
            for row in csv.DictReader(handle)
            if row.get(column)
        ]


EXCLUDED = csv_names(SNAPSHOT / "indexing" / "Tabella.csv", "URL")
PERFORMANCE_PAGES = csv_names(SNAPSHOT / "performance" / "Pagine.csv", "Pagine principali")
INDEXED_ARTICLES = [name for name in PERFORMANCE_PAGES if name.startswith("article-")]
INDEXED_NON_ARTICLES = [name for name in PERFORMANCE_PAGES if not name.startswith("article-")]


def load(path: Path) -> BeautifulSoup:
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def canonical_name(soup: BeautifulSoup) -> str:
    node = soup.find("link", rel="canonical")
    return Path(urlparse(node.get("href", "")).path).name if node else ""


def inbound_counts() -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in ROOT.glob("*.html"):
        soup = load(path)
        for link in soup.find_all("a", href=True):
            href = link["href"].split("#", 1)[0].split("?", 1)[0]
            name = Path(urlparse(href).path).name
            if name.startswith("article-") and name != path.name:
                counts[name] += 1
    return counts


def metrics(name: str, incoming: Counter[str]) -> dict[str, object]:
    path = ROOT / name
    soup = load(path)
    title_text = soup.title.get_text(" ", strip=True) if soup.title else ""
    description_node = soup.find("meta", attrs={"name": "description"})
    description = description_node.get("content", "").strip() if description_node else ""
    schema_node = soup.select_one("script[data-seo-schema]")
    schema = json.loads(schema_node.string or "{}") if schema_node else {}
    article_schema = next(
        (node for node in schema.get("@graph", []) if node.get("@type") == "NewsArticle"),
        {},
    )
    source_items = soup.select("section.sources li")
    return {
        "name": name,
        "canonical": canonical_name(soup) == name,
        "title_text": title_text,
        "description_text": description,
        "title": len(title_text),
        "description": len(description),
        "words": int(article_schema.get("wordCount", 0)),
        "sources": len(source_items),
        "incoming": incoming[name],
        "home": bool(load(ROOT / "index.html").find("a", href=re.compile(re.escape(name)))),
        "indagini": bool(load(ROOT / "indagini.html").find("a", href=re.compile(re.escape(name)))),
        "archive": any(
            load(path).find("a", href=re.compile(re.escape(name)))
            for path in ROOT.glob("archivio-*.html")
        ),
    }


def median(values: list[int]) -> int:
    ordered = sorted(values)
    size = len(ordered)
    return ordered[size // 2] if size % 2 else round((ordered[size // 2 - 1] + ordered[size // 2]) / 2)


def print_group(label: str, rows: list[dict[str, object]]) -> None:
    print(f"\n## {label}\n")
    print("| URL | parole | fonti | link interni | home | indagini | archivio | canonical |")
    print("|---|---:|---:|---:|:---:|:---:|:---:|:---:|")
    for row in rows:
        yes = lambda value: "sì" if value else "no"
        print(
            f"| `{row['name']}` | {row['words']} | {row['sources']} | {row['incoming']} | "
            f"{yes(row['home'])} | {yes(row['indagini'])} | {yes(row['archive'])} | {yes(row['canonical'])} |"
        )


def main() -> None:
    incoming = inbound_counts()
    excluded = [metrics(name, incoming) for name in EXCLUDED]
    indexed = [metrics(name, incoming) for name in INDEXED_ARTICLES]

    print(f"# Audit indicizzazione Search Console — {SNAPSHOT_DATE}")
    print(f"\nSnapshot del report di indicizzazione aggiornato al {INDEX_REPORT_DATE} e del "
          f"rendimento aggiornato al {PERFORMANCE_END_DATE}. Le 12 URL indicizzate "
          "comprendono soltanto 3 dossier; le altre 9 sono home, archivi o pagine istituzionali.")
    print_group(f"Dossier scansionati ma non indicizzati ({len(excluded)})", excluded)
    print_group(f"Dossier indicizzati con impressioni ({len(indexed)})", indexed)
    print("\n## Confronto delle mediane\n")
    print("| gruppo | parole | fonti | link interni |")
    print("|---|---:|---:|---:|")
    for label, rows in [("non indicizzati", excluded), ("indicizzati", indexed)]:
        print(
            f"| {label} | {median([int(r['words']) for r in rows])} | "
            f"{median([int(r['sources']) for r in rows])} | "
            f"{median([int(r['incoming']) for r in rows])} |"
        )
    print("\n## Altre URL indicizzate (9)\n")
    for name in INDEXED_NON_ARTICLES:
        print(f"- `{SITE if name == 'index.html' else SITE + name}`")

    all_rows = [
        metrics(path.name, incoming)
        for path in ROOT.glob("article-*.html")
        if canonical_name(load(path)) == path.name
    ]
    duplicate_titles = [
        value for value, count in Counter(str(row["title_text"]) for row in all_rows).items()
        if value and count > 1
    ]
    duplicate_descriptions = [
        value for value, count in Counter(str(row["description_text"]) for row in all_rows).items()
        if value and count > 1
    ]
    print("\n## Controlli trasversali\n")
    print(f"- Titoli duplicati tra i dossier canonici: {len(duplicate_titles)}")
    print(f"- Descrizioni duplicate tra i dossier canonici: {len(duplicate_descriptions)}")


if __name__ == "__main__":
    main()
