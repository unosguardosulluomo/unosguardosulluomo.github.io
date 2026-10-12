#!/usr/bin/env python3
"""Generate static, deterministic links between semantically related dossiers."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SECTION_RE = re.compile(
    r"\s*<section\b[^>]*class=\"[^\"]*\brelated-dossiers\b[^\"]*\"[^>]*>.*?</section>",
    flags=re.I | re.S,
)
SERIES_RE = re.compile(
    r"\s*<nav\b[^>]*class=\"[^\"]*\bdossier-series\b[^\"]*\"[^>]*>.*?</nav>",
    flags=re.I | re.S,
)
WORD_RE = re.compile(r"[\wÀ-ÿ]{4,}", flags=re.UNICODE)
STOPWORDS = {
    "alla", "alle", "anche", "come", "dalla", "delle", "della", "degli",
    "dello", "dietro", "italia", "italiana", "italiano", "nella", "nelle",
    "negli", "nello", "perché", "quale", "quello", "questa", "questo",
    "sono", "sulla", "sulle", "sugli", "sullo", "senza", "verso",
}
CATEGORY_ARCHIVES = {
    "Politica italiana": "archivio-politica-italiana.html",
    "Politica internazionale": "archivio-politica-internazionale.html",
    "Economia": "archivio-economia.html",
    "Società": "archivio-societa.html",
}


@dataclass(frozen=True)
class Dossier:
    path: Path
    title: str
    category: str
    topics: frozenset[str]
    title_terms: frozenset[str]
    published: str


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def title_terms(value: str) -> frozenset[str]:
    return frozenset(
        word.casefold()
        for word in WORD_RE.findall(value)
        if word.casefold() not in STOPWORDS
    )


def read_dossier(path: Path) -> Dossier:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    schema_node = soup.select_one("script[data-seo-schema]")
    if not schema_node:
        raise RuntimeError(f"Schema SEO mancante: {path.name}")
    schema = json.loads(schema_node.string or "")
    article = next(
        (node for node in schema.get("@graph", []) if node.get("@type") == "NewsArticle"),
        None,
    )
    if not article:
        raise RuntimeError(f"NewsArticle mancante: {path.name}")
    title = clean(article.get("headline", ""))
    topics = frozenset(clean(value).casefold() for value in article.get("keywords", []) if clean(value))
    return Dossier(
        path=path,
        title=title,
        category=clean(article.get("articleSection", "")),
        topics=topics,
        title_terms=title_terms(title),
        published=article.get("datePublished", ""),
    )


def score(source: Dossier, candidate: Dossier) -> tuple[int, str, str]:
    points = 8 if source.category == candidate.category else 0
    points += 3 * len(source.topics & candidate.topics)
    points += len(source.title_terms & candidate.title_terms)
    return points, candidate.published, candidate.path.name


def related_for(source: Dossier, dossiers: list[Dossier]) -> list[Dossier]:
    candidates = [item for item in dossiers if item.path != source.path]
    candidates.sort(key=lambda item: score(source, item), reverse=True)
    return candidates[:3]


def series_for(source: Dossier, dossiers: list[Dossier]) -> tuple[Dossier | None, Dossier | None]:
    category = sorted(
        (item for item in dossiers if item.category == source.category),
        key=lambda item: (item.published, item.path.name),
        reverse=True,
    )
    position = category.index(source)
    newer = category[position - 1] if position > 0 else None
    older = category[position + 1] if position + 1 < len(category) else None
    return newer, older


def render(items: list[Dossier]) -> str:
    links = "".join(
        "<li>"
        f'<a href="{html.escape(item.path.name, quote=True)}">{html.escape(item.title)}</a>'
        f'<span>{html.escape(item.category)}</span>'
        "</li>"
        for item in items
    )
    return (
        '<section class="related-dossiers" aria-labelledby="related-dossiers-heading">'
        '<h2 id="related-dossiers-heading">DOSSIER CORRELATI</h2>'
        f"<ul>{links}</ul>"
        "</section>"
    )


def render_series(source: Dossier, newer: Dossier | None, older: Dossier | None) -> str:
    archive = CATEGORY_ARCHIVES.get(source.category)
    if not archive:
        raise RuntimeError(f"Archivio mancante per la categoria {source.category!r}")
    links = []
    if newer:
        links.append(
            '<a class="dossier-series-link dossier-series-newer" rel="prev" '
            f'href="{html.escape(newer.path.name, quote=True)}">'
            '<span>Dossier più recente</span>'
            f'<strong>{html.escape(newer.title)}</strong></a>'
        )
    if older:
        links.append(
            '<a class="dossier-series-link dossier-series-older" rel="next" '
            f'href="{html.escape(older.path.name, quote=True)}">'
            '<span>Dossier precedente</span>'
            f'<strong>{html.escape(older.title)}</strong></a>'
        )
    return (
        '<nav class="dossier-series" aria-label="Continua nella categoria">'
        f'<a class="dossier-series-archive" href="{html.escape(archive, quote=True)}">'
        f'Tutti i dossier di {html.escape(source.category)}</a>'
        f'<div>{"".join(links)}</div></nav>'
    )


def update(source: Dossier, related: list[Dossier], newer: Dossier | None, older: Dossier | None) -> None:
    text = source.path.read_text(encoding="utf-8")
    text = SECTION_RE.sub("", text)
    text = SERIES_RE.sub("", text)
    section = render(related) + "\n" + render_series(source, newer, older)
    markers = [
        r'\s*(?=<section\b[^>]*class="[^"]*\bsources\b)',
        r'\s*(?=<section\b[^>]*class="[^"]*\bmethod-note\b)',
        r'\s*(?=</div>\s*</div>\s*</article>)',
        r'\s*(?=</article>)',
    ]
    for marker in markers:
        if re.search(marker, text, flags=re.I | re.S):
            text = re.sub(marker, "\n" + section + "\n", text, count=1, flags=re.I | re.S)
            source.path.write_text(text, encoding="utf-8", newline="\n")
            return
    raise RuntimeError(f"Punto di inserimento non trovato: {source.path.name}")


def main() -> None:
    paths = sorted(
        path
        for path in ROOT.glob("article-*.html")
        if "data-legacy-redirect" not in path.read_text(encoding="utf-8")[:1000]
    )
    dossiers = [read_dossier(path) for path in paths]
    if len(dossiers) < 4:
        raise RuntimeError("Servono almeno quattro dossier per generare i collegamenti correlati")
    for dossier in dossiers:
        newer, older = series_for(dossier, dossiers)
        update(dossier, related_for(dossier, dossiers), newer, older)
    print(
        f"Dossier correlati e navigazione di categoria generati: "
        f"{len(dossiers)} pagine, tre collegamenti correlati ciascuna."
    )


if __name__ == "__main__":
    main()
