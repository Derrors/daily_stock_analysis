# daily_stock_analysis final legacy sweep

日期：2026-04-17

## 目标

对 skill-first rewrite 之后仓库里剩余的 legacy/compat 文件做最后一轮分类，输出：
- 建议保留
- 建议删除
- 待观察

本次判断标准：
1. 是否仍直接服务新的 **skill + library + scripts** 主形态
2. 是否仍被当前通过的最小主链 / agent 回归所依赖
3. 是否只是旧产品壳遗留的兼容债或文档漂移

---

## 一、建议保留（当前仍有明确价值）

### 1. 配置底座
- `src/config.py`
- `src/core/config_registry.py`

**原因**：
- 新主链脚本（`run_stock_analysis.py`、`run_market_analysis.py`、`doctor.py`）仍依赖配置加载
- 当前模型、数据源、Tushare、LiteLLM、agent skill 行为都还从这里取配置
- 它们已经不再只是旧 Web/API 的配置中心，而是当前 skill runtime 的基础设施层

**结论**：保留。

### 2. 分析底座与输出底座
- `src/analyzer.py`
- `src/core/pipeline.py`
- `src/services/analysis_service.py`
- `src/services/analysis_context_service.py`
- `src/notification.py`
- `src/services/report_renderer.py`
- `templates/`
- `data_provider/`
- `strategies/`

**原因**：
- 这是当前 skill-first 仓库依然在复用的真正分析主链与渲染底座
- 尽管名称中还残留旧“notification”语义，但实际已经承担报告输出兼容层功能

**结论**：保留；后续只做语义收口，不建议再大拆。

### 3. Agent 基础设施（已收口后仍可用）
- `src/agent/memory.py`
- `src/agent/skills/aggregator.py`
- `src/agent/factory.py`
- `src/agent/tools/registry.py`
- `src/agent/tools/analysis_tools.py`
- `src/agent/tools/search_tools.py`
- `src/agent/tools/market_tools.py`
- `tests/test_agent_behavior.py`
- `tests/test_agent_registry.py`
- `tests/test_skill_load_warning.py`

**原因**：
- 这些能力已经不再直接依赖已删的 backtest / portfolio / api 产品壳
- 本轮已把 backtest 自动加权改成 neutral fallback，并完成 73 项 skill+agent 回归通过
- 说明它们已经从“旧产品依赖”转成“仍然有价值的 agent runtime 层”

**结论**：保留。

### 4. 历史信号对比服务
- `src/services/history_comparison_service.py`

**原因**：
- 仍被 `src/notification.py` 用于报告渲染对比上下文
- 这是分析结果展示增强，不属于旧 Web/API 产品壳

**结论**：保留。

---

## 二、建议删除（下一步可直接清）

### 1. 明确仍依赖已删 API 的测试
- `tests/test_autocomplete_pr0.py`
- `tests/test_agent_sse_cleanup.py`

**原因**：
- 二者仍显式依赖 `api.*` 模块
- `api/` 已经删除，这类测试不再属于 skill-first 仓库
- 当前未纳入 73 项回归；若未来全量收集测试，会重新炸出已删 API 的引用错误

**结论**：建议直接删除。

### 2. `src/services/__init__.py` 中的旧示例文案
不是整文件删除，而是：
- **建议立刻修正文档串**

当前还写着：
- `from src.services.history_service import HistoryService`

但 `history_service.py` 已删除。

**结论**：应保留文件，但立即修正文案，避免继续误导。

---

## 三、待观察（现在先不删）

### 1. `src/agent/events.py`

**观察点**：
- 还保留“background task / --schedule” 口径
- 但它本身并不依赖已删 API；更像未来事件监控能力的 runtime 原型

**结论**：
- 暂不删除
- 如最终目标明确“不做任何事件监控 / alert”，再删
- 否则建议保留，并改文档表述，去掉 `--schedule` 这种旧 CLI 主程序口径

### 2. `.env.example`

**观察点**：
- 很可能还残留大量已删模块的配置项
- 但这类配置清理属于“配置契约收口”，改动面大，容易影响当前可运行性

**结论**：
- 建议作为下一步单独清理任务
- 不要在未重新核对 `src/config.py` 之前盲删

### 3. `src/config.py` 内的历史字段

**观察点**：
- 现在大量字段可能已不再被新 skill 主链使用
- 但它仍是运行时底座，不能粗暴删字段

**结论**：
- 当前不建议继续删字段
- 建议后续做一次“配置最小化审计”，逐项判断是否还能被 `scripts/*`、`src/stock_analysis_skill/*`、`src/analyzer.py`、`data_provider/*` 访问

---

## 四、当前判断

### 已经达到的状态
仓库主形态已经明确变成：
- `SKILL.md`
- `references/`
- `scripts/*`
- `src/stock_analysis_skill/*`
- 必要 runtime 底座

旧产品壳（API / Docker / auth / backtest / portfolio / history service / import / image-extract）已被大面积移除。

### 还剩的真正“硬残留”
本轮扫描后，最明确还值得立刻处理的只剩：
1. `tests/test_autocomplete_pr0.py`
2. `tests/test_agent_sse_cleanup.py`
3. `src/services/__init__.py` 里的旧 history_service 示例文案

除此之外，其余残留更像：
- 运行时底座
- agent runtime 层
- 配置兼容层
- 后续可再精修的语义债

---

## 五、建议的最后收尾动作

如果继续清最后一小刀，建议顺序：

1. 删除：
   - `tests/test_autocomplete_pr0.py`
   - `tests/test_agent_sse_cleanup.py`
2. 修正：
   - `src/services/__init__.py` 的旧使用示例
   - `src/agent/events.py` 里涉及 `--schedule` 的表述（如要继续收口）
3. 再跑当前 73 项 skill+agent 回归

做完之后，这轮重构可以认为进入“结构完成，后续只剩配置减脂”的阶段。
