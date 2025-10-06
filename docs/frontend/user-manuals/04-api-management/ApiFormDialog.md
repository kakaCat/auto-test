# ApiFormDialog（新增/编辑 API 表单弹窗）

文档定位：本页仅覆盖“新增/编辑 API”的对话框形态（ApiFormDialog），不涉及主页面的列表/分页；与独立组件 ApiForm 的差异见文末。

- 关联源码：
  - <mcfile name="ApiFormDialog.vue" path="/Users/mac/Documents/ai/auto-test/frontend/src/views/api-management/components/ApiFormDialog.vue"></mcfile>
  - <mcfile name="ParameterConfig.vue" path="/Users/mac/Documents/ai/auto-test/frontend/src/views/api-management/components/ParameterConfig.vue"></mcfile>
  - <mcfile name="ParamsEditor.vue" path="/Users/mac/Documents/ai/auto-test/frontend/src/components/common/ParamsEditor.vue"></mcfile>

## 1. 组件概述
- 用途：在 API 管理页面中以弹窗形式完成 API 的新增/编辑。
- 角色：开发/QA 可访问；不同角色的可见性与按钮权限在主页面控制，此弹窗按入参渲染。
- 数据：承载基础信息、请求参数、响应参数、标签管理四大区块。

## 2. 范围与约束
- 范围：仅描述弹窗内的结构、交互、校验、数据映射及异常提示。
- 不包含：主页面的树导航、搜索区、表格、分页与批量操作。
- 一致性：字段顺序、区块标题与按钮文案以源码为准。

## 3. 布局 ASCII（结构与控件）

+------------------------------------------------------------------------------------+
| <el-dialog title="新增API/编辑API" width=70% top=5vh :close-on-press-escape=true   |
|                                                                                    |
| [顶部导航]  (按区块动态高亮，点击滚动到对应区块)                                     |
|  ┌───────────────────────────────────────────────────────────────────────────────┐ |
|  | [基础信息] [请求参数] [响应参数] [标签管理]                                   | |
|  └───────────────────────────────────────────────────────────────────────────────┘ |
|                                                                                    |
| [进度条]  基于必填项完成度实时计算（basicInfoProgress/rawFormProgress/formProgress） |
|  ┌───────────────────────────────────────────────────────────────────────────────┐ |
|  | ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  60%                                                     | |
|  └───────────────────────────────────────────────────────────────────────────────┘ |
|                                                                                    |
| 1) 基础信息（el-collapse-item name="basic"）                                      |
|    ┌─────────────────────────────────────────────────────────────────────────────┐ |
|    | - API名称: <el-input v-model=name placeholder="请输入API名称"/>              | |
|    | - 方法:    <el-select v-model=method :options=httpMethods />                 | |
|    | - URL:     <el-input v-model=url placeholder="https://example.com/path"/>   | |
|    |            [解析GET参数]（GET 且 URL 包含 ? 时显示；可覆盖现有参数）          | |
|    | - 所属系统: <el-select v-model=system_id @change=handleSystemChange />       | |
|    | - 所属模块: <el-select v-model=module_id :options=availableModules />        | |
|    | - 描述:    <el-textarea v-model=description />                               | |
|    | - 状态:    <el-switch v-model=enabled active-text="启用" inactive-text="禁用"| |
|    └─────────────────────────────────────────────────────────────────────────────┘ |
|                                                                                    |
| 2) 请求参数（el-collapse-item name="params"）                                     |
|    ┌─────────────────────────────────────────────────────────────────────────────┐ |
|    | <ParameterConfig v-model=parameters @change=handleParametersChange />        | |
|    | - 表格模式：键/类型/必填/示例/描述                                           | |
|    | - JSON模式：原始 JSON 编辑、导入/导出、格式化                                | |
|    └─────────────────────────────────────────────────────────────────────────────┘ |
|                                                                                    |
| 3) 响应参数（el-collapse-item name="response"）                                   |
|    ┌─────────────────────────────────────────────────────────────────────────────┐ |
|    | <ParamsEditor v-model=response_parameters />                                 | |
|    | - 支持状态码标签页、字段层级树、示例值与描述                                | |
|    └─────────────────────────────────────────────────────────────────────────────┘ |
|                                                                                    |
| 4) 标签管理（el-collapse-item name="tags"）                                      |
|    ┌─────────────────────────────────────────────────────────────────────────────┐ |
|    | <el-select v-model=tags multiple filterable :options=predefinedTags />       | |
|    | - 预定义标签 + 自定义输入（可新增）                                          | |
|    └─────────────────────────────────────────────────────────────────────────────┘ |
|                                                                                    |
| [底部操作区]                                                                      |
|  ┌───────────────────────────────────────────────────────────────────────────────┐ |
|  | [取消]（关闭对话框，保留外部状态）  [保存]（校验→映射→emit('save')，父组件提交，loading: saving） | |
|  └───────────────────────────────────────────────────────────────────────────────┘ |
+------------------------------------------------------------------------------------+

