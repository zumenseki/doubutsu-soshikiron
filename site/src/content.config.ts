import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// 記事＝1ファイル1記事（Markdown）。Content Layer の glob ローダで src/content/articles を読む。
const articles = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/articles' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    tags: z.array(z.string()).optional(),
  }),
});

export const collections = { articles };
