// base 対応の内部リンク生成。GitHub Pages のサブパス配信（/doubutsu-soshikiron/）で内部リンクを 404 にしないため必須。
// import.meta.env.BASE_URL は末尾スラッシュの有無が Astro 設定で揺れる（実測: 末尾スラッシュ無し）。
// どちらでも単一スラッシュで連結されるよう正規化する。
// 使い方: url('') → '/doubutsu-soshikiron/'、url('theory/') → '/doubutsu-soshikiron/theory/'。
const ROOT = import.meta.env.BASE_URL.replace(/\/+$/, ''); // 末尾スラッシュを剥がす
export const url = (p = '') => {
  const path = String(p).replace(/^\/+/, ''); // 先頭スラッシュを剥がす
  return path ? `${ROOT}/${path}` : `${ROOT}/`;
};
