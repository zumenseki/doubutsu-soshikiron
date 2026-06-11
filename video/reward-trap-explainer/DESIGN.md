# DESIGN — 報酬の罠（横型16:9・YouTube解説・約3分・TTSナレ付き 第2作）

横型解説系統の第2作。1作目 five-types-explainer と同一トンマナ・同一パイプライン（Edge TTSナレ＋SRT同期字幕）。テーマは「報酬を足すほど裏目に出る」逆説。

## Format
- 1920×1080（16:9）・約175秒（2分55秒）・30fps・5シーン
- 音声：Edge TTS `ja-JP-NanamiNeural --rate=+10%`（narration/ch1-5.mp3・track1直列）＋BGM小音量（bgm.mp3=bgm-calmループ・volume0.22・track0）
- ⚠️音声は**mp3直使用**（wav化すると page load 10s timeout で inspect/render 不能）
- 字幕：edge-tts SRT（文単位）を章オフセットでシフトした GROUPS 配列（32cue）・一度に1グループ・hard kill

## シーン構成
| S | 内容 | 主資産 |
|---|---|---|
| S1 | フック「もっと払えば動く、がなぜ裏目に」＋比喩でなく機構 | ハイエナ |
| S2 | 報酬が"何も教えない"＝非随伴・予測昇給は誤差ゼロ | コイン×3＋✕・対比カード |
| S3 | ノルマ＋恐怖→不正（Wells Fargo・ハイエナ型） | ハイエナ＋WFカード |
| S4 | 内発の谷グラフ（デシのメタ分析・内発が高い役割ほど金銭で動機が谷へ） | curve描画（reward-short流用） |
| S5 | だから＝情報的(承認/裁量/意味) vs 統制的(ノルマ連動の金銭) 対比＋§0＋CTA | 2カラム対比 |

## Colors / Typography
- `#faf8f4` 背景 / `#1d2321` 文字 / `#2f6f4f` 緑(内発を壊さない側) / `#d9893b` オレンジ(報酬・危険側・本作の主アクセント) / `#e6efe9` 淡緑 / `#6b7370` 補助 / `#e3e0d8` 罫線
- `"Noto Sans JP", sans-serif`（Serif不可）・見出し900 / 本文700 / 字幕700・40px

## Motion / §0
- シーン遷移＝クロスフェード＋content y:60→0。entrance のみ（最終シーン以外 exit 禁止）・SRT実測cueに同期
- 谷グラフ＝`strokeDasharray/Dashoffset` で描画アニメ（ナレ「シミュレートすると…谷に落ち」113.2s に同期）
- §0：reward-trap は Layer1正本寄り（比喩でなく機構）だが、**「式で機構を表したもので特定企業の内部を断定しない」**を末尾注記で必守。Wells Fargo は「公開事例に型が見える挿絵」の位置づけ

## What NOT to Do
- 原色べた塗り・ネオン／暗黒背景／明朝体
- Wells Fargo を「断定的な企業分析」に見せる（§0違反）／効果保証
- 字幕ゾーン（下部185px）にコンテンツを進入させる
