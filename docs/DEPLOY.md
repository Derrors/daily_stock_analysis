# 🚀 部署指南

本文档介绍如何将 A股自选股智能分析系统部署到服务器。

## 📋 部署方案对比

| 方案 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| **Docker Compose** ⭐ | 一键部署、环境隔离、易迁移、易升级 | 需要安装 Docker | **推荐**：大多数场景 |
| **直接部署** | 简单直接、无额外依赖 | 环境依赖、迁移麻烦 | 临时测试 |
| **Systemd 服务** | 系统级管理、开机自启 | 配置繁琐 | 长期稳定运行 |
| **Supervisor** | 进程管理、自动重启 | 需要额外安装 | 多进程管理 |

**结论：推荐使用 Docker Compose，迁移最快最方便！**

---

## 🐳 方案一：Docker Compose 部署（推荐）

### 1. 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# CentOS
sudo yum install -y docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 准备配置文件

```bash
# 克隆代码（或上传代码到服务器）
git clone <your-repo-url> /opt/stock-analyzer
cd /opt/stock-analyzer

# 复制并编辑配置文件
cp .env.example .env
vim .env  # 填入真实的 API Key 等配置
```

### 3. 一键启动

```bash
# 构建并启动（同时包含定时分析和 Web 界面服务）
docker-compose -f ./docker/docker-compose.yml up -d

# 查看日志
docker-compose -f ./docker/docker-compose.yml logs -f

# 查看运行状态
docker-compose -f ./docker/docker-compose.yml ps
```

启动成功后，可通过 `http://服务器公网IP:8000/docs` 访问 API 文档。如果打不开，记得先在云服务器控制台的「安全组」里放行 8000 端口。

### 4. 常用管理命令

```bash
# 停止服务
docker-compose -f ./docker/docker-compose.yml down

# 重启服务
docker-compose -f ./docker/docker-compose.yml restart

# 更新代码后重新部署
git pull
docker-compose -f ./docker/docker-compose.yml build --no-cache
docker-compose -f ./docker/docker-compose.yml up -d

# 进入容器调试
docker-compose -f ./docker/docker-compose.yml exec stock-analyzer bash

# 手动执行一次分析
docker-compose -f ./docker/docker-compose.yml exec stock-analyzer python main.py
```

### 5. 数据持久化

数据自动保存在宿主机目录：
- `./data/` - 数据库文件
- `./logs/` - 日志文件
- `./reports/` - 分析报告

---

## 🖥️ 方案二：直接部署

### 1. 安装 Python 环境

```bash
# 安装 Python 3.10+
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip

# 创建虚拟环境
python3.10 -m venv /opt/stock-analyzer/venv
source /opt/stock-analyzer/venv/bin/activate
```

### 2. 安装依赖

```bash
cd /opt/stock-analyzer
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 配置环境变量

```bash
cp .env.example .env
vim .env  # 填入配置
```

### 4. 运行

```bash
# 单次运行
python main.py

# 定时任务模式（前台运行）
python main.py --schedule

# 后台运行（使用 nohup）
nohup python main.py --schedule > /dev/null 2>&1 &

# 启动 API 服务
python main.py --serve-only

# 启动 API 服务并执行一次分析（需每日定时请加 --schedule 或设 SCHEDULE_ENABLED=true）
python main.py --serve
```

---

## 🔧 方案三：Systemd 服务

创建 systemd 服务文件实现开机自启和自动重启：

### 1. 创建服务文件

```bash
sudo vim /etc/systemd/system/stock-analyzer.service
```

内容：
```ini
[Unit]
Description=A股自选股智能分析系统
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/stock-analyzer
Environment="PATH=/opt/stock-analyzer/venv/bin"
ExecStart=/opt/stock-analyzer/venv/bin/python main.py --schedule
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

### 2. 启动服务

```bash
# 重载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start stock-analyzer

# 开机自启
sudo systemctl enable stock-analyzer

# 查看状态
sudo systemctl status stock-analyzer

# 查看日志
journalctl -u stock-analyzer -f
```

---

## ⚙️ 配置说明

