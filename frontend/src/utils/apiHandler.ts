/**
 * 通用API请求处理工具 (Universal API Handler)
 * 
 * 功能概述：
 * - 统一的API请求处理逻辑
 * - 减少重复的错误处理代码
 * - 提供标准化的响应格式
 * - 支持重试机制和加载状态管理
 * 
 * 核心功能：
 * 1. 请求封装 (Request Wrapper)
 *    - 统一的请求格式
 *    - 自动错误处理
 *    - 加载状态管理
 *    - 重试机制支持
 * 
 * 2. 响应处理 (Response Handler)
 *    - 标准化响应格式
 *    - 业务错误处理
 *    - 数据转换支持
 *    - 成功消息提示
 * 
 * 3. 批量操作 (Batch Operations)
 *    - 并行请求处理
 *    - 批量状态更新
 *    - 进度追踪
 *    - 错误汇总
 * 
 * 4. 缓存管理 (Cache Management)
 *    - 请求结果缓存
 *    - 缓存失效策略
 *    - 内存优化
 *    - 数据一致性
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024-01-15
 * @updated 2024-01-15
 */

import { ElMessage, ElLoading } from 'element-plus'
import { request } from './request'
import type { ApiHandlerOptions, CacheData, ApiResponse } from '@/types'

/**
 * 批量操作结果
 */
export interface BatchResult {
  total: number
  successful: number
  failed: number
  results: Array<{
    success: boolean
    result?: any
    error?: Error
    index: number
  }>
  errors: Array<{
    error: Error
    index: number
  }>
}

/**
 * API请求配置选项
 */
const DEFAULT_OPTIONS: ApiHandlerOptions = {
  showLoading: true,        // 是否显示加载状态
  showSuccess: false,       // 是否显示成功消息
  showError: true,          // 是否显示错误消息
  retryCount: 0,           // 重试次数
  retryDelay: 1000,        // 重试延迟(ms)
  timeout: 30000,          // 请求超时(ms)
  cache: false,            // 是否启用缓存
  cacheTime: 300000,       // 缓存时间(ms) - 5分钟
  transform: null,         // 数据转换函数
  successMessage: null,    // 自定义成功消息
  errorMessage: null       // 自定义错误消息
}

/**
 * 请求缓存管理
 */
class RequestCache {
  private cache: Map<string, CacheData>
  private timers: Map<string, number>

  constructor() {
    this.cache = new Map()
    this.timers = new Map()
  }

  /**
   * 生成缓存键
   * @param {string} method - 请求方法
   * @param {string} url - 请求URL
   * @param {Record<string, any>} params - 请求参数
   * @returns {string} 缓存键
   */
  generateKey(method: string, url: string, params: Record<string, any> = {}): string {
    const paramsStr = JSON.stringify(params)
    return `${method.toUpperCase()}:${url}:${paramsStr}`
  }

  /**
   * 获取缓存数据
   * @param {string} key - 缓存键
   * @returns {any} 缓存数据
   */
  get(key: string): any {
    const cached = this.cache.get(key)
    if (cached && Date.now() < cached.expireTime) {
      return cached.data
    }
    this.delete(key)
    return null
  }

  /**
   * 设置缓存数据
   * @param {string} key - 缓存键
   * @param {any} data - 缓存数据
   * @param {number} cacheTime - 缓存时间
   */
  set(key: string, data: any, cacheTime: number): void {
    const expireTime = Date.now() + cacheTime
    this.cache.set(key, { data, expireTime })

    // 设置自动清理定时器
    if (this.timers.has(key)) {
      const existing = this.timers.get(key)
      if (existing !== undefined) {
        window.clearTimeout(existing)
      }
    }
    
    const timerId = window.setTimeout(() => {
      this.delete(key)
    }, cacheTime)
    
    this.timers.set(key, timerId)
  }

  /**
   * 删除缓存数据
   * @param {string} key - 缓存键
   */
  delete(key: string): void {
    this.cache.delete(key)
    if (this.timers.has(key)) {
      const timerId = this.timers.get(key)
      if (timerId !== undefined) {
        window.clearTimeout(timerId)
        this.timers.delete(key)
      }
    }
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.cache.clear()
    this.timers.forEach(timerId => window.clearTimeout(timerId))
    this.timers.clear()
  }

