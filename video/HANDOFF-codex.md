# 動物組織論ショート動画 量産 — Codex 引き継ぎプロンプト

あなた（Codex）のミッション：動物組織論サイトの記事を、**縦型9:16ショート動画（動物キャラ寸劇）に完全¥0で変換し続ける**。11作完成済。同じパイプラインで残り記事を量産する。

## 前提環境（Windows）
- hyperframes CLI（`npx hyperframes` ／ Node22 + FFmpeg 必須）
- ffmpeg（BGM加工・フレーム抽出）
- git（PR運用・branch `feat/video-shorts` は既存）
- 作業ルート：`C:\Users\hayat\OneDrive\デスクトップ\動物実験から学ぶマネージメント理論`

## 1作の手順（パイプライン）
1. 記事を読む：`site/src/content/articles/<slug>.md`
2. **45秒台本（5シーン）**を作る：フック → 論点3つ → オチ。§0スタンス必守（「比喩」と明示・「効果保証でない/単一原因断定でない」を最終シーンに注記）
3. プロジェクト作成：`video/<name>-short/` に `DESIGN.md`（下記トンマナ）＋ BGMコピー
   - 落ち着き：`copy video/procrastination-short/bgm-calm.wav video/<name>-short/bgm.wav`
   - ノリ：`bgm-fun.wav`
4. **index.html 土台**：`<div data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="45">` の中に5つの `.scene`（#scene1だけ表示、#scene2-5は `opacity:0`）。CSS＋テロップを書き、キャラ/グラフは `__PLACEHOLDER__` に
5. **キャラSVG**：インライン自作（資産9体は既存作からコピー）。placeholderを置換
6. **GSAP timeline**：各要素 `tl.set({隠す}, sceneStart)` → `tl.to({出す}, cue)`。シーン遷移は `scene opacity0→1` ＋ `.scene-content` を `y:60→0`。グラフは `strokeDasharray/strokeDashoffset` で描画
7. **audio要素を必ず追加**（入れ忘れ多発）：root内に `<audio id="bgm" src="bgm.wav" data-start="0" data-duration="45" data-track-index="0" data-volume="1.0"></audio>`
8. `npx hyperframes lint video/<name>-short` → `inspect`（両方 0/0 を確認）
9. `npx hyperframes render video/<name>-short --workers 1 --quality standard --output video/<name>-short/<name>.mp4`
10. ffmpegで代表フレーム抽出→目視（`ffmpeg -y -ss <t> -i <mp4> -frames:v 1 out.png`）
11. **PR反映**：`feat/video-shorts` に `index.html`+`DESIGN.md` のみ commit（生成物は除外）

## トンマナ（DESIGN.md・全作共通）
- 色：bg `#faf8f4` ／ 文字 `#1d2321` ／ アクセント深緑 `#2f6f4f` ／ 強調オレンジ `#d9893b` ／ 補助灰 `#6b7370` ／ 淡緑 `#e6efe9` ／ 線 `#e3e0d8`
- フォント：`"Noto Sans JP"`（**Serif/mono は hyperframes 非対応**） ／ 見出し900・本文600・数字は tabular-nums

## キャラ資産（既存作の index.html からSVGをコピー）
| キャラ | 特徴 | コピー元 |
|---|---|---|
| ハイエナ | 茶・だらっと眠目 | procrastination-short |
| ボノボ | 黒顔＋緑メガネ | procrastination-short |
| ハト | 白・オレンジくちばし | procrastination-short |
| オオカミ | 青灰・黄目・鋭眉 | five-types-short |
| アリ | 茶3分割＋触角 | five-types-short |
| チンパン | 肌茶・大耳・険眉 | five-types-short |
| オマキザル | 満足/怒り2表情 | unfairness-short |
| イヌ | うなだれ（無力感） | uprising-short |
| ラット | 灰＋ピンク耳・前歯 | habit-short |

## 確定した落とし穴（回避必須）
- `npx hyperframes init` は **exit5 で動かない** → index.html を手書き
- `generate_image`（higgsfield MCP）は **free plan で不可** → キャラはSVG自作で¥0
- **kokoro日本語TTSは遅すぎ**（speed2.0でも0.44秒/字）＋510トークン上限 → ナレ無し字幕版が現実解
- フォント：**Noto Serif JP / mono は非対応**（lint警告）→ Noto Sans JP のみ
- 空きメモリが少なくても `--workers 1 --quality standard` で通る
- **audio要素を土台に入れ忘れやすい**（lint の `audio_file_without_element` で気づく）
- BGM：**Pixabay CC0素材が本命**（`bgm-fun`=ノリ/`bgm-calm`=落ち着き、`procrastination-short/` にある）。自作sineは `loudnorm=I=-18:TP=-2` 必須
- **git push の前に gh account 切替**：`gh auth switch --user zumenseki` → `git push` → `gh auth switch --user nyusatsu-agent`（全session共有のグローバル状態。元はnyusatsu-agent）

## PR運用
- branch：`feat/video-shorts`（origin/main から・既存）
- commit：`index.html` + `DESIGN.md` のみ（mp4/wav/png/frames は **明示addで除外**）
- PR#1：https://github.com/zumenseki/doubutsu-soshikiron/pull/1（既存・追記していく）
- commitメッセージ末尾：`Co-Authored-By:` 行（運用に合わせる）

## 完成済11作（video/）
procrastination（先延ばし・A/B 2本）, five-types（5類型）, unfairness（不公平・カプチン猿）, fear（恐怖⇄学習グラフ）, reward（報酬・内発の谷）, bankrun（取り付け・恐怖ドミノ）, uprising（蜂起・勇気カスケード＝bankrunの鏡像）, rewilding（再野生化・0.94数字対比）, dunbar（ダンバー・崖グラフ）, habit（習慣・ラット）, status（地位・序列ストレス）

## 残りの記事（未動画化・10本）
`precedent-lockin`（前例ロックイン）, `sales-ethology`（営業）, `price-ethology`（価格）, `recruitment-ethology`（採用）, `attribution-ethology`（帰属）, `mobbing-ethology`（モビング）, `negotiation-ethology`（交渉）, `swarm-ethology`（群れ）, `hierarchy-design`（階層設計）, `controllability`（制御可能性）

## テンプレとして参照すべき既存作
- **グラフ系**（描画アニメ）：`dunbar-short`（崖）, `fear-short`（右下がり）, `reward-short`（谷）, `status-short`（右上がり勾配）
- **複数キャラ/集合**：`five-types-short`（8シーン・5体集合）
- **ドミノ/カスケード**（stagger伝播）：`bankrun-short`（恐怖!）, `uprising-short`（勇気↑）
- **小物・表情切替・投げ演出**：`unfairness-short`（オマキザル満足→怒り・キュウリ投げ）
- **数字対比・隔離枠**：`rewilding-short`

## 進め方
残り10記事を1本ずつ、上記パイプラインで動画化。最速は「近いテンプレの既存 index.html をコピーして中身を差し替え」。各作 完了したら PR#1 に追記。ユーザーへは各作のフレーム確認結果を提示してから次へ。

## 参照
- memory（このマシンのClaude用）：`doubutsu-video-pipeline.md`
- ワークスペース規約：`CLAUDE.md`（§0認識論・原始人モード・確認多め・並行セッションWIP）
