# 系统重构设计文档 - 向AI驱动平台演进

## 现状分析

### 现有系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    前端 (Vue 3 + Element Plus)                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   API管理页面   │  │   系统管理      │  │   工作流管理    │   │
│  │   index.vue     │  │   systems.vue   │  │   workflows.vue │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP API
┌─────────────────────────┴───────────────────────────────────────┐
│                 后端 (FastAPI + SQLAlchemy)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   API层         │  │   Service层     │  │   DAO层         │   │
│  │ api_interfaces  │  │ api_interface   │  │ ApiInterfaceDAO │   │
│  │ .py             │  │ _service.py     │  │                 │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ SQL
┌─────────────────────────┴───────────────────────────────────────┐
│                      数据库 (MySQL)                             │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│ │ api_interfaces  │ │ systems         │ │ modules         │     │
│ │ workflows       │ │ scenarios       │ │ logs            │     │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### 现有技术栈

**后端技术栈**：
- **框架**：FastAPI 0.104.0
- **ORM**：SQLAlchemy 2.0.0
- **数据库**：MySQL (通过 mysqlclient/pymysql)
- **AI框架**：LangChain 0.1.0, LangGraph 0.0.40
- **配置管理**：Pydantic Settings 2.0.0
- **依赖注入**：dependency-injector 4.40.0
- **日志**：structlog 23.0.0, loguru 0.7.0

**前端技术栈**：
- **框架**：Vue 3.4.0
- **UI组件**：Element Plus 2.4.4
- **状态管理**：Pinia 2.1.7
- **路由**：Vue Router 4.2.5
- **构建工具**：Vite 4.5.2
- **图表**：ECharts 5.4.3
- **流程图**：Vue Flow 1.46.5

### 现有架构优势

1. **成熟的分层架构**：Controller → Service → DAO 三层架构清晰
2. **完善的API管理**：已有完整的API接口CRUD功能
3. **良好的前端基础**：Vue 3 + Element Plus 提供现代化UI
4. **AI框架就绪**：已集成LangChain和LangGraph
5. **规范的代码结构**：遵循防腐层设计原则

### 现有架构不足

1. **缺乏MCP协议支持**：未集成MCP工具层
2. **AI能力未充分利用**：LangChain仅用于示例，未集成到业务流程
3. **缺乏智能编排**：API调用仍需手动配置，无AI驱动的自动编排
4. **测试能力有限**：缺乏UI自动化测试和智能测试生成
5. **需求管理缺失**：无需求到测试的闭环管理

### 兼容性澄清：现有能力保留并增强

为避免误解，本次重构不会移除现有系统能力，而是在其之上做“增量式增强”。以下能力全部保留：

- API管理与接口详情（后端 `api_interfaces.py`、前端 `api-management/index.vue`）
- 系统/模块分类与过滤
- 工作流可视化与管理（保留现有流程视图与交互）

在此基础上新增/增强：

- 新增 AI Agent 层（意图理解、流程规划、执行协调），用于自动生成/建议编排方案
- 新增 MCP 工具层，标准化工具调用（HTTP、认证、数据处理、断言等）
- 新增 WebSocket 实时监控与 AI 执行记录表，强化可观测性

为何目标架构图看起来像“替换”？

- 该图强调“新增层”，为简化展示未逐一展开既有页面与API；图中“现有业务层（保留+增强）”表示现有功能整体保留
- 文档各处均以“保留+增强”“向后兼容”为原则，不影响已有功能与使用习惯

影响评估与兼容承诺：

- API 兼容：不更改现有接口签名与行为；AI相关能力通过新增端点与可选参数提供
- 数据兼容：新增表（如 `ai_executions`、`mcp_tool_configs`、`api_orchestration_plans`），不修改现有表结构
- 前端兼容：现有页面不做破坏性调整，AI编排将以新增页面/入口方式集成
- 风险控制：通过功能开关灰度启用AI能力，可随时关闭回退

## 重构目标架构

