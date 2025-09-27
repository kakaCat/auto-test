# 系统架构和操作逻辑文档

## 概述

本文档详细说明了自动化测试平台的系统架构、前端组件布局、后端API接口以及各模块的操作逻辑。平台主要包含三个核心管理模块：系统管理、API管理和页面管理。

## 技术架构

### 前端架构
- **框架**: Vue 3 + TypeScript + Vite
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由管理**: Vue Router
- **HTTP客户端**: Axios

### 后端架构
- **框架**: FastAPI + Python
- **数据库**: SQLite/PostgreSQL
- **ORM**: SQLAlchemy
- **API文档**: Swagger/OpenAPI
- **架构模式**: 分层架构（Controller → Service → Repository）

## 1. 系统管理模块

### 1.1 前端组件结构

#### 主页面组件: `service-management/index.vue`

**布局结构:**
```
┌─────────────────────────────────────────────────────────┐
│ 页面头部 (Header)                                        │
│ ├─ 错误提示 (ErrorAlert)                                │
│ ├─ 标题: "系统管理"                                      │
│ ├─ 操作按钮组                                           │
│ │  ├─ 新增系统 (createSystem)                           │
│ │  └─ 刷新 (refreshData)                               │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ 主内容区域 (Main Content)                               │
│ ┌─────────────┬─────────────────────────────────────────┐ │
│ │ 左侧面板    │ 右侧面板                                │ │
│ │ (Left Panel)│ (Right Panel)                          │ │
│ │             │                                        │ │
│ │ 系统类型筛选 │ 系统/模块详细信息                       │ │
│ │ ├─ 全部     │ ├─ 基本信息卡片                        │ │
│ │ ├─ 后端系统 │ ├─ 统计信息卡片                        │ │
│ │ └─ 前端系统 │ ├─ 模块列表                            │ │
│ │             │ └─ 操作按钮组                          │ │
│ │ SystemTree  │                                        │ │
│ │ 组件        │                                        │ │
│ └─────────────┴─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**核心组件:**
- **SystemTree**: 系统树形导航组件
- **ErrorAlert**: 错误提示组件
- **系统详情面板**: 显示选中系统的详细信息

### 1.2 操作逻辑

#### 数据流程:
1. **初始化**: 页面加载时调用 `loadEnabledSystems()` 获取启用的系统列表
2. **系统筛选**: 通过类型筛选器切换显示不同分类的系统
3. **系统选择**: 点击系统树节点触发 `handleSystemSelect()` 显示系统详情
4. **系统操作**: 支持新增、编辑、删除、启用/禁用系统

#### 关键方法:
- `loadEnabledSystems()`: 加载启用的系统列表
- `handleSystemSelect(system)`: 处理系统选择事件
- `createSystem()`: 创建新系统
- `refreshData()`: 刷新数据

### 1.3 后端API接口

#### 系统管理API (`/api/systems/v1/`)

| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/api/systems/v1/` | 获取系统列表 | category, enabled, page, size |
| GET | `/api/systems/v1/enabled` | 获取启用系统列表 | - |
| GET | `/api/systems/v1/enabled/{category}` | 按分类获取启用系统 | category: backend/frontend |
| GET | `/api/systems/v1/{system_id}` | 获取系统详情 | system_id |
| POST | `/api/systems/v1/` | 创建系统 | SystemCreate对象 |
| PUT | `/api/systems/v1/{system_id}` | 更新系统 | system_id, SystemUpdate对象 |
| DELETE | `/api/systems/v1/{system_id}` | 删除系统 | system_id |
| PATCH | `/api/systems/v1/{system_id}/status` | 切换启用状态 | system_id, enabled |

#### 数据模型:
```python
class SystemCreate:
    name: str
    description: str
    category: str  # 'backend' | 'frontend'
    base_url: str
    enabled: bool = True
    tags: List[str] = []
```

## 2. API管理模块

### 2.1 前端组件结构

#### 主页面组件: `api-management/index.vue`

