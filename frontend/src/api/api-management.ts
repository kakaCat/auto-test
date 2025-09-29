import { apiHandler } from '@/utils/apiHandler'
import type { ApiResponse } from '@/types'

/**
 * API管理相关接口
 */

// 查询参数接口定义
export interface ServiceListParams {
  keyword?: string
  serviceId?: string
  method?: string
}

export interface ModuleListParams {
  system_id?: string
  keyword?: string
  method?: string
  status?: string
}

export interface ApiListParams {
  system_id?: string
  module_id?: string
  enabled_only?: boolean
  keyword?: string
  method?: string
}

// 数据接口定义
export interface ServiceData {
  name: string
  description: string
  url: string
  category: string
  icon: string
  enabled: boolean
}

export interface ApiData {
  system_id: number
  module_id?: number
  name: string
  description?: string
  method: string
  path: string
  version?: string
  status?: string
  request_format?: string
  response_format?: string
  auth_required?: number
  rate_limit?: number
  timeout?: number
  tags?: string
  request_schema?: string
  response_schema?: string
  example_request?: string
  example_response?: string
}

// 草稿正确性校验请求体

export interface TestData {
  [key: string]: any
}

export interface TestConfig {
  [key: string]: any
}

// Mock数据相关接口定义
export interface MockFieldConfig {
  name: string
  type: string
  description?: string
  required?: boolean
  example?: any
}

export interface MockConfig {
  dataType: 'object' | 'array'
  arraySize?: number
  fields: MockFieldConfig[]
}

export interface MockGenerateRequest {
  apiId: string
  config: MockConfig
}

export interface MockGenerateResponse {
  mockData: any
  config: MockConfig
  generatedAt: string
}

export interface ApiStatistics {
  total_apis: number
  [key: string]: any
}

export interface WorkflowStats {
  total_workflows: number
  [key: string]: any
}

export interface ScenarioStats {
  total_scenarios: number
  [key: string]: any
}

export interface StatsData {
  workflow_stats: WorkflowStats
  scenario_stats: ScenarioStats
  api_stats: ApiStatistics
  recent_activity: any[]
}