### 目标架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                前端 (Vue 3 + Element Plus)                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   需求管理      │  │   AI编排界面    │  │   测试监控      │   │
│  │ RequirementMgmt │  │ OrchestrationUI │  │ TestMonitor     │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP API + WebSocket
┌─────────────────────────┴───────────────────────────────────────┐
│                    AI Agent层 (新增)                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ 需求理解Agent   │  │ API编排Agent    │  │ UI测试Agent     │   │
│  │ ReqAgent        │  │ ApiAgent        │  │ UIAgent         │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ MCP Protocol
┌─────────────────────────┴───────────────────────────────────────┐
│                    MCP工具层 (新增)                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ API工具集       │  │ UI工具集        │  │ 数据工具集      │   │
│  │ HttpTool        │  │ WebTool         │  │ DataTool        │   │
│  │ AuthTool        │  │ MobileTool      │  │ AssertTool      │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                 现有业务层 (保留+增强)                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ FastAPI Controllers│ Service层       │  │ DAO层           │   │
│  │ (保留现有API)    │  │ (增强AI集成)    │  │ (保留现有)      │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                    数据库层 (扩展)                              │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│ │ 现有表结构      │ │ AI执行记录      │ │ MCP工具配置     │     │
│ │ (保留)          │ │ (新增)          │ │ (新增)          │     │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## 重构策略

### 渐进式重构原则

1. **保持现有功能稳定**：重构过程中不影响现有API管理功能
2. **增量添加AI能力**：逐步集成AI Agent和MCP工具
3. **向后兼容**：新架构兼容现有API接口
4. **分阶段交付**：按三个阶段逐步实现完整AI驱动能力

### 重构实施路径

```
现有系统 → 阶段1(API编排) → 阶段2(UI测试) → 阶段3(需求管理) → AI驱动平台
```

## 第一阶段重构：API编排模块集成

### 1.1 MCP工具层集成

**新增组件**：
```python
# backend/src/auto_test/mcp/
├── __init__.py
├── client.py              # MCP客户端
├── tools/
│   ├── __init__.py
│   ├── http_tools.py      # HTTP请求工具
│   ├── auth_tools.py      # 认证工具
│   ├── data_tools.py      # 数据处理工具
│   └── assert_tools.py    # 断言验证工具
└── schemas/
    ├── __init__.py
    └── tool_schemas.py    # 工具Schema定义
```

**技术实现**：
- 使用 `mcp` Python包 (需添加到requirements.txt)
- 集成现有的 `aiohttp` 进行异步HTTP调用
- 复用现有的 `pydantic` 进行Schema验证

### 1.2 AI Agent层集成

**新增组件**：
```python
# backend/src/auto_test/agents/
├── __init__.py
├── base_agent.py          # Agent基类
├── api_orchestration_agent.py  # API编排Agent
├── intent_parser.py       # 意图理解组件
├── flow_planner.py        # 流程规划组件
└── execution_engine.py    # 执行引擎
```

**技术实现**：
- 基于现有的 `langchain` 和 `langgraph` 框架
- 集成现有的 `openai` API配置
- 复用现有的 `structlog` 日志系统

### 1.3 现有API层增强

**修改文件**：
```python
# backend/src/auto_test/api/
├── orchestration.py      # 新增：AI编排API
└── api_interfaces.py     # 增强：添加AI编排接口
```

**增强内容**：
- 添加AI编排相关的API端点
- 保持现有API接口不变
- 新增WebSocket支持实时执行监控

### 1.4 前端界面集成

**新增组件**：
```vue
// frontend/src/views/api-orchestration/
├── index.vue             # AI编排主页面
├── components/
│   ├── IntentInput.vue   # 意图输入组件
│   ├── FlowViewer.vue    # 流程可视化组件
│   ├── ExecutionMonitor.vue # 执行监控组件
│   └── ResultDisplay.vue # 结果展示组件
```

**技术实现**：
- 复用现有的 `Vue 3` 和 `Element Plus`
- 集成现有的 `Vue Flow` 进行流程可视化
- 使用现有的 `axios` 进行API调用

## 数据库扩展设计

### 新增表结构

