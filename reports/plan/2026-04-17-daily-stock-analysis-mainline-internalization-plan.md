# daily_stock_analysis mainline internalization plan

日期：2026-04-17
阶段：Phase F.1 设计冻结

## 1. 目标

将 `daily_stock_analysis` 从“skill-first 外壳 + 旧主链真相源”推进到“`src/stock_analysis_skill/*` 成为业务真相源”的状态。

本阶段**只做设计冻结，不做执行链迁移**。

目标不是继续做语义收口，而是明确以下问题：
- 谁是未来唯一主链真相源
- 旧主链模块如何退化为兼容壳
- 同步链、异步链、脚本链、Agent 链未来如何对齐
- 如何避免在迁移过程中形成新的双真相源

---

## 2. 当前已确认事实

### 2.1 当前同步/异步主链

当前长期边界已明确：
- **同步主链**：`AnalysisService -> StockAnalysisPipeline`
- **异步主链**：`AnalysisTaskQueue -> AnalysisService -> StockAnalysisPipeline`

这仍是当前仓库的真实执行链。

### 2.2 当前 skill-first 层的真实定位

当前 `src/stock_analysis_skill/*` 已完成：
- contract 层
- facade/service 层
- script entry 层
- renderer / strategy resolver 等外围层

但它仍不是主业务真相源；更接近：
- facade
- wrapper
- contract boundary
- agent/script friendly surface

### 2.3 当前必须保护的外部入口

迁移过程中，这些入口应尽量保持 contract 稳定：
- `scripts/run_stock_analysis.py`
- `scripts/run_market_analysis.py`
- `scripts/resolve_strategy.py`
- `StockAnalysisSkillService.analyze_request()`
- `AnalysisService.analyze_stock_unified()`
- `AnalysisTaskQueue` 的任务提交 / 查询 / 进度回调主契约

---

## 3. 目标边界（冻结版）

## 3.1 最终唯一真相源

未来唯一业务真相源应收敛到：
- `src/stock_analysis_skill/*`

至少包含：
- `contracts.py`：唯一合同层
- `service.py`：唯一主服务入口（对外）
- `runtime/` 或 `pipeline/`：真正主链执行编排
- `analyzers/`：分析能力组件
- `renderers/`：输出能力

## 3.2 旧模块未来定位

### `src/services/analysis_service.py`
未来定位：**compat facade**

保留职责：
- 兼容旧 import 路径
- 兼容旧返回结构/桥接逻辑
- 可继续暴露 unified bridge

禁止继续承担：
- 新主业务逻辑增长
- 新编排真相源

### `src/core/pipeline.py`
未来定位：**compat pipeline shell / thin wrapper**

保留职责：
- 兼容旧 patch 点与旧类名
- 转发到新 runtime pipeline

禁止继续承担：
- 主链业务编排增长
- 新依赖装配逻辑增长

### `src/analyzer.py`
未来定位：**可拆分的分析内核组件宿主**

短期：
- 允许继续存在
- 允许作为被 skill runtime 调用的内部分析器

中期：
- 逐步拆分出 LLM 调用、结果归一化、fallback、report generation 等子模块
- 最终降为兼容壳或薄聚合层

---

## 4. 未来目标调用链

## 4.1 同步主链（目标）

建议目标形态：

`StockAnalysisSkillService -> stock_analysis_skill.runtime.stock_pipeline -> internal analyzers/providers/renderers`

兼容层路径：

`AnalysisService -> StockAnalysisSkillService`

即：
- `StockAnalysisSkillService` 成为真正主入口
- `AnalysisService` 退为旧调用方桥接壳

## 4.2 异步主链（目标）

建议目标形态：

`AnalysisTaskQueue -> StockAnalysisSkillService`

兼容层要求：
- task queue 不再把 `AnalysisService` 当作真服务层入口
- `AnalysisService` 仍可留，但不再是异步链的真相源

## 4.3 脚本链（目标）

- `scripts/run_stock_analysis.py` 直接走 `StockAnalysisSkillService`
- `scripts/run_market_analysis.py` 直接走 `stock_analysis_skill` 内部市场分析链
- script contract 保持稳定，不跟随内部目录迁移频繁变化

## 4.4 Agent 链（目标）

Agent 调用链继续以 skill facade 为统一边界：
- Agent 不直接依赖旧 `AnalysisService -> StockAnalysisPipeline` 真相链
- Agent 通过 `stock_analysis_skill` 暴露的统一 service/runtime 入口取能力

---

