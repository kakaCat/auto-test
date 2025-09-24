# 场景管理系统使用指南

## 概述

场景管理系统是基于DDD架构设计的测试场景编排工具，支持创建、管理和执行复杂的API测试场景。系统采用分层架构设计，提供灵活的场景配置和执行能力。

## 核心特性

### 🎯 场景管理
- **场景创建**: 支持创建各种类型的测试场景
- **API编排**: 灵活配置多个API的调用顺序和依赖关系
- **执行策略**: 支持多种执行模式和条件控制
- **数据持久化**: 基于SQLite数据库的可靠存储
- **执行监控**: 完整的执行日志和状态跟踪

### 🔄 场景类型
1. **功能测试场景 (functional)**: 验证API功能正确性
2. **性能测试场景 (performance)**: 测试API性能指标
3. **集成测试场景 (integration)**: 测试多个API的集成
4. **回归测试场景 (regression)**: 回归测试验证

### 🛠 高级功能
- **场景模板**: 创建可重用的场景模板
- **执行步骤**: 详细的执行步骤记录和追踪
- **执行日志**: 完整的执行过程日志记录
- **优先级管理**: 支持场景优先级设置

## 数据模型

### 测试场景表 (test_scenarios)

```sql
CREATE TABLE test_scenarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  api_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  scenario_type TEXT NOT NULL DEFAULT 'functional',
  test_data TEXT,
  expected_result TEXT,
  priority INTEGER NOT NULL DEFAULT 1,
  enabled INTEGER NOT NULL DEFAULT 1,
  version TEXT NOT NULL DEFAULT '1.0.0',
  tags TEXT,
  config TEXT,
  order_index INTEGER NOT NULL DEFAULT 0,
  deleted INTEGER NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (api_id) REFERENCES api_interfaces(id)
);
```

### 测试执行表 (test_executions)

```sql
CREATE TABLE test_executions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scenario_id INTEGER NOT NULL,
  execution_status TEXT NOT NULL DEFAULT 'pending',
  start_time DATETIME,
  end_time DATETIME,
  duration_ms INTEGER,
  result_data TEXT,
  error_message TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (scenario_id) REFERENCES test_scenarios(id)
);
```

## 架构设计

### 目录结构

```
scenario_management/
├── domain/                    # 领域层
│   ├── entities/             # 实体
│   │   ├── scenario.py       # 场景实体
│   │   └── execution.py      # 执行实体
│   ├── value_objects/        # 值对象
│   │   ├── scenario_type.py  # 场景类型
│   │   └── execution_status.py # 执行状态
│   └── repositories/         # 仓储接口
│       └── scenario_repository.py
├── application/              # 应用层
│   ├── services/            # 应用服务
│   │   └── scenario_service.py
│   ├── commands/            # 命令
│   │   └── scenario_commands.py
│   └── queries/             # 查询
│       └── scenario_queries.py
├── infrastructure/          # 基础设施层
│   ├── persistence/         # 数据持久化
│   │   └── scenario_dao.py
│   └── database/           # 数据库配置
└── presentation/           # 表现层
    └── controllers/        # 控制器
        └── scenario_controller.py
```

## 使用方法

### 1. 创建测试场景

通过REST API创建测试场景：

```bash
curl -X POST "http://localhost:8000/api/v1/scenarios" \
  -H "Content-Type: application/json" \
  -d '{
    "api_id": 1,
    "name": "用户注册测试",
    "description": "测试用户注册功能",
    "scenario_type": "functional",
    "test_data": "{\"username\": \"test\", \"email\": \"test@example.com\"}",
    "expected_result": "{\"success\": true}",
    "priority": 1
  }'
```

### 2. 查询测试场景

```bash
# 获取所有场景
curl -X GET "http://localhost:8000/api/v1/scenarios"

# 按API ID查询
curl -X GET "http://localhost:8000/api/v1/scenarios?api_id=1"

# 按场景类型查询
curl -X GET "http://localhost:8000/api/v1/scenarios?scenario_type=functional"
```

### 3. 执行测试场景

