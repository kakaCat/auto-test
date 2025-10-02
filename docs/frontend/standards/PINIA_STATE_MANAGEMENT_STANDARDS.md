# 状态管理规范（Pinia State Management Standards）

> Status: Stable
> Version: 1.0
> Last Updated: 2025-10-01
> Owner: @frontend-team
> Tags: frontend, standards, pinia, state

## 适用范围
- 适用于基于 Pinia 的全局/模块状态管理，源代码位于 `frontend/src/stores/`。

## 目录与命名
- 每个业务域一个 Store：`useXxxStore`（如 `useApiStore`）。
- 文件命名：`xxx.store.ts`；导出 `state/getters/actions`。

## 设计原则
- 单一职责：Store 只负责状态与业务动作，不处理视图逻辑。
- 可序列化：State 保持可序列化并最小化；将不可序列化对象放到组件或服务层。
- 错误统一：Action 返回 `Result<T>`，不抛未包装异常；透传 `traceId`。

## 使用规范
- Getter 只做派生计算；避免复杂副作用。
- Action 内部调用 `services/*` 或 `api/*`，统一错误与返回结构。
- 持久化：必要时使用 `pinia-plugin-persistedstate`，明确持久化键与版本。

## 事件与日志
- 在关键 Action 中记录摘要日志（开发下可开启 verbose）；避免泄露敏感信息。

## 示例
```ts
import { defineStore } from 'pinia'

export const useApiStore = defineStore('api', {
  state: () => ({ apis: [], loading: false }),
  getters: {
    enabledApis: (s) => s.apis.filter(a => a.enabled)
  },
  actions: {
    async fetchApis() {
      this.loading = true
      const res = await unifiedApi.apiManagementApi.getApis({ enabledOnly: true })
      this.loading = false
      if (res.success) this.apis = res.data || []
      return res
    }
  }
})
```

---
本规范确保状态管理与统一错误/返回结构一致，降低复杂度与维护成本。