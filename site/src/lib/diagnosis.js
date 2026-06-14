// どうぶつ診断：採点・判定の純関数。docs/診断ロジック仕様.md §2-4・§9 の実装。
// 決定的（乱数なし）／クライアント完結（サーバ・API不要）。
// 3対象：組織org（7型＋Stage）／自分self・家庭family（5動物・関わり方の設計）。
import { TYPES, TYPES_SELF, TYPES_FAMILY, STAGES } from '../data/types.js';

const mean = (...xs) => xs.reduce((a, b) => a + b, 0) / xs.length;
const norm = (m) => Math.round(((m - 1) / 4) * 100); // 回答平均 1..5 → 0..100
const clamp01 = (x) => Math.max(0, Math.min(1, x));
const hi = (v) => clamp01((v - 50) / 50); // 50→0, 100→1（高いほど該当）
const lo = (v) => clamp01((50 - v) / 50); // 50→0,   0→1（低いほど該当）
const mid = (v) => clamp01(1 - Math.abs(v - 65) / 35); // 65付近で1
const stdev = (xs) => Math.sqrt(mean(...xs.map((x) => (x - mean(...xs)) ** 2)));
const balance = (...vs) =>
  clamp01((mean(...vs) - 55) / 35) * clamp01(1 - stdev(vs) / 30);

// 回答済みソースだけで norm 平均（未回答=NaN を捨てる＝12問運用や追加問欠落でも NaN を出さない）。
// データ無しは中庸 50 に縮退。これにより既存 q16-24 が無くても採点が壊れない。
const normMean = (...vals) => {
  const xs = vals.filter((v) => Number.isFinite(v));
  return xs.length ? norm(mean(...xs)) : 50;
};

// タイブレーク：安全リスクの高い病態を優先して警告（顧客価値が高い側へ倒す）
const ORG_PRIORITY = ['hyena', 'kochoku', 'chimp', 'bonobo', 'ookami', 'ari', 'ecosys'];
const ANIMAL_PRIORITY = ['hyena', 'chimp', 'bonobo', 'ookami', 'ari'];

// 適合スコア(0..1) → 100%正規化した「配合」。純血種はいない＝混血を見せる（§0・比喩ルール）。
// exclude：健全アンカー（org=ecosys 等）は配合バーから除外し、病態/運営スタイルの混合比を見せる。
// 合計が極小（全同一回答など）は weak=true でバーを出さない。
function blend(scores, { exclude = [], types = null } = {}) {
  const entries = Object.entries(scores).filter(([k]) => !exclude.includes(k));
  const S = entries.reduce((a, [, v]) => a + Math.max(0, v), 0);
  const maxRaw = entries.reduce((m, [, v]) => Math.max(m, v), 0);
  // 合計が極小（全同一回答）／最大適合すら低い（材料が弱い）→ 配合を出さない（精度を装わない＝§0）
  if (S < 0.05 || maxRaw < 0.25) return { ordered: [], weak: true };
  const raw = entries
    .map(([k, v]) => ({ key: k, label: types?.[k]?.label || k, pct: (Math.max(0, v) / S) * 100 }))
    .sort((a, b) => b.pct - a.pct)
    .map((p) => ({ ...p, pct: Math.round(p.pct) }));
  const diff = 100 - raw.reduce((a, p) => a + p.pct, 0); // 丸め誤差は最大要素へ寄せ合計100%固定
  if (raw.length) raw[0].pct += diff;
  return { ordered: raw, weak: false };
}

// 最大スコア採用 → 僅差(<0.05)は priority 順タイブレーク
function pickWinner(scores, priority) {
  const ranked = Object.entries(scores).sort(
    (a, b) => b[1] - a[1] || priority.indexOf(a[0]) - priority.indexOf(b[0])
  );
  const top = ranked[0][1];
  const near = ranked
    .filter(([, v]) => top - v < 0.05)
    .sort((a, b) => priority.indexOf(a[0]) - priority.indexOf(b[0]));
  const winnerKey = near[0][0];
  return { ranked, winnerKey, winnerScore: scores[winnerKey] };
}

/**
 * 診断ディスパッチャ。
 * @param {string|Object} a - target('org'|'self'|'family') または answers（後方互換：文字列でなければ org）
 * @param {Object} [b] - target 指定時の answers
 */
