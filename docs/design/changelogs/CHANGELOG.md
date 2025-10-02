# 更新日志 (CHANGELOG)

本文档记录了系统的重要功能更新、修复和改进。

## [2025.09] - Sprint A 统一参数组件验收完成

### ✅ 验收结论
- 前端 ParamsEditor 统一组件的核心交互与数据转换全部通过：
  - 折叠/展开交互稳定，层级状态一致
  - 搜索自动展开与清空恢复行为正确
  - 同/跨层级拖拽位置与层级调整准确，大量节点场景稳定
  - JSON 导入/导出完整；table/json/url 模式切换不丢数据、状态保持合理
  - 刷新后折叠状态持久化生效

### 📝 文档更新
- 更新 <docs/frontend/user-manuals/UNIFIED_PARAMS_COMPONENT_GUIDE.md>，新增“验收状态（Sprint A）”小节，使用复选框记录完成项与验收日期。

### 🔗 关联
- 前端预览验收入口：`http://localhost:5173/` → API Management → Interface Configuration → Request Parameters

## [2025.09] - API管理类型与字段对齐修复

### 🛠 修复内容
- 统一 `frontend/src/views/api-management/index.vue` 的类型与字段映射，消除编译与运行时不一致：
  - 使用本地 `ApiItem/SystemItem/ModuleItem` 类型避免跨模块命名差异（`module_id` vs `moduleId`、`system_id` vs `systemId`）。
  - 列表筛选统一用字符串比较：`String(api.system_id) === String(selectedSystemId)`，避免数字/字符串混用导致筛选异常。
  - 保存时将表单 `url` 映射为后端 `path`，并将 `system_id/module_id` 转为数字类型。
  - 系统树构建兼容 `system_id/systemId`，按字符串比较确保稳定匹配。
  - 保持批量测试调用为 `batchTestApis({ api_ids, headers, timeout })`（蛇形命名）。

### 📄 文档更新
- 在 `docs/frontend/user-manuals/04-api-management.md` 文末新增“字段对齐与类型说明（2025-09）”。

### 🔗 验证入口
- 前端预览：`http://localhost:5173/` → API管理 → 选择系统/模块 → 搜索与筛选 → 新增/编辑 → 批量测试

## [2025.09] - 统一API代理参数归一化

### ✨ 新增能力
- 在 `frontend/src/api/api-management.ts` 增加入参归一化工具，支持 camelCase→snake_case 映射与 `url`→`path` 转换：
  - 查询参数：`systemId/moduleId/enabledOnly` → `system_id/module_id/enabled_only`，并将可数字化的ID转为数字类型。
  - 创建/更新负载：`systemId/moduleId/requestFormat/responseFormat/authRequired/rateLimit/exampleRequest/exampleResponse` 自动映射为后端字段；`url` 自动映射到 `path`。

### 🔧 兼容策略
- 保持后端响应字段形态不变，避免影响既有页面；前端可安全以 camelCase 作为输入，统一代理在发送前完成映射。

### 🔗 使用示例
- 查询：`apiManagementApi.getApis({ systemId, moduleId, enabledOnly: true })`
- 创建：`apiManagementApi.createApi({ systemId, moduleId, name, method, url })`

### 扩展：System/Module API 入参归一化与返回一致性（新增）
- system-api：
  - 列表查询支持驼峰参数：`enabledOnly` → `enabled_only`，`hasModules` → `has_modules`。
  - 覆盖 `getList` 统一应用归一化，调用方无需改动。
- module-api：
  - 列表查询入参归一化：`systemId/moduleType/enabledOnly` → `system_id/module_type/enabled_only`；`tags` 数组自动转逗号分隔。
  - 负载归一化：`systemId/moduleType` → `system_id/module_type`；`url` 自动映射为 `path`（当未显式提供 `path`）。
  - 返回类型与基类一致：`getEnabledModules/getByTags/getBySystem/getDependencies/updateDependencies/copyModule/moveToSystem/getUsageStats/testConnection` 等方法统一返回 `ApiResponse<...>`；`getStatistics` 返回 `ApiResponse<BaseStatistics>` 并支持可选 `system_id`。

