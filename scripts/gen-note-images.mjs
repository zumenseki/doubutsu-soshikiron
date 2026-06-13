// note アイキャッチ画像 一括生成（依存ゼロ：システムChromeを --headless --screenshot で直叩き）
// 実行: node scripts/gen-note-images.mjs            -> 全39枚
//       node scripts/gen-note-images.mjs <slug>     -> 1枚だけ（サンプル確認用）
// 出力: note-images/<slug>.png（1280x670）。タイトルは note 用最適化版を内蔵辞書で保持。
import { writeFileSync, mkdirSync, existsSync, rmSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const OUT = 'note-images';
const TMP = 'note-images/_tmp';

const EMOJI = {
  'connection-ethology':'🐵','wolf-ethology':'🐺','ant-ethology':'🐜','chimp-ethology':'🐵',
  'bonobo-ethology':'🦧','hyena-ethology':'🐆','swarm-ethology':'🐝','mobbing-ethology':'🐦‍⬛',
  'recruitment-ethology':'🦚','negotiation-ethology':'🦅','cooperation-ethology':'🦇',
  'parasitism-ethology':'🐦','territory-ethology':'🦁','play-ethology':'🐶','controllability':'🐕',
  'sales-ethology':'🐭','habit-ethology':'🐀','one-trial-ethology':'🐀','status-ethology':'🐒',
  'hedonic-treadmill-ethology':'🐒','procrastination-ethology':'🕊️','foraging-ethology':'🦌',
  'unfairness-cost':'🍇','industry-ethology':'🦈','evolution-ethology':'🧬','diagnosis-ethology':'🔬',
  'uprising':'✊','bank-run':'🏦','crowding-out':'💰','reward-trap':'🥕','precedent-lockin':'🦖',
  'five-types-ethology':'🦓','division-of-labor-ethology':'🐜','hierarchy-design':'🐜',
  'rewilding':'🐺','dunbar-wall':'👥','fear-kills-learning':'🙈','price-ethology':'🏷️',
  'attribution-ethology':'🐦','fear-kills-learning-dialogue':'🦉🐤','reward-trap-dialogue':'🦉🐤','controllability-dialogue':'🦉🐤','five-types-ethology-dialogue':'🦉🐤',
  'parenting-types':'🐾','parenting-helplessness':'🐕','parenting-praise':'🦜',
  'parenting-reward':'🎨','parenting-consistency':'🎲','parenting-fear':'🥢',
};
const ORANGE=['#E8943A','#B96A22'], RED=['#C0504D','#8F3330'], BLUE=['#3E6E9E','#274C72'],
      PURPLE=['#6E5C9E','#473A6E'], GREEN=['#4E8C5A','#2F5C39'], TEAL=['#2F8F8F','#1C6060'],
      ROSE=['#C76B8E','#8E4763'];
const CAT = {
  'sales-ethology':ORANGE,'price-ethology':ORANGE,'reward-trap':ORANGE,'hedonic-treadmill-ethology':ORANGE,
  'crowding-out':ORANGE,'attribution-ethology':ORANGE,'recruitment-ethology':ORANGE,'negotiation-ethology':ORANGE,'unfairness-cost':ORANGE,'reward-trap-dialogue':ORANGE,
  'controllability':RED,'fear-kills-learning':RED,'one-trial-ethology':RED,'fear-kills-learning-dialogue':RED,'controllability-dialogue':RED,
  'habit-ethology':BLUE,'procrastination-ethology':BLUE,'foraging-ethology':BLUE,'play-ethology':BLUE,'connection-ethology':BLUE,
  'swarm-ethology':PURPLE,'mobbing-ethology':PURPLE,'uprising':PURPLE,'bank-run':PURPLE,'dunbar-wall':PURPLE,
  'five-types-ethology':GREEN,'five-types-ethology-dialogue':GREEN,'wolf-ethology':GREEN,'ant-ethology':GREEN,'chimp-ethology':GREEN,'bonobo-ethology':GREEN,
  'hyena-ethology':GREEN,'hierarchy-design':GREEN,'evolution-ethology':GREEN,'industry-ethology':GREEN,
  'division-of-labor-ethology':GREEN,'rewilding':GREEN,'precedent-lockin':GREEN,
  'cooperation-ethology':TEAL,'territory-ethology':TEAL,'parasitism-ethology':TEAL,'diagnosis-ethology':TEAL,
  'parenting-types':ROSE,'parenting-helplessness':ROSE,'parenting-praise':ROSE,
  'parenting-reward':ROSE,'parenting-consistency':ROSE,'parenting-fear':ROSE,
};
// note 用 最終タイトル（最適化17本＋現行22本）
const TITLE = {
  'sales-ethology':'なぜ「あの人」だけ売れるのか — ネズミとサルが先に知っていた営業の正体',
  'price-ethology':'「とりあえず値下げ」が会社を弱らせる — 価格と脳の錯覚',
  'recruitment-ethology':'あなたの職務経歴書は「クジャクの尾」だ — 採用の動物行動学',
  'negotiation-ethology':'交渉で勝つのは「退路を断った」方だ — タカとハトの進化ゲーム',
  'reward-trap':'インセンティブを強めたら不正が増えた — 報酬設計の罠',
  'crowding-out':'罰金を導入したら遅刻が「増えた」— お金が善意を締め出すとき',
  'habit-ethology':'三日坊主は意志の弱さではない — 習慣を作る「きっかけ」の設計',
  'one-trial-ethology':'たった一度の失敗が一生消えない理由 — ガルシア効果',
  'foraging-ethology':'「成功を続けろ」が次の成功を殺す — 撤退タイミングの科学',
  'ant-ethology':'アリに上司はいない、なのに分業する — アリ型組織の動物行動学',
  'bonobo-ethology':'チンパンジーと同じDNAで、殺し合わないサル — ボノボ型組織',
  'hyena-ethology':'生まれた瞬間に「勝ち組」が決まる社会 — ハイエナ型組織',
  'status-ethology':'「2番手」が一番早く老ける — 地位とストレスの科学',
  'cooperation-ethology':'「いい人」だから協力するのではない — 協力が生まれる3条件',
  'parasitism-ethology':'カッコウに学ぶ「タダ乗り」の見抜き方 — 托卵と寄生',
  'fear-kills-learning':'悪い知らせほど上がってこない — 恐怖が学習を殺す仕組み',
  'fear-kills-learning-dialogue':'〔対話〕悪い知らせほど、なぜ上がってこないのか',
  'reward-trap-dialogue':'〔対話〕ボーナスを増やしたのに、なぜ熱が上がらないのか',
  'controllability-dialogue':'〔対話〕同じ強さで叱っても、なぜ育つ人と潰れる人がいるのか',
  'five-types-ethology-dialogue':'〔対話〕うちは何型だろう、で止まる人へ',
  'diagnosis-ethology':'「うちの社風」を数字で測る方法 — 行動で組織を診断する',
  'connection-ethology':'怖いとき、子ザルがしがみついたのは餌より布だった — つながりの動物行動学',
  'attribution-ethology':'「たまたま」を実力と誤解する脳 — 帰属の動物行動学',
  'procrastination-ethology':'「明日やる」がなぜ嘘になるのか — 先延ばしの動物行動学',
  'five-types-ethology':'あなたの組織は、どの動物の群れか — 組織の5類型',
  'wolf-ethology':'「アルファオオカミ」は誤解だった — オオカミ型組織の動物行動学',
  'chimp-ethology':'社内政治は、チンパンジーが先に発明していた — チンパン型組織の動物行動学',
  'evolution-ethology':'なぜ大企業は必ず老いるのか — 組織進化の動物行動学',
  'hierarchy-design':'全社を一つの型で揃えると、なぜ弱くなるのか — 階層別の最適化',
  'industry-ethology':'同じ「営業」でも最適な群れは逆になる — 業種の動物行動学',
  'swarm-ethology':'ミツバチはどう「みんなで決める」か — 群れの意思決定の動物行動学',
  'mobbing-ethology':'群れはなぜ一匹を狩るのか — 同調圧力の動物行動学',
  'dunbar-wall':'人を増やすと、組織は「ある日」急に壊れる — 数の壁',
  'uprising':'なぜ人は耐え、ある日いっせいに立つのか — 蜂起の心理学',
  'bank-run':'銀行はなぜ一夜で倒れるのか — 取り付け騒ぎの心理学',
  'unfairness-cost':'同じ総額でも、不公平は組織を壊す — サルが教える代償',
  'territory-ethology':'なぜ部門は資源を抱え込むのか — 縄張りの動物行動学',
  'play-ethology':'よく遊ぶ動物ほど、よく学ぶ — 遊びの動物行動学',
  'controllability':'罰が効くかは「強さ」ではなく「避けられるか」で決まる',
  'precedent-lockin':'「前からこうだ」の正体 — Blockbuster はなぜ Netflix を逃したか',
  'rewilding':'号令では、固まった組織は動かない — 再野生化の生態学',
  'division-of-labor-ethology':'誰も指示していないのに、仕事は割り振られる — 分業の動物行動学',
  'hedonic-treadmill-ethology':'昇給はなぜ一度しか効かないのか — 快楽順応の動物行動学',
  'parenting-types':'あなたの家庭は、どの動物の群れか — 子育ての四つのダイヤル',
  'parenting-helplessness':'「厳しい親」と「優しすぎる親」が、同じ無力感の子を育てる',
  'parenting-praise':'「頭がいいね」が、子どもの挑戦を殺す — ほめ方の符号',
  'parenting-reward':'ご褒美で勉強させると、勉強嫌いになる — お絵描きの逆説',
  'parenting-consistency':'何度言っても直らないのは、叱り方が弱いからではない',
  'parenting-fear':'「アメとムチ」は一本のダイヤルではない — 止める力と育てる力',
};

const onlyArg = process.argv[2];
if (!existsSync(OUT)) mkdirSync(OUT, { recursive: true });
if (!existsSync(TMP)) mkdirSync(TMP, { recursive: true });

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
function fontSize(t) { const n = t.length; return n <= 18 ? 66 : n <= 28 ? 56 : n <= 40 ? 48 : 42; }
function html(title, emoji, [c1, c2], slug) {
  const brand = (slug && slug.startsWith('parenting')) ? '🐾 動物から読む子育て' : '🐾 動物行動学シリーズ';
  return `<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1280px;height:670px;overflow:hidden}
.card{width:1280px;height:670px;display:flex;flex-direction:column;align-items:center;justify-content:center;
background:linear-gradient(135deg,${c1},${c2});position:relative;
font-family:"Yu Gothic","Meiryo","Hiragino Kaku Gothic ProN","Segoe UI Emoji",sans-serif}
.emoji{font-size:250px;line-height:1;filter:drop-shadow(0 10px 22px rgba(0,0,0,.32))}
.title{margin-top:22px;max-width:1120px;text-align:center;color:#fff;font-weight:800;
font-size:${fontSize(title)}px;line-height:1.38;text-shadow:0 3px 14px rgba(0,0,0,.45);padding:0 44px}
.brand{position:absolute;bottom:0;left:0;right:0;height:72px;background:rgba(0,0,0,.30);
display:flex;align-items:center;justify-content:space-between;padding:0 46px;color:#fff}
.brand .s{font-size:29px;font-weight:700;letter-spacing:.04em}
.brand .u{font-size:21px;opacity:.85}
</style></head><body><div class="card">
<div class="emoji">${emoji}</div>
<div class="title">${esc(title)}</div>
<div class="brand"><span class="s">${brand}</span><span class="u">zumenseki.github.io/doubutsu-soshikiron</span></div>
</div></body></html>`;
}

const slugs = onlyArg ? [onlyArg] : Object.keys(TITLE);
let n = 0;
for (const slug of slugs) {
  const title = TITLE[slug];
  if (!title) { console.warn('skip (no title):', slug); continue; }
  const emoji = EMOJI[slug] || '🐾';
  const col = CAT[slug] || TEAL;
  const tmpHtml = resolve(join(TMP, `${slug}.html`));
  writeFileSync(tmpHtml, html(title, emoji, col, slug), 'utf8');
  const outPng = resolve(join(OUT, `${slug}.png`));
  execFileSync(CHROME, ['--headless=new', '--disable-gpu', '--hide-scrollbars',
    `--screenshot=${outPng}`, '--window-size=1280,670', '--force-device-scale-factor=1',
    `file://${tmpHtml.replace(/\\/g, '/')}`], { stdio: 'ignore' });
  console.log('generated', slug);
  n++;
}
try { rmSync(TMP, { recursive: true, force: true }); } catch {}
console.log(`done: ${n} image(s) -> ${OUT}/`);
