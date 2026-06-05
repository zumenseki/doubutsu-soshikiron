"""
全シミュレーションを1コマンドで実行し、総括図（contact sheet）を生成する。

  python sim/run_all.py

各シムの main() を順に呼んで out/ に全図を再生成し、代表図を 1 枚に集約した
out/fig_overview.png を作る（サイト/発信用の「理論の検証 一覧」素材）。
再現性は各 config の seed 固定で担保。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import theorem_a_reward_withdrawal as A
import theorem_b_controllability as B
import theorem_c_undermining as Cmod
import theorem_d_compound_cost as D
import multiagent_fear_contagion as MA1
import multiagent_social_reference as MA2
import multiagent_policy_imitation as MA3
import multiagent_archetypes as MA4
import multiagent_rewilding as MA5
import multiagent_dunbar as MA6

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# (コンソール見出し[JP], 図タイトル[ASCII], モジュール, 代表図)
SIMS = [
    ("定理B 統制可能性の崖", "Thm B: controllability cliff", B, "fig2_intensity_sweep.png"),
    ("定理A 報酬撤回=罰", "Thm A: reward withdrawal = punishment", A, "figA3_asymmetry.png"),
    ("定理C アンダーマイニング罠", "Thm C: undermining trap", Cmod, "figC1_reffective.png"),
    ("定理D 恐怖の複合コスト", "Thm D: fear's compound cost", D, "figD2_three_channels.png"),
    ("MA-1 恐怖伝播（粛清カスケード）", "MA-1: fear contagion (purge cascade)", MA1, "figMA1_cascade.png"),
    ("MA-2 社会的参照点（公平性）", "MA-2: social reference (fairness)", MA2, "figE1_relative_deprivation.png"),
    ("MA-3 方策模倣（同調）", "MA-3: conformity (norm lock-in)", MA3, "figF3_lockin.png"),
    ("MA-4 5類型の創発的導出", "MA-4: 5 archetypes emerge", MA4, "figG3_trait_space.png"),
    ("MA-5 再野生化（Stage5脱出）", "MA-5: rewilding (escape lock-in)", MA5, "figH1_rewilding.png"),
    ("MA-6 規模（Dunbar壁）", "MA-6: Dunbar wall (size)", MA6, "figI2_dunbar_wall.png"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    for jp, _, mod, _ in SIMS:
        print("\n" + "#" * 80)
        print("# " + jp)
        print("#" * 80)
        mod.main()

    # 総括 contact sheet（代表図を 3×4 で集約・余り枠は消す）
    fig, axes = plt.subplots(3, 4, figsize=(24, 13))
    flat = axes.ravel()
    for ax, (_, ascii_title, _, figname) in zip(flat, SIMS):
        path = os.path.join(OUT, figname)
        ax.imshow(mpimg.imread(path))
        ax.axis("off")
        ax.set_title(ascii_title, fontsize=10)
    for ax in flat[len(SIMS):]:        # 余った枠は消す（SIMS が枠数未満でも安全）
        ax.axis("off")
    fig.suptitle("Theory validation overview — 4 theorems (single-agent) + multi-agent MA-1..6",
                 fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    overview = os.path.join(OUT, "fig_overview.png")
    fig.savefig(overview, dpi=110)
    plt.close(fig)

    print("\n" + "=" * 80)
    print(f"全シム完了。総括図 -> {overview}")
    print("=" * 80)


if __name__ == "__main__":
    main()
