# 测试API管理后端开发功能点列表

说明：本列表依据《01_TEST_API_MANAGEMENT_BACKEND_IMPLEMENTATION_PLAN》梳理形成，作为落地开发的任务拆解参考。功能点为可交付的开发项，便于排期与验收。

## 一、数据与模型
- 设计 `test_apis`、`test_api_runs`（及可选 `test_api_variables`）三张表的 ORM 模型。
- 编写数据库迁移脚本（创建表、索引、默认值）。
- 实现模型间关联与约束（`test_apis.api_id` 外键校验）。

## 二、测试API管理接口（CRUD）
- GET `/test-apis`：分页查询、筛选（keyword、api_id、enabled_only、tags）。
- POST `/test-apis`：创建测试API配置（入参校验、camelCase→snake_case 归一化）。
- GET `/test-apis/{id}`：详情查询。
- PUT `/test-apis/{id}`：更新测试API配置（字段校验、部分更新）。
- DELETE `/test-apis/{id}`：删除测试API配置（软删或硬删实现）。

## 三、测试执行服务
- 单次执行：`POST /test-apis/{id}/execute`，变量替换、HTTP 请求、断言评估、结果入库。
- 批量执行：`POST /test-apis/batch-execute`，并发控制、失败继续策略、总体统计。
- 执行指标采集：耗时、状态码、断言通过率、错误信息。

## 四、断言引擎
- 实现基础断言：`status_code`、`contains`、`jsonpath`、`exact`、`headers` 包含。
- 断言执行流程：收集断言结果、统计通过/总数，返回结构化结果。
- 可扩展接口：预留新增断言类型的扩展点与注册机制。

## 五、结果与报告
- 运行记录查询：`GET /test-apis/{id}/runs`、`GET /test-apis/{id}/latest-run`。
- 报告聚合：`GET /test-apis/{id}/reports`（成功率、平均响应时间、失败原因TopN、断言通过率）。
- 报告维度：按用例、按 API、按标签；支持时间范围过滤。

## 六、导入导出
- 测试API配置导入：`POST /test-apis/import`（JSON 校验、去重策略、错误报告）。
- 测试API配置导出：`POST /test-apis/export`（批量导出，字段选择）。

## 七、接口层与中间件
- 统一响应结构：`{ success, data, message }`。
- 参数归一化中间件：camelCase → snake_case。
- 身份校验与权限控制：登录态校验、接口授权（读/写）。
- 频率限制：批量执行限流与并发上限控制。

## 八、服务层与仓储层
- Repository/DAO 实现：测试API配置、运行记录的增删改查。
- Service 组合：执行服务、断言服务、报告服务模块化。
- 事务与一致性：批量执行中运行记录的写入与失败回滚策略。

## 九、日志与监控
- 执行日志记录：关键事件（开始、结束、失败原因）与上下文。
- 指标埋点：成功率、平均耗时、失败率。
- 异常捕获与告警：接口层捕获、服务层重试与降级策略。

## 十、测试与文档
- 单元测试：断言引擎、执行服务、参数归一化。
- 集成测试：单次/批量执行路径、报告聚合。
- 示例与文档：接口说明与示例请求/响应、导入导出示例。

## 十一、前后端对齐与兼容
- 与前端 TestApiManagement 弹框字段对齐（执行配置、期望响应结构）。
- `enabled` 布尔存储，`tags` 字符串存储（逗号分隔）。
- 与既有 `/api/interfaces/{id}/test` 兼容策略（如需透传或复用底层执行器）。

## 十二、发布与运维
- 配置项：执行超时上限、并发阈值、重试策略默认值。
- 运维脚本：迁移、回滚、数据导入导出脚本。
- 安全与审计：访问日志、操作日志、数据留痕（软删标记）。

## 十三、分层约定（API/Service）
- API 模块拆分：页面一个 API 模块、弹框一个 API 模块，职责边界清晰。
- 复用规则：公共业务逻辑集中在 Service 层，由多个 API 模块共享复用。
- 参考命名：`test_apis_page.py`、`test_apis_dialog.py`（路由模块）；`TestApiService`（服务）。
- 目录建议：`backend/src/auto_test/api/`（test_apis_page.py、test_apis_dialog.py）、`services/`（test_api_service.py）、`repositories/`。
- 交互映射：前端页面/弹框分别调用对应 API 路由；Service 提供统一方法供两者使用。