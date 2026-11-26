import { z } from 'astro/zod';
import { categories } from '../data/categories';

const categoryIds = categories.map((category) => category.id);
if (categoryIds.length < 1) {
  throw new Error('src/data/categories.ts にカテゴリがありません');
}

const categoryList = categoryIds.join(', ');

const text = (label: string, min: number, max: number) =>
  z
    .string({ error: `${label} は文字列にしてください` })
    .trim()
    .min(min, `${label} は${min}文字以上にしてください`)
    .max(max, `${label} は${max}文字以内にしてください`);

const day = (label: string) =>
  z.coerce.date({ error: `${label} は YYYY-MM-DD の日付にしてください` });

export const articleSchema = z
  .object({
    title: text('title', 4, 70),
    description: text('description', 30, 160),
    publishedAt: day('publishedAt'),
    updatedAt: day('updatedAt').optional(),
    category: z.enum(categoryIds as [string, ...string[]], {
      error: `category は次のいずれかです: ${categoryList}`,
    }),
    tags: z
      .array(
        z
          .string({ error: 'tags は文字列の配列にしてください' })
          .trim()
          .min(1, '空のタグは使えません')
          .max(24, 'タグは24文字以内にしてください')
          .regex(/^[^/#?%&<>"'\s.]+$/u, {
            error: 'タグに空白、ドット、/ # ? % & < > は使えません',
          }),
      )
      .min(1, 'tags は1つ以上必要です')
      .max(8, 'tags は8個までです'),
    thumbnail: z.string().regex(/^\/thumbnails\/[a-z0-9]+(?:-[a-z0-9]+)*\.(webp|png)$/, {
      error: 'thumbnail は /thumbnails/<slug>.webp または .png にしてください',
    }),
    thumbnailAlt: text('thumbnailAlt', 8, 140),
    sources: z
      .array(
        z
          .object({
            title: text('sources.title', 1, 120),
            url: z.url({
              protocol: /^https?$/,
              error: 'sources.url は http:// または https:// のURLにしてください',
            }),
          })
          .strict(),
      )
      .max(12, 'sources は12件までです'),
    draft: z.boolean({ error: 'draft は true か false にしてください' }),
    faq: z
      .array(
        z
          .object({
            q: text('faq.q', 1, 120),
            a: text('faq.a', 1, 600),
          })
          .strict(),
      )
      .min(1, 'faq を書くときは1件以上必要です。不要なら faq 自体を消してください')
      .optional(),
    featured: z.boolean({ error: 'featured は true か false にしてください' }).default(false),
    rank: z
      .int({ error: 'rank は 1 から 20 の整数にしてください' })
      .min(1, 'rank は 1 以上にしてください')
      .max(20, 'rank は 20 以下にしてください')
      .optional(),
  })
  .strict();

export type ArticleData = z.infer<typeof articleSchema>;
