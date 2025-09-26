# AI自动化测试系统 - 文档中心

本项目采用**文件夹分类隔离**的文档组织方式，便于查找、维护和扩展。

## 📚 文档结构

### 📁 [后端文档](./backend/)
- **[API 文档](./backend/api/)** - 接口参考和使用指南
- **[架构设计](./backend/architecture/)** - v4极简架构设计 ⭐ **推荐**
- **[开发指南](./backend/guides/)** - 模块指南和开发流程
- **[编码规范](./backend/standards/)** - 极简控制器编码规范

### 📁 [前端文档](./frontend/)
- **[API 文档](./frontend/api/)** - API调用和切换器指南
- **[架构设计](./frontend/architecture/)** - 组件架构和设计原则
- **[开发指南](./frontend/guides/)** - 开发流程和组件指南
- **[编码规范](./frontend/standards/)** - TypeScript规范和注释标准

### 📋 [文档组织规范](./DOCUMENTATION_STANDARDS.md)
- 文档分类原则和标准
- 文件夹组织规范
- 命名和维护规范

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
# API管理模块v2（推荐）
python start_api_v2.py --debug --port 8002

# 或启动服务API模块
python start_service_api.py

# 或启动主应用
cd src && python -m auto_test.main
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