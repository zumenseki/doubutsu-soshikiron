# DESIGN — 組織の5類型（横型16:9・YouTube解説・約3分半・TTSナレ付き 第1作）

縦型ショート（five-types-short）と同一トンマナの横型展開。ナレーション主役・字幕常時・図解で支える解説動画。

## Style Prompt
深緑×クリームの自然なパレット。フラットSVGの動物キャラ5体（オオカミ／アリ／チンパン／ボノボ／ハイエナ）と情報カードの2カラム構成。背景クリーム、文字は濃い緑墨、アクセント森林の深緑、強調は土オレンジ。ゴシック太字。装飾最小・余白広め。下部はナレ同期字幕の予約ゾーン。

## Format
- 1920×1080（16:9）・約209秒・30fps
- 音声：Edge TTS `ja-JP-NanamiNeural --rate=+10%`（narration/ch1-5.mp3・track1直列）＋BGM小音量（bgm.mp3=bgm-calmループ・volume0.22・track0）
- ⚠️ 音声は**mp3のまま使う**（wav化すると計70MB超→ inspect/render の page load が10秒timeoutで死ぬ。実測で確認済）
- 字幕：edge-tts SRT（文単位）を章オフセットでシフトした GROUPS 配列・一度に1グループ・hard kill

## Colors
- `#faf8f4` 背景 / `#1d2321` 文字 / `#2f6f4f` アクセント(深緑) / `#e6efe9` 淡緑 / `#6b7370` 補助 / `#e3e0d8` 罫線 / `#d9893b` 強調(要所のみ)

## Typography
- `"Noto Sans JP", sans-serif`（Serif/mono は hyperframes 非対応）
- 見出し900 / カード見出し800 / 本文600 / 字幕700・44px / tabular-nums

## Layout
- `.scene-content` padding下側を厚く（字幕ゾーン170px予約）
- 型シーン＝左:キャラ大＋型名＋主軸chip ／ 右:強み・弱み・生息域の3カード（ナレcueでentrance）
- 階層図シーン＝現場/管理/経営/文化 × ミニキャラ4行

## Motion
- シーン遷移＝クロスフェード＋content y:60→0（縦型と同型）。exit禁止（最終シーンのみ可）
- entrance: `power3.out`/`back.out`/`expo.out` 混在・ナレSRT実測時刻にcue同期
- 字幕: fade+y 0.18s in / 0.12s out / `tl.set` hard kill

## What NOT to Do
- 原色べた塗り・ネオン／暗黒背景／明朝体
- §0違反（「うちは○○型」と断定・効果保証）→「比喩・レンズ」明示、純血種は存在しないスタンス維持
- 字幕とコンテンツの重なり（下部170pxはコンテンツ進入禁止）
