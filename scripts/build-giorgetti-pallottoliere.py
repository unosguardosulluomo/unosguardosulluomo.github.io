"""Build the Giorgetti dossier and all editorial placements from DOCX and metadata."""

import html
import json
import re
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "editorial/giorgetti-pallottoliere.json").read_text(encoding="utf-8"))
SITE = "https://unosguardosulluomo.github.io/"
URL = SITE + D["slug"]


def esc(value):
    return html.escape(str(value), quote=True)


def card(kind="archive-card", heading="h3", eager=False):
    priority = ' fetchpriority="high"' if eager else ' loading="lazy"'
    return (
        f'<article class="{kind}" data-dossier="{esc(D["slug"])}">'
        f'<a class="story-image" href="{esc(D["slug"])}" aria-label="Leggi il dossier {esc(D["title"])}">'
        f'<img src="{esc(D["image"])}" width="{D["imageWidth"]}" height="{D["imageHeight"]}" '
        f'alt="{esc(D["imageAlt"])}"{priority}></a>'
        f'<p class="eyebrow">{esc(D["cardEyebrow"])}</p>'
        f'<p class="archive-meta"><time datetime="{D["datePublished"]}">{D["dateLabel"]}</time></p>'
        f'<{heading}><a class="headline-link" href="{esc(D["slug"])}">{esc(D["title"])}</a></{heading}>'
        f'<p>{esc(D["description"])}</p>'
        f'<a class="read-more" href="{esc(D["slug"])}">Leggi il dossier →</a></article>'
    )


doc = Document(ROOT / D["sourceDocx"])
body = []
contents = []
sources = []
heading_number = 0
in_sources = False

for paragraph in doc.paragraphs[3:]:
    text = paragraph.text.strip()
    if not text:
        continue
    style = paragraph.style.name
    if style == "Heading 1" and text == "Fonti principali":
        in_sources = True
        continue
    if in_sources:
        sources.append(text)
        continue
    if style == "Heading 1":
        heading_number += 1
        if heading_number == 2:
            body.append(
                f'<figure class="article-inline-figure"><img src="{esc(D["inlineImage"])}" '
                f'width="{D["inlineImageWidth"]}" height="{D["inlineImageHeight"]}" '
                f'alt="{esc(D["inlineImageAlt"])}" loading="lazy">'
                f'<figcaption>{esc(D["inlineImageCaption"])}</figcaption></figure>'
            )
        anchor = f"sezione-{heading_number}"
        contents.append(f'<li><a href="#{anchor}">{esc(text)}</a></li>')
        body.append(f'<h2 id="{anchor}">{esc(text)}</h2>')
    elif style == "Pull Quote":
        body.append(f'<blockquote class="article-pullquote">{esc(text)}</blockquote>')
    else:
        body.append(f'<p>{esc(text)}</p>')

if not sources:
    raise RuntimeError("No document sources found")

