# 页面管理页面交互文档

## 页面概述

页面管理是自动化测试平台的核心功能模块，用于管理测试页面和页面与API的关联关系。该页面提供了完整的页面生命周期管理，包括页面创建、编辑、删除、API关联管理、页面导入导出等功能。

## 界面布局

### 整体结构
```
┌─────────────────────────────────────────────────────────────┐
│                        页面头部                              │
│  [页面管理] [描述文本] [新增页面] [导入] [导出] [批量操作]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────────────────────────────┐   │
│  │             │  │                                     │   │
│  │   左侧导航   │  │          右侧页面管理面板            │   │
│  │  SystemTree │  │                                     │   │
│  │             │  │  ┌─────────────────────────────┐    │   │
│  │   系统列表   │  │  │        搜索筛选区域          │    │   │
│  │   模块分类   │  │  └─────────────────────────────┘    │   │
│  │             │  │                                     │   │
│  │             │  │  ┌─────────────────────────────┐    │   │
│  │             │  │  │        页面列表展示          │    │   │
│  │             │  │  │                             │    │   │
│  │             │  │  │  [页面卡片1] [页面卡片2]    │    │   │
│  │             │  │  │  [页面卡片3] [页面卡片4]    │    │   │
│  │             │  │  │                             │    │   │
│  │             │  │  └─────────────────────────────┘    │   │
│  │             │  │                                     │   │
│  │             │  │  ┌─────────────────────────────┐    │   │
│  │             │  │  │        分页控件             │    │   │
│  │             │  │  └─────────────────────────────┘    │   │
│  └─────────────┘  └─────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 头部区域
- **页面标题**: "页面管理"
- **描述文本**: "管理测试页面和API关联关系"
- **操作按钮组**:
  - `新增页面`: 主要操作按钮，蓝色背景
  - `导入页面`: 次要操作按钮，支持批量导入
  - `导出页面`: 次要操作按钮，支持数据导出
  - `批量操作`: 下拉菜单，包含批量删除、批量更新状态等

### 左侧导航面板

#### 系统和模块树形结构 (SystemTree组件)

左侧导航面板采用SystemTree组件，提供完整的系统和模块管理功能：

**核心功能特性：**
- **层级展示**：以树形结构展示前端系统和模块的层级关系
- **全部节点**：顶层"全部"节点，用于查看所有页面
- **系统节点**：展示各个前端系统，点击可筛选该系统下的页面
- **模块节点**：展示系统下的模块，点击可筛选该模块下的页面

**筛选功能：**
- **系统筛选**：选择系统节点时，右侧页面列表显示该系统的所有页面
- **模块筛选**：选择模块节点时，右侧页面列表显示该模块的所有页面
- **筛选状态**：导航面板显示当前选中的系统/模块状态
- **清除筛选**：支持清除当前筛选条件，显示所有页面

**交互功能：**
- **节点选择**：点击节点可筛选对应的页面列表
  - 点击系统节点：筛选该系统下所有页面
  - 点击模块节点：筛选该系统和模块对应的页面
- **展开/收起**：支持一键展开/收起所有节点
  - 点击系统节点展开或收起模块列表
- **搜索功能**：支持按系统名称和模块名称进行实时搜索
- **刷新功能**：支持重新加载系统和模块数据
- **多选支持**：支持选择多个系统/模块进行批量操作
- **右键菜单**：提供编辑、删除、添加子模块等操作

**数据来源：**
- 系统数据：通过 `apiProxy.system.getEnabledListByCategory('frontend')` 获取前端系统列表
- 模块数据：通过 `apiProxy.module.getEnabledList()` 获取启用的模块列表
- 数据关联：模块通过 `system_id` 字段关联到对应系统

**状态管理：**
- `systemTreeData`：树形结构数据
- `selectedSystemId`：当前选中的系统ID
- `selectedPageId`：当前选中的页面ID（用于模块节点选择）
- 支持节点点击事件和刷新事件处理

### 右侧页面管理面板

#### 搜索筛选区域
```
┌─────────────────────────────────────────────────────────┐
│ [搜索框: 输入页面名称或路由]  [搜索按钮]  [重置按钮]      │
├─────────────────────────────────────────────────────────┤
│ 筛选条件:                                               │
│ [页面类型▼] [状态▼] [执行类型▼] [创建时间▼] [更多筛选▼] │
└─────────────────────────────────────────────────────────┘
```

#### 页面列表展示
页面以表格形式展示，包含以下列：
```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 页面列表表格                                                                                 │
├──┬─────────────┬────────┬─────────────────┬──────────┬─────────────┬────────┬─────────────────┤
│☐ │ 页面名称    │ 类型   │ 路由            │ 状态     │ 系统/模块   │ API数量│ 操作            │
├──┼─────────────┼────────┼─────────────────┼──────────┼─────────────┼────────┼─────────────────┤
│☐ │ 用户登录页  │ 登录页 │ /login          │ 启用     │ 用户系统    │ 3      │ [编辑][API管理] │
│☐ │ 用户列表页  │ 列表页 │ /users          │ 启用     │ 用户系统    │ 5      │ [编辑][API管理] │
│☐ │ 订单详情页  │ 详情页 │ /order/detail   │ 禁用     │ 订单系统    │ 8      │ [编辑][API管理] │
│☐ │ 商品管理页  │ 管理页 │ /products       │ 启用     │ 商品系统    │ 12     │ [编辑][API管理] │
│☐ │ 支付页面    │ 功能页 │ /payment        │ 开发中   │ 支付系统    │ 6      │ [编辑][API管理] │
└──┴─────────────┴────────┴─────────────────┴──────────┴─────────────┴────────┴─────────────────┘

