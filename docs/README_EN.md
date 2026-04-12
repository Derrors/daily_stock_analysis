<div align="center">

# AI Stock Analysis System

[![GitHub stars](https://img.shields.io/github/stars/ZhuLinsen/daily_stock_analysis?style=social)](https://github.com/ZhuLinsen/daily_stock_analysis/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/)

<p>
  <a href="https://trendshift.io/repositories/18527" target="_blank"><img src="https://trendshift.io/api/badge/repositories/18527" alt="ZhuLinsen%2Fdaily_stock_analysis | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
  <a href="https://hellogithub.com/repository/ZhuLinsen/daily_stock_analysis" target="_blank"><img src="https://api.hellogithub.com/v1/widgets/recommend.svg?rid=6daa16e405ce46ed97b4a57706aeb29f&claim_uid=pfiJMqhR9uvDGlT&theme=neutral" alt="Featured｜HelloGitHub" style="width: 250px; height: 54px;" width="250" height="54" /></a>
</p>

**Agent-first stock-analysis backend core for A-shares / Hong Kong / US stocks**

Run analysis → generate a decision dashboard → persist local reports or optional Feishu cloud docs → let your outer caller deliver results

**Docker / local deployment** · API-first / skill-friendly

[**Quick Start**](#-quick-start) · [**Key Features**](#-key-features) · [**Output Examples**](#-output-examples) · [**Full Guide**](./full-guide_EN.md) · [**FAQ**](./FAQ_EN.md) · [**Contributing**](./CONTRIBUTING_EN.md) · [**All Docs**](./INDEX_EN.md)

English | [简体中文](../README.md) | [繁體中文](README_CHT.md)

</div>

## 💖 Sponsors

<div align="center">
  <a href="https://serpapi.com/baidu-search-api?utm_source=github_daily_stock_analysis" target="_blank">
    <img src="../sources/serpapi_banner_en.png" alt="Easily scrape real-time financial news data from search engines - SerpApi" height="160">
  </a>
</div>
<br>

## ✨ Key Features

| Module | Feature | Description |
|--------|---------|-------------|
| AI | Decision Dashboard | One-sentence conclusion + precise entry/exit levels + action checklist |
| Analysis | Multi-dimensional Analysis | Technicals + chip distribution + sentiment + real-time quotes |
| Market | Global Markets | A-shares, Hong Kong stocks, US stocks |
| Search | Smart Autocomplete (MVP) | **[Beta]** Home search supports code/name/pinyin/aliases; the local index now covers A-shares, Hong Kong, and US stocks and can be refreshed from Tushare or AkShare data |
| Review | Market Review | Daily overview, sectors, northbound capital flow |
| Intel | Announcement + Capital Flow Intelligence | IntelAgent now also pulls listed-company announcements (SSE/SZSE/CNINFO) and A-share main-force capital flow, and exposes `capital_flow_signal` (`inflow/outflow/neutral/not_available`) for flow direction context |
| Backtest | AI Backtest Validation | Auto-evaluate historical analysis accuracy, with a 1-day next-session validation view for AI prediction vs actual move and accuracy |
| Agent Q&A | Strategy Chat | Multi-turn strategy chat with 11 built-in trading strategies (internally loaded as skills) (API/Skill) |
| Output Boundary | Report-first | Local markdown reports and optional Feishu cloud docs; message delivery is handled outside this repo |
| Automation | Scheduled Runs | Docker, local cron, or any external scheduler can drive runs |

> The Backtest page now includes a 1-day next-session validation view. You can filter by stock code and analysis date range to compare the original AI prediction with the next trading day close and inspect the filtered accuracy rate. This is based on historical analysis plus `eval_window_days=1` backtest data, not real trade execution logs.

### Tech Stack & Data Sources

| Type | Supported |
|------|----------|
| LLMs | Gemini (free), OpenAI-compatible, DeepSeek, Qwen, Claude, Ollama |
| Market Data | Tushare (the only retained runtime market-data provider after simplification) |
| News Search | Tavily, SerpAPI, Bocha, Brave |

> **Current data-source boundary:** runtime market data is now simplified to **Tushare only**; news search keeps **Bocha / Tavily / Brave / SerpAPI**. Historical provider implementations may remain in the repo temporarily, but the main runtime no longer initializes them.

### Built-in Trading Rules

| Rule | Description |
|------|-------------|
| No chasing highs | Auto warn when deviation > 5% |
| Trend trading | Bull alignment: MA5 > MA10 > MA20 |
| Precise levels | Entry, stop loss, target |
| Checklist | Each condition marked as Pass / Watch / Fail |

## 🚀 Quick Start

### Option 1: Local Deployment

#### 1. Clone Repository

```bash
git clone https://github.com/ZhuLinsen/daily_stock_analysis.git
cd daily_stock_analysis
```

#### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Configure Environment Variables

```bash
# Copy configuration template
cp .env.example .env

# Edit .env file
nano .env  # or use any editor
```

Configure the following:

```bash
# AI Model (Choose one)
GEMINI_API_KEY=your_gemini_api_key_here

# Stock Watchlist (Mixed markets supported)
STOCK_LIST=600519,AAPL,hk00700

# Result carrying (optional)
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=secret_xxx
FEISHU_FOLDER_TOKEN=fldr_xxx

# News Search (Optional)
TAVILY_API_KEYS=your_tavily_key
```

#### 4. Run

```bash
# One-time analysis
python main.py

# Scheduled mode (runs daily at 18:00)
python main.py --schedule

# Analyze specific stocks
python main.py --stocks AAPL,TSLA,GOOGL

# Market review only
python main.py --market-review
```

### API Endpoints

| Endpoint | Method | Description |
|------|------|------|
| `/` | GET | Configuration page |
| `/health` | GET | Health check |
| `/analysis?code=xxx` | GET | Trigger async analysis for a single stock |
| `/analysis/history` | GET | Query analysis history records |
| `/tasks` | GET | Query all task statuses |
| `/task?id=xxx` | GET | Query a single task status |

---

## 📦 Result Handling Boundary

Notification delivery has been removed from the repository. Use the generated report text / local markdown files / optional Feishu cloud document as outputs, and let your outer caller deliver messages.

## 🎨 Output Examples

### Decision Dashboard Format

```markdown
# 🎯 2026-01-24 Decision Dashboard

> Total **3** stocks analyzed | 🟢Buy:1 🟡Hold:1 🔴Sell:1

## 📊 Analysis Summary

🟢 **AAPL(Apple Inc.)**: Buy | Score 85 | Strong Bullish
🟡 **600519(Kweichow Moutai)**: Hold | Score 65 | Bullish
🔴 **TSLA(Tesla)**: Sell | Score 35 | Bearish

---

## 🟢 AAPL (Apple Inc.)

### 📰 Key Information
**💭 Sentiment**: Positive news on iPhone 16 sales
**📊 Earnings**: Q1 2024 earnings beat expectations

### 📌 Core Conclusion

**🟢 Buy** | Strong Bullish

> **One-sentence Decision**: Strong technical setup with positive catalyst, ideal entry point

⏰ **Time Sensitivity**: Within this week

| Position | Action |
|----------|--------|
| 🆕 **No Position** | Buy at pullback |
| 💼 **With Position** | Continue holding |

### 📊 Data Perspective

**MA Alignment**: MA5>MA10>MA20 | Bull Trend: ✅ Yes | Trend Strength: 85/100

| Price Metrics | Value |
|--------------|-------|
| Current | $185.50 |
| MA5 | $183.20 |
| MA10 | $180.50 |
| MA20 | $177.80 |
| Bias (MA5) | +1.26% ✅ Safe |
| Support | $183.20 |
| Resistance | $190.00 |

**Volume**: Ratio 1.8 (Moderate increase) | Turnover 2.3%
💡 *Volume confirms bullish momentum*

### 🎯 Action Plan

**📍 Sniper Points**

| Level Type | Price |
|-----------|-------|
| 🎯 Ideal Entry | $183-184 |
| 🔵 Secondary Entry | $180-181 |
| 🛑 Stop Loss | $177 |
| 🎊 Target | $195 |

**💰 Position Sizing**: 20-30% of portfolio
- Entry Plan: Enter in 2-3 batches
- Risk Control: Strict stop loss at $177

**✅ Checklist**

- ✅ Bull trend confirmed
- ✅ Price near MA5 support
- ✅ Volume confirms trend
- ⚠️ Monitor market volatility

---
```

---

## 🔧 Advanced Configuration

### Environment Variables

```bash
# === Analysis Behavior ===
ANALYSIS_DELAY=10              # Delay between analysis (seconds) to avoid API rate limit
REPORT_TYPE=full               # Report type: simple/full

# === Schedule ===
SCHEDULE_ENABLED=true          # Enable scheduled task
SCHEDULE_TIME=18:00            # Daily run time (HH:MM, 24-hour format)
MARKET_REVIEW_ENABLED=true     # Enable market review

# === Data Source ===
TUSHARE_TOKEN=your_token       # Tushare Pro (priority data source if configured)

# === System ===
MAX_WORKERS=3                  # Concurrent threads (3 recommended to avoid blocking)
DEBUG=false                    # Enable debug logging
```

---

## 🧩 FastAPI Web Service (Optional)

Enable the FastAPI service for configuration management and triggering analysis when running locally.

### Startup Methods

| Command | Description |
|---------|-------------|
| `python main.py --serve` | Start API service + run full analysis once |
| `python main.py --serve-only` | Start API service only, manually trigger analysis |

- URL: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`

### Features

- 📝 **Configuration Management** - View/modify watchlist
- 🚀 **Quick Analysis** - Trigger analysis via API
- 📊 **Real-time Progress** - Analysis task status updates in real-time, supports parallel tasks
- 🤖 **Agent Strategy Chat** - Use `/api/v1/agent/chat*` endpoints for multi-turn strategy Q&A, session history, and deep-research style follow-ups (enable with `AGENT_MODE=true`)
- 🧩 **Intel compatibility** - `capital_flow_signal` is an additive Intel output field; clients that do not consume it can ignore it safely, while existing fields such as `risk_alerts` and `positive_catalysts` remain unchanged.
- 📈 **Backtest Validation** - Evaluate historical analysis accuracy, query direction win rate and simulated returns

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analysis/analyze` | POST | Trigger stock analysis |
| `/api/v1/analysis/tasks` | GET | Query task list |
| `/api/v1/analysis/status/{task_id}` | GET | Query task status |
| `/api/v1/history` | GET | Query analysis history |
| `/api/v1/backtest/run` | POST | Trigger backtest |
| `/api/v1/backtest/results` | GET | Query backtest results (paginated) |
| `/api/v1/backtest/performance` | GET | Get overall backtest performance |
| `/api/v1/backtest/performance/{code}` | GET | Get per-stock backtest performance |
| `/api/v1/agent/skills` | GET | Get available built-in/custom strategy skills |
| `/api/v1/agent/chat/stream` | POST (SSE) | Stream multi-turn Agent strategy chat |
| `/api/health` | GET | Health check |

> Note: `POST /api/v1/analysis/analyze` supports only one stock when `async_mode=false`; batch `stock_codes` requires `async_mode=true`. The async `202` response returns a single `task_id` for one stock, or an `accepted` / `duplicates` summary for batch requests.

> For detailed instructions, see [Full Guide - API Service](./full-guide_EN.md#fastapi-api-service)

---


## 📖 Documentation

- [Complete Configuration Guide](./full-guide_EN.md)
- [FAQ](./FAQ_EN.md)
- [Deployment Guide](DEPLOY_EN.md)
- [Feishu Webhook Setup](bot/feishu-bot-config.md)

---

## ☕ Support the Project

| Alipay | WeChat Pay | Xiaohongshu |
| :---: | :---: | :---: |
| <img src="../sources/alipay.jpg" width="200" alt="Alipay"> | <img src="../sources/wechatpay.jpg" width="200" alt="WeChat Pay"> | <img src="../sources/xiaohongshu.png" width="200" alt="Xiaohongshu"> |

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⭐ Star History
**Made with ❤️ by AI enthusiasts | Star ⭐ this repo if you find it useful!**


<a href="https://star-history.com/#ZhuLinsen/daily_stock_analysis&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date" />
 </picture>
</a>

## ⚠️ Disclaimer

This tool is for **informational and educational purposes only**. The analysis results are generated by AI and should not be considered as investment advice. Stock market investments carry risk, and you should:

- Do your own research before making investment decisions
- Understand that past performance does not guarantee future results
- Only invest money you can afford to lose
- Consult with a licensed financial advisor for personalized advice

The developers of this tool are not liable for any financial losses resulting from the use of this software.

---

## 🙏 Acknowledgments

- [AkShare](https://github.com/akfamily/akshare) - Stock data source
- [Google Gemini](https://ai.google.dev/) - AI analysis engine
- [Tavily](https://tavily.com/) - News search API
- All contributors who helped improve this project

---

## 📞 Contact

- GitHub Issues: [Report bugs or request features](https://github.com/ZhuLinsen/daily_stock_analysis/issues)
- Discussions: [Join discussions](https://github.com/ZhuLinsen/daily_stock_analysis/discussions)
- Email: zhuls345@gmail.com

----
