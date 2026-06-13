// note-drafts/<slug>.md → note入稿用JSON {title, blocks:[{t,h2}]}
// 使い方: node scripts/_md2note.mjs <draftFileName>   (例: parenting-praise-paid.md)
// frontmatterコメント / # タイトル案 / 【...】マーカー / --- を除去。
// ## と ### を h2、> 引用は段落化、- 箇条は「・」段落に分割、**bold**と[text](url)は除去。
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const file = process.argv[2];
const raw = readFileSync(resolve('note-drafts', file), 'utf8');

// 1) HTMLコメント除去
let s = raw.replace(/<!--[\s\S]*?-->/g, '');

// 2) タイトル案1抽出（最初の「N. **...**」）
const titleM = s.match(/^\s*1\.\s*\*\*(.+?)\*\*/m);
let title = titleM ? titleM[1].trim() : '';
title = title.replace(/（推奨）\s*$/, '').trim();

// 3) 最初の「# 【...】」マーカー以降を本文に
const bodyStart = s.search(/^#\s*【/m);
let body = bodyStart >= 0 ? s.slice(bodyStart) : s;

// インライン整形：**bold**除去・[text](url)→text・全角/半角は保持
const inline = (t) => t
  .replace(/\*\*(.+?)\*\*/g, '$1')
  .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
  .trim();

const blocks = [];
const paras = body.split(/\n{2,}/);
for (let p of paras) {
  p = p.replace(/\r/g, '').trim();
  if (!p) continue;
  if (/^#\s*【/.test(p)) continue;          // 【無料エリア】【ここから有料】等のマーカー行
  if (/^#\s*タイトル案/.test(p)) continue;
  if (/^-{3,}$/.test(p)) continue;          // 区切り線
  // 箇条書きブロック：各「- 」行を「・」段落に分割
  const lines = p.split('\n');
  const isBulletBlock = lines.every(l => /^\s*-\s+/.test(l));
  if (isBulletBlock) {
    for (const l of lines) blocks.push({ t: '・' + inline(l.replace(/^\s*-\s+/, '')), h2: false });
    continue;
  }
  // 見出し
  let m;
  if ((m = p.match(/^#{2,3}\s+(.+)$/m)) && /^#{2,3}\s+/.test(p)) {
    let ht = inline(p.replace(/^#{2,3}\s+/, ''));
    // 「1. 」等のASCII番号付き見出しは、PM貼付時の順序リスト自動変換を避けるため全角ピリオドへ
    ht = ht.replace(/^(\d+)\.\s+/, '$1．');
    blocks.push({ t: ht, h2: true });
    continue;
  }
  // 引用 > （各行頭の「> 」を剥がして結合）
  if (lines.every(l => /^>\s?/.test(l))) {
    blocks.push({ t: inline(lines.map(l => l.replace(/^>\s?/, '')).join(' ')), h2: false });
    continue;
  }
  // 通常段落（内部改行は結合）
  blocks.push({ t: inline(lines.join(' ')), h2: false });
}

process.stdout.write(JSON.stringify({ title, blocks }, null, 0));
