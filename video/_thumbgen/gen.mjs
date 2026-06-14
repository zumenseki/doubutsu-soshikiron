import { writeFileSync } from 'fs';

const VID = "C:/Users/hayat/OneDrive/デスクトップ/動物実験から学ぶマネージメント理論/video";

const BAND = {
  green:  { grad:'linear-gradient(180deg,#e6efe9 0%, #d6e7dc 100%)', line:'#2f6f4f', shadow:'rgba(47,111,79,0.13)' },
  orange: { grad:'linear-gradient(180deg,#f7ece1 0%, #f1ddc9 100%)', line:'#d9893b', shadow:'rgba(217,137,59,0.16)' },
};

const ANIM = {
  wolf:{vb:'0 0 280 280', inner:'<polygon points="72,74 54,6 122,52" fill="#8a97a5"/><polygon points="208,74 226,6 158,52" fill="#8a97a5"/><ellipse cx="140" cy="150" rx="94" ry="88" fill="#9aa6b3"/><ellipse cx="140" cy="182" rx="52" ry="44" fill="#eef1f4"/><circle cx="111" cy="139" r="9" fill="#c9aa3c"/><circle cx="169" cy="139" r="9" fill="#c9aa3c"/><circle cx="111" cy="139" r="4" fill="#1d2321"/><circle cx="169" cy="139" r="4" fill="#1d2321"/><ellipse cx="140" cy="170" rx="14" ry="10" fill="#1d2321"/>'},
  hyena:{vb:'0 0 280 280', inner:'<polygon points="70,70 58,12 118,55" fill="#b8a48c"/><polygon points="210,70 222,12 162,55" fill="#b8a48c"/><ellipse cx="140" cy="150" rx="96" ry="86" fill="#c4b095"/><ellipse cx="140" cy="178" rx="56" ry="46" fill="#efe7d8"/><circle cx="108" cy="136" r="17" fill="#fff"/><circle cx="172" cy="136" r="17" fill="#fff"/><circle cx="110" cy="141" r="7.5" fill="#1d2321"/><circle cx="170" cy="141" r="7.5" fill="#1d2321"/><path d="M92,130 Q108,121 125,131" stroke="#8a7960" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M155,131 Q172,121 188,130" stroke="#8a7960" stroke-width="5" fill="none" stroke-linecap="round"/><ellipse cx="140" cy="166" rx="14" ry="10" fill="#1d2321"/>'},
  chimp:{vb:'0 0 280 280', inner:'<circle cx="56" cy="142" r="36" fill="#7a5230"/><circle cx="224" cy="142" r="36" fill="#7a5230"/><ellipse cx="140" cy="150" rx="86" ry="92" fill="#5a3a22"/><ellipse cx="140" cy="166" rx="64" ry="74" fill="#b98a5e"/><circle cx="117" cy="153" r="9" fill="#1d2321"/><circle cx="163" cy="153" r="9" fill="#1d2321"/><path d="M114,206 Q140,220 166,206" stroke="#3a2415" stroke-width="5" fill="none" stroke-linecap="round"/>'},
  ant:{vb:'0 0 280 280', inner:'<path d="M120,66 Q104,28 88,18" stroke="#5a2d1a" stroke-width="7" fill="none" stroke-linecap="round"/><path d="M160,66 Q176,28 192,18" stroke="#5a2d1a" stroke-width="7" fill="none" stroke-linecap="round"/><ellipse cx="140" cy="226" rx="50" ry="50" fill="#6b3320"/><ellipse cx="140" cy="150" rx="38" ry="42" fill="#8a4528"/><circle cx="140" cy="80" r="42" fill="#7a3b22"/><circle cx="126" cy="76" r="5" fill="#fff"/><circle cx="154" cy="76" r="5" fill="#fff"/>'},
  rat:{vb:'0 0 280 280', inner:'<circle cx="82" cy="102" r="32" fill="#e8aeb8"/><circle cx="198" cy="102" r="32" fill="#e8aeb8"/><ellipse cx="140" cy="154" rx="88" ry="86" fill="#9ca3a3"/><ellipse cx="140" cy="186" rx="52" ry="42" fill="#d7dddd"/><circle cx="116" cy="146" r="8" fill="#1d2321"/><circle cx="164" cy="146" r="8" fill="#1d2321"/><ellipse cx="140" cy="166" rx="12" ry="9" fill="#e8aeb8"/><rect x="126" y="196" width="12" height="24" rx="3" fill="#fff"/><rect x="142" y="196" width="12" height="24" rx="3" fill="#fff"/>'},
  capA:{vb:'0 0 280 280', inner:'<ellipse cx="140" cy="150" rx="92" ry="86" fill="#6b4a2f"/><path d="M70,120 Q140,40 210,120 Q200,150 140,150 Q80,150 70,120 Z" fill="#d8c4a8"/><ellipse cx="140" cy="172" rx="62" ry="64" fill="#caa878"/><circle cx="60" cy="150" r="30" fill="#6b4a2f"/><circle cx="220" cy="150" r="30" fill="#6b4a2f"/><circle cx="60" cy="150" r="15" fill="#caa878"/><circle cx="220" cy="150" r="15" fill="#caa878"/><ellipse cx="116" cy="156" rx="14" ry="16" fill="#fff"/><ellipse cx="164" cy="156" rx="14" ry="16" fill="#fff"/><circle cx="117" cy="159" r="7.5" fill="#1d2321"/><circle cx="163" cy="159" r="7.5" fill="#1d2321"/><path d="M104,138 L130,148" stroke="#3a2415" stroke-width="5" stroke-linecap="round"/><path d="M176,138 L150,148" stroke="#3a2415" stroke-width="5" stroke-linecap="round"/><ellipse cx="140" cy="186" rx="14" ry="10" fill="#3a2415"/><path d="M120,210 Q140,200 160,210" stroke="#3a2415" stroke-width="4" fill="none" stroke-linecap="round"/>'},
  capN:{vb:'0 0 280 280', inner:'<ellipse cx="140" cy="150" rx="92" ry="86" fill="#6b4a2f"/><path d="M70,120 Q140,40 210,120 Q200,150 140,150 Q80,150 70,120 Z" fill="#d8c4a8"/><ellipse cx="140" cy="172" rx="62" ry="64" fill="#caa878"/><circle cx="60" cy="150" r="30" fill="#6b4a2f"/><circle cx="220" cy="150" r="30" fill="#6b4a2f"/><circle cx="60" cy="150" r="15" fill="#caa878"/><circle cx="220" cy="150" r="15" fill="#caa878"/><ellipse cx="116" cy="156" rx="14" ry="16" fill="#fff"/><ellipse cx="164" cy="156" rx="14" ry="16" fill="#fff"/><circle cx="117" cy="159" r="7.5" fill="#1d2321"/><circle cx="163" cy="159" r="7.5" fill="#1d2321"/><path d="M104,140 L130,148" stroke="#3a2415" stroke-width="5" stroke-linecap="round"/><path d="M176,140 L150,148" stroke="#3a2415" stroke-width="5" stroke-linecap="round"/><ellipse cx="140" cy="186" rx="14" ry="10" fill="#3a2415"/><path d="M120,206 Q140,216 160,206" stroke="#3a2415" stroke-width="4" fill="none" stroke-linecap="round"/>'},
  hawk:{vb:'0 0 220 220', inner:'<path d="M110,44 L150,80 Q170,100 158,128 L150,140 Q130,158 110,158 Q90,158 70,140 L62,128 Q50,100 70,80 Z" fill="#c97a3a"/><path d="M150,80 Q186,70 200,52 Q176,86 158,96 Z" fill="#a8632a"/><path d="M70,80 Q34,70 20,52 Q44,86 62,96 Z" fill="#a8632a"/><path d="M110,150 L96,180 L110,172 L124,180 Z" fill="#a8632a"/><circle cx="92" cy="98" r="9" fill="#fff"/><circle cx="128" cy="98" r="9" fill="#fff"/><circle cx="93" cy="99" r="4.5" fill="#1d2321"/><circle cx="127" cy="99" r="4.5" fill="#1d2321"/><path d="M101,84 L86,76" stroke="#7a4a1e" stroke-width="5" stroke-linecap="round"/><path d="M119,84 L134,76" stroke="#7a4a1e" stroke-width="5" stroke-linecap="round"/><path d="M110,108 L98,120 L110,124 L122,120 Z" fill="#e3b23a"/>'},
  doveg:{vb:'0 0 220 220', inner:'<ellipse cx="110" cy="120" rx="56" ry="60" fill="#7fae90"/><ellipse cx="110" cy="138" rx="38" ry="42" fill="#a8cbb5"/><circle cx="110" cy="74" r="36" fill="#8fbb9f"/><path d="M160,108 Q196,96 206,76 Q190,118 166,128 Z" fill="#6f9d80"/><circle cx="98" cy="70" r="8" fill="#fff"/><circle cx="124" cy="70" r="8" fill="#fff"/><circle cx="99" cy="71" r="4" fill="#1d2321"/><circle cx="123" cy="71" r="4" fill="#1d2321"/><path d="M110,80 L122,86 L110,92 Z" fill="#e3b23a"/>'},
  peacock:{vb:'0 0 280 280', inner:'<path d="M140,130 C70,32 36,86 92,132 C52,140 64,210 124,176 C116,236 184,236 176,176 C236,210 248,140 208,132 C264,86 210,32 140,130Z" fill="#e6efe9" stroke="#2f6f4f" stroke-width="8"/><circle cx="92" cy="116" r="10" fill="#d9893b"/><circle cx="140" cy="86" r="10" fill="#d9893b"/><circle cx="208" cy="116" r="10" fill="#d9893b"/><ellipse cx="140" cy="164" rx="44" ry="64" fill="#2f6f4f"/><circle cx="122" cy="146" r="7" fill="#fff"/><circle cx="158" cy="146" r="7" fill="#fff"/><path d="M118,188 Q140,204 162,188" stroke="#1d2321" stroke-width="5" fill="none"/>'},
  gazelle:{vb:'0 0 280 280', inner:'<path d="M112,72 Q98,26 78,12" stroke="#5a3a22" stroke-width="8" fill="none"/><path d="M168,72 Q182,26 202,12" stroke="#5a3a22" stroke-width="8" fill="none"/><ellipse cx="140" cy="150" rx="78" ry="86" fill="#c99a62"/><ellipse cx="140" cy="180" rx="42" ry="46" fill="#f1ddbd"/><path d="M96,90 L56,52 L72,122" fill="#c99a62"/><path d="M184,90 L224,52 L208,122" fill="#c99a62"/><circle cx="116" cy="142" r="8" fill="#1d2321"/><circle cx="164" cy="142" r="8" fill="#1d2321"/><ellipse cx="140" cy="164" rx="13" ry="9" fill="#5a3a22"/><path d="M116,202 Q140,218 164,202" stroke="#5a3a22" stroke-width="5" fill="none"/>'},
};

