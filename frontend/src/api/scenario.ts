import { request } from '@/utils/request'
import { ApiResponse } from '@/types/api'

/**
 * 场景管理API接口
 */

// 查询参数接口定义（对齐无分页与API上下文）
export interface ScenarioListParams {
  api_id: string
  keyword?: string
  status?: string
  tags?: string[]
  created_by?: string
  created_time_range?: [string, string]
  is_parameters_saved?: boolean
}

export interface ExecutionHistoryParams {
  [key: string]: any
}

export interface TemplateListParams {
  [key: string]: any
}

export interface TagListParams {
  [key: string]: any
}

// 数据接口定义
export interface ScenarioData {
  name: string
  description: string
  scenario_type?: 'normal' | 'exception' | 'boundary' | 'security' | 'performance'
  tags?: string[]
  steps?: StepData[]
  config?: Record<string, any>
  variables?: Record<string, any>
  is_parameters_saved?: boolean
  saved_parameters_id?: string
  status?: string
}

export interface StepData {
  id?: string
  name: string
  type: string
  config: Record<string, any>
  order?: number
}

export interface CopyData {
  name?: string
  description?: string
}

export interface ExecutionParams {
  variables?: Record<string, any>
  config?: Record<string, any>
}

export interface ReorderData {
  steps: Array<{ id: string; order: number }>
}

export interface ScenarioCreateData {
  name: string
  description: string
  scenario_type?: 'normal' | 'exception' | 'boundary' | 'security' | 'performance'
  tags?: string[]
  variables?: Record<string, any>
  config?: Record<string, any>
  api_id?: string
}

export interface ExportData {
  ids: string[]
  format: string
}

export interface TagData {
  name: string
  color?: string
  description?: string
}

// 场景管理相关接口
export const scenarioApi = {
  /**
   * 参数归一化：支持 camelCase → snake_case，并处理数组/空值
   */
  _normalizeQueryParams(params: Record<string, any> = {}): Record<string, any> {
    const p: Record<string, any> = { ...params }

    // camelCase → snake_case
    if (p.createdBy !== undefined) {
      p.created_by = p.createdBy
      delete p.createdBy
    }
    if (p.createdTimeRange !== undefined) {
      const arr = Array.isArray(p.createdTimeRange) ? p.createdTimeRange : []
      if (arr.length === 2) {
        p.created_time_range = [arr[0], arr[1]]
      }
      delete p.createdTimeRange
    }
    if (p.isParametersSaved !== undefined) {
      p.is_parameters_saved = p.isParametersSaved
      delete p.isParametersSaved
    }

    // tags 数组转逗号字符串
    if (p.tags !== undefined) {
      if (Array.isArray(p.tags)) {
        p.tags = p.tags.filter((t: any) => !!t).join(',')
      }
    }

    // 去除空字符串和空数组
    Object.keys(p).forEach((key) => {
      const val = p[key]
      if (val === '' || (Array.isArray(val) && val.length === 0)) {
        delete p[key]
      }
    })

    // 保留 api_id，按方案要求为必填

    return p
  },
  /**
   * 获取场景列表
   * @param params - 查询参数
   * @returns 场景列表数据
   */
  getList(params: ScenarioListParams): Promise<ApiResponse> {
    const normalized = (this as any)._normalizeQueryParams(params)
    return request.get('/api/scenarios/v1/', normalized)
  },

  /**
   * 获取场景详情
   * @param scenarioId - 场景ID
   * @returns 场景详情数据
   */
  getDetail(scenarioId: string): Promise<ApiResponse> {
    return request.get(`/api/scenarios/v1/${scenarioId}`)
  },

  /**
   * 创建场景
   * @param data - 场景数据
   * @returns 创建结果
   */
  create(data: ScenarioCreateData): Promise<ApiResponse> {
    return request.post('/api/scenarios/v1/', data)
  },

  /**
   * 更新场景
   * @param scenarioId - 场景ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  update(scenarioId: string, data: Partial<ScenarioData>): Promise<ApiResponse> {
    return request.put(`/api/scenarios/v1/${scenarioId}`, data)
  },

  /**
   * 删除场景
   * @param scenarioId - 场景ID
   * @returns 删除结果
   */
  delete(scenarioId: string): Promise<ApiResponse> {
    return request.delete(`/api/scenarios/v1/${scenarioId}`)
  },

  /**
   * 批量删除场景
   * @param scenarioIds - 场景ID数组
   * @returns 删除结果
   */
  batchDelete(scenarioIds: string[]): Promise<ApiResponse> {
    return request.post('/api/scenarios/batch-delete', { ids: scenarioIds })
  },

  /**
   * 复制场景
   * @param scenarioId - 场景ID
   * @param data - 复制配置
   * @returns 复制结果
   */
  copy(scenarioId: string, data: CopyData = {}): Promise<ApiResponse> {
    return request.post(`/api/scenarios/${scenarioId}/copy`, data)
  },

  /**
   * 执行场景
   * @param scenarioId - 场景ID
   * @param params - 执行参数
   * @returns 执行结果
   */
  execute(scenarioId: string, params: ExecutionParams = {}): Promise<ApiResponse> {
    return request.post(`/api/scenarios/${scenarioId}/execute`, params)
  },

  /**
   * 停止场景执行
   * @param scenarioId - 场景ID
   * @param executionId - 执行ID
   * @returns 停止结果
   */
  stop(scenarioId: string, executionId: string): Promise<ApiResponse> {
    return request.post(`/api/scenarios/${scenarioId}/executions/${executionId}/stop`)
  },

  /**
   * 获取场景执行历史
   * @param scenarioId - 场景ID
   * @param params - 查询参数
   * @returns 执行历史数据
   */
  getExecutionHistory(scenarioId: string, params: ExecutionHistoryParams = {}): Promise<ApiResponse> {
    return request.get(`/api/scenarios/v1/${scenarioId}/executions`, { params })
  },

  /**
   * 获取场景执行详情
   * @param scenarioId - 场景ID
   * @param executionId - 执行ID
   * @returns 执行详情数据
   */
  getExecutionDetail(scenarioId: string, executionId: string): Promise<ApiResponse> {
    return request.get(`/api/scenarios/v1/executions/${executionId}`)
  },

  /**
   * 获取场景统计信息
   * @returns 统计数据
   */
  getStatistics(): Promise<ApiResponse> {
    return request.get('/api/scenarios/v1/stats')
  }
,
  /**
   * 获取场景创建人列表
   * @param params - 查询参数，如 keyword
   * @returns 创建人选项列表
   */
  getCreators(params: Record<string, any> = {}): Promise<ApiResponse> {
    return request.get('/api/scenarios/v1/creators', params)
  }
}

