"""
定理A（報酬撤回 = 罰）— 単一エージェント・シミュレーション

検証する主張（docs/正本_ミクロ機構.md §4 修正項2, §6 定理A）:
  「u は参照点依存で κ>1。R_eff を ρ 未満に下げると δ は負かつ κ倍に増幅され、
   恐怖系の動態（τ↓・回避学習）を呼ぶ。報酬の撤回・相対的減額は『baseline に戻る』
   ではなく破壊エンジンへ押し込む別カテゴリ。維持できない報酬は据え付けてはいけない。」

3条件を比較:
  never      … 報酬を上げない（baseline のまま）
  sustained  … 報酬を上げて維持する（撤回しない）
  withdraw   … 報酬を上げてから撤回する（baseline へ戻す）

機構:
  - 参照点 ρ が経験報酬へ適応（快楽の踏み車）。引き上げを維持すると ρ も上がる。
  - 撤回時 R<ρ → u=κ(R−ρ) で負の δ が κ倍に増幅 → V 急落。
  - 負の損失 δ が恐怖エンジンを起動し τ を狭める（探索の崩壊）。V には書かない。
  - 「baseline に戻る」のではなく、never 条件より一時的に悪化する（破壊エンジン）。

出力: sim/out/figA1_timeseries.png, figA2_fear_tau.png, figA3_asymmetry.png ＋ stdout サマリ。
再現性: config.ConfigA.seed 固定（reward_noise=0 のときは決定論）。
実行: python sim/theorem_a_reward_withdrawal.py
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

from config import CONFIG_A as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

CONDITIONS = ("never", "sustained", "withdraw")
COLORS = {"never": "C0", "sustained": "C1", "withdraw": "C3"}


def schedule(cond, rng):
    """条件ごとの報酬系列 R[t]。"""
    R = np.full(C.T, C.R_base, dtype=float)
    if cond in ("sustained", "withdraw"):
        R[C.t1:] = C.R_high
    if cond == "withdraw":
        R[C.t2:] = C.R_base       # 撤回：baseline へ戻す
    if C.reward_noise > 0.0:
        R = R + rng.normal(0.0, C.reward_noise, size=C.T)
    return R


def run_agent(cond, rng):
    """1エージェントを T ステップ回し、V, δ, τ, ρ の時系列を返す。"""
    R = schedule(cond, rng)
    V = 0.0
    rho = C.R_base
    tau = C.tau_base
    Vh = np.empty(C.T)
    dh = np.empty(C.T)
    th = np.empty(C.T)
    rh = np.empty(C.T)
    for t in range(C.T):
        diff = R[t] - rho
        # 参照点依存・損失は κ倍に増幅（§4 修正項2）
        u = diff if diff >= 0.0 else C.kappa * diff
        delta = C.g * (u - V)
        V += C.eta * delta                              # マスター方程式 §5（V には u を通して書く）

        # --- 恐怖エンジン：負の損失 δ が τ を狭める（V には書かない）---
        if delta < 0.0:
            tau -= C.fear_c * (-delta)
            if tau < C.tau_min:
                tau = C.tau_min
        tau += C.tau_recover * (C.tau_base - tau)       # 平常へ緩和

        # 参照点が経験報酬へ適応（踏み車）
        rho += C.rho_rate * (R[t] - rho)

        Vh[t] = V
        dh[t] = delta
        th[t] = tau
        rh[t] = rho
    return Vh, dh, th, rh


def run_population(cond, base_rng):
    V = np.empty((C.n_agents, C.T))
    D = np.empty((C.n_agents, C.T))
    Tn = np.empty((C.n_agents, C.T))
    Rn = np.empty((C.n_agents, C.T))
    for i in range(C.n_agents):
        rng = np.random.default_rng(base_rng.integers(0, 2**63 - 1))
        v, d, tt, rr = run_agent(cond, rng)
        V[i] = v
        D[i] = d
        Tn[i] = tt
        Rn[i] = rr
    return V.mean(0), D.mean(0), Tn.mean(0), Rn.mean(0)


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def _phase_lines(ax):
    ax.axvline(C.t1, c="k", lw=0.8, alpha=0.35)
    ax.axvline(C.t2, c="k", lw=0.8, alpha=0.35)


def figA1(V, D):
    """FigA1: V(t) と δ(t)。撤回時にのみ κ倍の負の δ が出て V が baseline 以下へ。"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for cond in CONDITIONS:
        ax1.plot(V[cond], c=COLORS[cond], label=cond)
        ax2.plot(D[cond], c=COLORS[cond], label=cond)
    ax1.axhline(0, ls="--", c="gray", lw=1)
    _phase_lines(ax1)
    ax1.set(title="Theorem A: reward withdrawal vs never / sustained",
            ylabel="V (value of the deal)")
    ax1.text(C.t1, ax1.get_ylim()[1] * 0.95, " raise", fontsize=8, va="top")
    ax1.text(C.t2, ax1.get_ylim()[1] * 0.95, " withdraw", fontsize=8, va="top")
    ax1.legend(loc="center right")
    ax2.axhline(0, ls="--", c="gray", lw=1)
    _phase_lines(ax2)
    ax2.set(title="Prediction error delta (loss is kappa-amplified)",
            ylabel="delta", xlabel="step")
    ax2.legend(loc="lower right")
    fig.tight_layout()
    path = os.path.join(OUT, "figA1_timeseries.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figA1] saved -> {path}")


