"""Build the capital-human dossier and its editorial placements from one source."""

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "editorial/capitale-umano-lavoro-senior-italia.json").read_text(encoding="utf-8"))
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


body = []
contents = []
heading_number = 0
for block in D["blocks"]:
    kind = block["kind"]
    if kind == "h2":
        heading_number += 1
        anchor = f"sezione-{heading_number}"
        contents.append(f'<li><a href="#{anchor}">{esc(block["text"])}</a></li>')
        body.append(f'<h2 id="{anchor}">{esc(block["text"])}</h2>')
    elif kind == "image":
        body.append(
            f'<figure class="article-inline-figure"><img src="{esc(block["image"])}" '
            f'width="{block["width"]}" height="{block["height"]}" alt="{esc(block["alt"])}" '
            f'loading="lazy"><figcaption>{esc(block["caption"])}</figcaption></figure>'
        )
    elif kind == "quote":
        body.append(f'<blockquote class="article-pullquote">{esc(block["text"])}</blockquote>')
    elif kind == "p":
        body.append(f'<p>{esc(block["text"])}</p>')
    else:
        raise ValueError(f"Unknown block kind: {kind}")

organization = {
    "@type": ["Organization", "NewsMediaOrganization"],
    "@id": SITE + "#organization",
    "name": "Uno Sguardo sull’Uomo",
    "url": SITE,
    "logo": {"@type": "ImageObject", "url": SITE + "assets/testata.webp"},
}
schema = {
    "@context": "https://schema.org",
    "@graph": [
        organization,
        {
            "@type": "WebSite", "@id": SITE + "#website", "url": SITE,
            "name": "Uno Sguardo sull’Uomo", "publisher": {"@id": SITE + "#organization"},
            "inLanguage": "it-IT",
        },
        {
            "@type": "NewsArticle", "@id": URL + "#article", "headline": D["title"],
            "description": D["description"], "url": URL,
            "mainEntityOfPage": {"@type": "WebPage", "@id": URL},
            "datePublished": D["datePublished"], "image": [SITE + D["socialImage"]],
            "inLanguage": "it-IT", "articleSection": D["category"],
            "keywords": ", ".join(D["tags"]),
            "author": {"@type": "Organization", "name": "Redazione Uno Sguardo sull’Uomo", "url": SITE + "chi-siamo.html"},
            "publisher": {"@id": SITE + "#organization"},
            "isPartOf": {"@id": SITE + "#website"},
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": link}
                for i, (name, link) in enumerate([
                    ("Prima pagina", SITE),
                    (D["category"], SITE + D["categoryPath"]),
                    (D["title"], URL),
                ])
            ],
        },
    ],
}

