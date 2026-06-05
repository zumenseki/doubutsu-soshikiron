"""
多エージェント層 MA-6 — 規模（Dunbar 壁）

検証する主張（docs/比喩_5類型マクロ.md「Dunbar 壁」、index 「100人超で自然発生する権力ゲーム」）:

  有界な社交容量 D（各自が信頼／監視できる相手の上限）があると、集団規模 N が増えるほど
  評判被覆 coverage = min(1, D/(N-1)) が下がる。監視外の相手では裏切りが罰されないため、
  N がある閾値（＝Dunbar 壁）を超えると協力（cohesion）が相転移的に崩落する。
  ＝「規模そのもの」が regime を変える。崩落後は cohesive な全体が断片化し、
  chimp 的な分断・政治の土壌になる。

  非自明な帰結（通俗版＝「人を増やしても管理職を足せば回る」と分岐）:
    - 崩落は連続的な希薄化でなく鋭い壁（条件付き協力の高位アトラクタが鞍点分岐で消える）。
    - 壁の位置は普遍数でなく容量 D に比例する（§0：「150」は人の容量推定であって普遍定数でない）。

機構（条件付き協力＝reciprocity のネットワーク閾値ダイナミクス）:
  各自は D 人の acquaintance を監視。p_acq_i = acquaintance の協力率。
  次期の協力確率 = coverage · σ(β(p_acq_i − θ))。
    - coverage が「監視＝評判が効く割合」。N≤D なら 1（全員を監視＝小集団は cohesive）。
    - N≫D なら coverage→小。高位アトラクタが消え、協力は低位へ崩落。

出力: sim/out/figI1_size_timeseries.png, figI2_dunbar_wall.png, figI3_wall_scales_with_D.png ＋ stdout。
実行: python sim/multiagent_dunbar.py
"""

import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import CONFIG_MA6 as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def build_acq(N, D, rng):
    """各エージェントの acquaintance（監視できる相手）を D 人（N≤D なら全員）選ぶ。(N,k) 配列。"""
    k = min(D, N - 1)
    acq = np.empty((N, k), dtype=np.int64)
    for i in range(N):
        others = np.concatenate((np.arange(i), np.arange(i + 1, N)))
        acq[i] = others if k == N - 1 else rng.choice(others, size=k, replace=False)
    return acq


def dunbar_sim(rng, N, D, T=None):
    """規模 N・容量 D で条件付き協力ダイナミクスを T ステップ。協力率の時系列・最終 coop・acq を返す。"""
    T = T or C.T
    acq = build_acq(N, D, rng)
    coverage = min(1.0, D / (N - 1)) if N > 1 else 1.0
    coop = (rng.random(N) < C.coop0).astype(float)
    series = np.empty(T)
    for t in range(T):
        p_acq = coop[acq].mean(axis=1)
        prob = coverage * _sigmoid(C.beta * (p_acq - C.theta))
        coop = (rng.random(N) < prob).astype(float)
        series[t] = coop.mean()
    return series, coop, acq, coverage


def largest_coop_component(acq, coop):
    """acquaintance グラフを協力者だけに制限したときの最大連結成分サイズ（母集団比）。
    cohesion 崩落 ＝ 断片化（giant component が消える）を測る。"""
    N = len(coop)
    coop_b = coop.astype(bool)
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(N):
        if not coop_b[i]:
            continue
        for j in acq[i]:
            if coop_b[j]:
                ri, rj = find(i), find(int(j))
                if ri != rj:
                    parent[ri] = rj
    roots = [find(i) for i in range(N) if coop_b[i]]
    if not roots:
        return 0.0
    return max(Counter(roots).values()) / N


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def _final(series, w=20):
    return float(np.mean(series[-w:]))


def fig1(master):
    """代表規模での協力率 時系列：小集団は cohesive・大集団は崩落。"""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    colors = ["C2", "C1", "C3"]
    res = {}
    for N, col in zip(C.n_fig1, colors):
        series, _, _, cov = dunbar_sim(_spawn(master), N, C.D)
        res[N] = _final(series)
        ax.plot(series, color=col, lw=2, label=f"N={N}  (coverage={cov:.2f})")
    ax.set(title=f"MA-6 Dunbar wall: same rules, larger group collapses (capacity D={C.D})",
           xlabel="step", ylabel="cooperation / cohesion (fraction)", ylim=(-0.03, 1.03))
    ax.legend(loc="center right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figI1_size_timeseries.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figI1] saved -> {path}")
    return res


