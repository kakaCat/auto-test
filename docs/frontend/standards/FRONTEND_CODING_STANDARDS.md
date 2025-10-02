# 前端编码规范（Frontend Coding Standards）

> Status: Stable
> Version: 1.0
> Last Updated: 2025-10-01
> Owner: @frontend-team
> Tags: frontend, standards, coding

## 适用范围
- 适用于 `frontend/` 项目的源码与文档示例；与通用规范 `docs/standards/README.md` 配合使用。
- 与 API 层统一返回结构与错误模型保持一致（参见 `docs/frontend/guides/API_LAYER_REFACTOR_PLAN.md`）。

## 基本原则
- 一致性优先：类型、错误处理、命名和目录结构统一。
- 薄封装：领域 API 薄、Service 编排、Converter 静态化。
- 明确职责：组件、服务、工具各司其职，避免跨层耦合。

## TypeScript 与类型
- 必须声明返回类型；禁止隐式 `any`。
- 统一错误与返回：`Result<T> { success; data?; error? }`、`ApiError { code; message; details? }`。
- Converter 使用静态方法进行数据转换，避免状态污染。

## 命名与结构
- 模块与文件：使用清晰、动词或名词短语，避免缩写。
- 目录职责：`api/`（接口调用）、`services/`（业务编排）、`components/`（UI）、`utils/`（工具）。
- 常量与枚举：使用 `UPPER_SNAKE_CASE`（常量）与枚举类型代替魔法字符串。

## 错误处理
- 禁止在领域 API 与 Service 层抛出未包装异常；统一返回 `Result<T>`。
- 仅在拦截器与 `apiHandler` 层进行错误展示与重试逻辑。
- 允许在调用点传入 `skipErrorHandler` 但需本地统一处理。

## 异步与状态
- 优先使用 `async/await`；避免层层回调与 Promise 链嵌套。
- UI 状态与加载提示在视图/组件层统一管理，业务层不重复处理。

## 代码风格
- 遵循 ESLint/Prettier 项目配置；提交前修复警告与格式化。
- 导入顺序：第三方 → 别名 → 相对路径；去除未使用导入。
- 注释：仅在必要处说明“为什么”，避免赘述“做了什么”。

## 测试与可观测性
- 关键路径需具备单元测试或集成测试；断言统一返回结构。
- 日志与跟踪：透传 `traceId`；避免打印敏感信息。

## 文档与示例
- 示例代码与路径用反引号包裹；与用户指南互链。
- 变更规范需在 `docs/design/changelogs/CHANGELOG.md` 登记重要更新。

---
本规范与通用文档规范协同，目标是降低维护成本、提升一致性与可读性。