```bash
curl -X POST "http://localhost:8000/api/v1/scenarios/1/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "execution_config": {
      "timeout": 30,
      "retry_count": 3
    }
  }'
    }
}

result = await scenario_manager.create_scenario(**scenario_data)
scenario_id = result['scenario']['id']

# 添加API（按执行顺序）
apis = [
    {
        'api_id': 1,  # 邮箱验证API
        'execution_order': 1,
        'parameter_mapping': {
            'email': '${user_email}'
        },
        'response_mapping': {
            'is_valid': 'email_validation_result'
        },
        'is_required': True,
        'timeout_seconds': 30
    },
    {
        'api_id': 2,  # 用户创建API
        'execution_order': 2,
        'parameter_mapping': {
            'email': '${user_email}',
            'name': '${user_name}'
        },
        'response_mapping': {
            'user_id': 'created_user_id'
        },
        'pre_condition': '${email_validation_result} == true',
        'is_required': True,
        'timeout_seconds': 60
    },
    {
        'api_id': 3,  # 发送欢迎邮件API
        'execution_order': 3,
        'parameter_mapping': {
            'user_id': '${created_user_id}',
            'email': '${user_email}'
        },
        'is_required': False,
        'timeout_seconds': 30
    }
]

# 添加API到场景
for api_config in apis:
    await scenario_manager.add_api_to_scenario(
        scenario_id=scenario_id,
        **api_config
    )
```

#### 2. 并行执行场景

并行执行适用于相互独立的API调用：

```python
# 创建并行执行场景
scenario_data = {
    'name': '多数据源同步',
    'description': '并行同步多个数据源',
    'execution_type': ExecutionType.PARALLEL.value,
    'config': {
        'timeout_seconds': 600,
        'allow_partial_success': True
    },
    'variables': {
        'sync_timestamp': datetime.utcnow().isoformat(),
        'batch_size': 1000
    }
}

result = await scenario_manager.create_scenario(**scenario_data)
scenario_id = result['scenario']['id']

# 添加并行执行的API
parallel_apis = [
    {
        'api_id': 4,  # 用户数据同步
        'execution_order': 1,
        'execution_group': 'sync_group_1',
        'parameter_mapping': {
            'timestamp': '${sync_timestamp}',
            'data_type': 'users'
        },
        'timeout_seconds': 300
    },
    {
        'api_id': 5,  # 订单数据同步
        'execution_order': 1,
        'execution_group': 'sync_group_1',
        'parameter_mapping': {
            'timestamp': '${sync_timestamp}',
            'data_type': 'orders'
        },
        'timeout_seconds': 300
    },
    {
        'api_id': 6,  # 产品数据同步
        'execution_order': 1,
        'execution_group': 'sync_group_1',
        'parameter_mapping': {
            'timestamp': '${sync_timestamp}',
            'data_type': 'products'
        },
        'timeout_seconds': 300
    }
]

for api_config in parallel_apis:
    await scenario_manager.add_api_to_scenario(
        scenario_id=scenario_id,
        **api_config
    )
```

#### 3. 混合执行场景

混合执行结合了顺序和并行执行：

```python
# 创建混合执行场景
scenario_data = {
    'name': '电商订单处理流程',
    'description': '包含验证、检查、支付和后续处理的完整流程',
    'execution_type': ExecutionType.MIXED.value,
    'config': {
        'timeout_seconds': 900,
        'rollback_on_failure': True
    },
    'variables': {
        'order_id': 'ORD-2024-001',
        'customer_id': 'CUST-001'
    }
}

result = await scenario_manager.create_scenario(**scenario_data)
scenario_id = result['scenario']['id']

# 添加混合执行的API
mixed_apis = [
    # 第一组：订单验证（顺序执行）
    {
        'api_id': 7,
        'execution_order': 1,
        'execution_group': 'validation',
        'parameter_mapping': {'order_id': '${order_id}'},
        'response_mapping': {'is_valid': 'order_valid'}
    },
    {
        'api_id': 8,
        'execution_order': 2,
        'execution_group': 'validation',
        'parameter_mapping': {'customer_id': '${customer_id}'},
        'pre_condition': '${order_valid} == true'
    },
    
    # 第二组：并行检查（库存、价格、优惠）
    {
        'api_id': 9,
        'execution_order': 3,
        'execution_group': 'parallel_checks',
        'parameter_mapping': {'order_id': '${order_id}'},
        'response_mapping': {'stock_available': 'inventory_status'}
    },
    {
        'api_id': 10,
        'execution_order': 3,
        'execution_group': 'parallel_checks',
        'parameter_mapping': {'order_id': '${order_id}'},
        'response_mapping': {'final_price': 'calculated_price'}
    },
    
    # 第三组：支付处理（顺序执行）
    {
        'api_id': 11,
        'execution_order': 4,
        'execution_group': 'payment',
        'parameter_mapping': {
            'amount': '${calculated_price}',
            'customer_id': '${customer_id}'
        },
        'pre_condition': '${inventory_status} == "available"',
        'response_mapping': {'payment_id': 'transaction_id'}
    }
]

for api_config in mixed_apis:
    await scenario_manager.add_api_to_scenario(
        scenario_id=scenario_id,
        **api_config
    )
```

