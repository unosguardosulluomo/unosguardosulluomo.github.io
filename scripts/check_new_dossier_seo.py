#!/usr/bin/env python3
"""Require an evidence-based SEO brief for every newly added dossier."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_INTENTS = {
    "informativo-attualità",
    "informativo-approfondimento",
    "navigazionale",
}
REQUIRED_SLUG_PREFIXES = (
    "article-geopolitica-politica-italiana-",
    "article-geopolitica-politica-internazionale-",
    "article-geopolitica-economia-",
    "article-geopolitica-societa-",
)
STOPWORDS = {
    "alla", "alle", "anche", "come", "dalla", "delle", "della", "degli",
    "dello", "italia", "italiana", "italiano", "nella", "nelle", "negli",
    "nello", "perché", "questa", "questo", "sulla", "sulle", "sugli",
    "sullo", "senza", "verso",
}


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Comando Git fallito")
    return result.stdout


def comparison_base() -> str:
    if len(sys.argv) == 3 and sys.argv[1] == "--base":
        return sys.argv[2]
    github_base = os.environ.get("GITHUB_BASE_REF", "").strip()
    if github_base:
        return f"origin/{github_base}"
    return "HEAD^"


def normal(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in folded if not unicodedata.combining(char))


def significant_words(value: str) -> set[str]:
    return {
        word for word in re.findall(r"[a-z0-9]{4,}", normal(value))
        if word not in STOPWORDS
    }


def main() -> None:
    base = comparison_base()
    added = [
        line.strip()
        for line in git("diff", "--name-only", "--diff-filter=A", f"{base}...HEAD", "--", "article-*.html").splitlines()
        if line.strip()
    ]
    errors: list[str] = []
    metadata_files = list((ROOT / "editorial").glob("*.json"))
    metadata = []
    for path in metadata_files:
        try:
            metadata.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}: JSON non valido ({exc})")

    for relative in added:
        path = ROOT / relative
        source = path.read_text(encoding="utf-8")
        if "data-legacy-redirect" in source[:1000]:
            continue
        if not path.name.startswith(REQUIRED_SLUG_PREFIXES):
            errors.append(f"{relative}: slug privo di macroarea e microarea")
        matches = [(meta_path, data) for meta_path, data in metadata if data.get("slug") == path.name]
        if len(matches) != 1:
            errors.append(f"{relative}: atteso un solo file editorial/*.json, trovati {len(matches)}")
            continue
        meta_path, data = matches[0]
        seo = data.get("seo")
        if not isinstance(seo, dict):
            errors.append(f"{meta_path.relative_to(ROOT)}: oggetto seo mancante")
            continue
        primary = str(seo.get("primaryQuery", "")).strip()
        intent = str(seo.get("searchIntent", "")).strip()
        questions = seo.get("supportingQueries")
        checked = str(seo.get("serpCheckedAt", "")).strip()
        if len(primary) < 4:
            errors.append(f"{meta_path.relative_to(ROOT)}: seo.primaryQuery mancante")
        if intent not in ALLOWED_INTENTS:
            errors.append(f"{meta_path.relative_to(ROOT)}: seo.searchIntent non riconosciuto")
        if not isinstance(questions, list) or len({str(item).strip() for item in questions if str(item).strip()}) < 3:
            errors.append(f"{meta_path.relative_to(ROOT)}: servono almeno tre seo.supportingQueries distinte")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", checked):
            errors.append(f"{meta_path.relative_to(ROOT)}: seo.serpCheckedAt deve essere AAAA-MM-GG")

        soup = BeautifulSoup(source, "html.parser")
        h1 = soup.find("h1")
        lead = soup.select_one(".article-lead")
        searchable = " ".join([
            h1.get_text(" ", strip=True) if h1 else "",
            lead.get_text(" ", strip=True) if lead else "",
            path.stem.replace("-", " "),
        ])
        query_words = significant_words(primary)
        matched_words = query_words & significant_words(searchable)
        if query_words and len(matched_words) * 2 < len(query_words):
            errors.append(f"{relative}: query principale poco coerente con titolo, slug e apertura")
        if not lead or not 80 <= len(lead.get_text(" ", strip=True)) <= 900:
            errors.append(f"{relative}: apertura assente, troppo breve o troppo lunga")

    if errors:
        print("CONTROLLO SEO NUOVI DOSSIER: FALLITO", file=sys.stderr)
        for error in errors:
            print("- " + error, file=sys.stderr)
        raise SystemExit(1)
    print(f"CONTROLLO SEO NUOVI DOSSIER: OK — {len(added)} nuovi file verificati rispetto a {base}.")


if __name__ == "__main__":
    main()