表格列说明：
- 复选框：支持多选进行批量操作
- 页面名称：页面的业务名称，可点击查看详情
- 类型：页面类型（登录页、列表页、详情页、管理页等）
- 路由：页面的访问路径
- 状态：启用、禁用、开发中等状态标签
- 系统/模块：所属系统和模块信息
- API数量：该页面关联的API接口数量
- 操作：编辑、删除、API管理、复制等操作按钮
```

## 交互流程

### 页面初始化
1. **加载系统树**: 获取系统列表并构建树形结构
2. **加载页面列表**: 获取默认的页面列表数据
3. **初始化筛选条件**: 设置默认筛选参数
4. **状态同步**: 同步URL参数和页面状态

### 页面搜索与筛选
1. **实时搜索**:
   - 用户输入关键词（页面名称或路由）
   - 300ms防抖延迟
   - 自动触发搜索请求
   - 更新页面列表

2. **条件筛选**:
   - 选择页面类型（登录页、列表页、详情页等）
   - 选择状态（启用、禁用、开发中等）
   - 选择执行类型（手动、自动化、混合）
   - 选择时间范围
   - 组合筛选条件

3. **筛选重置**:
   - 点击重置按钮
   - 清空所有筛选条件
   - 恢复默认列表

### 页面操作流程

#### 新增页面
1. **触发操作**: 点击"新增页面"按钮
2. **打开表单**: 弹出页面创建对话框
3. **表单填写**:
   - 基本信息：页面名称、路由、页面类型
   - 详细信息：描述、所属系统、模块
   - 配置信息：执行类型、状态、标签
   - 元数据：页面元素、测试数据
4. **数据验证**: 实时验证表单数据
5. **提交保存**: 发送创建请求
6. **结果反馈**: 显示成功/失败消息
7. **列表更新**: 刷新页面列表

#### 编辑页面
1. **触发操作**: 点击页面卡片的"编辑"按钮
2. **加载数据**: 获取页面详细信息
3. **填充表单**: 预填充现有数据
4. **修改数据**: 用户编辑相关字段
5. **保存更新**: 提交修改请求
6. **状态更新**: 更新列表中的页面信息

#### 删除页面
1. **触发操作**: 点击"删除"按钮
2. **依赖检查**: 检查页面是否有关联的API或测试用例
3. **确认对话框**: 显示删除确认提示和影响范围
4. **执行删除**: 发送删除请求
5. **级联处理**: 处理关联数据的删除或解绑
6. **列表更新**: 从列表中移除已删除项
7. **消息提示**: 显示删除成功消息

### API关联管理

#### 查看页面API
1. **触发操作**: 点击"API管理"按钮
2. **打开API面板**: 显示页面API关联管理界面
3. **API列表展示**: 显示当前页面关联的所有API
4. **API信息显示**: 展示API名称、方法、路径、状态等

#### 添加API关联
1. **点击添加**: 点击"添加API"按钮
2. **API选择器**: 打开API选择对话框
3. **筛选搜索**: 通过系统、模块、名称筛选API
4. **多选API**: 支持批量选择多个API
5. **关联配置**: 设置API在页面中的作用和参数
6. **确认添加**: 建立页面与API的关联关系
7. **列表更新**: 刷新页面API列表

#### 编辑API关联
1. **选择API**: 点击已关联API的编辑按钮
2. **编辑配置**: 修改API在页面中的配置
3. **参数设置**: 调整API调用参数和响应处理
4. **保存更改**: 更新关联配置
5. **状态同步**: 同步API关联状态

#### 删除API关联
1. **选择API**: 点击要删除的API关联
2. **确认删除**: 显示删除确认对话框
3. **解除关联**: 删除页面与API的关联关系
4. **影响评估**: 提示删除对测试用例的影响
5. **列表更新**: 从关联列表中移除API

### 批量操作
1. **选择页面**: 勾选多个页面项目
2. **选择操作**: 从批量操作菜单选择
   - 批量删除页面
   - 批量更新状态
   - 批量修改分类
   - 批量导出数据
3. **确认执行**: 显示批量操作确认对话框
4. **执行操作**: 并行处理选中的页面
5. **进度显示**: 显示批量操作进度
6. **结果汇总**: 展示操作结果统计

### 导入导出功能

#### 导入页面
1. **选择文件**: 点击导入按钮，选择文件
2. **格式验证**: 验证文件格式（JSON、Excel等）
3. **数据预览**: 显示导入数据预览
4. **冲突处理**: 处理重复页面的策略选择
5. **关联处理**: 处理页面API关联的导入
6. **执行导入**: 批量创建页面和关联
7. **结果报告**: 显示导入成功/失败统计

#### 导出页面
1. **选择范围**: 选择导出的页面范围
2. **选择格式**: 选择导出格式（JSON、Excel、CSV）
3. **配置选项**: 设置导出字段和关联数据
4. **生成文件**: 创建导出文件
5. **下载文件**: 提供文件下载链接

## 响应式设计

### 桌面端 (>1200px)
- 左侧导航固定宽度 280px
- 右侧内容区域自适应
- 页面表格完整显示所有列
- 完整显示所有操作按钮
- API管理面板侧边栏显示

### 平板端 (768px-1200px)
- 左侧导航可折叠
- 页面表格隐藏部分次要列（如创建时间）
- 部分操作按钮收缩到下拉菜单
- API管理面板全屏显示

### 移动端 (<768px)
- 左侧导航抽屉式显示
- 页面表格转为卡片式布局
- 操作按钮简化为图标
- 搜索筛选区域垂直排列
- API管理面板全屏模态框

## 键盘快捷键

- `Ctrl/Cmd + N`: 新增页面
- `Ctrl/Cmd + F`: 聚焦搜索框
- `Ctrl/Cmd + R`: 刷新列表
- `Ctrl/Cmd + A`: 全选页面（批量操作模式）
- `Escape`: 关闭对话框或面板
- `Enter`: 确认操作
- `Tab`: 在表单字段间切换
- `Ctrl/Cmd + M`: 打开API管理面板

## 加载状态和反馈

### 加载状态
- **页面初始化**: 骨架屏显示
- **搜索加载**: 搜索框显示加载图标
- **页面操作**: 按钮显示加载状态
- **API关联加载**: API面板显示加载动画
- **批量操作**: 进度条显示

### 用户反馈
- **成功操作**: 绿色Toast消息
- **错误处理**: 红色错误提示
- **警告信息**: 橙色警告提示（如删除有依赖的页面）
- **信息提示**: 蓝色信息提示

### 空状态处理
- **无页面数据**: 显示空状态插画和引导
- **搜索无结果**: 提供搜索建议
- **无API关联**: 显示添加API的引导
- **网络错误**: 显示重试按钮

## 特殊交互场景

### API关联冲突处理
1. **冲突检测**: 检测API参数冲突或重复关联
2. **冲突提示**: 明确显示冲突原因和影响
3. **解决方案**: 提供冲突解决选项
4. **自动修复**: 支持自动修复简单冲突

### 页面依赖管理
1. **依赖检查**: 检查页面的测试用例依赖
2. **影响分析**: 分析删除或修改的影响范围
3. **依赖可视化**: 图形化显示页面依赖关系
4. **安全操作**: 提供安全的依赖解除方案

### 版本控制
1. **变更记录**: 记录页面的所有变更历史
2. **版本对比**: 支持不同版本的对比查看
3. **回滚功能**: 支持回滚到历史版本
4. **变更审核**: 重要变更需要审核确认

## 常见问题与解决方案

### 性能优化
- **虚拟表格**: 大量页面数据时使用虚拟表格
- **表格优化**: 固定表头、列宽自适应
- **分页加载**: 每页显示 20-100 条数据
- **搜索防抖**: 输入延迟 300ms 后执行搜索
- **缓存策略**: 缓存页面列表和筛选结果
- **API关联缓存**: 缓存页面API关联数据
- **懒加载**: 延迟加载页面详细信息

### 用户体验
- **操作确认**: 重要操作提供二次确认
- **撤销功能**: 支持删除操作的撤销
- **自动保存**: 表单数据自动保存草稿
- **快速操作**: 提供常用操作的快捷方式
- **智能推荐**: 根据页面类型推荐相关API

### 错误处理
- **网络异常**: 提供重试机制
- **权限不足**: 明确提示权限要求
- **数据冲突**: 提供冲突解决方案
- **表单验证**: 实时验证和错误提示
- **API关联错误**: 详细的关联错误信息

## 接口调用说明

### 前端API接口

#### 页面管理接口
```javascript
// 获取页面列表
pageApi.getPageList(params)
// 参数: { system_id?, module_id?, keyword?, page_type?, status?, page?, size? }
// 返回: Promise<ApiResponse>