**布局结构:**
```
┌─────────────────────────────────────────────────────────┐
│ 页面头部 (Header)                                        │
│ ├─ 标题: "API管理"                                       │
│ ├─ 描述: "管理和维护系统API接口"                          │
│ ├─ 操作按钮组                                           │
│ │  ├─ 新增API (showCreateDialog)                        │
│ │  ├─ 导入API (showImportDialog)                        │
│ │  └─ 导出API (exportApis)                             │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ 主内容区域 (Main Content)                               │
│ ┌─────────────┬─────────────────────────────────────────┐ │
│ │ 左侧面板    │ 右侧面板                                │ │
│ │ (Left Panel)│ (Right Panel)                          │ │
│ │             │                                        │ │
│ │ SystemTree  │ API管理面板                            │ │
│ │ 组件        │ ├─ 搜索筛选区域                        │ │
│ │             │ │  ├─ 关键词搜索                       │ │
│ │             │ │  ├─ HTTP方法筛选                     │ │
│ │             │ │  └─ 状态筛选                         │ │
│ │             │ ├─ 批量操作区域                        │ │
│ │             │ │  ├─ 全选/反选                        │ │
│ │             │ │  ├─ 批量启用/禁用                    │ │
│ │             │ │  └─ 批量删除                         │ │
│ │             │ └─ API列表展示                         │ │
│ │             │    ├─ API卡片列表                      │ │
│ │             │    └─ 分页组件                         │ │
│ └─────────────┴─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**核心组件:**
- **SystemTree**: 系统树形导航（复用）
- **ApiFormDialog**: API创建/编辑对话框
- **ApiCard**: API信息卡片组件
- **SearchFilter**: 搜索筛选组件

### 2.2 操作逻辑

#### 数据流程:
1. **初始化**: 页面加载时调用 `loadSystems()` 和 `loadApis()` 获取数据
2. **系统选择**: 选择系统后筛选显示该系统的API列表
3. **API筛选**: 支持按关键词、HTTP方法、状态等条件筛选
4. **API操作**: 支持创建、编辑、删除、批量操作API

#### 关键方法:
- `loadSystems()`: 加载系统列表
- `loadApis()`: 加载API列表
- `handleSystemSelect(system)`: 处理系统选择
- `handleSearch()`: 处理搜索筛选
- `showCreateDialog()`: 显示创建API对话框
- `batchOperation()`: 批量操作API

### 2.3 后端API接口

#### API接口管理API (`/api/api-interfaces/v1/`)

| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/api/api-interfaces/v1/` | 获取API列表 | system_id, module_id, keyword, method, status |
| GET | `/api/api-interfaces/v1/{api_id}` | 获取API详情 | api_id |
| POST | `/api/api-interfaces/v1/` | 创建API | ApiInterfaceCreate对象 |
| PUT | `/api/api-interfaces/v1/{api_id}` | 更新API | api_id, ApiInterfaceUpdate对象 |
| DELETE | `/api/api-interfaces/v1/{api_id}` | 删除API | api_id |
| POST | `/api/api-interfaces/v1/search` | 搜索API | ApiInterfaceQueryRequest对象 |
| GET | `/api/api-interfaces/v1/stats/summary` | 获取API统计 | - |
| POST | `/api/api-interfaces/v1/batch/status` | 批量更新状态 | ApiInterfaceBatchRequest对象 |
| POST | `/api/api-interfaces/v1/batch/delete` | 批量删除 | api_ids列表 |

#### 数据模型:
```python
class ApiInterfaceCreate:
    system_id: int
    module_id: Optional[int]
    name: str
    description: str
    url: str
    method: str  # GET, POST, PUT, DELETE, etc.
    enabled: bool = True
    tags: List[str] = []
```

## 3. 页面管理模块

### 3.1 前端组件结构

#### 主页面组件: `page-management/index.vue`

