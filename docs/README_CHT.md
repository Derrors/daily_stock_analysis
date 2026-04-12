<div align="center">

# 股票智能分析系統

[![GitHub stars](https://img.shields.io/github/stars/ZhuLinsen/daily_stock_analysis?style=social)](https://github.com/ZhuLinsen/daily_stock_analysis/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/)

<p>
  <a href="https://trendshift.io/repositories/18527" target="_blank"><img src="https://trendshift.io/api/badge/repositories/18527" alt="ZhuLinsen%2Fdaily_stock_analysis | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
  <a href="https://hellogithub.com/repository/ZhuLinsen/daily_stock_analysis" target="_blank"><img src="https://api.hellogithub.com/v1/widgets/recommend.svg?rid=6daa16e405ce46ed97b4a57706aeb29f&claim_uid=pfiJMqhR9uvDGlT&theme=neutral" alt="Featured｜HelloGitHub" style="width: 250px; height: 54px;" width="250" height="54" /></a>
</p>

**面向 Agent / skill / API 的 A股/港股/美股股票分析後端內核**

執行分析 → 生成決策儀表盤 → 落本地報告或可選飛書雲文檔 → 由外部調用方自行投遞結果

**Docker / 本地部署可用** · API-first / skill-friendly

[**功能特性**](#-功能特性) · [**快速開始**](#-快速開始) · [**輸出示例**](#-輸出示例) · [**完整指南**](./full-guide.md) · [**常見問題**](./FAQ.md) · [**更新日誌**](./CHANGELOG.md)

 繁體中文 | [English](README_EN.md) | [简体中文](../README.md)

</div>

## 💖 贊助商 (Sponsors)

<div align="center">
  <a href="https://serpapi.com/baidu-search-api?utm_source=github_daily_stock_analysis" target="_blank">
    <img src="../sources/serpapi_banner_zh.png" alt="輕鬆抓取搜尋引擎上的即時金融新聞數據 - SerpApi" height="160">
  </a>
</div>
<br>

## ✨ 功能特性

| 模組 | 功能 | 說明 |
|------|------|------|
| AI | 決策儀表盤 | 一句話核心結論 + 精確買賣點位 + 操作檢查清單 |
| 分析 | 多維度分析 | 技術面 + 籌碼分布 + 輿情情報 + 實時行情 |
| 市場 | 全球市場 | 支援 A股、港股、美股 |
| 補全 | 智慧補全 (MVP) | **[測試階段]** 首頁搜尋框支援代碼 / 名稱 / 拼音 / 別名聯想；本地索引已覆蓋 A股、港股、美股，並可透過 Tushare 或 AkShare 重新生成 |
| 復盤 | 大盤復盤 | 每日市場概覽、板塊漲跌、北向資金 |
| 回測 | AI 回測驗證 | 自動評估歷史分析準確率，方向勝率、止盈止損命中率 |
| **Agent 問股** | **策略對話** | **多輪策略問答，支援 11 種內建策略（API/Skill）** |
| 輸出邊界 | 報告優先 | 本地 Markdown 報告與可選飛書雲文檔承載；消息投遞由倉庫外調用方處理 |
| 自動化 | 定時運行 | Docker / 本地 cron / 外部調度器均可接入 |

### 技術棧與數據來源

| 類型 | 支援 |
|------|------|
| AI 模型 | Gemini（免費）、OpenAI 兼容、DeepSeek、通義千問、Claude、Ollama |
| 行情數據 | Tushare（目前精簡運行時唯一保留的行情資料源） |
| 新聞搜索 | Tavily、SerpAPI、Bocha、Brave |

> **目前資料源邊界**：運行時行情資料已收斂為 **Tushare only**；新聞搜索僅保留 **Bocha / Tavily / Brave / SerpAPI**。其餘歷史資料源實作後續可再做實體清理，但主鏈目前已不再初始化它們。

### 內建交易紀律

| 規則 | 說明 |
|------|------|
| 嚴禁追高 | 乖離率 > 5% 自動提示風險 |
| 趨勢交易 | MA5 > MA10 > MA20 多頭排列 |
| 精確點位 | 買入價、止損價、目標價 |
| 檢查清單 | 每項條件以「符合 / 注意 / 不符合」標記 |

## 🚀 快速開始

### 方式一：本地運行 / Docker 部署

> 📖 本地運行、Docker 部署詳細步驟請參考 [完整配置指南](./full-guide.md)

## 📱 輸出示例

### 決策儀表盤
```
📊 2026-01-10 決策儀表盤
3隻股票 | 🟢買入:1 🟡觀望:2 🔴賣出:0

🟢 買入 | 貴州茅台(600519)
📌 縮量回踩MA5支撐，乖離率1.2%處於最佳買點
💰 狙擊: 買入1800 | 止損1750 | 目標1900
✅多頭排列 ✅乖離安全 ✅量能配合

🟡 觀望 | 寧德時代(300750)
📌 乖離率7.8%超過5%警戒線，嚴禁追高
⚠️ 等待回調至MA5附近再考慮

---
生成時間: 18:00
```

### 大盤復盤

```
🎯 2026-01-10 大盤復盤

📊 主要指數
- 上證指數: 3250.12 (🟢+0.85%)
- 深證成指: 10521.36 (🟢+1.02%)
- 創業板指: 2156.78 (🟢+1.35%)

📈 市場概況
上漲: 3920 | 下跌: 1349 | 漲停: 155 | 跌停: 3

🔥 板塊表現
領漲: 互聯網服務、文化傳媒、小金屬
領跌: 保險、航空機場、光伏設備
```

## 配置說明

> 📖 完整環境變量、定時任務配置請參考 [完整配置指南](./full-guide.md)

## 🧩 FastAPI Web 服務（可選）

本地運行時，可啟用 FastAPI 服務來管理配置和觸發分析。

### 啟動方式

| 命令 | 說明 |
|------|------|
| `python main.py --serve` | 啟動 API 服務 + 執行一次完整分析 |
| `python main.py --serve-only` | 僅啟動 API 服務，手動觸發分析 |

- 訪問地址：`http://127.0.0.1:8000`
- API 文檔：`http://127.0.0.1:8000/docs`

### 功能特性

- 📝 **配置管理** - 查看/修改自選股列表
- 🚀 **快速分析** - 通過 API 接口觸發分析
- 📊 **實時進度** - 分析任務狀態實時更新，支持多任務並行
- 🤖 **Agent 策略對話** - 啟用 `AGENT_MODE=true` 後，可透過 `/api/v1/agent/chat*` 相關接口進行多輪問答、查看歷史會話與深度研究式追問
- 📈 **回測驗證** - 評估歷史分析準確率，查詢方向勝率與模擬收益

### API 接口

| 接口 | 方法 | 說明 |
|------|------|------|
| `/api/v1/analysis/analyze` | POST | 觸發股票分析 |
| `/api/v1/analysis/tasks` | GET | 查詢任務列表 |
| `/api/v1/analysis/status/{task_id}` | GET | 查詢任務狀態 |
| `/api/v1/history` | GET | 查詢分析歷史記錄 |
| `/api/v1/backtest/run` | POST | 觸發回測 |
| `/api/v1/backtest/results` | GET | 查詢回測結果（分頁） |
| `/api/v1/backtest/performance` | GET | 獲取整體回測表現 |
| `/api/v1/backtest/performance/{code}` | GET | 獲取單股回測表現 |
| `/api/v1/agent/skills` | GET | 取得可用策略技能清單（內建/自訂） |
| `/api/v1/agent/chat/stream` | POST (SSE) | Agent 多輪策略對話（流式） |
| `/api/health` | GET | 健康檢查 |

> 備註：`POST /api/v1/analysis/analyze` 在 `async_mode=false` 時僅支援單一股票；批量 `stock_codes` 需使用 `async_mode=true`。異步 `202` 對單股回傳 `task_id`，對批量回傳 `accepted` / `duplicates` 匯總。

## 🔎 智慧搜尋補全 (MVP)


## 項目結構

```
daily_stock_analysis/
├── main.py              # 主程序入口
├── server.py            # FastAPI 服務入口
├── src/                 # 核心業務代碼
│   ├── analyzer.py      # AI 分析器（Gemini）
│   ├── config.py        # 配置管理
│   ├── notification.py  # 消息推送
│   ├── storage.py       # 數據存儲
│   └── ...
├── api/                 # FastAPI API 模塊
├── data_provider/       # 數據源適配器
├── docker/              # Docker 配置
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                # 項目文檔
│   ├── full-guide.md    # 完整配置指南
│   └── ...
└── .github/workflows/   # GitHub Actions
```

## 🗺️ Roadmap

> 📢 以下功能將視後續情況逐步完成，如果你有好的想法或建議，歡迎 [提交 Issue](https://github.com/ZhuLinsen/daily_stock_analysis/issues) 討論！

### 🎯 功能增強
- [x] 決策儀表盤
- [x] 大盤復盤
- [x] 定時推送
- [x] GitHub Actions
- [x] 港股支持
- [x] Web 管理界面 (簡易版)
- [x] 美股支持
- [ ] 歷史分析回測

## ☕ 支持項目

| 支付寶 (Alipay) | 微信支付 (WeChat) | 小紅書 |
| :---: | :---: | :---: |
| <img src="../sources/alipay.jpg" width="200" alt="Alipay"> | <img src="../sources/wechatpay.jpg" width="200" alt="WeChat Pay"> | <img src="../sources/xiaohongshu.png" width="200" alt="小紅書"> |

## 貢獻

歡迎提交 Issue 和 Pull Request！

詳見 [貢獻指南](CONTRIBUTING.md)

## License
[MIT License](../LICENSE) © 2026 ZhuLinsen

如果你在項目中使用或基於本项目进行二次开发，
非常歡迎在 README 或文檔中註明來源並附上本倉庫鏈接。
這將有助於項目的持續維護和社區發展。

## 聯繫與合作
- GitHub Issues：[提交 Issue](https://github.com/ZhuLinsen/daily_stock_analysis/issues)
- 合作郵箱：zhuls345@gmail.com

## Star History
**如果覺得有用，請給個 ⭐ Star 支持一下！**

<a href="https://star-history.com/#ZhuLinsen/daily_stock_analysis&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ZhuLinsen/daily_stock_analysis&type=Date" />
 </picture>
</a>

## 免責聲明

本項目僅供學習和研究使用，不構成任何投資建議。股市有風險，投資需謹慎。作者不對使用本項目產生的任何損失負責。

---