// 根据ID获取页面详情
pageApi.getPageById(pageId)
// 参数: pageId (string)
// 返回: Promise<ApiResponse>

// 创建页面
pageApi.createPage(data)
// 参数: { name, description, route, page_type, system_id, module_id, enabled }
// 返回: Promise<ApiResponse>

// 更新页面
pageApi.updatePage(pageId, data)
// 参数: pageId (string), data (Partial<PageData>)
// 返回: Promise<ApiResponse>

// 删除页面
pageApi.deletePage(pageId)
// 参数: pageId (string)
// 返回: Promise<ApiResponse>

// 搜索页面
pageApi.searchPages(params)
// 参数: { keyword?, system_id?, module_id?, page_type?, status? }
// 返回: Promise<ApiResponse>
```

#### 页面API关联管理
```javascript
// 获取页面的API列表
pageApi.getPageApis(pageId, params)
// 参数: pageId (string), params ({ keyword?, method?, status? })
// 返回: Promise<ApiResponse>

// 为页面添加API关联
pageApi.addPageApi(pageId, data)
// 参数: pageId (string), data ({ api_id, execution_type, order })
// 返回: Promise<ApiResponse>

// 更新页面API关联
pageApi.updatePageApi(pageId, apiId, data)
// 参数: pageId (string), apiId (string), data (Partial<PageApiData>)
// 返回: Promise<ApiResponse>

