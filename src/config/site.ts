/**
 * サイト名と公開URLはここだけを変える。
 * 記事のカテゴリは src/data/categories.ts。
 */
export const site = {
  name: 'koi-media',
  tagline: '恋愛と占いのメディア',
  description:
    '四柱推命、六星占術、九星気学、星座、タロット、数秘術、動物占い、血液型。恋愛の傾向とタイミングを、占術ごとに読み解くウェブメディアです。',
  /** 末尾スラッシュなし。canonical、OGP、サイトマップ、RSS、robots.txt がこれを使う。 */
  url: 'https://koi-media-uranai.netlify.app',
  locale: 'ja_JP',
  postsPerPage: 6,
  editorName: 'koi-media編集部',
  defaultOgImage: '/og-default.webp',
} as const;
