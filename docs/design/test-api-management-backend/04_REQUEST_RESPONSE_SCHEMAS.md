# 测试API管理请求/响应Schema（JSON Schema草案）

## 1. TestApi（测试API配置）
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TestApi",
  "type": "object",
  "required": ["api_id", "name", "request_config"],
  "properties": {
    "api_id": {"type": "integer"},
    "name": {"type": "string", "minLength": 1},
    "description": {"type": "string"},
    "enabled": {"type": "boolean"},
    "tags": {"type": "string"},
    "request_config": {"$ref": "#/definitions/RequestConfig"},
    "execution_config": {"$ref": "#/definitions/ExecutionConfig"},
    "expected_response": {"$ref": "#/definitions/ExpectedResponse"},
    "metadata": {"type": "object"}
  },
  "definitions": {
    "RequestConfig": {
      "type": "object",
      "required": ["method", "url"],
      "properties": {
        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
        "url": {"type": "string"},
        "headers": {"type": "object"},
        "params": {"type": "object"},
        "body": {},
        "body_type": {"type": "string", "enum": ["json", "form", "text"]},
        "timeout": {"type": "integer", "minimum": 0},
        "follow_redirects": {"type": "boolean"},
        "validate_ssl": {"type": "boolean"}
      }
    },
    "ExecutionConfig": {
      "type": "object",
      "properties": {
        "retry_count": {"type": "integer", "minimum": 0},
        "retry_delay": {"type": "integer", "minimum": 0},
        "continue_on_failure": {"type": "boolean"},
        "parallel": {"type": "boolean"},
        "variables": {"type": "object"}
      }
    },
    "ExpectedResponse": {
      "type": "object",
      "properties": {
        "status_code": {"type": "integer"},
        "assertions": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": {"type": "string", "enum": ["jsonpath", "contains", "exact", "headers"]},
              "path": {"type": "string"},
              "target": {"type": "string"},
              "operator": {"type": "string"},
              "value": {}
            },
            "required": ["type"]
          }
        }
      }
    }
  }
}
```

## 2. RunResult（执行结果）
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RunResult",
  "type": "object",
  "required": ["test_api_id", "api_id", "status"],
  "properties": {
    "run_id": {"type": "string"},
    "test_api_id": {"type": "integer"},
    "api_id": {"type": "integer"},
    "status": {"type": "string", "enum": ["success", "failed"]},
    "started_at": {"type": "string", "format": "date-time"},
    "ended_at": {"type": "string", "format": "date-time"},
    "response_status_code": {"type": "integer"},
    "response_time_ms": {"type": "integer"},
    "response_headers": {"type": "object"},
    "response_body": {},
    "assertions_passed": {"type": "integer"},
    "assertions_total": {"type": "integer"},
    "error_message": {"type": "string"},
    "environment": {"type": "object"}
  }
}
```

## 3. 批量执行请求
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "BatchExecuteRequest",
  "type": "object",
  "required": ["test_api_ids"],
  "properties": {
    "test_api_ids": {"type": "array", "items": {"type": "integer"}},
    "retry_count": {"type": "integer"},
    "retry_delay": {"type": "integer"},
    "continue_on_failure": {"type": "boolean"},
    "parallel": {"type": "boolean"},
    "variables": {"type": "object"},
    "environment": {"type": "object"}
  }
}
```

## 4. 约定
- `tags` 为逗号分隔字符串；客户端可传数组，网关需归一化为字符串。
- 时间统一为 ISO8601；时区存储为 UTC。
- 执行与断言类型可扩展；Schema 作为最低对齐标准。