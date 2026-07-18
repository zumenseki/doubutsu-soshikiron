// Member-series note header images.
// Zero-cost pipeline: write local HTML/SVG, then capture with system Chrome.
// Usage: node scripts/gen-member-images.mjs
// Output: note-images/measure-conformity-v2.png and note-images/measure-helplessness-v2.png
import { existsSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const OUT_DIR = 'note-images';
const TMP_DIR = 'note-images/_tmp-member';
const WIDTH = 1280;
const HEIGHT = 670;

const images = {
  'measure-conformity-v2': conformitySvg,
  'measure-helplessness-v2': helplessnessSvg,
};

function html(svg) {
  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: ${WIDTH}px; height: ${HEIGHT}px; overflow: hidden; background: #0f3438; }
    svg { display: block; width: ${WIDTH}px; height: ${HEIGHT}px; }
  </style>
</head>
<body>${svg}</body>
</html>`;
}

function bird({ x, y, s = 1, fill = '#d8ece8', wing = '#b9d2ce', stroke = '#719795', opacity = 1, flip = false, rotate = 0 }) {
  const scale = flip ? `scale(${-s} ${s})` : `scale(${s})`;
  return `<g transform="translate(${x} ${y}) rotate(${rotate}) ${scale}" opacity="${opacity}">
    <path d="M-42 3 C-26 -12 9 -18 38 -7 C55 -1 56 10 37 18 C6 31 -27 22 -42 3 Z" fill="${fill}" stroke="${stroke}" stroke-width="1.35"/>
    <path d="M-18 -2 C-2 -44 40 -72 86 -57 C52 -42 26 -23 4 5 Z" fill="${wing}" opacity=".78" stroke="${stroke}" stroke-width="1" stroke-opacity=".22"/>
    <path d="M-11 7 C4 41 43 54 80 34 C50 28 22 16 3 0 Z" fill="${wing}" opacity=".56" stroke="${stroke}" stroke-width="1" stroke-opacity=".18"/>
    <path d="M-39 3 C-60 -6 -77 -3 -95 -14 C-83 2 -65 13 -42 12 Z" fill="${fill}" opacity=".92"/>
    <path d="M39 -8 C49 -17 62 -17 72 -7 C61 -5 50 -2 40 1 Z" fill="${fill}" stroke="${stroke}" stroke-width="1" stroke-opacity=".18"/>
    <path d="M54 -5 C68 -9 82 -5 96 4 C78 6 66 9 51 8 Z" fill="${fill}"/>
    <path d="M-5 -3 C8 -11 25 -11 42 -3" fill="none" stroke="#ffffff" stroke-width="2.1" stroke-opacity=".30" stroke-linecap="round"/>
    <path d="M-1 -1 C13 -18 33 -32 61 -43" fill="none" stroke="#ffffff" stroke-width="1.35" stroke-opacity=".22" stroke-linecap="round"/>
    <path d="M2 6 C20 14 40 21 64 25" fill="none" stroke="#315b5f" stroke-width="1" stroke-opacity=".20" stroke-linecap="round"/>
    <path d="M-33 3 C-13 13 14 16 38 9" fill="none" stroke="#315b5f" stroke-width="1" stroke-opacity=".15" stroke-linecap="round"/>
    <circle cx="59" cy="-8" r="1.9" fill="#102d31" opacity=".76"/>
  </g>`;
}

function conformitySvg() {
  const flock = [
    [138, 170, .70, -2], [250, 152, .76, 1], [366, 174, .70, -1], [482, 153, .74, 2],
    [602, 176, .70, -1], [724, 154, .76, 1], [838, 176, .68, -2], [954, 154, .72, 2],
    [1084, 178, .66, -1],
    [176, 292, .90, 1], [304, 272, .86, -2], [438, 294, .88, 1], [568, 274, .84, -1],
    [826, 294, .90, 2], [960, 274, .86, -1], [1096, 296, .82, 1],
    [116, 426, .72, -1], [242, 408, .78, 2], [370, 430, .76, -1], [502, 410, .74, 1],
    [632, 430, .78, -1], [764, 410, .74, 2], [896, 430, .78, -2], [1030, 410, .76, 1],
    [1160, 432, .70, -1],
  ];
  const birds = flock
    .map(([x, y, s, r]) => bird({ x, y, s, rotate: r, opacity: y < 220 ? .58 : .78 }))
    .join('\n');

  return `<svg viewBox="0 0 ${WIDTH} ${HEIGHT}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="">
  <defs>
    <linearGradient id="conformBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0f4a54"/>
      <stop offset="48%" stop-color="#1f7677"/>
      <stop offset="100%" stop-color="#9fc8bf"/>
    </linearGradient>
    <radialGradient id="conformGlow" cx="54%" cy="48%" r="46%">
      <stop offset="0%" stop-color="#f0a35a" stop-opacity=".34"/>
      <stop offset="48%" stop-color="#f0a35a" stop-opacity=".10"/>
      <stop offset="100%" stop-color="#f0a35a" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="vignette" cx="50%" cy="45%" r="72%">
      <stop offset="60%" stop-color="#0b2c31" stop-opacity="0"/>
      <stop offset="100%" stop-color="#082b31" stop-opacity=".42"/>
    </radialGradient>
    <filter id="paperGrain" x="-10%" y="-10%" width="120%" height="120%">
      <feTurbulence type="fractalNoise" baseFrequency=".82" numOctaves="2" seed="12" result="noise"/>
      <feColorMatrix in="noise" type="saturate" values="0"/>
      <feComponentTransfer>
        <feFuncA type="table" tableValues="0 .08"/>
      </feComponentTransfer>
      <feBlend in="SourceGraphic" mode="multiply"/>
    </filter>
    <filter id="softShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="12" stdDeviation="10" flood-color="#073034" flood-opacity=".28"/>
    </filter>
    <filter id="softBlur">
      <feGaussianBlur stdDeviation="18"/>
    </filter>
  </defs>
  <rect width="${WIDTH}" height="${HEIGHT}" fill="url(#conformBg)"/>
  <rect width="${WIDTH}" height="${HEIGHT}" fill="#ffffff" opacity=".06" filter="url(#paperGrain)"/>
  <circle cx="702" cy="344" r="282" fill="url(#conformGlow)"/>
  <path d="M-30 226 C185 154 350 218 538 190 C760 156 935 92 1324 154" fill="none" stroke="#d6eee8" stroke-opacity=".18" stroke-width="18" filter="url(#softBlur)"/>
  <path d="M-20 492 C184 420 366 478 548 446 C760 410 964 344 1324 394" fill="none" stroke="#d6eee8" stroke-opacity=".13" stroke-width="16" filter="url(#softBlur)"/>
  <path d="M60 214 C310 154 565 190 830 142 C1014 108 1136 112 1238 140" fill="none" stroke="#e4f3ee" stroke-opacity=".18" stroke-width="3"/>
  <path d="M42 458 C276 390 520 436 760 390 C962 352 1110 354 1236 388" fill="none" stroke="#e4f3ee" stroke-opacity=".14" stroke-width="3"/>
  <g filter="url(#softShadow)">
    ${birds}
    <circle cx="694" cy="292" r="74" fill="#f0a35a" opacity=".12"/>
    <circle cx="694" cy="292" r="106" fill="none" stroke="#f4b06a" stroke-width="3" stroke-opacity=".18"/>
    ${bird({ x: 694, y: 292, s: 1.08, fill: '#d8853f', wing: '#b8622e', stroke: '#8f542d', flip: true, rotate: -3 })}
  </g>
  <path d="M0 618 C250 584 386 636 604 604 C824 572 1000 608 1280 566 L1280 670 L0 670 Z" fill="#083238" opacity=".16"/>
  <rect width="${WIDTH}" height="${HEIGHT}" fill="url(#vignette)"/>
</svg>`;
}

function dogLying() {
  return `<g transform="translate(330 448)">
    <ellipse cx="72" cy="73" rx="230" ry="49" fill="#34414a" opacity=".24"/>
    <path d="M-94 20 C-58 -62 54 -96 156 -73 C242 -54 306 0 294 62 C281 126 178 150 48 132 C-62 116 -132 86 -94 20 Z" fill="url(#dogBody)" stroke="#6f6a63" stroke-opacity=".34" stroke-width="2"/>
    <path d="M-148 38 C-154 2 -128 -36 -82 -48 C-34 -61 14 -40 28 0 C42 39 8 68 -50 76 C-104 84 -141 68 -148 38 Z" fill="url(#dogHead)" stroke="#706a62" stroke-opacity=".35" stroke-width="2"/>
    <path d="M-142 34 C-162 27 -187 32 -198 46 C-207 58 -194 69 -170 68 C-148 67 -132 56 -118 45 Z" fill="#aa9e8e" stroke="#6e675f" stroke-opacity=".25" stroke-width="2"/>
    <ellipse cx="-196" cy="50" rx="9.5" ry="7" fill="#303a40" opacity=".80"/>
    <path d="M-88 -36 C-124 -66 -128 -104 -94 -114 C-58 -124 -39 -84 -48 -41 Z" fill="#776f65"/>
    <path d="M-3 -40 C20 -74 55 -78 68 -52 C82 -24 43 -10 14 -16 Z" fill="#7a7167"/>
    <path d="M-122 37 C-96 24 -61 21 -24 31" fill="none" stroke="#c0b4a3" stroke-width="8" stroke-linecap="round" opacity=".25"/>
    <ellipse cx="-62" cy="12" rx="5.2" ry="3.7" fill="#27323a" opacity=".76"/>
    <path d="M-73 7 C-61 1 -47 2 -36 10" fill="none" stroke="#5b574f" stroke-width="2.3" stroke-linecap="round" opacity=".34"/>
    <path d="M-133 83 C-91 98 -28 99 36 86" fill="none" stroke="#6a635b" stroke-width="10" stroke-linecap="round" opacity=".56"/>
    <path d="M-116 92 C-66 110 16 111 100 96" fill="none" stroke="#8d8172" stroke-width="20" stroke-linecap="round" opacity=".72"/>
    <path d="M36 90 C104 106 190 101 252 78" fill="none" stroke="#6a635b" stroke-width="11" stroke-linecap="round" opacity=".50"/>
    <path d="M224 3 C274 -27 320 -9 340 26" fill="none" stroke="#8d8172" stroke-width="20" stroke-linecap="round"/>
    <g fill="none" stroke="#c4b8a7" stroke-linecap="round" opacity=".28">
      <path d="M-4 -54 C50 -62 116 -50 174 -19"/>
      <path d="M6 -34 C82 -42 164 -19 228 24"/>
      <path d="M-56 -48 C-24 -61 20 -63 68 -55"/>
      <path d="M-105 -11 C-72 -28 -29 -31 12 -19"/>
      <path d="M-74 55 C-9 69 70 67 152 48"/>
      <path d="M28 11 C96 7 166 24 232 58"/>
    </g>
    <g fill="none" stroke="#5c5750" stroke-linecap="round" opacity=".20">
      <path d="M-56 -31 C-20 -45 24 -45 66 -30"/>
      <path d="M52 -55 C116 -48 176 -22 238 29"/>
      <path d="M-8 78 C62 91 154 85 238 60"/>
    </g>
  </g>`;
}

function dogStanding() {
  return `<g transform="translate(952 367) scale(.54)" opacity=".86">
    <ellipse cx="100" cy="112" rx="132" ry="28" fill="#35414a" opacity=".18"/>
    <path d="M-22 18 C18 -22 114 -34 184 4 C236 32 252 92 206 124 C160 156 48 148 -8 118 C-48 96 -58 54 -22 18 Z" fill="url(#dogSmall)" stroke="#756e65" stroke-opacity=".34" stroke-width="3"/>
    <circle cx="-42" cy="16" r="44" fill="#aaa092"/>
    <path d="M-72 -18 C-98 -52 -90 -76 -62 -66 C-44 -58 -40 -34 -42 -12 Z" fill="#837970"/>
    <path d="M-12 -22 C14 -54 42 -56 40 -28 C38 -8 12 2 -4 4 Z" fill="#837970"/>
    <circle cx="-60" cy="4" r="4" fill="#30383d" opacity=".72"/>
    <ellipse cx="-86" cy="18" rx="8" ry="6" fill="#333b40" opacity=".65"/>
    <path d="M10 112 L-2 184" stroke="#8a8279" stroke-width="24" stroke-linecap="round"/>
    <path d="M78 124 L70 188" stroke="#8a8279" stroke-width="24" stroke-linecap="round"/>
    <path d="M150 118 L168 184" stroke="#8a8279" stroke-width="23" stroke-linecap="round"/>
    <path d="M208 96 C254 70 292 80 316 116" fill="none" stroke="#9c9386" stroke-width="18" stroke-linecap="round"/>
    <path d="M-10 20 C56 -1 138 8 208 58" fill="none" stroke="#c6bbac" stroke-opacity=".26" stroke-width="4" stroke-linecap="round"/>
  </g>`;
}

function helplessnessSvg() {
  return `<svg viewBox="0 0 ${WIDTH} ${HEIGHT}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="">
  <defs>
    <linearGradient id="helplessBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#d9dee1"/>
      <stop offset="52%" stop-color="#87939e"/>
      <stop offset="100%" stop-color="#46535f"/>
    </linearGradient>
    <radialGradient id="quietLight" cx="31%" cy="22%" r="58%">
      <stop offset="0%" stop-color="#f3ebe0" stop-opacity=".54"/>
      <stop offset="58%" stop-color="#f3ebe0" stop-opacity=".12"/>
      <stop offset="100%" stop-color="#f3ebe0" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#7b8790"/>
      <stop offset="100%" stop-color="#56626b"/>
    </linearGradient>
    <linearGradient id="dogBody" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#b6a996"/>
      <stop offset="52%" stop-color="#928674"/>
      <stop offset="100%" stop-color="#6d675f"/>
    </linearGradient>
    <linearGradient id="dogHead" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#b8ad9c"/>
      <stop offset="62%" stop-color="#978b7a"/>
      <stop offset="100%" stop-color="#746b61"/>
    </linearGradient>
    <linearGradient id="dogSmall" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#b3a898"/>
      <stop offset="100%" stop-color="#867d71"/>
    </linearGradient>
    <linearGradient id="wood" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#cfc6b6"/>
      <stop offset="45%" stop-color="#b9b0a3"/>
      <stop offset="100%" stop-color="#ddd5c8"/>
    </linearGradient>
    <radialGradient id="helplessVignette" cx="45%" cy="42%" r="74%">
      <stop offset="58%" stop-color="#27333b" stop-opacity="0"/>
      <stop offset="100%" stop-color="#27333b" stop-opacity=".28"/>
    </radialGradient>
    <filter id="quietGrain" x="-10%" y="-10%" width="120%" height="120%">
      <feTurbulence type="fractalNoise" baseFrequency=".72" numOctaves="2" seed="23" result="noise"/>
      <feColorMatrix in="noise" type="saturate" values="0"/>
      <feComponentTransfer>
        <feFuncA type="table" tableValues="0 .07"/>
      </feComponentTransfer>
      <feBlend in="SourceGraphic" mode="multiply"/>
    </filter>
    <filter id="dogShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="13" stdDeviation="10" flood-color="#27323a" flood-opacity=".25"/>
    </filter>
    <filter id="mist">
      <feGaussianBlur stdDeviation="20"/>
    </filter>
  </defs>
  <rect width="${WIDTH}" height="${HEIGHT}" fill="url(#helplessBg)"/>
  <rect width="${WIDTH}" height="${HEIGHT}" fill="url(#quietLight)"/>
  <rect width="${WIDTH}" height="${HEIGHT}" fill="#ffffff" opacity=".05" filter="url(#quietGrain)"/>
  <circle cx="200" cy="130" r="170" fill="#eef0ee" opacity=".15" filter="url(#mist)"/>
  <path d="M0 454 C184 424 352 468 540 438 C776 400 1008 426 1280 392 L1280 670 L0 670 Z" fill="url(#ground)"/>
  <path d="M0 548 C232 518 434 566 646 536 C870 504 1056 520 1280 492 L1280 670 L0 670 Z" fill="#44515b" opacity=".34"/>

  <g opacity=".72">
    <path d="M598 393 H980" stroke="url(#wood)" stroke-width="24" stroke-linecap="round"/>
    <path d="M588 326 V435" stroke="#c9c0b3" stroke-width="22" stroke-linecap="round"/>
    <path d="M986 316 V428" stroke="#c9c0b3" stroke-width="22" stroke-linecap="round"/>
    <path d="M1018 396 H1118" stroke="url(#wood)" stroke-width="18" stroke-linecap="round" opacity=".36"/>
    <path d="M622 388 C720 376 846 382 955 392" fill="none" stroke="#8f877d" stroke-width="3" stroke-opacity=".22" stroke-linecap="round"/>
    <path d="M608 400 C716 407 846 405 969 397" fill="none" stroke="#f4ead9" stroke-width="2" stroke-opacity=".20" stroke-linecap="round"/>
  </g>
  <path d="M602 405 H842" stroke="#67737c" stroke-width="3" stroke-opacity=".22"/>
  <path d="M986 407 H1115" stroke="#67737c" stroke-width="3" stroke-opacity=".14"/>

  <g filter="url(#dogShadow)">
    ${dogStanding()}
    ${dogLying()}
  </g>
  <path d="M110 566 C272 526 458 566 620 542 C758 522 920 542 1124 512" fill="none" stroke="#d7dedc" stroke-width="3" stroke-opacity=".12"/>
  <path d="M132 606 C304 578 472 614 664 588 C840 564 1002 580 1168 552" fill="none" stroke="#d7dedc" stroke-width="3" stroke-opacity=".10"/>
  <rect width="${WIDTH}" height="${HEIGHT}" fill="url(#helplessVignette)"/>
</svg>`;
}

if (!existsSync(CHROME)) {
  throw new Error(`Chrome not found: ${CHROME}`);
}
if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });
if (!existsSync(TMP_DIR)) mkdirSync(TMP_DIR, { recursive: true });

let count = 0;
for (const [slug, makeSvg] of Object.entries(images)) {
  const tmpHtml = resolve(join(TMP_DIR, `${slug}.html`));
  const outPng = resolve(join(OUT_DIR, `${slug}.png`));
  writeFileSync(tmpHtml, html(makeSvg()), 'utf8');
  execFileSync(CHROME, [
    '--headless=new',
    '--disable-gpu',
    '--hide-scrollbars',
    `--screenshot=${outPng}`,
    `--window-size=${WIDTH},${HEIGHT}`,
    '--force-device-scale-factor=1',
    pathToFileURL(tmpHtml).href,
  ], { stdio: 'ignore' });
  console.log(`generated ${outPng}`);
  count += 1;
}

try {
  rmSync(TMP_DIR, { recursive: true, force: true });
} catch {}

console.log(`done: ${count} image(s) -> ${OUT_DIR}/`);
