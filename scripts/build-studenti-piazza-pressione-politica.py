"""Build the approved dossier on student protest and political pressure."""

import email.utils
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentObject
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph


ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "editorial/studenti-piazza-pressione-politica.json").read_text(encoding="utf-8"))
SITE = "https://unosguardosulluomo.github.io/"
URL = SITE + D["slug"]


def esc(value):
    return html.escape(str(value), quote=True)


DISPLAY_TEXT = {
    "Il quadriennio dei governi a guida PD": "Il quadriennio dei governi a guida Partito Democratico (PD)",
    "USB OSA e Cambiare Rotta": "Unione Sindacale di Base (USB), Opposizione Studentesca d'Alternativa (OSA) e Cambiare Rotta",
    "Sinistra studentesca e sindacale; patto di lavoro con UDU e CGIL": "Sinistra studentesca e sindacale; patto di lavoro con Unione degli Universitari (UDU) e Confederazione Generale Italiana del Lavoro (CGIL)",
    "Totale UDU REDS": "Totale Unione degli Universitari (UDU) e Rete degli Studenti (REDS)",
    "Perquisizioni DIGOS a Padova in vista del corteo studentesco": "Perquisizioni della Direzione Investigazioni Generali e Operazioni Speciali (DIGOS) a Padova in vista del corteo studentesco",
}


def display_text(value):
    return DISPLAY_TEXT.get(value, value)


def blocks(parent):
    if not isinstance(parent, DocumentObject):
        raise TypeError("The dossier source must be a DOCX document")
    for child in parent.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def rich_paragraph(paragraph):
    fragments = []
    for child in paragraph._p.iterchildren():
        if child.tag.endswith("}hyperlink"):
            relationship_id = child.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            target = paragraph.part.rels[relationship_id].target_ref if relationship_id else ""
            label = "".join(node.text or "" for node in child.iter() if node.tag.endswith("}t"))
            if label:
                if target.startswith(SITE):
                    target = target.removeprefix(SITE)
                fragments.append(f'<a href="{esc(target)}">{esc(label)}</a>')
            continue
        if not child.tag.endswith("}r"):
            continue
        text = "".join(node.text or "" for node in child.iter() if node.tag.endswith("}t"))
        if not text:
            continue
        value = esc(text)
        properties = child.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr")
        if properties is not None and properties.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}b") is not None:
            value = f"<strong>{value}</strong>"
        if properties is not None and properties.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}i") is not None:
            value = f"<em>{value}</em>"
        fragments.append(value)
    return "".join(fragments) or esc(paragraph.text)


def figure(image, width, height, alt, extra_class=""):
    css_class = "article-inline-image" + (" " + extra_class if extra_class else "")
    return (
        f'<figure class="{css_class}">'
        f'<img src="{esc(image)}" width="{width}" height="{height}" alt="{esc(alt)}" loading="lazy">'
        f'<figcaption>{esc(D["imageCaption"])}</figcaption></figure>'
    )


TABLE_CAPTIONS = {
    ("Fase", "Attore", "Funzione", "Strumenti osservati"): "La filiera della mobilitazione",
    ("Periodo", "Manifestazioni", "Criticità", "Incidenza", "Forze dell'ordine ferite"): "Manifestazioni, criticità e forze dell'ordine ferite",
    ("Periodo", "Governo prevalente", "Manifestazioni", "Con disordini"): "Il quadriennio dei governi a guida Partito Democratico",
    ("Periodo", "Eventi critici", "Feriti", "Feriti per evento critico"): "La capacità lesiva degli eventi critici",
    ("Periodo", "Manifestazioni studentesche", "Quota o natura del dato"): "Le mobilitazioni studentesche censite",
    ("Sigla", "Ambito", "Area della sinistra e funzione"): "Le principali organizzazioni studentesche",
    ("Anno", "Prima voce", "Seconda voce", "Totale UDU REDS"): "I contributi documentati nei bilanci della CGIL",
    ("Luogo e data", "Soggetti", "Condotta documentata"): "La presenza politica nella scuola",
    ("Data", "Città", "Promotori e contesto", "Condotta o conseguenza", "Area"): "Cronologia degli episodi principali",
}


