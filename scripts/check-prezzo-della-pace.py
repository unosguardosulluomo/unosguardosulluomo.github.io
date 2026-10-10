"""Regression checks for the Trump-Putin peace dossier."""

import json
from pathlib import Path
from xml.etree import ElementTree

from lxml import html
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "editorial/prezzo-della-pace.json").read_text(encoding="utf-8"))
SITE = "https://unosguardosulluomo.github.io/"

article_text = (ROOT / D["slug"]).read_text(encoding="utf-8")
article = html.fromstring(article_text)
visible = " ".join(article.text_content().split())

assert article.xpath("string(//h1)").strip() == D["title"]
assert article.xpath("string(//title)").startswith(D["seoTitle"])
assert article.xpath("string(//p[contains(@class,'article-deck')])").strip() == D["deck"]
assert article.xpath("string(//p[contains(@class,'article-lead')])").strip() == D["lead"]
assert article.xpath("string(//link[@rel='canonical']/@href)") == SITE + D["slug"]
assert article.xpath("string(//meta[@property='article:published_time']/@content)") == D["datePublished"]
assert article.xpath("string(//meta[@property='article:modified_time']/@content)") == D["dateModified"]
assert article.xpath("string(//figure[contains(@class,'article-hero')]/img/@src)") == D["image"]
assert article.xpath("string(//figure[contains(@class,'article-inline-image')]/img/@src)") == D["secondaryImage"]
assert all(caption.strip() == D["imageCaption"] for caption in article.xpath("//figcaption/text()"))
assert len(article.xpath("//section[contains(@class,'sources')]//li")) == 16
assert not article.xpath("//section[contains(@class,'sources')]//a")
assert "https://" not in article.xpath("string(//section[contains(@class,'sources')])")
assert "Central Intelligence Agency" not in visible and "CIA" not in visible

for required in (
    "Office of Foreign Assets Control (OFAC)",
    "Unione europea (UE)",
    "Organizzazione del Trattato dell’Atlantico del Nord (NATO)",
    "prodotto interno lordo (PIL)",
    "Qui è necessario distinguere il fatto dallo scenario.",
    "Da qui in avanti entriamo nel campo degli scenari",
    "La nostra tesi: la biodiversità delle nazioni",
    "Come l’iPhone nel mercato degli smartphone",
):
    assert required in visible, required

schema = json.loads(article.xpath("string(//script[@data-seo-schema])"))
news = next(item for item in schema["@graph"] if item.get("@type") == "NewsArticle")
assert news["datePublished"] == D["datePublished"]
assert news["dateModified"] == D["dateModified"]
assert news["articleSection"] == D["category"]
assert news["keywords"] == D["tags"]
assert {item["name"] for item in news["about"]} >= {"Geopolitica", D["category"], "Donald Trump", "Vladimir Putin"}

for image_key in ("image", "secondaryImage"):
    with Image.open(ROOT / D[image_key]) as asset:
        assert asset.size == (D[image_key + "Width"], D[image_key + "Height"])

for filename in ("index.html", "indagini.html", D["categoryPath"]):
    document = html.fromstring((ROOT / filename).read_text(encoding="utf-8"))
    cards = document.xpath(f"//article[@data-dossier='{D['slug']}']")
    assert len(cards) == 1, filename
    assert cards[0].xpath("string(.//time/@datetime)") == D["datePublished"]

archive_doc = html.fromstring((ROOT / D["categoryPath"]).read_text(encoding="utf-8"))
archive_cards = archive_doc.xpath("//div[contains(@class,'archive-grid')]/article")
archive_dates = [card.xpath("string(.//time/@datetime)") for card in archive_cards]
assert archive_dates == sorted(archive_dates, reverse=True)

indagini_doc = html.fromstring((ROOT / "indagini.html").read_text(encoding="utf-8"))
politics = indagini_doc.xpath("//section[.//a[@href='archivio-politica-internazionale.html']]/div[contains(@class,'archive-grid')]/article")
assert len(politics) == 3
assert politics[0].get("data-dossier") == D["slug"]

home_doc = html.fromstring((ROOT / "index.html").read_text(encoding="utf-8"))
assert home_doc.xpath("string(//article[contains(@class,'lead-story')]/@data-dossier)") == D["slug"]

for filename in ("feed.xml", "sitemap-articles.xml", "sitemap-news.xml", "sitemap-pages.xml", "sitemap.xml", "sitemap-google.xml", "sitemap-index.xml"):
    ElementTree.parse(ROOT / filename)
assert D["slug"] in (ROOT / "feed.xml").read_text(encoding="utf-8")
assert D["slug"] in (ROOT / "sitemap-articles.xml").read_text(encoding="utf-8")
assert D["slug"] in (ROOT / "sitemap-news.xml").read_text(encoding="utf-8")

for element in article.xpath("//*[@href or @src]"):
    target = element.get("href") or element.get("src")
    if not target or target.startswith(("http://", "https://", "mailto:", "#", "/")):
        continue
    assert (ROOT / target.split("?", 1)[0]).exists(), target

print("Trump-Putin peace dossier checks passed")