**布局结构:**
```
┌─────────────────────────────────────────────────────────┐
│ 页面头部 (Header)                                        │
│ ├─ 标题: "页面管理"                                       │
│ ├─ 描述: "管理和维护系统页面"                             │
│ ├─ 操作按钮组                                           │
│ │  ├─ 新增页面 (showCreateDialog)                       │
│ │  ├─ 导入页面 (showImportDialog)                       │
│ │  └─ 导出页面 (exportPages)                           │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ 主内容区域 (Main Content)                               │
│ ┌─────────────┬─────────────────────────────────────────┐ │
│ │ 左侧面板    │ 右侧面板                                │ │
│ │ (Left Panel)│ (Right Panel)                          │ │
│ │             │                                        │ │
│ │ SystemTree  │ 页面管理主面板                         │ │
│ │ 组件        │ ├─ 搜索筛选区域                        │ │
│ │             │ │  ├─ 关键词搜索                       │ │
│ │             │ │  ├─ 页面类型筛选                     │ │
│ │             │ │  └─ 状态筛选                         │ │
│ │             │ ├─ 页面列表展示                        │ │
│ │             │ │  ├─ 页面卡片                         │ │
│ │             │ │  │  ├─ 页面名称                      │ │
│ │             │ │  │  ├─ 页面类型                      │ │
│ │             │ │  │  ├─ 状态标识                      │ │
│ │             │ │  │  ├─ 描述信息                      │ │
│ │             │ │  │  ├─ 路由信息                      │ │
│ │             │ │  │  └─ API数量                       │ │
│ │             │ │  └─ 操作按钮                         │ │
│ │             │ └─ 页面API关联管理                     │ │
│ │             │    ├─ API关联列表                      │ │
│ │             │    └─ 添加/移除API关联                 │ │
│ └─────────────┴─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**核心组件:**
- **SystemTree**: 系统树形导航（复用）
- **PageFormDialog**: 页面创建/编辑对话框
- **PageCard**: 页面信息卡片组件
- **PageApiManager**: 页面API关联管理组件

### 3.2 操作逻辑

#### 数据流程:
1. **初始化**: 页面加载时调用 `loadSystems()` 和 `loadPages()` 获取数据
2. **系统选择**: 选择系统后筛选显示该系统的页面列表
3. **页面筛选**: 支持按关键词、页面类型、状态等条件筛选
4. **页面操作**: 支持创建、编辑、删除页面
5. **API关联**: 管理页面与API的关联关系

#### 关键方法:
- `loadSystems()`: 加载系统列表
- `loadPages()`: 加载页面列表
- `handleSystemSelect(system)`: 处理系统选择
- `handleSearch()`: 处理搜索筛选
- `showCreateDialog()`: 显示创建页面对话框
- `managePageApis(page)`: 管理页面API关联

### 3.3 后端API接口

#### 页面管理API (`/api/pages/v1/`)

| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/api/pages/v1/` | 获取页面列表 | system_id |
| GET | `/api/pages/v1/{page_id}` | 获取页面详情 | page_id |
| POST | `/api/pages/v1/` | 创建页面 | PageCreate对象 |
| PUT | `/api/pages/v1/{page_id}` | 更新页面 | page_id, PageUpdate对象 |
| DELETE | `/api/pages/v1/{page_id}` | 删除页面 | page_id |
| POST | `/api/pages/v1/search` | 搜索页面 | PageQueryRequest对象 |
| GET | `/api/pages/v1/{page_id}/apis` | 获取页面API列表 | page_id |
| POST | `/api/pages/v1/{page_id}/apis` | 添加页面API关联 | page_id, PageApiCreateRequest对象 |
| PUT | `/page-apis/v1/{relation_id}` | 更新页面API关联 | relation_id, PageApiUpdate对象 |
| DELETE | `/page-apis/v1/{relation_id}` | 删除页面API关联 | relation_id |
| POST | `/api/pages/v1/{page_id}/apis/batch` | 批量管理页面API关联 | page_id, PageApiBatchRequest对象 |

#### 数据模型:
```python
class PageCreate:
    system_id: int
    name: str
    description: str
    page_type: str  # 页面类型
    route: str      # 路由路径
    status: str = "active"
    
class PageApiCreateRequest:
    api_interface_id: int
    description: Optional[str]
    is_required: bool = True
```

## 4. 共享组件

### 4.1 SystemTree 组件

**功能**: 系统树形导航组件，在所有管理页面中复用