// 删除页面API关联
pageApi.deletePageApi(pageId, apiId)
// 参数: pageId (string), apiId (string)
// 返回: Promise<ApiResponse>

// 批量管理页面API关联
pageApi.batchManagePageApis(pageId, data)
// 参数: pageId (string), data ({ add_apis?, remove_apis?, update_apis? })
// 返回: Promise<ApiResponse>
```

#### 批量操作接口
```javascript
// 批量启用页面
pageApi.batchEnable(pageIds)
// 参数: pageIds (string[])
// 返回: Promise<ApiResponse>

// 批量禁用页面
pageApi.batchDisable(pageIds)
// 参数: pageIds (string[])
// 返回: Promise<ApiResponse>

// 批量删除页面
pageApi.batchDelete(pageIds)
// 参数: pageIds (string[])
// 返回: Promise<ApiResponse>

// 批量导出页面
pageApi.batchExport(pageIds)
// 参数: pageIds (string[])
// 返回: Promise<Blob>
```

#### 统计和配置接口
```javascript
// 获取页面统计概览
pageApi.getPageStats()
// 返回: Promise<ApiResponse<PageStats>>

// 获取页面类型列表
pageApi.getPageTypes()
// 返回: Promise<ApiResponse<PageType[]>>

// 获取执行类型列表
pageApi.getExecutionTypes()
// 返回: Promise<ApiResponse<ExecutionType[]>>
```

### 后端API接口

#### 页面管理 (`/pages/v1/`)

| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/pages/v1/` | 获取页面列表 | system_id?, module_id?, keyword?, page_type?, status?, page?, size? |
| GET | `/pages/v1/{page_id}` | 获取页面详情 | page_id |
| POST | `/pages/v1/` | 创建页面 | PageCreate对象 |
| PUT | `/pages/v1/{page_id}` | 更新页面 | page_id, PageUpdate对象 |
| DELETE | `/pages/v1/{page_id}` | 删除页面 | page_id |
| POST | `/pages/v1/search` | 搜索页面 | PageQueryRequest对象 |

