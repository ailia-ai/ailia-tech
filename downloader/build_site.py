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
PUBLICATION_TITLE = "ailia Tech BLOG"
PUBLICATION_TAGLINE = "The latest technology related to AI."
PUBLICATION_LOGO = (
    "https://miro.medium.com/v2/resize:fill:160:160/1*5yfBcdCERuuQ1y98iuvhAg.png"
)
MEDIUM_PUBLICATION_URL = "https://medium.com/axinc"

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
<meta name="description" content="{tagline}">
<link rel="stylesheet" href="style.css">
{gtm_head}
</head>
<body>
{gtm_body}
<header class="pub-header">
  <img src="{logo}" alt="{title}" class="pub-logo">
  <div class="pub-meta">
    <h1>{title}</h1>
    <p class="pub-tagline">{tagline}</p>
    <p class="pub-source">Mirror of <a href="{medium_url}">medium.com/axinc</a> · {count} articles</p>
  </div>
</header>
<nav class="tag-filter" role="tablist" aria-label="タグで絞り込み">
{tag_chips}
</nav>
<main class="article-feed">
{cards}
</main>
<script>
(function() {{
  var chips = document.querySelectorAll('.tag-chip');
  var cards = document.querySelectorAll('.card');
  function apply(tag) {{
    chips.forEach(function(c) {{ c.classList.toggle('active', c.dataset.tag === tag); }});
    cards.forEach(function(card) {{
      var tags = (card.dataset.tags || '').split(' ').filter(Boolean);
      card.style.display = (!tag || tags.indexOf(tag) !== -1) ? '' : 'none';
    }});
    if (history.replaceState) {{
      var url = tag ? '?tag=' + encodeURIComponent(tag) : location.pathname;
      history.replaceState(null, '', url);
    }}
  }}
  chips.forEach(function(c) {{ c.addEventListener('click', function() {{ apply(c.dataset.tag); }}); }});
  // Apply initial filter from URL ?tag=...
  var m = location.search.match(/[?&]tag=([^&]+)/);
  if (m) apply(decodeURIComponent(m[1]));
}})();
</script>
</body>
</html>
"""

ARTICLE_CARD = """<article class="card" data-tags="{tags_attr}">
  <a class="card-link" href="{slug}/">
    <div class="card-body">
      <h2 class="card-title">{title}</h2>
      <p class="card-excerpt">{excerpt}</p>
      <p class="card-meta"><span class="card-author">{author}</span><span class="card-date">{date}</span>{tag_pills}</p>
    </div>
    {thumb_html}
  </a>
</article>"""

# Mediumのpublication navで使われている主要トピック (表示順 / 表示名)
PRIMARY_TAGS = [
    ("", "All"),
    ("ailia-models", "ailia MODELS"),
    ("ailia-sdk", "ailia SDK"),
    ("ailia-tutorial", "ailia Tutorial"),
    ("ailia-technology", "ailia Technology"),
]

ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {pub_title}</title>
<meta name="description" content="{excerpt}">
<link rel="stylesheet" href="../style.css">
<link rel="canonical" href="{original_url}">
{gtm_head}
</head>
<body>
{gtm_body}
<header class="post-nav">
  <a href="../"><img src="{logo}" alt="{pub_title}" class="post-nav-logo">{pub_title}</a>
</header>
<article class="post">
  <header class="post-header">
    <h1>{title}</h1>
    <p class="post-meta"><span class="post-author">{author}</span>{date_sep}<span class="post-date">{date}</span></p>
  </header>
  <div class="post-body">
{content}
  </div>
</article>
<footer class="site-footer">
  <p>原文: <a href="{original_url}">{original_url}</a></p>
  <p><a href="../">&larr; 記事一覧へ</a></p>
</footer>
</body>
</html>
"""

