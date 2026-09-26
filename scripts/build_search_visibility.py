#!/usr/bin/env python3
"""Build static search-engine metadata from the editorial HTML itself.

The visible title, description, category, publication date and topic chips are the
single source of truth.  The script materialises those values as static metadata,
Schema.org, sitemaps and RSS so no crawler has to execute JavaScript.
"""

from __future__ import annotations

import email.utils
import html
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from xml.sax.saxutils import escape

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://unosguardosulluomo.github.io/"
BRAND = "Uno Sguardo sull’Uomo"
ALIASES = ["UNO SGUARDO SULL'UOMO", "unosguardosulluomo"]
ORG_ID = SITE + "#organization"
WEB_ID = SITE + "#website"
LOGO = SITE + "assets/testata.webp"
FEED = SITE + "feed.xml"

CATEGORY_PATHS = {
    "Politica italiana": "archivio-politica-italiana.html",
    "Politica internazionale": "archivio-politica-internazionale.html",
    "Economia": "archivio-economia.html",
    "Società": "archivio-societa.html",
}

CATEGORY_DESCRIPTIONS = {
    "archivio-politica-internazionale.html": "Notizie, analisi e dossier di geopolitica, politica estera, guerre, difesa, energia, Unione europea e rapporti tra Stati.",
    "archivio-politica-italiana.html": "Notizie, analisi e dossier su Governo, Parlamento, partiti, istituzioni, amministrazioni e decisioni della politica italiana.",
    "archivio-economia.html": "Notizie, analisi e dossier su economia italiana, lavoro, energia, industria, imprese, finanza e conti pubblici.",
    "archivio-societa.html": "Notizie, analisi e dossier su società, sanità, diritti, sicurezza, tecnologia, giovani, lavoro e trasformazioni sociali.",
}

CATEGORY_TOPICS = {
    "archivio-politica-internazionale.html": ["Geopolitica", "Politica estera", "Guerre", "Difesa", "Esteri", "Unione europea", "Relazioni internazionali"],
    "archivio-politica-italiana.html": ["Politica italiana", "Governo", "Parlamento", "Partiti", "Istituzioni"],
    "archivio-economia.html": ["Economia", "Lavoro", "Energia", "Industria", "Imprese", "Finanza pubblica"],
    "archivio-societa.html": ["Società", "Sanità", "Diritti", "Sicurezza", "Tecnologia", "Giovani"],
}

MONTHS = {
    1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile", 5: "maggio",
    6: "giugno", 7: "luglio", 8: "agosto", 9: "settembre",
    10: "ottobre", 11: "novembre", 12: "dicembre",
}


def canonical_for(path: Path) -> str:
    return SITE if path.name == "index.html" else SITE + path.name


def first_git_date(path: Path) -> str:
    result = subprocess.run(
        ["git", "log", "--diff-filter=A", "--follow", "--format=%cs", "--", path.name],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    dates = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not dates:
        raise RuntimeError(f"Data di primo inserimento Git non trovata: {path.name}")
    return dates[-1]


def latest_git_date(path: Path) -> str:
    dirty = subprocess.run(
        ["git", "diff", "--quiet", "--", path.name], cwd=ROOT, check=False,
    ).returncode != 0
    if dirty:
        return datetime.now(timezone.utc).date().isoformat()
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", path.name],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    return result.stdout.strip() or datetime.now(timezone.utc).date().isoformat()


def meta(soup: BeautifulSoup, *, name: str | None = None, prop: str | None = None) -> str:
    attrs = {"name": name} if name else {"property": prop}
    node = soup.find("meta", attrs=attrs)
    return node.get("content", "").strip() if node else ""


def absolute(value: str) -> str:
    return urljoin(SITE, value)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def organisation() -> dict:
    return {
        "@type": ["Organization", "NewsMediaOrganization"],
        "@id": ORG_ID,
        "name": BRAND,
        "alternateName": ALIASES,
        "url": SITE,
        "description": "Testata editoriale indipendente italiana di approfondimento: indagini, dati, documenti e ricostruzione dei fatti oltre la narrazione.",
        "email": "mailto:unosguardosulluomo@gmail.com",
        "logo": {"@type": "ImageObject", "url": LOGO},
        "sameAs": [
            "https://www.facebook.com/profile.php?id=61593043131759",
            "https://www.linkedin.com/company/unosguardosulluomo/",
        ],
    }


def website() -> dict:
    return {
        "@type": "WebSite",
        "@id": WEB_ID,
        "url": SITE,
        "name": BRAND,
        "alternateName": ALIASES,
        "description": "Notizie, indagini e dossier su politica italiana, geopolitica, economia, società, guerre, esteri e istituzioni.",
        "publisher": {"@id": ORG_ID},
        "inLanguage": "it-IT",
    }


def breadcrumbs(items: list[tuple[str, str]]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": pos, "name": name, "item": url}
            for pos, (name, url) in enumerate(items, 1)
        ],
    }


