# 代码重构 ToDoList（基于 test-case-management-solution v2.2.0 与现有代码差异）

## 进度与任务清单（勾选）
- ✅ 文档：移除“场景”术语与功能，统一为“测试用例管理”
- ✅ 文档：补充“测试用例管理弹框”详细设计（v2.2.0）
- [ ] 前端：移除场景测试抽屉入口与相关逻辑（ApiTestScenarioDrawer）
- [ ] 前端：停止导出并删除 ApiTestScenarioDrawer 组件文件
- [ ] 前端：删除所有与场景测试抽屉相关的前端测试文件
- [ ] 前端：在 API 管理页接入“测试用例管理弹框”（TestCaseManagement.vue）
- [ ] 前端：类型与接口契约更新（用例无分页、统一字段、`api_id` 上下文）
- [ ] 前端：清理旧逻辑与统一字段（移除 `priority/category/pagination/sequential`）
- [ ] 前端：测试与验收（类型/组件/交互测试及人工验收）
- [ ] 后端：测试用例管理接口契约与服务层（可选，若采用本地存储则延期）
- [ ] 后端：数据库迁移与模型更新（新增/删除字段与索引，若落地）
- [ ] 回归与发布（全局搜索清理与最终交付）

## 范围与依据
- 依据文档：`docs/design/test-case-management-solution.md`（v2.2.0）
- 比对对象：当前前端 `frontend/` 与后端 `backend/` 代码，实现“API 测试用例管理”，淘汰“场景”相关入口与组件。
- 目标：统一术语与契约（字段/无分页/交互），以“测试用例管理弹框”为核心，保留参数保存/加载能力，并按代理入参归一化策略继续推进一致性。

## 差异摘要（发现）
- 前端接口与类型：
  - 仍存在以“场景”为核心的类型与接口（如 `src/api/scenario.ts`、`ScenarioListParams`），需要改造/移除。
  - 旧字段 `priority/category/page/size/sequential` 在若干页面与类型中仍有引用，需统一清理。
- 前端交互与页面：
  - API 管理页存在“场景”入口与 `ApiTestScenarioDrawer.vue` 使用，需移除并替换为“测试用例管理弹框”。
  - 参数保存/加载组件已存在，但与“场景抽屉”耦合，需要解耦到“测试用例弹框”。
- 后端接口与实现：
  - 若采用后端存储测试用例，需新增或改造接口（列表无分页、按 `api_id` 过滤、统一字段）。如近期以本地存储为主，可推迟后端改造。

## 执行事项（分域）

### 1) 前端
- 移除“场景”相关入口与组件
  - 从 `api-management/index.vue` 删除“场景”按钮、`openScenarioDrawer` 方法、`scenarioDrawerVisible/currentScenarioApi` 状态及 `<ApiTestScenarioDrawer .../>` 标签。
  - 从 `src/views/api-management/components/index.ts` 取消导出 `ApiTestScenarioDrawer`。
  - 删除组件文件：`src/views/api-management/components/ApiTestScenarioDrawer.vue`。
  - 删除测试文件：`src/test/ApiTestScenarioDrawer.*.test.js`。
- 接入“测试用例管理弹框”（设计已完成，代码待落地）
  - 新增/接入 `TestCaseManagement.vue`：支持创建/编辑/删除/复制/加载/导入导出（详见设计文档 6.1）。
  - 在 API 管理页加入入口，传递 `api_id` 上下文。
  - 事件通信：`load-test-case`、`save-test-case`、`apply-parameters` 等。
- 类型与契约对齐（无分页、统一字段）
  - 用例模型：`test_case_type`（normal/exception/boundary/security/performance）、`tags[]`、`is_parameters_saved`、`saved_parameters_id` 等。
  - 查询入参：`api_id`（必需）、`keyword/status/tags/created_by/created_time_range/is_parameters_saved`，无分页。
  - 统一代理层参数归一化：`camelCase → snake_case`；`tags[] → 逗号字符串`；时间区间数组转逗号字符串。
- 清理旧逻辑与统一字段
  - 全局移除：`priority|category|PaginationParams|page|size|sequential|场景` 等关键词的使用。
  - 需求管理中的模拟数据可暂保留并加 TODO 标注。
