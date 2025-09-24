# 后端 API 参考文档

本文档提供了AI自动化测试平台后端API的完整参考。

## 基础信息

- **基础URL**: `http://localhost:8000`
- **API版本**: v2.0.0
- **认证方式**: 暂无（开发阶段）
- **数据格式**: JSON

### 🏗️ 架构特点

- **分层架构**: 表现层、应用层、领域层、基础设施层
- **聚合设计**: 通过聚合根维护业务一致性
- **事件驱动**: 使用领域事件处理跨聚合操作
- **类型安全**: 完整的Pydantic数据验证
- **依赖注入**: 松耦合的组件设计

### 📋 响应格式

所有API响应都遵循RESTful设计原则和统一的数据传输对象（DTO）格式：

**成功响应**:
```json
{
  "id": "uuid",
  "name": "资源名称",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**列表响应**:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "has_next": true
}
```

**错误响应**:
```json
{
  "detail": "具体错误描述",
  "error_code": "DOMAIN_VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z",
  "path": "/api/v1/systems"
}
```

**验证错误响应**:
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "字段不能为空",
      "type": "value_error.missing"
    }
  ]
}
```

## 🏥 健康检查和监控

### GET /health

检查API服务健康状态。

**响应示例**:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "architecture": "DDD",
  "database": "connected",
  "dependencies": {
    "event_bus": "active",
    "cache": "connected"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### GET /ready

检查服务就绪状态（用于Kubernetes就绪探针）。

**响应示例**:
```json
{
  "ready": true,
  "checks": {
    "database": "ok",
    "migrations": "up_to_date",
    "dependencies": "loaded"
  }
}
```

### GET /metrics

获取服务指标（Prometheus格式）。

**响应**: Prometheus metrics format

## 🔧 系统管理聚合 (System Management Aggregate)

基于DDD设计，系统管理是一个独立的聚合，负责管理测试系统的配置、状态和生命周期。

### GET /api/v1/systems

获取所有测试系统列表。

**查询参数**:
- `page` (int, 可选): 页码，默认为1
- `size` (int, 可选): 每页数量，默认为20
- `category` (str, 可选): 系统分类筛选
- `status` (str, 可选): 状态筛选 (active, inactive, maintenance)
- `search` (str, 可选): 名称或描述搜索

**响应示例**:
```json
{
  "items": [
    {
      "id": "sys_001",
      "name": "用户管理系统",
      "description": "处理用户相关业务逻辑",
      "category": "user_management",
      "base_url": "https://api.example.com/users",
      "version": "1.0.0",
      "status": "active",
      "health_check_url": "/health",
      "authentication": {
        "type": "bearer_token",
        "required": true
      },
      "rate_limit": {
        "requests_per_minute": 1000,
        "burst_limit": 100
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "has_next": false
}
```

### POST /api/v1/systems

创建新的测试系统。

**请求体**:
```json
{
  "name": "订单管理系统",
  "description": "处理电商订单相关业务逻辑",
  "category": "order_management",
  "base_url": "https://api.example.com/orders",
  "version": "1.0.0",
  "health_check_url": "/health",
  "authentication": {
    "type": "bearer_token",
    "required": true,
    "token_endpoint": "/auth/token"
  },
  "rate_limit": {
    "requests_per_minute": 500,
    "burst_limit": 50
  },
  "endpoints": [
    {
      "path": "/orders",
      "method": "GET",
      "description": "获取订单列表"
    },
    {
      "path": "/orders",
      "method": "POST", 
      "description": "创建新订单"
    }
  ],
  "tags": ["订单", "电商", "业务系统"]
}
```

**字段说明**:
- `name` (string, 必需): 系统名称，1-100字符
- `description` (string, 可选): 系统描述，最大1000字符
- `category` (string, 必需): 系统分类
- `base_url` (string, 必需): 系统基础URL
- `version` (string, 可选): 系统版本号
- `health_check_url` (string, 可选): 健康检查端点
- `authentication` (object, 可选): 认证配置
- `rate_limit` (object, 可选): 限流配置
- `endpoints` (array, 可选): 端点列表
- `tags` (array, 可选): 标签列表

**响应示例**:
```json
{
  "id": "sys_002",
  "name": "订单管理系统",
  "description": "处理电商订单相关业务逻辑",
  "category": "order_management",
  "base_url": "https://api.example.com/orders",
  "version": "1.0.0",
  "status": "active",
  "health_check_url": "/health",
  "authentication": {
    "type": "bearer_token",
    "required": true,
    "token_endpoint": "/auth/token"
  },
  "rate_limit": {
    "requests_per_minute": 500,
    "burst_limit": 50
  },
  "endpoints": [
    {
      "path": "/orders",
      "method": "GET",
      "description": "获取订单列表"
    },
    {
      "path": "/orders", 
      "method": "POST",
      "description": "创建新订单"
    }
  ],
  "tags": ["订单", "电商", "业务系统"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### GET /api/v1/systems/{system_id}

获取指定测试系统的详细信息。

**路径参数**:
- `system_id` (string, 必需): 系统的唯一标识符

**响应示例**:
```json
{
  "id": "sys_001",
  "name": "用户管理系统",
  "description": "处理用户相关业务逻辑",
  "category": "user_management",
  "base_url": "https://api.example.com/users",
  "version": "1.0.0",
  "status": "active",
  "health_check_url": "/health",
  "authentication": {
    "type": "bearer_token",
    "required": true
  },
  "rate_limit": {
    "requests_per_minute": 1000,
    "burst_limit": 100
  },
  "endpoints": [
    {
      "path": "/users",
      "method": "GET",
      "description": "获取用户列表"
    },
    {
      "path": "/users/{id}",
      "method": "GET", 
      "description": "获取用户详情"
    }
  ],
  "tags": ["用户", "认证", "权限"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### PUT /api/v1/systems/{system_id}

更新指定测试系统的信息。

**路径参数**:
- `system_id` (string, 必需): 系统的唯一标识符

**请求体**:
```json
{
  "name": "用户管理系统（增强版）",
  "description": "处理用户相关业务逻辑，支持多租户",
  "version": "2.0.0",
  "rate_limit": {
    "requests_per_minute": 2000,
    "burst_limit": 200
  },
  "endpoints": [
    {
      "path": "/users",
      "method": "GET",
      "description": "获取用户列表"
    },
    {
      "path": "/users/{id}",
      "method": "GET",
      "description": "获取用户详情"
    },
    {
      "path": "/users/{id}/profile",
      "method": "GET",
      "description": "获取用户档案"
    }
  ],
  "tags": ["用户", "认证", "权限", "多租户"]
}
```

**响应示例**:
```json
{
  "id": "sys_001",
  "name": "用户管理系统（增强版）",
  "description": "处理用户相关业务逻辑，支持多租户",
  "category": "user_management",
  "base_url": "https://api.example.com/users",
  "version": "2.0.0",
  "status": "active",
  "health_check_url": "/health",
  "authentication": {
    "type": "bearer_token",
    "required": true
  },
  "rate_limit": {
    "requests_per_minute": 2000,
    "burst_limit": 200
  },
  "endpoints": [
    {
      "path": "/users",
      "method": "GET",
      "description": "获取用户列表"
    },
    {
      "path": "/users/{id}",
      "method": "GET",
      "description": "获取用户详情"
    },
    {
      "path": "/users/{id}/profile",
      "method": "GET",
      "description": "获取用户档案"
    }
  ],
  "tags": ["用户", "认证", "权限", "多租户"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### DELETE /api/v1/systems/{system_id}

删除指定的测试系统。

**路径参数**:
- `system_id` (string, 必需): 系统的唯一标识符

**查询参数**:
- `hard_delete` (boolean, 可选): 是否硬删除，默认false（软删除）

**请求示例**:
```bash
DELETE /api/v1/systems/sys_001?hard_delete=false
```

**响应示例**:
```json
{
  "message": "系统已成功删除",
  "deleted_id": "sys_001",
  "hard_delete": false
}
```

## 🤖 智能代理聚合 (Agent Aggregate)

智能代理聚合负责管理AI测试代理的配置、执行和监控。

### GET /api/v1/agents

获取所有智能代理列表。

**查询参数**:
- `page` (int, 可选): 页码，默认为1
- `size` (int, 可选): 每页数量，默认为20
- `type` (str, 可选): 代理类型筛选 (test_executor, data_generator, validator)
- `status` (str, 可选): 状态筛选 (active, idle, busy, error)

**响应示例**:
```json
{
  "items": [
    {
      "id": "agent_001",
      "name": "API测试执行代理",
      "type": "test_executor",
      "description": "专门执行API自动化测试",
      "status": "active",
      "capabilities": [
        "http_requests",
        "response_validation",
        "performance_testing"
      ],
      "configuration": {
        "max_concurrent_tests": 10,
        "timeout_seconds": 30,
        "retry_attempts": 3
      },
      "metrics": {
        "tests_executed": 1250,
        "success_rate": 0.95,
        "average_response_time": 150
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "has_next": false
}
```

### POST /api/v1/agents

创建新的智能代理。

**请求体**:
```json
{
  "name": "数据验证代理",
  "type": "validator",
  "description": "验证测试数据的完整性和准确性",
  "capabilities": [
    "data_validation",
    "schema_checking",
    "business_rule_validation"
  ],
  "configuration": {
    "validation_rules": ["not_null", "format_check", "range_check"],
    "error_threshold": 0.05,
    "batch_size": 100
  }
}
```

## 🧪 测试执行聚合 (Test Execution Aggregate)

测试执行聚合负责管理测试用例的执行、结果收集和报告生成。

### GET /api/v1/test-executions

获取测试执行记录列表。

**查询参数**:
- `page` (int, 可选): 页码，默认为1
- `size` (int, 可选): 每页数量，默认为20
- `status` (str, 可选): 执行状态筛选 (pending, running, completed, failed)
- `system_id` (str, 可选): 按系统ID筛选
- `agent_id` (str, 可选): 按代理ID筛选

**响应示例**:
```json
{
  "items": [
    {
      "id": "exec_001",
      "system_id": "sys_001",
      "agent_id": "agent_001",
      "test_suite": "用户管理API测试套件",
      "status": "completed",
      "started_at": "2024-01-01T10:00:00Z",
      "completed_at": "2024-01-01T10:05:30Z",
      "duration_seconds": 330,
      "results": {
        "total_tests": 25,
        "passed": 23,
        "failed": 2,
        "skipped": 0,
        "success_rate": 0.92
      },
      "metrics": {
        "average_response_time": 145,
        "max_response_time": 890,
        "min_response_time": 45
      },
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:05:30Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "has_next": false
}
```

### POST /api/v1/test-executions

启动新的测试执行。

**请求体**:
```json
{
  "system_id": "sys_001",
  "agent_id": "agent_001",
  "test_suite": "用户管理API测试套件",
  "configuration": {
    "parallel_execution": true,
    "max_workers": 5,
    "timeout_seconds": 300,
    "retry_failed_tests": true
  },
  "test_cases": [
    {
      "name": "获取用户列表",
      "endpoint": "/users",
      "method": "GET",
      "expected_status": 200
    },
    {
      "name": "创建新用户",
      "endpoint": "/users",
      "method": "POST",
      "payload": {"name": "测试用户", "email": "test@example.com"},
      "expected_status": 201
    }
  ]
}
```

## 🔗 端点管理聚合 (Endpoint Management Aggregate)

端点管理聚合负责管理系统内具体API端点的配置和调用。

### POST /apis/{api_id}/call

调用指定的API并记录结果。

**路径参数**:
- `api_id` (string, 必需): API的唯一标识符

**请求体**:
```json
{
  "parameters": {
    "page": 1,
    "size": 10,
    "search": "张三"
  },
  "headers": {
    "Authorization": "Bearer custom_token",
    "X-Custom-Header": "custom_value"
  },
  "timeout": 30
}
```

**字段说明**:
- `parameters` (object, 可选): 调用参数，会与API记录中的参数合并
- `headers` (object, 可选): 额外的请求头，会与API记录中的请求头合并
- `timeout` (int, 可选): 超时时间（秒），默认30，范围1-300

**响应示例**:

成功调用:
```json
{
  "success": true,
  "status_code": 200,
  "response_data": {
    "users": [
      {"id": "1", "name": "张三", "email": "zhangsan@example.com"}
    ],
    "total": 1
  },
  "error_message": null,
  "response_time": 150,
  "call_record_id": "record_123456"
}
```

失败调用:
```json
{
  "success": false,
  "status_code": 404,
  "response_data": null,
  "error_message": "API endpoint not found",
  "response_time": 100,
  "call_record_id": "record_789012"
}
```

## 调用记录

### GET /apis/{api_id}/records

获取指定API的调用记录。

**路径参数**:
- `api_id` (string, 必需): API的唯一标识符

**查询参数**:
- `skip` (int, 可选): 跳过的记录数，默认0
- `limit` (int, 可选): 返回的记录数，默认50，最大100

**请求示例**:
```bash
GET /apis/api_123456/records?skip=0&limit=20
```

**响应示例**:
```json
[
  {
    "id": "record_123456",
    "api_id": "api_123456",
    "request_parameters": "{\"page\": 1, \"size\": 10}",
    "request_headers": "{\"Authorization\": \"Bearer token\"}",
    "response_status_code": 200,
    "response_data": "{\"users\": [], \"total\": 0}",
    "response_time": 150,
    "success": true,
    "error_message": null,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

## ⚠️ 错误处理

### HTTP状态码

- `200` - 请求成功
- `201` - 资源创建成功
- `204` - 请求成功，无返回内容
- `400` - 请求参数错误
- `401` - 未授权访问
- `403` - 权限不足
- `404` - 资源不存在
- `409` - 资源冲突
- `422` - 数据验证失败
- `429` - 请求频率超限
- `500` - 服务器内部错误
- `503` - 服务不可用

### 领域错误码

基于DDD设计，每个聚合都有自己的错误码前缀：

- `SYS_xxx` - 系统管理聚合错误
- `AGT_xxx` - 智能代理聚合错误
- `TST_xxx` - 测试执行聚合错误
- `EPT_xxx` - 端点管理聚合错误

### 常见错误示例

**400 Bad Request**:
```json
{
  "detail": "Invalid request parameters",
  "error_code": "SYS_INVALID_PARAMS",
  "timestamp": "2024-01-01T00:00:00Z",
  "path": "/api/v1/systems"
}
```

**404 Not Found**:
```json
{
  "detail": "System not found",
  "error_code": "SYS_NOT_FOUND",
  "timestamp": "2024-01-01T00:00:00Z",
  "path": "/api/v1/systems/sys_999"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "系统名称不能为空",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "base_url"],
      "msg": "URL格式不正确",
      "type": "value_error.url"
    }
  ],
  "error_code": "SYS_VALIDATION_ERROR"
}
```

**429 Rate Limit Exceeded**:
```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 💡 使用示例

### Python示例 (使用httpx)

```python
import httpx
import asyncio

class AutoTestClient:
    def __init__(self, base_url="http://localhost:8003"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def get_systems(self, page=1, size=20):
        """获取系统列表"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/systems",
            params={"page": page, "size": size}
        )
        return response.json()
    
    async def create_system(self, system_data):
        """创建新系统"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/systems",
            json=system_data
        )
        return response.json()
    
    async def execute_test(self, execution_data):
        """执行测试"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/test-executions",
            json=execution_data
        )
        return response.json()

# 使用示例
async def main():
    client = AutoTestClient()
    
    # 获取系统列表
    systems = await client.get_systems()
    print(f"找到 {systems['total']} 个系统")
    
    # 创建新系统
    new_system = {
        "name": "订单管理系统",
        "description": "处理电商订单业务",
        "category": "order_management",
        "base_url": "https://api.shop.com/orders"
    }
    created = await client.create_system(new_system)
    print(f"创建系统: {created['id']}")

asyncio.run(main())
```

### TypeScript示例

```typescript
interface System {
  id: string;
  name: string;
  description: string;
  category: string;
  base_url: string;
  status: 'active' | 'inactive' | 'maintenance';
}

interface TestExecution {
  id: string;
  system_id: string;
  agent_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  results: {
    total_tests: number;
    passed: number;
    failed: number;
    success_rate: number;
  };
}

class AutoTestAPI {
  constructor(private baseUrl = 'http://localhost:8003') {}

  async getSystems(params?: {
    page?: number;
    size?: number;
    category?: string;
    status?: string;
  }): Promise<{ items: System[]; total: number }> {
    const url = new URL('/api/v1/systems', this.baseUrl);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.set(key, value.toString());
        }
      });
    }

    const response = await fetch(url.toString());
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  async createSystem(systemData: Omit<System, 'id' | 'status'>): Promise<System> {
    const response = await fetch(`${this.baseUrl}/api/v1/systems`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(systemData)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  async getTestExecutions(systemId?: string): Promise<{ items: TestExecution[] }> {
    const url = new URL('/api/v1/test-executions', this.baseUrl);
    if (systemId) {
      url.searchParams.set('system_id', systemId);
    }

    const response = await fetch(url.toString());
    return response.json();
  }
}
```

### cURL示例

```bash
# 获取系统列表
curl -X GET "http://localhost:8003/api/v1/systems?page=1&size=10" \
  -H "Accept: application/json"

# 创建新系统
curl -X POST "http://localhost:8003/api/v1/systems" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "支付系统",
    "description": "处理支付相关业务",
    "category": "payment",
    "base_url": "https://api.payment.com",
    "authentication": {
      "type": "bearer_token",
      "required": true
    }
  }'

# 启动测试执行
curl -X POST "http://localhost:8003/api/v1/test-executions" \
  -H "Content-Type: application/json" \
  -d '{
    "system_id": "sys_001",
    "agent_id": "agent_001",
    "test_suite": "支付API测试套件",
    "configuration": {
      "parallel_execution": true,
      "max_workers": 3
    }
  }'

# 获取测试执行结果
curl -X GET "http://localhost:8003/api/v1/test-executions/exec_001" \
  -H "Accept: application/json"
```

## 🎯 最佳实践

### 系统设计原则

1. **单一职责**: 每个聚合专注于特定的业务领域
2. **松耦合**: 聚合间通过事件进行通信
3. **高内聚**: 聚合内部保持强一致性
4. **事件驱动**: 使用领域事件处理跨聚合操作

### API设计规范

1. **RESTful设计**: 遵循REST原则和HTTP语义
2. **版本控制**: 使用URL路径版本控制 (`/api/v1/`)
3. **统一响应**: 保持响应格式的一致性
4. **错误处理**: 提供清晰的错误信息和错误码

### 性能优化

1. **分页查询**: 大数据集使用分页避免性能问题
2. **缓存策略**: 合理使用缓存提升响应速度
3. **异步处理**: 长时间操作使用异步模式
4. **限流保护**: 实施请求频率限制

### 安全考虑

1. **认证授权**: 生产环境必须启用JWT认证
2. **输入验证**: 严格验证所有输入数据
3. **HTTPS**: 生产环境强制使用HTTPS
4. **审计日志**: 记录所有重要操作

## 📋 更新日志

### v3.0.0 (2024-01-01) - DDD架构重构

**重大变更**:
- 🏗️ 采用领域驱动设计(DDD)架构
- 🔄 API端点重新设计 (`/api/v1/` 前缀)
- 📦 引入聚合概念 (系统管理、智能代理、测试执行)
- 🎯 基于业务领域的模块划分

**新增功能**:
- 🤖 智能代理管理聚合
- 🧪 测试执行聚合
- 🔗 端点管理聚合
- 📊 实时监控和指标收集
- 🔄 事件驱动架构支持
- 🏥 增强的健康检查和就绪探针

**架构改进**:
- 🎯 清晰的业务边界和聚合设计
- 🔧 依赖注入和松耦合设计
- 📝 完整的类型安全和数据验证
- 🚀 更好的性能和可扩展性
- 🛡️ 增强的错误处理和安全性

**开发体验**:
- 📚 Swagger/OpenAPI 3.0 文档
- 🔍 更详细的错误信息和调试支持
- 🧪 完整的测试覆盖
- 📖 基于DDD的代码组织和文档

**迁移指南**:
- 旧版API (`/apis`) 将在v4.0.0中移除
- 建议使用新的聚合端点 (`/api/v1/systems`, `/api/v1/agents`, `/api/v1/test-executions`)
- 更新客户端代码以适配新的响应格式

---

如有问题或建议，请联系开发团队或查看项目文档。