def replace_or_insert_head(source: str, pattern: str, replacement: str) -> str:
    if re.search(pattern, source, flags=re.I | re.S):
        return re.sub(pattern, replacement, source, count=1, flags=re.I | re.S)
    return source.replace("</head>", replacement + "\n</head>", 1)


def normalise_article_date(source: str, published: str) -> str:
    date = datetime.strptime(published, "%Y-%m-%d")
    rendered = f"{date.day} {MONTHS[date.month]} {date.year}"

    def update(match: re.Match[str]) -> str:
        opening, body, closing = match.groups()
        if "current-date" in opening:
            return match.group(0)
        prefix = "Pubblicato: " if clean(BeautifulSoup(body, "html.parser").get_text()).lower().startswith("pubblicato:") else ""
        opening = re.sub(r'datetime="[^"]*"', f'datetime="{published}"', opening)
        return opening + prefix + rendered + closing

    return re.sub(r'(<time\b[^>]*datetime="[^"]*"[^>]*>)(.*?)(</time>)', update, source, flags=re.I | re.S)


def page_schema(path: Path, soup: BeautifulSoup, article_data: dict[str, dict]) -> tuple[dict, list[str]]:
    canonical = canonical_for(path)
    description = meta(soup, name="description")
    h1 = soup.find("h1")
    title = clean(h1.get_text(" ", strip=True)) if h1 else clean((soup.title.string if soup.title else BRAND))
    graph: list[dict] = [organisation(), website()]
    extra_meta: list[str] = []

    if path.name.startswith("article-"):
        category_node = soup.select_one("a.category-label")
        category = clean(category_node.get_text(" ", strip=True)) if category_node else ""
        if category not in CATEGORY_PATHS:
            raise RuntimeError(f"Categoria non riconosciuta in {path.name}: {category!r}")
        topics = [clean(node.get_text(" ", strip=True)) for node in soup.select(".topic-list span")]
        if not topics:
            raise RuntimeError(f"Argomenti mancanti in {path.name}")
        published = first_git_date(path)
        modified = meta(soup, prop="article:modified_time")[:10] or published
        if modified < published:
            modified = published
        image = meta(soup, prop="og:image") or LOGO
        article = soup.find("article")
        word_count = len(re.findall(r"\b[\wÀ-ÿ’'-]+\b", article.get_text(" ", strip=True) if article else ""))
        node = {
            "@type": "NewsArticle",
            "@id": canonical + "#article",
            "headline": title,
            "description": description,
            "url": canonical,
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
            "datePublished": published,
            "dateModified": modified,
            "image": [absolute(image)],
            "inLanguage": "it-IT",
            "isAccessibleForFree": True,
            "articleSection": category,
            "keywords": topics,
            "about": [{"@type": "Thing", "name": topic} for topic in topics],
            "wordCount": word_count,
            "author": {"@type": "Organization", "name": "Redazione Uno Sguardo sull’Uomo", "url": SITE + "chi-siamo.html"},
            "publisher": {"@id": ORG_ID},
            "isPartOf": {"@id": WEB_ID},
        }
        graph.extend([
            node,
            breadcrumbs([
                ("Prima pagina", SITE),
                (category, SITE + CATEGORY_PATHS[category]),
                (title, canonical),
            ]),
        ])
        article_data[path.name] = {
            "title": title, "description": description, "category": category,
            "topics": topics, "published": published, "modified": modified,
            "url": canonical, "image": absolute(image),
        }
        extra_meta.extend([
            f'<meta property="article:published_time" content="{published}">',
            f'<meta property="article:modified_time" content="{modified}">',
            f'<meta property="article:section" content="{html.escape(category, quote=True)}">',
            '<meta name="author" content="Redazione Uno Sguardo sull’Uomo">',
        ])
        extra_meta.extend(
            f'<meta property="article:tag" content="{html.escape(topic, quote=True)}">' for topic in topics
        )
    elif path.name == "index.html":
        graph.extend([
            {
                "@type": "WebPage", "@id": SITE + "#webpage", "url": SITE,
                "name": title, "description": description, "inLanguage": "it-IT",
                "isPartOf": {"@id": WEB_ID}, "about": [
                    {"@type": "Thing", "name": value} for value in
                    ["Politica italiana", "Geopolitica", "Politica internazionale", "Economia", "Società", "Guerre", "Esteri"]
                ],
            }
        ])
    else:
        page_types = {
            "chi-siamo.html": "AboutPage", "contatti.html": "ContactPage",
            "metodo.html": "WebPage", "indagini.html": "CollectionPage",
        }
        page_type = "CollectionPage" if path.name.startswith("archivio-") else page_types.get(path.name, "WebPage")
        page = {
            "@type": page_type, "@id": canonical + "#webpage", "url": canonical,
            "name": title, "description": description, "inLanguage": "it-IT",
            "isPartOf": {"@id": WEB_ID}, "publisher": {"@id": ORG_ID},
        }
        if page_type == "CollectionPage":
            seen: list[str] = []
            for link in soup.select('a[href^="article-"]'):
                href = link.get("href", "").split("#", 1)[0].split("?", 1)[0]
                if href in article_data and href not in seen:
                    seen.append(href)
            page["mainEntity"] = {
                "@type": "ItemList", "numberOfItems": len(seen),
                "itemListElement": [
                    {"@type": "ListItem", "position": i, "url": SITE + href,
                     "name": article_data[href]["title"]}
                    for i, href in enumerate(seen, 1)
                ],
            }
            if path.name in CATEGORY_TOPICS:
                page["about"] = [{"@type": "Thing", "name": topic} for topic in CATEGORY_TOPICS[path.name]]
        graph.append(page)
        graph.append(breadcrumbs([("Prima pagina", SITE), (title, canonical)]))

    return {"@context": "https://schema.org", "@graph": graph}, extra_meta


