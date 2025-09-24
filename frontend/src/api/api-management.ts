import { request } from '@/utils/request'

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
  system_id: string
  name: string
  description: string
  url: string
  enabled: boolean
  tags: string[]
}

export interface TestData {
  [key: string]: any
}

export interface TestConfig {
  [key: string]: any
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

export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data: T
}

// API接口管理
export const apiManagementApi = {
  /**
   * 获取服务列表（系统列表）
   * @param params - 查询参数
   * @returns 服务列表数据
   */
  getServiceList(params: ServiceListParams = {}): Promise<ApiResponse> {
    return request.get('/api/systems', params)
  },

  /**
   * 获取模块列表
   * @param params - 查询参数
   * @returns 模块列表数据
   */
  getModuleList(params: ModuleListParams = {}): Promise<ApiResponse> {
    return request.get('/api/modules', params)
  },

  /**
   * 获取API详情
   * @param apiId - API ID
   * @returns API详情数据
   */
  getApiDetail(apiId: string): Promise<ApiResponse> {
    return request.get(`/api/interfaces/${apiId}`)
  },

  /**
   * 获取扁平化的API列表
   * @param params - 查询参数
   * @returns API列表数据
   */
  getApis(params: ApiListParams = {}): Promise<ApiResponse> {
    return request.get('/api/interfaces', params)
  },

  /**
   * 创建服务（系统）
   * @param data - 服务数据
   * @returns 创建结果
   */
  createService(data: ServiceData): Promise<ApiResponse> {
    return request.post('/api/systems', data)
  },

  /**
   * 创建API（模块）
   * @param data - API数据
   * @returns 创建结果
   */
  createApi(data: ApiData): Promise<ApiResponse> {
    return request.post('/api/interfaces', data)
  },

  /**
   * 更新服务（系统）
   * @param systemId - 系统ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  updateService(systemId: string, data: Partial<ServiceData>): Promise<ApiResponse> {
    return request.put(`/api/systems/${systemId}`, data)
  },

  /**
   * 更新API
   * @param apiId - API ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  updateApi(apiId: string, data: Partial<ApiData>): Promise<ApiResponse> {
    return request.put(`/api/interfaces/${apiId}`, data)
  },

  /**
   * 删除服务（系统）
   * @param systemId - 系统ID
   * @returns 删除结果
   */
  deleteService(systemId: string): Promise<ApiResponse> {
    return request.delete(`/api/systems/${systemId}`)
  },

  /**
   * 删除API
   * @param apiId - API ID
   * @returns 删除结果
   */
  deleteApi(apiId: string): Promise<ApiResponse> {
    return request.delete(`/api/interfaces/${apiId}`)
  },

  /**
   * 测试API
   * @param apiId - API ID
   * @param testData - 测试数据
   * @returns 测试结果
   */
  testApi(apiId: string, testData: TestData = {}): Promise<ApiResponse> {
    return request.post(`/api/interfaces/${apiId}/test`, testData)
  },

  /**
   * 批量测试API
   * @param apiIds - API ID数组
   * @param testConfig - 测试配置
   * @returns 批量测试结果
   */
  batchTestApis(apiIds: string[], testConfig: TestConfig = {}): Promise<ApiResponse> {
    return request.post('/api/interfaces/batch-test', { api_ids: apiIds, ...testConfig })
  },

  /**
   * 获取API统计
   * @returns API统计数据
   */
  getApiStatistics(): Promise<ApiResponse<ApiStatistics>> {
    return request.get('/api/interfaces/stats/summary')
  },

  /**
   * 获取通用统计数据
   * @returns 通用统计数据
   */
  getStats(): Promise<ApiResponse<StatsData>> {
    return Promise.all([
      request.get('/api/workflows/stats'),
      request.get('/api/scenarios/stats')
    ]).then(([workflowResponse, scenarioResponse]) => {
      return {
        success: true,
        message: '获取统计数据成功',
        data: {
          workflow_stats: workflowResponse.data,
          scenario_stats: scenarioResponse.data,
          api_stats: {
            total_apis: 0 // 暂时使用默认值
          },
          recent_activity: []
        }
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
        }
      }
    })
  },

  /**
   * 导入API
   * @param formData - 包含文件的表单数据
   * @returns 导入结果
   */
  importApis(formData: FormData): Promise<ApiResponse> {
    return request.upload('/api/interfaces/import', formData)
  },

  /**
   * 导出API
   * @param params - 导出参数
   * @returns 导出文件
   */
  exportApis(params: Record<string, any> = {}): Promise<Blob> {
    return request.download('/api/interfaces/export', params, 'apis.json')
  }
}

export default apiManagementApi