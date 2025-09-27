# 前端代码风格规范

> 视觉总览：以下 ASCII 图示帮助你一眼掌握统一 API 架构与使用方式。

```
┌────────────────────┐      use       ┌─────────────────────────┐
│   Pages / Views    │ ─────────────▶ │  Composables / Stores   │
└────────────────────┘                └─────────────────────────┘
              │                                   │
              ▼                                   ▼
                  ┌────────────────────────────────────────────┐
                  │        unified-api 〈薄聚合器 / 单一入口〉     │
                  └────────────────────────────────────────────┘
                        │      │        │        │        │
                        ▼      ▼        ▼        ▼        ▼
                     system  module  apiManagement  category  monitor/log
                        │      │        │                         │
                        └──────┴────────┴──────────┬──────────────┘
                                                   ▼
                                   unifiedRequest（封装 request 工具）
                                                   ▼
                                 /api/... 后端 RESTful 接口（V2）
```

核心认识
- 所有 API 调用都从 `unified-api` 出发；具体域经由分入口暴露，如 `apiManagementApi`、`system`、`module` 等。
- `unified-api` 是“薄聚合器”，仅做命名聚合与少量适配，真正调用经 `unifiedRequest` 统一下沉至 `request` 工具。
- 严禁直接在根对象上使用已废弃直通方法（如 `unifiedApi.getApis()`）。

API 管理域调用路径（最常用）
```
[View/Component]
   │
   ├─ import unifiedApi from '@/api/unified-api'
   │
   └─ unifiedApi.apiManagementApi.getApis(params)
                      │
                      └─ unifiedRequest.get('/api/api-interfaces/v1/', params)
                                             │
                                             └─ Backend API (V2)
```

目录导览（与调用约束强关联）
```
frontend/
  src/
    api/
      unified-api.ts        # 单一入口，分域导出：system/module/apiManagementApi/...
    views/
      api-management/       # 仅通过 unifiedApi.apiManagementApi 调用
      page-management/      # 弹窗/表单内拉取 API 列表同样走 apiManagementApi
      workflow-orchestration/
        designer.vue        # 可命名导入：{ unifiedApiManagementApi }
```

使用对照·速查（复制即可修复）
```
// Bad（已废弃）
const apiProxy = unifiedApi
await unifiedApi.getApis(params)

// Good（统一分域入口）
const apiProxy = unifiedApi.apiManagementApi
await apiProxy.getApis(params)
```

常见错误与定位
- 报错 `getApis is not a function`：检查是否从根对象调用，改为 `unifiedApi.apiManagementApi.getApis()`。
- 无法加载模块列表：使用 `unifiedApi.apiManagementApi.getModuleList()`，不要用根对象直通方法。
- 统一导入风格：页面可用默认导出 `unifiedApi`，也可命名导入 `{ unifiedApiManagementApi }`，但不要混用旧直通命名。


## 概述

本文档定义了前端项目的代码风格规范，特别是API层的设计模式和编码标准。通过统一的代码风格，确保项目的可维护性、可读性和团队协作效率。

## API架构设计规范（重构版·强制要求）

本节为此次 API 重构确立的强制规范，覆盖设计理念、原则与必须遵循的约束。除非显式豁免，所有新旧代码均需对齐。

### 0. 设计理念
- 统一入口、分域实现：`unified-api.ts` 仅作“薄聚合器”，各域在独立文件中实现（如 `system-api.ts`、`module-api.ts`）。
- 无兼容映射：删除旧接口与适配层，不再保留“旧 → 新”映射逻辑。
- 类型优先：接口、参数、返回值使用 TypeScript 接口，`strict: true`，杜绝 `any`。
- 可演进：按“域 → 子域”增长，文件超过可维护阈值再拆分，不回退到巨石文件。

### 1. 强制结构
- 入口：`src/api/unified-api.ts` 只导出各域 API 的命名聚合，不暴露“便捷直通方法”。
- 分域：`src/api/{domain}-api.ts` 中实现具体域 API，依赖 `BaseApi`、`request` 等基础设施。
- 类型：`src/api/types/` 统一定义基础类型与域类型，优先使用接口（interface）。
- 工具：转换器（converters）、规则（rules）等为静态工具类，禁止在其中进行数据收集或外部调用。

### 2. 禁止事项
- 禁止再引入或保留旧文件：`api/service.ts`、`api/service-optimized.ts`、`utils/apiSwitcher.ts` 等已移除。
- 禁止在 `unified-api.ts` 中写业务或映射逻辑；仅聚合命名导出。
- 禁止使用 `any` 与隐式 `Promise<any>`；异步函数必须返回 `Promise<T>`。
- 禁止魔法值，使用常量或枚举；禁止空指针，入参与返回做空值检查。

