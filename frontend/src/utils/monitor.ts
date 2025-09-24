/**
 * 前端性能监控工具
 */

/**
 * API调用指标
 */
export interface ApiMetric {
  duration: number
  status: number
  timestamp: number
}

/**
 * 性能指标类型
 */
export type MetricValue = number | ApiMetric

/**
 * 前端性能监控类
 */
export class FrontendMonitor {
  private metrics: Map<string, MetricValue>
  private startTime: number

  constructor() {
    this.metrics = new Map()
    this.startTime = Date.now()
  }
  
  /**
   * 记录页面加载时间
   */
  recordPageLoad(): void {
    if (window.performance) {
      const timing = window.performance.timing
      const loadTime = timing.loadEventEnd - timing.navigationStart
      this.metrics.set('page_load_time', loadTime)
    }
  }
  
  /**
   * 记录API请求时间
   * @param {string} url - API URL
   * @param {number} duration - 请求耗时
   * @param {number} status - 响应状态码
   */
  recordApiCall(url: string, duration: number, status: number): void {
    const key = `api_${url.replace(/[^a-zA-Z0-9]/g, '_')}`
    this.metrics.set(key, { duration, status, timestamp: Date.now() })
  }
  
  /**
   * 获取性能指标
   * @returns {Record<string, MetricValue>} 性能指标对象
   */
  getMetrics(): Record<string, MetricValue> {
    return Object.fromEntries(this.metrics)
  }

  /**
   * 清除所有指标
   */
  clearMetrics(): void {
    this.metrics.clear()
  }

  /**
   * 获取运行时间
   * @returns {number} 运行时间（毫秒）
   */
  getUptime(): number {
    return Date.now() - this.startTime
  }
}

/**
 * 全局前端监控实例
 */
export const frontendMonitor = new FrontendMonitor()