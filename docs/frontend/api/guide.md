# API接口和数据流文档

## 项目概述

本文档详细记录了AI自动化测试平台前端项目的API接口设计、数据流向、后端交互方式以及相关的数据模型和状态管理。

## API切换架构

### 概述

为了支持新旧API之间的平滑切换和渐进式迁移，项目引入了API切换工具(`apiSwitcher`)。该工具提供了统一的API调用接口，支持在新版统一API和旧版分散API之间自动切换。

### 核心特性

- **透明切换**: 基于环境变量自动选择API版本
- **降级策略**: 当新API不可用时自动降级到旧API
- **统一接口**: 提供一致的API调用方式
- **健康检查**: 实时监控API服务状态
- **错误处理**: 完整的错误处理和重试机制

### 环境配置

在 `.env.development` 文件中配置API切换相关参数：

```bash
# API版本控制
VITE_USE_UNIFIED_API=true
VITE_API_VERSION=v2

# 新版统一API端点
VITE_UNIFIED_API_BASE_URL=http://localhost:8003

# 旧版API端点
VITE_API_BASE_URL=http://localhost:8001
```

### 使用方式

#### 基础用法

```javascript
import { getApiInstance } from '@/utils/apiSwitcher'

// 获取API实例
const apiInstance = getApiInstance()

// 使用API（自动选择新旧版本）
const response = await apiInstance.apiManagementApi.getStats()
```

#### 在组件中使用

```javascript
// 在Vue组件中
import { getApiInstance } from '@/utils/apiSwitcher'
import apiManagementApi from '@/api/api-management'

// 创建API代理
const apiInstance = getApiInstance()
const apiProxy = apiInstance.apiManagementApi || apiManagementApi

// 使用代理调用API
const data = await apiProxy.getServiceList()
```

#### 手动切换API

```javascript
import { switchApiType, getApiStatus } from '@/utils/apiSwitcher'

// 手动切换到统一API
switchApiType('unified')

// 手动切换到旧版API
switchApiType('legacy')

// 获取当前API状态
const status = getApiStatus()
console.log('当前使用的API:', status.currentApi)
```

### API健康检查

```javascript
import { checkApiHealth } from '@/utils/apiSwitcher'

// 检查所有API健康状态
const healthStatus = await checkApiHealth()

// 检查特定API
const unifiedHealth = await checkApiHealth('unified')
const legacyHealth = await checkApiHealth('legacy')
```

### 错误处理和降级

API切换工具内置了完整的错误处理和降级机制：

1. **自动重试**: 失败时自动重试指定次数
2. **智能降级**: 新API失败时自动切换到旧API
3. **错误上报**: 记录切换历史和错误信息
4. **用户提示**: 通过Element Plus消息组件提示用户

### 迁移指南

#### 现有组件迁移

1. **导入API切换工具**:
   ```javascript
   import { getApiInstance } from '@/utils/apiSwitcher'
   ```

2. **创建API代理**:
   ```javascript
   const apiInstance = getApiInstance()
   const apiProxy = apiInstance.apiManagementApi || apiManagementApi
   ```

3. **替换API调用**:
   ```javascript
   // 旧方式
   const data = await apiManagementApi.getServiceList()
   
   // 新方式
   const data = await apiProxy.getServiceList()
   ```

#### 新组件开发

新开发的组件建议直接使用API切换工具：

```javascript
<script setup>
import { getApiInstance } from '@/utils/apiSwitcher'

const apiInstance = getApiInstance()
const apiProxy = apiInstance.apiManagementApi

// 直接使用代理调用API
const loadData = async () => {
  const response = await apiProxy.getServiceList()
  // 处理响应数据
}
</script>
```

## HTTP请求配置

### 基础配置

项目使用 `axios` 作为HTTP客户端，配置文件位于 `src/utils/request.js`：

```javascript
// 基础配置
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})
```

### 请求拦截器

- **认证处理**: 自动添加 `Bearer Token` 到请求头
- **请求追踪**: 添加 `X-Request-ID` 用于请求追踪
- **加载状态**: 集成全局加载状态管理

### 响应拦截器

- **错误处理**: 统一处理HTTP状态码错误
- **业务逻辑**: 处理业务状态码和错误消息
- **认证失效**: 自动处理401状态码，清除token并跳转登录

### 封装方法

```javascript
export const request = {
  get(url, params, config),
  post(url, data, config),
  put(url, data, config),
  delete(url, config),
  patch(url, data, config),
  upload(url, formData, config),    // 文件上传
  download(url, params, filename)   // 文件下载
}
```

## API接口设计

### 1. 认证相关接口

