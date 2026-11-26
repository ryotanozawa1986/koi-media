import rss from '@astrojs/rss';
import type { APIRoute } from 'astro';
import { getPublishedArticles } from '../lib/articles';
import { getCategory } from '../lib/categories';
import { site } from '../config/site';
import { articlePath } from '../lib/paths';

export const GET: APIRoute = async (context) => {
  const articles = await getPublishedArticles();
  return rss({
    title: site.name,
    description: site.description,
    site: context.site ?? site.url,
    trailingSlash: true,
    customData: '<language>ja</language>',
    items: articles.map((article) => ({
      title: article.data.title,
      description: article.data.description,
      pubDate: article.data.publishedAt,
      link: articlePath(article.id),
      categories: [getCategory(article.data.category).name, ...article.data.tags],
    })),
  });
};