organization = {
    "@type": ["Organization", "NewsMediaOrganization"],
    "@id": SITE + "#organization", "name": "Uno Sguardo sull’Uomo", "url": SITE,
    "logo": {"@type": "ImageObject", "url": SITE + "assets/testata.webp"},
}
schema = {
    "@context": "https://schema.org",
    "@graph": [
        organization,
        {"@type": "WebSite", "@id": SITE + "#website", "url": SITE, "name": "Uno Sguardo sull’Uomo", "publisher": {"@id": SITE + "#organization"}, "inLanguage": "it-IT"},
        {"@type": "NewsArticle", "@id": URL + "#article", "headline": D["title"], "description": D["description"], "url": URL,
         "mainEntityOfPage": {"@type": "WebPage", "@id": URL}, "datePublished": D["datePublished"],
         "image": [SITE + D["socialImage"]], "inLanguage": "it-IT", "articleSection": D["category"],
         "keywords": ", ".join(D["tags"]), "author": {"@type": "Organization", "name": "Redazione Uno Sguardo sull’Uomo", "url": SITE + "chi-siamo.html"},
         "publisher": {"@id": SITE + "#organization"}, "isPartOf": {"@id": SITE + "#website"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Prima pagina", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": D["category"], "item": SITE + D["categoryPath"]},
            {"@type": "ListItem", "position": 3, "name": D["title"], "item": URL},
        ]},
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
  <meta property="og:title" content="{esc(D['title'])}">
  <meta property="og:description" content="{esc(D['description'])}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{URL}">
  <meta property="og:image" content="{SITE+D['socialImage']}">
  <meta property="og:image:alt" content="{esc(D['imageAlt'])}">
  <meta property="og:image:width" content="{D['socialImageWidth']}">
  <meta property="og:image:height" content="{D['socialImageHeight']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(D['title'])}">
  <meta name="twitter:description" content="{esc(D['description'])}">
  <meta name="twitter:image" content="{SITE+D['socialImage']}">
  <meta property="article:published_time" content="{D['datePublished']}">
  <meta property="article:section" content="{D['category']}">
  <link rel="canonical" href="{URL}">
  <title>{esc(D['title'])} — Uno Sguardo sull'Uomo</title>
  <link rel="stylesheet" href="styles.css?v=20260921-brand-1">
  <link rel="stylesheet" href="editorial-rules.css?v=20260812-1">
  <link rel="stylesheet" href="dossier-tables.css?v=20260919-2">
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
  <script type="application/ld+json" data-seo-schema>{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body><main class="newspaper">
  <div class="utility-bar"><span>Quotidiano indipendente di approfondimento</span><span>Politica, società e istituzioni</span><time class="current-date" datetime="{D['datePublished']}">{D['dateLabel']}</time></div>
  <header class="masthead"><a href="/" aria-label="Prima pagina"><img src="assets/testata.webp" alt="Uno Sguardo sull’Uomo"></a></header>
  <nav class="nav" aria-label="Navigazione principale"><a href="/">Prima pagina</a><a href="indagini.html">Indagini</a><a href="metodo.html">Metodo</a><a href="chi-siamo.html">Chi siamo</a><a href="contatti.html">Contatti</a></nav>
  <article class="article-page">
    <header class="article-header"><a class="category-label" href="{D['categoryPath']}">{D['category']}</a><p class="eyebrow">DOSSIER</p><h1>{esc(D['title'])}</h1><p class="article-deck">{esc(D['deck'])}</p><div class="article-meta"><span>{D['author']}</span><time datetime="{D['datePublished']}">Pubblicato: {D['dateLabel']}</time><span>Tempo di lettura: {D['readingMinutes']} minuti</span></div><div class="topic-list" aria-label="Argomenti">{''.join('<span>'+esc(t)+'</span>' for t in D['tags'])}</div></header>
    <figure class="article-hero"><img src="{D['image']}" width="{D['imageWidth']}" height="{D['imageHeight']}" alt="{esc(D['imageAlt'])}" fetchpriority="high"><figcaption>{esc(D['imageCaption'])}</figcaption></figure>
    <div class="article-layout"><div class="article-body"><details class="dossier-contents"><summary>In questo dossier</summary><ol>{''.join(contents)}<li><a href="#fonti">Fonti documentali</a></li></ol></details>
{chr(10).join(body)}
<section class="sources" aria-labelledby="fonti"><h2 id="fonti">FONTI DOCUMENTALI</h2><ul class="sources-list">{''.join('<li>'+esc(s)+'</li>' for s in sources)}</ul></section>
    </div></div>
  </article>
  <footer class="footer"><span>Uno Sguardo sull’Uomo — {D['category']}</span><span><a href="privacy-cookie.html">Privacy e Cookie Policy</a></span><span><a href="mailto:unosguardosulluomo@gmail.com">unosguardosulluomo@gmail.com</a></span></footer>
</main><script src="seo.js?v=20260903-google-1"></script><script src="date.js?v=20260826-audit-1"></script></body></html>
'''
(ROOT / D["slug"]).write_text(page, encoding="utf-8")

archive_path = ROOT / D["categoryPath"]
archive = archive_path.read_text(encoding="utf-8")
archive = re.sub(r'<article class="archive-card" data-dossier="' + re.escape(D["slug"]) + r'".*?</article>', "", archive, flags=re.S)
archive = re.sub(r'(<div class="archive-grid">)\s*', r'\1\n', archive, count=1)
archive = archive.replace('<div class="archive-grid">\n', '<div class="archive-grid">\n' + card() + '\n', 1)
archive_path.write_text(archive, encoding="utf-8")

cards = re.findall(r'<article class="archive-card".*?</article>', archive, re.S)
latest = sorted(cards, key=lambda c: re.search(r'datetime="(\d{4}-\d{2}-\d{2})"', c).group(1), reverse=True)

indagini_path = ROOT / "indagini.html"
indagini = indagini_path.read_text(encoding="utf-8")
section = re.compile(r'(<section class="archive-section"><div class="archive-section-header"><h2><a class="headline-link" href="archivio-economia.html">Economia</a></h2></div><div class="archive-grid">).*?(</div><a class="category-archive-link" href="archivio-economia.html">)', re.S)
indagini, count = section.subn(lambda m: m.group(1) + "".join(latest[:3]) + m.group(2), indagini, count=1)
assert count == 1, "Economia selection not found"
indagini_path.write_text(indagini, encoding="utf-8")

home_path = ROOT / "index.html"
home = home_path.read_text(encoding="utf-8")
home, count = re.subn(r'<article class="lead-story".*?</article>', lambda _: card("lead-story", "h1", True), home, count=1, flags=re.S)
assert count == 1, "Home lead not found"
def side(c):
    return c.replace('class="archive-card"', 'class="side-story"').replace('<h3>', '<h2>').replace('</h3>', '</h2>')
home, count = re.subn(r'(<aside>).*?(</aside>)', lambda m: m.group(1) + side(latest[1]) + side(latest[2]) + m.group(2), home, count=1, flags=re.S)
assert count == 1, "Home sidebar not found"
home_path.write_text(home, encoding="utf-8")

for filename in ("sitemap.xml", "sitemap-google.xml"):
    path = ROOT / filename
    xml = path.read_text(encoding="utf-8")
    for suffix in ("", "indagini.html", D["categoryPath"], D["slug"]):
        loc = SITE + suffix
        entry = f'<url><loc>{loc}</loc><lastmod>{D["datePublished"]}</lastmod></url>'
        pattern = re.compile(r'<url>\s*<loc>' + re.escape(loc) + r'</loc>.*?</url>', re.S)
        xml = pattern.sub(entry, xml, count=1) if pattern.search(xml) else xml.replace('</urlset>', '  ' + entry + '\n</urlset>')
    path.write_text(xml, encoding="utf-8")

print("Built Giorgetti dossier, placements and sitemaps")