### 场景执行

#### 执行场景

```python
# 执行场景
execution_variables = {
    'execution_id': f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
    'environment': 'production'
}

result = await scenario_executor.execute_scenario(
    scenario_id=scenario_id,
    variables=execution_variables
)

if result['success']:
    execution_record = result['execution_record']
    print(f"执行完成，ID: {execution_record['id']}")
    print(f"状态: {execution_record['status']}")
    print(f"执行时间: {execution_record['execution_time']}秒")
else:
    print(f"执行失败: {result['error']}")
```

#### 监控执行状态

```python
# 获取执行状态
execution_id = "exec_123"
status_result = await scenario_executor.get_execution_status(execution_id)

if status_result['success']:
    status = status_result['status']
    print(f"执行状态: {status['status']}")
    print(f"进度: {status['progress']}%")
    print(f"当前步骤: {status['current_step']}")
```

### 场景管理操作

#### 列出场景

```python
# 获取所有场景
result = await scenario_manager.list_scenarios()
if result['success']:
    for scenario in result['scenarios']:
        print(f"场景: {scenario['name']} (ID: {scenario['id']})")
        print(f"类型: {scenario['execution_type']}")
        print(f"API数量: {len(scenario['apis'])}")
```

#### 更新场景

```python
# 更新场景信息
update_data = {
    'description': '更新后的场景描述',
    'config': {
        'timeout_seconds': 600,
        'max_retries': 5
    }
}

result = await scenario_manager.update_scenario(
    scenario_id=scenario_id,
    **update_data
)
```

#### 删除场景

```python
# 删除场景
result = await scenario_manager.delete_scenario(scenario_id)
if result['success']:
    print("场景删除成功")
```

### 场景模板

#### 创建模板

```python
# 创建场景模板
template_result = await scenario_manager.create_scenario_template(
    name="API测试模板",
    description="用于API测试的通用模板",
    template_config={
        'default_timeout': 60,
        'default_retry_count': 2,
        'required_variables': ['api_endpoint', 'test_data']
    }
)

template_id = template_result['template']['id']
```

#### 从模板创建场景

```python
# 从模板创建场景
result = await scenario_manager.create_scenario_from_template(
    template_id=template_id,
    scenario_name="基于模板的测试场景",
    variables={
        'api_endpoint': 'https://api.example.com/test',
        'test_data': {'key': 'value'}
    }
)
```

### 批量操作

#### 批量创建场景

```python
# 批量创建场景
batch_scenarios = [
    {
        'name': '批量测试场景1',
        'description': '批量创建的测试场景1',
        'execution_type': ExecutionType.SEQUENTIAL.value
    },
    {
        'name': '批量测试场景2',
        'description': '批量创建的测试场景2',
        'execution_type': ExecutionType.PARALLEL.value
    }
]

result = await scenario_manager.batch_create_scenarios(batch_scenarios)
if result['success']:
    print(f"批量创建 {len(result['scenarios'])} 个场景成功")
```

#### 导出和导入

```python
# 导出场景
export_result = await scenario_manager.export_scenarios(
    format='json',
    include_execution_records=False
)

if export_result['success']:
    # 保存到文件
    with open('scenarios_export.json', 'w') as f:
        json.dump(export_result['data'], f, indent=2)

# 导入场景
with open('scenarios_export.json', 'r') as f:
    import_data = json.load(f)

import_result = await scenario_manager.import_scenarios(
    data=import_data,
    format='json'
)
```

## 参数映射和变量系统

### 变量语法

场景管理系统支持强大的变量系统：

```python
# 变量引用语法
'${variable_name}'          # 引用变量
'${response.field_name}'    # 引用响应字段
'${env.ENVIRONMENT_VAR}'    # 引用环境变量
'${func.uuid()}'           # 调用内置函数
```

### 参数映射示例

```python
api_config = {
    'api_id': 1,
    'parameter_mapping': {
        # 直接变量引用
        'user_id': '${user_id}',
        
        # 响应字段引用
        'email': '${previous_response.email}',
        
        # 组合字符串
        'full_name': '${first_name} ${last_name}',
        
        # 条件表达式
        'status': '${age >= 18 ? "adult" : "minor"}',
        
        # 数组和对象
        'tags': ['${category}', 'test'],
        'metadata': {
            'created_by': '${user_name}',
            'timestamp': '${func.now()}'
        }
    },
    'response_mapping': {
        # 将响应字段映射到变量
        'user_id': 'created_user_id',
        'status': 'creation_status',
        'details.email': 'user_email'  # 嵌套字段映射
    }
}
```

