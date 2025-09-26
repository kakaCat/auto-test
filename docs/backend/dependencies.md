# 依赖管理说明

本项目采用分层依赖管理策略，根据不同的使用场景提供不同的依赖文件。

## 依赖文件说明

### 📦 requirements.txt
**基础依赖文件**
- 包含项目运行的核心依赖
- 适用于最小化安装
- 包含AI/ML核心库、Web框架、数据库等基础功能

### 🛠️ requirements-dev.txt
**开发环境依赖文件**
- 继承 `requirements.txt` 的所有依赖
- 额外包含开发工具和测试框架
- 包含代码格式化、静态检查、测试工具等
- 适用于本地开发和CI/CD环境

**包含的开发工具：**
- 代码格式化：black, isort
- 代码检查：flake8, mypy, pylint
- 测试框架：pytest, pytest-asyncio, pytest-cov
- 文档生成：sphinx
- 交互式开发：jupyter, ipython
- 性能分析：memory-profiler, line-profiler

### 🚀 requirements-prod.txt
**生产环境依赖文件**
- 继承 `requirements.txt` 的所有依赖
- 额外包含生产环境增强功能
- 包含安全、监控、缓存、任务队列等生产级功能
- 适用于生产部署

**包含的生产增强：**
- Web服务器：gunicorn
- 安全增强：python-jose, passlib, cryptography
- 性能监控：psutil, prometheus-client
- 缓存系统：redis, aioredis
- 任务队列：celery, kombu
- 健康检查：healthcheck

## 安装指南

### 开发环境安装
```bash
# 推荐：完整开发环境
pip install -r requirements-dev.txt
```

### 生产环境安装
```bash
# 推荐：生产环境
pip install -r requirements-prod.txt
```

### 最小化安装
```bash
# 仅核心功能
pip install -r requirements.txt
```

## Docker部署

### 开发环境
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements-dev.txt
COPY . .
```

### 生产环境
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements-prod.txt ./
RUN pip install -r requirements-prod.txt
COPY . .
```

## 依赖更新

当需要添加新依赖时：

1. **核心功能依赖** → 添加到 `requirements.txt`
2. **开发工具** → 添加到 `requirements-dev.txt`
3. **生产增强功能** → 添加到 `requirements-prod.txt`

## 备份文件

- `requirements.txt.backup` - 原始requirements.txt备份
- `requirements_full.txt.backup` - 原始requirements_full.txt备份

这些备份文件可以在需要时恢复原始配置。