**特性**:
- 支持系统分类筛选（全部、后端系统、前端系统）
- 树形结构显示系统和模块层级关系
- 支持系统选择和高亮显示
- 实时更新系统状态

**API调用**:
- `getEnabledListByCategory(category)`: 获取指定分类的启用系统列表

### 4.2 前端API调用层

#### 统一API模块 (`unified-api.ts`)

**核心特性**:
- 统一的API基础配置和请求封装
- 支持多种HTTP方法（GET, POST, PUT, DELETE, PATCH）
- 统一的错误处理和响应格式
- 兼容性适配器支持旧版API调用

**主要API模块**:
- `unifiedSystemApi`: 系统管理API
- `unifiedModuleApi`: 模块管理API  
- `unifiedApiManagementApi`: API管理API
- `unifiedCategoryApi`: 分类标签管理API

## 5. 数据流和状态管理

### 5.1 前端状态管理

**全局状态**:
- 当前选中的系统
- 用户权限信息
- 系统配置信息

**页面级状态**:
- 列表数据（系统、API、页面）
- 筛选条件
- 分页信息
- 加载状态

### 5.2 数据同步机制

**实时更新**:
- 系统状态变更时自动刷新相关列表
- 支持手动刷新数据
- 错误状态的自动恢复

**缓存策略**:
- 系统列表缓存5分钟
- API列表根据筛选条件缓存
- 页面数据实时获取

## 6. 错误处理和用户体验

### 6.1 错误处理机制

**前端错误处理**:
- 统一的错误提示组件
- 网络错误自动重试
- 表单验证和错误提示

**后端错误处理**:
- 统一的异常处理中间件
- 详细的错误信息返回
- 日志记录和监控

### 6.2 用户体验优化

**加载状态**:
- 骨架屏加载效果
- 按钮加载状态
- 数据加载进度提示

**交互反馈**:
- 操作成功/失败提示
- 确认对话框
- 批量操作进度显示

## 7. 安全和权限

### 7.1 权限控制

**前端权限**:
- 路由级权限控制
- 组件级权限显示
- 操作按钮权限控制

**后端权限**:
- API接口权限验证
- 数据访问权限控制
- 操作日志记录

### 7.2 数据安全

**输入验证**:
- 前端表单验证
- 后端参数验证
- SQL注入防护

**数据传输**:
- HTTPS加密传输
- 敏感数据脱敏
- 请求签名验证

## 8. 性能优化

### 8.1 前端性能

**代码优化**:
- 组件懒加载
- 路由懒加载
- 图片懒加载

**渲染优化**:
- 虚拟滚动
- 防抖节流
- 组件缓存

### 8.2 后端性能

**数据库优化**:
- 索引优化
- 查询优化
- 连接池管理

**API优化**:
- 响应缓存
- 分页查询
- 批量操作

## 9. 工作流设计器架构

### 9.1 工作流设计器概述

工作流设计器是AI自动化测试系统的核心功能模块，位于6层架构体系的第4层（调用流程层），提供可视化的工作流创建和编辑能力。

**核心功能**:
- 可视化节点拖拽和连接
- 多种节点类型支持（开始、API调用、数据转换、结束）
- 智能连接验证机制
- 实时工作流预览和执行

### 9.2 节点连接架构

#### 9.2.1 连接关系设计

**连接关系矩阵**:
| 源节点类型 | 目标节点类型 | 连接关系 | 验证规则 |
|-----------|-------------|----------|----------|
| 开始节点 | API调用节点 | 1对N | 开始节点可连接多个API节点 |
| 开始节点 | 数据转换节点 | 1对N | 开始节点可连接多个数据转换节点 |
| API调用节点 | 结束节点 | 1对1 | API节点只能连接一个结束节点 |
| API调用节点 | 数据转换节点 | 1对1 | API节点只能连接一个数据转换节点 |
| 数据转换节点 | 结束节点 | 1对1 | 数据转换节点只能连接一个结束节点 |

#### 9.2.2 连接验证逻辑

**验证层级**:
1. **基础验证**: 节点自连接检测、重复连接检测
2. **类型验证**: 端口类型匹配、连接关系验证
3. **业务验证**: 循环依赖检测、工作流完整性验证

