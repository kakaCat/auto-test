# 前端 API 层重构方案（`frontend/src/api/`）
> 版本更新：本方案已调整为“彻底去兼容、单一入口”模式，不保留旧调用路径与兼容开关，统一错误与返回结构，确保页面稳定且不因 API 异常导致崩溃。

## 核心决策（无兼容、强一致）
- 不保留旧内容：移除旧的 `request.*` 直接调用与兼容分支，统一通过 `BaseApi + apiHandler` 调用。
- 单一返回结构：所有 API 均返回 `Result<T> { data: T; success: boolean; error?: ApiError }`，禁止返回裸数据或抛出未包装异常。
- 统一错误模型：错误统一为 `ApiError { code: string; message: string; details?: unknown }`；禁止在领域 API 中自定义错误结构。
- 禁止冗余捕获：领域 API 不写 `try/catch`；错误在拦截器与 `apiHandler` 层完成统一包装与记录。
- 严格使用 `skipErrorHandler`：仅限少数场景（导出、心跳），且需在代码注释中注明理由；默认不允许跳过统一错误处理。
- Lint 约束：在前端代码中禁止 `import request from '@/api/request'`（除 `request.ts` 自身与底层工具），避免绕过统一入口。

## 目标与效果
- 页面稳定：即使后端错误也返回结构化 `Result`，UI 不因异常而报错或崩溃。
- 一致行为：错误提示、日志码与数据结构全局一致，降低调试成本。
- 降低复杂度：移除多层兼容与重复封装，简化 API 层次与调用路径。

## 重构范围与约束
- 涉及文件：`frontend/src/api/request.ts`、`frontend/src/api/apiHandler.ts`、`frontend/src/api/base-api.ts`、以及所有直接调用 `request.*` 的模块（如 `requirement-management.ts`、`page-management.ts`、`api-management.ts`）。
- 约束：
  - 统一通过 `BaseApi + apiHandler` 发起请求。
  - 严禁在视图/组件中直接处理基础设施异常；只消费 `Result<T>`。
  - Converter 使用静态方法进行数据转换，避免在调用方混入转换逻辑。

## 实施步骤（一次到位，无兼容路径）
1) 定义统一类型
   - 新增 `frontend/src/types/api.ts`：声明 `ApiError`、`Result<T>` 与辅助工具（如 `unwrapResult()`）。
2) 改造底层入口
   - 重写 `frontend/src/api/request.ts`：拦截器统一错误包装，不抛出未处理异常；方法统一返回 `Result<T>`。
   - 调整 `apiHandler.ts`：仅做请求编排与批量/并发控制，返回 `Result<T>`，不再二次包装或分支兼容。
   - 规范 `base-api.ts`：移除局部 `try/catch`；CRUD 方法返回 `Result<T>`，将数据转换交由 Converter。
3) 替换调用方
   - 将 `requirement-management.ts`、`page-management.ts`、`api-management.ts` 等直接 `request.*` 调用，统一替换为 `BaseApi/apiHandler` 路径。
   - 视图/服务层改为响应式消费 `Result<T>`，根据 `success` 渲染或提示，避免未捕获异常导致页面报错。
4) 清理与守护
   - 移除旧的兼容代码与注释。
   - 增加 ESLint 规则或项目约定（代码扫描）禁止新引入 `request.*` 直接调用。

## 验收标准
- 不抛原始异常：所有调用返回 `Result<T>`；UI 不因未处理异常而崩溃。
- 关键路径稳定：登录、列表、详情、编辑/保存、导出等页面在重构后行为一致。
- 错误一致：统一错误码/文案；日志链路清晰且可追踪。
- 代码简化：领域 API 无冗余 `try/catch` 与自定义错误包装；直接 `request.*` 调用为零。

## 风险与应对
- 文件上传/下载：保留专用管线（`request.upload/download`）但仍返回 `Result`；后续视情况抽象到 `apiHandler` 的文件通道。
- 并发/批量：在 `apiHandler` 中统一控制，不在调用方分散处理；返回聚合 `Result`（成功与失败列表）。
- 类型复杂度：通过 `Converter` 统一转换，避免在页面或服务层出现隐式数据形态切换。

## 测试与映射
- 测试：更新 `tests/test_frontend_api_calls.js`，断言所有 API 均返回 `Result<T>`；失败时不抛出未包装异常，UI 正常渲染错误态。
- 文档：本方案取代兼容策略；`DOCUMENT_MAPPING_GUIDE.md` 标注“API 层实现变更但 UI/交互不受影响”的更新流程与检查清单。


