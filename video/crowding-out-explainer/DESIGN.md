# DESIGN — 動機の締め出し／罰金が価格に（横型16:9・YouTube解説・約3.4分・TTSナレ付き 第5作）

横型解説系統の第5作。報酬3部作の完結編（[報酬の罠]reward-trap-explainer ／ 本作=締め出し）。1作目 five-types-explainer と同一トンマナ・同一パイプライン（Edge TTSナレ＋SRT同期字幕）。

## reward-trap との差別化（重要）
- reward-trap = **実務（報酬設計）寄り**：非随伴コイン・Wells Fargo・内発の谷・情報的vs統制的
- 本作 crowding-out = **ドメイン外の一致**が主題：動物実験の機構が「檻の外」＝人間の制度設計（社会政策・経済学）に届く。託児所の罰金（A Fine is a Price）・献血（Titmuss）が主役。内発の谷curveは流用するが、文脈は「献血の供血が細る」に差し替え。**伝播（蜂起・取り付け）vs 置換（締め出し）**の対比が本作固有の山場（第4・5・6の一致シリーズの締め）。

## Format
- 1920×1080（16:9）・約204秒（3分24秒）・30fps・5シーン
- 音声：Edge TTS `ja-JP-NanamiNeural --rate=+10%`（narration/ch1-5.mp3・track1直列）＋BGM小音量（bgm.mp3=procrastination-short/bgm-calm ループ・volume0.22・track0）
- ⚠️音声は**mp3直使用**（wav化すると page load 10s timeout で inspect/render 不能）
- 字幕：edge-tts SRT（文単位）を章オフセットでシフトした GROUPS 配列（40cue）・一度に1グループ・hard kill
- 章オフセット：ch1=1.0 / ch2=31.8 / ch3=73.8 / ch4=110.79 / ch5=151.38（章間 約2.5秒の「間」）

## シーン構成
| S | 内容 | 主資産 |
|---|---|---|
| S1 | フック「お金が善意を締め出すとき」＝報酬を足すと行動が減る逆転・動物実験の機構が檻の外へ | ハイエナ（報酬・危険側／reward-trap流用） |
| S2 | 託児所の罰金＝「価格」に変わる。罪悪感(内発)→価格(外発)のbefore/after。撤回しても戻らない | before/after 2カード＋矢印 |
| S3 | 献血＝謝礼が善意を追い出す（Titmus・論争注付き）。内発の谷グラフ（供血が細る文脈） | curveV描画（reward-short流用）＋論争caveat |
| S4 | 機構＝内発の置換（定理C）。R_eff式＋伝播(蜂起/取付) vs 置換(締め出し)の対比 | 式カード＋2カラム対比 |
| S5 | 問題は額でなく形。情報的vs統制的＋損失として効く（参照点）＋§0＋CTA | 2カラム対比 |

## Colors / Typography
- `#faf8f4` 背景 / `#1d2321` 文字 / `#2f6f4f` 緑(内発・善意・壊さない側) / `#d9893b` オレンジ(報酬・価格・置換側＝本作の主アクセント) / `#e6efe9` 淡緑 / `#6b7370` 補助 / `#e3e0d8` 罫線
- `"Noto Sans JP", sans-serif`（Serif不可）・見出し900 / 本文700 / 字幕700・40px

## Motion / §0
- シーン遷移＝クロスフェード＋content y:60→0。entrance のみ（最終シーン以外 exit 禁止）・SRT実測cueに同期
- S3 内発の谷＝`strokeDasharray/Dashoffset` で描画アニメ（ナレ「上書きされ供血が細る」84.66s に同期）
- §0：crowding-out は Layer1正本寄り（比喩でなく機構）。**Titmus献血は論争ありを字幕・図中caveat・末尾注すべてで明示**（記事§0踏襲）。託児所/献血は「機構が檻の外に届いた事実」の引用で、特定制度の単一原因断定ではない。独立性は蜂起/取付より弱い（経済学はデシ参照）と記事は注記するが、動画では尺の都合で末尾注の出典明示に留める

## What NOT to Do
- 原色べた塗り・ネオン／暗黒背景／明朝体
- Titmus献血を「確定した事実」に見せる（論争注を落とさない・§0違反）／効果保証
- 字幕ゾーン（下部185px）にコンテンツを進入させる
- reward-trap と同じ画作り（Wells Fargo等）の再演＝差別化（ドメイン外の一致＝託児所/献血/伝播vs置換を前面に）
