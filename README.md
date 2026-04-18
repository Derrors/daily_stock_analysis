# daily_stock_analysis

面向 Agent 的 **stock-analysis skill package repository**。

这个仓库已经从历史上的多入口股票分析系统，收敛为一个以 skill 为核心的可复用能力包，主目标是让下面这组入口一眼可见：

- `SKILL.md`
- `references/`
- `scripts/`
- `strategies/`
- `assets/`
- `src/stock_analysis_skill/`

> 当前主目标不再是 Web / FastAPI / Docker 产品壳，而是 **skill package + runtime library + deterministic scripts**。

---

## skill 包核心能力

- **单标的股票分析**：统一 request/response 合同，适合 Agent 调用
- **市场分析**：A股 / 美股最小市场复盘入口
- **策略解析**：从 `strategies/*.yaml` 解析策略资源
- **结构化结果输出**：优先返回统一合同，再按需渲染 Markdown
- **数据源边界**：Tushare + 新闻搜索源（Bocha / Tavily / Brave / SerpAPI）

## 工程支撑层（不是 skill 包主入口）

- `docs/`：补充性人工文档
- `support/`：规划 / 复盘 / 历史 patch 等工程支撑材料
- `tests/`：回归与契约验证
- `data_provider/`：当前阶段仍保留在顶层的运行时数据访问层

新接入默认不要从这些目录开始理解仓库；优先先看 skill 包核心面。

---

## 仓库结构

```text
daily_stock_analysis/
├── SKILL.md
├── references/
├── scripts/
├── strategies/
├── assets/
│   ├── templates/
│   └── media/
├── src/
│   └── stock_analysis_skill/
├── tests/
├── docs/
├── support/
└── data_provider/
```

### 推荐阅读顺序
1. `SKILL.md`
2. `references/package-layout.md`
3. `references/contracts.md`
4. `scripts/run_stock_analysis.py`
5. `src/stock_analysis_skill/*`

### canonical path
- 合同层：`src.stock_analysis_skill.contracts`
- 服务入口：`src.stock_analysis_skill.service`
- 股票分析：`src.stock_analysis_skill.analyzers.stock`
- 市场分析：`src.stock_analysis_skill.analyzers.market`
- 策略解析：`src.stock_analysis_skill.analyzers.strategy`
- Markdown 输出：`src.stock_analysis_skill.renderers.markdown`

`src.schemas` 只保留报告 schema；分析请求 / 响应合同请直接从 `src.stock_analysis_skill.contracts` 导入。

### assets / support 说明
- `assets/templates/`：Jinja2 报告模板
- `assets/media/`：图片、品牌素材、示例媒体
- `support/reports/`：历史规划 / 评审材料
- `support/patch/`：历史 patch 工具

---

## 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-ci.txt
```

### 2. 检查环境

```bash
python scripts/doctor.py
```

### 3. 查看股票分析请求规范化结果

```bash
python scripts/run_stock_analysis.py --stock 600519 --dry-run --pretty
```

### 4. 查看市场分析请求规范化结果

```bash
python scripts/run_market_analysis.py --region cn --dry-run --pretty
```

### 5. 解析策略资源

```bash
python scripts/resolve_strategy.py 均线金叉 --pretty
```

---

## 运行说明

### 股票分析

```bash
python scripts/run_stock_analysis.py --stock 600519
python scripts/run_stock_analysis.py --stock AAPL --market us --mode deep
```

如果缺少模型配置，脚本会 **fail-fast**，明确返回缺失项，而不是进入无意义执行链路。

### 市场分析

```bash
python scripts/run_market_analysis.py --region cn
python scripts/run_market_analysis.py --region us
```

### 策略解析

```bash
python scripts/resolve_strategy.py ma_golden_cross --pretty
python scripts/resolve_strategy.py 金叉 --pretty
python scripts/resolve_strategy.py --list
```

---

## 环境要求

### 模型相关
至少需要：
- `LITELLM_MODEL`
- 一个可用的 provider key，例如：
  - `GEMINI_API_KEY`
  - `OPENAI_API_KEY`
  - `AIHUBMIX_KEY`
  - `DEEPSEEK_API_KEY`
  - `ANTHROPIC_API_KEY`

### 数据相关
- `TUSHARE_TOKEN`：建议配置，用于市场数据主链
- `REPORT_TEMPLATES_DIR`：默认 `assets/templates`

---

## 测试

当前最小 skill 主链验证：

```bash
.venv/bin/python -m pytest \
  tests/test_stock_analysis_skill_contracts.py \
  tests/test_run_stock_analysis_entry.py \
  tests/test_stock_analysis_skill_market_strategy.py \
  tests/test_stock_analysis_skill_renderers.py
```

---

## 当前状态

当前迁移主线已经完成到 **Phase H：更纯的 skill 包化第一轮**：
- Phase A：已完成
- Phase B：已完成
- Phase C：已完成最小主链
- Phase D：已完成主结构瘦身
- Phase E：已完成多轮语义收口与兼容层减脂
- Phase F：已完成主链内迁与同步 / 异步 / agent / script 契约回归
- Phase G：已完成真实兼容面收缩
- Phase H：已完成第一轮结构纯化与 skill 包口径收尾

当前主方向不再是继续扩张工程外围，而是：
- 保持 skill 包核心暴露面清晰
- 把工程支撑层继续压到二线
- 保持全量回归稳定

---

## 相关文档

- `SKILL.md`
- `references/package-layout.md`
- `references/contracts.md`
- `references/data-sources.md`
- `references/output-format.md`
- `references/strategies.md`
- `docs/LLM_CONFIG_GUIDE.md`
- `docs/TUSHARE_STOCK_LIST_GUIDE.md`
- `docs/openclaw-skill-integration.md`（历史 / compatibility-only 参考，不是当前主线推荐接入方式）

---

## License

MIT License
