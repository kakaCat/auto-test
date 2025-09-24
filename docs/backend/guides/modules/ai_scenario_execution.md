# AI场景执行代理使用指南

## 概述

AI场景执行代理是一个智能化的自动化测试执行系统，它能够：

1. **智能参数增强**：根据用户的自然语言描述，自动完善和补充执行参数
2. **场景查询与解析**：自动查询场景配置，解析接口流程和依赖关系
3. **智能接口执行**：按照配置的执行策略（顺序、并行、混合）智能遍历和执行接口
4. **错误处理与恢复**：在接口调用失败时提供智能的错误处理和恢复机制
5. **实时监控与反馈**：提供执行过程的实时状态监控和详细的执行报告

## 核心流程

```
用户输入场景ID和参数描述
        ↓
    AI参数增强
        ↓
    查询场景配置
        ↓
    解析接口流程
        ↓
    智能遍历执行接口
        ↓
    处理执行结果
```

## 快速开始

### 1. 架构设计

基于DDD（领域驱动设计）架构，采用分层设计：

- **表现层**: REST API控制器
- **应用层**: 场景执行服务
- **领域层**: AI代理和执行逻辑
- **基础设施层**: 数据库访问和外部服务

### 2. 技术栈

- **FastAPI**: REST API框架
- **SQLAlchemy**: ORM数据库操作
- **SQLite**: 数据存储
- **AI Agent**: 智能参数增强和执行策略

### 3. 基本使用示例

#### 执行AI场景
```bash
curl -X POST "http://localhost:8001/scenarios/1/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "user_description": "注册用户，邮箱是 john@example.com，姓名是 John Doe",
    "initial_parameters": {
      "priority": "high",
      "timeout": 30
    },
    "execution_config": {
      "strategy": "sequential",
      "auto_enhance": true
    }
  }'
```

#### 查看执行结果
```bash
curl "http://localhost:8001/executions/1"
```

响应示例：
```json
{
  "id": 1,
  "scenario_id": 1,
  "status": "completed",
  "success_count": 3,
  "failure_count": 0,
  "enhanced_parameters": {
    "email": "john@example.com",
    "name": "John Doe",
    "priority": "high"
  },
  "execution_time": 2.5
}
```

## 详细功能说明

### 1. 智能参数增强

AI代理能够从用户的自然语言描述中智能提取和增强参数：

#### 支持的参数提取模式

1. **直接匹配**：
   ```
   "邮箱是 user@example.com" → email: "user@example.com"
   "用户名：张三" → user_name: "张三"
   ```

2. **格式识别**：
   ```
   "联系我：13800138000" → phone: "13800138000"
   "发送到 admin@company.com" → email: "admin@company.com"
   ```

3. **上下文推理**：
   ```
   "注册VIP用户" → user_type: "vip"
   "紧急处理" → priority: "high"
   ```

#### 参数增强配置

```python
agent_config = {
    'auto_enhance_parameters': True,  # 启用自动参数增强
    'parameter_extraction_rules': {   # 自定义提取规则
        'email': ['邮箱', 'email', '邮件地址'],
        'user_name': ['用户名', 'username', '姓名', 'name'],
        'phone': ['电话', 'phone', '手机号']
    },
    'default_values': {               # 默认值配置
        'user_type': 'normal',
        'priority': 'medium'
    }
}
```

### 2. 场景配置与查询

#### 场景配置结构

```python
scenario_config = {
    'id': 1,
    'name': '用户注册流程',
    'description': '完整的用户注册流程',
    'execution_type': 'sequential',  # sequential, parallel, mixed
    'variables': {
        'user_email': '',
        'user_name': '',
        'verification_code': ''
    },
    'apis': [
        {
            'api_id': 1,
            'execution_order': 1,
            'is_required': True,
            'parameter_mapping': {
                'email': '${user_email}',
                'name': '${user_name}'
            },
            'response_mapping': {
                'verification_code': 'verification_code'
            },
            'pre_condition': None,
            'timeout_seconds': 30
        }
    ]
}
```

#### 参数映射语法

- `${variable_name}` - 引用场景变量
- `${api_1.response_field}` - 引用其他API的响应字段
- `${api_1.data.user_id}` - 引用嵌套响应字段

### 3. 执行策略

#### 顺序执行（Sequential）

```python
# 按execution_order顺序依次执行
apis = [
    {'api_id': 1, 'execution_order': 1},  # 先执行
    {'api_id': 2, 'execution_order': 2},  # 后执行
    {'api_id': 3, 'execution_order': 3}   # 最后执行
]
```

#### 并行执行（Parallel）

