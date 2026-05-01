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
    <p class="pub-source"><a href="https://ailia.ai/">ailia.ai</a> · {count} articles</p>
  </div>
</header>
<nav class="tag-filter" role="tablist" aria-label="タグで絞り込み">
{tag_chips}
</nav>
<div class="search-bar">
  <input type="search" id="search-input" placeholder="キーワードで検索 (タイトル / 本文抜粋 / 著者 / タグ)" autocomplete="off">
  <p id="search-hits" class="search-hits" aria-live="polite"></p>
</div>
<main class="article-feed">
{cards}
</main>
<p id="empty-state" class="empty-state" hidden>該当する記事がありません</p>
<script>
(function() {{
  var chips = document.querySelectorAll('.tag-chip');
  var cards = document.querySelectorAll('.card');
  var input = document.getElementById('search-input');
  var hits = document.getElementById('search-hits');
  var empty = document.getElementById('empty-state');
  var activeTag = '';
  var activeQuery = '';

  function syncURL() {{
    if (!history.replaceState) return;
    var params = [];
    if (activeTag) params.push('tag=' + encodeURIComponent(activeTag));
    if (activeQuery) params.push('q=' + encodeURIComponent(activeQuery));
    var qs = params.length ? '?' + params.join('&') : '';
    history.replaceState(null, '', location.pathname + qs);
  }}

  function applyFilters() {{
    var q = activeQuery.toLowerCase();
    var visible = 0;
    cards.forEach(function(card) {{
      var tags = (card.dataset.tags || '').split(' ').filter(Boolean);
      var hay = card.dataset.search || '';
      var tagMatch = !activeTag || tags.indexOf(activeTag) !== -1;
      var queryMatch = !q || hay.indexOf(q) !== -1;
      var show = tagMatch && queryMatch;
      card.style.display = show ? '' : 'none';
      if (show) visible++;
    }});
    chips.forEach(function(c) {{ c.classList.toggle('active', c.dataset.tag === activeTag); }});
    if (empty) empty.hidden = visible !== 0;
    if (hits) {{
      hits.textContent = (activeQuery || activeTag)
        ? visible + ' / ' + cards.length + ' 件'
        : '';
    }}
    syncURL();
  }}

  chips.forEach(function(c) {{
    c.addEventListener('click', function() {{
      activeTag = c.dataset.tag;
      applyFilters();
    }});
  }});

  if (input) {{
    input.addEventListener('input', function() {{
      activeQuery = input.value.trim();
      applyFilters();
    }});
  }}

  // Apply initial filters from URL ?tag=...&q=...
  var params = new URLSearchParams(location.search);
  activeTag = params.get('tag') || '';
  activeQuery = params.get('q') || '';
  if (input && activeQuery) input.value = activeQuery;
  applyFilters();
}})();
</script>
</body>
</html>
"""

ARTICLE_CARD = """<article class="card" data-tags="{tags_attr}" data-search="{search_attr}">
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
<body class="page-article">
{gtm_body}
<header class="post-nav">
  <a href="../"><img src="{logo}" alt="{pub_title}" class="post-nav-logo">{pub_title}</a>
</header>
<article class="post">
  <header class="post-header">
    <h1>{title}</h1>
    <p class="post-meta"><span class="post-author">{author}</span><span class="post-date">{date}</span></p>
  </header>
  <div class="post-body">
{content}
  </div>
</article>
<footer class="site-footer">
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
  max-width: 1100px;
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

/* Keyword search */
.search-bar { padding: 12px 0 4px; }
.search-bar input[type="search"] {
  width: 100%;
  padding: 9px 14px;
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 0.95em;
  font-family: inherit;
  color: var(--fg);
  background: #fff;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.search-bar input[type="search"]:focus {
  border-color: var(--fg);
  box-shadow: 0 0 0 1px var(--fg);
}
.search-hits { margin: 6px 4px 0; color: var(--fg-muted); font-size: 0.82em; min-height: 1em; }
.empty-state { padding: 32px 0; color: var(--fg-muted); text-align: center; }

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