// API接口管理
export const apiManagementApi = {
  /**
   * 获取服务列表（系统列表）
   * @param params - 查询参数
   * @returns 服务列表数据
   */
  getServiceList(params: ServiceListParams = {}): Promise<ApiResponse> {
    return apiHandler.get('/api/systems/v1/', params)
  },

  /**
   * 获取模块列表
   * @param params - 查询参数
   * @returns 模块列表数据
   */
  getModuleList(params: ModuleListParams = {}): Promise<ApiResponse> {
    return apiHandler.get('/api/modules/v1/', params)
  },

  /**
   * 获取API详情
   * @param apiId - API ID
   * @returns API详情数据
   */
  getApiDetail(apiId: string): Promise<ApiResponse> {
    return apiHandler.get(`/api/interfaces/${apiId}`)
  },

  /**
   * 获取扁平化的API列表
   * @param params - 查询参数
   * @returns API列表数据
   */
  getApis(params: ApiListParams = {}): Promise<ApiResponse> {
    return apiHandler.get('/api/interfaces', params)
  },

  /**
   * 创建服务（系统）
   * @param data - 服务数据
   * @returns 创建结果
   */
  createService(data: ServiceData): Promise<ApiResponse> {
    return apiHandler.post('/api/systems/v1/', data)
  },

  /**
   * 创建API（模块）
   * @param data - API数据
   * @returns 创建结果
   */
  createApi(data: ApiData): Promise<ApiResponse> {
    return apiHandler.post('/api/api-interfaces/v1/', data)
  },

  /**
   * 更新服务（系统）
   * @param systemId - 系统ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  updateService(systemId: string, data: Partial<ServiceData>): Promise<ApiResponse> {
    return apiHandler.put(`/api/systems/v1/${systemId}`, data)
  },

  /**
   * 更新API
   * @param apiId - API ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  updateApi(apiId: string, data: Partial<ApiData>): Promise<ApiResponse> {
    return apiHandler.put(`/api/interfaces/${apiId}`, data)
  },

  /**
   * 删除服务（系统）
   * @param systemId - 系统ID
   * @returns 删除结果
   */
  deleteService(systemId: string): Promise<ApiResponse> {
    return apiHandler.delete(`/api/systems/v1/${systemId}`)
  },

  /**
   * 删除API
   * @param apiId - API ID
   * @returns 删除结果
   */
  deleteApi(apiId: string): Promise<ApiResponse> {
    return apiHandler.delete(`/api/interfaces/${apiId}`)
  },

  /**
   * 测试API
   * @param apiId - API ID
   * @param testData - 测试数据
   * @returns 测试结果
   */
  testApi(apiId: string, testData: TestData = {}): Promise<ApiResponse> {
    return apiHandler.post(`/api/interfaces/${apiId}/test`, testData)
  },


  /**
   * 批量测试API
   * @param apiIds - API ID数组
   * @param testConfig - 测试配置
   * @returns 批量测试结果
   */
  batchTestApis(apiIds: string[], testConfig: TestConfig = {}): Promise<ApiResponse> {
    return apiHandler.post('/api/interfaces/batch-test', { api_ids: apiIds, ...testConfig })
  },

  /**
   * 获取API统计
   * @returns API统计数据
   */
  getApiStatistics(): Promise<ApiResponse<ApiStatistics>> {
    return apiHandler.get('/api/interfaces/stats/summary')
  },

  /**
   * 获取通用统计数据
   * @returns 通用统计数据
   */
  getStats(): Promise<ApiResponse<StatsData>> {
    return Promise.all([
      apiHandler.get('/api/workflows/v1/stats'),
      apiHandler.get('/api/scenarios/v1/stats')
    ]).then(([workflowRes, scenarioRes]) => {
      return {
        success: workflowRes.success && scenarioRes.success,
        message: '获取统计数据成功',
        data: {
          workflow_stats: (workflowRes.data as any) || { total_workflows: 0 },
          scenario_stats: (scenarioRes.data as any) || { total_scenarios: 0 },
          api_stats: { total_apis: 0 },
          recent_activity: []
        },
        timestamp: new Date().toISOString()
      }
    }).catch((error: Error) => {
      console.error('获取统计数据失败:', error)
      return {
        success: false,
        message: '获取统计数据失败',
        data: {
          workflow_stats: { total_workflows: 0 },
          scenario_stats: { total_scenarios: 0 },
          api_stats: { total_apis: 0 },
          recent_activity: []
        },
        timestamp: new Date().toISOString()
      }
    })
  },

  /**
   * 导入API
   * @param formData - 包含文件的表单数据
   * @returns 导入结果
   */
  importApis(formData: FormData): Promise<ApiResponse> {
    // TODO: 后端需要实现 POST /api/import 接口
    console.warn('导入API接口未在后端实现')
    return Promise.resolve({
      success: false,
      message: '接口未实现',
      data: null,
      timestamp: new Date().toISOString()
    })
  },

  /**
   * 导出API
   * @param params - 导出参数
   * @returns 文件数据
   */
  exportApis(params: Record<string, any> = {}): Promise<Blob> {
    // TODO: 后端需要实现 GET /api/apis/export 接口
    console.warn('导出API接口未在后端实现')
    return Promise.resolve(new Blob())
  },

  /**
   * 生成Mock数据
   * @param request - Mock生成请求
   * @returns Mock数据生成结果
   */
  generateMockData(request: MockGenerateRequest): Promise<ApiResponse<MockGenerateResponse>> {
    return apiHandler.post('/api/mock/generate', request)
  },

  /**
   * 获取API的智能字段推荐
   * @param apiId - API ID
   * @returns 推荐的字段配置
   */
  getSmartFieldRecommendations(apiId: string): Promise<ApiResponse<MockFieldConfig[]>> {
    return apiHandler.get(`/api/mock/recommendations/${apiId}`)
  },

  /**
   * 保存Mock配置
   * @param apiId - API ID
   * @param config - Mock配置
   * @returns 保存结果
   */
  saveMockConfig(apiId: string, config: MockConfig): Promise<ApiResponse> {
    return apiHandler.post(`/api/mock/config/${apiId}`, config)
  },

  /**
   * 获取已保存的Mock配置
   * @param apiId - API ID
   * @returns Mock配置
   */
  getMockConfig(apiId: string): Promise<ApiResponse<MockConfig>> {
    return apiHandler.get(`/api/mock/config/${apiId}`)
  }
}

export default apiManagementApi