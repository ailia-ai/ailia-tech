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


_HEX_ID_RE = re.compile(r"-[a-f0-9]{10,14}$")


def collect_urls_from_sitemap(custom_domain: str) -> dict:
    """publicationのカスタムドメインのsitemap.xmlから記事URLとlastmodを収集。
    返り値は {url: lastmod_date_str} の dict。lastmodはMediumが記事を編集
    すると更新されるため、ローカル保存版との差分検知に使う。"""
    sitemap_url = f"https://{custom_domain}/sitemap/sitemap.xml"
    print(f"[sitemap] {sitemap_url}")
    xml = fetch(sitemap_url)
    if not xml:
        return {}
    result: dict = {}
    for block in re.findall(r"<url>(.*?)</url>", xml, re.DOTALL):
        loc_m = re.search(r"<loc>([^<]+)</loc>", block)
        if not loc_m:
            continue
        url = loc_m.group(1)
        if not _HEX_ID_RE.search(url):
            continue
        lastmod_m = re.search(r"<lastmod>([^<]+)</lastmod>", block)
        result[url] = lastmod_m.group(1)[:10] if lastmod_m else ""
    print(f"[sitemap] found {len(result)} article URLs")
    return result


def collect_urls_from_feed(publication: str) -> list:
    """publicationのRSSフィードから最新10記事のURLを収集。
    sitemap.xmlは反映が遅く最新記事を含まないことがあるため、
    sitemapで取りこぼした新着URLをRSS経由で補完する。

    sitemap.xmlは生の日本語slugを含むのに対しRSS<link>はURLエンコード
    済みなので、unquote()で復号して文字列比較できる形に揃える。"""
    from urllib.parse import unquote

    feed_url = f"https://medium.com/feed/{publication}"
    print(f"[feed]    {feed_url}")
    xml = fetch(feed_url)
    if not xml:
        return []
    items = re.findall(r"<item>(.*?)</item>", xml, re.DOTALL)
    urls: list = []
    for item in items:
        m = re.search(r"<link>([^<]+)</link>", item)
        if not m:
            continue
        url = unquote(m.group(1).split("?")[0].rstrip("/"))
        if _HEX_ID_RE.search(url):
            urls.append(url)
    print(f"[feed]    found {len(urls)} article URLs in feed")
    return urls


def extract_tags(soup) -> list:
    """Mediumの記事HTMLからtag slugの一覧を抽出。"""
    tags: list = []
    seen = set()
    for a in soup.find_all("a", href=True):
        m = re.search(r"medium\.com/tag/([A-Za-z0-9_-]+)", a["href"])
        if m:
            t = m.group(1).lower()
            if t not in seen:
                seen.add(t)
                tags.append(t)
    return tags


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


def _read_lastmod(md_path: Path) -> str:
    """既存記事の YAML フロントマターから lastmod の値を取り出す。"""
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception:
        return ""
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 4)
    fm = text[4:end] if end != -1 else text[4:]
    m = re.search(r"^lastmod:\s*(.+)$", fm, re.M)
    return m.group(1).strip() if m else ""


def _inject_lastmod(md_path: Path, lastmod: str) -> bool:
    """フロントマターに ``lastmod: <date>`` を挿入する。
    本文の再取得が不要な既存記事 (旧バージョンで保存された記事) に
    sitemap の lastmod を後付けするために使う。"""
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return False
    end = text.find("\n---\n", 4)
    if end == -1:
        return False
    fm = text[4:end]
    body = text[end + 5 :]
    if re.search(r"^lastmod:", fm, re.M):
        return False
    # date: の直後に挿入。date: が無ければ original_url: の前に置く。
    new_fm, n = re.subn(
        r"^(date:.*\n)", r"\1lastmod: " + lastmod + "\n", fm, count=1, flags=re.M
    )
    if n == 0:
        new_fm, n = re.subn(
            r"^(original_url:)",
            "lastmod: " + lastmod + "\n" + r"\1",
            fm,
            count=1,
            flags=re.M,
        )
    if n == 0:
        new_fm = fm.rstrip() + f"\nlastmod: {lastmod}\n"
    md_path.write_text(f"---\n{new_fm}\n---\n{body}", encoding="utf-8")
    return True


