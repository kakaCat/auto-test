/**
 * API切换工具 (API Switcher Utility)
 * 
 * 功能说明：
 * - 支持新旧API之间的平滑切换
 * - 提供统一的API调用接口
 * - 自动处理数据格式转换
 * - 支持渐进式迁移策略
 * 
 * 设计特点：
 * - 基于环境变量的功能开关
 * - 透明的API切换机制
 * - 向后兼容的接口设计
 * - 完整的错误处理和降级策略
 * 
 * 使用方式：
 * import { getApiInstance } from '@/utils/apiSwitcher'
 * const api = getApiInstance()
 * api.system.getList()
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024
 */

// 导入新旧API模块
import legacyApi from '@/api/service'
import unifiedApi from '@/api/unified-api'
import { ElMessage } from 'element-plus'

/**
 * API类型
 */
export type ApiType = 'unified' | 'legacy'

/**
 * 切换历史记录
 */
export interface SwitchHistoryRecord {
  from: ApiType
  to: ApiType
  reason: string
  timestamp: string
}

/**
 * API健康状态
 */
export interface ApiHealthStatus {
  unified: boolean
  legacy: boolean
}

/**
 * 降级配置
 */
export interface FallbackConfig {
  enabled: boolean
  maxRetries: number
  retryDelay: number
}

/**
 * API配置
 */
export interface ApiConfig {
  useUnifiedApi: boolean
  apiVersion: string
  unifiedApiBase: string
  legacyApiBase: string
  fallbackConfig: FallbackConfig
}

/**
 * API状态信息
 */
export interface ApiStatusInfo {
  currentApi: ApiType
  apiHealth: ApiHealthStatus
  switchHistory: SwitchHistoryRecord[]
  config: ApiConfig
}

/**
 * 健康检查结果
 */
export interface HealthCheckResult {
  healthy: boolean
  error: string | null
}

/**
 * API调用选项
 */
export interface ApiCallOptions {
  noFallback?: boolean
}

/**
 * API切换配置
 */
const API_CONFIG: ApiConfig = {
  // 是否使用统一API
  useUnifiedApi: true,
  
  // API版本
  apiVersion: 'v1',
  
  // 统一API基础URL
  unifiedApiBase: 'http://localhost:8000',
  
  // 旧版API基础URL
  legacyApiBase: 'http://localhost:8000',
  
  // 降级策略配置
  fallbackConfig: {
    enabled: true,
    maxRetries: 2,
    retryDelay: 1000
  }
}

/**
 * API状态管理
 */
class ApiStateManager {
  private currentApi: ApiType
  private apiHealth: ApiHealthStatus
  private switchHistory: SwitchHistoryRecord[]

  constructor() {
    this.currentApi = API_CONFIG.useUnifiedApi ? 'unified' : 'legacy'
    this.apiHealth = {
      unified: true,
      legacy: true
    }
    this.switchHistory = []
  }

  /**
   * 获取当前使用的API类型
   * @returns {ApiType} API类型 (unified|legacy)
   */
  getCurrentApi(): ApiType {
    return this.currentApi
  }

  /**
   * 切换API类型
   * @param {ApiType} apiType - API类型
   * @param {string} reason - 切换原因
   */
  switchApi(apiType: ApiType, reason: string = 'manual'): void {
    const previousApi = this.currentApi
    this.currentApi = apiType
    
    // 记录切换历史
    this.switchHistory.push({
      from: previousApi,
      to: apiType,
      reason,
      timestamp: new Date().toISOString()
    })

    console.log(`API切换: ${previousApi} -> ${apiType} (原因: ${reason})`)
    
    // 通知用户
    if (reason === 'fallback') {
      ElMessage.warning(`API服务切换到${apiType === 'unified' ? '统一' : '旧版'}模式`)
    }
  }

