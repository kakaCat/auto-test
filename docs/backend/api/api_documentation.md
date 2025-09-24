# API 文档和使用示例

## 概述

本文档提供了自动化测试系统后端API的完整文档和使用示例。API基于FastAPI构建，遵循RESTful设计原则。

## 基础信息

- **基础URL**: `http://localhost:8000`
- **API前缀**: `/api`
- **内容类型**: `application/json`
- **响应格式**: 统一JSON格式

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "code": 400
}
```

## 系统管理 API

### 1. 获取系统列表

**请求**
```http
GET /api/systems/
```

**响应示例**
```json
{
  "success": true,
  "message": "获取系统列表成功，共 3 个系统",
  "data": [
    {
      "id": 1,
      "name": "用户管理系统",
      "description": "处理用户注册、登录、权限管理等功能",
      "status": "active",
      "created_at": "2025-09-23 12:56:47",
      "updated_at": "2025-09-23 12:56:47",
      "system_key": "SYS_1",
      "is_active": true,
      "system_type": "general",
      "priority": 4,
      "version": "unknown",
      "created_at_formatted": "2025-09-23 12:56:47",
      "created_date": "2025-09-23",
      "updated_at_formatted": "2025-09-23 12:56:47",
      "updated_date": "2025-09-23",
      "system_age_days": 0,
      "system_age_display": "今天",
      "status_display": "活跃",
      "status_color": "success",
      "status_icon": "check-circle",
      "description_length": 18,
      "has_description": true,
      "name_length": 6,
      "search_keywords": [
        "处理用户注册、登录、权限管理等功能",
        "active",
        "用户管理系统"
      ],
      "health_score": 85,
      "module_count": 3,
      "has_modules": true,
      "system_scale": "small",
      "can_edit": true,
      "can_delete": false,
      "importance_level": "medium",
      "status_recommendation": "状态正常"
    }
  ]
}
```

**cURL示例**
```bash
curl -X GET "http://localhost:8000/api/systems/" \
  -H "accept: application/json"
```

### 2. 获取系统详情

**请求**
```http
GET /api/systems/{system_id}
```

**路径参数**
- `system_id` (integer): 系统ID

**响应示例**
```json
{
  "success": true,
  "message": "获取系统详情成功",
  "data": {
    "id": 1,
    "name": "用户管理系统",
    "description": "处理用户注册、登录、权限管理等功能",
    "status": "active",
    "created_at": "2025-09-23 12:56:47",
    "updated_at": "2025-09-23 12:56:47",
    "status_display": "活跃",
    "created_at_formatted": "2025-09-23 12:56:47",
    "updated_at_formatted": "2025-09-23 12:56:47"
  }
}
```

**cURL示例**
```bash
curl -X GET "http://localhost:8000/api/systems/1" \
  -H "accept: application/json"
```

### 3. 创建系统

**请求**
```http
POST /api/systems/
```

**请求体**
```json
{
  "name": "测试系统",
  "description": "这是一个测试系统",
  "status": "active"
}
```

**字段说明**
- `name` (string, 必填): 系统名称，1-100字符
- `description` (string, 可选): 系统描述
- `status` (string, 可选): 系统状态，默认为"active"

**响应示例**
```json
{
  "success": true,
  "message": "创建系统成功",
  "data": {
    "id": 40,
    "name": "测试系统",
    "description": "这是一个测试系统",
    "status": "active",
    "created_at": "2025-09-23 13:23:43",
    "updated_at": "2025-09-23 13:23:43",
    "status_display": "活跃",
    "created_at_formatted": "2025-09-23 13:23:43",
    "updated_at_formatted": "2025-09-23 13:23:43"
  }
}
```

**cURL示例**
```bash
curl -X POST "http://localhost:8000/api/systems/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试系统",
    "description": "这是一个测试系统",
    "status": "active"
  }'
```

### 4. 更新系统

**请求**
```http
PUT /api/systems/{system_id}
```

**路径参数**
- `system_id` (integer): 系统ID

**请求体**
```json
{
  "name": "更新后的系统名称",
  "description": "更新后的描述",
  "status": "inactive"
}
```

**字段说明**
- `name` (string, 可选): 系统名称
- `description` (string, 可选): 系统描述
- `status` (string, 可选): 系统状态

**cURL示例**
```bash
curl -X PUT "http://localhost:8000/api/systems/40" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "更新后的系统名称",
    "description": "更新后的描述"
  }'
```

### 5. 删除系统

**请求**
```http
DELETE /api/systems/{system_id}
```

**路径参数**
- `system_id` (integer): 系统ID

**cURL示例**
```bash
curl -X DELETE "http://localhost:8000/api/systems/40" \
  -H "accept: application/json"
