# API管理页面交互文档

## 页面概述

API管理页面是自动化测试平台的核心功能模块，用于管理和维护系统中的API接口。页面提供了完整的API生命周期管理功能，包括创建、编辑、删除、搜索、导入导出等操作。

## 界面布局

### 整体结构
```
┌─────────────────────────────────────────────────────────────┐
│                        页面头部                              │
│  [API管理] [描述文本] [新增API] [导入] [导出] [批量操作]      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────────────────────────────┐   │
│  │             │  │                                     │   │
│  │   左侧导航   │  │           右侧API管理面板            │   │
│  │  SystemTree │  │                                     │   │
│  │             │  │  ┌─────────────────────────────┐    │   │
│  │   系统列表   │  │  │        搜索筛选区域          │    │   │
│  │   模块分类   │  │  └─────────────────────────────┘    │   │
│  │             │  │                                     │   │
│  │             │  │  ┌─────────────────────────────┐    │   │
│  │             │  │  │        API列表展示          │    │   │
│  │             │  │  │                             │    │   │
│  │             │  │  │  [API卡片1] [API卡片2]      │    │   │
│  │             │  │  │  [API卡片3] [API卡片4]      │    │   │
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
- **页面标题**: "API管理"
- **描述文本**: "管理和维护系统API接口"
- **操作按钮组**:
  - `新增API`: 主要操作按钮，蓝色背景
  - `导入`: 次要操作按钮，支持批量导入
  - `导出`: 次要操作按钮，支持数据导出
  - `批量操作`: 下拉菜单，包含批量删除、批量更新状态等

### 左侧导航面板
- **SystemTree组件**: 系统和模块树形结构
- **功能特性**:
  - 展示系统和模块层级结构
  - 支持系统和模块筛选
  - 点击系统节点筛选该系统下所有API
  - 点击模块节点筛选该系统和模块对应的API

#### 系统和模块树形结构
- **系统节点**: 显示系统名称，支持展开查看模块
- **模块节点**: 显示模块名称，作为系统的子节点
- **展开/收起**: 点击系统节点展开或收起模块列表
- **节点选择**: 
  - 点击系统节点：筛选该系统下所有API
  - 点击模块节点：筛选该系统和模块对应的API
- **刷新按钮**: 重新加载系统和模块树结构

#### 筛选功能
- **系统筛选**: 选择系统节点时，右侧API列表显示该系统的所有API
- **模块筛选**: 选择模块节点时，右侧API列表显示该模块的所有API
- **筛选状态**: 导航面板显示当前选中的系统/模块状态
- **清除筛选**: 支持清除当前筛选条件，显示所有API

#### 交互功能
- **节点点击**: 选中系统或模块，右侧显示对应API列表
- **多选支持**: 支持选择多个系统/模块进行批量操作
- **拖拽排序**: 支持系统和模块节点拖拽调整顺序
- **右键菜单**: 提供编辑、删除、添加子模块等操作

### 右侧API管理面板

#### 搜索筛选区域
```
┌─────────────────────────────────────────────────────────┐
│ [搜索框: 输入API名称或路径]  [搜索按钮]  [重置按钮]      │
├─────────────────────────────────────────────────────────┤
│ 筛选条件:                                               │
│ [HTTP方法▼] [状态▼] [分类▼] [创建时间▼] [更多筛选▼]     │
└─────────────────────────────────────────────────────────┘
```

#### API列表展示
API以表格形式展示，包含以下列：
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ API列表表格                                                                          │
├──┬─────────────┬────────┬─────────────────┬──────────┬─────────────┬─────────────────┤
│☐ │ API名称     │ 方法   │ 路径            │ 状态     │ 系统/模块   │ 操作            │
├──┼─────────────┼────────┼─────────────────┼──────────┼─────────────┼─────────────────┤
│☐ │ 用户登录    │ POST   │ /api/v1/login   │ 启用     │ 用户系统    │ [编辑][删除]    │
│☐ │ 获取用户信息│ GET    │ /api/v1/user    │ 启用     │ 用户系统    │ [编辑][删除]    │
│☐ │ 创建订单    │ POST   │ /api/v1/order   │ 禁用     │ 订单系统    │ [编辑][删除]    │
│☐ │ 查询订单    │ GET    │ /api/v1/order   │ 启用     │ 订单系统    │ [编辑][删除]    │
│☐ │ 支付接口    │ POST   │ /api/v1/pay     │ 开发中   │ 支付系统    │ [编辑][删除]    │
└──┴─────────────┴────────┴─────────────────┴──────────┴─────────────┴─────────────────┘

表格列说明：
- 复选框：支持多选进行批量操作
- API名称：接口的业务名称，可点击查看详情
- 方法：HTTP方法（GET、POST、PUT、DELETE等）
- 路径：API的完整路径
- 状态：启用、禁用、开发中等状态标签
- 系统/模块：所属系统和模块信息
- 操作：编辑、删除、测试、复制等操作按钮
```