## 5. 迁移实施顺序（冻结版）

## Phase F.2 同步主链内迁

### 目标
把同步股票分析主执行链逐步迁入 `src/stock_analysis_skill/*`。

### 推荐步骤
1. 新建：
   - `src/stock_analysis_skill/runtime/__init__.py`
   - `src/stock_analysis_skill/runtime/stock_pipeline.py`
2. 把 `src/core/pipeline.py` 中真正承担主链编排的逻辑搬进去
3. 让 `StockAnalysisSkillService.analyze_request()` 直接走新 runtime pipeline
4. 让 `AnalysisService` 改为 compat facade，内部转发到 skill runtime
5. `src/core/pipeline.py` 降为 thin wrapper / compat shell

### 本阶段不做
- 不动 task queue
- 不动 async 主链
- 不大拆 `src/analyzer.py`

## Phase F.3 异步主链对齐

### 目标
把 `AnalysisTaskQueue` 调用关系对齐到新的 skill runtime 主链。

### 推荐步骤
1. `AnalysisTaskQueue` 改为调 `StockAnalysisSkillService`
2. 保持 query_id / progress_callback / task state contract 不变
3. `AnalysisService` 继续保留兼容桥接，但不再作为异步真入口

## Phase F.4 Analyzer 内核拆分（可选延后）

### 目标
继续拆 `src/analyzer.py`，但这不是 F.2 / F.3 的前置条件。

### 原则
- 先完成编排真相源迁移
- 再拆 analyzer 内部能力块
- 避免在未完成主链内迁前同时大拆 analyzer，导致风险叠加

---

## 6. 明确禁止事项

### 6.1 禁止形成新的双真相源

迁移过程中，不允许出现：
- 新 runtime pipeline 增长一套逻辑
- 旧 `StockAnalysisPipeline` 又继续增长一套逻辑

规则：
- 一旦某段逻辑迁入 `src/stock_analysis_skill/*`，旧位置只能退壳，不能继续长肉

### 6.2 禁止同步/异步链同时大改

必须按顺序：
1. 先同步主链
2. 再异步主链

### 6.3 禁止在 F.2 阶段重构 public contract

不要同时改：
- scripts 输出结构
- unified response 形状
- task queue 对外状态结构
- Agent 已依赖的主 service 调用方式

### 6.4 禁止在 compat shell 中新增业务逻辑

旧模块只允许：
- re-export
- 参数适配
- 返回结构桥接
- 旧类名兼容

---

## 7. 风险点

### 7.1 `StockAnalysisPipeline` 的测试覆盖很深

当前大量测试直接 patch 或实例化：
- `src.core.pipeline.StockAnalysisPipeline`

因此 F.2 不适合直接删除类；应先降壳，保留 patch 点。

### 7.2 `AnalysisService` 还承担桥接返回结构

它不只是“调用 pipeline”，还承担：
- legacy response shape
- unified response bridge

因此不能直接删，只能先 compat facade 化。

### 7.3 `task_queue` 改动容易牵连进度与状态语义

异步链改造必须单独成阶段，不和同步主链同 turn 混改。

### 7.4 `src/analyzer.py` 体量大且耦合多

其拆分应后置，否则会把“主链内迁”与“分析器重构”叠成同一次高风险变更。

---

## 8. 回归与验收策略

## F.2 完成后至少要验证
- `tests/test_run_stock_analysis_entry.py`
- `tests/test_run_stock_analysis_script.py`
- `tests/test_stock_analysis_skill_contracts.py`
- `tests/test_stock_analysis_skill_market_strategy.py`
- `tests/test_stock_analysis_skill_renderers.py`
- `tests/test_analysis_service_unified_bridge.py`
- `tests/test_agent_pipeline.py`
- 相关 `tests/test_pipeline_*`
- 最后全量 `pytest`

## F.3 完成后至少要验证
- `tests/test_task_queue_config_sync.py`
- `tests/test_analysis_metadata.py`
- 所有 task queue / async 相关测试
- 最后全量 `pytest`

---

## 9. 建议的下一步

当前建议只进入：
- **Phase F.2 同步主链内迁**

具体第一刀建议：
1. 新建 `src/stock_analysis_skill/runtime/stock_pipeline.py`
2. 先迁同步股票分析主链编排
3. `StockAnalysisSkillService` 改为直接走新 runtime
4. `AnalysisService` 改为 compat facade
5. `src/core/pipeline.py` 退为 compat shell

完成这一里程碑后，再单独汇报并等待确认是否进入 F.3。
