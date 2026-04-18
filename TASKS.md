# TASKS.md

## Goal
将 `daily_stock_analysis` 彻底重构/重写为一个 **面向 Agent 的 stock-analysis skill 项目**，移除非核心产品壳，保留并重建“股票分析、市场分析、策略分析、结果输出”这些可复用核心能力。

## Scope Assumption（已确认）
- 目标形态：**skill-first repository**，不再继续维护 FastAPI / Web / Docker 服务形态
- 服务对象：**只服务 Agent**，不再把通用产品壳作为仓库核心目标
- 市场范围：继续覆盖 **A股 / 港股 / 美股**
- 数据源策略：继续以 **Tushare + 新闻搜索源** 为主，当前阶段**暂不收缩**
- 改造强度：接受 **高强度删改**，包括大面积删除旧目录、重写 README / docs / tests
- 核心输出：供 Agent / skill 调用的分析能力、技能说明、必要脚本、参考文档、最小验证测试
- 默认保留对象：分析主链、市场分析能力、策略能力、结构化输入输出合同、必要的数据获取与报告生成能力

## Status
- [x] 审查当前仓库 README、项目 AGENTS、既有长期记忆与历史重构结论
- [x] 明确最终目标架构与保留/删除边界
- [x] 盘点现有模块，划分为：保留 / 重写 / 删除 / 迁移参考
- [x] 设计新的 skill-first 目录结构与运行入口
- [x] 定义 skill 对外合同：输入、输出、能力边界、依赖配置
- [x] 重建最小可用主链：股票分析 / 市场分析 / 策略分析
- [x] 重建 skill 资源：`SKILL.md`、必要 `scripts/`、必要 `references/`、示例与验证脚本
- [x] 删除旧产品壳与无关耦合模块，完成目录瘦身
- [x] 重写 README / docs，使仓库说明与新形态一致
- [x] 执行最小可运行验证与回归验证
- [x] 汇报结果并给出 commit message 建议
- [x] 配置层减脂：收口 `.env.example` / `src/config.py` / `src/core/config_registry.py` 的旧产品壳字段与文案
- [x] 复跑配置相关测试与当前 skill+agent 回归，确认配置收口未破坏现有主链
- [x] Phase E.1 语义收口：将 `notification/notifier` 语义统一到报告输出口径，保留必要兼容层
- [x] Phase E.2 测试与工具清洁：收口 `test_env.py` / benchmark mark / 非阻塞 warning，降低回归噪音
- [x] Phase E.3 命名统一：继续收口 `strategy` / `skill` 双命名，明确“对外策略、对内 skill”或单一口径
- [x] Phase E.4 Agent 兼容层审计：盘点 `src/agent/*` 中的 legacy/compat wrapper，删无用、聚合有用兼容层
- [x] Phase E.5 配置最小化审计 v2：继续盘 `src/config.py` 里仅为旧入口保留的 LLM / runtime fallback 逻辑
- [x] Phase E.6 数据/搜索兼容债清理：继续抽离已下线 provider 的 compat 语义，收紧主路径说明
- [x] Phase F.1 主链真相源内迁设计：明确 `src/analyzer.py` / `src/core/pipeline.py` / `src/services/analysis_service.py` 与 `src/stock_analysis_skill/*` 的目标边界
- [x] Phase F.2 同步主链内迁：把股票分析主执行链逐步迁入 `src/stock_analysis_skill/*`，旧入口退为兼容壳
- [x] Phase F.3 异步主链对齐：把 `AnalysisTaskQueue -> AnalysisService -> StockAnalysisPipeline` 的调用关系对齐到新的 skill runtime 主链
- [x] Phase F.4 Analyzer 内核拆分：逐步拆 `src/analyzer.py`，优先迁出纯函数/结果归一化/后处理逻辑，避免与 F.2/F.3 混成一次高风险爆破
- [x] Phase F.5 回归与契约校验：按同步/异步/agent/script 四条链重跑回归，确认不存在双真相源
- [x] Phase E.9.A 提交当前文档对齐改动，清理工作区基线
- [x] Phase E.9.B 收口 `use_legacy_default_prompt` 命名为更准确的默认 bull-trend prompt 语义
- [x] Phase E.9.C 收口 agent/analyzer 的 env-managed LiteLLM Router 变量名与日志文案
- [x] Phase E.9.D 收薄 OrchestratorStageRuntime 委托层，避免重复创建 runtime helper
- [x] Phase E.9.E 继续收口 compatibility 文案：task payload / strategies 资源目录 / stage runtime / constructor shim 注释
- [x] Phase E.9.F 收口 agent_model_service / config.py 中仍带 legacy 心智的内部 helper 命名
- [x] Phase E.9.G 收口 agent memory / skill loader / runner / prompt defaults / runtime helper 的过时 legacy 文案
- [x] Phase E.9.H 收口配置元数据 / 搜索服务 / 数据源参考里的 transition wording
- [x] Phase G.1 兼容面收缩设计冻结：明确哪些字段/参数/placeholder 属于“可删 / 仅保留一层 shim / 必须长期保留”
- [x] Phase G.2 Task payload 收缩方案：评估 `result` / `runtime_payload` / `legacy_result` 的最终对外契约，并设计迁移顺序
- [x] Phase G.3 Managed-env placeholder 方案审计：评估 `__legacy_*` sentinel 是否保留、替换或包裹隐藏
- [x] Phase G.4 配置兼容字段退役计划：梳理 `RUN_IMMEDIATELY`、旧 env alias、no-op 开关、UI metadata 的退役等级与验证矩阵
- [x] Phase H.1 纯 skill 包目标冻结：明确“更纯 skill 包”允许保留/必须下沉/必须外移的目录与文件
- [x] Phase H.2 仓库结构纯化：收缩顶层非必要目录，优先把 skill 核心聚焦到 `SKILL.md` / `references/` / `scripts/` / `src/stock_analysis_skill/` / `strategies/`
- [x] Phase H.3 工程支撑分层：评估 `docs/` / `reports/` / `data_provider` / `templates` / `sources` / `patch` 是否应保留、下沉或移出主 skill 暴露面
- [x] Phase H.4 skill 包口径收尾：重写 README / SKILL / references，使仓库对外更像可分发的 skill bundle，而不是通用工程仓库
- [x] Phase H.5 回归与可发布性校验：验证脚本入口、合同层、skill 资源索引和最小/全量回归，确认纯化后仍可稳定使用
- [x] Phase I.1 Provider 内迁设计冻结：明确 `data_provider/` 与 `src/stock_analysis_skill/providers/` 的 canonical/compat 边界
- [x] Phase I.2 Provider 主体内迁：将运行时数据访问实现迁入 `src/stock_analysis_skill/providers/`
- [x] Phase I.3 兼容桥收口：将 `data_provider/*` 收口为 legacy import shim，避免外部导入立即中断
- [x] Phase I.4 口径同步：README/SKILL/references/docs 更新 provider canonical path 说明
- [x] Phase I.5 回归校验：验证 provider 相关定点矩阵与全量回归

