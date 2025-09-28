# AI自动化测试系统 - 文档导航中心

## 📋 项目概述

本项目是一个现代化的自动化测试平台，采用前后端分离架构，提供智能化的API测试和工作流编排功能。

## 📚 文档组织结构

### 🎯 **项目级文档** (当前目录)
- **[系统架构](./SYSTEM_ARCHITECTURE.md)** - 整体系统设计和技术架构
- **[数据库设计](./DATABASE_DESIGN.md)** - 数据库表结构和关系设计
- **[变更记录](./CHANGELOG.md)** - 项目重要功能更新和修复记录
- **[文档规范](./DOCUMENTATION_STANDARDS.md)** - 文档组织标准
- **[AI协作习惯](./AI_ASSISTANT_GUIDE.md)** - AI助手工作流程与执行准则
- **[临时文件夹使用指南](./TEMP_FOLDER_USAGE_GUIDE.md)** - 文件生成和组织的规范指南
- **[文档映射关系指南](./DOCUMENT_MAPPING_GUIDE.md)** - 代码变更与文档更新的映射关系

### 🎨 **前端项目文档** → [frontend/docs/](../frontend/docs/)
- **[API文档](../frontend/docs/api/)** - 前端API接口层文档
- **[开发指南](../frontend/docs/guides/)** - 前端开发规范和指南
- **[组件文档](../frontend/docs/components/)** - UI组件文档
- **[变更记录](../frontend/docs/changelogs/)** - 前端版本变更

### 🐍 **后端项目文档** → [backend/docs/](../backend/docs/)
- **[API文档](../backend/docs/api/)** - 后端API接口文档
- **[架构文档](../backend/docs/architecture/)** - 后端架构设计
- **[开发指南](../backend/docs/guides/)** - 后端开发规范
- **[变更记录](../backend/docs/changelogs/)** - 后端版本变更

### 🤖 **AI平台设计文档** → [ai-platform/](./ai-platform/)
- **[AI平台PRD](./ai-platform/01_AI_DRIVEN_TESTING_PLATFORM_PRD.md)** - 平台整体架构和愿景
- **[系统重构设计](./ai-platform/02_SYSTEM_REFACTORING_DESIGN.md)** - 向AI驱动平台的重构方案
- **[第一阶段：API编排](./ai-platform/03_PHASE1_API_ORCHESTRATION_DESIGN.md)** - API编排详细设计
- **[第一阶段：实施指南](./ai-platform/04_PHASE1_IMPLEMENTATION_GUIDE.md)** - 详细开发指南和代码示例
- **[第二阶段：UI自动化](./ai-platform/05_PHASE2_UI_AUTOMATION_DESIGN.md)** - UI测试的AI驱动设计
- **[第三阶段：需求管理](./ai-platform/06_PHASE3_REQUIREMENT_MANAGEMENT_DESIGN.md)** - 需求到测试闭环设计

### 📋 **技术文档** (当前目录)
- **[后端技术文档](./backend/)** - 后端开发指南和API文档
- **[前端技术文档](./frontend/)** - 前端开发指南和用户文档

## 🚀 快速开始

### 前端开发
```bash
cd frontend
npm install
npm run dev
```
📖 详细指南: [前端开发文档](../frontend/docs/README.md)

### 后端开发
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn src.auto_test.main:app --reload --host 0.0.0.0 --port 8000
```
📖 详细指南: [后端开发文档](../backend/docs/README.md)

## 📚 文档分类

## 🐍 后端文档 (Python)

### 核心模块使用指南
面向后端开发者和系统集成人员，提供Python模块的使用方法、配置说明和API调用示例：

| 模块 | 文档 | 功能描述 |
|------|------|----------|
| **API管理** | [api_management_guide.md](./backend/api_management_guide.md) | 接口信息录入、存储和调用功能 |
| **场景管理** | [scenario_management_guide.md](./backend/scenario_management_guide.md) | 接口流程编排和执行策略配置 |
| **工作流编排** | [workflow_orchestration_guide.md](./backend/workflow_orchestration_guide.md) | 复杂API调用流程管理 |
| **AI执行代理** | [ai_scenario_execution_guide.md](./backend/ai_scenario_execution_guide.md) | 智能化自动化测试执行 |
| **系统集成** | [integration_guide.md](./backend/integration_guide.md) | 统一的接口流程自动化解决方案 |

### 后端技术栈
- **语言**: Python 3.8+
- **框架**: FastAPI / Flask
- **数据库**: SQLite / PostgreSQL
- **AI框架**: LangChain, LangGraph
- **测试**: pytest

---

## 🎨 前端文档 (Vue.js)

### 项目开发文档
面向前端开发者，提供Vue项目的技术架构、开发规范和维护指南：

| 类型 | 文档 | 功能描述 |
|------|------|----------|
| **项目概览** | [project_guide.md](./frontend/project_guide.md) | 项目架构、技术栈和核心功能 |
| **路由配置** | [routing_guide.md](./frontend/routing_guide.md) | 路由结构、菜单系统和权限控制 |
| **组件功能** | [components_guide.md](./frontend/components_guide.md) | 业务组件分析和开发规范 |
| **开发环境** | [development_guide.md](./frontend/development_guide.md) | 环境配置、启动流程和构建部署 |
| **API接口** | [api_guide.md](./frontend/api_guide.md) | HTTP请求配置、数据流和状态管理 |

### 前端技术栈
- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **UI组件**: Element Plus
- **HTTP客户端**: Axios

## 🚀 快速开始

### 🐍 后端开发流程
```bash
# 1. 进入后端目录
cd backend

