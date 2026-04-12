<div align="center">

# 📈 股票智能分析系统

[![GitHub stars](https://img.shields.io/github/stars/ZhuLinsen/daily_stock_analysis?style=social)](https://github.com/ZhuLinsen/daily_stock_analysis/stargazers)
[![CI](https://github.com/ZhuLinsen/daily_stock_analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/ZhuLinsen/daily_stock_analysis/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Ready-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/)

<p>
  <a href="https://trendshift.io/repositories/18527" target="_blank"><img src="https://trendshift.io/api/badge/repositories/18527" alt="ZhuLinsen%2Fdaily_stock_analysis | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
  <a href="https://hellogithub.com/repository/ZhuLinsen/daily_stock_analysis" target="_blank"><img src="https://api.hellogithub.com/v1/widgets/recommend.svg?rid=6daa16e405ce46ed97b4a57706aeb29f&claim_uid=pfiJMqhR9uvDGlT&theme=neutral" alt="Featured｜HelloGitHub" style="width: 250px; height: 54px;" width="250" height="54" /></a>
</p>

> 🤖 面向 Agent / skill / API 的股票分析后端内核：负责分析执行、决策仪表盘生成、本地结果落盘，以及可选飞书云文档承载。

[**功能特性**](#-功能特性) · [**快速开始**](#-快速开始) · [**输出示例**](#-输出示例) · [**完整指南**](docs/full-guide.md) · [**常见问题**](docs/FAQ.md) · [**更新日志**](docs/CHANGELOG.md)

简体中文 | [English](docs/README_EN.md) | [繁體中文](docs/README_CHT.md)

</div>

## 💖 赞助商 (Sponsors)
<div align="center">
  <a href="https://serpapi.com/baidu-search-api?utm_source=github_daily_stock_analysis" target="_blank">
    <img src="./sources/serpapi_banner_zh.png" alt="轻松抓取搜索引擎上的实时金融新闻数据 - SerpApi" height="160">
  </a>
</div>
<br>


## ✨ 功能特性

| 模块 | 功能 | 说明 |
|------|------|------|
| AI | 决策仪表盘 | 一句话核心结论 + 精确买卖点位 + 操作检查清单 |
| 分析 | 多维度分析 | 技术面（盘中实时 MA/多头排列）+ 筹码分布 + 舆情情报 + 实时行情 |
| 市场 | 全球市场 | 支持 A股、港股、美股及美股指数（SPX、DJI、IXIC 等） |
| 基本面 | 结构化聚合 | 新增 `fundamental_context`（valuation/growth/earnings/institution/capital_flow/dragon_tiger/boards，其中 `earnings.data` 新增 `financial_report` 与 `dividend`，`boards` 表示板块涨跌榜），主链路 fail-open 降级 |
| 策略 | 市场策略系统 | 内置 A股「三段式复盘策略」与美股「Regime Strategy」，输出进攻/均衡/防守或 risk-on/neutral/risk-off 计划，并附“仅供参考，不构成投资建议”提示 |
| 复盘 | 大盘复盘 | 每日市场概览、板块涨跌；支持 cn(A股)/us(美股)/both(两者) 切换 |
| 输出 | 结果承载 | 决策仪表盘、本地 Markdown 报告、可选飞书云文档承载 |
| 补全 | 智能补全 (MVP) | **[测试阶段]** 代码/名称/拼音/别名联想能力已沉淀为后端检索与解析能力，可供 API / Agent 复用 |
| 智能导入 | 多源导入 | 支持图片、CSV/Excel 文件、剪贴板粘贴；Vision LLM 提取代码+名称；名称→代码解析（本地+拼音+AkShare） |
| 回测 | AI 回测验证 | 自动评估历史分析准确率，支持按股票与分析日期查看“AI 预测 vs 次日实际（1 日窗口）”和准确率 |
| 资讯 | 公司公告 + 资金流 | IntelAgent 新增公告抓取与主力资金流维度（上交所/深交所/cninfo + A 股主力资金流）用于补强舆情链路 |
| **Agent 问股** | **策略对话** | **多轮策略问答，支持均线金叉/缠论/波浪等 11 种内置策略，API / Skill 全链路** |
| API | FastAPI 服务 | 提供分析触发、历史查询、Agent 对话等后端接口 |
| 自动化 | 定时运行 | GitHub Actions / Docker / 本地定时执行，无需额外产品壳 |

> 当前仓库已完成 **agent-first backend core** 收敛：主职责是分析执行、报告生成、本地结果落盘，以及为外部调用方提供 API / skill 可复用能力。

> 消息投递能力已从仓库主链移除。若需要把结果发送到飞书 / Telegram / 邮件 / Slack / Discord 等渠道，请在仓库外部由调用方自行处理。

> 历史分析、回测、持仓、Agent 问股等能力仍以后端接口与本地结果物形式保留；其中历史报告详情会优先展示 AI 返回的原始「狙击点位」文本，避免区间价、条件说明等复杂内容在历史回看时被压缩成单个数字。

### 技术栈与数据来源

| 类型 | 支持 |
|------|------|
| AI 模型 | [AIHubMix](https://aihubmix.com/?aff=CfMq)、Gemini、OpenAI 兼容、DeepSeek、通义千问、Claude、Ollama 本地模型 等（统一通过 [LiteLLM](https://github.com/BerriAI/litellm) 调用，支持多 Key 负载均衡）|
| 行情数据 | Tushare（当前精简运行时唯一保留的数据源） |
| 新闻搜索 | Tavily、SerpAPI、Bocha、Brave |
| 社交舆情 | [Stock Sentiment API](https://api.adanos.org/docs)（Reddit / X / Polymarket，仅美股，可选） |

> **当前数据源边界**：本轮精简后，运行时行情数据仅保留 **Tushare**；新闻搜索仅保留 **Bocha / Tavily / Brave / SerpAPI**。其余历史数据源实现后续可继续物理清理，但当前主链已不再初始化它们。

> **Tushare 口径说明**：配置 `TUSHARE_TOKEN` 后，仓库将统一通过 Tushare 获取行情与相关增强数据；若对应市场或字段不在当前 Tushare 权限范围内，主链会明确报出数据源失败，而不再自动切到其他供应商。

### 内置交易纪律

| 规则 | 说明 |
|------|------|
| 严禁追高 | 乖离率超阈值（默认 5%，可配置）自动提示风险；强势趋势股自动放宽 |
| 趋势交易 | MA5 > MA10 > MA20 多头排列 |
| 精确点位 | 买入价、止损价、目标价 |
| 检查清单 | 每项条件以「满足 / 注意 / 不满足」标记 |
| 新闻时效 | 可配置新闻最大时效（默认 3 天），避免使用过时信息 |

## 🚀 快速开始

### 方式一：GitHub Actions（推荐）

> 5 分钟完成部署，零成本，无需服务器。


#### 1. Fork 本仓库

点击右上角 `Fork` 按钮（顺便点个 Star⭐ 支持一下）

#### 2. 配置 Secrets

`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

**AI 模型配置（至少配置一个）**

> 详细配置说明见 [LLM 配置指南](docs/LLM_CONFIG_GUIDE.md)（极简接入、渠道模式、高级 YAML 路由、Vision、Agent、排错）。默认推荐先选服务商并填写 API Key；需要多模型时再启用渠道模式；只有高级用户才需要 YAML 路由配置。

> 现在推荐把多模型配置统一写成 `LLM_CHANNELS + LLM_<NAME>_PROTOCOL/BASE_URL/API_KEY/MODELS/ENABLED`。如需显式指定主模型或备选模型，再额外配置 `LITELLM_MODEL` / `LITELLM_FALLBACK_MODELS`。API 服务、本地运行与 Docker 均使用同一套字段。

> 💡 **推荐 [AIHubMix](https://aihubmix.com/?aff=CfMq)**：一个 Key 即可使用 Gemini、GPT、Claude、DeepSeek 等全球主流模型，无需科学上网，含免费模型（glm-5、gpt-4o-free 等），付费模型高稳定性无限并发。本项目可享 **10% 充值优惠**。

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `AIHUBMIX_KEY` | [AIHubMix](https://aihubmix.com/?aff=CfMq) API Key，一 Key 切换使用全系模型，免费模型可用 | 可选 |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) 获取免费 Key（需科学上网） | 可选 |
| `ANTHROPIC_API_KEY` | [Anthropic Claude](https://console.anthropic.com/) API Key | 可选 |
| `ANTHROPIC_MODEL` | Claude 模型（如 `claude-3-5-sonnet-20241022`） | 可选 |
| `OPENAI_API_KEY` | OpenAI 兼容 API Key（支持 DeepSeek、通义千问等） | 可选 |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 地址（如 `https://api.deepseek.com/v1`） | 可选 |
| `OPENAI_MODEL` | 模型名称（如 `gemini-3.1-pro-preview`、`gemini-3-flash-preview`、`gpt-5.2`） | 可选 |
| `OPENAI_VISION_MODEL` | 图片识别专用模型（部分第三方模型不支持图像；不填则用 `OPENAI_MODEL`） | 可选 |
| `OLLAMA_API_BASE` | Ollama 本地服务地址（如 `http://localhost:11434`），本地/Docker 部署时使用，**不要**用 `OPENAI_BASE_URL` 配置 Ollama，详见 [LLM 配置指南 - Ollama](docs/LLM_CONFIG_GUIDE.md#示例-4使用-ollama-本地模型) | 可选 |

> 注：AI 优先级 Gemini > Anthropic > OpenAI（含 AIHubmix）> Ollama，至少配置一个。`AIHUBMIX_KEY` 无需配置 `OPENAI_BASE_URL`，系统自动适配。图片识别需 Vision 能力模型。DeepSeek 思考模式（deepseek-reasoner、deepseek-r1、qwq、deepseek-chat）按模型名自动识别，无需额外配置。**Ollama 本地模型**（无需 API Key）必须使用 `OLLAMA_API_BASE`，误用 `OPENAI_BASE_URL` 会导致 404。

<details>
<summary><b>结果输出边界</b>（点击展开）</summary>

> 通知发送能力已下线。当前仓库只负责：分析执行、报告生成、本地结果落盘，以及可选飞书云文档创建。
>
> 如需把结果发送到飞书 / Telegram / 邮件 / Slack / Discord 等渠道，请在仓库外部由调用方自行处理。

保留的输出相关配置：

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `REPORT_TYPE` | 报告类型：`simple` / `full` / `brief` | 可选 |
| `REPORT_LANGUAGE` | 报告输出语言：`zh` / `en` | 可选 |
| `REPORT_SUMMARY_ONLY` | 仅输出摘要，不含个股详情 | 可选 |
| `REPORT_TEMPLATES_DIR` | Jinja2 模板目录 | 可选 |
| `REPORT_RENDERER_ENABLED` | 启用 Jinja2 模板渲染 | 可选 |
| `REPORT_INTEGRITY_ENABLED` | 启用报告完整性校验 | 可选 |
| `REPORT_INTEGRITY_RETRY` | 完整性校验重试次数 | 可选 |
| `REPORT_HISTORY_COMPARE_N` | 历史信号对比条数 | 可选 |
| `ANALYSIS_DELAY` | 个股分析与大盘复盘之间的延迟 | 可选 |
| `MAX_WORKERS` | 分析并发线程数 | 可选 |

</details>

**其他配置**

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `STOCK_LIST` | 自选股代码，如 `600519,hk00700,AAPL,TSLA` | ✅ |
| `TAVILY_API_KEYS` | [Tavily](https://tavily.com/) 搜索 API（新闻搜索） | 推荐 |
| `SERPAPI_API_KEYS` | [SerpAPI](https://serpapi.com/baidu-search-api?utm_source=github_daily_stock_analysis) 全渠道搜索 | 可选 |
| `BOCHA_API_KEYS` | [博查搜索](https://open.bocha.cn/) Web Search API（中文搜索优化，支持AI摘要，多个key用逗号分隔） | 可选 |
| `BRAVE_API_KEYS` | [Brave Search](https://brave.com/search/api/) API（隐私优先，美股优化，多个key用逗号分隔） | 可选 |
| `SOCIAL_SENTIMENT_API_KEY` | [Stock Sentiment API](https://api.adanos.org/docs)（Reddit/X/Polymarket 社交舆情，仅美股） | 可选 |
| `SOCIAL_SENTIMENT_API_URL` | 自定义社交舆情 API 地址（默认 `https://api.adanos.org`） | 可选 |
| `TUSHARE_TOKEN` | [Tushare Pro](https://tushare.pro/weborder/#/login?reg=834638 ) Token | ✅ |
| `PREFETCH_REALTIME_QUOTES` | 实时行情预取开关；在当前 Tushare-only 模式下主要影响全量实时行情预热 | 可选 |
| `WECHAT_MSG_TYPE` | 企微消息类型，默认 markdown，支持配置 text 类型，发送纯 markdown 文本 | 可选 |
| `NEWS_STRATEGY_PROFILE` | 新闻策略窗口档位：`ultra_short`(1天) / `short`(3天) / `medium`(7天) / `long`(30天)，默认 `short` | 可选 |
| `NEWS_MAX_AGE_DAYS` | 新闻最大时效上限（天），默认 3；实际窗口 `effective_days = min(profile_days, NEWS_MAX_AGE_DAYS)`，例如 `ultra_short(1)` + `7` 仍为 `1` 天 | 可选 |
| `BIAS_THRESHOLD` | 乖离率阈值（%），默认 5.0，超过提示不追高；强势趋势股自动放宽 | 可选 |
| `AGENT_MODE` | 开启 Agent 策略问股模式（内部统一命名为 skill，`true`/`false`，默认 false） | 可选 |
| `AGENT_LITELLM_MODEL` | Agent 主模型（可选）；留空继承主模型，无前缀会按 `openai/<model>` 解析 | 可选 |
| `AGENT_SKILLS` | 激活的策略技能 id（逗号分隔），`all` 启用全部策略技能；留空时使用主默认策略 skill（内置默认是 `bull_trend`），详见 `.env.example` | 可选 |
| `AGENT_MAX_STEPS` | Agent 最大推理步数上限（默认 `10`）；保持默认时各子 Agent 按自身预设步数运行；用户主动调高到高于默认值时，所有子 Agent 统一采用该值；若设置值低于某子 Agent 的默认步数，则仍按该值作为上限进行限制 | 可选 |
| `AGENT_SKILL_DIR` | 自定义策略技能目录（默认沿用内置 `strategies/` 兼容路径） | 可选 |
| `TRADING_DAY_CHECK_ENABLED` | 交易日检查（默认 `true`）：非交易日跳过执行；设为 `false` 或使用 `--force-run` 强制执行 | 可选 |
| `ENABLE_CHIP_DISTRIBUTION` | 启用筹码分布（Actions 默认 false；需筹码数据时在 Variables 中设为 true，接口可能不稳定） | 可选 |
| `ENABLE_FUNDAMENTAL_PIPELINE` | 基本面聚合总开关；关闭时保持主流程不变 | 可选 |
| `FUNDAMENTAL_STAGE_TIMEOUT_SECONDS` | 基本面阶段总预算（秒） | 可选 |
| `FUNDAMENTAL_FETCH_TIMEOUT_SECONDS` | 单能力源调用超时（秒） | 可选 |
| `FUNDAMENTAL_RETRY_MAX` | 基本面能力重试次数（包含首次） | 可选 |
| `FUNDAMENTAL_CACHE_TTL_SECONDS` | 基本面缓存 TTL（秒） | 可选 |
| `FUNDAMENTAL_CACHE_MAX_ENTRIES` | 基本面缓存最大条目数（避免长时间运行内存增长） | 可选 |

> 基本面超时语义（P0）：
> - 当前采用 `best-effort` 软超时（fail-open），超时会立即降级并继续主流程；
> - 不承诺严格硬中断第三方调用线程，因此 `P95 <= 1.5s` 是阶段目标而非硬 SLA；
> - 若业务需要硬 SLA，可在后续阶段升级为“子进程隔离 + kill”的硬超时方案。
> - 字段契约：
>   - `fundamental_context.boards.data` = `sector_rankings`（板块涨跌榜，结构 `{top, bottom}`）；
>   - `fundamental_context.earnings.data.financial_report` = 财报摘要（报告期、营收、归母净利润、经营现金流、ROE）；
>   - `fundamental_context.earnings.data.dividend` = 分红指标（仅现金分红税前口径，含 `events`、`ttm_cash_dividend_per_share`、`ttm_dividend_yield_pct`）；
>   - `get_stock_info.belong_boards` = 个股所属板块列表；
>   - `get_stock_info.boards` 为兼容别名，值与 `belong_boards` 相同（未来仅在大版本考虑移除）；
>   - `get_stock_info.sector_rankings` 与 `fundamental_context.boards.data` 保持一致。
> - 运行时行情数据当前统一收敛到 **Tushare**；若目标市场、字段或权限不在当前 Tushare 范围内，主链会明确报出失败，而不再静默切到其他供应商。
> - 搜索链当前统一收敛到 **Bocha / Tavily / Brave / SerpAPI**；历史搜索源实现后续可继续做物理清理。

#### 3. 启用 Actions

`Actions` 标签 → `I understand my workflows, go ahead and enable them`

#### 4. 手动测试

`Actions` → `每日股票分析` → `Run workflow` → `Run workflow`

#### 完成

默认每个**工作日 18:00（北京时间）**自动执行，也可手动触发。默认非交易日（含 A/H/US 节假日）不执行。

> 💡 **关于跳过交易日检查的两种机制：**
> | 机制 | 配置方式 | 生效范围 | 适用场景 |
> |------|----------|----------|----------|
> | `TRADING_DAY_CHECK_ENABLED=false` | 环境变量/Secrets | 全局、长期有效 | 测试环境、长期关闭检查 |
> | `force_run` (UI 勾选) | Actions 手动触发时选择 | 单次运行 | 临时在非交易日执行一次 |
>
> - **环境变量方式**：在 `.env` 或 GitHub Secrets 中设置，影响所有运行方式（定时触发、手动触发、本地运行）
> - **UI 勾选方式**：仅在 GitHub Actions 手动触发时可见，不影响定时任务，适合临时需求
> - **断点续传与 `--dry-run` 的数据存在性判断**：会按股票所属市场的本地时区和交易日历解析“最新可复用交易日”；周末/节假日复用最近交易日，交易日盘中复用上一已完成交易日，盘后若当日数据已落库则可直接跳过。详细规则见 [完整指南](docs/full-guide.md)。

### 方式二：本地运行 / Docker 部署

```bash
# 克隆项目
git clone https://github.com/ZhuLinsen/daily_stock_analysis.git && cd daily_stock_analysis

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env && vim .env

# 运行分析
python main.py
```

如果你不用 Web，推荐直接在 `.env` 里按条写模型渠道：

```env
LLM_CHANNELS=primary
LLM_PRIMARY_PROTOCOL=openai
LLM_PRIMARY_BASE_URL=https://api.deepseek.com/v1
LLM_PRIMARY_API_KEY=sk-xxxxxxxx
LLM_PRIMARY_MODELS=deepseek-chat
LITELLM_MODEL=openai/deepseek-chat
```

保存后也可以继续通过 `.env`、Docker 环境变量或外部配置管理维护同一组字段；不会要求额外配置文件。

如果同时启用了高级模型路由 YAML（`LITELLM_CONFIG`），YAML 主要用于定义可用模型和路由规则（`model_list`）；运行时主模型 / 备选模型 / Vision / Temperature 仍由 `LITELLM_MODEL`、`LITELLM_FALLBACK_MODELS`、`VISION_MODEL`、`LLM_TEMPERATURE` 等字段决定。渠道编辑器只保存渠道条目，不会覆盖这些运行时字段的选择。

> Docker 部署、定时任务配置请参考 [完整指南](docs/full-guide.md)

## 📱 输出示例

### 决策仪表盘
```
🎯 2026-02-08 决策仪表盘
共分析3只股票 | 🟢买入:0 🟡观望:2 🔴卖出:1

📊 分析结果摘要
⚪ 中钨高新(000657): 观望 | 评分 65 | 看多
⚪ 永鼎股份(600105): 观望 | 评分 48 | 震荡
🟡 新莱应材(300260): 卖出 | 评分 35 | 看空

⚪ 中钨高新 (000657)
📰 重要信息速览
💭 舆情情绪: 市场关注其AI属性与业绩高增长，情绪偏积极，但需消化短期获利盘和主力流出压力。
📊 业绩预期: 基于舆情信息，公司2025年前三季度业绩同比大幅增长，基本面强劲，为股价提供支撑。

🚨 风险警报:

风险点1：2月5日主力资金大幅净卖出3.63亿元，需警惕短期抛压。
风险点2：筹码集中度高达35.15%，表明筹码分散，拉升阻力可能较大。
风险点3：舆情中提及公司历史违规记录及重组相关风险提示，需保持关注。
✨ 利好催化:

利好1：公司被市场定位为AI服务器HDI核心供应商，受益于AI产业发展。
利好2：2025年前三季度扣非净利润同比暴涨407.52%，业绩表现强劲。
📢 最新动态: 【最新消息】舆情显示公司是AI PCB微钻领域龙头，深度绑定全球头部PCB/载板厂。2月5日主力资金净卖出3.63亿元，需关注后续资金流向。

---
生成时间: 18:00
```

### 大盘复盘
```
🎯 2026-01-10 大盘复盘

📊 主要指数
- 上证指数: 3250.12 (🟢+0.85%)
- 深证成指: 10521.36 (🟢+1.02%)
- 创业板指: 2156.78 (🟢+1.35%)

📈 市场概况
上涨: 3920 | 下跌: 1349 | 涨停: 155 | 跌停: 3

🔥 板块表现
领涨: 互联网服务、文化传媒、小金属
领跌: 保险、航空机场、光伏设备
```
## ⚙️ 配置说明

> 📖 完整环境变量、定时任务配置请参考 [完整配置指南](docs/full-guide.md)
> 邮件通知当前基于 SMTP 授权码/基础认证；若 Outlook / Exchange 账号或租户强制 OAuth2，当前版本暂不支持。


## 🖥️ Web 界面

![img.png](sources/fastapi_server.png)

包含完整的配置管理、任务监控和手动分析功能。

**本轮界面升级亮点：**

- **全新浅色主题**：不再只是深色工作台，浅色模式针对输入框、卡片层级、边界对比、状态提示做了成套重绘。
- **主题切换可持久化**：侧边栏内可随时切换浅色 / 深色主题，页面刷新后仍保留用户选择。
- **核心页面统一收口**：首页、问股、回测、持仓、设置共用同一套视觉 token、状态原语和表面组件，减少“每页一个风格”的割裂感。
- **移动端与触屏体验增强**：抽屉遮罩、滚动契约、消息操作可达性和关键按钮语义同步补强，小屏设备上更稳定。

**可选密码保护**：在 `.env` 中设置 `ADMIN_AUTH_ENABLED=true` 可启用 Web 登录，首次访问在网页设置初始密码，保护 Settings 中的 API 密钥等敏感配置。系统设置现支持运行时开启或关闭认证；关闭认证不会删除已保存密码，后续可直接重新启用。认证开启时，`POST /api/v1/auth/logout` 也需要有效会话；如果会话已经过期，前端会直接回到登录页。详见 [完整指南](docs/full-guide.md)。

### 智能导入

在 **设置 → 基础设置** 中找到「智能导入」区块，支持三种方式添加自选股：

1. **图片**：拖拽或选择自选股截图（如 APP 持仓页、行情列表），Vision AI 自动识别代码+名称，并给出置信度
2. **文件**：上传 CSV 或 Excel (.xlsx)，自动解析代码/名称列
3. **粘贴**：从 Excel 或表格复制后粘贴，点击「解析」即可

**预览与合并**：高置信度默认勾选，中/低置信度需手动勾选；支持按代码去重、清空、全选；仅合并已勾选且解析成功的项。

**配置与限制**：
- 图片需配置 Vision API（`GEMINI_API_KEY`、`ANTHROPIC_API_KEY` 或 `OPENAI_API_KEY` 至少一个）
- 图片：JPG/PNG/WebP/GIF，≤5MB；文件：≤2MB；粘贴文本：≤100KB

**API**：`POST /api/v1/stocks/extract-from-image`（图片）、`POST /api/v1/stocks/parse-import`（文件/粘贴）。详见 [完整指南](docs/full-guide.md)。

### 智能搜索补全 (MVP)

首页分析输入框已升级为”类搜索引擎”补全框，显著降低记忆负担：

- **多维匹配**：支持输入股票代码、中文名、拼音缩写或别名（如 `gzmt` -> 贵州茅台、`tencent` -> 腾讯控股、`aapl` -> Apple Inc.）。
- **多市场覆盖**：本地索引已覆盖 **A股、港股、美股** 三个市场；通过 Tushare 或 AkShare 数据源生成，支持按需更新索引。
- **自动降级逻辑**：
  - **新股/异常**：若索引未及时更新或加载失败，系统将无缝退回普通输入模式，确保分析链路 100% 可用。
  - **未命中**：搜索未命中时，用户直接按回车即可走原有手动输入流程，完全不影响分析。


**LLM 用量查询**：`GET /api/v1/usage/summary?period=today|month|all`，返回按调用类型和模型分组的 token 消耗汇总（`total_calls`、`total_tokens`、`by_call_type`、`by_model`）。

**分析 API 说明**：`POST /api/v1/analysis/analyze` 在 `async_mode=false` 时仅支持单只股票；批量 `stock_codes` 需要 `async_mode=true`。异步 `202` 响应对单股返回 `task_id`，对批量返回 `accepted` / `duplicates` 汇总结构；空白股票代码会在服务端过滤，若过滤后为空则返回 `400`。未知 `/api` 路径（含 `/api` 本身）返回 JSON `404`，不再回退到前端页面。详见 [API 规范](docs/architecture/api_spec.json)。

### 历史报告详情

在首页历史记录中选择一条分析记录后，点击「完整分析报告」按钮可在右侧抽屉中查看与推送通知格式一致的完整 Markdown 分析报告，包含舆情情报、核心结论、数据透视、作战计划等完整内容。

报告头部提供两种复制方式：

- 「复制 Markdown 源码」：保留原始 Markdown 结构，适合二次编辑、技术社区分享和笔记归档。
- 「复制纯文本」：去除常见 Markdown 格式符号，适合微信、群聊等纯文本分享场景。

### 🤖 Agent 策略问股

在 `.env` 中设置 `AGENT_MODE=true` 后启动服务，即可通过 `/api/v1/agent/chat*` 相关接口开始多轮策略问答。

> 对用户侧文案，本项目仍以“策略”为主称呼；代码、配置和 API 主字段统一使用 `skill`，可理解为“可复用的策略能力包”。

- **选择策略**：均线金叉、缠论、波浪理论、多头趋势等 11 种内置策略
- **自然语言提问**：如「用缠论分析 600519」，Agent 自动调用实时行情、K线、技术指标、新闻等工具
- **流式进度反馈**：实时展示 AI 思考路径（行情获取 → 技术分析 → 新闻搜索 → 生成结论）
- **多轮对话**：支持追问上下文，会话历史持久化保存
- **导出与归档**：可将会话导出为 `.md` 文件，便于二次整理、审阅与外部系统继续处理
- **后台执行**：切换页面不中断分析，完成时 Dock 问股图标显示角标
- **自定义策略（Skill）**：在 `strategies/` 目录下新建 YAML 文件或在自定义 skill 目录中放入 `SKILL.md` bundle，即可添加新的交易策略，无需写代码
- **多 Agent 架构**（实验性）：设置 `AGENT_ARCH=multi` 启用 Technical → Intel → Risk → Specialist → Decision 多 Agent 级联编排，通过 `AGENT_ORCHESTRATOR_MODE` 控制深度（quick/standard/full/specialist）。其中 `strategy` / `skill` 仍作为旧值兼容并会自动归一化到 `specialist`。超时或中间阶段 JSON 解析失败时，系统会优先保留已完成阶段结果并降级生成最小可用仪表盘，避免整份报告直接退回默认占位。详见 [完整配置指南](docs/full-guide.md)
- **Intel 增强字段兼容说明**：`capital_flow_signal` 为新增扩展字段（`inflow/outflow/neutral/not_available`），用于描述 A 股资金流方向，未返回时不会影响后续阶段；下游解析建议以 `risk_alerts` 与 `positive_catalysts` 为主，新增字段可忽略，兼容历史客户端。

> **注意**：配置了任意 AI API Key 后，Agent 对话功能自动可用，无需手动设置 `AGENT_MODE=true`。如需显式关闭可设置 `AGENT_MODE=false`。每次对话会产生 LLM API 调用费用。若你手动修改了 `.env` 中的主模型 / Agent 主模型 / 备选模型 / 模型渠道配置（如 `LITELLM_MODEL` / `AGENT_LITELLM_MODEL` / `LITELLM_FALLBACK_MODELS` / `LLM_CHANNELS`），需要重启服务或触发配置重载后，新进程才会按新模型生效。

### 启动方式

1. **启动 API 服务**
   ```bash
   python main.py --serve       # 启动 API 服务 + 执行分析
   python main.py --serve-only  # 仅启动 API 服务
   ```

访问 `http://127.0.0.1:8000/docs` 即可查看接口文档。

## 🗺️ Roadmap

查看已支持的功能和未来规划：[更新日志](docs/CHANGELOG.md)

> 有建议？欢迎 [提交 Issue](https://github.com/ZhuLinsen/daily_stock_analysis/issues)

> ⚠️ **UI 调整提示**：项目当前正在持续进行 Web UI 调整与升级，部分页面在过渡阶段可能仍存在样式、交互或兼容性问题。欢迎通过 [Issue](https://github.com/ZhuLinsen/daily_stock_analysis/issues) 反馈问题，或直接提交 [Pull Request](https://github.com/ZhuLinsen/daily_stock_analysis/pulls) 一起完善。
---

## ☕ 支持项目

如果本项目对你有帮助，欢迎支持项目的持续维护与迭代，感谢支持 🙏  
赞赏可备注联系方式，祝股市长虹

| 支付宝 (Alipay) | 微信支付 (WeChat) | 小红书 |
| :---: | :---: | :---: |
| <img src="./sources/alipay.jpg" width="200" alt="Alipay"> | <img src="./sources/wechatpay.jpg" width="200" alt="WeChat Pay"> | <img src="./sources/xiaohongshu.png" width="200" alt="小红书"> |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

详见 [贡献指南](docs/CONTRIBUTING.md)

### 本地门禁（建议先跑）

```bash
pip install -r requirements.txt
pip install flake8 pytest
./scripts/ci_gate.sh
```


## 📄 License
[MIT License](LICENSE) © 2026 ZhuLinsen

如果你在项目中使用或基于本项目进行二次开发，
非常欢迎在 README 或文档中注明来源并附上本仓库链接。
这将有助于项目的持续维护和社区发展。

## 📬 联系与合作
- GitHub Issues：[提交 Issue](https://github.com/ZhuLinsen/daily_stock_analysis/issues)
- 合作邮箱：zhuls345@gmail.com

## ⭐ Star History
**如果觉得有用，请给个 ⭐ Star 支持一下！**

<a href="https://star-history.com/#ZhuLinsen/daily_stock_analysis&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date" />
 </picture>
</a>

## ⚠️ 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。作者不对使用本项目产生的任何损失负责。

---