def table_markup(table):
    headers = tuple(cell.text.strip() for cell in table.rows[0].cells)
    if headers in {("Campo", "Valore"), ("Elemento", "Contenuto")}:
        return ""
    caption = TABLE_CAPTIONS.get(headers)
    if not caption:
        raise RuntimeError(f"Unexpected dossier table: {headers}")
    head = "".join(f'<th scope="col">{esc(display_text(value))}</th>' for value in headers)
    rows = []
    for row in table.rows[1:]:
        cells = []
        for index, cell in enumerate(row.cells):
            tag = 'th scope="row"' if index == 0 else "td"
            close = "th" if index == 0 else "td"
            cells.append(f"<{tag}>{esc(display_text(cell.text.strip()))}</{close}>")
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return (
        '<div class="data-table-wrap" tabindex="0"><table class="data-table">'
        f'<caption>{esc(caption)}</caption><thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


document = Document(ROOT / D["sourceDocx"])
body = []
contents = []
sources = []
started = False
in_sources = False
heading_number = 0
lead = ""

for item in blocks(document):
    if isinstance(item, Table):
        if started and not in_sources:
            markup = table_markup(item)
            if markup:
                body.append(markup)
        continue

    image_targets = [item.part.rels[rel].target_ref for rel in item._p.xpath('.//a:blip/@r:embed')]
    if image_targets and started and not in_sources:
        for target in image_targets:
            if target.endswith("image3.png"):
                body.append(figure(D["chartImage"], D["chartImageWidth"], D["chartImageHeight"], D["chartImageAlt"], "article-data-graphic"))
            elif target.endswith("image2.png"):
                body.append(figure(D["secondaryImage"], D["secondaryImageWidth"], D["secondaryImageHeight"], D["secondaryImageAlt"]))
        continue

    text = item.text.strip()
    if not text:
        continue
    style = item.style.name
    if not started:
        if style == "Heading 1" and text == "Il 17 ottobre come punto di arrivo":
            started = True
            heading_number = 1
            contents.append(f'<li><a href="#sezione-1">{esc(text)}</a></li>')
            body.append(f'<h2 id="sezione-1">{esc(text)}</h2>')
        continue
    if style == "Heading 1" and text == "Fonti documentali":
        in_sources = True
        continue
    if in_sources:
        sources.append(text.removeprefix("•").strip())
        continue
    if not lead:
        lead = rich_paragraph(item)
        continue
    if text == D["imageCaption"]:
        continue
    if style == "Heading 1":
        heading_number += 1
        anchor = f"sezione-{heading_number}"
        shown = display_text(text)
        contents.append(f'<li><a href="#{anchor}">{esc(shown)}</a></li>')
        body.append(f'<h2 id="{anchor}">{esc(shown)}</h2>')
    elif style == "Heading 2":
        body.append(f'<h3>{esc(display_text(text))}</h3>')
    elif text.startswith("•"):
        items = [line.removeprefix("•").strip() for line in text.splitlines() if line.strip()]
        body.append('<ul class="article-facts">' + "".join(f'<li>{esc(value)}</li>' for value in items) + '</ul>')
    else:
        body.append(f'<p>{rich_paragraph(item)}</p>')

if not lead:
    raise RuntimeError("Article lead not found")
if len(sources) != 63:
    raise RuntimeError(f"Expected 63 documentary sources, found {len(sources)}")
if sum(fragment.count('<figure class="article-inline-image') for fragment in body) != 2:
    raise RuntimeError("Expected the chart and one internal editorial image")

word_count = len(re.findall(r"\b[\wÀ-ÖØ-öø-ÿ’'-]+\b", " ".join(p.text for p in document.paragraphs[14:])))

organization = {
    "@type": ["Organization", "NewsMediaOrganization"],
    "@id": SITE + "#organization",
    "name": "Uno Sguardo sull’Uomo",
    "alternateName": ["UNO SGUARDO SULL'UOMO", "unosguardosulluomo"],
    "url": SITE,
    "description": "Testata editoriale indipendente italiana di approfondimento: indagini, dati, documenti e ricostruzione dei fatti oltre la narrazione.",
    "email": "mailto:unosguardosulluomo@gmail.com",
    "logo": {"@type": "ImageObject", "url": SITE + "assets/testata.webp"},
    "sameAs": [
        "https://www.facebook.com/profile.php?id=61593043131759",
        "https://www.linkedin.com/company/unosguardosulluomo/",
    ],
}
website = {
    "@type": "WebSite",
    "@id": SITE + "#website",
    "url": SITE,
    "name": "Uno Sguardo sull’Uomo",
    "alternateName": ["UNO SGUARDO SULL'UOMO", "unosguardosulluomo"],
    "description": "Dossier di geopolitica organizzati tra politica italiana, politica internazionale, economia e società.",
    "publisher": {"@id": SITE + "#organization"},
    "inLanguage": "it-IT",
}
schema = {
    "@context": "https://schema.org",
    "@graph": [
        organization,
        website,
        {
            "@type": "ImageObject",
            "@id": URL + "#primaryimage",
            "url": SITE + D["socialImage"],
            "contentUrl": SITE + D["socialImage"],
            "caption": D["title"],
            "width": D["socialImageWidth"],
            "height": D["socialImageHeight"],
            "inLanguage": "it-IT",
        },
        {
            "@type": "NewsArticle",
            "@id": URL + "#article",
            "headline": D["title"],
            "alternativeHeadline": D["deck"],
            "description": D["description"],
            "url": URL,
            "mainEntityOfPage": {"@id": URL + "#webpage"},
            "datePublished": D["datePublished"],
            "dateModified": D["dateModified"],
            "image": [{"@id": URL + "#primaryimage"}],
            "thumbnailUrl": SITE + D["socialImage"],
            "inLanguage": "it-IT",
            "isAccessibleForFree": True,
            "articleSection": D["category"],
            "genre": "Dossier geopolitico",
            "keywords": D["tags"],
            "about": [
                {"@type": "Thing", "name": D["macroTopic"]},
                {"@type": "Thing", "name": D["category"]},
                *[{"@type": "Thing", "name": tag} for tag in D["tags"]],
            ],
            "wordCount": word_count,
            "author": {"@type": "Organization", "name": D["schemaAuthor"], "url": SITE + "chi-siamo.html"},
            "publisher": {"@id": SITE + "#organization"},
            "isPartOf": {"@id": SITE + "#website"},
        },
        {
            "@type": "WebPage",
            "@id": URL + "#webpage",
            "url": URL,
            "name": D["title"],
            "description": D["description"],
            "inLanguage": "it-IT",
            "datePublished": D["datePublished"],
            "dateModified": D["dateModified"],
            "isPartOf": {"@id": SITE + "#website"},
            "breadcrumb": {"@id": URL + "#breadcrumb"},
            "primaryImageOfPage": {"@id": URL + "#primaryimage"},
            "mainEntity": {"@id": URL + "#article"},
        },
        {
            "@type": "BreadcrumbList",
            "@id": URL + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Prima pagina", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": D["category"], "item": SITE + D["categoryPath"]},
                {"@type": "ListItem", "position": 3, "name": D["title"], "item": URL},
            ],
        },
    ],
}

