"""
多エージェント層 MA-1 — 恐怖伝播（粛清カスケード）

検証する主張（docs/多エージェント設計.md §4, docs/正本_ミクロ機構.md §6 定理D の「伝播」）:
  局所的な粛清（一部への統制不能な罰）が、直接罰を受けていないエージェントにも
  リスク回避（Ĝ↓・撤退）を伝播させ、母集団規模の文化的萎縮を生む。
  しかも tipping（閾値）を持つ＝伝染強度が回復を上回ると集団全体が相転移的に崩落。
  単一エージェントでは出ない、多エージェント層に固有の創発現象。

モデル（トーラス格子 L×L・4近傍・同期更新）:
  - collapsed_i = Ĝ_i < θ_giveup。崩落者は helpless 信号 s=0 を発する（§1 自己封止）。
  - 非崩落者：粛清窓内のシードなら統制不能罰 g=0、それ以外は統制可能で成功 g=1 → s=g。
  - 直接更新（非崩落のみ）：Ĝ ← update(Ĝ, g_direct, λ_direct)。
  - 伝染更新（全員・撤退者も観察する）：近傍信号平均 s̄ へ Ĝ ← update(Ĝ, s̄, λ_obs)。
  - update：上方は帰属ゲート Ĝ←Ĝ+λ·Ĝ·(g−Ĝ)、下方は素直に Ĝ←Ĝ+λ·(g−Ĝ)（定理B/Dと同形）。

出力: sim/out/figMA1_cascade.png, figMA2_tipping.png, figMA3_vicarious.png ＋ stdout。
再現性: config.ConfigMA.seed 固定。実行: python sim/multiagent_fear_contagion.py
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

from config import CONFIG_MA as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def seed_mask():
    m = np.zeros((C.L, C.L), dtype=bool)
    c = (C.L - C.purge_side) // 2
    m[c:c + C.purge_side, c:c + C.purge_side] = True   # 中央の patch を粛清シードに（放射状に広がる）
    return m


def simulate(lam_obs, lam_direct, rng, record=False):
    """格子を T ステップ。崩落率の時系列・シード/非シード平均Ĝ・スナップショットを返す。

    非対称な結合（忠実性の要）:
      Ĝ↓ = 自分の罰（直接）／ 恐怖の隣人を観察（vicarious・下方のみ）
      Ĝ↑ = 自分の統制成功のみ（直接）。他者の成功は借りられない（§1 自己封止）。
      崩落者も確率 p_try で再挑戦し、統制可能なら回復する（tipping の対抗力）。
    """
    L = C.L
    seed = seed_mask()
    G = np.full((L, L), C.Ghat0, dtype=float)
    frac_collapsed = np.empty(C.T)
    meanG_seed = np.empty(C.T)
    meanG_non = np.empty(C.T)
    snaps = {}
    snap_times = {0, C.t_purge_end - 1, C.t_purge_end + 50, C.T - 1}
    for t in range(C.T):
        collapsed = G < C.theta_giveup
        purge_active = seed & (C.t_purge_start <= t < C.t_purge_end)

        # 行動する者：非崩落は常に、崩落者は確率 p_try で再挑戦
        try_mask = collapsed & (rng.random((L, L)) < C.p_try)
        acts = (~collapsed) | try_mask

        # 直接経験（行動者のみ・両方向）：統制可能なら成功 g=1（回復）、粛清中シードは g=0（下落）
        g_direct = np.where(purge_active, 0.0, 1.0)
        direct = lam_direct * (g_direct - G) * acts

        # 恐怖の伝染（全員・下方のみ・graded downhill）：自分より怖がっている隣人へ引きずられる。
        # relu(G_i − G_j) の近傍和。深く崩れた隣人が1体でも強く感染する（percolating front）。
        # calmer な隣人からは引き上げられない＝恐怖は一方向（§1 自己封止：自信は自分の成功でしか得ない）。
        down = (np.maximum(0.0, G - np.roll(G, 1, 0))
                + np.maximum(0.0, G - np.roll(G, -1, 0))
                + np.maximum(0.0, G - np.roll(G, 1, 1))
                + np.maximum(0.0, G - np.roll(G, -1, 1)))
        vicarious = -lam_obs * down

        G = np.clip(G + direct + vicarious, C.Ghat_floor, 1.0)

        frac_collapsed[t] = float((G < C.theta_giveup).mean())
        meanG_seed[t] = float(G[seed].mean())
        meanG_non[t] = float(G[~seed].mean())
        if record and t in snap_times:
            snaps[t] = G.copy()
    return dict(frac_collapsed=frac_collapsed, meanG_seed=meanG_seed,
                meanG_non=meanG_non, snaps=snaps, seed=seed)


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def figMA1(res):
    """空間カスケード：Ĝ 格子のスナップショット（粛清が伝染で広がる）。"""
    times = sorted(res["snaps"].keys())
    fig, axes = plt.subplots(1, len(times), figsize=(4 * len(times), 4.2))
    for ax, t in zip(axes, times):
        im = ax.imshow(res["snaps"][t], vmin=0, vmax=1, cmap="RdYlGn", origin="upper")
        if t < C.t_purge_start:
            phase = "before purge"
        elif t < C.t_purge_end:
            phase = "purge on"
        else:
            phase = "after purge"
        ax.set_title(f"t={t}  ({phase})")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02, label="Ghat (green=healthy, red=collapsed)")
    fig.suptitle(f"MA-1 spatial cascade: a local purge ({C.purge_side}x{C.purge_side} center patch) "
                 f"spreads fear across the population (lam_obs={C.lam_obs})")
    path = os.path.join(OUT, "figMA1_cascade.png")
    fig.savefig(path, dpi=125, bbox_inches="tight")
    plt.close(fig)
    print(f"[figMA1] saved -> {path}")


def figMA2(xs, finals):
    """tipping：伝染強度 λ_obs → 最終崩落率（文化的相転移の閾値）。"""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(xs, finals, "-o", ms=4, c="C3")
    ax.set(title="Cultural phase transition: final collapsed fraction vs contagion strength",
           xlabel="lam_obs (contagion strength)", ylabel="final collapsed fraction",
           ylim=(-0.03, 1.03), xlim=(C.sweep_lo, C.sweep_hi))
    # tipping point（最大勾配）
    d = np.gradient(finals, xs)
    ti = int(np.argmax(d))
    ax.axvline(xs[ti], ls="--", c="gray", lw=1)
    ax.text(xs[ti], 0.5, f" tipping ~ {xs[ti]:.2f}", fontsize=9)
    fig.tight_layout()
    path = os.path.join(OUT, "figMA2_tipping.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figMA2] saved -> {path}")
    return xs[ti]


def figMA3(on, off):
    """直接経験なしの伝播：粛清シード vs 非シードの平均Ĝ、伝染 ON/OFF。"""
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(on["meanG_seed"], c="C3", lw=2, label="purged seed (contagion ON)")
    ax.plot(on["meanG_non"], c="C1", lw=2, label="never-purged (contagion ON)")
    ax.plot(off["meanG_seed"], c="C3", lw=1.3, ls="--", label="purged seed (contagion OFF)")
    ax.plot(off["meanG_non"], c="C0", lw=1.3, ls="--", label="never-purged (contagion OFF)")
    ax.axhline(C.theta_giveup, c="gray", lw=1, ls=":", label="collapse threshold")
    ax.axvspan(C.t_purge_start, C.t_purge_end, color="red", alpha=0.07)
    ax.text(C.t_purge_start, 1.0, " purge window", fontsize=8, va="top")
    ax.set(title="Helplessness spreads WITHOUT direct experience (only when contagion is ON)",
           xlabel="step", ylabel="mean Ghat", ylim=(0, 1.05))
    ax.legend(loc="center right", fontsize=8)
    fig.tight_layout()
    path = os.path.join(OUT, "figMA3_vicarious.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figMA3] saved -> {path}")


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 74)
    print("多エージェント MA-1 恐怖伝播（粛清カスケード）— grid simulation")
    print(f"seed={C.seed}  N={C.L*C.L} ({C.L}x{C.L} torus)  purge={C.purge_side}x{C.purge_side} "
          f"corner, window=[{C.t_purge_start},{C.t_purge_end})  lam_obs={C.lam_obs}")
    print("検証: 局所粛清が直接経験なしに伝播し、tipping を超えると母集団が相転移的に崩落するか")
    print("=" * 74)

    # 既定（カスケード regime）でのカスケード＋vicarious
    on = simulate(C.lam_obs, C.lam_direct, _spawn(master), record=True)
    off = simulate(0.0, C.lam_direct, _spawn(master), record=False)
    print(f"[ON ] final collapsed={on['frac_collapsed'][-1]:.3f}  "
          f"non-seed meanG: start={on['meanG_non'][0]:.2f} end={on['meanG_non'][-1]:.2f}")
    print(f"[OFF] final collapsed={off['frac_collapsed'][-1]:.3f}  "
          f"non-seed meanG: start={off['meanG_non'][0]:.2f} end={off['meanG_non'][-1]:.2f}  "
          f"<- 伝染なしなら非シードは崩れない")

    # tipping スイープ
    xs = np.linspace(C.sweep_lo, C.sweep_hi, C.sweep_points)
    finals = np.empty(C.sweep_points)
    for i, lo in enumerate(xs):
        vals = []
        for _ in range(C.sweep_seeds):
            r = simulate(lo, C.lam_direct, _spawn(master), record=False)
            vals.append(r["frac_collapsed"][-1])
        finals[i] = float(np.mean(vals))

    figMA1(on)
    tip = figMA2(xs, finals)
    figMA3(on, off)
    print(f"[tipping] 最終崩落率の急変は lam_obs ~ {tip:.2f} 付近 "
          f"(low端={finals[0]:.2f}, high端={finals[-1]:.2f})")
    print("=" * 74)
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
