# AI自动化测试平台 - 后端服务

## 🚀 项目概述

AI自动化测试平台后端是一个基于Python的现代化微服务架构，集成了AI代理、API管理、场景编排和工作流自动化等功能。采用FastAPI框架构建，支持高性能异步处理和智能化测试执行。

### 🎯 核心特性

- **🤖 AI驱动**: 集成LangChain和LangGraph，支持智能化测试场景生成和执行
- **📡 API管理**: 完整的API生命周期管理，支持录入、调用、监控和统计
- **🔄 场景编排**: 灵活的测试场景配置，支持顺序、并行和条件执行
- **⚡ 工作流引擎**: 强大的工作流编排系统，支持复杂业务流程自动化
- **🏗️ 现代架构**: 基于依赖注入、类型安全和异步处理的现代化架构
- **📊 实时监控**: 完整的执行监控、日志记录和性能分析

## 🏗️ 技术架构

### 技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **Web框架** | FastAPI | 0.104+ | 高性能异步API框架 |
| **AI框架** | LangChain | 0.1+ | AI代理和链式处理 |
| **图执行** | LangGraph | 0.0.40+ | 复杂工作流图执行 |
| **数据库ORM** | SQLAlchemy | 2.0+ | 现代化数据库操作 |
| **依赖注入** | dependency-injector | 4.40+ | 服务容器管理 |
| **配置管理** | Pydantic Settings | 2.0+ | 类型安全配置 |
| **日志系统** | Structlog | 23.0+ | 结构化日志记录 |
| **异步HTTP** | aiohttp | 3.8+ | 异步HTTP客户端 |

### 架构模式