/* Tablet以上 (>=720px): Mediumライクなカードグリッドに切り替える */
@media (min-width: 720px) {
  .article-feed {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 36px 28px;
    border-top: 1px solid var(--border);
    padding-top: 28px;
  }
  .card { border-bottom: none; }
  .card-link {
    display: flex;
    flex-direction: column-reverse;  /* DOM順 (body, thumb) を逆転して
                                        thumb が上 / body が下になるよう描画 */
    gap: 14px;
    padding: 0;
  }
  .card-body { min-width: 0; }
  .card-thumb, .card-thumb-placeholder {
    width: 100%;
    height: auto;
    aspect-ratio: 16 / 9;
    border-radius: 4px;
  }
  .card-title { font-size: 1.25em; -webkit-line-clamp: 3; }
  .card-excerpt { -webkit-line-clamp: 3; }
}

/* PC ワイド (>=1024px): 3列グリッド */
@media (min-width: 1024px) {
  .article-feed { grid-template-columns: repeat(3, 1fr); }
}

/* Article page */
.post-nav {
  display: flex;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 32px;
  max-width: 728px;
  margin-left: auto;
  margin-right: auto;
}
/* 記事の本文は可読性のため index より狭めの 728px に制限する */
.post { max-width: 728px; margin: 0 auto; }
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

