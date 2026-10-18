"""Validate the published student protest dossier and its placements."""

import json
import re
from html import unescape
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "editorial/studenti-piazza-pressione-politica.json").read_text(encoding="utf-8"))
PAGE_PATH = ROOT / DATA["slug"]
PAGE = PAGE_PATH.read_text(encoding="utf-8")
PUBLIC_URL = f'https://unosguardosulluomo.github.io/{DATA["slug"]}'


def plain(value):
    text = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()
    return text.translate(str.maketrans({"’": "'", "–": "-", "—": "-", "‑": "-"}))


assert DATA["macroTopic"] == "Geopolitica"
assert DATA["category"] == "Politica italiana"
assert DATA["datePublished"] == "2026-10-17"
assert DATA["dateModified"] == DATA["datePublished"]
assert f'<link rel="canonical" href="{PUBLIC_URL}">' in PAGE
assert f'<meta property="og:url" content="{PUBLIC_URL}">' in PAGE
assert f'<meta property="article:published_time" content="{DATA["datePublished"]}">' in PAGE
assert f'<meta property="article:section" content="{DATA["category"]}">' in PAGE
assert '<meta name="robots" content="index, follow, max-image-preview:large">' in PAGE

assert PAGE.count('<figure class="article-') == 3
assert PAGE.count("Immagine prodotta da Uno Sguardo sull") == 3
for image, width, height in (
    (DATA["image"], DATA["imageWidth"], DATA["imageHeight"]),
    (DATA["secondaryImage"], DATA["secondaryImageWidth"], DATA["secondaryImageHeight"]),
    (DATA["chartImage"], DATA["chartImageWidth"], DATA["chartImageHeight"]),
):
    assert (ROOT / image).exists(), image
    assert f'src="{image}"' in PAGE
    assert f'width="{width}" height="{height}"' in PAGE
assert '<img src="assets/testata.webp" width="1230" height="279"' in PAGE

page_text = plain(PAGE)
for expansion in (
    "Partito Democratico (PD)",
    "Confederazione Generale Italiana del Lavoro (CGIL)",
    "Unione degli Universitari (UDU)",
    "Unione Sindacale di Base (USB)",
    "Opposizione Studentesca d'Alternativa (OSA)",
    "Direzione Investigazioni Generali e Operazioni Speciali (DIGOS)",
    "Brigate Rosse (BR)",
):
    assert expansion in page_text, f"Missing acronym expansion: {expansion}"

for statement in (
    "50.348",
    "1.445",
    "almeno 1.141",
    "quasi 100",
    "circa 1.400",
    "La condanna che dura una frase",
    "Elly Schlein non risponde nel merito al primo appello",
    "Giuseppe Conte pronuncia la condanna che Schlein evita",
    "Angelo Bonelli adotta la stessa struttura",
    "Nicola Fratoianni interviene soprattutto sul significato politico della mobilitazione",
    "Maurizio Landini",
    "Quando i nonni finanziano i nipoti",
):
    assert statement in page_text, f"Missing approved content: {statement}"

assert 'href="article-geopolitica-societa-poverta-contagiosa.html"' in PAGE
assert PAGE.count('<table class="data-table">') == 9

sources_html = re.search(r'<ul class="sources-list">(.*?)</ul>', PAGE, re.S).group(1)
assert sources_html.count("<li>") == 63
assert "<a " not in sources_html
assert not re.search(r"https?://|www\.", sources_html)

document = Document(ROOT / DATA["sourceDocx"])
started = False
for paragraph in document.paragraphs:
    text = re.sub(r"\s+", " ", paragraph.text).strip()
    if text == "Il 17 ottobre come punto di arrivo":
        started = True
    if started and text and text not in {"Fonti documentali"}:
        if text.startswith("•"):
            for item in (line.removeprefix("•").strip().translate(str.maketrans({"’": "'", "–": "-", "—": "-", "‑": "-"})) for line in paragraph.text.splitlines() if line.strip()):
                assert item in page_text, f"DOCX list item missing from HTML: {item[:100]}"
            continue
        expected = {
            "Il quadriennio dei governi a guida PD": "Il quadriennio dei governi a guida Partito Democratico (PD)",
            "USB OSA e Cambiare Rotta": "Unione Sindacale di Base (USB), Opposizione Studentesca d'Alternativa (OSA) e Cambiare Rotta",
        }.get(text, text).translate(str.maketrans({"’": "'", "–": "-", "—": "-", "‑": "-"}))
        assert expected in page_text, f"DOCX paragraph missing from HTML: {text[:100]}"
for table in document.tables[2:]:
    for row in table.rows:
        for cell in row.cells:
            text = re.sub(r"\s+", " ", cell.text).strip()
            if text:
                expected = {
                    "Sinistra studentesca e sindacale; patto di lavoro con UDU e CGIL": "Sinistra studentesca e sindacale; patto di lavoro con Unione degli Universitari (UDU) e Confederazione Generale Italiana del Lavoro (CGIL)",
                    "Totale UDU REDS": "Totale Unione degli Universitari (UDU) e Rete degli Studenti (REDS)",
                    "Perquisizioni DIGOS a Padova in vista del corteo studentesco": "Perquisizioni della Direzione Investigazioni Generali e Operazioni Speciali (DIGOS) a Padova in vista del corteo studentesco",
                }.get(text, text).translate(str.maketrans({"’": "'", "–": "-", "—": "-", "‑": "-"}))
                assert expected in page_text, f"DOCX table value missing from HTML: {text[:100]}"

for filename in (
    "index.html",
    "indagini.html",
    "archivio-politica-italiana.html",
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

schema_text = re.search(r'<script type="application/ld\+json" data-seo-schema>(.*?)</script>', PAGE, re.S).group(1)
schema = json.loads(schema_text)
article = next(item for item in schema["@graph"] if item.get("@type") == "NewsArticle")
assert article["datePublished"] == DATA["datePublished"]
assert article["dateModified"] == DATA["dateModified"]
assert article["articleSection"] == DATA["category"]
assert {item["name"] for item in article["about"]} >= {"Geopolitica", "Politica italiana"}

print("CONTROLLO DOSSIER STUDENTI E PIAZZA: OK")