## Proposed Phases

### Phase A - 边界定稿
- 明确仓库不再以 Web/API 产品为核心
- 明确 skill 的主要使用方式：单次分析、市场复盘、策略问答/策略分析
- 明确保留的数据源/模型接入策略

### Phase B - 结构重建
- 设计新的 skill-first 目录骨架
- 把“可迁移核心能力”从现有仓库中抽离出来
- 为 skill 定义稳定的 request/response 合同

### Phase C - 能力迁移与重写
- 重建股票分析主链
- 重建市场分析主链
- 重建策略/Agent 适配层
- 重建最小报告输出能力

### Phase D - 仓库瘦身
- 清理旧 Web/UI/API/通知/部署壳
- 清理与 skill 定位冲突的文档、脚本、配置、测试
- 补齐 skill 文档与最小验证

### Phase E - 语义收口与兼容层减脂
- 统一报告输出 / notifier / notification 语义
- 收口 strategy vs skill 双命名
- 清理 Agent 侧 legacy wrapper / compat layer
- 二次审计 config / provider fallback / 已下线搜索源兼容逻辑
- 清洁测试噪音与工具脚本历史包袱

### Phase F - 主链真相源内迁（高风险）
- 把 `src/analyzer.py` / `src/core/pipeline.py` / `src/services/analysis_service.py` 中仍然承担“业务真相源”的执行链逐步迁入 `src/stock_analysis_skill/*`
- 明确 `StockAnalysisSkillService`、`AnalysisService`、`StockAnalysisPipeline` 的最终边界，避免继续形成双真相源
- 对齐同步主链、异步任务链、脚本入口与 agent 调用链
- 迁移过程中旧入口只允许退化为兼容壳，不允许继续增长新业务逻辑

### Phase G - 真实兼容面收缩（需单独确认，高风险）
- 识别哪些“legacy / compatibility”残留已不只是文案，而是对外契约或运行时机制的一部分
- 先冻结收缩顺序，再分层处理：task payload → managed-env placeholder → config/env alias / metadata
- 每一类改动都必须先定义“兼容窗口 / 迁移路径 / 回滚点 / 回归矩阵”，禁止一次性爆破
- 默认目标不是“全部删除”，而是把必须长期保留的兼容面显式归类，把可退役部分收成有节奏的 deprecation 计划

### Phase H - 更纯的 skill 包化（需单独确认，高风险）
- 从“skill-first 工程仓库”进一步收口到“更像可分发 skill bundle 的仓库形态”
- 明确哪些目录属于 skill 核心（必须保留），哪些只是工程支撑（可下沉/外移），哪些已经不值得继续暴露在顶层
- 改造重点是 **结构纯化 + 对外暴露面纯化 + 文档口径纯化**，不是为了美观而删掉必要测试或运行时代码
- 默认目标不是把仓库压成极简模板，而是把它做成“核心一眼看出是 skill 包，工程配套尽量退到二线”的结构

### Phase I - Provider 层内迁（需单独确认，高风险）
- 将运行时数据访问层的 canonical path 从顶层 `data_provider/` 内迁到 `src/stock_analysis_skill/providers/`
- 允许短期保留 `data_provider/*` 作为兼容导入桥（shim），但不再承载业务真相源
- 目标是进一步提高 skill 包内聚度，同时避免一次性爆破历史导入路径

## Key Design Decisions（已确认）
- [x] 新仓库**完全放弃** FastAPI / Web / Docker 服务形态，只保留 skill + library + scripts
- [x] 新 skill **只服务 Agent**，不再把通用产品壳作为主目标
- [x] 市场范围继续覆盖 **A股 / 港股 / 美股** 三市场
- [x] 数据源策略继续以 **Tushare + 新闻搜索源** 为主，当前阶段暂不收缩
- [x] 旧仓库接受 **高强度删改**（大面积删除目录、重写 README/docs/tests）

