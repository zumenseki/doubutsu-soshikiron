// 現場どうぶつ診断：型カルテのテンプレ。docs/診断ロジック仕様.md §5 ／ docs/比喩_5類型マクロ.md §2-3 準拠。
// 注意（§0）：型は「組織の原型＝比喩」。個人の評価でも、係数を当てた実測モデルでもない。

export const STAGES = {
  1: '狩猟集団',
  2: '部族期',
  3: '制度期',
  4: '官僚期',
  5: '硬直期',
};

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
    kit: '親方の頭を移植する引き継ぎ1枚＋最初の番頭の選び方',
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
    kit: '現場にオオカミ枠を作る再野生化チェック',
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
    kit: '根回しを減らす意思決定フロー1枚',
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
    kit: '層の継ぎ目点検チェックリスト（維持運用）',
  },
};
