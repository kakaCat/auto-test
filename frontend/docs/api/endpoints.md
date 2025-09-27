# API接口文档（占位）

> 说明：该文档用于沉淀对外暴露的接口规范与示例，随着功能演进逐步补齐。当前为占位版本，确保导航链接有效、结构一致。

## 编写原则
- 命名使用小写短横线：如 `get-task-list`、`create-report`
- 路径以业务域分组：如 `/tasks/...`、`/reports/...`
- 入参/出参统一由 `Converter` 进行格式化，禁止直接透传底层结构
- 错误使用业务异常语义化返回，例如：`code`, `message`

## 路由总览（样例）

### /tasks
- GET `/tasks` 列表查询
  - 入参：`page`、`pageSize`、`filters`
  - 出参：`TaskListResponse`
- POST `/tasks` 新建任务
  - 入参：`CreateTaskRequest`
  - 出参：`CreateTaskResponse`

### /reports
- GET `/reports/:id` 查询报告
  - 入参：`id`
  - 出参：`ReportDetailResponse`

> 以上为占位示例。请基于实际接口增补，保持风格一致。

## 约定与规范
- 控制器：薄控制器，不含业务逻辑
- Service：数据收集与编排，统一异常处理
- Converter：入参/出参标准化，禁止透传实体
- 命名：请求 `*Request`、响应 `*Response`、数据 `*VO`/`*Data`

## 示例
```ts
// 仅为示例，实际以 src/api 下实现为准
export interface CreateTaskRequest {
  name: string;
  priority?: 'low' | 'medium' | 'high';
}

export interface CreateTaskResponse {
  id: string;
  createdAt: string;
}
```

---
维护者：前端团队
最后更新：占位创建