# API网关路由方案（测试API管理，纯新域）

## 目标
- 在统一API治理之上引入 `test-apis` 纯新域，仅按新方案实现。
- 不保留旧路径兼容，前端与脚本全部迁移到新域。

## 路由与路径
- 基础路径：`/api/test-apis/v1`
  - `GET    /test-apis`                查询列表
  - `POST   /test-apis`                创建
  - `GET    /test-apis/{id}`           查询详情
  - `PUT    /test-apis/{id}`           更新
  - `DELETE /test-apis/{id}`           删除
  - `POST   /test-apis/{id}/execute`   单次执行
  - `POST   /test-apis/batch-execute`  批量执行
  - `GET    /test-apis/{id}/runs`      执行记录列表
  - `GET    /test-apis/{id}/reports`   报告列表/下载

## 统一规范
- 鉴权与限流：网关统一处理。
- 参数归一化：入口允许 camelCase；网关统一转为 snake_case 进入后端。
- 响应结构：`{ success: boolean, data?: any, message?: string }`。

## 中间件与拦截
- Auth拦截：登录态与权限校验（读/写分级）。
- 限流：批量执行需阈值控制（并发、频率）。
- 观察：请求/响应日志、异常捕获与告警（含断言失败统计）。

## 参数归一化示意
- 输入示例（前端传）：
```json
{
  "retryCount": 1,
  "retryDelay": 1000,
  "continueOnFailure": true,
  "variables": {"env": "dev"}
}
```
- 后端转：
```json
{
  "retry_count": 1,
  "retry_delay": 1000,
  "continue_on_failure": true,
  "variables": {"env": "dev"}
}
```

## 错误码与消息
- 4xx：参数错误、鉴权失败、资源不存在。
- 5xx：执行器异常、外部接口超时、断言引擎异常。
- 消息示例：
  - `400`：`{"success":false,"message":"request_config.url required"}`
  - `404`：`{"success":false,"message":"test_api not found"}`
  - `500`：`{"success":false,"message":"execution failed","detail":"timeout"}`

## 与统一聚合（unified-api）的集成
- 前端聚合层导出 `testApiManagementApi`（命名示例），由后端路由对应 `test-apis` 域。
- 保持与 `system/module/api` 子域一致的封装风格，复用 `apiHandler`。

## 发布与变更
- 这是一次破坏性重构：旧测试路径不再保留或桥接。
- 前端与脚本需全部切换到 `test-apis` 新域方可使用。