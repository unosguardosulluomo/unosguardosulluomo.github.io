"""Regression checks for the Spain, return-hub and Ceuta dossier."""

import json
import re
from pathlib import Path

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "editorial/due-piedi-in-una-scarpa.json").read_text(encoding="utf-8"))

article_text = (ROOT / D["slug"]).read_text(encoding="utf-8")
article = html.fromstring(article_text)

assert article.xpath("string(//h1)").strip() == D["title"]
assert article.xpath("string(//p[contains(@class,'article-deck')])").strip() == D["deck"]
assert article.xpath("string(//link[@rel='canonical']/@href)") == "https://unosguardosulluomo.github.io/" + D["slug"]
assert article.xpath("string(//meta[@property='article:published_time']/@content)") == D["datePublished"]
assert article.xpath("string(//figure[contains(@class,'article-hero')]/img/@src)") == D["image"]
assert article.xpath("string(//figure[contains(@class,'article-hero')]/figcaption)").strip() == D["imageCaption"]
assert article.xpath("string(//figure[contains(@class,'article-inline-image')]/img/@src)") == D["secondaryImage"]
assert len(article.xpath("//blockquote[contains(@class,'article-pullquote')]")) == 3
assert "63.000 persone erano tornate in Marocco" in article_text
assert "Consiglio dell’Unione europea (UE)" in article_text
assert "PSOE" in article_text and "Socialista Obrero" in article_text
assert "Organizzazione internazionale per le migrazioni (IOM)" in article_text
assert "Fondo delle Nazioni Unite per l’infanzia (UNICEF)" in article_text
assert "Geopolitica" in article.xpath("string(//nav[contains(@class,'topic-breadcrumb')])")
assert D["category"] in article.xpath("string(//nav[contains(@class,'topic-breadcrumb')])")

sources = article.xpath("//section[contains(@class,'sources')]")[0]
assert len(sources.xpath(".//li")) == 12
assert not sources.xpath(".//a"), "Published sources must not expose clickable external URLs"

for filename in ("index.html", "indagini.html", D["categoryPath"]):
    document = html.fromstring((ROOT / filename).read_text(encoding="utf-8"))
    cards = document.xpath(f"//article[@data-dossier='{D['slug']}']")
    assert len(cards) == 1, filename
    assert cards[0].xpath("string(.//time/@datetime)") == D["datePublished"]
    assert cards[0].xpath("string(.//img/@src)") == D["image"]

archive = (ROOT / D["categoryPath"]).read_text(encoding="utf-8")
archive_grid = re.search(r'<div class="archive-grid">(.*?)</div>', archive, re.S).group(1)
assert archive_grid.index(D["slug"]) < archive_grid.index("article-stati-uniti-ancora-indispensabili.html")

indagini = (ROOT / "indagini.html").read_text(encoding="utf-8")
politics = re.search(r'<section class="archive-section"><div class="archive-section-header"><h2><a class="headline-link" href="archivio-politica-internazionale.html">Politica internazionale</a></h2></div><div class="archive-grid">(.*?)</div><a class="category-archive-link"', indagini, re.S).group(1)
assert politics.count('<article class="archive-card"') == 3
assert politics.index(D["slug"]) < politics.index("article-stati-uniti-ancora-indispensabili.html")

home = html.fromstring((ROOT / "index.html").read_text(encoding="utf-8"))
assert home.xpath("string(//article[contains(@class,'lead-story')]/@data-dossier)") == D["slug"]
assert len(home.xpath("//article[contains(@class,'lead-story') or contains(@class,'side-story') or contains(@class,'story-card')]")) == 9

print("Due piedi in una scarpa checks passed")
