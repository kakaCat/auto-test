import { request } from '@/utils/request'
import { ApiResponse } from '@/types/api'

/**
 * 工作流编排相关接口
 */

// 查询参数接口定义
export interface WorkflowListParams {
  keyword?: string
  status?: string
  category?: string
  page?: number
  pageSize?: number
}

export interface ExecutionHistoryParams {
  [key: string]: any
}

// 数据接口定义
export interface WorkflowNode {
  id: string
  type: string
  [key: string]: any
}

export interface WorkflowConnection {
  id: string
  source: string
  target: string
  [key: string]: any
}

export interface WorkflowConfig {
  [key: string]: any
}

export interface WorkflowData {
  name: string
  description: string
  category: string
  version: string
  config: WorkflowConfig
  nodes: WorkflowNode[]
  connections: WorkflowConnection[]
}

export interface PublishData {
  version: string
  description: string
}

export interface ExecutionData {
  variables?: Record<string, any>
  config?: Record<string, any>
}

export interface CopyWorkflowData {
  name: string
  description: string
}

export interface TemplateData {
  name: string
  description: string
  category: string
  config: WorkflowConfig
  nodes: WorkflowNode[]
  connections: WorkflowConnection[]
}

export interface ExportParams {
  workflowIds?: string[]
  format?: string
}

// 工作流管理
export const workflowApi = {
  /**
   * 内部工具：参数键名归一化（支持常见 camelCase→snake_case）
   */
  _normalizeQueryParams(params: Record<string, any> = {}): Record<string, any> {
    const p = { ...params }
    if (p.pageSize !== undefined) {
      p.page_size = p.pageSize
      delete p.pageSize
    }
    if (p.createdTime !== undefined) {
      p.created_time = p.createdTime
      delete p.createdTime
    }
    if (Array.isArray(p.createdTimeRange)) {
      p.created_time_range = p.createdTimeRange.join(',')
      delete p.createdTimeRange
    }
    if (p.updatedTime !== undefined) {
      p.updated_time = p.updatedTime
      delete p.updatedTime
    }
    if (Array.isArray(p.updatedTimeRange)) {
      p.updated_time_range = p.updatedTimeRange.join(',')
      delete p.updatedTimeRange
    }
    if (p.enabledOnly !== undefined) {
      p.enabled_only = p.enabledOnly
      delete p.enabledOnly
    }
    return p
  },
  /**
   * 获取工作流列表
   * @param params - 查询参数
   * @returns 工作流列表数据
   */
  getWorkflowList(params: WorkflowListParams = {}): Promise<ApiResponse> {
    const normalized = (this as any)._normalizeQueryParams(params)
    return request.get('/api/workflows/v1/', normalized)
  },

  /**
   * 获取工作流详情
   * @param workflowId - 工作流ID
   * @returns 工作流详情数据
   */
  getWorkflowDetail(workflowId: string): Promise<ApiResponse> {
    return request.get(`/api/workflows/v1/${workflowId}`)
  },

  /**
   * 创建工作流
   * @param data - 工作流数据
   * @returns 创建结果
   */
  createWorkflow(data: WorkflowData): Promise<ApiResponse> {
    return request.post('/api/workflows/v1/', data)
  },

  /**
   * 更新工作流
   * @param workflowId - 工作流ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  updateWorkflow(workflowId: string, data: Partial<WorkflowData>): Promise<ApiResponse> {
    return request.put(`/api/workflows/v1/${workflowId}`, data)
  },

  /**
   * 删除工作流
   * @param workflowId - 工作流ID
   * @returns 删除结果
   */
  deleteWorkflow(workflowId: string): Promise<ApiResponse> {
    return request.delete(`/api/workflows/v1/${workflowId}`)
  },

  /**
   * 发布工作流
   * @param workflowId - 工作流ID
   * @param data - 发布数据
   * @returns 发布结果
   */
  publishWorkflow(workflowId: string, data: PublishData): Promise<ApiResponse> {
    return request.post(`/api/workflows/v1/${workflowId}/publish`, data)
  },

  /**
   * 执行工作流
   * @param workflowId - 工作流ID
   * @param data - 执行数据
   * @returns 执行结果
   */
  executeWorkflow(workflowId: string, data: ExecutionData = {}): Promise<ApiResponse> {
    return request.post(`/api/workflows/v1/${workflowId}/execute`, data)
  },

  /**
   * 停止工作流执行
   * @param workflowId - 工作流ID
   * @param executionId - 执行ID
   * @returns 停止结果
   */
  stopExecution(workflowId: string, executionId: string): Promise<ApiResponse> {
    return request.post(`/api/workflows/v1/${workflowId}/stop`, { execution_id: executionId })
  },

  /**
   * 获取执行历史
   * @param workflowId - 工作流ID
   * @param params - 查询参数
   * @returns 执行历史
   */
  getExecutionHistory(workflowId: string, params: ExecutionHistoryParams = {}): Promise<ApiResponse> {
    const normalized = (this as any)._normalizeQueryParams(params)
    return request.get(`/api/workflows/v1/${workflowId}/executions`, { params: normalized })
  },

  /**
   * 获取执行详情
   * @param executionId - 执行ID
   * @returns 执行详情
   */
  getExecutionDetail(executionId: string): Promise<ApiResponse> {
    return request.get(`/api/workflows/executions/${executionId}`)
  },

  /**
   * 获取工作流统计
   * @returns 统计数据
   */
  getWorkflowStatistics(): Promise<ApiResponse> {
    return request.get('/api/workflows/v1/stats')
  },

  /**
   * 复制工作流
   * @param workflowId - 工作流ID
   * @param data - 复制数据
   * @returns 复制结果
   */
  copyWorkflow(workflowId: string, data: CopyWorkflowData): Promise<ApiResponse> {
    return request.post(`/api/workflows/v1/${workflowId}/copy`, data)
  },


}

