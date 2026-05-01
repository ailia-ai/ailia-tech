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

1. sitemap.xml から最新の記事URL一覧を取得 (RSSフィードでも補完)
2. ローカルに無い記事だけを新規スクレイピング
3. 差分があれば `medium_export/` を `github-actions[bot]` がコミット & push
4. push を検知して `pages.yml` がサイトを再ビルド & 再デプロイ

> 注意: GitHub Actions の `schedule` イベントはデフォルトブランチ上の
> ワークフローのみ実行される。フィーチャーブランチでは
> `workflow_dispatch` から手動でテストすること。

## 既存記事の更新

Medium上で過去記事を編集した場合、デフォルトの cron では再取得されない
(同名のmarkdownが既にあるためスキップされる)。次のいずれかで再取得する。

### GitHub Actions UI から (推奨)

Actions タブ → **Daily scrape** → **Run workflow** で以下の入力を選ぶ:

| `refresh` | 動作                                                       |
| --------- | ---------------------------------------------------------- |
| `off`     | 新着のみ取得 (cron既定動作)                                |
| `updated` | sitemap の `<lastmod>` がローカルより新しい記事を再取得    |
| `all`     | 全記事を強制再取得 (時間がかかる)                          |

`only_url` を指定すると、その記事1本だけを `--refresh` 付きで再取得できる。

### CLIから

```bash
# sitemap の lastmod が新しい記事だけ再取得
python downloader/medium_publication.py \
    --publication axinc --custom-domain tech.ailia.ai --refresh

# 全記事を強制再取得
python downloader/medium_publication.py \
    --publication axinc --custom-domain tech.ailia.ai --refresh-all

# 1記事だけ更新
python downloader/medium_publication.py \
    --publication axinc --custom-domain tech.ailia.ai \
    --only-url "https://tech.ailia.ai/<slug>" --refresh
```

スクレイパーは sitemap.xml の `<lastmod>` を各記事の YAMLフロントマターに
`lastmod: YYYY-MM-DD` として保存し、次回以降の `--refresh` で
ローカル値より新しい場合のみ再取得する。

## アナリティクス

各ページに ailia.ai と同じ Google Tag Manager (`GTM-5Q579RMM`) を埋め込んで
いる。`build_site.py` の `GTM_ID` 定数で変更可能。
