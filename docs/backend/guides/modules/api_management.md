# API管理模块使用指南

## 概述

API管理模块基于DDD架构设计，提供完整的API接口管理功能，包括API的创建、查询、更新、删除、执行和验证等核心业务能力。模块采用分层架构，确保业务逻辑的清晰分离和高可维护性。

## 功能特性

### 核心功能
- **API生命周期管理**: 支持API的完整生命周期管理（创建、更新、删除、激活/停用）
- **多维度查询**: 支持按系统、模块、名称等多种条件查询API
- **批量操作**: 支持批量创建、更新、删除API
- **API执行**: 提供API执行功能，支持自定义请求数据和头部
- **数据验证**: 完整的API数据验证机制，确保数据完整性
- **搜索功能**: 支持模糊搜索和相似API查找
- **统计分析**: 提供API统计信息和使用分析

### 技术特性
- 基于DDD分层架构设计
- 使用FastAPI构建RESTful API
- SQLAlchemy ORM数据持久化
- Pydantic数据验证和序列化
- 异步处理支持
- 完整的错误处理和日志记录

## 架构设计

### DDD分层架构

API管理模块采用领域驱动设计（DDD）的分层架构：

```
表现层 (Presentation Layer)
├── api_controller.py          # API控制器，处理HTTP请求
└── 请求/响应模型               # Pydantic模型

应用层 (Application Layer)
├── api_service.py             # API应用服务
├── api_handlers.py            # 命令和查询处理器
├── commands/                  # 命令对象
├── queries/                   # 查询对象
└── dto/                       # 数据传输对象

领域层 (Domain Layer)
├── entities/api.py            # API实体
├── value_objects/             # 值对象（ApiPath, HttpMethod）
├── repositories/              # 仓储接口
├── services/                  # 领域服务
└── events/                    # 领域事件

基础设施层 (Infrastructure Layer)
├── repositories/              # 仓储实现
├── database/dao/              # 数据访问对象
└── external/                  # 外部服务集成
```

### 核心组件

- **API实体**: 封装API的核心业务逻辑和状态
- **值对象**: ApiPath（API路径）、HttpMethod（HTTP方法）
- **领域服务**: 处理复杂的业务规则和验证
- **应用服务**: 协调领域对象完成业务用例
- **仓储**: 提供数据持久化抽象

## 数据模型

### API实体模型

API实体包含以下核心属性：

```python
@dataclass
class Api:
    """API实体"""
    id: Optional[str] = None                    # API唯一标识
    name: str = ""                              # API名称
    description: Optional[str] = None           # API描述
    path: Optional[ApiPath] = None              # API路径（值对象）
    method: Optional[HttpMethod] = None         # HTTP方法（值对象）
    system_id: Optional[int] = None             # 所属系统ID
    module_id: Optional[int] = None             # 所属模块ID
    request_body: Optional[Dict[str, Any]] = None   # 请求体结构
    response_body: Optional[Dict[str, Any]] = None  # 响应体结构
    headers: Optional[Dict[str, str]] = None    # 请求头配置
    is_active: bool = True                      # 是否激活
    created_at: Optional[datetime] = None       # 创建时间
    updated_at: Optional[datetime] = None       # 更新时间
```

### 值对象

#### ApiPath（API路径）
```python
@dataclass(frozen=True)
class ApiPath:
    """API路径值对象"""
    value: str
    
    def __post_init__(self):
        """验证路径格式"""
        if not self.value or not self.value.startswith('/'):
            raise ValueError("API路径必须以'/'开头")
```

#### HttpMethod（HTTP方法）
```python
class HttpMethodEnum(Enum):
    """HTTP方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
```
| request_url | VARCHAR(500) | 请求URL |
| request_method | VARCHAR(10) | 请求方法 |
| request_headers | JSON | 请求头 |
| request_params | JSON | 请求参数 |
| request_body | TEXT | 请求体 |
| response_status | INTEGER | 响应状态码 |
| response_headers | JSON | 响应头 |
| response_body | TEXT | 响应体 |
| response_size | INTEGER | 响应大小 |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 结束时间 |
| duration_ms | INTEGER | 耗时（毫秒） |
| is_success | BOOLEAN | 是否成功 |
| error_message | TEXT | 错误信息 |
| created_at | DATETIME | 创建时间 |

## API接口使用

### 基础URL
```
http://localhost:8000/api/v1/apis
```

### 1. 创建API

**POST** `/api/v1/apis/`

```bash
curl -X POST "http://localhost:8000/api/v1/apis/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "获取用户信息",
    "path": "/users/{user_id}",
    "method": "GET",
    "system_id": 1,
    "module_id": 1,
    "description": "根据用户ID获取用户详细信息",
    "request_body": {},
    "response_body": {
      "id": "integer",
      "name": "string",
      "email": "string"
    },
    "headers": {
      "Authorization": "Bearer {token}"
    }
  }'
```

**响应示例：**
```json
{
  "success": true,
  "message": "API创建成功",
  "data": {
    "id": "api-uuid-123",
    "name": "获取用户信息",
    "path": "/users/{user_id}",
    "method": "GET",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

### 2. 获取API详情

**GET** `/api/v1/apis/{api_id}`

```bash
curl -X GET "http://localhost:8000/api/v1/apis/api-uuid-123"
```

### 3. 获取API列表

**GET** `/api/v1/apis/`

支持的查询参数：
- `system_id`: 系统ID过滤
- `module_id`: 模块ID过滤
- `active_only`: 仅显示激活的API（默认true）
- `skip`: 跳过数量（分页）
- `limit`: 限制数量（默认50）
- `sort_by`: 排序字段（id/name/created_at/updated_at）
- `sort_order`: 排序顺序（asc/desc）

```bash
curl -X GET "http://localhost:8000/api/v1/apis/?system_id=1&limit=10&sort_by=name"
```

### 4. 更新API

**PUT** `/api/v1/apis/{api_id}`

```bash
curl -X PUT "http://localhost:8000/api/v1/apis/api-uuid-123" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "更新后的API描述",
    "is_active": true
  }'