## Notes
- 已有历史结论表明，这个项目此前已经在往 **Agent / skill / API 内核仓库** 方向收敛；这次不是小修，而是进一步推进到 **skill-first** 终态。
- 这是一次高风险、大范围改造，按当前 `AGENTS.md` 规则，必须先由 User 确认任务拆解与边界，再进入编码阶段。
- Phase A 蓝图已产出：`support/reports/plan/2026-04-16-daily-stock-analysis-skill-first-rewrite-blueprint.md`
- Phase B 已建立初版 skill-first 骨架：`SKILL.md`、`references/`、`src/stock_analysis_skill/`、`scripts/doctor.py`
- 合同层 canonical path 已迁到 `src.stock_analysis_skill.contracts`；当前 `src.schemas` 只保留 `AnalysisReportSchema` 导出，分析合同模型要求直接从 canonical path 导入
- `scripts/run_stock_analysis.py` 已切到 `StockAnalysisSkillService` 新服务入口；dry-run 与 doctor smoke 已通过
- 已按 `requirements-ci.txt` 在项目 `.venv` 中补装最小测试依赖：`pytest`；当前最小测试已正式通过 `pytest`
- 最小验证结果：`tests/test_stock_analysis_skill_contracts.py` + `tests/test_run_stock_analysis_entry.py` 共 5 项通过
- `scripts/run_stock_analysis.py --stock 600519` 在缺少模型配置时已验证为 **fail-fast**：当前会返回 `preflight_failed`（缺 `LITELLM_MODEL` 与 provider key），不会进入无意义执行链路
- Phase C 已补齐最小可用主链：`StockSkillAnalyzer`、`MarketSkillAnalyzer`、`StrategyResolver`、`SkillMarkdownRenderer`
- 新增 agent-facing 脚本：`scripts/run_market_analysis.py`、`scripts/resolve_strategy.py`
- 当前最小验证扩大到 13 项 pytest：contracts / stock entry / market dry-run / strategy resolution / markdown renderer 全部通过
- Phase D 第一刀已完成：删除 `api/`、`docker/`、`server.py`、`src/auth.py`，并清理一批 API / auth / system-config / portfolio 相关测试；13 项 skill 测试复跑仍全绿
- Phase D 第二刀已完成：删除 backtest / history / portfolio 的核心服务与仓储入口，清理相关测试，并从 agent factory / data tools / package exports 中移除对应入口
- Phase D 第三刀已完成：README 与 `docs/README_EN.md` 已改写为 skill-first 口径；已删除过时的 deploy / faq / full-guide / API spec / image-extract 文档
- Phase D 第四刀已完成：删除 `main.py`、`system_config_service.py`、`import_parser.py`、`image_stock_extractor.py` 及对应测试；当前 13 项 skill 测试仍全部通过
- Phase D 深层收口已完成：`AgentMemory` / `SkillAggregator` 中遗留的 backtest 自动加权逻辑已改为 neutral fallback；当前 skill + agent 侧回归扩大到 73 项 pytest，全部通过
- CHANGELOG 已补充 skill-first rewrite、主链迁移、产品壳删除、文档重写与测试覆盖条目
- 当前主线已经进入“结构完成、语义收口”的阶段；后续价值最高的工作不再是继续大删目录，而是统一命名、压缩兼容层、降低维护噪音
- Phase E.9 已完成一轮低风险收尾：先提交当前文档状态对齐，再把默认 bull-trend prompt 开关命名、env-managed LiteLLM Router 变量/日志，以及 OrchestratorStageRuntime 的重复委托层同步收口；定点回归为 `152 passed`（agent executor / analyzer prompt / agent pipeline / orchestrator runtime / registry / run script / agent model service）。
- Phase E.9.E 又补了一刀纯语义收口：task queue payload 说明、`strategies/` 资源目录口径、stage runtime 注释、以及少量 constructor/runtime shim 文案已改成当前 skill-first 语义；相关定点回归为 `65 passed`（task queue payload / orchestrator runtime / agent registry / agent model service）。
- Phase E.9.F 再补了一刀内部命名收口：`src/services/agent_model_service.py` 的 helper 命名已从 `non_legacy` / `MANAGED_LEGACY_*` 收口为更准确的 declared-router / managed-env placeholder 语义；`src/config.py` 里 `legacy_run_immediately*` 内部变量也已改为 fallback 语义，同时保持行为不变。相关定点回归为 `47 passed`（agent model service / config env compat / llm channel config / run script）。
- Phase E.9.G 继续做了一刀过时文案清理：agent memory、runner、skill loader、default skill policy、env-managed config 注释、analyzer execution 与 batch runtime fallback 说明都已从旧 legacy/compatibility 心智收口到当前 skill-first 语义；定点回归为 `83 passed`（agent memory / agent executor / agent model service / config env compat / llm channel config / run script）。
- Phase E.9.H 又补了一刀 transition wording：`src/core/config_registry.py` 的 Tushare-only / startup flag 描述、`src/search_service.py` 的 retired SearXNG 输入说明，以及 `references/data-sources.md` 的 runtime fetcher 提示已同步收口；定点回归为 `8 passed`（config registry / search searxng / agent model service）。
- Phase G 已完成真实兼容面收缩：设计冻结报告已写入 `support/reports/plan/2026-04-18-daily-stock-analysis-phase-g-compatibility-contraction-plan.md`；task queue 对外 payload 删除 `legacy_result`，保留 `result` / `runtime_payload` / `unified_response`；managed-env Router placeholder 已从 `__legacy_*` 更换为 `__managed_env_*`；配置层退役 `RUN_IMMEDIATELY` 的 schedule fallback / registry 暴露以及 `AGENT_SKILL_AUTOWEIGHT` no-op 字段。定点回归矩阵为 `84 passed`（task queue payload / config env compat / config registry / agent model service / config validate structured / llm channel config / run script），随后再次全量 `pytest` 为 **802 passed**。
- Phase H 已完成第一轮 skill 包纯化：目标冻结文档已写入 `support/reports/plan/2026-04-18-daily-stock-analysis-phase-h-skill-package-purification-plan.md`；`templates/` 下沉为 `assets/templates/`，`sources/` 下沉为 `assets/media/`，`reports/` 下沉为 `support/reports/`，`patch/` 下沉为 `support/patch/`；`README.md`、`docs/README_EN.md`、`SKILL.md` 与新增 `references/package-layout.md` 已改成 skill package surface 优先口径；定点回归为 `50 passed`，随后全量 `pytest` 为 **802 passed**。
- Phase I 已完成第一刀 provider 内迁：`data_provider/*.py` 业务实现已迁入 `src/stock_analysis_skill/providers/`，原 `data_provider/*` 收口为 compatibility shim（仍可导入）；`src/stock_analysis_skill/*` 主链已改用 provider canonical path；README/SKILL/references/docs 已同步口径为 `src.stock_analysis_skill.providers` 主路径。
- Phase E 规划口径：优先做低风险高收益项（报告输出语义 / 测试清洁 / strategy-vs-skill 统一），高风险项（把 `src/analyzer.py` / `src/core/pipeline.py` 真正内迁到 `src/stock_analysis_skill/*`）暂不纳入这一轮默认范围
- Phase E 第一批已完成：新增 `src/report_output.py` 作为首选报告输出入口，`NotificationService` 降为兼容名；`SkillResolver` 成为内部优先命名，`StrategyResolver` 作为兼容别名保留；`setup.cfg` 改为只从 `tests/` 收集 pytest，并补充 `benchmark` marker；全量回归结果为 **808 passed + 96 subtests passed**
- Phase E 第二批第一刀已完成：删除 `Config.has_searxng_enabled()` 这类无调用 compat helper；`SearchService` 默认不再隐式开启已下线的 SearXNG compat 开关；搜索能力缺失提示已收口为当前保留源（Bocha/Tavily/Brave/SerpAPI）；`src.agent.strategies.__init__` 改为直接桥接到 `src.agent.skills.*`，减少一层 legacy wrapper 跳转；本轮后全量回归仍为 **808 passed + 96 subtests passed**
- Phase E 第二批第二刀已完成：`AgentMemory` 中 `get_strategy_performance` / `compute_strategy_weights` 已改成对 `skill` 版本的别名，`SkillRouter.select_strategies` 也已改成对 `select_skills` 的别名，`src/agent/factory.py` 中单 Agent 路径的旧 `legacy single-agent` 表述已收口；相关定点验证 `112 passed + 4 subtests passed`，随后全量 pytest 仍为 **808 passed + 96 subtests passed**
- Phase E 第二批第三刀已完成：`llm_models_source` 的 env-key 路径已从 `legacy_env` 语义收口为 `managed_env`（`agent_model_service` 仍兼容识别旧值）；`Config._managed_env_keys_to_model_list()` 成为主名，旧 `_legacy_keys_to_model_list()` 保留兼容别名；`get_managed_api_keys_for_model()` / `get_managed_litellm_params()` 成为 analyzer 与 agent llm-adapter 的主用 helper，旧 `get_api_keys_for_model()` / `extra_litellm_params()` 保留兼容别名；定点验证 `98 passed`，全量 pytest 仍为 **808 passed + 96 subtests passed**
- Phase E 第二批第四刀已完成：README / `docs/README_EN.md` 的迁移状态已从 Phase D 更新到 Phase E；`src/services/__init__.py` 明确不再作为旧产品壳的全量服务总入口；`src/notification.py` 与 `src/report_output.py` 的注释已进一步强调“新代码优先走报告输出语义，notification 仅是兼容层”；`docs/CHANGELOG.md` 的 Unreleased 已补齐本轮语义收口条目。该刀仅涉及文档/注释与说明口径，已通过 `py_compile` 快速校验，无新增行为回归风险。
- 你已明确选择高风险路线「方案 1：主链内迁」。按当前规则，这一轮必须先把 Phase F 拆成单独里程碑并暂停确认，避免在未锁边界的情况下直接动 `src/analyzer.py` / `src/core/pipeline.py` / `src/services/analysis_service.py` 造成双真相源或调用链断裂。
- Phase F.1 设计冻结文档已落地：`support/reports/plan/2026-04-17-daily-stock-analysis-mainline-internalization-plan.md`。
- Phase F.2 第一刀已完成：新增 `src/stock_analysis_skill/runtime/stock_pipeline.py` 与 `runtime/__init__.py`，把同步股票分析服务编排抽到 canonical skill runtime；`StockSkillAnalyzer` 默认改为直接走 `StockAnalysisMainlineRuntime`，`AnalysisService` 已退化为 compat facade（内部转发到新 runtime），`src/stock_analysis_skill/pipeline.py` 也已切到新 runtime alias；当前 `src/core/pipeline.py` 仍保留为低层执行器，尚未退成纯壳，因此 Phase F.2 仍处于进行中。
- Phase F.2 第一刀验证结果：定点验证 `45 passed`，随后全量 `pytest` 通过 `808 passed + 96 subtests passed`。
- Phase F.2 第二刀已完成：`AnalysisService` 的历史依赖与注释已进一步收薄，当前语义已经明确为 compat facade，而不是服务层真相源；定点验证继续为 `45 passed`，全量 `pytest` 仍为 `808 passed + 96 subtests passed`。
- Phase F.2 第三刀已完成：同步编排入口 `process_single_stock/run/_save_local_report/_generate_aggregate_report` 已抽到 `src/stock_analysis_skill/runtime/pipeline_batch.py`；`src/core/pipeline.StockAnalysisPipeline` 现改为继承 `StockAnalysisBatchRuntimeMixin`，更明确地退化为“低层执行器 + compat shell”形态。该刀的定点验证为 `82 passed`，随后全量 `pytest` 仍为 `808 passed + 96 subtests passed`。
- Phase F.3 第一刀已完成：`AnalysisTaskQueue` 的真调用入口已从 `AnalysisService` 对齐到 `StockAnalysisSkillService`，但任务结果字典契约保持不变；同时补了 runtime/test-stub 兼容修复（`runtime/__init__.py` 轻量化、`task_queue.py` 对 `normalize_stock_code` 提供测试兜底、`stock_pipeline.py` 对 `data_provider` 顶层导入改为延迟兜底）。该刀的定点验证为 `48 passed`，随后全量 `pytest` 仍为 `808 passed + 96 subtests passed`。
- Phase F.3 第二刀已完成：`TaskInfo` 现在内部优先持有 `unified_result`，同时继续保留 legacy `result` dict 作为兼容字段；`TaskInfo.to_dict()` 已新增只增不破的 `unified_response` 输出字段；新增测试 `tests/test_task_queue_payload_contract.py` 覆盖这层 payload 兼容关系。该刀的定点验证为 `49 passed`，随后全量 `pytest` 为 **810 passed + 96 subtests passed**。
- Phase F.3 第三刀已完成：任务队列读取侧现在默认把 `result` 映射到 canonical payload（优先 `unified_result`，其次 legacy dict 内嵌的 `unified_response`，最后才回退到 legacy `result` 本体），同时新增 `legacy_result` 字段显式保留旧 payload；这使 task queue 的对外读取面开始向 skill-first contract 倾斜，但仍保持向后兼容。该刀的定点验证为 `32 passed`，随后全量 `pytest` 为 **810 passed + 96 subtests passed**。
- F.2/F.3 收尾阶段又补了一刀低风险空心化：`src/core/pipeline.py` 的顶部说明与类说明已收口到“低层分析执行器兼容层”，并删除了随同步编排迁出而失效的高层调度语义；针对 pipeline / skill / task queue 相关定点验证为 `59 passed`，全量 `pytest` 仍维持 **810 passed + 96 subtests passed**。
- Phase F.4 已继续推进到核心拆分第四刀：在 `_call_litellm()` 主体迁入 `src/stock_analysis_skill/analysis/litellm_caller.py` 的基础上，进一步将 `analyze()` 主循环迁入 `src/stock_analysis_skill/analysis/execution.py`；`src/analyzer.py` 中 `analyze()` 已退为 compat delegate，并通过依赖注入继续复用 `is_available/_format_prompt/_call_litellm/_parse_response/_build_market_snapshot/_check_content_integrity/_build_integrity_retry_prompt/_apply_placeholder_fill` 等既有 patch 面，保证测试与旧调用方不炸。该刀定点验证为 `45 passed`，随后全量 `pytest` 仍维持 **810 passed + 96 subtests passed**。
- Phase F.5 已完成两组契约级回归矩阵并收口：第一组覆盖同步主链 / 异步任务链 / script / skill contract / market analyzer（`57 passed`）；第二组覆盖 agent/orchestrator/skill service/script entry/renderers（`121 passed`）；其后再次全量 `pytest` 仍为 **810 passed + 96 subtests passed**。当前可视为 Phase F 已完成“内核内迁 + 契约回归”验收。
- Phase E.4 已完成多刀低风险兼容层减脂：① `src/agent/strategies/*` 已收口为 strategy-first legacy bridge，public surface 优先保留 `Strategy*`；② `src/agent/orchestrator.py` 底部与 `src/agent/orchestration/result_resolver.py` 重复的一批 dashboard/result helper 已删除，改为直接复用 resolver 实现，仅保留风险 override 相关独有 helper；③ `src/agent/skills/router.py` 已删除无人使用的 `_get_available_ids()` 死 helper；④ `src/agent/factory.py` 的 `build_executor` 从裸 alias 改为显式兼容 wrapper；⑤ `src/agent/memory.py` 的 strategy 兼容入口从裸 alias 改为显式 wrapper。当前 E.4 定点验证已覆盖 strategy compat（`59 passed`）、orchestrator/runtime/result 路径（`64 passed`）、agent/router/pipeline（`83 passed`）与 memory/factory（`51 passed`）。
- Phase E.5 已完成配置最小化审计 v2：① `GEMINI_MODEL_FALLBACK` 与 `AGENT_STRATEGY_DIR` 已从静默 fallback 改为显式 resolver + deprecation warning；② `OPENAI_API_KEYS / AIHUBMIX_KEY / OPENAI_API_KEY / OPENAI_BASE_URL` 的优先级与默认 base_url 注入逻辑已统一到同一套 runtime resolver，并补充兼容测试锁死；③ `LITELLM_CONFIG / LLM_CHANNELS / managed_env` 的加载优先级已在 runtime、registry 与 `.env.example` 对齐，并新增优先级测试；④ `REALTIME_SOURCE_PRIORITY` 与 `AGENT_SKILL_AUTOWEIGHT`/`AGENT_STRATEGY_AUTOWEIGHT` 已明确为兼容壳/no-op 并补 warning 测试，`src/core/pipeline.py` 的实时行情日志也已从“优先级”收口为“数据源”。
- Phase E.6 已完成数据/搜索兼容债清理：① `src/search_service.py` 中 retired 搜索源（Anspire / MiniMax / SearXNG）配置从 info 提升为显式 warning；② 已物理删除不再进入运行时 provider 列表的 `SearXNGSearchProvider` 实现，仅保留 `SearchService` 构造参数级 compat warning；③ `tests/test_search_searxng.py` 已收缩为 retired-provider compat 测试，不再为已下线 provider 维护整套 failover 行为测试；④ `src/config.py` 与 `.env.example` 中实时行情区域的旧多数据源说明已收紧到 tushare-only 当前口径。
- Phase E.7 文档口径清理已完成第一刀：`docs/CHANGELOG.md` 的 `[Unreleased]` 段已重写为当前 skill-first / Phase E-F / 配置与搜索兼容债收口事实，不再把旧 WebUI、Docker、Longbridge、Anspire、SearXNG 公共实例等历史条目挂在未发布主线中；`docs/CONTRIBUTING_EN.md` 的 CI Checks 已移除过时 Docker build required gate，并对齐到当前 `scripts/ci_gate.sh` 及其分阶段运行方式。
- Phase E.7 文档口径清理已完成第二刀：`README.md` 与 `docs/README_EN.md` 已显式补充“compatibility-only 残留面不是当前推荐入口”的边界说明；`docs/openclaw-skill-integration.md` 已改写为历史/兼容参考文档，不再把 `main.py --serve-only` / 长期 REST API 部署描述成当前主线接入方式；`docs/CONTRIBUTING.md` 也已与英文版同步，对齐当前 `backend-gate` 与分阶段本地运行方式。
- Phase E.8 代码层减脂已完成第一刀：删除 `Config._legacy_keys_to_model_list()` 这个已无真实调用的内部 alias，只保留 `_managed_env_keys_to_model_list()` 作为 env-managed model_list 构建入口；同时把 `validate_structured()` 内对应注释从旧 `get_api_keys_for_model` 主名更新到 `get_managed_api_keys_for_model`。
- Phase E.8 代码层减脂已完成第二刀：`src/services/agent_model_service.py` 中 `llm_models_source` 的归一逻辑已收敛为 `_normalize_models_source()` 单点入口，不再为 `legacy_env` 维持多余分支；行为保持不变——`legacy_env` 与任意未知值都会统一映射到 `managed_env`。同时新增 `tests/test_agent_model_service.py`，显式锁定这两条归一规则。
- Phase E.8 代码层减脂已完成第三刀：`src/agent/memory.py` 的 canonical API 与 compat API 测试职责已分离——主行为测试改为直接覆盖 `compute_skill_weights()`，而 `compute_strategy_weights()` / `get_strategy_performance()` 只保留薄 delegation 测试；同时在 compat wrapper docstring 中明确 canonical 入口应优先使用 `compute_skill_weights()` / `get_skill_performance()`。定点验证 `18 passed`（`test_agent_memory.py` + `test_agent_strategy_aggregator.py` + `test_agent_behavior.py`）。
- Phase E.8 代码层减脂已完成第四刀：`src/agent/skills/aggregator.py` 中 `StrategyAggregator` 已从裸 alias 改为显式兼容 wrapper class，canonical 主名仍为 `SkillAggregator`；`tests/test_agent_strategy_aggregator.py` 的主行为覆盖已切到 `SkillAggregator`，旧 `src.agent.strategies.aggregator.StrategyAggregator` 导入路径仅保留 wrapper 兼容测试。定点验证 `17 passed`（`test_agent_strategy_aggregator.py` + `test_skill_load_warning.py` + `test_agent_orchestrator_runtime.py`）。
- Phase E.8 代码层减脂已完成第五刀：`src/agent/strategies/aggregator.py` 的反向 `SkillAggregator = StrategyAggregator` 裸 alias 已收口为 `__getattr__` 兼容导出；旧 `from src.agent.strategies.aggregator import SkillAggregator` 仍可用，但现在会显式返回 canonical 的 `src.agent.skills.aggregator.SkillAggregator`。同时补了兼容测试锁定这条映射。定点验证 `18 passed`（`test_agent_strategy_aggregator.py` + `test_agent_orchestrator_runtime.py` + `test_skill_load_warning.py`）。
- Phase E.8 代码层减脂已完成第六刀：`src/agent/strategies/router.py` 与 `src/agent/strategies/strategy_agent.py` 的反向 `SkillRouter` / `SkillAgent` 以及 `_DEFAULT_SKILLS` 裸 alias 已统一收口为 `__getattr__` 兼容导出；旧 `from src.agent.strategies.* import Skill*` 仍可用，但现在会显式返回 canonical 的 `src.agent.skills.*` 对象。新增 `tests/test_agent_strategy_agent_compat.py`，并在 `tests/test_agent_strategy_router.py` 中补兼容测试锁定这些映射。定点验证 `70 passed`（`test_agent_strategy_router.py` + `test_agent_strategy_agent_compat.py` + `test_agent_orchestrator_runtime.py` + `test_agent_registry.py`）。
- Phase E.8 代码层减脂已完成第七刀（delete-first 版）：已物理删除 `src/agent/strategies/*` 整个 legacy package，不再继续维护 `Strategy*` ↔ `Skill*` 双向 compat bridge；`src/agent/skills/aggregator.py` / `router.py` / `skill_agent.py` 里对应的 `StrategyAggregator` / `StrategyRouter` / `StrategyAgent` 兼容名也一并删除，仅保留 canonical 的 `Skill*` 主名与 `_DEFAULT_SKILLS`。同时删除无真实调用的 `src/config.py:get_api_keys_for_model()` / `extra_litellm_params()` 两个旧 helper，并把旧 `strategy_*` 测试收口为 canonical `skills.*` 行为测试、删除纯 compat 测试文件。定点验证 `127 passed`（`test_agent_strategy_aggregator.py` + `test_agent_strategy_router.py` + `test_agent_memory.py` + `test_agent_orchestrator_runtime.py` + `test_agent_registry.py` + `test_agent_model_service.py` + `test_llm_channel_config.py` + `test_config_env_compat.py` + `test_run_stock_analysis_script.py`）。
- Phase E.8 代码层减脂已完成第八刀（delete-first 继续）：删除 `src/agent/memory.py` 中仅用于 legacy strategy 命名的 `get_strategy_performance()` / `compute_strategy_weights()`，`get_calibration()` 移除 `strategy_id` 入参，仅保留 `skill_id`；`src/agent/skills/skill_agent.py` 移除 `strategy_id` 兼容构造参数，改为强制 `skill_id`；`src/stock_analysis_skill/service.py` 移除 `strategy_resolver` 兼容属性，仅保留 `skill_resolver`。同时移除对应 legacy 测试断言并保持 canonical 行为测试。定点验证 `77 passed`（`test_agent_memory.py` + `test_agent_orchestrator_runtime.py` + `test_agent_registry.py` + `test_stock_analysis_skill_market_strategy.py` + `test_run_stock_analysis_script.py`）。
- Phase E.8 代码层减脂已完成第九刀（delete-first 继续）：移除 `src/services/analysis_service.py` 兼容层及其测试 `tests/test_analysis_service_unified_bridge.py`；`src/stock_analysis_skill/analyzers/stock.py` 不再依赖 `AnalysisService`，统一直连 `StockAnalysisMainlineRuntime`；`src/stock_analysis_skill/service.py` 构造签名同步去掉 `analysis_service` 注入；`src/services/__init__.py` 去除 `AnalysisService` 懒加载导出。定点验证 `123 passed`（`test_stock_analysis_skill_market_strategy.py` + `test_run_stock_analysis_script.py` + `test_agent_orchestrator_runtime.py` + `test_agent_registry.py` + `test_agent_memory.py` + `test_analysis_context_service.py` + `test_agent_pipeline.py`）。
- Phase E.8 代码层减脂已完成第十刀（delete-first 继续）：`src/core/pipeline.py` 不再提供 `NotificationService`/`report_service`/`notifier` 兼容属性，统一使用 `report_output_service`；`src/stock_analysis_skill/runtime/pipeline_batch.py` 去掉对 `report_service/notifier` 的回退，改为只依赖 `report_output_service`；对应 pipeline/agent/market/event 测试全部切到 `ReportOutputService` 与 `report_output_service` 主语义。定点验证 `66 passed`（`test_pipeline_notification_image_routing.py` + `test_pipeline_single_notify_thread_safety.py` + `test_pipeline_single_stock_notify.py` + `test_pipeline_optional_service_resilience.py` + `test_agent_pipeline.py` + `test_market_review.py` + `test_agent_events.py`）。
- Phase E.8 代码层减脂已完成第十一刀（delete-first 继续）：`src/notification.py` 里旧 `NotificationService` 主名与 `get_notification_service()` 已移除，统一以 `ReportOutputService` 作为唯一服务类；`src/report_output.py` 同步去掉 `NotificationService` 再导出；`tests/test_notification.py` / `tests/test_notification_sender.py` 全量改为 `ReportOutputService` 断言；`tests/test_agent_events.py` 去掉对 `src.notification.NotificationService` 的无效 patch（事件监控构建已不依赖通知对象）。定点验证 `71 passed`（`test_notification.py` + `test_notification_sender.py` + `test_agent_events.py` + `test_pipeline_notification_image_routing.py` + `test_pipeline_optional_service_resilience.py` + `test_pipeline_single_notify_thread_safety.py` + `test_pipeline_single_stock_notify.py` + `test_agent_pipeline.py` + `test_market_review.py`）。
- Phase E.8 代码层减脂已完成第十二刀（delete-first 继续）：移除 `src/schemas/analysis_contract.py` compat re-export，`src/services/analysis_context_service.py`、`scripts/build_analysis_context.py` 及相关测试统一改为直接引用 `src.stock_analysis_skill.contracts`；`src/schemas/__init__.py` 同步改为从 canonical contracts 直接导出；`tests/test_stock_analysis_skill_contracts.py` 去掉 legacy import 兼容断言。定点验证 `19 passed`（`test_analysis_contract_models.py` + `test_analysis_context_service.py` + `test_run_stock_analysis_script.py` + `test_stock_analysis_skill_contracts.py` + `test_task_queue_payload_contract.py` + `test_stock_analysis_skill_market_strategy.py`）。
- Phase E.8 代码层减脂已完成第十三刀（delete-first 继续）：`src/schemas/__init__.py` 不再继续二次 re-export 分析合同模型，收口为仅导出 `AnalysisReportSchema`；分析请求/响应模型统一要求直接从 `src.stock_analysis_skill.contracts` 导入，避免 `src.schemas` 继续承担 compat 聚合入口。定点验证 `26 passed`（`test_report_schema.py` + `test_analysis_contract_models.py` + `test_analysis_context_service.py` + `test_run_stock_analysis_script.py` + `test_stock_analysis_skill_contracts.py` + `test_task_queue_payload_contract.py` + `test_stock_analysis_skill_market_strategy.py`）。
- Phase E.8 代码层减脂已完成第十四刀（delete-first 继续）：`src/services/name_to_code_resolver.py` 删除 `_is_code_like` / `_normalize_code` 两个仅历史兼容意义的内部 wrapper，直接调用 `src.services.stock_code_utils` 的 canonical 工具函数；`tests/test_name_to_code_resolver.py` 同步从 wrapper 断言切换为直接校验 `is_code_like` / `normalize_code` 行为，保持解析主链断言不变。定点验证 `22 passed`（`test_name_to_code_resolver.py` + `test_search_performance.py`）。
- Phase E.8 代码层减脂已完成第十五刀（delete-first 继续）：`src/stock_analysis_skill/runtime/stock_pipeline.py` 去掉 `LegacyStockAnalysisPipeline` 命名兼容 alias，统一改为直接引用 `StockAnalysisPipeline`（包括 `StockAnalysisSkillPipeline` 的继承基类）；运行中发现并修复一处遗漏基类引用（见 `.learnings/ERRORS.md` 的 `ERR-20260417-005`）。定点验证 `55 passed`（`test_task_queue_payload_contract.py` + `test_stock_analysis_skill_market_strategy.py` + `test_run_stock_analysis_script.py` + `test_agent_pipeline.py`）。
- Phase E.8 代码层减脂已完成第十六刀（delete-first 继续）：物理删除零引用的 compat 入口 `src/stock_analysis_skill/pipeline.py`，并从 `src/stock_analysis_skill/runtime/stock_pipeline.py` 删除无实际调用的 `StockAnalysisSkillPipeline` alias class，仅保留 `StockAnalysisMainlineRuntime` 与 `StockAnalysisPipeline` 主路径。定点验证 `55 passed`（`test_task_queue_payload_contract.py` + `test_stock_analysis_skill_market_strategy.py` + `test_run_stock_analysis_script.py` + `test_agent_pipeline.py`）。
- Phase E.8 代码层减脂已完成第十七刀（delete-first 继续）：`src/stock_analysis_skill/analyzers/strategy.py` 删除零引用的 `StrategyResolver = SkillResolver` compat alias，仅保留 `SkillResolver` 作为 canonical resolver 类；对应策略解析与脚本链路回归通过。定点验证 `11 passed`（`test_stock_analysis_skill_market_strategy.py` + `test_run_stock_analysis_script.py` + `test_task_queue_payload_contract.py`）。
- Phase E.8 代码层减脂已完成第十八刀（delete-first 继续）：`scripts/run_stock_analysis.py` 删除仅用于旧测试/旧调用方的 `_resolve_report_type` compat helper，主流程直接调用 `resolve_report_type(request.mode)`；`tests/test_run_stock_analysis_script.py` 同步改为直接验证 `src.stock_analysis_skill.service.resolve_report_type`。定点验证 `11 passed`（`test_run_stock_analysis_script.py` + `test_stock_analysis_skill_market_strategy.py` + `test_task_queue_payload_contract.py`）。
- Phase E.8 代码层减脂已完成第十九刀（delete-first 继续）：`src/agent/skills/router.py` 删除 strategy 命名兼容方法 `select_strategies`，统一只保留 `select_skills`；`tests/test_agent_strategy_router.py` 同步改用 canonical 方法名。定点验证 `68 passed`（`test_agent_strategy_router.py` + `test_agent_orchestrator_runtime.py` + `test_agent_registry.py`）。
- Phase E.8 代码层减脂已完成第二十刀（delete-first 继续）：Agent 上下文元数据中移除 strategy 命名兼容键——`src/agent/orchestrator.py` 不再写入 `strategies_requested` / `context.strategies`，`src/agent/skills/router.py` 与 `src/agent/agents/decision_agent.py` 不再读取 `strategies_requested`，统一仅使用 `skills_requested` / `context.skills`；`tests/test_agent_strategy_router.py` 同步切到 `skills_requested`。定点验证 `118 passed`（`test_agent_strategy_router.py` + `test_agent_orchestrator_runtime.py` + `test_agent_registry.py` + `test_agent_behavior.py` + `test_agent_pipeline.py`）。
- Phase E.8 代码层减脂已完成第二十一刀（delete-first 继续）：`src/agent/orchestrator.py` 删除零引用的 legacy compat wrapper 方法 `_build_skill_agents` / `_build_strategy_agents` / `_aggregate_strategy_opinions`，统一仅保留 `build_specialist_agents` 与 `aggregate_skill_opinions` 主路径。定点验证 `112 passed`（`test_agent_orchestrator_runtime.py` + `test_agent_strategy_router.py` + `test_agent_registry.py` + `test_agent_pipeline.py`）。
- Phase E.8 代码层减脂已完成第二十二刀（delete-first 继续）：`src/agent/skills/base.py` 删除 `load_builtin_strategies` / `load_custom_strategies` 兼容方法，统一仅保留 canonical 的 `load_builtin_skills` / `load_custom_skills`；`src/agent/factory.py` 删除零引用的 `build_executor` compat 入口；相关回归测试同步改到 canonical API（`tests/test_agent_registry.py`、`tests/test_agent_pipeline.py`）。定点验证 `111 passed`（`test_agent_registry.py` + `test_agent_pipeline.py` + `test_agent_orchestrator_runtime.py` + `test_agent_behavior.py`）。
- Phase E.8 代码层减脂已完成第二十三刀（delete-first 继续）：移除 skill 名称解析链路对 `strategy_*` / `strategy_consensus` 的兼容识别，`src/agent/skills/defaults.py` 中 `extract_skill_id` 与 `is_skill_consensus_name` 统一只认 `skill_*` / `skill_consensus`；`src/agent/orchestration/result_resolver.py` 的 base-opinion 优先组去掉 `strategy_consensus`；对应 agent 回归测试中的历史 `strategy_*` agent_name 全量切换为 canonical `skill_*`（`test_agent_strategy_aggregator.py`、`test_agent_orchestrator_runtime.py`、`test_agent_orchestrator_results.py`、`test_agent_memory.py`）。定点验证 `122 passed`（`test_agent_strategy_aggregator.py` + `test_agent_orchestrator_runtime.py` + `test_agent_orchestrator_results.py` + `test_agent_memory.py` + `test_agent_pipeline.py` + `test_agent_registry.py`）。
- Phase E.8 代码层减脂已完成第二十四刀（delete-first 继续）：`src/agent/memory.py` 删除零引用的 `get_skill_performance` 兼容接口；`src/agent/skills/defaults.py` 删除零引用的 `is_skill_consensus_name` helper；`src/agent/skills/aggregator.py` 去掉仅返回 `1.0` 的 `_compatibility_factor` 空壳并将权重计算直接归一到 `confidence/perf_weight`。定点验证 `115 passed`（`test_agent_memory.py` + `test_agent_strategy_aggregator.py` + `test_agent_orchestrator_runtime.py` + `test_agent_registry.py` + `test_agent_pipeline.py`）。
- Phase E.8 代码层减脂已完成第二十五刀（delete-first 继续）：`src/agent/executor.py` 移除历史上下文里的 `previous_strategy` 注入分支，仅保留 `previous_analysis_summary` 等 canonical 上下文字段；`src/agent/runner.py` 删除零引用的 `get_strategy_backtest_summary` 进度文案映射。定点验证 `111 passed`（`test_agent_pipeline.py` + `test_agent_behavior.py` + `test_agent_orchestrator_runtime.py` + `test_agent_registry.py`）。
- Phase E.8 代码层减脂已完成第二十六刀（delete-first 继续）：`src/agent/skills/defaults.py` 删除零引用的 `_build_regime_skill_ids` 与 `REGIME_SKILL_IDS` 预计算常量（全仓库已无引用），保留 `get_regime_skill_ids(...)` 运行时解析作为唯一 regime 路由入口。定点验证 `118 passed`（`test_agent_registry.py` + `test_agent_strategy_router.py` + `test_agent_pipeline.py` + `test_agent_orchestrator_runtime.py` + `test_agent_behavior.py`）。
- Phase E.8 代码层减脂已完成第二十七刀（delete-first 继续）：删除 `src/agent/skills/defaults.py` 中零引用的预计算导出常量 `DEFAULT_ACTIVE_SKILL_IDS` / `DEFAULT_ROUTER_SKILL_IDS` / `PRIMARY_DEFAULT_SKILL_ID`，并在 `src/agent/skills/__init__.py` 去掉对应 re-export，只保留运行时 helper 函数导出。定点验证 `118 passed`（`test_agent_registry.py` + `test_agent_strategy_router.py` + `test_agent_pipeline.py` + `test_agent_orchestrator_runtime.py` + `test_agent_behavior.py`）。
- Phase E.8 代码层减脂已完成第二十八刀（delete-first 继续）：删除 `src/agent/skills/defaults.py` 中零引用 helper `get_primary_default_skill_id`，并在 `src/agent/skills/__init__.py` 去掉对应导出；`tests/test_agent_registry.py` 的默认技能断言改为使用 `get_default_active_skill_ids(..., max_count=1)` 验证同等语义。定点验证 `118 passed`（`test_agent_registry.py` + `test_agent_strategy_router.py` + `test_agent_pipeline.py` + `test_agent_orchestrator_runtime.py` + `test_agent_behavior.py`）。
- Phase E.8 代码层减脂已完成第二十九刀（delete-first 继续）：`src/agent/skills/router.py` 删除零引用常量 `_DEFAULT_SKILLS`；`tests/test_agent_strategy_router.py` 不再依赖该内部常量，改为断言手工模式下从可用技能列表解析出的默认结果（`bull_trend` / `shrink_pullback`）。定点验证 `118 passed`（`test_agent_strategy_router.py` + `test_agent_orchestrator_runtime.py` + `test_agent_registry.py` + `test_agent_pipeline.py` + `test_agent_behavior.py`）。
- Phase E.8 代码层减脂已完成第三十刀（delete-first 继续）：`src/agent/memory.py` 删除零引用常量 `_ROLLING_WINDOW` 与零引用内部函数 `_get_accuracy_stats`，`get_calibration` 收口为当前真实行为（memory enabled 时仍返回中性校准，等待后续新证据源）。定点验证 `115 passed`（`test_agent_memory.py` + `test_agent_strategy_aggregator.py` + `test_agent_orchestrator_runtime.py` + `test_agent_pipeline.py` + `test_agent_registry.py`）。
- Phase E.8 代码层减脂已完成第三十一刀（delete-first 继续）：`src/agent/skills/aggregator.py` 删除零引用常量 `_MIN_BACKTEST_SAMPLES`，并去掉 `aggregate/_compute_weight` 中已无业务意义的 `min_samples` 参数，权重计算接口收口为当前实际使用的 `confidence + perf_weight` 路径。定点验证 `115 passed`（`test_agent_strategy_aggregator.py` + `test_agent_orchestrator_runtime.py` + `test_agent_orchestrator_results.py` + `test_agent_pipeline.py` + `test_agent_registry.py`）。
- Phase E.8 代码层减脂已完成第三十二刀（delete-first 继续）：`src/agent/runner.py` 删除零引用的回测工具进度文案映射 `get_skill_backtest_summary` / `get_stock_backtest_summary`，保留当前真实可调用工具标签集。定点验证 `140 passed`（`test_agent_executor.py` + `test_agent_pipeline.py` + `test_agent_behavior.py` + `test_agent_orchestrator_runtime.py` + `test_agent_registry.py`）。
- Phase E.8 代码层减脂已完成第三十三刀（delete-first 继续）：`src/agent/memory.py` 删除零引用常量 `_MIN_CALIBRATION_SAMPLES` 以及无实际作用的构造参数 `min_samples`（`AgentMemory` 当前校准逻辑已固定为中性返回），构造签名收口为 `AgentMemory(enabled=False)`。定点验证 `115 passed`（`test_agent_memory.py` + `test_agent_strategy_aggregator.py` + `test_agent_orchestrator_runtime.py` + `test_agent_pipeline.py` + `test_agent_registry.py`）。
- Phase E.8 代码层减脂已完成第三十四刀（delete-first 继续）：进入主线收口的 2/3 类问题同步处理——`src/services/task_queue.py` 内部变量/注释从 `legacy_result` 语义统一收口为 `runtime_payload`（对外 `legacy_result` 字段保留兼容，不破契约）；`src/stock_analysis_skill/service.py` 与 `src/stock_analysis_skill/analyzers/stock.py` 的 `MODE_TO_REPORT_TYPE` 语义统一更名为 `MODE_TO_PIPELINE_REPORT_TYPE`；`src/stock_analysis_skill/runtime/stock_pipeline.py` 的 `build_legacy_analysis_response` 与 `legacy_response` 命名同步收口为 `build_runtime_payload` / `runtime_payload`。定点验证 `65 passed`（`test_task_queue_payload_contract.py` + `test_task_queue_config_sync.py` + `test_stock_analysis_skill_contracts.py` + `test_stock_analysis_skill_market_strategy.py` + `test_stock_analysis_skill_renderers.py` + `test_run_stock_analysis_script.py` + `test_agent_pipeline.py`）。
- Phase E.8 代码层减脂已完成第三十五刀（delete-first 继续）：完成你要求的 1) 低风险语义收口：`src/stock_analysis_skill/__init__.py`、`src/stock_analysis_skill/analyzers/market.py`、`src/stock_analysis_skill/runtime/pipeline_batch.py`、`src/agent/executor.py` 的 legacy 说明文案已改为当前 runtime/canonical 口径，且不改业务逻辑。定点验证 `137 passed`（`test_stock_analysis_skill_market_strategy.py` + `test_agent_executor.py` + `test_agent_pipeline.py` + `test_agent_registry.py` + `test_agent_behavior.py` + `test_task_queue_payload_contract.py`）。
- Phase E.8 代码层减脂已完成第三十六刀（delete-first 继续）：按你要求把 1/2/3 同步做完并收口——1) `src/services/task_queue.py` 在响应字典中新增 canonical 别名 `runtime_payload`，保留 `legacy_result` 仅作兼容；2) `src/core/config_registry.py` 把 Agent 配置标题/描述从 strategy 口径统一到 skill 口径（`Agent Skills` / `Agent Skill Dir`）；3) `src/config.py` 完成 deprecated alias 最终收口：`AGENT_STRATEGY_DIR`、`AGENT_STRATEGY_AUTOWEIGHT`、`GEMINI_MODEL_FALLBACK` 改为 retired+ignored（仅告警，不再参与运行时解析），并同步更新 `tests/test_config_env_compat.py` 与 `tests/test_task_queue_payload_contract.py` 契约断言。定点验证 `134 passed`（`test_config_env_compat.py` + `test_task_queue_payload_contract.py` + `test_task_queue_config_sync.py` + `test_agent_pipeline.py` + `test_agent_registry.py` + `test_agent_behavior.py` + `test_run_stock_analysis_script.py`）。