const S = (a,w,h)=>({a,w,h});
const WORKS = [
  {dir:'reward-trap-explainer',     band:'orange', badge:'報酬の罠',      t1:'ご褒美が、',        t2:'やる気を奪う<span class="q">？</span>', layout:'right', gap:16, chars:[S('hyena',332,332)]},
  {dir:'controllability-explainer', band:'orange', badge:'学習性無力感',  t1:'なぜ人は、',        t2:'あきらめるのか<span class="q">？</span>', layout:'right', gap:16, chars:[S('wolf',332,332)]},
  {dir:'crowding-out-explainer',    band:'orange', badge:'動機の締め出し', t1:'お金を払うと、',     t2:'善意が消える<span class="q">？</span>', layout:'right', gap:16, chars:[S('hyena',332,332)]},
  {dir:'unfairness-cost-explainer', band:'orange', badge:'不公平のコスト', t1:'同じ給料でも、',     t2:'なぜ不満が爆発<span class="q">？</span>', layout:'right', gap:16, chars:[S('capA',332,332)]},
  {dir:'bank-run-explainer',        band:'orange', badge:'取り付け騒ぎ',   t1:'銀行はなぜ、',       t2:'一夜で潰れる<span class="q">？</span>', layout:'center', gap:26, chars:[S('ant',182,182),S('ant',182,182),S('ant',182,182)]},
  {dir:'uprising-explainer',        band:'green',  badge:'蜂起のメカニズム', t1:'なぜ人は、',        t2:'一斉に立つ<span class="q">？</span>', layout:'center', gap:26, chars:[S('ant',182,182),S('ant',182,182),S('ant',182,182)]},
  {dir:'negotiation-explainer',     band:'green',  badge:'交渉の科学',      t1:'引けない者が、',     t2:'なぜ勝つ<span class="q">？</span>', layout:'center', gap:48, chars:[S('hawk',238,238),S('doveg',238,238)]},
  {dir:'recruitment-explainer',     band:'green',  badge:'採用の科学',      t1:'経歴は、',          t2:'クジャクの尾', layout:'center', gap:36, chars:[S('peacock',268,268),S('gazelle',252,252)]},
  {dir:'price-explainer',           band:'green',  badge:'価格の心理',      t1:'安くすれば、',       t2:'売れるは本当<span class="q">？</span>', layout:'right', gap:16, chars:[S('capN',332,332)]},
  {dir:'status-explainer',          band:'orange', badge:'地位とストレス',  t1:'順位が、',          t2:'体を蝕む', layout:'right', gap:16, chars:[S('chimp',332,332)]},
  {dir:'procrastination-explainer', band:'orange', badge:'先延ばしの正体',  t1:'「明日やる」が、',   t2:'嘘になる理由', layout:'right', gap:16, chars:[S('hyena',332,332)]},
  {dir:'precedent-lockin-explainer',band:'orange', badge:'規範ロックイン',  t1:'「前からこう」が、', t2:'会社を殺す<span class="q">？</span>', layout:'center', gap:40, chars:[S('ant',252,252),S('wolf',252,252)]},
];

