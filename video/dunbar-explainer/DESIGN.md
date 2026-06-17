# dunbar-explainer — ダンバー数／150の壁（YouTube横型解説 第18作）

元記事：`site/src/content/articles/dunbar-wall.md`（群れには脳が決めた上限があり、超えると協力が崖から落ちる）

## 仕様
- 横型 16:9 / 1920×1080 / **約244秒（4分4秒）** / **24fps**（5856フレーム）
- 5シーン・`.scene` opacity 切替＋`xfade(s,t)`（**前シーンを `t+0.6` で opacity:0 にして hard hide**＝inspect の text_occluded 回避）・各要素は SRT 実測 cue 秒で entrance
- 字幕＝下部 `#caps`・46グループ・out 後 `tl.set(visibility:hidden)` で hard kill
- 音声：EdgeTTS `ja-JP-NanamiNeural --rate=+10%` 章別 mp3直使用＋BGM（procrastination `bgm-calm` ループ・volume 0.22）
- 章実測：ch1=46.49 / ch2=37.92 / ch3=52.06 / ch4=40.49 / ch5=52.42（章間 約2.5秒）
- オフセット：1.0 / 49.99 / 90.41 / 144.96 / 187.95

## 5シーン構成（規模の壁＝MA-6）
1. **フック**（1.0-49.99）：群れにはちょうどいい大きさがある。脳が群れの上限を決める。人を増やすと、ある日いっせいに協力が崩れる。チンパン5体の群れ
2. **脳が群れの上限を決める**（49.99-90.41）：新皮質∝群れサイズ。グルーミング時間に上限。巨大数字 **150**（ダンバー数）。チンパン顔
3. **壁はガクッと来る**（90.41-144.96）：崖グラフ＝45人で0.89のプラトー→55人で0.04へ垂直落下。連続希薄化でなく鋭い壁（鞍点）
4. **「150」は定数でない**（144.96-187.95）：壁は容量に比例。打ち手2つ＝①容量を上げる（透明性）②容量を超えない単位に分ける（2ピザ/分隊）
5. **まとめ＋3予測＋§0**（187.95-244）：①人数だけ増やすと崩れる ②評判可視化で壁が遠ざかる ③壁超えはチンパン型の派閥・政治へ

## トンマナ（全作共通）
- 色：bg `#faf8f4`／文字 `#1d2321`／深緑 `#2f6f4f`（結束/協力）／オレンジ `#d9893b`（崩壊/崖/強調）／淡緑 `#e6efe9`／補助 `#6b7370`
- フォント：`"Noto Sans JP"` のみ・見出し900/本文700/字幕700 40px
- `.scene-content` padding `70px 120px 185px`（下185px=字幕ゾーン）

## 流用元・新規資産
- 骨格＝mobbing/attribution（確立形）＋**scene-hide版xfade**
- **チンパン顔SVG**＝short/既存explainerから流用（群れ＝5体／S2の霊長類）
- **新規＝崖グラフ（strokeDasharray描画・プラトー→急落）／巨大数字150（CSS）／2手カード**

## 落とし穴記録
- ⚠️**stacked sceneのtext_occluded**: 前シーンのテキストがS5不透明背景に隠れる→inspect 11 error。**xfadeで前シーンを opacity:0 にして解決**（現シーンが覆うので視覚変化なし・以降の全作に適用）
- 244×24=5856フレーム＝24fpsでクラッシュ0完走。lint 0err（warn 2は既知誤検知）／inspect 0issue（scene-hide修正後）／音声-19.8dB
- GSAP `attr`/`textContent` 禁止。崖の落下点マーカーは半径固定＋`transform-box:fill-box`+scale で pulse

## §0（認識論・必守）
末尾 `.note`：「有界な容量が規模の壁を生む」機構の写像で、特定組織の最適人数を保証しない。150は幅のある推定値。動物を主役に組織は応用。出典：Dunbar（社会脳仮説／ダンバー数）。

## commit 対象（8ファイル＋サムネ）
`index.html` ＋ `DESIGN.md` ＋ `narration/ch1-5.txt`（5）＋ `narration/make_groups.py` ＋ `thumbnail.html`。mp4/mp3/srt/bgm/thumbnail.png/frames/work は除外。
