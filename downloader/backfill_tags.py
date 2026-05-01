#!/usr/bin/env python3
"""
既存の medium_export/articles/*.md にタグ情報を付与するバックフィルスクリプト。

medium_publication.py が出力する YAML フロントマターには初版時点では
``tags`` が存在しなかったため、各記事の Medium URL を再取得して
``medium.com/tag/<name>`` リンクからタグを抽出し、フロントマターを
書き換える。既に ``tags:`` を含む記事はスキップする (本文の再ダウンロード
や画像取得は一切行わない)。

使い方:
    pip install curl-cffi beautifulsoup4
    python downloader/backfill_tags.py
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup
from curl_cffi import requests

from medium_publication import extract_tags

IMPERSONATE = "chrome120"
DELAY = 1.0


def fetch(url: str) -> str:
    try:
        r = requests.get(url, impersonate=IMPERSONATE, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  [warn] fetch failed: {e}", file=sys.stderr)
        return ""


def update(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return "skip-no-fm"
    end = text.find("\n---\n", 4)
    if end == -1:
        return "skip-no-fm-end"
    fm = text[4:end]
    body = text[end + 5 :]
    if re.search(r"^tags:", fm, re.M):
        return "already"
    m = re.search(r"^original_url:\s*(.+)$", fm, re.M)
    if not m:
        return "no-url"
    url = m.group(1).strip()

    html = fetch(url)
    if not html:
        return "fetch-failed"
    soup = BeautifulSoup(html, "html.parser")
    tags = extract_tags(soup)
    if not tags:
        return "no-tags"

    yaml_tags = "[" + ", ".join(tags) + "]"
    new_fm = f"{fm}\ntags: {yaml_tags}"
    md_path.write_text(f"---\n{new_fm}\n---\n{body}", encoding="utf-8")
    time.sleep(DELAY)
    return "updated:" + ",".join(tags)


def main():
    articles_dir = Path("medium_export/articles")
    files = sorted(articles_dir.glob("*.md"))
    counts: dict[str, int] = {}
    for i, mdf in enumerate(files, 1):
        result = update(mdf)
        key = result.split(":", 1)[0]
        counts[key] = counts.get(key, 0) + 1
        print(f"[{i}/{len(files)}] {mdf.name}: {result}")

    print("\n=== summary ===")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
