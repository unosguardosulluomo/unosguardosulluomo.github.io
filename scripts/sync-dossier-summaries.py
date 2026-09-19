"""Add or rebuild the same collapsible table of contents in every dossier."""

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STYLE = '<link rel="stylesheet" href="dossier-tables.css?v=20260919-2">'
BODY_MARKER = '<div class="article-body">'


def plain_text(markup):
    value = re.sub(r"<[^>]+>", " ", markup)
    return " ".join(html.unescape(value).split())


def synchronize(path):
    source = path.read_text(encoding="utf-8")
    if BODY_MARKER not in source:
        raise RuntimeError(f"Article body not found: {path.name}")

    body_start = source.index(BODY_MARKER) + len(BODY_MARKER)
    article_end = source.index("</article>", body_start)
    body = source[body_start:article_end]
    body = re.sub(
        r"\s*<details class=\"dossier-contents\">.*?</details>\s*",
        "\n",
        body,
        count=1,
        flags=re.S,
    )

    used_ids = set(re.findall(r'\bid="([^"]+)"', source))
    entries = []
    number = 0

    def prepare_heading(match):
        nonlocal number
        number += 1
        attributes, contents = match.group(1), match.group(2)
        existing = re.search(r'\bid="([^"]+)"', attributes)
        if existing:
            anchor = existing.group(1)
        else:
            anchor = f"sezione-{number}"
            suffix = 2
            while anchor in used_ids:
                anchor = f"sezione-{number}-{suffix}"
                suffix += 1
            attributes += f' id="{anchor}"'
            used_ids.add(anchor)
        entries.append((anchor, plain_text(contents)))
        return f"<h2{attributes}>{contents}</h2>"

    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", prepare_heading, body, flags=re.S | re.I)
    if not entries:
        raise RuntimeError(f"No section headings found: {path.name}")

    items = "".join(
        f'<li><a href="#{html.escape(anchor, quote=True)}">{html.escape(label)}</a></li>'
        for anchor, label in entries
    )
    summary = (
        '<details class="dossier-contents"><summary>In questo dossier</summary>'
        f"<ol>{items}</ol></details>"
    )
    updated = source[:body_start] + "\n" + summary + body + source[article_end:]

    if "dossier-tables.css" in updated:
        updated = re.sub(
            r'<link rel="stylesheet" href="dossier-tables\.css\?v=[^"]+">',
            STYLE,
            updated,
            count=1,
        )
    else:
        updated = updated.replace("</head>", f"  {STYLE}\n</head>", 1)

    if updated != source:
        path.write_text(updated, encoding="utf-8")
    return len(entries)


results = [(path.name, synchronize(path)) for path in sorted(ROOT.glob("article-*.html"))]
print(f"Synchronized {len(results)} dossier summaries ({sum(count for _, count in results)} links).")
