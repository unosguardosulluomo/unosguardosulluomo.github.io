from __future__ import annotations

import html
import json
import re
import shutil
import unicodedata
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = Path(r"C:\Users\utente\OneDrive\Documenti\ChatGPT\sito uno sguardo sull'uomo")
SOURCE_DOCX = SOURCE_ROOT / "DOSSIER_FORZA_ITALIA_EBOOK_SCOLASTICI_MONDADORI.docx"
SOURCE_HERO = SOURCE_ROOT / "work" / "ebook-indagine-images" / "craxi-berlusconi-mondadori-v2.png"
SOURCE_SECONDARY = SOURCE_ROOT / "work" / "ebook-indagine-images" / "libro-trasferibile-ebook-bloccato-v1.png"

SLUG = "article-geopolitica-politica-italiana-ebook-scolastici-forza-italia.html"
DOCX_NAME = SOURCE_DOCX.name
HERO_NAME = "assets/ebook-scolastici-forza-italia-editori.webp"
SECONDARY_NAME = "assets/ebook-scolastici-licenza-digitale.webp"
TITLE = "Ebook scolastici, Forza Italia dalla parte degli editori"
SEO_TITLE = "Ebook scolastici: Forza Italia dalla parte degli editori"
DECK = (
    "Il voto contro il tetto al prezzo degli ebook scolastici espone il conflitto politico del partito "
    "che porta ancora Berlusconi nel nome. Le opposizioni perdono l'occasione di isolarlo"
)
DESCRIPTION = (
    "Il voto di Forza Italia contro il tetto al prezzo degli ebook scolastici, gli interessi Mondadori "
    "e l'occasione sprecata dalle opposizioni."
)
PUBLISHED = "2026-11-19"
DATE_LABEL = "19 novembre 2026"
READING_MINUTES = 26
TAGS = [
    "Forza Italia",
    "Fratelli d'Italia",
    "Stefania Craxi",
    "Mondadori",
    "Libri scolastici",
    "Ebook",
    "Famiglie",
    "Diritto d'autore",
]
HERO_ALT = (
    "Stefania Craxi e Marina Berlusconi davanti al marchio Mondadori con libri scolastici e un tablet"
)
SECONDARY_ALT = (
    "Due studenti si passano un libro scolastico usato mentre su un tablet compare un lucchetto digitale"
)
CAPTION = "Immagine prodotta da Uno Sguardo sull'Uomo"


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value


def iter_blocks(document: Document):
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, document)
        elif child.tag.endswith("}tbl"):
            yield Table(child, document)


def has_drawing(paragraph: Paragraph) -> bool:
    return bool(paragraph._p.xpath(".//w:drawing"))


