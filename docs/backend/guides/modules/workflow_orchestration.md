# 工作流编排模块使用指南

## 概述

工作流编排模块是一个强大的接口流程管理系统，支持创建、编排、执行和监控复杂的API调用流程。该模块与API管理模块深度集成，提供完整的接口流程自动化解决方案。

## 核心功能

### 1. 工作流管理
- **流程定义**: 创建、编辑、删除工作流定义
- **版本控制**: 支持工作流版本管理
- **导入导出**: 支持工作流配置的导入导出
- **标签管理**: 支持工作流分类和标签

### 2. 节点类型
- **START**: 流程开始节点
- **END**: 流程结束节点
- **API_CALL**: API调用节点
- **CONDITION**: 条件判断节点
- **DELAY**: 延迟等待节点
- **PARALLEL**: 并行执行节点
- **LOOP**: 循环执行节点

### 3. 连接类型
- **SEQUENCE**: 顺序连接
- **CONDITIONAL**: 条件连接
- **CONDITIONAL_TRUE**: 条件为真时连接
- **CONDITIONAL_FALSE**: 条件为假时连接
- **PARALLEL**: 并行连接
- **LOOP**: 循环连接

### 4. 执行引擎
- **异步执行**: 支持异步工作流执行
- **条件分支**: 支持复杂的条件判断和分支
- **错误处理**: 完善的错误处理和重试机制
- **上下文管理**: 执行过程中的数据传递和共享

### 5. 监控分析
- **执行统计**: 详细的执行统计信息
- **性能分析**: 执行时间和性能指标
- **错误分析**: 错误统计和分析
- **实时监控**: 实时执行状态监控

## 架构设计

### 技术栈
- **FastAPI**: REST API框架
- **SQLAlchemy**: ORM数据库操作
- **SQLite**: 数据存储
- **Pydantic**: 数据验证和序列化
- **Dependency Injector**: 依赖注入

### 目录结构
```
workflow_orchestration/
├── entities/           # 实体层
│   ├── workflow.py    # 工作流实体
│   └── execution.py   # 执行实体
├── services/          # 应用服务层
│   ├── workflow_service.py
│   └── execution_service.py
├── repositories/      # 仓储层
│   ├── workflow_repository.py
│   └── execution_repository.py
└── controllers/       # 控制器层
    └── workflow_controller.py
```

## 数据库表结构

### 1. 工作流定义表 (workflow_definitions)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID |
| name | VARCHAR(255) | 工作流名称 |
| description | TEXT | 工作流描述 |
| version | VARCHAR(50) | 版本号 |
| config | JSON | 配置信息 |
| tags | JSON | 标签列表 |
| is_active | BOOLEAN | 是否激活 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 2. 工作流节点表 (workflow_nodes)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID |
| workflow_id | INT | 工作流ID |
| name | VARCHAR(255) | 节点名称 |
| node_type | ENUM | 节点类型 |
| config | JSON | 节点配置 |
| position_x | FLOAT | X坐标 |
| position_y | FLOAT | Y坐标 |
| description | TEXT | 节点描述 |
| created_at | DATETIME | 创建时间 |

### 3. 工作流连接表 (workflow_connections)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID |
| workflow_id | INT | 工作流ID |
| from_node_id | INT | 源节点ID |
| to_node_id | INT | 目标节点ID |
| connection_type | ENUM | 连接类型 |
| condition | TEXT | 连接条件 |
| config | JSON | 连接配置 |
| created_at | DATETIME | 创建时间 |

### 4. 工作流执行表 (workflow_executions)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID |
| workflow_id | INT | 工作流ID |
| execution_name | VARCHAR(255) | 执行名称 |
| status | ENUM | 执行状态 |
| input_data | JSON | 输入数据 |
| output_data | JSON | 输出数据 |
| error_message | TEXT | 错误信息 |
| started_at | DATETIME | 开始时间 |
| completed_at | DATETIME | 完成时间 |
| created_at | DATETIME | 创建时间 |