```
┌─────────────────────────────────────────────────────────────┐
│                    AI自动化测试平台后端                        │
├─────────────────────────────────────────────────────────────┤
│  🌐 API层 (FastAPI)                                        │
│  ├── API管理模块     ├── 场景管理模块     ├── 工作流模块      │
│  └── AI执行模块      └── 监控模块        └── 集成模块       │
├─────────────────────────────────────────────────────────────┤
│  🧠 AI服务层 (LangChain + LangGraph)                       │
│  ├── 智能代理        ├── 执行链          ├── 决策图         │
│  └── 场景生成        └── 结果分析        └── 自动优化       │
├─────────────────────────────────────────────────────────────┤
│  🔧 核心服务层                                              │
│  ├── 依赖注入容器    ├── 配置管理        ├── 数据库管理      │
│  └── 日志系统        └── 缓存服务        └── 任务队列       │
├─────────────────────────────────────────────────────────────┤
│  💾 数据层                                                  │
│  ├── SQLite/MySQL    ├── Redis缓存       ├── 文件存储       │
│  └── 向量数据库      └── 时序数据库      └── 对象存储       │
└─────────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
backend/
├── 📄 README.md                    # 项目说明文档
├── 📄 ARCHITECTURE_V2.md           # 架构设计文档
├── 📄 requirements.txt             # Python依赖
├── 📄 .env.example                 # 环境配置模板
├── 🚀 start_api_v2.py             # 新版API启动脚本
├── 🚀 start_service_api.py         # 服务API启动脚本
├── 🚀 main.py                      # 主启动入口
├── 📊 api_v2.py                    # 新版API管理模块
├── 🔧 migrate_to_v2.py             # 数据迁移脚本
├── 📁 config/                      # 配置文件目录
│   └── default.yaml
├── 📁 examples/                    # 使用示例
│   ├── api_management_example.py
│   ├── scenario_management_example.py
│   ├── workflow_orchestration_example.py
│   ├── ai_scenario_execution_example.py
│   ├── integration_example.py
│   ├── langchain_examples.py
│   ├── langgraph_examples.py
│   └── cli_usage_example.md
└── 📁 src/auto_test/               # 核心源码目录
    ├── 🧠 agents/                  # AI代理模块
    │   ├── base_agent.py           # 基础代理类
    │   ├── chat_agent.py           # 对话代理
    │   ├── research_agent.py       # 研究代理
    │   └── scenario_agent.py       # 场景代理
    ├── 📡 api/                     # API接口模块
    │   ├── scenario_ai_api.py      # AI场景API
    │   ├── service_management_api.py # 服务管理API
    │   └── service_management_api_optimized.py
    ├── 🔧 api_management/          # API管理核心
    │   ├── api.py                  # API管理接口
    │   ├── api_v2.py              # 新版API管理
    │   ├── api_caller.py          # API调用器
    │   ├── api_recorder.py        # 调用记录器
    │   ├── database.py            # 数据库操作
    │   └── models.py              # 数据模型
    ├── 🔗 chains/                  # LangChain链模块
    │   ├── base_chain.py          # 基础链
    │   ├── qa_chain.py            # 问答链
    │   └── summarization_chain.py  # 摘要链
    ├── 💻 cli/                     # 命令行接口
    │   └── scenario_cli.py
    ├── 🏗️ core/                    # 核心基础模块
    │   ├── config.py              # 配置管理
    │   ├── database.py            # 数据库管理
    │   ├── models.py              # 核心数据模型
    │   └── container.py           # 依赖注入容器
    ├── 💾 database/                # 数据库相关
    │   ├── connection.py          # 数据库连接
    │   ├── dao/                   # 数据访问对象
    │   ├── migrations/            # 数据库迁移
    │   └── *.sql                  # SQL脚本文件
    ├── 📊 graphs/                  # LangGraph图模块
    │   ├── base_graph.py          # 基础图
    │   ├── agent_graph.py         # 代理图
    │   └── workflow_graph.py      # 工作流图
    ├── 🔄 integration/             # 系统集成模块
    │   ├── manager.py             # 集成管理器
    │   ├── batch_processor.py     # 批处理器
    │   ├── unified_monitor.py     # 统一监控
    │   └── workflow_api_bridge.py # 工作流API桥接
    ├── 🎭 scenario_management/     # 场景管理模块
    │   ├── api.py                 # 场景API
    │   ├── manager.py             # 场景管理器
    │   ├── executor.py            # 场景执行器
    │   ├── database.py            # 场景数据库
    │   ├── models.py              # 场景模型
    │   └── integration.py         # 场景集成
    ├── 🛠️ utils/                   # 工具模块
    │   ├── config.py              # 配置工具
    │   ├── helpers.py             # 辅助函数
    │   ├── error_analyzer.py      # 错误分析
    │   └── performance_monitor.py  # 性能监控
    └── 🌊 workflow_orchestration/  # 工作流编排模块
        ├── api.py                 # 工作流API
        ├── orchestrator.py        # 编排器
        ├── executor.py            # 执行器
        ├── monitor.py             # 监控器
        ├── database.py            # 工作流数据库
        └── models.py              # 工作流模型
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd ai-auto-test/backend

# 创建或激活虚拟环境
# 如果你“已经有虚拟环境”，请直接激活它，无需重新创建：
# 例如（替换为你的路径）：
# source /path/to/your-venv/bin/activate  # Linux/Mac
# 或
# C:\Path\to\your-venv\Scripts\activate  # Windows

# 如需新建一个（可选）：
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖（统一）
pip install -r requirements.txt
```

### 2. 环境配置

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
vim .env
```

关键配置项：
```env
# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
ENVIRONMENT=development

# 数据库配置
DATABASE_URL=sqlite:///./auto_test.db
DATABASE_ECHO=false

# AI配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 3. 数据库初始化

```bash
# 自动初始化数据库（首次启动时）
python start_api_v2.py --init-db

# 或手动运行迁移
python migrate_to_v2.py
```

### 4. 启动服务

#### 方式一：通用启动（推荐）
```bash
python -m uvicorn src.auto_test.main:app --reload --host 0.0.0.0 --port 8000
```

#### 方式二：传统服务API
```bash
python start_service_api.py
```

#### 方式三：主入口启动
```bash
python main.py
```

#### 方式四：脚本入口（备用）
```bash
python start_api_v2.py --host 0.0.0.0 --port 8000
```

### 5. 验证安装

访问以下地址验证服务：

- **API文档**: http://localhost:8002/docs
- **健康检查**: http://localhost:8002/health
- **API管理**: http://localhost:8002/api/v2/apis
- **场景管理**: http://localhost:8002/api/v2/scenarios

## 📚 核心模块使用

### 🤖 AI代理模块

```python
from src.auto_test.agents import ScenarioAgent, ChatAgent

# 创建场景代理
agent = ScenarioAgent()
result = await agent.generate_test_scenario(
    api_description="用户登录接口",
    requirements=["正常登录", "密码错误", "用户不存在"]
)
```

### 📡 API管理模块

