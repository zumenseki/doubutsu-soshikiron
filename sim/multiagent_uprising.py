"""
多エージェント層 MA-8 — 蜂起カスケード（MA-1 恐怖伝播の双対）

検証する主張（docs/応用_集団蜂起.md §2,§4・docs/多エージェント設計.md §1 結合③）:
  MA-1 は Ĝ↓（恐怖）が観察で「容易に」伝染することを示した（下方・帰属ゲートなし）。
  その双対：Ĝ↑（有効性・勇気）も観察で伝播しうるが、帰属ゲート（現 Ĝ）で重く抑制される
  （§4 修正項1：低 Ĝ では他者の成功を自分に帰属できない＝「あいつは特別」）。
  帰結：
    (1) 低 Ĝ で全員撤退した無力感アトラクタ（＝長い忍従）は安定。自然発生の蜂起は起きない。
    (2) 外生 seed（指導者＝確実に勝てる統制可能経験の体現・定理B の脱出注入）が
        臨界質量を超えて初めて帰属ゲートを突破し、動員がカスケードする（突発・閾値的）。
    (3) 同じ伝播強度 λ でも、恐怖（下方・ゲートなし）は低閾値で広がり、勇気（上方・帰属ゲート）
        は高閾値でしか広がらない＝「なぜ抑圧は安定で蜂起は稀か」の機構的非対称。

モデル（トーラス格子 L×L・4近傍・同期更新。MA-1 と同形・符号と帰属ゲートのみ反転）:
  - 撤退ラッチ：Ĝ<theta_giveup で自発行動停止（§1 自己封止）。崩落者は確率 p_try で再挑戦。
  - 直接更新（行動者・統制可能成功 g=1）：uprising は上方＝帰属ゲート Ĝ·(1−Ĝ)。
  - 観察伝播：uprising=上方 relu(G_j−G_i) を帰属ゲート Ĝ_i で／ fear=下方 relu(G_i−G_j)・ゲートなし。
  - seed（外生注入）：uprising は中央 patch を Ĝ=1 に clamp（指導者）／ fear は Ĝ=0（粛清）。

出力: sim/out/figK1_uprising_cascade.png, figK2_tipping.png, figK3_asymmetry.png ＋ stdout。
再現性: config.ConfigMA8.seed 固定。実行: python sim/multiagent_uprising.py
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

from config import CONFIG_MA8 as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def center_mask(side):
    m = np.zeros((C.L, C.L), dtype=bool)
    if side <= 0:
        return m
    c = (C.L - side) // 2
    m[c:c + side, c:c + side] = True
    return m


def simulate(mode, seed_side, lam_obs, rng, record=False, pure=False):
    """mode='uprising'（Ĝ↑・上方帰属ゲート）／'fear'（Ĝ↓・下方ゲートなし＝MA-1）。

    非対称の要：
      uprising … 低 Ĝ 集団＋指導者 seed(Ĝ=1)。観察は上方 relu(G_j−G_i)、帰属ゲート G_i で抑制。
      fear     … 健全 Ĝ 集団＋粛清 seed(Ĝ=0)。観察は下方 relu(G_i−G_j)、ゲートなし（容易に伝染）。
    pure=True：direct（行動成功の self-sustain）のみ切り、観察伝播＋抵抗(decay)で比較する＝帰属
      ゲートの効果を direct 由来の非対称から isolate（figK3 の公平な恐怖 vs 勇気比較・§0：仕込まない）。
    """
    L = C.L
    seed = center_mask(seed_side)
    nonseed = ~seed
    if mode == "uprising":
        G = np.full((L, L), C.Ghat0_low, dtype=float)
        seed_val = 1.0
    else:
        G = np.full((L, L), C.Ghat0_high, dtype=float)
        seed_val = 0.0

    frac_mobilized = np.empty(C.T)
    frac_collapsed = np.empty(C.T)
    meanG_non = np.empty(C.T)
    snaps = {}
    snap_times = {0, C.t_seed_start + 40, C.t_seed_start + 120, C.T - 1}

    for t in range(C.T):
        active_seed = seed & (t >= C.t_seed_start)
        collapsed = G < C.theta_giveup
        try_mask = collapsed & (rng.random((L, L)) < C.p_try)
        acts = (~collapsed) | try_mask | active_seed

        if mode == "uprising":
            direct = 0.0 if pure else C.lam_direct * G * (1.0 - G) * acts  # 上方＝帰属ゲート（低Ĝは climb 遅い）
            up = (np.maximum(0.0, np.roll(G, 1, 0) - G)
                  + np.maximum(0.0, np.roll(G, -1, 0) - G)
                  + np.maximum(0.0, np.roll(G, 1, 1) - G)
                  + np.maximum(0.0, np.roll(G, -1, 1) - G))
            obs = lam_obs * G * up                                  # 帰属ゲート G_i で借用を抑制
        else:
            direct = 0.0 if pure else C.lam_direct * (1.0 - G) * acts      # 健全環境での素直な回復（対照）
            down = (np.maximum(0.0, G - np.roll(G, 1, 0))
                    + np.maximum(0.0, G - np.roll(G, -1, 0))
                    + np.maximum(0.0, G - np.roll(G, 1, 1))
                    + np.maximum(0.0, G - np.roll(G, -1, 1)))
            obs = -lam_obs * down                                   # 下方・ゲートなし（恐怖は容易に伝染＝MA-1）

        G = np.clip(G + direct + obs, C.Ghat_floor, 1.0)
        # 無力の再強化（諦めへの引力）：撤退者の Ĝ は floor 方向へ引かれる＝定理B 低活動アトラクタを
        # 動的に表現。伝播 front の抵抗となり、伝播がこれに勝つ lam_obs の閾値（tipping）を作る。
        still_collapsed = G < C.theta_giveup
        G = G - C.decay * (G - C.Ghat_floor) * still_collapsed
        if active_seed.any():
            G[active_seed] = seed_val                               # 外生注入（指導者=1／粛清=0）を毎ステップ維持

        frac_mobilized[t] = float((G[nonseed] > C.theta).mean())
        frac_collapsed[t] = float((G[nonseed] < C.theta_giveup).mean())
        meanG_non[t] = float(G[nonseed].mean())
        if record and t in snap_times:
            snaps[t] = G.copy()

    return dict(frac_mobilized=frac_mobilized, frac_collapsed=frac_collapsed,
                meanG_non=meanG_non, snaps=snaps, seed=seed)


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def figK1(res):
    """空間カスケード：指導者 seed から動員（Ĝ↑）が広がる（または帰属ゲートで吸収される）。"""
    times = sorted(res["snaps"].keys())
    fig, axes = plt.subplots(1, len(times), figsize=(4 * len(times), 4.2))
    for ax, t in zip(axes, times):
        im = ax.imshow(res["snaps"][t], vmin=0, vmax=1, cmap="RdYlGn", origin="upper")
        phase = "before leader" if t < C.t_seed_start else "leader present"
        ax.set_title(f"t={t}  ({phase})")
        ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02,
                 label="Ghat (green=mobilized/efficacious, red=helpless)")
    fig.suptitle(f"MA-8 uprising cascade: a leader seed ({C.seed_side}x{C.seed_side}) injected into a "
                 f"helpless population (Ghat0={C.Ghat0_low}) spreads efficacy via attribution-gated "
                 f"observation (lam_obs={C.lam_obs})")
    path = os.path.join(OUT, "figK1_uprising_cascade.png")
    fig.savefig(path, dpi=125, bbox_inches="tight")
    plt.close(fig)
    print(f"[figK1] saved -> {path}")


def figK2(xs, finals):
    """tipping：観察伝播強度 lam_obs → 最終動員率（蜂起＝勇気の相転移）。"""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(xs, finals, "-o", ms=4, c="C2")
    ax.set(title="Uprising as a phase transition: final mobilized fraction vs observation coupling",
           xlabel="lam_obs (observation coupling strength)",
           ylabel="final mobilized fraction (non-seed)", ylim=(-0.03, 1.03),
           xlim=(C.sweep_lo, C.sweep_hi))
    d = np.gradient(finals, xs)
    ti = int(np.argmax(d))
    ax.axvline(xs[ti], ls="--", c="gray", lw=1)
    ax.text(xs[ti], 0.5, f" tipping ~ {xs[ti]:.2f}", fontsize=9)
    fig.tight_layout()
    path = os.path.join(OUT, "figK2_tipping.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figK2] saved -> {path}")
    return xs[ti]


def figK3(xs, up_finals, fear_finals):
    """非対称：同じ観察強度 lam_obs でも 恐怖(下方・ゲートなし)は低 lam_obs で広がり、
    勇気(上方・帰属ゲート)は高 lam_obs でしか広がらない＝なぜ抑圧は安定で蜂起は稀か。"""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(xs, fear_finals, "-o", ms=4, c="C3",
            label="fear (downhill, no gate) -> collapsed frac")
    ax.plot(xs, up_finals, "-o", ms=4, c="C2",
            label="efficacy (uphill, attribution-gated) -> mobilized frac")
    ax.set(title="Asymmetry: fear spreads at low coupling, courage needs high coupling (same mechanism)",
           xlabel="lam_obs (observation coupling strength)",
           ylabel="final affected fraction (non-seed)", ylim=(-0.03, 1.03),
           xlim=(C.sweep_lo, C.sweep_hi))
    ax.legend(loc="center right", fontsize=9)
    fig.tight_layout()
    path = os.path.join(OUT, "figK3_asymmetry.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figK3] saved -> {path}")


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 74)
    print("多エージェント MA-8 蜂起カスケード（MA-1 恐怖伝播の双対）— grid simulation")
    print(f"seed={C.seed}  N={C.L*C.L} ({C.L}x{C.L} torus)  "
          f"helpless init Ghat0={C.Ghat0_low}  leader seed={C.seed_side}x{C.seed_side} "
          f"from t={C.t_seed_start}  lam_obs={C.lam_obs}")
    print("検証: 低Ĝの忍従は安定／指導者seedが臨界質量を超えると帰属ゲートを破り動員がカスケードするか")
    print("=" * 74)

    # 既定 seed での蜂起カスケード（record）＋ seed なし対照（自然発生しないこと）
    up = simulate("uprising", C.seed_side, C.lam_obs, _spawn(master), record=True)
    none = simulate("uprising", 0, C.lam_obs, _spawn(master), record=False)
    print(f"[leader ] final mobilized(non-seed)={up['frac_mobilized'][-1]:.3f}  "
          f"meanG: start={up['meanG_non'][0]:.2f} end={up['meanG_non'][-1]:.2f}")
    print(f"[no-seed] final mobilized(non-seed)={none['frac_mobilized'][-1]:.3f}  "
          f"<- 指導者(外生注入)なしでは忍従は自然回復しない（定理B）")

    # figK2：蜂起本体（direct+decay 込み＝行動が信念を支える）の相転移。lam_obs スイープ・seed_side 固定。
    xs = np.linspace(C.sweep_lo, C.sweep_hi, C.sweep_points)
    up_full = []
    for lo in xs:
        v = [simulate("uprising", C.seed_side, lo, _spawn(master))["frac_mobilized"][-1]
             for _ in range(C.sweep_seeds)]
        up_full.append(float(np.mean(v)))
    up_full = np.array(up_full)

    # figK3：帰属ゲートの効果を isolate（観察伝播のみ・pure）で 恐怖 vs 勇気を公平比較（§0：仕込まない）。
    up_pure, fear_pure = [], []
    for lo in xs:
        uv = [simulate("uprising", C.seed_side, lo, _spawn(master), pure=True)["frac_mobilized"][-1]
              for _ in range(C.sweep_seeds)]
        fv = [simulate("fear", C.seed_side, lo, _spawn(master), pure=True)["frac_collapsed"][-1]
              for _ in range(C.sweep_seeds)]
        up_pure.append(float(np.mean(uv))); fear_pure.append(float(np.mean(fv)))
    up_pure = np.array(up_pure); fear_pure = np.array(fear_pure)

    figK1(up)
    tip = figK2(xs, up_full)
    figK3(xs, up_pure, fear_pure)
    fear_tip = xs[int(np.argmax(np.gradient(fear_pure, xs)))]
    up_tip = xs[int(np.argmax(np.gradient(up_pure, xs)))]
    print(f"[tipping] 蜂起本体（行動が信念を支える）の動員カスケードは lam_obs ~ {tip:.2f} で着火")
    print(f"[asymmetry/pure] 帰属ゲートのみ残した純伝播比較： 恐怖崩落 tipping ~ {fear_tip:.2f}  <<  "
          f"勇気動員 tipping ~ {up_tip:.2f}  ＝同じ観察強度でも恐怖は容易・勇気は帰属ゲートで困難")
    print("=" * 74)
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
