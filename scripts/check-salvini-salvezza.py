"""Publication checks for the Salvini and Lega congress dossier."""

import re
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SLUG = "article-geopolitica-politica-italiana-salvini-salvezza-lega.html"
page = BeautifulSoup((ROOT / SLUG).read_text(encoding="utf-8"), "html.parser")
text = page.get_text(" ", strip=True)

assert page.h1.get_text(" ", strip=True) == "SALVINI E LA SALVEZZA CHE ANCORA NON ARRIVA…"
assert "Il ventiquattro per cento non è una perdita da recuperare" in text
assert "Zaia non è il capo del ventiquattro per cento" in text
assert not re.search(r"\[\d+\]", text)
assert len(page.select(".sources-list li")) == 18
assert not page.select(".sources a")
assert len(page.select(".related-dossiers a")) == 3
assert page.select_one('link[rel="canonical"]')["href"].endswith(SLUG)
assert page.select_one("article")["data-macro-topic"] == "Geopolitica"
assert page.select_one("article")["data-micro-topic"] == "Politica italiana"
assert all(image.get("width") and image.get("height") for image in page.select("img"))
assert page.select_one(".article-hero img").get("loading") != "lazy"
assert page.select_one(".article-inline-image img").get("loading") == "lazy"
assert all(
    figure.figcaption.get_text(" ", strip=True) == "Immagine prodotta da Uno Sguardo sull'Uomo"
    for figure in page.select("figure")
)

for image_name in ("assets/salvini-congresso-lega.webp", "assets/zaia-congresso-lega.webp"):
    with Image.open(ROOT / image_name) as image:
        assert image.size == (1672, 941)

for file_name in (
    "index.html",
    "indagini.html",
    "archivio-politica-italiana.html",
    "feed.xml",
    "sitemap-articles.xml",
    "sitemap-news.xml",
    "search-index.json",
):
    assert SLUG in (ROOT / file_name).read_text(encoding="utf-8"), file_name

print("CONTROLLO DOSSIER SALVINI E LEGA: OK")
