"""
多エージェント層 MA-2 — 社会的参照点（公平性）

検証する主張（docs/正本_ミクロ機構.md §4 修正項2, docs/多エージェント設計.md §3 MA-2）:
  参照点が社会的に決まる（ρ_i = ω·E_self + (1−ω)·他者の結果）とき、
  (1) 純粋な相対的剥奪：不遇側の絶対報酬が変わらなくても、他者が厚遇されるだけで
      ρ が引き上げられ R<ρ → κ倍の損失 → 士気崩壊（Brosnan-de Waal の cucumber-grape）。
  (2) 総報酬一定の再分配でも、κ>1 ゆえ不平等は純損失（不遇の損 > 厚遇の得）。

モデル（N 体 well-mixed・決定論）:
    R_i = 配分（favored: R_base+Δ_fav / disfavored: R_base+Δ_dis）
    peer_mean_i = 他者の平均報酬
    u_i = (R_i−ρ_i) if R_i≥ρ_i else κ(R_i−ρ_i)                    # 参照点依存・損失は κ倍
    V_i ← V_i + η(u_i − V_i)                                       # 士気
    ρ_i ← ρ_i + ρ_rate( [ω·R_i + (1−ω)·peer_mean_i] − ρ_i )       # 社会的参照点の適応

出力: sim/out/figE1_relative_deprivation.png, figE2_inequality_curve.png, figE3_asymmetry.png ＋ stdout。
実行: python sim/multiagent_social_reference.py
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

from config import CONFIG_SR as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def simulate(omega, delta_fav, delta_dis, introduce_at):
    """N 体を T ステップ。introduce_at 以降に favored=R_base+Δ_fav, disfavored=R_base+Δ_dis。
    平均V・厚遇V・不遇V・平均u の時系列を返す。"""
    N = C.N
    favored = np.zeros(N, dtype=bool)
    favored[: int(C.phi * N)] = True
    V = np.zeros(N)
    rho = np.full(N, C.R_base)
    meanV = np.empty(C.T)
    favV = np.empty(C.T)
    disV = np.empty(C.T)
    meanU = np.empty(C.T)
    for t in range(C.T):
        if t < introduce_at:
            R = np.full(N, C.R_base)
        else:
            R = np.where(favored, C.R_base + delta_fav, C.R_base + delta_dis)
        mean_all = R.mean()
        peer_mean = (N * mean_all - R) / (N - 1)         # 他者の平均
        diff = R - rho
        u = np.where(diff >= 0.0, diff, C.kappa * diff)   # 損失は κ倍（§4 修正項2）
        V = V + C.eta * (u - V)
        rho_target = omega * R + (1.0 - omega) * peer_mean
        rho = rho + C.rho_rate * (rho_target - rho)
        meanV[t] = V.mean()
        favV[t] = V[favored].mean()
        disV[t] = V[~favored].mean()
        meanU[t] = u.mean()
    return dict(meanV=meanV, favV=favV, disV=disV, meanU=meanU)


def figE1():
    """純粋な相対的剥奪：不遇側の絶対報酬は不変（R_base のまま）、他者だけ昇給(+Δ)。
    それでも不遇側の士気は崩落する（社会的参照点の引き上げ）。"""
    uneq = simulate(C.omega, C.Delta, 0.0, C.t_intro)     # favored +Δ, disfavored 据え置き
    ctrl = simulate(C.omega, 0.0, 0.0, C.t_intro)         # 統制：全員ずっと据え置き
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(uneq["favV"], c="C2", lw=2, label="favored (got a raise +Delta)")
    ax.plot(uneq["disV"], c="C3", lw=2.4, label="disfavored (pay UNCHANGED)")
    ax.plot(ctrl["disV"], c="gray", lw=1.5, ls="--", label="disfavored if no one was favored")
    ax.axhline(0, c="k", lw=0.8, alpha=0.4)
    ax.axvline(C.t_intro, c="k", lw=0.8, alpha=0.4)
    ax.text(C.t_intro, ax.get_ylim()[0] * 0.9, " others get a raise\n (your pay unchanged)", fontsize=8, va="bottom")
    ax.set(title="MA-2: pure relative deprivation. The disfavored's ABSOLUTE pay never changes,\n"
                 "yet their morale collapses once others are favored (Brosnan-de Waal cucumber-grape)",
           xlabel="step", ylabel="morale V")
    ax.legend(loc="lower left", fontsize=8)
    fig.tight_layout()
    path = os.path.join(OUT, "figE1_relative_deprivation.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figE1] saved -> {path}")
    return uneq, ctrl


def figE2():
    """総報酬一定の再分配（favored +Δ, disfavored −Δ, 平均不変）。
    不平等度 Δ → 最終平均士気。社会比較の強弱で2線。"""
    deltas = np.linspace(0.0, C.Delta_max, C.sweep_points)
    fig, ax = plt.subplots(figsize=(10, 5))
    out = {}
    for omega, label, color in ((C.omega_high_compare, "strong social comparison (low omega)", "C3"),
                                (C.omega_low_compare, "weak social comparison (high omega)", "C0")):
        finals = []
        for d in deltas:
            r = simulate(omega, d, -d, introduce_at=0)     # 再分配＝平均一定
            finals.append(r["meanV"][-50:].mean())
        finals = np.array(finals)
        out[label] = finals
        ax.plot(deltas, finals, "-o", ms=3, c=color, label=label)
    ax.axhline(0, c="gray", lw=1, ls="--")
    ax.set(title="Inequality destroys mean morale at CONSTANT total reward (because kappa>1)",
           xlabel="inequality magnitude Delta (mean reward held fixed)", ylabel="final mean morale V")
    ax.legend(loc="lower left")
    fig.tight_layout()
    path = os.path.join(OUT, "figE2_inequality_curve.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figE2] saved -> {path}")
    return deltas, out


def figE3():
    """総報酬一定の再分配での分解：厚遇の得 vs 不遇の損 の κ非対称、と純損。"""
    r = simulate(C.omega, C.Delta, -C.Delta, introduce_at=0)
    fav = r["favV"][-1]
    dis = r["disV"][-1]
    mean = r["meanV"][-1]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(["favored\ngain (+Delta)", "disfavored\nloss (-Delta)", "net mean\n(population)"],
                  [fav, dis, mean], color=["C2", "C3", "C0"])
    ax.axhline(0, c="k", lw=1)
    for b, v in zip(bars, [fav, dis, mean]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}",
                ha="center", va="bottom" if v >= 0 else "top", fontsize=10)
    ax.set(title=f"Constant total, +Delta/-Delta split: loss outweighs gain (kappa={C.kappa}) "
                 f"=> net morale < 0",
           ylabel="final morale V")
    fig.tight_layout()
    path = os.path.join(OUT, "figE3_asymmetry.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figE3] saved -> {path}")
    return fav, dis, mean


def main():
    os.makedirs(OUT, exist_ok=True)
    print("=" * 72)
    print("多エージェント MA-2 社会的参照点（公平性）— well-mixed simulation")
    print(f"N={C.N}  kappa={C.kappa}  omega={C.omega}  R_base={C.R_base}  Delta={C.Delta}")
    print("検証: 社会的参照点ゆえ、(1)絶対報酬不変でも相対的剥奪で士気崩壊 (2)総額一定でも不平等は純損")
    print("=" * 72)

    uneq, ctrl = figE1()
    deltas, sweep = figE2()
    fav, dis, mean = figE3()

    print(f"[figE1 純粋剥奪] 不遇の最終 morale={uneq['disV'][-1]:.3f}（絶対報酬は不変）"
          f" vs 誰も厚遇されなければ {ctrl['disV'][-1]:.3f}")
    print(f"[figE3 再分配]  厚遇の得=+{fav:.3f}  不遇の損={dis:.3f}  純平均={mean:.3f}（|損|>得＝κ非対称）")
    sc = sweep["strong social comparison (low omega)"]
    wc = sweep["weak social comparison (high omega)"]
    print(f"[figE2 スイープ] Δ={deltas[-1]:.1f} での最終平均士気: 強い社会比較={sc[-1]:.3f}  "
          f"弱い社会比較={wc[-1]:.3f}（比較が強いほど損が深い）")
    print("=" * 72)
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
