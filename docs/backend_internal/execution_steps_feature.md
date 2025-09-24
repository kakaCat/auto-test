# AI代理执行步骤记录功能

## 概述

AI代理执行步骤记录功能是一个强大的监控和调试工具，它能够详细记录AI代理在执行场景过程中的每一步操作，包括输入输出参数、AI参数增强过程、执行状态、性能指标等关键信息。

## 功能特性

### 🎯 核心功能

1. **详细步骤记录**
   - 记录每个API调用的完整信息
   - 跟踪输入输出参数的变化
   - 保存请求和响应的详细数据

2. **AI增强过程跟踪**
   - 记录用户原始描述
   - 保存AI增强后的参数
   - 记录AI推理过程和逻辑

3. **执行状态监控**
   - 实时跟踪执行状态
   - 记录成功、失败、异常情况
   - 提供详细的错误信息和堆栈跟踪

4. **性能指标分析**
   - 记录执行时间和响应时间
   - 统计成功率和失败率
   - 提供性能分析报告

5. **上下文信息保存**
   - 保存执行上下文
   - 记录环境信息
   - 支持变量映射和数据提取

## 数据库模型

### ScenarioExecution (场景执行记录)

主要记录场景级别的执行信息：

```python
class ScenarioExecution(Base):
    __tablename__ = 'scenario_executions'
    
    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, nullable=False)
    execution_id = Column(String(255), unique=True, nullable=False)
    user_description = Column(Text)
    original_parameters = Column(JSON)
    ai_enhanced_parameters = Column(JSON)
    ai_reasoning = Column(Text)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    progress = Column(Float, default=0.0)
    # ... 更多字段
```

### ScenarioExecutionStep (场景执行步骤记录)

详细记录每个API调用步骤的信息：

```python
class ScenarioExecutionStep(Base):
    __tablename__ = 'scenario_execution_steps'
    
    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey('scenario_executions.id'))
    step_order = Column(Integer, nullable=False)
    api_id = Column(Integer, nullable=False)
    step_name = Column(String(255), nullable=False)
    
    # AI增强相关
    original_description = Column(Text)
    ai_enhanced_params = Column(JSON)
    ai_reasoning = Column(Text)
    
    # 输入输出参数
    input_parameters = Column(JSON)
    enhanced_parameters = Column(JSON)
    output_parameters = Column(JSON)
    
    # 请求响应信息
    request_url = Column(String(500))
    request_method = Column(String(10))
    request_headers = Column(JSON)
    request_body = Column(JSON)
    response_status_code = Column(Integer)
    response_headers = Column(JSON)
    response_body = Column(JSON)
    response_time_ms = Column(Float)
    
    # 执行状态
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    
    # 错误信息
    error_message = Column(Text)
    error_code = Column(String(100))
    error_details = Column(JSON)
    stack_trace = Column(Text)
    
    # 重试信息
    retry_count = Column(Integer, default=0)
    retry_details = Column(JSON)
    
    # 数据处理
    extracted_data = Column(JSON)
    mapped_variables = Column(JSON)
    
    # 上下文信息
    execution_context = Column(JSON)
    environment_info = Column(JSON)
    
    # 时间信息
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_ms = Column(Float)
    # ... 更多字段
```

## 使用方法

### 1. 数据库迁移

首先运行数据库迁移脚本创建必要的表结构：

```bash
cd /path/to/auto-test/src/auto-test
python database/migrations/add_execution_steps.py
```

### 2. 基本使用

```python
from agents.scenario_agent import ScenarioAgent, ScenarioRequest

# 创建代理实例
agent = ScenarioAgent()

# 创建执行请求
request = ScenarioRequest(
    scenario_id=1,
    user_description="查询用户信息并更新状态",
    raw_parameters={"email": "test@example.com"}
)

# 执行场景（自动记录步骤）
result = await agent.process_scenario_request(request)
```

### 3. 查询执行记录

```python
from scenario_management.models import ScenarioExecution, ScenarioExecutionStep
from sqlalchemy.orm import sessionmaker

# 查询执行记录
session = SessionLocal()
execution = session.query(ScenarioExecution).filter(
    ScenarioExecution.execution_id == "your_execution_id"
).first()

# 查询步骤记录
steps = session.query(ScenarioExecutionStep).filter(
    ScenarioExecutionStep.execution_id == execution.id
).order_by(ScenarioExecutionStep.step_order).all()

for step in steps:
    print(f"步骤 {step.step_order}: {step.step_name}")
    print(f"状态: {step.status}")
    print(f"输入参数: {step.input_parameters}")
    print(f"输出参数: {step.output_parameters}")
```

### 4. 运行演示示例

```bash
cd /path/to/auto-test/src/auto-test
python examples/execution_steps_example.py
```

## API接口

### 核心方法

#### `_create_execution_record(request: ScenarioRequest) -> int`

创建场景执行记录。

**参数：**
- `request`: 场景执行请求

**返回：**
- 执行记录ID

#### `_save_execution_step(**kwargs) -> int`