### 5. 工作流执行日志表 (workflow_execution_logs)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID |
| execution_id | INT | 执行ID |
| node_id | INT | 节点ID |
| step_name | VARCHAR(255) | 步骤名称 |
| status | ENUM | 步骤状态 |
| input_data | JSON | 输入数据 |
| output_data | JSON | 输出数据 |
| error_message | TEXT | 错误信息 |
| execution_time | FLOAT | 执行时间(秒) |
| started_at | DATETIME | 开始时间 |
| completed_at | DATETIME | 完成时间 |
| created_at | DATETIME | 创建时间 |

## 使用方法

### 1. 创建工作流

```bash
curl -X POST "http://localhost:8001/workflows" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "示例工作流",
    "description": "这是一个示例工作流",
    "version": "1.0",
    "config": {
      "timeout": 300,
      "retry_count": 3
    },
    "tags": ["demo", "example"]
  }'
```

响应示例：
```json
{
  "id": 1,
  "name": "示例工作流",
  "description": "这是一个示例工作流",
  "version": "1.0",
  "status": "draft",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### 2. 添加工作流节点

```bash
curl -X POST "http://localhost:8001/workflows/1/nodes" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API调用节点",
    "node_type": "API_CALL",
    "config": {
      "api_id": 1,
      "parameters": {"param1": "{{input.value}}"},
      "timeout": 30
    },
    "position_x": 100,
    "position_y": 200,
    "description": "调用用户API"
  }'
```

### 3. 添加节点连接

```bash
curl -X POST "http://localhost:8001/workflows/1/connections" \
  -H "Content-Type: application/json" \
  -d '{
    "from_node_id": 1,
    "to_node_id": 2,
    "connection_type": "SEQUENCE",
    "condition": null,
    "config": {
      "delay": 0
    }
  }'
```

### 4. 执行工作流

```bash
curl -X POST "http://localhost:8001/workflows/1/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "execution_name": "测试执行",
    "input_data": {
      "value": "test_data",
      "user_id": 123
    },
    "config": {
      "async": true,
      "timeout": 600
    }
  }'
```

### 5. 查询执行状态

```bash
curl "http://localhost:8001/executions/1"
```

响应示例：
```json
{
  "id": 1,
  "workflow_id": 1,
  "execution_name": "测试执行",
  "status": "running",
  "progress": 50,
  "started_at": "2024-01-01T10:00:00Z",
  "current_step": "API调用节点"
}
```

### 6. 条件分支示例

```bash
# 创建带条件分支的工作流
curl -X POST "http://localhost:8001/workflows/1/nodes" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "条件判断",
    "node_type": "CONDITION",
    "config": {
      "condition": "{{input.score}} >= 60",
      "true_path": "通过处理",
      "false_path": "失败处理"
    }
  }'

# 添加条件连接
curl -X POST "http://localhost:8001/workflows/1/connections" \
  -H "Content-Type: application/json" \
  -d '{
    "from_node_id": 2,
    "to_node_id": 3,
    "connection_type": "CONDITIONAL_TRUE"
  }'
```

### 3. 并行执行

```python
async def parallel_example():
    orchestrator = WorkflowOrchestrator()
    
    # 创建工作流
    workflow = await orchestrator.create_workflow(
        name="并行执行示例",
        description="演示并行执行功能"
    )
    
    # 添加并行节点
    parallel_node = await orchestrator.add_node(
        workflow.id,
        name="并行处理",
        node_type=NodeType.PARALLEL,
        config={
            "max_concurrent": 3,
            "wait_for_all": True
        }
    )
    
    # 添加并行任务
    task1 = await orchestrator.add_node(
        workflow.id,
        name="任务1",
        node_type=NodeType.API_CALL,
        config={"api_id": 4}
    )
    
    task2 = await orchestrator.add_node(
        workflow.id,
        name="任务2",
        node_type=NodeType.API_CALL,
        config={"api_id": 5}
    )
    
    # 添加并行连接
    await orchestrator.add_connection(
        workflow.id,
        parallel_node.id,
        task1.id,
        ConnectionType.PARALLEL
    )
    
    await orchestrator.add_connection(
        workflow.id,
        parallel_node.id,
        task2.id,
        ConnectionType.PARALLEL
    )