def update_html(path: Path, article_data: dict[str, dict]) -> None:
    source = path.read_text(encoding="utf-8")
    if not path.name.startswith("article-"):
        def update_card(match: re.Match[str]) -> str:
            block = match.group(0)
            href = re.search(r'href="(article-[^"]+\.html)', block, flags=re.I)
            if not href or href.group(1) not in article_data:
                return block
            published = article_data[href.group(1)]["published"]
            date = datetime.strptime(published, "%Y-%m-%d")
            rendered = f"{date.day} {MONTHS[date.month]} {date.year}"
            return re.sub(
                r'(<time\b[^>]*datetime=")[^"]*("[^>]*>).*?(</time>)',
                lambda time_match: time_match.group(1) + published + time_match.group(2) + rendered + time_match.group(3),
                block, flags=re.I | re.S,
            )
        source = re.sub(r'<article\b[^>]*>.*?</article>', update_card, source, flags=re.I | re.S)
    if path.name in CATEGORY_DESCRIPTIONS:
        description = CATEGORY_DESCRIPTIONS[path.name]
        source = re.sub(r'(<meta\b[^>]*name="description"[^>]*content=")[^"]*(")', rf'\1{description}\2', source, count=1, flags=re.I)
        source = re.sub(r'(<meta\b[^>]*property="og:description"[^>]*content=")[^"]*(")', rf'\1{description}\2', source, count=1, flags=re.I)
        source = re.sub(r'(<meta\b[^>]*name="twitter:description"[^>]*content=")[^"]*(")', rf'\1{description}\2', source, count=1, flags=re.I)
        if 'class="archive-page-lead"' not in source:
            source = re.sub(
                r'(<header class="archive-page-header"><h1>.*?</h1>)',
                rf'\1<p class="archive-page-lead">{description}</p>', source, count=1, flags=re.I | re.S,
            )
    soup = BeautifulSoup(source, "html.parser")
    schema, extra_meta = page_schema(path, soup, article_data)

    description = meta(soup, name="description")
    og_title = meta(soup, prop="og:title") or clean(soup.title.get_text(" ", strip=True))
    og_image = meta(soup, prop="og:image") or LOGO
    social_defaults = [
        (soup.find("meta", attrs={"property": "og:site_name"}), '<meta property="og:site_name" content="UNO SGUARDO SULL\'UOMO">'),
        (soup.find("meta", attrs={"name": "twitter:card"}), '<meta name="twitter:card" content="summary_large_image">'),
        (soup.find("meta", attrs={"name": "twitter:title"}), f'<meta name="twitter:title" content="{html.escape(og_title, quote=True)}">'),
        (soup.find("meta", attrs={"name": "twitter:description"}), f'<meta name="twitter:description" content="{html.escape(description, quote=True)}">'),
        (soup.find("meta", attrs={"name": "twitter:image"}), f'<meta name="twitter:image" content="{html.escape(absolute(og_image), quote=True)}">'),
    ]
    extra_meta[:0] = [markup for node, markup in social_defaults if not node]

    if path.name.startswith("article-"):
        category = article_data[path.name]["category"]
        category_path = CATEGORY_PATHS[category]
        source = re.sub(
            r'(<a\b[^>]*class="[^"]*category-label[^"]*"[^>]*href=")[^"]*("[^>]*>)',
            rf'\1{category_path}\2', source, count=1, flags=re.I,
        )
        source = normalise_article_date(source, article_data[path.name]["published"])

    source = re.sub(r'\s*<script\b[^>]*data-seo-schema[^>]*>.*?</script>', "", source, flags=re.I | re.S)
    source = re.sub(r'\s*<script\b[^>]*src="seo\.js[^\"]*"[^>]*></script>', "", source, flags=re.I)
    source = re.sub(r'\s*<meta\b[^>]*(?:property="article:(?:published_time|modified_time|section|tag)"|name="author")[^>]*>', "", source, flags=re.I)
    source = re.sub(r'\s*<link\b[^>]*type="application/rss\+xml"[^>]*>', "", source, flags=re.I)

    static = "\n  " + "\n  ".join(extra_meta + [
        f'<link rel="alternate" type="application/rss+xml" title="{BRAND}" href="{FEED}">',
        '<script type="application/ld+json" data-seo-schema>' +
        json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + '</script>',
    ])
    source = source.replace("</head>", static + "\n</head>", 1)
    for attempt in range(5):
        try:
            path.write_text(source, encoding="utf-8", newline="\n")
            break
        except OSError:
            if attempt == 4:
                raise
            time.sleep(0.25 * (attempt + 1))