// 场景步骤管理相关接口
export const stepApi = {
  /**
   * 获取场景步骤列表
   * @param scenarioId - 场景ID
   * @returns 步骤列表数据
   */
  getList(scenarioId: string): Promise<ApiResponse> {
    return request.get(`/api/scenarios/${scenarioId}/steps`)
  },

  /**
   * 创建场景步骤
   * @param scenarioId - 场景ID
   * @param data - 步骤数据
   * @returns 创建结果
   */
  create(scenarioId: string, data: StepData): Promise<ApiResponse> {
    return request.post(`/api/scenarios/${scenarioId}/steps`, data)
  },

  /**
   * 更新场景步骤
   * @param scenarioId - 场景ID
   * @param stepId - 步骤ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  update(scenarioId: string, stepId: string, data: Partial<StepData>): Promise<ApiResponse> {
    return request.put(`/api/scenarios/${scenarioId}/steps/${stepId}`, data)
  },

  /**
   * 删除场景步骤
   * @param scenarioId - 场景ID
   * @param stepId - 步骤ID
   * @returns 删除结果
   */
  delete(scenarioId: string, stepId: string): Promise<ApiResponse> {
    return request.delete(`/api/scenarios/${scenarioId}/steps/${stepId}`)
  },

  /**
   * 调整步骤顺序
   * @param scenarioId - 场景ID
   * @param steps - 步骤顺序数组
   * @returns 更新结果
   */
  reorder(scenarioId: string, steps: Array<{ id: string; order: number }>): Promise<ApiResponse> {
    return request.put(`/api/scenarios/${scenarioId}/steps/reorder`, { steps })
  }
}

// 场景模板管理相关接口
export const templateApi = {
  /**
   * 获取场景模板列表
   * @param params - 查询参数
   * @returns 模板列表数据
   */
  getList(params: TemplateListParams = {}): Promise<ApiResponse> {
    return request.get('/api/scenario-templates', params)
  },

  /**
   * 获取模板详情
   * @param templateId - 模板ID
   * @returns 模板详情数据
   */
  getDetail(templateId: string): Promise<ApiResponse> {
    return request.get(`/api/scenario-templates/${templateId}`)
  },

  /**
   * 从模板创建场景
   * @param templateId - 模板ID
   * @param data - 场景数据
   * @returns 创建结果
   */
  createScenario(templateId: string, data: ScenarioCreateData): Promise<ApiResponse> {
    return request.post(`/api/scenario-templates/${templateId}/create-scenario`, data)
  }
}

// 场景导入导出相关接口
export const importExportApi = {
  /**
   * 导出场景
   * @param scenarioIds - 场景ID数组
   * @param format - 导出格式
   * @returns 导出结果
   */
  exportScenarios(scenarioIds: string[], format: string = 'json'): Promise<ApiResponse> {
    return request.post('/api/scenarios/export', { ids: scenarioIds, format })
  },

  /**
   * 导入场景
   * @param formData - 文件数据
   * @returns 导入结果
   */
  importScenarios(formData: FormData): Promise<ApiResponse> {
    return request.post('/api/scenarios/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  /**
   * 验证导入文件
   * @param formData - 文件数据
   * @returns 验证结果
   */
  validateImportFile(formData: FormData): Promise<ApiResponse> {
    return request.post('/api/scenarios/validate-import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// 场景分类和标签相关接口
export const categoryApi = {
  /**
   * 获取场景分类列表
   * @returns 分类列表数据
   */
  getCategories(): Promise<ApiResponse> {
    return request.get('/api/scenario-categories')
  },

  /**
   * 获取场景标签列表
   * @param params - 查询参数
   * @returns 标签列表数据
   */
  getTags(params: TagListParams = {}): Promise<ApiResponse> {
    return request.get('/api/scenario-tags', params)
  },

  /**
   * 创建标签
   * @param data - 标签数据
   * @returns 创建结果
   */
  createTag(data: TagData): Promise<ApiResponse> {
    return request.post('/api/scenario-tags', data)
  }
}

export default {
  scenario: scenarioApi,
  step: stepApi,
  template: templateApi,
  importExport: importExportApi,
  category: categoryApi
}