def figA2(Tn):
    """FigA2: τ(t)。撤回条件でのみ恐怖エンジンが起動し τ が崩壊（探索の狭窄）。"""
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for cond in CONDITIONS:
        ax.plot(Tn[cond], c=COLORS[cond], label=cond)
    ax.axhline(C.tau_base, ls="--", c="gray", lw=1, label="baseline tau")
    _phase_lines(ax)
    ax.set(title="Reward withdrawal fires the fear engine: exploration temperature tau collapses",
           ylabel="tau (exploration temperature)", xlabel="step", ylim=(0, C.tau_base * 1.15))
    ax.legend(loc="lower right")
    fig.tight_layout()
    path = os.path.join(OUT, "figA2_fear_tau.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figA2] saved -> {path}")


def figA3(give_peak, withdraw_trough, ratio, minV):
    """FigA3: (左) 損失/利得 の非対称 ≈ κ。(右) Phase C 最小V：withdraw は never より悪い。"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    ax1.bar(["raise\n(gain)", "withdrawal\n(loss)"], [give_peak, withdraw_trough],
            color=["C2", "C3"])
    ax1.axhline(0, c="gray", lw=1)
    # 利得を κ 倍した参照線（撤回の損失とほぼ一致するはず）
    ax1.axhline(-C.kappa * give_peak, ls="--", c="k", lw=1,
                label=f"-kappa x gain (kappa={C.kappa})")
    ax1.set(title=f"Loss is kappa-amplified: |delta_withdraw|/|delta_raise| = {ratio:.2f}",
            ylabel="peak delta at event")
    ax1.legend(loc="lower left")

    vals = [minV[c] for c in CONDITIONS]
    ax2.bar(list(CONDITIONS), vals, color=[COLORS[c] for c in CONDITIONS])
    ax2.axhline(0, ls="--", c="gray", lw=1)
    ax2.set(title="Post-phase minimum V: withdraw ends WORSE than 'never'",
            ylabel="min V after t1")
    for i, v in enumerate(vals):
        ax2.text(i, v, f"{v:.2f}", ha="center",
                 va="bottom" if v >= 0 else "top", fontsize=9)

    fig.suptitle("Withdrawing a reward is not 'returning to baseline' — it is a separate, destructive category")
    fig.tight_layout()
    path = os.path.join(OUT, "figA3_asymmetry.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figA3] saved -> {path}")


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 68)
    print("定理A 報酬撤回 = 罰 — single-agent simulation")
    print(f"seed={C.seed}  kappa={C.kappa}  R_base={C.R_base} R_high={C.R_high}")
    print("検証: 報酬の撤回は baseline 復帰でなく、κ倍の負δ→恐怖エンジン起動の別カテゴリ")
    print("=" * 68)

    V, D, Tn, Rn = {}, {}, {}, {}
    for cond in CONDITIONS:
        v, d, tt, rr = run_population(cond, _spawn(master))
        V[cond], D[cond], Tn[cond], Rn[cond] = v, d, tt, rr

    # サマリ統計
    w = 20
    dW = D["withdraw"]
    give_peak = float(dW[C.t1:C.t1 + w].max())          # 付与時の正の δ（利得・非増幅）
    withdraw_trough = float(dW[C.t2:C.t2 + w].min())    # 撤回時の負の δ（損失・κ倍）
    ratio = abs(withdraw_trough) / abs(give_peak) if give_peak != 0 else float("nan")
    minV = {c: float(V[c][C.t1:].min()) for c in CONDITIONS}
    minTauW = float(Tn["withdraw"][C.t2:].min())

    print(f"[delta] raise(gain)=+{give_peak:.3f}  withdraw(loss)={withdraw_trough:.3f}  "
          f"ratio|loss/gain|={ratio:.2f} (≈ kappa={C.kappa})")
    print(f"[V min after t1] never={minV['never']:.3f}  sustained={minV['sustained']:.3f}  "
          f"withdraw={minV['withdraw']:.3f}  <- withdraw < never ＝ baseline より悪い")
    print(f"[tau] withdraw min={minTauW:.3f} (baseline={C.tau_base})  "
          f"<- 恐怖エンジンで探索が崩壊")

    figA1(V, D)
    figA2(Tn)
    figA3(give_peak, withdraw_trough, ratio, minV)
    print("=" * 68)
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