```

## 模块管理 API

### 1. 获取模块列表

**请求**
```http
GET /api/modules/
```

**查询参数**
- `system_id` (integer, 可选): 按系统ID筛选

**响应示例**
```json
{
  "success": true,
  "message": "获取模块列表成功，共 8 个模块",
  "data": [
    {
      "id": 1,
      "system_id": 1,
      "name": "用户注册",
      "description": "处理用户注册功能",
      "status": "active",
      "tags": "user,register",
      "created_at": "2025-09-23 12:56:47",
      "updated_at": "2025-09-23 12:56:47",
      "system_name": "用户管理系统",
      "module_key": "1_1",
      "is_active": true,
      "module_type": "general",
      "priority": 4,
      "created_at_formatted": "2025-09-23 12:56:47",
      "created_date": "2025-09-23",
      "updated_at_formatted": "2025-09-23 12:56:47",
      "updated_date": "2025-09-23",
      "tags_list": ["user", "register"],
      "tags_count": 2,
      "has_tags": true,
      "tag_categories": {
        "other": ["user", "register"]
      },
      "status_display": "活跃",
      "status_color": "success",
      "status_icon": "check-circle",
      "description_length": 9,
      "has_description": true,
      "name_length": 4,
      "search_keywords": [
        "处理用户注册功能",
        "user",
        "register",
        "用户注册"
      ],
      "can_edit": true,
      "can_delete": false,
      "risk_level": "low"
    }
  ]
}
```

**cURL示例**
```bash
# 获取所有模块
curl -X GET "http://localhost:8000/api/modules/" \
  -H "accept: application/json"

# 获取特定系统的模块
curl -X GET "http://localhost:8000/api/modules/?system_id=1" \
  -H "accept: application/json"
```

### 2. 获取模块详情

**请求**
```http
GET /api/modules/{module_id}
```

**路径参数**
- `module_id` (integer): 模块ID

**响应示例**
```json
{
  "success": true,
  "message": "获取模块详情成功",
  "data": {
    "id": 113,
    "system_id": 40,
    "name": "测试模块",
    "description": "这是一个测试模块",
    "status": "active",
    "tags": "test,demo",
    "created_at": "2025-09-23 13:24:23",
    "updated_at": "2025-09-23 13:24:23",
    "system_name": "测试系统",
    "status_display": "活跃",
    "system_description": "这是一个测试系统",
    "tags_list": ["test", "demo"],
    "created_at_formatted": "2025-09-23 13:24:23",
    "updated_at_formatted": "2025-09-23 13:24:23"
  }
}
```

**cURL示例**
```bash
curl -X GET "http://localhost:8000/api/modules/113" \
  -H "accept: application/json"
```

### 3. 创建模块

**请求**
```http
POST /api/modules/
```

**请求体**
```json
{
  "system_id": 40,
  "name": "测试模块",
  "description": "这是一个测试模块",
  "status": "active",
  "tags": "test,demo"
}
```

**字段说明**
- `system_id` (integer, 必填): 所属系统ID
- `name` (string, 必填): 模块名称，1-100字符
- `description` (string, 可选): 模块描述
- `status` (string, 可选): 模块状态，默认为"active"
- `tags` (string, 可选): 标签，用逗号分隔

**响应示例**
```json
{
  "success": true,
  "message": "创建模块成功",
  "data": {
    "id": 113,
    "system_id": 40,
    "name": "测试模块",
    "description": "这是一个测试模块",
    "status": "active",
    "tags": "test,demo",
    "created_at": "2025-09-23 13:24:23",
    "updated_at": "2025-09-23 13:24:23",
    "system_name": "测试系统",
    "status_display": "活跃",
    "system_description": "这是一个测试系统",
    "tags_list": ["test", "demo"],
    "created_at_formatted": "2025-09-23 13:24:23",
    "updated_at_formatted": "2025-09-23 13:24:23"
  }
}
```

**cURL示例**
```bash
curl -X POST "http://localhost:8000/api/modules/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "system_id": 40,
    "name": "测试模块",
    "description": "这是一个测试模块",
    "status": "active",
    "tags": "test,demo"
  }'
```

### 4. 更新模块

**请求**
```http
PUT /api/modules/{module_id}
```

**路径参数**
- `module_id` (integer): 模块ID

**请求体**
```json
{
  "name": "更新后的模块名称",
  "description": "更新后的描述",
  "status": "testing",
  "tags": "test,demo,updated"
}
```

**字段说明**
- `name` (string, 可选): 模块名称
- `description` (string, 可选): 模块描述
- `status` (string, 可选): 模块状态
- `tags` (string, 可选): 标签

**cURL示例**
```bash
curl -X PUT "http://localhost:8000/api/modules/113" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "更新后的模块名称",
    "description": "更新后的描述",
    "status": "testing"
  }'
```

### 5. 删除模块

**请求**
```http
DELETE /api/modules/{module_id}
```

**路径参数**
- `module_id` (integer): 模块ID

**cURL示例**
```bash
curl -X DELETE "http://localhost:8000/api/modules/113" \
  -H "accept: application/json"
```

## 统计信息 API

### 1. 获取模块标签

**请求**
```http
GET /api/modules/tags
```

**响应示例**
```json
{
  "success": true,
  "message": "获取标签列表成功",
  "data": [
    "demo",
    "inventory",
    "order",
    "query",
    "test",
    "update",
    "user"
  ]
}
```

**cURL示例**
```bash
curl -X GET "http://localhost:8000/api/modules/tags" \
  -H "accept: application/json"
