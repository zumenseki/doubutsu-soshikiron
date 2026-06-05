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


@dataclass(frozen=True)
class ConfigMA:
    """多エージェント層 MA-1（恐怖伝播＝粛清カスケード）の設定。

    N=L×L 体をトーラス格子に置き、観察学習＋情動伝染で Ĝ の崩落が伝播する
    （docs/多エージェント設計.md §4）。
    """
    seed: int = 20260604
    L: int = 24                 # 格子の一辺（N=L*L 体）
    Ghat0: float = 0.70         # 全員の初期 Ĝ
    theta_giveup: float = 0.30  # この値未満で「崩落（撤退）」＝helpless 信号 s=0 を発する
    Ghat_floor: float = 0.02
    lam_direct: float = 0.15    # 直接経験での Ĝ 更新率（自分の統制成功＝回復／自分の罰＝下落）
    lam_obs: float = 0.40       # 恐怖の伝染率（恐怖の隣人観察→Ĝ↓のみ。上方伝染はない＝§1）
    #                             既定は tipping(≈0.35) の少し上＝front が時間をかけて広がる cascade regime
    p_try: float = 0.06         # 崩落者が稀に再挑戦する確率（統制可能なら回復＝tipping の対抗力）
    purge_side: int = 6         # 粛清シードのパッチ（角 purge_side×purge_side）
    t_purge_start: int = 20
    t_purge_end: int = 80       # 粛清は窓 [start,end)。その後 環境は全員 統制可能へ戻る
    T: int = 300
    # Fig2 スイープ（伝染強度 → 最終崩落率）
    sweep_lo: float = 0.0
    sweep_hi: float = 0.5
    sweep_points: int = 21
    sweep_seeds: int = 4


CONFIG_MA = ConfigMA()


@dataclass(frozen=True)
class ConfigSR:
    """多エージェント MA-2（社会的参照点＝公平性）の設定。

    ρ_i = ω·E_self + (1−ω)·(他者の結果) を集団へ（§4 修正項2）。決定論なので seed 不要。
    """
    N: int = 400               # エージェント数（well-mixed）
    eta: float = 0.20          # V（士気）の学習率
    kappa: float = 2.25        # 損失回避（>1）。相対的剥奪の損を κ倍に増幅
    rho_rate: float = 0.05     # 参照点 ρ の適応速度
    omega: float = 0.50        # 自己重み。(1−ω)＝社会比較の重み（FigE1/E3 既定）
    R_base: float = 1.0        # 基準報酬
    phi: float = 0.50          # 厚遇される割合
    Delta: float = 0.60        # 不平等の大きさ（厚遇=+Δ, 不遇=−Δ。平均は不変）
    t_intro: int = 150         # 不平等を導入する時点（FigE1）
    T: int = 400
    # FigE2 スイープ（不平等度 → 平均士気）と社会比較の強弱
    sweep_points: int = 21
    Delta_max: float = 1.0
    omega_high_compare: float = 0.15   # 社会比較が強い（他者参照が重い）
    omega_low_compare: float = 0.85    # 社会比較が弱い（自己参照が重い）


CONFIG_SR = ConfigSR()


@dataclass(frozen=True)
class ConfigCF:
    """多エージェント MA-3（方策模倣＝規範・同調）の設定。

    他者の選択（人気）を観察して模倣。score = V + κ_conf·人気。
    同調が強いと、より良い選択肢があっても status quo にロックインする（前例主義）。
    """
    seed: int = 20260604
    N: int = 400
    K: int = 4
    # 真の平均報酬。option1 が最良(1.5)、option0 は全員が最初にやっている status quo(1.0)
    true_r: tuple = (1.0, 1.5, 0.6, 0.6)
    incumbent: int = 0         # 初期規範（status quo）
    best: int = 1              # 真の最良
    reward_noise: float = 0.30
    eta: float = 0.15          # 個人の RL 学習率
    tau: float = 0.30          # 探索温度
    V_init_incumbent: float = 1.0   # 全員 status quo を「知っている」状態から開始
    kappa_conf: float = 3.0    # 同調強度の既定（FigF1 の high 側。low は 0 と比較）
    T: int = 300
    # FigF2 スイープ（同調強度 → 合意 と 最適性）
    sweep_points: int = 21
    kappa_max: float = 4.0
    sweep_seeds: int = 6


CONFIG_CF = ConfigCF()


@dataclass(frozen=True)
class ConfigMA4:
    """多エージェント MA-4（5類型の創発的導出）の共有パラメータ。

    全チャネルを統合した統一 population 模型。経営者の (C,A) 設計＝ノブ
    (fear, f, kconf, ineq, omega, contingency) を振り、集団 regime を測る。
    5プリセット（type 別ノブ）は multiagent_archetypes.py の PRESETS。
    """
    seed: int = 20260604
    N: int = 400
    K: int = 4
    T: int = 300
    true_value: tuple = (1.0, 1.5, 0.6, 0.6)   # option1=最良, option0=status quo
    incumbent: int = 0
    best: int = 1
    theta: float = 0.30        # これ未満で撤退（無力・離脱）
    floor: float = 0.02
    M0: float = 0.60           # 初期 morale
    eta_M: float = 0.10        # morale 更新率
    eta_V: float = 0.15        # 方策（option価値）更新率
    rho_rate: float = 0.05     # 参照点の適応速度
    tau_base: float = 0.35     # 基礎探索温度
    tau_min: float = 0.08
    fear_tau: float = 0.80     # 恐怖が τ を狭める強さ（τ_eff=max(tau_min, tau_base(1−fear_tau·fear)))
    kappa: float = 2.25        # 損失回避
    lam_contagion: float = 0.20  # 恐怖伝染係数（fear·崩落率でスケール・runaway 抑制）
    p_try: float = 0.05        # 崩落者の再挑戦率
    R_ext: float = 1.0         # 外発報酬スケール
    I0: float = 0.60           # 内在価値（f で抑制される）
    punish_mag: float = 1.0    # 統制不能罰の大きさ
    frac_fav: float = 0.30     # 厚遇される割合（不平等）
    ineq_boost: float = 1.2    # 厚遇の上乗せ（ineq でスケール）
    # 相図スイープ（fear × conformity）
    sweep_points: int = 15
    kconf_max: float = 3.0