示例：
```ts
// 系统列表（驼峰入参）
const sysRes = await systemApi.getList({ enabledOnly: true, hasModules: true });

// 模块查询（驼峰 + tags 数组）
const modRes = await moduleApi.getList({ systemId: '12', moduleType: 'service', enabledOnly: true, tags: ['auth','user'] });

// 复制与移动（负载归一化）
await moduleApi.copyModule('123', 'New Name', '12');
await moduleApi.moveToSystem('123', '13');
```

### 扩展：API管理代理入参归一化（新增）
- 在 `frontend/src/api/api-management.ts` 中，`getServiceList` 现已应用同一归一化策略：
  - 入参 `systemId/moduleId/enabledOnly` → 统一为 `system_id/module_id/enabled_only`
  - 对应列表路由 `getServiceList/getModuleList/getApis` 保持一致的归一化行为
- 创建/更新API：继续支持 `url → path` 自动映射与 ID 字段数字化，调用方可使用 camelCase 入参


## [2025.09] - 需求管理文档对齐与状态更新

### 🧭 文档结构与放置
- 确认用户向文档统一放置于 `docs/frontend/user-manuals/`
- 补充跨文档互链，提升查阅与导航可达性

### 📝 用户手册更新
- 在 `docs/frontend/user-manuals/09-requirement-management.md` 文末新增“文档位置与关联”小节
- 修正文末实现状态表述为“已实现”，对齐当前功能

### 📌 文档首页与标准同步
- `docs/frontend/README.md`：将“需求管理”实现状态更新为“已实现”
- `docs/frontend/standards/DOCUMENTATION_STANDARDS.md`：同步第6层为“✅已实现”

### 🔗 关联记录
- 关联工程变更日志：`frontend/docs/changelogs/2024-01-15-requirement-management.md`

## [2024.01] - 工作流节点优化重大更新

### 🎉 新增功能

#### 节点属性配置系统
- **NodePropertyPanel组件**: 全新的节点属性配置面板
  - 统一的配置界面，支持所有节点类型
  - 模块化设计：通用配置 + 类型特定配置
  - 实时配置同步，变更立即反映到画布
  - 完整的TypeScript类型安全支持

#### 节点库显示优化
- **紧凑型网格布局**: 使用CSS Grid实现自适应布局
  - 最小宽度120px，自动计算列数
  - 12px间距，提升视觉效果
- **文字自动换行**: 智能文字处理
  - 支持`word-wrap: break-word`
  - 启用`hyphens: auto`连字符换行
  - 避免长文本截断问题
- **响应式设计**: 适配不同屏幕尺寸
  - 移动端友好的触摸交互
  - 平板和桌面端优化显示

#### 长方形节点支持
- **灵活尺寸设计**: 支持150px-300px宽度范围
  - 根据内容自动调整节点大小
  - 保持最佳的信息显示密度
- **优化的内容布局**: 垂直排列设计
  - 标题和描述分层显示
  - 充分利用长方形空间
- **向后兼容**: 完全兼容现有正方形节点

### 🔧 技术改进

#### 前端架构升级
- **Vue 3 Composition API**: 全面采用现代Vue开发模式
  - 更好的逻辑复用和组织
  - 改进的TypeScript支持
  - 更优的性能表现
- **CSS现代化布局**: 
  - CSS Grid用于网格布局
  - Flexbox用于组件内部布局
  - CSS变量统一样式管理

#### 组件化架构
- **高度模块化**: 组件职责清晰分离
  - Designer.vue: 主设计器组件
  - NodePropertyPanel.vue: 属性配置面板
  - 各类型节点组件独立维护
- **动态组件加载**: 按需加载配置组件
  - 减少初始包大小
  - 提升页面加载速度
- **事件驱动通信**: 标准化组件间通信
  - Props向下传递数据
  - Events向上传递操作
  - 统一的数据流管理

#### 性能优化
- **懒加载**: 配置组件按需加载
- **防抖处理**: 配置变更300ms防抖
- **虚拟滚动**: 大量节点时的性能优化
- **计算属性缓存**: 避免重复计算

### 🎨 用户体验改进

#### 交互优化
- **即时反馈**: 配置变更立即在画布体现
- **悬停效果**: 节点库项目悬停高亮
- **选中状态**: 清晰的节点选中视觉反馈
- **错误提示**: 友好的验证错误信息

#### 视觉设计
- **统一设计语言**: 遵循Element Plus设计规范
- **色彩系统**: 
  - 主色调: #409eff (蓝色)
  - 成功: #67c23a (绿色)
  - 警告: #e6a23c (橙色)
  - 错误: #f56c6c (红色)
