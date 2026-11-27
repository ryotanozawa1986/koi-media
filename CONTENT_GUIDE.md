# 記事の追加手順

koi-media は、人が承認しなくても公開できるファイル方式です。記事は Markdown、サムネイルは画像ファイルです。`main` に置いて push すると、Netlify が `npm run build` を実行して公開します。形式が壊れているとビルドが失敗し、その版は公開されません。

サイト名と URL は `src/config/site.ts` だけを変えます。カテゴリは `src/data/categories.ts` だけを変えます。

## 1. ファイルを二つ置く

| 置く場所 | 内容 |
| --- | --- |
| `src/content/articles/<slug>.md` | 記事。サブフォルダは作らない |
| `public/thumbnails/<slug>.webp` | サムネイル。`.png` でもよい |

`<slug>` は半角英小文字、数字、ハイフンだけです。例: `shichu-love-basics`。ファイル名が URL になります。

- 記事URL: `/articles/shichu-love-basics/`
- 画像のフロントマター: `/thumbnails/shichu-love-basics.webp`
- ファイル名 `page.md` は使えません
- フロントマターに `slug` は書きません

見本記事は `sample-` で始まります。本番の記事には付けません。見本を消すときは、`.md` とサムネイルを両方削除します。

## 2. フロントマター

次のキーだけを書きます。知らないキーがあると失敗します。文字列はダブルクォートで囲みます。

| キー | 必須 | 内容 |
| --- | --- | --- |
| `title` | はい | 4〜70文字 |
| `description` | はい | 検索結果に出る説明。30〜160文字 |
| `publishedAt` | はい | `YYYY-MM-DD` |
| `updatedAt` | いいえ | `YYYY-MM-DD`。公開日より前は不可 |
| `category` | はい | 下の表の id |
| `tags` | はい | 1〜8個。24文字以内。空白、`.`、`/`、`#`、`?`、`%`、`&` は不可。`page` も不可 |
| `thumbnail` | はい | `/thumbnails/<slug>.webp` または `.png` |
| `thumbnailAlt` | はい | 画像の説明。8〜140文字。記事タイトルの繰り返しにしない |
| `sources` | はい | 出典の配列。0件なら `[]`。各要素は `title` と `http(s)` の `url` |
| `draft` | はい | `false` で公開、`true` で非公開 |
| `faq` | いいえ | `{ q, a }` の配列。書くなら1件以上。不要ならキーごと消す |
| `featured` | いいえ | `true` だとトップの大きく出す記事。複数あるときは新しい日付が優先 |
| `rank` | いいえ | `1`〜`20` の整数。小さいほど「人気の記事」の上位。書かなければ順位に出ない |

`category` に使える id（`src/data/categories.ts` の並びがナビの順です）:

| id | 名前 |
| --- | --- |
| `shichu-suimei` | 四柱推命 |
| `rokusei-senjutsu` | 六星占術 |
| `kyusei-kigaku` | 九星気学 |
| `seiza` | 星座占い |
| `tarot` | タロット |
| `suhijutsu` | 数秘術 |
| `dobutsu-uranai` | 動物占い |
| `ketsuekigata` | 血液型 |

## 3. 見本

このまま保存しても、画像ファイルが無いと失敗します。スラッグと画像名は、その記事のものに変えます。

```yaml
---
title: "四柱推命とは？恋愛傾向の見方"
description: "四柱推命の命式と日主から、恋愛で気持ちが出る方向の読み方を解説します。出生時刻がわからない場合の扱いも含みます。"
publishedAt: 2026-11-24
updatedAt: 2026-11-25
category: shichu-suimei
tags:
  - "四柱推命"
  - "恋愛"
thumbnail: /thumbnails/shichu-love-basics.webp
thumbnailAlt: "生成り色の余白に、細い金の三日月と四本の短い縦線、記事タイトルを入れた画像"
sources:
  - title: "参照したページのタイトル"
    url: https://example.com/sources/shichu-suimei
draft: false
featured: false
rank: 3
faq:
  - q: "出生時刻がわからないと読めませんか？"
    a: "時柱を外し、年・月・日の三柱だけで読める範囲に限る、と書きます。"
---

リード文。占いは娯楽であり、交際の判断には使わない、と必要ならここに書く。

## 最初の見出し

本文。見出しは `##` と `###` にすると、記事ページの目次に出ます。

## 出典がある場合