## 交互流程

### 页面初始化
1. **加载系统树**: 获取系统列表并构建树形结构
2. **加载API列表**: 获取默认的API列表数据
3. **初始化筛选条件**: 设置默认筛选参数
4. **状态同步**: 同步URL参数和页面状态

### API搜索与筛选
1. **实时搜索**:
   - 用户输入关键词
   - 300ms防抖延迟
   - 自动触发搜索请求
   - 更新API列表

2. **条件筛选**:
   - 选择HTTP方法（GET、POST、PUT、DELETE等）
   - 选择状态（启用、禁用、开发中等）
   - 选择分类或模块
   - 选择时间范围
   - 组合筛选条件

3. **筛选重置**:
   - 点击重置按钮
   - 清空所有筛选条件
   - 恢复默认列表

### API操作流程

#### 新增API
1. **触发操作**: 点击"新增API"按钮
2. **打开表单**: 弹出API创建对话框
3. **表单填写**:
   - 基本信息：名称、路径、HTTP方法
   - 详细信息：描述、分类、标签
   - 请求参数：Headers、Query、Body
   - 响应信息：状态码、响应体结构
4. **数据验证**: 实时验证表单数据
5. **提交保存**: 发送创建请求
6. **结果反馈**: 显示成功/失败消息
7. **列表更新**: 刷新API列表

##### API表单对话框详细说明

**对话框组件**: `ApiFormDialog.vue`

**表单字段结构**:

1. **基本信息区域**:
   - **API名称** (必填): 文本输入框，最大长度100字符
   - **请求方法** (必填): 下拉选择框，支持GET、POST、PUT、DELETE、PATCH等
   - **URL路径** (必填): 文本输入框，带基础URL前缀显示
   - **所属系统** (必填): 下拉选择框，选择后自动加载对应模块
   - **所属模块**: 下拉选择框，依赖于所属系统的选择

2. **详细信息区域**:
   - **API描述**: 多行文本框，最大500字符，支持字数统计
   - **状态**: 开关组件，启用/禁用状态切换

3. **请求参数配置**:
   - **参数列表**: 动态参数配置区域
     - 参数名: 文本输入框
     - 参数类型: 下拉选择(string/number/boolean/object/array)
     - 是否必填: 开关组件
     - 参数描述: 文本输入框
     - 删除按钮: 移除当前参数
   - **添加参数**: 按钮，动态添加新参数行

4. **响应配置**:
   - **响应示例**: 多行文本框，支持JSON格式输入，4行高度

5. **标签管理**:
   - **标签选择**: 多选下拉框，支持筛选、创建新标签
   - **预定义标签**: 系统预设的常用标签选项

**表单验证规则**:
- API名称: 必填，长度1-100字符
- 请求方法: 必填，从预定义选项中选择
- URL路径: 必填，符合URL路径格式
- 所属系统: 必填，从现有系统中选择
- 参数配置: 参数名不能重复，类型必须选择

**交互特性**:
- **实时验证**: 表单字段失焦时进行验证
- **动态依赖**: 系统选择后自动更新模块列表
- **参数管理**: 支持动态添加/删除请求参数
- **标签创建**: 支持在选择时创建新标签
- **保存状态**: 提交时显示loading状态，防止重复提交
- **错误处理**: 验证失败时高亮错误字段并显示提示信息

#### 编辑API
1. **触发操作**: 点击API卡片的"编辑"按钮
2. **加载数据**: 获取API详细信息
3. **填充表单**: 预填充现有数据
4. **修改数据**: 用户编辑相关字段
5. **保存更新**: 提交修改请求
6. **状态更新**: 更新列表中的API信息

