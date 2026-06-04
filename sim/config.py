"""定理B（統制可能性の崖）シミュレーションの設定。

各パラメータが機構（docs/正本_ミクロ機構.md §6 定理B）のどの量に対応するかを
コメントで明記する。pyyaml への依存を避けるため設定は Python で持つ（新規依存ゼロ）。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # --- 乱数（再現性）---
    seed: int = 20260604           # マスターシード。固定で完全再現

    # --- エージェント（学習主体）---
    Ghat0: float = 0.60            # Ĝ 初期値：一般化統制可能性の信念, [0,1]
    beta: float = 30.0             # 行動ゲートの急峻さ P(act)=σ(β(Ĝ−θ))。大きいほど崖が鋭い。
    #                                ※定理Bの「行動はĜが閾値を超える間だけ持続」を素直に表すには
    #                                  急峻なゲートが要る。緩いと撤退状態でも稀に行動し、統制可能環境で
    #                                  snowball 回復してしまい「自然回復しない」を再現できない（吸収的でない）。
    theta: float = 0.45            # 行動ゲートの閾値：Ĝ<θ で関与（行動）が崩れ撤退へ
    theta_giveup: float = 0.30     # 撤退ラッチ：Ĝ<この値 で自発行動を完全停止（§1 回避＝データ遮断）。
    #                                自発サンプリングが絶えるため低活動状態は吸収的になり「自然回復しない」。
    #                                外生注入（force）だけがラッチを無視して行動させられる＝唯一の脱出路。
    lam: float = 0.08              # Ĝ の学習率。※行動した試行でのみ更新＝自己封止（要石）
    Ghat_floor: float = 0.02       # Ĝ の下限（残余の希望）。0に張り付くと外生注入でも
    #                                脱出不能になるため、わずかな種を残す

    # --- 環境（随伴構造 C）---
    p_punish_if_act: float = 0.05  # 統制可能条件：行動すれば罰はほぼ回避できる
    # 統制可能の「行動しない時の罰率」と統制不能の「罰率」は、罰強度 intensity で外から与える
    # （統制不能＝行動に依存しない＝Seligman の yoked-control 設計）

    # --- 実験規模 ---
    n_agents: int = 200            # 平均を取るエージェント数
    T: int = 400                   # Fig1 の試行数
    intensity_fig1: float = 0.85   # Fig1 の罰強度（高め：不能条件で崩落が明瞭に出る）

    # --- Fig2 罰強度スイープ ---
    sweep_points: int = 31         # intensity を 0..1 で何点刻むか
    T_sweep: int = 400             # スイープ各点の試行数

    # --- Fig3 回復テスト（3フェーズ）---
    T_phase: int = 400             # 各フェーズの試行数
    # Phase3 は全試行で行動を強制（＝「確実に勝てる統制可能経験」の外生注入）


CONFIG = Config()


@dataclass(frozen=True)
class ConfigA:
    """定理A（報酬撤回 = 罰）シミュレーションの設定。

    マスター方程式 §5 ＋ 参照点依存 §4 修正項2 を使う。3条件（never/sustained/withdraw）を比較。
    """
    # --- 乱数（再現性）※ reward_noise=0 のときは決定論的で seed は無関係 ---
    seed: int = 20260604

    # --- エージェント（§5 マスター方程式 ＋ §4 修正項2）---
    eta: float = 0.20          # V の学習率
    kappa: float = 2.25        # 損失回避 κ>1。撤回時の負の δ を κ 倍に増幅（K&T の標準値 2.25）
    g: float = 1.0             # 帰属ゲート。ここでは統制可能と仮定し 1 に固定して κ/ρ 効果を分離
    rho_rate: float = 0.05     # 参照点 ρ が経験報酬へ適応する速さ（快楽の踏み車）

    # --- 恐怖エンジン（負の損失 δ が τ を狭める。V には書かない）---
    tau_base: float = 1.0      # 平常の探索温度
    tau_min: float = 0.10      # τ の下限
    fear_c: float = 0.30       # 損失 δ が τ を狭める強さ
    tau_recover: float = 0.03  # τ が平常へ戻る速さ

    # --- 報酬スケジュール ---
    R_base: float = 1.0        # 基準報酬
    R_high: float = 2.0        # 引き上げ後の報酬
    reward_noise: float = 0.0  # 報酬ノイズ σ（0＝決定論。定理Aは構造的必然なので既定0）

    # --- フェーズ ---
    t1: int = 100              # 報酬引き上げ開始（全条件の give イベント）
    t2: int = 250              # 撤回（withdraw 条件のみ baseline へ戻す）
    T: int = 500               # 総ステップ
    n_agents: int = 1          # reward_noise>0 のとき平均を取る個体数


CONFIG_A = ConfigA()


@dataclass(frozen=True)
class ConfigC:
    """定理C（アンダーマイニング罠）の設定。

    R_eff = D·(w·x_ext) + I₀·(1−f) を解析（§4 修正項3, §6 定理C）。
    f は内在価値の抑制関数：統制的報酬で大きく、情報的報酬で f≈0。決定論なので seed 不要。
    """
    I0_high: float = 2.0       # 内在価値の高い役割（危険：抑制される余地が大きい）
    I0_low: float = 0.3        # 内在価値の低い役割
    f_max: float = 0.9         # 統制的報酬による内発抑制の上限（最大 90%）
    x_half: float = 0.4        # f の半飽和点（小さいほど f が x_ext に対し急峻に立ち上がる）
    w: float = 1.0             # 外発報酬の重み
    D: float = 1.0             # 遅延割引（ここでは即時 = 1）
    x_max: float = 3.0         # x_ext スイープ上限
    n_points: int = 241        # スイープ解像度
    I0_max: float = 3.0        # ヒートマップの I₀ 上限


CONFIG_C = ConfigC()