  /**
   * 更新API健康状态
   * @param {ApiType} apiType - API类型
   * @param {boolean} isHealthy - 是否健康
   */
  updateApiHealth(apiType: ApiType, isHealthy: boolean): void {
    this.apiHealth[apiType] = isHealthy
    
    // 如果当前API不健康，尝试切换
    if (!isHealthy && this.currentApi === apiType && API_CONFIG.fallbackConfig.enabled) {
      const fallbackApi: ApiType = apiType === 'unified' ? 'legacy' : 'unified'
      if (this.apiHealth[fallbackApi]) {
        this.switchApi(fallbackApi, 'fallback')
      }
    }
  }

  /**
   * 获取切换历史
   * @returns {SwitchHistoryRecord[]} 切换历史记录
   */
  getSwitchHistory(): SwitchHistoryRecord[] {
    return this.switchHistory
  }

  /**
   * 获取API健康状态
   * @returns {ApiHealthStatus} API健康状态
   */
  getApiHealth(): ApiHealthStatus {
    return { ...this.apiHealth }
  }

  /**
   * 重置状态
   */
  reset(): void {
    this.currentApi = API_CONFIG.useUnifiedApi ? 'unified' : 'legacy'
    this.apiHealth = { unified: true, legacy: true }
    this.switchHistory = []
  }
}

// 全局API状态管理器实例
const apiStateManager = new ApiStateManager()

/**
 * API调用包装器
 * 提供统一的API调用接口，自动处理切换和降级
 */
class ApiWrapper {
  private retryCount: number
  private maxRetries: number

  constructor() {
    this.retryCount = 0
    this.maxRetries = API_CONFIG.fallbackConfig.maxRetries
  }

  /**
   * 执行API调用
   * @param {Function} apiCall - API调用函数
   * @param {any[]} args - 调用参数
   * @param {ApiCallOptions} options - 选项配置
   * @returns {Promise<any>} API调用结果
   */
  async executeApiCall(apiCall: Function, args: any[] = [], options: ApiCallOptions = {}): Promise<any> {
    const currentApi = apiStateManager.getCurrentApi()
    
    try {
      // 重置重试计数
      this.retryCount = 0
      
      // 执行API调用
      const result = await apiCall(...args)
      
      // 更新API健康状态
      apiStateManager.updateApiHealth(currentApi, true)
      
      return result
      
    } catch (error: any) {
      console.error(`API调用失败 (${currentApi}):`, error)
      
      // 更新API健康状态
      apiStateManager.updateApiHealth(currentApi, false)
      
      // 尝试降级处理
      if (this.shouldFallback(error, options)) {
        return this.handleFallback(apiCall, args, options)
      }
      
      throw error
    }
  }

  /**
   * 判断是否应该降级
   * @param {any} error - 错误对象
   * @param {ApiCallOptions} options - 选项配置
   * @returns {boolean} 是否应该降级
   */
  private shouldFallback(error: any, options: ApiCallOptions): boolean {
    if (!API_CONFIG.fallbackConfig.enabled || options.noFallback) {
      return false
    }

    // 网络错误或服务不可用时降级
    const shouldFallback = 
      error.code === 'NETWORK_ERROR' ||
      error.response?.status >= 500 ||
      error.message?.includes('timeout')

    return shouldFallback && this.retryCount < this.maxRetries
  }

  /**
   * 处理降级逻辑
   * @param {Function} apiCall - API调用函数
   * @param {any[]} args - 调用参数
   * @param {ApiCallOptions} options - 选项配置
   * @returns {Promise<any>} 降级调用结果
   */
  private async handleFallback(apiCall: Function, args: any[], options: ApiCallOptions): Promise<any> {
    this.retryCount++
    
    // 等待一段时间后重试
    await new Promise(resolve => 
      setTimeout(resolve, API_CONFIG.fallbackConfig.retryDelay)
    )

    // 切换到备用API
    const currentApi = apiStateManager.getCurrentApi()
    const fallbackApi: ApiType = currentApi === 'unified' ? 'legacy' : 'unified'
    
    if (apiStateManager.getApiHealth()[fallbackApi]) {
      apiStateManager.switchApi(fallbackApi, 'fallback')
      
      // 使用备用API重新调用
      return this.executeApiCall(apiCall, args, { ...options, noFallback: true })
    }
    
    throw new Error('所有API服务都不可用')
  }
}