/* Mediumライクな関連リンクカード */
.link-card {
  display: block;
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 14px 18px;
  margin: 20px 0;
  text-decoration: none !important;
  color: var(--fg);
  transition: background 0.15s, border-color 0.15s;
}
.link-card:hover { background: var(--hover); border-color: #d8d8d8; }
.link-card-title {
  display: block;
  font-weight: 600;
  font-size: 1em;
  line-height: 1.35;
  color: var(--fg);
  margin-bottom: 4px;
}
.link-card-subtitle {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: var(--fg-muted);
  font-size: 0.9em;
  line-height: 1.45;
  margin-bottom: 6px;
}
.link-card-domain {
  display: block;
  color: var(--fg-muted);
  font-size: 0.8em;
}

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
/* 記事ページの footer も 728px に揃える */
body.page-article .site-footer { max-width: 728px; margin-left: auto; margin-right: auto; }
"""


_BYLINE_PATTERNS = [
    re.compile(r"^\d+\s*min\s*read$", re.I),
    re.compile(r"^[·•\-—]+$"),
    re.compile(r"^Share$", re.I),
    re.compile(r"^Listen$", re.I),
    # English month dates: "Sep 26, 2023" / "26 Sep 2023"
    re.compile(r"^[A-Z][a-z]{2,9}\s+\d{1,2},?\s+\d{4}$"),
    re.compile(r"^\d{1,2}\s+[A-Z][a-z]{2,9}\s+\d{4}$"),
    # Mediumが投稿直後の記事に表示する相対時刻 ("1 hour ago" 等)
    re.compile(
        r"^(?:Just now|Yesterday|\d+\s+(?:second|minute|hour|day|week|month)s?\s+ago)$",
        re.I,
    ),
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
    # Mediumが本文中に差し込む購読CTA。"## Get X's stories in your inbox"
    # 見出し + その下の4段落がワンセットで挿入される。
    re.compile(r"^#+\s+Get\s+.+?\s+stories\s+in\s+your\s+inbox\s*$", re.I),
    re.compile(r"^Join\s+Medium\s+for\s+free", re.I),
    re.compile(r"^Subscribe\s*$", re.I),
    re.compile(r"^Remember\s+me\s+for\s+faster\s+sign\s+in\s*$", re.I),
]


def _is_inline_noise(text: str) -> bool:
    s = text.strip()
    return any(p.match(s) for p in _INLINE_NOISE_PATTERNS)


def apply_substitutions(text: str) -> str:
    """記事本文・タイトル中の旧社名・旧URL・旧GitHub組織名を現行表記に置き換える。
    出力HTML/抜粋の両方で使用されるよう、markdownレベルで適用する。"""
    if not text:
        return text
    text = text.replace("ax株式会社", "アイリア株式会社")
    # axinc.jp はURL／表示テキストの両方に出るので一律置換。
    text = text.replace("axinc.jp", "ailia.ai")
    # axinc-ai (GitHub org) → ailia-ai。ただし "axinc-ailia" の様に
    # 末尾が単語の途中である場合は置換しない。Pythonの \b は Unicode
    # 文字 (日本語) と隣接する位置で word boundary を認識しないので、
    # 明示的な lookbehind/lookahead を使う。
    text = re.sub(
        r"(?<![A-Za-z0-9_])axinc-ai(?![A-Za-z0-9_])", "ailia-ai", text
    )
    return text


_INTERNAL_LINK_HEX_RE = re.compile(r"-[a-f0-9]{10,14}$")

# Mediumのembed/cardレンダリングで生まれる複数行 `[...](url)` パターン:
#   [## タイトル\n\n### サブタイトル (...…)\n\ndomain.com](url)
# 内部にH2/H3を含み厳密にはmarkdown不正なため、Python-Markdownでは
# プレーンテキスト扱いになる。タイトルと、(あれば) サブタイトルを残しつつ
# シンプルな `[**タイトル** — サブタイトル](url)` に整形する。サブタイトルには
# Mediumが付ける末尾の `…` などが含まれるため、これを残すことで関連記事の
# プレビュー文が消えないようにする。
_CARD_LINK_RE = re.compile(r"\[(#+\s+[\s\S]*?)\]\(([^)]+)\)")


def _normalize_one_card(label_body: str, url: str) -> str:
    headings = re.findall(r"^#+\s+(.+?)\s*$", label_body, re.M)
    title = headings[0].strip() if headings else ""
    subtitle = headings[1].strip() if len(headings) >= 2 else ""
    # ドメイン名は最後の非見出し行 (非空白の素テキスト)
    non_heading = [
        l.strip()
        for l in label_body.split("\n")
        if l.strip() and not l.strip().startswith("#")
    ]
    domain = non_heading[-1] if non_heading else ""

    rewritten_url = _rewrite_internal_link_url(url)

    if not title:
        return f"[{label_body.strip()}]({rewritten_url})"

    parts = [f'<span class="link-card-title">{html.escape(title)}</span>']
    if subtitle:
        parts.append(
            f'<span class="link-card-subtitle">{html.escape(subtitle)}</span>'
        )
    if domain:
        parts.append(
            f'<span class="link-card-domain">{html.escape(domain)}</span>'
        )
    inner = "".join(parts)
    # Python-Markdown が <p> でくるまないよう、前後に空行を入れて block として扱わせる
    return (
        f'\n\n<a class="link-card" href="'
        f'{html.escape(rewritten_url, quote=True)}">{inner}</a>\n\n'
    )


def normalize_card_links(text: str) -> str:
    return _CARD_LINK_RE.sub(
        lambda m: _normalize_one_card(m.group(1), m.group(2)), text
    )


def _rewrite_internal_link_url(url: str) -> str:
    """1つのリンクURLを判定し、本ミラー内の記事を指していれば
    記事ページから見た相対パス ``../<slug>/`` 形式に書き換える。それ以外は
    そのまま返す。

    GitHub Pages のプロジェクトページ (``ailia-ai.github.io/ailia-tech/``)
    で配信するため、絶対パス ``/<slug>/`` だと
    ``ailia-ai.github.io/<slug>/`` (basepath が抜ける) になり 404 する。
    記事HTMLは ``_site/<slug>/index.html`` に置かれているので
    隣の記事へは ``../<other-slug>/`` で安全に到達できる。"""
    from urllib.parse import unquote as _unq

    url = url.strip()
    # 絶対URL: medium.com/axinc/<slug>
    m = re.match(r"https?://medium\.com/axinc/([^?\s#)]+)", url)
    if m:
        slug = m.group(1).rstrip("/")
    elif url.startswith("/") and not url.startswith("//"):
        # /<slug>?source=...   (Mediumが本文中の関連記事カードに使う形式)
        m = re.match(r"^/([^?\s#)]+)", url)
        if not m:
            return url
        slug = m.group(1).rstrip("/")
    else:
        return url
    if not _INTERNAL_LINK_HEX_RE.search(slug):
        return url
    return f"../{_unq(slug)}/"


def rewrite_internal_links(text: str) -> str:
    """記事markdown中の Medium 記事URLを本ミラー内の相対URLに書き換える。

    対象は ``[text](url)`` 形式の絶対URL ``medium.com/axinc/<slug>`` と
    Mediumがレンダリングで使う相対形式 ``/<slug>?source=...`` のみ。
    本ミラーに無い ``kyakuno.medium.com`` 等の外部リンクはそのまま残す。
    画像リンク ``![alt](url)`` の URL も処理対象になるが、画像URLは
    記事スラグ形式でないため _rewrite_internal_link_url が unchanged を返す。
    """

    def repl(m: re.Match) -> str:
        return f"]({_rewrite_internal_link_url(m.group(1))})"

    return re.sub(r"\]\(([^)]+)\)", repl, text)


_BOILERPLATE_LEAD_RE = re.compile(
    r"\n+(アイリア株式会社(?:は|では|の)|AIで、しごとするなら|株式会社アクセル)"
)
_REDUNDANT_HR_RE = re.compile(r"(?:\n*---\n+){2,}")


def inject_company_separator(text: str) -> str:
    """既存スクレイプ済みの記事は ``<div role="separator">`` がmarkdownify
    時点で読み飛ばされて ``---`` が残っていない。記事末尾に登場する既知の
    定型パラグラフ (アイリア株式会社のお問い合わせ案内、AIで、しごとするなら
    の媒体紹介、株式会社アクセル始まりのco-author案内など) の直前に ``---``
    を注入することでこの取りこぼしを救う。

    新規スクレイプでは medium_publication.py が事前に ``<hr>`` を入れて
    ``---`` が markdown に残るため、二重挿入回避として最後に連続 ``---`` を
    一本に畳む。"""
    text = _BOILERPLATE_LEAD_RE.sub(r"\n\n---\n\n\1", text)
    text = _REDUNDANT_HR_RE.sub("\n\n---\n\n", text)
    return text


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

        title = apply_substitutions(fm.get("title") or mdf.stem)
        date = fm.get("date", "")
        author = fm.get("author", "")
        original_url = fm.get("original_url", "")
        slug = medium_slug_from_url(original_url) or mdf.stem

        tags = fm.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        thumb_url = extract_thumbnail(body)
        cleaned = rewrite_internal_links(
            inject_company_separator(
                apply_substitutions(normalize_card_links(clean_body(body)))
            )
        )
        excerpt = extract_excerpt(cleaned)

        body_html = md.convert(cleaned)
        md.reset()

        out_html = ARTICLE_TEMPLATE.format(
            title=html.escape(title),
            pub_title=html.escape(PUBLICATION_TITLE),
            author=html.escape(author),
            date=html.escape(date),
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

    def _search_haystack(p: dict) -> str:
        # 検索対象は (タイトル | 抜粋 | 著者 | タグ) を小文字化して結合。
        # JS側で input.value.toLowerCase() と部分一致させる。
        parts = [
            p.get("title", ""),
            p.get("excerpt", ""),
            p.get("author", ""),
            " ".join(p.get("tags") or []),
        ]
        return " ".join(parts).lower()

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
            search_attr=html.escape(_search_haystack(p), quote=True),
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