## 背景与问题
- 层级过深且使用不一致：存在 `request` → `apiHandler` → `BaseApi` → 领域 API 多层封装，但各文件对这些层的使用不统一。
- 错误处理分散：
  - `request.ts` 拦截器处理 HTTP/业务错误并弹消息；
  - `apiHandler.ts` 再次包装错误、重试与 Loading；
  - 领域 API（如 `module-api.ts`）局部 `try/catch` 拼接文案；
  - `services/*` 与页面组件处再行 `console.error`。
- 可观的维护成本与调试难度：配置项（如 `skipErrorHandler`）使用不一致，行为不可预测。

## 重构目标
- 单一入口与一致用法：统一所有 API 调用走 `BaseApi + apiHandler`，禁止在 API 与 Service 层直接调用 `request`。
- 错误处理统一：拦截器与 `apiHandler` 负责错误提示与重试；领域 API 不再做局部 `try/catch` 文案拼接，让错误冒泡并统一展示。
- 分层职责清晰（前端对应后端分层理念）：
  - View → Service（业务编排、数据收集） → Converter（静态数据转换） → API（薄封装） → ApiHandler（执行/重试/缓存/提示） → Request（拦截器、协议细节）。
- 兼容性与可迁移：保留 `unified-api.ts` 聚合导出与命名别名，逐步替换内部实现，保持调用方不变。

## 设计原则
- 统一错误模型：建议在 `src/types` 增加
  - `interface ApiError { code?: number; message: string; traceId?: string }`
  - `interface Result<T> { success: boolean; data?: T; error?: ApiError }`
  `request` 响应拦截统一归一化为该形态，`apiHandler.execute` 仅负责展示与重试，不修改错误结构。
- `skipErrorHandler` 使用规范：默认不使用；仅当调用点需要自定义错误展示（如表单逐字段反馈）时显式传入，并在本地消费错误。

## 实施状态（2025-09-28）
- 已完成：`request.ts` 响应归一化为 `ApiResponse`，`apiHandler.ts` 统一 GET/POST/PUT/PATCH/DELETE 返回结构并按 `success` 控制重试。
- 已完成：`base-api.ts` 领域通用方法统一返回 `ApiResponse`，`page-management.ts`、`api-management.ts`、`requirement-management.ts`、`system-api.ts`、`services/ModuleService.ts` 对齐使用 `apiHandler`。
- 已完成：`unified-api.ts` 作为薄聚合器导出各域 API；删除无用文件 `category-api.ts`、`compatibility-test.ts`，`simplified/` 目录为空待后续移除。
- 待迁移：部分旧模块（如 `scenario.ts`、`workflow.ts`）仍直接使用 `request.*`，后续将按统一模式迁移到 `apiHandler`。

## 使用示例（统一返回 ApiResponse）
```ts
import unifiedApi from '@/api/unified-api'

const res = await unifiedApi.apiManagementApi.getApis({ page: 1 })
if (res.success) {
  // 使用 res.data
} else {
  // 统一错误结构，无需抛异常
  console.warn(res.error?.message)
}
```
- Converter 静态化：所有转换类使用静态方法，避免状态污染，提升复用。

## 重构范围与清单（文件级）
- 需要迁移到 `BaseApi/apiHandler` 的直接 `request` 调用：
  - `src/api/api-management.ts`
  - `src/api/page-management.ts`
  - `src/api/requirement-management.ts`
  - `src/api/services/ModuleService.ts`
  - `src/api/services/SystemService.ts`
- 需要清理局部 `try/catch` 的领域 API：
  - `src/api/module-api.ts`
  - `src/api/system-api.ts`
- 聚合导出与兼容层保留：
  - `src/api/unified-api.ts`（保持别名导出与现有入口，不更改调用方式）

## 分阶段实施计划
### Phase 0：类型与共用策略对齐
- 在 `src/types` 补充或对齐 `ApiError` 与 `Result<T>`；明确全局响应约定。
- 在 `apiHandler.ts` 明确仅负责 Loading/重试/成功提示与数据转换钩子，不自行拼接错误文案。

### Phase 1：直接调用 `request` 的文件统一到 `apiHandler`
- 核心策略：保留原 URL 与参数，替换为 `apiHandler.get/post/put/delete/patch`。
- 示例（以 `page-management.ts` 为例）：
```ts
// Before
getPagesStats(): Promise<ApiResponse> {
  return request.get('/api/pages/v1/stats/overview')
}

// After
import { apiHandler } from '@/utils/apiHandler'

getPagesStats(): Promise<any> {
  return apiHandler.get('/api/pages/v1/stats/overview', {}, {
    cache: true,
    cacheTime: 60_000,
    loadingText: '加载页面统计中...'
  })
}
```
- 对 `api-management.ts` 与 `requirement-management.ts` 进行同类替换，移除 `skipErrorHandler: true` 的“沉默失败”用法，改为在调用点（页面/组件）按需控制提示。

