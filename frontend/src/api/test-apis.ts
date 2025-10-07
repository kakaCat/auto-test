/**
 * API测试场景管理前端接口封装
 * 基础路径：/api/test-apis/v1
 */
import { request } from '@/utils/request'
import type { ApiResponse } from '@/types'

export interface TestApisListParams {
  keyword?: string
  api_id?: number | string
  enabled_only?: boolean
  tags?: string
  page?: number
  size?: number
}

// 保存接口的请求体定义（与后端字段对齐，snake_case）
export interface TestRequestConfigPayload {
  method: string
  url: string
  headers?: Record<string, unknown>
  query_params?: Record<string, unknown>
  body_type?: 'json' | 'form' | 'raw' | 'none'
  body?: unknown
  timeout?: number
  follow_redirects?: boolean
  validate_ssl?: boolean
}

export interface TestExpectedResponsePayload {
  status_code?: number | number[]
  headers?: Record<string, unknown>
  body?: { type: string; assertions: unknown[] }
  response_time?: number
  size?: number
}

export interface TestApiCreateData {
  api_id: number | string
  name: string
  description?: string
  enabled?: boolean
  tags?: string | string[]
  request_config?: TestRequestConfigPayload
  expected_response?: TestExpectedResponsePayload
}

export type TestApiUpdateData = Partial<TestApiCreateData>

function normalizeParams(params: TestApisListParams = {}): Record<string, unknown> {
  const p: Record<string, unknown> = { ...params }
  // 兼容 camelCase → snake_case（如有传入）
  if ((p as any).apiId !== undefined) { (p as any).api_id = (p as any).apiId; delete (p as any).apiId }
  if ((p as any).enabledOnly !== undefined) { (p as any).enabled_only = (p as any).enabledOnly; delete (p as any).enabledOnly }
  return p
}

function normalizePayload(data: Record<string, unknown>): Record<string, unknown> {
  const p: Record<string, unknown> = { ...data }
  // tags 数组转逗号字符串
  if (Array.isArray(p.tags)) {
    p.tags = (p.tags as string[]).filter(Boolean).join(',')
  }
  // 兼容 camelCase → snake_case 内嵌对象
  const rc = (p as any).requestConfig
  if (rc) {
    (p as any).request_config = {
      method: rc.method,
      url: rc.url,
      headers: rc.headers ?? {},
      query_params: rc.queryParams ?? {},
      body_type: rc.bodyType ?? 'json',
      body: rc.body ?? null,
      timeout: rc.timeout,
      follow_redirects: rc.followRedirects,
      validate_ssl: rc.validateSSL
    }
    delete (p as any).requestConfig
  }
  const er = (p as any).expectedResponse
  if (er) {
    (p as any).expected_response = {
      status_code: er.statusCode ?? er.status_code,
      headers: er.headers ?? {},
      body: er.body,
      response_time: er.responseTime ?? er.response_time,
      size: er.size
    }
    delete (p as any).expectedResponse
  }
  return p
}

export const testApisApi = {
  /**
   * 获取测试API列表
   */
  async getList(params: TestApisListParams = {}): Promise<ApiResponse> {
    const normalized = normalizeParams(params)
    return request.get('/api/test-apis/v1/test-apis', normalized)
  },

  /**
   * 获取测试API详情
   */
  async getDetail(id: number | string): Promise<ApiResponse> {
    return request.get(`/api/test-apis/v1/test-apis/${id}`)
  },

  /**
   * 创建测试API场景（保存请求体与期望响应）
   */
  async create(data: TestApiCreateData | Record<string, unknown>): Promise<ApiResponse> {
    const payload = normalizePayload(data as Record<string, unknown>)
    return request.post('/api/test-apis/v1/test-apis', payload)
  },

  /**
   * 更新测试API场景（保存请求体与期望响应）
   */
  async update(id: number | string, data: TestApiUpdateData | Record<string, unknown>): Promise<ApiResponse> {
    const payload = normalizePayload(data as Record<string, unknown>)
    return request.put(`/api/test-apis/v1/test-apis/${id}`, payload)
  }
}

export default testApisApi