"""Regression checks for the Ravenna CPR dossier and its placements."""

import json
import re
from pathlib import Path

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "editorial/medici-sotto-torchio.json").read_text(encoding="utf-8"))

article_text = (ROOT / D["slug"]).read_text(encoding="utf-8")
article = html.fromstring(article_text)

assert article.xpath("string(//h1)").strip() == D["title"]
assert article.xpath("string(//p[contains(@class,'article-deck')])").strip() == D["deck"]
assert article.xpath("string(//link[@rel='canonical']/@href)") == "https://unosguardosulluomo.github.io/" + D["slug"]
assert article.xpath("string(//meta[@property='article:published_time']/@content)") == D["datePublished"]
assert article.xpath("string(//figure[contains(@class,'article-hero')]/img/@src)") == D["image"]
assert article.xpath("string(//figure[contains(@class,'article-hero')]/figcaption)").strip() == D["imageCaption"]
assert len(article.xpath("//table[contains(@class,'data-table')]/tbody/tr")) == 3
assert "Gli facciamo il culo a sti sbirri maledetti" in article_text
assert "La mafia paga chi piega una funzione dello Stato" in article_text
assert "Qui “mafioso” descrive il metodo e il comportamento" in article_text
assert "Non è una stima nazionale" in article_text
assert "giudice per le indagini preliminari (GIP)" in article_text
assert article_text.index("giudice per le indagini preliminari (GIP)") < article_text.index("ordinanza del GIP")

sources = article.xpath("//section[contains(@class,'sources')]")[0]
assert len(sources.xpath(".//li")) >= 20
assert not sources.xpath(".//a"), "Published sources must not expose clickable external URLs"

for filename in ("index.html", "indagini.html", D["categoryPath"]):
    document = html.fromstring((ROOT / filename).read_text(encoding="utf-8"))
    cards = document.xpath(f"//article[@data-dossier='{D['slug']}']")
    assert len(cards) == 1, filename
    assert cards[0].xpath("string(.//time/@datetime)") == D["datePublished"]
    assert cards[0].xpath("string(.//img/@src)") == D["image"]

archive = (ROOT / D["categoryPath"]).read_text(encoding="utf-8")
archive_grid = re.search(r'<div class="archive-grid">(.*?)</div>', archive, re.S).group(1)
assert archive_grid.index(D["slug"]) < archive_grid.index("article-elly-nome-garanzia.html")

indagini = (ROOT / "indagini.html").read_text(encoding="utf-8")
politics = re.search(r'href="archivio-politica-italiana.html">Politica italiana.*?<div class="archive-grid">(.*?)</div><a class="category-archive-link"', indagini, re.S).group(1)
assert politics.count('<article class="archive-card"') == 3
assert politics.index(D["slug"]) < politics.index("article-elly-nome-garanzia.html")

home = html.fromstring((ROOT / "index.html").read_text(encoding="utf-8"))
assert home.xpath("string(//article[contains(@class,'lead-story')]/@data-dossier)") == D["slug"]
assert len(home.xpath("//article[contains(@class,'lead-story') or contains(@class,'side-story') or contains(@class,'story-card')]")) == 9

print("Medici sotto torchio checks passed")
