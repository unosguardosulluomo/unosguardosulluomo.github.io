"""Publication checks for the Verdi in canna dossier."""

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SLUG = "article-geopolitica-politica-italiana-programma-avs-cannabis.html"
URL = "https://unosguardosulluomo.github.io/" + SLUG
META = json.loads((ROOT / "editorial/verdi-in-canna-avs-cannabis.json").read_text(encoding="utf-8"))
page = BeautifulSoup((ROOT / SLUG).read_text(encoding="utf-8"), "html.parser")
text = page.get_text(" ", strip=True)

assert page.h1.get_text(" ", strip=True) == "VERDI IN CANNA: IL PROGRAMMA AVS SULLA CANNABIS"
assert page.select_one(".article-deck") is None
assert page.select_one(".article-lead") is None
hero = page.select_one(".article-hero")
body = page.select_one(".article-body")
assert hero is not None and body is not None
assert body.find("h2").get_text(" ", strip=True) == "Venghino, signori, venghino"
assert "L'isola felice ha sempre una produzione" in text
assert "Quattro piante: una cifra piccola soltanto sulla carta" in text
assert "L'alternativa: monopolio pubblico e filiera controllata" in text
assert "Conclusione: Verdi in canna" in text
assert "Alleanza Verdi e Sinistra (AVS)" in text
assert "Organizzazione per la cooperazione e lo sviluppo economico (OCSE)" in text
assert "Cassa depositi e prestiti (CDP)" in text
assert "tetraidrocannabinolo (THC) e cannabidiolo (CBD)" in text
assert "Société québécoise du cannabis (SQDC)" in text
assert "Direzione investigativa antimafia (DIA)" in text
assert len(page.select(".dossier-contents li")) == 22
assert len(page.select(".sources-list li")) == 26
assert not page.select(".sources a")
assert len(page.select(".related-dossiers a")) == 3
assert page.select_one(".dossier-series")
assert page.select_one('link[rel="canonical"]')["href"] == URL
assert page.select_one("article")["data-macro-topic"] == "Geopolitica"
assert page.select_one("article")["data-micro-topic"] == "Politica italiana"
assert all(image.get("width") and image.get("height") for image in page.select("img"))
assert page.select_one(".article-hero img").get("loading") != "lazy"
assert page.select_one(".article-inline-image img").get("loading") == "lazy"
assert all(
    figure.figcaption.get_text(" ", strip=True) == "Immagine prodotta da Uno Sguardo sull'Uomo"
    for figure in page.select("figure")
)

schema = json.loads(page.select_one("script[data-seo-schema]").string)
article = next(node for node in schema["@graph"] if node.get("@type") == "NewsArticle")
assert article["datePublished"] == "2026-11-08"
assert article["dateModified"] == "2026-11-08"
assert article["articleSection"] == "Politica italiana"
assert article["headline"] == META["title"]
assert article["wordCount"] >= 7000
assert 45 <= len(META["seoTitle"]) <= 70
assert 110 <= len(META["description"]) <= 165

for image_name in ("assets/verdi-in-canna-avs.webp", "assets/verdi-in-canna-balcone.webp"):
    with Image.open(ROOT / image_name) as image:
        assert image.size == (1672, 941)

for file_name in (
    "index.html",
    "indagini.html",
    "archivio-politica-italiana.html",
    "feed.xml",
    "sitemap.xml",
    "sitemap-articles.xml",
    "search-index.json",
):
    assert SLUG in (ROOT / file_name).read_text(encoding="utf-8"), file_name

for element in page.select("[href], [src]"):
    target = element.get("href") or element.get("src")
    if not target or target.startswith(("http://", "https://", "mailto:", "#", "/")):
        continue
    local = target.split("?", 1)[0].split("#", 1)[0]
    assert (ROOT / local).exists(), f"Missing local target: {target}"

print("CONTROLLO DOSSIER VERDI IN CANNA: OK")

