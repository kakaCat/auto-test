# API管理模块数据流与运行策略

## 数据流设计

```
数据流向图:
┌─────────────────────────────────────────────────────────────┐
│                      API管理数据流                          │
├─────────────────────────────────────────────────────────────┤
│ 用户操作 → 组件事件 → Composable逻辑 → Pinia Store → API请求 │
│    ↓         ↓           ↓            ↓          ↓        │
│ 点击按钮   emit事件   业务逻辑处理   状态更新   后端接口     │
│    ↓                                   ↓          ↓        │
│ 界面反馈 ← 组件更新 ← 响应式更新 ← 状态变更 ← 响应数据      │
└─────────────────────────────────────────────────────────────┘
```

## 性能优化策略
- 虚拟滚动: 使用`vue-virtual-scroller`处理大量API数据
- 防抖搜索: 搜索输入使用300ms防抖，减少API调用
- 缓存策略: 使用Pinia持久化插件缓存常用数据
- 懒加载: 非关键组件使用动态导入
- 代码分割: 按路由和功能模块分割代码包

### 示例：虚拟滚动
```typescript
const VirtualApiList = defineComponent({
  setup() {
    const { list, containerProps, wrapperProps } = useVirtualList(
      apis,
      { itemHeight: 120, overscan: 10 }
    )
    return { list, containerProps, wrapperProps }
  }
})
```

### 示例：防抖搜索
```typescript
const searchKeyword = ref('')
const debouncedSearch = useDebounceFn((keyword: string) => {
  setFilters({ searchKeyword: keyword })
  fetchApis()
}, 500)
watch(searchKeyword, debouncedSearch)
```

### 示例：智能缓存
```typescript
const apiDetailsCache = new Map<string, ApiInfo>()
const cacheExpiry = new Map<string, number>()
const getApiDetails = async (id: string) => {
  const now = Date.now()
  const expiry = cacheExpiry.get(id)
  if (apiDetailsCache.has(id) && expiry && now < expiry) {
    return apiDetailsCache.get(id)
  }
  const details = await apiService.getApiDetails(id)
  apiDetailsCache.set(id, details)
  cacheExpiry.set(id, now + 5 * 60 * 1000)
  return details
}
```

### 示例：代码分割
```typescript
const ApiManagement = defineAsyncComponent(() => import('@/views/api-management/index.vue'))
const ApiEditor = defineAsyncComponent(() => import('@/components/api-editor/index.vue'))
const ApiTester = defineAsyncComponent(() => import('@/components/api-tester/index.vue'))
```

## 错误处理机制

### 统一错误处理类
```typescript
class ApiErrorHandler {
  static handleNetworkError(error: AxiosError): void {
    if (error.code === 'NETWORK_ERROR') {
      message.error('网络连接失败，请检查网络设置')
    } else if (error.code === 'TIMEOUT') {
      message.error('请求超时，请稍后重试')
    }
  }
  static handleBusinessError(error: BusinessError): void {
    switch (error.code) {
      case 'API_NOT_FOUND':
        message.error('API不存在或已被删除')
        break
      case 'PERMISSION_DENIED':
        message.error('权限不足，无法执行此操作')
        break
      default:
        message.error(error.message || '操作失败')
    }
  }
}
```

### API测试错误处理
```typescript
const handleApiTestError = (error: ApiTestError) => {
  switch (error.type) {
    case 'NETWORK_ERROR':
      showErrorMessage('网络连接失败，请检查网络设置')
      break
    case 'TIMEOUT_ERROR':
      showErrorMessage('请求超时，请稍后重试')
      break
    case 'VALIDATION_ERROR':
      showValidationErrors(error.details)
      break
    case 'SERVER_ERROR':
      showErrorMessage(`服务器错误: ${error.message}`)
      break
    default:
      showErrorMessage('未知错误，请联系管理员')
  }
}
```

### 批量操作错误处理
```typescript
const handleBatchOperationError = (results: BatchOperationResult[]) => {
  const failed = results.filter(r => !r.success)
  if (failed.length === 0) {
    showSuccessMessage('批量操作完成')
  } else if (failed.length === results.length) {
    showErrorMessage('批量操作失败')
  } else {
    showWarningMessage(`部分操作失败: ${failed.length}/${results.length}`)
    showFailedItems(failed)
  }
}
```

## 数据同步策略

### 实时同步
```typescript
const useApiSync = () => {
  const { connect, disconnect, on } = useWebSocket('/api/ws/apis')
  on('api:created', (api: ApiInfo) => { addApiToList(api); updateApiTree() })
  on('api:updated', (api: ApiInfo) => { updateApiInList(api); invalidateCache(api.id) })
  on('api:deleted', (apiId: string) => { removeApiFromList(apiId); clearCache(apiId) })
  on('api:tested', (result: ApiTestResult) => { updateTestResult(result) })
  return { connect, disconnect }
}
```

### 离线缓存
```typescript
const useApiCache = () => {
  const db = useIndexedDB('apis', 1)
  const cacheApi = async (api: ApiInfo) => { await db.put('apis', api) }
  const getCachedApis = async (filters: ApiFilters) => {
    const allApis = await db.getAll('apis')
    return filterApis(allApis, filters)
  }
  const syncWithServer = async () => {
    const lastSync = await db.get('metadata', 'lastSync')
    const changes = await apiService.getChanges(lastSync)
    for (const change of changes) {
      switch (change.type) {
        case 'create':
        case 'update':
          await db.put('apis', change.data)
          break
        case 'delete':
          await db.delete('apis', change.id)
          break
      }
    }
    await db.put('metadata', Date.now(), 'lastSync')
  }
  return { cacheApi, getCachedApis, syncWithServer }
}
```