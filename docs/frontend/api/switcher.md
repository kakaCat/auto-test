# API切换工具使用指南

## 概述

API切换工具(`apiSwitcher`)是为了支持AI自动化测试平台新旧API之间平滑切换而设计的工具。它提供了统一的API调用接口，支持渐进式迁移策略，确保系统在API升级过程中的稳定性和可用性。

## 设计目标

- **平滑迁移**: 支持从旧版分散API到新版统一API的无缝切换
- **向后兼容**: 保持现有代码的兼容性，减少迁移成本
- **高可用性**: 提供降级策略，确保服务的持续可用
- **易于使用**: 简单的API接口，最小化学习成本

## 架构设计

### 核心组件

1. **ApiStateManager**: API状态管理器
   - 管理当前使用的API类型
   - 记录API切换历史
   - 监控API健康状态

2. **ApiWrapper**: API包装器
   - 统一API调用接口
   - 处理错误和重试逻辑
   - 实现降级策略

3. **API代理**: 动态API代理
   - 根据配置选择API实现
   - 透明的API调用切换
   - 数据格式转换

### 工作流程

```
用户调用API
    ↓
检查当前API配置
    ↓
选择API实现（新版/旧版）
    ↓
执行API调用
    ↓
处理响应/错误
    ↓
必要时执行降级策略
    ↓
返回结果给用户
```

## 配置说明

### 环境变量

在 `.env.development` 文件中配置：

```bash
# 是否使用统一API
VITE_USE_UNIFIED_API=true

# API版本
VITE_API_VERSION=v2

# 新版统一API基础URL
VITE_UNIFIED_API_BASE_URL=http://localhost:8003

# 旧版API基础URL
VITE_API_BASE_URL=http://localhost:8001
```

### 运行时配置

```javascript
const API_CONFIG = {
  useUnifiedApi: import.meta.env.VITE_USE_UNIFIED_API === 'true',
  apiVersion: import.meta.env.VITE_API_VERSION || 'v1',
  unifiedApiBase: import.meta.env.VITE_UNIFIED_API_BASE_URL,
  legacyApiBase: import.meta.env.VITE_API_BASE_URL,
  fallbackConfig: {
    enabled: true,
    maxRetries: 2,
    retryDelay: 1000
  }
}
```

## API接口

### 主要方法

#### getApiInstance()
获取API实例，根据配置自动选择新旧API。

```javascript
import { getApiInstance } from '@/utils/apiSwitcher'

const apiInstance = getApiInstance()
const response = await apiInstance.apiManagementApi.getStats()
```

#### switchApiType(apiType)
手动切换API类型。

```javascript
import { switchApiType } from '@/utils/apiSwitcher'

// 切换到统一API
switchApiType('unified')

// 切换到旧版API
switchApiType('legacy')
```

#### getApiStatus()
获取当前API状态信息。

```javascript
import { getApiStatus } from '@/utils/apiSwitcher'

const status = getApiStatus()
console.log('当前API:', status.currentApi)
console.log('API健康状态:', status.apiHealth)
console.log('切换历史:', status.switchHistory)
```

#### checkApiHealth(apiType)
检查API健康状态。

```javascript
import { checkApiHealth } from '@/utils/apiSwitcher'

// 检查所有API
const allHealth = await checkApiHealth()

// 检查特定API
const unifiedHealth = await checkApiHealth('unified')
```

#### resetApiState()
重置API状态。

```javascript
import { resetApiState } from '@/utils/apiSwitcher'

resetApiState()
```

## 使用示例

### 基础使用

```javascript
// 在Vue组件中
<script setup>
import { getApiInstance } from '@/utils/apiSwitcher'
import apiManagementApi from '@/api/api-management'

// 创建API代理
const apiInstance = getApiInstance()
const apiProxy = apiInstance.apiManagementApi || apiManagementApi

// 使用API
const loadData = async () => {
  try {
    const response = await apiProxy.getServiceList()
    // 处理响应数据
  } catch (error) {
    console.error('API调用失败:', error)
  }
}
</script>
```

### 高级使用

```javascript
// 带有健康检查的API调用
<script setup>
import { getApiInstance, checkApiHealth, getApiStatus } from '@/utils/apiSwitcher'

const apiInstance = getApiInstance()

const loadDataWithHealthCheck = async () => {
  // 检查API健康状态
  const health = await checkApiHealth()
  
  if (!health.unified.isHealthy && !health.legacy.isHealthy) {
    ElMessage.error('所有API服务不可用')
    return
  }
  
  try {
    const response = await apiInstance.apiManagementApi.getStats()
    
    // 获取API状态信息
    const status = getApiStatus()
    console.log(`使用${status.currentApi}API获取数据`)
    
    return response
  } catch (error) {
    console.error('API调用失败:', error)
  }
}
</script>
```

