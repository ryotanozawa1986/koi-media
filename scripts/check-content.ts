import fs from 'node:fs';
import path from 'node:path';
import matter from 'gray-matter';
import type { z } from 'astro/zod';
import { categories } from '../src/data/categories';
import { kyuseiStars, rokuseiTypes } from '../src/data/result-types';
import { articleSchema } from '../src/lib/article-schema';
import { readImageSize } from '../src/lib/image-size';

const root = process.cwd();
const articlesDir = path.join(root, 'src/content/articles');
const errors: string[] = [];

function report(file: string, messages: string[]): void {
  errors.push(`${file}\n${messages.map((message) => `  - ${message}`).join('\n')}`);
}

function formatIssue(issue: z.core.$ZodIssue): string {
  if (issue.code === 'unrecognized_keys') {
    const keys = 'keys' in issue && Array.isArray(issue.keys) ? issue.keys.join(', ') : '';
    return `未対応のフィールドです${keys ? `: ${keys}` : ''}。CONTENT_GUIDE.md にある項目だけを書いてください`;
  }
  const where = issue.path.map(String).join('.');
  return where ? `${where}: ${issue.message}` : issue.message;
}

if (!fs.existsSync(articlesDir)) {
  console.error('src/content/articles がありません。');
  process.exit(1);
}

const slugs = new Set<string>();
let count = 0;

for (const entry of fs.readdirSync(articlesDir, { withFileTypes: true })) {
  if (entry.name.startsWith('.')) continue;
  if (entry.isDirectory()) {
    report(entry.name, ['記事ディレクトリの中にフォルダは置けません。直下の .md だけにしてください']);
    continue;
  }
  if (!entry.name.endsWith('.md')) {
    report(entry.name, ['記事は .md ファイルだけです']);
    continue;
  }

  const slug = entry.name.slice(0, -3);
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {
    report(entry.name, ['ファイル名は半角英小文字・数字・ハイフンだけにしてください（例: shichu-love-basics.md）']);
    continue;
  }
  if (slug === 'page') {
    report(entry.name, ['ファイル名 page.md は一覧ページと衝突するので使えません']);
    continue;
  }
  if (slugs.has(slug)) {
    report(entry.name, ['同じスラッグの記事が重複しています']);
    continue;
  }
  slugs.add(slug);

  let parsed: matter.GrayMatterFile<string>;
  try {
    parsed = matter.read(path.join(articlesDir, entry.name));
  } catch (error) {
    report(entry.name, [`フロントマターを読めません: ${error instanceof Error ? error.message : String(error)}`]);
    continue;
  }

  const result = articleSchema.safeParse(parsed.data);
  if (!result.success) {
    report(entry.name, result.error.issues.map((issue) => formatIssue(issue)));
    continue;
  }

  const data = result.data;
  const extra: string[] = [];
  if (!parsed.content.trim()) extra.push('本文が空です');

  const expected = [`/thumbnails/${slug}.webp`, `/thumbnails/${slug}.png`];
  if (!expected.includes(data.thumbnail)) {
    extra.push(`thumbnail は ${expected.join(' または ')} にしてください。ファイル名と揃えます`);
  } else {
    const imagePath = path.join(root, 'public', data.thumbnail);
    if (!fs.existsSync(imagePath)) {
      extra.push(`画像ファイルがありません: public${data.thumbnail}`);
    } else {
      const size = readImageSize(imagePath);
      if (!size) {
        extra.push('画像サイズを読めません。1200x630 の PNG または WebP にしてください');
      } else if (size.width !== 1200 || size.height !== 630) {
        extra.push(`画像は 1200x630 にしてください（いま ${size.width}x${size.height}）`);
      }
    }
  }

  const seenTags = new Set<string>();
  for (const tag of data.tags) {
    if (seenTags.has(tag)) extra.push(`タグが重複しています: ${tag}`);
    seenTags.add(tag);
    if (tag === 'page') extra.push('タグに page は使えません');
  }

  if (data.updatedAt && data.updatedAt.getTime() < data.publishedAt.getTime()) {
    extra.push('updatedAt は publishedAt より前の日付にできません');
  }

  if (extra.length > 0) {
    report(entry.name, extra);
    continue;
  }

  count += 1;
  const state = data.draft ? '非公開 draft: true' : '公開';
  console.log(`OK ${entry.name}（${state}）`);
}

for (const category of categories) {
  if (!category.pillarSlug) continue;
  const pillar = path.join(articlesDir, `${category.pillarSlug}.md`);
  if (!fs.existsSync(pillar)) {
    report(`categories.ts (${category.id})`, [
      `pillarSlug「${category.pillarSlug}」に対応する src/content/articles/${category.pillarSlug}.md がありません`,
    ]);
  }
}

if (rokuseiTypes.length === 0 || kyuseiStars.length === 0) {
  report('result-types.ts', ['六星占術と九星気学のタイプ台帳が空です']);
}

if (errors.length > 0) {
  console.error(`\n記事の検証に失敗しました（${errors.length}件）。\n`);
  console.error(errors.join('\n\n'));
  console.error('\n直し方は CONTENT_GUIDE.md を見てください。');
  process.exit(1);
}

console.log(`\n記事 ${count} 件を確認しました。`);