```

### 5. 删除API

**DELETE** `/api/v1/apis/{api_id}`

```bash
curl -X DELETE "http://localhost:8000/api/v1/apis/api-uuid-123"
```

### 6. 搜索API

**GET** `/api/v1/apis/search`

```bash
curl -X GET "http://localhost:8000/api/v1/apis/search?query=用户&limit=10"
```

### 7. 批量操作

#### 批量创建
**POST** `/api/v1/apis/batch`

```bash
curl -X POST "http://localhost:8000/api/v1/apis/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "apis": [
      {
        "name": "API1",
        "path": "/api1",
        "method": "GET",
        "system_id": 1,
        "module_id": 1
      },
      {
        "name": "API2", 
        "path": "/api2",
        "method": "POST",
        "system_id": 1,
        "module_id": 1
      }
    ]
  }'
```

### 8. 执行API

**POST** `/api/v1/apis/{api_id}/execute`

```bash
curl -X POST "http://localhost:8000/api/v1/apis/api-uuid-123/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "request_data": {
      "user_id": 123
    },
    "headers": {
      "Authorization": "Bearer your-token"
    },
    "timeout": 30
  }'
```

### 9. 验证API数据

**POST** `/api/v1/apis/validate`

```bash
curl -X POST "http://localhost:8000/api/v1/apis/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试API",
    "path": "/test",
    "method": "GET",
    "system_id": 1,
    "module_id": 1
  }'
```

### 3. 参数验证规则

### 4. 查询API

#### 获取所有API

```bash
curl -X GET "http://localhost:8000/api/v1/apis" \
  -H "Content-Type: application/json"
```

#### 分页查询

```bash
curl -X GET "http://localhost:8000/api/v1/apis?page=1&size=10" \
  -H "Content-Type: application/json"
```

#### 按条件查询

```bash
# 按名称查询
curl -X GET "http://localhost:8000/api/v1/apis?name=用户" \
  -H "Content-Type: application/json"

# 按HTTP方法查询
curl -X GET "http://localhost:8000/api/v1/apis?method=GET" \
  -H "Content-Type: application/json"

# 按标签查询
curl -X GET "http://localhost:8000/api/v1/apis?tags=user,profile" \
  -H "Content-Type: application/json"
```

### 5. 删除API

```bash
curl -X DELETE "http://localhost:8000/api/v1/apis/1" \
  -H "Content-Type: application/json"
```

响应示例：
```json
{
  "success": true,
  "message": "API删除成功"
}
```

## 最佳实践

### 1. API设计规范

- 使用清晰、描述性的API名称
- 遵循RESTful设计原则
- 合理设置HTTP方法（GET、POST、PUT、DELETE）
- 使用标准的HTTP状态码

### 2. 路径设计

- 使用小写字母和连字符分隔
- 避免在路径中使用特殊字符
- 保持路径结构的一致性
- 使用版本号管理API变更

### 3. 标签管理

- 使用有意义的标签对API进行分类
- 保持标签命名的一致性
- 避免过度细分标签
- 定期清理无用的标签

### 4. 错误处理

- 检查API响应的success字段
- 处理网络连接异常
- 记录错误日志便于调试
- 提供用户友好的错误信息

## 故障排除

### 常见问题

1. **API创建失败**
   - 检查请求体格式是否正确
   - 验证必填字段是否提供
   - 确认API路径格式是否有效

2. **查询结果为空**
   - 检查查询条件是否正确
   - 验证数据库中是否有匹配的数据
   - 确认分页参数是否合理

3. **更新失败**
   - 检查API ID是否存在
   - 验证更新数据的格式
   - 确认权限是否足够

4. **删除失败**
   - 检查API ID是否存在
   - 验证是否有关联数据阻止删除
   - 确认权限是否足够

### 调试技巧

1. **查看日志**
   ```bash
   # 查看应用日志
   tail -f logs/app.log
   
   # 查看错误日志
   tail -f logs/error.log
   ```

2. **使用调试模式**
   ```bash
   # 启动调试模式
   python start_api_v2.py --debug
   ```

3. **数据库检查**
   ```bash
   # 连接数据库查看数据
   sqlite3 data/auto_test.db
   .tables
   SELECT * FROM apis LIMIT 10;
   ```

## 扩展开发

### 自定义验证规则

如需扩展API路径验证规则，可以修改 `ApiPath` 值对象：

```python
@dataclass
class ApiPath:
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("API路径不能为空")
        
        if not self.value.startswith('/'):
            raise ValueError("API路径必须以'/'开头")
        
        # 添加自定义验证规则
        if len(self.value) > 255:
            raise ValueError("API路径长度不能超过255个字符")
```

### 添加新的HTTP方法

如需支持新的HTTP方法，可以扩展 `HttpMethodEnum`：

```python
class HttpMethodEnum(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"  # 新增方法
    HEAD = "HEAD"    # 新增方法
```

```python
class CustomAPICaller(APICaller):
    def build_auth_headers(self, api_info):
        headers = super().build_auth_headers(api_info)
        
        if api_info.auth_type == 'custom_auth':
            # 添加自定义认证逻辑
            headers['Custom-Auth'] = 'custom_value'
        
        return headers
```

## 版本更新

### v1.0.0
- 初始版本发布
- 基本的API录入和调用功能
- 支持SQLite数据库存储
- 提供同步和异步调用方式

---

更多详细信息请参考源代码注释和示例代码。