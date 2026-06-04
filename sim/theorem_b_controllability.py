"""
定理B（統制可能性の崖）— 単一エージェント・シミュレーション

検証する主張（docs/正本_ミクロ機構.md §6-7, docs/橋渡し_対応表.md §1③）:
  「同じ強度の罰でも、統制可能なら適応的回避、統制不能（恣意的）なら無力感。
   両者は連続的グラデーションでなく『質的な不連続』を示すはず。
   効くのは『どれだけ厳しいか』でなく『コントロールできるか』。」

機構（段差をハードコードせず、創発させる）:
  - 行動ゲート P(act)=σ(β(Ĝ−θ)): Ĝ が高い間だけ関与（行動）が持続する。
  - 自己封止更新: Ĝ は「行動した試行でのみ」観測統制性へ更新される。
    撤退すると更新が凍結し、低活動アトラクタが創発する（自然回復しない）。
  - 脱出: 外生的に行動を強制（確実に勝てる統制可能経験の注入）したときのみ Ĝ が回復。

出力:
  sim/out/fig1_timeseries.png       2条件の Ĝ・行動率の時系列（高位安定 vs 崩落）
  sim/out/fig2_intensity_sweep.png  罰強度スイープ → 最終Ĝ（統制可能=平坦, 不能=崖）
  sim/out/fig3_recovery.png         回復テスト（自然回復しない／外生注入で脱出）
  ＋ stdout に検証用サマリ

実行: python sim/theorem_b_controllability.py  （cwd に依らず動く）
再現性: config.seed 固定。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows コンソールでも日本語を安全に出す
except Exception:
    pass

import numpy as np
import matplotlib

matplotlib.use("Agg")  # 画面なしで PNG 保存
import matplotlib.pyplot as plt

from config import CONFIG as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# 条件コード
CONTROLLABLE = 0
UNCONTROLLABLE = 1


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def p_act(Ghat):
    """行動ゲート：Ĝ が閾値 θ を超える間だけ関与が立つ。
    Ĝ が give-up 閾値を下回ると撤退ラッチ（自発サンプリングを止める＝§1 自己封止）。
    注入（force）はこのラッチを無視して行動を起こせる＝唯一の脱出路。"""
    if Ghat < C.theta_giveup:
        return 0.0
    return float(sigmoid(C.beta * (Ghat - C.theta)))


def simulate(cond, intensity, force, rng):
    """1エージェントを len(cond) 試行回す。

    cond[t]      : 0=統制可能 / 1=統制不能
    intensity[t] : その試行の罰強度（統制可能では「行動しない時の罰率」、不能では「罰率」）
    force[t]     : True なら行動を強制（外生注入）
    返り値        : (Ghat_hist, acted_hist)
    """
    T = len(cond)
    Ghat = C.Ghat0
    Gh = np.empty(T)
    ac = np.zeros(T, dtype=bool)
    for t in range(T):
        acted = True if force[t] else (rng.random() < p_act(Ghat))

        if cond[t] == CONTROLLABLE:
            # 行動すれば回避できる。行動しなければ強度どおり罰。
            pp = C.p_punish_if_act if acted else intensity[t]
        else:
            # 統制不能：行動してもしなくても罰率は同じ（yoked）。
            pp = intensity[t]
        punished = rng.random() < pp

        # --- 自己封止更新：行動した試行でのみ Ĝ を更新する（要石）---
        if acted:
            g_trial = 0.0 if punished else 1.0   # 行動が罰を避けられたか＝統制の証拠
            delta = g_trial - Ghat
            if delta > 0.0:
                # 上方更新は帰属ゲート（現在のĜ＝統制感）でゲートする（docs §4 修正項1）。
                # 無力状態では「成功は自分のせい」と信じられず上方更新が立ち上がらない
                # → 低活動アトラクタが吸収的になり、稀な成功では雪だるま回復しない。
                Ghat += C.lam * Ghat * delta
            else:
                # 下方更新（悪い証拠）は素直に効く＝損失側が重い。
                Ghat += C.lam * delta
            if Ghat < C.Ghat_floor:
                Ghat = C.Ghat_floor
            elif Ghat > 1.0:
                Ghat = 1.0
        # 行動しなければ更新なし → 撤退が続くと Ĝ は凍結（低活動アトラクタ）

        Gh[t] = Ghat
        ac[t] = acted
    return Gh, ac


def run_population(cond, intensity, force, n_agents, base_rng):
    """n_agents 体を回し、(Ghat[n,T], acted[n,T]) を返す。"""
    T = len(cond)
    Gh = np.empty((n_agents, T))
    Ac = np.empty((n_agents, T))
    for i in range(n_agents):
        rng = np.random.default_rng(base_rng.integers(0, 2**63 - 1))
        g, a = simulate(cond, intensity, force, rng)
        Gh[i] = g
        Ac[i] = a
    return Gh, Ac


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def fig1(master):
    """Fig1: 同一強度の罰でも、統制可能/不能で Ĝ と行動率が分岐することを示す。"""
    T = C.T
    force = np.zeros(T, dtype=bool)
    inten = np.full(T, C.intensity_fig1)
    series = {}
    for name, code in (("controllable", CONTROLLABLE), ("uncontrollable", UNCONTROLLABLE)):
        cond = np.full(T, code)
        Gh, Ac = run_population(cond, inten, force, C.n_agents, _spawn(master))
        series[name] = (Gh.mean(0), Ac.mean(0))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    for name, (gh, ac) in series.items():
        ax1.plot(gh, label=name)
        ax2.plot(ac, label=name)
    ax1.axhline(C.theta, ls="--", c="gray", lw=1, label="gate threshold")
    ax1.set(title="Theorem B: controllability belief (Ghat) over time",
            xlabel="trial", ylabel="Ghat", ylim=(0, 1))
    ax2.set(title="Engagement (action rate) over time",
            xlabel="trial", ylabel="action rate", ylim=(0, 1))
    ax1.legend()
    ax2.legend()
    fig.suptitle(f"Same punishment intensity = {C.intensity_fig1}  |  controllable vs uncontrollable")
    fig.tight_layout()
    path = os.path.join(OUT, "fig1_timeseries.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)

    print(f"[fig1] final Ghat   : controllable={series['controllable'][0][-1]:.3f}  "
          f"uncontrollable={series['uncontrollable'][0][-1]:.3f}")
    print(f"[fig1] final act-rate: controllable={series['controllable'][1][-1]:.3f}  "
          f"uncontrollable={series['uncontrollable'][1][-1]:.3f}")
    print(f"[fig1] saved -> {path}")


def fig2(master):
    """Fig2: 罰強度を連続に振り、最終Ĝを見る。不連続(崖)は強度でなく統制性が駆動。"""
    xs = np.linspace(0.0, 1.0, C.sweep_points)
    T = C.T_sweep
    finalG = {CONTROLLABLE: [], UNCONTROLLABLE: []}
    finalA = {CONTROLLABLE: [], UNCONTROLLABLE: []}
    for code in (CONTROLLABLE, UNCONTROLLABLE):
        cond = np.full(T, code)
        force = np.zeros(T, dtype=bool)
        for x in xs:
            inten = np.full(T, x)
            Gh, Ac = run_population(cond, inten, force, C.n_agents, _spawn(master))
            finalG[code].append(Gh[:, -50:].mean())
            finalA[code].append(Ac[:, -50:].mean())
    finalG = {k: np.array(v) for k, v in finalG.items()}
    finalA = {k: np.array(v) for k, v in finalA.items()}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    ax1.plot(xs, finalG[CONTROLLABLE], "-o", ms=3, label="controllable")
    ax1.plot(xs, finalG[UNCONTROLLABLE], "-o", ms=3, label="uncontrollable")
    ax1.axhline(C.theta, ls="--", c="gray", lw=1, label="gate threshold")
    ax1.set(title="Final Ghat vs punishment intensity",
            xlabel="punishment intensity", ylabel="final Ghat", ylim=(0, 1))
    ax2.plot(xs, finalA[CONTROLLABLE], "-o", ms=3, label="controllable")
    ax2.plot(xs, finalA[UNCONTROLLABLE], "-o", ms=3, label="uncontrollable")
    ax2.set(title="Final engagement vs punishment intensity",
            xlabel="punishment intensity", ylabel="final action rate", ylim=(0, 1))
    ax1.legend()
    ax2.legend()
    fig.suptitle("Discontinuity is driven by controllability, not intensity")
    fig.tight_layout()
    path = os.path.join(OUT, "fig2_intensity_sweep.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)

    dG_unc = np.gradient(finalG[UNCONTROLLABLE], xs)
    ci = int(np.argmin(dG_unc))
    print(f"[fig2] uncontrollable cliff near intensity={xs[ci]:.2f} "
          f"(steepest dGhat/dI={dG_unc[ci]:.2f})")
    print(f"[fig2] controllable final Ghat range=[{finalG[CONTROLLABLE].min():.3f},"
          f"{finalG[CONTROLLABLE].max():.3f}] (flat-high)")
    print(f"[fig2] uncontrollable final Ghat range=[{finalG[UNCONTROLLABLE].min():.3f},"
          f"{finalG[UNCONTROLLABLE].max():.3f}] (collapses)")
    print(f"[fig2] max |dGhat/dI|: controllable={np.abs(np.gradient(finalG[CONTROLLABLE], xs)).max():.2f}  "
          f"uncontrollable={np.abs(dG_unc).max():.2f}")
    print(f"[fig2] saved -> {path}")


def fig3(master):
    """Fig3: 定理Bの脱出条項。Phase1 不能で崩落→Phase2 可能でも自然回復しない
    →Phase3 外生注入（行動強制）で初めて脱出。"""
    Tp = C.T_phase
    cond = np.concatenate([np.full(Tp, UNCONTROLLABLE),
                           np.full(Tp, CONTROLLABLE),
                           np.full(Tp, CONTROLLABLE)])
    inten = np.full(3 * Tp, C.intensity_fig1)
    force = np.concatenate([np.zeros(Tp, bool),
                            np.zeros(Tp, bool),
                            np.ones(Tp, bool)])   # Phase3 のみ行動強制＝外生注入
    Gh, Ac = run_population(cond, inten, force, C.n_agents, _spawn(master))
    g = Gh.mean(0)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(g, c="C3", label="mean Ghat")
    ax.axhline(C.theta, ls="--", c="gray", lw=1, label="gate threshold")
    for b in (Tp, 2 * Tp):
        ax.axvline(b, c="k", lw=0.8, alpha=0.4)
    ax.set(title="Theorem B escape: no self-recovery; exogenous injection rescues",
           xlabel="trial", ylabel="Ghat", ylim=(0, 1))
    ax.text(Tp * 0.5, 0.72, "Phase1\nuncontrollable", ha="center", va="top", fontsize=9)
    ax.text(Tp * 1.5, 0.72, "Phase2\ncontrollable\n(no injection)", ha="center", va="top", fontsize=9)
    ax.text(Tp * 2.5, 0.72, "Phase3\ninjection\n(forced action)", ha="center", va="top", fontsize=9)
    ax.legend(loc="center right")
    fig.tight_layout()
    path = os.path.join(OUT, "fig3_recovery.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)

    print(f"[fig3] Ghat end of Phase1 (uncontrollable)       = {g[Tp - 1]:.3f}")
    print(f"[fig3] Ghat end of Phase2 (controllable, no inj.) = {g[2 * Tp - 1]:.3f}   <- 自然回復しない")
    print(f"[fig3] Ghat end of Phase3 (injection)             = {g[3 * Tp - 1]:.3f}   <- 外生注入で脱出")
    print(f"[fig3] saved -> {path}")


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 64)
    print("定理B 統制可能性の崖 — single-agent simulation")
    print(f"seed={C.seed}  n_agents={C.n_agents}")
    print("検証: 同強度の罰でも統制可能/不能で Ghat・行動が質的不連続に分岐するか")
    print("=" * 64)
    fig1(_spawn(master))
    fig2(_spawn(master))
    fig3(_spawn(master))
    print("=" * 64)
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
