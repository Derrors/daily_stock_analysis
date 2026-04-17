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
- [-] Phase E.4 Agent 兼容层审计：盘点 `src/agent/*` 中的 legacy/compat wrapper，删无用、聚合有用兼容层
- [-] Phase E.5 配置最小化审计 v2：继续盘 `src/config.py` 里仅为旧入口保留的 LLM / runtime fallback 逻辑
- [-] Phase E.6 数据/搜索兼容债清理：继续抽离已下线 provider 的 compat 语义，收紧主路径说明

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