### 必须配置项

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `GEMINI_API_KEY` | AI 分析必需 | [Google AI Studio](https://aistudio.google.com/) |
| `STOCK_LIST` | 自选股列表 | 逗号分隔的股票代码 |

### 可选配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `SCHEDULE_ENABLED` | `false` | 是否启用定时任务 |
| `SCHEDULE_TIME` | `18:00` | 每日执行时间 |
| `MARKET_REVIEW_ENABLED` | `true` | 是否启用大盘复盘 |
| `TAVILY_API_KEYS` | - | 新闻搜索（可选） |

---

## 🌐 代理配置

如果服务器在国内，访问 Gemini API 需要代理：

### Docker 方式

编辑 `docker-compose.yml`：
```yaml
environment:
  - http_proxy=http://your-proxy:port
  - https_proxy=http://your-proxy:port
```

### 直接部署方式

编辑 `main.py` 顶部：
```python
os.environ["http_proxy"] = "http://your-proxy:port"
os.environ["https_proxy"] = "http://your-proxy:port"
```

---

## 📊 监控与维护

### 日志查看

```bash
# Docker 方式
docker-compose -f ./docker/docker-compose.yml logs -f --tail=100

# 直接部署
tail -f /opt/stock-analyzer/logs/stock_analysis_*.log
```

### 健康检查

```bash
# 检查进程
ps aux | grep main.py

# 检查最近的报告
ls -la /opt/stock-analyzer/reports/
```

### 定期维护

```bash
# 清理旧日志（保留7天）
find /opt/stock-analyzer/logs -mtime +7 -delete

# 清理旧报告（保留30天）
find /opt/stock-analyzer/reports -mtime +30 -delete
```

---

## ❓ 常见问题

### 1. Docker 构建失败

```bash
# 清理缓存重新构建
docker-compose -f ./docker/docker-compose.yml build --no-cache
```

### 2. API 访问超时

检查代理配置，确保服务器能访问 Gemini API。

### 3. 数据库锁定

```bash
# 停止服务后删除 lock 文件
rm /opt/stock-analyzer/data/*.lock
```

### 4. 内存不足

调整 `docker-compose.yml` 中的内存限制：
```yaml
deploy:
  resources:
    limits:
      memory: 1G
```

### 5. 历史镜像仍残留旧 WebUI 静态页怎么办？

**现象**：升级后仍访问到旧的静态前端页面，或页面样式错乱，与当前仓库“仅提供 API 服务”的定位不一致。

**根因**：本地或容器里仍残留旧版静态资源 / 旧镜像缓存，浏览器继续命中了历史前端产物。

**解决方法**：

- **Docker 部署**：执行以下命令重新构建镜像并清理旧容器缓存：
  ```bash
  docker-compose -f ./docker/docker-compose.yml down
  docker-compose -f ./docker/docker-compose.yml build --no-cache
  docker-compose -f ./docker/docker-compose.yml up -d
  ```
  构建完成后刷新浏览器缓存（`Ctrl+Shift+R`）再访问 `http://localhost:8000/docs` 确认当前服务已回到 API 文档页。

- **直接部署（pip + python）**：启动 API 服务：
  ```bash
  python main.py --serve-only
  ```

**验证**：访问 `/docs` 与 `/api/health`，确认 API 可用即可。

---

## 🔄 快速迁移

从一台服务器迁移到另一台：

```bash
# 源服务器：打包
cd /opt/stock-analyzer
tar -czvf stock-analyzer-backup.tar.gz .env data/ logs/ reports/

# 目标服务器：部署
mkdir -p /opt/stock-analyzer
cd /opt/stock-analyzer
git clone <your-repo-url> .
tar -xzvf stock-analyzer-backup.tar.gz
docker-compose -f ./docker/docker-compose.yml up -d
```

---


## 🌐 云服务器访问说明

默认访问：
- `http://服务器公网IP:8000/docs`
- `http://服务器公网IP:8000/api/health`

如无法访问，请检查：
- 安全组 / 防火墙是否放行 8000 端口
- 服务是否以 `python main.py --serve-only` 或 Docker server 模式启动

---

**祝部署顺利！🎉**