说明：各折叠区展开状态会被持久化（localStorage）；顶部导航按钮类型与高亮受 getSectionButtonType 与当前折叠状态影响；滚动定位使用 scrollToSection。

## 4. 关键交互与动态行为
- 顶部导航与高亮：点击导航按钮滚动到对应区块，并基于完成度/折叠态决定按钮样式；当区块校验通过时按钮显示“success”类型。
- 折叠状态持久化：首次挂载 onMounted 时从 localStorage 读取上次折叠态；每次切换通过 handleCollapseChange 写回。
- 进度计算：
  - basicInfoProgress/basicInfoComplete：名称、方法、URL、系统/模块、启用状态等必填完成度；
  - rawFormProgress：参数/响应等结构完成度；
  - formProgress：综合进度，debounce 更新避免频繁重绘。
- 解析 GET 参数：
  - 条件显示：method===GET 且 url 包含 '?'；
  - 点击后解析 query string → 参数表格结构（含类型与必填推断），若已有参数则弹出覆盖确认；
  - URL 校验失败或不含查询部分时给出提示。
- 系统/模块联动：
  - handleSystemChange 加载并刷新 availableModules；
  - 初始挂载 loadModuleList 根据当前 system_id 拉取并填充模块选项。
- 保存流程：
  - 表单校验 → URL 合法性检查 → 数据映射 → 提交；
  - 保存中 saving=true，成功后关闭对话框并向父层回传；失败展示错误消息。

## 5. 字段与校验规则
- API名称 name：必填，非空字符串；
- 方法 method：必选，来源于 httpMethods（GET/POST/PUT/DELETE/...）；
- URL url：必填，必须符合 http/https URL 规范；当方法为 GET 且包含查询参数时可触发“解析GET参数”。
- 所属系统 system_id：必选；
- 所属模块 module_id：在选择系统后加载并可选；部分实现中为必选，具体以业务约定为准；
- 描述 description：可选，文本；
- 启用 enabled：布尔；
- 请求参数 parameters：由 <ParameterConfig> 提供；
- 响应参数 response_parameters：由 <ParamsEditor> 提供；
- 标签 tags：多选；

## 6. 数据映射契约（前端 → 后端）
保存前端字段将映射到后端创建/更新模型（示例）：
- name → ApiInterfaceCreate.name
- method → ApiInterfaceCreate.method
- url → ApiInterfaceCreate.url
- system_id → ApiInterfaceCreate.system_id
- module_id → ApiInterfaceCreate.module_id
- description → ApiInterfaceCreate.description
- enabled → ApiInterfaceCreate.enabled
- parameters（表格/JSON）→ ApiInterfaceCreate.parameters（JSON 字符串）
- response_parameters（结构/示例）→ ApiInterfaceCreate.response_schema 或 response_example（JSON 字符串）
- tags（字符串数组）→ ApiInterfaceCreate.tags

注：具体后端模型字段命名以接口返回契约为准；组件内已实现字符串化与空值保护。

## 7. 权限与可见性
- 弹窗入口由主页面控制：仅在有“新增/编辑”权限时展示入口按钮；
- 弹窗内部字段不做权限判定，按传入数据决定可编辑性；被禁用的字段样式与交互由父层决定。

## 8. 异常与提示
- 校验失败：聚焦到对应字段并显示错误文案；
- URL 非法：阻止保存并弹出错误消息；
- 解析 GET 参数：若无查询部分或 URL 不合法，弹出错误消息；已有参数时弹出覆盖确认；
- 保存失败：展示后端返回 message 或通用网络错误；
- 折叠态读写异常：回退为默认展开策略，不阻断表单流程。

## 9. 与独立 ApiForm 的差异
- 展现形态：ApiFormDialog 为对话框集成形态；ApiForm 为独立组件/页面形态；
- 内容聚合：ApiFormDialog 内聚 ParameterConfig 与 ParamsEditor，完成度与折叠状态的持久化在此实现；
- 入口：ApiFormDialog 由主页面“新增/编辑”操作触发；ApiForm 可用于更自由的嵌入场景；
- 交互统一：解析 GET、系统/模块联动、保存映射在二者间保持一致，但布局与导航差异较大。

## 10. 版本与维护
- 适用代码版本：以 <ApiFormDialog.vue> 最新实现为准；
- 维护建议：变更字段或交互后同步更新本页 ASCII 与规则说明；为子组件（ParameterConfig、ParamsEditor）单独维护文档。