CSS = """:root {
  --fg: #242424;
  --fg-muted: #6b6b6b;
  --bg: #ffffff;
  --link: #1a8917;
  --border: #f2f2f2;
  --hover: #fafafa;
}
* { box-sizing: border-box; }
html { font-size: 16px; overflow-x: hidden; }
body {
  font-family: "Hiragino Kaku Gothic ProN", "Yu Gothic", Meiryo,
    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  max-width: 728px;
  margin: 0 auto;
  padding: 24px 24px 64px;
  line-height: 1.6;
  color: var(--fg);
  background: var(--bg);
  overflow-wrap: break-word;
  word-wrap: break-word;
}
/* iOS Safari 等で長いURLや英単語が viewport をはみ出さないように */
.post-body, .site-footer, .card-body, .pub-meta { min-width: 0; overflow-wrap: anywhere; }
.post-body img, .post-body video, .post-body iframe {
  max-width: 100%;
  height: auto;
}
.post-body pre { white-space: pre-wrap; max-width: 100%; }
.post-body table { display: block; max-width: 100%; overflow-x: auto; }
a { color: inherit; text-decoration: none; }
a:hover { text-decoration: underline; }

/* Publication header (index page) */
.pub-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 32px 0 28px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}
.pub-logo {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  flex-shrink: 0;
  object-fit: cover;
}
.pub-meta h1 {
  margin: 0 0 6px;
  font-size: 1.7em;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.pub-tagline { margin: 0 0 6px; color: var(--fg); font-size: 1em; }
.pub-source { margin: 0; color: var(--fg-muted); font-size: 0.85em; }
.pub-source a { color: var(--link); }

/* Tag filter (publication-wide topic chips) */
.tag-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px 0 4px;
  margin-bottom: 4px;
  border-bottom: 1px solid var(--border);
}
.tag-chip {
  appearance: none;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--fg);
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 0.85em;
  font-family: inherit;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.tag-chip:hover { background: var(--hover); }
.tag-chip.active {
  background: var(--fg);
  color: #fff;
  border-color: var(--fg);
}

/* Inline tag pills shown next to author/date on each card */
.card-tags {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-left: 4px;
}
.card-tags::before { content: "·"; margin-right: 4px; color: var(--fg-muted); }
.card-tag {
  font-size: 0.78em;
  color: var(--fg-muted);
  background: var(--border);
  padding: 1px 8px;
  border-radius: 999px;
  white-space: nowrap;
}

/* Article feed (cards) */
.article-feed { display: flex; flex-direction: column; }
.card { border-bottom: 1px solid var(--border); }
.card-link {
  display: grid;
  grid-template-columns: 1fr 112px;
  gap: 24px;
  padding: 24px 0;
  align-items: center;
  text-decoration: none;
  color: inherit;
}
.card-link:hover { text-decoration: none; background: var(--hover); }
.card-body { min-width: 0; }
.card-title {
  margin: 0 0 6px;
  font-size: 1.15em;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.3;
  color: var(--fg);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-excerpt {
  margin: 0 0 12px;
  color: var(--fg-muted);
  font-size: 0.95em;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  margin: 0;
  font-size: 0.82em;
  color: var(--fg-muted);
  display: flex;
  gap: 8px;
  align-items: center;
}
.card-meta span:not(:last-child)::after {
  content: "·";
  margin-left: 8px;
  color: var(--fg-muted);
}
.card-thumb {
  width: 112px;
  height: 112px;
  object-fit: cover;
  background: var(--border);
  border-radius: 2px;
  display: block;
}
.card-thumb-placeholder {
  width: 112px;
  height: 112px;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
  border-radius: 2px;
}
@media (max-width: 540px) {
  .card-link { grid-template-columns: 1fr 80px; gap: 16px; }
  .card-thumb, .card-thumb-placeholder { width: 80px; height: 80px; }
  .pub-logo { width: 64px; height: 64px; }
  .pub-meta h1 { font-size: 1.4em; }
}

/* Article page */
.post-nav {
  display: flex;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 32px;
}
.post-nav a { display: flex; align-items: center; gap: 10px; color: var(--fg); font-weight: 600; }
.post-nav-logo { width: 36px; height: 36px; border-radius: 50%; }
.post-header { margin-bottom: 28px; }
.post-header h1 {
  font-size: 2em;
  margin: 0 0 12px;
  line-height: 1.2;
  letter-spacing: -0.015em;
  font-weight: 800;
}
.post-meta { margin: 0; color: var(--fg-muted); font-size: 0.92em; }
.post-meta span + span::before { content: "·"; margin: 0 8px; }
.post-body { font-size: 1.05em; line-height: 1.75; }
.post-body h2 { margin: 36px 0 14px; font-size: 1.45em; letter-spacing: -0.01em; }
.post-body h3 { margin: 28px 0 10px; font-size: 1.2em; }
.post-body p { margin: 16px 0; }
.post-body img { max-width: 100%; height: auto; display: block; margin: 20px auto; }
.post-body pre {
  background: #f7f7f7;
  padding: 16px;
  overflow-x: auto;
  border-radius: 4px;
  font-size: 0.92em;
}
.post-body code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
}
.post-body pre code { background: transparent; padding: 0; }
.post-body blockquote {
  border-left: 3px solid var(--link);
  margin: 20px 0;
  padding: 4px 16px;
  color: var(--fg-muted);
}
.post-body table { border-collapse: collapse; margin: 16px 0; }
.post-body th, .post-body td { border: 1px solid var(--border); padding: 8px 12px; }
.post-body a { color: var(--link); text-decoration: underline; text-decoration-thickness: 1px; }

/* Footer */
.site-footer {
  margin-top: 48px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  color: var(--fg-muted);
  font-size: 0.85em;
}
.site-footer p { margin: 6px 0; }
.site-footer a { color: var(--link); }
"""


