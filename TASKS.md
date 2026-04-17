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
- 当前 diff 规模约为 96 个已跟踪文件变更（含大量删除），另有 `SKILL.md`、`references/`、`src/stock_analysis_skill/`、新脚本与新测试等未跟踪新增文件
