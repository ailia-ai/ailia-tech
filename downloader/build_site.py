#!/usr/bin/env python3
"""
Static site builder for the scraped Medium articles.

Reads markdown files from medium_export/articles/ (with YAML front matter
written by medium_publication.py), renders them to HTML, and copies the
referenced images. The output directory layout is::

    _site/
      ├── index.html               # Article list, sorted by date desc
      ├── style.css
      ├── <medium-slug>/
      │   └── index.html           # one per article (slug == original Medium URL slug)
      └── images/
          └── <safe-slug>/
              └── image_NNN.<ext>

URL mapping:
    https://medium.com/axinc/<slug>          (Medium)
    https://<github-pages-host>/<repo>/<slug>/   (GitHub Pages)

i.e. replacing the prefix ``medium.com/axinc/`` with the GitHub Pages base
URL produces the corresponding mirror URL.

Image references in the source markdown use ``../images/<safe-slug>/...``
which resolves correctly from ``_site/<slug>/`` to ``_site/images/``.
"""

import argparse
import html
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

import markdown

GTM_ID = "GTM-5Q579RMM"

GTM_HEAD = f"""<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{GTM_ID}');</script>
<!-- End Google Tag Manager -->"""

GTM_BODY = f"""<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="style.css">
{gtm_head}
</head>
<body>
{gtm_body}
<header class="site-header">
  <h1>{title}</h1>
  <p class="subtitle">{subtitle}</p>
</header>
<main>
<ul class="article-list">
{items}
</ul>
</main>
<footer class="site-footer">
  <p>Total {count} articles. Source: <a href="https://medium.com/axinc">medium.com/axinc</a></p>
</footer>
</body>
</html>
"""

ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | ailia Tech BLOG (Mirror)</title>
<link rel="stylesheet" href="../style.css">
<link rel="canonical" href="{original_url}">
{gtm_head}
</head>
<body>
{gtm_body}
<header class="site-header">
  <p><a href="../">&larr; 記事一覧</a></p>
  <h1>{title}</h1>
  <p class="meta">{meta}</p>
</header>
<article class="post">
{content}
</article>
<footer class="site-footer">
  <p>原文: <a href="{original_url}">{original_url}</a></p>
</footer>
</body>
</html>
"""

CSS = """:root {
  --fg: #2d2d2d;
  --bg: #fafafa;
  --link: #0066cc;
  --muted: #666;
  --border: #e5e5e5;
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "Hiragino Kaku Gothic ProN", "Yu Gothic", Meiryo, sans-serif;
  max-width: 760px;
  margin: 0 auto;
  padding: 24px 20px 64px;
  line-height: 1.7;
  color: var(--fg);
  background: var(--bg);
}
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
.site-header { padding-bottom: 16px; border-bottom: 1px solid var(--border); margin-bottom: 24px; }
.site-header h1 { margin: 0 0 6px; font-size: 1.6em; }
.subtitle, .meta { color: var(--muted); font-size: 0.92em; margin: 4px 0; }
.site-footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--border); color: var(--muted); font-size: 0.9em; }
img { max-width: 100%; height: auto; display: block; margin: 12px auto; }
pre { background: #f0f0f0; padding: 12px; overflow-x: auto; border-radius: 4px; }
code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; font-size: 0.92em; }
pre code { background: transparent; padding: 0; }
blockquote { border-left: 3px solid var(--border); margin-left: 0; padding-left: 14px; color: var(--muted); }
.article-list { list-style: none; padding: 0; }
.article-list li { padding: 10px 0; border-bottom: 1px solid var(--border); }
.article-list .date { color: var(--muted); font-family: ui-monospace, monospace; font-size: 0.9em; margin-right: 10px; }
.post h1, .post h2, .post h3 { line-height: 1.3; }
.post h1 { display: none; }  /* Title already shown in header */
table { border-collapse: collapse; }
th, td { border: 1px solid var(--border); padding: 6px 10px; }
"""


def parse_front_matter(text: str) -> tuple[dict, str]:
    """medium_publication.pyが書き出すYAMLフロントマターを簡易パース。"""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5 :]
    fm: dict = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        fm[key.strip()] = val.strip().strip('"')
    return fm, body


def medium_slug_from_url(url: str) -> str:
    """元記事URL末尾のスラグ部を返す (例: '...axinc/foo-bar-deadbeef1234' -> 'foo-bar-deadbeef1234')。"""
    if not url:
        return ""
    return urlparse(url).path.rstrip("/").split("/")[-1]


def build(source: Path, output: Path) -> int:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    src_images = source / "images"
    if src_images.exists():
        shutil.copytree(src_images, output / "images")

    articles_dir = source / "articles"
    md = markdown.Markdown(extensions=["fenced_code", "tables", "sane_lists"])

    posts = []
    for mdf in sorted(articles_dir.glob("*.md")):
        text = mdf.read_text(encoding="utf-8")
        fm, body = parse_front_matter(text)

        title = fm.get("title") or mdf.stem
        date = fm.get("date", "")
        author = fm.get("author", "")
        original_url = fm.get("original_url", "")
        slug = medium_slug_from_url(original_url) or mdf.stem

        body_html = md.convert(body)
        md.reset()

        meta_parts = [p for p in (date, author) if p]
        meta = " · ".join(html.escape(p) for p in meta_parts)

        out_html = ARTICLE_TEMPLATE.format(
            title=html.escape(title),
            meta=meta,
            content=body_html,
            original_url=html.escape(original_url, quote=True),
            gtm_head=GTM_HEAD,
            gtm_body=GTM_BODY,
        )
        article_dir = output / slug
        article_dir.mkdir(parents=True, exist_ok=True)
        (article_dir / "index.html").write_text(out_html, encoding="utf-8")
        posts.append({"title": title, "date": date, "slug": slug})

    posts.sort(key=lambda p: p["date"], reverse=True)

    items = "\n".join(
        '<li><span class="date">{date}</span>'
        '<a href="{slug}/">{title}</a></li>'.format(
            date=html.escape(p["date"] or "----------"),
            slug=html.escape(p["slug"], quote=True),
            title=html.escape(p["title"]),
        )
        for p in posts
    )

    index_html = INDEX_TEMPLATE.format(
        title="ailia Tech BLOG (Mirror)",
        subtitle="medium.com/axinc から取得した記事のミラー",
        items=items,
        count=len(posts),
        gtm_head=GTM_HEAD,
        gtm_body=GTM_BODY,
    )
    (output / "index.html").write_text(index_html, encoding="utf-8")
    (output / "style.css").write_text(CSS, encoding="utf-8")
    return len(posts)


def main():
    parser = argparse.ArgumentParser(description="Build static site from scraped articles")
    parser.add_argument("--source", default="medium_export", help="入力ディレクトリ")
    parser.add_argument("--output", default="_site", help="出力ディレクトリ")
    args = parser.parse_args()

    n = build(Path(args.source), Path(args.output))
    print(f"Built {n} articles to {args.output}/")


if __name__ == "__main__":
    main()
