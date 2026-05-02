# ailia-tech

ailia Tech BLOG の記事ミラー。Medium の2つの publication をスクレイプし、
独自ドメイン `tech.ailia.ai` で GitHub Pages から配信する。

| 言語 | Medium 元 publication                  | 公開URL                       |
| ---- | -------------------------------------- | ----------------------------- |
| 日本語 | <https://medium.com/axinc>            | <https://tech.ailia.ai/>      |
| 英語   | <https://medium.com/axinc-ai>         | <https://tech.ailia.ai/en/>   |

## ディレクトリ構成

```
.
├── downloader/
│   ├── medium_publication.py       # Mediumスクレイパー (curl_cffi で Cloudflare 回避)
│   └── build_site.py               # 静的サイトジェネレータ (Markdown → HTML)
├── medium_export/
│   ├── ja/                         # 日本語 (axinc) スクレイプ結果
│   │   ├── urls.txt
│   │   ├── articles/               # YAMLフロントマター付きMarkdown
│   │   └── images/                 # 記事内画像
│   └── en/                         # 英語 (axinc-ai) スクレイプ結果
│       ├── urls.txt
│       ├── articles/
│       └── images/
└── .github/workflows/
    ├── pages.yml                   # GitHub Pagesビルド & デプロイ
    └── scrape.yml                  # 1日1回 ja/en 両方の新着記事を取得 → 自動コミット
```

## URLマッピング

各記事は元 Medium スラグを保持しているため、`medium.com/<publication>/<slug>`
の publication 部分を `tech.ailia.ai/[en/]` に置き換えるだけで本ミラーへ
切り替わる。記事ページには `<link rel="canonical">` で本ミラーURLを、
`<link rel="alternate" hreflang>` で各言語のホームを指す。

| 種別          | 例                                                                |
| ------------- | ----------------------------------------------------------------- |
| Medium ja    | `https://medium.com/axinc/<slug>`                                  |
| Medium en    | `https://medium.com/axinc-ai/<slug>`                               |
| ミラー ja     | `https://tech.ailia.ai/<slug>/`                                    |
| ミラー en     | `https://tech.ailia.ai/en/<slug>/`                                 |

## 記事をスクレイピング

```bash
pip install curl-cffi beautifulsoup4 markdownify

# 日本語
python downloader/medium_publication.py --publication axinc    --output medium_export/ja
# 英語
python downloader/medium_publication.py --publication axinc-ai --output medium_export/en
```

URL収集は (1) Apollo state from `medium.com/<publication>/`、(2) RSSフィード、
(3) 既存記事のクロスリファレンス の3経路。独自ドメインの sitemap は
ミラー側 (= 自分自身) を指すようになったため使用しない。

## サイトをローカルでビルド

```bash
pip install markdown
python downloader/build_site.py --source medium_export --output _site
# _site/index.html (ja)、_site/en/index.html (en)
```

`build_site.py` は `medium_export/<lang>/` を順番に読み、`_site/[<lang_path>]`
に出力する。各記事のリンクには相対パス (`../<slug>/`) を使うので、ホスト名
変更時もリンク切れしない。

## GitHub Pagesでホスティング

1. リポジトリの **Settings → Pages** を開く
2. **Build and deployment → Source** を **GitHub Actions** に設定
3. **Settings → Pages → Custom domain** に `tech.ailia.ai` を設定
4. ブランチへの push、または日次cron (`scrape.yml`) からの自動コミットで
   `pages.yml` ワークフローが起動し、`_site/` がデプロイされる
5. 手動デプロイは Actions タブから "Deploy GitHub Pages" を選択して
   **Run workflow** でも可能

`build_site.py` はビルド時に `_site/CNAME` (= `tech.ailia.ai`) を出力する
ので、Actions デプロイでも独自ドメインが維持される。

## 自動更新 (1日1回)

`.github/workflows/scrape.yml` が毎日 01:00 UTC (10:00 JST) に実行される。
ja と en の両方が同一ジョブで処理される (`run_one ja axinc` →
`run_one en axinc-ai`)。

1. Medium publication ホームの Apollo state から最新 ~99 記事の ID を取得
2. RSSフィード (直近10件) でも補完
3. 既存記事の本文中リンクから未知URLを発見 (cross-reference)
4. **新着記事**: ローカルに無いものを新規スクレイピング
5. **更新された記事**: Apollo の `latestPublishedAt` がローカル保存値より
   新しい記事は本文・画像を再取得して上書き
6. 差分があれば `medium_export/` を `github-actions[bot]` がコミット & push
7. push を検知して `pages.yml` がサイトを再ビルド & 再デプロイ

> 注意: GitHub Actions の `schedule` イベントはデフォルトブランチ上の
> ワークフローのみ実行される。フィーチャーブランチでは
> `workflow_dispatch` から手動でテストすること。

## 既存記事の更新

Medium上で過去記事を編集した場合、デフォルトの cron では再取得されない
(同名のmarkdownが既にあるためスキップされる)。次のいずれかで再取得する。

### GitHub Actions UI から (推奨)

Actions タブ → **Daily scrape** → **Run workflow** で以下の入力を選ぶ:

| 入力       | 動作                                                                  |
| ---------- | --------------------------------------------------------------------- |
| `refresh`  | `off` / `updated` (Apollo の lastmod 比較) / `all` (強制全件再取得)    |
| `only_url` | 1記事だけ `--refresh` 付きで再取得 (medium.com の URL を指定)          |
| `lang`     | 空 (両方) / `ja` / `en`                                                |

### CLIから

```bash
# 更新された記事だけ再取得
python downloader/medium_publication.py --publication axinc    --output medium_export/ja --refresh
python downloader/medium_publication.py --publication axinc-ai --output medium_export/en --refresh

# 全記事を強制再取得
python downloader/medium_publication.py --publication axinc --output medium_export/ja --refresh-all

# 1記事だけ更新
python downloader/medium_publication.py --publication axinc --output medium_export/ja \
    --only-url "https://medium.com/axinc/<slug>" --refresh
```

各記事の YAMLフロントマターに `lastmod: YYYY-MM-DD` として保存され、次回
以降の `--refresh` でローカル値より新しい場合のみ再取得される。

## SEO

- 各ページに `<meta name="robots" content="index, follow,
  max-image-preview:large, max-snippet:-1">`
- 自己参照 canonical (記事ごと、index ごと)
- `hreflang` (ja / en / x-default)
- Open Graph + Twitter Card (記事は `summary_large_image`、index は `summary`)
- JSON-LD (`BlogPosting`)
- 全言語をまとめた `sitemap.xml` を `tech.ailia.ai/sitemap.xml` に出力
- `robots.txt` から sitemap を案内

## アナリティクス

各ページに ailia.ai と同じ Google Tag Manager (`GTM-5Q579RMM`) を埋め込んで
いる。`build_site.py` の `GTM_ID` 定数で変更可能。
