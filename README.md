# ailia-tech

[ailia Tech BLOG](https://medium.com/axinc) (Medium publication `axinc`,
カスタムドメイン `tech.ailia.ai`) の全記事をスクレイピングし、
GitHub Pages でホスティングするためのリポジトリ。

## ディレクトリ構成

```
.
├── downloader/
│   ├── medium_publication.py   # スクレイパー (curl_cffi + sitemap.xml)
│   └── build_site.py           # 静的サイトジェネレータ (Markdown → HTML)
├── medium_export/
│   ├── urls.txt                # スクレイプ対象URL一覧
│   ├── articles/               # YAMLフロントマター付きMarkdown (224件)
│   └── images/                 # 記事内画像 (約1,400件, 約500MB)
└── .github/workflows/pages.yml # GitHub Pagesデプロイワークフロー
```

## 記事をスクレイピング

```bash
pip install curl-cffi beautifulsoup4 markdownify
python downloader/medium_publication.py \
    --publication axinc \
    --custom-domain tech.ailia.ai
```

## サイトをローカルでビルド

```bash
pip install markdown
python downloader/build_site.py --source medium_export --output _site
# _site/index.html をブラウザで開く
```

## GitHub Pagesでホスティング

1. リポジトリの **Settings → Pages** を開く
2. **Build and deployment → Source** を **GitHub Actions** に設定
3. `main` ブランチまたは `claude/medium-article-scraper-mPxdV` ブランチに
   push するとワークフロー (`.github/workflows/pages.yml`) が実行され、
   `_site/` がデプロイされる
4. 手動デプロイは Actions タブから "Deploy GitHub Pages" を選択して
   **Run workflow** でも可能

デプロイURL: `https://ailia-ai.github.io/ailia-tech/`
