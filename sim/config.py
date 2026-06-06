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
class ConfigMA6:
    """多エージェント MA-6（規模＝Dunbar 壁）の設定。

    有界社交容量 D（各自が信頼／監視できる相手の上限）を置く。集団規模 N が増えると
    評判被覆 coverage=min(1, D/(N-1)) が下がり、監視外の相手では裏切りが罰されず協力が
    維持不能になる。条件付き協力（reciprocity 閾値）の閾値ダイナミクスにより、協力の
    高位アトラクタが鞍点分岐で消え、N≈壁 で相転移的に崩落する（＝Dunbar 壁）。
    壁は普遍数でなく容量 D に比例する（§0：「150」は人の容量推定であって普遍定数でない）。

    脱「通俗版」：規模の問題を「もっと管理職を増やせ」でなく、容量 D に対する構造問題として
    示す。N>壁 では同じ施策でも cohesion が崩れ chimp 的な分断・政治が創発しうる。
    """
    seed: int = 20260604
    D: int = 40                # Dunbar 容量（監視/信頼できる相手数の上限）
    beta: float = 8.0          # 条件付き協力ゲートの急峻さ（大きいほど壁が鋭い）
    theta: float = 0.40        # reciprocity 閾値（acquaintance の協力率がこれ未満だと裏切りへ）
    coop0: float = 1.0         # 初期協力率（全員協力＝cohesive な小集団から成長させる）
    T: int = 120               # ダイナミクスのステップ数
    n_fig1: tuple = (20, 70, 250)   # Fig1 の代表規模（壁の下／近傍／上）。壁は実測で確認
    # Fig2 規模スイープ
    N_min: int = 5
    N_max: int = 320
    sweep_points: int = 32
    sweep_seeds: int = 5
    # Fig3 壁 × 容量 D（壁が D に比例することの確認）
    D_values: tuple = (20, 40, 60, 80)
    wall_thresh: float = 0.5   # 最終協力率がこれを下回る最小 N を「壁」と定義


CONFIG_MA6 = ConfigMA6()


@dataclass(frozen=True)
class ConfigMA7:
    """多エージェント MA-7（階層別最適化＝層ごとに別 regime）の設定。

    比喩 §5「同じ会社でも層で最適な生き物は違う」を形式化。層ごとに『タスク』が違う：
      - 現場（floor）＝探索タスク（真実=より良い practice の発見）。低同調が最適（wolf）。
      - 管理（body）＝調整タスク（整列=皆が同じ規格に揃う）。高同調が最適（ant）。
    経営（exec）＝この architecture（各層の regime と結合 λ）を設計する層。
    org 性能 P = 現場探索 E × 管理調整 Co。

    非自明な帰結（通俗版＝「全社を1つの型で揃える」と分岐）:
      - 一律 regime（全 wolf / 全 ant）は必ずどこかの層を犠牲にし劣る。
      - 最適は差別化（現場=低同調・管理=高同調）＝(c_F,c_B) 平面の対角線(一律)でなく off-diagonal。
      - ただし結合 λ が強い（管理の同調が現場へ漏れ＝process 押し付け）と現場の実効同調
        c_F+λ·c_B が上がり探索が死に P が崩落＝現場の autonomy が要る（MA-5 と連結）。
    """
    seed: int = 20260604
    K: int = 4
    true_value: tuple = (1.0, 1.5, 0.6, 0.6)   # 現場の探索: option1=最良, option0=status quo
    incumbent: int = 0
    best: int = 1
    N_floor: int = 200         # 現場（探索）人数
    N_body: int = 400          # 管理下の本体（調整）人数
    T: int = 150
    eta: float = 0.15          # RL 学習率（共通）
    tau: float = 0.30          # 現場の探索温度
    tau_body: float = 0.30     # 本体の温度
    reward_noise: float = 0.30 # 現場 報酬ノイズ
    coord_noise: float = 0.20  # 調整ゲームのノイズ（大きいほど低同調で整列しにくい）
    V_init_incumbent: float = 1.0

    # Fig1 の4アーキテクチャ（c_F=現場同調, c_B=管理同調, lam=結合）
    c_wolf: float = 0.2        # 低同調（wolf 寄り）
    c_ant: float = 3.0         # 高同調（ant 寄り）
    lam_loose: float = 0.05    # 緩い結合（現場の autonomy 保持）
    lam_tight: float = 1.0     # 強い結合（管理が現場に process 押し付け）

    # Fig2 (c_F × c_B) 相図（lam=loose）, Fig3 結合 λ スイープ
    grid_points: int = 15
    c_max: float = 3.0
    lam_points: int = 16
    lam_max: float = 1.5
    sweep_seeds: int = 3