### 条件执行

```python
api_config = {
    'api_id': 2,
    'pre_condition': '${email_validation_result} == true && ${user_age} >= 18',
    'post_condition': '${response.status} == "success"',
    'parameter_mapping': {
        'email': '${user_email}'
    }
}
```

## 数据库结构

### 主要表结构

```sql
-- 场景表
CREATE TABLE scenarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    execution_type ENUM('sequential', 'parallel', 'conditional', 'mixed') NOT NULL,
    status ENUM('active', 'inactive', 'archived') DEFAULT 'active',
    config JSON,
    variables JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 场景API关联表
CREATE TABLE scenario_apis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scenario_id INT NOT NULL,
    api_id INT NOT NULL,
    execution_order INT NOT NULL,
    execution_group VARCHAR(100),
    parameter_mapping JSON,
    response_mapping JSON,
    pre_condition TEXT,
    post_condition TEXT,
    timeout_seconds INT,
    retry_count INT DEFAULT 0,
    is_required BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE
);

-- 执行记录表
CREATE TABLE execution_records (
    id VARCHAR(100) PRIMARY KEY,
    scenario_id INT NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed', 'cancelled') NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    execution_time DECIMAL(10,3),
    variables JSON,
    result JSON,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
);
```

## 集成功能

### 与工作流编排系统集成

```python
from src.auto_test.scenario_management import get_scenario_integration

# 获取集成实例
integration = get_scenario_integration(DATABASE_URL)

# 将场景转换为工作流
result = await integration.scenario_to_workflow(
    scenario_id=scenario_id,
    workflow_name="转换的工作流",
    create_workflow=True
)

# 将工作流转换为场景
result = await integration.workflow_to_scenario(
    workflow_id=workflow_id,
    scenario_name="转换的场景",
    create_scenario=True
)

# 统一执行接口
result = await integration.execute_unified(
    execution_type='scenario',
    execution_id=scenario_id,
    variables={'env': 'production'}
)
```

### 获取集成状态

```python
# 获取集成状态
status_result = await integration.get_integration_status()
if status_result['success']:
    status = status_result['status']
    print(f"工作流模块可用: {status['workflow_available']}")
    print(f"API管理模块可用: {status['api_management_available']}")
    print(f"场景总数: {status['statistics']['total_scenarios']}")
```

## 最佳实践

### 1. 场景设计原则

- **单一职责**: 每个场景应该专注于一个特定的业务流程
- **模块化**: 将复杂流程拆分为多个较小的场景
- **可重用**: 使用场景模板提高复用性
- **容错性**: 合理设置超时和重试机制

### 2. 执行策略选择

- **顺序执行**: 适用于有明确依赖关系的API调用
- **并行执行**: 适用于相互独立的API调用，可提高执行效率
- **混合执行**: 适用于复杂业务流程，结合顺序和并行的优势
- **条件执行**: 适用于需要根据条件动态决定执行路径的场景

### 3. 参数映射技巧

```python
# 使用描述性的变量名
parameter_mapping = {
    'user_email': '${registration.email}',
    'user_full_name': '${registration.first_name} ${registration.last_name}'
}

# 使用条件表达式处理可选参数
parameter_mapping = {
    'notification_enabled': '${user_preferences.notifications || false}',
    'user_type': '${user_age >= 18 ? "adult" : "minor"}'
}

# 使用函数生成动态值
parameter_mapping = {
    'request_id': '${func.uuid()}',
    'timestamp': '${func.now()}',
    'random_number': '${func.random(1, 100)}'
}
```

### 4. 错误处理

```python
# 设置合理的超时时间
api_config = {
    'timeout_seconds': 60,  # 根据API复杂度设置
    'retry_count': 3,       # 设置重试次数
    'is_required': True     # 标记是否为必需API
}

# 使用条件控制执行
api_config = {
    'pre_condition': '${previous_api_success} == true',
    'post_condition': '${response.status} == "success"'
}
```

### 5. 性能优化

- **合理使用并行执行**: 对于独立的API调用使用并行执行
- **设置适当的超时**: 避免长时间等待
- **使用执行组**: 在混合执行中合理分组
- **监控执行时间**: 定期检查和优化慢执行的场景

