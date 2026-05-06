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
import json
import re
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from curl_cffi import requests
from markdownify import markdownify as html_to_md

IMPERSONATE = "chrome120"
DELAY = 2  # サーバ負荷を避けるための待機秒数


_FETCH_RETRIES = 3
_FETCH_BACKOFF = 4  # 秒。失敗1回目→4s, 2回目→8s, 3回目→16s

# Cloudflareのbot判定はTLSフィンガープリントとUAをセットで見るので、
# 失敗時は別ブラウザに切り替えて当たり直す。最初に Chrome を試して、
# それで通らないなら Safari / Edge / Firefox を順番に投げる。
_IMPERSONATE_POOL = [
    "chrome120",
    "chrome131",
    "safari17_2",
    "edge101",
    "firefox133",
]

# curl_cffi の Session を使い回し、RSSフィードで一度cookieを焼いて
# おく事で、後続の home / 個別記事リクエストが既存セッション (cf_*
# クッキー含む) として扱われやすくする。
_SESSION_CACHE: dict = {}


def _get_session(impersonate: str):
    sess = _SESSION_CACHE.get(impersonate)
    if sess is not None:
        return sess
    sess = requests.Session(impersonate=impersonate)
    # ウォームアップ: RSSフィード (CIでも200を返す) を1回叩いて
    # CloudflareのcookieをSessionに取り込む。
    try:
        sess.get("https://medium.com/feed/axinc", timeout=30)
    except Exception:
        pass
    _SESSION_CACHE[impersonate] = sess
    return sess


def fetch(url: str) -> str:
    """URLをGETしてHTMLを返す。Cloudflareの一時的な403/接続エラーには
    指数バックオフ + 別フィンガープリントへの切替で対抗する。"""
    last_err = None
    for attempt in range(_FETCH_RETRIES):
        impersonate = _IMPERSONATE_POOL[attempt % len(_IMPERSONATE_POOL)]
        try:
            sess = _get_session(impersonate)
            r = sess.get(
                url,
                timeout=30,
                headers={
                    "Referer": "https://medium.com/",
                    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
                },
            )
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_err = e
            if attempt < _FETCH_RETRIES - 1:
                next_imp = _IMPERSONATE_POOL[(attempt + 1) % len(_IMPERSONATE_POOL)]
                wait = _FETCH_BACKOFF * (2 ** attempt)
                print(
                    f"  [warn] fetch failed (attempt {attempt + 1}/{_FETCH_RETRIES} "
                    f"with {impersonate}): {url} ({e}); retrying in {wait}s as {next_imp}"
                )
                time.sleep(wait)
    print(
        f"  [warn] fetch failed after {_FETCH_RETRIES} attempts: {url} ({last_err})"
    )
    return ""


def fetch_bytes(url: str) -> bytes:
    last_err = None
    for attempt in range(_FETCH_RETRIES):
        impersonate = _IMPERSONATE_POOL[attempt % len(_IMPERSONATE_POOL)]
        try:
            sess = _get_session(impersonate)
            r = sess.get(url, timeout=30, headers={"Referer": "https://medium.com/"})
            r.raise_for_status()
            return r.content
        except Exception as e:
            last_err = e
            if attempt < _FETCH_RETRIES - 1:
                time.sleep(_FETCH_BACKOFF * (2 ** attempt))
    print(f"  [warn] fetch_bytes failed: {url} ({last_err})")
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


def _resolve_post_id(post_id: str) -> str:
    """medium.com/p/<id> のリダイレクトを辿り、canonical URLを取得する。
    fetch() と同じ指数バックオフ + 別UAローテで再試行する。"""
    target = f"https://medium.com/p/{post_id}"
    last_err = None
    for attempt in range(_FETCH_RETRIES):
        impersonate = _IMPERSONATE_POOL[attempt % len(_IMPERSONATE_POOL)]
        try:
            sess = _get_session(impersonate)
            r = sess.get(
                target,
                timeout=30,
                allow_redirects=False,
                headers={"Referer": "https://medium.com/"},
            )
            loc = r.headers.get("location", "")
            if not loc:
                return ""
            if loc.startswith("/"):
                loc = "https://medium.com" + loc
            url = unquote(loc.split("?")[0].rstrip("/"))
            return url if _HEX_ID_RE.search(url) else ""
        except Exception as e:
            last_err = e
            if attempt < _FETCH_RETRIES - 1:
                time.sleep(_FETCH_BACKOFF * (2 ** attempt))
    print(f"  [warn] resolve {post_id} failed: {last_err}")
    return ""


