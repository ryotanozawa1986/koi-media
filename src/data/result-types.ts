/**
 * 六星占術・九星気学のタイプ解説ページの台帳。
 * published を true にし、summary と paragraphs を書くと
 * /rokusei/<id>/ または /kyusei/<id>/ がビルドされる。
 * 診断ツール本体はまだ作らない。計算は src/lib/divination.ts に足す。
 */
export interface TypePage {
  id: string;
  name: string;
  /** 公開するときの meta description。未公開のあいだは空でよい。 */
  summary: string;
  /** 公開するときの本文。1要素が1段落。 */
  paragraphs: string[];
  published: boolean;
}

export const rokuseiTypes: TypePage[] = [
  { id: 'dosei-plus', name: '土星人＋', summary: '', paragraphs: [], published: false },
  { id: 'dosei-minus', name: '土星人−', summary: '', paragraphs: [], published: false },
  { id: 'kinsei-plus', name: '金星人＋', summary: '', paragraphs: [], published: false },
  { id: 'kinsei-minus', name: '金星人−', summary: '', paragraphs: [], published: false },
  { id: 'kasei-plus', name: '火星人＋', summary: '', paragraphs: [], published: false },
  { id: 'kasei-minus', name: '火星人−', summary: '', paragraphs: [], published: false },
  { id: 'tennosei-plus', name: '天王星人＋', summary: '', paragraphs: [], published: false },
  { id: 'tennosei-minus', name: '天王星人−', summary: '', paragraphs: [], published: false },
  { id: 'mokusei-plus', name: '木星人＋', summary: '', paragraphs: [], published: false },
  { id: 'mokusei-minus', name: '木星人−', summary: '', paragraphs: [], published: false },
  { id: 'suisei-plus', name: '水星人＋', summary: '', paragraphs: [], published: false },
  { id: 'suisei-minus', name: '水星人−', summary: '', paragraphs: [], published: false },
];

export const kyuseiStars: TypePage[] = [
  { id: 'ippaku-suisei', name: '一白水星', summary: '', paragraphs: [], published: false },
  { id: 'jikoku-dosei', name: '二黒土星', summary: '', paragraphs: [], published: false },
  { id: 'sanpeki-mokusei', name: '三碧木星', summary: '', paragraphs: [], published: false },
  { id: 'shiroku-mokusei', name: '四緑木星', summary: '', paragraphs: [], published: false },
  { id: 'goou-dosei', name: '五黄土星', summary: '', paragraphs: [], published: false },
  { id: 'roppaku-kinsei', name: '六白金星', summary: '', paragraphs: [], published: false },
  { id: 'shichiseki-kinsei', name: '七赤金星', summary: '', paragraphs: [], published: false },
  { id: 'happaku-dosei', name: '八白土星', summary: '', paragraphs: [], published: false },
  { id: 'kyushi-kasei', name: '九紫火星', summary: '', paragraphs: [], published: false },
];

const idPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function assertTypePages(label: string, items: TypePage[]): void {
  const seen = new Set<string>();
  for (const item of items) {
    if (!idPattern.test(item.id) || item.id === 'page') {
      throw new Error(`${label} の id が不正です: ${item.id}`);
    }
    if (seen.has(item.id)) {
      throw new Error(`${label} の id が重複しています: ${item.id}`);
    }
    seen.add(item.id);
    if (!item.name.trim()) {
      throw new Error(`${label} ${item.id} の name が空です`);
    }
    if (!item.published) continue;
    if (item.summary.trim().length < 40 || item.summary.trim().length > 160) {
      throw new Error(`${label} ${item.id} の summary は、公開するなら40〜160文字にしてください`);
    }
    if (item.paragraphs.length < 2 || item.paragraphs.some((paragraph) => paragraph.trim().length < 40)) {
      throw new Error(`${label} ${item.id} は published ですが、本文の段落が足りません`);
    }
  }
}

assertTypePages('六星占術', rokuseiTypes);
assertTypePages('九星気学', kyuseiStars);