**编辑模式特性**:
- **表单复用**: 使用与新增相同的`ApiFormDialog`组件
- **数据预填充**: 自动填充API的现有信息到表单各字段
- **字段限制**: 某些关键字段(如所属系统)在编辑模式下可能被禁用
- **增量更新**: 只提交发生变化的字段数据
- **版本控制**: 支持并发编辑检测，防止数据覆盖
- **保存状态管理**: 编辑保存后正确重置组件状态，支持连续编辑操作

#### 删除API
1. **触发操作**: 点击"删除"按钮
2. **确认对话框**: 显示删除确认提示
3. **执行删除**: 发送删除请求
4. **列表更新**: 从列表中移除已删除项
5. **消息提示**: 显示删除成功消息

#### API测试
1. **触发操作**: 点击"测试"按钮
2. **打开测试面板**: 显示API测试界面
3. **参数配置**: 设置请求参数和Headers
4. **发送请求**: 执行API调用
5. **结果展示**: 显示响应数据和状态
6. **保存测试**: 可选保存测试用例

### 批量操作
1. **选择API**: 勾选多个API项目
2. **选择操作**: 从批量操作菜单选择
3. **确认执行**: 显示批量操作确认对话框
4. **执行操作**: 并行处理选中的API
5. **进度显示**: 显示批量操作进度
6. **结果汇总**: 展示操作结果统计

### 导入导出功能

#### 导入API
1. **选择文件**: 点击导入按钮，选择文件
2. **格式验证**: 验证文件格式（JSON、Excel等）
3. **数据预览**: 显示导入数据预览
4. **冲突处理**: 处理重复API的策略选择
5. **执行导入**: 批量创建API
6. **结果报告**: 显示导入成功/失败统计

#### 导出API
1. **选择范围**: 选择导出的API范围
2. **选择格式**: 选择导出格式（JSON、Excel、CSV）
3. **配置选项**: 设置导出字段和格式
4. **生成文件**: 创建导出文件
5. **下载文件**: 提供文件下载链接

## 响应式设计

### 桌面端 (>1200px)
- 左侧导航固定宽度 280px
- 右侧内容区域自适应
- API表格完整显示所有列
- 完整显示所有操作按钮

### 平板端 (768px-1200px)
- 左侧导航可折叠
- API表格隐藏部分次要列（如创建时间）
- 部分操作按钮收缩到下拉菜单

### 移动端 (<768px)
- 左侧导航抽屉式显示
- API表格转为卡片式布局
- 操作按钮简化为图标
- 搜索筛选区域垂直排列

## 键盘快捷键

- `Ctrl/Cmd + N`: 新增API
- `Ctrl/Cmd + F`: 聚焦搜索框
- `Ctrl/Cmd + R`: 刷新列表
- `Escape`: 关闭对话框
- `Enter`: 确认操作
- `Tab`: 在表单字段间切换

## 加载状态和反馈

### 加载状态
- **页面初始化**: 骨架屏显示
- **搜索加载**: 搜索框显示加载图标
- **API操作**: 按钮显示加载状态
- **批量操作**: 进度条显示

### 用户反馈
- **成功操作**: 绿色Toast消息
- **错误处理**: 红色错误提示
- **警告信息**: 橙色警告提示
- **信息提示**: 蓝色信息提示

### 空状态处理
- **无API数据**: 显示空状态插画和引导
- **搜索无结果**: 提供搜索建议
- **网络错误**: 显示重试按钮

## 常见问题与解决方案

### 性能优化
- **虚拟滚动**: 大量API数据时使用虚拟表格
- **分页加载**: 合理设置每页数据量（建议20-50条）
- **表格优化**: 固定表头、列宽自适应
- **缓存策略**: 缓存常用的筛选结果

### 用户体验
- **操作确认**: 重要操作提供二次确认
- **撤销功能**: 支持删除操作的撤销
- **自动保存**: 表单数据自动保存草稿
- **快速操作**: 提供常用操作的快捷方式

### 错误处理
- **网络异常**: 提供重试机制
- **权限不足**: 明确提示权限要求
- **数据冲突**: 提供冲突解决方案
- **表单验证**: 实时验证和错误提示

## 接口调用说明

### 前端API接口