```sql
-- AI执行记录表
CREATE TABLE ai_executions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    execution_id VARCHAR(64) UNIQUE NOT NULL,
    agent_type VARCHAR(32) NOT NULL,
    input_data JSON NOT NULL,
    output_data JSON,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- MCP工具配置表
CREATE TABLE mcp_tool_configs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tool_name VARCHAR(64) NOT NULL,
    tool_type VARCHAR(32) NOT NULL,
    schema_definition JSON NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    config_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- API编排计划表
CREATE TABLE api_orchestration_plans (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(128) NOT NULL,
    description TEXT,
    intent_text TEXT NOT NULL,
    execution_plan JSON NOT NULL,
    created_by VARCHAR(64),
    is_template BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 配置文件更新

### requirements.txt 新增依赖

```txt
# MCP Protocol support
mcp>=0.1.0
mcp-client>=0.1.0

# Enhanced AI capabilities  
openai>=1.0.0
anthropic>=0.8.0

# WebSocket support
websockets>=11.0.0
fastapi-websocket>=0.1.0

# Enhanced async support
asyncio-mqtt>=0.13.0
```

### 配置文件增强

```python
# backend/src/auto_test/config.py
class Config:
    # 现有配置保持不变
    
    # 新增AI配置
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    DEFAULT_LLM_MODEL: str = Field(default="gpt-3.5-turbo", env="DEFAULT_LLM_MODEL")
    
    # 新增MCP配置
    MCP_SERVER_HOST: str = Field(default="localhost", env="MCP_SERVER_HOST")
    MCP_SERVER_PORT: int = Field(default=8003, env="MCP_SERVER_PORT")
    MCP_TOOLS_CONFIG_PATH: str = Field(default="config/mcp_tools.json", env="MCP_TOOLS_CONFIG_PATH")
    
    # 新增执行配置
    MAX_CONCURRENT_EXECUTIONS: int = Field(default=5, env="MAX_CONCURRENT_EXECUTIONS")
    EXECUTION_TIMEOUT: int = Field(default=300, env="EXECUTION_TIMEOUT")  # 5分钟
```

## 实施计划

### 第一周：基础设施准备
- [ ] 安装和配置MCP相关依赖
- [ ] 创建数据库表结构
- [ ] 搭建AI Agent基础框架
- [ ] 实现基础MCP工具

### 第二周：核心功能开发
- [ ] 实现意图理解组件
- [ ] 开发流程规划引擎
- [ ] 集成执行引擎
- [ ] 创建API编排接口

### 第三周：前端集成
- [ ] 开发AI编排界面
- [ ] 实现流程可视化
- [ ] 添加执行监控功能
- [ ] 集成现有API管理页面

### 第四周：测试与优化
- [ ] 端到端功能测试
- [ ] 性能优化和调试
- [ ] 文档更新
- [ ] 用户验收测试

## 风险控制

### 技术风险
1. **MCP协议兼容性**：选择成熟的MCP实现库
2. **AI模型稳定性**：提供多模型支持和降级方案
3. **性能影响**：异步执行，避免阻塞现有功能

### 业务风险
1. **功能回归**：保持现有API完全兼容
2. **用户体验**：渐进式UI更新，保持操作习惯
3. **数据安全**：AI执行过程中的敏感数据保护

### 缓解措施
1. **分支开发**：在独立分支进行重构，主分支保持稳定
2. **功能开关**：通过配置控制AI功能的启用
3. **回滚机制**：保持数据库向后兼容，支持快速回滚

## 成功指标

### 技术指标
- [ ] MCP工具调用成功率 > 95%
- [ ] AI意图理解准确率 > 85%
- [ ] API编排执行成功率 > 90%
- [ ] 系统响应时间增加 < 20%

### 业务指标
- [ ] 现有功能零回归
- [ ] 新功能用户采用率 > 60%
- [ ] API编排效率提升 > 200%
- [ ] 用户满意度 > 4.0/5.0

---

*本文档为系统重构的总体设计，具体实施过程中请参考各阶段的详细技术文档。*