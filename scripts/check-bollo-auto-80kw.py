"""Static publication checks for a dossier generated from editorial JSON."""

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from lxml import etree, html
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "editorial/bollo-auto-80kw.json"
if not data_path.is_absolute():
    data_path = ROOT / data_path
DATA = json.loads(data_path.read_text(encoding="utf-8"))
ARTICLE = ROOT / DATA["slug"]
SITE = "https://unosguardosulluomo.github.io/"


def document(path):
    return html.fromstring(path.read_text(encoding="utf-8"))


article = document(ARTICLE)
assert len(article.xpath("//h1")) == 1
assert article.xpath("string(//h1)").strip() == DATA["title"]
assert article.xpath("string(//link[@rel='canonical']/@href)") == SITE + DATA["slug"]
assert article.xpath("string(//meta[@name='description']/@content)") == DATA["description"]
assert article.xpath("string(//meta[@property='og:image']/@content)") == SITE + DATA.get("socialImage", DATA["image"])
assert article.xpath("string(//meta[@property='article:published_time']/@content)") == DATA["datePublished"]
assert article.xpath("string(//meta[@property='article:section']/@content)") == DATA["category"]

schema = json.loads(article.xpath("string(//script[@type='application/ld+json'])"))
news_article = next(item for item in schema["@graph"] if item.get("@type") == "NewsArticle")
assert news_article["headline"] == DATA["title"]
assert news_article["datePublished"] == DATA["datePublished"]
assert news_article["articleSection"] == DATA["category"]

ids = article.xpath("//@id")
assert len(ids) == len(set(ids))
article_text = article.xpath("string(//article)")
for block in DATA["blocks"]:
    if "text" in block:
        assert block["text"] in article_text, block["text"][:80]
    for row in block.get("rows", []):
        for cell in row:
            assert cell in article_text, cell

source_section = article.xpath("//section[contains(concat(' ',normalize-space(@class),' '),' sources ')]")[0]
assert not source_section.xpath(".//a")
assert len(source_section.xpath(".//li")) == len(DATA["sources"])

for attribute in ("href", "src"):
    for value in article.xpath(f"//*[@{attribute}]/@{attribute}"):
        parsed = urlparse(value)
        if parsed.scheme or value.startswith("#") or value.startswith("mailto:") or value == "/":
            continue
        target = ROOT / parsed.path
        assert target.exists(), f"Missing local target: {value}"

for image_key in ("image", "socialImage"):
    if image_key not in DATA:
        continue
    with Image.open(ROOT / DATA[image_key]) as image:
        prefix = "socialImage" if image_key == "socialImage" else "image"
        assert image.size == (DATA[prefix + "Width"], DATA[prefix + "Height"])
for block in DATA["blocks"]:
    if block["kind"] == "figure":
        with Image.open(ROOT / block["image"]) as image:
            assert image.size == (block["width"], block["height"])

for filename in ("index.html", "indagini.html", DATA["categoryPath"]):
    doc = document(ROOT / filename)
    cards = doc.xpath(f"//article[@data-dossier='{DATA['slug']}']")
    assert len(cards) == 1, filename
    assert cards[0].xpath("string(.//time/@datetime)") == DATA["datePublished"]
    assert cards[0].xpath("string(.//img/@src)") == DATA["image"]

home = document(ROOT / "index.html")
home_cards = home.xpath(
    "//article["
    "contains(concat(' ',normalize-space(@class),' '),' lead-story ') or "
    "contains(concat(' ',normalize-space(@class),' '),' side-story ') or "
    "contains(concat(' ',normalize-space(@class),' '),' story-card ')"
    "]"
)
assert len(home_cards) == 9
home_dates = [card.xpath("string(.//time/@datetime)") for card in home_cards]
home_links = [card.xpath("string(.//a[contains(@class,'headline-link')]/@href)") for card in home_cards]
assert all(home_dates), "Every home card must show its publication date"
assert home_dates == sorted(home_dates, reverse=True), home_dates
assert len(home_links) == len(set(home_links)), home_links
if DATA["datePublished"] == max(home_dates):
    assert home.xpath("string(//article[contains(@class,'lead-story')][1]/@data-dossier)") == DATA["slug"]

for sitemap_name in ("sitemap.xml", "sitemap-google.xml"):
    tree = etree.parse(str(ROOT / sitemap_name))
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = tree.xpath("//s:loc/text()", namespaces=namespace)
    assert len(locations) == len(set(locations))
    assert locations.count(SITE + DATA["slug"]) == 1

assert "Testo pronto per pubblicazione" not in ARTICLE.read_text(encoding="utf-8")
assert "Dossier editoriale definitivo" not in ARTICLE.read_text(encoding="utf-8")

print(
    json.dumps(
        {
            "article": DATA["slug"],
            "blocks": len(DATA["blocks"]),
            "sources": len(DATA["sources"]),
            "readingMinutes": DATA["readingMinutes"],
            "images": 1 + int("socialImage" in DATA),
            "status": "ok",
        },
        ensure_ascii=False,
    )
)
