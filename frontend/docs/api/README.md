# API 目录结构与统一入口

## 📋 概述

本目录说明前端 `src/api` 的最新结构、统一入口用法，以及重构清理后的约定，确保文档与代码一致。

## 📁 文档结构

- **[refactor-summary.md](./refactor-summary.md)** - 重构完成总结（已更新）
- **[refactor-plan.md](./refactor-plan.md)** - 重构计划与后续迁移建议
- **[endpoints.md](./endpoints.md)** - API接口说明
- **[types.md](./types.md)** - 类型定义入口与用法（已更新）

## 📂 最新目录结构（代码已生效）

- `src/api/unified-api.ts`
  - 统一入口（Aggregator）。默认导出 `unifiedApi`，并命名导出 `systemApi`、`moduleApi`、`categoryApi`、`apiManagementApi`；兼容别名 `unified*Api`。
- `src/api/system-api.ts`（默认导出 `systemApi`）
- `src/api/module-api.ts`（默认导出 `moduleApi`）
- `src/api/api-management.ts`（命名导出 `apiManagementApi`）
- `src/api/scenario.ts`（命名导出 `categoryApi`）
- `src/api/base-api.ts`（基础抽象与通用类型）
- `src/api/services/`（Service 层，过渡阶段存在）
- `src/api/converters/`（Converter 层，静态转换工具）

## 🗑️ 已清理（删除）

- `src/api/unified/` 目录：已删除，统一入口统一为 `unified-api.ts`。
- `src/api/types/` 目录：已删除，类型统一入口为 `src/types`。

## ✅ 使用示例

```ts
import unifiedApi, { systemApi, moduleApi } from '@/api/unified-api'

// 统一返回 ApiResponse<T>，不抛异常，按 success 分支处理
const listResult = await unifiedApi.system.getList()
if (listResult.success) {
  console.log(listResult.data)
}

const createResult = await unifiedApi.module.create({ /* ... */ })
if (!createResult.success) {
  console.warn(createResult.error?.message)
}

// 命名导出同样返回 ApiResponse<T>
const detail = await systemApi.getDetail('id-123')
const updated = await moduleApi.update('id-456', { /* ... */ })
```

## 🔗 相关链接

- [API源码目录](../../src/api/)
- [类型定义入口](../../src/types/)
- [开发指南](../guides/)

## 📝 最近更新

- 2025-09-28: 删除 `api/unified/` 与 `api/types/`；统一入口对齐。
- 2025-09-28: 更新文档以反映最新结构与约定。

---

**维护者**: 开发团队  
**最后更新**: 2025年9月28日