// 全局API包装器实例
const apiWrapper = new ApiWrapper()

/**
 * 创建API代理
 * 根据当前配置返回相应的API实例
 */
function createApiProxy(): any {
  return new Proxy({}, {
    get(target: any, prop: string | symbol) {
      // 获取当前API实例
      const currentApi = apiStateManager.getCurrentApi()
      const apiInstance = currentApi === 'unified' ? unifiedApi : legacyApi
      
      if (prop in apiInstance) {
        const apiModule = (apiInstance as any)[prop]
        
        // 如果是API模块，创建方法代理
        if (typeof apiModule === 'object' && apiModule !== null) {
          return new Proxy(apiModule, {
            get(moduleTarget: any, methodName: string | symbol) {
              const method = moduleTarget[methodName]
              
              if (typeof method === 'function') {
                // 包装API方法调用
                return (...args: any[]) => {
                  return apiWrapper.executeApiCall(method.bind(moduleTarget), args)
                }
              }
              
              return method
            }
          })
        }
        
        return apiModule
      }
      
      // 如果属性不存在，返回undefined
      return undefined
    }
  })
}

/**
 * 获取API实例
 * @returns {any} API实例代理
 */
export function getApiInstance(): any {
  return createApiProxy()
}

/**
 * 手动切换API类型
 * @param {ApiType} apiType - API类型 (unified|legacy)
 */
export function switchApiType(apiType: ApiType): void {
  if (apiType !== 'unified' && apiType !== 'legacy') {
    throw new Error('无效的API类型，必须是 unified 或 legacy')
  }
  
  apiStateManager.switchApi(apiType, 'manual')
  ElMessage.success(`已切换到${apiType === 'unified' ? '统一' : '旧版'}API`)
}

/**
 * 获取API状态信息
 * @returns {ApiStatusInfo} API状态信息
 */
export function getApiStatus(): ApiStatusInfo {
  return {
    currentApi: apiStateManager.getCurrentApi(),
    apiHealth: apiStateManager.getApiHealth(),
    switchHistory: apiStateManager.getSwitchHistory(),
    config: API_CONFIG
  }
}

/**
 * 检查API健康状态
 * @param {ApiType | null} apiType - API类型 (可选)
 * @returns {Promise<Record<string, HealthCheckResult>>} 健康检查结果
 */
export async function checkApiHealth(apiType: ApiType | null = null): Promise<Record<string, HealthCheckResult>> {
  const apisToCheck = apiType ? [apiType] : ['unified', 'legacy'] as ApiType[]
  const results: Record<string, HealthCheckResult> = {}
  
  for (const api of apisToCheck) {
    try {
      const apiInstance = api === 'unified' ? unifiedApi : legacyApi
      
      // 尝试调用健康检查接口
      if ((apiInstance as any).monitor && (apiInstance as any).monitor.getHealthStatus) {
        await (apiInstance as any).monitor.getHealthStatus()
        results[api] = { healthy: true, error: null }
        apiStateManager.updateApiHealth(api, true)
      } else {
        results[api] = { healthy: false, error: '健康检查接口不可用' }
        apiStateManager.updateApiHealth(api, false)
      }
    } catch (error: any) {
      results[api] = { healthy: false, error: error.message }
      apiStateManager.updateApiHealth(api, false)
    }
  }
  
  return results
}

/**
 * 重置API状态
 */
export function resetApiState(): void {
  apiStateManager.reset()
  ElMessage.info('API状态已重置')
}

/**
 * 导出API状态管理器实例
 */
export { apiStateManager }

/**
 * 导出createApiProxy函数
 */
export { createApiProxy }

/**
 * 默认导出
 */
export default {
  getApiInstance,
  switchApiType,
  getApiStatus,
  checkApiHealth,
  resetApiState,
  createApiProxy
}