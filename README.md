# ailia-tech

[ailia Tech BLOG](https://medium.com/axinc) (Medium publication `axinc`,
カスタムドメイン `tech.ailia.ai`) の全記事をスクレイピングし、
GitHub Pages でホスティングするためのリポジトリ。

公開URL: <https://ailia-ai.github.io/ailia-tech/>

## ディレクトリ構成

```
.
├── downloader/
│   ├── medium_publication.py       # スクレイパー (curl_cffi + sitemap.xml)
│   └── build_site.py               # 静的サイトジェネレータ (Markdown → HTML)
├── medium_export/
│   ├── urls.txt                    # スクレイプ対象URL一覧
│   ├── articles/                   # YAMLフロントマター付きMarkdown
│   └── images/                     # 記事内画像
└── .github/workflows/
    ├── pages.yml                   # GitHub Pagesビルド & デプロイ
    └── scrape.yml                  # 1日1回新着記事を取得 → 自動コミット
```

## URLマッピング

公開サイトのURLは Medium 側の slug を保持しているため、ホスト名部分の
置換だけで相互変換できる。

| 種別          | URL例                                                                         |
| ------------- | ----------------------------------------------------------------------------- |
| Medium        | `https://medium.com/axinc/<slug>`                                             |
| カスタムドメイン | `https://tech.ailia.ai/<slug>`                                                |
| 本ミラー       | `https://ailia-ai.github.io/ailia-tech/<slug>/`                              |

例えば `medium.com/axinc/` を `ailia-ai.github.io/ailia-tech/` に置き換える
だけで対応する記事へリンクが切り替わる。各記事ページには
`<link rel="canonical">` で元記事URLを指している。

## 記事をスクレイピング

```bash
pip install curl-cffi beautifulsoup4 markdownify
python downloader/medium_publication.py \
    --publication axinc \
    --custom-domain tech.ailia.ai
```

スクレイパーは毎回 `tech.ailia.ai/sitemap/sitemap.xml` を取得し、
新着URLを検出する。既にダウンロード済みの記事はスキップされる。

## サイトをローカルでビルド

```bash
pip install markdown
python downloader/build_site.py --source medium_export --output _site
# _site/index.html をブラウザで開く
```

## GitHub Pagesでホスティング

1. リポジトリの **Settings → Pages** を開く
2. **Build and deployment → Source** を **GitHub Actions** に設定
3. ブランチへの push、または日次cron (`scrape.yml`) からの自動コミットで
   `pages.yml` ワークフローが起動し、`_site/` がデプロイされる
4. 手動デプロイは Actions タブから "Deploy GitHub Pages" を選択して
   **Run workflow** でも可能

## 自動更新 (1日1回)

`.github/workflows/scrape.yml` が毎日 01:00 UTC (10:00 JST) に実行される。

1. sitemap.xml から最新の記事URL一覧を取得
2. ローカルに無い記事だけを新規スクレイピング
3. 差分があれば `medium_export/` を `github-actions[bot]` がコミット & push
4. push を検知して `pages.yml` がサイトを再ビルド & 再デプロイ

`workflow_dispatch` で手動実行も可。

> 注意: GitHub Actions の `schedule` イベントはデフォルトブランチ上の
> ワークフローのみ実行される。フィーチャーブランチでは
> `workflow_dispatch` から手動でテストすること。

## アナリティクス

各ページに ailia.ai と同じ Google Tag Manager (`GTM-5Q579RMM`) を埋め込んで
いる。`build_site.py` の `GTM_ID` 定数で変更可能。