def collect_urls_from_references(
    articles_dir: Path, ref_domain: str, publication: str, known: set
) -> list:
    """既にダウンロードした記事 markdown 内の内部リンクから、未知の記事URLを発見する。
    sitemap/feed/Apolloで取りこぼした古い記事 (publication初期の関連記事カード等) を
    クロスリファレンス経由で救済する。

    ``ref_domain`` は発見した URL を組み立てる時のホスト名 (独自ドメイン or
    medium.com)。``publication`` は medium.com/<pub>/ 形式の URL を組む際の
    publicationスラグ。"""
    if not articles_dir.exists():
        return []
    found: set = set()
    pub_prefix = f"{publication}/"
    medium_pub_re = re.compile(
        r"https?://medium\.com/" + re.escape(publication) + r"/([^?\s)\"<>]+)"
    )

    def _emit(slug: str) -> None:
        # 英語版 (axinc-ai) のように publication slug が記事相対パスにそのまま
        # 含まれる事があり、二重に prefix を付けると medium.com/axinc-ai/axinc-ai/...
        # のような不正URLになるため、先頭の <publication>/ は剥がしてから組み立てる。
        if slug.startswith(pub_prefix):
            slug = slug[len(pub_prefix):]
        # /@user/... 等、別 publication / ユーザー scope のパスは publication の
        # 配下に勝手に組み入れない (誤った URL を生成してしまう)。
        if "/" in slug:
            return
        if not _HEX_ID_RE.search(slug):
            return
        if ref_domain == "medium.com":
            found.add(f"https://medium.com/{publication}/{slug}")
        else:
            found.add(f"https://{ref_domain}/{slug}")

    for mdf in articles_dir.glob("*.md"):
        text = mdf.read_text(encoding="utf-8")
        # 絶対 URL: medium.com/<publication>/<encoded-slug-with-hex>
        for m in medium_pub_re.finditer(text):
            _emit(unquote(m.group(1).rstrip("/")))
        # 相対 URL: ](/<encoded-slug-with-hex>?source=...)
        for m in re.finditer(r"\]\(/([^?\s)\"<>]+)", text):
            _emit(unquote(m.group(1).rstrip("/")))
    new = sorted(found - known)
    print(f"[refs]    found {len(new)} new URL(s) referenced from existing articles")
    return new


def collect_urls_from_apollo(home_url: str, known_ids: set = None) -> list:
    """publicationトップページのApollo state を解析し、Post の ID 一覧を
    medium.com/p/<id> リダイレクトで canonical URL に解決する。
    sitemap.xml が時々取りこぼす中堅記事 (古いチュートリアル等) の救済用。

    ``known_ids`` を渡すとそれに含まれるIDは解決をスキップして時間を節約する。
    """
    print(f"[apollo]  {home_url}")
    html_text = fetch(home_url)
    if not html_text:
        return []
    m = re.search(
        r"window\.__APOLLO_STATE__\s*=\s*(\{.+?\});?</script>",
        html_text,
        re.DOTALL,
    )
    if not m:
        print("[apollo]  no Apollo state found")
        return []
    try:
        data = json.loads(m.group(1))
    except Exception as e:
        print(f"[apollo]  json parse failed: {e}")
        return []

    post_ids = sorted(
        {k.split(":", 1)[1] for k in data.keys() if k.startswith("Post:")}
    )
    print(f"[apollo]  found {len(post_ids)} post IDs in Apollo state")
    known = known_ids or set()
    unresolved = [pid for pid in post_ids if pid not in known]
    print(f"[apollo]  resolving {len(unresolved)} new IDs via /p/<id>")

    urls: list = []
    for pid in unresolved:
        url = _resolve_post_id(pid)
        if url:
            urls.append(url)
        time.sleep(0.2)
    print(f"[apollo]  resolved {len(urls)} canonical URLs")
    return urls