```python
from src.auto_test.api_management import APIManager

# 创建API管理器
api_manager = APIManager()

# 添加API
api_info = await api_manager.add_api(
    name="用户登录",
    url="https://api.example.com/login",
    method="POST",
    headers={"Content-Type": "application/json"},
    body={"username": "test", "password": "123456"}
)

# 调用API
result = await api_manager.call_api(api_info.id)
```

### 🎭 场景管理模块

```python
from src.auto_test.scenario_management import ScenarioManager, ExecutionType

# 创建场景管理器
scenario_manager = ScenarioManager()

# 创建测试场景
scenario = await scenario_manager.create_scenario(
    name="用户注册流程测试",
    description="完整的用户注册流程",
    execution_type=ExecutionType.SEQUENTIAL
)

# 添加API到场景
await scenario_manager.add_api_to_scenario(
    scenario_id=scenario.id,
    api_id=api_info.id,
    order=1
)

# 执行场景
result = await scenario_manager.execute_scenario(scenario.id)
```

### 🌊 工作流编排模块

```python
from src.auto_test.workflow_orchestration import WorkflowOrchestrator

# 创建工作流编排器
orchestrator = WorkflowOrchestrator()

# 创建工作流
workflow = await orchestrator.create_workflow(
    name="完整测试流程",
    description="从API测试到场景验证的完整流程"
)

# 执行工作流
result = await orchestrator.execute_workflow(workflow.id)
```

## 🔧 开发指南

### 添加新的API端点

1. 在相应模块的`api.py`文件中定义路由
2. 创建Pydantic模型用于请求/响应验证
3. 实现业务逻辑
4. 添加单元测试

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()

class CreateItemRequest(BaseModel):
    name: str
    description: str

@router.post("/items")
async def create_item(request: CreateItemRequest):
    # 实现逻辑
    return {"id": 1, "name": request.name}
```

### 添加新的AI代理

1. 继承`BaseAgent`类
2. 实现必要的方法
3. 配置LangChain组件

```python
from src.auto_test.agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # 初始化代理特定配置
    
    async def process(self, input_data):
        # 实现处理逻辑
        return result
```

### 数据库模型扩展

1. 在`models.py`中定义SQLAlchemy模型
2. 创建Pydantic模型用于API
3. 生成数据库迁移

```python
from sqlalchemy import Column, Integer, String
from src.auto_test.core.database import Base

class NewModel(Base):
    __tablename__ = "new_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_api_management.py

# 运行覆盖率测试
pytest --cov=src/auto_test tests/
```

### 测试结构

```
tests/
├── conftest.py              # 测试配置
├── test_api_management.py   # API管理测试
├── test_scenario_management.py # 场景管理测试
├── test_workflow_orchestration.py # 工作流测试
├── test_agents.py           # AI代理测试
└── integration/             # 集成测试
    ├── test_full_workflow.py
    └── test_api_integration.py
```

## 📊 监控和日志

### 日志配置

项目使用Structlog进行结构化日志记录：

```python
import structlog

logger = structlog.get_logger(__name__)

# 记录结构化日志
logger.info("API调用完成", 
           api_id=123, 
           response_time=0.5, 
           status_code=200)
```

### 性能监控

```python
from src.auto_test.utils.performance_monitor import PerformanceMonitor

# 监控API调用性能
with PerformanceMonitor("api_call"):
    result = await api_call()
```

## 🚀 部署

### Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
# 复制依赖文件
COPY requirements.txt ./
# 安装依赖（统一）
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.auto_test.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
```

### 生产环境配置

```bash
# 设置生产环境变量
export ENVIRONMENT=production
export DEBUG=false
export DATABASE_URL=postgresql://user:pass@localhost/autotest

# 启动服务
python -m uvicorn src.auto_test.main:app --host 0.0.0.0 --port 8000
```

## 🔗 相关链接

- **📖 详细文档**: [docs/backend/](../docs/backend/)
- **🏗️ 架构设计**: [ARCHITECTURE_V2.md](./ARCHITECTURE_V2.md)
- **🎯 使用示例**: [examples/](./examples/)
- **🐛 问题反馈**: [GitHub Issues](https://github.com/your-repo/issues)
- **💬 讨论交流**: [GitHub Discussions](https://github.com/your-repo/discussions)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。

---

**🎉 开始你的AI自动化测试之旅吧！**