```python
# 所有API同时执行
apis = [
    {'api_id': 1, 'execution_group': 'group1'},
    {'api_id': 2, 'execution_group': 'group1'},
    {'api_id': 3, 'execution_group': 'group1'}
]
```

#### 混合执行（Mixed）

```python
# 按组并行，组间顺序
apis = [
    {'api_id': 1, 'execution_group': 'init', 'execution_order': 1},
    {'api_id': 2, 'execution_group': 'parallel', 'execution_order': 2},
    {'api_id': 3, 'execution_group': 'parallel', 'execution_order': 2},
    {'api_id': 4, 'execution_group': 'cleanup', 'execution_order': 3}
]
```

### 4. 错误处理与恢复

#### 错误处理策略

```python
agent_config = {
    'stop_on_first_failure': True,      # 遇到失败立即停止
    'enable_smart_recovery': True,      # 启用智能恢复
    'max_retry_attempts': 3,            # 最大重试次数
    'retry_delay_seconds': 1,           # 重试延迟
    'ignore_non_critical_failures': True  # 忽略非关键失败
}
```

#### 前置条件检查

```python
api_config = {
    'api_id': 2,
    'pre_condition': '${verification_code} != ""',  # 前置条件
    'is_required': True,                            # 是否必需
    'failure_action': 'stop'                       # 失败时的动作
}
```

### 5. 实时监控

#### 执行状态查询

```python
# 获取代理状态
status = await agent.get_agent_status()
print(f"当前状态: {status['state']}")
print(f"执行次数: {status['execution_count']}")

# 获取执行历史
history = await agent.get_execution_history(limit=10)
for record in history:
    print(f"场景: {record['request']['scenario_id']}")
    print(f"状态: {record['final_status']}")
    print(f"执行时间: {record['total_execution_time']}秒")
```

#### 执行取消

```python
# 取消当前执行
cancel_result = await agent.cancel_current_execution()
print(f"取消结果: {cancel_result['message']}")
```

## REST API接口

### 1. 启动API服务

```bash
# 启动API管理模块v2（推荐）
python start_api_v2.py --debug --port 8002

# 或启动服务API模块
python start_service_api.py

# 或启动主应用
cd src && python -m auto_test.main
```

### 2. API端点

#### 执行场景

```bash
POST /api/scenario/execute
Content-Type: application/json

{
    "scenario_id": 1,
    "user_description": "注册用户，邮箱是 john@example.com，姓名是 John Doe",
    "initial_parameters": {
        "priority": "high"
    },
    "async_execution": true
}
```

响应：
```json
{
    "success": true,
    "message": "场景执行已启动",
    "data": {
        "execution_id": "exec_20241201_143022_1",
        "status": "pending",
        "async_execution": true
    },
    "timestamp": "2024-12-01T14:30:22.123456"
}
```

#### 查询执行状态

```bash
GET /api/scenario/status/{execution_id}
```

响应：
```json
{
    "execution_id": "exec_20241201_143022_1",
    "status": "completed",
    "progress": {
        "current_step": 3,
        "total_steps": 3
    },
    "result": {
        "final_status": "completed",
        "success_count": 3,
        "failure_count": 0,
        "total_execution_time": 2.45
    },
    "created_at": "2024-12-01T14:30:22.123456",
    "updated_at": "2024-12-01T14:30:24.567890"
}
```

#### 查询执行历史

```bash
GET /api/scenario/history?limit=10&offset=0
```

#### 取消执行

```bash
POST /api/scenario/cancel/{execution_id}
```

#### 获取代理状态

```bash
GET /api/agent/status
```

## 使用示例

### 示例1：用户注册流程

```python
# 用户输入
scenario_id = 1
user_description = """
注册新用户：
- 邮箱：alice@company.com
- 姓名：Alice Smith
- 手机：13900139000
- 用户类型：VIP
"""

# 执行场景
result = await agent.process_scenario_request(
    scenario_id=scenario_id,
    user_description=user_description
)

# AI自动增强的参数
enhanced_params = result.request.enhanced_parameters
# {
#     'user_email': 'alice@company.com',
#     'user_name': 'Alice Smith',
#     'user_phone': '13900139000',
#     'user_type': 'vip',
#     'priority': 'high',
#     'execution_id': 'exec_20241201_143022_1',
#     'execution_timestamp': '2024-12-01T14:30:22.123456'
# }
```

### 示例2：订单处理流程

```python
user_description = """
处理订单 ORD123456：
- 客户邮箱：customer@example.com
- 订单金额：299.99
- 支付方式：信用卡
- 紧急处理
"""

result = await agent.process_scenario_request(
    scenario_id=2,  # 订单处理场景
    user_description=user_description,
    initial_parameters={
        'notification_enabled': True
    }
)
```

