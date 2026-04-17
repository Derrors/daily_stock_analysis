# openclaw Skill 集成说明（历史 / compatibility-only）

> **重要说明**
>
> 本文档保留为**历史兼容参考**，不是 `daily_stock_analysis` 当前主线仓库的推荐接入方式。
>
> 当前仓库已经收敛为 **Agent-first / skill-first** 代码库，推荐入口是：
> - `scripts/run_stock_analysis.py`
> - `scripts/run_market_analysis.py`
> - `scripts/resolve_strategy.py`
> - `src.stock_analysis_skill.*`
>
> 仓库主线**不再把长期运行的 REST API / Web / Docker 产品壳**作为推荐目标形态。因此，过去基于 `main.py --serve-only`、长期暴露 `/api/...` 接口、再由 openclaw 通过 HTTP 调用的方案，应视为**旧架构或自维护兼容层**，而不是当前默认路径。

## 这份文档适用于谁

仅适用于以下场景：

1. 你手里已经有一套**旧版或自维护 fork**，仍然暴露 HTTP API；
2. 你明确打算在仓库外层自己维护一层 compatibility service，再让 openclaw 通过 HTTP 调用；
3. 你需要理解历史集成思路，以便迁移老系统。

如果你是在**当前主线仓库上做新接入**，请不要再把 HTTP API 作为第一选择。

## 当前推荐接入方式

### 方案 A：脚本入口（推荐）

让 openclaw Skill 直接调用仓库脚本，而不是先起一个长期运行的 API 服务。

推荐脚本：

- `scripts/run_stock_analysis.py`
- `scripts/run_market_analysis.py`
- `scripts/resolve_strategy.py`
- `scripts/doctor.py`

适用特点：

- 更贴近当前仓库主线
- 不需要额外维护 API 契约与服务进程
- 更适合 Agent / Skill / 本地自动化工作流

### 方案 B：直接 import canonical modules（推荐）

如果你的运行环境允许 Python 级集成，优先使用：

- `src.stock_analysis_skill.contracts`
- `src.stock_analysis_skill.service`
- `src.stock_analysis_skill.analyzers.stock`
- `src.stock_analysis_skill.analyzers.market`
- `src.stock_analysis_skill.analyzers.strategy`
- `src.stock_analysis_skill.renderers.markdown`

适用特点：

- 契约更稳定
- 不需要额外 HTTP 层
- 更适合后续继续跟随 skill-first 主线演进

## 历史 HTTP 集成方案的现状

过去的思路是：

- 启动 `daily_stock_analysis` 的 API 服务
- 由 openclaw Skill 通过 HTTP 请求 `/api/...` 端点
- 在对话中触发股票分析

这条路径现在有几个问题：

1. **不再是当前主线推荐形态**：仓库已从产品壳系统收敛为 skill/library/scripts。
2. **历史接口文档可能失真**：旧接口、旧 payload、旧部署方式不再保证与当前主线同步演进。
3. **维护成本更高**：你需要自己维护进程、部署、鉴权、超时、接口兼容与错误处理。

因此，如果你仍使用 HTTP 集成，请把它视为**自维护兼容层**。

## 若你必须继续用 HTTP 集成

请按下面原则处理，而不是依赖旧文档里的具体接口细节：

1. **先核实你的 fork / 服务实际暴露了哪些端点**；
2. **以你当前部署代码为准**，不要默认历史 `/api/v1/analysis/analyze`、`/api/v1/agent/chat` 等契约仍与主线一致；
3. **把 API 契约文档内收**到你的兼容层仓库或部署文档里；
4. **把 openclaw Skill 当成 HTTP 客户端**，不要再假设主仓库会持续为该方案优化。

## 迁移建议

如果你手里已有旧的 HTTP Skill：

### 迁移方向 1：HTTP → 脚本调用

把 Skill 的执行逻辑改成直接调用：

- `python scripts/run_stock_analysis.py ...`
- `python scripts/run_market_analysis.py ...`
- `python scripts/resolve_strategy.py ...`

### 迁移方向 2：HTTP → Python import

如果 Skill 运行环境就是 Python 工程环境，改为直接复用 `src.stock_analysis_skill.*` 的 contracts / service / analyzers / renderers。

### 迁移方向 3：保留 HTTP，但明确自维护

如果你必须保留 HTTP：

- 在仓库外层维护你的 compat service
- 固定自己的 API 契约版本
- 不再把本仓库 README / docs 视为该接口的权威文档

## 总结

一句话：

- **当前主线推荐**：脚本入口 + canonical Python modules
- **历史兼容方案**：自维护 HTTP / API service
- **不要再把本文件理解为当前默认接入手册**
