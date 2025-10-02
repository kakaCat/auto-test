# API重构计划文档

## 重构概述

本文档描述了前端API层的重构计划，旨在提高代码的可维护性、可扩展性和类型安全性。

## 当前状况分析

### 现有API结构
- **unified-api.ts** (767行)：包含所有API接口的统一文件
- 功能模块：系统管理、模块管理、分类管理、日志管理、监控管理、API管理
- 兼容性适配器：保持与旧版API的兼容性

### 存在的问题
1. **单文件过大**：767行代码集中在一个文件中，难以维护
2. **代码重复**：各模块间存在相似的CRUD操作代码
3. **类型定义分散**：接口定义混杂在实现代码中
4. **缺乏继承复用**：没有利用面向对象的继承特性
5. **测试困难**：单一大文件难以进行单元测试

## 重构目标

### 主要目标
1. **模块化分离**：将不同功能模块分离到独立文件
2. **代码复用**：创建基础API类，提供通用CRUD功能
3. **类型安全**：统一类型定义，提供完整的TypeScript支持
4. **可维护性**：清晰的文件结构和职责分离
5. **向后兼容**：保持现有API调用方式不变

### 性能目标
- 减少代码重复率至少50%
- 提高代码可读性和可维护性
- 保持API响应性能不变

## 架构设计

### 新的文件结构
```
src/api/
├── base-api.ts              # 基础API类
├── system-api.ts            # 系统管理API
├── module-api.ts            # 模块管理API
├── category-api.ts          # 分类管理API
├── log-api.ts              # 日志管理API
├── monitor-api.ts          # 监控管理API
├── api-management-api.ts   # API管理API
├── types/                  # 类型定义目录
│   ├── index.ts           # 统一导出
│   ├── base.ts            # 基础类型
│   ├── system.ts          # 系统相关类型
│   ├── module.ts          # 模块相关类型
│   └── ...
├── converters/            # 数据转换器
│   ├── system-converter.ts
│   ├── module-converter.ts
│   └── ...
└── unified-api.ts         # 兼容性适配器（保留）
```

### 分层架构

#### 1. 基础层 (BaseApi)
```typescript
abstract class BaseApi<T extends BaseEntity> {
  protected abstract endpoint: string
  
  // 通用CRUD操作
  getList(params?: BaseListParams): Promise<ApiResponse<T[]>>
  getDetail(id: string): Promise<ApiResponse<T>>
  create(data: CreateParams<T>): Promise<ApiResponse<T>>
  update(id: string, data: UpdateParams<T>): Promise<ApiResponse<T>>
  delete(id: string): Promise<ApiResponse<void>>
  
  // 通用功能
  toggleEnabled(id: string, enabled: boolean): Promise<ApiResponse<T>>
  batchOperation(data: BatchOperationParams): Promise<ApiResponse<void>>
  getStatistics(): Promise<ApiResponse<StatisticsData>>
  search(keyword: string): Promise<ApiResponse<T[]>>
  export(params?: ExportParams): Promise<ApiResponse<Blob>>
  import(file: File): Promise<ApiResponse<ImportResult>>
}
```

#### 2. 业务层 (具体API类)
```typescript
class SystemApi extends BaseApi<SystemEntity> {
  protected endpoint = '/systems'
  
  // 系统特有功能
  getCategories(): Promise<ApiResponse<CategoryData[]>>
  getEnabledListByCategory(category: string): Promise<ApiResponse<SystemEntity[]>>
  getSystemModuleCount(systemId: string): Promise<ApiResponse<number>>
  getSystemApiCount(systemId: string): Promise<ApiResponse<number>>
}
```

#### 3. 转换层 (Converters)
```typescript
class SystemConverter {
  static toEntity(data: any): SystemEntity
  static toCreateParams(data: any): CreateSystemParams
  static toUpdateParams(data: any): UpdateSystemParams
  static toListResponse(data: any): SystemEntity[]
}
```

#### 4. 兼容层 (Compatibility Adapter)
保持现有的 `unified-api.ts` 作为兼容性适配器，确保现有代码无需修改。

## 实施计划

### 第一阶段：基础架构搭建
1. ✅ 创建基础类型定义 (`types/base.ts`)
2. ✅ 实现BaseApi基础类 (`base-api.ts`)
3. ✅ 创建系统管理API (`system-api.ts`)
4. 🔄 创建模块管理API (`module-api.ts`)
5. 📋 创建其他业务API类

### 第二阶段：数据转换层
1. 📋 实现系统数据转换器
2. 📋 实现模块数据转换器
3. 📋 实现其他转换器
4. 📋 统一错误处理机制

