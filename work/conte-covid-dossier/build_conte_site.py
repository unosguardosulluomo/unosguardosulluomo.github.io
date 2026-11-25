from __future__ import annotations

import html
import json
import re
import runpy
import shutil
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = Path(r"C:\Users\utente\OneDrive\Documenti\ChatGPT\sito uno sguardo sull'uomo")
SOURCE_DOCX = SOURCE_ROOT / "DOSSIER_CONTE_DA_COMMISSARIO_A_TESTIMONE_CONTRO_SE_STESSO.docx"
SOURCE_HERO = Path(
    r"C:\Users\utente\.codex\generated_images\01a20e98-b657-7582-b53b-b35c830b4aa1"
    r"\exec-e2998903-f6e5-4f5e-89c7-c18b82478c83.png"
)
SOURCE_SECONDARY = SOURCE_ROOT / "work" / "conte-covid-dossier" / "mortalita-covid-europa-2020.png"

SLUG = "article-geopolitica-politica-italiana-conte-commissione-covid.html"
DOCX_NAME = SOURCE_DOCX.name
HERO_NAME = "assets/conte-bignami-commissione-covid.webp"
SECONDARY_NAME = "assets/mortalita-covid-europa-2020.webp"
TITLE = "CONTE, DA COMMISSARIO A TESTIMONE CONTRO SE STESSO"
SEO_TITLE = "Conte in Commissione Covid: da commissario a testimone"
DECK = (
    "Quando l’avvocato si sente imputato, la storia cambia. "
    "E il nervosismo, a volte, gioca brutti scherzi…"
)
DESCRIPTION = (
    "L’audizione di Giuseppe Conte in Commissione Covid, lo scontro con Bignami e il nodo dei 685 giorni "
    "trascorsi nell’organo che indagava sul suo governo."
)
EDITORIAL_SUMMARY = (
    "Il dossier ricostruisce le decisioni dei governi Conte e Draghi durante la pandemia, confronta sacrifici "
    "e mortalità e analizza i 685 giorni trascorsi da Conte nella Commissione prima della sua audizione."
)
PUBLISHED = "2026-11-25"
DATE_LABEL = "25 novembre 2026"
READING_MINUTES = 25
TAGS = [
    "Giuseppe Conte",
    "Commissione Covid",
    "Galeazzo Bignami",
    "Pandemia",
    "Mario Draghi",
    "Domenico Arcuri",
    "Green Pass",
    "Mortalità",
]
HERO_ALT = "Galeazzo Bignami e Giuseppe Conte durante un confronto nella Commissione parlamentare Covid"
SECONDARY_ALT = (
    "Confronto tra decessi attribuiti al Covid-19 ed eccesso di mortalità nel 2020 "
    "in cinque Paesi europei"
)
CAPTION = "Immagine prodotta da Uno Sguardo sull'Uomo"


template = runpy.run_path(str(ROOT / "work" / "ebook-dossier" / "build_ebook_site.py"))
template.update(
    {
        "SOURCE_DOCX": SOURCE_DOCX,
        "SOURCE_HERO": SOURCE_HERO,
        "SOURCE_SECONDARY": SOURCE_SECONDARY,
        "SLUG": SLUG,
        "DOCX_NAME": DOCX_NAME,
        "HERO_NAME": HERO_NAME,
        "SECONDARY_NAME": SECONDARY_NAME,
        "TITLE": TITLE,
        "SEO_TITLE": SEO_TITLE,
        "DECK": DECK,
        "DESCRIPTION": DESCRIPTION,
        "PUBLISHED": PUBLISHED,
        "DATE_LABEL": DATE_LABEL,
        "READING_MINUTES": READING_MINUTES,
        "TAGS": TAGS,
        "HERO_ALT": HERO_ALT,
        "SECONDARY_ALT": SECONDARY_ALT,
        "CAPTION": CAPTION,
    }
)
template["build_html"].__globals__.update(template)


def listing_card(css_class: str = "archive-card", heading: str = "h3") -> str:
    image_loading = 'fetchpriority="high"' if css_class == "lead-story" else 'loading="lazy"'
    return (
        f'<article class="{css_class}" data-dossier="{SLUG}">'
        f'<a class="story-image" href="{SLUG}" aria-label="Leggi il dossier {html.escape(TITLE, quote=True)}">'
        f'<img src="{HERO_NAME}" width="1672" height="941" alt="{html.escape(HERO_ALT, quote=True)}" '
        f'{image_loading}></a>'
        '<p class="eyebrow">Politica italiana • Commissione Covid • Giuseppe Conte</p>'
        f'<p class="archive-meta"><time datetime="{PUBLISHED}">{DATE_LABEL}</time></p>'
        f'<{heading}><a class="headline-link" href="{SLUG}">{html.escape(TITLE)}</a></{heading}>'
        f'<p>{html.escape(DESCRIPTION)}</p>'
        f'<a class="read-more" href="{SLUG}">Leggi il dossier →</a></article>'
    )


