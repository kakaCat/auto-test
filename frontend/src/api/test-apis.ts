/**
 * 测试API管理前端接口封装
 * 基础路径：/api/test-apis/v1
 */
import { apiHandler } from '@/utils/apiHandler'
import type { ApiResponse } from '@/types'

export interface TestApisListParams {
  keyword?: string
  api_id?: number | string
  enabled_only?: boolean
  tags?: string
  page?: number
  size?: number
}

function normalizeParams(params: Record<string, any> = {}) {
  const p = { ...params }
  // 兼容 camelCase → snake_case（如有传入）
  if (p.apiId !== undefined) { p.api_id = p.apiId; delete p.apiId }
  if (p.enabledOnly !== undefined) { p.enabled_only = p.enabledOnly; delete p.enabledOnly }
  return p
}

export const testApisApi = {
  /**
   * 获取测试API列表
   */
  async getList(params: TestApisListParams = {}): Promise<ApiResponse> {
    const normalized = normalizeParams(params)
    return apiHandler.get('/api/test-apis/v1/test-apis', normalized)
  },

  /**
   * 获取测试API详情（预留，当前页面未用到）
   */
  async getDetail(id: number | string): Promise<ApiResponse> {
    return apiHandler.get(`/api/test-apis/v1/test-apis/${id}`)
  }
}

export default testApisApi