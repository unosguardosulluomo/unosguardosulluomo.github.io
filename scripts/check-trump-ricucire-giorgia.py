"""Regression checks for the Trump, Meloni and diesel dossier."""

import json
import re
from pathlib import Path

from lxml import html
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "editorial/trump-ricucire-giorgia.json").read_text(encoding="utf-8"))

article_text = (ROOT / D["slug"]).read_text(encoding="utf-8")
article = html.fromstring(article_text)

assert article.xpath("string(//h1)").strip() == D["title"]
assert article.xpath("string(//p[contains(@class,'article-deck')])").strip() == D["deck"]
assert article.xpath("string(//link[@rel='canonical']/@href)") == "https://unosguardosulluomo.github.io/" + D["slug"]
assert article.xpath("string(//meta[@property='article:published_time']/@content)") == D["datePublished"]
assert article.xpath("string(//figure[contains(@class,'article-hero')]/img/@src)") == D["image"]
assert article.xpath("string(//figure[contains(@class,'article-hero')]/figcaption)").strip() == D["imageCaption"]
assert article.xpath("string(//figure[contains(@class,'article-inline-image')]/img/@src)") == D["secondaryImage"]
assert "Meloni non offre una ricucitura gratuita" in article_text
assert "non dimostra che Meloni abbia preteso delle scuse" in article_text
assert "agevolazione fiscale sulle accise" in article_text
assert "Gruppo dei Sette (G7)" in article_text
assert "gas naturale liquefatto (GNL)" in article_text
assert "Organismo centrale di stoccaggio italiano (OCSIT)" in article_text
assert "Ministero dell’economia e delle finanze (MEF)" in article_text
assert "Servizi assicurativi del commercio estero (SACE)" in article_text
assert "Geopolitica" in article.xpath("string(//nav[contains(@class,'topic-breadcrumb')])")
assert D["category"] in article.xpath("string(//nav[contains(@class,'topic-breadcrumb')])")

schema = json.loads(article.xpath("string(//script[@data-seo-schema])"))
news = next(item for item in schema["@graph"] if item.get("@type") == "NewsArticle")
assert news["datePublished"] == D["datePublished"]
assert news["articleSection"] == D["category"]
assert {item["name"] for item in news["about"]} >= {"Geopolitica", D["category"], "Eni", "Donald Trump", "Giorgia Meloni"}

sources = article.xpath("//section[contains(@class,'sources')]")[0]
assert len(sources.xpath(".//li")) == 28
assert not sources.xpath(".//a"), "Published sources must not expose clickable external URLs"

for image_key in ("image", "secondaryImage"):
    image_path = ROOT / D[image_key]
    assert image_path.exists(), image_path
    with Image.open(image_path) as asset:
        assert asset.size == (1672, 941), (image_key, asset.size)

for filename in ("index.html", "indagini.html", D["categoryPath"]):
    document = html.fromstring((ROOT / filename).read_text(encoding="utf-8"))
    cards = document.xpath(f"//article[@data-dossier='{D['slug']}']")
    assert len(cards) == 1, filename
    assert cards[0].xpath("string(.//time/@datetime)") == D["datePublished"]
    assert cards[0].xpath("string(.//img/@src)") == D["image"]

archive = (ROOT / D["categoryPath"]).read_text(encoding="utf-8")
archive_grid = re.search(r'<div class="archive-grid">(.*?)</div>', archive, re.S).group(1)
assert archive_grid.index(D["slug"]) < archive_grid.index("article-geopolitica-politica-internazionale-spagna-return-hub-ceuta.html")

indagini = (ROOT / "indagini.html").read_text(encoding="utf-8")
politics = re.search(r'<section class="archive-section"><div class="archive-section-header"><h2><a class="headline-link" href="archivio-politica-internazionale.html">Politica internazionale</a></h2></div><div class="archive-grid">(.*?)</div><a class="category-archive-link"', indagini, re.S).group(1)
assert politics.count('<article class="archive-card"') == 3
assert politics.index(D["slug"]) < politics.index("article-geopolitica-politica-internazionale-spagna-return-hub-ceuta.html")

home = html.fromstring((ROOT / "index.html").read_text(encoding="utf-8"))
assert home.xpath("string(//article[contains(@class,'lead-story')]/@data-dossier)") == D["slug"]
assert len(home.xpath("//article[contains(@class,'lead-story') or contains(@class,'side-story') or contains(@class,'story-card')]")) == 9

for filename in ("feed.xml", "sitemap-articles.xml", "sitemap-news.xml"):
    assert D["slug"] in (ROOT / filename).read_text(encoding="utf-8"), filename
for filename in ("sitemap.xml", "sitemap-google.xml", "sitemap-index.xml"):
    sitemap_index = (ROOT / filename).read_text(encoding="utf-8")
    assert "sitemap-articles.xml" in sitemap_index and "sitemap-news.xml" in sitemap_index, filename

print("Trump and Meloni dossier checks passed")
