import { defineConfig } from 'astro/config';

// 完全無料・静的サイト（SSG）。GitHub Pages（zumenseki.github.io/doubutsu-soshikiron/）へデプロイ。
// site + base は必須：サブパス配信のため、内部リンクは src/lib/url.js の url() で base を前置する。
export default defineConfig({
  site: 'https://zumenseki.github.io',
  base: '/doubutsu-soshikiron',
});