### Phase 2：Service 层依赖领域 API，而非 `request`
- `services/ModuleService.ts`、`SystemService.ts` 改为：
  - 仅调用 `moduleApi/systemApi` 暴露的方法获取数据；
  - 使用 `ModuleConverter/SystemConverter` 的静态方法进行转换；
  - 不直接 `request.get/put`，避免重复封装。

### Phase 3：领域 API 清理局部 `try/catch`
- 在 `module-api.ts`、`system-api.ts` 移除 `try/catch + throw new Error('中文提示')`，直接返回 `apiHandler.get/put/...` 的结果，让错误统一由拦截器与 `apiHandler` 提示。
- 如需语义化错误映射，集中在一个 `ApiErrorMapper`（静态工具）中处理，而非分散在各方法。

### Phase 4：日志与调试一致性
- 保留 `X-Request-ID` 并透传到错误对象（在拦截器中读取并附加到 `ApiError.traceId`）。
- 提供开发开关 `VITE_API_VERBOSE_LOG`，在开发模式下打印请求/响应摘要，定位问题更友好。

### Phase 5：测试与回归
- 执行现有前端 API 测试：`tests/test_frontend_api.js`、`tests/test_frontend_api_calls.js`。
- 人工验证典型视图：页面管理、系统管理、模块管理的常用操作是否仍然得到一致的加载与错误提示，且无重复消息。

## 文件级改动建议
- `src/api/page-management.ts`：
  - 将所有 `request.*` 替换为 `apiHandler.*`；
  - 对统计类接口增加 `cache + cacheTime`；
  - 移除局部错误拼接，错误留给统一层处理。
- `src/api/api-management.ts`：
  - 统一通过 `apiHandler` 调用；
  - 移除 `skipErrorHandler: true` 的默认使用；
  - 若某调用需要局部自定义提示，在页面或调用点传入选项并本地消费错误。
- `src/api/requirement-management.ts`：同上。
- `src/api/services/ModuleService.ts`、`src/api/services/SystemService.ts`：
  - 改为调用 `moduleApi/systemApi`，保留 Converter 静态转换；
  - 不直接触达 `request`。
- `src/api/module-api.ts`、`src/api/system-api.ts`：
  - 移除 `try/catch + throw new Error('...')`；
  - 采用 `apiHandler.get/post/...` 并通过 `options` 控制 Loading/缓存/成功提示。

## 错误处理统一策略
- HTTP/网络错误：由 `request.ts` 响应拦截器根据状态码生成统一消息，并记录日志。
- 业务错误（`success === false`）：拦截器弹统一消息；返回 `Result<T>` 结构给调用方。
- 重试与 Loading：由 `apiHandler.execute` 控制，领域 API 不重复处理。
- 特殊场景：表单逐字段、批量操作的细粒度反馈，调用点可传 `skipErrorHandler: true` 并自行处理，但需在 Service 或页面内集中、规范化处理。

## 兼容性与迁移策略
- 保留 `unified-api.ts` 的别名导出，避免历史代码报错。
- 逐步替换内部实现，调用签名保持不变或提供过渡别名（若签名调整）。
- 渐进式提交：每个文件独立 PR，回归通过后再继续下一个，降低风险。

## 验收标准
- 调用方不需要了解底层封装差异；错误提示一致，无重复消息；Loading 行为一致。
- 直接 `request` 的调用点清零（API/Service 层）；
- 领域 API 无局部 `try/catch` 文案；
- 测试通过：现有前端 API 测试与页面手动验证。

## 文档联动
- 更新 `docs/frontend/DOCUMENTATION_STANDARDS.md` 的“API 错误处理与层级规范”条目，引用本方案。
- 根据 `docs/DOCUMENT_MAPPING_GUIDE.md` 的映射规则，在涉及页面交互与文档示例时同步更新对应的用户指南。

## 参考示例（领域 API 方法改造）
```ts
// module-api.ts 片段示意
async getDependencies(moduleId: string): Promise<any> {
  // Before: try/catch + throw new Error('...')
  // After: 直接交由 apiHandler 与拦截器处理
  return this.apiHandler.get(`${this.baseUrl}/${moduleId}/dependencies`, {}, {
    loadingText: '加载模块依赖中...'
  })
}
```

---
该方案不引入新的复杂层级，只统一“怎么用”。核心是减少分散与重复，让 API 层薄、Service 层编排、Converter 静态化、错误处理归一，最终降低调试与维护成本。