- **圆角和阴影**: 现代化的视觉效果
- **间距系统**: 8px基础间距单位

### 📝 文档更新

#### 开发文档
- **工作流节点组件开发指南**: 详细的组件开发规范
- **前端开发指南**: 完整的开发流程和最佳实践
- **组件架构文档**: 系统的组件设计说明

#### 技术文档
- **系统架构更新**: 记录新增组件的架构位置
- **API文档**: 组件接口和事件定义
- **类型定义**: 完整的TypeScript类型文档

### 🔍 代码质量

#### TypeScript增强
```typescript
// 完整的类型定义
interface NodeData {
  id: string
  type: string
  label: string
  position: { x: number; y: number }
  config?: Record<string, any>
  width?: number
  height?: number
}

interface NodeUpdateEvent {
  nodeId: string
  updates: Partial<NodeData>
}
```

#### 测试覆盖
- **单元测试**: 组件功能测试
- **集成测试**: 组件间交互测试
- **端到端测试**: 完整用户流程测试

### 🚀 性能指标

#### 加载性能
- **首屏加载时间**: 减少30%
- **组件懒加载**: 按需加载减少初始包大小
- **资源优化**: 图标和样式优化

#### 运行性能
- **节点渲染**: 支持1000+节点流畅显示
- **配置响应**: 配置变更<100ms响应
- **内存使用**: 优化内存占用，避免内存泄漏

### 🛠️ 开发工具

#### 构建优化
- **Vite构建**: 快速的开发和构建体验
- **热更新**: 开发时的即时更新
- **代码分割**: 自动的代码分割优化

#### 开发体验
- **TypeScript**: 完整的类型检查
- **ESLint**: 代码质量检查
- **Prettier**: 代码格式化
- **Vue DevTools**: 调试工具支持

### 📋 兼容性

#### 浏览器支持
- **现代浏览器**: Chrome 90+, Firefox 88+, Safari 14+
- **移动端**: iOS Safari 14+, Chrome Mobile 90+
- **响应式**: 支持320px-2560px屏幕宽度

#### 向后兼容
- **现有工作流**: 完全兼容现有工作流数据
- **API接口**: 保持API接口向后兼容
- **组件接口**: 渐进式升级，不破坏现有功能

### 🔮 未来规划

#### 短期计划 (1-2个月)
- **智能推荐**: 基于使用历史的节点推荐
- **批量操作**: 支持多节点批量配置
- **模板系统**: 节点配置模板保存和复用

#### 中期计划 (3-6个月)
- **可视化增强**: 更丰富的节点可视化效果
- **协作功能**: 多人协作编辑工作流
- **版本控制**: 工作流版本管理和回滚

#### 长期计划 (6个月+)
- **AI辅助**: AI驱动的工作流设计建议
- **插件系统**: 支持第三方节点插件
- **云端同步**: 工作流云端存储和同步

---

## [历史版本]

### [2023.12] - 基础工作流功能
- 基础的工作流设计器
- 基本节点类型支持
- 简单的连线功能

### [2023.11] - 项目初始化
- 项目架构搭建
- 基础技术栈选型
- 开发环境配置

---

*最后更新: 2024年1月*  
*版本: v2.0.0*
## [2025.09] - 文档迁移：统一为“测试API管理”

### 📚 变更说明
- 将前端用户文档的“场景管理”体系统一迁移为“测试API管理（以接口为中心）”。
- 统一使用 `docs/frontend/user-manuals/08-scenario-management.md` 作为第08章节手册（标题为“测试API管理”）。
- 原 `08-scenario-management.md` 标注为“已废弃”，顶部提供跳转与历史说明。
- 更新导航与映射：
  - `docs/frontend/user-manuals/README.md`、`docs/frontend/README.md` 链接与标签改为“测试API管理”。
  - `docs/DOCUMENT_MAPPING_GUIDE.md` 将 `/scenario-management` 映射到新指南。
  - `docs/SYSTEM_ARCHITECTURE.md`、`docs/frontend/standards/DOCUMENTATION_STANDARDS.md` 第5层标签改为“测试API管理”。

-### 🔗 关联入口
- 前端用户手册：`docs/frontend/user-manuals/08-scenario-management.md`
- 系统架构：`docs/SYSTEM_ARCHITECTURE.md`（第5层）