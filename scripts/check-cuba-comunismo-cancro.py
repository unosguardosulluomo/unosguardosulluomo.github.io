"""Validate the Cuba dossier, metadata, placements and local references."""

import json
import re
from html import unescape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "editorial/cuba-comunismo-cancro.json").read_text(encoding="utf-8"))
PAGE_PATH = ROOT / DATA["slug"]
PAGE = PAGE_PATH.read_text(encoding="utf-8")
PUBLIC_URL = f'https://unosguardosulluomo.github.io/{DATA["slug"]}'

assert DATA["macroTopic"] == "Geopolitica"
assert DATA["category"] == "Politica internazionale"
assert DATA["datePublished"] == "2026-11-13"
assert DATA["dateModified"] == DATA["datePublished"]
assert DATA["seo"]["searchIntent"] == "informativo-attualità"
assert len(DATA["seo"]["supportingQueries"]) >= 3
assert f'<link rel="canonical" href="{PUBLIC_URL}">' in PAGE
assert f'<meta property="og:url" content="{PUBLIC_URL}">' in PAGE
assert f'<meta property="article:published_time" content="{DATA["datePublished"]}">' in PAGE
assert f'<meta property="article:section" content="{DATA["category"]}">' in PAGE

assert PAGE.count('<figure class="article-') == 2
assert PAGE.count("Immagine prodotta da Uno Sguardo sull") == 2
assert PAGE.count('width="1672" height="941"') == 2
assert 'loading="lazy"' in PAGE
assert 'fetchpriority="high"' in PAGE

plain = unescape(re.sub(r"<[^>]+>", " ", PAGE))
assert "vecchie centrali termoelettriche alimentate con combustibili petroliferi pesanti" in plain
assert "alimentate a olio" not in plain
assert "Partito comunista di Cuba (PCC)" in plain
assert "Unità militari di aiuto alla produzione (UMAP)" in plain
assert "Grupo de Administración Empresarial S.A. (GAESA)" in plain
assert "Ufficio nazionale di statistica e informazione (ONEI)" in plain

sources_html = re.search(r'<ul class="sources-list">(.*?)</ul>', PAGE, re.S).group(1)
assert sources_html.count("<li>") >= 35
assert "<a " not in sources_html
assert not re.search(r"https?://|www\.", sources_html)

for filename in (
    "index.html",
    "indagini.html",
    "archivio-politica-internazionale.html",
    "ricerca-indagini.html",
    "search-index.json",
    "feed.xml",
    "sitemap.xml",
    "sitemap-articles.xml",
    "sitemap-news.xml",
):
    text = (ROOT / filename).read_text(encoding="utf-8")
    assert DATA["slug"] in text, f"Missing placement in {filename}"

for value in re.findall(r'(?:href|src)="([^"]+)"', PAGE):
    if not value or value.startswith(("http://", "https://", "mailto:", "#", "/")):
        continue
    target = ROOT / value.split("?", 1)[0]
    assert target.exists(), f"Broken local reference: {value}"

schema_text = re.search(
    r'<script type="application/ld\+json" data-seo-schema>(.*?)</script>', PAGE, re.S
).group(1)
schema = json.loads(schema_text)
article = next(item for item in schema["@graph"] if item.get("@type") == "NewsArticle")
assert article["datePublished"] == DATA["datePublished"]
assert article["dateModified"] == DATA["dateModified"]
assert article["articleSection"] == DATA["category"]
assert article["wordCount"] > 5000
assert {item["name"] for item in article["about"]} >= {"Geopolitica", "Politica internazionale", "Cuba"}

print("CONTROLLO DOSSIER CUBA: OK")
