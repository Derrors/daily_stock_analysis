# Deployment Guide

This document explains how to deploy the AI Stock Analysis System to a server.

## Deployment Options Comparison

| Option | Pros | Cons | Recommended For |
|------|------|------|----------|
| **Docker Compose** ⭐ | One-click deploy, isolated environment, easy migration, easy upgrade | Requires Docker installation | **Recommended**: Most scenarios |
| **Direct Deployment** | Simple, no extra dependencies | Environment dependencies, migration difficulties | Temporary testing |
| **Systemd Service** | System-level management, auto-start on boot | Complex configuration | Long-term stable operation |
| **Supervisor** | Process management, auto-restart | Requires additional installation | Multi-process management |

**Conclusion: Docker Compose is recommended for the fastest and most convenient migration!**

---

## Option 1: Docker Compose Deployment (Recommended)

### 1. Install Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# CentOS
sudo yum install -y docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. Prepare Configuration Files

```bash
# Clone code (or upload code to server)
git clone <your-repo-url> /opt/stock-analyzer
cd /opt/stock-analyzer

# Copy and edit configuration file
cp .env.example .env
vim .env  # Fill in real API Keys and configuration
```

### 3. One-Click Start

```bash
# Build and start
docker-compose -f ./docker/docker-compose.yml up -d

# View logs
docker-compose -f ./docker/docker-compose.yml logs -f

# View running status
docker-compose -f ./docker/docker-compose.yml ps
```

### 4. Common Management Commands

```bash
# Stop services
docker-compose -f ./docker/docker-compose.yml down

# Restart services
docker-compose -f ./docker/docker-compose.yml restart

# Redeploy after code update
git pull
docker-compose -f ./docker/docker-compose.yml build --no-cache
docker-compose -f ./docker/docker-compose.yml up -d

# Enter container for debugging
docker-compose -f ./docker/docker-compose.yml exec stock-analyzer bash

# Manually run analysis once
docker-compose -f ./docker/docker-compose.yml exec stock-analyzer python main.py
```

### 5. Data Persistence

Data is automatically saved to host directories:
- `./data/` - Database files
- `./logs/` - Log files
- `./reports/` - Analysis reports

---

## Option 2: Direct Deployment

### 1. Install Python Environment

```bash
# Install Python 3.10+
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip

# Create virtual environment
python3.10 -m venv /opt/stock-analyzer/venv
source /opt/stock-analyzer/venv/bin/activate
```

### 2. Install Dependencies

```bash
cd /opt/stock-analyzer
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
vim .env  # Fill in configuration
```

### 4. Run

```bash
# Single run
python main.py

# Scheduled task mode (foreground)
python main.py --schedule

# Background run (using nohup)
nohup python main.py --schedule > /dev/null 2>&1 &
```

---

## Option 3: Systemd Service

Create systemd service file for auto-start on boot and auto-restart:

### 1. Create Service File

```bash
sudo vim /etc/systemd/system/stock-analyzer.service
```

Contents:
```ini
[Unit]
Description=AI Stock Analysis System
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

### 2. Start Service

```bash
# Reload configuration
sudo systemctl daemon-reload

# Start service
sudo systemctl start stock-analyzer

# Enable auto-start on boot
sudo systemctl enable stock-analyzer

# View status
sudo systemctl status stock-analyzer

# View logs
journalctl -u stock-analyzer -f
```

---

## Configuration Guide

### Required Configuration

| Config Item | Description | How to Get |
|--------|------|----------|
| `GEMINI_API_KEY` | Required for AI analysis | [Google AI Studio](https://aistudio.google.com/) |
| `STOCK_LIST` | Watchlist | Comma-separated stock codes |

### Optional Configuration

| Config Item | Default | Description |
|--------|--------|------|
| `SCHEDULE_ENABLED` | `false` | Enable scheduled tasks |
| `SCHEDULE_TIME` | `18:00` | Daily execution time |
| `MARKET_REVIEW_ENABLED` | `true` | Enable market review |
| `TAVILY_API_KEYS` | - | News search (optional) |

---

## Proxy Configuration

If server is in mainland China, accessing Gemini API requires proxy:

### Docker Method

Edit `docker-compose.yml`:
```yaml
environment:
  - http_proxy=http://your-proxy:port
  - https_proxy=http://your-proxy:port
```

### Direct Deployment Method

Edit top of `main.py`:
```python
os.environ["http_proxy"] = "http://your-proxy:port"
os.environ["https_proxy"] = "http://your-proxy:port"
```

---

## Monitoring & Maintenance

### View Logs

```bash
# Docker method
docker-compose -f ./docker/docker-compose.yml logs -f --tail=100

# Direct deployment
tail -f /opt/stock-analyzer/logs/stock_analysis_*.log
```

### Health Check

```bash
# Check process
ps aux | grep main.py

# Check recent reports
ls -la /opt/stock-analyzer/reports/
```

### Routine Maintenance

```bash
# Clean old logs (keep 7 days)
find /opt/stock-analyzer/logs -mtime +7 -delete

# Clean old reports (keep 30 days)
find /opt/stock-analyzer/reports -mtime +30 -delete
```

---

## FAQ

### 1. Docker build failed

```bash
# Clear cache and rebuild
docker-compose -f ./docker/docker-compose.yml build --no-cache
```

### 2. API access timeout

Check proxy configuration, ensure server can access Gemini API.

### 3. Database locked

```bash
# Stop service then delete lock file
rm /opt/stock-analyzer/data/*.lock
```

### 4. Insufficient memory

Adjust memory limits in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 1G
```

---

## Quick Migration

Migrate from one server to another:

```bash
# Source server: Package
cd /opt/stock-analyzer
tar -czvf stock-analyzer-backup.tar.gz .env data/ logs/ reports/

# Target server: Deploy
mkdir -p /opt/stock-analyzer
cd /opt/stock-analyzer
git clone <your-repo-url> .
tar -xzvf stock-analyzer-backup.tar.gz
docker-compose -f ./docker/docker-compose.yml up -d
```

---


**Wishing you a smooth deployment!**