def write_sitemaps(article_data: dict[str, dict], pages: list[Path]) -> None:
    articles = sorted(article_data.values(), key=lambda item: (item["published"], item["url"]), reverse=True)
    ordinary = [p for p in pages if not p.name.startswith("article-")]

    def urlset(rows: list[tuple[str, str, str | None]]) -> str:
        entries = []
        for url, lastmod, image in rows:
            image_xml = ""
            if image:
                image_xml = f"<image:image><image:loc>{escape(image)}</image:loc></image:image>"
            entries.append(f"  <url><loc>{escape(url)}</loc><lastmod>{lastmod}</lastmod>{image_xml}</url>")
        image_ns = ' xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"' if any(row[2] for row in rows) else ""
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"{image_ns}>\n' + "\n".join(entries) + "\n</urlset>\n"

    article_rows = [(a["url"], a["modified"], a["image"]) for a in articles]
    page_rows = [(canonical_for(p), latest_git_date(p), None) for p in ordinary]
    (ROOT / "sitemap-articles.xml").write_text(urlset(article_rows), encoding="utf-8", newline="\n")
    (ROOT / "sitemap-pages.xml").write_text(urlset(page_rows), encoding="utf-8", newline="\n")
    today = datetime.now(timezone.utc).date()
    recent = [item for item in articles if (today - datetime.fromisoformat(item["published"]).date()).days <= 2]
    news_rows = []
    for item in recent:
        news_rows.append(
            "  <url><loc>{url}</loc><news:news><news:publication>"
            "<news:name>{brand}</news:name><news:language>it</news:language>"
            "</news:publication><news:publication_date>{date}</news:publication_date>"
            "<news:title>{title}</news:title></news:news></url>".format(
                url=escape(item["url"]), brand=escape(BRAND), date=item["published"], title=escape(item["title"]),
            )
        )
    news_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n' + "\n".join(news_rows) + "\n</urlset>\n"
    (ROOT / "sitemap-news.xml").write_text(news_xml, encoding="utf-8", newline="\n")
    index = f'''<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>{SITE}sitemap-pages.xml</loc><lastmod>{max(row[1] for row in page_rows)}</lastmod></sitemap>
  <sitemap><loc>{SITE}sitemap-articles.xml</loc><lastmod>{max(row[1] for row in article_rows)}</lastmod></sitemap>
  <sitemap><loc>{SITE}sitemap-news.xml</loc><lastmod>{today.isoformat()}</lastmod></sitemap>
</sitemapindex>
'''
    for name in ["sitemap-index.xml", "sitemap.xml", "sitemap-google.xml"]:
        (ROOT / name).write_text(index, encoding="utf-8", newline="\n")


