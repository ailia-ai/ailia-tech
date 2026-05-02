#!/usr/bin/env python3
"""
既存の medium_export/articles/*.md の ``date:`` (投稿日) を Apollo state の
firstPublishedAt から取り直すバックフィルスクリプト。

旧版のスクレイパーは ``<meta property="article:published_time">`` を
投稿日として保存していたが、これは Medium が記事を再公開すると
``latestPublishedAt`` (= 最終更新日) で上書きされる仕様で、本当の
投稿日ではない。Apollo state の ``Post.<id>.firstPublishedAt`` が
真の投稿日。

このスクリプトは本文・画像を再取得せず、各記事HTMLからAppolo stateだけ
読み出して ``date:`` を書き換える。日付が変わった場合はファイル名の
``YYYY-MM-DD_<slug>.md`` プレフィックスもリネームする。
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

from medium_publication import (
    _extract_apollo_dates,
    _HEX_ID_RE,
    fetch,
)

DELAY = 0.5


def update(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return "skip-no-fm"
    end = text.find("\n---\n", 4)
    if end == -1:
        return "skip-no-fm-end"
    fm = text[4:end]
    body = text[end + 5 :]

    cur_date_m = re.search(r"^date:\s*(.+)$", fm, re.M)
    cur_date = cur_date_m.group(1).strip() if cur_date_m else ""

    url_m = re.search(r"^original_url:\s*(.+)$", fm, re.M)
    if not url_m:
        return "no-url"
    url = url_m.group(1).strip()
    pid_m = _HEX_ID_RE.search(url)
    if not pid_m:
        return "no-post-id"
    post_id = pid_m.group()[1:]

    html = fetch(url)
    if not html:
        return "fetch-failed"
    first, latest = _extract_apollo_dates(html, post_id)
    if not first:
        return "no-apollo-date"

    if first == cur_date:
        return "uptodate"

    # date 行を新しい値に置換 (lastmod の値も latestPublishedAt があれば更新)
    new_fm = re.sub(r"^date:\s*.+$", f"date: {first}", fm, count=1, flags=re.M)
    if latest:
        if re.search(r"^lastmod:\s*", new_fm, re.M):
            new_fm = re.sub(
                r"^lastmod:\s*.+$", f"lastmod: {latest}", new_fm, count=1, flags=re.M
            )
        else:
            new_fm = re.sub(
                r"^(date:.*\n)", r"\1lastmod: " + latest + "\n", new_fm, count=1, flags=re.M
            )
    md_path.write_text(f"---\n{new_fm}\n---\n{body}", encoding="utf-8")

    # ファイル名 prefix もリネーム
    name = md_path.name
    m = re.match(r"^(\d{4}-\d{2}-\d{2}|unknown-date)_(.+)$", name)
    if m and m.group(1) != first:
        new_name = f"{first}_{m.group(2)}"
        new_path = md_path.with_name(new_name)
        if new_path.exists():
            md_path.unlink()
        else:
            md_path.rename(new_path)
    time.sleep(DELAY)
    return f"updated:{cur_date}->{first}"


def main():
    articles_dir = Path("medium_export/articles")
    files = sorted(articles_dir.glob("*.md"))
    counts: dict = {}
    for i, mdf in enumerate(files, 1):
        result = update(mdf)
        key = result.split(":", 1)[0]
        counts[key] = counts.get(key, 0) + 1
        print(f"[{i}/{len(files)}] {mdf.name[:60]}: {result}")

    print("\n=== summary ===")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
