"""Publication checks specific to the urban-legends dossier."""

from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SLUG = "article-geopolitica-societa-leggende-metropolitane-disinformazione-web.html"
page = BeautifulSoup((ROOT / SLUG).read_text(encoding="utf-8"), "html.parser")
text = page.get_text(" ", strip=True)

assert page.h1.get_text(" ", strip=True) == "La patria delle leggende metropolitane"
assert "Youssef Siher" in text and "48.000" in text and "11.000" in text
assert not any(name in text.casefold() for name in ("cyabra", "arcadia"))
assert len(page.select(".sources-list li")) == 16
assert not page.select(".sources a")
assert len(page.select(".related-dossiers a")) == 3
assert page.select_one('link[rel="canonical"]')["href"].endswith(SLUG)
assert page.select_one("article")["data-macro-topic"] == "Geopolitica"
assert page.select_one("article")["data-micro-topic"] == "Società"
assert all(image.get("width") and image.get("height") for image in page.select("img"))
assert all(
    figure.figcaption.get_text(" ", strip=True) == "Immagine prodotta da Uno Sguardo sull'Uomo"
    for figure in page.select("figure")
)

for image_name in (
    "assets/leggende-metropolitane-elefanti-volanti.webp",
    "assets/leggende-metropolitane-collage-notizie.webp",
):
    with Image.open(ROOT / image_name) as image:
        assert image.size == (1672, 941)

for file_name in (
    "index.html",
    "indagini.html",
    "archivio-societa.html",
    "feed.xml",
    "sitemap-articles.xml",
    "sitemap-news.xml",
    "search-index.json",
):
    assert SLUG in (ROOT / file_name).read_text(encoding="utf-8"), file_name

print("CONTROLLO DOSSIER LEGGENDE METROPOLITANE: OK")
