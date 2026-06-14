// どうぶつ診断：質問定義（表示用）。3対象（組織org / 自分self / 家庭family）。
// 採点ロジックは ../lib/diagnosis.js が各設問 id を直接参照する。
// 設計根拠：docs/診断ロジック仕様.md §1・§9 ／ docs/比喩_5類型マクロ.md §3 ／ docs/応用_子育て.md §4。
// §0：型は「設計＝比喩」。個人の性格や能力の評価でも、係数を当てた実測モデルでもない。
//
// load = その設問がどの指標に効くかの注釈。
//   org は採点が id 直参照のため load は対応注釈用。self/family は採点が load を実際に使う。
//   load 値：fear/reward/learn/conform（4ダイヤル）＋ rewardCtrl（統制的報酬）/ consistency（随伴性の一貫性）
//          ＋ org 補助：solo/prec/inst/numBias/badNews/slack/open/kappa/crisis/confq
//   reverse:true は「高い回答ほど不健全（逆向き）」を表す。

export const QUESTION_SETS = {
  // ───────── 組織・チーム（既存15問 q1-15 ＋ 識別9問 q16-24）─────────
  org: [
    // 恐怖と安全
    { id: 'q1',  group: '恐怖と安全',   text: 'ヒヤリ・ミスがあったとき、すぐ上に報告が上がる', load: 'fear' },
    { id: 'q2',  group: '恐怖と安全',   text: '部下は「誰の責任か」より先に「どう直すか」を話す', load: 'fear' },
    { id: 'q3',  group: '恐怖と安全',   text: '朝礼・会議で若手が反対意見を言える', load: 'fear' },
    { id: 'q20', group: '恐怖と安全',   text: '悪い情報ほど、早く・正確に上へ上がってくる', load: 'badNews' },
    { id: 'q23', group: '恐怖と安全',   text: '普段は穏やかでも、事故・危険には即・厳しく切り替わる', load: 'crisis' },
    // 報酬と評価
    { id: 'q4',  group: '報酬と評価',   text: '頑張った職人がきちんと評価・処遇される', load: 'reward' },
    { id: 'q5',  group: '報酬と評価',   text: '評価・賃金の基準が明確で、不公平感が少ない', load: 'reward' },
    { id: 'q6',  group: '報酬と評価',   text: '賞与・歩合が「数字だけ」に偏っていない', load: 'reward' },
    { id: 'q16', group: '報酬と評価',   text: '未達のとき、詰め（強いプレッシャー）で取り返そうとする空気がある', load: 'numBias', reverse: true },
    { id: 'q22', group: '報酬と評価',   text: '一度与えた裁量や手当を戻すと、強い不満が出る', load: 'kappa', reverse: true },
    // 学習と改善
    { id: 'q7',  group: '学習と改善',   text: '現場改善の提案が出て、実際に採用される', load: 'learn' },
    { id: 'q8',  group: '学習と改善',   text: '失敗を共有して次に活かす場がある', load: 'learn' },
    { id: 'q9',  group: '学習と改善',   text: '新しい道具・工法を試す余地がある', load: 'learn' },
    { id: 'q19', group: '学習と改善',   text: '「うちのやり方」を変える提案は、通りにくい', load: 'prec', reverse: true },
    // 連携と一体感
    { id: 'q10', group: '連携と一体感', text: '班・支店でやり方がバラバラでない（共通の理念がある）', load: 'conform' },
    { id: 'q11', group: '連携と一体感', text: '新人の意見が通ることがある', load: 'conform' },
    { id: 'q12', group: '連携と一体感', text: '雑談・横の連携がある', load: 'conform' },
    { id: 'q17', group: '連携と一体感', text: '物事は、会議の前の根回しで実質的に決まる', load: 'open', reverse: true },
    { id: 'q24', group: '連携と一体感', text: '周りに合わせること自体が目的化していない（理念で揃っている）', load: 'confq' },
    // 現場の体質
    { id: 'q13', group: '現場の体質',   text: '親方・社長が抜けても現場が回る', load: 'solo' },
    { id: 'q14', group: '現場の体質',   text: '「前からこうだ」で提案が却下されがち', load: 'prec', reverse: true },
    { id: 'q15', group: '現場の体質',   text: 'マニュアル・KPI・評価制度が整っている', load: 'inst' },
    { id: 'q18', group: '現場の体質',   text: '締切や品質の基準が、あいまいなまま流れることがある', load: 'slack', reverse: true },
    { id: 'q21', group: '現場の体質',   text: '役割はかっちり決まっておらず、その場で動ける人が動く', load: 'solo', reverse: true },
  ],

  // ───────── 自分（関わり方の癖）─────────
  // §0：あなた個人の性格ではなく、「あなたの関わり方・マネジメントの癖がどの動物の設計に寄っているか」。
  self: [
    { id: 's1',  group: '恐怖と安全',   text: '相手が報告・相談しやすい雰囲気を、意識して作っている', load: 'fear' },
    { id: 's2',  group: '恐怖と安全',   text: 'うまくいかないと、つい語気が強くなる', load: 'fear', reverse: true },
    { id: 's3',  group: '報酬と承認',   text: '動いてほしいことは、報酬や評価とセットで示すことが多い', load: 'rewardCtrl', reverse: true },
    { id: 's4',  group: '報酬と承認',   text: '成果が出たら、金額や順位より先に「どこが良かったか」を具体的に伝える', load: 'reward' },
    { id: 's9',  group: '報酬と承認',   text: '「これができたら○○」と、先に交換条件を出すことが多い', load: 'rewardCtrl', reverse: true },
    { id: 's5',  group: '学習と自走',   text: 'やり方が非効率に見えても、まず本人に試させる', load: 'learn' },
    { id: 's6',  group: '学習と自走',   text: 'つい先回りして、答えややり方を渡してしまう', load: 'learn', reverse: true },
    { id: 's12', group: '学習と自走',   text: '相手が自分で決めて動けるよう、任せる範囲を意識している', load: 'learn' },
    { id: 's7',  group: '同調と比較',   text: '「普通はこうする」「みんなこうしている」で説明しがち', load: 'conform', reverse: true },
    { id: 's8',  group: '同調と比較',   text: '周りと違うやり方でも、理由があれば認める', load: 'confq' },
    { id: 's10', group: '一貫性',       text: '同じ失敗でも、自分の機嫌や状況で反応が変わってしまう', load: 'consistency', reverse: true },
    { id: 's11', group: '一貫性',       text: '言ったことと実際の対応が、ブレないようにしている', load: 'consistency' },
  ],

  // ───────── 家庭・子育て ─────────
  // §0（docs/応用_子育て.md §6）：育児メソッドでも診断でもない。型を子・親に貼らず「どんな配合か」を見るレンズ。
  family: [
    { id: 'f1',  group: '恐怖と安全',     text: '子どもは、失敗しても安心して親に話せている', load: 'fear' },
    { id: 'f2',  group: '恐怖と安全',     text: '言うことを聞かせるために、強い叱責や罰を使うことが多い', load: 'fear', reverse: true },
    { id: 'f12', group: '恐怖と安全',     text: '危険なこと（道路に飛び出す等）には、即・はっきり止める', load: 'crisis' },
    { id: 'f3',  group: '報酬とごほうび', text: '勉強や手伝いを、ごほうび・お小遣い・順位で動かすことが多い', load: 'rewardCtrl', reverse: true },
    { id: 'f4',  group: '報酬とごほうび', text: 'できたことは、ごほうびより先に「工夫した点」を具体的に認めている', load: 'reward' },
    { id: 'f11', group: '報酬とごほうび', text: '一度与えたごほうびや自由を取り上げると、強く反発する', load: 'kappa', reverse: true },
    { id: 'f5',  group: '学習と自走',     text: '時間がかかっても、本人にやり方を選ばせ、結果を本人に返している', load: 'learn' },
    { id: 'f6',  group: '学習と自走',     text: 'つい先回りして、代わりにやってあげてしまう', load: 'learn', reverse: true },
    { id: 'f7',  group: '同調と比較',     text: '「みんなやってる」「普通は」で行動を揃えさせがち', load: 'conform', reverse: true },
    { id: 'f8',  group: '同調と比較',     text: '他の子と比べず、昨日の本人と比べるようにしている', load: 'confq' },
    { id: 'f9',  group: '一貫性',         text: '同じことでも、親の機嫌でしかったり流したりすることがある', load: 'consistency', reverse: true },
    { id: 'f10', group: '一貫性',         text: '約束やルールは、ブレずに毎回同じ対応にしている', load: 'consistency' },
  ],
};

// 既存 import 互換（org をデフォルトの QUESTIONS として公開）
export const QUESTIONS = QUESTION_SETS.org;

// 1〜5 スケール（両端ラベルのみ画面表示）。全対象共通。
export const SCALE = [
  { v: 1, label: '全くそう思わない' },
  { v: 2, label: 'あまり' },
  { v: 3, label: 'どちらとも' },
  { v: 4, label: 'ややそう思う' },
  { v: 5, label: 'とてもそう思う' },
];

// 表示順を保ったグループ配列を返す（フォームのセクション分け用）。対象を引数で切替（既定 org）。
export function groupedQuestions(target = 'org') {
  const list = QUESTION_SETS[target] || QUESTION_SETS.org;
  const order = [];
  const map = new Map();
  for (const q of list) {
    if (!map.has(q.group)) { map.set(q.group, []); order.push(q.group); }
    map.get(q.group).push(q);
  }
  return order.map((g) => ({ group: g, items: map.get(g) }));
}