```

### 4. 循环执行

```python
async def loop_example():
    orchestrator = WorkflowOrchestrator()
    
    # 创建工作流
    workflow = await orchestrator.create_workflow(
        name="循环执行示例",
        description="演示循环执行功能"
    )
    
    # 添加循环节点
    loop_node = await orchestrator.add_node(
        workflow.id,
        name="循环处理",
        node_type=NodeType.LOOP,
        config={
            "condition": "{{loop.index}} < {{input.max_count}}",
            "max_iterations": 10,
            "break_on_error": True
        }
    )
    
    # 添加循环体
    loop_body = await orchestrator.add_node(
        workflow.id,
        name="循环体",
        node_type=NodeType.API_CALL,
        config={
            "api_id": 6,
            "parameters": {
                "index": "{{loop.index}}",
                "data": "{{input.data[loop.index]}}"
            }
        }
    )
    
    # 添加循环连接
    await orchestrator.add_connection(
        workflow.id,
        loop_node.id,
        loop_body.id,
        ConnectionType.LOOP
    )
```

## 参数和变量

### 1. 变量引用语法
- `{{input.field}}`: 引用输入数据字段
- `{{node_name.field}}`: 引用指定节点的输出字段
- `{{response.data}}`: 引用API响应数据
- `{{loop.index}}`: 引用循环索引
- `{{execution.id}}`: 引用执行ID

### 2. 条件表达式
```python
# 数值比较
"{{input.score}} >= 60"
"{{response.status}} == 200"

# 字符串比较
"{{input.type}} == 'premium'"
"{{response.message}}.contains('success')"

# 逻辑运算
"{{input.age}} >= 18 and {{input.verified}} == true"
"{{response.status}} == 200 or {{response.status}} == 201"

# 存在性检查
"{{input.email}} is not null"
"{{response.data}} is not empty"
```

### 3. 数据映射
```python
# 输出映射配置
"output_mapping": {
    "user_id": "response.data.id",
    "token": "response.data.access_token",
    "profile": "response.data.user_profile"
}

# 参数映射配置
"parameters": {
    "user_id": "{{login.user_id}}",
    "token": "{{login.token}}",
    "data": "{{input.update_data}}"
}
```

## 监控和分析

### 1. 执行统计
```python
async def monitoring_example():
    monitor = WorkflowMonitor()
    
    # 获取执行统计
    stats = await monitor.get_execution_stats(workflow_id)
    print(f"总执行次数: {stats['total_executions']}")
    print(f"成功率: {stats['success_rate']}%")
    print(f"平均执行时间: {stats['avg_execution_time']}秒")
    
    # 获取性能分析
    performance = await monitor.get_performance_analysis(workflow_id)
    print(f"最慢节点: {performance['slowest_node']}")
    print(f"瓶颈分析: {performance['bottlenecks']}")
    
    # 获取错误分析
    errors = await monitor.get_error_analysis(workflow_id)
    for error in errors:
        print(f"错误类型: {error['error_type']}")
        print(f"发生次数: {error['count']}")
        print(f"最近发生: {error['last_occurrence']}")
```

### 2. 实时监控
```python
async def real_time_monitoring():
    monitor = WorkflowMonitor()
    
    # 获取活跃执行
    active_executions = await monitor.get_active_executions()
    for execution in active_executions:
        print(f"执行ID: {execution['id']}")
        print(f"当前状态: {execution['status']}")
        print(f"当前节点: {execution['current_node']}")
        print(f"执行时间: {execution['elapsed_time']}秒")
    
    # 获取实时指标
    metrics = await monitor.get_real_time_metrics()
    print(f"当前活跃执行数: {metrics['active_executions']}")
    print(f"每分钟执行数: {metrics['executions_per_minute']}")
    print(f"系统负载: {metrics['system_load']}")
