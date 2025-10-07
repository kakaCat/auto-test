# 04 — API 管理（API Management）

本文档面向前端页面“API管理”，提供页面的直观布局 ASCII 图示、页面与组件的规格说明（信息架构、字段校验、交互行为、数据契约、权限），以及从零到一的完整操作步骤说明。

> 适用范围：docs/frontend/user-manuals/04-api-management/ 下各组件文档的顶层总览与索引说明。

---

## 1. 页面概览
- 目标：统一管理系统/模块下的 API 接口，支持创建、导入/导出、搜索筛选、批量操作、测试与 Mock。
- 主要能力：
  - 系统树导航选择（左侧）
  - API 列表管理（右侧）
  - 搜索与筛选（关键词、请求方法）
  - 新增/编辑对话框、测试抽屉、Mock 管理
  - 批量选择与批量操作、分页

## 2. 信息架构
- 页面结构：
  - 页面头部：标题与描述、主操作按钮（新增API、导入API、导出API）
  - 左侧面板：SystemTree（系统/模块树形导航）
  - 右侧面板：
    - 搜索与筛选（关键词、方法）
    - 批量操作栏（当勾选行时显示）
    - API 列表（选择框、名称、方法、URL、所属系统、描述、状态、操作）
    - 分页器
- 组件参与（示例）：ApiFormDialog（新增/编辑）、ApiTestDrawer（测试）、ApiTestScenarioDrawer（场景测试）、MockManagement/MockEditDialog/MockTestDialog（Mock 管理）、ParameterConfig（请求参数结构配置）、ResponseConfig（响应字段结构配置）

## 3. ASCII图示（直观布局与主流程）

### 3.1 页面布局（左右分栏 + 列表 + 分页）

+----------------------------------------------------------------------------------------------+
| 页面头部                                                                                      |
|  - 标题: API管理  - 描述: 左侧选择系统/模块，右侧管理对应API                                  |
|  - 主操作按钮: [新增API] [导入API] [导出API]                                                  |
+---------------------------+------------------------------------------------------------------+
| 左侧面板：SystemTree      | 右侧面板：API管理                                                 |
|  - 树形导航（系统/模块）  |  - 搜索区: [关键词输入框] [方法下拉] [搜索] [重置]                |
|                           |  - 批量区(选中时): [批量测试] [批量启用] [批量禁用] [批量删除]     |
|                           |  - API列表（表格）：                                              |
|                           |    [选择] [API名称(+禁用标签)] [方法(彩色Tag)] [URL] [所属系统]    |
|                           |    [描述] [状态开关] [操作(编辑|测试|Mock|删除)]                  |
|                           |  - 分页器: 总数/页码/每页大小/跳转                                |
+---------------------------+------------------------------------------------------------------+

### 3.2 主交互流程（选择 → 搜索 → 查看/操作）

[左侧选择系统/模块] --> [右侧展示API列表] --> [搜索/筛选] --> [列表刷新]
                                        \-> 单项操作: [编辑|测试|Mock|删除]
                                        \-> 多选后批量操作: [测试|启用|禁用|删除]

### 3.3 新增/编辑流程（对话框表单）

[点击新增API/编辑] --> [ApiFormDialog 弹出] --> [填写表单+校验] --> [提交保存] --> [列表刷新]

### 3.4 测试流程（抽屉）

[点击测试] --> [ApiTestDrawer 打开]
             --> [请求参数配置: ParameterConfig]
             --> [发送请求 / 查看响应预览]
             --> [（可选）保存参数: ParameterSaveDialog]
             --> [（可选）保存测试场景: ApiScenarioEditDialog]

### 3.5 Mock 管理流程

[点击 Mock] --> [MockManagement]
              --> [MockEditDialog 编辑规则]
              --> [MockTestDialog 验证示例]
              --> [保存/启用 Mock] --> [列表标记]

---

## 4. 规格说明（页面与组件）

### 4.1 信息架构（页面数据）
- SystemTree（左侧）：
  - 展示系统/模块层级，支持节点点击与刷新事件。
  - 选择系统或模块后，右侧列表按所选上下文刷新。
- 搜索区（右侧顶部）：
  - 关键词：匹配 API 名称/描述/URL。
  - 请求方法：GET/POST/PUT/DELETE/PATCH（清空为不过滤）。
- 批量区（条件显示）：当勾选 ≥1 项时出现批量操作按钮与数量统计。
- 列表区：
  - 列：选择框、API名称（禁用显示 info Tag）、方法（按类型上色）、URL、所属系统名称、描述、状态开关、操作按钮组。
  - 操作：编辑（打开表单对话框）、测试（打开测试抽屉）、Mock（进入 Mock 管理）、删除。
- 分页器：页码、每页大小、总数、跳转。

