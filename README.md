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
│   ├── update.sh                   # ローカル手動更新スクリプト (ja + en)
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
    └── pages.yml                   # GitHub Pagesビルド & デプロイ
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
4. ブランチへの push で `pages.yml` ワークフローが起動し、`_site/` が
   デプロイされる
5. 手動デプロイは Actions タブから "Deploy GitHub Pages" を選択して
   **Run workflow** でも可能

`build_site.py` はビルド時に `_site/CNAME` (= `tech.ailia.ai`) を出力する
ので、Actions デプロイでも独自ドメインが維持される。

## 記事の更新 (ローカルPCで手動実行)

GitHub Actions からのスクレイピングは Cloudflare に弾かれて動作しなかったため、
自動監視・自動更新 (日次cron) は廃止した。記事の更新はローカルPCから手動で行う。

```bash
pip install curl-cffi beautifulsoup4 markdownify

# ja + en の新着記事を取得し、Medium で編集された記事も再取得
downloader/update.sh

# 言語を絞る / フラグを変える
downloader/update.sh ja
downloader/update.sh en --refresh-all
```

`update.sh` は各言語について次を行う。

1. Medium publication ホームの Apollo state から最新 ~99 記事の ID を取得
2. RSSフィード (直近10件) でも補完
3. 既存記事の本文中リンクから未知URLを発見 (cross-reference)
4. **新着記事**: ローカルに無いものを新規スクレイピング
5. **更新された記事**: Apollo の `latestPublishedAt` がローカル保存値より
   新しい記事は本文・画像を再取得して上書き (`--refresh`)

独自ドメインの sitemap はミラー側 (= 自分自身) を指すようになったため使用しない。

> 注意:
> - `medium.com/<publication>/` (Apollo state) はローカルからでも HTTP 403 に
>   なることがある (`[warn] fetch failed` と表示される)。その場合は Medium 上で
>   編集された記事を検出できず、すべて up-to-date 扱いになる。編集した記事が
>   分かっている場合は下記の `--only-url` で個別に再取得する。
> - 公開直後の記事は RSS や publication ホームにまだ載らず、新着として
>   見つからないことがある。その場合も `--only-url` で URL を指定して取得する。

取得後に差分を確認して commit & push すると、`pages.yml` がサイトを
再ビルド & 再デプロイする。

```bash
git add medium_export/
git commit -m "Update articles"
git push
```

### スクリプトを使わず直接実行する場合

```bash
# 更新された記事だけ再取得
python downloader/medium_publication.py --publication axinc    --output medium_export/ja --refresh
python downloader/medium_publication.py --publication axinc-ai --output medium_export/en --refresh

# 全記事を強制再取得
python downloader/medium_publication.py --publication axinc --output medium_export/ja --refresh-all

# 1記事だけ取得 / 強制再取得 (Apollo が 403 のときは --refresh-all を使う)
python downloader/medium_publication.py --publication axinc --output medium_export/ja \
    --only-url "https://medium.com/axinc/<slug>" --refresh-all
```

各記事の YAMLフロントマターに `lastmod: YYYY-MM-DD` として保存され、次回
以降の `--refresh` でローカル値より新しい場合のみ再取得される。

フロントマターの `published: YYYY-MM-DDTHH:MM:SSZ` は Medium の投稿時刻 (UTC)。
記事一覧は `date` の新しい順で、同じ日の記事は `published` の新しい順に並ぶ。

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