### 3. 命名与导出
- API 文件：`{domain}-api.ts`；导出对象命名为 `{domain}Api`（例：`systemApi`、`moduleApi`）。
- 统一导入：`import { systemApi, moduleApi } from '@/api/unified-api'`。
- 类型命名：`{Domain}Entity`、`{Domain}ListParams`、`Create{Domain}Params`、`Update{Domain}Params`、`{Domain}Statistics`。

### 4. 分层职责（前端 API 防腐侧）
- BaseApi：通用 CRUD、标准化响应、错误处理与拦截，不承载业务逻辑。
- 业务API（域API）：组合基础能力，提供清晰的领域语义方法；不写跨域耦合逻辑。
- Converter/Rule/Wrapper：均为静态方法；Converter 负责字段映射与格式标准化；Rule 负责参数与业务规则校验；Wrapper 负责权限包装与脱敏。

### 5. 错误处理与异常
- 统一抛出具描述性的 `Error`：`throw new Error('获取系统列表失败: 具体原因')`。
- 网络与数据错误分流记录，日志归口到统一拦截层；API 方法内仅做必要补充语义信息。

### 6. 迁移与扩展
- 新增域：新增 `{domain}-api.ts` 与对应类型，更新 `unified-api.ts` 聚合导出。
- 扩展方法：优先在域 API 内扩展，不在入口下沉“直通函数”。
- 再拆分触发条件：单文件 > 600 行或导出方法 > 20 个；拆分为 `{domain}/{subdomain}-api.ts`，并在域文件内 re-export。

---

### 1. 分层架构原则（延续并细化）

#### 基础API层 (BaseApi)
- **职责**：提供通用的CRUD操作和标准化接口
- **特点**：
  - 统一的错误处理机制
  - 标准化的响应格式
  - 可复用的基础方法
  - 类型安全的参数定义

```typescript
// 示例：BaseApi类设计
export abstract class BaseApi<T extends BaseEntity> {
  protected apiHandler = apiHandler;
  
  // 标准CRUD方法
  async getList(params: BaseListParams): Promise<ApiResponse<T[]>>
  async getDetail(id: string): Promise<ApiResponse<T>>
  async create(data: Partial<T>): Promise<ApiResponse<T>>
  // ...其他标准方法
}
```

#### 业务API层 (具体业务API)
- **职责**：继承BaseApi，实现特定业务逻辑
- **特点**：
  - 继承基础功能，减少代码重复
  - 扩展业务特有方法
  - 保持接口一致性

```typescript
// 示例：SystemApi类设计
export class SystemApi extends BaseApi<SystemEntity> {
  constructor() {
    super('/api/v2/systems');
  }
  
  // 业务特有方法
  async getModuleCount(systemId: string): Promise<ApiResponse<number>>
  async getApiCount(systemId: string): Promise<ApiResponse<number>>
}
```

### 2. 类型定义规范（严格）

#### 接口命名规范
- **实体接口**：`{Domain}Entity`
- **列表参数**：`{Domain}ListParams`
- **创建参数**：`Create{Domain}Params`
- **更新参数**：`Update{Domain}Params`
- **统计数据**：`{Domain}Statistics`

#### 类型安全原则
- 优先使用接口而非类型别名
- 避免使用`any`类型，优先使用`unknown`
- 使用严格模式（strict: true）
- 为异步函数返回Promise<T>

```typescript
// 示例：类型定义
export interface SystemEntity extends BaseEntity {
  name: string;
  description?: string;
  category: string;
  enabled: boolean;
}

export interface SystemListParams extends BaseListParams {
  category?: string;
  enabled?: boolean;
}
```

### 3. 错误处理规范（统一）

#### 统一错误处理
- 使用统一的错误处理机制
- 提供清晰的错误信息
- 支持错误重试和降级

```typescript
// 示例：错误处理
try {
  const response = await this.apiHandler.get<T[]>(this.baseUrl, params);
  return response;
} catch (error) {
  throw new Error(`获取${this.resourceName}列表失败: ${error.message}`);
}
```

## 编码标准（TypeScript 强约束）

### 1. TypeScript规范

#### 基本原则
- 复杂对象形状首选接口而非类型别名
- 使用类型化对象进行复杂状态管理
- 使用带有描述性消息的Error对象
- 利用判别联合处理复杂类型场景

#### 代码示例
```typescript
// ✅ 推荐：使用接口
interface UserConfig {
  name: string;
  email: string;
  preferences: UserPreferences;
}

// ❌ 避免：使用any
function processData(data: any) { }

// ✅ 推荐：使用具体类型
function processData(data: UserConfig) { }
```

### 2. 架构约束（前端侧约束）

