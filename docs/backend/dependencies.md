# 依赖管理说明

本项目现采用“单一依赖文件”策略，简化安装与维护成本。

## 依赖文件说明

### 📦 requirements.txt（唯一依赖清单）
**说明**
- 包含运行所需的全部核心依赖
- 适用于开发与生产的统一安装
- 默认使用 `PyMySQL` 以避免本地编译问题（如 `mysqlclient`）

> 说明：历史上的 `requirements-dev.txt`、`requirements-prod.txt` 已移除，统一并入 `requirements.txt`。

若需要生产增强（如 `gunicorn`、监控、任务队列等），建议：
- 在部署脚本或镜像中按需追加安装，如 `pip install gunicorn prometheus-client`。
- 或在各自的服务/组件目录维护独立的最小化附加清单（可选）。

## 安装指南

### 通用安装
```bash
pip install -r requirements.txt
```

## Docker部署

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "-m", "uvicorn", "src.auto_test.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 依赖更新

当需要添加新依赖时：
1. 统一添加到 `requirements.txt`
2. 若仅生产使用，建议在部署脚本或 Dockerfile 中追加 `pip install ...`

> 注：历史备份文件已清理；如需回溯可使用版本管理记录。