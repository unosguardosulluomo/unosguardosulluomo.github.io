#!/usr/bin/env python3
"""Compare Search Console indexing examples with the current static HTML.

The URL groups below reproduce the Search Console report last updated on
2026-10-12 and inspected on 2026-10-15.  This is an evidence snapshot, not a
live Search Console client.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://unosguardosulluomo.github.io/"

EXCLUDED = [
    "article-geopolitica-politica-internazionale-trump-putin-quaranta-anni-parallelo.html",
    "article-crescere-con-uno-schermo-in-mano.html",
    "article-re-carlo-propaganda-militare.html",
    "article-geopolitica-politica-internazionale-spagna-return-hub-ceuta.html",
    "article-pickpocket-venezia.html",
    "article-politica-italiana-societa-immigrazione-cpr-medici-ravenna.html",
    "article-due-pesi-due-misure.html",
    "article-economia-fisco-societa-1973-iva-vita-italiani.html",
    "article-geopolitica-politica-internazionale-trump-putin-prezzo-pace.html",
    "article-geopolitica-societa-poverta-contagiosa.html",
]

INDEXED_ARTICLES = [
    "article-aler-lombardia.html",
    "article-sigfrido-ultima-battaglia.html",
    "article-dublinati.html",
]

INDEXED_NON_ARTICLES = [
    "index.html",
    "contatti.html",
    "archivio-politica-internazionale.html",
    "indagini.html",
    "archivio-politica-italiana.html",
    "archivio-economia.html",
    "archivio-societa.html",
    "chi-siamo.html",
    "metodo.html",
]


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

    print("# Audit indicizzazione Search Console — 15 ottobre 2026")
    print("\nSnapshot del report aggiornato al 12 ottobre 2026. Le 12 URL indicizzate "
          "comprendono soltanto 3 dossier; le altre 9 sono home, archivi o pagine istituzionali.")
    print_group("Dossier scansionati ma non indicizzati (10)", excluded)
    print_group("Dossier indicizzati mostrati dal report (3)", indexed)
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
