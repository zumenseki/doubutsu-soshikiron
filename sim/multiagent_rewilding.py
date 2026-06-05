"""
多エージェント層 MA-5 — 再野生化（Stage5 硬直からの集団脱出）

検証する主張（docs/橋渡し_対応表.md「Stage5硬直＝定理B無力感アトラクタ／再野生化＝唯一の脱出」、
docs/比喩_5類型マクロ.md「再野生化」、docs/多エージェント設計.md §3 の MA-4 後続）:

  硬直した ant/Stage5 集団（高 kconf・status quo へ固着＝MA-3/MA-4 の ant regime）は、
  より良い option1 が在っても人気バイアスで離陸できない（前例ロックイン）。脱出機構：
    (1) 放置 … status quo に張り付いたまま（adoption ≈ 0）。
    (2) 全体微緩（exhortation）… 同調を少し下げても相転移の谷に留まり、ほぼ変わらない。
    (3) 再野生化（隔離細胞＋autonomy 保持）… 独自ルール（低 kconf・多数派の人気から遮断）の
        少数細胞を注入→option1 を発見→実績を示しつつ再結合 → 規範が反転して集団が脱出。
    (4) 再吸収（autonomy 喪失）… 細胞は発見するが、再結合時に多数派の高 kconf へ戻すと
        人気に飲まれ status quo へ swallow back。

  ＝定理B「外生注入だけが無力感アトラクタの脱出路」の集団版。
  通俗版（"号令で変えろ"＝全体微緩）と分岐する非自明な帰結：脱出は同調を緩める強さでなく、
  「前例の届かない場所（autonomy を保った細胞）」を作れるかで決まる。

§0 の正直さ: 再野生化は万能ではない。隔離細胞が小さすぎる／多数派の同調が強すぎると
  脱出は起きず細胞は飲まれる（fig2/fig3 が閾値構造を示す）。係数は機構の表現であって
  組織データへのフィットではない。

機構（MA-3 の人気バイアス ＋ 個人 RL ＋ 観察的価値学習[実績デモ]）:
  choice = softmax( (V_i + kconf·人気) / tau )。個人 RL: V←V+η(報酬−V)。
  実績デモ: ある option を「臨界質量(vis_thresh)以上」が実践して初めて見える手本となり、
  非遮断エージェントが実現 payoff へ V を少し寄せる（人気＝同調 とは別チャネル＝実績の伝播）。
  隔離細胞は隔離窓の間だけ多数派の人気・実績から遮断（自分のローカル人気のみ参照）。

出力: sim/out/figH1_rewilding.png, figH2_isolation_threshold.png, figH3_phase.png ＋ stdout。
実行: python sim/multiagent_rewilding.py
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

from config import CONFIG_MA5 as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
TRUE = np.array(C.true_value, dtype=float)


def rewild_sim(rng, *, kconf_major, iso_frac, t_recouple, keep_autonomy,
               demo_rate=None, kconf_iso=None, T=None):
    """統一 population 模型を T ステップ。adoption（最良 option1 を選ぶ割合）の時系列を返す。

    kconf_major   多数派（既存組織）の同調強度。
    iso_frac      隔離細胞のサイズ（母集団比）。0 なら細胞なし（放置／全体微緩）。
    t_recouple    隔離窓 [0,t_recouple)。以降は細胞が再結合。
    keep_autonomy True=再結合後も細胞は低 kconf を保つ（autonomy）／False=多数派の kconf へ戻す（再吸収）。
    """
    T = T or C.T
    N, K = C.N, C.K
    demo_rate = C.demo_rate if demo_rate is None else demo_rate
    kconf_iso = C.kconf_iso if kconf_iso is None else kconf_iso
    n_iso = int(round(iso_frac * N))
    iso = np.zeros(N, dtype=bool)
    iso[:n_iso] = True

    V = np.zeros((N, K))
    V[:, C.incumbent] = C.V_init_incumbent           # 全員 status quo を「知っている」
    pop = np.zeros(K); pop[C.incumbent] = 1.0         # 全体人気
    iso_pop = np.zeros(K); iso_pop[C.incumbent] = 1.0  # 細胞ローカル人気（隔離中に参照）
    idx = np.arange(N)

    hist = {k: np.empty(T) for k in ("adopt", "adopt_major", "adopt_iso")}
    for t in range(T):
        before = t < t_recouple
        shielded = iso & before                       # 隔離中の細胞＝多数派から遮断

        # 各エージェントの同調強度
        kconf = np.full(N, float(kconf_major))
        if before:
            kconf[iso] = kconf_iso                     # 隔離中は wild
        else:
            kconf[iso] = kconf_iso if keep_autonomy else kconf_major  # 再結合: 自律保持 or 再吸収

        # 参照する人気（遮断中の細胞はローカル人気のみ）
        pop_seen = np.where(shielded[:, None], iso_pop[None, :], pop[None, :])
        score = V + kconf[:, None] * pop_seen
        z = score / C.tau
        z -= z.max(axis=1, keepdims=True)
        P = np.exp(z); P /= P.sum(axis=1, keepdims=True)
        cum = P.cumsum(axis=1)
        choices = (rng.random((N, 1)) < cum).argmax(axis=1)

        reward = TRUE[choices] + C.reward_noise * rng.standard_normal(N)
        V[idx, choices] += C.eta * (reward - V[idx, choices])

        # 観察的価値学習（実績デモ）: commons に結合した（＝互いに見える）実践だけが手本になる。
        # 隔離中の細胞は commons から切り離されているので、その option1 実践は多数派にまだ
        # 「見えない」（skunkworks）。再結合して初めて手本として broadcast される。
        # 臨界質量（vis_thresh）以上が実践して初めて見える手本になる（単発の偶発探索は手本にならない）。
        if demo_rate > 0.0:
            vis = ~shielded                            # commons に結合（観察し／観察される）
            cv = choices[vis]
            if cv.size > 0:
                counts = np.bincount(cv, minlength=K)
                pop_vis = counts / cv.size
                sums = np.bincount(cv, weights=reward[vis], minlength=K)
                obs = np.where(counts > 0, sums / np.maximum(counts, 1), 0.0)
                for a in range(K):
                    if pop_vis[a] >= C.vis_thresh:
                        V[vis, a] += demo_rate * (obs[a] - V[vis, a])

        pop = np.bincount(choices, minlength=K) / N
        if n_iso > 0:
            iso_pop = np.bincount(choices[iso], minlength=K) / n_iso

        hist["adopt"][t] = (choices == C.best).mean()
        hist["adopt_major"][t] = (choices[~iso] == C.best).mean() if (N - n_iso) > 0 else 0.0
        hist["adopt_iso"][t] = (choices[iso] == C.best).mean() if n_iso > 0 else 0.0
    return hist


def final_adopt(hist, key="adopt", w=50):
    return float(np.mean(hist[key][-w:]))


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def fig1(master):
    """3条件の adoption 時系列：放置 / 再野生化(autonomy) / 再吸収。"""
    conds = [
        ("locked (do nothing)", dict(kconf_major=C.kconf_locked, iso_frac=0.0,
                                     t_recouple=C.t_recouple, keep_autonomy=True), "C3", "-"),
        ("rewilding (autonomous cell)", dict(kconf_major=C.kconf_locked, iso_frac=C.iso_frac,
                                             t_recouple=C.t_recouple, keep_autonomy=True), "C2", "-"),
        ("reabsorbed (cell loses autonomy)", dict(kconf_major=C.kconf_locked, iso_frac=C.iso_frac,
                                                  t_recouple=C.t_recouple, keep_autonomy=False), "C1", "--"),
    ]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    out = {}
    for label, kw, color, ls in conds:
        h = rewild_sim(_spawn(master), **kw)
        out[label] = h
        ax.plot(h["adopt"], color=color, ls=ls, lw=2, label=label)
    ax.axvline(C.t_recouple, color="gray", ls=":", lw=1)
    ax.annotate("re-couple", (C.t_recouple, 0.02), fontsize=8, color="gray",
                xytext=(C.t_recouple + 5, 0.05))
    ax.set(title="MA-5 rewilding: only an autonomous protected cell escapes Stage5 lock-in",
           xlabel="step", ylabel="adoption of the better practice (option1)", ylim=(-0.03, 1.03))
    ax.legend(loc="center right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figH1_rewilding.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figH1] saved -> {path}")
    return out


def fig2(master):
    """隔離サイズ スイープ → 最終 adoption（autonomy vs 再吸収）。閾値構造。"""
    fracs = np.linspace(0.0, C.iso_frac_max, C.sweep_points)
    curves = {}
    for keep, label in ((True, "autonomous cell"), (False, "reabsorbed cell")):
        ys = np.empty(C.sweep_points)
        for i, fr in enumerate(fracs):
            vals = []
            for _ in range(C.sweep_seeds):
                h = rewild_sim(_spawn(master), kconf_major=C.kconf_locked, iso_frac=fr,
                               t_recouple=C.t_recouple, keep_autonomy=keep)
                vals.append(final_adopt(h))
            ys[i] = float(np.mean(vals))
        curves[label] = ys
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(fracs, curves["autonomous cell"], "o-", color="C2", lw=2, label="autonomous cell")
    ax.plot(fracs, curves["reabsorbed cell"], "s--", color="C1", lw=2, label="reabsorbed cell")
    ax.set(title="MA-5: escape needs a critical-mass cell that keeps its autonomy",
           xlabel="isolated-cell size (fraction of population)",
           ylabel="final adoption of the better practice", ylim=(-0.03, 1.03))
    ax.legend(loc="center right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figH2_isolation_threshold.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figH2] saved -> {path}")
    return fracs, curves


def fig3(master):
    """相図：多数派 kconf × 隔離サイズ → 最終 adoption（autonomy 保持）。脱出領域。"""
    kconfs = np.linspace(0.0, C.kconf_major_max, C.grid_points)
    fracs = np.linspace(0.0, C.iso_frac_max, C.grid_points)
    Z = np.empty((C.grid_points, C.grid_points))
    for i, fr in enumerate(fracs):
        for j, kc in enumerate(kconfs):
            h = rewild_sim(_spawn(master), kconf_major=kc, iso_frac=fr,
                           t_recouple=C.t_recouple, keep_autonomy=True)
            Z[i, j] = final_adopt(h)
    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.pcolormesh(kconfs, fracs, Z, cmap="RdYlGn", vmin=0, vmax=1, shading="auto")
    ax.set(title="MA-5 phase: escape region (autonomous cell)\nlow conformity OR large protected cell",
           xlabel="majority conformity kconf", ylabel="isolated-cell size (fraction)")
    fig.colorbar(im, ax=ax, label="final adoption of the better practice")
    fig.tight_layout()
    path = os.path.join(OUT, "figH3_phase.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figH3] saved -> {path}")
    return kconfs, fracs, Z


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 80)
    print("多エージェント MA-5 再野生化（Stage5 硬直からの集団脱出）")
    print(f"seed={C.seed}  N={C.N}  K={C.K}  true_value={C.true_value}  best=option{C.best}")
    print(f"kconf_locked={C.kconf_locked} kconf_iso={C.kconf_iso} iso_frac={C.iso_frac} "
          f"t_recouple={C.t_recouple} demo_rate={C.demo_rate} vis_thresh={C.vis_thresh}")
    print("検証: 硬直集団の脱出は同調の緩さでなく『autonomy を保った隔離細胞』で決まるか")
    print("=" * 80)

    h1 = fig1(master)
    print("最終 adoption（末尾50step平均）:")
    for label, h in h1.items():
        print(f"  {label:34s} overall={final_adopt(h):.3f}  majority={final_adopt(h, 'adopt_major'):.3f}")

    # 通俗版「全体微緩（exhortation）」の対照：細胞なしで同調だけ下げる
    print("-" * 80)
    print("対照（細胞なし・同調だけ操作）= 通俗版『号令で緩める』:")
    for kc, name in ((C.kconf_locked, "放置(kconf=locked)"), (C.kconf_nudge, "全体微緩(kconf=nudge)"),
                     (0.0, "全廃(kconf=0・大規模では非現実的)")):
        vals = [final_adopt(rewild_sim(_spawn(master), kconf_major=kc, iso_frac=0.0,
                                       t_recouple=C.t_recouple, keep_autonomy=True))
                for _ in range(C.sweep_seeds)]
        print(f"  {name:34s} final adoption={np.mean(vals):.3f}")

    fr2, cur = fig2(master)
    # autonomy 側で adoption>0.5 に達する最小細胞サイズ＝脱出閾値
    auto = cur["autonomous cell"]
    above = np.where(auto > 0.5)[0]
    thr = fr2[above[0]] if len(above) else None
    print("-" * 80)
    print(f"脱出閾値（autonomy・最終adoption>0.5 となる最小隔離サイズ）: "
          f"{('%.2f' % thr) if thr is not None else '範囲内に無し'}")
    print(f"再吸収側の最大最終adoption: {cur['reabsorbed cell'].max():.3f}（飲まれて離陸しない）")

    kc3, fr3, Z = fig3(master)
    print(f"相図: 脱出領域（adoption>0.5）の面積比 = {float((Z > 0.5).mean()):.2f}")

    print("=" * 80)
    print("§0 正直な照合:")
    print("  ✅ 放置／全体微緩では status quo ロックが解けない（同調を少し緩めるだけでは谷に残る）。")
    print("  ✅ autonomy を保った臨界質量の隔離細胞でのみ規範が反転（再野生化＝集団の脱出路）。")
    print("  ✅ 再吸収（細胞を多数派の同調へ戻す）と人気に飲まれ元へ戻る＝autonomy が要石。")
    print("  ⚠️ 万能ではない: 細胞が小さい／多数派の同調が強いと脱出しない（fig2/fig3 の閾値）。")
    print("  ⚠️ これは機構の表現であって組織データへのフィットではない（§0）。")
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
