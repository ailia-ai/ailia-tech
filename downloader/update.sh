#!/usr/bin/env bash
# ローカルPCから Medium の新着・更新記事を取得する手動更新スクリプト。
# (GitHub Actions からは Cloudflare に弾かれるため、自動更新は廃止した)
#
# 使い方:
#   downloader/update.sh            # ja + en、Medium で更新された記事も再取得
#   downloader/update.sh ja         # 日本語だけ
#   downloader/update.sh en --refresh-all   # 英語を全件強制再取得
#
# 取得後は差分を確認して main に commit & push すれば、pages.yml が
# サイトを再ビルド & デプロイする。
set -euo pipefail

cd "$(dirname "$0")/.."

target_lang=""
if [[ "${1:-}" == "ja" || "${1:-}" == "en" ]]; then
  target_lang="$1"
  shift
fi

# 追加フラグ未指定なら --refresh (Apollo の latestPublishedAt と比較)
flags=("$@")
if [[ ${#flags[@]} -eq 0 ]]; then
  flags=(--refresh)
fi

run_one() {
  local lang="$1"
  local pub="$2"
  echo "=== scrape ${lang} (${pub}) ==="
  # urls.txt が残っていると前回の収集結果が再利用されるので毎回削除
  rm -f "medium_export/${lang}/urls.txt"
  python downloader/medium_publication.py \
    --publication "${pub}" \
    --output "medium_export/${lang}" \
    "${flags[@]}"
}

if [[ -z "${target_lang}" || "${target_lang}" == "ja" ]]; then
  run_one ja axinc
fi
if [[ -z "${target_lang}" || "${target_lang}" == "en" ]]; then
  run_one en axinc-ai
fi

echo
git status --short medium_export/
