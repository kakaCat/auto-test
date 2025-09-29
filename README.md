# AI自动化测试平台 - 场景执行系统

一个基于AI的智能场景执行系统，支持用户通过自然语言描述来执行复杂的API调用流程。系统能够智能地完善参数、编排接口调用顺序，并提供完整的执行监控和结果分析。

## 🚀 项目特性

- **智能代理 (Agents)**: 研究代理和聊天代理，支持工具集成
- **链式处理 (Chains)**: 问答链和摘要链，支持文档检索
- **工作流图 (Graphs)**: 基于 LangGraph 的复杂工作流和多代理协作
- **配置管理**: 灵活的配置系统，支持环境变量和配置文件
- **工具集成**: 丰富的工具生态，包括搜索、计算、文件处理等
- **示例代码**: 完整的示例和最佳实践

## 📁 项目结构

```
auto-test/
├── backend/                 # 后端服务
│   ├── src/                # 源代码
│   │   └── auto-test/      # 核心应用
│   │       ├── agents/     # 智能代理模块
│   │       ├── chains/     # 链式处理模块
│   │       ├── graphs/     # 工作流图模块
│   │       └── utils/      # 工具模块
│   ├── config/             # 配置文件
│   │   └── default.yaml
│   ├── examples/           # 示例代码
│   │   ├── langchain_examples.py
│   │   └── langgraph_examples.py
│   ├── requirements.txt    # Python依赖
│   ├── main.py            # 主启动文件
│   └── .env.example       # 环境变量模板
├── frontend/               # 前端应用
│   ├── src/               # Vue.js源代码
│   ├── package.json       # Node.js依赖
│   └── vite.config.js     # Vite配置
├── docs/                  # 文档
├── scripts/               # 启动脚本
│   └── start_backend.sh
├── tests/                 # 测试文件
└── README.md              # 项目文档
```

## 🛠️ 安装指南

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd auto-test
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 使用 conda
conda create -n langchain-project python=3.9
conda activate langchain-project
```

### 3. 后端安装和配置

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 4. 前端安装和配置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

### 5. 启动服务

```bash
# 启动后端服务（在项目根目录）
./scripts/start_backend.sh

# 启动前端服务（在frontend目录）
cd frontend
npm run dev
```

### 6. 验证安装

```bash
# 运行后端示例代码（在backend目录）
cd backend
python examples/langchain_examples.py
python examples/langgraph_examples.py
```

## 🧪 测试

### 前端测试

项目包含完整的前端测试套件，覆盖单元测试、组件测试和集成测试。

#### 运行测试

```bash
# 进入前端目录
cd frontend

# 运行所有测试
npm test