### 手动切换示例

```javascript
// API切换测试组件
<template>
  <div>
    <el-button @click="switchToUnified">切换到统一API</el-button>
    <el-button @click="switchToLegacy">切换到旧版API</el-button>
    <el-button @click="testCurrentApi">测试当前API</el-button>
    
    <div>
      <p>当前API: {{ currentApiType }}</p>
      <p>API健康状态: {{ apiHealthStatus }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  switchApiType, 
  getApiStatus, 
  checkApiHealth,
  getApiInstance 
} from '@/utils/apiSwitcher'

const currentApiType = ref('')
const apiHealthStatus = ref({})
const apiInstance = getApiInstance()

const updateStatus = async () => {
  const status = getApiStatus()
  currentApiType.value = status.currentApi
  
  const health = await checkApiHealth()
  apiHealthStatus.value = health
}

const switchToUnified = async () => {
  switchApiType('unified')
  await updateStatus()
  ElMessage.success('已切换到统一API')
}

const switchToLegacy = async () => {
  switchApiType('legacy')
  await updateStatus()
  ElMessage.success('已切换到旧版API')
}

const testCurrentApi = async () => {
  try {
    const response = await apiInstance.apiManagementApi.getStats()
    ElMessage.success('API测试成功')
    console.log('API响应:', response)
  } catch (error) {
    ElMessage.error('API测试失败')
    console.error('API错误:', error)
  }
}

onMounted(() => {
  updateStatus()
})
</script>
```

## 错误处理

### 自动降级

当新版API不可用时，系统会自动降级到旧版API：

```javascript
// 内置降级逻辑
async executeApiCall(apiCall, args = [], options = {}) {
  try {
    // 尝试当前API
    return await apiCall(...args)
  } catch (error) {
    if (this.shouldFallback(error, options)) {
      // 执行降级策略
      return await this.handleFallback(apiCall, args, options)
    }
    throw error
  }
}
```

### 错误类型

1. **网络错误**: 连接超时、网络不可达
2. **服务错误**: 5xx状态码
3. **认证错误**: 401、403状态码
4. **业务错误**: 4xx状态码（除认证错误外）

### 重试策略

- **最大重试次数**: 2次
- **重试延迟**: 1秒
- **指数退避**: 支持配置

## 最佳实践

### 1. 组件迁移

```javascript
// 推荐的迁移方式
import { getApiInstance } from '@/utils/apiSwitcher'
import apiManagementApi from '@/api/api-management'

// 创建兼容的API代理
const apiInstance = getApiInstance()
const apiProxy = apiInstance.apiManagementApi || apiManagementApi

// 使用代理替换直接调用
const data = await apiProxy.getServiceList()
```

### 2. 错误处理

```javascript
// 完整的错误处理
try {
  const response = await apiProxy.getServiceList()
  return response
} catch (error) {
  // 记录错误
  console.error('API调用失败:', error)
  
  // 用户友好的错误提示
  ElMessage.error('获取数据失败，请稍后重试')
  
  // 可选：上报错误
  // errorReporting.report(error)
  
  throw error
}
```

### 3. 性能优化

```javascript
// 缓存API实例
const apiInstance = getApiInstance()
const apiProxy = apiInstance.apiManagementApi

// 避免重复创建
// ❌ 不推荐
const getData = async () => {
  const api = getApiInstance().apiManagementApi
  return await api.getServiceList()
}

// ✅ 推荐
const apiProxy = getApiInstance().apiManagementApi
const getData = async () => {
  return await apiProxy.getServiceList()
}
```

## 故障排除

### 常见问题

1. **API切换不生效**
   - 检查环境变量配置
   - 确认API服务是否正常运行
   - 查看浏览器控制台错误信息

2. **降级策略未触发**
   - 检查降级配置是否启用
   - 确认错误类型是否符合降级条件
   - 查看API健康检查结果

3. **性能问题**
   - 避免频繁创建API实例
   - 合理设置重试次数和延迟
   - 监控API响应时间

### 调试工具

```javascript
// 启用调试模式
import { apiStateManager } from '@/utils/apiSwitcher'

// 查看切换历史
console.log(apiStateManager.getSwitchHistory())

// 查看当前状态
console.log(apiStateManager.getCurrentApi())
```

## 版本历史

- **v1.0.0**: 初始版本，支持基础API切换功能
- **v1.1.0**: 添加健康检查和降级策略
- **v1.2.0**: 优化错误处理和用户体验

## 相关文档

- [API接口文档](./api_guide.md)
- [前端开发指南](./development_guide.md)
- [组件开发指南](./component_development_guide.md)