export function diagnose(a, b) {
  const [target, answers] = typeof a === 'string' ? [a, b] : ['org', a];
  if (target === 'self') return diagnoseSelf(answers);
  if (target === 'family') return diagnoseFamily(answers);
  return diagnoseOrg(answers);
}

// ───────── 組織（7型＋Stage）─────────
// 4軸（fear/reward/learn/conform）の3問平均は不変＝既存の axes/Stage を保つ。
// 追加9問(q16-24)は補助指標としてのみ作用（既存補助は2ソース化＝欠落時は単一ソースへ縮退）。
function diagnoseOrg(answers) {
  const r = (k) => Number(answers['q' + k]);

  // --- 4軸 健全度（0..100・高い=健全）---
  const fear = norm(mean(r(1), r(2), r(3))); // 安全（恐怖の低さ）
  const reward = norm(mean(r(4), r(5), r(6)));
  const learn = norm(mean(r(7), r(8), r(9)));
  const conform = norm(mean(r(10), r(11), r(12)));

  // --- 補助指標（0..100）---
  const solo = normMean(6 - r(13), r(21)); // 属人化（高=親方依存/即興・役割非固定）
  const prec = normMean(r(14), r(19)); // 前例主義（高=却下・やり方変更が通らない）
  const inst = normMean(r(15)); // 制度化
  const numBias = normMean(6 - r(6), r(16)); // 報酬の数字偏重・詰めの圧
  const unfair = normMean(6 - r(5)); // 不公平感
  const open = normMean(r(11), 6 - r(17)); // 異論許容（高=新人意見が通る/根回しで決まらない）
  const badNews = normMean(r(20)); // 悪い情報が上がる度（高=健全）
  const slack = normMean(r(18)); // 基準の緩さ（高=締切/基準があいまい）
  const kappa = normMean(r(22)); // 損失回避（高=撤回に強い不満）
  const crisis = normMean(r(23)); // 恐怖の正当域（高=危機時のみ厳格＝健全）
  const confq = normMean(r(24)); // 同調の質（高=理念で揃う＝健全な同調）

  // --- Stage（症状ベース・上位優先・既存ロジック）---
  let stageN = 1;
  if (prec >= 60 && learn < 40) stageN = 5;
  else if (inst >= 60 && (fear < 45 || open < 40)) stageN = 4;
  else if (inst >= 40) stageN = 3;
  else if (inst < 40 && solo >= 60) stageN = 2;

  // --- 型 適合スコア（0..1）---
  const scores = {
    ookami: mean(hi(learn), hi(fear), hi(solo), lo(inst)),
    ari: mean(hi(inst), hi(conform), mid(learn), mid(fear), hi(confq)),
    kochoku: mean(lo(learn), hi(conform), hi(prec), hi(inst), lo(confq)),
    hyena: mean(lo(fear), hi(numBias), lo(learn), lo(badNews)),
    chimp: mean(lo(fear), hi(inst), lo(open), mid(prec)),
    bonobo: mean(hi(fear), lo(learn), lo(reward), hi(conform), hi(slack)),
    ecosys: balance(fear, reward, learn, conform),
  };

  const { ranked, winnerKey, winnerScore } = pickWinner(scores, ORG_PRIORITY);
  const splitted = winnerScore < 0.35; // 適合が低い＝混成/移行期
  const alt = ranked
    .filter(([k]) => k !== winnerKey)
    .slice(0, 2)
    .map(([k]) => ({ key: k, label: TYPES[k].label }));
  const scoresPct = Object.fromEntries(
    Object.entries(scores).map(([k, v]) => [k, Math.round(v * 100)])
  );

  return {
    target: 'org',
    axes: { fear, reward, learn, conform },
    aux: { solo, prec, inst, numBias, unfair, open, badNews, slack, kappa, crisis, confq },
    stage: { n: stageN, name: STAGES[stageN] },
    type: { ...TYPES[winnerKey], score: Math.round(winnerScore * 100) / 100 },
    alt: splitted ? alt : [],
    splitted,
    scores: scoresPct,
    blend: blend(scores, { exclude: ['ecosys'], types: TYPES }),
  };
}