# 运行特定测试文件
npm test src/test/basic.test.js
npm test src/test/JsonUtils.test.js
npm test src/test/ParamsEditor.simple.test.js
npm test src/test/JsonImport.final.test.js
```

#### 测试覆盖

1. **基础工具测试** (`basic.test.js`)
   - 数据类型检测函数
   - 数组和对象处理工具
   - 字符串和数值处理函数

2. **JSON工具测试** (`JsonUtils.test.js`)
   - JSON解析和验证
   - 数据转换功能
   - 错误处理机制

3. **参数编辑器测试** (`ParamsEditor.simple.test.js`)
   - 组件渲染和交互
   - 参数展开和折叠
   - 键盘导航功能

4. **JSON导入测试** (`JsonImport.final.test.js`)
   - JSON导入模态框功能
   - 覆盖和合并模式
   - 参数验证和转换

#### 测试结果

- ✅ 基础工具测试：16/16 通过
- ✅ JSON工具测试：12/12 通过
- ✅ 参数编辑器测试：10/10 通过  
- ✅ JSON导入测试：14/14 通过
- **总计：52/52 测试通过**

### 测试策略

- **单元测试**：测试独立的工具函数和组件方法
- **组件测试**：测试Vue组件的渲染和交互
- **集成测试**：测试组件间的协作和数据流
- **模拟测试**：使用Mock数据测试边界情况

## 🔧 配置说明

### 环境变量

主要的环境变量包括：

- `OPENAI_API_KEY`: OpenAI API 密钥（必需）
- `MODEL_NAME`: 默认模型名称（默认: gpt-3.5-turbo）
- `MODEL_TEMPERATURE`: 模型温度（默认: 0.7）
- `LOG_LEVEL`: 日志级别（默认: INFO）

### 配置文件

项目支持 YAML 格式的配置文件，位于 `backend/config/default.yaml`。你可以创建 `backend/config/local.yaml` 来覆盖默认配置。

## 📚 使用指南

### 🎯 演示页面

项目提供了一个完整的演示页面，展示参数编辑器和JSON导入功能。

#### 访问演示页面

启动前端服务后，访问：
```
http://localhost:5173/dev/params-editor
```

#### 功能特性

演示页面包含三个主要标签页：

1. **基础配置**
   - 参数编辑器的基本配置选项
   - 展开深度控制 (defaultExpandDepth)
   - 自动展开节点数限制 (maxAutoExpandNodes)
   - 组件ID设置和本地存储管理

2. **JSON导入演示**
   - 四种预设JSON示例：
     - 用户信息：展示基本对象结构
     - API响应：展示复杂嵌套数据
     - 复杂嵌套：展示深层嵌套结构
     - 数组示例：展示数组和混合数据类型
   - 支持两种导入模式：
     - **覆盖模式**：完全替换现有参数
     - **合并模式**：将新参数添加到现有参数中
   - 自定义JSON导入功能

3. **性能测试**
   - 测试不同数据集的处理性能
   - 显示数据转换时间、渲染时间等指标
   - 支持多种数据集的性能对比

#### JSON导入功能使用

1. **使用预设示例**：
   ```javascript
   // 点击任意示例按钮加载预设数据
   // 示例会自动转换为参数编辑器格式
   ```

2. **自定义JSON导入**：
   ```javascript
   // 点击"自定义JSON导入"按钮
   // 在弹出的模态框中输入JSON数据
   // 选择导入模式（覆盖/合并）
   // 点击导入完成
   ```

3. **性能测试**：
   ```javascript
   // 点击"开始性能测试"按钮
   // 系统会自动测试多个数据集
   // 查看处理时间和渲染性能指标
   ```

#### 开发者工具

演示页面还提供了开发者友好的功能：

- **控制台日志**：所有操作都会在浏览器控制台输出详细信息
- **性能监控**：实时显示数据处理和渲染性能
- **本地存储管理**：支持重置组件状态和本地存储

### 智能代理 (Agents)

#### 研究代理

```python
from langchain_langgraph_project.agents import ResearchAgent

# 创建研究代理
agent = ResearchAgent(
    model_name="gpt-3.5-turbo",
    temperature=0.1
)

# 异步研究
result = await agent.run({"query": "人工智能的最新发展"})
print(result['answer'])

# 同步研究
result = agent.research_topic("机器学习趋势")
print(result['research_results'])
```

#### 聊天代理

```python
from langchain_langgraph_project.agents import ChatAgent

# 创建聊天代理
agent = ChatAgent(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    memory_window=5
)

# 进行对话
response = agent.chat("你好，请介绍一下 Python 编程")
print(response)

# 获取对话历史
history = agent.get_conversation_history()
print(f"对话轮数: {len(history)}")
```

### 链式处理 (Chains)

#### 问答链

```python
from langchain_langgraph_project.chains import QAChain

# 创建问答链
qa_chain = QAChain(
    model_name="gpt-3.5-turbo",
    use_retrieval=True
)

# 添加文档
documents = ["Python 是一种高级编程语言..."]
qa_chain.add_documents(documents, ["Python 介绍"])

# 提问
result = await qa_chain.run({"question": "什么是 Python？"})
print(result['answer'])
```

#### 摘要链

```python
from langchain_langgraph_project.chains import SummarizationChain

# 创建摘要链
summary_chain = SummarizationChain(
    model_name="gpt-3.5-turbo",
    temperature=0.3
)

# 生成摘要
long_text = "这是一段很长的文本..."
result = await summary_chain.run({
    'text': long_text,
    'length': 'medium'
})
print(result['summary'])
```

### 工作流图 (Graphs)

#### 简单工作流

```python
from langchain_langgraph_project.graphs import WorkflowGraph
from typing import TypedDict

class MyState(TypedDict):
    input_text: str
    processed_text: str
    result: str

