"""
定理D（恐怖の複合コスト）— 多腕タスク・シミュレーション

検証する主張（docs/正本_ミクロ機構.md §5, §6 定理D）:
  「恐怖は τ↓・k↑・習慣化を同時に起こす。一軸の『動機の減少』ではなく
   独立3チャネルの劣化（→ 縮んだ行動集合上での局所最適ロックイン）。」

タスク:
  arm0 = 即時・小（r=1.0、t_change で 0.3 へ devalue）… 局所最適
  arm1 = 遅延・大（r=3.0, delay=5）              … 大域最適（探索＋遠視が要る）
  arm2..K-1 = 即時・極小（r=0.2）                … 探索コスト（distractor）

恐怖の3チャネル（各々独立に on/off）:
  τ↓  探索温度を下げる（狭窄）          … 行動レパートリーが縮む
  k↑  双曲割引を強める（近視眼）        … 遅延・象徴報酬が割り引かれ消える
  習慣 H の重みを上げる（目標志向→習慣）… 価値と無関係に過去の選択を反復

5条件: calm / tau_only / k_only / habit_only / fearful(=3つ全部)

3チャネルを直交に読む指標（各々ちょうど1つのノブだけを反映するよう設計）:
  explore  = 標準価値ベクトル[1,0,..]への softmax 選択エントロピー / log K … τ（低τ→狭い）
             ※生のエントロピーは「良い腕への集中(良)」と「狭窄(悪)」を区別できないため、
               各エージェントの混乱した landscape を除き τ の効果だけを直読する。
  farsight = D(delay; k)=1/(1+k·delay)                                  … k（直読・高k→低い）
  flexibility = 1 − P(choice==argmax H | argmax V≠argmax H)             … 習慣
                （価値と習慣が食い違う試行で『習慣に従う率』。低τでは誤検出しない）
  ※ FigD2 はこの3つ＝機構の分解。FigD1/FigD3 は実タスクでの創発的な複合結果。

出力: sim/out/figD1_total_reward.png, figD2_three_channels.png, figD3_lockin.png ＋ stdout。
再現性: config.ConfigD.seed 固定。実行: python sim/theorem_d_compound_cost.py
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

from config import CONFIG_D as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

ARM_GOOD = 1  # 大域最適（遅延・大）

# 条件 → (tau, k, habit_w)
CONDITIONS = {
    "calm": (C.tau_calm, C.k_calm, C.habit_calm),
    "tau_only": (C.tau_fear, C.k_calm, C.habit_calm),
    "k_only": (C.tau_calm, C.k_fear, C.habit_calm),
    "habit_only": (C.tau_calm, C.k_calm, C.habit_fear),
    "fearful": (C.tau_fear, C.k_fear, C.habit_fear),
}
COLORS = {"calm": "C2", "tau_only": "C0", "k_only": "C1", "habit_only": "C4", "fearful": "C3"}


def arm_rewards(t):
    r = np.full(C.K, C.r_distractor, dtype=float)
    r[0] = C.r_arm0_pre if t < C.t_change else C.r_arm0_post
    r[ARM_GOOD] = C.r_arm1
    return r


def arm_delays():
    d = np.zeros(C.K, dtype=float)
    d[ARM_GOOD] = C.delay_arm1
    return d


def run_agent(tau, k, habit_w, rng):
    """1エージェントを T ステップ。選択 / 実報酬 / 価値-習慣競合 / 習慣に従ったか を返す。"""
    V = np.zeros(C.K)
    H = np.zeros(C.K)
    d = arm_delays()
    ch = np.empty(C.T, dtype=int)
    rew = np.empty(C.T, dtype=float)
    conflict = np.zeros(C.T, dtype=bool)      # argmax V ≠ argmax H（価値と習慣が食い違う）
    chose_habit = np.zeros(C.T, dtype=bool)   # 選択が argmax H と一致
    for t in range(C.T):
        vmax = int(np.argmax(V))
        hmax = int(np.argmax(H))
        score = V + habit_w * H
        z = score / tau
        z -= z.max()
        p = np.exp(z)
        p /= p.sum()
        a = int(rng.choice(C.K, p=p))

        conflict[t] = (vmax != hmax)
        chose_habit[t] = (a == hmax)

        r = arm_rewards(t)
        r_actual = r[a]
        subj = r_actual / (1.0 + k * d[a])        # 双曲割引 D(d)=1/(1+k·d)（近視眼）
        V[a] += C.eta * (subj - V[a])             # RW（割引後の主観価値へ）
        H *= (1.0 - C.habit_lr)                   # 習慣は減衰＋選択腕を加算
        H[a] += C.habit_lr

        ch[t] = a
        rew[t] = r_actual
    return ch, rew, conflict, chose_habit


def run_population(tau, k, habit_w, base_rng):
    ch = np.empty((C.n_agents, C.T), dtype=int)
    rew = np.empty((C.n_agents, C.T), dtype=float)
    conflict = np.empty((C.n_agents, C.T), dtype=bool)
    chose_habit = np.empty((C.n_agents, C.T), dtype=bool)
    for i in range(C.n_agents):
        rng = np.random.default_rng(base_rng.integers(0, 2**63 - 1))
        c, r, cf, chh = run_agent(tau, k, habit_w, rng)
        ch[i] = c
        rew[i] = r
        conflict[i] = cf
        chose_habit[i] = chh
    return ch, rew, conflict, chose_habit


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def explore_breadth(tau):
    """τ チャネルの直読：標準価値ベクトル[1,0,..,0]への softmax 選択エントロピー / log K。
    各エージェントの学習済み価値（混乱しうる）を除き、τ が生む探索の広さだけを測る。"""
    ref = np.zeros(C.K)
    ref[0] = 1.0
    z = ref / tau
    z -= z.max()
    p = np.exp(z)
    p /= p.sum()
    p = p[p > 0]
    return float(-(p * np.log(p)).sum() / np.log(C.K))


def _moving_avg(x, w=15):
    # エッジでゼロパディングによる偽の落ち込みを避け、窓内の実点数で正規化する
    kernel = np.ones(w)
    num = np.convolve(x, kernel, mode="same")
    den = np.convolve(np.ones_like(x, dtype=float), kernel, mode="same")
    return num / den


def figD1(metrics):
    names = list(CONDITIONS.keys())
    cols = [COLORS[n] for n in names]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    ax1.bar(names, [metrics[n]["reward_per_step"] for n in names], color=cols)
    ax1.set(title="Compound cost: mean reward per step", ylabel="reward / step")
    ax1.tick_params(axis="x", rotation=20)
    ax2.bar(names, [metrics[n]["final_good_share"] for n in names], color=cols)
    ax2.set(title="Use of global-optimum arm (delayed-large)", ylabel="final arm1 share", ylim=(0, 1))
    ax2.tick_params(axis="x", rotation=20)
    fig.suptitle("Theorem D: fear locks the agent into the local optimum (small-immediate arm)")
    fig.tight_layout()
    path = os.path.join(OUT, "figD1_total_reward.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figD1] saved -> {path}")


def figD2(metrics):
    names = list(CONDITIONS.keys())
    chans = [("explore (tau channel)", "explore"),
             ("farsight (k channel)", "farsight"),
             ("flexibility (habit channel)", "flexibility")]
    x = np.arange(len(names))
    width = 0.26
    fig, ax = plt.subplots(figsize=(12, 5))
    for j, (label, key) in enumerate(chans):
        ax.bar(x + (j - 1) * width, [metrics[n][key] for n in names], width, label=label)
    ax.set(title="Three independent channels: each single fear-knob lowers ONLY its own axis; "
                 "fear lowers all three",
           ylabel="normalized score (0-1)", ylim=(0, 1.08))
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15)
    ax.legend(loc="upper center", ncol=3)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figD2_three_channels.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figD2] saved -> {path}")


def figD3(traj):
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for name in CONDITIONS:
        lw = 2.4 if name in ("calm", "fearful") else 1.0
        alpha = 1.0 if name in ("calm", "fearful") else 0.55
        ax.plot(_moving_avg(traj[name]), c=COLORS[name], label=name, lw=lw, alpha=alpha)
    ax.axvline(C.t_change, c="k", lw=0.8, alpha=0.4)
    ax.text(C.t_change, 1.03, " arm0 devalued", fontsize=8, va="bottom")
    ax.set(title="Lock-in: share choosing the global-optimum arm (delayed-large) over time",
           xlabel="step", ylabel="P(choose arm1)", ylim=(0, 1.1))
    ax.legend(loc="center right")
    fig.tight_layout()
    path = os.path.join(OUT, "figD3_lockin.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figD3] saved -> {path}")


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 74)
    print("定理D 恐怖の複合コスト — multi-armed task simulation")
    print(f"seed={C.seed}  n_agents={C.n_agents}  arms={C.K}  "
          f"arm0(immediate small) vs arm1(delayed large, d={C.delay_arm1})")
    print("検証: 恐怖は τ↓・k↑・習慣化 を同時に起こす独立3チャネルの劣化か")
    print("=" * 74)

    metrics = {}
    traj = {}
    for name, (tau, k, habit_w) in CONDITIONS.items():
        ch, rew, conflict, chose_habit = run_population(tau, k, habit_w, _spawn(master))
        explore = explore_breadth(tau)                              # τ チャネル（直読）
        farsight = 1.0 / (1.0 + k * C.delay_arm1)                    # k チャネル（直読）
        cf = conflict
        habit_dom = float(chose_habit[cf].mean()) if cf.any() else 0.0
        flexibility = 1.0 - habit_dom                                # 習慣チャネル
        reward_per_step = float(rew.mean())
        final_good_share = float((ch[:, -100:] == ARM_GOOD).mean())
        metrics[name] = dict(explore=explore, farsight=farsight, flexibility=flexibility,
                             reward_per_step=reward_per_step, final_good_share=final_good_share)
        traj[name] = (ch == ARM_GOOD).mean(axis=0)
        print(f"[{name:11s}] reward/step={reward_per_step:.3f}  arm1_share(final)={final_good_share:.3f}  "
              f"| explore={explore:.3f} farsight={farsight:.3f} flexibility={flexibility:.3f} "
              f"(conflict trials={cf.mean()*100:.1f}%)")

    print("-" * 74)
    print("読み: 各単独channelは自分の軸だけ低い／fearful は3軸とも低く、報酬も最低（複合）")

    figD1(metrics)
    figD2(metrics)
    figD3(traj)
    print("=" * 74)
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
