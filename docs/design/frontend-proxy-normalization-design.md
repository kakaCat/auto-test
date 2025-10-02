# 前端代理层参数归一化与返回一致性（设计说明）

## 背景与目标
- 背景：前端各业务代理（API 代理）在不同模块存在入参键名风格差异（camelCase 与 snake_case 并存），以及返回结构不完全统一，导致调用处写重复映射逻辑、易出错。
- 目标：在代理层统一做参数归一化与返回结构一致化，实现“调用处传入自然的 camelCase 参数，代理层自动映射为后端约定的 snake_case”，并保持 `Promise<ApiResponse<...>>` 的一致响应包装，降低耦合与维护成本。

## 规范与映射规则
- 键名风格：统一将常见 camelCase 入参映射为 snake_case。
  - 示例：`pageSize/createdTime/createdTimeRange/updatedTime/updatedTimeRange/enabledOnly` → `page_size/created_time/created_time_range/updated_time/updated_time_range/enabled_only`
- 范围参数：数组统一转逗号分隔字符串。
  - 示例：`createdTimeRange: ['2025-01-01','2025-01-31']` → `created_time_range: '2025-01-01,2025-01-31'`
- 其他规则：
  - API 管理创建/更新：`url` 自动映射为 `path`；`systemId/moduleId` 在需要时做数字化处理（如 `'12'` → `12`）；`tags[]` 映射为逗号分隔字符串。
- 返回结构：各代理方法统一返回 `Promise<ApiResponse<...>>`，便于调用处统一处理成功/错误与数据结构。

## 覆盖范围（当前已实施）
- System/Module/API 管理（apiManagementApi）：
  - 列表与搜索：`systemId/moduleId/enabledOnly/keyword/method/pageSize` → `system_id/module_id/enabled_only/keyword/method/page_size`
  - 创建/更新：`url → path`；`systemId/moduleId` 数字化；`tags[] → 'a,b'`
- Page（pageApi）：
  - `getPages`、`searchPagesSimple` 支持上述分页、时间、启用字段的归一化与范围数组到字符串转换。
- Workflow（workflowApi）：
  - `getWorkflowList`、`getExecutionHistory` 支持分页、时间、启用字段归一化与范围转换。
- Requirement（requirementApi）：
  - 列表、树、覆盖分析、报表与导出均支持分页、时间、启用字段归一化与范围转换。

## 实现要点（代码侧）
- 为各代理新增 `_normalizeQueryParams(params: Record<string, any>)` 辅助方法，集中处理键名映射与范围转换。
- 在各列表/搜索/历史类方法中统一调用归一化方法，避免调用处重复映射。
- 在 API 管理创建/更新方法中处理 `url → path`、ID 字段数字化及 `tags[]` 转换。
- 保持类型签名与响应一致性：返回 `Promise<ApiResponse<...>>`。

## 兼容性与迁移
- 兼容性：调用处可继续使用 camelCase；代理层自动映射为后端契约，无需修改后端。
- 迁移建议：逐步将旧的调用处手动映射逻辑移除，改为直接传入自然的 camelCase 参数；对范围类参数统一传数组，代理层负责转换。

## 验证建议
- Page：
  - `pageApi.getPages({ pageSize: 20, createdTimeRange: ['2025-01-01','2025-01-31'], enabledOnly: true })`
  - 期望发送：`{ page_size: 20, created_time_range: '2025-01-01,2025-01-31', enabled_only: true }`
- Workflow：
  - `workflowApi.getExecutionHistory('wf_123', { pageSize: 10, updatedTimeRange: ['2025-09-01','2025-09-30'] })`
  - 期望发送：`{ page_size: 10, updated_time_range: '2025-09-01,2025-09-30' }`
- Requirement：
  - `requirementApi.exportRequirements({ pageSize: 50, createdTime: '2025-09-01' })`
  - 期望发送：`{ page_size: 50, created_time: '2025-09-01' }`
- API 管理：
  - `apiManagementApi.createApi({ systemId: '12', moduleId: '3', url: '/v1/users', tags: ['auth','user'] })`
  - 期望发送：`{ system_id: 12, module_id: 3, path: '/v1/users', tags: 'auth,user' }`

## 文档与变更记录
- 用户手册：已在 `frontend/user-manuals/04/05/07/09` 中分别补充归一化说明与示例。
- 变更记录：`docs/CHANGELOG-2025-09-proxy-normalization.md`。

## 后续扩展
- 可按同样策略扩展到 `scenarioApi` 与其他代理模块，保持全局一致性。