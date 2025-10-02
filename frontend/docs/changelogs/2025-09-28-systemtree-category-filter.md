# 2025-09-28 — SystemTree 类别过滤原则补充

## 背景
为消除歧义并与前端实现保持一致，明确 API 管理与页面管理中 SystemTree 的类别过滤范围：
- API 管理仅展示后端服务（`backend`）类别系统与模块。
- 页面管理仅展示前端应用（`frontend`）类别系统与模块。

## 变更内容
- 更新 `docs/frontend/user-manuals/04-api-management.md`：在“系统和模块树形结构”新增“仅展示 backend 类别”说明。
- 更新 `docs/frontend/user-manuals/05-page-management.md`：在“系统和模块树形结构 (SystemTree组件)”新增“仅展示 frontend 类别”说明。
 - 更新 `docs/frontend/guides/ARCHITECTURE_GUIDE.md`：在两处 SystemTree 节点下分别补充 backend/frontend 类别过滤说明。
- 更新 `docs/frontend/DOCUMENTATION_STANDARDS.md`：新增“小节：类别过滤原则（SystemTree）”。

## 影响范围
- 文档阅读者能快速理解左侧树加载范围；前端页面与文档描述保持一致。
- 不涉及 UI 视觉和交互改动；仅文档说明更新。

## 关联文件
- `docs/frontend/user-manuals/04-api-management.md`
- `docs/frontend/user-manuals/05-page-management.md`
- `docs/frontend/guides/ARCHITECTURE_GUIDE.md`
- `docs/frontend/DOCUMENTATION_STANDARDS.md`

## 验证建议
- 在前端代码中确认：
  - API 管理使用 `systemApi.getEnabledListByCategory('backend')` 加载系统树。
  - 页面管理使用 `systemApi.getEnabledListByCategory('frontend')` 加载系统树。
- 进入 `/api-management` 与 `/page-management`，检查左侧树仅加载对应类别的系统与模块。

## 后续规划
- 如引入新类别（如 `mobile`、`edge`），需在该原则中补充对应映射，并在相关页面文档同步说明。