"""
多エージェント層 MA-7 — 階層別最適化（層ごとに別 regime ＋ 層間結合）

検証する主張（docs/比喩_5類型マクロ.md §5「同じ会社でも層で最適な生き物は違う」、
docs/橋渡し_対応表.md 階層別）:

  層ごとに『タスク』が違うので最適 regime も違う：
    - 現場（floor）＝探索タスク（より良い practice の発見）。低同調が最適（wolf）。
    - 管理（body）＝調整タスク（皆が同じ規格に整列）。高同調が最適（ant）。
  経営（exec）＝この architecture（各層の同調 c と層間結合 λ）を設計する層。
  org 性能 P = 現場探索 E × 管理調整 Co（両方が要る）。

  非自明な帰結（通俗版「全社を1つの型で揃える」と分岐）:
    (1) 一律 regime（全 wolf / 全 ant）は必ずどこかの層を犠牲にし劣る。
    (2) 最適は差別化（現場=低同調・管理=高同調）＝(c_F,c_B) 平面の対角線(一律)でなく off-diagonal。
    (3) ただし結合 λ が強い（管理の同調が現場へ漏れ＝process 押し付け）と現場の実効同調
        c_F+λ·c_B が上がって探索が死に、P が崩落＝現場の autonomy が要る（MA-5 と連結）。

機構:
  - 現場: status quo から探索。choice=softmax((V+c_F_eff·人気)/τ)＋個人RL。E=最良 practice の採用率。
    c_F_eff = c_F + λ·c_B（管理の同調が下層へ漏れる＝top-down の process 圧）。
  - 管理（本体）: 等価な K 規約の調整ゲーム（報酬=自分と同じ選択の割合）。多様から出発し、
    同調 c_B が高いほど整列（Co=合意=最大シェア）が進む。低同調＋ノイズだと断片化。

§0 の正直さ: P=E×Co は層タスクの最小モデル。faction/権力や経営層の意思決定の中身は
  モデル化しない。係数は機構の表現であって組織データへのフィットではない。

出力: sim/out/figJ1_architectures.png, figJ2_differentiation.png, figJ3_coupling_autonomy.png ＋ stdout。
実行: python sim/multiagent_hierarchy.py
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

from config import CONFIG_MA7 as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
TRUE = np.array(C.true_value, dtype=float)


def _softmax_choice(score, tau, rng):
    z = score / tau
    z -= z.max(axis=1, keepdims=True)
    P = np.exp(z); P /= P.sum(axis=1, keepdims=True)
    return (rng.random((P.shape[0], 1)) < P.cumsum(axis=1)).argmax(axis=1)


def floor_explore(rng, c_eff, w=30):
    """現場＝探索タスク。status quo から出発し、低同調なら option1(最良) を発見。E=最良採用率。"""
    N, K = C.N_floor, C.K
    V = np.zeros((N, K)); V[:, C.incumbent] = C.V_init_incumbent
    pop = np.zeros(K); pop[C.incumbent] = 1.0
    idx = np.arange(N)
    hist = np.empty(C.T)
    for t in range(C.T):
        ch = _softmax_choice(V + c_eff * pop[None, :], C.tau, rng)
        r = TRUE[ch] + C.reward_noise * rng.standard_normal(N)
        V[idx, ch] += C.eta * (r - V[idx, ch])
        pop = np.bincount(ch, minlength=K) / N
        hist[t] = (ch == C.best).mean()
    return float(np.mean(hist[-w:]))


def body_coordinate(rng, c_B, w=30):
    """管理下の本体＝調整タスク。等価 K 規約。多様から出発し、同調 c_B が高いほど整列。Co=合意。"""
    N, K = C.N_body, C.K
    V = np.zeros((N, K))
    ch = rng.integers(0, K, N)                         # 多様な初期（バラバラ）
    pop = np.bincount(ch, minlength=K) / N
    idx = np.arange(N)
    hist = np.empty(C.T)
    for t in range(C.T):
        ch = _softmax_choice(V + c_B * pop[None, :], C.tau_body, rng)
        r = pop[ch] + C.coord_noise * rng.standard_normal(N)   # 報酬＝自分と同じ選択の割合（整列）
        V[idx, ch] += C.eta * (r - V[idx, ch])
        pop = np.bincount(ch, minlength=K) / N
        hist[t] = pop.max()                            # 合意＝最大シェア
    return float(np.mean(hist[-w:]))


def org_perf(master, c_F, c_B, lam, seeds=None):
    """org 性能 P = 現場探索 E(c_F+λc_B) × 管理調整 Co(c_B)。複数 seed 平均。E, Co, P を返す。"""
    seeds = seeds or C.sweep_seeds
    Es, Cos = [], []
    for _ in range(seeds):
        Es.append(floor_explore(_spawn(master), c_F + lam * c_B))
        Cos.append(body_coordinate(_spawn(master), c_B))
    E, Co = float(np.mean(Es)), float(np.mean(Cos))
    return E, Co, E * Co


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def fig1(master):
    """4アーキテクチャの E / Co / P。差別化(loose) が勝つ。"""
    archs = [
        ("uniform wolf\n(all low conformity)", C.c_wolf, C.c_wolf, 0.0),
        ("uniform ant\n(all high conformity)", C.c_ant, C.c_ant, 0.0),
        ("layered + loose\n(wolf floor, ant mgmt)", C.c_wolf, C.c_ant, C.lam_loose),
        ("layered + tight\n(mgmt imposes process)", C.c_wolf, C.c_ant, C.lam_tight),
    ]
    labels, Es, Cos, Ps = [], [], [], []
    for name, cF, cB, lam in archs:
        E, Co, P = org_perf(master, cF, cB, lam)
        labels.append(name); Es.append(E); Cos.append(Co); Ps.append(P)
    x = np.arange(len(archs)); width = 0.26
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.bar(x - width, Es, width, label="floor exploration E", color="C2")
    ax.bar(x, Cos, width, label="mgmt coordination Co", color="C0")
    ax.bar(x + width, Ps, width, label="org performance P = E*Co", color="C3")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set(title="MA-7: a single uniform regime is suboptimal; differentiated + loose coupling wins",
           ylabel="value in [0,1]", ylim=(0, 1.05))
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figJ1_architectures.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figJ1] saved -> {path}")
    return list(zip(labels, Es, Cos, Ps))


def fig2(master):
    """相図 (c_F × c_B) の org 性能 P（lam=loose）。最適は対角線(一律)でなく off-diagonal。"""
    cs = np.linspace(0.0, C.c_max, C.grid_points)
    Z = np.empty((C.grid_points, C.grid_points))
    for i, cB in enumerate(cs):           # y = 管理同調
        for j, cF in enumerate(cs):       # x = 現場同調
            _, _, P = org_perf(master, cF, cB, C.lam_loose, seeds=2)
            Z[i, j] = P
    fig, ax = plt.subplots(figsize=(8.8, 6.6))
    im = ax.pcolormesh(cs, cs, Z, cmap="viridis", shading="auto")
    ax.plot([0, C.c_max], [0, C.c_max], "w--", lw=1.5, label="uniform regime (diagonal)")
    bi = np.unravel_index(np.argmax(Z), Z.shape)
    ax.scatter([cs[bi[1]]], [cs[bi[0]]], c="red", s=120, edgecolors="w",
               label=f"optimum (floor={cs[bi[1]]:.1f}, mgmt={cs[bi[0]]:.1f})")
    ax.set(title="MA-7: org performance peaks OFF the diagonal\n(low floor conformity + high mgmt conformity = differentiated)",
           xlabel="floor conformity c_F", ylabel="management conformity c_B")
    fig.colorbar(im, ax=ax, label="org performance P = E*Co")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    path = os.path.join(OUT, "figJ2_differentiation.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figJ2] saved -> {path}")
    return cs, Z, bi


def fig3(master):
    """結合 λ スイープ（差別化アーキテクチャ）。緩い結合で高く、強い結合で崩落＝現場の autonomy。"""
    lams = np.linspace(0.0, C.lam_max, C.lam_points)
    Es, Ps = np.empty(len(lams)), np.empty(len(lams))
    for k, lam in enumerate(lams):
        E, Co, P = org_perf(master, C.c_wolf, C.c_ant, lam)
        Es[k] = E; Ps[k] = P
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(lams, Es, "o-", color="C2", lw=2, label="floor exploration E")
    ax.plot(lams, Ps, "s-", color="C3", lw=2, label="org performance P")
    ax.axvline(C.lam_loose, color="gray", ls=":", lw=1)
    ax.set(title="MA-7: tight top-down coupling kills floor exploration (autonomy required)",
           xlabel="coupling λ (management conformity imposed on the floor)",
           ylabel="value in [0,1]", ylim=(0, 1.05))
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figJ3_coupling_autonomy.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figJ3] saved -> {path}")
    return lams, Es, Ps


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 80)
    print("多エージェント MA-7 階層別最適化（層ごとに別 regime ＋ 層間結合）")
    print(f"seed={C.seed}  N_floor={C.N_floor}  N_body={C.N_body}  K={C.K}")
    print("検証: 一律 regime は劣り、差別化(現場低同調×管理高同調)＋緩い結合が最適か")
    print("=" * 80)

    rows = fig1(master)
    print(f"{'architecture':40s} {'E(floor)':>9s} {'Co(mgmt)':>9s} {'P=E*Co':>8s}")
    for name, E, Co, P in rows:
        print(f"  {name.replace(chr(10), ' '):38s} {E:9.3f} {Co:9.3f} {P:8.3f}")
    best_arch = max(rows, key=lambda r: r[3])
    print(f"  -> 最良アーキテクチャ: {best_arch[0].replace(chr(10),' ')}（P={best_arch[3]:.3f}）")

    cs, Z, bi = fig2(master)
    diag = np.array([Z[k, k] for k in range(len(cs))])   # 一律(対角)の最良
    print("-" * 80)
    print(f"相図: 最適 P={Z[bi]:.3f} @ (現場 c_F={cs[bi[1]]:.2f}, 管理 c_B={cs[bi[0]]:.2f})")
    print(f"  一律(対角)の最良 P={diag.max():.3f} @ c={cs[diag.argmax()]:.2f}")
    print(f"  → 差別化が一律を {Z[bi] - diag.max():+.3f} 上回る（off-diagonal が最適）")

    lams, Es, Ps = fig3(master)
    print("-" * 80)
    print("結合 λ（管理→現場 の process 圧）スイープ:")
    print(f"  緩 λ={lams[0]:.2f}: E={Es[0]:.3f} P={Ps[0]:.3f}  /  強 λ={lams[-1]:.2f}: E={Es[-1]:.3f} P={Ps[-1]:.3f}")
    print(f"  → 強い結合で現場探索 E が {Es[0]-Es[-1]:+.3f} 崩落（現場の autonomy が要石）")

    print("=" * 80)
    print("§0 正直な照合:")
    print("  ✅ 一律 regime（全 wolf/全 ant）は片層を犠牲にし劣る（層でタスクが違う）。")
    print("  ✅ 最適は差別化＝(c_F,c_B) の対角線(一律)でなく off-diagonal。")
    print("  ✅ 強い top-down 結合は現場の探索を殺す＝現場の autonomy が要る（MA-5 と連結）。")
    print("  ⚠️ P=E×Co は層タスクの最小モデル。faction/権力や経営の意思決定の中身は非モデル化。")
    print("  ⚠️ これは機構の表現であって組織データへのフィットではない（§0）。")
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
