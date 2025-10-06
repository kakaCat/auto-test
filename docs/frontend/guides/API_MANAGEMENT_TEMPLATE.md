# API 管理模板（示例/模板，不是标准）

本文件提供前端“API 管理”模块的示例性模板与落地参考，用于快速搭建与对齐实现方式。它不是标准，不具备强制约束力；约束性内容请参考：`../standards/API_MANAGEMENT_STANDARDS.md`。

## 目标与适用范围
- 目标：提供可复制的页面结构、状态管理、接口组织与错误处理模板。
- 适用：新建或改造“API 管理”相关页面/模块的前端实现。
- 不适用：跨域通用政策（版本兼容、权限策略等）应遵循标准文件。

## 模板结构（建议）
- 视图层（`views/api-management/`）
  - 页面入口与分区（概览/列表/详情/编辑）
  - 交互要素（筛选、分页、批量操作、导入导出）
- 状态层（`stores/apiManagementStore.ts`）
  - 查询条件、选中项、编辑态与提交状态
  - 并发控制与乐观更新的最小封装
- 接口层（`src/api/modules/apiManagement.ts`）
  - 统一的请求封装、错误码处理与类型定义
  - 分组接口（列表、详情、新增、更新、删除、导入、导出）
- 类型与规则（`src/types/`、`src/api/rules/`、`src/api/converters/`）
  - DTO/VO 明确分层；转换器/规则独立可测试
- 权限包装（`src/api/wrappers/permissionWrapper.ts`）
  - 资源操作的权限前置检查与提示

## 页面元素建议
- 查询区：关键字、分类、状态、时间范围
- 列表区：基础字段列（名称/路径/方法/负责人/更新时间）与操作列
- 详情/编辑：基础字段、扩展属性、版本备注、变更记录
- 导入导出：CSV/JSON 的双向支持；校验与预览
- 批量操作：启用/停用、分组调整、标签管理

## 错误处理与提示
- 统一采用“错误码 → 用户文案”的映射，并在失败后提供“重试/反馈/导出日志”选项。
- 前端日志记录关键事件（导入失败/权限拒绝/批量操作异常）并附带上下文。

## 与标准的关系（强约束来源）
- 约束性内容参见 `../standards/API_MANAGEMENT_STANDARDS.md`：路由、状态、错误、字段、权限、文档与自测清单。
- 本模板仅示例“如何做”，当与标准冲突时，以标准为准。

## 自检清单（落地前）
- [ ] 页面结构与交互符合模板建议
- [ ] 状态管理、接口组织与类型分层清晰
- [ ] 错误处理与权限包装完整且统一
- [ ] 导入/导出流程具备校验、预览与失败备选
- [ ] 与 `API_MANAGEMENT_STANDARDS.md` 的约束逐项核对通过

## 统一入口 API 导入与调用（MUST）

为确保实现与标准一致，模板层提供可复制示例，所有域 API 通过命名导入并统一调用：

- 导入方式：

```ts
import { SystemApi, ModuleApi, ApiInterfaceApi } from '@/api/unified-api';
```

- 系统列表（backend 类别）：

```ts
async function loadSystems() {
  const resp = await SystemApi.getEnabledListByCategory('backend');
  const { list, total } = apiHandler.normalizeList(resp);
  return { systems: list, total };
}
```

- 模块列表（按系统加载，兼容 systemId/system_id）：

```ts
async function loadModulesBySystem(sid: string | number) {
  const resp = await ModuleApi.getEnabledModules({ systemId: sid }); // 或 { system_id: sid }
  const { list } = apiHandler.normalizeList(resp);
  serviceStore.setSystemModules(String(sid), list);
  return list;
}
```

- API 列表（筛选与分页）：

```ts
async function fetchApiList(filters: unknown) {
  const resp = await ApiInterfaceApi.getList(filters);
  const { list, total, page, size } = apiHandler.normalizeList(resp);
  return { items: list, total, page, size };
}
```

- 禁止模式（MUST NOT）：
  - 动态属性调用：`unifiedApi[someKey]`、`(obj as any)[key]()`。
  - 默认导入后派生属性：`import unifiedApi from '@/api/unified-api'`。

- 错误与类型（MUST）：
  - 函数返回 `Promise<ApiResponse<T>> | Promise<NormalizedList<T>>`；避免 `any`，优先 `unknown` 并显式收敛。
  - 失败写入 `ui.error`；仅在不可恢复场景 `throw new Error('具体消息')`。

## 下一步
- 如需扩展，建议在本模板末尾增补“项目特定扩展”小节，并在提交时链接到标准文件。