  /**
   * 按模式清除缓存
   * @param {string} pattern - 缓存键模式
   */
  clearByPattern(pattern: string): void {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.delete(key)
      }
    }
  }
}

// 全局缓存实例
const requestCache = new RequestCache()

/**
 * 通用API请求处理器
 */
class ApiHandler {
  private loadingInstance: any

  constructor() {
    this.loadingInstance = null
  }

  /**
   * 显示加载状态
   * @param {boolean} show - 是否显示
   * @param {string} text - 加载文本
   */
  setLoading(show: boolean, text: string = '加载中...'): void {
    if (show) {
      if (!this.loadingInstance) {
        this.loadingInstance = ElLoading.service({
          lock: true,
          text,
          background: 'rgba(0, 0, 0, 0.7)'
        })
      }
    } else {
      if (this.loadingInstance) {
        this.loadingInstance.close()
        this.loadingInstance = null
      }
    }
  }

  /**
   * 执行API请求
   * @param {Function} requestFn - 请求函数
   * @param {ApiHandlerOptions} options - 请求选项
   * @returns {Promise} 请求结果
   */
  async execute<T = any>(requestFn: () => Promise<ApiResponse<T>>, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    const config = { ...DEFAULT_OPTIONS, ...options }
    
    try {
      // 显示加载状态
      if (config.showLoading) {
        this.setLoading(true, config.loadingText)
      }

      // 执行请求
      let result = await this.executeWithRetry<T>(requestFn, config)

      // 列表数据适配：统一为 data.list/total/page/size（兼容期保留 pageSize）
      if (result?.success && result?.data && typeof result.data === 'object') {
        const dataObj: any = result.data as any
        const hasList = Array.isArray(dataObj.list)
        const hasItems = Array.isArray(dataObj.items)
        const hasApis = Array.isArray(dataObj.apis)
        if (hasList || hasItems || hasApis) {
          const listArr = hasList ? dataObj.list : (hasItems ? dataObj.items : dataObj.apis)
          const pageVal = typeof dataObj.page === 'number' ? dataObj.page : 1
          const sizeVal = typeof dataObj.size === 'number' 
            ? dataObj.size 
            : (typeof dataObj.pageSize === 'number' ? dataObj.pageSize : (Array.isArray(listArr) ? listArr.length : 0))
          const totalVal = typeof dataObj.total === 'number' ? dataObj.total : (Array.isArray(listArr) ? listArr.length : 0)
          const adapted = {
            ...dataObj,
            list: listArr ?? [],
            total: totalVal,
            page: pageVal,
            size: sizeVal,
            // 兼容旧字段，逐步废弃
            pageSize: typeof dataObj.pageSize === 'number' ? dataObj.pageSize : sizeVal
          }
          result = { ...result, data: adapted as any }
        }
      }
      
      // 数据转换
      if (config.transform) {
        const transformedData = config.transform(result?.data)
        result = { ...result, data: transformedData }
      }

      // 显示成功消息
      if (config.showSuccess && config.successMessage && result?.success) {
        ElMessage.success(config.successMessage)
      }

      // 错误提示（不抛异常）
      if (config.showError && !result?.success) {
        const errorMessage = config.errorMessage || result?.message || '操作失败'
        ElMessage.error(errorMessage)
      }

      return result

    } catch (error) {
      const message = (error as Error)?.message || '请求执行失败'
      if (config.showError) {
        ElMessage.error(config.errorMessage || message)
      }
      const now = new Date().toISOString()
      return {
        success: false,
        message,
        error: { message, details: error, timestamp: now },
        timestamp: now
      }
    } finally {
      // 关闭加载状态
      if (config.showLoading) {
        this.setLoading(false)
      }
    }
  }

