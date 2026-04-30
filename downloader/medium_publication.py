#!/usr/bin/env python3
"""
Medium Publication Scraper
=========================
Mediumのpublication全記事をMarkdownでダウンロードするスクリプト。

使い方:
    pip install requests beautifulsoup4 markdownify
    python medium_scraper.py --publication axinc --start-year 2018 --end-year 2026

出力:
    medium_export/
      ├── urls.txt              # 全記事URL一覧
      ├── articles/             # Markdown化された各記事
      │   ├── article-slug-1.md
      │   └── article-slug-2.md
      └── images/               # 各記事の画像
          ├── article-slug-1/
          └── article-slug-2/
"""

import argparse
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_md

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
DELAY = 2  # サーバ負荷を避けるための待機秒数


def fetch(url: str) -> str:
    """URLをGETしてHTMLを返す。エラー時は空文字。"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  [warn] fetch failed: {url} ({e})")
        return ""


def extract_article_urls(html: str, publication: str) -> set:
    """HTMLからMedium記事URLを抽出。"""
    urls = set()
    soup = BeautifulSoup(html, "html.parser")
    # Medium記事URLの末尾は -[12桁hex]
    pattern = re.compile(r"-[a-f0-9]{10,14}(?:[/?#].*)?$")
    for a in soup.find_all("a", href=True):
        href = a["href"].split("?")[0].rstrip("/")
        # publication配下の記事のみ対象
        if f"/{publication}/" in href and pattern.search(href):
            if href.startswith("/"):
                href = "https://medium.com" + href
            urls.add(href)
    return urls


def collect_all_urls(publication: str, start_year: int, end_year: int) -> set:
    """publicationの全記事URLを年別アーカイブから収集。"""
    all_urls = set()
    for year in range(start_year, end_year + 1):
        year_url = f"https://medium.com/{publication}/archive/{year}"
        print(f"[archive] {year_url}")
        year_html = fetch(year_url)
        if not year_html:
            continue

        # 年ページから直接記事URLを取れる場合もある
        all_urls |= extract_article_urls(year_html, publication)

        # 月ページも巡回 (取りこぼし対策)
        for month in range(1, 13):
            for day in range(1, 32):
                day_url = f"https://medium.com/{publication}/archive/{year}/{month:02d}/{day:02d}"
                day_html = fetch(day_url)
                if not day_html:
                    continue
                found = extract_article_urls(day_html, publication)
                if found:
                    print(f"  {year}/{month:02d}/{day:02d}: {len(found)} articles")
                    all_urls |= found
                time.sleep(0.3)
        time.sleep(DELAY)
    return all_urls


def slugify(url: str) -> str:
    """URLからファイル名を生成。"""
    slug = url.rstrip("/").split("/")[-1]
    slug = re.sub(r"[^\w\-]", "_", slug)
    return slug[:120]


def download_images(article_soup, image_dir: Path) -> dict:
    """記事内の画像を一括DL。元URL→ローカルパスのdictを返す。"""
    image_dir.mkdir(parents=True, exist_ok=True)
    url_to_local = {}
    for i, img in enumerate(article_soup.find_all("img")):
        src = img.get("src") or img.get("data-src")
        if not src or not src.startswith("http"):
            continue
        try:
            r = requests.get(src, headers=HEADERS, timeout=30)
            r.raise_for_status()
            ext = Path(urlparse(src).path).suffix or ".jpg"
            filename = f"image_{i:03d}{ext}"
            local_path = image_dir / filename
            local_path.write_bytes(r.content)
            url_to_local[src] = f"images/{image_dir.name}/{filename}"
            time.sleep(0.5)
        except Exception as e:
            print(f"  [warn] image failed: {src} ({e})")
    return url_to_local


def scrape_article(url: str, output_dir: Path):
    """記事1本をMarkdownで保存。ファイル名は YYYY-MM-DD_slug.md 形式。"""
    slug = slugify(url)
    articles_dir = output_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)

    # 既存ファイルチェック (日付prefix有無の両方に対応)
    existing = (
        list(articles_dir.glob(f"????-??-??_{slug}.md"))
        + list(articles_dir.glob(f"unknown-date_{slug}.md"))
        + list(articles_dir.glob(f"{slug}.md"))
    )
    if existing:
        print(f"[skip] already saved: {existing[0].name}")
        return

    print(f"[scrape] {url}")
    html = fetch(url)
    if not html:
        return

    soup = BeautifulSoup(html, "html.parser")

    # タイトル取得
    title_el = soup.find("h1")
    title = title_el.get_text(strip=True) if title_el else slug

    # 著者取得 (任意)
    author_el = soup.find("meta", attrs={"name": "author"})
    author = author_el["content"] if author_el else ""

    # 公開日取得
    date_el = soup.find("meta", attrs={"property": "article:published_time"})
    pub_date = date_el["content"][:10] if date_el else ""

    # 本文取得
    article = soup.find("article")
    if not article:
        print(f"  [warn] no <article> tag: {url}")
        return

    # 画像をローカルにDL & URLを置換
    image_dir = output_dir / "images" / slug
    image_map = download_images(article, image_dir)
    for img in article.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src in image_map:
            img["src"] = "../" + image_map[src]

    # MarkdownへConvert
    markdown = html_to_md(str(article), heading_style="ATX", bullets="-")
    # 連続改行を整理
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()

    # ファイル名: YYYY-MM-DD_slug.md (日付不明時は unknown-date_slug.md)
    date_prefix = pub_date if pub_date else "unknown-date"
    md_path = articles_dir / f"{date_prefix}_{slug}.md"

    # フロントマター付きで保存
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f'title: "{title}"\n')
        if author:
            f.write(f'author: "{author}"\n')
        if pub_date:
            f.write(f"date: {pub_date}\n")
        f.write(f"original_url: {url}\n")
        f.write("---\n\n")
        f.write(f"# {title}\n\n")
        f.write(markdown)

    print(f"  [saved] {md_path.name}")
    time.sleep(DELAY)


def main():
    parser = argparse.ArgumentParser(description="Medium publication scraper")
    parser.add_argument("--publication", required=True, help="例: axinc")
    parser.add_argument("--output", default="medium_export")
    parser.add_argument("--start-year", type=int, default=2018)
    parser.add_argument("--end-year", type=int, default=2026)
    parser.add_argument("--urls-only", action="store_true", help="URL収集だけ実行")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. URL一覧を収集
    urls_file = output_dir / "urls.txt"
    if urls_file.exists():
        print(f"[info] reusing existing URL list: {urls_file}")
        urls = set(urls_file.read_text().strip().splitlines())
    else:
        print(f"[info] collecting URLs from medium.com/{args.publication}")
        urls = collect_all_urls(args.publication, args.start_year, args.end_year)
        urls_file.write_text("\n".join(sorted(urls)))
        print(f"[info] saved {len(urls)} URLs to {urls_file}")

    print(f"\n[info] total unique articles: {len(urls)}\n")

    if args.urls_only:
        return

    # 2. 各記事をスクレイピング
    for i, url in enumerate(sorted(urls), 1):
        print(f"\n--- {i}/{len(urls)} ---")
        scrape_article(url, output_dir)

    print(f"\n[done] export complete: {output_dir}")


if __name__ == "__main__":
    main()
