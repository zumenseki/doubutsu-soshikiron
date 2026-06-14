# mobbing-explainer — 同調圧力の動物行動学（YouTube横型解説 第17作）

元記事：`site/src/content/articles/mobbing-ethology.md`（群れはなぜ一匹を狩るのか・モビングと情報カスケード）

## 仕様
- 横型 16:9 / 1920×1080 / **約249秒（4分9秒）** / **24fps**（5971フレーム）
- 5シーン・`.scene` opacity 切替＋`xfade(s,t)`・各要素は SRT 実測 cue 秒で `tl.to`（entrance のみ・最終シーン以外 exit 禁止）
- 字幕＝下部 `#caps`・1グループずつ・out 後 `tl.set(visibility:hidden)` で hard kill（49グループ）
- 音声：EdgeTTS `ja-JP-NanamiNeural --rate=+10%` 章別 **mp3直使用**（track1直列）＋ BGM（`bgm.mp3`＝procrastination `bgm-calm` ループ・volume 0.22・track0）
- 章実測：ch1=38.64 / ch2=42.6 / ch3=52.34 / ch4=44.09 / ch5=57.1（章間 約2.5秒の「間」）
- オフセット：1.0 / 42.14 / 87.24 / 142.08 / 188.67（`make_groups.py` の OFFSETS）

## 5シーン構成（同調＝守る力／潰す力の二面）
1. **フック**（1.0-42.14）：同調は群れを守る力であると同時に、群れが個を潰す力。同じコインの裏表。鳥の群れ＋フクロウ（天敵）
2. **モビング＝防衛**（42.14-87.24）：カラス/スズメがタカ/フクロウを集団で取り囲み追い払う＝適応的な協調防衛＝生存装置。owl中心に群れが収束。同調の「善」の側面
3. **情報カスケード＝暴走**（87.24-142.08）：一匹が逃げ→全体が雪崩れ・誤報も増幅。自分の感覚より周りに従う＝多元的無知（アッシュの同調実験）。増幅curve＋7矢印カスケード。「沈黙は賛成と限らない」
4. **内側を狩る**（142.08-188.67）：モビングの矛先が内側の一匹へ。ニワトリのつつき＝弱った/毛色違いの個体。攻撃対象は罪でなく「目立つ差異」で選ばれる。村八分/スケープゴート＝内向き暴発。5羽（中央オレンジ標的を pulse）
5. **3予測＋§0**（188.67-249）：①同調は防衛に有用だが暴走で誤情報増幅 ②攻撃対象は罪でなく目立つ差異 ③沈黙は同意でない＝反対は構造で保護して初めて現れる。空気は根性でなく仕組みで止める＋§0＋CTA

## トンマナ（全作共通）
- 色：bg `#faf8f4`／文字 `#1d2321`／深緑 `#2f6f4f`（ポジ・防衛/協調）／オレンジ `#d9893b`（暴走/攻撃/差異/強調）／淡緑 `#e6efe9`／補助 `#6b7370`
- フォント：`"Noto Sans JP"` のみ・見出し900/本文700/字幕700 40px・数字 tabular-nums
- `.scene-content` padding `70px 120px 185px`（下185px=字幕ゾーン予約）

## 流用元・新規資産
- 骨格（CSS/xfade/caps/audio/script）＝attribution/sales（確立形）
- **pigeon SVG・owl SVG＝mobbing-ethology-short から流用**（群れ＝鳥／天敵＝フクロウ）
- **新規＝chicken SVG（白・とさか/くちばし/肉垂）＋chickenT（オレンジ＝標的の一匹＝目立つ差異）**
- S3 増幅 curve は `strokeDasharray/Dashoffset` の線描画（attr禁止回避）／カスケードは矢印7個の opacity stagger（誤報1個＝オレンジ）

## 落とし穴記録
- **長尺は最初から `--fps 24`**（249×24=5971＝sales 6744 完走実績内）。⚠️初回 background render は frame 5589/5971（93%）で**食事中のセッション中断/API Error によりプロセスが殺された**（メモリ壁でなく外的中断・pipe の `Select-Object` が exit0 を返し誤完了通知）→ work掃除して再render で完走
- GSAP `attr`/`textContent` 禁止。標的の強調は `scale` の yoyo pulse、メーター無し、curve は strokeDash＝OK
- 音声は mp3直使用。lint 0err（warn 4は既知誤検知）／inspect は S3 glabel「誤情報も増幅」が上6pxはみ出し→y=24→46 で 0issue

## §0（認識論・必守）
末尾 `.note`：式でなく機構の写像で効果保証でない。鳥のモビング・群れの情報カスケード・ニワトリのつつき順位は動物行動学で観察され、ヒトの同調・多元的無知はアッシュらの社会心理学で示されてきた。特定の集団や個人を断定しない。動物を主役に、組織はその応用。出典：鳥類のモビング行動／Asch (1951)／情報カスケード理論。

## commit 対象（8ファイル＋サムネ）
`index.html` ＋ `DESIGN.md` ＋ `narration/ch1-5.txt`（5）＋ `narration/make_groups.py` ＋ `thumbnail.html`。
mp4 / mp3 / srt / bgm / thumbnail.png / frames・work は **コミット外**。
