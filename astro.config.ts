import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';
import { site } from './src/config/site';

export default defineConfig({
  site: site.url,
  output: 'static',
  trailingSlash: 'always',
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/404'),
    }),
  ],
  redirects: {
    '/rokusei/': '/category/rokusei-senjutsu/',
    '/kyusei/': '/category/kyusei-kigaku/',
  },
});
