/**
 * 运行时API执行器（Runtime Executor）
 * 
 * 作用：
 * - 根据 ApiConfigItem 的 method + path 执行接口调用
 * - 统一使用 request 封装，返回标准 ApiResponse
 * - 记录调用耗时与状态码（若可用）到 FrontendMonitor
 * 
 * 设计原则：
 * - 工具类使用静态方法
 * - 类型安全（unknown优先）
 * - 严格错误信息
 */

import { request } from '@/utils/request'
import type { ApiResponse } from '@/types'
import type { ApiConfigItem } from '@/views/page-management/types/page-config'
import { frontendMonitor } from '@/utils/monitor'

export interface ExecuteOptions {
  query?: Record<string, unknown>
  body?: Record<string, unknown>
  headers?: Record<string, string>
  timeoutMs?: number
}

export class RuntimeExecutor {
  /**
   * 执行配置的API调用
   */
  static async execute(api: ApiConfigItem, options: ExecuteOptions = {}): Promise<ApiResponse<unknown>> {
    if (!api || !api.method || !api.path) {
      throw new Error('API配置不完整：缺少method或path')
    }
    const method = api.method.toUpperCase()
    const url = api.path
    const start = performance.now()

    let resp: ApiResponse<unknown>
    try {
      switch (method) {
        case 'GET':
          resp = await request.get(url, options.query || {})
          break
        case 'POST':
          resp = await request.post(url, options.body || {})
          break
        case 'PUT':
          resp = await request.put(url, options.body || {})
          break
        case 'DELETE':
          resp = await request.delete(url)
          break
        case 'PATCH':
          resp = await request.patch(url, options.body || {})
          break
        default:
          throw new Error(`不支持的HTTP方法: ${method}`)
      }
    } catch (e: unknown) {
      const duration = Math.round(performance.now() - start)
      // 无法从异常中读取状态码，记录-1
      frontendMonitor.recordApiCall(url, duration, -1)
      throw e
    }

    const duration = Math.round(performance.now() - start)
    // ApiResponse没有直接暴露HTTP状态码，这里用success映射为200或500
    const status = resp.success ? 200 : 500
    frontendMonitor.recordApiCall(url, duration, status)
    return resp
  }
}