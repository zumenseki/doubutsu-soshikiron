// どうぶつ診断：型カルテのテンプレ。docs/診断ロジック仕様.md §5 ／ docs/比喩_5類型マクロ.md §2-3 ／ docs/応用_子育て.md §4 準拠。
// 注意（§0）：型は「組織・関わり・家庭の原型＝比喩」。個人の性格・能力の評価でも、係数を当てた実測モデルでもない。
// video = data/videos.js のトピックキー。YouTube未発行の間は記事リンクへ自動フォールバック（壊れリンクを出さない）。

export const STAGES = {
  1: '狩猟集団',
  2: '部族期',
  3: '制度期',
  4: '官僚期',
  5: '硬直期',
};

// ───────── 組織・チーム（7型＋Stage）─────────
export const TYPES = {
  ookami: {
    key: 'ookami',
    label: '親方オオカミ型',
    healthy: true,
    finding: '少人数で現場判断が速い、熱量の高い群れ。創業期〜部族期の強さがある。',
    weakness: '親方依存。あの人が抜けたら回らない（属人化）。',
    action: '親方の判断基準を3つだけ言語化し、朝礼で共有することから始める。',
    article: 'precedent-lockin',
    articleHint: '拡大期に効いてくる、前例と属人化の落とし穴',
    video: 'precedent-lockin',
    kit: '親方の頭を移植する引き継ぎ1枚＋最初の番頭の選び方',
    // ↓ note購入URLを貼ると結果カードCTAが「相談」→「購入」へ自動切替。空ならフォールバック。原稿＝docs/note_親方オオカミ型_引き継ぎ.md
    kitUrl: '',
  },
  ari: {
    key: 'ari',
    label: '規律アリ型',
    healthy: true,
    finding: '手順と再現性が効いた安定した群れ。拡大・品質・安全管理に強い。',
    weakness: '現場の即応・創造が出にくい。放置すると硬直（Stage5）へ向かう。',
    action: '現場チームだけ「オオカミ枠」を作り、小さな実験を許可する。',
    article: 'controllability',
    articleHint: '同じ叱責が効く時と壊す時（統制可能性）',
    video: 'controllability',
    kit: '現場にオオカミ枠を作る再野生化チェック',
    // ↓ note購入URLを貼ると結果カードCTAが「相談」→「購入」へ自動切替。空ならフォールバック。原稿＝docs/note_規律アリ型_再野生化チェック.md
    kitUrl: '',
  },
  kochoku: {
    key: 'kochoku',
    label: '硬直アリ型',
    healthy: false,
    finding: '前例主義が強く、提案が出にくい。ゆっくり活力を失いつつある段階。',
    weakness: '学習が止まり、悪い情報も新しい工夫も上がってこない。',
    action: '「前からこう」が出たら「今ならどうする?」を15分問う場を、月1回入れる。',
    article: 'precedent-lockin',
    articleHint: '前例主義が組織を固める仕組みと、その壊し方',
    video: 'precedent-lockin',
    kit: '前例を壊す15分ふりかえり雛形＋ゾンビ手順の棚卸しリスト',
    // ↓ note購入URLを貼ると結果カードCTAが「相談」→「購入」へ自動切替。空ならフォールバック。原稿＝docs/note_硬直アリ型_前例ふりかえり.md
    kitUrl: '',
  },
  hyena: {
    key: 'hyena',
    label: '恐怖ハイエナ型',
    healthy: false,
    finding: '数字と未達への緊張で走る群れ。短期は強いが、代償が積み上がりやすい。',
    weakness: '悪い情報が遅れる構造。事故・離職・不正のリスクにつながりやすい。',
    action: 'ミス報告を「叱る対象」から外すと朝礼で宣言する。報告した人を責めない。',
    article: 'fear-kills-learning',
    articleHint: 'なぜ恐怖が、悪い情報と学習を止めるのか',
    video: 'fear',
    kit: 'ヒヤリが上がる10分朝礼キット＋叱り方を“統制可能”にする声かけ表',
    // ↓ note / Stripe の購入URLを貼ると、結果カードのCTAが「相談」から「購入」へ自動で切替わる。
    //    空文字のままなら相談導線にフォールバック（壊れたリンクを出さない）。原稿＝docs/note_恐怖ハイエナ型_ヒヤリ朝礼キット.md
    kitUrl: '',
  },
  chimp: {
    key: 'chimp',
    label: '政治チンパン型',
    healthy: false,
    finding: '規模が増え、根回し・社内調整にエネルギーが向き始めた群れ。',
    weakness: '力が社外（顧客）でなく社内（政治）へ向く。意思決定が遅くなる。',
    action: '意思決定の前の根回しを、「誰が決めるか」を書いた1枚のフローに置き換える。',
    article: 'unfairness-cost',
    articleHint: '不公平感が群れを壊すコスト',
    video: 'unfairness-cost',
    kit: '根回しを減らす意思決定フロー1枚',
    // ↓ note購入URLを貼ると結果カードCTAが「相談」→「購入」へ自動切替。空ならフォールバック。原稿＝docs/note_政治チンパン型_意思決定フロー.md
    kitUrl: '',
  },
  bonobo: {
    key: 'bonobo',
    label: 'ぬるいボノボ型',
    healthy: false,
    finding: '心理的に安全で離職は少ないが、駆動と緊張が不足した群れ。',
    weakness: '居心地は良いが停滞しやすい。基準と締切が緩い（ぬるま湯）。',
    action: '優しさは保ったまま、締切と基準だけを明確にする（高基準×高安全の学習ゾーンへ）。',
    article: 'reward-trap',
    articleHint: '報酬と随伴の設計（増やすと裏目に出る理由）',
    video: 'reward-trap',
    kit: '若手が辞める前の班長面談シート＋歩合を壊さず効かせるチェック',
    // ↓ note購入URLを貼ると結果カードCTAが「相談」→「購入」へ自動切替。空ならフォールバック。原稿＝docs/note_報酬の罠_班長面談シート.md
    kitUrl: '',
  },
  ecosys: {
    key: 'ecosys',
    label: '生態系混成型',
    healthy: true,
    finding: '層ごとに動物相を使い分けられている、バランスの良い群れ。',
    weakness: '目立つ弱点は少ない。慢心と慣性で、徐々にアリ化する点に注意。',
    action: '今の配置を維持。層の継ぎ目（どの規則がどこに効くか）を年1回点検する。',
    article: 'controllability',
    articleHint: '統制と自律の継ぎ目をどう設計するか',
    video: 'five-types',
    kit: '層の継ぎ目点検チェックリスト（維持運用）',
    // ↓ note購入URLを貼ると結果カードCTAが「相談」→「購入」へ自動切替。空ならフォールバック。原稿＝docs/note_生態系混成型_層の継ぎ目点検.md
    kitUrl: '',
  },
};

