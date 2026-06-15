# note 埋め込み診断 — 手順（CodePen × note）

診断を note 記事内に埋め込む（**無料診断 → 結果 → 会員型記事へ送客**）。本体は [shindan-codepen.html](shindan-codepen.html)（単一HTML・依存ゼロ・note URL送客・正本=site/src の Astro 版を1ファイル移植）。検証済（3対象・配合バー・note送客リンク・コンソール0err）。

## 前提（重要）
- note の CodePen 埋め込みは **PC・スマホのブラウザのみ**表示（**note アプリでは出ない**・公式仕様）→ **ハイブリッド**（埋め込み＋フォールバックリンク）で全読者をカバー。
- 診断はクライアント完結＝**データ送信なし**（回答は外部に送られない）。

## 手順
### 1. CodePen に Pen を作る
1. CodePen（無料アカウント）で **新規 Pen**。
2. `shindan-codepen.html` を **3ペインに分割して貼る**（確実）：
   - **CSS ペイン** ← `<style> … </style>` の中身
   - **JS ペイン** ← `<script> … </script>` の中身
   - **HTML ペイン** ← `<body>` 内の `<div class="wrap"> … </div>`（＝script以外の本文）
   - （丸ごとHTMLペインに貼ってもCodePenは大抵描画するが、崩れたら上記分割）
3. Pen を **Public（公開）** で保存。**Pen URL**（例 `https://codepen.io/＜あなた＞/pen/xxxxxx`）と **フルページURL**（`.../full/xxxxxx`）を控える。

### 2. note 記事に埋め込む（無料記事）
1. note で**新規記事**（無料公開）。導入文（「60秒で、あなた／組織／家庭がどの動物の設計に寄っているかを見る」等）。
2. 本文に **Pen URL を貼る**（自動で埋め込み＝ブラウザ読者は記事内で動く）。
3. その直下に **フォールバックリンク**：「うまく表示されない方（noteアプリ等）はこちら → 診断を開く」に **フルページURL** を貼る。
4. 末尾に「結果に出た型を深掘りするなら → 会員マガジン」等の導線。

### 3. 送客（会員深掘り）＝結果カルテの「noteの記事で読む」
結果ごとに note 型記事へリンク（`NOTE_LINKS` で定義済）：
- **family**：ハブ記事 `na510696cbe44`（**公開済**）→今すぐ有効。
- **org / self（5動物の型記事）**：ookami=wolf `ne12a84a42c15` / ari・kochoku=ant `n7a7dffb6cd19` / chimp `n106fde59a835` / bonobo `n23e38d55ef9d` / hyena `n97da4f76ffcf` / 混成=five-types `n6d98d24d19f3`。
  - 🔴 **これらは現在「下書き（未公開）」＝リンクは404**。note で**公開すると即有効化**（URLのIDは下書き→公開で不変＝種まき済）。
  - → org/self を綺麗に繋ぐには **5動物の型記事を公開する一手間**が必要（family は不要）。

## 位置づけ
- 診断＝**無料**（広く入口）→ 結果 → 型記事（**会員深掘り**）。membership funnel。

## メンテ
- 正本は `site/src`（Astro 版 questions.js / diagnosis.js / types.js）。文言・採点を変えたら**この1ファイルも同期**（将来はビルドで生成も可）。
- note記事URL（`NOTE_LINKS`）は公開後にIDを確認し、必要なら差し替え。

## オプション：フォールバックをサイトでホスト
CodePen フルページURLの代わりに、この1ファイルを `site/public/embed/shindan.html` に置けば `https://zumenseki.github.io/doubutsu-soshikiron/embed/shindan.html` で配信できる（site のデプロイに乗る・note記事のフォールバックリンク先に使える）。要望あれば対応。
