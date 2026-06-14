# attribution-explainer — 帰属の動物行動学（YouTube横型解説 第16作）

元記事：`site/src/content/articles/attribution-ethology.md`（「たまたま」を実力と誤解する脳・帰属ゲートg）

## 仕様
- 横型 16:9 / 1920×1080 / **230秒（3分50秒）** / **24fps**（5520フレーム）
- 5シーン・`.scene` opacity 切替＋`xfade(s,t)`・各要素は SRT 実測 cue 秒で `tl.to`（entrance のみ・最終シーン以外 exit 禁止）
- 字幕＝下部 `#caps`・1グループずつ・out 後 `tl.set(visibility:hidden)` で hard kill（44グループ）
- 音声：EdgeTTS `ja-JP-NanamiNeural --rate=+10%` 章別 **mp3直使用**（track1直列）＋ BGM（`bgm.mp3`＝procrastination `bgm-calm` ループ・volume 0.22・track0）
- 章実測：ch1=30.77 / ch2=44.64 / ch3=38.76 / ch4=40.3 / ch5=61.3（章間 約2.5秒の「間」）
- オフセット：1.0 / 34.27 / 81.41 / 122.67 / 165.46（`make_groups.py` の OFFSETS）

## 5シーン構成（単一機構＝帰属ゲートg）
1. **フック**（1.0-34.27）：努力が報われた手応えは成果でなく「自分のおかげ」と帰属できるか。鳩＋ラット
2. **鳩の迷信**（34.27-81.41）：スキナー1948＝非随伴の餌→偶然の動作を誤帰属→首振り/回転。帰属＝検出器、簡単に誤作動
3. **帰属ゲートg**（81.41-122.67）＝正本コア直結：`ΔV = η · g · (u − V)`（g強調）。報酬が学習・内発を生むのは随伴したときだけ。非随伴(迷信/無関心)×／随伴(学習点火)○の対比メーター
4. **マイクロマネジメント**（122.67-165.46）：細かい指示→成果は上司のもの→g閉じる(✕内発死)／裁量→自分でやった→g開く(○内発点火)。自律性＝gを開けること（デシ）
5. **組織の迷信＋3予測＋§0**（165.46-230）：勝ちパターンの教義化。3予測（①随伴で効く ②マイクロは育てない ③成功は誤帰属されやすい）＋§0＋タイトル回収

## トンマナ（全作共通）
- 色：bg `#faf8f4`／文字 `#1d2321`／深緑 `#2f6f4f`（ポジ・随伴/学習）／オレンジ `#d9893b`（誤帰属/非随伴/強調）／淡緑 `#e6efe9`／補助 `#6b7370`
- フォント：`"Noto Sans JP"` のみ・見出し900/本文700/字幕700 40px・数字 tabular-nums
- `.scene-content` padding `70px 120px 185px`（下185px=字幕ゾーン予約）

## 流用元・新規資産
- 骨格（CSS/xfade/caps/audio/script）＝sales/procrastination（確立形）
- **鳩SVG・ラットSVG・対比メーター（非随伴/随伴）＝attribution-ethology-short から流用**
- formula は ΔV=η·g·(u−V)（g をオレンジ強調＝帰属ゲートが主役）

## 落とし穴記録
- **長尺は最初から `--fps 24`**（230×24=5520＝過去壁5462超だがメモリ余裕で完走想定）
- GSAP `attr`/`textContent` 禁止。メーターは `scaleX`（transform-box left）でアニメ＝OK
- 音声は mp3直使用。lint 0err / inspect 0issue（一発）

## §0（認識論・必守）
末尾 `.note`：式で機構を表したもので効果保証でない。スキナーの迷信行動(1948)は解釈に議論あり挿絵扱い。随伴性の検出が学習を駆動することはロバストで、ヒトの内発（デシ自己決定理論）と二層接続。動物実験を主役に、組織はその応用。

## commit 対象（8ファイル＋サムネ）
`index.html` ＋ `DESIGN.md` ＋ `narration/ch1-5.txt`（5）＋ `narration/make_groups.py` ＋ `thumbnail.html`。
mp4 / mp3 / srt / bgm / thumbnail.png / frames は **コミット外**。
