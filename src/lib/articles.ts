import { getCollection, type CollectionEntry } from 'astro:content';

export type Article = CollectionEntry<'articles'>;

export function isSampleArticle(id: string): boolean {
  return id.startsWith('sample-');
}

export async function getPublishedArticles(): Promise<Article[]> {
  const articles = await getCollection('articles', ({ data }) => data.draft === false);
  return articles.sort((a, b) => {
    const byDate = b.data.publishedAt.getTime() - a.data.publishedAt.getTime();
    if (byDate !== 0) return byDate;
    return a.id < b.id ? -1 : 1;
  });
}

export function pickFeatured(articles: Article[]): Article | undefined {
  return articles.find((article) => article.data.featured) ?? articles[0];
}

export function pickRanking(articles: Article[]): Article[] {
  return articles
    .filter((article) => typeof article.data.rank === 'number')
    .sort((a, b) => {
      const byRank = (a.data.rank ?? 0) - (b.data.rank ?? 0);
      if (byRank !== 0) return byRank;
      return b.data.publishedAt.getTime() - a.data.publishedAt.getTime();
    });
}

export function articlesInCategory(articles: Article[], categoryId: string): Article[] {
  return articles.filter((article) => article.data.category === categoryId);
}

export function collectTags(articles: Article[]): string[] {
  const tags = new Set<string>();
  for (const article of articles) {
    for (const tag of article.data.tags) tags.add(tag);
  }
  return [...tags].sort((a, b) => a.localeCompare(b, 'ja'));
}

export function articlesWithTag(articles: Article[], tag: string): Article[] {
  return articles.filter((article) => article.data.tags.includes(tag));
}

export function getRelated(current: Article, articles: Article[], limit = 4): Article[] {
  const scored = articles
    .filter((article) => article.id !== current.id)
    .map((article) => {
      let score = 0;
      if (article.data.category === current.data.category) score += 3;
      const tags = new Set(current.data.tags);
      for (const tag of article.data.tags) {
        if (tags.has(tag)) score += 1;
      }
      return { article, score };
    })
    .sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      return b.article.data.publishedAt.getTime() - a.article.data.publishedAt.getTime();
    });

  const matched = scored.filter((item) => item.score > 0).map((item) => item.article);
  if (matched.length >= limit) return matched.slice(0, limit);
  const used = new Set(matched.map((article) => article.id));
  const rest = scored.map((item) => item.article).filter((article) => !used.has(article.id));
  return [...matched, ...rest].slice(0, limit);
}