_BYLINE_PATTERNS = [
    re.compile(r"^\d+\s*min\s*read$", re.I),
    re.compile(r"^[·•\-—]+$"),
    re.compile(r"^Share$", re.I),
    re.compile(r"^Listen$", re.I),
    # English month dates: "Sep 26, 2023" / "26 Sep 2023"
    re.compile(r"^[A-Z][a-z]{2,9}\s+\d{1,2},?\s+\d{4}$"),
    re.compile(r"^\d{1,2}\s+[A-Z][a-z]{2,9}\s+\d{4}$"),
]


def _is_byline_paragraph(text: str) -> bool:
    """Mediumがレンダリングする著者プロフィール周りのメタ行か判定する。"""
    s = text.strip()
    if not s:
        return True
    if any(p.match(s) for p in _BYLINE_PATTERNS):
        return True
    # "[![avatar](...)] (link to author)" — image link starting with [![
    if s.startswith("[!["):
        return True
    # Plain link line "[Author Name](url)" — single markdown link
    if re.fullmatch(r"\[[^\]]+\]\([^)]+\)", s):
        return True
    return False


_INLINE_NOISE_PATTERNS = [
    re.compile(r"^Press enter or click to view image in full size$", re.I),
]


def _is_inline_noise(text: str) -> bool:
    s = text.strip()
    return any(p.match(s) for p in _INLINE_NOISE_PATTERNS)


def clean_body(body: str) -> str:
    """先頭の重複H1 (Mediumは同タイトルを2回出力する) とバイラインブロック、
    本文中のMedium UIアーティファクトを取り除く。"""
    paragraphs = re.split(r"\n\s*\n", body)
    out = []
    in_intro = True
    for p in paragraphs:
        s = p.strip()
        if in_intro:
            if not s:
                continue
            if s.startswith("# ") or _is_byline_paragraph(s):
                continue
            in_intro = False
        if _is_inline_noise(s):
            continue
        out.append(p)
    return "\n\n".join(out).strip()


def extract_excerpt(cleaned_body: str, max_len: int = 180) -> str:
    """clean_body後の先頭段落から平文の抜粋を生成する。"""
    paragraphs = re.split(r"\n\s*\n", cleaned_body)
    for p in paragraphs:
        s = p.strip()
        if not s or s.startswith("#") or s.startswith("!["):
            continue
        # Strip markdown link/image syntax
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"[*_`>#]+", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) < 20:
            continue
        if len(text) > max_len:
            text = text[: max_len - 1].rstrip() + "…"
        return text
    return ""


def extract_thumbnail(body: str) -> str:
    """先頭から最初の本文画像 (image_000.* 以外) のsrcを返す。"""
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", body):
        url = m.group(1).strip()
        if "image_000." in url:
            continue
        return url
    return ""


