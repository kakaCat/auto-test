# AI 协作习惯与执行准则

目的：记录并统一本仓库中 AI 助手的工作习惯、执行流程与落地规则，便于长期维护和团队协作。

## 存放位置与范围
- 位置：`docs/AI_ASSISTANT_GUIDE.md`
- 范围：适用于本仓库的前端与后端子项目，以及根目录 `docs/` 的文档维护。
- 关联文档：
  - 文档组织规范：`docs/DOCUMENTATION_STANDARDS.md`
  - 根文档导航：`docs/README.md`
  - 前端文档导航：`frontend/docs/README.md`
  - 后端文档导航：`backend/docs/README.md`
  - 前端编码规范：`frontend/docs/guides/coding-style.md`

## 工作习惯总览
1) 文档组织（就近原则）
- 项目特定文档放在对应项目目录：`frontend/docs/`、`backend/docs/`
- 跨项目/系统级文档放在 `docs/`
- 创建文档后，若涉及导航页，增量更新相关 README 的导航链接

2) 变更落地
- 代码或文档改动尽量小步、可回滚，避免一次性大改
- 优先修复引用与链接的正确性（相对路径、文件重命名后的链接同步）
- 如移动/重命名文档，清理重复文件，确保唯一来源

3) 任务跟踪
- 多步骤或跨目录改动，建立待办清单并逐项完成
- 任务完成后立即更新状态与说明，避免批量补记

4) 测试与验证
- 前端：`npm run build` 做类型与构建校验；开发中使用 `npm run dev`
- 后端：按 `backend/README.md` 指引启动并验证 API
- 有 UI 影响时，通过本地预览地址确认无误

5) 命名与文件
- 文件名使用小写短横线或小写下划线，内容使用清晰的标题与目录
- 约定特殊文档名称（如 `README.md`、`CHANGELOG.md`、标准类文档）

6) 沟通与记录
- 在相关文档内简要记录：改动目的、范围、影响与回退方式
- 对外呈现的文档保持简洁一致，避免与代码实现不一致

7) 前端类型与架构（关键约定）
- TypeScript：严格模式、避免 `any`、用 `unknown`、异步统一 `Promise<T>`
- 架构约束（参考后端同构思想）：Controller/Facade → Service → DataService/Repository，Converter/Rule/Wrapper/Adapter 分层职责清晰；控制器薄、无业务逻辑

## 执行清单（Checklist）
- 目录选择正确：项目内 vs 根 `docs/`
- 链接有效：相对路径检查通过
- 导航更新：相关 README 是否需要增加链接
- 构建通过：前端/后端必要的校验是否通过
- 重复清理：历史同名或旧位置文档是否移除

## 更新规则
- 谁变更谁更新：改动涉及的导航、索引或交叉引用同时更新
- 文档与代码同步：功能合并或目录重组后，同步修订文档
- 非破坏性优先：能追加就不重写，能链接就不复制

## 快速定位
- 前端 API 文档：`frontend/docs/api/`
- 前端指南：`frontend/docs/guides/`
- 后端文档：`backend/docs/`
- 根导航：`docs/README.md`

—
最后更新时间：2025-09-26
维护人：AI 助手