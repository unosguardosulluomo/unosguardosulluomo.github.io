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
MACRO_TOPIC = "Geopolitica"
ERRORS: list[str] = []
ARTICLE_DATES: dict[str, str] = {}


def fail(message: str) -> None:
    ERRORS.append(message)


def canonical_for(path: Path) -> str:
    return SITE if path.name == "index.html" else SITE + path.name


def is_legacy_redirect(path: Path) -> bool:
    return "data-legacy-redirect" in path.read_text(encoding="utf-8")[:1000]


articles = sorted(path for path in ROOT.glob("article-*.html") if not is_legacy_redirect(path))
redirects = sorted(path for path in ROOT.glob("article-*.html") if is_legacy_redirect(path))
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
    if soup.find("meta", attrs={"name": re.compile(r"^keywords$", re.I)}):
        fail(f"{label}: meta keywords non ammesso")
    main_nav = soup.select_one("nav.nav")
    if not main_nav:
        fail(f"{label}: navigazione principale mancante")
    elif main_nav.find("a", href="geopolitica.html"):
        fail(f"{label}: collegamento ridondante alla pagina Geopolitica")
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
        seo_title = re.sub(r"\s+", " ", soup.title.get_text(" ", strip=True)) if soup.title else ""
        description_node = soup.find("meta", attrs={"name": "description"})
        description = description_node.get("content", "").strip() if description_node else ""
        if len(seo_title) > 70:
            fail(f"{label}: titolo SEO oltre 70 caratteri ({len(seo_title)})")
        if not 110 <= len(description) <= 165:
            fail(f"{label}: description fuori dall’intervallo 110-165 ({len(description)})")
        related = soup.select_one("section.related-dossiers")
        related_links = related.select('a[href^="article-"]') if related else []
        related_targets = [link.get("href", "").split("#", 1)[0].split("?", 1)[0] for link in related_links]
        if len(related_targets) != 3 or len(set(related_targets)) != 3:
            fail(f"{label}: servono tre dossier correlati distinti")
        if label in related_targets:
            fail(f"{label}: il blocco correlati contiene un collegamento a sé stesso")
        if any(len(re.sub(r"\s+", " ", link.get_text(" ", strip=True))) < 10 for link in related_links):
            fail(f"{label}: testo dei collegamenti correlati non descrittivo")
        for image in soup.find_all("img", src=True):
            src = image.get("src", "").split("?", 1)[0]
            if src.startswith(("http://", "https://", "data:", "/")):
                continue
            if (ROOT / src).is_file() and (not image.get("width") or not image.get("height")):
                fail(f"{label}: dimensioni mancanti per l’immagine locale {src}")
        news = next((node for node in graph if node.get("@type") == "NewsArticle"), None)
        if not news:
            fail(f"{label}: NewsArticle mancante")
            continue
        ARTICLE_DATES[path.name] = news.get("datePublished", "")
        for field in ["headline", "description", "datePublished", "dateModified", "image", "articleSection", "genre", "keywords", "about", "author", "publisher", "wordCount"]:
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
        category_name = category.get_text(" ", strip=True) if category else ""
        if news.get("articleSection") != category_name:
            fail(f"{label}: articleSection non coincide con il microargomento visibile")
        about_names = [item.get("name") for item in news.get("about", []) if isinstance(item, dict)]
        if MACRO_TOPIC not in about_names or category_name not in about_names:
            fail(f"{label}: macroargomento o microargomento mancanti in NewsArticle.about")
        if news.get("genre") != "Dossier geopolitico":
            fail(f"{label}: genere del dossier non coerente")
        article_node = soup.select_one("article.article-page")
        if not article_node or article_node.get("data-macro-topic") != MACRO_TOPIC or article_node.get("data-micro-topic") != category_name:
            fail(f"{label}: tassonomia visibile dell’articolo non coerente")
        visible_breadcrumb = soup.select_one("nav.topic-breadcrumb")
        breadcrumb_links = [link.get("href") for link in visible_breadcrumb.find_all("a")] if visible_breadcrumb else []
        breadcrumb_macro = visible_breadcrumb.select_one(".topic-breadcrumb-macro") if visible_breadcrumb else None
        if not breadcrumb_macro or breadcrumb_macro.get_text(" ", strip=True) != MACRO_TOPIC:
            fail(f"{label}: macroargomento visibile nel percorso tematico mancante")
        if breadcrumb_links != [category.get("href") if category else ""]:
            fail(f"{label}: percorso tematico visibile non coerente")
        breadcrumb_schema = next((node for node in graph if node.get("@type") == "BreadcrumbList"), None)
        breadcrumb_names = [item.get("name") for item in breadcrumb_schema.get("itemListElement", [])] if breadcrumb_schema else []
        if breadcrumb_names[:2] != ["Prima pagina", category_name]:
            fail(f"{label}: breadcrumb strutturato non coerente")

local_files = {path.name for path in ROOT.glob("*.html")} | {path.name for path in ROOT.glob("*.xml")}

for path in redirects:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    target = soup.find("meta", attrs={"http-equiv": re.compile(r"^refresh$", re.I)})
    canonical = soup.find("link", rel="canonical")
    if not target or "url=article-" not in target.get("content", ""):
        fail(f"{path.name}: reindirizzamento legacy mancante")
    if not canonical or canonical.get("href", "").replace(SITE, "") not in {item.name for item in articles}:
        fail(f"{path.name}: canonical legacy non valido")
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