def render_table(table: Table) -> str:
    rows: list[list[str]] = []
    for row_index, row in enumerate(table.rows):
        cells: list[str] = []
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
        '<p class="table-hint" id="cronologia-table-help">Su smartphone, scorri la tabella orizzontalmente.</p>'
        '<div class="data-table-wrap" role="region" aria-label="Cronologia delle misure adottate dai governi Conte e Draghi" '
        'aria-describedby="cronologia-table-help" tabindex="0">'
        '<table class="data-table"><caption>Dal governo Conte al governo Draghi: i principali passaggi</caption>'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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

    for block in template["iter_blocks"](document):
        if isinstance(block, Table):
            if started and not in_sources:
                body.append(render_table(block))
            continue

        assert isinstance(block, Paragraph)
        text = normalize(block.text)
        style = block.style.name if block.style else ""

        if not started:
            if text.startswith("Giuseppe Conte è arrivato davanti alla Commissione Covid"):
                started = True
            else:
                continue

        if template["has_drawing"](block):
            if not secondary_inserted:
                body.append(
                    f'<figure class="article-inline-figure"><img src="{SECONDARY_NAME}" width="1672" height="941" '
                    f'alt="{html.escape(SECONDARY_ALT, quote=True)}" loading="lazy">'
                    f"<figcaption>{CAPTION}</figcaption></figure>"
                )
                secondary_inserted = True
            continue

        if not text:
            continue

        if style == "Heading 1":
            if text == "Fonti":
                in_sources = True
                continue
            section_id = template["slugify"](text)
            headings.append((section_id, text))
            body.append(f'<h2 id="{section_id}">{html.escape(text)}</h2>')
            continue

        if in_sources:
            sources.append(text.lstrip("• ").strip())
            continue

        if first_body:
            lead = text
            first_body = False
        elif style == "Quote":
            lines = [normalize(line) for line in block.text.splitlines() if normalize(line)]
            quote = lines[0].strip("“”") if lines else text.strip("“”")
            attribution = lines[1] if len(lines) > 1 else ""
            cite = f"<cite>{html.escape(attribution)}</cite>" if attribution else ""
            body.append(f"<blockquote><p>{html.escape(quote)}</p>{cite}</blockquote>")
        elif not text.startswith("Immagine prodotta da Uno Sguardo sull"):
            body.append(f"<p>{html.escape(text)}</p>")

    if not lead or len(headings) < 10 or len(sources) < 20 or not secondary_inserted:
        raise RuntimeError(
            f"Estrazione incompleta: lead={bool(lead)} headings={len(headings)} "
            f"sources={len(sources)} secondary={secondary_inserted}"
        )
    return lead, headings, sources, "\n      ".join(body)


def convert_image(source: Path, destination: Path) -> tuple[int, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        rgb = image.convert("RGB").resize((1672, 941), Image.Resampling.LANCZOS)
        rgb.save(destination, format="WEBP", quality=88, method=6)
        return rgb.size


def main() -> None:
    already_listed = SLUG in (ROOT / "index.html").read_text(encoding="utf-8")
    for path in (SOURCE_DOCX, SOURCE_HERO, SOURCE_SECONDARY):
        if not path.is_file():
            raise FileNotFoundError(path)

    shutil.copy2(SOURCE_DOCX, ROOT / DOCX_NAME)
    hero_size = convert_image(SOURCE_HERO, ROOT / HERO_NAME)
    secondary_size = convert_image(SOURCE_SECONDARY, ROOT / SECONDARY_NAME)
    if hero_size != (1672, 941) or secondary_size != (1672, 941):
        raise RuntimeError(f"Dimensioni immagini inattese: {hero_size}, {secondary_size}")

    lead, headings, sources, body = extract_body()
    (ROOT / SLUG).write_text(
        template["build_html"](lead, headings, sources, body), encoding="utf-8", newline="\n"
    )

    metadata = {
        "slug": SLUG,
        "sourceDocx": DOCX_NAME,
        "title": TITLE,
        "seoTitle": SEO_TITLE,
        "ogTitle": TITLE,
        "deck": DECK,
        "lead": lead,
        "description": DESCRIPTION,
        "editorialSummary": EDITORIAL_SUMMARY,
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
        "cardEyebrow": "Politica italiana • Commissione Covid • Giuseppe Conte",
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
            "primaryQuery": "Conte Commissione Covid",
            "searchIntent": "informativo-attualità e approfondimento",
            "supportingQueries": [
                "Giuseppe Conte audizione Commissione Covid 23 novembre 2026",
                "Conte Bignami siamo prontissimi",
                "Conte commissario Commissione Covid conflitto di interessi",
                "governo Conte Draghi gestione pandemia mortalità",
            ],
            "serpCheckedAt": PUBLISHED,
        },
    }
    (ROOT / "editorial" / "conte-commissione-covid.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    if not already_listed:
        template["update_listing_pages"].__globals__["listing_card"] = listing_card
        template["update_listing_pages"]()
    print(f"Creati {SLUG}, metadati, DOCX, due immagini WebP e aggiornate le pagine elenco")


if __name__ == "__main__":
    main()