nav = ('<nav class="nav" aria-label="Navigazione principale"><a href="/">Prima pagina</a>'
       '<a href="indagini.html">Indagini</a><a href="metodo.html">Metodo</a>'
       '<a href="chi-siamo.html">Chi siamo</a><a href="contatti.html">Contatti</a></nav>')

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
  <link rel="stylesheet" href="styles.css?v=20260811-mobile">
  <link rel="stylesheet" href="editorial-rules.css?v=20260812-1">
  <link rel="stylesheet" href="dossier-tables.css?v=20260919-2">
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
  <script type="application/ld+json" data-seo-schema>{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
  <main class="newspaper">
    <div class="utility-bar"><span>Quotidiano indipendente di approfondimento</span><span>Politica, società e istituzioni</span><time class="current-date" datetime="{D['datePublished']}">{D['dateLabel']}</time></div>
    <header class="masthead"><a href="/" aria-label="Prima pagina"><img src="assets/testata.webp" alt="Uno Sguardo sull’Uomo"></a></header>
    {nav}
    <article class="article-page">
      <header class="article-header">
        <a class="category-label" href="{D['categoryPath']}">{D['category']}</a>
        <p class="eyebrow">DOSSIER</p>
        <h1>{esc(D['title'])}</h1>
        <p class="article-deck">{esc(D['deck'])}</p>
        <div class="article-meta"><span>{D['author']}</span><time datetime="{D['datePublished']}">Pubblicato: {D['dateLabel']}</time><span>Tempo di lettura: {D['readingMinutes']} minuti</span></div>
        <div class="topic-list" aria-label="Argomenti">{''.join('<span>'+esc(t)+'</span>' for t in D['tags'])}</div>
      </header>
      <figure class="article-hero"><img src="{D['image']}" width="{D['imageWidth']}" height="{D['imageHeight']}" alt="{esc(D['imageAlt'])}" fetchpriority="high"><figcaption>{esc(D['imageCaption'])}</figcaption></figure>
      <div class="article-layout"><div class="article-body">
        <details class="dossier-contents"><summary>In questo dossier</summary><ol>{''.join(contents)}<li><a href="#fonti">Fonti documentali</a></li></ol></details>
{chr(10).join(body)}
<section class="sources" aria-labelledby="fonti"><h2 id="fonti">FONTI DOCUMENTALI</h2><ul class="sources-list">{''.join('<li>'+esc(s)+'</li>' for s in D['sources'])}</ul></section>
      </div></div>
    </article>
    <footer class="footer"><span>Uno Sguardo sull’Uomo — {D['category']}</span><span><a href="privacy-cookie.html">Privacy e Cookie Policy</a></span><span><a href="mailto:unosguardosulluomo@gmail.com">unosguardosulluomo@gmail.com</a></span></footer>
  </main>
  <script src="seo.js?v=20260903-google-1"></script><script src="date.js?v=20260826-audit-1"></script>
</body>
</html>
'''
(ROOT / D["slug"]).write_text(page, encoding="utf-8")

# Keep every Economia dossier in its full archive, newest first.
archive_path = ROOT / D["categoryPath"]
archive = archive_path.read_text(encoding="utf-8")
archive_card = card()
existing = re.compile(r'<article class="archive-card" data-dossier="' + re.escape(D["slug"]) + r'".*?</article>', re.S)
archive = existing.sub("", archive)
archive = re.sub(r'(<div class="archive-grid">)\s*', r'\1\n', archive, count=1)
archive = archive.replace('<div class="archive-grid">\n', '<div class="archive-grid">\n' + archive_card + '\n', 1)
archive_path.write_text(archive, encoding="utf-8")

# The Indagini category is a latest-three selection; source cards come from the archive.
cards = re.findall(r'<article class="archive-card".*?</article>', archive, re.S)
latest = sorted(cards, key=lambda c: re.search(r'datetime="(\d{4}-\d{2}-\d{2})"', c).group(1), reverse=True)[:3]
indagini_path = ROOT / "indagini.html"
indagini = indagini_path.read_text(encoding="utf-8")
section = re.compile(
    r'(<section class="archive-section"><div class="archive-section-header"><h2><a class="headline-link" href="archivio-economia.html">Economia</a></h2></div><div class="archive-grid">)'
    r'.*?(</div><a class="category-archive-link" href="archivio-economia.html">)', re.S
)
indagini, count = section.subn(lambda m: m.group(1) + "".join(latest) + m.group(2), indagini, count=1)
assert count == 1, "Economia selection not found"
indagini_path.write_text(indagini, encoding="utf-8")

# Editorial front page: the new dossier leads, with the two previous Economia stories alongside.
home_path = ROOT / "index.html"
home = home_path.read_text(encoding="utf-8")
lead = re.compile(r'<article class="lead-story".*?</article>', re.S)
home, count = lead.subn(lambda _: card("lead-story", "h1", True), home, count=1)
assert count == 1, "Home lead not found"
aside = re.compile(r'(<aside>).*?(</aside>)', re.S)
eni = next(c for c in cards if 'data-dossier="article-eni-baleine.html"' in c)
bollo = next(c for c in cards if 'data-dossier="article-bollo-auto-80kw.html"' in c)
def side(c):
    return c.replace('class="archive-card"', 'class="side-story"').replace('<h3>', '<h2>').replace('</h3>', '</h2>')
home, count = aside.subn(lambda m: m.group(1) + side(eni) + side(bollo) + m.group(2), home, count=1)
assert count == 1, "Home sidebar not found"
home_path.write_text(home, encoding="utf-8")

for filename in ("sitemap.xml", "sitemap-google.xml"):
    path = ROOT / filename
    xml = path.read_text(encoding="utf-8")
    for suffix in ("", "indagini.html", D["categoryPath"], D["slug"]):
        loc = SITE + suffix
        entry = f'<url><loc>{loc}</loc><lastmod>{D["datePublished"]}</lastmod></url>'
        pattern = re.compile(r'<url>\s*<loc>' + re.escape(loc) + r'</loc>.*?</url>', re.S)
        if pattern.search(xml):
            xml = pattern.sub(entry, xml, count=1)
        else:
            xml = xml.replace('</urlset>', '  ' + entry + '\n</urlset>')
    path.write_text(xml, encoding="utf-8")

print("Built dossier, images, placements and sitemaps from editorial source")