  /**
   * 带重试的请求执行
   * @param {Function} requestFn - 请求函数
   * @param {ApiHandlerOptions} config - 配置选项
   * @returns {Promise} 请求结果
   */
  async executeWithRetry<T>(requestFn: () => Promise<ApiResponse<T>>, config: ApiHandlerOptions): Promise<ApiResponse<T>> {
    let result: ApiResponse<T> | null = null
    
    for (let attempt = 0; attempt <= (config.retryCount || 0); attempt++) {
      result = await requestFn()
      if (result.success) {
        return result
      }
      // 到达最后一次尝试或无重试配置，则返回失败结果
      if (attempt === (config.retryCount || 0)) {
        break
      }
      // 等待重试延迟
      if ((config.retryDelay || 0) > 0) {
        await new Promise(resolve => setTimeout(resolve, config.retryDelay))
      }
      console.warn(`请求失败，正在重试... (${attempt + 1}/${(config.retryCount || 0) + 1})`)
    }
    return result as ApiResponse<T>
  }

  /**
   * GET请求处理
   * @param {string} url - 请求URL
   * @param {Record<string, any>} params - 查询参数
   * @param {ApiHandlerOptions} options - 请求选项
   * @returns {Promise} 请求结果
   */
  async get<T = any>(url: string, params: Record<string, any> = {}, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    const config = { ...DEFAULT_OPTIONS, ...options }
    
    // 检查缓存
    if (config.cache) {
      const cacheKey = requestCache.generateKey('GET', url, params)
      const cached = requestCache.get(cacheKey)
      if (cached) {
        return cached
      }
    }

    const requestFn = () => request.get<T>(url, params, { skipErrorHandler: true })
    const result = await this.execute<T>(requestFn, config)

    // 设置缓存
    if (config.cache) {
      const cacheKey = requestCache.generateKey('GET', url, params)
      requestCache.set(cacheKey, result, config.cacheTime || 300000)
    }

    return result
  }

  /**
   * POST请求处理
   * @param {string} url - 请求URL
   * @param {any} data - 请求数据
   * @param {ApiHandlerOptions} options - 请求选项
   * @returns {Promise} 请求结果
   */
  async post<T = any>(url: string, data: any = {}, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    const config: ApiHandlerOptions = { 
      ...DEFAULT_OPTIONS, 
      showSuccess: true,
      successMessage: '操作成功',
      ...options 
    }
    
    const requestFn = () => request.post<T>(url, data, { skipErrorHandler: true })
    const result = await this.execute<T>(requestFn, config)
    return result
  }

  /**
   * PUT请求处理
   * @param {string} url - 请求URL
   * @param {any} data - 请求数据
   * @param {ApiHandlerOptions} options - 请求选项
   * @returns {Promise} 请求结果
   */
  async put<T = any>(url: string, data: any = {}, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    const config: ApiHandlerOptions = { 
      ...DEFAULT_OPTIONS, 
      showSuccess: true,
      successMessage: '更新成功',
      ...options 
    }
    
    const requestFn = () => request.put<T>(url, data, { skipErrorHandler: true })
    const result = await this.execute<T>(requestFn, config)
    return result
  }

  /**
   * PATCH请求处理
   * @param {string} url - 请求URL
   * @param {any} data - 请求数据
   * @param {ApiHandlerOptions} options - 请求选项
   * @returns {Promise} 请求结果
   */
  async patch<T = any>(url: string, data: any = {}, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    const config: ApiHandlerOptions = { 
      ...DEFAULT_OPTIONS, 
      showSuccess: true,
      successMessage: '操作成功',
      ...options 
    }
    
    const requestFn = () => request.patch<T>(url, data, { skipErrorHandler: true })
    const result = await this.execute<T>(requestFn, config)
    return result
  }

  /**
   * DELETE请求处理
   * @param {string} url - 请求URL
   * @param {ApiHandlerOptions} options - 请求选项
   * @returns {Promise} 请求结果
   */
  async delete<T = any>(url: string, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    const config: ApiHandlerOptions = { 
      ...DEFAULT_OPTIONS, 
      showSuccess: true,
      successMessage: '删除成功',
      ...options 
    }
    
    const requestFn = () => request.delete<T>(url, { skipErrorHandler: true })
    const result = await this.execute<T>(requestFn, config)
    return result
  }

