# 動物組織論 横型YouTube解説動画 量産 — 引継ぎプロンプト

あなた（次セッション/Codex）のミッション：動物組織論サイトの記事を、**横型16:9・約3分・TTSナレ＋同期字幕付きの「解説動画」に量産し続ける**。3作完成済（5類型／報酬の罠／恐怖⇄学習）。同じ確立済みパイプラインで残り記事を量産する。

> これは縦型9:16ショート（`HANDOFF-codex.md`／45秒・無音字幕の寸劇）とは**別系統**。本書は横型・長尺・ナレ付きの解説動画用。chat履歴なしで単独実行できる完全プロンプト。

## 前提環境（Windows）
- **hyperframes CLI**（`npx hyperframes` ／ Node22 + FFmpeg 必須）
- **edge-tts**（`pip install edge-tts` 済／日本語ナレ。kokoro=hyperframes標準ttsは日本語が遅すぎて却下済）
- **ffmpeg / ffprobe**（BGM加工・尺測定・フレーム抽出）
- **python**（`make_groups.py`＝SRT→字幕配列）
- **git**（branch `feat/video-shorts` は既存・PR#1系譜）
- 作業ルート：`C:\Users\hayat\OneDrive\デスクトップ\動物実験から学ぶマネージメント理論`

## 1作の手順（確立済みパイプライン）
1. **記事を読む**：`site/src/content/articles/<slug>.md`
2. **台本5章**を `video/<name>-explainer/narration/ch1-5.txt` に書く
   - 構成＝CH1フック → CH2-4論点3つ → CH5まとめ＋§0注＋CTA
   - 1章 ≈ 25〜40秒（日本語 約5.2字/秒 @ rate+10%）。計 **約1000字 → 約2分40秒〜3分半**
   - §0必守：「比喩/レンズ」明示・効果保証しない・特定企業/単一原因を断定しない（末尾注記）
3. **TTS生成**：各章
   `edge-tts --voice ja-JP-NanamiNeural --rate=+10% --file chN.txt --write-media chN.mp3 --write-subtitles chN.srt`
4. **実測**：`ffprobe -v error -show_entries format=duration -of csv=p=0 chN.mp3` で各章秒数を取得
   → 章開始オフセットを決める（**章間に約2.5秒の「間」**）。総尺 data-duration を確定
5. **字幕生成**：`narration/make_groups.py`（既存作のをコピーし `OFFSETS` だけ書換）を実行
   → `var GROUPS = [{s,e,t},...]`（SRT実測の文単位cue）を得る → index.html に貼る
6. **BGM**：`ffmpeg -y -stream_loop -1 -i video/procrastination-short/bgm-calm.wav -t <総尺> -af "volume=0.22,afade=t=in:st=0:d=1.5,afade=t=out:st=<総尺-3>:d=3" -codec:a libmp3lame -b:a 160k video/<name>-explainer/bgm.mp3`
7. **index.html**（1920×1080）：既存 explainer をコピーして中身差替が最速
   - `.scene` opacity切替＋`.scene-content` y:60→0、`xfade(s,t)` 関数でクロスフェード
   - シーン5枚前後。各要素を `tl.to(..., <SRT実測cue秒>)` でナレに同期（entrance のみ・最終シーン以外 exit 禁止）
   - 字幕：下部 `#caps`・GROUPS をループ生成・一度に1グループ・**out後 `tl.set(el,{visibility:"hidden"},g.e)` で hard kill**
   - audio：`track0`=BGM（data-volume 1.0・mp3側で-0.22済）／`track1`=章別ナレmp3を `data-start`=実測オフセットで直列
8. **キャラSVG・グラフ流用**：既存 short / explainer の index.html からコピー（下表）
9. **検証**：`npx hyperframes lint video/<name>-explainer` → `inspect`（両方）→ `render --workers 1 --quality standard --output video/<name>-explainer/<name>-explainer.mp4`
10. **目視**：`ffmpeg -y -ss <t> -i <mp4> -frames:v 1 out.png` で各シーン1枚抽出→確認。`ffmpeg -i <mp4> -af volumedetect -f null NUL` で mean -18〜-20dB 確認
11. **commit**：`index.html` + `DESIGN.md` + `narration/*.txt` + `narration/make_groups.py` のみ（**mp4/mp3/srt/frames/bgm は除外**）→ push

## トンマナ（DESIGN.md・全作共通）
- 色：bg `#faf8f4` ／ 文字 `#1d2321` ／ 深緑 `#2f6f4f`（学習・安全・ポジ側）／ オレンジ `#d9893b`（恐怖・報酬・危険側＝強調）／ 淡緑 `#e6efe9` ／ 補助 `#6b7370` ／ 罫線 `#e3e0d8`
- フォント：`"Noto Sans JP"`（**Serif/mono は hyperframes 非対応**）／ 見出し900・本文700・字幕700/40px・数字 tabular-nums
- `.scene-content` は `padding: 70px 120px 185px`（**下185pxは字幕ゾーン予約＝コンテンツ進入禁止**）

