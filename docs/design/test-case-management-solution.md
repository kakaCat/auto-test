# API测试用例管理解决方案设计文档

## 文档信息

| 项目名称 | AI自动化测试系统 - API测试用例管理 |
|----------|-----------------------------------|
| 文档版本 | v2.2.0 |
| 创建日期 | 2024-01-15 |
| 最后更新 | 2025-09-30 |
| 文档作者 | AI Assistant |
| 审核状态 | 待审核 |
| 适用版本 | v2.0.0+ |

## 文档概述

本设计文档描述了系统中的“API测试用例管理”功能，包括用例创建、参数配置、执行与结果查看等核心流程。文档全面去除了“场景”相关术语与功能描述，统一以“测试用例”作为核心对象。

## 目录

- 1. 抽屉式UI设计（ApiTestDrawer）
- 2. 用户交互流程设计
- 3. 项目概述与核心能力
- 4. 数据模型设计
- 5. 系统架构设计
- 6. 前端组件架构设计
- 7. 实施计划与质量保障

## 1. 抽屉式UI设计（ApiTestDrawer）

抽屉组件用于快速配置并执行 API 请求，支持：
- 基本请求信息：方法、URL、Headers、Query、Body（Raw/FormData）
- 认证配置：Token、Basic、Key（Header/Query）
- 请求选项：超时、是否跟随重定向
- 响应展示：Headers、Body（高亮/换行）、状态码与耗时
- 测试用例：保存/加载、列表展示与管理（本地持久化或服务端）

关键交互：
- 发送请求：根据抽屉中的配置即时发起请求并渲染响应
- 保存用例：将当前请求配置保存为测试用例条目用于复用
- 加载用例：选取历史用例填充请求配置后一键执行

## 2. 用户交互流程设计

- 新建用例：在抽屉中配置请求并保存为“测试用例”
- 编辑用例：从“测试用例管理”弹框中进入编辑，更新请求配置与描述
- 执行用例：加载或编辑当前用例后，直接在抽屉内发送请求
- 查看结果：在抽屉右侧响应面板查看响应体、Headers、状态码、耗时等

## 3. 项目概述与核心能力

- 用例生命周期：创建、编辑、保存、加载、执行、删除
- 参数管理：Headers/Query/Body/认证统一配置
- 快速反馈：响应面板高亮与结构化展示
- 复用与持久化：支持在浏览器或服务端持久化测试用例

## 4. 数据模型设计

测试用例数据（示例）：
```ts
type ApiTestCase = {
  id: string
  name: string
  description?: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS'
  url: string
  headers: Array<{ key: string; value: string }>
  query: Array<{ key: string; value: string }>
  bodyType: 'none' | 'raw' | 'formData'
  rawType?: 'text' | 'json' | 'xml'
  body?: string
  formData?: Array<{ key: string; value: string }>
  auth?: {
    type: 'none' | 'token' | 'basic' | 'key'
    token?: string
    username?: string
    password?: string
    keyName?: string
    keyValue?: string
    keyLocation?: 'header' | 'query'
  }
  options?: {
    followRedirects?: boolean
    timeout?: number
  }
}
```

## 5. 系统架构设计

- 前端：Vue 3 + Element Plus；Vitest 单元测试；Vite 构建
- 后端：统一 API 代理；用例存储接口（可选）
- 通信：REST 接口；错误信息统一处理与提示

## 6. 前端组件架构设计

- `ApiTestDrawer.vue`：测试抽屉主体，负责请求配置与响应展示
- `TestCaseManagement.vue`：测试用例管理弹窗，负责列表、增删改与加载
- `KeyValueEditor.vue`：键值对编辑器，复用在 Headers/Query/FormData 等位置

组件协作：
- 管理页面（API管理）中点击“测试用例”按钮，打开 `TestCaseManagement` 管理弹框
- 在抽屉中加载用例并执行，或从抽屉保存当前配置为新用例

### 6.1 测试用例管理弹框（TestCaseManagement.vue）

目标与范围：集中管理当前 API 的测试用例条目，支持创建、编辑、删除、复制、导入/导出与加载。

界面结构：
- 顶部工具栏：新增用例、批量删除、导入、导出、搜索框
- 用例列表：名称、方法、URL、描述、更新时间、操作（编辑/删除/复制/加载）
- 新增/编辑表单：名称、描述、绑定请求配置（方法、URL、Headers、Query、Body、认证、选项）

核心操作：
- 新增：打开表单，填写并保存为用例（生成 `id`），持久化到本地或服务端
- 编辑：从列表进入编辑，更新并保存
- 删除：单条或多选删除，二次确认
- 复制：以某一条为模板创建新用例，名称自动加后缀“(副本)”
- 加载：将所选用例配置发送至抽屉，抽屉直接填充并可执行
- 导入/导出：支持 JSON 文件导入/导出，用例结构统一

数据结构：
```ts
type ApiTestCaseListItem = {
  id: string
  name: string
  description?: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS'
  url: string
  updatedAt: string
}

type ApiTestCaseDetail = ApiTestCase & { updatedAt?: string }
```

表单校验：
- 必填：`name`、`method`、`url`
- URL 格式：允许相对路径或绝对路径（`http(s)://`）
- 键值对编辑器：去除空 key/value；允许重复 key；提供预设（如 `Content-Type`）

事件与通信：
```ts
// TestCaseManagement.vue -> ApiTestDrawer.vue
emit('load-test-case', testCaseDetail) // 加载至抽屉
emit('save-test-case', testCaseDetail) // 从抽屉保存或在弹框内保存

// ApiTestDrawer.vue <- TestCaseManagement.vue
on('load-test-case', fillRequestConfig)
on('save-test-case', persistTestCase)
```

持久化策略：
- 本地存储（默认）：`localStorage['api-test-cases'] = ApiTestCase[]`
- 服务端（可选）：统一接口 `unifiedApi.testCase.*`
  - `list(apiId): { success, data: ApiTestCaseListItem[] }`
  - `get(apiId, id): { success, data: ApiTestCaseDetail }`
  - `create(apiId, payload): { success, data: { id } }`
  - `update(apiId, id, payload): { success }`
  - `delete(apiId, id): { success }`
  - `import(apiId, cases: ApiTestCase[]): { success, imported: number }`
  - `export(apiId): { success, data: ApiTestCase[] }`

错误处理与提示：
- 接口失败：统一用 `ElMessage.error(message)`，必要时展示 `ElMessageBox` 重试/取消
- 表单错误：在表单项下方展示错误信息，并阻止提交

可用性与细节：
- 搜索：按名称/描述/URL 模糊搜索
- 排序：按 `updatedAt` 倒序默认排序
- 快捷操作：列表项点击即选中，回车触发“加载”
- 国际化：文案提取至 i18n 资源，避免硬编码

## 7. 实施计划与质量保障

- 分阶段实施：UI抽屉搭建 → 用例管理弹框 → 服务端持久化（可选）
- 测试策略：
  - 单元测试：请求参数构造、响应渲染、错误分支提示
  - 组件测试：抽屉渲染、用例保存与加载、交互行为
  - 集成测试（可选）：与后端接口的端到端校验
- 风险与对策：
  - 大响应体渲染性能：添加换行与折叠策略
  - 参数键值管理一致性：统一用 `KeyValueEditor`
  - 错误提示一致性：集中使用 `ElMessage` 与统一处理器

---

更新说明：本版本彻底移除所有与“场景”相关的描述、章节与示例，统一以“测试用例”作为术语与实现对象。后续如需扩展编排功能，请参考系统架构文档进行组件化设计，以测试用例为核心进行流程编排。