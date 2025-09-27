# 后端项目文档

## 📋 项目概述

本项目是基于Python + FastAPI的现代化后端服务，提供自动化测试平台的API接口和核心业务逻辑。

## 📁 文档结构

### 🔧 API文档
- **[api/](./api/)** - API接口相关文档
  - 接口规范
  - 数据模型
  - 认证授权

### 🏗️ 架构文档
- **[architecture/](./architecture/)** - 系统架构文档
  - 服务架构
  - 数据库设计
  - 模块设计

### 📖 开发指南
- **[guides/](./guides/)** - 开发指南和最佳实践
  - 环境搭建
  - 编码规范
  - 测试指南

### 📝 变更记录
- **[changelogs/](./changelogs/)** - 项目变更记录

## 🚀 快速开始

1. **环境准备**
   ```bash
   pip install -r requirements.txt
   python start_api_v2.py
   ```

2. **开发规范**
   - 遵循 [编码规范](./guides/coding-standards.md)
   - 了解 [架构设计](./architecture/README.md)

3. **项目结构**
   ```
   src/
   ├── auto_test/
   │   ├── controllers/    # 控制器层
   │   ├── services/       # 业务逻辑层
   │   ├── repositories/   # 数据访问层
   │   └── models/         # 数据模型
   ```

## 🔗 相关链接

- [项目根目录](../)
- [源码目录](../src/)
- [系统文档](../../docs/)
- [前端文档](../../frontend/docs/)

## 📞 技术支持

如有问题，请：
1. 查看相关文档
2. 检查日志输出
3. 联系开发团队

---

**技术栈**: Python + FastAPI + SQLAlchemy + PostgreSQL  
**最后更新**: 2024年1月15日