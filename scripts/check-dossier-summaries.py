"""Verify table-of-contents consistency across every published dossier."""

from pathlib import Path

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
articles = sorted(ROOT.glob("article-*.html"))
assert articles, "No dossier pages found"

total_links = 0
for path in articles:
    document = html.fromstring(path.read_text(encoding="utf-8"))
    summaries = document.xpath(
        "//div[contains(concat(' ',normalize-space(@class),' '),' article-body ')]"
        "/details[contains(concat(' ',normalize-space(@class),' '),' dossier-contents ')]"
    )
    assert len(summaries) == 1, path.name
    assert document.xpath("//link[contains(@href,'dossier-tables.css')]"), path.name

    article = document.xpath(
        "//article[contains(concat(' ',normalize-space(@class),' '),' article-page ')]"
    )[0]
    headings = article.xpath(".//h2")
    heading_ids = [heading.get("id") for heading in headings]
    summary_links = summaries[0].xpath("./ol/li/a/@href")
    assert headings, path.name
    assert all(heading_ids), path.name
    assert summary_links == [f"#{anchor}" for anchor in heading_ids], path.name

    all_ids = document.xpath("//@id")
    assert len(all_ids) == len(set(all_ids)), path.name
    total_links += len(summary_links)

print(f"Verified {len(articles)} dossier summaries ({total_links} working anchors).")
