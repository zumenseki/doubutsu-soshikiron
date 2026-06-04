"""
多エージェント層 MA-3 — 方策模倣（規範・同調）

検証する主張（docs/多エージェント設計.md §3 MA-3、Layer2 の「同調」ダイヤル）:
  他者の選択（人気）を観察して模倣すると、規範（共有された方策）が創発する。
  しかし同調が強すぎると、より良い選択肢が存在しても、母集団は既存の規範
  （status quo）にロックインし、改善を採用できない＝前例主義（アリ型・Stage5硬直）。
  同調は両刃：強いほど合意（consensus）は速いが、誤った規範に固着するリスクが上がる。

モデル（N 体・K 選択肢・well-mixed）:
  score_i[a] = V_i[a] + κ_conf · pop[a]      （個人の価値 ＋ 同調＝人気バイアス）
  P_i = softmax(score_i / τ);  選択 a ~ P_i
  r = true_r[a] + noise;  V_i[a] ← V_i[a] + η(r − V_i[a])   （個人の RL）
  pop[a] = 母集団でその選択肢を選んだ割合（次ステップの同調信号）

  全員 status quo(option0, V=1.0) を知っている状態から開始。option1 はより良い(1.2)が
  探索して初めて分かる。低同調なら個人学習で option1 へ移行、高同調なら option0 に固着。

出力: sim/out/figF1_norm_formation.png, figF2_conformity_tradeoff.png, figF3_lockin.png ＋ stdout。
再現性: config.ConfigCF.seed 固定。実行: python sim/multiagent_policy_imitation.py
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

from config import CONFIG_CF as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
TRUE_R = np.array(C.true_r, dtype=float)


def simulate(kappa_conf, rng):
    """N 体を T ステップ。pop_hist (T,K)＝各ステップの選択肢シェアを返す。"""
    N, K = C.N, C.K
    V = np.zeros((N, K))
    V[:, C.incumbent] = C.V_init_incumbent          # 全員 status quo を知っている
    pop = np.zeros(K)
    pop[C.incumbent] = 1.0                           # 初期規範＝全員 incumbent
    pop_hist = np.empty((C.T, K))
    for t in range(C.T):
        score = V + kappa_conf * pop[None, :]        # 同調＝人気バイアス
        z = score / C.tau
        z -= z.max(axis=1, keepdims=True)
        P = np.exp(z)
        P /= P.sum(axis=1, keepdims=True)
        # 各エージェントが自分の P からカテゴリカル抽選
        cum = P.cumsum(axis=1)
        u = rng.random((N, 1))
        choices = (u < cum).argmax(axis=1)
        # 個人の RL 更新（選んだ選択肢のみ）
        r = TRUE_R[choices] + rng.normal(0.0, C.reward_noise, size=N)
        V[np.arange(N), choices] += C.eta * (r - V[np.arange(N), choices])
        # 同調信号の更新
        pop = np.bincount(choices, minlength=K) / N
        pop_hist[t] = pop
    return pop_hist


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def figF1(master):
    """規範形成：最良選択肢(option1)の採用率の時系列。低同調＝移行、高同調＝固着。"""
    low = simulate(0.0, _spawn(master))
    high = simulate(C.kappa_conf, _spawn(master))
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(low[:, C.best], c="C2", lw=2, label=f"best-practice adoption (low conformity, kappa=0)")
    ax.plot(high[:, C.best], c="C3", lw=2, label=f"best-practice adoption (high conformity, kappa={C.kappa_conf})")
    ax.plot(low[:, C.incumbent], c="C2", lw=1, ls="--", alpha=0.6, label="status-quo share (low conformity)")
    ax.plot(high[:, C.incumbent], c="C3", lw=1, ls="--", alpha=0.6, label="status-quo share (high conformity)")
    ax.set(title="MA-3: imitation forms norms. High conformity locks the population into the\n"
                 "status quo (option0=1.0) and fails to adopt the better practice (option1=1.2)",
           xlabel="step", ylabel="population share", ylim=(0, 1.02))
    ax.legend(loc="center right", fontsize=8)
    fig.tight_layout()
    path = os.path.join(OUT, "figF1_norm_formation.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figF1] saved -> {path}")
    print(f"[figF1] best-practice adoption (final): low conf={low[-50:, C.best].mean():.3f}  "
          f"high conf={high[-50:, C.best].mean():.3f}")


def figF2(master):
    """同調の両刃：κ_conf スイープ → 合意（consensus）↑ だが 最適性（mean reward）↓。"""
    xs = np.linspace(0.0, C.kappa_max, C.sweep_points)
    consensus = np.empty(C.sweep_points)
    optimality = np.empty(C.sweep_points)
    best_adopt = np.empty(C.sweep_points)
    for i, kc in enumerate(xs):
        cons_s, opt_s, best_s = [], [], []
        for _ in range(C.sweep_seeds):
            ph = simulate(kc, _spawn(master))
            final = ph[-50:].mean(axis=0)
            cons_s.append(final.max())               # 合意＝最大シェア
            opt_s.append(float(final @ TRUE_R))      # 平均報酬（最適性）
            best_s.append(final[C.best])
        consensus[i] = np.mean(cons_s)
        optimality[i] = np.mean(opt_s)
        best_adopt[i] = np.mean(best_s)
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(xs, consensus, "-o", ms=3, c="C0", label="consensus (modal share)")
    ax1.plot(xs, best_adopt, "-o", ms=3, c="C2", label="best-practice adoption")
    ax1.set(xlabel="conformity strength kappa_conf", ylabel="population share", ylim=(0, 1.03))
    ax2 = ax1.twinx()
    ax2.plot(xs, optimality, "-s", ms=3, c="C3", label="mean reward (optimality)")
    ax2.set_ylabel("mean reward", color="C3")
    ax2.tick_params(axis="y", labelcolor="C3")
    ax1.set_title("Conformity is two-edged: more conformity buys consensus but locks in a worse norm")
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="center right", fontsize=8)
    fig.tight_layout()
    path = os.path.join(OUT, "figF2_conformity_tradeoff.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figF2] saved -> {path}")
    print(f"[figF2] kappa=0: consensus={consensus[0]:.2f} best={best_adopt[0]:.2f} reward={optimality[0]:.3f} "
          f"| kappa={xs[-1]:.1f}: consensus={consensus[-1]:.2f} best={best_adopt[-1]:.2f} reward={optimality[-1]:.3f}")


def figF3(master):
    """ロックイン：全選択肢シェアの時系列。高同調では option1(最良) が離陸できない。"""
    low = simulate(0.0, _spawn(master))
    high = simulate(C.kappa_conf, _spawn(master))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    labels = [f"option{a}" + (" (status quo)" if a == C.incumbent else "")
              + (" (BEST)" if a == C.best else "") + f"  r={C.true_r[a]}" for a in range(C.K)]
    for a in range(C.K):
        ax1.plot(low[:, a], label=labels[a])
        ax2.plot(high[:, a], label=labels[a])
    ax1.set(title="Low conformity (kappa=0): migrates to the BEST practice",
            xlabel="step", ylabel="population share", ylim=(0, 1.02))
    ax2.set(title=f"High conformity (kappa={C.kappa_conf}): locked on the status quo",
            xlabel="step", ylim=(0, 1.02))
    ax1.legend(loc="center right", fontsize=8)
    fig.tight_layout()
    path = os.path.join(OUT, "figF3_lockin.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figF3] saved -> {path}")


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 74)
    print("多エージェント MA-3 方策模倣（規範・同調）— well-mixed simulation")
    print(f"seed={C.seed}  N={C.N}  K={C.K}  true_r={C.true_r}  "
          f"incumbent=option{C.incumbent} best=option{C.best}")
    print("検証: 模倣で規範が創発するが、同調が強すぎると status quo にロックインし改善を採れないか")
    print("=" * 74)
    figF1(_spawn(master))
    figF2(_spawn(master))
    figF3(_spawn(master))
    print("=" * 74)
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