保存执行步骤记录。

**主要参数：**
- `step_order`: 步骤顺序
- `api_id`: API ID
- `step_name`: 步骤名称
- `input_parameters`: 输入参数
- `request_url`: 请求URL
- `request_method`: 请求方法
- `status`: 执行状态

**返回：**
- 步骤记录ID

#### `_update_execution_step_result(step_record_id: int, **kwargs)`

更新执行步骤结果。

**主要参数：**
- `step_record_id`: 步骤记录ID
- `status`: 执行状态
- `response_status_code`: 响应状态码
- `response_body`: 响应体
- `output_parameters`: 输出参数
- `error_message`: 错误信息
- `duration_ms`: 执行时长

## 配置选项

### 数据库配置

在 `ScenarioAgent` 初始化时配置数据库连接：

```python
class ScenarioAgent(BaseAgent):
    def __init__(self, database_url: str = None):
        super().__init__()
        
        # 数据库配置
        if database_url:
            self.engine = create_engine(database_url)
        else:
            # 默认SQLite数据库
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'auto_test.db')
            self.engine = create_engine(f'sqlite:///{db_path}')
        
        self.SessionLocal = sessionmaker(bind=self.engine)
```

### 记录级别配置

可以通过环境变量或配置文件控制记录的详细程度：

```python
# 环境变量
EXECUTION_LOGGING_LEVEL = "DETAILED"  # BASIC, DETAILED, FULL
EXECUTION_SAVE_REQUEST_BODY = "true"
EXECUTION_SAVE_RESPONSE_BODY = "true"
EXECUTION_SAVE_STACK_TRACE = "true"
```

## 性能考虑

### 1. 数据库优化

- 为常用查询字段添加索引
- 定期清理历史数据
- 考虑使用分区表处理大量数据

### 2. 异步处理

- 步骤记录操作使用异步方法
- 避免阻塞主执行流程
- 考虑使用消息队列处理大量记录

### 3. 存储优化

- JSON字段压缩存储
- 大文件单独存储
- 配置数据保留策略

## 监控和分析

### 1. 执行统计

```python
# 成功率统计
success_rate = session.query(ScenarioExecution).filter(
    ScenarioExecution.status == ExecutionStatus.COMPLETED
).count() / session.query(ScenarioExecution).count() * 100

# 平均执行时间
avg_duration = session.query(func.avg(ScenarioExecutionStep.duration_ms)).scalar()
```

### 2. 错误分析

```python
# 常见错误统计
error_stats = session.query(
    ScenarioExecutionStep.error_code,
    func.count(ScenarioExecutionStep.id)
).filter(
    ScenarioExecutionStep.status == ExecutionStatus.FAILED
).group_by(ScenarioExecutionStep.error_code).all()
```

### 3. 性能分析

```python
# 慢查询分析
slow_steps = session.query(ScenarioExecutionStep).filter(
    ScenarioExecutionStep.duration_ms > 5000  # 超过5秒
).order_by(ScenarioExecutionStep.duration_ms.desc()).all()
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库URL配置
   - 确认数据库服务运行状态
   - 验证连接权限

2. **记录保存失败**
   - 检查数据库表结构
   - 验证字段长度限制
   - 查看错误日志

3. **性能问题**
   - 检查数据库索引
   - 优化查询语句
   - 考虑数据分页

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   ```

2. **检查记录状态**
   ```python
   # 查看最近的执行记录
   recent_executions = session.query(ScenarioExecution).order_by(
       ScenarioExecution.started_at.desc()
   ).limit(10).all()
   ```

3. **验证数据完整性**
   ```python
   # 检查孤立的步骤记录
   orphaned_steps = session.query(ScenarioExecutionStep).filter(
       ~ScenarioExecutionStep.execution_id.in_(
           session.query(ScenarioExecution.id)
       )
   ).all()
   ```

## 最佳实践

1. **合理设置记录级别**
   - 开发环境使用详细记录
   - 生产环境根据需要调整
   - 定期清理历史数据

2. **错误处理**
   - 记录操作失败不应影响主流程
   - 提供降级机制
   - 监控记录系统健康状态

3. **数据安全**
   - 敏感信息脱敏处理
   - 访问权限控制
   - 数据备份策略

4. **性能优化**
   - 异步记录操作
   - 批量处理机制
   - 合理的索引策略

## 扩展功能

### 1. 可视化界面

可以基于记录数据开发Web界面，提供：
- 执行历史查看
- 实时监控面板
- 性能分析图表
- 错误统计报告

### 2. 告警机制

基于执行记录实现告警：
- 失败率超阈值告警
- 执行时间异常告警
- 错误频率告警

### 3. 数据导出

支持多种格式的数据导出：
- CSV格式报告
- JSON格式数据
- Excel分析报表

## 版本历史

- **v1.0.0** (2024-01-01)
  - 初始版本发布
  - 基础步骤记录功能
  - 数据库模型设计
  - 核心API实现

## 贡献指南

欢迎贡献代码和建议！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。