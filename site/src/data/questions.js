// 現場どうぶつ診断：質問定義（表示用）。採点ロジックは ../lib/diagnosis.js が q1..q15 を直接参照する。
// 設計根拠：docs/診断ロジック仕様.md §1 ／ docs/比喩_5類型マクロ.md §3。
export const QUESTIONS = [
  { id: 'q1',  group: '恐怖と安全',   text: 'ヒヤリ・ミスがあったとき、すぐ上に報告が上がる' },
  { id: 'q2',  group: '恐怖と安全',   text: '部下は「誰の責任か」より先に「どう直すか」を話す' },
  { id: 'q3',  group: '恐怖と安全',   text: '朝礼・会議で若手が反対意見を言える' },
  { id: 'q4',  group: '報酬と評価',   text: '頑張った職人がきちんと評価・処遇される' },
  { id: 'q5',  group: '報酬と評価',   text: '評価・賃金の基準が明確で、不公平感が少ない' },
  { id: 'q6',  group: '報酬と評価',   text: '賞与・歩合が「数字だけ」に偏っていない' },
  { id: 'q7',  group: '学習と改善',   text: '現場改善の提案が出て、実際に採用される' },
  { id: 'q8',  group: '学習と改善',   text: '失敗を共有して次に活かす場がある' },
  { id: 'q9',  group: '学習と改善',   text: '新しい道具・工法を試す余地がある' },
  { id: 'q10', group: '連携と一体感', text: '班・支店でやり方がバラバラでない（共通の理念がある）' },
  { id: 'q11', group: '連携と一体感', text: '新人の意見が通ることがある' },
  { id: 'q12', group: '連携と一体感', text: '雑談・横の連携がある' },
  { id: 'q13', group: '現場の体質',   text: '親方・社長が抜けても現場が回る' },
  { id: 'q14', group: '現場の体質',   text: '「前からこうだ」で提案が却下されがち' },
  { id: 'q15', group: '現場の体質',   text: 'マニュアル・KPI・評価制度が整っている' },
];

// 1〜5 スケール（両端ラベルのみ画面表示、中間は数字）
export const SCALE = [
  { v: 1, label: '全くそう思わない' },
  { v: 2, label: 'あまり' },
  { v: 3, label: 'どちらとも' },
  { v: 4, label: 'ややそう思う' },
  { v: 5, label: 'とてもそう思う' },
];

// 表示順を保ったグループ配列を返す（フォームのセクション分け用）
export function groupedQuestions() {
  const order = [];
  const map = new Map();
  for (const q of QUESTIONS) {
    if (!map.has(q.group)) { map.set(q.group, []); order.push(q.group); }
    map.get(q.group).push(q);
  }
  return order.map((g) => ({ group: g, items: map.get(g) }));
}
