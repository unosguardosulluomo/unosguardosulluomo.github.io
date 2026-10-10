"""Regression checks for the Povertà Contagiosa dossier."""

import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from lxml import etree, html
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "editorial/sindacato-vampiro.json").read_text(encoding="utf-8"))
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
assert len(article.xpath("//section[contains(@class,'sources')]//li")) == 11
assert not article.xpath("//section[contains(@class,'sources')]//a")
assert "https://" not in article.xpath("string(//section[contains(@class,'sources')])")
assert "suocero" not in visible.casefold()
assert "mia moglie" not in visible.casefold()

for required in (
    "Istituto nazionale di statistica (ISTAT)",
    "Istituto nazionale della previdenza sociale (INPS)",
    "centri di assistenza fiscale (CAF)",
    "Buoni ordinari del Tesoro (BOT)",
    "Cassa depositi e prestiti (CDP)",
    "514,59 milioni di euro",
    "Caritas incontra e accompagna le persone",
    "Banco Alimentare rifornisce gli enti che distribuiscono il cibo",
    "La quattordicesima sociale: una proposta, non una legge in vigore",
):
    assert required in visible, required

with zipfile.ZipFile(ROOT / D["sourceDocx"]) as package:
    source_root = etree.fromstring(package.read("word/document.xml"))
publishing = False
namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
for paragraph in source_root.xpath("//w:body/w:p", namespaces=namespaces):
    text = " ".join("".join(paragraph.xpath(".//w:t/text()", namespaces=namespaces)).split())
    if text.casefold() == "scheda editoriale per codex":
        break
    if text == "Cinque milioni e settecentomila persone. E qualcuno deve aiutarle":
        publishing = True
    if publishing and text and text.casefold() != "fonti":
        assert text in visible, text[:120]

schema = json.loads(article.xpath("string(//script[@data-seo-schema])"))
news = next(item for item in schema["@graph"] if item.get("@type") == "NewsArticle")
assert news["datePublished"] == D["datePublished"]
assert news["dateModified"] == D["dateModified"]
assert news["articleSection"] == D["category"]
assert news["keywords"] == D["tags"]
assert {item["name"] for item in news["about"]} >= {"Geopolitica", D["category"], "Pensioni", "Trattenute sindacali"}

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
society = indagini_doc.xpath("//section[.//a[@href='archivio-societa.html']]/div[contains(@class,'archive-grid')]/article")
assert len(society) == 3
assert society[0].get("data-dossier") == D["slug"]

home_doc = html.fromstring((ROOT / "index.html").read_text(encoding="utf-8"))
assert len(home_doc.xpath(f"//article[@data-dossier='{D['slug']}']")) == 1

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

print("Povertà Contagiosa dossier checks passed")
