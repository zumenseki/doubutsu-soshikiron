"""
多エージェント層 MA-4 — 5類型の創発的導出（橋の完成）

検証する主張（docs/多エージェント設計.md §3 MA-4, docs/橋渡し_対応表.md）:
  3結合チャネル（恐怖伝播・社会的参照点・同調）を統合した1つの population 模型で、
  経営者の (C,A) 設計＝ノブを変えると、5動物類型が「安定した集団 regime」として創発し、
  比喩 §2 の4軸署名と一致するか。一致する範囲で、5類型は「対応表 → 導出」へ格上げされる。

統一模型のノブ（(C,A) 設計空間。各 type は PRESETS の点）:
  fear        恐怖の使用（統制不能罰率＋伝染） … τ↓・Ĝ↓・無力感の伝播
  f           外発報酬の統制性（0=情報的, 1=有形/統制的） … 内在価値 I₀ を抑制（定理C）
  kconf       同調（人気バイアス） … 規範固着・前例主義（MA-3）
  ineq        不平等（厚遇と相対的剥奪） … κ倍の損失（MA-2）
  omega       自己重み。(1−ω)＝社会比較（地位・政治）
  c           随伴性（報酬が成果に結びつく度合い） … 低いと学習信号が消える（系1）

各エージェント: morale/controllability M∈[floor,1]、option 価値 V[K]。
  M↑ = 統制可能な成功（帰属ゲートで gated）／ M↓ = 統制不能罰・相対的剥奪(κ)・恐怖伝染。
  M<θ で撤退（離脱・無力）。choice = softmax(V + kconf·人気)/τ_eff（fear が τ を狭める）。

§0 の正直さ: 5つ全部が綺麗に出るとは限らない。各 type の予測署名と実測を並べ、
  一致/部分一致/欠落を明示する（誇張しない）。

出力: sim/out/figG1_fingerprints.png, figG2_phase_diagram.png, figG3_trait_space.png ＋ stdout。
実行: python sim/multiagent_archetypes.py
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

from config import CONFIG_MA4 as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
TRUE = np.array(C.true_value, dtype=float)

# (C,A) ノブのプリセット（比喩 §2 の4軸傾向を写像）
PRESETS = {
    "wolf":   dict(fear=0.05, f=0.10, kconf=0.2, ineq=0.10, omega=0.70, c=0.90),
    "ant":    dict(fear=0.20, f=0.50, kconf=3.0, ineq=0.10, omega=0.70, c=0.70),
    "chimp":  dict(fear=0.12, f=0.50, kconf=1.0, ineq=0.55, omega=0.25, c=0.60),
    "bonobo": dict(fear=0.02, f=0.10, kconf=0.5, ineq=0.05, omega=0.60, c=0.10),
    "hyena":  dict(fear=0.50, f=0.90, kconf=0.2, ineq=0.60, omega=0.30, c=0.90),
}
JP = {"wolf": "オオカミ", "ant": "アリ", "chimp": "チンパン", "bonobo": "ボノボ", "hyena": "ハイエナ"}
# 比喩からの予測署名（定性。H/M/L）：morale, innovation, helpless, consensus, performance
PRED = {
    "wolf":   "morale=H innov=H helpless=L consensus=L perf=H",
    "ant":    "morale=M innov=L helpless=M consensus=H perf=M",
    "chimp":  "morale=L(分断) innov=L helpless=M consensus=M perf=M (政治)",
    "bonobo": "morale=H helpless=L innov=L/M consensus=M perf=M (安全だが緩い)",
    "hyena":  "morale=L helpless=H innov=L consensus=L perf=短期H→burnout",
}


def unified_sim(knobs, rng, T=None):
    """統一 population 模型を T ステップ。各指標の時系列を返す。"""
    T = T or C.T
    N, K = C.N, C.K
    fear = knobs["fear"]; f = knobs["f"]; kconf = knobs["kconf"]
    ineq = knobs["ineq"]; omega = knobs["omega"]; c = knobs["c"]

    favored = np.zeros(N, dtype=bool)
    favored[: int(C.frac_fav * N)] = True
    M = np.full(N, C.M0)
    V = np.zeros((N, K)); V[:, C.incumbent] = 1.0       # status quo を知っている
    rho = np.zeros(N)                                    # 参照点（nominal reward 単位）
    pop = np.zeros(K); pop[C.incumbent] = 1.0
    idx = np.arange(N)
    tau_eff = max(C.tau_min, C.tau_base * (1.0 - C.fear_tau * fear))

    hist = {k: np.empty(T) for k in ("morale", "helpless", "perf", "innov", "consensus", "disfav", "fav")}
    for t in range(T):
        collapsed = M < C.theta
        # 選択（撤退者は p_try で再挑戦）
        score = V + kconf * pop[None, :]
        z = score / tau_eff
        z -= z.max(axis=1, keepdims=True)
        P = np.exp(z); P /= P.sum(axis=1, keepdims=True)
        cum = P.cumsum(axis=1); u_draw = rng.random((N, 1))
        choices = (u_draw < cum).argmax(axis=1)
        acts = (~collapsed) | (collapsed & (rng.random(N) < C.p_try))

        uncontrollable = rng.random(N) < fear            # 恐怖＝統制不能アバース事象
        opt_q = TRUE[choices]
        ext = C.R_ext * (c * opt_q + (1.0 - c) * 1.0)      # 随伴性 c：低いと成果に依存しない
        ext = ext + favored * (ineq * C.ineq_boost)         # 厚遇の上乗せ（可視の地位/報酬）

        # 社会比較は可視の報酬/地位(ext)で起きる（恐怖の罰イベントとは独立に）
        peer_ext = (ext.sum() - ext) / (N - 1)
        rho = rho + C.rho_rate * ((omega * ext + (1.0 - omega) * peer_ext) - rho)
        u_social = ext - rho                                # >0:厚遇感 / <0:相対的剥奪

        dM = np.zeros(N)
        succ = acts & (~uncontrollable)                     # 統制可能な成功＝有能感で上方（帰属ゲート）
        dM[succ] += C.eta_M * M[succ] * (1.0 - M[succ])
        dM[uncontrollable] -= C.eta_M * (M[uncontrollable] - C.floor)   # 統制不能罰＝無力感の下方
        dep = u_social < 0.0                                # 相対的剥奪＝κ倍の下方（恐怖と独立）
        dM[dep] -= C.eta_M * np.minimum(C.kappa * np.abs(u_social[dep]), 1.0) * (M[dep] - C.floor)
        collapse_frac = collapsed.mean()
        dM -= C.lam_contagion * fear * collapse_frac * (M - C.floor)    # 恐怖伝染（mean-field・抑制済）
        M = np.clip(M + dM, C.floor, 1.0)

        # V が学べる信号は随伴性 c でスケールされる：低 c ＝ 成果が報酬に結びつかず学習信号が消える（系1）
        learn_signal = np.where(uncontrollable, 0.0, c * opt_q + (1.0 - c) * float(TRUE.mean()))
        V[idx, choices] += C.eta_V * (learn_signal - V[idx, choices])
        pop = np.bincount(choices, minlength=K) / N

        engaged = (M >= C.theta) & (~uncontrollable)
        output = engaged * opt_q
        hist["morale"][t] = M.mean()
        hist["helpless"][t] = (M < C.theta).mean()
        hist["perf"][t] = output.mean()
        hist["innov"][t] = pop[C.best]
        hist["consensus"][t] = pop.max()
        hist["disfav"][t] = M[~favored].mean()
        hist["fav"][t] = M[favored].mean()
    return hist


def fingerprint(hist, w=50):
    """末尾 w ステップの平均で fingerprint を作る。"""
    return {k: float(np.mean(v[-w:])) for k, v in hist.items()}


def _spawn(master):
    return np.random.default_rng(master.integers(0, 2**63 - 1))


def figG1(fps):
    """5プリセットの fingerprint（正規化グループ棒）。"""
    metrics = [("morale", "morale"), ("innov", "innovation"), ("perf", "performance"),
               ("consensus", "consensus"), ("helpless", "helplessness")]
    names = list(PRESETS.keys())
    x = np.arange(len(metrics))
    width = 0.16
    fig, ax = plt.subplots(figsize=(12, 5.5))
    colors = {"wolf": "C0", "ant": "C1", "chimp": "C4", "bonobo": "C2", "hyena": "C3"}
    for j, nm in enumerate(names):
        vals = [fps[nm][key] for key, _ in metrics]
        ax.bar(x + (j - 2) * width, vals, width, label=nm, color=colors[nm])
    ax.set_xticks(x)
    ax.set_xticklabels([lab for _, lab in metrics])
    ax.set(title="MA-4: each management preset (C,A) yields a distinct population regime (fingerprint)",
           ylabel="value (morale/innovation/performance/consensus in [0,1]; helplessness=fraction)")
    ax.legend(loc="upper right", ncol=5, fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figG1_fingerprints.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figG1] saved -> {path}")


def figG2(master):
    """相図：fear × conformity を振り（他ノブは中庸）、morale を色表示。regime 構造。"""
    fears = np.linspace(0.0, 0.8, C.sweep_points)
    kconfs = np.linspace(0.0, C.kconf_max, C.sweep_points)
    Z = np.empty((C.sweep_points, C.sweep_points))
    Zi = np.empty((C.sweep_points, C.sweep_points))
    base = dict(f=0.3, ineq=0.2, omega=0.5, c=0.7)
    for i, kc in enumerate(kconfs):
        for j, fe in enumerate(fears):
            knobs = dict(fear=fe, kconf=kc, **base)
            fp = fingerprint(unified_sim(knobs, _spawn(master)))
            Z[i, j] = fp["morale"]
            Zi[i, j] = fp["innov"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    for ax, M_, title, lab in ((ax1, Z, "morale", "mean morale"),
                               (ax2, Zi, "innovation", "best-practice adoption")):
        im = ax.pcolormesh(fears, kconfs, M_, cmap="RdYlGn", vmin=0, vmax=1, shading="auto")
        ax.set(title=f"Regime landscape: {title}", xlabel="fear", ylabel="conformity kconf")
        fig.colorbar(im, ax=ax, label=lab)
    fig.suptitle("MA-4 phase diagram (other knobs neutral): (C,A) space has continuous regime structure")
    fig.tight_layout()
    path = os.path.join(OUT, "figG2_phase_diagram.png")
    fig.savefig(path, dpi=125); plt.close(fig)
    print(f"[figG2] saved -> {path}")


def figG3(fps):
    """形質空間：innovation × morale 平面に5プリセットを配置（互いに分離するか）。"""
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    colors = {"wolf": "C0", "ant": "C1", "chimp": "C4", "bonobo": "C2", "hyena": "C3"}
    for nm in PRESETS:
        x = fps[nm]["perf"]; y = fps[nm]["morale"]
        s = 250 + 900 * fps[nm]["helpless"]          # 点の大きさ＝無力感
        ax.scatter(x, y, s=s, c=colors[nm], alpha=0.7, edgecolors="k")
        ax.annotate(nm, (x, y), fontsize=9, ha="center", va="center")
    ax.set(title="MA-4 trait space: the 5 presets separate (x=performance, y=morale; size=helplessness)",
           xlabel="performance (engaged output)", ylabel="morale", xlim=(-0.05, 1.6), ylim=(0, 1.05))
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(OUT, "figG3_trait_space.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"[figG3] saved -> {path}")


def main():
    os.makedirs(OUT, exist_ok=True)
    master = np.random.default_rng(C.seed)
    print("=" * 80)
    print("多エージェント MA-4 5類型の創発的導出 — unified population simulation")
    print(f"seed={C.seed}  N={C.N}  K={C.K}  true_value={C.true_value}")
    print("検証: (C,A)ノブを変えると5動物類型が distinct な集団 regime として創発するか")
    print("=" * 80)
    hists = {nm: unified_sim(PRESETS[nm], _spawn(master)) for nm in PRESETS}
    fps = {nm: fingerprint(hists[nm]) for nm in PRESETS}
    print(f"{'type':16s} {'morale':>7s} {'innov':>7s} {'perf':>7s} {'consen':>7s} {'helpless':>8s} "
          f"{'split':>6s} {'perfE':>6s} {'perfL':>6s}")
    for nm in PRESETS:
        fp = fps[nm]
        pe = float(hists[nm]['perf'][:50].mean())
        pl = float(hists[nm]['perf'][-50:].mean())
        split = fp['fav'] - fp['disfav']                 # 厚遇−不遇の morale 差（chimp の分断署名）
        print(f"{nm+'('+JP[nm]+')':18s} {fp['morale']:7.3f} {fp['innov']:7.3f} {fp['perf']:7.3f} "
              f"{fp['consensus']:7.3f} {fp['helpless']:8.3f} {split:6.3f} {pe:6.3f} {pl:6.3f}")
    print("-" * 80)
    print("予測署名（比喩§2）との照合（§0：一致/部分/欠落を正直に）:")
    for nm in PRESETS:
        print(f"  {nm:7s} 予測: {PRED[nm]}")

    figG1(fps)
    figG2(_spawn(master))
    figG3(fps)
    print("=" * 80)
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