#### 分层职责
- **Controller层**：只做接收请求、调用Service、返回响应
- **Service层**：业务逻辑防腐层，数据收集与组装
- **Converter层**：静态数据转换工具
- **Rule层**：静态业务规则验证工具
- **Wrapper层**：静态权限包装工具

#### 命名规范
- **类命名**：`{Domain}Controller`、`{Domain}Service`、`{Domain}Converter`
- **方法命名**：Controller用get/create/update/delete前缀
- **文件结构**：controller/、service/{domain}/、infrastructure/

### 3. 代码模式

#### API调用模式
```typescript
// 标准API调用模式
export class SystemApi extends BaseApi<SystemEntity> {
  constructor() {
    super('/api/v2/systems');
  }
  
  async getSystemStatistics(): Promise<ApiResponse<SystemStatistics>> {
    try {
      return await this.apiHandler.get<SystemStatistics>(`${this.baseUrl}/statistics`);
    } catch (error) {
      throw new Error(`获取系统统计信息失败: ${error.message}`);
    }
  }
}
```

#### 组件设计模式
```typescript
// 组件设计模式
export default defineComponent({
  name: 'SystemManagement',
  setup() {
    const systemApi = new SystemApi();
    
    // 响应式数据
    const systems = ref<SystemEntity[]>([]);
    const loading = ref(false);
    
    // 方法定义
    const loadSystems = async () => {
      loading.value = true;
      try {
        const response = await systemApi.getList();
        systems.value = response.data;
      } catch (error) {
        ElMessage.error(error.message);
      } finally {
        loading.value = false;
      }
    };
    
    return {
      systems,
      loading,
      loadSystems
    };
  }
});
```

## 文件组织规范（最终结构）

### 1. 目录结构
```
src/
├── api/                    # API层
│   ├── base-api.ts         # 基础API类
│   ├── system-api.ts       # 系统管理API（域）
│   ├── module-api.ts       # 模块管理API（域）
│   ├── category-api.ts     # 分类API（域）
│   ├── log-api.ts          # 日志API（域）
│   ├── monitor-api.ts      # 监控API（域）
│   ├── api-management-api.ts # API管理（域）
│   ├── unified-api.ts      # 薄聚合器，仅命名导出
│   ├── types/              # 类型定义
│   ├── converters/         # 数据转换器（静态）
│   └── services/           # 业务服务（如有）
├── components/            # 通用组件
├── views/                 # 页面组件
├── utils/                 # 工具函数
└── types/                 # 全局类型定义
```

### 2. 文件命名
- **API文件**：`{domain}-api.ts`
- **类型文件**：`{domain}-types.ts`
- **组件文件**：`PascalCase.vue`
- **工具文件**：`camelCase.ts`

### 3. 导入导出规范（统一）
```typescript
// 统一导出
export { SystemApi } from './system-api';
export { ModuleApi } from './module-api';
export type { SystemEntity, SystemListParams } from './types/system-types';

// 统一导入
import { SystemApi, type SystemEntity } from '@/api';
```

## 代码质量保证（落地）

### 1. 代码检查
- 使用ESLint进行代码规范检查
- 使用Prettier进行代码格式化
- 使用TypeScript进行类型检查

### 2. 文档规范
- 所有公共API必须有JSDoc注释
- 复杂业务逻辑需要详细注释
- 接口和类型定义需要说明文档

```typescript
/**
 * 系统管理API
 * 提供系统的CRUD操作、状态管理、统计信息等功能
 * 
 * @example
 * ```typescript
 * const systemApi = new SystemApi();
 * const systems = await systemApi.getList();
 * ```
 */
export class SystemApi extends BaseApi<SystemEntity> {
  /**
   * 获取系统的模块数量
   * @param systemId 系统ID
   * @returns 模块数量
   */
  async getModuleCount(systemId: string): Promise<ApiResponse<number>> {
    // 实现代码
  }
}
```

### 3. 测试规范
- 单元测试覆盖率不低于80%
- 关键业务逻辑必须有测试用例
- API接口需要集成测试

## 性能优化规范

### 1. 代码优化
- 使用静态方法减少实例创建
- 合理使用缓存机制
- 避免不必要的重复计算

### 2. 网络优化
- 合理使用请求缓存
- 实现请求去重
- 支持请求取消

### 3. 内存优化
- 及时清理事件监听器
- 避免内存泄漏
- 合理使用响应式数据

## 安全规范

### 1. 数据安全
- 敏感信息不得在前端存储
- 使用HTTPS进行数据传输
- 实现请求签名验证

### 2. 权限控制
- 实现统一的权限验证
- 敏感操作需要二次确认
- 支持权限级联控制

## 版本控制规范

### 1. 提交规范
- 使用语义化提交信息
- 每次提交包含单一功能
- 重要变更需要详细说明

