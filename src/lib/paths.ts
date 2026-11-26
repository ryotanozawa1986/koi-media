import { site } from '../config/site';

export interface Crumb {
  name: string;
  href: string;
}

export function absoluteUrl(pathname: string): string {
  if (pathname.startsWith('http://') || pathname.startsWith('https://')) return pathname;
  const base = site.url.replace(/\/$/, '');
  const path = pathname.startsWith('/') ? pathname : `/${pathname}`;
  return `${base}${path}`;
}

export function articlePath(id: string): string {
  return `/articles/${id}/`;
}

export function categoryPath(id: string): string {
  return `/category/${id}/`;
}

export function tagPath(tag: string): string {
  return `/tag/${tag}/`;
}

export function rokuseiPath(id: string): string {
  return `/rokusei/${id}/`;
}

export function kyuseiPath(id: string): string {
  return `/kyusei/${id}/`;
}

/** basePath は /articles でも /articles/ でもよい。1ページ目は base 自身。 */
export function hrefForPage(basePath: string, page: number): string {
  const base = basePath.replace(/\/$/, '');
  if (page <= 1) return `${base}/`;
  return `${base}/page/${page}/`;
}
