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
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

import markdown

GTM_ID = "GTM-5Q579RMM"
PUBLICATION_TITLE = "ailia Tech BLOG"
PUBLICATION_TAGLINE = "The latest technology related to AI."
PUBLICATION_LOGO = "https://tech.ailia.ai/logo.png"

# 言語別の設定。site_url_path は SITE_BASE_URL からの相対 (空 or "en/" 等)、
# articles_label は記事カウント表記、search_placeholder は検索ボックスの
# プレースホルダ文。ヘッダーの言語切替リンクで参照される。
LANGUAGES = [
    {
        "code": "ja",
        "label": "JA",
        "html_lang": "ja",
        "source_dir": "ja",
        "site_path": "",
        "articles_label": "{n} articles",
        "search_placeholder": "キーワードで検索 (タイトル / 本文抜粋 / 著者 / タグ)",
        "tag_filter_aria": "タグで絞り込み",
        "all_label": "すべて",
        "back_to_index": "← 記事一覧",
        "empty_state": "該当する記事がありません",
        "footer_back": "← 記事一覧へ",
        "publication": "axinc",
        "ailia_url": "https://ailia.ai/",
        "docs_url": "https://docs.ailia.ai/",
        "github_url": "https://github.com/ailia-ai/ailia-models",
        "contact_url": "https://ailia.ai/contact/",
        "nav_docs_label": "Docs",
        "nav_github_label": "GitHub",
        "cta_title": "ailia SDK を試す",
        "cta_subtitle": "ailia SDK は ailia.ai が開発するクロスプラットフォーム対応の AI 推論エンジンです。Windows / macOS / Linux / iOS / Android で動作し、ailia MODELS の推論モデルがそのまま使えます。",
        "cta_primary_url": "https://docs.ailia.ai/sdk/",
        "cta_primary_label": "インストール手順",
        "cta_secondary_label": "お問い合わせ",
        "banner_sdk_label": "ailia SDK のドキュメント",
        "banner_tutorial_label": "インストール手順を先に見る",
    },
    {
        "code": "en",
        "label": "EN",
        "html_lang": "en",
        "source_dir": "en",
        "site_path": "en/",
        "articles_label": "{n} articles",
        "search_placeholder": "Search by keyword (title / excerpt / author / tags)",
        "tag_filter_aria": "Filter by tag",
        "all_label": "All",
        "back_to_index": "← All posts",
        "empty_state": "No matching articles",
        "footer_back": "← All posts",
        "publication": "axinc-ai",
        "ailia_url": "https://ailia.ai/en/",
        "docs_url": "https://docs.ailia.ai/en/",
        "github_url": "https://github.com/ailia-ai/ailia-models",
        "contact_url": "https://ailia.ai/en/contact/",
        "nav_docs_label": "Docs",
        "nav_github_label": "GitHub",
        "cta_title": "Try ailia SDK",
        "cta_subtitle": "ailia SDK is a cross-platform AI inference engine developed by ailia.ai. It runs on Windows / macOS / Linux / iOS / Android and supports every model published in ailia MODELS out of the box.",
        "cta_primary_url": "https://docs.ailia.ai/en/sdk/",
        "cta_primary_label": "Get Started",
        "cta_secondary_label": "Contact us",
        "banner_sdk_label": "ailia SDK documentation",
        "banner_tutorial_label": "Jump to install instructions",
    },
]

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
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{tagline}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{site_url}">
{hreflang_links}
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{tagline}">
<meta property="og:url" content="{site_url}">
<meta property="og:site_name" content="{title}">
<meta property="og:image" content="{logo}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{tagline}">
<meta name="twitter:image" content="{logo}">
<link rel="shortcut icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">
<link rel="stylesheet" href="/style.css">
{gtm_head}
</head>
<body>
{gtm_body}
<div class="site-top">
  <nav class="site-nav" aria-label="Site">{site_nav}</nav>
  <nav class="lang-switch" aria-label="Language">{lang_switch}</nav>
</div>
<header class="pub-header">
  <img src="{logo}" alt="{title}" class="pub-logo">
  <div class="pub-meta">
    <h1>{title}</h1>
    <p class="pub-tagline">{tagline}</p>
    <p class="pub-source"><a href="{ailia_url}">ailia.ai</a> · {articles_label}</p>
  </div>
</header>
<nav class="tag-filter" role="tablist" aria-label="{tag_filter_aria}">
{tag_chips}
</nav>
<div class="search-bar">
  <input type="search" id="search-input" placeholder="{search_placeholder}" autocomplete="off">
  <p id="search-hits" class="search-hits" aria-live="polite"></p>
