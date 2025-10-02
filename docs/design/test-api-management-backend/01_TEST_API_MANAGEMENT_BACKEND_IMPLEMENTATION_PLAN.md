# 测试API管理弹框后端实现方案

目标：为前端“测试API管理弹框”（TestApiManagement）提供完整的后端支撑，包括测试API的管理、执行与报告聚合，确保与现有统一接口治理保持一致性并可逐步迭代。

## 一、总体设计
- 功能域：测试API管理（CRUD）、测试执行（单次/批量）、结果存储与报告、导入导出。
- 设计原则：
  - 与现有 API 接口治理保持路径风格统一（restful，版本化）。
  - 所有持久化字段以 snake_case 存储；接口层支持 camelCase → snake_case 归一化。
  - 断言与变量采用 JSON 存储，支持扩展。
  - 执行引擎可并发、可重试、可忽略失败继续执行。

## 二、接口地址（REST API）
Base Path：`/api/test-apis/v1`

### 1. 测试API管理（CRUD）
- `GET /api/test-apis/v1/test-apis`
  - 查询参数：`keyword`、`api_id`、`enabled_only`、`tags`、`page`、`size`
  - 返回：分页的测试API配置列表

- `POST /api/test-apis/v1/test-apis`
  - 描述：创建测试API配置
  - 请求体：见数据结构定义

- `GET /api/test-apis/v1/test-apis/{id}`
  - 描述：获取测试API配置详情

- `PUT /api/test-apis/v1/test-apis/{id}`
  - 描述：更新测试API配置

- `DELETE /api/test-apis/v1/test-apis/{id}`
  - 描述：删除测试API配置（软删或硬删，建议软删）

### 2. 测试执行（单次与批量）
- `POST /api/test-apis/v1/test-apis/{id}/execute`
  - 描述：执行单个测试API配置
  - 请求体（可选覆盖项）：`variables`、`retry_count`、`retry_delay`、`continue_on_failure`、`parallel`、`environment`
  - 返回：单次执行结果（包含断言通过率、耗时、响应）

- `POST /api/test-apis/v1/test-apis/batch-execute`
  - 描述：批量执行多个测试API配置
  - 请求体：`test_api_ids: string[]`，以及同上可选覆盖项
  - 返回：批量执行结果聚合（统计成功/失败数、平均耗时等）

### 3. 结果与报告
- `GET /api/test-apis/v1/test-apis/{id}/runs`
  - 描述：分页查询测试执行记录（运行明细）

- `GET /api/test-apis/v1/test-apis/{id}/latest-run`
  - 描述：最近一次执行结果

- `GET /api/test-apis/v1/test-apis/{id}/reports`
  - 描述：获取聚合报告（成功率、平均响应时间、断言通过率等）

### 4. 导入导出
- `POST /api/test-apis/v1/test-apis/import`
  - 描述：导入测试API配置（JSON 格式）

- `POST /api/test-apis/v1/test-apis/export`
  - 描述：导出选定测试API配置（JSON 格式）

## 三、数据结构定义（请求/响应）

### 1. 测试API配置（TestApi）
```json
{
  "api_id": 123,
  "name": "用户登录-成功返回",
  "description": "校验登录接口在正确信息下响应200，并返回token",
  "enabled": true,
  "tags": "login,smoke",
  "request_config": {
    "method": "POST",
    "url": "https://example.com/api/login",
    "headers": {"Content-Type": "application/json"},
    "params": {},
    "body": {"username": "${user}", "password": "${pass}"},
    "body_type": "json",
    "timeout": 30000,
    "follow_redirects": true,
    "validate_ssl": true
  },
  "execution_config": {
    "retry_count": 0,
    "retry_delay": 0,
    "continue_on_failure": false,
    "parallel": false,
    "variables": {"user": "demo", "pass": "123456"}
  },
  "expected_response": {
    "status_code": 200,
    "assertions": [
      {"type": "jsonpath", "path": "$.token", "operator": "exists"},
      {"type": "contains", "target": "body", "value": "token"}
    ]
  },
  "metadata": {}
}
```

### 2. 执行结果（RunResult）
```json
{
  "run_id": "uuid",
  "test_api_id": 1,
  "api_id": 123,
  "status": "success",
  "started_at": "2025-10-02T12:00:00Z",
  "ended_at": "2025-10-02T12:00:01Z",
  "response_status_code": 200,
  "response_time_ms": 980,
  "response_headers": {"content-type": "application/json"},
  "response_body": {"token": "xxx"},
  "assertions_passed": 2,
  "assertions_total": 2,
  "error_message": null,
  "environment": {"base_url": "https://example.com"}
}
```

## 四、核心逻辑说明

### 1. CRUD 逻辑
- 创建/更新：校验 `name`、`request_config.method`、`request_config.url`；`tags` 存储为逗号分隔字符串；`api_id` 需存在于接口表。
- 删除：软删除（`deleted_at`）或硬删除；推荐软删除便于审计。

