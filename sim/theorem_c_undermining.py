"""
定理C（アンダーマイニング罠）— R_eff の解析的シミュレーション

検証する主張（docs/正本_ミクロ機構.md §4 修正項3, §6 定理C）:
  「f が x_ext より速く立ち上がる領域で dR_eff/dR_ext < 0。
   内在価値の高い（I₀大）役割では、関与に対する顕著な金銭報酬は実効動機を下げる。
   → 危険な役割（高I₀）と安全な報酬形態（情報的・予期せぬもの, f≈0）を式が指定する。」

機構:
  R_eff = D·(w·x_ext) + I₀·(1 − f(x_ext))
  f（内在価値の抑制）= 統制的・有形・予期される報酬で大、情報的・予期せぬ報酬で f≈0。
  ここでは統制的報酬を f = f_max·x_ext/(x_ext+x_half)（飽和・小 x で急峻）でモデル化。
  外発項 +x_ext が増えるより速く I₀·f が内発を削るとき、dR_eff/dx_ext < 0。

3ケース:
  high I0, controlling … 内在価値が高い役割に統制的（金銭）報酬 → 罠
  low  I0, controlling … 内在価値が低い役割 → 罠は出ない（削る内発が小さい）
  high I0, informational … 情報的報酬（f≈0）→ 罠は出ない（内発を削らない）

出力: sim/out/figC1_reffective.png, figC2_derivative.png, figC3_region.png ＋ stdout サマリ。
これは導関数の符号についての主張なので、R_eff の解析が忠実な検証になる（決定論）。
実行: python sim/theorem_c_undermining.py
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
from matplotlib.colors import TwoSlopeNorm

from config import CONFIG_C as C

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def f_suppress(x, character):
    """内在価値の抑制関数 f(x_ext)。統制的＝飽和的に立ち上がる、情報的＝0。"""
    x = np.asarray(x, dtype=float)
    if character == "controlling":
        return C.f_max * x / (x + C.x_half)
    return np.zeros_like(x)


def r_eff(x, I0, character):
    """実効報酬 R_eff = D·w·x_ext + I₀·(1 − f)。"""
    return C.D * C.w * np.asarray(x, dtype=float) + I0 * (1.0 - f_suppress(x, character))


def dr_eff_dx(x, I0, character):
    """∂R_eff/∂x_ext（解析）。controlling のみ抑制項が効く。"""
    x = np.asarray(x, dtype=float)
    if character == "controlling":
        return C.D * C.w - I0 * C.f_max * C.x_half / (x + C.x_half) ** 2
    return np.full_like(x, C.D * C.w)


CASES = [
    ("high I0, controlling", C.I0_high, "controlling", "C3"),
    ("low I0, controlling", C.I0_low, "controlling", "C0"),
    ("high I0, informational", C.I0_high, "informational", "C2"),
]


def figC1(xs):
    """FigC1: R_eff(x_ext)。高I₀×統制的 は自分の no-reward baseline を下回る（罠）。"""
    fig, ax = plt.subplots(figsize=(11, 5))
    r_high_ctrl = r_eff(xs, C.I0_high, "controlling")
    for label, I0, character, color in CASES:
        ax.plot(xs, r_eff(xs, I0, character), c=color, label=label)
    # 各ケースの no-reward baseline（x=0 の値＝純粋な内発 I₀）
    ax.axhline(C.I0_high, ls=":", c="gray", lw=1)
    ax.text(C.x_max, C.I0_high, " I0_high baseline", va="center", ha="right", fontsize=8, c="gray")
    # 罠の領域：高I₀×統制的 が baseline を下回る区間を陰影
    trap = r_high_ctrl < C.I0_high
    ax.fill_between(xs, 0, np.max(r_high_ctrl) + 1, where=trap, color="red", alpha=0.07)
    ax.set(title="Theorem C: tangible reward can LOWER effective motivation (high-I0 role)",
           xlabel="x_ext (external/monetary reward)", ylabel="R_eff (effective motivation)",
           xlim=(0, C.x_max), ylim=(0, max(r_high_ctrl.max(), r_eff(xs, C.I0_high, "informational").max()) * 1.05))
    ax.legend(loc="upper left")
    ax.text(0.45, 1.1, "undermining\ntrap", color="red", fontsize=9, ha="center")
    fig.tight_layout()
    path = os.path.join(OUT, "figC1_reffective.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figC1] saved -> {path}")


def figC2(xs):
    """FigC2: dR_eff/dx_ext。高I₀×統制的 のみ符号が負へ（負域を陰影）。"""
    fig, ax = plt.subplots(figsize=(11, 5))
    d_high_ctrl = dr_eff_dx(xs, C.I0_high, "controlling")
    for label, I0, character, color in CASES:
        ax.plot(xs, dr_eff_dx(xs, I0, character), c=color, label=label)
    ax.axhline(0, ls="--", c="k", lw=1)
    ax.fill_between(xs, d_high_ctrl, 0, where=(d_high_ctrl < 0), color="red", alpha=0.12,
                    label="dR_eff/dx_ext < 0 (backfire)")
    ax.set(title="Marginal effect of reward: dR_eff/dx_ext goes negative only for high-I0 + controlling",
           xlabel="x_ext (external/monetary reward)", ylabel="dR_eff / dx_ext",
           xlim=(0, C.x_max))
    ax.legend(loc="upper right")
    fig.tight_layout()
    path = os.path.join(OUT, "figC2_derivative.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figC2] saved -> {path}")


def figC3(xs):
    """FigC3: (I₀, x_ext) 平面で dR_eff/dx_ext を色表示。負（赤）＝報酬が逆効果になる領域。"""
    I0s = np.linspace(0.0, C.I0_max, 200)
    X, I = np.meshgrid(xs, I0s)
    dR = C.D * C.w - I * C.f_max * C.x_half / (X + C.x_half) ** 2

    fig, ax = plt.subplots(figsize=(10, 5.5))
    vmax = float(np.nanmax(np.abs(dR)))
    norm = TwoSlopeNorm(vcenter=0.0, vmin=-vmax, vmax=max(vmax * 0.3, np.nanmax(dR)))
    mesh = ax.pcolormesh(X, I, dR, cmap="RdBu", norm=norm, shading="auto")
    cs = ax.contour(X, I, dR, levels=[0.0], colors="k", linewidths=1.5)
    ax.clabel(cs, fmt={0.0: "dR_eff/dx = 0"}, fontsize=8)
    fig.colorbar(mesh, ax=ax, label="dR_eff / dx_ext")
    # 高/低 I₀ の参照線
    ax.axhline(C.I0_high, ls=":", c="k", lw=1)
    ax.text(C.x_max * 0.99, C.I0_high, " I0_high", va="bottom", ha="right", fontsize=8)
    ax.axhline(C.I0_low, ls=":", c="k", lw=1)
    ax.text(C.x_max * 0.99, C.I0_low, " I0_low", va="bottom", ha="right", fontsize=8)
    ax.set(title="Where adding external reward backfires (controlling reward)\n"
                 "red region = dR_eff/dx_ext < 0  → the formula flags high-I0 roles as dangerous",
           xlabel="x_ext (external/monetary reward)", ylabel="I0 (intrinsic value of the role)")
    fig.tight_layout()
    path = os.path.join(OUT, "figC3_region.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"[figC3] saved -> {path}")


def main():
    os.makedirs(OUT, exist_ok=True)
    print("=" * 70)
    print("定理C アンダーマイニング罠 — R_eff の解析")
    print(f"f_max={C.f_max} x_half={C.x_half} w={C.w} D={C.D}  I0_high={C.I0_high} I0_low={C.I0_low}")
    print("検証: 高I₀役割では顕著な統制的報酬が dR_eff/dx_ext<0 を生み実効動機を下げるか")
    print("=" * 70)

    xs = np.linspace(0.0, C.x_max, C.n_points)

    # x→0 での限界効果（符号）
    slope0_high = C.D * C.w - C.I0_high * C.f_max / C.x_half
    slope0_low = C.D * C.w - C.I0_low * C.f_max / C.x_half
    I0_thresh = C.D * C.w * C.x_half / C.f_max     # これを超える I₀ で x→0 から undermining
    print(f"[slope at x_ext→0] high-I0 controlling = {slope0_high:+.3f}  "
          f"low-I0 controlling = {slope0_low:+.3f}  informational = {C.D*C.w:+.3f}")
    print(f"[undermining 閾値] I0 > {I0_thresh:.3f} で x_ext→0 から報酬が逆効果 "
          f"(high={C.I0_high}>閾値, low={C.I0_low}<閾値)")

    # 高I₀×統制的の罠の深さ
    R = r_eff(xs, C.I0_high, "controlling")
    base = C.I0_high                               # x=0 の R_eff（純内発）
    imin = int(np.argmin(R))
    print(f"[trap] high-I0 controlling: R_eff(x=0)={base:.3f} → "
          f"最小 R_eff={R[imin]:.3f} @ x_ext={xs[imin]:.3f}  "
          f"(罠の深さ={base - R[imin]:.3f}：報酬を払う方が無報酬より悪い)")
    # baseline へ戻るのに要する x_ext
    above = np.where(xs > xs[imin], R >= base, False)
    x_recover = xs[np.argmax(above)] if above.any() else float("nan")
    print(f"[trap] R_eff が baseline({base:.2f}) に戻るのに要する x_ext ≈ {x_recover:.3f}")

    figC1(xs)
    figC2(xs)
    figC3(xs)
    print("=" * 70)
    print(f"done. figures in: {OUT}")


if __name__ == "__main__":
    main()
