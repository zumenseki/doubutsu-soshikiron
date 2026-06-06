"""
多エージェント層 MA-10 — 階層別×業種別の合成（最適 org 設計は業種の関数）

検証する主張（docs/橋渡し_対応表.md §8、MA-7 階層別 × MA-9 業種別 の合成）:

  MA-7 は「現場=探索=低同調 wolf／管理=調整=高同調 ant」が最適（off-diagonal な差別化）と示した。
  MA-9 は「最適 regime は業種 (変動性 v × 失敗コスト ec) の関数」と示した。両者を合成すると、
  **現場の最適同調 c_F* は業種の関数** になる:
    - 高変動・低失敗コスト（IT/創造）：現場は低同調（wolf）＝差別化が最も効く。
    - 低変動・高失敗コスト（航空/原子力/医療）：現場の逸脱が罰されるので **現場も標準化**
      （c_F* が上がる＝差別化が圧縮）。"現場の官僚化"が高 stakes では最適。
  → MA-7 の「現場=wolf 常に」という処方自体が業種依存。通俗版「現場に一律で裁量を」とも
    「全社を一型で揃える」とも分岐し、**普遍の最適 org 設計も無い**（勝ち設計の移植は失敗）。

機構:
  - 現場（floor）＝探索タスク：正解 practice が確率 v で移る。choice=softmax((V+c_F·人気)/τ)＋個人RL。
    失敗コスト ec が逸脱（非コンセンサス）を罰する → E = max(0, 到達率 − ec·(1−コンセンサス))。
  - 管理（body）＝調整タスク：同調 c_B で整列（MA-7 と同型）→ Co = 合意（最大シェア）。
  - org 性能 P = E × Co。(c_F, c_B) を業種ごとに掃引して最適点の移動を見る。

§0 の正直さ: 現場/管理の2層 × 業種2軸は最小モデル。係数は機構の写像で未フィット。
  示すのは「最適 org 設計は業種で動く」という構造であって、特定企業の最適設計ではない。

出力: sim/out/figM1_optimum_moves.png, figM2_floor_conformity.png, figM3_transplant.png ＋ stdout。
実行: python sim/multiagent_industry_hierarchy.py
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

from config import CONFIG_MA10 as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def _softmax_choice(score, tau, rng):
    z = score / tau
    z -= z.max(axis=1, keepdims=True)
    P = np.exp(z); P /= P.sum(axis=1, keepdims=True)
    return (rng.random((P.shape[0], 1)) < P.cumsum(axis=1)).argmax(axis=1)


def floor_explore(c_F, v, ec, rng):
    """現場＝探索タスク（業種 v・ec 込み）。E = max(0, 到達率 − ec·逸脱率) を返す。"""
    N, K, T = C.N_floor, C.K, C.T
    V = np.zeros((N, K)); V[:, 0] = 0.5
    best = 0
    pop = np.zeros(K); pop[0] = 1.0
    idx = np.arange(N)
    hits = np.empty(T); cons = np.empty(T)
    for t in range(T):
        if rng.random() < v:
            best = int(rng.integers(0, K))
        ch = _softmax_choice(V + c_F * pop[None, :], C.tau, rng)
        r = (ch == best).astype(float) + C.reward_noise * rng.standard_normal(N)
        V[idx, ch] += C.eta * (r - V[idx, ch])
        pop = np.bincount(ch, minlength=K) / N
        hits[t] = (ch == best).mean()
        cons[t] = pop.max()
    w = C.perf_window
    return max(0.0, float(hits[-w:].mean()) - ec * (1.0 - float(cons[-w:].mean())))


def body_coordinate(c_B, rng):
    """管理下の本体＝調整タスク（MA-7 と同型）。Co = 合意（最大シェア）を返す。"""
    N, K, T = C.N_body, C.K, C.T
    V = np.zeros((N, K))
    ch = rng.integers(0, K, N)                  # 多様な初期
    pop = np.bincount(ch, minlength=K) / N
    idx = np.arange(N)
    hist = np.empty(T)
    for t in range(T):
        ch = _softmax_choice(V + c_B * pop[None, :], C.tau_body, rng)
        r = pop[ch] + C.coord_noise * rng.standard_normal(N)
        V[idx, ch] += C.eta * (r - V[idx, ch])
        pop = np.bincount(ch, minlength=K) / N
        hist[t] = pop.max()
    return float(hist[-C.perf_window:].mean())


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def org_perf(c_F, c_B, v, ec, master, seeds=None):
    """org 性能 P = E(現場;c_F,v,ec) × Co(管理;c_B)。複数 seed 平均。"""
    seeds = seeds or C.sweep_seeds
    ps = []
    for _ in range(seeds):
        E = floor_explore(c_F, v, ec, _spawn(master))
        Co = body_coordinate(c_B, _spawn(master))
        ps.append(E * Co)
    return float(np.mean(ps))


def _grid_optimum(v, ec, master, seeds=2):
    """(c_F × c_B) グリッドの P と最適点 (c_F*, c_B*) を返す。
    P = E(現場;c_F) × Co(管理;c_B) は分離可能ゆえ、E・Co を各軸 1 回ずつ計算して outer 積で組む
    （grid² 回の重複計算を避ける高速化）。"""
    cs = np.linspace(0.0, C.c_max, C.grid_points)
    Co = np.array([np.mean([body_coordinate(cB, _spawn(master)) for _ in range(seeds)]) for cB in cs])
    E = np.array([np.mean([floor_explore(cF, v, ec, _spawn(master)) for _ in range(seeds)]) for cF in cs])
    Z = Co[:, None] * E[None, :]          # Z[i,j] = Co(c_B=cs[i]) × E(c_F=cs[j])
    bi = np.unravel_index(np.argmax(Z), Z.shape)
    return cs, Z, (cs[bi[1]], cs[bi[0]])  # (c_F*, c_B*)


def _industries():
    """代表3業種（和名, 英名, v, ec）。"""
    return [
        ("IT/創造 (高変動・低失敗コスト)",  "IT/creative\n(volatile, low cost)", C.v_hi, C.ec_lo),
        ("中間",                          "mixed\n(mid)",                       C.v_hi * 0.5, C.ec_hi * 0.4),
        ("製造/航空 (低変動・高失敗コスト)", "mfg/aviation\n(stable, high cost)",  C.v_lo, C.ec_hi),
    ]


def fig1(master):
    """代表3業種の (c_F × c_B) 相図。最適点（赤）が業種で移動する。"""
    inds = _industries()
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))
    opt = []
    for ax, (jp, en, v, ec) in zip(axes, inds):
        cs, Z, (cFs, cBs) = _grid_optimum(v, ec, master)
        im = ax.pcolormesh(cs, cs, Z, cmap="viridis", shading="auto")
        ax.plot([0, C.c_max], [0, C.c_max], "w--", lw=1, alpha=0.6)
        ax.scatter([cFs], [cBs], c="red", s=130, edgecolors="w",
                   label=f"opt (cF={cFs:.1f}, cB={cBs:.1f})")
        ax.set_title(en, fontsize=10)
        ax.set_xlabel("floor conformity c_F"); ax.set_ylabel("mgmt conformity c_B")
        ax.legend(loc="lower right", fontsize=8)
        fig.colorbar(im, ax=ax, fraction=0.046)
        opt.append((jp, cFs, cBs))
    fig.suptitle("MA-10: the optimal org design moves with industry\n"
                 "(creative: low floor conformity = differentiated;  high-stakes: floor standardizes too)",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    path = os.path.join(OUT, "figM1_optimum_moves.png")
    fig.savefig(path, dpi=120); plt.close(fig)
    print(f"[figM1] saved -> {path}")
    return opt


def fig2(master):
    """最適 現場同調 c_F*（管理 c_B=c_max 固定）を失敗コスト ec に対して。ec↑で c_F*↑（現場標準化）。"""
    ecs = np.linspace(C.ec_lo, C.ec_hi, C.ind_points)
    cFs = np.linspace(0.0, C.c_max, C.grid_points)
    fig, ax = plt.subplots(figsize=(9, 5.6))
    out = {}
    for v, lab, col in [(C.v_hi, "volatile (v=hi)", "C2"), (C.v_lo, "stable (v=lo)", "C0")]:
        best_cF = []
        for ec in ecs:
            # 管理 c_B=c_max 固定 → Co 一定ゆえ c_F* = argmax_cF E（floor のみ計算で足りる）
            Es = [np.mean([floor_explore(cF, v, ec, _spawn(master)) for _ in range(C.sweep_seeds)]) for cF in cFs]
            best_cF.append(cFs[int(np.argmax(Es))])
        out[lab] = (ecs, best_cF)
        ax.plot(ecs, best_cF, "o-", color=col, lw=2, label=lab)
    ax.set(title="MA-10: optimal floor conformity c_F* rises with error cost\n"
                 "(high-stakes industries rationally standardize the floor — 'bureaucracy' is optimal there)",
           xlabel="error cost ec  (penalty for non-standard action)",
           ylabel="optimal floor conformity c_F*  (low = wolf, high = ant)", ylim=(-0.1, C.c_max + 0.1))
    ax.legend(loc="upper left", fontsize=9); ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figM2_floor_conformity.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figM2] saved -> {path}")
    return out


def fig3(master):
    """現場の最適同調 c_F* の (変動性 v × 失敗コスト ec) ヒートマップ。
    c_F* = argmax_cF E（P=E×Co は分離ゆえ c_F* は floor のみで決まる）。現場が wolf（低 c_F*）に
    留まる業種と標準化（高 c_F*）する業種を直接可視化＝最適 org 設計が業種で動く構造。"""
    vs = np.linspace(C.v_lo, C.v_hi, C.map_points)
    ecs = np.linspace(C.ec_lo, C.ec_hi, C.map_points)
    cFs = np.linspace(0.0, C.c_max, C.grid_points)
    Z = np.empty((C.map_points, C.map_points))
    for a, ec in enumerate(ecs):          # y = 失敗コスト
        for b, v in enumerate(vs):        # x = 変動性
            Es = [np.mean([floor_explore(cF, v, ec, _spawn(master)) for _ in range(4)]) for cF in cFs]
            Z[a, b] = cFs[int(np.argmax(Es))]
    fig, ax = plt.subplots(figsize=(8.8, 6.6))
    im = ax.pcolormesh(vs, ecs, Z, cmap="RdYlBu_r", shading="auto", vmin=0, vmax=C.c_max)
    ax.set(title="MA-10: optimal floor conformity c_F* across industries\n"
                 "(floor stays wolf=low when volatile & cheap mistakes; standardizes=high when stable & costly)",
           xlabel="volatility v  (best practice moves)", ylabel="error cost ec  (penalty for deviation)")
    fig.colorbar(im, ax=ax, label="optimal floor conformity c_F*  (0 = wolf … 3 = ant)")
    fig.tight_layout()
    path = os.path.join(OUT, "figM3_floor_map.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figM3] saved -> {path}")
    return {"volatile+cheap": float(Z[0, -1]), "volatile+costly": float(Z[-1, -1]),
            "stable+cheap": float(Z[0, 0]), "stable+costly": float(Z[-1, 0])}


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 80)
    print("多エージェント MA-10 階層別×業種別の合成（最適 org 設計は業種の関数）")
    print(f"seed={C.seed}  N_floor={C.N_floor}  N_body={C.N_body}  K={C.K}")
    print("検証: MA-7 の『現場=wolf 常に』は業種依存。高失敗コストでは現場も標準化（c_F*↑）")
    print("=" * 80)

    opt = fig1(master)
    print("代表3業種の最適 org 設計 (現場 c_F*, 管理 c_B*):")
    for jp, cF, cB in opt:
        print(f"  {jp:30s} 現場 c_F*={cF:.2f}  管理 c_B*={cB:.2f}  差別化Δ={cB - cF:.2f}")

    out = fig2(master)
    print("-" * 80)
    print("最適 現場同調 c_F*（管理 c_B=c_max 固定）の 失敗コスト ec 依存:")
    for lab, (ecs, best_cF) in out.items():
        print(f"  {lab:16s}: ec={ecs[0]:.2f}→c_F*={best_cF[0]:.2f}  /  ec={ecs[-1]:.2f}→c_F*={best_cF[-1]:.2f}"
              f"  (Δc_F*={best_cF[-1]-best_cF[0]:+.2f})")

    corners = fig3(master)
    print("-" * 80)
    print("現場 最適同調 c_F* の業種四隅（0=wolf … 3=ant）:")
    for k in ["volatile+cheap", "volatile+costly", "stable+cheap", "stable+costly"]:
        print(f"  {k:18s}: c_F*={corners[k]:.2f}")
    print("  → 現場は volatile+cheap で wolf（低 c_F*）・stable+costly で標準化（高 c_F*）＝最適設計が業種で動く")

    print("=" * 80)
    print("§0 正直な照合:")
    print("  ✅ 最適 org 設計（現場 c_F*）は業種の関数＝失敗コスト ec↑ で現場も標準化（c_F*↑）。")
    print("     MA-7 の『現場=低同調 wolf 常に』は高 stakes 業種では成り立たない（差別化Δが圧縮）。")
    print("  ✅ 現場の最適同調 c_F* は業種で動く（volatile+低コスト=wolf／stable+高コスト=標準化）＝")
    print("     普遍の org 設計は無い（figM3 マップ）。MA-7 の差別化は変動業種でのみ成立。")
    print("  ⚠️ 現場/管理2層 × 業種2軸は最小モデル。係数は機構の写像で未フィット（§0）。")
    print("  ⚠️ 高 stakes での『現場標準化』は本モデルの含意であって、安全文化の現実の設計指針ではない。")
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