page = f'''<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="description" content="{esc(D['description'])}">
  <meta property="og:site_name" content="UNO SGUARDO SULL'UOMO">
  <meta property="og:title" content="{esc(D['ogTitle'])}">
  <meta property="og:description" content="{esc(D['description'])}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{URL}">
  <meta property="og:image" content="{SITE+D['socialImage']}">
  <meta property="og:image:alt" content="{esc(D['imageAlt'])}">
  <meta property="og:image:width" content="{D['socialImageWidth']}">
  <meta property="og:image:height" content="{D['socialImageHeight']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(D['ogTitle'])}">
  <meta name="twitter:description" content="{esc(D['description'])}">
  <meta name="twitter:image" content="{SITE+D['socialImage']}">
  <meta property="article:published_time" content="{D['datePublished']}">
  <meta property="article:modified_time" content="{D['dateModified']}">
  <meta property="article:section" content="{esc(D['category'])}">
  <meta name="author" content="{esc(D['schemaAuthor'])}">
  {''.join(f'<meta property="article:tag" content="{esc(tag)}">' for tag in D['tags'])}
  <link rel="canonical" href="{URL}">
  <link rel="alternate" type="application/rss+xml" title="Uno Sguardo sull’Uomo" href="{SITE}feed.xml">
  <title>{esc(D['seoTitle'])} — Uno Sguardo sull'Uomo</title>
  <link rel="stylesheet" href="styles.css?v=20261014-inline-image-1">
  <link rel="stylesheet" href="editorial-rules.css?v=20260812-1">
  <link rel="stylesheet" href="dossier-tables.css?v=20260925-1">
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
  <script type="application/ld+json" data-seo-schema>{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
</head>
<body><main class="newspaper">
  <div class="utility-bar"><span>Quotidiano indipendente di approfondimento</span><span>Politica, società e istituzioni</span><time class="current-date" datetime="{D['datePublished']}">{D['dateLabel']}</time></div>
  <header class="masthead"><a href="/" aria-label="Prima pagina"><img src="assets/testata.webp" width="1230" height="279" alt="Uno Sguardo sull’Uomo"></a></header>
  <nav class="nav" aria-label="Navigazione principale"><a href="/">Prima pagina</a><a href="indagini.html">Indagini</a><a href="metodo.html">Metodo</a><a href="chi-siamo.html">Chi siamo</a><a href="contatti.html">Contatti</a></nav>
  <article class="article-page" data-macro-topic="{esc(D['macroTopic'])}" data-micro-topic="{esc(D['category'])}">
    <nav class="topic-breadcrumb" aria-label="Percorso tematico"><span class="topic-breadcrumb-macro">{esc(D['macroTopic'])}</span><span aria-hidden="true">›</span><a href="{D['categoryPath']}">{esc(D['category'])}</a><span aria-hidden="true">›</span><span aria-current="page">{esc(D['title'])}</span></nav>
    <header class="article-header"><a class="category-label" href="{D['categoryPath']}">{esc(D['category'])}</a><p class="eyebrow">DOSSIER</p><h1>{esc(D['title'])}</h1><p class="article-deck">{esc(D['deck'])}</p><div class="article-meta"><span>{esc(D['author'])}</span><time datetime="{D['datePublished']}">Pubblicato: {D['dateLabel']}</time><span>Tempo di lettura: {D['readingMinutes']} minuti</span></div><div class="topic-list" aria-label="Argomenti">{''.join('<span>'+esc(tag)+'</span>' for tag in D['tags'])}</div></header>
    <figure class="article-hero"><img src="{D['image']}" width="{D['imageWidth']}" height="{D['imageHeight']}" alt="{esc(D['imageAlt'])}" fetchpriority="high"><figcaption>{esc(D['imageCaption'])}</figcaption></figure>
    <div class="article-layout"><div class="article-body"><p class="article-lead">{lead}</p><details class="dossier-contents"><summary>In questo dossier</summary><ol>{''.join(contents)}<li><a href="#fonti">Fonti</a></li></ol></details>
{chr(10).join(body)}
<section class="sources" aria-labelledby="fonti"><h2 id="fonti">FONTI</h2><ul class="sources-list">{''.join('<li>'+esc(source)+'</li>' for source in sources)}</ul></section>
    </div></div>
  </article>
  <footer class="footer"><span>Uno Sguardo sull’Uomo — {esc(D['category'])}</span><span><a href="privacy-cookie.html">Privacy e Cookie Policy</a></span><span><a href="mailto:unosguardosulluomo@gmail.com">unosguardosulluomo@gmail.com</a></span></footer>
</main><script src="date.js?v=20260826-audit-1"></script></body></html>
'''
(ROOT / D["slug"]).write_text(page, encoding="utf-8", newline="\n")