**验证实现**:
```typescript
// 连接验证核心函数
export function isValidConnection(
  sourceNode: Node,
  targetNode: Node,
  sourceHandle: string,
  targetHandle: string,
  existingEdges: Edge[]
): boolean {
  // 1. 基础验证
  if (sourceNode.id === targetNode.id) return false;
  
  // 2. 类型验证
  if (!isValidNodeConnection(sourceNode.type, targetNode.type)) return false;
  
  // 3. 重复连接检测
  const connectionExists = existingEdges.some(edge =>
    edge.source === sourceNode.id && 
    edge.target === targetNode.id &&
    edge.sourceHandle === sourceHandle &&
    edge.targetHandle === targetHandle
  );
  
  return !connectionExists;
}
```

### 9.3 节点组件架构

#### 9.3.1 节点组件设计原则

**架构原则**:
- **单一职责**: 每个节点类型有明确的功能定位
- **类型安全**: 通过TypeScript类型系统确保连接的正确性
- **可扩展性**: 支持新节点类型的快速添加
- **性能优化**: 最小化渲染开销和内存占用

#### 9.3.2 端口配置规范

**端口类型定义**:
```typescript
interface NodePortConfig {
  input: {
    count: number;
    type: 'data' | 'trigger';
    position: Position;
  };
  output: {
    count: number;
    type: 'data' | 'trigger';
    position: Position;
  };
}
```

**节点类型配置**:
- **开始节点**: 无输入端口，1个输出端口（trigger类型）
- **API调用节点**: 1个输入端口，1个输出端口（data类型）
- **数据转换节点**: 1个输入端口，1个输出端口（data类型）
- **结束节点**: 1个输入端口，无输出端口

### 9.4 性能优化

#### 9.4.1 连接验证性能

**优化策略**:
- **缓存机制**: 缓存节点类型兼容性矩阵
- **早期返回**: 在验证失败时立即返回，避免不必要的计算
- **批量验证**: 支持批量连接的一次性验证

**性能指标**:
- 单次连接验证时间: < 3ms
- 复杂工作流验证时间: < 50ms
- 内存占用优化: 减少30%的组件渲染开销

#### 9.4.2 渲染优化

**优化技术**:
- **虚拟化**: 大型工作流的节点虚拟化渲染
- **懒加载**: 节点组件的按需加载
- **状态管理**: 最小化不必要的重新渲染

### 9.5 错误处理和用户体验

#### 9.5.1 连接错误处理

**错误类型**:
- **无效连接**: 不符合连接规则的操作
- **循环依赖**: 工作流中存在循环引用
- **孤立节点**: 未连接的节点检测

**用户反馈**:
- **实时提示**: 连接操作时的即时反馈
- **视觉指示**: 无效连接的视觉警告
- **错误说明**: 详细的错误原因和解决建议

#### 9.5.2 用户体验优化

**交互优化**:
- **智能连接**: 自动识别可连接的目标节点
- **连接预览**: 连接操作的实时预览效果
- **快捷操作**: 键盘快捷键支持

**视觉优化**:
- **连接状态**: 不同连接状态的视觉区分
- **节点高亮**: 可连接节点的智能高亮
- **动画效果**: 流畅的连接动画和状态转换

## 总结

本系统采用现代化的前后端分离架构，通过统一的API接口和组件化的前端设计，实现了系统、API和页面的完整生命周期管理。工作流设计器作为核心功能模块，提供了强大的可视化编排能力和智能的连接验证机制。

关键特性：
- **模块化设计**: 系统、API、页面、工作流四大核心模块独立且关联
- **统一的用户界面**: 一致的布局和交互体验
- **完整的CRUD操作**: 支持创建、读取、更新、删除等完整操作
- **灵活的筛选和搜索**: 多维度的数据筛选和搜索功能
- **批量操作支持**: 提高操作效率的批量处理功能
- **实时数据同步**: 确保数据的一致性和实时性
- **智能工作流编排**: 可视化的工作流设计和执行能力
- **完善的连接验证**: 多层级的连接验证和错误处理机制