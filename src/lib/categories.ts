import { categories, type CategoryDef } from '../data/categories';

export function getCategory(id: string): CategoryDef {
  const found = categories.find((category) => category.id === id);
  if (!found) throw new Error(`未知のカテゴリです: ${id}`);
  return found;
}

export function latestInCategory<T extends { data: { category: string }; id: string }>(
  articles: T[],
  categoryId: string,
): T | undefined {
  return articles.find((article) => article.data.category === categoryId);
}