#### 用户登录
- **接口**: `POST /api/auth/login`
- **描述**: 用户登录验证
- **请求参数**:
  ```json
  {
    "username": "string",
    "password": "string",
    "remember": "boolean"
  }
  ```
- **响应数据**:
  ```json
  {
    "success": true,
    "data": {
      "token": "string",
      "userInfo": {
        "id": "number",
        "username": "string",
        "email": "string",
        "role": "string"
      }
    }
  }
  ```

#### 用户注册
- **接口**: `POST /api/auth/register`
- **描述**: 用户注册
- **状态**: 活跃，调用次数: 456

### 2. 用户管理接口

#### 获取用户信息
- **接口**: `GET /api/user/profile`
- **版本**: v1.2.0
- **描述**: 获取当前用户详细信息
- **状态**: 活跃，调用次数: 890

#### 更新用户资料
- **接口**: `PUT /api/user/update`
- **版本**: v1.1.0
- **描述**: 更新用户基本资料
- **状态**: 非活跃，调用次数: 456

### 3. API管理接口

#### 服务管理
- **获取管理系统列表**: `GET /api/systems`
- **创建管理系统**: `POST /api/systems`
- **更新管理系统**: `PUT /api/systems/{id}`
- **删除管理系统**: `DELETE /api/systems/{id}`
- **获取系统详情**: `GET /api/systems/{id}`
- **获取系统模块**: `GET /api/systems/{id}/modules`
- **创建模块**: `POST /api/systems/{systemId}/modules`
- **更新模块**: `PUT /api/modules/{id}`
- **删除模块**: `DELETE /api/modules/{id}`
- **获取模块详情**: `GET /api/modules/{id}`

#### API接口管理
- **获取API列表**: `GET /api/apis`
- **创建API**: `POST /api/apis`
- **更新API**: `PUT /api/apis/{id}`
- **删除API**: `DELETE /api/apis/{id}`
- **导入API**: `POST /api/apis/import`

### 4. 场景管理接口

#### 测试场景
- **获取场景列表**: `GET /api/scenarios`
- **创建场景**: `POST /api/scenarios`
- **执行场景**: `POST /api/scenarios/{id}/execute`
- **获取执行结果**: `GET /api/scenarios/{id}/results`

### 5. 工作流编排接口

#### 工作流管理
- **获取工作流列表**: `GET /api/workflows`
- **创建工作流**: `POST /api/workflows`
- **发布工作流**: `POST /api/workflows/{id}/publish`
- **执行工作流**: `POST /api/workflows/{id}/execute`

### 6. 系统集成接口

#### 集成管理
- **获取集成列表**: `GET /api/integrations`
- **创建集成**: `POST /api/integrations`
- **同步集成**: `POST /api/integrations/{id}/sync`
- **监控集成**: `GET /api/integrations/{id}/monitor`

### 7. AI场景执行接口

#### AI执行
- **快速执行**: `POST /api/ai/execute`
- **获取执行历史**: `GET /api/ai/executions`
- **获取执行结果**: `GET /api/ai/executions/{id}`
- **取消执行**: `POST /api/ai/executions/{id}/cancel`

## 数据模型

### 1. API接口模型

```typescript
interface ApiModel {
  id: number
  name: string
  version: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  url: string
  description: string
  status: 'active' | 'inactive'
  callCount: number
  lastCallTime: string
  headers: Array<{key: string, value: string}>
  parameters: Array<{
    name: string
    type: string
    required: boolean
    description: string
  }>
}
```

### 2. 管理系统模型

```typescript
interface SystemModel {
  id: number
  name: string
  description: string
  category: 'web' | 'mobile' | 'desktop' | 'api'
  enabled: boolean
  icon: string
  modules: Array<ModuleModel>
}

interface ModuleModel {
  id: number
  name: string
  description: string
  version: string
  enabled: boolean
  systemId: number
}
```

### 3. 测试场景模型

```typescript
interface ScenarioModel {
  id: number
  name: string
  version: string
  type: 'sequential' | 'parallel' | 'mixed'
  apiCount: number
  description: string
  status: 'active' | 'draft' | 'archived'
  executionCount: number
  successRate: number
  lastExecutionTime: Date
  tags: string[]
}
```

### 4. 工作流模型

```typescript
interface WorkflowModel {
  id: number
  name: string
  version: string
  category: 'api-test' | 'data-process' | 'business' | 'monitor'
  nodeCount: number
  description: string
  status: 'running' | 'stopped' | 'draft' | 'published'
  executionCount: number
  successRate: number
  lastExecutionTime: Date
  creator: string
}
```

### 5. 系统集成模型

