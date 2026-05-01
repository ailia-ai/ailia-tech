#!/usr/bin/env python3
"""
Medium Publication Scraper
=========================
Mediumのpublication全記事をMarkdownでダウンロードするスクリプト。

使い方:
    pip install curl-cffi beautifulsoup4 markdownify
    python medium_publication.py --publication axinc --custom-domain tech.ailia.ai

出力:
    medium_export/
      ├── urls.txt              # 全記事URL一覧 (sitemap.xmlから取得)
      ├── articles/             # Markdown化された各記事
      │   ├── YYYY-MM-DD_article-slug-1.md
      │   └── YYYY-MM-DD_article-slug-2.md
      └── images/               # 各記事の画像
          ├── article-slug-1/
          └── article-slug-2/

備考:
    Mediumは現在Cloudflareで保護されているため、curl_cffiでブラウザ
    フィンガープリントを偽装してアクセスする。記事URL一覧はpublicationの
    カスタムドメインのsitemap.xmlから取得する (例: tech.ailia.ai)。
"""

import argparse
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from curl_cffi import requests
from markdownify import markdownify as html_to_md

IMPERSONATE = "chrome120"
DELAY = 2  # サーバ負荷を避けるための待機秒数


def fetch(url: str) -> str:
    """URLをGETしてHTMLを返す。エラー時は空文字。"""
    try:
        r = requests.get(url, impersonate=IMPERSONATE, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  [warn] fetch failed: {url} ({e})")
        return ""


def fetch_bytes(url: str) -> bytes:
    try:
        r = requests.get(url, impersonate=IMPERSONATE, timeout=30)
        r.raise_for_status()
        return r.content
    except Exception as e:
        print(f"  [warn] fetch failed: {url} ({e})")
        return b""


def collect_urls_from_sitemap(custom_domain: str) -> list:
    """publicationのカスタムドメインのsitemap.xmlから記事URLを収集。"""
    sitemap_url = f"https://{custom_domain}/sitemap/sitemap.xml"
    print(f"[sitemap] {sitemap_url}")
    xml = fetch(sitemap_url)
    if not xml:
        return []
    locs = re.findall(r"<loc>([^<]+)</loc>", xml)
    # 記事URLは末尾が -[12桁hex] (10〜14桁を許容)
    pattern = re.compile(r"-[a-f0-9]{10,14}$")
    articles = sorted({l for l in locs if pattern.search(l)})
    print(f"[sitemap] found {len(articles)} article URLs (out of {len(locs)} total)")
    return articles


def slugify(url: str) -> str:
    """URLから安全なファイル名を生成 (英数字とハイフンのみ)。"""
    slug = url.rstrip("/").split("/")[-1]
    # 日本語など非ASCIIを_に置換しつつ、末尾のhex IDは保持
    slug = re.sub(r"[^\w\-]", "_", slug, flags=re.ASCII)
    return slug[:120]


_MIRO_IMG_ID = re.compile(r"/(\d+\*[A-Za-z0-9_-]+\.[A-Za-z0-9]+)(?:[?#].*)?$")


def normalize_pictures(article_soup) -> None:
    """<picture>内の<img>はsrc未設定のことが多いので、<source srcset>から
    オリジナル解像度のmiro URLを推定して<img src>にセットする。"""
    for picture in article_soup.find_all("picture"):
        img = picture.find("img")
        if img is None or img.get("src"):
            continue
        candidate_url = None
        for source in picture.find_all("source"):
            srcset = source.get("srcset", "")
            for entry in srcset.split(","):
                entry = entry.strip()
                if not entry:
                    continue
                url = entry.split()[0]
                # webpはマスター画像でないことが多いので、後で見つかった非webpを優先
                if "format:webp" in url and candidate_url:
                    continue
                candidate_url = url
                if "format:webp" not in url:
                    break
            if candidate_url and "format:webp" not in candidate_url:
                break
        if not candidate_url:
            continue
        m = _MIRO_IMG_ID.search(candidate_url)
        img["src"] = (
            f"https://miro.medium.com/v2/{m.group(1)}" if m else candidate_url
        )


def download_images(article_soup, image_dir: Path) -> dict:
    """記事内の画像を一括DL。元URL→ローカルパスのdictを返す。"""
    image_dir.mkdir(parents=True, exist_ok=True)
    url_to_local = {}
    for i, img in enumerate(article_soup.find_all("img")):
        src = img.get("src") or img.get("data-src")
        if not src or not src.startswith("http"):
            continue
        if src in url_to_local:
            continue
        data = fetch_bytes(src)
        if not data:
            continue
        ext = Path(urlparse(src).path).suffix or ".jpg"
        filename = f"image_{i:03d}{ext}"
        local_path = image_dir / filename
        local_path.write_bytes(data)
        url_to_local[src] = f"images/{image_dir.name}/{filename}"
        time.sleep(0.3)
    return url_to_local


def scrape_article(url: str, output_dir: Path):
    """記事1本をMarkdownで保存。ファイル名は YYYY-MM-DD_slug.md 形式。"""
    slug = slugify(url)
    articles_dir = output_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)

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

    title_el = soup.find("h1")
    title = title_el.get_text(strip=True) if title_el else slug

    author_el = soup.find("meta", attrs={"name": "author"})
    author = author_el["content"] if author_el else ""

    date_el = soup.find("meta", attrs={"property": "article:published_time"})
    pub_date = date_el["content"][:10] if date_el else ""

    article = soup.find("article")
    if not article:
        print(f"  [warn] no <article> tag: {url}")
        return

    normalize_pictures(article)

    image_dir = output_dir / "images" / slug
    image_map = download_images(article, image_dir)
    for img in article.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src in image_map:
            img["src"] = "../" + image_map[src]

    markdown = html_to_md(str(article), heading_style="ATX", bullets="-")
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()

    date_prefix = pub_date if pub_date else "unknown-date"
    md_path = articles_dir / f"{date_prefix}_{slug}.md"

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
    parser.add_argument(
        "--custom-domain",
        required=True,
        help="publicationのカスタムドメイン (例: tech.ailia.ai)。"
        "sitemap.xmlから記事URL一覧を取得するために使用。",
    )
    parser.add_argument("--output", default="medium_export")
    parser.add_argument("--urls-only", action="store_true", help="URL収集だけ実行")
    parser.add_argument("--limit", type=int, default=0, help="最大記事数 (0=全件)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    urls_file = output_dir / "urls.txt"
    previous = (
        set(urls_file.read_text().strip().splitlines())
        if urls_file.exists()
        else set()
    )
    urls = collect_urls_from_sitemap(args.custom_domain)
    if not urls:
        print("[warn] sitemap returned no URLs; aborting")
        return
    urls_file.write_text("\n".join(urls))
    new_urls = [u for u in urls if u not in previous]
    print(
        f"[info] total: {len(urls)} articles "
        f"({len(new_urls)} new since last run, {len(previous)} previously known)\n"
    )

    if args.urls_only:
        return

    if args.limit > 0:
        urls = urls[: args.limit]

    for i, url in enumerate(urls, 1):
        print(f"\n--- {i}/{len(urls)} ---")
        scrape_article(url, output_dir)

    print(f"\n[done] export complete: {output_dir}")


if __name__ == "__main__":
    main()
