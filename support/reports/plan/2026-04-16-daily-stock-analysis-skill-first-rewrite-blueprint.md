# daily_stock_analysis skill-first rewrite blueprint

日期：2026-04-16

## 1. 目标

将 `daily_stock_analysis` 从当前 **agent-first backend core / API 仓库**，进一步重构为 **只服务 Agent 的 stock-analysis skill-first 仓库**。

重构后的仓库核心职责：
- 接收 Agent 发起的股票分析 / 市场分析 / 策略分析请求
- 组装必要上下文（行情、新闻、市场、策略）
- 调用统一分析主链
- 产出结构化结果与 Markdown/summary 等适合 Agent 消费的输出
- 通过 `SKILL.md + scripts + references` 直接为 Agent 提供可复用能力

明确不再作为仓库核心的能力：
- FastAPI 服务
- Web UI / Desktop 产品壳
- 登录认证 / 系统配置页面 / 使用量统计页面
- 多渠道通知投递壳
- Docker 部署与产品化运行包装

## 2. 已确认边界

- **完全放弃** FastAPI / Web / Docker 服务形态，只保留 `skill + library + scripts`
- **只服务 Agent**，不再以通用产品壳为目标
- 继续覆盖 **A股 / 港股 / 美股**
- 数据源继续以 **Tushare + 新闻搜索源** 为主，当前阶段暂不收缩
- 接受 **高强度删改**：允许大面积删除旧目录、重写 README/docs/tests

## 3. 当前仓库诊断

### 3.1 当前最有价值、可迁移的核心

1. **统一合同模型**
   - `src/schemas/analysis_contract.py`
   - 已具备 skill-first 方向最关键的 request/response 语义基础

2. **脚本化入口雏形**
   - `scripts/run_stock_analysis.py`
   - 已经是“未来 skill 可执行入口”的第一块砖

3. **分析主链骨架**
   - `src/services/analysis_service.py`
   - `src/core/pipeline.py`
   - `src/services/analysis_context_service.py`
   - 当前同步主链口径已经比较清晰：`AnalysisService -> StockAnalysisPipeline`

4. **数据获取层**
   - `data_provider/`
   - 当前已收敛为 **Tushare-only runtime**，适合作为新 skill 的市场数据入口基础

5. **策略资源**
   - `strategies/*.yaml`
   - 这些 YAML 策略文件天然适合保留为 skill 资源或转成 references/assets

6. **报告渲染能力**
   - `src/services/report_renderer.py`
   - `templates/*.j2`
   - 可保留“能力”，但需改写为面向 Agent 输出，而非面向产品 UI/通知模板

### 3.2 当前明显偏离新目标的部分

1. **API 产品层**
   - `api/`
   - `server.py`
   - 这是旧产品壳，不属于 skill-first 终态

2. **部署包装**
   - `docker/`
   - 与新目标不再匹配

3. **Web / auth / system-config / usage / history 等产品管理能力**
   - 相关 endpoint、middleware、system config service
   - 这些都是产品壳能力，不是 Agent skill 核心

4. **回测 / 组合管理 / 导入 / 图片识别 / 持仓管理等外围模块**
   - 其中少量能力可作为未来扩展，但不应进入第一版 skill 核心主链

5. **测试体系过重，且大量围绕旧 API / 产品壳**
   - 当前 `tests/` 数量很大，需按新形态重建验证矩阵

## 4. 模块处置建议

## 4.1 保留并重写（核心）

- `src/schemas/analysis_contract.py`
  - 继续保留，作为新 skill 的统一合同基础
- `scripts/run_stock_analysis.py`
  - 保留，但重写为新 skill 官方执行入口
- `src/services/analysis_service.py`
  - 保留语义，重写实现，去除对 API / 历史存储 / 产品壳的依赖
- `src/core/pipeline.py`
  - 保留语义，收敛为纯分析编排主链
- `src/services/analysis_context_service.py`
  - 保留，继续作为上下文组装服务
- `src/core/market_review.py`
  - 保留并重写为市场分析主链的一部分
- `src/core/market_strategy.py`
  - 保留并收敛到策略输出层
- `data_provider/`
  - 保留，重写接口边界，使之只服务新 skill 主链
- `strategies/`
  - 保留，作为策略能力资源层
- `src/services/report_renderer.py` + `templates/`
  - 保留能力，重写输出目标

## 4.2 删除（第一版 skill 不保留）