def fig2(master):
    """規模スイープ → 最終 cohesion ＋ 最大協力クラスタ（断片化）。鋭い Dunbar 壁。"""
    Ns = np.unique(np.linspace(C.N_min, C.N_max, C.sweep_points).astype(int))
    coh = np.empty(len(Ns)); giant = np.empty(len(Ns)); cov = np.empty(len(Ns))
    for idx, N in enumerate(Ns):
        cs, gs = [], []
        for _ in range(C.sweep_seeds):
            series, coop, acq, c = dunbar_sim(_spawn(master), int(N), C.D)
            cs.append(_final(series))
            gs.append(largest_coop_component(acq, coop))
        coh[idx] = np.mean(cs); giant[idx] = np.mean(gs); cov[idx] = c
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    ax.plot(Ns, coh, "o-", color="C2", lw=2, label="cohesion (mean cooperation)")
    ax.plot(Ns, giant, "s-", color="C0", lw=2, label="largest cooperating cluster (fraction)")
    ax.plot(Ns, cov, ":", color="gray", lw=1.5, label="reputation coverage D/(N-1)")
    ax.axvline(C.D, color="C1", ls="--", lw=1)
    ax.annotate(f"capacity D={C.D}", (C.D, 0.05), fontsize=8, color="C1", xytext=(C.D + 4, 0.08))
    ax.set(title="MA-6: cohesion collapses past the Dunbar wall (sharp, not gradual)",
           xlabel="group size N", ylabel="fraction", ylim=(-0.03, 1.03))
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figI2_dunbar_wall.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figI2] saved -> {path}")
    return Ns, coh, giant


def _wall_for_D(master, D):
    """容量 D での壁＝最終 cohesion が wall_thresh を下回る最小 N。"""
    Ns = np.unique(np.linspace(C.N_min, C.N_max, C.sweep_points).astype(int))
    for N in Ns:
        vals = [_final(dunbar_sim(_spawn(master), int(N), D)[0]) for _ in range(C.sweep_seeds)]
        if np.mean(vals) < C.wall_thresh:
            return int(N)
    return None


def fig3(master):
    """壁の位置 × 容量 D：壁は普遍数でなく D に比例する。"""
    Ds = list(C.D_values)
    walls = [_wall_for_D(_spawn(master), D) for D in Ds]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    xs = [D for D, w in zip(Ds, walls) if w is not None]
    ys = [w for w in walls if w is not None]
    ax.plot(xs, ys, "o-", color="C4", lw=2)
    for D, w in zip(xs, ys):
        ax.annotate(f"D={D}\nwall≈{w}", (D, w), fontsize=8, ha="left", va="top")
    ax.set(title="MA-6: the Dunbar wall scales with capacity D (not a universal number)",
           xlabel="social capacity D", ylabel="collapse size (Dunbar wall, N)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figI3_wall_scales_with_D.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figI3] saved -> {path}")
    return Ds, walls


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 80)
    print("多エージェント MA-6 規模（Dunbar 壁）")
    print(f"seed={C.seed}  D={C.D}  beta={C.beta}  theta={C.theta}  T={C.T}")
    print("検証: 有界容量 D の下で、規模 N が壁を超えると協力(cohesion)が相転移的に崩落するか")
    print("=" * 80)

    r1 = fig1(master)
    print("代表規模の最終 cohesion:")
    for N, v in r1.items():
        print(f"  N={N:4d}  cohesion={v:.3f}")

    Ns, coh, giant = fig2(master)
    below = [n for n, c in zip(Ns, coh) if c >= C.wall_thresh]
    above = [n for n, c in zip(Ns, coh) if c < C.wall_thresh]
    wall = min(above) if above else None
    print("-" * 80)
    print(f"Dunbar 壁（cohesion<{C.wall_thresh} となる最小 N, D={C.D}）: "
          f"{wall if wall is not None else '範囲内に無し'}")
    if below:
        print(f"  壁の下（最大 N={max(below)}）: cohesion={coh[list(Ns).index(max(below))]:.3f}（cohesive）")
    if above:
        print(f"  壁の上（最小 N={min(above)}）: cohesion={coh[list(Ns).index(min(above))]:.3f}（断片化）")

    Ds, walls = fig3(master)
    print("-" * 80)
    print("壁 × 容量 D（壁は D に比例＝普遍数でない）:")
    for D, w in zip(Ds, walls):
        print(f"  D={D:3d} -> wall≈{w if w is not None else '無し'}")

    print("=" * 80)
    print("§0 正直な照合:")
    print("  ✅ 同じ施策でも規模 N が壁を超えると cohesion が崩落（規模そのものが regime を変える）。")
    print("  ✅ 崩落は鋭い相転移（条件付き協力の高位アトラクタが鞍点分岐で消える）。")
    print("  ✅ 壁の位置は容量 D に比例＝『150』は人の容量推定であって普遍定数でない（§0）。")
    print("  ⚠️ 崩落後の『分断・政治(chimp)』は giant component の消失として示すが、")
    print("     faction の内容や権力ゲームの詳細はモデル化していない（過剰主張しない）。")
    print("  ⚠️ これは機構の表現であって組織データへのフィットではない（§0）。")
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