#### 系统管理接口
```javascript
// 获取系统列表
apiManagementApi.getServiceList(params)
// 参数: { keyword?, serviceId?, method? }
// 返回: Promise<ApiResponse>

// 创建系统
apiManagementApi.createService(data)
// 参数: { name, description, url, category, icon, enabled }
// 返回: Promise<ApiResponse>

// 更新系统
apiManagementApi.updateService(systemId, data)
// 参数: systemId (string), data (Partial<ServiceData>)
// 返回: Promise<ApiResponse>

// 删除系统
apiManagementApi.deleteService(systemId)
// 参数: systemId (string)
// 返回: Promise<ApiResponse>
```

#### 模块管理接口
```javascript
// 获取模块列表
apiManagementApi.getModuleList(params)
// 参数: { system_id?, keyword?, method?, status? }
// 返回: Promise<ApiResponse>
```

#### API接口管理
```javascript
// 获取API列表
apiManagementApi.getApis(params)
// 参数: { system_id?, module_id?, enabled_only?, keyword?, method? }
// 返回: Promise<ApiResponse>

// 获取API详情
apiManagementApi.getApiDetail(apiId)
// 参数: apiId (string)
// 返回: Promise<ApiResponse>

// 创建API
apiManagementApi.createApi(data)
// 参数: { system_id, name, description, url, enabled, tags }
// 返回: Promise<ApiResponse>

// 更新API
apiManagementApi.updateApi(apiId, data)
// 参数: apiId (string), data (Partial<ApiData>)
// 返回: Promise<ApiResponse>

// 删除API
apiManagementApi.deleteApi(apiId)
// 参数: apiId (string)
// 返回: Promise<ApiResponse>

// 测试API
apiManagementApi.testApi(apiId, testData)
// 参数: apiId (string), testData (TestData)
// 返回: Promise<ApiResponse>

// 批量测试API
apiManagementApi.batchTestApis(apiIds, testConfig)
// 参数: apiIds (string[]), testConfig (TestConfig)
// 返回: Promise<ApiResponse>
```

#### 统计和工具接口
```javascript
// 获取API统计
apiManagementApi.getApiStatistics()
// 返回: Promise<ApiResponse<ApiStatistics>>

// 获取综合统计
apiManagementApi.getStats()
// 返回: Promise<ApiResponse<StatsData>>

// 导入API
apiManagementApi.importApis(formData)
// 参数: formData (FormData)
// 返回: Promise<ApiResponse>

// 导出API
apiManagementApi.exportApis(params)
// 参数: params (Record<string, any>)
// 返回: Promise<Blob>
```

### 后端API接口

#### API接口管理 (`/api-interfaces/v1/`)

| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/api-interfaces/v1/` | 获取API接口列表 | system_id?, module_id?, keyword?, method?, status?, enabled_only?, page?, size? |
| GET | `/api-interfaces/v1/{api_id}` | 获取API接口详情 | api_id |
| POST | `/api-interfaces/v1/` | 创建API接口 | ApiInterfaceCreate对象 |
| PUT | `/api-interfaces/v1/{api_id}` | 更新API接口 | api_id, ApiInterfaceUpdate对象 |
| DELETE | `/api-interfaces/v1/{api_id}` | 删除API接口 | api_id |
| POST | `/api-interfaces/v1/search` | 搜索API接口 | ApiInterfaceQueryRequest对象 |
| GET | `/api-interfaces/v1/search/simple` | 简单搜索API接口 | keyword?, system_id?, module_id?, method?, status?, page?, size? |

#### 系统和模块管理
| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/api-interfaces/v1/system/{system_id}` | 获取系统的API接口 | system_id |
| GET | `/api-interfaces/v1/module/{module_id}` | 获取模块的API接口 | module_id |

#### 批量操作
| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| POST | `/api-interfaces/v1/batch/status` | 批量更新状态 | ApiInterfaceBatchRequest对象 |
| POST | `/api-interfaces/v1/batch/delete` | 批量删除API接口 | api_ids (List[int]) |

#### 数据导入导出
| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/api-interfaces/v1/export/data` | 导出API接口数据 | system_id?, status? |
| POST | `/api-interfaces/v1/import/data` | 导入API接口数据 | apis_data (List[ApiInterfaceCreate]) |

#### 统计和配置
| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/api-interfaces/v1/stats/summary` | 获取API接口统计 | 无 |
| GET | `/api-interfaces/v1/methods/list` | 获取HTTP方法列表 | 无 |
| GET | `/api-interfaces/v1/statuses/list` | 获取状态列表 | 无 |

