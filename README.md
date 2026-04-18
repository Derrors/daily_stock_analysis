# daily_stock_analysis

面向 Agent 的 **stock-analysis skill-first 仓库**。

这个仓库正在从历史上的多入口股票分析系统，收敛为一个只服务 Agent 的可复用能力包：
- 股票分析
- 市场分析 / 大盘复盘
- 策略解析
- 结构化结果输出
- Agent 友好的脚本入口与 skill 资源

> 当前仓库主目标不再是 Web / FastAPI / Docker 产品壳，而是 **skill + library + scripts**。

---

## 当前定位

### 保留的核心能力
- **单标的股票分析**：统一 request/response 合同，适合 Agent 调用
- **市场分析**：A股 / 美股最小市场复盘入口
- **策略解析**：从 `strategies/*.yaml` 解析策略资源
- **Markdown 输出**：面向 Agent 的确定性文本渲染
- **数据源边界**：Tushare + 新闻搜索源（Bocha / Tavily / Brave / SerpAPI）

### 已从主线移除的产品壳
- FastAPI API
- Web UI
- Docker 部署包装
- 登录认证 / 系统配置后台
- 组合管理、回测、历史页面等产品外围能力

### 兼容但不推荐作为当前入口的残留面
- 少量历史字段 / 兼容语义仍保留，用于避免旧调用方或过渡期结果解析直接炸掉
- 这些兼容面不代表仓库当前推荐用法；新接入应优先走 `scripts/*` 与 `src.stock_analysis_skill.*`

---

## 仓库结构

```text
daily_stock_analysis/
├── SKILL.md
├── strategies/
├── references/
├── scripts/
│   ├── run_stock_analysis.py
│   ├── run_market_analysis.py
│   ├── resolve_strategy.py
│   └── doctor.py
├── src/
│   └── stock_analysis_skill/
└── tests/
```

### 新 canonical path
- 合同层：`src.stock_analysis_skill.contracts`
- 服务入口：`src.stock_analysis_skill.service`
- 股票分析：`src.stock_analysis_skill.analyzers.stock`
- 市场分析：`src.stock_analysis_skill.analyzers.market`
- 策略解析：`src.stock_analysis_skill.analyzers.strategy`
- Markdown 输出：`src.stock_analysis_skill.renderers.markdown`

`src.schemas` 只保留报告 schema；分析请求 / 响应合同请直接从 `src.stock_analysis_skill.contracts` 导入。

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

当前已通过：
- contracts
- stock entry
- market dry-run
- strategy resolution
- markdown renderer

---

## 迁移状态

当前迁移主线已经完成 **Phase F：主链真相源内迁与契约回归**，后续工作进入低风险收尾：
- Phase A：已完成
- Phase B：已完成
- Phase C：已完成最小主链
- Phase D：已完成主结构瘦身
- Phase E：已完成多轮语义收口与兼容层减脂
- Phase F：已完成主链内迁与同步 / 异步 / agent / script 契约回归

当前主方向不再是继续大拆目录，而是：
- 清理文档里的过时迁移口径
- 压缩剩余 compatibility surface
- 保持 skill-first 主链回归稳定

---

## 相关文档

- `SKILL.md`
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
