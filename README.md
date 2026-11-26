# koi-media

恋愛と占いのウェブメディアです。記事は `src/content/articles/` の Markdown、サムネイルは `public/thumbnails/` の画像です。CMS はありません。`main` への push で Netlify が静的サイトを公開します。

## コマンド

```bash
npm install
npm run dev          # http://localhost:4321
npm run check:content
npm run build        # 検証のあと dist/ を作る
npm run preview
```

Netlify のビルドコマンドは `npm run build`、公開ディレクトリは `dist`、Node は 22 です。設定は `netlify.toml` にあります。

## 設定

| ファイル | 役割 |
| --- | --- |
| `src/config/site.ts` | サイト名、公開URL、1ページの件数 |
| `src/data/categories.ts` | 占術カテゴリと、カテゴリページ上部の柱テキスト |
| `src/data/result-types.ts` | 六星・九星のタイプ解説（`published: true` でページ化） |
| `CONTENT_GUIDE.md` | 記事を追加する手順、フロントマター、非公開の方法 |

公開URLは `https://koi-love.net` です。`src/config/site.ts` の `url` が canonical、OGP、サイトマップ、RSS、`robots.txt` の基準になります。サイト名は `koi-media` です。
