/**
 * 需求管理API接口
 * Requirement Management API
 */

import { apiHandler } from '@/utils/apiHandler'
import type { ApiResponse } from '@/types'
import { request } from '@/utils/request'

// 参数与数据类型
interface RequirementListParams { [key: string]: unknown }
interface RequirementData { [key: string]: unknown }

// 需求管理API
export const requirementApi = {
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
   * 获取需求列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 需求列表
   */
  getRequirements(params: RequirementListParams = {}): Promise<ApiResponse> {
    const normalized = (this as any)._normalizeQueryParams(params)
    return apiHandler.get('/api/requirements/v1/', normalized)
  },

  /**
   * 获取需求详情
   * @param {string} id - 需求ID
   * @returns {Promise} 需求详情
   */
  getRequirement(id: string): Promise<ApiResponse> {
    return apiHandler.get(`/api/requirements/v1/${id}`)
  },

  /**
   * 创建需求
   * @param {Object} data - 需求数据
   * @returns {Promise} 创建结果
   */
  createRequirement(data: RequirementData): Promise<ApiResponse> {
    return apiHandler.post('/api/requirements/v1/', data)
  },

  /**
   * 更新需求
   * @param {string} id - 需求ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  updateRequirement(id: string, data: RequirementData): Promise<ApiResponse> {
    return apiHandler.put(`/api/requirements/v1/${id}`, data)
  },

  /**
   * 删除需求
   * @param {string} id - 需求ID
   * @returns {Promise} 删除结果
   */
  deleteRequirement(id: string): Promise<ApiResponse> {
    return apiHandler.delete(`/api/requirements/v1/${id}`)
  },

  /**
   * 搜索需求
   * @param {Object} query - 搜索条件
   * @returns {Promise} 搜索结果
   */
  searchRequirements(query: RequirementData): Promise<ApiResponse> {
    return apiHandler.post('/api/requirements/v1/search', query)
  },

  /**
   * 获取需求树形结构
   * @param {Object} params - 查询参数
   * @returns {Promise} 树形数据
   */
  getRequirementTree(params: RequirementListParams = {}): Promise<ApiResponse> {
    const normalized = (this as any)._normalizeQueryParams(params)
    return apiHandler.get('/api/requirements/v1/tree', normalized)
  },

  /**
   * 获取项目列表
   * @returns {Promise} 项目列表
   */
  getProjects(): Promise<ApiResponse> {
    return apiHandler.get('/api/requirements/v1/projects')
  },

  /**
   * 创建项目
   * @param {Object} data - 项目数据
   * @returns {Promise} 创建结果
   */
  createProject(data: RequirementData): Promise<ApiResponse> {
    return apiHandler.post('/api/requirements/v1/projects', data)
  },

  /**
   * 获取需求关联的场景
   * @param {string} requirementId - 需求ID
   * @returns {Promise} 关联场景列表
   */
  getAssociatedScenarios(requirementId: string): Promise<ApiResponse> {
    return apiHandler.get(`/api/requirements/v1/${requirementId}/scenarios`)
  },

  /**
   * 关联需求与场景
   * @param {string} requirementId - 需求ID
   * @param {Array} scenarioIds - 场景ID列表
   * @returns {Promise} 关联结果
   */
  linkScenarios(requirementId: string, scenarioIds: string[]): Promise<ApiResponse> {
    return apiHandler.post(`/api/requirements/v1/${requirementId}/scenarios`, {
      scenarioIds
    })
  },

  /**
   * 取消需求与场景关联
   * @param {string} requirementId - 需求ID
   * @param {string} scenarioId - 场景ID
   * @returns {Promise} 取消关联结果
   */
  unlinkScenario(requirementId: string, scenarioId: string): Promise<ApiResponse> {
    return request.delete(`/api/requirements/v1/${requirementId}/scenarios/${scenarioId}`)
  },

  /**
   * 获取需求的测试计划
   * @param {string} requirementId - 需求ID
   * @returns {Promise} 测试计划列表
   */
  getTestPlans(requirementId: string): Promise<ApiResponse> {
    return request.get(`/api/requirements/v1/${requirementId}/test-plans`)
  },

  /**
   * 创建测试计划
   * @param {Object} data - 测试计划数据
   * @returns {Promise} 创建结果
   */
  createTestPlan(data: RequirementData): Promise<ApiResponse> {
    return request.post('/api/requirements/v1/test-plans', data)
  },

  /**
   * 更新测试计划
   * @param {string} planId - 计划ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  updateTestPlan(planId: string, data: RequirementData): Promise<ApiResponse> {
    return request.put(`/api/requirements/v1/test-plans/${planId}`, data)
  },

  /**
   * 获取需求执行统计
   * @param {string} requirementId - 需求ID
   * @returns {Promise} 执行统计数据
   */
  getExecutionStats(requirementId: string): Promise<ApiResponse> {
    return request.get(`/api/requirements/v1/${requirementId}/stats`)
  },

  /**
   * 获取覆盖率分析
   * @param {Object} params - 分析参数
   * @returns {Promise} 覆盖率分析结果
   */
  getCoverageAnalysis(params: RequirementListParams = {}): Promise<ApiResponse> {
    const normalized = (this as any)._normalizeQueryParams(params)
    return request.get('/api/requirements/v1/coverage-analysis', normalized)
  },

  /**
   * 生成需求测试报告
   * @param {Object} params - 报告参数
   * @returns {Promise} 报告数据
   */
  generateReport(params: RequirementListParams = {}): Promise<ApiResponse> {
    const normalized = (this as any)._normalizeQueryParams(params)
    return request.post('/api/requirements/v1/reports', normalized)
  },

  /**
   * 导入需求
   * @param {FormData} formData - 文件数据
   * @returns {Promise} 导入结果
   */
  importRequirements(formData: FormData): Promise<ApiResponse> {
    return request.post('/api/requirements/v1/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 导出需求
   * @param {Object} params - 导出参数
   * @returns {Promise} 导出文件
   */
  exportRequirements(params: RequirementListParams = {}): Promise<unknown> {
    // 注意：此处期望返回文件流（blob），因此类型为 unknown
    const normalized = (this as any)._normalizeQueryParams(params)
    return request.get('/api/requirements/v1/export', normalized, { responseType: 'blob' })
  },

  /**
   * 批量操作需求
   * @param {Object} data - 批量操作数据
   * @returns {Promise} 操作结果
   */
  batchOperateRequirements(data: RequirementData): Promise<ApiResponse> {
    return request.post('/api/requirements/v1/batch', data)
  }
}

export default requirementApi