  /**
   * 批量操作处理
   * @param {Array<() => Promise<any>>} operations - 操作列表
   * @param {ApiHandlerOptions} options - 选项配置
   * @returns {Promise<BatchResult>} 批量操作结果
   */
  async batch(operations: Array<() => Promise<any>>, options: ApiHandlerOptions = {}): Promise<BatchResult> {
    const config = {
      showProgress: true,
      maxConcurrent: 5,
      stopOnError: false,
      ...options
    }

    const results: Array<{
      success: boolean
      result?: any
      error?: Error
      index: number
    }> = []
    const errors: Array<{
      error: Error
      index: number
    }> = []
    let completed = 0

    // 分批处理，控制并发数
    const chunks = this.chunkArray(operations, config.maxConcurrent || 5)
    
    for (const chunk of chunks) {
      const promises = chunk.map(async (operation, index) => {
        try {
          const result = await operation()
          completed++
          
          if (config.showProgress) {
            console.log(`批量操作进度: ${completed}/${operations.length}`)
          }
          
          return { success: true, result, index: results.length + index }
        } catch (error) {
          completed++
          const errorObj = error as Error
          errors.push({ error: errorObj, index: results.length + index })
          
          if (config.stopOnError) {
            throw error
          }
          
          return { success: false, error: errorObj, index: results.length + index }
        }
      })

      const chunkResults = await Promise.all(promises)
      results.push(...chunkResults)
    }

    return {
      total: operations.length,
      successful: results.filter(r => r.success).length,
      failed: errors.length,
      results,
      errors
    }
  }

  /**
   * 数组分块
   * @param {Array<T>} array - 原数组
   * @param {number} size - 块大小
   * @returns {Array<Array<T>>} 分块后的数组
   */
  chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = []
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size))
    }
    return chunks
  }

  /**
   * 清除缓存
   * @param {string | null} pattern - 缓存键模式（可选）
   */
  clearCache(pattern: string | null = null): void {
    if (pattern) {
      // 清除匹配模式的缓存
      requestCache.clearByPattern(pattern)
    } else {
      // 清除所有缓存
      requestCache.clear()
    }
  }
}

// 全局API处理器实例
const apiHandler = new ApiHandler()

/**
 * 常用操作的便捷方法接口
 */
export interface ApiUtils {
  getList<T = any>(url: string, params?: Record<string, any>, options?: ApiHandlerOptions): Promise<ApiResponse<T>>
  getDetail<T = any>(url: string, options?: ApiHandlerOptions): Promise<ApiResponse<T>>
  create<T = any>(url: string, data: any, options?: ApiHandlerOptions): Promise<ApiResponse<T>>
  update<T = any>(url: string, data: any, options?: ApiHandlerOptions): Promise<ApiResponse<T>>
  remove<T = any>(url: string, options?: ApiHandlerOptions): Promise<ApiResponse<T>>
  toggleStatus<T = any>(url: string, enabled: boolean, options?: ApiHandlerOptions): Promise<ApiResponse<T>>
  batchToggleStatus(items: any[], enabled: boolean, getUrl: (item: any) => string, options?: ApiHandlerOptions): Promise<BatchResult>
}

/**
 * 常用操作的便捷方法
 */