// ───────── 自分（関わり方の癖・5動物）─────────
// §0：個人の性格ではなく「あなたの関わり方・マネジメントの癖がどの動物の設計に寄っているか」。
//      「あなたは○○型の人間だ」ではなく「いまの関わりが○○の設計に寄っている」と読む。
export const TYPES_SELF = {
  ookami: {
    key: 'ookami',
    label: '牽引オオカミ型',
    healthy: false,
    finding: '恐怖・締切・緊張で人を動かす関わりに寄っている。立ち上げや危機ではスピードが出る。',
    weakness: '悪い情報が遅れ、相手が「止まった」のを「育った」と読み違えやすい。',
    action: '危機以外では、「叱る」を「同じ基準を毎回フィードバックする」へ置き換える。',
    article: 'fear-kills-learning',
    articleHint: 'なぜ恐怖が、相手の学習と本音を止めるのか',
    video: 'fear',
  },
  ari: {
    key: 'ari',
    label: '規範アリ型',
    healthy: true,
    finding: '前例・規範・「普通は」で揃える関わりに寄っている。再現性と安定に強い。',
    weakness: '相手個人の手応えが育ちにくく、例外や新しいやり方への即応が鈍る。',
    action: '「他の人はこうしている」ではなく「あなたは前回どうだった」で返す場面を増やす。',
    article: 'five-types-ethology',
    articleHint: '同調が効く場面と、内発を薄める場面',
    video: 'five-types',
  },
  chimp: {
    key: 'chimp',
    label: '競争チンパン型',
    healthy: false,
    finding: '比較・順位・インセンティブで動かす関わりに寄っている。短期の駆動は強い。',
    weakness: '統制的な報酬が内発を締め出し（crowding-out）、不公平感のコストが出やすい。',
    action: '「ご褒美の予告」を一つ減らし、事後に「工夫した点」を具体的に認める形へ。',
    article: 'crowding-out',
    articleHint: '報酬が、もともとの意欲を締め出すとき',
    video: 'crowding-out',
  },
  bonobo: {
    key: 'bonobo',
    label: '受容ボノボ型',
    healthy: false,
    finding: '衝突を避け、受け止め・先回りで支える関わりに寄っている。安心の土台はある。',
    weakness: '先回り＝随伴の肩代わりが続くと、優しさが相手の自走（学習）を奪う側に回る。',
    action: '小さくても「本人に決めさせ、結果を本人に返す」場面を一つ戻す。',
    article: 'reward-trap',
    articleHint: '支え方が裏目に出る、随伴の設計',
    video: 'reward-trap',
  },
  hyena: {
    key: 'hyena',
    label: '気分ハイエナ型',
    healthy: false,
    finding: 'その場の状況や気分で対応が変わる関わりに寄っている。',
    weakness: '一貫性の揺れが「行動→結果」の随伴性を壊し、何度言っても学習が載らない。',
    action: '叱る「強さ」より「毎回同じ」を優先する。まず一つの行動だけ対応を固定して試す。',
    article: 'controllability',
    articleHint: '一貫性（随伴性）が、強さより効く理由',
    video: 'controllability',
  },
};

