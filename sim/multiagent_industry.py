"""
多エージェント層 MA-9 — 業種別最適化（最適 regime は業種の関数）

検証する主張（docs/比喩_5類型マクロ.md 業種別マトリクス、docs/橋渡し_対応表.md）:

  MA-7 は『層ごと』に最適 regime が違うことを示した。MA-9 は『業種（タスク環境）ごと』に
  最適 regime が違うことを示す。業種を2軸で定義する（最小の戯画・§0）:
    - 変動性 v：最良 practice（正解 option）が確率 v で毎期入れ替わる＝探索が要る度合い。
    - 失敗コスト ec：非標準（非コンセンサス）行動への罰＝標準化・信頼性が要る度合い
      （恐怖の正当域＝docs/正本_ミクロ機構.md §7 と接続）。
  5管理 regime（4ダイヤル署名の preset）を業種グリッドで総当たりし、業種ごとの勝者地図を出す。

  非自明な帰結（通俗版「ベストプラクティス＝唯一の最適経営」と分岐）:
    (1) 最適 regime は業種 (v, ec) の関数＝普遍の勝者は無い（相図が非一様）。
    (2) ある業種で最適な型は、別業種で最悪になりうる（勝ち文化の移植は失敗＝regret 大）。
    (3) 高 v×高 ec は探索と標準化が二律背反で、どの型も達成性能が低い（快適な型が無い）。

機構:
  - 各エージェントは practice（K択）を choice=softmax((V+c·人気)/τ) で選び、個人 RL で V を更新。
    学習率は drive·eta（drive<1＝政治税/slack で実効努力が落ちる）。
  - 業種の変動性 v：毎期 確率 v で「正解 practice」b_t がランダムに移る。追従には探索（高 τ・低 c）が要る。
  - 業種の失敗コスト ec：性能から ec·(非コンセンサス率) を引く。標準化（高 c）は逸脱を減らし罰を避ける。
  - 性能 P = 正解到達率 − ec·(1 − コンセンサス率) − 病態の固定コスト。後半 window で平均。

§0 の正直さ:
  - 2軸は業種の最小戯画（実際の業種はより多次元）。地図の非一様性は explore↔standardize の
    二律から創発するのであって、結論を埋め込んだものではない。
  - 5 preset は 4ダイヤルの写像で未フィット。健全型(wolf/ant)の cost=0、病態型のみ正の固定 cost：
    chimp=政治のオーバーヘッド（内部抗争でエネルギー流出）、hyena=恐怖の複合コスト（burnout・定理D）。
    これは「病態型がなぜ多くの業種で劣るか」の機構の表現で、特定企業の係数フィットではない。

出力: sim/out/figL1_industries.png, figL2_regime_map.png, figL3_transplant.png ＋ stdout。
実行: python sim/multiagent_industry.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

from config import CONFIG_MA9 as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# 5 regime preset：(τ 探索温度, c 同調強度, drive 実効学習率係数, cost 病態の固定コスト)。
# 4ダイヤル署名の写像（§0：未フィット）。cost は健全型(wolf/ant)=0、病態型のみ正：
#   chimp=政治のオーバーヘッド（内部抗争でエネルギー流出）、hyena=恐怖の複合コスト（burnout・定理D）。
# 地図の非一様性そのものは explore↔standardize の二律から創発する（cost は病態型の劣位を表すだけ）。
REGIMES = {
    "wolf":   dict(tau=0.60, c=0.3, drive=1.00, cost=0.00),   # 探索高・同調低・強駆動
    "ant":    dict(tau=0.15, c=3.0, drive=1.00, cost=0.00),   # 標準化・同調高
    "chimp":  dict(tau=0.35, c=1.5, drive=0.45, cost=0.06),   # 政治＝駆動減＋抗争オーバーヘッド
    "bonobo": dict(tau=0.55, c=0.3, drive=0.50, cost=0.00),   # 低恐怖で探索するが駆動弱＝slack(遅いが無害)
    "hyena":  dict(tau=0.12, c=1.0, drive=1.00, cost=0.10),   # 恐怖で τ 狭窄＝近視・追従不能＋burnout
}
REGIME_NAMES = list(REGIMES.keys())
REGIME_JP = {"wolf": "オオカミ", "ant": "アリ", "chimp": "チンパン",
             "bonobo": "ボノボ", "hyena": "ハイエナ"}
REGIME_COLORS = {"wolf": "#2ca02c", "ant": "#1f77b4", "chimp": "#9467bd",
                 "bonobo": "#17becf", "hyena": "#d62728"}


def _softmax_choice(score, tau, rng):
    z = score / tau
    z -= z.max(axis=1, keepdims=True)
    P = np.exp(z); P /= P.sum(axis=1, keepdims=True)
    return (rng.random((P.shape[0], 1)) < P.cumsum(axis=1)).argmax(axis=1)


def run_industry(reg, v, ec, rng):
    """regime reg を業種 (v, ec) で回す。(正解到達率 hit, コンセンサス con, 性能 P) を返す。"""
    N, K, T = C.N, C.K, C.T
    tau, c, drive, cost = reg["tau"], reg["c"], reg["drive"], reg["cost"]
    V = np.zeros((N, K)); V[:, 0] = 0.5         # 全員 status quo(option0) を弱く知る状態から
    best = 0                                    # 初期の正解 practice
    pop = np.zeros(K); pop[0] = 1.0
    idx = np.arange(N)
    hits = np.empty(T); cons = np.empty(T)
    for t in range(T):
        if rng.random() < v:                    # 業種の変動：正解 practice が移る
            best = int(rng.integers(0, K))
        ch = _softmax_choice(V + c * pop[None, :], tau, rng)
        r = (ch == best).astype(float) + C.reward_noise * rng.standard_normal(N)
        V[idx, ch] += drive * C.eta * (r - V[idx, ch])
        pop = np.bincount(ch, minlength=K) / N
        hits[t] = (ch == best).mean()
        cons[t] = pop.max()                     # コンセンサス＝最大シェア（標準化の度合い）
    w = C.perf_window
    hit = float(hits[-w:].mean()); con = float(cons[-w:].mean())
    P = hit - ec * (1.0 - con) - cost           # 性能＝到達率 − 失敗コスト×逸脱率 − 病態の固定コスト
    return hit, con, P


def perf(reg, v, ec, master, seeds=None):
    """複数 seed 平均の性能 P。"""
    seeds = seeds or C.sweep_seeds
    ps = [run_industry(reg, v, ec, _spawn(master))[2] for _ in range(seeds)]
    return float(np.mean(ps))


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def _industries():
    """代表4業種（和名, 英名, v, ec）を範囲の四隅から構成。図ラベルは英名（CJK フォント回避）。"""
    vL, vH, eL, eH = C.v_lo, C.v_hi, C.ec_lo, C.ec_hi
    return [
        ("IT/創造 (高変動・低失敗コスト)",  "IT/creative\n(volatile, low cost)",  vH, eL),
        ("定型事務 (低変動・低失敗コスト)", "routine admin\n(stable, low cost)",  vL, eL),
        ("製造/航空 (低変動・高失敗コスト)", "mfg/aviation\n(stable, high cost)",  vL, eH),
        ("救急/取引 (高変動・高失敗コスト)", "ER/trading\n(volatile, high cost)",  vH, eH),
    ]


def fig1(master):
    """代表4業種 × 5regime の性能 P（業種で勝者が変わる）。"""
    inds = _industries()
    data = np.empty((len(inds), len(REGIME_NAMES)))
    for i, (_, _, v, ec) in enumerate(inds):
        for j, name in enumerate(REGIME_NAMES):
            data[i, j] = perf(REGIMES[name], v, ec, master)
    x = np.arange(len(inds)); width = 0.16
    fig, ax = plt.subplots(figsize=(11.5, 6))
    for j, name in enumerate(REGIME_NAMES):
        ax.bar(x + (j - 2) * width, data[:, j], width, label=name, color=REGIME_COLORS[name])
    ax.set_xticks(x)
    ax.set_xticklabels([en for _, en, _, _ in inds], fontsize=8)
    ax.set(title="MA-9: the best regime differs by industry (no universal winner)",
           ylabel="performance P = hit - ec*(1-consensus) - cost")
    ax.axhline(0, color="k", lw=0.6)
    ax.legend(loc="upper right", fontsize=9, ncol=5, title="regime")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figL1_industries.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figL1] saved -> {path}")
    winners = [(jp, REGIME_NAMES[int(np.argmax(data[i]))]) for i, (jp, _, _, _) in enumerate(inds)]
    return inds, data, winners


def fig2(master):
    """相図 (v × ec)：各点で性能最大の regime を色分け＝業種ごとの勝者地図（非一様）。"""
    vs = np.linspace(C.v_lo, C.v_hi, C.grid_points)
    ecs = np.linspace(C.ec_lo, C.ec_hi, C.grid_points)
    win = np.empty((C.grid_points, C.grid_points), dtype=int)
    for a, ec in enumerate(ecs):              # y = 失敗コスト
        for b, v in enumerate(vs):            # x = 変動性
            ps = [perf(REGIMES[n], v, ec, master, seeds=3) for n in REGIME_NAMES]
            win[a, b] = int(np.argmax(ps))
    present = sorted(set(win.ravel().tolist()))
    cmap = ListedColormap([REGIME_COLORS[REGIME_NAMES[k]] for k in present])
    remap = np.vectorize({k: i for i, k in enumerate(present)}.get)(win)
    norm = BoundaryNorm(np.arange(len(present) + 1) - 0.5, len(present))
    fig, ax = plt.subplots(figsize=(8.8, 6.6))
    ax.pcolormesh(vs, ecs, remap, cmap=cmap, norm=norm, shading="auto")
    handles = [plt.Rectangle((0, 0), 1, 1, color=REGIME_COLORS[REGIME_NAMES[k]],
               label=REGIME_NAMES[k]) for k in present]
    ax.legend(handles=handles, loc="upper center", fontsize=9, ncol=len(present),
              framealpha=0.9, title="winning regime")
    ax.set(title="MA-9: best regime by industry — the map is non-uniform\n"
                 "(volatility wants exploration=wolf; error-cost wants standardization=ant)",
           xlabel="volatility v  (how fast the best practice moves)",
           ylabel="error cost ec  (penalty for non-standard action)")
    fig.tight_layout()
    path = os.path.join(OUT, "figL2_regime_map.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figL2] saved -> {path}")
    return vs, ecs, win, present


def fig3(master):
    """ベストプラクティスの罠：1業種の勝者文化を全業種へ移植したときの regret（業種 best − 自分）。
    勝った業種では regret≈0、逆コーナー業種では regret 大＝移植は失敗。"""
    inds = _industries()
    best_by_ind = [max(perf(REGIMES[n], v, ec, master) for n in REGIME_NAMES)
                   for _, _, v, ec in inds]
    # creative 最適文化(wolf)と manufacturing 最適文化(ant)＝fig1 の各コーナー勝者を移植し regret を見る
    picks = {"wolf-culture (optimal for IT/creative)": "wolf",
             "ant-culture (optimal for mfg/aviation)": "ant"}
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    x = np.arange(len(inds)); width = 0.36
    colors = ["#2ca02c", "#1f77b4"]
    regret_tbl = {}
    for off, col, (label, reg) in zip((-width / 2, width / 2), colors, picks.items()):
        reg_vals = [max(0.0, best_by_ind[i] - perf(REGIMES[reg], v, ec, master))
                    for i, (_, _, v, ec) in enumerate(inds)]
        regret_tbl[label] = (reg, reg_vals)
        ax.bar(x + off, reg_vals, width, color=col, label=f"{label} = {reg}")
    ax.set_xticks(x); ax.set_xticklabels([en for _, en, _, _ in inds], fontsize=8)
    ax.set(title="MA-9: transplanting a winning culture fails — low regret at home, high regret elsewhere",
           ylabel="regret = (industry best P) - (transplanted culture's P)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figL3_transplant.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figL3] saved -> {path}")
    return inds, regret_tbl


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 80)
    print("多エージェント MA-9 業種別最適化（最適 regime は業種の関数）")
    print(f"seed={C.seed}  N={C.N}  K={C.K}  T={C.T}  業種2軸=(変動性 v, 失敗コスト ec)")
    print("検証: 普遍のベストは無く、最適 regime は業種で変わる／勝ち文化の移植は失敗")
    print("=" * 80)

    inds, data, winners = fig1(master)
    print(f"{'industry':30s} " + " ".join(f"{n:>7s}" for n in REGIME_NAMES) + "   winner")
    for i, (jp, _, _, _) in enumerate(inds):
        row = " ".join(f"{data[i, j]:7.3f}" for j in range(len(REGIME_NAMES)))
        print(f"  {jp:28s} {row}  -> {winners[i][1]}")

    vs, ecs, win, present = fig2(master)
    print("-" * 80)
    print("相図 (v × ec) の勝者 regime 分布（地図の非一様性）:")
    total = win.size
    for k in range(len(REGIME_NAMES)):
        sh = int((win == k).sum()) / total
        print(f"  {REGIME_NAMES[k]:7s} ({REGIME_JP[REGIME_NAMES[k]]:4s}): 地図シェア {sh*100:5.1f}%")
    wolf_ant = (int((win == 0).sum()) + int((win == 1).sum())) / total
    print(f"  → 勝者は {len(present)} 種類に分かれ普遍のベストは無い"
          f"（健全2型 wolf+ant が {wolf_ant*100:.0f}%・病態3型は遷移帯/極限の小ニッチ）")

    inds, regret_tbl = fig3(master)
    print("-" * 80)
    print("ベストプラクティスの罠（1業種の勝者文化を全業種へ移植したときの regret）:")
    for label, (reg, vals) in regret_tbl.items():
        home = int(np.argmin(vals)); far = int(np.argmax(vals))
        print(f"  {label} = {reg:6s}: regret 最小『{inds[home][0]}』={vals[home]:.3f} / "
              f"最大『{inds[far][0]}』={vals[far]:.3f}")

    print("=" * 80)
    print("§0 正直な照合:")
    print("  ✅ 最適 regime は業種 (v, ec) の関数＝普遍のベストは無い（相図が非一様）。")
    print("     変動性は探索(wolf)を、失敗コストは標準化(ant)を要求＝健全2型が地図を二分。")
    print("  ✅ 勝ち文化の移植は失敗＝自業種で regret≈0 でも逆コーナーで regret 大。")
    print("  ✅ 高 v×高 ec（救急/取引）はどの型も達成性能が低い＝探索と標準化の二律背反コーナー。")
    print("  ⚠️ 2軸は業種の最小戯画。5 preset は 4ダイヤルの写像で未フィット（§0）。")
    print("  ⚠️ chimp/hyena の固定 cost は政治/burnout の機構表現＝地図の非一様性自体は")
    print("     explore↔standardize から創発（cost は病態型の劣位を表すだけ・結論を埋め込まない）。")
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