def card(kind="archive-card", heading="h3", eager=False):
    priority = ' fetchpriority="high"' if eager else ' loading="lazy"'
    return (
        f'<article class="{kind}" data-dossier="{esc(D["slug"])}">'
        f'<a class="story-image" href="{esc(D["slug"])}" aria-label="Leggi il dossier {esc(D["title"])}">'
        f'<img src="{esc(D["image"])}" width="{D["imageWidth"]}" height="{D["imageHeight"]}" alt="{esc(D["imageAlt"])}"{priority}></a>'
        f'<p class="eyebrow">{esc(D["cardEyebrow"])}</p>'
        f'<p class="archive-meta"><time datetime="{D["datePublished"]}">{D["dateLabel"]}</time></p>'
        f'<{heading}><a class="headline-link" href="{esc(D["slug"])}">{esc(D["title"])}</a></{heading}>'
        f'<p>{esc(D["description"])}</p>'
        f'<a class="read-more" href="{esc(D["slug"])}">Leggi il dossier →</a></article>'
    )


def dated_cards(markup):
    cards = re.findall(r'<article class="archive-card".*?</article>', markup, re.S)
    return sorted(cards, key=lambda item: re.search(r'datetime="(\d{4}-\d{2}-\d{2})"', item).group(1), reverse=True)


def change_card(markup, kind, heading):
    updated = re.sub(r'class="archive-card"', f'class="{kind}"', markup, count=1)
    updated = re.sub(r'<h3>', f'<{heading}>', updated, count=1)
    updated = re.sub(r'</h3>', f'</{heading}>', updated, count=1)
    updated = updated.replace(' fetchpriority="high"', ' loading="lazy"')
    return updated


