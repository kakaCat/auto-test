# API 字段命名与类型对齐规范（2025-09）

> 目标：在前端开发中统一字段命名风格与类型处理，降低前后端协作中的不一致与运行风险。
>
> 范围：`src/api/*`、`views/api-management/*`、以及相关表单/列表交互。

## 字段命名
- 服务端主体字段采用蛇形命名：`system_id`、`module_id`、`path`。
- 前端表单可使用 `form.url`，提交时统一映射到服务端的 `path`。

## 类型对齐
- `system_id/module_id` 在提交时转换为数字：`Number(form.system_id)`、`Number(form.module_id)`。
- 列表筛选统一使用字符串比较，避免数字/字符串混用：
  - `String(api.system_id) === String(selectedSystemId)`
  - `String(api.module_id) === String(selectedModuleId)`

## 系统树构建
- 模块与系统匹配时兼容 `system_id` 与 `systemId`：
  - `String(module.system_id ?? module.systemId) === String(system.id)`

## 批量测试调用
- 保持蛇形命名的参数：`batchTestApis({ api_ids, headers, timeout })`。

## 推荐做法
- 在页面内使用本地 `ApiItem/SystemItem/ModuleItem` 类型，避免跨模块字段命名差异导致 TS 报错。

## 统一代理层（能力说明）
- `apiManagementApi` 支持将前端入参的 `camelCase` 自动归一化为服务端 `snake_case`，并处理 `url → path`。
  - 查询参数：`systemId/moduleId/enabledOnly` → `system_id/module_id/enabled_only`，并将数字字符串转为数字类型。
  - 创建/更新负载：`systemId/moduleId/requestFormat/responseFormat/authRequired/rateLimit/exampleRequest/exampleResponse` 自动映射；如传入 `url`，将自动映射为 `path`。
- 详细策略与覆盖范围请参考：`../api/refactor-plan.md` 的“参数归一化与返回一致性”。

## 示例（统一代理入参归一化）
```ts
// 查询（前端使用 camelCase）
apiManagementApi.getApis({ systemId: '12', moduleId: '5', enabledOnly: true })

// 创建（url 自动映射为 path，ID 自动数字化）
apiManagementApi.createApi({
  systemId: '12',
  moduleId: '5',
  name: '登录接口',
  method: 'POST',
  url: '/api/v1/login',
  requestFormat: 'json',
  responseFormat: 'json',
  authRequired: 1,
  rateLimit: 100
})
```

## 示例（保存映射）
```ts
const payload = {
  name: form.name,
  description: form.description,
  method: form.method,
  path: form.url || '',
  system_id: form.system_id ? Number(form.system_id) : undefined,
  module_id: form.module_id ? Number(form.module_id) : undefined,
  enabled: form.enabled,
  tags: form.tags,
  metadata: form.metadata
}
```

---
维护者：前端团队  
最后更新：2025-10-01