CONFIG_MA7 = ConfigMA7()


@dataclass(frozen=True)
class ConfigMA8:
    """多エージェント MA-8（蜂起カスケード＝MA-1 恐怖伝播の counterpart・別構成）の設定。

    MA-1 は Ĝ↓（恐怖）が観察で「容易に」伝染することを示した（下方・帰属ゲートなし）。
    MA-8 は同じ観察伝播の枠組みで Ĝ↑（有効性・勇気）を扱うが、帰属ゲート（現 Ĝ）で抑制される
    （§4 修正項1：低 Ĝ では他者の成功を自分に帰属できない＝「あいつは特別」）。p_try=0・decay
    追加・初期条件など差異ゆえ厳密な「双対」ではない（multiagent_uprising.py docstring 参照）。
    だから無力感アトラクタ（低 Ĝ で全員撤退＝長い忍従）は安定で、蜂起は稀かつ突発的：
    外生 seed（指導者＝確実に勝てる統制可能経験の体現・定理B の脱出注入）が臨界質量を
    超えて初めて帰属ゲートを突破しカスケードする。figK3 で恐怖伝播（下方・ゲートなし）と
    有効性伝播（上方・帰属ゲート）を同条件で並べ「なぜ抑圧は安定で蜂起は稀か」を機構の
    非対称として示す。（docs/応用_集団蜂起.md §2,§4／docs/多エージェント設計.md §1 結合③）
    """
    seed: int = 20260604
    L: int = 24                  # 格子の一辺（N=L*L 体）
    Ghat0_low: float = 0.15      # 無力感アトラクタ初期（全員 theta_giveup 未満＝撤退・長い忍従）
    Ghat0_high: float = 0.85     # 恐怖対照（figK3）の健全初期
    theta: float = 0.45          # 行動ゲート閾値：Ĝ>theta で「動員（立ち上がった）」と判定
    theta_giveup: float = 0.30   # 撤退ラッチ：Ĝ<この値 で自発行動停止（§1 自己封止）
    Ghat_floor: float = 0.02
    lam_direct: float = 0.15     # 自分の行動成功による Ĝ↑（上方＝帰属ゲート Ĝ·(1−Ĝ) 付き）
    lam_obs: float = 0.40        # 観察伝播率（恐怖down／有効性up 共通係数。非対称はゲートの有無から創発）
    p_try: float = 0.0           # 0＝撤退ラッチは吸収的（定理B：忍従は自然回復しない）。
    #                              MA-1 と違い自発再挑戦の対抗力は置かない＝蜂起は観察伝播でのみ着火する。
    #                              （>0 にすると統制可能環境で自発成功が snowball し無力感が自然回復してしまう）
    decay: float = 0.05          # 撤退者の Ĝ が floor へ引かれる速さ＝無力の再強化（諦めへの引力）。
    #                              定理B 低活動アトラクタの動的表現。弱い伝播 front を消し、臨界質量を
    #                              超える seed だけがカスケードを着火させる＝蜂起の閾値性（Granovetter）。
    seed_side: int = 8           # 指導者 patch（中央 seed_side×seed_side）。外生注入の核（スイープ中は固定）
    t_seed_start: int = 20       # 指導者の出現（以降 seed を外生 clamp）
    T: int = 300
    # figK2/K3 スイープ（観察伝播強度 lam_obs → 最終動員率／崩落率）。seed_side 固定で社会的結合を振る。
    sweep_lo: float = 0.0
    sweep_hi: float = 0.5
    sweep_points: int = 21
    sweep_seeds: int = 4         # p_try=0 で全 run 決定論＝実質1回。将来 p_try>0 用の平均足場


CONFIG_MA8 = ConfigMA8()


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


