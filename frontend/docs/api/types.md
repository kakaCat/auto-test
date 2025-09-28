# 类型定义入口与约定（已对齐）

> 说明：类型统一入口为 `src/types`，`src/api/types` 目录已删除。本文档对齐最新代码结构，提供常用导入示例与编写约定。

## 统一入口

- 主入口：`src/types/index.ts`
- API相关：`src/types/api.ts`
- 通用类型：`src/types/common.ts`

常用导入方式：

```ts
// API领域类型
import type { SystemData, ModuleData, ApiResponse } from '@/types/api'

// 通用类型
import type { PaginationParams, PaginatedResponse } from '@/types/common'
```

## 编写原则（与代码一致）
- 复杂对象优先使用 `interface`；避免 `any`，必要使用 `unknown`
- 使用判别联合处理复杂分支
- 异常统一：`throw new Error('具体消息')`
- 严格模式：`tsconfig.json` 中 `strict: true`

## 迁移说明（2025-09-28）
- 移除 `src/api/types/` 目录，避免重复入口与认知负担
- 所有类型统一通过 `src/types` 导出与消费
- 文档与代码已同步更新，按上述路径导入即可

---
维护者：前端团队  
最后更新：2025-09-28