"""Validate the Arctic dossier, its metadata, placements and local references."""

import json
import re
from html import unescape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "editorial/artico-nuova-via-seta.json").read_text(encoding="utf-8"))
PAGE_PATH = ROOT / DATA["slug"]
PAGE = PAGE_PATH.read_text(encoding="utf-8")
PUBLIC_URL = f'https://unosguardosulluomo.github.io/{DATA["slug"]}'

assert DATA["macroTopic"] == "Geopolitica"
assert DATA["category"] == "Politica internazionale"
assert DATA["datePublished"] == "2026-10-14"
assert DATA["dateModified"] == DATA["datePublished"]
assert DATA["seo"]["searchIntent"] == "informativo-approfondimento"
assert f'<link rel="canonical" href="{PUBLIC_URL}">' in PAGE
assert f'<meta property="og:url" content="{PUBLIC_URL}">' in PAGE
assert f'<meta property="article:published_time" content="{DATA["datePublished"]}">' in PAGE
assert f'<meta property="article:section" content="{DATA["category"]}">' in PAGE

assert PAGE.count('<figure class="article-') == 2
assert PAGE.count("Immagine prodotta da Uno Sguardo sull") == 2
assert 'width="1672" height="941"' in PAGE
assert PAGE.count('width="1672" height="941"') == 2

plain = unescape(re.sub(r"<[^>]+>", " ", PAGE))
for expansion in (
    "Organizzazione del Trattato dell'Atlantico del Nord (NATO)",
    "Costellazione di piccoli satelliti per l'osservazione del bacino del Mediterraneo (COSMO-SkyMed)",
    "Registro Italiano Navale (RINA)",
    "rete transeuropea dei trasporti (TEN-T)",
    "Ministero delle infrastrutture e dei trasporti (MIT)",
    "unità equivalenti a venti piedi (TEU)",
):
    assert expansion in plain, f"Missing acronym expansion: {expansion}"

assert "Il governo Meloni ha negoziato la nuova mappa TEN-T" in plain
assert "Oggi come allora, l'Italia c'è nella costruzione del nuovo ordine mondiale" in plain

table_html = re.search(r'<table class="data-table">(.*?)</table>', PAGE, re.S).group(1)
assert table_html.count('<th scope="col">') == 3
assert table_html.count("<tr>") == 5
for actor in ("Russia", "Cina", "NATO", "Italia"):
    assert f"<td>{actor}</td>" in table_html

sources_html = re.search(r'<ul class="sources-list">(.*?)</ul>', PAGE, re.S).group(1)
assert sources_html.count("<li>") == 25
assert "<a " not in sources_html
assert not re.search(r"https?://|www\.", sources_html)

for filename in (
    "index.html",
    "indagini.html",
    "archivio-politica-internazionale.html",
    "feed.xml",
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
assert {item["name"] for item in article["about"]} >= {"Geopolitica", "Politica internazionale"}

print("CONTROLLO DOSSIER ARTICO: OK")
