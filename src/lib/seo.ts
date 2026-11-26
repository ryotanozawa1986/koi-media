import { site } from '../config/site';
import type { Article } from './articles';
import { absoluteUrl, type Crumb } from './paths';

export function breadcrumbLd(crumbs: Crumb[]): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: crumbs.map((crumb, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: crumb.name,
      item: absoluteUrl(crumb.href),
    })),
  };
}

export function websiteLd(): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: site.name,
    description: site.description,
    url: absoluteUrl('/'),
    inLanguage: 'ja',
    publisher: {
      '@type': 'Organization',
      name: site.editorName,
      url: absoluteUrl('/about/'),
    },
  };
}

export function webPageLd(name: string, description: string, path: string): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name,
    description,
    url: absoluteUrl(path),
    inLanguage: 'ja',
    isPartOf: {
      '@type': 'WebSite',
      name: site.name,
      url: absoluteUrl('/'),
    },
  };
}

export function collectionLd(name: string, description: string, path: string): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name,
    description,
    url: absoluteUrl(path),
    inLanguage: 'ja',
    isPartOf: {
      '@type': 'WebSite',
      name: site.name,
      url: absoluteUrl('/'),
    },
  };
}

export function itemListLd(articles: Article[], pathFor: (id: string) => string): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    itemListElement: articles.slice(0, 12).map((article, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: article.data.title,
      url: absoluteUrl(pathFor(article.id)),
    })),
  };
}

export function articleLd(article: Article, categoryName: string): Record<string, unknown> {
  const pageUrl = absoluteUrl(`/articles/${article.id}/`);
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    mainEntityOfPage: pageUrl,
    headline: article.data.title,
    description: article.data.description,
    image: {
      '@type': 'ImageObject',
      url: absoluteUrl(article.data.thumbnail),
      width: 1200,
      height: 630,
    },
    datePublished: article.data.publishedAt.toISOString(),
    dateModified: (article.data.updatedAt ?? article.data.publishedAt).toISOString(),
    articleSection: categoryName,
    keywords: article.data.tags.join(','),
    inLanguage: 'ja',
    author: {
      '@type': 'Organization',
      name: site.editorName,
      url: absoluteUrl('/about/'),
    },
    publisher: {
      '@type': 'Organization',
      name: site.name,
      url: absoluteUrl('/'),
      logo: {
        '@type': 'ImageObject',
        url: absoluteUrl('/favicon.svg'),
      },
    },
  };
}

export function faqLd(faq: { q: string; a: string }[]): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faq.map((item) => ({
      '@type': 'Question',
      name: item.q,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.a,
      },
    })),
  };
}