# 创建工作流
workflow = WorkflowGraph[MyState]()

# 定义步骤
def process_step(state: MyState) -> MyState:
    state['processed_text'] = state['input_text'].upper()
    return state

def finalize_step(state: MyState) -> MyState:
    state['result'] = f"处理结果: {state['processed_text']}"
    return state

# 添加步骤
workflow.add_step("process", process_step)
workflow.add_step("finalize", finalize_step)

# 运行工作流
initial_state = {
    'input_text': 'hello world',
    'processed_text': '',
    'result': ''
}

result = await workflow.run(initial_state)
print(result['result'])
```

#### 多代理协作

```python
from langchain_langgraph_project.graphs import AgentGraph
from langchain_langgraph_project.agents import ResearchAgent, ChatAgent

# 创建代理
research_agent = ResearchAgent()
chat_agent = ChatAgent()

# 创建代理图
agent_graph = AgentGraph[MyState]()
agent_graph.add_agent("researcher", research_agent)
agent_graph.add_agent("chat_assistant", chat_agent)

# 定义协作流程
# ... (详见示例代码)
```

## 🔍 示例代码

项目提供了丰富的示例代码：

- `examples/langchain_examples.py`: LangChain 组件使用示例
- `examples/langgraph_examples.py`: LangGraph 工作流示例

运行示例：

```bash
# 运行 LangChain 示例
python examples/langchain_examples.py

# 运行 LangGraph 示例
python examples/langgraph_examples.py
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_agents.py

# 运行测试并生成覆盖率报告
python -m pytest tests/ --cov=src/langchain_langgraph_project
```

## 📊 监控和日志

### 日志配置

项目使用 Python 标准库的 logging 模块，支持：

- 控制台输出
- 文件日志（支持轮转）
- 可配置的日志级别
- 结构化日志格式

### 性能监控

```python
from langchain_langgraph_project.utils import ContextTimer

# 使用计时器
with ContextTimer("API 调用"):
    result = await some_api_call()
```

## 🔒 安全注意事项

1. **API 密钥安全**:
   - 永远不要将 API 密钥提交到版本控制
   - 使用环境变量或安全的密钥管理服务
   - 定期轮换 API 密钥

2. **输入验证**:
   - 对所有用户输入进行验证
   - 使用项目提供的验证工具

3. **访问控制**:
   - 在生产环境中启用适当的访问控制
   - 配置速率限制

## 🚀 部署

### Docker 部署

```dockerfile
# Dockerfile 示例
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/
COPY examples/ ./examples/

CMD ["python", "examples/langchain_examples.py"]
```

### 云平台部署

项目支持部署到各种云平台：

- **AWS**: 使用 Lambda、ECS 或 EC2
- **Google Cloud**: 使用 Cloud Run、GKE 或 Compute Engine
- **Azure**: 使用 Container Instances、AKS 或 Virtual Machines

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装 pre-commit 钩子
pre-commit install

# 运行代码格式化
black src/ examples/
flake8 src/ examples/
```

## 📝 更新日志

### v1.0.0 (2024-01-XX)

- 初始版本发布
- 实现基础代理、链和图功能
- 添加配置管理系统
- 提供完整的示例代码

## 🆘 故障排除

### 常见问题

1. **API 密钥错误**:
   ```
   错误: OpenAI API key not found
   解决: 确保设置了 OPENAI_API_KEY 环境变量
   ```

2. **依赖包冲突**:
   ```
   错误: Package version conflicts
   解决: 使用虚拟环境并重新安装依赖
   ```

3. **内存不足**:
   ```
   错误: Out of memory
   解决: 减少批处理大小或使用更小的模型
   ```

### 获取帮助

- 查看 [Issues](https://github.com/your-repo/issues) 页面
- 阅读 [Wiki](https://github.com/your-repo/wiki) 文档
- 加入社区讨论

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 强大的 LLM 应用开发框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - 多代理工作流框架
- [OpenAI](https://openai.com/) - 提供优秀的 AI 模型

## 📞 联系方式

- 项目维护者: [Your Name](mailto:your.email@example.com)
- 项目主页: [GitHub Repository](https://github.com/your-repo)
- 文档网站: [Documentation](https://your-docs-site.com)

---

**Happy Coding! 🎉**