const svgTag = (c)=>`<svg width="${c.w}" height="${c.h}" viewBox="${ANIM[c.a].vb}">${ANIM[c.a].inner}</svg>`;
const rowCss = (w)=> w.layout==='right'
  ? 'right:120px; bottom:24px;'
  : 'left:0; right:0; bottom:30px; justify-content:center;';

const tpl = (w)=>`<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
  * { box-sizing: border-box; }
  body { margin:0; background:#faf8f4; font-family:"Noto Sans JP","Yu Gothic UI",Meiryo,sans-serif; }
  #root { position:relative; width:1280px; height:720px; overflow:hidden; background:#faf8f4; }
  .band { position:absolute; left:0; right:0; bottom:0; height:296px; background:${BAND[w.band].grad}; }
  .band:before { content:""; position:absolute; left:0; right:0; top:0; height:7px; background:${BAND[w.band].line}; opacity:0.29; }
  .kicker { position:absolute; left:60px; top:52px; font-weight:800; font-size:31px; color:#2f6f4f; letter-spacing:0.08em; background:#e6efe9; padding:11px 30px; border-radius:999px; }
  .badge { position:absolute; right:54px; top:50px; font-weight:900; font-size:34px; color:#fff; background:#d9893b; padding:13px 32px; border-radius:14px; box-shadow:0 9px 0 rgba(184,110,40,0.30); }
  .titlewrap { position:absolute; left:66px; top:154px; }
  .t1 { font-weight:900; font-size:62px; color:#1d2321; letter-spacing:-0.01em; white-space:nowrap; }
  .t2 { font-weight:900; font-size:120px; line-height:1.0; color:#d9893b; white-space:nowrap; letter-spacing:-0.02em; text-shadow:0 6px 0 rgba(29,35,33,0.14); margin-top:6px; }
  .t2 .q { color:#1d2321; }
  .row { position:absolute; ${rowCss(w)} display:flex; gap:${w.gap}px; align-items:flex-end; }
  .row svg { filter:drop-shadow(0 11px 0 ${BAND[w.band].shadow}); }
</style>
</head>
<body>
  <div id="root" data-composition-id="main" data-width="1280" data-height="720" data-start="0" data-duration="1">
    <div class="band"></div>
    <div class="kicker">動物行動学 × マネジメント</div>
    <div class="badge">${w.badge}</div>
    <div class="titlewrap">
      <div class="t1">${w.t1}</div>
      <div class="t2">${w.t2}</div>
    </div>
    <div class="row">${w.chars.map(svgTag).join('')}</div>
  </div>
  <script>window.__timelines = window.__timelines || {}; var tl = gsap.timeline({ paused: true }); window.__timelines["main"] = tl;</script>
</body>
</html>
`;

for (const w of WORKS) {
  writeFileSync(`${VID}/${w.dir}/thumbnail.html`, tpl(w));
  console.log('wrote', w.dir);
}
console.log('done', WORKS.length);