```typescript
interface IntegrationModel {
  id: number
  name: string
  version: string
  type: 'api' | 'workflow' | 'data' | 'message'
  description: string
  status: 'running' | 'stopped' | 'configuring'
  environment: 'dev' | 'test' | 'prod'
  apiCount: number
  workflowCount: number
  successRate: number
  lastSyncTime: Date
  creator: string
}
```

## 数据流向

### 1. 用户认证流程

```
用户输入 → 登录组件 → request.post('/api/auth/login') 
→ 后端验证 → 返回token → 存储到localStorage → 更新全局状态
```

### 2. API管理流程

```
页面加载 → 获取服务列表 → 展示服务树 → 用户操作 
→ API调用 → 更新本地数据 → 刷新界面
```

### 3. 场景执行流程

```
选择场景 → 配置参数 → 提交执行 → 轮询状态 
→ 获取结果 → 展示报告 → 存储历史
```

### 4. 实时数据更新

```
WebSocket连接 → 监听事件 → 更新组件状态 → 界面实时刷新
```

## 状态管理

### 全局状态 (Pinia Store)

```javascript
// app.js store
const useAppStore = defineStore('app', {
  state: () => ({
    loading: false,
    userInfo: null,
    theme: 'light',
    sidebarCollapsed: false,
    deviceType: 'desktop'
  }),
  
  actions: {
    setLoading(loading),
    setUserInfo(userInfo),
    toggleTheme(),
    toggleSidebar(),
    logout()
  }
})
```

### 组件级状态

每个业务组件维护自己的状态：
- 列表数据 (`ref([])`)
- 搜索条件 (`reactive({})`)
- 分页信息 (`reactive({})`)
- 对话框状态 (`ref(false)`)
- 表单数据 (`reactive({})`)

## 错误处理

### 1. HTTP错误处理

```javascript
// 响应拦截器中的错误处理
switch (status) {
  case 400: message = '请求参数错误'; break
  case 401: 
    message = '未授权，请重新登录'
    // 清除token并跳转登录
    break
  case 403: message = '拒绝访问'; break
  case 404: message = '请求的资源不存在'; break
  case 500: message = '服务器内部错误'; break
  // ...
}
```

### 2. 业务错误处理

```javascript
// 检查业务状态码
if (data.success === false) {
  ElMessage.error(data.message || '请求失败')
  return Promise.reject(new Error(data.message))
}
```

### 3. 组件错误处理

```javascript
// 在组件中使用try-catch
try {
  await loadData()
} catch (error) {
  console.error('加载失败:', error)
  ElMessage.error('加载失败')
}
```

## 性能优化

### 1. 请求优化

- **请求去重**: 防止重复请求
- **请求取消**: 使用 `CancelToken` 取消无效请求
- **缓存策略**: 对静态数据进行缓存

### 2. 数据处理

- **分页加载**: 大数据集分页处理
- **虚拟滚动**: 长列表虚拟化
- **防抖搜索**: 搜索输入防抖处理

### 3. 状态管理

- **按需加载**: 组件状态按需初始化
- **状态持久化**: 关键状态本地存储
- **内存清理**: 组件卸载时清理状态

## 安全考虑

### 1. 认证安全

- **Token管理**: JWT token安全存储
- **自动刷新**: Token过期自动刷新
- **权限控制**: 基于角色的权限验证

### 2. 数据安全

- **输入验证**: 前端数据验证
- **XSS防护**: 输出内容转义
- **CSRF防护**: 请求头验证

### 3. 传输安全

- **HTTPS**: 强制使用HTTPS
- **请求签名**: 关键请求数字签名
- **数据加密**: 敏感数据加密传输

## 开发规范

### 1. API调用规范

```javascript
// 推荐的API调用方式
const loadData = async () => {
  try {
    loading.value = true
    const response = await request.get('/api/data', params)
    dataList.value = response.data
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}
```

### 2. 错误处理规范

- 所有API调用必须包含错误处理
- 使用统一的错误消息提示
- 记录详细的错误日志

### 3. 状态管理规范

- 全局状态使用Pinia Store
- 组件状态使用Vue 3 Composition API
- 避免状态冗余和循环依赖

## 测试策略

### 1. 单元测试

- API工具类测试
- 状态管理测试
- 组件逻辑测试

### 2. 集成测试

- API接口集成测试
- 数据流测试
- 用户交互测试

### 3. E2E测试

- 完整业务流程测试
- 跨页面交互测试
- 错误场景测试

## 更新日志

### v1.0.0 (2024-01-15)
- 初始版本API接口设计
- 基础HTTP请求配置
- 核心业务模块API定义

### 后续版本
- 根据业务需求持续更新API接口
- 优化数据流和状态管理
- 完善错误处理和安全机制

---

*本文档将随着项目开发进度持续更新，确保API接口和数据流的准确性和完整性。*