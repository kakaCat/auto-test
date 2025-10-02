# 代码重构待办清单（ToDo List）

目标
- 落实测试场景管理简化与一致性改造：去除“管理API/测试分类/优先级”，取消分页；联动前端/后端/数据库与测试，确保契约统一与可回归。

最新进展（同步）
- 已完成：前端类型与场景API契约首批改造（无分页/字段统一）。
  - 文件：`frontend/src/types/api.ts`、`frontend/src/api/scenario.ts`
  - 统一字段：`scenario_type`、`tags`、`is_parameters_saved`、`saved_parameters_id`、`api_id`
  - 移除字段：`type`、`apis`、`category`、分页参数（如 `page/size`、`PaginationParams` 继承）
  - 列表查询：必须显式传入 `api_id`，支持 `keyword/status/tags/created_by/created_time_range/is_parameters_saved`
- 已完成：API 管理页接入“场景测试抽屉”（非分页列表/基础筛选/创建）
  - 文件：`frontend/src/views/api-management/components/ApiTestScenarioDrawer.vue`、`frontend/src/views/api-management/index.vue`
  - 集成点：操作列新增“场景”按钮，维护 `scenarioDrawerVisible/currentScenarioApi`
  - 接口调用：`unifiedApi.scenario.getList({ api_id, keyword?, status?, is_parameters_saved? })`；`unifiedApi.scenario.create({ name, description, scenario_type, api_id })`
  - 状态：开发环境已启动并完成初步页面验收
 - 已完成：参数保存/加载对话框对接（占位实现）
   - 文件：`frontend/src/views/api-management/components/ParameterSaveDialog.vue`、`SavedParametersList.vue`
   - 集成点：抽屉工具栏新增“保存参数/已保存参数”入口；支持批量保存与列表应用事件
   - 保存逻辑：设置 `is_parameters_saved=true` 与生成 `saved_parameters_id`（时间戳占位），后续对齐后端真实保存接口


范围与现状
- 涉及目录：`frontend/src`、`backend/src`、`docs/`、`monitoring/`（如有相关）、`tests/`
- 已完成的文档侧改动：`docs/design/test-case-management-solution.md` 已移除统计、分页、废弃字段并统一列表/筛选/表单示意。

工作分解结构（WBS）
1) 前端（frontend/）
- [ ] 类型与接口移除
  - 删除 `testCategory`、`priority`、`apiInterface`、`page`、`pageSize` 在 `src/types/`、`src/stores/`、`src/services/` 的定义与引用
  - 定义完成标准：全仓搜索无残留；类型编译通过
- [ ] 状态与数据流调整
  - 更新过滤器与查询参数，采用统一命名：`keyword/status/tags/created_by/created_time_range/is_parameters_saved`
  - `api_id` 通过路由或上层上下文提供（必填），不出现在表单字段
  - 完成标准：页面加载与筛选可用，无类型错误
- [ ] 服务与API调用签名
  - 修改 `scenarioApi` 请求：列表不带分页且必须 `api_id`；创建/编辑体移除废弃字段，新增 `scenario_type/tags/variables/is_parameters_saved/saved_parameters_id/api_id`
  - 完成标准：调用成功、与后端契约一致
- [ ] 组件与视图
  - 列表列为：选择、场景名称、状态、参数保存、操作；移除分页控件与逻辑（如需可加虚拟滚动）
  - 表单基础信息仅保留：场景名称、场景描述、标签
  - 完成标准：UI展示与交互符合设计，无废弃项
  - ✅ 已完成阶段性集成：场景抽屉基础版本（列表/筛选/创建）
  - ✅ 已完成阶段性集成：参数保存/加载入口（保存与列表占位实现）
- [ ] 路由与上下文
  - 明确当前 API 上下文的传递方案（路由参数/全局 store）
  - 完成标准：基于 `apiId` 的场景列表/新建/编辑正常工作
- [ ] 前端测试
  - 更新单元/组件测试；覆盖无分页、字段校验与交互流程
  - 完成标准：测试绿，关键路径手动验收通过

2) 后端（backend/）
- [ ] DTO与路由契约
  - 列表查询参数移除分页与废弃字段；保留并要求 `api_id`（路径或查询）
  - 创建/编辑请求体移除 `test_category/priority/apiInterface`
  - 完成标准：接口文档与实现一致
- [ ] 控制器与服务层
  - 移除分类/优先级/分页处理；实现基于 `api_id` 的关联过滤与非分页返回，默认按创建时间倒序
  - 完成标准：逻辑简化无回归，性能可接受
- [ ] DAO与查询
  - 移除分页 SQL；调整排序（默认按创建时间倒序）与返回限制策略
  - 完成标准：查询正确，边界下返回合理
- [ ] 后端测试
  - 更新单元/集成测试用例覆盖新契约
  - 完成标准：测试绿，接口自测通过

3) 数据库（迁移与模型）
- [ ] Schema迁移
  - 删除 `test_category` 与 `priority` 字段；移除相关索引（`idx_test_category`、`idx_priority`）
  - 保留并校验 `api_id` 外键与必要索引
  - 完成标准：迁移成功、约束完整
- [ ] 数据迁移与兼容
  - 旧数据字段的处理策略（可选择迁移到 `tags` 或忽略）
  - 完成标准：数据一致性验证通过

4) 文档与契约同步
- [ ] 后端接口文档 `docs/backend/api/`
  - 新旧契约差异、参数示例、错误码、边界条件
- [ ] 前端说明文档 `docs/frontend/`
  - 新UI字段、交互与数据流说明；明确场景查询参数与必填 `api_id`
- [ ] 变更日志 `docs/CHANGELOG.md`
  - 去除字段与取消分页的影响范围与迁移提示
  - 完成标准：文档齐备、可读性好

5) 验证与交付
- [ ] 本地运行与预览
  - 前端 `npm run dev` 启动，人工验收列表/筛选/表单无分页且无废弃字段
  - 后端服务启动，使用脚本/工具请求接口检验契约
- [ ] 自动化测试
  - 运行前后端测试套件，确保全部通过
- [ ] 回归检查
  - 搜索与清理其他模块对旧字段或分页逻辑的引用
  - 完成标准：关键功能回归正常

执行顺序建议
- 1) 后端契约与数据库迁移 → 2) 前端类型/服务/组件联动 → 3) 文档同步 → 4) 测试与验收 → 5) 回归与发布

风险与回滚
- 去除分页可能导致长列表性能风险：应准备列表虚拟化或服务端限流/分段加载方案
- 字段移除对旧数据的影响：保留迁移脚本，支持回滚（保留原字段的临时影子表或备份）

交付物清单
- 更新后的前端代码、后端代码、数据库迁移脚本
- 更新接口与前端文档、变更日志
- 测试报告（自动化与人工验收结论）

验收标准（统一）
- UI与API契约一致；数据库变更到位；测试全部通过；关键页面人工验收通过；文档更新完备

执行提示
- 搜索关键字：`testCategory|priority|apiInterface|page|pageSize|分页`
- 重点目录：`frontend/src/`、`backend/src/`、`docs/`
- 验收标准：契约统一、迁移安全、测试通过、文档完善