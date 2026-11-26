import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { articleSchema } from './lib/article-schema';

const articles = defineCollection({
  loader: glob({
    base: './src/content/articles',
    pattern: '*.md',
    generateId: ({ entry }) => entry.replace(/\.md$/, '').replace(/\\/g, '/'),
  }),
  schema: articleSchema,
});

export const collections = { articles };