### 第三阶段：兼容性保证
1. 📋 更新unified-api.ts为适配器模式
2. 📋 确保所有现有API调用正常工作
3. 📋 添加弃用警告（可选）

### 第四阶段：测试和优化
1. 📋 编写单元测试
2. 📋 性能测试和优化
3. 📋 文档更新
4. 📋 代码审查

## 技术规范

### 命名约定
- 文件名：kebab-case (如 `system-api.ts`)
- 类名：PascalCase (如 `SystemApi`)
- 方法名：camelCase (如 `getSystemList`)
- 接口名：PascalCase + 描述性后缀 (如 `SystemEntity`, `SystemListParams`)

### 代码规范
- 严格的TypeScript类型检查
- 统一的错误处理机制
- 完整的JSDoc注释
- 遵循ESLint规则

### 代码风格规范
详细的代码风格规范请参考：[前端代码风格规范](../guides/coding-style.md)

该文档包含：
- **API架构设计规范**：分层架构原则、类型定义规范、错误处理规范
- **编码标准**：TypeScript规范、架构约束、代码模式
- **文件组织规范**：目录结构、文件命名、导入导出规范
- **代码质量保证**：代码检查、文档规范、测试规范
- **性能优化规范**：代码优化、网络优化、内存优化
- **安全规范**：数据安全、权限控制
- **版本控制规范**：提交规范、分支管理

### 参数归一化与返回一致性

为保证前后端协作稳定性与一致性，API 层在代理/转换层实施统一的入参归一化与返回结构约束。

#### 归一化策略
- 字段风格统一：`camelCase` → `snake_case` 在 Converter/代理层完成映射
- 路由与查询参数：遵循相同策略；分页/筛选等公共参数统一映射
- 页面/组件不重复映射：上层使用 `camelCase`，由 API 层承担格式转换职责

#### 覆盖范围
- 主域 API：`systemApi`、`moduleApi`、`apiManagementApi` 等均执行归一化
- 统一在 `src/api/converters/` 维护领域转换器，避免分散至视图或 Service 层

#### 统一返回结构
- 所有 API 方法返回 `ApiResponse<T>`，采用结果分支处理，不抛异常
- 返回结构示例：
  - 成功：`{ success: true, data: T, code?: string }`
  - 失败：`{ success: false, error: { code: string, message: string }, data?: undefined }`

#### 示例
```ts
// 页面使用 camelCase
await moduleApi.create({ systemId: 'sys-1', moduleName: '新模块' })

// API 层 Converter 负责映射到 snake_case
// create => POST /modules  payload: { system_id, module_name }

// 统一返回结构
const res = await systemApi.getList({ page: 1, pageSize: 20 })
if (res.success) {
  // res.data: SystemEntity[]
} else {
  console.warn(res.error?.message)
}
```

#### 注意事项
- 归一化只在 API 层进行；不要在组件、Store、Service 重复做大小写转换
- 新增接口必须提供对应 Converter；类型与转换保持同步更新
- 服务端新增字段需在 Converter 与类型入口中同步维护

> 设计文档参考：`docs/design/frontend-proxy-normalization-design.md`

> 命名与类型对齐规范：请参见 `../standards/api-naming-type-alignment.md`，与本章节配套执行。

### 性能考虑
- 懒加载API模块
- 请求缓存机制
- 批量操作优化
- 错误重试机制

## 风险评估

### 潜在风险
1. **兼容性问题**：新API可能与现有代码不兼容
2. **性能影响**：重构可能影响API响应性能
3. **开发周期**：重构需要一定的开发时间

### 风险缓解
1. **渐进式重构**：保持现有API不变，新增重构后的API
2. **充分测试**：确保所有功能正常工作
3. **回滚计划**：准备快速回滚机制

## 预期收益

### 开发效率提升
- 减少代码重复，提高开发效率
- 清晰的文件结构，便于定位和修改
- 统一的API模式，降低学习成本

### 代码质量提升
- 更好的类型安全性
- 更容易进行单元测试
- 更好的代码可读性和可维护性

### 长期维护
- 易于扩展新功能
- 便于重构和优化
- 降低维护成本

## 总结

本次API重构将显著提升前端代码的质量和可维护性，为后续功能开发奠定良好基础。通过分层架构和模块化设计，我们将构建一个更加健壮、可扩展的API层。

---

**状态图例：**
- ✅ 已完成
- 🔄 进行中  
- 📋 待开始

**最后更新：** 2024年1月
**负责人：** AI Assistant
**审核人：** 待定