### 4.2 字段校验（示例约定）
- ApiForm（表单）字段：
  - name：必填，字符串，不含仅空白；
  - version：可选，建议 SemVer 格式；
  - serviceName：必填；
  - moduleId：必选（从系统/模块上下文或下拉选择）；
  - method：必选（GET/POST/PUT/DELETE/PATCH）；
  - protocol：必选（如 http/https）；
  - url：必填，应满足路径格式；
  - description：可选；
  - headers：键值对列表，key/value 字符串；
  - parameters：参数项列表（name 必填，type ∈ string|number|boolean|object|array|file，required 复选）。
- ParameterConfig（请求参数配置）：
  - 支持 table/json 双模式；
  - table 模式支持拖拽排序、层级（对象/数组子项）、折叠、搜索；
  - json 模式支持格式化与验证，错误提示。
- ResponseConfig（响应结构配置）：
  - 支持 table/json 双模式；
  - table 模式以状态码为标签页，字段支持层级、拖拽、必返开关；
  - 示例生成与 JSON 编辑器，格式化与校验。

### 4.3 交互行为（页面）
- 状态管理：关键字段双向绑定；搜索与选择事件触发列表刷新；分页变更触发数据更新。
- 空状态：未选择系统/模块时显示引导提示。
- 条件显隐：批量区在勾选行后显示；清空搜索恢复默认列表。
- 安全与反馈：删除需确认；保存/测试/Mock 操作反馈成功或错误信息。

### 4.4 数据契约（列表与表单的核心字段）
- 列表项（示例）：
  - id: string
  - name: string
  - method: 'GET'|'POST'|'PUT'|'DELETE'|'PATCH'
  - url: string
  - system_name: string
  - description: string
  - enabled: boolean
- 表单项（示例）：参见“字段校验”章节的 ApiForm 字段说明。

### 4.5 权限（示例策略）
- 角色示例：Admin / QA / Dev。
- 建议可见性与操作权限：
  - Admin：全部页面可见，允许新增/编辑/删除/导入/导出/Mock/测试/批量操作。
  - QA：页面可见，允许测试、保存测试场景、导出；可编辑非关键字段；限制删除与导入。
  - Dev：页面可见，允许编辑与测试；限制导入/导出/批量删除；Mock 管理按项目策略控制。

---

## 5. 详细步骤（完整操作指南）

### 5.1 新增 API
1) 打开“API管理”页面，确认左侧系统树加载完成。
2) 点击页面头部“新增API”。
3) 在 ApiFormDialog 中填写：名称、方法、URL、所属模块等必填项，必要时补充 headers 与 parameters。
4) 提交保存，校验通过后关闭对话框，列表自动刷新显示新条目。

### 5.2 导入 / 导出
- 导入：
  1) 点击“导入API”，选择 .json / .yaml 文件。
  2) 校验格式后导入成功，列表刷新；失败时给出错误提示与修复建议。
- 导出：
  1) 点击“导出API”，选择导出范围（当前筛选或全部）。
  2) 生成并下载文件，文件名建议含系统/模块与时间戳。

### 5.3 搜索与筛选
1) 在关键词输入框输入名称/描述/URL 关键字。
2) 在“请求方法”下拉选择 GET/POST 等；可清空恢复默认。
3) 点击“搜索”，列表按条件刷新；点击“重置”恢复初始状态。

### 5.4 批量操作
1) 在列表中勾选需要处理的多条 API。
2) 在批量区域选择“批量测试/启用/禁用/删除”。
3) 执行后给出成功/失败反馈；删除需二次确认。

### 5.5 测试 API
1) 点击某条 API 的“测试”。
2) 在 ApiTestDrawer 中配置请求参数（可通过 ParameterConfig 表格/JSON 模式编辑）。
3) 发送请求，查看响应；必要时在 ResponseConfig 中整理期望字段结构与示例。
4) 可保存当前参数为模板（ParameterSaveDialog），或保存为测试场景（ApiScenarioEditDialog）。

### 5.6 Mock 管理
1) 点击某条 API 的“Mock”。
2) 在 MockManagement 中选择/创建 Mock 规则。
3) 使用 MockEditDialog 编辑规则细节；通过 MockTestDialog 验证示例数据与匹配逻辑。
4) 保存并启用 Mock，返回列表显示状态标识。

---

## 6. 组件索引（供后续详细文档使用）
- ApiFormDialog：新增与编辑表单（对话框形态） — 详见 [子文档](./04-api-management/ApiFormDialog.md)
- ParameterConfig：请求参数结构配置（表格/JSON） — 详见 [子文档](./04-api-management/ParameterConfig.md)
- ResponseConfig：响应结构配置（状态码标签页 + 表格/JSON） — 详见 [子文档](./04-api-management/ResponseConfig.md)
- ApiTestDrawer / ApiTestScenarioDrawer：测试抽屉与场景管理
- ParameterSaveDialog / ApiScenarioEditDialog：参数模板与场景编辑
- MockManagement / MockEditDialog / MockTestDialog：Mock 管理与规则编辑/验证
- SavedParametersList / KeyValueEditor / MockDataGenerator：辅助组件

