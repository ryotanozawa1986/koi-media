/**
 * 恋愛診断・相性診断の計算は、ここへ生年月日を受け取る純関数として足す。
 * 画面は src/components/shindan/ に島コンポーネントを作り、client:visible で読む。
 * タイプごとの解説本文は src/data/result-types.ts。published を true にすると
 * /rokusei/<id>/ と /kyusei/<id>/ が静的ページになる。
 */
export { kyuseiStars, rokuseiTypes } from '../data/result-types';
export type { TypePage } from '../data/result-types';