def scrape_article(
    url: str,
    output_dir: Path,
    sitemap_lastmod: str = "",
    refresh: bool = False,
    force: bool = False,
) -> str:
    """記事1本をMarkdownで保存。ファイル名は YYYY-MM-DD_slug.md 形式。

    挙動:
      - ``force=True``        : 既存記事を必ず再取得 (--refresh-all)
      - ``refresh=True``      : sitemap の lastmod がローカルより新しいときだけ
                                再取得。ローカルに lastmod が無い旧記事は本文を
                                再取得せず lastmod の付与だけ行う。
      - それ以外               : 既存記事はスキップ
    """
    slug = slugify(url)
    articles_dir = output_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)

    existing = (
        list(articles_dir.glob(f"????-??-??_{slug}.md"))
        + list(articles_dir.glob(f"unknown-date_{slug}.md"))
        + list(articles_dir.glob(f"{slug}.md"))
    )
    if existing:
        if force:
            print(f"[force-refresh] {existing[0].name}")
            for f in existing:
                f.unlink()
        elif not refresh:
            print(f"[skip] already saved: {existing[0].name}")
            return "skip"
        else:
            local_lastmod = _read_lastmod(existing[0])
            # 旧バージョンで保存された記事は lastmod を持たない。sitemap に
            # 値があるなら本文は再取得せず lastmod だけ埋めて、次回以降の
            # 差分検知が機能するようにブートストラップする。
            if not local_lastmod and sitemap_lastmod:
                if _inject_lastmod(existing[0], sitemap_lastmod):
                    print(
                        f"[backfill-lastmod] {existing[0].name} "
                        f"(lastmod={sitemap_lastmod})"
                    )
                    return "backfill"
            # 両方の lastmod が揃っているケースだけ「新しいほうへ更新」と判定。
            # ローカルが新しい・どちらかが空、の場合は安全側に倒してスキップ。
            if (
                local_lastmod
                and sitemap_lastmod
                and local_lastmod < sitemap_lastmod
            ):
                print(
                    f"[refresh] {existing[0].name} "
                    f"(lastmod {local_lastmod} -> {sitemap_lastmod})"
                )
                for f in existing:
                    f.unlink()
            else:
                print(
                    f"[skip-uptodate] {existing[0].name} "
                    f"(local={local_lastmod or '-'} sitemap={sitemap_lastmod or '-'})"
                )
                return "uptodate"

    print(f"[scrape] {url}")
    html = fetch(url)
    if not html:
        return "fetch-failed"

    soup = BeautifulSoup(html, "html.parser")

    title_el = soup.find("h1")
    title = title_el.get_text(strip=True) if title_el else slug

    author_el = soup.find("meta", attrs={"name": "author"})
    author = author_el["content"] if author_el else ""

    date_el = soup.find("meta", attrs={"property": "article:published_time"})
    pub_date = date_el["content"][:10] if date_el else ""

    tags = extract_tags(soup)

    article = soup.find("article")
    if not article:
        print(f"  [warn] no <article> tag: {url}")
        return "no-article"

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
        if sitemap_lastmod:
            f.write(f"lastmod: {sitemap_lastmod}\n")
        if tags:
            f.write("tags: [" + ", ".join(tags) + "]\n")
        f.write(f"original_url: {url}\n")
        f.write("---\n\n")
        f.write(f"# {title}\n\n")
        f.write(markdown)

    print(f"  [saved] {md_path.name}")
    time.sleep(DELAY)
    return "saved"


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
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="既存記事もsitemap lastmodと比較して、更新されていれば再取得する",
    )
    parser.add_argument(
        "--refresh-all",
        action="store_true",
        help="既存記事を強制的にすべて再取得する",
    )
    parser.add_argument(
        "--only-url",
        default="",
        help="指定したURLのみを (再) 取得する。--refresh と併用で1記事だけ更新可能。",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    urls_file = output_dir / "urls.txt"
    previous = (
        set(urls_file.read_text().strip().splitlines())
        if urls_file.exists()
        else set()
    )
    sitemap_map = collect_urls_from_sitemap(args.custom_domain)
    if not sitemap_map:
        print("[warn] sitemap returned no URLs; aborting")
        return
    # sitemap.xmlは更新が遅延し最新記事を取りこぼすことがあるため、RSSフィードから
    # 直近10件を追加で取得してマージする (重複は集合で吸収)。
    feed_urls = collect_urls_from_feed(args.publication)
    extra = len(set(feed_urls) - set(sitemap_map))
    if extra:
        print(f"[info]    {extra} URL(s) only in feed (sitemap missed)")
    # feed-only URLは lastmod 未知なので空文字 (= 強制スキップ判定にならず、
    # 既存があれば skip / 無ければ scrape)
    for u in feed_urls:
        sitemap_map.setdefault(u, "")
    urls = sorted(sitemap_map.keys())
    urls_file.write_text("\n".join(urls))
    new_urls = [u for u in urls if u not in previous]
    print(
        f"[info] total: {len(urls)} articles "
        f"({len(new_urls)} new since last run, {len(previous)} previously known)\n"
    )

    if args.only_url:
        if args.only_url not in sitemap_map:
            sitemap_map[args.only_url] = ""
        urls = [args.only_url]

    if args.urls_only:
        return

    refresh_mode = args.refresh or args.refresh_all
    counts: dict = {}
    for i, url in enumerate(urls, 1):
        print(f"\n--- {i}/{len(urls)} ---")
        lastmod = sitemap_map.get(url, "")
        result = scrape_article(
            url,
            output_dir,
            sitemap_lastmod=lastmod,
            refresh=refresh_mode,
            force=args.refresh_all,
        )
        if result:
            counts[result] = counts.get(result, 0) + 1

    print(f"\n[done] export complete: {output_dir}")
    if counts:
        summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"[summary] {summary}")


if __name__ == "__main__":
    main()