注：各组件的详细说明与更细粒度 ASCII 图示将分别在 docs/frontend/user-manuals/04-api-management/ 子目录下的独立文档中提供。

## 7. 状态与数据流 / 事件与契约（统一入口 API 导入与调用 — MUST）

为避免运行时错误（例如“{} is not a function”）以及保证类型安全与一致的数据契约，本页面及其子组件必须通过统一入口进行命名导入与调用，不得使用默认导入或动态属性调用。

### 7.1 统一入口命名导入（必须）
- 必须从 `@/api/unified-api` 进行命名导入，使用项目统一暴露的客户端对象或实例。
- 禁止模式：`import unifiedApi from '@/api/unified-api'`（默认导入）；`unifiedApi['xxx'](...)`（动态属性调用）；`(obj as any)[key](...)`。
- 推荐模式（示例）：

```ts
// 推荐使用命名实例导入（若项目已提供命名实例）
import { systemApi, moduleApi, apiManagementApi } from '@/api/unified-api'

// 如统一入口导出为类（例如 SystemApi/ModuleApi），请在集中位置实例化并复用
// import { SystemApi, ModuleApi, ApiManagementApi } from '@/api/unified-api'
// export const systemApi = new SystemApi()
// export const moduleApi = new ModuleApi()
// export const apiManagementApi = new ApiManagementApi()
```

### 7.2 事件流与数据契约（SystemTree → 列表）
- 事件流：
  - 左侧 SystemTree 选择系统/模块节点 → 触发右侧 API 列表刷新。
  - 首次进入或切换系统：先加载系统列表与模块列表；模块列表应按系统缓存，避免重复拉取。
- 数据契约（响应示例）：
  - 系统列表：`ApiResponse<SystemEntity[]>` 或 `ApiResponse<{ data: SystemEntity[], total: number }>`。
  - 模块列表：`ApiResponse<{ data: ModuleEntity[], total: number }>`（部分接口可能直接返回数组，需规范化）。
  - 统一处理：若返回为数组，直接使用；若返回含 `data` 字段，则取 `res.data.data`。

### 7.3 示例：加载系统/模块并构建树（标准调用 + 规范化）

```ts
// 严格模式 + 强类型 + Promise<T> 返回
// 注意：以下为页面/组合式函数示例片段，演示统一入口调用与数据规范化

import { systemApi, moduleApi } from '@/api/unified-api'
import { useServiceStore } from '@/stores/service'

interface SystemEntity { id: string; name: string; category?: string }
interface ModuleEntity { id: string; name: string; system_id?: string; systemId?: string }
interface ApiResponse<T> { data: T; message?: string; code?: number }

const serviceStore = useServiceStore()

async function loadSystems(): Promise<SystemEntity[]> {
  const res = await systemApi.getEnabledListByCategory({ category: 'default' })
  const list = Array.isArray((res as unknown as ApiResponse<SystemEntity[]>).data)
    ? (res as unknown as ApiResponse<SystemEntity[]>).data
    : ((res as unknown as ApiResponse<{ data: SystemEntity[] }>).data?.data ?? [])
  return list
}

async function loadModulesBySystem(systemId: string): Promise<ModuleEntity[]> {
  const res = await moduleApi.getEnabledModules({ systemId })
  const list = Array.isArray((res as unknown as ApiResponse<ModuleEntity[]>).data)
    ? (res as unknown as ApiResponse<ModuleEntity[]>).data
    : ((res as unknown as ApiResponse<{ data: ModuleEntity[] }>).data?.data ?? [])
  // 缓存到 serviceStore，优先使用 system_id，其次兼容 systemId
  const normalized = list.map(m => ({ ...m, system_id: m.system_id ?? m.systemId }))
  serviceStore.setSystemModules(systemId, normalized)
  return normalized
}

async function buildSystemTree(): Promise<void> {
  const systems = await loadSystems()
  for (const s of systems) {
    const sid = s.id
    const cached = serviceStore.getModulesBySystem(sid)
    const modules = cached?.length ? cached : await loadModulesBySystem(sid)
    // 在此将系统节点与模块子节点绑定到树数据（略）
  }
}
```

### 7.4 禁止与迁移提示
- 禁止：
  - 默认导入统一入口：`import unifiedApi from '@/api/unified-api'`。
  - 任何形式的动态属性调用：`unifiedApi['xxx'](...)`、`(obj as any)[key](...)`。
- 迁移建议：
  - 将默认导入替换为命名导入；统一使用强类型方法调用，返回 `Promise<T>`；
  - 对返回结构进行规范化处理（数组 vs `{ data: T[], total }`），避免 UI 构建阶段出现空列表；
  - 在 SystemTree 构建前完成模块缓存填充，优先从 `serviceStore.getModulesBySystem(sid)` 读取，缺失时再拉取。

提示：以上规范与示例与“API 管理标准（API_MANAGEMENT_STANDARDS.md）”保持一致，请在开发、重构与联调阶段统一遵循。