# 2. 环境准备
pip install -r requirements.txt

# 3. 配置环境变量（可选）
cp .env.example .env

# 4. 启动后端服务
# 通用启动（推荐）
python -m uvicorn src.auto_test.main:app --reload --host 0.0.0.0 --port 8000

# 备用：脚本入口
python start_api_v2.py --debug --port 8000
```

**推荐阅读顺序**:
1. [API管理模块使用指南](./backend/api_management_guide.md) - 了解基础功能
2. [场景管理系统使用指南](./backend/scenario_management_guide.md) - 配置测试场景  
3. [工作流编排模块使用指南](./backend/workflow_orchestration_guide.md) - 设计复杂流程
4. [AI场景执行代理使用指南](./backend/ai_scenario_execution_guide.md) - 实现智能化测试

### 🎨 前端开发流程
```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

**推荐阅读顺序**:
1. [前端项目概览指南](./frontend/project_guide.md) - 了解整体架构
2. [前端开发环境指南](./frontend/development_guide.md) - 配置开发环境
3. [前端组件功能指南](./frontend/components_guide.md) - 了解业务组件
4. [前端API接口指南](./frontend/api_guide.md) - 掌握数据交互

### 🔗 全栈集成
1. **系统整合**: [接口流程编排集成模块使用指南](./backend/integration_guide.md)
2. **前后端联调**: 确保前端API配置与后端接口一致
3. **部署上线**: 参考各自的部署文档进行生产环境配置

## 📋 文档索引

### 🐍 后端文档列表
| 文档名称 | 文件路径 | 更新频率 |
|---------|---------|----------|
| API管理模块 | `backend/api_management_guide.md` | 随功能更新 |
| 场景管理系统 | `backend/scenario_management_guide.md` | 随功能更新 |
| 工作流编排模块 | `backend/workflow_orchestration_guide.md` | 随功能更新 |
| AI场景执行代理 | `backend/ai_scenario_execution_guide.md` | 随AI模型更新 |
| 系统集成模块 | `backend/integration_guide.md` | 随架构变更 |

### 🎨 前端文档列表
| 文档名称 | 文件路径 | 更新频率 |
|---------|---------|----------|
| 项目概览指南 | `frontend/project_guide.md` | 随架构变更 |
| 路由配置指南 | `frontend/routing_guide.md` | 随路由变更 |
| 组件功能指南 | `frontend/components_guide.md` | 随组件更新 |
| 开发环境指南 | `frontend/development_guide.md` | 随工具链更新 |
| API接口指南 | `frontend/api_guide.md` | 随接口变更 |

## 🔄 维护规范

### 文档更新原则
1. **🎯 准确性**: 确保文档与代码实现一致
2. **📖 完整性**: 覆盖所有核心功能和使用场景  
3. **✨ 易读性**: 使用清晰的结构和示例说明
4. **⏰ 时效性**: 及时更新过时的信息和配置

### 更新触发条件
- **后端文档**: 模块功能变更、API接口调整、配置参数修改
- **前端文档**: 组件结构变化、路由调整、开发工具升级
- **通用文档**: 项目架构重构、部署方式变更

## 📞 支持与反馈

### 🐛 问题反馈
如果您在使用过程中遇到问题：

1. **📚 查阅文档**: 先检查对应的技术文档
2. **💡 查看示例**: 参考 `examples/` 目录下的示例代码
3. **🔍 搜索问题**: 在项目中搜索类似问题的解决方案
4. **📝 提交反馈**: 创建Issue描述具体问题和复现步骤

### 🚀 贡献指南
欢迎为文档贡献内容：

- **🐍 后端文档**: 补充使用示例、最佳实践、常见问题
- **🎨 前端文档**: 完善组件说明、开发技巧、UI规范
- **📖 通用文档**: 改进文档结构、修正错误、增加图表

---

*📚 本文档中心将持续更新，为AI自动化测试平台的全栈开发提供完整的技术支持。*