// ───────── 家庭・子育て（5動物・docs/応用_子育て.md §4 準拠）─────────
// §0：型を子・親に貼り付けない。「うちはどの配合か」を見るレンズ。係数は測っていない。
export const TYPES_FAMILY = {
  ookami: {
    key: 'ookami',
    label: 'オオカミ家庭',
    healthy: false,
    finding: '上下と規律が明確で、止めるべき行動は速く止まる関わりに寄っている。',
    weakness: '恐怖の正当域を超えると、回避と無力感（定理B）に着く。「止まった＝育った」は別物。',
    action: '危険の即時停止だけ恐怖を残し、日常のしつけは「同じ行動には毎回同じ結果」へ寄せる。',
    article: 'fear-kills-learning',
    articleHint: '叱りが「止める」だけで「育てない」とき',
    video: 'fear',
  },
  ari: {
    key: 'ari',
    label: 'アリ家庭',
    healthy: true,
    finding: '「みんなやってる」「普通は」で揃える、秩序の効いた関わりに寄っている。',
    weakness: '随伴性が外部の規範に外注され、子ども個人の手応え（ΔV）が育ちにくい。',
    action: '「他の子」ではなく「昨日の本人」と比べる場面を一つ増やす。',
    article: 'five-types-ethology',
    articleHint: '同調で揃えることの強みと副作用',
    video: 'five-types',
  },
  chimp: {
    key: 'chimp',
    label: 'チンパン家庭',
    healthy: false,
    finding: 'ごほうび・順位・比較でやる気を作る関わりに寄っている。短期は動く。',
    weakness: '統制的なごほうびほど内発を置換し（定理C）、与えた報酬の撤回は参照点κで過大に効く。',
    action: 'ごほうびを「事後の・予期せぬ・工夫を認める」形へ。「○点で△△」の予告を一つ減らす。',
    article: 'reward-trap',
    articleHint: 'ごほうびが勉強嫌いを生む仕組み',
    video: 'reward-trap',
  },
  bonobo: {
    key: 'bonobo',
    label: 'ボノボ家庭',
    healthy: false,
    finding: '受容的で衝突が少なく、安心の土台がある関わりに寄っている。',
    weakness: '先回り＝随伴の肩代わりが続くと、優しさが無力感（定理B）を作る側に回る。',
    action: '小さくても「本人に選ばせ、結果を本人に返す」場面を一つ戻す。',
    article: 'controllability',
    articleHint: '過保護が「どうせ無理」を育てるとき',
    video: 'controllability',
  },
  hyena: {
    key: 'hyena',
    label: 'ハイエナ家庭',
    healthy: false,
    finding: 'その場の機嫌・損得で対応が決まる関わりに寄っている。',
    weakness: '同じ行動に結果がランダム＝随伴性ゼロで、回数を増やすほどノイズが増える（§3-1）。',
    action: '叱る「強さ」より「毎回同じ」を優先する。一つの行動だけ対応を固定して試す。',
    article: 'controllability',
    articleHint: '「何度言っても直らない」の正体',
    video: 'controllability',
  },
};

// 対象ごとのメタ（セレクタ表示・結果見出し・§0注記の出し分け）
export const TARGETS = {
  org: {
    key: 'org',
    label: '組織・チーム',
    tagline: '部下が動かない・若手が辞める・ヒヤリが上がらない、その背景を見る',
    typeHeading: 'あなたの現場タイプ',
    note: 'これは実測モデルではなく、行動学の知見を使った仮説生成ツールです。組織の自己点検であり、個人の評価・医療や心理の診断ではありません。',
  },
  self: {
    key: 'self',
    label: '自分（関わり方の癖）',
    tagline: 'あなたの関わり方・マネジメントの癖が、どの動物の設計に寄っているかを見る',
    typeHeading: 'あなたの関わりが寄っている設計',
    note: 'これは性格占いではありません。あなたの“関わり方・マネジメントの癖”がどの動物の設計に寄っているかを見る仮説生成ツールであり、人格や能力の評価ではありません。',
  },
  family: {
    key: 'family',
    label: '家庭・子育て',
    tagline: '家庭の関わりの配合を、しつけ・学習の機構から見る',
    typeHeading: '家庭の関わりが寄っている配合',
    note: 'これは育児メソッドでも診断でもありません。型を子どもや親に貼り付けず、“どんな配合か”を見るレンズ（仮説生成ツール）です。係数は測っていません。',
  },
};

// 対象キー → 型テーブルの解決（diagnosis.js / shindan.astro 共用）
export const TYPES_BY_TARGET = {
  org: TYPES,
  self: TYPES_SELF,
  family: TYPES_FAMILY,
};
