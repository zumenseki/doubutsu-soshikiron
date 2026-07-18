# YouTube 結線手順（2026-07-14 claude-mirror 監査発）

在庫: **explainer(横型) 22本 + short(縦型) 21本 = 43本・約370MB。公開先ゼロ**（6/22開設予定のまま宙吊り→今週中に「開設」か「凍結」のどちらかを付ける。宙吊り禁止）。

## 開設（親方の手・10分）
1. YouTube（運用Googleアカウント）→ 設定 → チャンネル作成（名前案:「動物に学ぶ組織論」等）
2. studio.youtube.com → 電話認証を済ませる（15分超動画・カスタムサムネイル解禁）
3. チャンネル説明に note マガジンURL + 無料診断URLを記載（回遊導線）

## アップロード順（推奨）
- 週2本ペース: 同テーマの explainer + short ペア（例: dunbar-explainer + dunbar-short）
- 初週: **five-types**（診断アプリと直結）→ dunbar → habit（検索需要順）
- 各動画の説明欄: 対応するnote記事URL + 無料診断URL（CVファネル）

## メタデータ
- タイトル/説明/タグの一括生成は、本フォルダでClaudeセッションを開き「video/ 43本分のYouTubeメタデータを note-drafts の対応記事から生成」と依頼すれば一括で出る
- アップロード自体は YouTube Studio（Google認証=親方の手）。YouTube Data API 化は quota 申請が要るため、初期は手動アップの方が速い

## 判定
roadmap.md 準拠: 3週間試験→再生数・note流入の数字で継続/凍結を決める。「またやろうかと」は禁止。
