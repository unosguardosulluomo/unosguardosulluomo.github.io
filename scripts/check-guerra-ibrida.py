"""Regression checks for the hybrid warfare dossier."""

import json
import re
from pathlib import Path
from xml.etree import ElementTree

from docx import Document
from lxml import html
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "editorial/guerra-ibrida.json").read_text(encoding="utf-8"))
SITE = "https://unosguardosulluomo.github.io/"


def normalize(value):
    replacements = {
        "nel SISMI — Servizio per le Informazioni e la Sicurezza Militare —": "nel Servizio per le Informazioni e la Sicurezza Militare (SISMI)",
        "del DIS — Dipartimento delle Informazioni per la Sicurezza —": "del Dipartimento delle Informazioni per la Sicurezza (DIS)",
        "La NATO considera": "L’Organizzazione del Trattato dell’Atlantico del Nord (NATO) considera",
        "L’Unione europea, nel luglio 2025": "L’Unione europea (UE), nel luglio 2025",
        "compreso il GRU — Direzione principale dello Stato maggiore delle Forze armate russe, cioè l’intelligence militare —": "compresa la Direzione principale dello Stato maggiore delle Forze armate russe (GRU), cioè l’intelligence militare,",
        "a APT28 — Advanced Persistent Threat 28 —,": "all’attore Advanced Persistent Threat 28 (APT28),",
        "con ORION 2026": "con l’Operazione di grande portata per eserciti resilienti, interoperabili, orientati al combattimento ad alta intensità e innovativi (ORION) 2026",
        "Il 7 ottobre Regno Unito e Germania": "L’8 ottobre Regno Unito e Germania",
        "Sala CSIRT — Computer Security Incident Response Team — mentre l’ACN — Agenzia per la Cybersicurezza Nazionale —": "Sala Computer Security Incident Response Team (CSIRT), mentre l’Agenzia per la Cybersicurezza Nazionale (ACN)",
        "del GNL — gas naturale liquefatto —": "del gas naturale liquefatto (GNL)",
        "GPS e guerra elettronica": "Sistema di posizionamento globale (GPS) e guerra elettronica",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


article_text = (ROOT / D["slug"]).read_text(encoding="utf-8")
article = html.fromstring(article_text)
visible = " ".join(article.text_content().split())

assert article.xpath("string(//h1)").strip() == D["title"]
assert article.xpath("string(//p[contains(@class,'article-deck')])").strip() == D["deck"]
assert article.xpath("string(//p[contains(@class,'article-lead')])").strip() == D["lead"]
assert article.xpath("string(//link[@rel='canonical']/@href)") == SITE + D["slug"]
assert article.xpath("string(//meta[@property='article:published_time']/@content)") == D["datePublished"]
assert article.xpath("string(//meta[@property='article:modified_time']/@content)") == D["dateModified"]
assert article.xpath("string(//figure[contains(@class,'article-hero')]/img/@src)") == D["image"]
assert article.xpath("string(//figure[contains(@class,'article-inline-image')]/img/@src)") == D["secondaryImage"]
assert all(caption.strip() == D["imageCaption"] for caption in article.xpath("//figcaption/text()"))
assert len(article.xpath("//section[contains(@class,'sources')]//li")) == 27
assert not article.xpath("//section[contains(@class,'sources')]//a")
assert "https://" not in article.xpath("string(//section[contains(@class,'sources')])")
assert "L’8 ottobre Regno Unito e Germania" in visible
assert "Il 7 ottobre Regno Unito e Germania" not in visible

for required in (
    "Organizzazione del Trattato dell’Atlantico del Nord (NATO)",
    "Unione europea (UE)",
    "Servizio per le Informazioni e la Sicurezza Militare (SISMI)",
    "Dipartimento delle Informazioni per la Sicurezza (DIS)",
    "Computer Security Incident Response Team (CSIRT)",
    "Agenzia per la Cybersicurezza Nazionale (ACN)",
    "gas naturale liquefatto (GNL)",
):
    assert required in visible, required

source_doc = Document(ROOT / D["sourceDocx"])
for paragraph in source_doc.paragraphs:
    text = paragraph.text.strip()
    if not text or paragraph.style.name in {"Kicker", "Caption"}:
        continue
    expected = " ".join(normalize(text).split())
    assert expected in visible, f"Missing source paragraph: {expected[:120]}"

schema = json.loads(article.xpath("string(//script[@data-seo-schema])"))
news = next(item for item in schema["@graph"] if item.get("@type") == "NewsArticle")
assert news["datePublished"] == D["datePublished"]
assert news["dateModified"] == D["dateModified"]
assert news["articleSection"] == D["category"]
assert news["keywords"] == D["tags"]
assert {item["name"] for item in news["about"]} >= {"Geopolitica", D["category"], "Guerra ibrida", "Italia"}
breadcrumb = next(item for item in schema["@graph"] if item.get("@type") == "BreadcrumbList")
assert [item["name"] for item in breadcrumb["itemListElement"]] == ["Prima pagina", D["category"], D["title"]]

for image_key in ("image", "secondaryImage"):
    image_path = ROOT / D[image_key]
    assert image_path.exists(), image_path
    with Image.open(image_path) as asset:
        assert asset.size == (D[image_key + "Width"] if image_key + "Width" in D else 1672, D[image_key + "Height"] if image_key + "Height" in D else 941)

for filename in ("index.html", "indagini.html", D["categoryPath"]):
    document = html.fromstring((ROOT / filename).read_text(encoding="utf-8"))
    cards = document.xpath(f"//article[@data-dossier='{D['slug']}']")
    assert len(cards) == 1, filename
    assert cards[0].xpath("string(.//time/@datetime)") == D["datePublished"]
    assert cards[0].xpath("string(.//img/@src)") == D["image"]

archive_doc = html.fromstring((ROOT / D["categoryPath"]).read_text(encoding="utf-8"))
archive_cards = archive_doc.xpath("//div[contains(@class,'archive-grid')]/article")
archive_dates = [card.xpath("string(.//time/@datetime)") for card in archive_cards]
assert archive_dates == sorted(archive_dates, reverse=True)
archive_schema = json.loads(archive_doc.xpath("string(//script[@data-seo-schema])"))
collection = next(item for item in archive_schema["@graph"] if item.get("@type") == "CollectionPage")
assert collection["mainEntity"]["numberOfItems"] == len(archive_cards)
assert collection["mainEntity"]["itemListElement"][0]["url"] == SITE + D["slug"]

indagini_doc = html.fromstring((ROOT / "indagini.html").read_text(encoding="utf-8"))
politics = indagini_doc.xpath("//section[.//a[@href='archivio-politica-internazionale.html']]/div[contains(@class,'archive-grid')]/article")
assert len(politics) == 3
assert politics[0].get("data-dossier") == D["slug"]

home_doc = html.fromstring((ROOT / "index.html").read_text(encoding="utf-8"))
assert home_doc.xpath("string(//article[contains(@class,'lead-story')]/@data-dossier)") == D["slug"]
assert len(home_doc.xpath("//article[contains(@class,'lead-story') or contains(@class,'side-story') or contains(@class,'story-card')]") ) == 9

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

assert "Sitemap:" in (ROOT / "robots.txt").read_text(encoding="utf-8")
print("Hybrid warfare dossier checks passed")
