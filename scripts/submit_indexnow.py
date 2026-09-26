#!/usr/bin/env python3
"""Notify IndexNow participants after the GitHub Pages deployment is reachable."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://unosguardosulluomo.github.io/"
KEY = "a6f4c8e25d9b4170b3e18f726c904d5a"
KEY_LOCATION = SITE + KEY + ".txt"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def sitemap_urls(name: str) -> list[str]:
    root = ET.parse(ROOT / name).getroot()
    return [node.text for node in root.findall("sm:url/sm:loc", NS) if node.text]


def key_is_live() -> bool:
    try:
        with urllib.request.urlopen(KEY_LOCATION, timeout=20) as response:
            return response.status == 200 and response.read().decode("utf-8").strip() == KEY
    except (urllib.error.URLError, TimeoutError):
        return False


for attempt in range(8):
    if key_is_live():
        break
    if attempt == 7:
        raise SystemExit("La chiave IndexNow non è ancora pubblica: invio rinviato.")
    time.sleep(15)

urls = sitemap_urls("sitemap-pages.xml") + sitemap_urls("sitemap-articles.xml")
payload = json.dumps({
    "host": "unosguardosulluomo.github.io",
    "key": KEY,
    "keyLocation": KEY_LOCATION,
    "urlList": urls,
}).encode("utf-8")
request = urllib.request.Request(
    "https://api.indexnow.org/indexnow", data=payload,
    headers={"Content-Type": "application/json; charset=utf-8"}, method="POST",
)
try:
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status not in (200, 202):
            raise SystemExit(f"IndexNow ha risposto HTTP {response.status}")
except urllib.error.HTTPError as exc:
    raise SystemExit(f"IndexNow ha risposto HTTP {exc.code}") from exc
print(f"IndexNow notificato: {len(urls)} URL.")