def parse_front_matter(text: str) -> tuple[dict, str]:
    """medium_publication.pyが書き出すYAMLフロントマターを簡易パース。
    インラインリスト記法 ``tags: [a, b, c]`` のみサポート。"""
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
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1]
            fm[key] = [
                item.strip().strip('"').strip("'")
                for item in inner.split(",")
                if item.strip()
            ]
        else:
            fm[key] = val.strip('"')
    return fm, body


def medium_slug_from_url(url: str) -> str:
    if not url:
        return ""
    return urlparse(url).path.rstrip("/").split("/")[-1]


def thumb_html_for(thumb_url: str, alt: str) -> str:
    if not thumb_url:
        return '<div class="card-thumb-placeholder" aria-hidden="true"></div>'
    # 記事カード上のサムネイルは、index.htmlからの相対パスに整える。
    # 本文markdown中のパスは "../images/<safe>/..." なので、index.html (output直下)
    # からは "images/<safe>/..." に書き換える必要がある。
    if thumb_url.startswith("../images/"):
        thumb_url = thumb_url[3:]  # "../images/" -> "/images/" -> remove leading
        thumb_url = thumb_url.lstrip("/")
    return f'<img src="{html.escape(thumb_url, quote=True)}" alt="{html.escape(alt)}" class="card-thumb" loading="lazy">'


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

        tags = fm.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        thumb_url = extract_thumbnail(body)
        cleaned = clean_body(body)
        excerpt = extract_excerpt(cleaned)

        body_html = md.convert(cleaned)
        md.reset()

        out_html = ARTICLE_TEMPLATE.format(
            title=html.escape(title),
            pub_title=html.escape(PUBLICATION_TITLE),
            author=html.escape(author),
            date=html.escape(date),
            date_sep="" if not (author and date) else "",
            excerpt=html.escape(excerpt, quote=True),
            content=body_html,
            original_url=html.escape(original_url, quote=True),
            logo=html.escape(PUBLICATION_LOGO, quote=True),
            gtm_head=GTM_HEAD,
            gtm_body=GTM_BODY,
        )
        article_dir = output / slug
        article_dir.mkdir(parents=True, exist_ok=True)
        (article_dir / "index.html").write_text(out_html, encoding="utf-8")
        posts.append(
            {
                "title": title,
                "date": date,
                "author": author,
                "slug": slug,
                "excerpt": excerpt,
                "thumb": thumb_url,
                "tags": tags,
            }
        )

    posts.sort(key=lambda p: p["date"], reverse=True)

    def _tag_pills(tags: list) -> str:
        # 主要タグだけインラインpillとしてカードに表示する
        primary = {t for t, _ in PRIMARY_TAGS if t}
        shown = [t for t in tags if t in primary]
        if not shown:
            return ""
        items = "".join(
            f'<span class="card-tag">{html.escape(t)}</span>' for t in shown
        )
        return f'<span class="card-tags">{items}</span>'

    cards = "\n".join(
        ARTICLE_CARD.format(
            slug=html.escape(p["slug"], quote=True),
            title=html.escape(p["title"]),
            excerpt=html.escape(p["excerpt"]),
            author=html.escape(p["author"]),
            date=html.escape(p["date"] or ""),
            thumb_html=thumb_html_for(p["thumb"], p["title"]),
            tags_attr=html.escape(" ".join(p["tags"]), quote=True),
            tag_pills=_tag_pills(p["tags"]),
        )
        for p in posts
    )

    tag_chips_html = "\n".join(
        '<button type="button" class="tag-chip{active}" data-tag="{tag}">{label}</button>'.format(
            tag=html.escape(tag, quote=True),
            label=html.escape(label),
            active=" active" if tag == "" else "",
        )
        for tag, label in PRIMARY_TAGS
    )

    index_html = INDEX_TEMPLATE.format(
        title=html.escape(PUBLICATION_TITLE),
        tagline=html.escape(PUBLICATION_TAGLINE),
        logo=html.escape(PUBLICATION_LOGO, quote=True),
        medium_url=html.escape(MEDIUM_PUBLICATION_URL, quote=True),
        cards=cards,
        tag_chips=tag_chips_html,
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
