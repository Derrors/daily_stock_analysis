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

## Key Design Decisions（已确认）
- [x] 新仓库**完全放弃** FastAPI / Web / Docker 服务形态，只保留 skill + library + scripts
- [x] 新 skill **只服务 Agent**，不再把通用产品壳作为主目标
- [x] 市场范围继续覆盖 **A股 / 港股 / 美股** 三市场
- [x] 数据源策略继续以 **Tushare + 新闻搜索源** 为主，当前阶段暂不收缩
- [x] 旧仓库接受 **高强度删改**（大面积删除目录、重写 README/docs/tests）

## Notes
- 已有历史结论表明，这个项目此前已经在往 **Agent / skill / API 内核仓库** 方向收敛；这次不是小修，而是进一步推进到 **skill-first** 终态。
- 这是一次高风险、大范围改造，按当前 `AGENTS.md` 规则，必须先由 User 确认任务拆解与边界，再进入编码阶段。
- Phase A 蓝图已产出：`reports/plan/2026-04-16-daily-stock-analysis-skill-first-rewrite-blueprint.md`
- Phase B 已建立初版 skill-first 骨架：`SKILL.md`、`references/`、`src/stock_analysis_skill/`、`scripts/doctor.py`
- 合同层 canonical path 已迁到 `src.stock_analysis_skill.contracts`，旧 `src.schemas.analysis_contract` 保留兼容 re-export
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
- Phase E 规划口径：优先做低风险高收益项（报告输出语义 / 测试清洁 / strategy-vs-skill 统一），高风险项（把 `src/analyzer.py` / `src/core/pipeline.py` 真正内迁到 `src/stock_analysis_skill/*`）暂不纳入这一轮默认范围
- Phase E 第一批已完成：新增 `src/report_output.py` 作为首选报告输出入口，`NotificationService` 降为兼容名；`SkillResolver` 成为内部优先命名，`StrategyResolver` 作为兼容别名保留；`setup.cfg` 改为只从 `tests/` 收集 pytest，并补充 `benchmark` marker；全量回归结果为 **808 passed + 96 subtests passed**
- Phase E 第二批第一刀已完成：删除 `Config.has_searxng_enabled()` 这类无调用 compat helper；`SearchService` 默认不再隐式开启已下线的 SearXNG compat 开关；搜索能力缺失提示已收口为当前保留源（Bocha/Tavily/Brave/SerpAPI）；`src.agent.strategies.__init__` 改为直接桥接到 `src.agent.skills.*`，减少一层 legacy wrapper 跳转；本轮后全量回归仍为 **808 passed + 96 subtests passed**
- Phase E 第二批第二刀已完成：`AgentMemory` 中 `get_strategy_performance` / `compute_strategy_weights` 已改成对 `skill` 版本的别名，`SkillRouter.select_strategies` 也已改成对 `select_skills` 的别名，`src/agent/factory.py` 中单 Agent 路径的旧 `legacy single-agent` 表述已收口；相关定点验证 `112 passed + 4 subtests passed`，随后全量 pytest 仍为 **808 passed + 96 subtests passed**
- Phase E 第二批第三刀已完成：`llm_models_source` 的 env-key 路径已从 `legacy_env` 语义收口为 `managed_env`（`agent_model_service` 仍兼容识别旧值）；`Config._managed_env_keys_to_model_list()` 成为主名，旧 `_legacy_keys_to_model_list()` 保留兼容别名；`get_managed_api_keys_for_model()` / `get_managed_litellm_params()` 成为 analyzer 与 agent llm-adapter 的主用 helper，旧 `get_api_keys_for_model()` / `extra_litellm_params()` 保留兼容别名；定点验证 `98 passed`，全量 pytest 仍为 **808 passed + 96 subtests passed**
- Phase E 第二批第四刀已完成：README / `docs/README_EN.md` 的迁移状态已从 Phase D 更新到 Phase E；`src/services/__init__.py` 明确不再作为旧产品壳的全量服务总入口；`src/notification.py` 与 `src/report_output.py` 的注释已进一步强调“新代码优先走报告输出语义，notification 仅是兼容层”；`docs/CHANGELOG.md` 的 Unreleased 已补齐本轮语义收口条目。该刀仅涉及文档/注释与说明口径，已通过 `py_compile` 快速校验，无新增行为回归风险。
- 你已明确选择高风险路线「方案 1：主链内迁」。按当前规则，这一轮必须先把 Phase F 拆成单独里程碑并暂停确认，避免在未锁边界的情况下直接动 `src/analyzer.py` / `src/core/pipeline.py` / `src/services/analysis_service.py` 造成双真相源或调用链断裂。
- Phase F.1 设计冻结文档已落地：`reports/plan/2026-04-17-daily-stock-analysis-mainline-internalization-plan.md`。
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