### 示例3：批量数据处理

```python
user_description = """
批量导入用户数据：
- 数据文件：users_2024.csv
- 包含1000条记录
- 需要验证邮箱格式
- 自动分配用户组
"""

result = await agent.process_scenario_request(
    scenario_id=3,  # 批量处理场景
    user_description=user_description,
    initial_parameters={
        'batch_size': 100,
        'validation_enabled': True
    }
)
```

## 高级配置

### 1. 自定义参数提取器

```python
class CustomParameterExtractor:
    def extract_parameters(self, description: str, required_params: List[str]) -> Dict[str, Any]:
        # 自定义参数提取逻辑
        extracted = {}
        
        # 使用NLP模型或正则表达式提取参数
        # ...
        
        return extracted

# 配置自定义提取器
agent.parameter_extractor = CustomParameterExtractor()
```

### 2. 自定义执行策略

```python
class CustomExecutionStrategy:
    async def execute_apis(self, apis: List[Dict], context: Dict) -> List[Dict]:
        # 自定义执行策略
        results = []
        
        # 实现自定义的执行逻辑
        # ...
        
        return results

# 配置自定义策略
agent.execution_strategy = CustomExecutionStrategy()
```

### 3. 集成外部AI模型

```python
# 集成OpenAI GPT
from openai import AsyncOpenAI

class GPTParameterEnhancer:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def enhance_parameters(self, description: str, schema: Dict) -> Dict[str, Any]:
        prompt = f"""
        根据用户描述提取参数：
        描述：{description}
        参数模式：{schema}
        
        请返回JSON格式的参数。
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.choices[0].message.content)

# 配置GPT增强器
agent.parameter_enhancer = GPTParameterEnhancer(api_key="your-api-key")
```

## 最佳实践

### 1. 场景设计原则

- **单一职责**：每个场景专注于一个业务流程
- **参数标准化**：使用统一的参数命名规范
- **错误处理**：为每个API配置合适的错误处理策略
- **依赖管理**：明确定义API之间的依赖关系

### 2. 参数描述规范

- **结构化描述**：使用清晰的格式描述参数
- **关键信息突出**：重要参数使用明确的标识
- **上下文完整**：提供足够的上下文信息

### 3. 性能优化

- **并行执行**：合理使用并行执行策略
- **缓存机制**：缓存常用的场景配置
- **连接池**：使用数据库连接池
- **异步处理**：使用异步API处理长时间运行的任务

### 4. 监控与日志

- **详细日志**：记录执行过程的详细信息
- **性能指标**：监控执行时间和成功率
- **错误追踪**：建立完善的错误追踪机制
- **告警机制**：设置关键指标的告警

## 故障排除

### 常见问题

1. **参数提取失败**
   - 检查用户描述格式
   - 验证参数提取规则
   - 查看日志中的提取过程

2. **API执行失败**
   - 检查API配置和参数映射
   - 验证前置条件
   - 查看API响应和错误信息

3. **执行超时**
   - 调整超时配置
   - 检查网络连接
   - 优化API性能

4. **数据库连接问题**
   - 验证数据库连接字符串
   - 检查数据库服务状态
   - 查看连接池配置

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看执行步骤详情
for step in result.execution_steps:
    print(f"步骤: {step.api_name}")
    print(f"输入: {step.input_parameters}")
    print(f"输出: {step.output_result}")
    if step.error_message:
        print(f"错误: {step.error_message}")

# 检查参数增强过程
print("原始参数:", result.request.raw_parameters)
print("增强参数:", result.request.enhanced_parameters)
```

## 扩展开发

### 1. 配置参数提取器

通过REST API配置参数提取规则：

```bash
curl -X POST "http://localhost:8001/admin/parameter-extractors" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "email_extractor",
    "pattern": "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
    "parameter_name": "email",
    "description": "提取邮箱地址"
  }'
```

### 2. 配置执行策略

```bash
curl -X POST "http://localhost:8001/admin/execution-strategies" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "conditional",
    "description": "条件执行策略",
    "config": {
      "stop_on_critical_failure": true,
      "retry_failed_steps": false,
      "parallel_execution": false
    }
  }'
```

## 版本更新

### v1.0.0
- 基础AI场景执行功能
- 智能参数增强
- 多种执行策略支持
- HTTP API接口

### 未来计划
- 集成更多AI模型
- 可视化执行监控界面
- 更丰富的执行策略
- 性能优化和扩展性改进

## 技术支持

如果您在使用过程中遇到问题，可以：

1. 查看详细的执行日志
2. 参考本文档的故障排除部分
3. 查看示例代码和最佳实践
4. 联系技术支持团队

---

*本文档持续更新中，最新版本请查看项目文档。*