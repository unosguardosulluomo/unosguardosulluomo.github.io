"""Generate the dossier and its cards from editorial/guerra-pace-difesa.json.

Run from any directory with Python 3. Only this dossier, its home placement,
its category's latest-three cards, its archive and sitemap entries are managed.
No runtime JavaScript rewrites editorial content.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'editorial/guerra-pace-difesa.json').read_text(encoding='utf-8'))
SITE = 'https://unosguardosulluomo.github.io/'
esc = html.escape
url = SITE + D['slug']

def text(value):
    value = esc(value)
    for title, path in [('ELLY: UN NOME, UNA GARANZIA?', 'article-elly-nome-garanzia.html'),
                        ('VANNACCI: UN ALTRO BUGIARDO?', 'article-vannacci-un-altro-bugiardo.html')]:
        value = value.replace(esc(title), f'<a href="{path}">{esc(title)}</a>')
    return value

def card(kind='archive-card', heading='h3', lazy=True):
    loading = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return (f'<article class="{kind}" data-dossier="{D["slug"]}">'
            f'<a class="story-image" href="{D["slug"]}" aria-label="Leggi il dossier {esc(D["title"])}">'
            f'<img src="{D["image"]}" width="1672" height="941" alt="{esc(D["imageAlt"])}"{loading}></a>'
            f'<p class="eyebrow">{D["category"]} • Ucraina • Difesa</p>'
            f'<p class="archive-meta"><time datetime="{D["datePublished"]}">{D["dateLabel"]}</time></p>'
            f'<{heading}><a class="headline-link" href="{D["slug"]}">{esc(D["title"])}</a></{heading}>'
            f'<p>{esc(D["description"])}</p><a class="read-more" href="{D["slug"]}">Leggi il dossier →</a></article>')

body=[]
contents=[]
for block in D['blocks']:
    kind=block['kind']
    if kind=='table':
        rows=block['rows']
        head=''.join(f'<th scope="col">{esc(v)}</th>' for v in rows[0])
        table=[]
        for row in rows[1:]:
            table.append('<tr>'+''.join(f'<th scope="row">{esc(v)}</th>' if i==0 else f'<td>{esc(v)}</td>' for i,v in enumerate(row))+'</tr>')
        body.append('<p class="table-hint" id="table-help">Su smartphone, scorri la tabella orizzontalmente per confrontare tutte le posizioni.</p>'
                    '<div class="data-table-wrap" role="region" aria-label="Confronto delle posizioni politiche" aria-describedby="table-help" tabindex="0">'
                    f'<table class="data-table"><caption>{esc(block["caption"])}</caption><thead><tr>{head}</tr></thead><tbody>{"".join(table)}</tbody></table></div>')
    elif kind in ('h2','h3'):
        anchor=f'sezione-{block["sourceParagraph"]}'
        body.append(f'<{kind} id="{anchor}">{text(block["text"])}</{kind}>')
        if kind=='h2':contents.append(f'<li><a href="#{anchor}">{esc(block["text"])}</a></li>')
    else:
        cls=' class="article-pullquote"' if kind=='quote' else ''
        body.append(f'<p{cls}>{text(block["text"])}</p>')

org={'@type':['Organization','NewsMediaOrganization'],'@id':SITE+'#organization','name':'Uno Sguardo sull’Uomo','url':SITE,'logo':{'@type':'ImageObject','url':SITE+'assets/testata.webp'}}
schema={'@context':'https://schema.org','@graph':[org,{'@type':'WebSite','@id':SITE+'#website','url':SITE,'name':'Uno Sguardo sull’Uomo','publisher':{'@id':SITE+'#organization'},'inLanguage':'it-IT'},
 {'@type':'NewsArticle','@id':url+'#article','headline':D['title'],'description':D['description'],'url':url,'mainEntityOfPage':{'@type':'WebPage','@id':url},'datePublished':D['datePublished'],'image':[SITE+D['image']],'inLanguage':'it-IT','articleSection':D['category'],'keywords':', '.join(D['tags']),'author':{'@type':'Organization','name':'Redazione Uno Sguardo sull’Uomo','url':SITE+'chi-siamo.html'},'publisher':{'@id':SITE+'#organization'},'isPartOf':{'@id':SITE+'#website'}},
 {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':link} for i,(name,link) in enumerate([('Prima pagina',SITE),(D['category'],SITE+D['categoryPath']),(D['title'],url)])]}]}
nav='<nav class="nav" aria-label="Navigazione principale"><a href="/">Prima pagina</a><a href="indagini.html">Indagini</a><a href="metodo.html">Metodo</a><a href="chi-siamo.html">Chi siamo</a><a href="contatti.html">Contatti</a></nav>'
out=f'''<!doctype html>
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
  <meta property="og:image" content="{SITE+D['image']}">
  <meta property="og:image:alt" content="{esc(D['imageAlt'])}">
  <meta property="og:image:width" content="1672">
  <meta property="og:image:height" content="941">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(D['title'])}">
  <meta name="twitter:description" content="{esc(D['description'])}">
  <meta name="twitter:image" content="{SITE+D['image']}">
  <meta property="article:published_time" content="{D['datePublished']}">
  <meta property="article:section" content="{D['category']}">
  <link rel="canonical" href="{url}">
  <title>{esc(D['title'])} — Uno Sguardo sull'Uomo</title>
  <link rel="stylesheet" href="styles.css?v=20260811-mobile">
  <link rel="stylesheet" href="editorial-rules.css?v=20260812-1">
  <link rel="stylesheet" href="dossier-tables.css?v=20260917-1">
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
  <script type="application/ld+json" data-seo-schema>{json.dumps(schema,ensure_ascii=False)}</script>
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
        <div class="topic-list" aria-label="Argomenti">{''.join('<span>'+esc(t)+'</span>' for t in D['tags'])}</div>
      </header>
      <figure class="article-hero"><img src="{D['image']}" width="1672" height="941" alt="{esc(D['imageAlt'])}" fetchpriority="high"><figcaption>{esc(D['imageCaption'])}</figcaption></figure>
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
(ROOT/D['slug']).write_text(out,encoding='utf-8')

# Archive remains complete. Only insert/replace the card managed by this source.
archive=ROOT/D['categoryPath']
a=archive.read_text(encoding='utf-8')
managed=r'<article\b[^>]*>\s*<a\b[^>]*href="'+re.escape(D['slug'])+r'".*?</article>'
if re.search(managed,a,re.S):a=re.sub(managed,card(),a,count=1,flags=re.S)
else:a=a.replace('<div class="archive-grid">','<div class="archive-grid">\n'+card(),1)
archive.write_text(a,encoding='utf-8')
all_cards=re.findall(r'<article\b[^>]*>.*?</article>',a,re.S)
latest=sorted(all_cards,key=lambda c:re.search(r'datetime="([\d-]+)"',c)[1],reverse=True)[:3]
indagini=ROOT/'indagini.html'
s=indagini.read_text(encoding='utf-8')
pattern=r'(<section class="archive-section"><div class="archive-section-header"><h2><a class="headline-link" href="'+re.escape(D['categoryPath'])+r'">.*?</h2></div><div class="archive-grid">).*?(</div><a class="category-archive-link")'
s,n=re.subn(pattern,lambda m:m[1]+''.join(latest)+m[2],s,count=1,flags=re.S)
assert n==1,'Category section not found'
indagini.write_text(s,encoding='utf-8')

home=ROOT/'index.html'
s=home.read_text(encoding='utf-8')
match=re.search(r'<article class="lead-story"[^>]*>.*?</article>',s,re.S)
assert match,'Home lead not found'
old=match[0]
s=s[:match.start()]+card('lead-story','h1',False)+s[match.end():]
if D['slug'] not in old:
    old=old.replace('class="lead-story"','class="story-card"').replace('<h1>','<h3>').replace('</h1>','</h3>')
    marker='<section class="story-grid" aria-label="Ultime indagini">'
    start=s.index(marker)+len(marker)
    end=s.index('</section>',start)
    existing=re.findall(r'<article\b[^>]*>.*?</article>',s[start:end],re.S)
    s=s[:start]+'\n      '+'\n      '.join([old]+existing[:2])+'\n    '+s[end:]
home.write_text(s,encoding='utf-8')

for name in ('sitemap.xml','sitemap-google.xml'):
    path=ROOT/name
    s=path.read_text(encoding='utf-8')
    for page in ('','indagini.html',D['categoryPath'],D['slug']):
        loc=SITE+page
        entry=f'<url><loc>{loc}</loc><lastmod>{D["datePublished"]}</lastmod></url>'
        pattern=r'<url>\s*<loc>'+re.escape(loc)+r'</loc>.*?</url>'
        if re.search(pattern,s,re.S):s=re.sub(pattern,entry,s,count=1,flags=re.S)
        else:s=s.replace('</urlset>','  '+entry+'\n</urlset>')
    path.write_text(s,encoding='utf-8')
print('Generated dossier, home, category archive, latest three and both sitemaps.')