`sources` の URL は実在するページにします。見本の `example.com` は本番では使いません。
```

対応する画像は `public/thumbnails/shichu-love-basics.webp` です。

## 4. サムネイル

サイズはちょうど 1200×630、形式は WebP（または PNG）、パスは `public/thumbnails/<slug>.webp` です。フロントマターの `thumbnail` とファイル名を揃えます。カードと OGP の両方に使います。

スタイルは D（生成り色の線画）、E（淡い水彩）、F（水色のフラット）の3つです。記事ごとにこの中からランダムに1つ選びます。いずれも余白の多い淡いデザインで、月や星は小さめのアクセントにします。定義は `scripts/thumbnail-styles.json` にあります。

作り方:

1. スタイルをランダムに選ぶ（`python scripts/compose-thumbnail.py --pick-style --category-id <カテゴリid> --print-prompt` で、そのスタイルの英語プロンプトが出ます）
2. プロンプトどおり、文字・数字・記号のない背景だけを画像生成する（タイトルは画像モデルに描かせない）
3. 背景を 1200×630 にし、日本語タイトルとカテゴリ名を Noto CJK で載せる

```bash
python scripts/compose-thumbnail.py \
  --image /tmp/background.png \
  --style D \
  --title "四柱推命とは？恋愛傾向の見方" \
  --category "四柱推命" \
  --output public/thumbnails/shichu-love-basics.webp
```

`scripts/overlay-title.py` だけを直接呼ぶこともできます。タイトルは最大2行、句読点や「とは？」「で読む」の直後で折り返します。色と配置はスタイル定義に合わせ、月のある右側を避けて左の余白に置きます。

### フォント

自動化の実行環境に Noto CJK が必要です。Debian / Ubuntu では次で入ります。

```bash
sudo apt install fonts-noto-cjk
```

スクリプトが見に行くパス（先頭から、最初に見つかったものを使う）:

- タイトル: Noto Serif CJK Bold（例 `/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc`）
- カテゴリ: Noto Sans CJK Regular（例 `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`）

TTC の場合は JP の面を自動で選びます。フォントが無いと合成は失敗します。Netlify のビルドでは画像を作り直さないので、フォントは記事を書く側の環境にだけあれば足ります。

サイト全体のデフォルト OGP（`public/og-default.webp`）も、同じ淡いスタイルでサイト名を合成します。

古い `scripts/generate-sample-images.py` は、初期サンプル用の Pillow 抽象画像を出すだけで、今の運用では使いません（非推奨）。

## 5. 非公開にする

ファイルは残したまま、サイトから消すときは `draft` だけを変えます。

```yaml
draft: true
```

`draft: true` の記事は、トップ、記事URL、カテゴリ、タグ、関連記事、人気の順位、RSS、サイトマップに出ません。形式が壊れていれば、非公開でも検証は失敗します。直すか、ファイルと画像を削除してください。

完全に消すときは、次の二つを削除します。

- `src/content/articles/<slug>.md`
- `public/thumbnails/<slug>.webp`（または `.png`）

## 6. カテゴリを足す

`src/data/categories.ts` の配列に、次の形で一つ足します。他のファイルにカテゴリ名を書き足す必要はありません。

```ts
{
  id: 'shinkoku',
  name: '新しい占術名',
  description: '一覧と検索結果に出る説明。40〜160文字。',
  lead: 'トップの枠に出る一文。16〜80文字。',
  paragraphs: [
    'カテゴリページの上に出る柱の文章。40文字以上。',
    '二つ目の段落。占術が何を見て、恋愛の記事で何を書かないかを入れる。',
  ],
}
```

`id` はスラッグと同じ規則です。`paragraphs` はカテゴリページの柱（pillar）になります。基幹記事ができたら `pillarSlug: 'その記事のslug'` を足すと、公開中の記事だけ「基本から読む」リンクになります。

## 7. 公開前の検証

```bash
npm run check:content
```

成功すると `OK ファイル名（公開）` または `OK ファイル名（非公開 draft: true）` と出ます。失敗すると、ファイル名と直す箇所が日本語で出て、終了コードは 1 です。

`npm run build` はこの検証のあとでサイトを作ります。Netlify のビルドコマンドは `npm run build`、公開ディレクトリは `dist` です。

## 8. 診断とタイプページ（これからの拡張）

まだ計算ツールは作りません。置き場だけあります。

- 診断トップ: `/shindan/`
- ナビの「診断」はこのページです
- 入力UIを足すときは `src/components/shindan/ShindanTool.astro` を `client:visible` の島にする
- 生年月日の計算は `src/lib/divination.ts` に純関数として足す
- 六星占術の解説: `src/data/result-types.ts` の `rokuseiTypes` で `published: true` にし、`summary`（40〜160文字）と `paragraphs`（40文字以上を2つ以上）を書くと `/rokusei/<id>/` ができる
- 九星気学は `kyuseiStars` と `/kyusei/<id>/`
- `/rokusei/` と `/kyusei/` 自体は、それぞれのカテゴリページへ転送します

未公開のタイプはページを出しません。空の解説ページは作りません。
