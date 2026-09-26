#!/usr/bin/env python3
"""Fail-fast checks for crawlability, metadata, Schema.org, sitemaps and links."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://unosguardosulluomo.github.io/"
ERRORS: list[str] = []
ARTICLE_DATES: dict[str, str] = {}


def fail(message: str) -> None:
    ERRORS.append(message)


def canonical_for(path: Path) -> str:
    return SITE if path.name == "index.html" else SITE + path.name


articles = sorted(ROOT.glob("article-*.html"))
pages = [
    ROOT / name for name in [
        "index.html", "indagini.html", "archivio-politica-italiana.html",
        "archivio-politica-internazionale.html", "archivio-economia.html",
        "archivio-societa.html", "metodo.html", "chi-siamo.html", "contatti.html",
    ]
]

for path in pages + articles:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    label = path.name
    required = [
        (soup.title and soup.title.get_text(strip=True), "title"),
        (soup.find("meta", attrs={"name": "description"}), "description"),
        (soup.find("meta", attrs={"name": "robots"}), "robots"),
        (soup.find("link", rel="canonical"), "canonical"),
        (soup.find("meta", attrs={"property": "og:title"}), "og:title"),
        (soup.find("meta", attrs={"property": "og:site_name"}), "og:site_name"),
        (soup.find("meta", attrs={"property": "og:description"}), "og:description"),
        (soup.find("meta", attrs={"property": "og:url"}), "og:url"),
        (soup.find("meta", attrs={"property": "og:image"}), "og:image"),
        (soup.find("meta", attrs={"name": "twitter:card"}), "twitter:card"),
        (soup.find("meta", attrs={"name": "twitter:title"}), "twitter:title"),
        (soup.find("meta", attrs={"name": "twitter:description"}), "twitter:description"),
        (soup.find("meta", attrs={"name": "twitter:image"}), "twitter:image"),
        (soup.find("link", attrs={"type": "application/rss+xml"}), "RSS autodiscovery"),
    ]
    for value, field in required:
        if not value:
            fail(f"{label}: {field} mancante")
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href") != canonical_for(path):
        fail(f"{label}: canonical incoerente")
    if soup.find("script", src=re.compile(r"seo\.js")):
        fail(f"{label}: dipendenza SEO JavaScript ancora presente")
    schemas = soup.select("script[data-seo-schema]")
    if len(schemas) != 1:
        fail(f"{label}: atteso un solo schema statico, trovati {len(schemas)}")
        continue
    try:
        schema = json.loads(schemas[0].string or "")
    except json.JSONDecodeError as exc:
        fail(f"{label}: JSON-LD non valido ({exc})")
        continue
    graph = schema.get("@graph", [])
    if not any("WebSite" in (node.get("@type") if isinstance(node.get("@type"), list) else [node.get("@type")]) for node in graph):
        fail(f"{label}: WebSite mancante nel grafo")

    if path.name.startswith("article-"):
        news = next((node for node in graph if node.get("@type") == "NewsArticle"), None)
        if not news:
            fail(f"{label}: NewsArticle mancante")
            continue
        ARTICLE_DATES[path.name] = news.get("datePublished", "")
        for field in ["headline", "description", "datePublished", "dateModified", "image", "articleSection", "keywords", "about", "author", "publisher", "wordCount"]:
            if not news.get(field):
                fail(f"{label}: NewsArticle.{field} mancante")
        visible_topics = [re.sub(r"\s+", " ", node.get_text(" ", strip=True)) for node in soup.select(".topic-list span")]
        if news.get("keywords") != visible_topics:
            fail(f"{label}: keywords non corrispondono agli argomenti visibili")
        if len(soup.find_all("meta", attrs={"property": "article:tag"})) != len(visible_topics):
            fail(f"{label}: article:tag incompleti")
        category = soup.select_one("a.category-label")
        if not category or not category.get("href", "").startswith("archivio-"):
            fail(f"{label}: link categoria non statico")

local_files = {path.name for path in ROOT.glob("*.html")} | {path.name for path in ROOT.glob("*.xml")}
for path in pages + articles:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"].split("#", 1)[0].split("?", 1)[0]
        if not href or href.startswith(("http://", "https://", "mailto:", "tel:")):
            continue
        if href.endswith(".html") and Path(href).name not in local_files:
            fail(f"{path.name}: link locale rotto {href}")

    listing_dates: list[str] = []
    for card in soup.select("article.archive-card"):
        link = card.find("a", href=re.compile(r"^article-.*\.html"))
        shown = card.find("time", attrs={"datetime": True})
        if not link or not shown:
            fail(f"{path.name}: scheda archivio senza URL o data")
            continue
        article_name = link["href"].split("#", 1)[0].split("?", 1)[0]
        expected = ARTICLE_DATES.get(article_name)
        if expected and shown.get("datetime") != expected:
            fail(f"{path.name}: data scheda incoerente per {article_name}")
        if expected:
            listing_dates.append(expected)
    if path.name.startswith("archivio-") and listing_dates != sorted(listing_dates, reverse=True):
        fail(f"{path.name}: archivio non ordinato dalla pubblicazione più recente")
    if path.name == "indagini.html":
        for section in soup.select("section.archive-section"):
            if len(section.select("article.archive-card")) != 3:
                fail("indagini.html: ogni categoria deve mostrare esattamente tre pubblicazioni")

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
try:
    index = ET.parse(ROOT / "sitemap-index.xml").getroot()
    children = [node.text for node in index.findall("sm:sitemap/sm:loc", NS)]
    expected_children = [SITE + "sitemap-pages.xml", SITE + "sitemap-articles.xml"]
    expected_children.append(SITE + "sitemap-news.xml")
    if children != expected_children:
        fail("sitemap-index.xml: elenco sitemap inatteso")
    urls: list[str] = []
    for name in ["sitemap-pages.xml", "sitemap-articles.xml"]:
        tree = ET.parse(ROOT / name).getroot()
        urls.extend(node.text or "" for node in tree.findall("sm:url/sm:loc", NS))
    expected_urls = {canonical_for(path) for path in pages + articles}
    if set(urls) != expected_urls or len(urls) != len(expected_urls):
        fail("sitemap: URL mancanti, duplicate o estranee")
except (ET.ParseError, FileNotFoundError) as exc:
    fail(f"sitemap XML non valida: {exc}")

try:
    news_root = ET.parse(ROOT / "sitemap-news.xml").getroot()
    news_urls = [node.text or "" for node in news_root.findall("sm:url/sm:loc", NS)]
    if not set(news_urls).issubset({canonical_for(path) for path in articles}):
        fail("sitemap-news.xml: contiene URL non editoriali")
except (ET.ParseError, FileNotFoundError) as exc:
    fail(f"sitemap-news.xml non valida: {exc}")

try:
    feed = ET.parse(ROOT / "feed.xml").getroot()
    if len(feed.findall("./channel/item")) != len(articles):
        fail("feed.xml: non contiene tutti gli articoli")
except (ET.ParseError, FileNotFoundError) as exc:
    fail(f"feed.xml non valido: {exc}")

robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
if SITE + "sitemap-index.xml" not in robots:
    fail("robots.txt: sitemap index non dichiarata")

if ERRORS:
    print("CONTROLLO VISIBILITÀ: FALLITO", file=sys.stderr)
    for error in ERRORS:
        print("- " + error, file=sys.stderr)
    raise SystemExit(1)
print(f"CONTROLLO VISIBILITÀ: OK — {len(articles)} articoli, {len(pages)} pagine, sitemap e feed coerenti.")
