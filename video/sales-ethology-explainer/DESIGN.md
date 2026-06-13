# sales-ethology-explainer — 営業の動物行動学（YouTube横型解説 第15作）

元記事：`site/src/content/articles/sales-ethology.md`（営業＝4ダイヤル×7実験の俯瞰）

## 仕様
- 横型 16:9 / 1920×1080 / **281秒（4分41秒）** / **24fps**（長尺＝メモリ壁回避で最初から24fps）
- 5シーン・`.scene` opacity 切替＋`xfade(s,t)`・各要素は SRT 実測 cue 秒で `tl.to`（entrance のみ・最終シーン以外 exit 禁止）
- 字幕＝下部 `#caps`・1グループずつ・out 後 `tl.set(visibility:hidden)` で hard kill（54グループ）
- 音声：EdgeTTS `ja-JP-NanamiNeural --rate=+10%` 章別 **mp3直使用**（track1直列・data-start=実測オフセット）＋ BGM（`bgm.mp3`＝procrastination `bgm-calm` ループ・volume 0.22・afade in1.5/out3・track0）
- 章実測：ch1=40.2 / ch2=53.3 / ch3=46.03 / ch4=61.9 / ch5=65.76（章間 約2.5秒の「間」）
- オフセット：1.0 / 43.70 / 99.50 / 148.04 / 212.43（`make_groups.py` の OFFSETS）

## 5シーン構成（4ダイヤルを横断する俯瞰）
1. **フック**（1.0-43.70）：ノウハウは寄せ集めに見えて底は同じ4ダイヤル。報酬／学習／恐怖／同調のチップ。「営業＝動物行動学の応用編」
2. **報酬ダイヤル**（43.70-99.50）：変動比率の消去抵抗グラフ（変動=消えにくい緑／固定=すぐ消えるオレンジ）＋ドーパミンは予告サインへ（シュルツ）＋返報性（チンパン・吸血コウモリ）
3. **学習ダイヤル**（99.50-148.04）：正本コアに直結。`ΔV = η · g · (u − V)`。信頼は「回数」でなく「随伴」＝非随伴（雑談）×／随伴（約束を守る）○の対比
4. **恐怖＋同調**（148.04-212.43）：2カラム。左＝恐怖（逆U字グラフ＝ヤーキーズ-ドッドソン・最適点超で逆効果＋損失回避オマキザル chips）／右＝同調（グッピーの配偶者選択コピー図＋社会的証明 chips）
5. **統合＋3予測**（212.43-281）：4つは独立に・非線形に効く。3予測（①煽るほど売れるは誤り ②信頼は回数でなく約束の当たり方 ③値引き常態化は持続を短く）＋§0注＋タイトル回収「売れる理由はネズミとサルが先に知っていた」＋CTA

## トンマナ（全作共通）
- 色：bg `#faf8f4`／文字 `#1d2321`／深緑 `#2f6f4f`（ポジ）／オレンジ `#d9893b`（恐怖・強調）／淡緑 `#e6efe9`／補助 `#6b7370`／罫線 `#e3e0d8`。学習=`#3f7d8c`（青緑）／同調=`#7a9a4a`（黄緑）でダイヤル色分け
- フォント：`"Noto Sans JP"` のみ（Serif/mono 非対応）・見出し900/本文700/字幕700 40px・数字 tabular-nums
- `.scene-content` padding `70px 120px 185px`（下185px=字幕ゾーン予約）

## 流用元・新規資産
- 骨格（CSS/xfade/caps/audio/script）＝`procrastination-explainer`（確立形）
- カプチン猿SVG・`fork-row`/`scale-item`/`lineDown` パターン＝`unfairness-cost-explainer`
- **新規SVG**：逆U字グラフ（覚醒×成績・緑上昇/オレンジ下降の2パス strokeDash 描画）／グッピー3匹のコピー連鎖（人気オス＋メス2匹＋点線矢印）／4ダイヤルチップ・消去抵抗グラフ

## 落とし穴記録（このパイプラインの確定知見）
- **長尺は最初から `--fps 24`**：30fps だと frame~5462（≈182秒）で `Target closed` メモリクラッシュ（決定論的）。281s×24fps=6744フレーム
- **GSAP `attr:{}`/`textContent` のアニメート禁止**（lint/inspect は通るが render で即死）。線描画は `strokeDasharray/Dashoffset` のみ可。最適点○は半径固定＋`transform-box:fill-box`+scale
- 音声は **mp3直使用**（wav化で70MB超→page load 10s timeout で render 死）
- lint：0 error / 5 warning（`overlapping_gsap_tweens "__unresolved__"`・`gsap_studio_edit_blocked`・`composition_file_too_large` は誤検知→inspect 0 issue で無視可）
- inspect：初回 2 error（text_box_overflow）→ ① S2「変動比率（消えにくい）」x 470→394 ② S4「真似る（コピー）」x 296→282・font 24→22 で解消 → **0 issue**

## §0（認識論・必守）
末尾 `.note`：式で機構を表したもので組織データで係数を当てたモデルでない／効果保証でない。損失回避・変動比率はヒトでも実証が厚いが、グッピー＝社会的証明は売り場を読む比喩（比喩を式に薄めず、比喩を式が説明する）。動物実験を主役に、営業はその応用として読む。

## commit 対象（8ファイルのみ）
`index.html` ＋ `DESIGN.md` ＋ `narration/ch1-5.txt`（5）＋ `narration/make_groups.py`。
mp4 / mp3 / srt / bgm / frames は **コミット外**。
