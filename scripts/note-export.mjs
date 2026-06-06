// note 転載用 変換スクリプト
// site/src/content/articles/*.md を note 貼り付け用テキストへ一括変換し note-export/ へ出力する。
// 変換内容: frontmatter除去(titleは1行目へ) / 相対リンク絶対化 / 表→箇条書き / 末尾にcanonical(初出=本家リンク)。
// 実行: リポジトリルートで `node scripts/note-export.mjs`
// 依存なし(Node標準のみ)。出力 note-export/ は .gitignore 済(複製を追跡しない・再生成可)。
import { readFileSync, writeFileSync, readdirSync, mkdirSync, existsSync } from 'node:fs';
import { join, basename } from 'node:path';

const SRC = 'site/src/content/articles';
const OUT = 'note-export';
const BASE = 'https://zumenseki.github.io/doubutsu-soshikiron/articles';

if (!existsSync(OUT)) mkdirSync(OUT, { recursive: true });

// Markdown の表は note が非対応 → 各行を「ヘッダ：値 ／ …」の箇条書きに変換
function convertTables(md) {
  const lines = md.split('\n');
  const out = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const isRow = /^\s*\|.*\|\s*$/.test(line);
    const isSep = i + 1 < lines.length && /^\s*\|[\s:|-]+\|\s*$/.test(lines[i + 1]);
    if (isRow && isSep) {
      const headers = line.split('|').slice(1, -1).map((s) => s.trim());
      i += 2; // ヘッダ行と区切り行をスキップ
      out.push('');
      while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) {
        const cells = lines[i].split('|').slice(1, -1).map((s) => s.trim());
        const parts = headers.map((h, idx) => (cells[idx] ? `${h}：${cells[idx]}` : '')).filter(Boolean);
        out.push(`- ${parts.join(' ／ ')}`);
        i++;
      }
      out.push('');
      continue;
    }
    out.push(line);
    i++;
  }
  return out.join('\n');
}

const files = readdirSync(SRC).filter((f) => f.endsWith('.md')).sort();
let n = 0;
for (const file of files) {
  const slug = basename(file, '.md');
  const raw = readFileSync(join(SRC, file), 'utf8').replace(/\r/g, ''); // CRLF→LF 統一
  const m = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!m) {
    console.warn('skip (no frontmatter):', file);
    continue;
  }
  const front = m[1];
  let body = m[2].trim();
  const tm = front.match(/title:\s*(.+)/);
  const title = tm ? tm[1].trim().replace(/^["']|["']$/g, '') : slug;

  body = body.replace(/\]\(\.\.\/([a-z0-9-]+)\/\)/g, `](${BASE}/$1/)`); // 相対リンク→絶対URL
  body = convertTables(body);

  const footer = `\n\n———\n※この記事の初出は本家サイトです：${BASE}/${slug}/`;
  const text = `${title}\n\n${body}${footer}\n`;
  writeFileSync(join(OUT, `${slug}.md`), text, 'utf8');
  n++;
}

const readme = `# note 転載用テキスト（自動生成・git管理外）

\`node scripts/note-export.mjs\` で再生成できます。各 <slug>.md の使い方:
- **1行目** = note の「タイトル」欄に貼る
- **空行より下（本文〜末尾）** = note の本文欄に貼る（見出し/リスト/引用/太字/リンクは note が自動認識）
- 末尾の「※初出は本家サイト」行 = 重複コンテンツ対策。基本は残す（本家へ誘導＆初出明示）。

注記:
- 表は note が非対応のため箇条書きへ変換済み。
- 記事内の相対リンクは本家の絶対URLへ変換済み。
- 全 ${n} 本。タイトルが長い記事は note 側で適宜短縮可。
`;
writeFileSync(join(OUT, '_README.md'), readme, 'utf8');

console.log(`変換完了: ${n}本 -> ${OUT}/`);