CONFIG_MA4 = ConfigMA4()


@dataclass(frozen=True)
class ConfigMA5:
    """多エージェント MA-5（再野生化＝Stage5硬直からの集団脱出）の設定。

    硬直した ant/Stage5 集団（高 kconf・status quo へ固着・MA-3/MA-4 の ant regime）は、
    より良い option1 が在っても人気バイアスで離陸できない。脱出機構を検証する：
      - 全体を少し緩めるだけ（kconf 微減）では谷に留まる（exhortation は効かない）。
      - 独自ルールの隔離細胞（低 kconf・多数派の人気から遮断）を注入し、発見後に
        再結合すると規範が反転しうる。ただし細胞が autonomy を保つ場合のみ。
        再吸収（細胞を多数派の高 kconf に戻す）すると人気に飲まれ元へ戻る。
    ＝定理B「外生注入だけが脱出路」の集団版（橋渡し：再野生化）。
    """
    seed: int = 20260604
    N: int = 400
    K: int = 4
    true_value: tuple = (1.0, 1.5, 0.6, 0.6)   # option1=最良, option0=status quo（既知）
    incumbent: int = 0
    best: int = 1
    T: int = 400
    eta: float = 0.15          # 個人 RL（option 価値）の学習率
    tau: float = 0.30          # 探索温度
    reward_noise: float = 0.30
    V_init_incumbent: float = 1.0   # 全員 status quo を「知っている」状態から開始

    kconf_locked: float = 3.0  # ant/Stage5：硬直集団の同調強度（単独でロック）
    kconf_nudge: float = 1.2   # 全体微緩：緩めても相転移閾値(≈0.8)超で谷に留まる
    kconf_iso: float = 0.0     # 隔離細胞：多数派の人気から自由（独自ルール）

    iso_frac: float = 0.30     # Fig1 の隔離細胞サイズ（母集団比）
    t_recouple: int = 150      # 隔離窓 [0,t_recouple)。以降は再結合
    # 観察的価値学習（実績デモ）：隔離細胞が示す option の実現 payoff を多数派が観察し
    # V を少し寄せる。0 なら人気(同調)のみで規範伝播（MA-3 と同型）。
    demo_rate: float = 0.05
    # 可視化閾値：ある option を実践する者が母集団比でこれ以上いて初めて「見える手本」となり
    # demo 対象になる。単発の偶発探索（pop≈1/N）は手本にならず、臨界質量（隔離細胞）が要る。
    vis_thresh: float = 0.05

    # Fig2 隔離サイズ スイープ
    sweep_points: int = 21
    iso_frac_max: float = 0.5
    sweep_seeds: int = 4
    # Fig3 相図（多数派 kconf × 隔離サイズ）
    grid_points: int = 15
    kconf_major_max: float = 3.0


CONFIG_MA5 = ConfigMA5()


@dataclass(frozen=True)
class ConfigD:
    """定理D（恐怖の複合コスト）の設定。

    恐怖は τ↓（狭窄）・k↑（近視眼）・習慣化 を同時に起こす独立3チャネルの劣化、を多腕タスクで検証。
    """
    seed: int = 20260604

    # --- タスク（多腕）---
    K: int = 6                 # 腕の数
    r_arm0_pre: float = 1.0    # arm0＝即時・小（局所最適）。途中で価値が下がる
    r_arm0_post: float = 0.3   # devaluation 後の arm0 報酬
    r_arm1: float = 3.0        # arm1＝遅延・大（大域最適。要探索＋遠視）
    delay_arm1: int = 5        # arm1 の遅延（割引 D(d)=1/(1+k·d) で効く）
    r_distractor: float = 0.2  # arm2..K-1（探索コスト）
    t_change: int = 300        # arm0 を devalue する時点
    T: int = 600               # 総ステップ
    n_agents: int = 200

    # --- 学習 ---
    eta: float = 0.10          # V（目標志向価値）の学習率
    habit_lr: float = 0.05     # 習慣 H の更新率

    # --- 恐怖の3チャネル（calm 値 と fear 値）---
    tau_calm: float = 0.60     # 探索温度（高＝広く探索）
    tau_fear: float = 0.12     # 恐怖で狭窄
    k_calm: float = 0.02       # 双曲割引（低＝遠い報酬も保つ）
    k_fear: float = 0.60       # 恐怖で近視眼（遅延大報酬を割り引いて消す）
    habit_calm: float = 0.0    # 習慣の重み（0＝目標志向）
    habit_fear: float = 4.0    # 恐怖で習慣優位（過去の選択を価値と無関係に反復）


CONFIG_D = ConfigD()