#### 页面API关联管理
| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/pages/v1/{page_id}/apis` | 获取页面的API列表 | page_id, keyword?, method?, status? |
| POST | `/pages/v1/{page_id}/apis` | 为页面添加API关联 | page_id, PageApiCreate对象 |
| PUT | `/pages/v1/{page_id}/apis/{api_id}` | 更新页面API关联 | page_id, api_id, PageApiUpdate对象 |
| DELETE | `/pages/v1/{page_id}/apis/{api_id}` | 删除页面API关联 | page_id, api_id |
| POST | `/pages/v1/{page_id}/apis/batch` | 批量管理页面API关联 | page_id, PageApiBatchRequest对象 |

#### 批量操作
| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| POST | `/pages/v1/batch/enable` | 批量启用页面 | page_ids (List[int]) |
| POST | `/pages/v1/batch/disable` | 批量禁用页面 | page_ids (List[int]) |
| POST | `/pages/v1/batch/delete` | 批量删除页面 | page_ids (List[int]) |
| POST | `/pages/v1/batch/status` | 批量更新状态 | PageBatchRequest对象 |

#### 数据导入导出
| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/pages/v1/export/data` | 导出页面数据 | system_id?, status? |
| POST | `/pages/v1/import/data` | 导入页面数据 | pages_data (List[PageCreate]) |

#### 统计和配置
| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/pages/v1/stats/summary` | 获取页面统计 | 无 |
| GET | `/pages/v1/types/list` | 获取页面类型列表 | 无 |
| GET | `/pages/v1/execution-types/list` | 获取执行类型列表 | 无 |

### 数据模型

#### PageCreate
```typescript
interface PageCreate {
  name: string              // 页面名称
  description?: string      // 页面描述
  route: string            // 页面路由
  page_type: string        // 页面类型
  system_id: number        // 所属系统ID
  module_id?: number       // 所属模块ID
  enabled: boolean         // 是否启用
  tags?: string[]          // 标签列表
  config?: object          // 页面配置
  metadata?: object        // 元数据
}
```

#### PageUpdate
```typescript
interface PageUpdate {
  name?: string
  description?: string
  route?: string
  page_type?: string
  enabled?: boolean
  tags?: string[]
  config?: object
  metadata?: object
}
```

#### PageQueryRequest
```typescript
interface PageQueryRequest {
  system_id?: number       // 系统ID筛选
  module_id?: number       // 模块ID筛选
  keyword?: string         // 搜索关键词
  page_type?: string       // 页面类型筛选
  status?: string          // 状态筛选
  page?: number           // 页码
  size?: number           // 每页数量
}
```

#### PageApiCreate
```typescript
interface PageApiCreate {
  api_id: number           // API接口ID
  execution_type: string   // 执行类型
  order?: number          // 执行顺序
  config?: object         // 配置信息
  enabled: boolean        // 是否启用
}
```

#### PageApiUpdate
```typescript
interface PageApiUpdate {
  execution_type?: string
  order?: number
  config?: object
  enabled?: boolean
}
```

#### PageApiBatchRequest
```typescript
interface PageApiBatchRequest {
  add_apis?: PageApiCreate[]     // 要添加的API关联
  remove_apis?: number[]         // 要移除的API ID列表
  update_apis?: {               // 要更新的API关联
    api_id: number
    data: PageApiUpdate
  }[]
}
```

#### PageBatchRequest
```typescript
interface PageBatchRequest {
  page_ids: number[]       // 页面ID列表
  action: string          // 操作类型: enable, disable, delete
  data?: object           // 附加数据
}
```

## 最佳实践

### 页面管理建议
1. **清晰命名**: 使用描述性的页面名称和路由
2. **合理分类**: 按功能模块组织页面结构
3. **完整描述**: 提供详细的页面功能描述
4. **及时更新**: 保持页面信息的时效性

### API关联管理
1. **精准关联**: 只关联页面真正需要的API
2. **参数配置**: 正确配置API调用参数
3. **状态同步**: 保持API状态与页面状态一致
4. **定期检查**: 定期检查API关联的有效性

### 团队协作
1. **命名规范**: 统一页面命名和路由规范
2. **文档标准**: 建立页面文档编写标准
3. **审核流程**: 建立页面创建和修改审核机制
4. **知识共享**: 定期分享页面管理经验

### 数据管理
1. **备份导出**: 定期导出页面数据备份
2. **版本控制**: 记录页面的变更历史
3. **权限管理**: 合理设置页面的访问权限
4. **监控告警**: 设置页面状态监控