def render_table(table: Table) -> str:
    rows = []
    for row_index, row in enumerate(table.rows):
        cells = []
        for cell_index, cell in enumerate(row.cells):
            text = " ".join(p.text.strip() for p in cell.paragraphs if p.text.strip())
            if row_index == 0:
                cells.append(f'<th scope="col">{html.escape(text)}</th>')
            elif cell_index == 0:
                cells.append(f'<th scope="row">{html.escape(text)}</th>')
            else:
                cells.append(f"<td>{html.escape(text)}</td>")
        rows.append(cells)
    head = "".join(rows[0])
    body = "".join("<tr>" + "".join(row) + "</tr>" for row in rows[1:])
    return (
        '<p class="table-hint" id="prezzi-table-help">Su smartphone, scorri la tabella orizzontalmente.</p>'
        '<div class="data-table-wrap" role="region" aria-label="Prezzi di listino dei libri scolastici" '
        'aria-describedby="prezzi-table-help" tabindex="0">'
        '<table class="data-table"><caption>Prezzi di listino rilevati nelle schede ufficiali Rizzoli Education</caption>'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def extract_body() -> tuple[str, list[tuple[str, str]], list[str], str]:
    document = Document(SOURCE_DOCX)
    started = False
    first_body = True
    in_sources = False
    lead = ""
    body: list[str] = []
    headings: list[tuple[str, str]] = []
    sources: list[str] = []
    secondary_inserted = False

    for block in iter_blocks(document):
        if isinstance(block, Table):
            if started and not in_sources:
                body.append(render_table(block))
            continue

        text = re.sub(r"\s+", " ", block.text).strip()
        style = block.style.name if block.style else ""

        if not started:
            if style == "Heading 1" and text == "Prefazione":
                started = True
            continue

        if has_drawing(block):
            if not secondary_inserted:
                body.append(
                    f'<figure class="article-inline-figure"><img src="{SECONDARY_NAME}" width="1672" height="941" '
                    f'alt="{html.escape(SECONDARY_ALT, quote=True)}" loading="lazy"><figcaption>{CAPTION}</figcaption></figure>'
                )
                secondary_inserted = True
            continue

        if not text or style == "Caption":
            continue

        if style == "Heading 1":
            if text == "Fonti":
                in_sources = True
                continue
            section_id = slugify(text)
            headings.append((section_id, text))
            body.append(f'<h2 id="{section_id}">{html.escape(text)}</h2>')
            continue

        if in_sources:
            sources.append(text.lstrip("• ").strip())
            continue

        if first_body:
            lead = text
            first_body = False
        else:
            body.append(f"<p>{html.escape(text)}</p>")

    if not lead or not sources or not secondary_inserted:
        raise RuntimeError("Estrazione incompleta dal DOCX")
    return lead, headings, sources, "\n      ".join(body)


def convert_image(source: Path, destination: Path) -> tuple[int, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        rgb = image.convert("RGB")
        rgb.save(destination, format="WEBP", quality=88, method=6)
        return rgb.size


def build_html(lead: str, headings: list[tuple[str, str]], sources: list[str], body: str) -> str:
    topics = "".join(f"<span>{html.escape(tag)}</span>" for tag in TAGS)
    article_tags = "\n  ".join(
        f'<meta property="article:tag" content="{html.escape(tag, quote=True)}">' for tag in TAGS
    )
    toc = "".join(
        f'<li><a href="#{section_id}">{html.escape(label)}</a></li>' for section_id, label in headings
    ) + '<li><a href="#fonti">Fonti</a></li>'
    source_items = "".join(f"<li>{html.escape(source)}</li>" for source in sources)
    canonical = "https://unosguardosulluomo.github.io/" + SLUG
    image_url = "https://unosguardosulluomo.github.io/" + HERO_NAME

    return f'''<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="description" content="{html.escape(DESCRIPTION, quote=True)}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="UNO SGUARDO SULL'UOMO">
  <meta property="og:title" content="{html.escape(TITLE, quote=True)}">
  <meta property="og:description" content="{html.escape(DESCRIPTION, quote=True)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{image_url}">
  <meta property="og:image:alt" content="{html.escape(HERO_ALT, quote=True)}">
  <meta property="og:image:width" content="1672">
  <meta property="og:image:height" content="941">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(TITLE, quote=True)}">
  <meta name="twitter:description" content="{html.escape(DESCRIPTION, quote=True)}">
  <meta name="twitter:image" content="{image_url}">
  <title>{html.escape(SEO_TITLE)}</title>
  <link rel="canonical" href="{canonical}">
  <link rel="stylesheet" href="styles.css?v=20261014-inline-image-1">
  <link rel="stylesheet" href="navigation.css?v=20261021-search-1">
  <link rel="stylesheet" href="dossier-tables.css?v=20261119-ebook-1">
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
  <meta property="article:published_time" content="{PUBLISHED}">
  <meta property="article:modified_time" content="{PUBLISHED}">
  <meta property="article:section" content="Politica italiana">
  <meta name="author" content="Redazione Uno Sguardo sull’Uomo">
  {article_tags}
  <script type="application/ld+json" data-seo-schema>{{"@context":"https://schema.org","@graph":[]}}</script>
</head>
<body><main class="newspaper">
  <div class="utility-bar"><span>Quotidiano indipendente di approfondimento</span><span>Politica, società e istituzioni</span><time class="current-date" datetime="{PUBLISHED}">{DATE_LABEL}</time></div>
  <header class="masthead"><a href="/" aria-label="Prima pagina"><img src="assets/testata.webp" width="1230" height="279" alt="Uno Sguardo sull'Uomo"></a></header>
  <nav class="nav" aria-label="Navigazione principale"><a href="/">Prima pagina</a><a href="indagini.html">Indagini</a><a href="ricerca-indagini.html">Ricerca indagini</a><a href="metodo.html">Metodo</a><a href="chi-siamo.html">Chi siamo</a><a href="contatti.html">Contatti</a></nav>
  <article class="article-page" data-macro-topic="Geopolitica" data-micro-topic="Politica italiana">
    <nav class="topic-breadcrumb" aria-label="Percorso tematico"><span class="topic-breadcrumb-macro">Geopolitica</span><span aria-hidden="true">›</span><a href="archivio-politica-italiana.html">Politica italiana</a><span aria-hidden="true">›</span><span aria-current="page">{html.escape(TITLE)}</span></nav>
    <header class="article-header"><a class="category-label" href="archivio-politica-italiana.html">Politica italiana</a><p class="eyebrow">DOSSIER</p><h1>{html.escape(TITLE)}</h1><p class="article-deck">{html.escape(DECK)}</p><div class="article-meta"><span>Redazione Uno Sguardo sull'Uomo</span><time datetime="{PUBLISHED}">Pubblicato: {DATE_LABEL}</time><span>Tempo di lettura: {READING_MINUTES} minuti</span></div><div class="topic-list" aria-label="Argomenti">{topics}</div></header>
    <figure class="article-hero"><img src="{HERO_NAME}" width="1672" height="941" alt="{html.escape(HERO_ALT, quote=True)}" fetchpriority="high"><figcaption>{CAPTION}</figcaption></figure>
    <div class="article-layout"><div class="article-body">
      <p class="article-lead">{html.escape(lead)}</p>
      <details class="dossier-contents"><summary>In questo dossier</summary><ol>{toc}</ol></details>
      {body}
      <section class="sources" aria-labelledby="fonti"><h2 id="fonti">FONTI</h2><ul class="sources-list">{source_items}</ul></section>
    </div></div>
  </article>
  <footer class="footer"><span>Uno Sguardo sull’Uomo — Politica italiana</span><span><a href="privacy-cookie.html">Privacy e Cookie Policy</a></span><span><a href="mailto:unosguardosulluomo@gmail.com">unosguardosulluomo@gmail.com</a></span></footer>
</main><script src="date.js?v=20260826-audit-1"></script></body></html>
'''


def main() -> None:
    for path in (SOURCE_DOCX, SOURCE_HERO, SOURCE_SECONDARY):
        if not path.is_file():
            raise FileNotFoundError(path)

    shutil.copy2(SOURCE_DOCX, ROOT / DOCX_NAME)
    hero_size = convert_image(SOURCE_HERO, ROOT / HERO_NAME)
    secondary_size = convert_image(SOURCE_SECONDARY, ROOT / SECONDARY_NAME)
    if hero_size != (1672, 941) or secondary_size != (1672, 941):
        raise RuntimeError(f"Dimensioni immagini inattese: {hero_size}, {secondary_size}")

    lead, headings, sources, body = extract_body()
    (ROOT / SLUG).write_text(build_html(lead, headings, sources, body), encoding="utf-8", newline="\n")

    metadata = {
        "slug": SLUG,
        "sourceDocx": DOCX_NAME,
        "title": TITLE,
        "seoTitle": SEO_TITLE,
        "ogTitle": TITLE,
        "deck": DECK,
        "lead": lead,
        "description": DESCRIPTION,
        "editorialSummary": (
            "Il dossier ricostruisce il voto di Forza Italia contro il limite al prezzo degli ebook scolastici, "
            "il peso economico di Mondadori, i limiti delle licenze digitali e la scelta politica delle opposizioni."
        ),
        "datePublished": PUBLISHED,
        "dateModified": PUBLISHED,
        "dateLabel": DATE_LABEL,
        "category": "Politica italiana",
        "categoryPath": "archivio-politica-italiana.html",
        "macroTopic": "Geopolitica",
        "author": "Redazione Uno Sguardo sull'Uomo",
        "schemaAuthor": "Redazione Uno Sguardo sull’Uomo",
        "readingMinutes": READING_MINUTES,
        "tags": TAGS,
        "cardEyebrow": "Politica italiana • Ebook scolastici • Forza Italia",
        "image": HERO_NAME,
        "imageWidth": 1672,
        "imageHeight": 941,
        "imageAlt": HERO_ALT,
        "imageCaption": CAPTION,
        "secondaryImage": SECONDARY_NAME,
        "secondaryImageWidth": 1672,
        "secondaryImageHeight": 941,
        "secondaryImageAlt": SECONDARY_ALT,
        "socialImage": HERO_NAME,
        "socialImageWidth": 1672,
        "socialImageHeight": 941,
        "seo": {
            "primaryQuery": "ebook scolastici Forza Italia",
            "searchIntent": "informativo-attualità",
            "supportingQueries": [
                "emendamento ebook scolastici 50 per cento",
                "Stefania Craxi ebook scolastici",
                "Forza Italia voto libri scolastici digitali",
                "Mondadori prezzi ebook scolastici",
            ],
            "serpCheckedAt": PUBLISHED,
        },
    }
    (ROOT / "editorial" / "ebook-scolastici-forza-italia.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Creati {SLUG}, metadati, DOCX e due immagini WebP")


if __name__ == "__main__":
    main()