export const apiUtils: ApiUtils = {
  /**
   * 获取列表数据
   * @param {string} url - API地址
   * @param {Record<string, any>} params - 查询参数
   * @param {ApiHandlerOptions} options - 选项配置
   * @returns {Promise} 列表数据
   */
  async getList<T = any>(url: string, params: Record<string, any> = {}, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    return apiHandler.get<T>(url, params, {
      cache: true,
      loadingText: '加载列表中...',
      ...options
    })
  },

  /**
   * 获取详情数据
   * @param {string} url - API地址
   * @param {ApiHandlerOptions} options - 选项配置
   * @returns {Promise} 详情数据
   */
  async getDetail<T = any>(url: string, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    return apiHandler.get<T>(url, {}, {
      cache: true,
      cacheTime: 60000, // 1分钟缓存
      loadingText: '加载详情中...',
      ...options
    })
  },

  /**
   * 创建数据
   * @param {string} url - API地址
   * @param {any} data - 创建数据
   * @param {ApiHandlerOptions} options - 选项配置
   * @returns {Promise} 创建结果
   */
  async create<T = any>(url: string, data: any, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    return apiHandler.post<T>(url, data, {
      successMessage: '创建成功',
      loadingText: '创建中...',
      ...options
    })
  },

  /**
   * 更新数据
   * @param {string} url - API地址
   * @param {any} data - 更新数据
   * @param {ApiHandlerOptions} options - 选项配置
   * @returns {Promise} 更新结果
   */
  async update<T = any>(url: string, data: any, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    return apiHandler.put<T>(url, data, {
      successMessage: '更新成功',
      loadingText: '更新中...',
      ...options
    })
  },

  /**
   * 删除数据
   * @param {string} url - API地址
   * @param {ApiHandlerOptions} options - 选项配置
   * @returns {Promise} 删除结果
   */
  async remove<T = any>(url: string, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    return apiHandler.delete<T>(url, {
      successMessage: '删除成功',
      loadingText: '删除中...',
      ...options
    })
  },

  /**
   * 切换状态
   * @param {string} url - API地址
   * @param {boolean} enabled - 启用状态
   * @param {ApiHandlerOptions} options - 选项配置
   * @returns {Promise} 切换结果
   */
  async toggleStatus<T = any>(url: string, enabled: boolean, options: ApiHandlerOptions = {}): Promise<ApiResponse<T>> {
    return apiHandler.patch<T>(url, { enabled }, {
      successMessage: `${enabled ? '启用' : '禁用'}成功`,
      loadingText: '状态切换中...',
      showLoading: false, // 状态切换通常不需要全屏加载
      ...options
    })
  },

  /**
   * 批量状态切换
   * @param {Array<any>} items - 项目列表
   * @param {boolean} enabled - 启用状态
   * @param {Function} getUrl - 获取URL的函数
   * @param {ApiHandlerOptions} options - 选项配置
   * @returns {Promise<BatchResult>} 批量操作结果
   */
  async batchToggleStatus(items: any[], enabled: boolean, getUrl: (item: any) => string, options: ApiHandlerOptions = {}): Promise<BatchResult> {
    const operations = items.map(item => 
      () => this.toggleStatus(getUrl(item), enabled, { showSuccess: false })
    )

    const result = await apiHandler.batch(operations, {
      showProgress: true,
      ...options
    })

    // 显示批量操作结果
    if (result.successful > 0) {
      ElMessage.success(`成功${enabled ? '启用' : '禁用'} ${result.successful} 个项目`)
    }
    
    if (result.failed > 0) {
      ElMessage.warning(`${result.failed} 个项目操作失败`)
    }

    return result
  }
}

// 导出API处理器和工具方法
export { apiHandler, requestCache }

// 统一列表响应归一化（提供独立工具函数，页面可选直接使用）
export function normalizeList<T = any>(resp: ApiResponse<any>) {
  const dataObj: any = resp?.data ?? {}
  const listArr = Array.isArray(dataObj.list)
    ? dataObj.list
    : (Array.isArray(dataObj.items) ? dataObj.items : (Array.isArray(dataObj.apis) ? dataObj.apis : []))
  const pageVal = typeof dataObj.page === 'number' ? dataObj.page : 1
  const sizeVal = typeof dataObj.size === 'number' 
    ? dataObj.size 
    : (typeof dataObj.pageSize === 'number' ? dataObj.pageSize : (Array.isArray(listArr) ? listArr.length : 0))
  const totalVal = typeof dataObj.total === 'number' ? dataObj.total : (Array.isArray(listArr) ? listArr.length : 0)
  return {
    success: !!resp?.success,
    message: resp?.message,
    code: typeof resp?.code === 'number' ? resp.code : 0,
    list: listArr,
    total: totalVal,
    page: pageVal,
    size: sizeVal
  }
}
export default apiUtils