</div>
<main class="article-feed">
{cards}
</main>
<p id="empty-state" class="empty-state" hidden>{empty_state}</p>
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
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {pub_title}</title>
<meta name="description" content="{excerpt}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{page_url}">
{hreflang_links}
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{excerpt}">
<meta property="og:url" content="{page_url}">
<meta property="og:site_name" content="{pub_title}">
<meta property="og:image" content="{og_image}">
<meta property="article:published_time" content="{date}">
<meta property="article:modified_time" content="{lastmod}">
<meta property="article:author" content="{author}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{excerpt}">
<meta name="twitter:image" content="{og_image}">
<script type="application/ld+json">{ld_json}</script>
<link rel="shortcut icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">
<link rel="stylesheet" href="/style.css">
{gtm_head}
</head>
<body class="page-article">
{gtm_body}
<div class="site-top">
  <nav class="site-nav" aria-label="Site">{site_nav}</nav>
  <nav class="lang-switch" aria-label="Language">{lang_switch}</nav>
</div>
<header class="post-nav">
  <a href="../"><img src="{logo}" alt="{pub_title}" class="post-nav-logo">{pub_title}</a>
</header>
<article class="post">
  <header class="post-header">
    <h1>{title}</h1>
    <p class="post-meta"><span class="post-author">{author}</span><span class="post-date">{date}</span></p>
  </header>
  {opening_banner}
  <div class="post-body">
{content}
  </div>
  <aside class="article-cta" aria-label="Try ailia SDK">
    <h3>{cta_title}</h3>
    <p>{cta_subtitle}</p>
    <p class="cta-buttons">
      <a class="cta-primary" href="{cta_primary_url}">{cta_primary_label}</a>
      <a class="cta-secondary" href="{cta_secondary_url}">{cta_secondary_label}</a>
    </p>
  </aside>
</article>
<footer class="site-footer">
  <p><a href="../">{footer_back}</a></p>
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
/* ブラウザ既定の <hr> は inset 縁取りで太く見えるので、シンプルな
   1px の細いラインに揃える。 */
.post-body hr {
  border: 0;
  border-top: 1px solid var(--border);
  height: 0;
  margin: 28px 0;
}
a { color: inherit; text-decoration: none; }
a:hover { text-decoration: underline; }

/* Top bar: site navigation + language switcher */
.site-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 6px 0 4px;
  font-size: 0.88em;
  flex-wrap: wrap;
}
.site-nav { display: flex; gap: 4px; flex-wrap: wrap; }
.site-nav a {
  color: var(--fg);
  text-decoration: none;
  padding: 4px 10px;
  border-radius: 999px;
}
.site-nav a:hover { background: var(--hover); }
.lang-switch { display: flex; gap: 6px; }
.lang-switch a {
  color: var(--fg-muted);
  text-decoration: none;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid transparent;
  font-weight: 600;
}
.lang-switch a.active { color: var(--fg); border-color: var(--border); }
.lang-switch a:hover { background: var(--hover); }

/* Opening banner: category-aware callout shown above the article body */
.article-banner {
  margin: 0 0 28px;
  padding: 10px 16px;
  border-left: 3px solid var(--link);
  background: #f3faf3;
  font-size: 0.92em;
}
.article-banner a { color: var(--link); text-decoration: none; font-weight: 600; }
.article-banner a:hover { text-decoration: underline; }

