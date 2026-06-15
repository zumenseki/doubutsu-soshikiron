#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verify-article.py — 発信ループ VERIFY 評価関数の「自動で落とせる部分」だけを実装。
（docs/発信ループ設計.md §6 / docs/発信ループ_VERIFYチェックリスト.md に対応）

思想（§0）：これは「合格判定機」ではなく「疑わしきを人間に上げる adversarial な採点器」。
- FAIL = 機械が確実に言える規約違反（frontmatter 欠落など）。直してから先へ。
- WARN = 誇張/断定/法令注記漏れの「疑い」。人間が§0観点で確認する（自動採用しない）。
- INFO = 二層表記・分量の素材提示（判断材料）。

Windows 必須：  python -X utf8 scripts/verify-article.py site/src/content/articles/<slug>.md
複数可・glob 可：python -X utf8 scripts/verify-article.py site/src/content/articles/*.md
"""
import sys, re, glob, os

# --- 誇張・断定の危険語（§6-1 誇張禁止）。当たっても FAIL にせず WARN（正当な用法もあるため人間確認）。
# 注: 単独「必ず」は手順説明/「ほぼ必ず」/モデル帰結（"必ず最適を外す"）等のノイズが多く除外。
#     効果主張に結合した「必ず効く/成功/儲かる」だけを拾う（2026-06-15 全38本の文脈確認で調整）。
HYPE = [
    "実証済み", "実証された", "証明された", "証明する", "確実に効",
    "必ず効", "必ず成功", "必ず儲", "100%", "断言", "絶対に",
    "科学的に正しい", "データが裏付け", "実測で当", "当たっている", "効果を保証",
]
# --- 法令・数値（§6-1）。出現したら「変わりうる」系の注記が近傍に要る。
LAW = ["労働基準法", "労基法", "最低賃金", "36協定", "三六協定", "割増賃金", "残業代", "有給"]
LAW_NOTE = ["変わりうる", "変わり得る", "時点", "現行", "改正", "最新の", "確認"]
# --- 二層表記の素材（§6-1 二層）。式記号と比喩語の両在を「情報」として見せる。
FORMULA = [r"ΔV", r"η", r"κ", r"ρ", r"τ", r"Ĝ", r"δ", r"dR_eff", r"softmax",
           r"Rescorla", r"予測誤差", r"随伴", r"マスター方程式"]
# 5類型名だけだと「動物行動学の一般語（採餌/タカ-ハト/犬実験…）」の記事を誤って比喩ゼロ判定する
# → 動物・生態に直結する具体語を追加（汎用語=進化/適応/個体/生物 は検出力が死ぬので入れない）。
METAPHOR = ["オオカミ", "アリ", "チンパン", "ボノボ", "ハイエナ", "群れ", "生態系",
            "比喩", "レンズ", "再野生化",
            "犬", "猿", "サル", "ネズミ", "ラット", "鳥", "ハチドリ", "ミツバチ", "働き蜂", "魚", "タカ", "ハト",
            "カラス", "カプチン", "霊長類", "採餌", "捕食", "縄張り", "テリトリー", "つがい",
            "営巣", "帰巣", "餌", "本能", "警戒", "威嚇", "求愛", "順位", "エソグラム",
            "ハンディキャップ", "威信", "個体群", "共生"]
# --- 「動物比喩が薄い」を §0 判断で意図的に許容する記事（slug→理由）。比喩チェックのみ免除。
#     記事側は触らず採点器で管理（現状維持の決定に忠実・Astro frontmatter スキーマに影響しない）。
EXEMPT_THIN_METAPHOR = {
    "crowding-out": "ドメイン外の一致記事＝設計上あえて人間制度(託児所罰金/献血謝礼)を主役にし、動物機構は reward-trap に委譲（2026-06-15 §0判断で意図的例外と確定）",
}
# --- §0 注記っぽい語（末尾注記の有無を info で）。
S0_NOTE = ["比喩", "レンズ", "仮説", "実測モデルでは", "係数は観測", "断定するもの", "単一の原因"]

RESET = "\033[0m"; RED = "\033[31m"; YEL = "\033[33m"; GRN = "\033[32m"; DIM = "\033[2m"
USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None  # パイプ/リダイレクト時は無色
def _c(s, c):  # 端末色（Windows Terminal/PS7 は ANSI 対応）
    return f"{c}{s}{RESET}" if USE_COLOR else s

def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None, text
    fm_raw, body = m.group(1), text[m.end():]
    fm = {}
    for line in fm_raw.splitlines():
        mm = re.match(r"^(\w+)\s*:\s*(.*)$", line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip()
    return fm, body

def find_near(body, words, window=80):
    """words のいずれかが body に在れば、その周辺 window 字に LAW_NOTE があるか。"""
    for w in words:
        for m in re.finditer(re.escape(w), body):
            s = max(0, m.start() - window); e = min(len(body), m.end() + window)
            ctx = body[s:e]
            if any(n in ctx for n in LAW_NOTE):
                return True, w  # 注記あり
    return None, None

def verify(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    fm, body = parse_frontmatter(text)
    fails, warns, infos = [], [], []

    # --- FAIL: frontmatter 必須フィールド
    if fm is None:
        fails.append("frontmatter（--- ... ---）が無い")
        fm = {}
    for k in ("title", "description", "pubDate", "tags"):
        if k not in fm:
            fails.append(f"frontmatter に {k}: が無い")

    # --- WARN: 誇張・断定語
    hits = sorted({w for w in HYPE if w in body})
    if hits:
        warns.append("誇張/断定の疑い語: " + ", ".join(hits) + " → §0（誇張禁止）で人間確認")

    # --- WARN: 法令語に「変わりうる」注記が無い
    laws = sorted({w for w in LAW if w in body})
    if laws:
        ok, _ = find_near(body, laws)
        if not ok:
            warns.append("法令/数値語あり（" + ", ".join(laws) + "）だが近傍に「変わりうる/時点/改正」注記なし")

    # --- INFO: 二層表記の素材
    has_formula = any(re.search(p, body) for p in FORMULA)
    has_meta = any(w in body for w in METAPHOR)
    infos.append(f"二層素材: 式記号={'有' if has_formula else '無'} / 比喩語={'有' if has_meta else '無'}")
    if not has_meta:
        slug = os.path.basename(path)[:-3] if path.endswith(".md") else os.path.basename(path)
        if slug in EXEMPT_THIN_METAPHOR:
            infos.append("比喩語なし・意図的例外: " + EXEMPT_THIN_METAPHOR[slug])
        else:
            warns.append("比喩語（動物/生態系/レンズ）が見当たらない → ブランド核が薄まっていないか確認")

    # --- INFO: §0 注記の気配
    infos.append(f"§0注記の気配: {'有' if any(w in body for w in S0_NOTE) else '無（末尾に比喩/仮説の注記を検討）'}")

    # --- INFO: 分量
    chars = len(re.sub(r"\s", "", body))
    h2 = len(re.findall(r"^##\s+", body, re.M))
    infos.append(f"分量: 本文 {chars} 字 / h2 見出し {h2} 本")

    return fails, warns, infos

def main(argv):
    args = argv[1:]
    if not args:
        print("usage: python -X utf8 scripts/verify-article.py <article.md> [more.md ...]")
        return 2
    paths = []
    for a in args:
        paths.extend(glob.glob(a))
    if not paths:
        print("no files matched")
        return 2

    tot_fail = tot_warn = 0
    for p in sorted(paths):
        fails, warns, infos = verify(p)
        tot_fail += len(fails); tot_warn += len(warns)
        verdict = _c("FAIL", RED) if fails else (_c("WARN", YEL) if warns else _c("PASS", GRN))
        print(f"\n[{verdict}] {os.path.basename(p)}")
        for x in fails: print("  " + _c("✗ " + x, RED))
        for x in warns: print("  " + _c("⚠ " + x, YEL))
        for x in infos: print("  " + _c("· " + x, DIM))

    print(_c(f"\n— {len(paths)} 記事: FAIL {tot_fail} / WARN {tot_warn} —", DIM))
    print(_c("FAIL=直す / WARN=§0観点で人間確認（自動採用しない） / 固定タグ#動物行動学はnote入稿時に付与", DIM))
    return 1 if tot_fail else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
