# 错误日志：formData.tags.join is not a function

- 日期：2025-10-04
- 环境：前端开发环境（Vite），本地预览端口：5173/5174
- 影响范围：
  - API 管理页面保存接口（编辑/创建）
  - 服务管理模块保存接口（编辑/创建）
  - 模块查询接口的 tags 查询参数

## 现象
- 在保存或查询时抛出 TypeError：`tags.join is not a function`。
- 部分接口返回的 `tags` 为逗号分隔字符串，前端使用 `.join(',')` 假定其为数组时发生报错。

## 根因分析
- `tags` 字段在不同流程中存在类型不一致（可能为 `string` 或 `string[]`），直接调用 `Array.prototype.join` 导致运行时错误。
- 历史代码中对 `tags` 的处理缺乏统一的转换规范，造成同一字段在表单、查询参数、保存 payload 中类型不稳定。

## 修复方案（已实施）
1. 在 API 管理页面统一转换 `tags` 为逗号分隔字符串：
   - 新增辅助函数 `ensureTagsString(tags)`，对 `string | string[] | unknown` 进行类型收敛与安全转换，避免 `.join` 报错。
   - 保存（编辑/创建）时统一使用该函数组装 payload。
2. 在服务管理模块保存逻辑中统一处理 `tags`：
   - 使用 `unknown` 中间变量配合类型缩小（`Array.isArray` / `typeof === 'string'`），将 `string[]` 转为逗号分隔字符串；将 `string` 做 `split`/`trim`/去空 后再 `join(',')`，其他类型置为空字符串，规避 `any`/`never` 问题。
3. 在模块查询 API 中规范 `tags` 参数：
   - `_normalizeQueryParams` 中对 `p.tags` 进行统一转换：若是数组则 `join(',')`，若是字符串则直接使用（`trim()` 后）；其他情况忽略。

## 受影响与修复涉及文件
- 前端 API 管理页面保存逻辑：`frontend/src/views/api-management/index.vue`
- 前端服务管理保存逻辑：`frontend/src/views/service-management/composables/useServiceManagement.ts`
- 前端模块查询 API：`frontend/src/api/module-api.ts`

## 验证与结果
- 本地开发环境预览运行正常，保存/编辑/查询流程未再出现 `.join` 相关错误。
- 表单输入 `tags` 支持：数组选择（多选）与逗号分隔字符串输入，两者均可正确保存并回显。

## 后续工作与风险控制
- Phase 1：在 `api-management.ts`、`requirement-management.ts`、`page-management.ts` 中用统一 `request` 替换历史 `apiHandler`，确保路径与参数兼容（进行中）。
- Phase 2：重构 `base-api.ts`，移除 `apiHandler` 依赖与成功提示副作用，保留类型与返回结构一致性。
- Phase 3：在依赖 `BaseApi` 的 `system-api.ts`、`module-api.ts` 校验并调整调用，消除对消息副作用的依赖。
- 端到端验证：本地预览、网络请求、成功/失败提示与加载行为回归测试。
- 清理：删除 `utils/apiHandler.ts` 与残留 import；必要时保留临时兼容导出以便一键回退。

## 备注
- 此错误已在上述文件中统一修复；后续如发现 `tags` 类型不稳定的入口，建议复用同一转换策略，避免分散处理导致回归。