## 故障排除

### 常见问题

#### 1. 数据库连接问题

```python
# 检查数据库连接
try:
    await scenario_manager.initialize_database()
    print("数据库连接成功")
except Exception as e:
    print(f"数据库连接失败: {e}")
    # 检查数据库URL、用户名、密码等配置
```

#### 2. 场景执行失败

```python
# 检查场景配置
scenario_result = await scenario_manager.get_scenario(scenario_id)
if scenario_result['success']:
    scenario = scenario_result['scenario']
    print(f"场景状态: {scenario['status']}")
    print(f"API数量: {len(scenario['apis'])}")
    
    # 检查每个API的配置
    for api in scenario['apis']:
        print(f"API {api['api_id']}: 必需={api['is_required']}, 超时={api['timeout_seconds']}")
```

#### 3. 参数映射错误

```python
# 验证参数映射
test_variables = {
    'user_email': 'test@example.com',
    'user_name': 'TestUser'
}

# 检查变量是否正确解析
for api in scenario['apis']:
    parameter_mapping = api['parameter_mapping']
    for key, value in parameter_mapping.items():
        if '${' in value:
            print(f"参数 {key} 使用变量: {value}")
            # 确保所需变量在 test_variables 中存在
```

### 调试技巧

#### 1. 启用详细日志

```python
import logging

# 设置详细日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('scenario_management')
logger.setLevel(logging.DEBUG)
```

#### 2. 使用测试模式

```python
# 创建测试场景
test_scenario = {
    'name': '测试场景',
    'description': '用于调试的测试场景',
    'execution_type': ExecutionType.SEQUENTIAL.value,
    'config': {
        'test_mode': True,  # 启用测试模式
        'dry_run': True     # 只验证不实际执行
    }
}
```

#### 3. 分步执行

```python
# 逐个API测试
for api in scenario['apis']:
    # 单独测试每个API的配置
    single_api_scenario = {
        'name': f"测试API {api['api_id']}",
        'execution_type': ExecutionType.SEQUENTIAL.value,
        'apis': [api]
    }
    # 执行单个API测试
```

## 扩展开发

### 自定义执行策略

```python
from src.auto_test.scenario_management.executor import ScenarioExecutor

class CustomScenarioExecutor(ScenarioExecutor):
    async def execute_custom_strategy(
        self,
        scenario_apis: List[Dict],
        context: ExecutionContext
    ) -> List[APIExecutionResult]:
        """自定义执行策略"""
        results = []
        
        # 实现自定义执行逻辑
        for api in scenario_apis:
            # 自定义执行逻辑
            result = await self._execute_single_api(api, context)
            results.append(result)
            
            # 自定义条件判断
            if not result.success and api.get('stop_on_failure'):
                break
        
        return results
```

### 自定义参数解析器

```python
from src.auto_test.scenario_management.models import ParameterResolver

class CustomParameterResolver(ParameterResolver):
    def resolve_custom_function(self, func_name: str, args: List[str]) -> Any:
        """解析自定义函数"""
        if func_name == 'custom_uuid':
            return f"CUSTOM-{uuid.uuid4()}"
        elif func_name == 'custom_timestamp':
            return datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        else:
            return super().resolve_function(func_name, args)
```

## 版本更新

### v1.0.0 (当前版本)
- 基础场景管理功能
- 多种执行策略支持
- 参数映射和变量系统
- SQLite数据库集成
- 基础监控和日志

### 计划功能
- 可视化场景编辑器
- 更多内置函数
- 性能监控和分析
- 分布式执行支持
- 更多数据库支持

## 技术支持

### 获取帮助

1. **查看日志**: 检查详细的执行日志
2. **参考示例**: 查看 `examples/scenario_management_example.py`
3. **检查配置**: 验证数据库连接和API配置
4. **测试环境**: 在测试环境中验证场景配置

### 性能监控

```python
# 获取执行统计
stats_result = await scenario_manager.get_execution_statistics(
    start_date='2024-01-01',
    end_date='2024-12-31'
)

if stats_result['success']:
    stats = stats_result['statistics']
    print(f"总执行次数: {stats['total_executions']}")
    print(f"成功率: {stats['success_rate']}%")
    print(f"平均执行时间: {stats['avg_execution_time']}秒")
```

---

通过本指南，您可以充分利用场景管理系统的强大功能，创建和管理复杂的接口流程编排，实现高效的自动化测试和业务流程执行。所有数据都安全地存储在SQLite数据库中，确保数据的持久性和可靠性。