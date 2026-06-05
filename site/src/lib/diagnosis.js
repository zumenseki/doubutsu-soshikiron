// 現場どうぶつ診断：採点・判定の純関数。docs/診断ロジック仕様.md §2-4 の実装。
// 決定的（乱数なし）／クライアント完結（サーバ・API不要）。
import { TYPES, STAGES } from '../data/types.js';

const mean = (...xs) => xs.reduce((a, b) => a + b, 0) / xs.length;
const norm = (m) => Math.round(((m - 1) / 4) * 100); // 回答平均 1..5 → 0..100
const clamp01 = (x) => Math.max(0, Math.min(1, x));
const hi = (v) => clamp01((v - 50) / 50); // 50→0, 100→1（高いほど該当）
const lo = (v) => clamp01((50 - v) / 50); // 50→0,   0→1（低いほど該当）
const mid = (v) => clamp01(1 - Math.abs(v - 65) / 35); // 65付近で1
const stdev = (xs) => Math.sqrt(mean(...xs.map((x) => (x - mean(...xs)) ** 2)));
const balance = (...vs) =>
  clamp01((mean(...vs) - 55) / 35) * clamp01(1 - stdev(vs) / 30);

// タイブレーク：安全リスクの高い病態を優先して警告（顧客価値が高い側へ倒す）
const PRIORITY = ['hyena', 'kochoku', 'chimp', 'bonobo', 'ookami', 'ari', 'ecosys'];

/**
 * @param {Object} answers - { q1..q15: 1..5 }
 * @returns {Object} result（docs/診断ロジック仕様.md §6）
 */
export function diagnose(answers) {
  const r = (k) => Number(answers['q' + k]);

  // --- 4軸 健全度（0..100・高い=健全）---
  const fear = norm(mean(r(1), r(2), r(3))); // 安全（恐怖の低さ）
  const reward = norm(mean(r(4), r(5), r(6)));
  const learn = norm(mean(r(7), r(8), r(9)));
  const conform = norm(mean(r(10), r(11), r(12)));

  // --- 補助指標（0..100）---
  const solo = norm(6 - r(13)); // 属人化（高=親方依存）
  const prec = norm(r(14)); // 前例主義（高=却下されがち）
  const inst = norm(r(15)); // 制度化（高=制度が揃う）
  const numBias = norm(6 - r(6)); // 報酬の数字偏重
  const unfair = norm(6 - r(5)); // 不公平感
  const open = norm(r(11)); // 異論許容

  // --- Stage（症状ベース・上位優先）---
  let stageN = 1;
  if (prec >= 60 && learn < 40) stageN = 5;
  else if (inst >= 60 && (fear < 45 || open < 40)) stageN = 4;
  else if (inst >= 40) stageN = 3;
  else if (inst < 40 && solo >= 60) stageN = 2;

  // --- 型 適合スコア（0..1）---
  const scores = {
    ookami: mean(hi(learn), hi(fear), hi(solo), lo(inst)),
    ari: mean(hi(inst), hi(conform), mid(learn), mid(fear)),
    kochoku: mean(lo(learn), hi(conform), hi(prec), hi(inst)),
    hyena: mean(lo(fear), hi(numBias), lo(learn)),
    chimp: mean(lo(fear), hi(inst), lo(open), mid(prec)),
    bonobo: mean(hi(fear), lo(learn), lo(reward), hi(conform)),
    ecosys: balance(fear, reward, learn, conform),
  };

  // --- 採用（最大スコア → 僅差は安全リスク順タイブレーク）---
  const ranked = Object.entries(scores).sort(
    (a, b) => b[1] - a[1] || PRIORITY.indexOf(a[0]) - PRIORITY.indexOf(b[0])
  );
  const top = ranked[0][1];
  const near = ranked
    .filter(([, v]) => top - v < 0.05)
    .sort((a, b) => PRIORITY.indexOf(a[0]) - PRIORITY.indexOf(b[0]));
  const winnerKey = near[0][0];
  const winnerScore = scores[winnerKey];

  // 適合が低い＝混成/移行期。上位2つを併記。
  const splitted = winnerScore < 0.35;
  const alt = ranked
    .filter(([k]) => k !== winnerKey)
    .slice(0, 2)
    .map(([k]) => ({ key: k, label: TYPES[k].label }));

  const scoresPct = Object.fromEntries(
    Object.entries(scores).map(([k, v]) => [k, Math.round(v * 100)])
  );

  return {
    axes: { fear, reward, learn, conform },
    aux: { solo, prec, inst, numBias, unfair, open },
    stage: { n: stageN, name: STAGES[stageN] },
    type: { ...TYPES[winnerKey], score: Math.round(winnerScore * 100) / 100 },
    alt: splitted ? alt : [],
    splitted,
    scores: scoresPct,
  };
}

export default diagnose;