```

### 2. 获取模块统计信息

**请求**
```http
GET /api/modules/stats
```

**响应示例**
```json
{
  "success": true,
  "message": "获取统计信息成功",
  "data": {
    "total": 9,
    "by_status": {
      "active": 9
    },
    "by_system": [
      {
        "system_name": "用户管理系统",
        "count": 3
      },
      {
        "system_name": "订单管理系统",
        "count": 3
      },
      {
        "system_name": "库存管理系统",
        "count": 2
      },
      {
        "system_name": "测试系统",
        "count": 1
      }
    ]
  }
}
```

**cURL示例**
```bash
curl -X GET "http://localhost:8000/api/modules/stats" \
  -H "accept: application/json"
```

## 健康检查 API

### 1. 应用状态检查

**请求**
```http
GET /
```

**响应示例**
```json
{
  "message": "Auto Test API is running",
  "version": "1.0.0",
  "status": "healthy"
}
```

**cURL示例**
```bash
curl -X GET "http://localhost:8000/" \
  -H "accept: application/json"
```

### 2. 健康检查

**请求**
```http
GET /health
```

**响应示例**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-23T13:30:00Z"
}
```

**cURL示例**
```bash
curl -X GET "http://localhost:8000/health" \
  -H "accept: application/json"
```

## 错误代码说明

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 200 | 请求成功 | 正常获取数据 |
| 400 | 请求参数错误 | 缺少必填字段、数据格式错误 |
| 404 | 资源不存在 | 系统ID或模块ID不存在 |
| 500 | 服务器内部错误 | 数据库连接失败、业务逻辑异常 |

## 使用示例

### Python 示例

```python
import requests
import json

# 基础配置
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def get_systems():
    """获取系统列表"""
    response = requests.get(f"{BASE_URL}/api/systems/")
    return response.json()

def create_system(name, description):
    """创建系统"""
    data = {
        "name": name,
        "description": description,
        "status": "active"
    }
    response = requests.post(
        f"{BASE_URL}/api/systems/",
        headers=HEADERS,
        data=json.dumps(data)
    )
    return response.json()

def create_module(system_id, name, description, tags=None):
    """创建模块"""
    data = {
        "system_id": system_id,
        "name": name,
        "description": description,
        "status": "active"
    }
    if tags:
        data["tags"] = tags
    
    response = requests.post(
        f"{BASE_URL}/api/modules/",
        headers=HEADERS,
        data=json.dumps(data)
    )
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 获取系统列表
    systems = get_systems()
    print("系统列表:", systems)
    
    # 创建新系统
    new_system = create_system("API测试系统", "用于API测试的系统")
    print("创建系统:", new_system)
    
    # 创建模块
    if new_system["success"]:
        system_id = new_system["data"]["id"]
        new_module = create_module(
            system_id, 
            "API测试模块", 
            "用于测试API功能的模块",
            "api,test"
        )
        print("创建模块:", new_module)
```

### JavaScript 示例

```javascript
const BASE_URL = "http://localhost:8000";

// 获取系统列表
async function getSystems() {
    try {
        const response = await fetch(`${BASE_URL}/api/systems/`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("获取系统列表失败:", error);
        throw error;
    }
}

// 创建系统
async function createSystem(name, description) {
    try {
        const response = await fetch(`${BASE_URL}/api/systems/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                description: description,
                status: 'active'
            })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("创建系统失败:", error);
        throw error;
    }
}

// 创建模块
async function createModule(systemId, name, description, tags = null) {
    try {
        const requestBody = {
            system_id: systemId,
            name: name,
            description: description,
            status: 'active'
        };
        
        if (tags) {
            requestBody.tags = tags;
        }
        
        const response = await fetch(`${BASE_URL}/api/modules/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("创建模块失败:", error);
        throw error;
    }
}

// 使用示例
async function example() {
    try {
        // 获取系统列表
        const systems = await getSystems();
        console.log("系统列表:", systems);
        
        // 创建新系统
        const newSystem = await createSystem("JS测试系统", "用于JavaScript测试的系统");
        console.log("创建系统:", newSystem);
        
        // 创建模块
        if (newSystem.success) {
            const systemId = newSystem.data.id;
            const newModule = await createModule(
                systemId,
                "JS测试模块",
                "用于测试JavaScript API功能的模块",
                "javascript,test"
            );
            console.log("创建模块:", newModule);
        }
    } catch (error) {
        console.error("示例执行失败:", error);
    }
}

// 运行示例
example();
```

## 最佳实践

### 1. 错误处理
- 始终检查响应中的 `success` 字段
- 根据 `code` 字段处理不同类型的错误
- 记录错误信息用于调试

### 2. 数据验证
- 在发送请求前验证必填字段
- 确保数据类型正确
- 处理字符长度限制

### 3. 性能优化
- 使用适当的查询参数进行数据筛选
- 避免频繁的API调用
- 实现客户端缓存机制

### 4. 安全考虑
- 验证输入数据
- 使用HTTPS（生产环境）
- 实现适当的认证机制

这个API文档提供了完整的接口说明和使用示例，帮助开发者快速集成和使用后端服务。