def extract_tags(soup, html_text: str = "") -> list:
    """Mediumの記事HTMLからtag slugの一覧を抽出。

    日本語版は ``<a href="medium.com/tag/<name>">`` リンクが本文末尾に
    出力されるが、英語版ではそれが省かれているケースがあるため、
    Apollo state の ``Tag:<name>`` エントリをフォールバックとして使う。"""
    tags: list = []
    seen = set()
    for a in soup.find_all("a", href=True):
        m = re.search(r"medium\.com/tag/([A-Za-z0-9_-]+)", a["href"])
        if m:
            t = m.group(1).lower()
            if t not in seen:
                seen.add(t)
                tags.append(t)
    if tags:
        return tags
    # Apollo state にしか tag 情報が無いケース (en記事など) の救済
    if html_text:
        m = re.search(
            r"window\.__APOLLO_STATE__\s*=\s*(\{.+?\});?</script>",
            html_text,
            re.DOTALL,
        )
        if m:
            try:
                data = json.loads(m.group(1))
                for k in data.keys():
                    if k.startswith("Tag:"):
                        t = k.split(":", 1)[1].lower()
                        if t not in seen:
                            seen.add(t)
                            tags.append(t)
            except Exception:
                pass
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


def _extract_apollo_dates(html_text: str, post_id: str) -> tuple:
    """記事HTMLの ``window.__APOLLO_STATE__`` から (firstPublishedAt,
    latestPublishedAt) を ISO 日付 (YYYY-MM-DD) で取り出す。
    Mediumの ``article:published_time`` メタタグは latestPublishedAt を
    返してしまうので、真の投稿日を取得する目的で Apollo state を直接見る。"""
    m = re.search(
        r"window\.__APOLLO_STATE__\s*=\s*(\{.+?\});?</script>",
        html_text,
        re.DOTALL,
    )
    if not m:
        return "", ""
    try:
        data = json.loads(m.group(1))
    except Exception:
        return "", ""
    post = data.get(f"Post:{post_id}") or {}
    if not post:
        # ID が分からない場合: 最初に見つかる Post:* エントリを使う
        for k, v in data.items():
            if k.startswith("Post:") and isinstance(v, dict):
                post = v
                break

    def _to_iso(ts) -> str:
        try:
            from datetime import datetime, timezone

            return (
                datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
                .date()
                .isoformat()
            )
        except Exception:
            return ""

    first = _to_iso(post.get("firstPublishedAt")) if post.get("firstPublishedAt") else ""
    latest = _to_iso(post.get("latestPublishedAt")) if post.get("latestPublishedAt") else ""
    return first, latest


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
    meta_published = date_el["content"][:10] if date_el else ""

    # Mediumの article:published_time メタは「最終更新日」(latestPublishedAt)
    # を返すため、真の投稿日として Apollo state の firstPublishedAt を使う。
    # 値が取れなかったときだけメタタグの値にフォールバック。
    post_id_m = _HEX_ID_RE.search(url)
    post_id = post_id_m.group()[1:] if post_id_m else ""
    first_published, latest_published = _extract_apollo_dates(html, post_id)
    pub_date = first_published or meta_published
    # lastmod は: sitemap > Apollo latestPublishedAt > article:published_time の優先順
    if not sitemap_lastmod:
        sitemap_lastmod = latest_published or meta_published

    tags = extract_tags(soup, html)

    article = soup.find("article")
    if not article:
        print(f"  [warn] no <article> tag: {url}")
        return "no-article"

    normalize_pictures(article)
    # Mediumは <hr> ではなく装飾された <div role="separator"> でセクション
    # 区切りを表現する。markdownify は空の div として読み飛ばしてしまうので
    # ここで <hr> に差し替えて、出力markdownに `---` が残るようにする。
    for sep in article.find_all(attrs={"role": "separator"}):
        sep.replace_with(BeautifulSoup("<hr/>", "html.parser"))

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
    parser.add_argument("--publication", required=True, help="例: axinc / axinc-ai")
    parser.add_argument(
        "--custom-domain",
        default="",
        help="publicationのカスタムドメイン (例: tech.ailia.ai)。"
        "指定すると sitemap.xml と Apollo state を独自ドメイン側から取得する。"
        "未指定なら medium.com/<publication> を使用 (sitemap.xmlは存在しないため Apollo+RSF+ref のみで発見)。",
    )
    parser.add_argument("--output", default="medium_export")
    parser.add_argument(
        "--reference-domain",
        default="",
        help="既存記事のクロスリファレンス展開時の補完ドメイン (例: tech.ailia.ai)。"
        "未指定なら --custom-domain がフォールバック、それも無ければ medium.com。",
    )
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
    sitemap_map: dict = {}
    if args.custom_domain:
        sitemap_map = collect_urls_from_sitemap(args.custom_domain)
        if not sitemap_map:
            print("[warn] sitemap returned no URLs (will rely on feed + Apollo)")
    # sitemap.xmlは反映遅延だけでなく、それ以前の中堅記事も取りこぼすことが
    # あるため、(a) RSSフィードの直近10件 (b) publication ホームページの
    # Apollo state (Post:<id> 由来) の2つから補完する。独自ドメインが無い場合
    # (en) は sitemap が無いのでこの2つが主要な発見経路となる。
    feed_urls = collect_urls_from_feed(args.publication)
    extra_feed = len(set(feed_urls) - set(sitemap_map))
    if extra_feed:
        print(f"[info]    {extra_feed} URL(s) only in feed (sitemap missed)")
    for u in feed_urls:
        sitemap_map.setdefault(u, "")

    known_ids = set()
    for url in sitemap_map.keys():
        m = _HEX_ID_RE.search(url)
        if m:
            known_ids.add(m.group()[1:])
    apollo_home = (
        f"https://{args.custom_domain}/"
        if args.custom_domain
        else f"https://medium.com/{args.publication}/"
    )
    apollo_urls = collect_urls_from_apollo(apollo_home, known_ids=known_ids)
    extra_apollo = len(set(apollo_urls) - set(sitemap_map))
    if extra_apollo:
        print(f"[info]    {extra_apollo} URL(s) only in Apollo state (sitemap+feed missed)")
    for u in apollo_urls:
        sitemap_map.setdefault(u, "")

    # 既存scrape済み記事の本文から、まだ未知のURLをクロスリファレンスで救済する。
    ref_domain = args.reference_domain or args.custom_domain or "medium.com"
    ref_urls = collect_urls_from_references(
        output_dir / "articles",
        ref_domain,
        args.publication,
        set(sitemap_map.keys()),
    )
    for u in ref_urls:
        sitemap_map.setdefault(u, "")

    if not sitemap_map:
        print("[warn] no URLs discovered from any source; aborting")
        return

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
    failed_urls: list = []
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
            if result in ("fetch-failed", "no-article"):
                failed_urls.append((url, lastmod))

    # CIではCloudflareから一時的に弾かれることがある。冷却時間を置いた後に
    # fetch-failed / no-article になったURLを最後にもう一度試す。
    if failed_urls:
        print(f"\n[retry] cooling down 30s, then retrying {len(failed_urls)} failed URL(s)")
        time.sleep(30)
        for i, (url, lastmod) in enumerate(failed_urls, 1):
            print(f"\n--- retry {i}/{len(failed_urls)} ---")
            result = scrape_article(
                url,
                output_dir,
                sitemap_lastmod=lastmod,
                refresh=refresh_mode,
                force=args.refresh_all,
            )
            if result:
                counts[f"retry-{result}"] = counts.get(f"retry-{result}", 0) + 1

    print(f"\n[done] export complete: {output_dir}")
    if counts:
        summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"[summary] {summary}")


if __name__ == "__main__":
    main()
