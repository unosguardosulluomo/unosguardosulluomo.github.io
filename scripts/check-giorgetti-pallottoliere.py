"""Validate publication metadata, placements, sources, links and acronyms."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "editorial/giorgetti-pallottoliere.json").read_text(encoding="utf-8"))
page_path = ROOT / D["slug"]
page = page_path.read_text(encoding="utf-8")

assert f'<link rel="canonical" href="https://unosguardosulluomo.github.io/{D["slug"]}">' in page
assert f'<meta property="og:url" content="https://unosguardosulluomo.github.io/{D["slug"]}">' in page
assert f'<meta property="article:published_time" content="{D["datePublished"]}">' in page
assert f'<meta property="article:section" content="{D["category"]}">' in page
assert page.count("<figure class=") == 2
assert page.count("intelligenza artificiale") == 2
sources_html = re.search(r'<ul class="sources-list">(.*?)</ul>', page, re.S).group(1)
assert sources_html.count("<li>") >= 10
assert "<a " not in sources_html
plain = re.sub(r"<[^>]+>", " ", page)
assert "Istituto nazionale di statistica (Istat)" in plain
assert "prodotto interno lordo (PIL)" in plain
assert "imposta sul valore aggiunto (IVA)" in plain
assert "una aspettativa" not in plain

for filename in ("index.html", "indagini.html", "archivio-economia.html", "sitemap.xml", "sitemap-google.xml"):
    text = (ROOT / filename).read_text(encoding="utf-8")
    assert D["slug"] in text, f"Missing placement in {filename}"

for value in re.findall(r'(?:href|src)="([^"]+)"', page):
    if not value or value.startswith(("http://", "https://", "mailto:", "#", "/")):
        continue
    target = ROOT / value.split("?", 1)[0]
    assert target.exists(), f"Broken local reference: {value}"

schema_text = re.search(r'<script type="application/ld\+json" data-seo-schema>(.*?)</script>', page, re.S).group(1)
schema = json.loads(schema_text)
article = next(item for item in schema["@graph"] if item.get("@type") == "NewsArticle")
assert article["datePublished"] == D["datePublished"]
assert article["articleSection"] == D["category"]

print("Giorgetti dossier checks passed")