/* End-of-article CTA */
.article-cta {
  margin: 48px 0 16px;
  padding: 22px 24px 24px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: linear-gradient(135deg, #fbfbfb 0%, #f3f6f9 100%);
}
.article-cta h3 {
  margin: 0 0 8px;
  font-size: 1.15em;
  letter-spacing: -0.01em;
  color: var(--fg);
}
.article-cta p { margin: 0 0 14px; color: var(--fg-muted); font-size: 0.95em; line-height: 1.6; }
.article-cta .cta-buttons { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 0; }
.article-cta .cta-primary,
.article-cta .cta-secondary {
  display: inline-block;
  padding: 9px 18px;
  border-radius: 999px;
  font-size: 0.9em;
  font-weight: 600;
  text-decoration: none;
}
.article-cta .cta-primary { background: var(--fg); color: #fff !important; }
.article-cta .cta-primary:hover { background: #000; text-decoration: none; }
.article-cta .cta-secondary {
  background: #fff;
  color: var(--fg) !important;
  border: 1px solid var(--border);
}
.article-cta .cta-secondary:hover { background: var(--hover); text-decoration: none; }

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
    # 拍手数 ("2", "10", "1.2K", "10K", "1M" など) - 英語版だと
    # 著者バイラインの直後に剥き出しの数字パラグラフとして出る。
    re.compile(r"^\d+(?:\.\d+)?[KMm]?$"),
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
    # 日本語表記
    text = text.replace("ax株式会社", "アイリア株式会社")
    # 英語表記。"ax Inc." / "ax Inc" 両方拾う。前後にalphanumericが無いことを
    # lookahead/lookbehindで確認して "max Inc" のような単語境界誤マッチを防ぐ。
    text = re.sub(
        r"(?<![A-Za-z0-9_])ax\s+Inc\.?(?![A-Za-z0-9_])",
        lambda m: "ailia Inc." if m.group().rstrip().endswith(".") else "ailia Inc",
        text,
    )
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


def _normalize_one_card(label_body: str, url: str, lang_pub: str = "axinc") -> str:
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

    rewritten_url = _rewrite_internal_link_url(url, lang_pub)

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


def normalize_card_links(text: str, lang_pub: str = "axinc") -> str:
    return _CARD_LINK_RE.sub(
        lambda m: _normalize_one_card(m.group(1), m.group(2), lang_pub), text
    )


def _rewrite_internal_link_url(url: str, lang_pub: str = "axinc") -> str:
    """1つのリンクURLを判定し、現在処理中の言語に属する記事を指していれば
    記事ページから見た相対パス ``../<slug>/`` に書き換える。

    ``lang_pub`` には現在のpublicationスラグ (``axinc`` / ``axinc-ai``) を
    渡す。違う publication の URL は cross-language リンク扱いで Medium URL
    のまま残す。tech.ailia.ai/<slug> は ja 専用の表記だったので axinc 扱い。"""
    from urllib.parse import unquote as _unq

    url = url.strip()
    # 絶対URL: medium.com/<lang_pub>/<slug>
    m = re.match(
        rf"https?://medium\.com/{re.escape(lang_pub)}/([^?\s#)]+)", url
    )
    if m:
        slug = m.group(1).rstrip("/")
    # tech.ailia.ai は ja の旧Medium custom domain。axinc の同義として処理。
    elif lang_pub == "axinc" and re.match(
        r"https?://tech\.ailia\.ai/([^?\s#)]+)", url
    ):
        m2 = re.match(r"https?://tech\.ailia\.ai/([^?\s#)]+)", url)
        slug = m2.group(1).rstrip("/")
    elif url.startswith("/") and not url.startswith("//"):
        m2 = re.match(r"^/([^?\s#)]+)", url)
        if not m2:
            return url
        slug = m2.group(1).rstrip("/")
    else:
        return url
    if not _INTERNAL_LINK_HEX_RE.search(slug):
        return url
    return f"../{_unq(slug)}/"


def rewrite_internal_links(text: str, lang_pub: str = "axinc") -> str:
    """記事markdown中の Medium 記事URLを本ミラー内の相対URLに書き換える。

    対象は ``[text](url)`` 形式の絶対URL ``medium.com/<lang_pub>/<slug>`` と
    Mediumがレンダリングで使う相対形式 ``/<slug>?source=...`` のみ。
    本ミラーに無い ``kyakuno.medium.com`` 等の外部リンクはそのまま残す。"""

    def repl(m: re.Match) -> str:
        return f"]({_rewrite_internal_link_url(m.group(1), lang_pub)})"

    return re.sub(r"\]\(([^)]+)\)", repl, text)


_BOILERPLATE_LEAD_RE = re.compile(
    # 会社名がmarkdownリンク化されているケース ([アイリア株式会社](...) や
    # [ailia Inc.](...)) もあるため、先頭の "[" を任意で受け付ける。
    r"\n+(\[?(?:アイリア株式会社(?:は|では|の|\])"
    r"|AIで、しごとするなら"
    r"|株式会社アクセル"
    r"|ailia Inc\."
    r"))"
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


# NLPで使う特殊トークン名のうち、HTMLでも有効な要素名と被る/被りそうな
# ものを列挙。<s>...</s> は HTML strikethrough として描画され、本文末尾が
# まるまる取り消し線になる事故が起きた。コードブロックの外でこれらが
# 出現したら HTML エンティティに置換する。
_NLP_TOKEN_NAMES = ["s", "bos", "eos", "sos", "pad", "unk", "sep", "cls", "mask"]
_NLP_TOKEN_RE = re.compile(
    r"</?(?:" + "|".join(_NLP_TOKEN_NAMES) + r")>", re.IGNORECASE
)


def escape_nlp_tokens(text: str) -> str:
    """``<s>`` 等のNLP特殊トークンをコードブロック外でHTMLエンティティに
    置き換える。コードブロック (fenced + inline) はプレースホルダで退避し、
    エスケープ後に復元する。"""
    if not text:
        return text
    fences: list = []
    inline_codes: list = []

    def _stash_fence(m: re.Match) -> str:
        fences.append(m.group())
        return f"\x01{len(fences) - 1}\x01"

    def _stash_inline(m: re.Match) -> str:
        inline_codes.append(m.group())
        return f"\x02{len(inline_codes) - 1}\x02"

    text = re.sub(r"```[\s\S]*?```", _stash_fence, text)
    text = re.sub(r"`[^`\n]+`", _stash_inline, text)

    text = _NLP_TOKEN_RE.sub(
        lambda m: m.group().replace("<", "&lt;").replace(">", "&gt;"), text
    )

    text = re.sub(r"\x02(\d+)\x02", lambda m: inline_codes[int(m.group(1))], text)
    text = re.sub(r"\x01(\d+)\x01", lambda m: fences[int(m.group(1))], text)
    return text


def _escape_inline_hash(body: str) -> str:
    """blockquote内の ``#`` をH1誤認識から救う。

    Python-Markdown の atx heading パーサは空白の有無を問わないので
    ``> #x`` でも ``> # comment`` でも H1 として扱われ、ローカルでは超巨大な
    見出しになってしまう。Mediumのblockquoteはコード片や引用文として
    使われ、内部にmarkdownの見出しを意図することはまず無いので、
    blockquote先頭の ``#`` は一律バックスラッシュでエスケープする。"""
    return re.sub(r"^(\s*>+\s*)#", r"\1\\#", body, flags=re.M)


def clean_body(body: str) -> str:
    """先頭の重複H1 (Mediumは同タイトルを2回出力する) とバイラインブロック、
    本文中のMedium UIアーティファクトを取り除く。"""
    body = _escape_inline_hash(body)
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
    # index.html は各言語ディレクトリの直下 (例: _site/ または _site/en/) で、
    # その隣にある images/ を参照させたい。本文markdown中のパスは
    # "../images/<safe>/..." なので、index.html位置からは "images/<safe>/..."
    # に書き換える必要がある。
    if thumb_url.startswith("../images/"):
        thumb_url = thumb_url[len("../"):]
    return f'<img src="{html.escape(thumb_url, quote=True)}" alt="{html.escape(alt)}" class="card-thumb" loading="lazy">'


# 公開ホスト名 (project basepath を含めた絶対 URL の前置部分)。独自ドメイン
# 利用時はホスト名のみで basepath は付かない。CDN/別ドメインに移すときは
# ここを書き換えるだけで sitemap / canonical / OGP の URL が同期する。
SITE_BASE_URL = "https://tech.ailia.ai/"
# GitHub Pages に独自ドメインを伝える CNAME ファイルの中身。
SITE_HOST = "tech.ailia.ai"


def _write_sitemap_combined(all_posts: list, output: Path) -> None:
    """全言語の index + 記事をまとめた sitemap.xml を生成する。
    ``all_posts`` は ``[(lang_dict, posts_list), ...]`` 形式。"""
    from urllib.parse import quote as _q

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for lang, posts in all_posts:
        index_url = f"{SITE_BASE_URL}{lang['site_path']}"
        lines.append("  <url>")
        lines.append(f"    <loc>{html.escape(index_url)}</loc>")
        if posts:
            latest = max(p.get("lastmod") or p.get("date") or "" for p in posts)
            if latest:
                lines.append(f"    <lastmod>{latest}</lastmod>")
        lines.append("    <changefreq>daily</changefreq>")
        lines.append("    <priority>1.0</priority>")
        lines.append("  </url>")
        for p in posts:
            slug_q = _q(p["slug"], safe="-_")
            loc = f"{SITE_BASE_URL}{lang['site_path']}{slug_q}/"
            lastmod = p.get("lastmod") or p.get("date") or ""
            lines.append("  <url>")
            lines.append(f"    <loc>{html.escape(loc)}</loc>")
            if lastmod:
                lines.append(f"    <lastmod>{lastmod}</lastmod>")
            lines.append("    <priority>0.7</priority>")
            lines.append("  </url>")
    lines.append("</urlset>")
    (output / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_robots(output: Path) -> None:
    """robots.txt から sitemap.xml を案内する。"""
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_BASE_URL}sitemap.xml\n"
    )
    (output / "robots.txt").write_text(body, encoding="utf-8")


def _hreflang_links(current_lang_code: str) -> str:
    """全言語の <link rel="alternate" hreflang> を生成。
    どのページからも各言語のホームに導けるようにする。"""
    parts = []
    for l in LANGUAGES:
        href = f"{SITE_BASE_URL}{l['site_path']}"
        parts.append(
            f'<link rel="alternate" hreflang="{l["html_lang"]}" href="{html.escape(href, quote=True)}">'
        )
    # x-default はデフォルト言語 (ja) のホーム
    default_href = f"{SITE_BASE_URL}{LANGUAGES[0]['site_path']}"
    parts.append(
        f'<link rel="alternate" hreflang="x-default" href="{html.escape(default_href, quote=True)}">'
    )
    return "\n".join(parts)


def _lang_switch_html(current_lang_code: str) -> str:
    """ヘッダー右上の言語切替リンク。各言語のホームへ飛ぶ。"""
    parts = []
    for l in LANGUAGES:
        href = f"{SITE_BASE_URL}{l['site_path']}"
        cls = "active" if l["code"] == current_lang_code else ""
        parts.append(
            f'<a href="{html.escape(href, quote=True)}" '
            f'class="{cls}" hreflang="{l["html_lang"]}">{html.escape(l["label"])}</a>'
        )
    return "".join(parts)


def _site_nav_html(lang: dict) -> str:
    """ヘッダー左寄せのサイトナビゲーション。検索流入してきた読者を
    Docs / GitHub に誘導するための共通リンクをすべてのページに表示する。"""
    items = [
        ("ailia.ai", lang["ailia_url"]),
        (lang["nav_docs_label"], lang["docs_url"]),
        (lang["nav_github_label"], lang["github_url"]),
    ]
    return "".join(
        f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'
        for label, url in items
    )


# 製品名 → Docs上のサブパス。``docs_url`` は言語別 (en は /en/) なので
# 自動リンク先も言語に応じて切り替わる。長い名前から順にマッチさせるため
# リストで保持し、リンク先は build 時に組み立てる。
_PRODUCT_PATHS = [
    # ホワイトリスト方針: docs.ailia.ai に実在するページだけを対象にする。
    # 長い名前ほど先に置いてマッチを取る (例: "ailia AI Voice" は "ailia
    # Voice" より先に判定する必要がある)。
    ("ailia TFLite Runtime", "tflite/"),
    ("ailia AI Speech", "speech/"),
    ("ailia AI Voice", "voice/"),
    ("ailia Tokenizer", "tokenizer/"),
    ("ailia Tracker", "tracker/"),
    ("ailia Speech", "speech/"),
    ("ailia Voice", "voice/"),
    ("ailia LLM", "llm/"),
    ("ailia SDK", "sdk/"),
]

# CTA の subtitle を製品別に差し替えるためのコピー集。キーは Docs パス
# (sdk/ / voice/ / speech/ / ...) で、値は言語コードごとの本文。
_PRODUCT_CTA_COPY = {
    "sdk/": {
        "ja": "ailia SDK は ailia.ai が開発するクロスプラットフォーム対応の AI 推論エンジンです。Windows / macOS / Linux / iOS / Android で動作し、ailia MODELS の推論モデルがそのまま使えます。",
        "en": "ailia SDK is a cross-platform AI inference engine developed by ailia.ai. It runs on Windows / macOS / Linux / iOS / Android and supports every model published in ailia MODELS out of the box.",
    },
    "llm/": {
        "ja": "ailia LLM はエッジデバイス上で大規模言語モデル (LLM) を動作させるライブラリです。Windows / macOS / Linux / iOS / Android で動作します。",
        "en": "ailia LLM is a library that runs large language models (LLMs) on edge devices, supporting Windows / macOS / Linux / iOS / Android.",
    },
    "voice/": {
        "ja": "ailia AI Voice はクロスプラットフォーム対応の音声合成ライブラリです。Unity や C++ から呼び出してアプリにオフラインの TTS 機能を組み込めます。",
        "en": "ailia AI Voice is a cross-platform voice-synthesis library callable from Unity, C++ and more, ready for fully on-device TTS in your apps.",
    },
    "speech/": {
        "ja": "ailia AI Speech はクロスプラットフォーム対応の音声認識ライブラリです。Unity や C++ から呼び出してアプリにオフラインの音声認識機能を組み込めます。",
        "en": "ailia AI Speech is a cross-platform speech-recognition library callable from Unity, C++ and more, ready for fully on-device ASR in your apps.",
    },
    "tokenizer/": {
        "ja": "ailia Tokenizer は自然言語処理向けトークナイザライブラリです。Unity や C++ から BERT 等の前処理を呼び出せます。",
        "en": "ailia Tokenizer is an NLP tokenizer library callable from Unity, C++ and more, for BERT-style preprocessing.",
    },
    "tracker/": {
        "ja": "ailia Tracker はクロスプラットフォーム対応の物体追跡ライブラリです。Unity や C++ から呼び出してトラッキング機能をアプリに組み込めます。",
        "en": "ailia Tracker is a cross-platform object-tracking library callable from Unity, C++ and more for embedding tracking into your apps.",
    },
    "tflite/": {
        "ja": "ailia TFLite Runtime はクロスプラットフォーム対応の TensorFlow Lite ランタイムです。Windows / macOS / Linux / iOS / Android / WebAssembly で TFLite モデルを高速に実行できます。",
        "en": "ailia TFLite Runtime is a cross-platform runtime for TensorFlow Lite that runs TFLite models on Windows / macOS / Linux / iOS / Android / WebAssembly.",
    },
}


def auto_link_products(text: str, docs_url: str) -> str:
    """本文markdown中で初めて出てくる ailia 製品名にDocsページへのリンクを
    付与する。

    実装は次の手順:
      1. 既存の markdown link `[..](..)` と fenced code block を一時的に
         プレースホルダ ``\\x00n\\x00`` / ``\\x01n\\x01`` に退避。これで
         「リンクのテキスト中の製品名」「コード内の製品名」を誤マッチ
         させないようにする。
      2. 長い名前から順に ``count=1`` で置換し、初出だけリンク化。
         同じ名前を2回以上自動リンクするとくどくなるのでスキップ。
      3. プレースホルダを元に戻す。
    """
    if not text:
        return text

    # Step 1: stash markdown links and fenced code blocks
    links: list = []
    code_fences: list = []

    def _stash_link(m: re.Match) -> str:
        links.append(m.group())
        return f"\x00{len(links) - 1}\x00"

    def _stash_code(m: re.Match) -> str:
        code_fences.append(m.group())
        return f"\x01{len(code_fences) - 1}\x01"

    # Fenced code blocks are matched first to avoid eating the closing ```
    # of a code block as part of an inline backtick later.
    text = re.sub(r"```[\s\S]*?```", _stash_code, text)
    # Inline code `like this`
    text = re.sub(r"`[^`\n]+`", _stash_code, text)
    # Image references ![alt](url) - tag images BEFORE plain links so the
    # leading `!` stays glued to its alt/url
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", _stash_link, text)
    # Plain markdown links [text](url)
    text = re.sub(r"\[[^\]]+\]\([^)]+\)", _stash_link, text)

    # Step 2: substitute first occurrence per product
    seen = set()
    for name, path in _PRODUCT_PATHS:
        if name in seen:
            continue
        url = docs_url.rstrip("/") + "/" + path
        pattern = re.compile(r"(?<![A-Za-z0-9_/\.])" + re.escape(name) + r"(?![A-Za-z0-9_])")
        text, n = pattern.subn(f"[{name}]({url})", text, count=1)
        if n:
            seen.add(name)

    # Step 3: restore placeholders
    text = re.sub(
        r"\x01(\d+)\x01", lambda m: code_fences[int(m.group(1))], text
    )
    text = re.sub(r"\x00(\d+)\x00", lambda m: links[int(m.group(1))], text)
    return text


def detect_primary_product(title: str, slug: str, body: str) -> tuple:
    """記事の主題となっている ailia 製品を推定する。
    優先順位: title → slug → body の出現頻度。

    返り値: ``(display_name, docs_path)`` のタプル。判定不能時は ``(None, None)``。
    最長マッチ優先 ("ailia AI Voice" を "ailia Voice" や "ailia" より先に判定)。"""
    if not (title or slug or body):
        return (None, None)
    title_l = (title or "").lower()
    # スラグはハイフン/アンダースコア区切りなので空白に正規化
    slug_l = (slug or "").lower().replace("-", " ").replace("_", " ")
    body_l = (body or "").lower()

    # title / slug のどちらかに含まれていれば即決
    for name, path in _PRODUCT_PATHS:
        n = name.lower()
        if n in title_l or n in slug_l:
            return (name, path)

    # 本文中の最頻出を採用 (短い名前が長い名前を侵食しないよう減算する)。
    # ただし ``ailia SDK`` は ailia エコシステム全般の枠組み名で、ほぼ
    # どの記事にも頻繁に出るため、より具体的な製品 (Voice / Speech /
    # LLM / Tokenizer / Tracker / MODELS) が1回でも言及されていれば
    # そちらを優先する。SDK は他に何も検出できなかった場合のフォールバック。
    counts: list = []
    sdk_fallback: tuple = ()
    seen_spans: list = []  # (start, end) of already-counted matches
    for name, path in _PRODUCT_PATHS:
        n = name.lower()
        c = 0
        idx = 0
        while True:
            i = body_l.find(n, idx)
            if i == -1:
                break
            # 既により長い名前で計上済みの位置はスキップ
            if any(s <= i < e for s, e in seen_spans):
                idx = i + 1
                continue
            c += 1
            seen_spans.append((i, i + len(n)))
            idx = i + len(n)
        if c > 0:
            if path == "sdk/":
                if not sdk_fallback or c > sdk_fallback[0]:
                    sdk_fallback = (c, name, path)
            else:
                counts.append((c, name, path))
    if counts:
        counts.sort(key=lambda x: -x[0])
        return (counts[0][1], counts[0][2])
    if sdk_fallback:
        return (sdk_fallback[1], sdk_fallback[2])
    return (None, None)


def article_opening_banner(
    tags: list, lang: dict, product_path: str = "", product_name: str = ""
) -> str:
    """記事先頭に出すカテゴリ別CTAバナー。

    - 本文に出現する具体的な製品 (ailia AI Voice 等) が検出されていれば
      その製品のDocsへのリンクを優先する。"<Product> のドキュメント" の
      形でラベルを作って統一感を出す。
    - 製品が検出されない場合のみ、タグに応じて
      ailia-sdk → ailia SDK のドキュメント
      ailia-tutorial → インストール手順を先に見る
      他は出さない。
    """
    docs = lang["docs_url"].rstrip("/") + "/"
    if product_path and product_name:
        target_path = product_path if product_path != "sdk/" else "sdk/"
        if lang["code"] == "ja":
            label = f"{product_name} のドキュメント"
        else:
            label = f"{product_name} documentation"
        return (
            '<aside class="article-banner">'
            f'<a href="{html.escape(docs + target_path, quote=True)}">'
            f'{html.escape(label)} →</a>'
            "</aside>"
        )
    if "ailia-tutorial" in tags:
        return (
            '<aside class="article-banner">'
            f'<a href="{html.escape(docs + "sdk/", quote=True)}">'
            f'{html.escape(lang["banner_tutorial_label"])} →</a>'
            "</aside>"
        )
    if "ailia-sdk" in tags:
        return (
            '<aside class="article-banner">'
            f'<a href="{html.escape(docs + "sdk/", quote=True)}">'
            f'{html.escape(lang["banner_sdk_label"])} →</a>'
            "</aside>"
        )
    return ""


def _build_language(lang: dict, source: Path, output_root: Path, md) -> list:
    """1言語分の記事と index ページをビルドし、posts (sitemap用) を返す。"""
    out = output_root / lang["site_path"].rstrip("/") if lang["site_path"] else output_root
    out.mkdir(parents=True, exist_ok=True)

    src_images = source / "images"
    if src_images.exists():
        if (out / "images").exists():
            shutil.rmtree(out / "images")
        shutil.copytree(src_images, out / "images")

    articles_dir = source / "articles"
    if not articles_dir.exists():
        print(f"[{lang['code']}] no articles directory; skipping")
        return []
    posts = []
    for mdf in sorted(articles_dir.glob("*.md")):
        text = mdf.read_text(encoding="utf-8")
        fm, body = parse_front_matter(text)

        title = apply_substitutions(fm.get("title") or mdf.stem)
        date = fm.get("date", "")
        lastmod = fm.get("lastmod", "") or date
        author = fm.get("author", "")
        original_url = fm.get("original_url", "")
        slug = medium_slug_from_url(original_url) or mdf.stem
        from urllib.parse import quote as _q
        slug_q = _q(slug, safe='-_')
        page_url = f"{SITE_BASE_URL}{lang['site_path']}{slug_q}/"

        tags = fm.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        thumb_url = extract_thumbnail(body)
        cleaned = auto_link_products(
            rewrite_internal_links(
                inject_company_separator(
                    apply_substitutions(
                        escape_nlp_tokens(
                            normalize_card_links(clean_body(body), lang["publication"])
                        )
                    )
                ),
                lang["publication"],
            ),
            lang["docs_url"],
        )
        excerpt = extract_excerpt(cleaned)

        # 記事の主題製品 (ailia AI Voice / ailia LLM など) を検出して
        # 末尾CTAと冒頭バナーを切り替える。検出できなかった場合は
        # LANGUAGES に書いた既定値 (ailia SDK) のまま。
        product_name, product_path = detect_primary_product(title, slug, cleaned)
        if product_path:
            cta_primary_url = (
                lang["docs_url"].rstrip("/") + "/" + product_path
            )
            if lang["code"] == "ja":
                cta_title = f"{product_name} を試す"
            else:
                cta_title = f"Try {product_name}"
            cta_subtitle = (
                _PRODUCT_CTA_COPY.get(product_path, {}).get(lang["code"])
                or lang["cta_subtitle"]
            )
        else:
            cta_primary_url = lang["cta_primary_url"]
            cta_title = lang["cta_title"]
            cta_subtitle = lang["cta_subtitle"]

        body_html = md.convert(cleaned)
        md.reset()

        # OGP / JSON-LD で参照する画像は CDN 上の絶対 URL でないと SNS 等で
        # 解決されないため、本文中の miro.medium.com 画像 URL があればそちらを
        # 優先し、無ければ自サイトのアバター画像を使う。
        og_image = thumb_url if (thumb_url and thumb_url.startswith("http")) else (
            f"{SITE_BASE_URL}{lang['site_path']}images/{slug_q}/image_001.png"
            if thumb_url else PUBLICATION_LOGO
        )

        ld_json = json.dumps({
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "description": excerpt,
            "datePublished": date,
            "dateModified": lastmod,
            "author": {"@type": "Person", "name": author} if author else None,
            "image": og_image,
            "url": page_url,
            "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
            "publisher": {
                "@type": "Organization",
                "name": PUBLICATION_TITLE,
                "logo": {"@type": "ImageObject", "url": PUBLICATION_LOGO},
            },
        }, ensure_ascii=False, separators=(",", ":"))

        out_html = ARTICLE_TEMPLATE.format(
            html_lang=lang["html_lang"],
            title=html.escape(title),
            pub_title=html.escape(PUBLICATION_TITLE),
            author=html.escape(author),
            date=html.escape(date),
            lastmod=html.escape(lastmod),
            excerpt=html.escape(excerpt, quote=True),
            content=body_html,
            page_url=html.escape(page_url, quote=True),
            og_image=html.escape(og_image, quote=True),
            ld_json=ld_json,
            logo=html.escape(PUBLICATION_LOGO, quote=True),
            hreflang_links=_hreflang_links(lang["code"]),
            lang_switch=_lang_switch_html(lang["code"]),
            site_nav=_site_nav_html(lang),
            opening_banner=article_opening_banner(
                tags, lang, product_path or "", product_name or ""
            ),
            footer_back=html.escape(lang["footer_back"]),
            cta_title=html.escape(cta_title),
            cta_subtitle=html.escape(cta_subtitle),
            cta_primary_url=html.escape(cta_primary_url, quote=True),
            cta_primary_label=html.escape(lang["cta_primary_label"]),
            cta_secondary_url=html.escape(lang["contact_url"], quote=True),
            cta_secondary_label=html.escape(lang["cta_secondary_label"]),
            gtm_head=GTM_HEAD,
            gtm_body=GTM_BODY,
        )
        article_dir = out / slug
        article_dir.mkdir(parents=True, exist_ok=True)
        (article_dir / "index.html").write_text(out_html, encoding="utf-8")
        posts.append(
            {
                "title": title,
                "date": date,
                "lastmod": lastmod,
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
            label=html.escape(lang["all_label"] if tag == "" else label),
            active=" active" if tag == "" else "",
        )
        for tag, label in PRIMARY_TAGS
    )

    index_url = f"{SITE_BASE_URL}{lang['site_path']}"
    articles_label = lang["articles_label"].format(n=len(posts))
    index_html = INDEX_TEMPLATE.format(
        html_lang=lang["html_lang"],
        title=html.escape(PUBLICATION_TITLE),
        tagline=html.escape(PUBLICATION_TAGLINE),
        logo=html.escape(PUBLICATION_LOGO, quote=True),
        site_url=html.escape(index_url, quote=True),
        ailia_url=html.escape(lang["ailia_url"], quote=True),
        cards=cards,
        tag_chips=tag_chips_html,
        articles_label=html.escape(articles_label),
        search_placeholder=html.escape(lang["search_placeholder"], quote=True),
        tag_filter_aria=html.escape(lang["tag_filter_aria"], quote=True),
        empty_state=html.escape(lang["empty_state"]),
        hreflang_links=_hreflang_links(lang["code"]),
        lang_switch=_lang_switch_html(lang["code"]),
        site_nav=_site_nav_html(lang),
        gtm_head=GTM_HEAD,
        gtm_body=GTM_BODY,
    )
    (out / "index.html").write_text(index_html, encoding="utf-8")
    return posts


def build(source_root: Path, output: Path) -> int:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    md = markdown.Markdown(extensions=["fenced_code", "tables", "sane_lists"])
    all_posts: list = []  # [(lang_dict, posts_list), ...]
    for lang in LANGUAGES:
        src = source_root / lang["source_dir"]
        posts = _build_language(lang, src, output, md)
        if posts:
            all_posts.append((lang, posts))

    # 共有アセット
    (output / "style.css").write_text(CSS, encoding="utf-8")
    (output / "CNAME").write_text(SITE_HOST + "\n", encoding="utf-8")
    assets_dir = Path(__file__).parent / "assets"
    for asset_name in ("favicon.png", "logo.png"):
        src = assets_dir / asset_name
        if src.exists():
            shutil.copy(src, output / asset_name)
    _write_sitemap_combined(all_posts, output)
    _write_robots(output)

    return sum(len(posts) for _, posts in all_posts)


def main():
    parser = argparse.ArgumentParser(description="Build static site from scraped articles")
    parser.add_argument(
        "--source",
        default="medium_export",
        help="入力ディレクトリ (この下に ja/, en/ といった言語別サブディレクトリが必要)",
    )
    parser.add_argument("--output", default="_site", help="出力ディレクトリ")
    args = parser.parse_args()

    n = build(Path(args.source), Path(args.output))
    print(f"Built {n} articles to {args.output}/")


if __name__ == "__main__":
    main()
