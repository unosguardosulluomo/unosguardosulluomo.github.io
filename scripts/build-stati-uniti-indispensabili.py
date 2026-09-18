"""Publish the United States dossier from its single editorial JSON source."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "editorial/stati-uniti-indispensabili.json").read_text(encoding="utf-8"))
SITE = "https://unosguardosulluomo.github.io/"
esc = html.escape
url = SITE + D["slug"]


def card(kind="archive-card", heading="h3", lazy=True):
    loading = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return (
        f'<article class="{kind}" data-dossier="{D["slug"]}">'
        f'<a class="story-image" href="{D["slug"]}" aria-label="Leggi il dossier {esc(D["title"])}">'
        f'<img src="{D["image"]}" width="{D["imageWidth"]}" height="{D["imageHeight"]}" '
        f'alt="{esc(D["imageAlt"])}"{loading}></a>'
        '<p class="eyebrow">Politica internazionale • Canada • Stati Uniti</p>'
        f'<p class="archive-meta"><time datetime="{D["datePublished"]}">{D["dateLabel"]}</time></p>'
        f'<{heading}><a class="headline-link" href="{D["slug"]}">{esc(D["title"])}</a></{heading}>'
        f'<p>{esc(D["description"])}</p>'
        f'<a class="read-more" href="{D["slug"]}">Leggi il dossier →</a></article>'
    )


body = []
contents = []
heading_number = 0
for block in D["blocks"]:
    kind = block["kind"]
    if kind in ("h2", "h3"):
        heading_number += 1
        anchor = f"sezione-{heading_number}"
        body.append(f'<{kind} id="{anchor}">{esc(block["text"])}</{kind}>')
        if kind == "h2":
            contents.append(f'<li><a href="#{anchor}">{esc(block["text"])}</a></li>')
    elif kind == "figure":
        body.append(
            '<figure class="article-inline-figure">'
            f'<img src="{block["image"]}" width="{block["width"]}" height="{block["height"]}" '
            f'alt="{esc(block["alt"])}" loading="lazy">'
            f'<figcaption>{esc(block["caption"])}</figcaption></figure>'
        )
    else:
        body.append(f'<p>{esc(block["text"])}</p>')

org = {
    "@type": ["Organization", "NewsMediaOrganization"],
    "@id": SITE + "#organization",
    "name": "Uno Sguardo sull’Uomo",
    "url": SITE,
    "logo": {"@type": "ImageObject", "url": SITE + "assets/testata.webp"},
}
schema = {
    "@context": "https://schema.org",
    "@graph": [
        org,
        {
            "@type": "WebSite",
            "@id": SITE + "#website",
            "url": SITE,
            "name": "Uno Sguardo sull’Uomo",
            "publisher": {"@id": SITE + "#organization"},
            "inLanguage": "it-IT",
        },
        {
            "@type": "NewsArticle",
            "@id": url + "#article",
            "headline": D["title"],
            "description": D["description"],
            "url": url,
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "datePublished": D["datePublished"],
            "image": [SITE + D["image"]],
            "inLanguage": "it-IT",
            "articleSection": D["category"],
            "keywords": ", ".join(D["tags"]),
            "author": {
                "@type": "Organization",
                "name": "Redazione Uno Sguardo sull’Uomo",
                "url": SITE + "chi-siamo.html",
            },
            "publisher": {"@id": SITE + "#organization"},
            "isPartOf": {"@id": SITE + "#website"},
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Prima pagina", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": D["category"], "item": SITE + D["categoryPath"]},
                {"@type": "ListItem", "position": 3, "name": D["title"], "item": url},
            ],
        },
    ],
}
nav = (
    '<nav class="nav" aria-label="Navigazione principale"><a href="/">Prima pagina</a>'
    '<a href="indagini.html">Indagini</a><a href="metodo.html">Metodo</a>'
    '<a href="chi-siamo.html">Chi siamo</a><a href="contatti.html">Contatti</a></nav>'
)
out = f'''<!doctype html>
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
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE + D['image']}">
  <meta property="og:image:alt" content="{esc(D['imageAlt'])}">
  <meta property="og:image:width" content="{D['imageWidth']}">
  <meta property="og:image:height" content="{D['imageHeight']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(D['title'])}">
  <meta name="twitter:description" content="{esc(D['description'])}">
  <meta name="twitter:image" content="{SITE + D['image']}">
  <meta property="article:published_time" content="{D['datePublished']}">
  <meta property="article:section" content="{D['category']}">
  <link rel="canonical" href="{url}">
  <title>{esc(D['title'])} — Uno Sguardo sull'Uomo</title>
  <link rel="stylesheet" href="styles.css?v=20260811-mobile">
  <link rel="stylesheet" href="editorial-rules.css?v=20260812-1">
  <link rel="stylesheet" href="dossier-tables.css?v=20260917-1">
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
        <div class="article-meta"><span>{D['author']}</span><time datetime="{D['datePublished']}">Pubblicato: {D['dateLabel']}</time><span>Tempo di lettura: {D['readingMinutes']} minuti</span><span>Quadro politico al {D['contentAsOf']}</span></div>
        <div class="topic-list" aria-label="Argomenti">{''.join('<span>' + esc(tag) + '</span>' for tag in D['tags'])}</div>
      </header>
      <figure class="article-hero"><img src="{D['image']}" width="{D['imageWidth']}" height="{D['imageHeight']}" alt="{esc(D['imageAlt'])}" fetchpriority="high"><figcaption>{esc(D['imageCaption'])}</figcaption></figure>
      <div class="article-layout"><div class="article-body">
        <details class="dossier-contents"><summary>In questo dossier</summary><ol>{''.join(contents)}<li><a href="#fonti">Fonti documentali</a></li></ol></details>
{chr(10).join(body)}
<section class="sources" aria-labelledby="fonti"><h2 id="fonti">FONTI DOCUMENTALI</h2><ul class="sources-list">{''.join('<li>' + esc(source) + '</li>' for source in D['sources'])}</ul></section>
      </div></div>
    </article>
    <footer class="footer"><span>Uno Sguardo sull’Uomo — {D['category']}</span><span><a href="privacy-cookie.html">Privacy e Cookie Policy</a></span><span><a href="mailto:unosguardosulluomo@gmail.com">unosguardosulluomo@gmail.com</a></span></footer>
  </main>
  <script src="seo.js?v=20260903-google-1"></script><script src="date.js?v=20260826-audit-1"></script>
</body>
</html>
'''
(ROOT / D["slug"]).write_text(out, encoding="utf-8")

# Keep the category archive complete and ordered newest first.
archive = ROOT / D["categoryPath"]
archive_html = archive.read_text(encoding="utf-8")
managed = r'<article\b[^>]*>\s*<a\b[^>]*href="' + re.escape(D["slug"]) + r'".*?</article>'
if re.search(managed, archive_html, re.S):
    archive_html = re.sub(managed, card(), archive_html, count=1, flags=re.S)
else:
    archive_html = archive_html.replace('<div class="archive-grid">', '<div class="archive-grid">\n' + card(), 1)
archive.write_text(archive_html, encoding="utf-8")

all_cards = re.findall(r'<article\b[^>]*>.*?</article>', archive_html, re.S)
latest = sorted(
    all_cards,
    key=lambda item: re.search(r'datetime="([\d-]+)"', item).group(1),
    reverse=True,
)[:3]
indagini = ROOT / "indagini.html"
indagini_html = indagini.read_text(encoding="utf-8")
pattern = (
    r'(<section class="archive-section"><div class="archive-section-header"><h2><a class="headline-link" href="'
    + re.escape(D["categoryPath"])
    + r'">.*?</h2></div><div class="archive-grid">).*?(</div><a class="category-archive-link")'
)
indagini_html, replacements = re.subn(
    pattern, lambda match: match.group(1) + "".join(latest) + match.group(2),
    indagini_html, count=1, flags=re.S
)
assert replacements == 1, "Category section not found"
indagini.write_text(indagini_html, encoding="utf-8")

# Promote the dossier to the home lead and retain the former lead among the latest stories.
home = ROOT / "index.html"
home_html = home.read_text(encoding="utf-8")
lead = re.search(r'<article class="lead-story"[^>]*>.*?</article>', home_html, re.S)
assert lead, "Home lead not found"
old_lead = lead.group(0)
home_html = home_html[:lead.start()] + card("lead-story", "h1", False) + home_html[lead.end():]
if D["slug"] not in old_lead:
    old_lead = (
        old_lead.replace('class="lead-story"', 'class="story-card"')
        .replace(' fetchpriority="high"', ' loading="lazy"')
        .replace("<h1>", "<h3>")
        .replace("</h1>", "</h3>")
    )
    marker = '<section class="story-grid" aria-label="Ultime indagini">'
    start = home_html.index(marker) + len(marker)
    end = home_html.index("</section>", start)
    existing = re.findall(r'<article\b[^>]*>.*?</article>', home_html[start:end], re.S)
    home_html = home_html[:start] + "\n      " + "\n      ".join([old_lead] + existing[:2]) + "\n    " + home_html[end:]
home.write_text(home_html, encoding="utf-8")

for sitemap_name in ("sitemap.xml", "sitemap-google.xml"):
    sitemap_path = ROOT / sitemap_name
    sitemap = sitemap_path.read_text(encoding="utf-8")
    for page in ("", "indagini.html", D["categoryPath"], D["slug"]):
        location = SITE + page
        entry = f'<url><loc>{location}</loc><lastmod>{D["datePublished"]}</lastmod></url>'
        url_pattern = r'<url>\s*<loc>' + re.escape(location) + r'</loc>.*?</url>'
        if re.search(url_pattern, sitemap, re.S):
            sitemap = re.sub(url_pattern, entry, sitemap, count=1, flags=re.S)
        else:
            sitemap = sitemap.replace("</urlset>", "  " + entry + "\n</urlset>")
    sitemap_path.write_text(sitemap, encoding="utf-8")

print("Generated dossier, home, archive, latest three and both sitemaps.")