// 工作流模板管理 (注意：以下接口在后端未实现，仅作为前端接口定义)
export const workflowTemplateApi = {
  /**
   * 获取模板列表 (后端未实现)
   * @param params - 查询参数
   * @returns 模板列表数据
   */
  getTemplateList(params: Record<string, any> = {}): Promise<ApiResponse> {
    // TODO: 后端需要实现 /api/workflow-templates 接口
    console.warn('工作流模板接口未在后端实现')
    return Promise.resolve({
      success: true,
      message: '模拟数据',
      data: [],
      timestamp: new Date().toISOString()
    })
  },

  /**
   * 获取模板详情 (后端未实现)
   * @param templateId - 模板ID
   * @returns 模板详情数据
   */
  getTemplateDetail(templateId: string): Promise<ApiResponse> {
    // TODO: 后端需要实现 /api/workflow-templates/{id} 接口
    console.warn('工作流模板接口未在后端实现')
    return Promise.resolve({
      success: false,
      message: '接口未实现',
      data: null,
      timestamp: new Date().toISOString()
    })
  },

  /**
   * 创建模板 (后端未实现)
   * @param data - 模板数据
   * @returns 创建结果
   */
  createTemplate(data: TemplateData): Promise<ApiResponse> {
    // TODO: 后端需要实现 POST /api/workflow-templates 接口
    console.warn('工作流模板接口未在后端实现')
    return Promise.resolve({
      success: false,
      message: '接口未实现',
      data: null,
      timestamp: new Date().toISOString()
    })
  },

  /**
   * 更新模板 (后端未实现)
   * @param templateId - 模板ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  updateTemplate(templateId: string, data: Partial<TemplateData>): Promise<ApiResponse> {
    // TODO: 后端需要实现 PUT /api/workflow-templates/{id} 接口
    console.warn('工作流模板接口未在后端实现')
    return Promise.resolve({
      success: false,
      message: '接口未实现',
      data: null,
      timestamp: new Date().toISOString()
    })
  },

  /**
   * 删除模板 (后端未实现)
   * @param templateId - 模板ID
   * @returns 删除结果
   */
  deleteTemplate(templateId: string): Promise<ApiResponse> {
    // TODO: 后端需要实现 DELETE /api/workflow-templates/{id} 接口
    console.warn('工作流模板接口未在后端实现')
    return Promise.resolve({
      success: false,
      message: '接口未实现',
      data: null,
      timestamp: new Date().toISOString()
    })
  },

  /**
   * 从模板创建工作流 (后端未实现)
   * @param templateId - 模板ID
   * @param data - 工作流数据
   * @returns 创建结果
   */
  createWorkflowFromTemplate(templateId: string, data: Partial<WorkflowData>): Promise<ApiResponse> {
    // TODO: 后端需要实现 POST /api/workflow-templates/{id}/create-workflow 接口
    console.warn('工作流模板接口未在后端实现')
    return Promise.resolve({
      success: false,
      message: '接口未实现',
      data: null,
      timestamp: new Date().toISOString()
    })
  }
}

// 工作流导入导出管理 (注意：以下接口在后端未实现，仅作为前端接口定义)
export const workflowImportExportApi = {
  /**
   * 导入工作流 (后端未实现)
   * @param formData - 文件数据
   * @returns 导入结果
   */
  importWorkflow(formData: FormData): Promise<ApiResponse> {
    // TODO: 后端需要实现 POST /api/workflows/v1/import 接口
    console.warn('工作流导入接口未在后端实现')
    return Promise.resolve({
      success: false,
      message: '接口未实现',
      data: null,
      timestamp: new Date().toISOString()
    })
  },

  /**
   * 导出工作流 (后端未实现)
   * @param params - 导出参数
   * @returns 文件数据
   */
  exportWorkflow(params: ExportParams = {}): Promise<Blob> {
    // TODO: 后端需要实现 GET /api/workflows/v1/export 接口
    console.warn('工作流导出接口未在后端实现')
    return Promise.resolve(new Blob())
  }
}

export default {
  workflow: workflowApi,
  template: workflowTemplateApi,
  importExport: workflowImportExportApi
}