- `api/`
- `server.py`
- `docker/`
- `src/auth.py`
- `src/services/system_config_service.py`
- `src/services/history_service.py`
- `src/services/backtest_service.py`
- `src/services/portfolio_*`
- `src/services/import_parser.py`
- `src/services/image_stock_extractor.py`
- `src/services/social_sentiment_service.py`（若仍强绑定旧产品链路，则先删，后续按独立插件重加）
- 旧 Web / auth / usage / history / backtest / portfolio 对应测试
- 旧产品导向文档（README、full-guide、DEPLOY、FAQ 中相关内容）

## 4.3 暂存观察 / 迁移参考

- `src/agent/`
  - 需要区分“对外 Agent skill 接口”与“仓库内部多 agent 编排实验”。
  - 第一版 skill 不建议直接保留整套多 agent 子系统；应只提炼必要协议与能力。
- `scripts/build_analysis_context.py`
  - 已被历史结论明确为 context-first 工具，不是业务真相源。
  - 第一版 skill 中不应让它继续成为第二主链。
- `tests/`
  - 先不整体继承；按新主链重建最小验证集。

## 5. 目标目录结构（建议）

```text
projects/daily_stock_analysis/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── requirements.txt
├── SKILL.md
├── scripts/
│   ├── run_stock_analysis.py
│   ├── run_market_analysis.py
│   └── doctor.py
├── references/
│   ├── contracts.md
│   ├── strategies.md
│   ├── data-sources.md
│   └── output-format.md
├── src/
│   └── stock_analysis_skill/
│       ├── __init__.py
│       ├── contracts.py
│       ├── service.py
│       ├── pipeline.py
│       ├── context/
│       ├── analyzers/
│       │   ├── stock.py
│       │   ├── market.py
│       │   └── strategy.py
│       ├── providers/
│       ├── renderers/
│       ├── strategies/
│       └── utils/
├── templates/
├── tests/
│   ├── test_contracts.py
│   ├── test_run_stock_analysis.py
│   ├── test_stock_pipeline.py
│   ├── test_market_pipeline.py
│   └── test_strategy_resolution.py
└── reports/
    └── ...
```

## 6. 第一版 skill 的能力边界

### 6.1 必须有

1. **单标的股票分析**
   - 输入：代码/名称/市场/策略/模式
   - 输出：结构化响应 + Markdown/summary

2. **市场分析 / 大盘复盘**
   - 支持 A股 / 美股 / 可扩展到港股
   - 输出市场状态、板块/指数概览、策略倾向

3. **策略分析**
   - 基于 `strategies/*.yaml` 做策略解析与应用
   - 支持 Agent 调用时显式传入 strategy

4. **统一合同**
   - 保留 request/response schema
   - 保证脚本调用、Agent 调用、未来集成的一致性

5. **最小诊断能力**
   - `doctor.py` 检查模型配置、Tushare 配置、核心依赖与主链可运行性

### 6.2 第一版可不做

- 历史分析 UI
- 回测系统
- 组合管理
- 图片导入 / 文件导入
- 多渠道通知
- 鉴权 / 用户系统 / 配置后台
- API 服务

## 7. 实施策略

### Phase A - 边界与蓝图（当前阶段）
- 输出本蓝图
- 固化保留/删除/重写边界

### Phase B - 目录与骨架重建
- 新建 `SKILL.md`
- 新建 `src/stock_analysis_skill/` 主包
- 迁移/别名统一合同模型
- 把脚本入口切到新包

### Phase C - 主链迁移
- 迁移并收敛 `AnalysisService -> Pipeline`
- 迁移 market / strategy 核心能力
- 重建最小渲染链路

### Phase D - 删旧壳
- 删除 API / Docker / 认证 / 产品层
- 删除无关测试
- 重写 README / docs

### Phase E - 最小验证
- 合同测试
- 单股分析 smoke
- 市场分析 smoke
- strategy 解析测试
- doctor 检查

## 8. 风险点

1. `src/agent/` 体系较大，若直接保留，容易把“skill-first”再次拖回“多入口系统”
2. `AnalysisService` / `Pipeline` 当前仍可能残留历史依赖，需要在迁移时切断
3. 旧测试数量过大，若不重建边界会拖慢整个重写节奏
4. README / docs 当前强产品化，若不一起改，仓库会出现“代码已经 skill-first，文档仍像 SaaS 产品”的撕裂

## 9. 当前建议

不要直接从“全量删除”开始。

建议下一步顺序：
1. 先建立新 skill 目录骨架与 `SKILL.md`
2. 再把统一合同、脚本入口、分析服务迁入新骨架
3. 等新主链可跑后，再大面积删除旧 API / Docker / 产品壳

这样可以避免仓库长时间停在“全拆了但新主链还没站起来”的半残状态。
