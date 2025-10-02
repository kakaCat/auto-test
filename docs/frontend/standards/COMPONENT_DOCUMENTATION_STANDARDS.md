# 组件文档规范（Component Documentation Standards）

> Status: Stable
> Version: 1.0
> Last Updated: 2025-10-01
> Owner: @frontend-team
> Tags: frontend, standards, components, docs

## 适用范围
- 适用于前端组件的文档撰写与维护，组件实现位于 `frontend/src/components/`，示例与说明可参考 `frontend/docs/components/`。

## 文档结构（推荐）
- 概述：组件定位、上下游关系、使用场景。
- Props/Emits/Expose：表格列出字段、类型、默认值与说明。
- 使用示例：最小示例 + 常见组合；包含错误态与加载态示例。
- 交互与状态：加载、禁用、空态、错误展示、快捷键等。
- 可扩展点：插槽、样式覆盖、主题化入口。
- 可观测性：埋点与日志（如 `traceId` 透传）。
- 兼容与迁移：旧属性映射与废弃项说明。
- 关联文档：链接到相关用户指南与技术方案。

## 写作要点
- 任务导向与示例优先；避免仅列 API 无示例。
- 统一术语与命名；与页面/方案文档保持一致。
- 错误语义标准化：使用 `message/code/fieldErrors` 描述与示例。

## 放置与互链
- 组件文档集中在 `frontend/docs/components/`；本规范作为写作规则存于 `docs/frontend/standards/`。
- 当用户指南需要补充组件细节时，新增或更新组件文档，并在用户指南建立链接（不在用户指南内展开组件细节）。

## 元信息模板（建议粘贴）
```
> Status: Draft | Stable | Deprecated
> Version: 1.0
> Last Updated: YYYY-MM-DD
> Owner: @frontend-team
> Tags: frontend, components, docs
```

---
本规范旨在保证组件文档清晰、可用、可维护，并与整体文档规范保持一致。