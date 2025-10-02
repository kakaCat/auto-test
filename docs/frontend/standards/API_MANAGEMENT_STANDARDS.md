# API管理规范（API Management Standards）

> Status: Draft
> Version: 1.0
> Last Updated: 2025-10-01
> Owner: @frontend-team
> Scope: frontend
> Links: `./ROUTING_NAVIGATION_STANDARDS.md`, `./PINIA_STATE_MANAGEMENT_STANDARDS.md`, `./STYLE_THEME_STANDARDS.md`, `./DOCUMENTATION_STANDARDS.md`, `../guides/API_MANAGEMENT_TEMPLATE.md`

## 1. 目标与范围
- 约束前端“API管理”功能的路由、状态、视图、交互与错误模型，确保一致性与可维护性。
- 范围涵盖：列表、搜索与筛选、详情/编辑弹窗、创建/删除、导入/导出、批量操作、权限包装。

## 2. 路由与导航（MUST）
- 基本路径：`/api-management`，子路由采用显式命名：`list`, `create`, `edit/:id`。
- 路由命名：`ApiManagementList`, `ApiManagementCreate`, `ApiManagementEdit`。
- 返回与跳转：操作成功后返回列表并保留筛选参数；失败保留当前上下文与校验状态。

## 3. 状态管理（Pinia）（MUST）
- Store 命名：`useApiManagementStore`；按模块拆分 `entities`, `filters`, `ui`。
- 状态字段：
  - `entities.items: ApiItem[]`, `entities.total: number`。
  - `filters.query: string`, `filters.module: string | null`, `filters.method: 'GET'|'POST'|'PUT'|'DELETE'|'PATCH'|null`。
  - `ui.loading: boolean`, `ui.error: { code?: string; message?: string; fieldErrors?: Record<string,string> } | null`。
- Action 约定：`fetchList(params)`, `create(payload)`, `update(id, payload)`, `remove(id)`, `import(file)`, `export(params)`；所有返回 Promise，错误统一写入 `ui.error`。

## 4. 错误模型与交互（MUST）
- 统一错误结构：`{ code, message, fieldErrors? }`；与后端兼容模型保持一致。
- 表单校验错误：映射到 `fieldErrors` 并高亮对应字段；全局错误弹出消息与可重试入口。
- 交互兜底：网络失败显示重试；权限失败显示说明并禁用相应操作。

## 5. 视图与组件（SHOULD）
- 列表页：分页、模块/方法筛选、关键字搜索；行内操作提供“编辑/删除/更多”。
- 编辑弹窗：固定尺寸建议 `850x700`；分组字段与表单校验统一；支持保存与取消。
- 组件文档：关键组件（如 `ApiFormDialog.vue`、`ApiListTable.vue`）在 `frontend/docs/components/` 建立文档并与本规范互链。

## 6. 字段与校验（MUST）
- 必填：`serviceName`, `moduleName`, `path`, `method`。
- 约束：
  - `path` 以 `/` 开头，禁止重复斜杠；参数段使用 `:param` 或 `{param}` 一致化。
  - `method` 使用标准枚举；大小写统一为大写。
  - `tags` 为字符串数组；展示时逗号分隔；存储保持数组。
  - `docLink` 使用相对路径或完整 URL；推荐相对路径到 `docs/backend/api/` 对应文档。

## 7. 导入与导出（SHOULD）
- 导入：支持 `JSON`；在导入前进行 schema 校验并预览差异。
- 导出：支持 `JSON`；包含版本与时间戳；保留筛选条件上下文。

## 8. 权限包装（MUST）
- 所有“写操作”（创建、编辑、删除、导入）通过权限包装层实现；在 UI 上按权限动态显示或禁用。
- 在 `api/wrappers/` 内统一实现权限校验与包装；规范化错误为统一结构。

## 9. 文档与互链（MUST）
- 本规范为唯一约束源；执行细节与示例参见 `../guides/API_MANAGEMENT_TEMPLATE.md`。
- 更新功能时，同时更新组件文档与用户手册 `docs/frontend/user-manuals/04-api-management.md`。
- 变更记录进入 `frontend/docs/changelogs/`。

## 10. 自测清单（SHOULD）
- 列表加载与筛选正确；分页与总数同步。
- 创建/编辑表单校验全面；错误提示清晰并可重试。
- 删除/批量操作权限与兜底完备；错误记录统一。
- 导入/导出流程稳定；异常与回滚策略明确。

## 11. 统一列表响应与分页（MUST）

为降低页面适配成本、统一契约命名，前端仅消费以下列表响应结构：

- 列表字段：`data.list`（不再读取 `items`/`apis` 等旧字段）
- 统计字段：`data.total`
- 分页字段：`data.page`、`data.size`
- 顶层包装：`success`、`message`、`data`、`code`

兼容期适配（统一在 `apiHandler` 层实现，页面不做判断）：

```ts
type ListEnvelope<T> = {
  success: boolean;
  message?: string;
  code?: number;
  data: {
    list?: T[];
    apis?: T[]; // 兼容旧字段（将映射为 list）
    total?: number;
    page?: number;
    size?: number;
  };
};

export function normalizeList<T>(resp: ListEnvelope<T>) {
  const list = resp.data.list ?? resp.data.apis ?? [];
  return {
    success: resp.success,
    message: resp.message,
    code: resp.code ?? 0,
    list,
    total: resp.data.total ?? list.length,
    page: resp.data.page ?? 1,
    size: resp.data.size ?? 20,
  };
}
```

实施要求：
- 列表页与 Store 统一使用 `entities.items` 承载数据，但来源一律通过 `normalizeList(resp).list` 映射；分页与总数同步自 `normalizeList(resp)`。
- 不得在页面或组件内出现对 `data.apis` 的直接读取；迁移完成后将删除兼容逻辑。
- 新增接口与文档示例一律使用 `list/total/page/size`；变更记录进入 `frontend/docs/changelogs/` 并关联后端规范。