```

## 最佳实践

### 1. 工作流设计
- **模块化设计**: 将复杂流程拆分为小的、可重用的子流程
- **错误处理**: 为每个关键节点添加错误处理分支
- **超时设置**: 为长时间运行的节点设置合理的超时时间
- **资源管理**: 合理设置并行度，避免资源过度消耗

### 2. 性能优化
- **批量操作**: 对于大量数据处理，使用批量API调用
- **缓存策略**: 对于重复调用的API，实施缓存策略
- **异步执行**: 充分利用异步执行能力，提高并发性
- **资源池**: 使用连接池管理数据库和HTTP连接

### 3. 监控告警
- **关键指标**: 监控执行成功率、响应时间、错误率等关键指标
- **告警设置**: 设置合理的告警阈值，及时发现问题
- **日志记录**: 详细记录执行日志，便于问题排查
- **定期清理**: 定期清理历史执行记录，保持系统性能

### 4. 安全考虑
- **权限控制**: 实施细粒度的权限控制
- **数据加密**: 对敏感数据进行加密存储
- **审计日志**: 记录所有操作的审计日志
- **输入验证**: 严格验证所有输入参数

## 故障排除

### 1. 常见问题

**问题**: 工作流执行失败
```
解决方案:
1. 检查节点配置是否正确
2. 验证API接口是否可用
3. 检查输入参数是否符合要求
4. 查看执行日志获取详细错误信息
```

**问题**: 条件判断不生效
```
解决方案:
1. 检查条件表达式语法是否正确
2. 验证引用的变量是否存在
3. 确认数据类型是否匹配
4. 使用调试模式查看变量值
```

**问题**: 执行性能差
```
解决方案:
1. 分析性能瓶颈节点
2. 优化API调用参数
3. 调整并行度设置
4. 检查数据库连接池配置
```

### 2. 调试技巧

```python
# 启用调试模式
executor = WorkflowExecutor(debug=True)

# 查看详细执行日志
logs = await monitor.get_execution_logs(execution_id)
for log in logs:
    print(f"步骤: {log.step_name}")
    print(f"状态: {log.status}")
    print(f"输入: {log.input_data}")
    print(f"输出: {log.output_data}")
    if log.error_message:
        print(f"错误: {log.error_message}")

# 单步执行
execution = await executor.execute_workflow(
    workflow_id,
    input_data,
    step_by_step=True
)
```

## 扩展开发

### 1. 自定义节点类型

通过REST API扩展自定义节点类型：

```bash
# 注册自定义节点类型
curl -X POST "http://localhost:8001/admin/node-types" \
  -H "Content-Type: application/json" \
  -d '{
    "type_name": "CUSTOM_PROCESSOR",
    "description": "自定义数据处理节点",
    "config_schema": {
      "processor_type": "string",
      "parameters": "object"
    },
    "execution_handler": "custom_processor_handler"
  }'
```

### 2. 自定义监控指标

```bash
# 获取自定义指标
curl "http://localhost:8001/workflows/1/metrics?type=custom"
```

响应示例：
```json
{
  "custom_metrics": {
    "processing_time": 2.5,
    "data_throughput": 1000,
    "error_rate": 0.02
  }
}
```

### 3. 插件系统

```python
# 定义插件接口
class WorkflowPlugin:
    async def before_execution(self, workflow_id, input_data):
        pass
    
    async def after_execution(self, execution_id, result):
        pass
    
    async def on_node_execution(self, node_id, context):
        pass

# 实现具体插件
class LoggingPlugin(WorkflowPlugin):
    async def before_execution(self, workflow_id, input_data):
        print(f"开始执行工作流 {workflow_id}")
    
    async def after_execution(self, execution_id, result):
        print(f"工作流执行完成 {execution_id}")

# 注册插件
executor = WorkflowExecutor()
executor.register_plugin(LoggingPlugin())
```

## 版本更新

### v1.0.0 (当前版本)
- 基础工作流编排功能
- 支持多种节点类型
- 条件分支和并行执行
- 执行监控和分析
- API管理模块集成

### 计划功能
- 可视化工作流编辑器
- 更多内置节点类型
- 工作流模板库
- 分布式执行支持
- 更丰富的监控指标

## 技术支持

如果您在使用过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查示例代码和最佳实践
3. 查看执行日志和错误信息
4. 联系技术支持团队

---

*本文档持续更新中，请关注最新版本。*