@dataclass(frozen=True)
class ConfigMA9:
    """多エージェント MA-9（業種別最適化＝最適 regime は業種の関数）の設定。

    橋渡しの「業種別」を形式化。MA-7 が『層ごと』に最適 regime が違うことを示したのに対し、
    MA-9 は『業種（タスク環境）ごと』に最適 regime が違うことを示す。業種を2軸で定義する
    （最小の戯画・§0）:
      - 変動性 v：最良 practice（正解 option）が確率 v で毎期入れ替わる＝探索が要る度合い。
      - 失敗コスト ec：非標準（非コンセンサス）行動への罰＝標準化・信頼性が要る度合い
        （恐怖の正当域＝docs/正本_ミクロ機構.md §7 と接続）。
    5管理 regime（4ダイヤル署名の preset）を業種グリッドで総当たりし、業種ごとの勝者地図を出す。

    非自明な帰結（通俗版「ベストプラクティス＝唯一の最適経営」と分岐）:
      - 最適 regime は業種 (v, ec) の関数＝普遍の勝者は無い。
      - ある業種で最適な型は、別業種で最悪になりうる（勝ち文化の移植は失敗）。
      - 高 v×高 ec（救急/トレーディング）は探索と標準化が二律背反でどの型も快適でない。
    """
    seed: int = 20260604
    N: int = 300               # エージェント数（well-mixed）
    K: int = 4                 # practice 選択肢数
    T: int = 400               # ステップ数（変動の合間に収束する余地を与える）
    eta: float = 0.20          # 個人 RL（practice 価値）の基礎学習率（変動を追える速さ）
    reward_noise: float = 0.12 # 報酬ノイズ（小さめ＝追従シグナルを noise に埋もれさせない）
    perf_window: int = 80      # 後半 window で性能平均（過渡を除く）

    # 業種2軸の範囲（v は「追従可能な変動」域＝探索が効く範囲に取る・§0：軸範囲も戯画）
    v_lo: float = 0.0          # 変動性 下限（完全に安定）
    v_hi: float = 0.05         # 変動性 上限（≒20手に1度 正解が動く＝探索なら追え・固着なら追えない速さ）
    ec_lo: float = 0.0         # 失敗コスト 下限（逸脱は無罰）
    ec_hi: float = 1.00        # 失敗コスト 上限（逸脱を強く罰）

    grid_points: int = 15      # Fig2 相図（v × ec）の解像度
    sweep_seeds: int = 4       # 各点の seed 平均


CONFIG_MA9 = ConfigMA9()


@dataclass(frozen=True)
class ConfigMA10:
    """多エージェント MA-10（階層別×業種別の合成＝最適 org 設計は業種の関数）の設定。

    MA-7（層別最適：現場=探索=低同調 wolf／管理=調整=高同調 ant）を MA-9 の業種
    （変動性 v × 失敗コスト ec）に埋め込む。すると **現場の最適同調 c_F* が業種の関数** になる:
      - 高変動・低失敗コスト（IT/創造）：現場は低同調（wolf）＝MA-7 の差別化が最も効く。
      - 低変動・高失敗コスト（航空/原子力/医療）：現場の逸脱が罰されるので **現場も標準化**
        （c_F* が上がる＝差別化が圧縮）。"現場の官僚化"が高 stakes では最適。
    通俗版「現場に一律で裁量を」とも「全社一型」とも分岐し、MA-7 の処方自体が業種依存と示す。

    機構：現場＝探索タスク（正解 practice が確率 v で移る）＋ ec·逸脱の罰 → E=現場性能[0,1]。
      管理＝調整タスク（同調 c_B で整列）→ Co=合意。org 性能 P=E×Co。c_F・c_B を業種ごとに掃引。
    """
    seed: int = 20260604
    K: int = 4
    N_floor: int = 200         # 現場（探索）人数
    N_body: int = 400          # 管理下の本体（調整）人数
    T: int = 300
    eta: float = 0.20          # 現場 RL 学習率（変動を追える速さ）
    tau: float = 0.30          # 現場の探索温度
    tau_body: float = 0.30     # 本体の温度
    reward_noise: float = 0.15
    coord_noise: float = 0.20  # 調整ゲームのノイズ
    perf_window: int = 60      # 後半 window で平均

    # 業種の範囲（MA-9 と整合）
    v_lo: float = 0.0
    v_hi: float = 0.05         # 追従可能な変動上限
    ec_lo: float = 0.0
    ec_hi: float = 1.20        # 失敗コスト上限

    grid_points: int = 15      # (c_F × c_B) 相図解像度（figM1）
    c_max: float = 3.0         # 同調強度の掃引上限
    ind_points: int = 13       # figM2 業種スイープ点（ec 軸）
    map_points: int = 9        # figM3 c_F* ヒートマップの (v × ec) 解像度（粗め＝計算量抑制）
    sweep_seeds: int = 8        # seed 平均（E(c_F) の最適は平坦ゆえ argmax 安定化に多めに取る）


CONFIG_MA10 = ConfigMA10()