def update_current_date(markup):
    return re.sub(
        r'<time class="current-date" datetime="[^"]+">.*?</time>',
        f'<time class="current-date" datetime="{D["datePublished"]}">{D["dateLabel"]}</time>',
        markup,
        count=1,
    )


def card_items(markup):
    items = []
    for position, article in enumerate(re.findall(r'<article class="[^"]*".*?</article>', markup, re.S), 1):
        href = re.search(r'<h[123]><a class="headline-link" href="([^"]+)">', article)
        name = re.search(r'<h[123]><a class="headline-link" href="[^"]+">(.*?)</a></h[123]>', article, re.S)
        if href and name:
            items.append({"@type": "ListItem", "position": position, "url": SITE + html.unescape(href.group(1)), "name": html.unescape(re.sub('<.*?>', '', name.group(1)))})
    return items


def rewrite_schema(markup, updater):
    match = re.search(r'<script type="application/ld\+json" data-seo-schema>(.*?)</script>', markup, re.S)
    if not match:
        raise RuntimeError("SEO schema not found")
    data = json.loads(match.group(1))
    updater(data)
    replacement = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return markup[:match.start(1)] + replacement + markup[match.end(1):]


archive_path = ROOT / D["categoryPath"]
archive = archive_path.read_text(encoding="utf-8")
archive = re.sub(r'<article class="archive-card" data-dossier="' + re.escape(D["slug"]) + r'".*?</article>', "", archive, flags=re.S)
archive = re.sub(r'(<div class="archive-grid">)\s*', r'\1\n', archive, count=1)
archive = archive.replace('<div class="archive-grid">\n', '<div class="archive-grid">\n' + card() + '\n', 1)
archive = update_current_date(archive)


def update_archive_schema(data):
    collection = next(item for item in data["@graph"] if item.get("@type") == "CollectionPage")
    items = card_items(archive)
    collection["mainEntity"]["numberOfItems"] = len(items)
    collection["mainEntity"]["itemListElement"] = items


archive = rewrite_schema(archive, update_archive_schema)
archive_path.write_text(archive, encoding="utf-8", newline="\n")

category_cards = dated_cards(archive)
indagini_path = ROOT / "indagini.html"
indagini = indagini_path.read_text(encoding="utf-8")
section = re.compile(r'(<section class="archive-section"><div class="archive-section-header"><h2><a class="headline-link" href="archivio-politica-italiana.html">Politica italiana</a></h2></div><div class="archive-grid">).*?(</div><a class="category-archive-link" href="archivio-politica-italiana.html">)', re.S)
indagini, count = section.subn(lambda match: match.group(1) + "".join(category_cards[:3]) + match.group(2), indagini, count=1)
if count != 1:
    raise RuntimeError("Politica italiana selection not found")
indagini = update_current_date(indagini)


def update_indagini_schema(data):
    collection = next(item for item in data["@graph"] if item.get("@type") == "CollectionPage")
    items = card_items(indagini)
    collection["mainEntity"]["numberOfItems"] = len(items)
    collection["mainEntity"]["itemListElement"] = items


indagini = rewrite_schema(indagini, update_indagini_schema)
indagini_path.write_text(indagini, encoding="utf-8", newline="\n")

all_archive_cards = []
for category_archive in ("archivio-politica-italiana.html", "archivio-politica-internazionale.html", "archivio-economia.html", "archivio-societa.html"):
    all_archive_cards.extend(dated_cards((ROOT / category_archive).read_text(encoding="utf-8")))
all_archive_cards.sort(key=lambda item: re.search(r'datetime="(\d{4}-\d{2}-\d{2})"', item).group(1), reverse=True)

home_path = ROOT / "index.html"
home = home_path.read_text(encoding="utf-8")
lead_card = change_card(all_archive_cards[0], "lead-story", "h1").replace(' loading="lazy"', ' fetchpriority="high"', 1)
side = "".join(change_card(item, "side-story", "h2") for item in all_archive_cards[1:3])
latest = "".join(change_card(item, "story-card", "h3") for item in all_archive_cards[3:6])
other = "".join(change_card(item, "story-card", "h3") for item in all_archive_cards[6:9])
home, count = re.subn(r'<article class="lead-story".*?</article>', lambda _: lead_card, home, count=1, flags=re.S)
if count != 1:
    raise RuntimeError("Home lead not found")
home, count = re.subn(r'(<aside>).*?(</aside>)', lambda match: match.group(1) + side + match.group(2), home, count=1, flags=re.S)
if count != 1:
    raise RuntimeError("Home sidebar not found")