### 2. 执行流程
1) 读取测试API配置 → 合并覆盖配置（变量、重试、并发等）。
2) 变量替换（`${var}`）→ 组装 HTTP 请求（headers、params、body）。
3) 调用接口 → 记录耗时、响应信息。
4) 执行断言：支持 `status_code`、`contains`、`jsonpath`、`exact`、`headers` 包含等。
5) 生成结果：统计断言通过数、总数，确定 `success/failed`，持久化 `test_api_runs`。
6) 返回结果（同步）；批量执行可异步并在队列中运行。

### 3. 批量执行
- 输入：`test_api_ids`，可选覆盖项。
- 并发：根据 `parallel` 控制；失败是否继续由 `continue_on_failure` 决定。
- 输出：总体统计、每个用例的简要结果与 run_id 列表。

### 4. 报告聚合
- 指标：成功率、平均响应时间、失败原因 TopN、断言通过率。
- 维度：按测试API、按 API、按标签；时间范围过滤。

### 5. 错误处理
- 请求错误、断言失败、超时等统一归类并记录 `error_message`。
- 接口返回 `success=false` 时携带详细 `message/detail`。

## 五、表结构设计（SQL DDL 示例）

### 1. `test_apis`
```sql
CREATE TABLE test_apis (
  id BIGSERIAL PRIMARY KEY,
  api_id BIGINT NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  enabled BOOLEAN DEFAULT TRUE,
  tags VARCHAR(512),
  request_config JSONB NOT NULL,
  execution_config JSONB,
  expected_response JSONB,
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  deleted_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_test_apis_api_id ON test_apis(api_id);
CREATE INDEX idx_test_apis_tags ON test_apis USING GIN (to_tsvector('simple', tags));
```

### 2. `test_api_runs`
```sql
CREATE TABLE test_api_runs (
  id BIGSERIAL PRIMARY KEY,
  test_api_id BIGINT NOT NULL,
  api_id BIGINT NOT NULL,
  status VARCHAR(32) NOT NULL,
  started_at TIMESTAMP WITH TIME ZONE,
  ended_at TIMESTAMP WITH TIME ZONE,
  response_status_code INT,
  response_time_ms INT,
  response_headers JSONB,
  response_body JSONB,
  assertions_passed INT,
  assertions_total INT,
  error_message TEXT,
  environment JSONB,
  variables JSONB
);
CREATE INDEX idx_test_api_runs_api_id ON test_api_runs(test_api_id);
CREATE INDEX idx_test_api_runs_status ON test_api_runs(status);
```

### 3. （可选）`test_api_variables`
```sql
CREATE TABLE test_api_variables (
  id BIGSERIAL PRIMARY KEY,
  test_api_id BIGINT NOT NULL,
  key VARCHAR(128) NOT NULL,
  value TEXT,
  type VARCHAR(32) DEFAULT 'string',
  scope VARCHAR(32) DEFAULT 'case' -- case/global
);
CREATE INDEX idx_test_api_variables_api_id ON test_api_variables(test_api_id);
```

## 六、技术选型与实现要点
- Web 层：FastAPI/Flask（参考后端现有框架）；统一响应格式（`success/data/message`）。
- 访问层：DAO/Repository 封装，SQLAlchemy/ORM 管理模型与迁移。
- 执行引擎：requests/httpx + 重试机制；并发采用 asyncio 或队列。
- 断言引擎：内置基础断言；保留扩展点以支持正则、Schema 验证。
- 权限与安全：接口需登录态；批量执行设限与审计日志。
- 归一化：入参支持 camelCase，服务端转 snake_case 存储。

## 七、与前端对齐点
- 前端弹框中“执行配置字段”与“期望响应体”结构与此方案一致。
- `enabled` 在前端作为布尔勾选，后端存储为布尔；`tags` 以逗号字符串保存。
- 返回字段满足前端报告视图展示（测试API详情、单次执行结果、批量统计）。

## 八、架构约定（API/Service 分层）
- API 模块（controller）职责：入参校验、DTO→领域模型映射、调用 Service、统一响应；不承载业务复杂度。
- 服务职责：业务编排、规则复用、事务边界控制；可被多个 API 模块复用。
- 页面与弹框分离：
  - 页面对应一个后端 API 模块（示例文件：`test_apis_page.py`）。
  - 弹框对应一个后端 API 模块（示例文件：`test_apis_dialog.py`）。
  - 若页面与弹框使用相同业务逻辑（例如 CRUD 或执行触发），统一置于 `TestApiService`。
- 命名与目录建议：
  - `backend/src/auto_test/api/`：`test_apis_page.py`、`test_apis_dialog.py`（FastAPI/Flask 路由定义）。
  - `backend/src/auto_test/services/`：`test_api_service.py`、`assertion_service.py`、`report_service.py`。
  - `backend/src/auto_test/repositories/`：`test_api_repository.py`、`test_api_run_repository.py`。
- 面向对象原则：API 模块面向交互（页面/弹框）清晰分治，Service 面向领域能力复用与组合。