/**
 * 运行时API执行器（Runtime Executor）
 * 
 * 作用：
 * - 根据 ApiConfigItem 的 method + path 执行接口调用
 * - 统一使用 request 封装，返回标准 ApiResponse
 * - 记录调用耗时与状态码（若可用）到 FrontendMonitor
 * - 支持基于 TestCase 的前端直连执行与断言评估
 * 
 * 设计原则：
 * - 工具类使用静态方法
 * - 类型安全（unknown优先）
 * - 严格错误信息
 */

import { request } from '@/utils/request'
import type { ApiResponse } from '@/types'
import type { ApiConfigItem } from '@/views/page-management/types/page-config'
import type { TestCase, TestRequestConfig, TestExpectedResponse, TestAssertion, TestAssertionResult, TestResponseBodyAssertion } from '@/types/test-case'
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

  /**
   * 安全读取对象路径
   */
  private static getValueByPath(obj: unknown, path: string): unknown {
    if (!obj || typeof obj !== 'object') return undefined
    const keys = path.split('.').filter(Boolean)
    let cur: unknown = obj
    for (const k of keys) {
      if (cur && typeof cur === 'object' && k in (cur as Record<string, unknown>)) {
        cur = (cur as Record<string, unknown>)[k]
      } else {
        return undefined
      }
    }
    return cur
  }

  private static deepEqual(a: unknown, b: unknown): boolean {
    if (a === b) return true
    if (typeof a !== typeof b) return false
    if (a && b && typeof a === 'object') {
      const aa = a as Record<string, unknown>
      const bb = b as Record<string, unknown>
      const aKeys = Object.keys(aa)
      const bKeys = Object.keys(bb)
      if (aKeys.length !== bKeys.length) return false
      for (const k of aKeys) {
        if (!RuntimeExecutor.deepEqual(aa[k], bb[k])) return false
      }
      return true
    }
    return false
  }

  private static evaluateAssertion(body: unknown, assertion: TestAssertion): TestAssertionResult {
    const actual = RuntimeExecutor.getValueByPath(body, assertion.field)
    const expected = assertion.value
    let passed = false
    let message = ''
    switch (assertion.operator) {
      case 'equals':
        passed = RuntimeExecutor.deepEqual(actual, expected)
        message = passed ? '值相等' : '值不相等'
        break
      case 'not_equals':
        passed = !RuntimeExecutor.deepEqual(actual, expected)
        message = passed ? '值不相等' : '值相等'
        break
      case 'contains':
        if (typeof actual === 'string' && typeof expected === 'string') {
          passed = actual.includes(expected)
        } else if (Array.isArray(actual)) {
          passed = actual.some(v => RuntimeExecutor.deepEqual(v, expected))
        }
        message = passed ? '包含期望值' : '不包含期望值'
        break
      case 'not_contains':
        if (typeof actual === 'string' && typeof expected === 'string') {
          passed = !actual.includes(expected)
        } else if (Array.isArray(actual)) {
          passed = !actual.some(v => RuntimeExecutor.deepEqual(v, expected))
        } else {
          passed = true // 不支持的类型视为不包含
        }
        message = passed ? '不包含期望值' : '包含期望值'
        break
      case 'greater_than':
        passed = typeof actual === 'number' && typeof expected === 'number' && actual > expected
        message = passed ? '大于期望值' : '不大于期望值'
        break
      case 'less_than':
        passed = typeof actual === 'number' && typeof expected === 'number' && actual < expected
        message = passed ? '小于期望值' : '不小于期望值'
        break
      case 'exists':
        passed = actual !== undefined && actual !== null
        message = passed ? '字段存在' : '字段不存在'
        break
      case 'not_exists':
        passed = actual === undefined || actual === null
        message = passed ? '字段不存在' : '字段存在'
        break
      case 'regex':
        if (typeof actual === 'string' && typeof expected === 'string') {
          const reg = new RegExp(expected)
          passed = reg.test(actual)
        }
        message = passed ? '匹配正则' : '不匹配正则'
        break
      case 'type_of':
        if (typeof expected === 'string') {
          if (expected === 'array') {
            passed = Array.isArray(actual)
          } else {
            passed = typeof actual === expected
          }
        }
        message = passed ? '类型匹配' : '类型不匹配'
        break
      default:
        passed = false
        message = `不支持的操作符: ${assertion.operator}`
    }
    return { assertionId: assertion.id, passed, actual, expected, message }
  }

  private static computeSize(val: unknown): number {
    try {
      const enc = new TextEncoder()
      const text = typeof val === 'string' ? val : JSON.stringify(val)
      return enc.encode(text).length
    } catch {
      return 0
    }
  }

  // 将查询参数拼接到URL（支持绝对URL与相对路径）
  private static buildUrlWithQuery(url: string, params?: Record<string, unknown>): string {
    const qp = params || {}
    if (!qp || Object.keys(qp).length === 0) return url

    const appendParam = (sp: URLSearchParams, key: string, value: unknown) => {
      if (value === undefined || value === null) return
      if (Array.isArray(value)) {
        value.forEach(v => sp.append(key, String(v)))
        return
      }
      if (typeof value === 'object') {
        try {
          sp.append(key, JSON.stringify(value))
        } catch {
          sp.append(key, String(value))
        }
        return
      }
      sp.append(key, String(value))
    }

    try {
      if (/^https?:\/\//i.test(url)) {
        const u = new URL(url)
        for (const [k, v] of Object.entries(qp)) {
          appendParam(u.searchParams, k, v)
        }
        return u.toString()
      }
    } catch {
      // ignore
    }

    const [path, existingQuery = ''] = url.split('?')
    const sp = new URLSearchParams(existingQuery)
    for (const [k, v] of Object.entries(qp)) {
      appendParam(sp, k, v)
    }
    const qs = sp.toString()
    return qs ? `${path}?${qs}` : path
  }

  /**
   * 基于测试用例执行HTTP请求并进行断言评估
   */
  static async executeTestCase(testCase: TestCase): Promise<{
    testCase: TestCase
    success: boolean
    statusCode: number
    responseTime: number
    executedAt: string
    error?: string
    response?: { statusCode: number; headers: Record<string, unknown>; body: unknown }
    assertionResults?: TestAssertionResult[]
  }> {
    const cfg: TestRequestConfig = testCase.requestConfig
    const method = (cfg.method || 'GET').toUpperCase()
    const url = cfg.url || ''
    const headers: Record<string, string> = { ...(cfg.headers || {}) }

    // 处理不同body类型
    let data: unknown = undefined
    if (method !== 'GET' && method !== 'DELETE') {
      switch (cfg.bodyType) {
        case 'form': {
          const fd = new FormData()
          const b = (cfg.body ?? {}) as Record<string, unknown>
          Object.entries(b).forEach(([k, v]) => {
            if (v instanceof Blob) fd.append(k, v)
            else fd.append(k, v == null ? '' : String(v))
          })
          data = fd
          headers['Content-Type'] = 'multipart/form-data'
          break
        }
        case 'raw': {
          data = typeof cfg.body === 'string' ? cfg.body : JSON.stringify(cfg.body ?? {})
          headers['Content-Type'] = headers['Content-Type'] || 'text/plain'
          break
        }
        case 'json':
        default:
          data = cfg.body ?? {}
          headers['Content-Type'] = headers['Content-Type'] || 'application/json'
      }
    }

    const start = performance.now()
    let axiosResp: unknown
    try {
      const commonConfig = { headers, timeout: cfg.timeout ?? 30000, returnRaw: true, skipErrorHandler: true } as any
      const finalUrl = RuntimeExecutor.buildUrlWithQuery(url, cfg.queryParams || {})
      switch (method) {
        case 'GET':
          axiosResp = await request.get(finalUrl, {}, { ...commonConfig }) as unknown
          break
        case 'POST':
          axiosResp = await request.post(finalUrl, data, { ...commonConfig }) as unknown
          break
        case 'PUT':
          axiosResp = await request.put(finalUrl, data, { ...commonConfig }) as unknown
          break
        case 'DELETE':
          axiosResp = await request.delete(finalUrl, { ...commonConfig }) as unknown
          break
        case 'PATCH':
          axiosResp = await request.patch(finalUrl, data, { ...commonConfig }) as unknown
          break
        default:
          throw new Error(`不支持的HTTP方法: ${method}`)
      }
    } catch (e: unknown) {
      const duration = Math.round(performance.now() - start)
      const now = new Date().toISOString()
      return {
        testCase,
        success: false,
        statusCode: 0,
        responseTime: duration,
        executedAt: now,
        error: e instanceof Error ? e.message : '请求执行失败'
      }
    }

    const duration = Math.round(performance.now() - start)
    const now = new Date().toISOString()

    // 窄化到AxiosResponse结构
    const isAxios = (r: unknown): r is { status: number; headers: Record<string, unknown>; data: unknown } => {
      return !!r && typeof (r as any).status === 'number' && typeof (r as any).headers === 'object'
    }
    if (!isAxios(axiosResp)) {
      // 回退处理：当拦截器未返回原始响应时，视为成功但无法断言
      const statusCode = (axiosResp as any)?.success ? 200 : 500
      const body = (axiosResp as any)?.data
      return {
        testCase,
        success: Boolean((axiosResp as any)?.success),
        statusCode,
        responseTime: duration,
        executedAt: now,
        response: { statusCode, headers: {}, body }
      }
    }

    const statusCode = axiosResp.status
    const headersResp = axiosResp.headers || {}
    const bodyResp = axiosResp.data

    // 断言评估
    const expected: TestExpectedResponse | undefined = testCase.expectedResponse
    const assertionResults: TestAssertionResult[] = []
    let allPassed = true

    // 状态码断言
    if (expected && expected.statusCode != null) {
      const codes = Array.isArray(expected.statusCode) ? expected.statusCode : [expected.statusCode]
      const ok = codes.includes(statusCode)
      assertionResults.push({ assertionId: 'status_code', passed: ok, actual: statusCode, expected: codes, message: ok ? '状态码匹配' : '状态码不匹配' })
      if (!ok) allPassed = false
    }

    // 响应头断言
    if (expected && expected.headers) {
      for (const [key, val] of Object.entries(expected.headers)) {
        const actualHeader = (headersResp as Record<string, unknown>)[key.toLowerCase()] ?? (headersResp as Record<string, unknown>)[key]
        let ok = false
        if (typeof val === 'string') ok = String(actualHeader) === val
        else if (val instanceof RegExp) ok = typeof actualHeader === 'string' && val.test(actualHeader as string)
        assertionResults.push({ assertionId: `header:${key}`, passed: ok, actual: actualHeader, expected: val, message: ok ? '响应头匹配' : '响应头不匹配' })
        if (!ok) allPassed = false
      }
    }

    // 响应体断言
    const bodyAssertion: TestResponseBodyAssertion | undefined = expected?.body as TestResponseBodyAssertion | undefined
    if (bodyAssertion && Array.isArray(bodyAssertion.assertions)) {
      for (const a of bodyAssertion.assertions) {
        if (a && a.enabled !== false) {
          const result = RuntimeExecutor.evaluateAssertion(bodyResp, a)
          assertionResults.push(result)
          if (!result.passed) allPassed = false
        }
      }
      // exact类型的整体比较
      if (bodyAssertion.type === 'exact' && bodyAssertion.value !== undefined) {
        const ok = RuntimeExecutor.deepEqual(bodyResp, bodyAssertion.value)
        assertionResults.push({ assertionId: 'body_exact', passed: ok, actual: bodyResp, expected: bodyAssertion.value, message: ok ? '响应体完全匹配' : '响应体不匹配' })
        if (!ok) allPassed = false
      }
    }

    // 响应大小与耗时限制（若配置）
    const size = RuntimeExecutor.computeSize(bodyResp)
    if (expected?.responseTime != null) {
      const ok = duration <= expected.responseTime
      assertionResults.push({ assertionId: 'response_time', passed: ok, actual: duration, expected: expected.responseTime, message: ok ? '响应时间满足要求' : '响应时间超出限制' })
      if (!ok) allPassed = false
    }
    if (expected?.size != null) {
      const ok = size <= expected.size
      assertionResults.push({ assertionId: 'response_size', passed: ok, actual: size, expected: expected.size, message: ok ? '响应大小满足要求' : '响应大小超出限制' })
      if (!ok) allPassed = false
    }

    const success = allPassed

    return {
      testCase,
      success,
      statusCode,
      responseTime: duration,
      executedAt: now,
      response: { statusCode, headers: headersResp, body: bodyResp },
      assertionResults
    }
  }
}