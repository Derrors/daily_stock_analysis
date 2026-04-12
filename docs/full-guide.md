# 📖 完整配置与部署指南

本文档包含 A股智能分析系统的完整配置说明，适合需要高级功能或特殊部署方式的用户。

> 💡 快速上手请参考 [README.md](../README.md)，本文档为进阶配置。

## 📁 项目结构

```
daily_stock_analysis/
├── main.py              # 主程序入口
├── src/                 # 核心业务逻辑
│   ├── analyzer.py      # AI 分析器
│   ├── config.py        # 配置管理
│   ├── notification.py  # 报告生成 / 兼容发送空壳
│   └── ...
├── data_provider/       # 多数据源适配器
├── api/                 # FastAPI 后端服务
├── docker/              # Docker 配置
├── docs/                # 项目文档
```

## 📑 目录

- [项目结构](#项目结构)
- [环境变量完整列表](#环境变量完整列表)
- [Docker 部署](#docker-部署)
- [本地运行详细配置](#本地运行详细配置)
- [定时任务配置](#定时任务配置)
- [结果输出说明](#结果输出说明)
- [数据源配置](#数据源配置)
- [高级功能](#高级功能)
- [回测功能](#回测功能)

---

## 环境变量完整列表

### AI 模型配置

> 完整说明见 [LLM 配置指南](LLM_CONFIG_GUIDE.md)（三层配置、渠道模式、Vision、Agent、排错）。

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|:----:|
| `LITELLM_MODEL` | 主模型，格式 `provider/model`（如 `gemini/gemini-2.5-flash`），推荐优先使用 | - | 否 |
| `AGENT_LITELLM_MODEL` | Agent 主模型（可选）；留空继承主模型，无 provider 前缀按 `openai/<model>` 解析 | - | 否 |
| `LITELLM_FALLBACK_MODELS` | 备选模型，逗号分隔 | - | 否 |
| `LLM_CHANNELS` | 渠道名称列表（逗号分隔），配合 `LLM_{NAME}_*` 使用，详见 [LLM 配置指南](LLM_CONFIG_GUIDE.md) | - | 否 |
| `LITELLM_CONFIG` | 高级模型路由 YAML 配置文件路径（高级） | - | 否 |
| `AIHUBMIX_KEY` | [AIHubmix](https://aihubmix.com/?aff=CfMq) API Key，一 Key 切换使用全系模型，无需额外配置 Base URL | - | 可选 |
| `GEMINI_API_KEY` | Google Gemini API Key | - | 可选 |
| `GEMINI_MODEL` | 主模型名称（legacy，`LITELLM_MODEL` 优先） | `gemini-3-flash-preview` | 否 |
| `GEMINI_MODEL_FALLBACK` | 备选模型（legacy） | `gemini-2.5-flash` | 否 |
| `OPENAI_API_KEY` | OpenAI 兼容 API Key | - | 可选 |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 地址 | - | 可选 |
| `OLLAMA_API_BASE` | Ollama 本地服务地址（如 `http://localhost:11434`），详见 [LLM 配置指南](LLM_CONFIG_GUIDE.md) | - | 可选 |
| `OPENAI_MODEL` | OpenAI 模型名称（legacy，AIHubmix 用户可填如 `gemini-3.1-pro-preview`、`gpt-5.2`） | `gpt-5.2` | 可选 |
| `ANTHROPIC_API_KEY` | Anthropic Claude API Key | - | 可选 |
| `ANTHROPIC_MODEL` | Claude 模型名称 | `claude-3-5-sonnet-20241022` | 可选 |
| `ANTHROPIC_TEMPERATURE` | Claude 温度参数（0.0-1.0） | `0.7` | 可选 |
| `ANTHROPIC_MAX_TOKENS` | Claude 响应最大 token 数 | `8192` | 可选 |

> *注：`AIHUBMIX_KEY`、`GEMINI_API_KEY`、`ANTHROPIC_API_KEY`、`OPENAI_API_KEY` 或 `OLLAMA_API_BASE` 至少配置一个。`AIHUBMIX_KEY` 无需配置 `OPENAI_BASE_URL`，系统自动适配。

### 结果输出边界

> 通知发送能力已下线。需要把结果投递到外部渠道时，请在调用方完成。
>
> 这里仍保留飞书云文档配置，用于承载较长结果内容。

#### 飞书云文档配置（可选，解决长报告承载问题）

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `FEISHU_APP_ID` | 飞书应用 ID | 可选 |
| `FEISHU_APP_SECRET` | 飞书应用 Secret | 可选 |
| `FEISHU_FOLDER_TOKEN` | 飞书云盘文件夹 Token | 可选 |

> 飞书云文档配置步骤：
> 1. 在 [飞书开发者后台](https://open.feishu.cn/app) 创建应用
> 2. 配置 GitHub Secrets
> 3. 将应用加入需要访问的飞书空间或文档场景
> 4. 在云盘文件夹中添加对应协作者权限
>
> 说明：`FEISHU_APP_ID` / `FEISHU_APP_SECRET` / `FEISHU_FOLDER_TOKEN` 仅用于飞书云文档等结果承载集成。

### 搜索服务配置

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `TAVILY_API_KEYS` | Tavily 搜索 API Key（推荐） | 推荐 |
| `BOCHA_API_KEYS` | 博查搜索 API Key（中文优化） | 可选 |
| `BRAVE_API_KEYS` | Brave Search API Key（美股优化） | 可选 |
| `SERPAPI_API_KEYS` | SerpAPI 备用搜索 | 可选 |
| `SOCIAL_SENTIMENT_API_KEY` | Stock Sentiment API Key（Reddit / X / Polymarket，可选） | 可选 |
| `SOCIAL_SENTIMENT_API_URL` | Stock Sentiment API 地址（默认 `https://api.adanos.org`） | 可选 |
| `NEWS_STRATEGY_PROFILE` | 新闻策略窗口档位：`ultra_short`(1天)/`short`(3天)/`medium`(7天)/`long`(30天)；实际窗口取与 `NEWS_MAX_AGE_DAYS` 的最小值 | 默认 `short` |
| `NEWS_MAX_AGE_DAYS` | 新闻最大时效（天），搜索时限制结果在近期内 | 默认 `3` |
| `BIAS_THRESHOLD` | 乖离率阈值（%），超过提示不追高；强势趋势股自动放宽到 1.5 倍 | 默认 `5.0` |

> 行为说明：搜索服务与社交舆情服务为可选增强链路。任一服务初始化失败时，系统会记录 warning 并降级为跳过该服务，仅影响对应环节，不会阻塞技术面主链路和主任务流。

### 数据源配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|:----:|
| `TUSHARE_TOKEN` | Tushare Pro Token（当前唯一保留的运行时行情数据源） | - | ✅ |
| `ENABLE_REALTIME_QUOTE` | 启用实时行情（关闭后使用历史收盘价分析） | `true` | 可选 |
| `ENABLE_REALTIME_TECHNICAL_INDICATORS` | 盘中实时技术面：启用时用实时价计算 MA5/MA10/MA20 与多头排列；关闭则用昨日收盘 | `true` | 可选 |
| `ENABLE_CHIP_DISTRIBUTION` | 启用筹码分布分析（若当前 Tushare 能力或权限不支持，将明确报错） | `true` | 可选 |
| `REALTIME_SOURCE_PRIORITY` | 兼容字段；当前运行时会统一归一为 `tushare` | `tushare` | 可选 |
| `ENABLE_FUNDAMENTAL_PIPELINE` | 基本面聚合总开关；关闭时仅返回 `not_supported` 块，不改变原分析链路 | `true` | 可选 |
| `FUNDAMENTAL_STAGE_TIMEOUT_SECONDS` | 基本面阶段总时延预算（秒） | `1.5` | 可选 |
| `FUNDAMENTAL_FETCH_TIMEOUT_SECONDS` | 单能力源调用超时（秒） | `0.8` | 可选 |
| `FUNDAMENTAL_RETRY_MAX` | 基本面能力重试次数（含首次） | `1` | 可选 |
| `FUNDAMENTAL_CACHE_TTL_SECONDS` | 基本面聚合缓存 TTL（秒），短缓存减轻重复拉取 | `120` | 可选 |
| `FUNDAMENTAL_CACHE_MAX_ENTRIES` | 基本面缓存最大条目数（TTL 内按时间淘汰） | `256` | 可选 |

> 行为说明：
> - 当前运行时行情数据统一走 **Tushare**；主链不再自动回退到 AkShare / YFinance / Longbridge / TickFlow / efinance / pytdx / baostock。
> - A 股：按 `valuation/growth/earnings/institution/capital_flow/dragon_tiger/boards` 聚合能力返回；
> - ETF：返回可得项，缺失能力标记为 `not_supported`，整体不影响原流程；
> - 美股/港股：返回 `not_supported` 兜底块；
> - 任何异常走 fail-open，仅记录错误，不影响技术面/新闻/筹码主链路。
> - 字段契约：
>   - `fundamental_context.belong_boards` = 个股关联板块列表（当前仅 A 股写入；无数据时为 `[]`）；
>   - `fundamental_context.boards.data` = `sector_rankings`（板块涨跌榜，结构 `{top, bottom}`）；
>   - `fundamental_context.earnings.data.financial_report` = 财报摘要（报告期、营收、归母净利润、经营现金流、ROE）；
>   - `fundamental_context.earnings.data.dividend` = 分红指标（仅现金分红税前口径，含 `events`、`ttm_cash_dividend_per_share`、`ttm_dividend_yield_pct`）；
>   - `get_stock_info.belong_boards` = 个股所属板块列表；
>   - `get_stock_info.boards` 为兼容别名，值与 `belong_boards` 相同（未来仅在大版本考虑移除）；
>   - `get_stock_info.sector_rankings` 与 `fundamental_context.boards.data` 保持一致。
>   - `AnalysisReport.details.belong_boards` = 结构化报告详情中的关联板块列表；
>   - `AnalysisReport.details.sector_rankings` = 结构化报告详情中的板块涨跌榜（用于前端板块联动展示）。
> - 板块涨跌榜使用数据源顺序：与全局 priority 一致。
> - 超时控制为 `best-effort` 软超时：阶段会按预算快速降级继续执行，但不保证硬中断底层三方调用。
> - `FUNDAMENTAL_STAGE_TIMEOUT_SECONDS=1.5` 表示新增基本面阶段的目标预算，不是严格硬 SLA。
> - 若要硬 SLA，请在后续版本升级为子进程隔离执行并在超时后强制终止。

### 其他配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `STOCK_LIST` | 自选股代码（逗号分隔） | - |
| `ADMIN_AUTH_ENABLED` | Web 登录：设为 `true` 启用密码保护；首次访问在网页设置初始密码，可在「系统设置 > 修改密码」修改；忘记密码执行 `python -m src.auth reset_password` | `false` |
| `TRUST_X_FORWARDED_FOR` | 单层可信反向代理部署时设为 `true`，取 `X-Forwarded-For` 最右值作为真实客户端 IP（用于登录限流等）；直连公网时保持 `false` 防伪造。多级代理/CDN 场景下限流 key 可能退化为边缘代理 IP，需额外评估 | `false` |
| `MAX_WORKERS` | 并发线程数 | `3` |
| `MARKET_REVIEW_ENABLED` | 启用大盘复盘 | `true` |
| `MARKET_REVIEW_REGION` | 大盘复盘市场区域：cn(A股)、us(美股)、both(两者)，us 适合仅关注美股的用户 | `cn` |
| `TRADING_DAY_CHECK_ENABLED` | 交易日检查：默认 `true`，非交易日跳过执行；设为 `false` 或使用 `--force-run` 可强制执行（Issue #373） | `true` |
| `SCHEDULE_ENABLED` | 启用定时任务 | `false` |
| `SCHEDULE_TIME` | 定时执行时间 | `18:00` |
| `LOG_DIR` | 日志目录 | `./logs` |

---

## Docker 部署

Dockerfile 使用多阶段构建，前端会在构建镜像时自动打包并内置到 `static/`。
如需覆盖静态资源，可挂载本地 `static/` 到容器内 `/app/static`。
项目已下线内置前端托管；运行中的 `server` 容器现在只提供 API 服务，无需再构建或挂载 WebUI 静态资源。

### 快速启动

```bash
# 1. 克隆仓库
git clone https://github.com/ZhuLinsen/daily_stock_analysis.git
cd daily_stock_analysis

# 2. 配置环境变量
cp .env.example .env
vim .env  # 填入 API Key 和配置

# 3. 启动容器
docker-compose -f ./docker/docker-compose.yml up -d server     # API 服务模式（推荐，提供 FastAPI 接口）
docker-compose -f ./docker/docker-compose.yml up -d analyzer   # 定时任务模式
docker-compose -f ./docker/docker-compose.yml up -d            # 同时启动两种模式

# 4. 访问 API
# http://localhost:8000/docs

# 5. 查看日志
docker-compose -f ./docker/docker-compose.yml logs -f server
```

### 运行模式说明

| 命令 | 说明 | 端口 |
|------|------|------|
| `docker-compose -f ./docker/docker-compose.yml up -d server` | API 服务模式，提供 FastAPI 接口 | 8000 |
| `docker-compose -f ./docker/docker-compose.yml up -d analyzer` | 定时任务模式，每日自动执行 | - |
| `docker-compose -f ./docker/docker-compose.yml up -d` | 同时启动两种模式 | 8000 |

### Docker Compose 配置

`docker-compose.yml` 使用 YAML 锚点复用配置：

```yaml
version: '3.8'

x-common: &common
  build:
    context: ..
    dockerfile: docker/Dockerfile
  restart: unless-stopped
  env_file:
    - ../.env
  environment:
    - TZ=Asia/Shanghai
  volumes:
    - ../data:/app/data
    - ../logs:/app/logs
    - ../reports:/app/reports
    - ../.env:/app/.env

services:
  # 定时任务模式
  analyzer:
    <<: *common
    container_name: stock-analyzer

  # FastAPI 模式
  server:
    <<: *common
    container_name: stock-server
    command: ["python", "main.py", "--serve-only", "--host", "0.0.0.0", "--port", "8000"]
    ports:
      - "8000:8000"
```

### 常用命令

```bash
# 查看运行状态
docker-compose -f ./docker/docker-compose.yml ps

# 查看日志
docker-compose -f ./docker/docker-compose.yml logs -f server

# 停止服务
docker-compose -f ./docker/docker-compose.yml down

# 重建镜像（代码更新后）
docker-compose -f ./docker/docker-compose.yml build --no-cache
docker-compose -f ./docker/docker-compose.yml up -d server
```

### 手动构建镜像

```bash
docker build -f docker/Dockerfile -t stock-analysis .
docker run -d --env-file .env -p 8000:8000 -v ./data:/app/data stock-analysis python main.py --serve-only --host 0.0.0.0 --port 8000
```

---

## 本地运行详细配置

### 安装依赖

```bash
# Python 3.10+ 推荐
pip install -r requirements.txt

# 或使用 conda
conda create -n stock python=3.10
conda activate stock
pip install -r requirements.txt
```

**智能导入依赖**：`pypinyin`（名称→代码拼音匹配）和 `openpyxl`（Excel .xlsx 解析）已包含在 `requirements.txt` 中，执行上述 `pip install -r requirements.txt` 时会自动安装。若使用智能导入（图片/CSV/Excel/剪贴板）功能，请确保依赖已正确安装；缺失时可能报 `ModuleNotFoundError`。

### 命令行参数

```bash
python main.py                        # 完整分析（个股 + 大盘复盘）
python main.py --market-review        # 仅大盘复盘
python main.py --no-market-review     # 仅个股分析
python main.py --stocks 600519,300750 # 指定股票
python main.py --dry-run              # 仅获取数据，不 AI 分析
python main.py --schedule             # 定时任务模式
python main.py --force-run            # 非交易日也强制执行（Issue #373）
python main.py --debug                # 调试模式（详细日志）
python main.py --workers 5            # 指定并发数
```

---

## 定时任务配置

### GitHub Actions 定时

编辑 `.github/workflows/daily_analysis.yml`:

```yaml
schedule:
  # UTC 时间，北京时间 = UTC + 8
  - cron: '0 10 * * 1-5'   # 周一到周五 18:00（北京时间）
```

常用时间对照：

| 北京时间 | UTC cron 表达式 |
|---------|----------------|
| 09:30 | `'30 1 * * 1-5'` |
| 12:00 | `'0 4 * * 1-5'` |
| 15:00 | `'0 7 * * 1-5'` |
| 18:00 | `'0 10 * * 1-5'` |
| 21:00 | `'0 13 * * 1-5'` |

#### GitHub Actions 非交易日手动运行（Issue #461 / #466）

`daily_analysis.yml` 支持两种控制方式：

- `TRADING_DAY_CHECK_ENABLED`：仓库级配置（`Settings → Secrets and variables → Actions`），默认 `true`
- `workflow_dispatch.force_run`：手动触发时的单次开关，默认 `false`

推荐优先级理解：

| 配置组合 | 非交易日行为 |
|---------|-------------|
| `TRADING_DAY_CHECK_ENABLED=true` + `force_run=false` | 跳过执行（默认行为） |
| `TRADING_DAY_CHECK_ENABLED=true` + `force_run=true` | 本次强制执行 |
| `TRADING_DAY_CHECK_ENABLED=false` + `force_run=false` | 始终执行（定时和手动都不检查交易日） |
| `TRADING_DAY_CHECK_ENABLED=false` + `force_run=true` | 始终执行 |

手动触发步骤：

1. 打开 `Actions → 每日股票分析 → Run workflow`
2. 选择 `mode`（`full` / `market-only` / `stocks-only`）
3. 若当天是非交易日且希望仍执行，将 `force_run` 设为 `true`
4. 点击 `Run workflow`

### 本地定时任务

内建的定时任务调度器支持每天在指定时间（默认 18:00）运行分析。

#### 命令行方式

```bash
# 启动定时模式（启动时立即执行一次，随后每天 18:00 执行）
python main.py --schedule

# 启动定时模式（启动时不执行，仅等待下次定时触发）
python main.py --schedule --no-run-immediately
```

> 说明：定时模式每次触发前都会重新读取当前保存的 `STOCK_LIST`。如果同时传入 `--stocks`，该参数不会锁定后续计划执行的股票列表；需要临时只跑指定股票时，请使用非定时的单次运行命令。
>
> 从 `python main.py --schedule`、`python main.py --serve --schedule` 或等价内置调度模式启动后，如果持久化 `.env` 或外部配置管理写入了新的 `SCHEDULE_TIME`，系统会在下一轮调度检查内自动重绑 daily job，无需重启进程；旧的执行时间不会继续保留。

#### 环境变量方式

你也可以通过环境变量配置定时行为（适用于 Docker 或 .env）：

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|:-------:|:-----:|
| `SCHEDULE_ENABLED` | 是否启用定时任务 | `false` | `true` |
| `SCHEDULE_TIME` | 每日执行时间 (HH:MM) | `18:00` | `09:30` |
| `SCHEDULE_RUN_IMMEDIATELY` | 启动服务时是否立即运行一次 | `true` | `false` |
| `TRADING_DAY_CHECK_ENABLED` | 交易日检查：非交易日跳过执行；设为 `false` 可强制执行 | `true` | `false` |

例如在 Docker 中配置：

```bash
# 设置启动时不立即分析
docker run -e SCHEDULE_ENABLED=true -e SCHEDULE_RUN_IMMEDIATELY=false ...
```

#### 交易日判断（Issue #373）

默认根据自选股市场（A 股 / 港股 / 美股）和 `MARKET_REVIEW_REGION` 判断是否为交易日：
- 使用 `exchange-calendars` 区分 A 股 / 港股 / 美股各自的交易日历（含节假日）
- 混合持仓时，每只股票只在其市场开市日分析，休市股票当日跳过
- 全部相关市场均为非交易日时，整体跳过执行（不启动 pipeline、不发推送）
- 断点续传和 `--dry-run` 的“数据已存在”判断共用同一套“最新可复用交易日”解析逻辑，不再直接使用服务器自然日
- `最新可复用交易日` 会按股票所属市场的本地时区解析：A 股使用 `Asia/Shanghai`，港股使用 `Asia/Hong_Kong`，美股使用 `America/New_York`
- 非交易日（周末 / 节假日）运行时，会回退到最近一个交易日检查本地数据；若该交易日数据已存在，则跳过重复抓取，否则继续补数
- 交易日盘中或收盘前运行时，会以上一个已完成交易日作为复用目标；交易日收盘后运行时，当日数据已存在则可直接跳过，不存在则继续抓取
- 覆盖方式：`TRADING_DAY_CHECK_ENABLED=false` 或 命令行 `--force-run`

#### 使用 Crontab

如果不想使用常驻进程，也可以使用系统的 Cron：

```bash
crontab -e
# 添加：0 18 * * 1-5 cd /path/to/project && python main.py
```

---

## 结果输出说明

- 报告文本仍由仓库生成。
- 本地 Markdown 报告仍可保存。
- 飞书云文档仍可作为结果承载方式保留。
- 如需消息投递，请由外部调用方自行处理。

---

## 数据源配置

系统默认使用 AkShare（免费），也支持其他数据源：

### AkShare（默认）
- 免费，无需配置
- 数据来源：东方财富爬虫

### Tushare Pro
- 需要注册获取 Token
- 更稳定，数据更全
- 设置 `TUSHARE_TOKEN`

### Baostock
- 免费，无需配置
- 作为备用数据源

### YFinance
- 免费，无需配置
- 支持美股/港股数据
- 美股历史数据与实时行情均统一使用 YFinance，以避免 akshare 美股复权异常导致的技术指标错误

### 当前数据源口径
- 当前运行时行情数据统一走 **Tushare**。
- 仓库不再自动回退到 Longbridge / YFinance / AkShare / TickFlow / efinance / pytdx / baostock 等旧数据源。
- 若当前 Tushare 能力、权限或市场覆盖不足，运行时会直接暴露该限制，而不是继续走旧兼容分支。

### 东财接口频繁失败时的处理

若日志出现 `RemoteDisconnected`、`push2his.eastmoney.com` 连接被关闭等，多为东财限流。建议：

1. 在 `.env` 中设置 `ENABLE_EASTMONEY_PATCH=true`
2. 将 `MAX_WORKERS=1` 降低并发
3. 若已配置 Tushare，可优先使用 Tushare 数据源

---

## 高级功能

### 港股支持

使用 `hk` 前缀指定港股代码：

```bash
STOCK_LIST=600519,hk00700,hk01810
```

### ETF 与指数分析

针对指数跟踪型 ETF 和美股指数（如 VOO、QQQ、SPY、510050、SPX、DJI、IXIC），分析仅关注**指数走势、跟踪误差、市场流动性**，不纳入基金管理人/发行方的公司层面风险（诉讼、声誉、高管变动等）。风险警报与业绩预期均基于指数成分股整体表现，避免将基金公司新闻误判为标的本身利空。详见 Issue #274。

### 多模型切换

配置多个模型，系统自动切换：

```bash
# Gemini（主力）
GEMINI_API_KEY=xxx
GEMINI_MODEL=gemini-3-flash-preview

# OpenAI 兼容（备选）
OPENAI_API_KEY=xxx
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
# 思考模式：deepseek-reasoner、deepseek-r1、qwq 等自动识别；deepseek-chat 系统按模型名自动启用
```

### 高级模型路由（底层由 LiteLLM 驱动）

详见 [LLM 配置指南](LLM_CONFIG_GUIDE.md)。默认使用时你只需要理解主模型、备选模型和模型渠道；如果进入这一节，说明你要直接使用底层 [LiteLLM](https://github.com/BerriAI/litellm) 路由能力，无需单独启动 Proxy 服务。

**两层机制**：同一模型多 Key 轮换（Router）与跨模型降级（Fallback）分层独立，互不干扰。

**多 Key + 跨模型降级配置示例**：

```env
# 主模型：3 个 Gemini Key 轮换，任一 429 时 Router 自动切换下一个 Key
GEMINI_API_KEYS=key1,key2,key3
LITELLM_MODEL=gemini/gemini-3-flash-preview

# 跨模型降级：主模型全部 Key 均失败时，按序尝试 Claude → GPT
# 需配置对应 API Key：ANTHROPIC_API_KEY、OPENAI_API_KEY
LITELLM_FALLBACK_MODELS=anthropic/claude-3-5-sonnet-20241022,openai/gpt-4o-mini
```

**预期行为**：首次请求用 `key1`；若 429，Router 下次用 `key2`；若 3 个 Key 均不可用，则切换到 Claude，再失败则切换到 GPT。

> ⚠️ `LITELLM_MODEL` 必须包含 provider 前缀（如 `gemini/`、`anthropic/`、`openai/`），
> 否则系统无法识别应使用哪组 API Key。旧格式的 `GEMINI_MODEL`（无前缀）仅用于未配置 `LITELLM_MODEL` 时的自动推断。

**依赖说明**：`requirements.txt` 中保留 `openai>=1.0.0`，因 LiteLLM 内部依赖 OpenAI SDK 作为统一接口；显式保留可确保版本兼容性，用户无需单独配置。

**视觉模型（图片提取股票代码）**：详见 [LLM 配置指南 - Vision](LLM_CONFIG_GUIDE.md#41-vision-模型图片识别股票代码)。

从图片提取股票代码（如 `/api/v1/stocks/extract-from-image`）使用统一视觉模型接入，底层采用 LiteLLM Vision 与 OpenAI `image_url` 格式，支持 Gemini、Claude、OpenAI、DeepSeek 等 Vision-capable 模型。返回 `items`（code、name、confidence）及兼容的 `codes` 数组。

> 兼容性说明：`/api/v1/stocks/extract-from-image` 响应在原 `codes` 基础上新增 `items` 字段。若下游客户端使用严格 JSON Schema 且不接受未知字段，请同步更新 schema。

**智能导入**：除图片外，还支持 CSV/Excel 文件及剪贴板粘贴（`/api/v1/stocks/parse-import`），自动解析代码/名称列，名称→代码解析支持本地映射、拼音匹配及 AkShare 在线 fallback。依赖 `pypinyin`（拼音匹配）和 `openpyxl`（Excel 解析），已包含在 `requirements.txt` 中。

- **AkShare 名称解析缓存**：名称→代码解析使用 AkShare 在线 fallback 时，结果缓存 1 小时（TTL），避免频繁请求；首次调用或缓存过期后会自动刷新。
- **CSV/Excel 列名**：支持 `code`、`股票代码`、`代码`、`name`、`股票名称`、`名称` 等（不区分大小写）；无表头时默认第 1 列为代码、第 2 列为名称。
- **常见解析失败**：文件过大（>2MB）、编码非 UTF-8/GBK、Excel 工作表为空或损坏、CSV 分隔符/列数不一致时，API 会返回具体错误提示。

- **模型优先级**：`VISION_MODEL` > `LITELLM_MODEL` > 根据已有 API Key 推断（`OPENAI_VISION_MODEL` 已废弃，请改用 `VISION_MODEL`）
- **Provider 回退**：主模型失败时，按 `VISION_PROVIDER_PRIORITY`（默认 `gemini,anthropic,openai`）自动切换到下一个可用 provider
- **主模型不支持 Vision 时**：若主模型为 DeepSeek 等非 Vision 模型，可显式配置 `VISION_MODEL=openai/gpt-4o` 或 `gemini/gemini-2.0-flash` 供图片提取使用
- **配置校验**：若配置了 `VISION_MODEL` 但未配置对应 provider 的 API Key，启动时会输出 warning，图片提取功能将不可用

### 调试模式

```bash
python main.py --debug
```

日志文件位置：
- 常规日志：`logs/stock_analysis_YYYYMMDD.log`
- 调试日志：`logs/stock_analysis_debug_YYYYMMDD.log`

### SQLite 写入稳态配置

默认文件型 SQLite 会在连接建立时启用 `WAL` 并设置 `busy_timeout`，`save_daily_data()` 也已改为按 `(code, date)` 批量原子 upsert，以降低批量更新和并发回写时的锁竞争。

如需调整，可在 `.env` 中设置：

| 变量 | 默认值 | 说明 |
|------|-------|------|
| `SQLITE_WAL_ENABLED` | `true` | 文件型 SQLite 是否启用 `journal_mode=WAL` |
| `SQLITE_BUSY_TIMEOUT_MS` | `5000` | SQLite 等锁超时（毫秒） |
| `SQLITE_WRITE_RETRY_MAX` | `3` | 遇到 `database is locked` / `database table is locked` 时的最大重试次数 |
| `SQLITE_WRITE_RETRY_BASE_DELAY` | `0.1` | 写入重试基础退避时间（秒，按指数退避递增） |

---

## 回测功能

回测模块自动对历史 AI 分析记录进行事后验证，评估分析建议的准确性。

### 工作原理

1. 选取已过冷却期（默认 14 天）的 `AnalysisHistory` 记录
2. 获取分析日之后的日线数据（前向 K 线）
3. 根据操作建议推断预期方向，与实际走势对比
4. 评估止盈/止损命中情况，模拟执行收益
5. 汇总为整体和单股两个维度的表现指标

### 操作建议映射

| 操作建议 | 仓位推断 | 预期方向 | 胜利条件 |
|---------|---------|---------|---------|
| 买入/加仓/strong buy | long | up | 涨幅 ≥ 中性带 |
| 卖出/减仓/strong sell | cash | down | 跌幅 ≥ 中性带 |
| 持有/hold | long | not_down | 未显著下跌 |
| 观望/等待/wait | cash | flat | 价格在中性带内 |

### 配置

在 `.env` 中设置以下变量（均有默认值，可选）：

| 变量 | 默认值 | 说明 |
|------|-------|------|
| `BACKTEST_ENABLED` | `true` | 是否在每日分析后自动运行回测 |
| `BACKTEST_EVAL_WINDOW_DAYS` | `10` | 评估窗口（交易日数） |
| `BACKTEST_MIN_AGE_DAYS` | `14` | 仅回测 N 天前的记录，避免数据不完整 |
| `BACKTEST_ENGINE_VERSION` | `v1` | 引擎版本号，升级逻辑时用于区分结果 |
| `BACKTEST_NEUTRAL_BAND_PCT` | `2.0` | 中性区间阈值（%），±2% 内视为震荡 |

### 自动运行

回测在每日分析流程完成后自动触发（非阻塞，失败不影响主分析结果落盘）。也可通过 API 手动触发。

### 评估指标

| 指标 | 说明 |
|------|------|
| `direction_accuracy_pct` | 方向预测准确率（预期方向与实际一致） |
| `win_rate_pct` | 胜率（胜 / (胜+负)，不含中性） |
| `avg_stock_return_pct` | 平均股票收益率 |
| `avg_simulated_return_pct` | 平均模拟执行收益率（含止盈止损退出） |
| `stop_loss_trigger_rate` | 止损触发率（仅统计配置了止损的记录） |
| `take_profit_trigger_rate` | 止盈触发率（仅统计配置了止盈的记录） |

---

## FastAPI API 服务

FastAPI 提供 RESTful API 服务，支持配置管理和触发分析。

### 启动方式

| 命令 | 说明 |
|------|------|
| `python main.py --serve` | 启动 API 服务 + 执行一次完整分析 |
| `python main.py --serve-only` | 仅启动 API 服务，手动触发分析 |

### 功能特性

- 📝 **配置管理** - 查看/修改自选股列表
- 🚀 **快速分析** - 通过 API 接口触发分析
- 📊 **实时进度** - 分析任务状态实时更新，支持多任务并行；普通分析链路在进入 LLM 阶段后会优先尝试 LiteLLM 流式生成，并通过任务 SSE 回灌更细粒度的 `message/progress`
- 📈 **回测验证** - 评估历史分析准确率，查询方向胜率与模拟收益
- 🔗 **API 文档** - 访问 `/docs` 查看 Swagger UI

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/analysis/analyze` | POST | 触发股票分析 |
| `/api/v1/analysis/tasks` | GET | 查询任务列表 |
| `/api/v1/analysis/tasks/stream` | GET (SSE) | 订阅任务实时状态流 |
| `/api/v1/analysis/status/{task_id}` | GET | 查询任务状态 |
| `/api/v1/history` | GET | 查询分析历史 |
| `/api/v1/backtest/run` | POST | 触发回测 |
| `/api/v1/backtest/results` | GET | 查询回测结果（分页） |
| `/api/v1/backtest/performance` | GET | 获取整体回测表现 |
| `/api/v1/backtest/performance/{code}` | GET | 获取单股回测表现 |
| `/api/v1/stocks/extract-from-image` | POST | 从图片提取股票代码（multipart，超时 60s） |
| `/api/v1/stocks/parse-import` | POST | 解析 CSV/Excel/剪贴板（multipart file 或 JSON `{"text":"..."}`，文件≤2MB，文本≤100KB） |
| `/api/health` | GET | 健康检查 |
| `/docs` | GET | API Swagger 文档 |

> 说明：`POST /api/v1/analysis/analyze` 在 `async_mode=false` 时仅支持单只股票；批量 `stock_codes` 需使用 `async_mode=true`。异步 `202` 响应对单股返回 `task_id`，对批量返回 `accepted` / `duplicates` 汇总结构。

> 进度流说明：`GET /api/v1/analysis/tasks/stream` 除 `task_created / task_started / task_completed / task_failed` 外，新增 `task_progress` 事件。普通分析链路会在“行情准备 / 新闻检索 / 上下文整理 / LLM 生成 / 报告保存”等阶段持续更新 `progress` 与 `message`。LiteLLM 流式返回仅在服务端累积完整文本，最终 JSON 解析成功后才会持久化历史报告；若流式在首个 chunk 前不可用，会自动回退到原非流式调用；若已产生部分 chunk 后失败，系统先尝试同模型非流式重试，失败后再按既有主模型->备用模型顺序继续尝试。  
> 如果任务进度回调异常，主链路不会中断，系统会提升告警为 warning 级别并在服务端日志中输出完整异常，便于排查 SSE 推送断点。
>  
> 说明：该特性属于运行时 SSE 与回退链路细节，优先记录于完整指南（`full-guide*.md`），不在 `README.md` 中展开详细行为分支。

**调用示例**：
```bash
# 健康检查
curl http://127.0.0.1:8000/api/health

# 触发分析（A股）
curl -X POST http://127.0.0.1:8000/api/v1/analysis/analyze \
  -H 'Content-Type: application/json' \
  -d '{"stock_code": "600519"}'

# 查询任务状态
curl http://127.0.0.1:8000/api/v1/analysis/status/<task_id>

# 触发回测（全部股票）
curl -X POST http://127.0.0.1:8000/api/v1/backtest/run \
  -H 'Content-Type: application/json' \
  -d '{"force": false}'

# 触发回测（指定股票）
curl -X POST http://127.0.0.1:8000/api/v1/backtest/run \
  -H 'Content-Type: application/json' \
  -d '{"code": "600519", "force": false}'

# 查询整体回测表现
curl http://127.0.0.1:8000/api/v1/backtest/performance

# 查询单股回测表现
curl http://127.0.0.1:8000/api/v1/backtest/performance/600519

# 分页查询回测结果
curl "http://127.0.0.1:8000/api/v1/backtest/results?page=1&limit=20"
```

### 自定义配置

修改默认端口或允许局域网访问：

```bash
python main.py --serve-only --host 0.0.0.0 --port 8888
```

### 支持的股票代码格式

| 类型 | 格式 | 示例 |
|------|------|------|
| A股 | 6位数字 | `600519`、`000001`、`300750` |
| 北交所 | 8/4/92 开头 6 位 | `920748`、`838163`、`430047` |
| 港股 | hk + 5位数字 | `hk00700`、`hk09988` |
| 美股 | 1-5 字母（可选 .X 后缀） | `AAPL`、`TSLA`、`BRK.B` |
| 美股指数 | SPX/DJI/IXIC 等 | `SPX`、`DJI`、`NASDAQ`、`VIX` |

### 注意事项

- 浏览器访问 API 文档：`http://127.0.0.1:8000/docs`（或您配置的端口）
- 分析完成后会生成本地报告；外部渠道投递由调用方自行处理
- 此功能在 GitHub Actions 环境中会自动禁用
- 另见 [openclaw Skill 集成指南](openclaw-skill-integration.md)

---

## 常见问题

### Q: 长报告怎么承载？
A: 当前建议使用本地 Markdown 报告或飞书云文档；消息投递与分段由外部调用方自行处理。

### Q: 数据获取失败？
A: AkShare 使用爬虫机制，可能被临时限流。系统已配置重试机制，一般等待几分钟后重试即可。

### Q: 如何添加自选股？
A: 修改 `STOCK_LIST` 环境变量，多个代码用逗号分隔。

### Q: GitHub Actions 没有执行？
A: 检查是否启用了 Actions，以及 cron 表达式是否正确（注意是 UTC 时间）。

---

更多问题请 [提交 Issue](https://github.com/ZhuLinsen/daily_stock_analysis/issues)

## Portfolio P0 PR1 (Core Ledger and Snapshot)

### Scope
- Core portfolio domain models:
  - account, trade, cash ledger, corporate action, position cache, lot cache, daily snapshot, fx cache
- Core service capability:
  - account CRUD
  - event writes
  - read-time replay snapshot for one account or all active accounts

### Accounting semantics
- Cost method:
  - `fifo` (default)
  - `avg`
- Same-day event ordering:
  - `cash -> corporate action -> trade`
- Corporate action effective-date rule:
  - `effective_date` is treated as effective before market trading on that day.

### Error and stability semantics
- `trade_uid` unique conflict returns `409` (API conflict semantics).
- sell writes now validate available quantity before insert; oversell is rejected with `409 portfolio_oversell`.
- portfolio source-event writes now serialize through a SQLite write lock; direct write/delete endpoints may return `409 portfolio_busy` when another ledger mutation is in progress.
- Snapshot write path is atomic for positions/lots/daily snapshot.
- FX conversion keeps fail-open behavior (fallback 1:1 with stale marker) to avoid pipeline interruption.

### Test coverage in PR1
- FIFO/AVG partial sell replay
- Dividend and split replay
- Same-day ordering (dividend/trade, split/trade)
- API account/event/snapshot contract
- API duplicate trade_uid conflict

## Portfolio P0 PR2 (Import and Risk)

### CSV import
- Supported broker ids: `huatai`, `citic`, `cmb`.
- Unified workflow: parse CSV into normalized records, then commit into portfolio trades.
- Commit remains row-by-row instead of one long transaction; busy rows count into `failed_count` rather than converting the whole request to `409`.
- Dedup policy:
  - First key: `trade_uid` (account-scoped)
  - Fallback key: deterministic hash of date/symbol/side/qty/price/fee/tax/currency

### Risk report
- Concentration monitoring: top position weight alert by config threshold.
- Drawdown monitoring: max/current drawdown computed from daily snapshots.
- Stop-loss proximity warning: mark near-alert and triggered items with threshold echo.

### FX fail-open
- FX refresh first tries online source (YFinance).
- On online failure, fallback to latest cached rate and mark `is_stale=true`.
- Main snapshot/risk pipeline stays available even when online FX fetch is unavailable.

## Portfolio P0 PR3 (Agent/API Consumption)

### API consumption
- Portfolio snapshot and risk data are consumed via API/service paths.
- Data sources:
  - `GET /api/v1/portfolio/snapshot`
  - `GET /api/v1/portfolio/risk`
- Suitable for Agent/API clients and downstream integrations.

### Agent tool
- Added `get_portfolio_snapshot` data tool for account-aware LLM suggestions.
- Default behavior:
  - compact summary output (token-friendly)
  - includes optional compact risk block
- Optional parameters:
  - `account_id`
  - `cost_method` (`fifo` / `avg`)
  - `as_of` (`YYYY-MM-DD`)
  - `include_positions` (default `false`)
  - `include_risk` (default `true`)

### Stability and compatibility
- New capability is additive only; no removal of existing keys/routes.
- Fail-open semantics:
  - If risk block fails, snapshot is still returned.
  - If portfolio module is unavailable, tool returns structured `not_supported`.

## Portfolio P0 PR4 (Gap Closure)

### API query closure
- Added event query endpoints:
  - `GET /api/v1/portfolio/trades`
  - `GET /api/v1/portfolio/cash-ledger`
  - `GET /api/v1/portfolio/corporate-actions`
- Added event delete endpoints:
  - `DELETE /api/v1/portfolio/trades/{trade_id}`
  - `DELETE /api/v1/portfolio/cash-ledger/{entry_id}`
  - `DELETE /api/v1/portfolio/corporate-actions/{action_id}`
- Unified query parameters:
  - `account_id`, `date_from`, `date_to`, `page`, `page_size`
- Trade/cash/corporate-action specific filters:
  - trades: `symbol`, `side`
  - cash-ledger: `direction`
  - corporate-actions: `symbol`, `action_type`
- Unified response shape:
  - `items`, `total`, `page`, `page_size`

### CSV import framework
- Reworked parser logic into extensible parser registry.
- Built-in adapters remain: `huatai`, `citic`, `cmb` with alias mapping.
- Added parser discovery endpoint:
  - `GET /api/v1/portfolio/imports/csv/brokers`

### Web closure
- `/portfolio` page now includes:
  - inline account creation entry with empty-state guide and auto-switch to created account
  - manual event entry forms: trade / cash / corporate action
  - CSV parse + commit operations (supports `dry_run`)
  - event list panel with filters and pagination
  - single-account scoped event deletion for trade / cash / corporate action correction
  - broker selector fallback to built-in brokers (`huatai/citic/cmb`) when broker list API fails or returns empty
  - FX status card manual refresh action that calls existing `POST /api/v1/portfolio/fx/refresh`; if upstream FX fetch fails, the page may still show stale after refresh and will explain the result inline
  - when `PORTFOLIO_FX_UPDATE_ENABLED=false`, the refresh API now returns explicit disabled status and the page will show “汇率在线刷新已被禁用” instead of “当前范围无可刷新的汇率对”

### Risk sector concentration semantics
- Added `sector_concentration` in `GET /api/v1/portfolio/risk`.
- Mapping rules:
  - CN positions try board mapping from `get_belong_boards`.
  - Non-CN or mapping failure falls back to `UNCLASSIFIED`.
  - Uses single primary board per symbol to avoid duplicate weighting.
- Fail-open:
  - board lookup errors do not interrupt risk response.
  - response returns coverage/error details for explainability.