## キャラ/グラフ資産（既存からコピー）
| 資産 | コピー元 |
|---|---|
| 動物キャラ5体（オオカミ/アリ/チンパン/ボノボ/ハイエナ） | `five-types-short` or `five-types-explainer` |
| 内発の谷グラフ（curveV・下に凸） | `reward-short` / `reward-trap-explainer` |
| 右下がりグラフ（curveDown）＋3劣化アイコン | `fear-short` / `fear-explainer` |
| コイン¥・✕印 | `reward-short` |
| 情報フロー断絶（box→壁✕→box） | `fear-explainer` S2 |
| Edmondson 2×2マトリクス | `fear-explainer` S4 |
| 2カラム対比（good緑/bad白） | `reward-trap-explainer` S5 / `fear-explainer` S5 |

## 確定した落とし穴（回避必須）
- **音声は mp3 直使用**：wav化すると章5本+BGMで計70MB超 → headless page load が **10秒timeoutで inspect/render が死ぬ**（実害発生→mp3で解決。BGMも `-codec:a libmp3lame -b:a 160k`）
- **kokoro日本語TTSは遅すぎ**（0.44秒/字）＋510トークン上限 → **edge-tts が解**（自然・速い・¥0・APIキー不要）
- **Noto Serif/mono は hyperframes 非対応** → Noto Sans JP のみ
- lint の `overlapping_gsap_tweens "__unresolved__"` 警告は **関数(xfade等)経由セレクタの誤検知** → `inspect` が 0 issue なら無視可（0 error なら render 可）
- **字幕の1文が長いと2行折返し**（はみ出しはしないが見栄え）→ 台本側で句点を増やし1cueを短く割ると綺麗（特にデシ/グーグル等の長い説明文）
- **push 前に gh account 切替**：`gh auth switch -h github.com -u zumenseki` → `git push origin feat/video-shorts` → `gh auth switch -h github.com -u nyusatsu-agent`（全session共有global・元はnyusatsu-agent）。push前に `git log origin/feat/video-shorts..HEAD --oneline` で対象commit確認
- `npx hyperframes init` は exit5 で動かない → index.html は既存コピーで手書き

## 完成済み3作（video/）
| 作 | ディレクトリ | 尺 | 構成の見どころ |
|---|---|---|---|
| 5類型 | `five-types-explainer` | 209s/9シーン | 4ダイヤルゲージ・5類型カード段階表示・階層図 |
| 報酬の罠 | `reward-trap-explainer` | 175s/5シーン | 非随伴コイン・Wells Fargo・内発の谷グラフ描画・情報的vs統制的2カラム |
| 恐怖⇄学習 | `fear-explainer` | 160s/5シーン | 情報フロー断絶・右下がりグラフ+3劣化・Edmondson 2×2・効く/効かない2分 |

## 残りの記事候補（横型解説向き・優先度順）
- **理論核**：`controllability`（統制可能性/学習性無力感）／`unfairness-cost`（公平・カプチン猿）／`crowding-out`（動機の締め出し・罰金が価格に）／`precedent-lockin`（前例固執）
- **応用（対の構造が映える）**：`bank-run`（恐怖伝播）／`uprising`（蜂起・bank-runの鏡像）
- **実務how-to**：`sales-ethology`／`negotiation-ethology`（タカ-ハトESS）／`price-ethology`（参照点）／`recruitment-ethology`（ハンディキャップ原理）／`procrastination-ethology`（双曲割引）／`status-ethology`（順位×ストレス）
- ※既存**縦型short 21本は元台本（5シーン）がある**＝横型化の核として流用しやすい（対応表は `SHORTS-youtube-metadata.md` 冒頭にあり）

## 既存縦型ショート21本のYouTube Shorts投稿メタ
- `video/SHORTS-youtube-metadata.md`：21本のタイトル(40字・#Shorts)/説明文/タグ。コピペでShorts投稿可。
- ⚠️ 記事リンクは現状 GitHub Pages（site）向き。**note一本化で site 公開停止したらリンク差替要**。

## YouTube運用（投稿は人間が手動）
- アップロードは**人間**（自動化しない）。各動画の概要欄に①チャプター ②記事リンク（site or note）③noteメンバーシップ導線 ④§0注 を入れる。
- サムネ：`thumbnail.html` を作り `chrome --headless --screenshot` で1280×720 PNG化（`five-types-explainer/thumbnail.html` が雛形）。
- タイトル/概要欄/タグの雛形は5類型作成時にチャットで提示済（同型で各作に展開）。

## git / PR
- branch：`feat/video-shorts`（PR#1：https://github.com/zumenseki/doubutsu-soshikiron/pull/1 ・追記していく）
- commit：ソースのみ（`index.html`/`DESIGN.md`/`narration/*.txt`/`make_groups.py`）。生成物（mp4/mp3/srt/bgm/frames）は明示addで除外
- commitメッセージ末尾：`Co-Authored-By:` 行

## 参照
- memory（このマシンのClaude用）：`doubutsu-video-pipeline.md`（横型系統の節）
- 既存作のソース：`five-types-explainer/` `reward-trap-explainer/` `fear-explainer/`（index.html・DESIGN.md・narration/）
- ワークスペース規約：`CLAUDE.md`（§0認識論・原始人モード・確認多め・並行セッションWIP）