### 2. 分支管理
- 功能开发使用feature分支
- 重构工作使用refactor分支
- 主分支保持稳定状态

## 总结

本规范文档定义了前端项目的代码风格标准，特别是API层的设计模式。通过遵循这些规范，我们可以：

1. **提高代码质量**：统一的编码标准确保代码的可读性和可维护性
2. **增强团队协作**：一致的代码风格减少沟通成本
3. **降低维护成本**：标准化的架构设计便于后续维护和扩展
4. **提升开发效率**：可复用的组件和模式加速开发进程

所有团队成员都应该严格遵循本规范，确保项目代码的一致性和质量。

---

## API 路径规范（重要）

为彻底避免路径前缀歧义，前端在 API 路径书写与配置上必须遵循以下强约束：

### 核心原则
- 全局基础路径：`request.baseURL` 仅在设置了 `VITE_API_BASE_URL` 时生效；默认不设置任何基础路径（不会自动添加 `/api`）。
- 端点写全路径：在业务域中书写完整端点路径（至少包含 `'/api/...'`，或直接使用完整域名）。
- 统一接口单独基地址：`unified-api` 通过 `unifiedRequest` 设置绝对 `UNIFIED_API_BASE`，该通道内 URL 可包含 `/api/...`，与全局代理互不影响。

### 网关与基础路径配置
- `/api` 是后端对外暴露的路径片段之一，并非“全局自动前缀”。
- 如需通过网关或不同环境域名访问，可在业务域端点中直接写完整路径；也可选择在 `.env.*` 中设置 `VITE_API_BASE_URL`（可选）。
- 建议：默认不配置全局 `baseURL`，端点写全路径；只有在明确需要集中切换基地址时，才配置 `VITE_API_BASE_URL`。

### 名词解释：基础路径 vs 网关前缀
- 基础路径（baseURL）：仅当通过 `VITE_API_BASE_URL` 配置时才生效；默认不设置。
- 网关前缀（gateway prefix）：如 `'/gateway'` 或完整域名（`https://gw.company.com`）。若使用网关，可直接在端点中写完整路径或通过 `VITE_API_BASE_URL` 统一配置。
- 端点路径（endpoint path）：业务代码中建议直接书写完整路径，例如 `'/api/workflows/v1'`、`'/api/modules/v1'`，或使用完整域名。

### Do / Don't（立即可用的修复对照）
```ts
// ✅ Do：端点显式包含 '/api' 或完整域名（request.baseURL 默认未设置）
request.get('/api/workflows/v1/')
request.post('/api/modules/v1/', data)

// ❌ Don't：遗漏 '/api'（在未配置 baseURL 的情况下会 404）
request.get('/workflows/v1/')
request.post('/modules/v1/', data)

// ✅ Do：统一接口走绝对基础地址
unifiedRequest.get('/api/api-interfaces/v1/', params)
```

### 配置示例（可选：仅在需要集中切换基地址时）
```bash
# .env.development（默认不设置，全路径由端点显式书写）
# VITE_API_BASE_URL=

# .env.staging（如需集中切换，可设置完整网关或域名）
# VITE_API_BASE_URL=https://staging.api.company.com

# .env.production（如需集中切换，可设置完整域名）
# VITE_API_BASE_URL=https://api.company.com
```

注意：`'/api'` 是后端接口路径的一部分，并非“全局自动前缀”。默认不配置 `baseURL` 时，请在端点中显式书写 `'/api/...'` 或完整域名。

### 兼容性与防御性增强（可选）
- 兼容历史代码：如项目曾配置 `baseURL='/api'`，`normalizeUrl` 会在发现重复时自动剥除，避免 `/api/api/...`。
- 规范约束：结合当前约定，建议检测“在未配置 baseURL 时遗漏 '/api'”的情况。

### 迁移指引
1. 去除对默认 `'/api'` baseURL 的依赖：不再提供默认基础路径。
2. 在各模块 API 文件中将端点改为包含 `'/api/...'` 的完整路径，或根据需要写入完整域名。
3. 如需集中切换基地址，可在 `.env.*` 配置 `VITE_API_BASE_URL`，否则保持未配置并在端点中显式书写。
4. 统一接口（`unified-api.ts`）保持使用 `UNIFIED_API_BASE`，内部 URL 可保留 `/api/...`。

### 设计来源与现状
- 后端 API 前缀统一为 `/api`，本地通过 Vite 代理或环境变量直连；
- 统一接口模块使用独立服务端口与绝对基础地址；
- 出现 404 的根因是“`request.baseURL='/api'` + 端点自身以 `/api/...` 开头”的双重前缀叠加，已在工作流与场景模块修复。

请在新增或改动任何 API 时，严格按照本节规范执行，确保不会产生路径前缀重复问题；不要在源码中重复书写 `/api` 或网关前缀。