def write_feed(article_data: dict[str, dict]) -> None:
    articles = sorted(article_data.values(), key=lambda item: (item["published"], item["url"]), reverse=True)
    items = []
    for item in articles:
        pub_date = email.utils.format_datetime(datetime.fromisoformat(item["published"]).replace(tzinfo=timezone.utc))
        items.append(f'''    <item>
      <title>{escape(item["title"])}</title>
      <link>{escape(item["url"])}</link>
      <guid isPermaLink="true">{escape(item["url"])}</guid>
      <pubDate>{pub_date}</pubDate>
      <category>{escape(item["category"])}</category>
      <description>{escape(item["description"])}</description>
    </item>''')
    feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{BRAND}</title>
    <link>{SITE}</link>
    <description>Notizie, indagini e dossier indipendenti su politica, geopolitica, economia e società.</description>
    <language>it-IT</language>
    <atom:link href="{FEED}" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>
'''
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8", newline="\n")


def main() -> None:
    articles = sorted(ROOT.glob("article-*.html"))
    public_pages = [
        ROOT / name for name in [
            "index.html", "indagini.html", "archivio-politica-italiana.html",
            "archivio-politica-internazionale.html", "archivio-economia.html",
            "archivio-societa.html", "metodo.html", "chi-siamo.html", "contatti.html",
        ]
    ]
    article_data: dict[str, dict] = {}
    for path in articles:
        update_html(path, article_data)
    for path in public_pages:
        update_html(path, article_data)
    write_sitemaps(article_data, public_pages + articles)
    write_feed(article_data)
    print(f"Visibilità generata: {len(articles)} articoli, {len(public_pages)} pagine istituzionali.")


if __name__ == "__main__":
    main()