- 前端测试
  - 更新/新增单元与组件测试：弹框交互、类型校验、参数保存/加载、执行入口与回填。

### 2) 后端（可选）
- 接口契约（若落地用例后端存储）：
  - 列表：`GET /api/test-cases/v1/` 按 `api_id` 必填过滤；支持 `keyword/status/tags/created_by/created_time_range/is_parameters_saved`；无分页。
  - 详情/创建/更新/删除：统一字段，移除旧字段（如 `priority/category`）。
- 服务与转换：在对应 service/converter 中统一返回结构。
- 数据库与迁移：新增/对齐字段与索引；删除旧字段与索引；默认创建时间倒序。

### 3) 文档与验收
- 文档同步
  - 更新接口文档与前端说明，替换“场景”为“测试用例”，同步字段与示例。
  - 维护变更日志与迁移指引：移除旧字段、全局术语统一。
- 验收标准
  - 前端：API 管理页弹框可用；参数保存/加载跑通；无“场景”入口与组件。
  - 后端：接口契约一致（如启用后端存储）；过滤生效；无分页参数。
  - 测试：关键路径测试通过；人工验收完成。
- 交付物
  - 代码更新（前后端，视实现范围而定）、使用说明与变更日志。

## 详细实现步骤（前端页面）

### 步骤 A：前置校准与基础设施
- 校准请求基址与代理归一化策略，确保无重复前缀与字段映射正确。
- 路由上下文：在 API 管理页为弹框传递 `api_id`；可选 Query 保持状态。

### 步骤 B：移除场景抽屉与相关逻辑
- 精确删除入口按钮、方法与组件标签；移除状态与事件；确保页面可构建。
- 伴随删除相关测试与导出项；运行测试确认无残留引用。

### 步骤 C：接入测试用例管理弹框
- 组件结构：工具栏、列表与筛选、表单区、操作区（详见设计文档）。
- 事件通信与数据持久化：默认 `localStorage`；可切换为后端接口。
- 验收：弹框打开/关闭稳定；基本 CRUD 与参数保存/加载可用。

### 步骤 D：类型与服务契约对齐
- 更新前端类型文件与 API 层；统一返回类型 `ApiResponse<...>`。
- 验收：无 TS 报错；Mock 或真实接口调用成功。

### 步骤 E：清理旧逻辑与统一字段
- 全局搜索并移除旧字段与分页控件；保守处理非本模块依赖，标注 TODO。

### 步骤 F：测试与验收
- 单元/组件测试：弹框交互、数据模型、参数保存/加载、执行入口。
- 人工验收：在 API 管理页打开弹框、创建/编辑/删除/复制用例；无分页 UI；过滤器与交互一致。

## 组件拆分清单（建议）
- `TestCaseManagement.vue`：测试用例管理弹框（主控件）。
- `TestCaseFilterBar.vue`：筛选区组件。
- `TestCaseTable.vue`：用例列表组件。
- `TestCaseForm.vue`：用例创建/编辑表单。
- `ParameterSaveDialog.vue` / `SavedParametersList.vue`：参数保存/加载。

## 里程碑与验收门槛
- ✅ 里程碑 1：文档更新完成（v2.2.0，术语统一）。
- [ ] 里程碑 2：场景入口与组件完全移除。
- [ ] 里程碑 3：测试用例弹框接入并基本 CRUD 可用。
- [ ] 里程碑 4：测试全部通过与人工验收完成。

## 受影响文件（导航）
- 前端：
  - `src/views/api-management/index.vue`
  - `src/views/api-management/components/ApiTestScenarioDrawer.vue`（删除）
  - `src/views/api-management/components/index.ts`
  - `src/views/api-management/components/TestCaseManagement.vue`（新增/接入）
  - `src/views/api-management/components/ParameterSaveDialog.vue`
  - `src/views/api-management/components/SavedParametersList.vue`
  - `src/test/ApiTestScenarioDrawer.*.test.js`（删除）
- 后端（可选）：
  - `backend/src/test_case_service.py`（新增，若启用后端存储）
  - `backend/src/models/*` 与迁移脚本（若启用后端存储）

## 搜索关键词建议（清理旧逻辑）
- `ApiTestScenarioDrawer|Scenario|场景|appliedParams|openScenarioDrawer|priority|category|PaginationParams|page|size|sequential`