// ───────── 自分・家庭（5動物・関わり方の設計）─────────
// 4ダイヤル＋派生（統制的報酬 rewardCtrl・随伴性の一貫性 consistency）→ 5動物。
// docs/応用_子育て.md §4 の家庭5類型ダイヤル配合が正本。self は同式を「自己の関わりの癖」フレームで。
const SELF_MAP = {
  safety: [['s1', 0], ['s2', 1]], // 高=報告しやすい/語気が荒れない＝安全
  intrinsic: [['s4', 0]], // 高=過程・工夫を承認
  rewardCtrl: [['s3', 0], ['s9', 0]], // 高=統制的・予告的な報酬を多用
  autonomy: [['s5', 0], ['s12', 0], ['s6', 1]], // 高=本人に試させ任せる（先回りしない）
  conform: [['s7', 0]], // 高=「普通は/みんな」で揃えさせる
  confq: [['s8', 0]], // 高=理由があれば逸脱を認める（健全な柔軟さ）
  consist: [['s11', 0], ['s10', 1]], // 高=対応が一貫（機嫌で変わらない）
};
const FAMILY_MAP = {
  safety: [['f1', 0], ['f2', 1]],
  intrinsic: [['f4', 0]],
  rewardCtrl: [['f3', 0]],
  autonomy: [['f5', 0], ['f6', 1]],
  conform: [['f7', 0]],
  confq: [['f8', 0]],
  consist: [['f10', 0], ['f9', 1]],
  crisis: [['f12', 0]], // 高=危険時のみ厳格＝恐怖の正当域（健全）
  kappa: [['f11', 0]], // 高=撤回に強く反発（参照点κ・補助）
};

function relatingConstructs(answers, map) {
  const a = (id) => Number(answers[id]);
  const c = {};
  for (const [key, sources] of Object.entries(map)) {
    c[key] = normMean(...sources.map(([id, rev]) => (rev ? 6 - a(id) : a(id))));
  }
  // 任意ダイヤルは欠落時 50（normMean 既定）になるよう保証
  for (const k of ['safety', 'intrinsic', 'rewardCtrl', 'autonomy', 'conform', 'confq', 'consist']) {
    if (!(k in c)) c[k] = 50;
  }
  return c;
}

// 5動物 適合スコア（hi/lo/mid 再利用・§4 配合表準拠）。self/family 共通。
function relatingScores(c) {
  return {
    ookami: mean(lo(c.safety), hi(c.conform)), // 恐怖高・規律高
    ari: mean(hi(c.conform), mid(c.autonomy)), // 同調高・ルール高（恐怖駆動でない）
    chimp: mean(hi(c.rewardCtrl), lo(c.intrinsic)), // 報酬高・競争高
    bonobo: mean(hi(c.safety), lo(c.rewardCtrl), lo(c.autonomy)), // 受容高・先回り（随伴肩代わり）
    hyena: mean(lo(c.consist), lo(c.safety)), // 一貫性低・場当たり
  };
}

function relatingResult(answers, map, types, targetName) {
  const c = relatingConstructs(answers, map);
  const scores = relatingScores(c);
  // 健全アンカー（学習ゾーンへの近さ）＝透明性表示のみ・配合バーには混ぜない
  const healthyAnchor = clamp01(
    mean(hi(c.safety), hi(c.autonomy), hi(c.confq), hi(c.intrinsic), hi(c.consist))
  );

  const { ranked, winnerKey, winnerScore } = pickWinner(scores, ANIMAL_PRIORITY);
  const splitted = winnerScore < 0.35;
  const alt = ranked
    .filter(([k]) => k !== winnerKey)
    .slice(0, 2)
    .map(([k]) => ({ key: k, label: types[k].label }));
  const scoresPct = Object.fromEntries(
    Object.entries(scores).map(([k, v]) => [k, Math.round(v * 100)])
  );

  // レーダー4軸（高=健全な関わり）。4軸目は「一貫」。
  const axes = {
    fear: Math.round(c.safety),
    reward: Math.round((c.intrinsic + (100 - c.rewardCtrl)) / 2),
    learn: Math.round(c.autonomy),
    conform: Math.round(c.consist),
  };

  return {
    target: targetName,
    axes,
    aux: { ...c, healthyAnchor: Math.round(healthyAnchor * 100) },
    type: { ...types[winnerKey], score: Math.round(winnerScore * 100) / 100 },
    alt: splitted ? alt : [],
    splitted,
    scores: scoresPct,
    blend: blend(scores, { exclude: [], types }), // 5動物すべてが「癖の混合比」
  };
}

function diagnoseSelf(answers) {
  return relatingResult(answers, SELF_MAP, TYPES_SELF, 'self');
}
function diagnoseFamily(answers) {
  return relatingResult(answers, FAMILY_MAP, TYPES_FAMILY, 'family');
}

export default diagnose;
