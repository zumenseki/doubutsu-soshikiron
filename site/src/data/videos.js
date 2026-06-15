// どうぶつ診断：型/トピック → 関連動画（YouTube）の対応表。
// YouTube チャンネルは開設前（2026-06-22 予定）。youtubeId は全て空文字で「種まき」。
// 公開後はこの1ファイルに動画IDを貼るだけで、結果カードの動画導線が自動で有効化される。
// youtubeId が空の間は videoHref() が null を返し、shindan.astro が記事リンクへフォールバック（壊れリンクを出さない）。
//
// articleSlug は site/src/content/articles/*.md の実在スラッグ（横型解説17本と1:1対応・全件存在確認済）。

export const VIDEOS = {
  'five-types':       { label: '組織の5類型（総論）',       articleSlug: 'five-types-ethology',     youtubeId: '' },
  'fear':             { label: '恐怖が学習を殺す',           articleSlug: 'fear-kills-learning',     youtubeId: '' },
  'reward-trap':      { label: '報酬の罠',                   articleSlug: 'reward-trap',             youtubeId: '' },
  'controllability':  { label: '統制可能性と学習性無力感',   articleSlug: 'controllability',         youtubeId: '' },
  'crowding-out':     { label: '動機の締め出し',             articleSlug: 'crowding-out',            youtubeId: '' },
  'unfairness-cost':  { label: '不公平感のコスト',           articleSlug: 'unfairness-cost',         youtubeId: '' },
  'status':           { label: '地位と承認のストレス',       articleSlug: 'status-ethology',         youtubeId: '' },
  'recruitment':      { label: '採用の動物行動学',           articleSlug: 'recruitment-ethology',    youtubeId: '' },
  'negotiation':      { label: '交渉の動物行動学',           articleSlug: 'negotiation-ethology',    youtubeId: '' },
  'price':            { label: '価格と参照点',               articleSlug: 'price-ethology',          youtubeId: '' },
  'precedent-lockin': { label: '前例ロックインと属人化',     articleSlug: 'precedent-lockin',        youtubeId: '' },
  'procrastination':  { label: '先延ばしと双曲割引',         articleSlug: 'procrastination-ethology', youtubeId: '' },
  'bank-run':         { label: '取り付け騒ぎ（恐怖伝播）',   articleSlug: 'bank-run',                youtubeId: '' },
  'uprising':         { label: '集団蜂起',                   articleSlug: 'uprising',                youtubeId: '' },
  'attribution':      { label: '帰属ゲートと随伴性',         articleSlug: 'attribution-ethology',    youtubeId: '' },
  'sales-ethology':   { label: '営業の動物行動学（俯瞰）',   articleSlug: 'sales-ethology',          youtubeId: '' },
  'mobbing':          { label: '集団攻撃・同調圧力',         articleSlug: 'mobbing-ethology',        youtubeId: '' },
};

// トピックキー → YouTube URL。youtubeId 未設定なら null（呼び出し側が記事へフォールバック）。
export function videoHref(topicKey) {
  const v = VIDEOS[topicKey];
  if (!v || !v.youtubeId) return null;
  return `https://youtu.be/${v.youtubeId}`;
}