### 数据模型

#### ApiInterfaceCreate
```typescript
interface ApiInterfaceCreate {
  name: string              // API名称
  description?: string      // API描述
  url: string              // API路径
  method: string           // HTTP方法
  system_id: number        // 所属系统ID
  module_id?: number       // 所属模块ID
  enabled: boolean         // 是否启用
  tags?: string[]          // 标签列表
  headers?: object         // 请求头
  params?: object          // 请求参数
  body?: object            // 请求体
  response_example?: object // 响应示例
}
```

#### ApiInterfaceUpdate
```typescript
interface ApiInterfaceUpdate {
  name?: string
  description?: string
  url?: string
  method?: string
  enabled?: boolean
  tags?: string[]
  headers?: object
  params?: object
  body?: object
  response_example?: object
}
```

#### ApiInterfaceQueryRequest
```typescript
interface ApiInterfaceQueryRequest {
  system_id?: number       // 系统ID筛选
  module_id?: number       // 模块ID筛选
  keyword?: string         // 搜索关键词
  method?: string          // HTTP方法筛选
  status?: string          // 状态筛选
  enabled_only?: boolean   // 仅显示启用的
  page?: number           // 页码
  size?: number           // 每页数量
}
```

## 常见问题与解决方案

### API编辑保存状态管理问题

#### 问题描述
在API编辑表单中，点击保存按钮后，保存状态（loading）一直显示，无法重置，导致用户无法进行后续操作。

#### 根本原因
前端`ApiFormDialog`组件的保存状态管理存在缺陷：
- 子组件`ApiFormDialog`触发保存事件后，`saving`状态设置为`true`
- 父组件`api-management/index.vue`处理保存逻辑，但未通知子组件重置状态
- 导致无论保存成功或失败，`saving`状态都无法重置为`false`

#### 解决方案
1. **修改子组件** (`ApiFormDialog.vue`)：
   ```javascript
   // 添加重置保存状态的方法
   const resetSavingState = () => {
     saving.value = false
   }
   
   // 使用 defineExpose 暴露方法给父组件
   defineExpose({
     resetSavingState
   })
   ```

2. **修改父组件** (`api-management/index.vue`)：
   ```javascript
   // 添加子组件引用
   const apiFormDialogRef = ref()
   
   // 在 saveApi 方法中调用子组件的重置方法
   const saveApi = async (formData) => {
     try {
       // ... 保存逻辑
       // 保存成功后重置状态
       apiFormDialogRef.value.resetSavingState()
     } catch (error) {
       // 保存失败后也要重置状态
       apiFormDialogRef.value.resetSavingState()
     }
   }
   ```

#### 修复效果
- 保存成功或失败后，loading状态都能正确重置
- 用户可以正常进行多次编辑保存操作
- 提升了用户体验和界面响应性

### 其他常见问题

#### 表单验证问题
- **问题**: 表单提交时验证不通过但没有明确提示
- **解决**: 确保所有验证规则都有对应的错误提示信息

#### 网络请求超时
- **问题**: API请求超时导致页面卡死
- **解决**: 设置合理的请求超时时间和重试机制

## 最佳实践

### 操作建议
1. **合理分类**: 为API设置清晰的分类和标签
2. **详细描述**: 提供完整的API描述和文档
3. **定期维护**: 及时更新API状态和信息
4. **测试验证**: 定期测试API的可用性

### 数据管理
1. **备份导出**: 定期导出API数据备份
2. **版本控制**: 记录API的变更历史
3. **权限管理**: 合理设置API的访问权限
4. **监控告警**: 设置API状态监控

### 团队协作
1. **命名规范**: 统一API命名和路径规范
2. **文档标准**: 建立API文档编写标准
3. **审核流程**: 建立API创建和修改审核机制
4. **知识共享**: 定期分享API使用经验

### 状态管理最佳实践
1. **父子组件通信**: 使用`defineExpose`暴露子组件方法给父组件调用
2. **状态重置**: 确保异步操作完成后及时重置loading状态
3. **错误处理**: 在catch块中也要处理状态重置
4. **用户反馈**: 提供明确的操作成功/失败反馈