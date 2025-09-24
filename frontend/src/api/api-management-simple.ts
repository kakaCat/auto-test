import { request } from '@/utils/request'

/**
 * API管理相关接口 - 简化版
 * 使用自增ID而非UUID
 */

// 查询参数接口
interface ServiceListParams {
  keyword?: string
  serviceId?: number
  method?: string
}

interface ModuleListParams {
  system_id?: number
  keyword?: string
  method?: string
  status?: string
}

interface ApiListParams {
  system_id?: string
  module_id?: string
  enabled_only?: boolean
  keyword?: string
  method?: string
}

// 数据接口
interface ServiceData {
  name: string
  description?: string
  url?: string
  category?: string
  icon?: string
  enabled?: boolean
}

interface ApiData {
  system_id: number
  name: string
  description?: string
  url?: string
  enabled?: boolean
  tags?: string[]
}

interface TestData {
  [key: string]: any
}

interface TestConfig {
  [key: string]: any
}

interface ApiStatistics {
  total_apis: number
  enabled_apis: number
  disabled_apis: number
  apis_by_method: Record<string, number>
  apis_by_system: Record<string, number>
}

interface WorkflowStats {
  [key: string]: any
}

interface ScenarioStats {
  [key: string]: any
}

interface StatsData {
  api_stats: ApiStatistics
  workflow_stats: WorkflowStats
  scenario_stats: ScenarioStats
}

interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
}

interface ExportParams {
  [key: string]: any
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
   * @param systemId - 系统ID（自增ID）
   * @param data - 更新数据
   * @returns 更新结果
   */
  updateService(systemId: number, data: ServiceData): Promise<ApiResponse> {
    return request.put(`/api/systems/${systemId}`, data)
  },

  /**
   * 更新API
   * @param apiId - API ID（自增ID）
   * @param data - 更新数据
   * @returns 更新结果
   */
  updateApi(apiId: number, data: ApiData): Promise<ApiResponse> {
    return request.put(`/api/interfaces/${apiId}`, data)
  },

  /**
   * 删除服务（系统）
   * @param systemId - 系统ID（自增ID）
   * @returns 删除结果
   */
  deleteService(systemId: number): Promise<ApiResponse> {
    return request.delete(`/api/systems/${systemId}`)
  },

  /**
   * 删除API
   * @param apiId - API ID（自增ID）
   * @returns 删除结果
   */
  deleteApi(apiId: number): Promise<ApiResponse> {
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
   * 获取统计数据
   * @returns 统计数据
   */
  async getStats(): Promise<ApiResponse<StatsData>> {
    const response = await request.get('/api/stats')
    if (response.success) {
      return {
        success: true,
        data: {
          api_stats: {
            total_apis: response.data.api_stats?.total_apis || 0,
            enabled_apis: response.data.api_stats?.enabled_apis || 0,
            disabled_apis: response.data.api_stats?.disabled_apis || 0,
            apis_by_method: response.data.api_stats?.apis_by_method || {},
            apis_by_system: response.data.api_stats?.apis_by_system || {}
          },
          workflow_stats: response.data.workflow_stats || {},
          scenario_stats: response.data.scenario_stats || {}
        }
      }
    }
    return response
  },

  /**
   * 导入API
   * @param formData - 包含文件的表单数据
   * @returns 导入结果
   */
  importApis(formData: FormData): Promise<ApiResponse> {
    return request.post('/api/interfaces/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 导出API
   * @param params - 导出参数
   * @returns 导出结果
   */
  exportApis(params: ExportParams = {}): Promise<ApiResponse> {
    return request.get('/api/interfaces/export', params)
  }
}

export default apiManagementApi