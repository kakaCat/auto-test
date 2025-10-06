# 前端变更日志：API 表单中“所属系统/所属模块”回显为 ID（非名称）问题记录

日期：2025-10-03
作者：前端

## 背景与现象
- 在 API 表单弹窗中，“所属系统”和“所属模块”的选择框在回显（编辑已有数据或加载表单初始值）时，显示的是 ID，而不是名称。
- 期望行为是显示选项的名称（`system.name` / `module.name`）。

## 影响范围
- 受影响文件：<mcfile name="ApiFormDialog.vue" path="/Users/mac/Documents/ai/auto-test/frontend/src/views/api-management/components/ApiFormDialog.vue"></mcfile>
- 受影响字段：`localFormData.system_id`、`localFormData.module_id`

## 证据与代码片段
- 选项绑定（显示名称、绑定值）：
  - 系统：`<el-option v-for="system in systemList" :key="system.id" :label="system.name" :value="system.id" />`
  - 模块：`<el-option v-for="module in availableModules" :key="module.id" :label="module.name" :value="module.id" />`
- 本地表单数据初始化（ID 字段为字符串）：
  - `const localFormData = reactive({ system_id: '', module_id: '' /* ... */ })`（见约 234 行附近）
- Props 中的 `systemList` 默认值为空数组：
  - `systemList: { type: Array, default: () => [] }`（见约 205 行附近）

## 根因分析
1) 类型不一致导致选项匹配失败：
- `el-select` 的选中值匹配使用严格等值（`===`）。当 `localFormData.system_id`/`module_id` 是字符串（例如 `'10'`），而选项的 `:value` 为数字（例如 `10`）时，匹配失败，组件会直接显示 `v-model` 的原始值（即 ID 字符串），而非选项的名称。

2) 列表异步加载导致初次渲染无选项：
- `systemList`/`moduleList` 在弹窗打开时可能尚未加载完成。此时 `el-select` 没有可选项，组件会显示 `v-model` 的原始值（ID）。后续列表加载完成后，由于类型不一致或未触发重新匹配，仍可能维持显示 ID。

3) 非直接因素（不构成根因，但与流程相关）：
- 已将“所属系统/所属模块”上移至“基本信息”最上方以便先选择系统并动态计算 `baseUrl`，这优化了使用流程，但不直接影响本回显问题。

## 解决方案建议
- 数据标准化（推荐，符合防腐层/Converter 设计原则）：
  - 在进入表单前，对系统与模块数据进行统一转换（Converter 静态方法），确保 `id` 类型一致（建议统一为字符串），例如 `String(system.id)`、`String(module.id)`。
- 选项值显式字符串化：
  - 在 `el-option` 上使用 `:value="String(system.id)"` 与 `:value="String(module.id)"`，与 `localFormData` 的字符串类型保持一致。
- 表单初值类型对齐：
  - 在为 `localFormData.system_id`/`module_id` 赋初值时，显式调用 `String(...)` 或将二者统一为数字类型，并在 `el-option` 同步使用数字类型绑定，保持一致性。
- 异步加载与匹配刷新：
  - 监听 `systemList`/`moduleList` 加载完成事件（或使用 `watch`），在列表就绪后触发一次匹配刷新（例如重新赋值 `localFormData.system_id = String(localFormData.system_id)`），以确保组件进行选项匹配。

## 后续动作（计划）
- 在父组件中增加 Converter 层：标准化 `SystemItem`/`ModuleItem` 数据结构（包含统一的 `id: string`、`name: string`、`url: string`），避免子组件兼容多个字段名与类型。
- 在 `ApiFormDialog.vue` 中对 `el-option` 的 `:value` 做显式字符串化处理，确保与 `localFormData` 保持一致。
- 增加列表就绪的校验与重匹配逻辑（`watch(systemList)`，当列表长度变化时检查并刷新选中项）。

## 备注
- 该问题与 `baseUrl` 动态计算逻辑独立，根因集中在 `el-select` 的值匹配与列表加载时序/类型一致性上。