home, count = re.subn(r'(<section class="story-grid" aria-label="Ultime indagini">).*?(</section>)', lambda match: match.group(1) + latest + match.group(2), home, count=1, flags=re.S)
if count != 1:
    raise RuntimeError("Home latest grid not found")
home, count = re.subn(r'(<section class="story-grid" aria-label="Altre indagini recenti">).*?(</section>)', lambda match: match.group(1) + other + match.group(2), home, count=1, flags=re.S)
if count != 1:
    raise RuntimeError("Home other grid not found")
home = update_current_date(home)


def update_home_schema(data):
    webpage = next(item for item in data["@graph"] if item.get("@type") == "WebPage")
    webpage["name"] = D["title"]


home = rewrite_schema(home, update_home_schema)
home_path.write_text(home, encoding="utf-8", newline="\n")

article_entry = f'  <url><loc>{URL}</loc><lastmod>{D["dateModified"]}</lastmod><image:image><image:loc>{SITE + D["socialImage"]}</image:loc></image:image></url>\n'
sitemap_articles_path = ROOT / "sitemap-articles.xml"
sitemap_articles = sitemap_articles_path.read_text(encoding="utf-8")
sitemap_articles = re.sub(r'\s*<url><loc>' + re.escape(URL) + r'</loc>.*?</url>', "", sitemap_articles, flags=re.S)
sitemap_articles = re.sub(r'(xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">)\s*', r'\1\n' + article_entry, sitemap_articles, count=1)
sitemap_articles_path.write_text(sitemap_articles, encoding="utf-8", newline="\n")

news_entry = f'  <url><loc>{URL}</loc><news:news><news:publication><news:name>Uno Sguardo sull’Uomo</news:name><news:language>it</news:language></news:publication><news:publication_date>{D["datePublished"]}</news:publication_date><news:title>{esc(D["title"])}</news:title></news:news></url>\n'
sitemap_news_path = ROOT / "sitemap-news.xml"
sitemap_news = sitemap_news_path.read_text(encoding="utf-8")
sitemap_news = re.sub(r'\s*<url><loc>' + re.escape(URL) + r'</loc>.*?</url>', "", sitemap_news, flags=re.S)
sitemap_news = re.sub(r'(xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">)\s*', r'\1\n' + news_entry, sitemap_news, count=1)
sitemap_news_path.write_text(sitemap_news, encoding="utf-8", newline="\n")

pub_dt = datetime.fromisoformat(D["datePublished"]).replace(tzinfo=timezone.utc)
rss_date = email.utils.format_datetime(pub_dt)
feed_item = f'''    <item>
      <title>{esc(D['title'])}</title>
      <link>{URL}</link>
      <guid isPermaLink="true">{URL}</guid>
      <pubDate>{rss_date}</pubDate>
      <category>{esc(D['category'])}</category>
      <description>{esc(D['description'])}</description>
    </item>
'''
feed_path = ROOT / "feed.xml"
feed = feed_path.read_text(encoding="utf-8")
feed = re.sub(r'\s*<item>\s*<title>' + re.escape(esc(D["title"])) + r'</title>.*?</item>', "", feed, flags=re.S)
feed = feed.replace('    <atom:link href="https://unosguardosulluomo.github.io/feed.xml" rel="self" type="application/rss+xml"/>\n', '    <atom:link href="https://unosguardosulluomo.github.io/feed.xml" rel="self" type="application/rss+xml"/>\n' + feed_item, 1)
feed_path.write_text(feed, encoding="utf-8", newline="\n")

sitemap_pages_path = ROOT / "sitemap-pages.xml"
sitemap_pages = sitemap_pages_path.read_text(encoding="utf-8")
for page_url in (SITE, SITE + "indagini.html", SITE + D["categoryPath"]):
    sitemap_pages = re.sub(r'(<loc>' + re.escape(page_url) + r'</loc><lastmod>)[^<]+', r'\g<1>' + D["dateModified"], sitemap_pages)
sitemap_pages_path.write_text(sitemap_pages, encoding="utf-8", newline="\n")

for filename in ("sitemap.xml", "sitemap-google.xml", "sitemap-index.xml"):
    path = ROOT / filename
    markup = path.read_text(encoding="utf-8")
    markup = re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{D["dateModified"]}</lastmod>', markup)
    path.write_text(markup, encoding="utf-8", newline="\n")

print("Built student protest dossier, editorial placements, feed and sitemaps")
