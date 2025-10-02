/**
 * 页面管理API接口
 * Page Management API
 */

import { apiHandler } from '@/utils/apiHandler'
import type { ApiResponse } from '@/types'

// 查询参数与数据类型
interface PageListParams {
  [key: string]: unknown
}

interface PageData {
  [key: string]: unknown
}

// 页面管理API
export const pageApi = {
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
    if (p.updatedTime !== undefined) {
      p.updated_time = p.updatedTime
      delete p.updatedTime
    }
    if (Array.isArray(p.createdTimeRange)) {
      p.created_time_range = p.createdTimeRange.join(',')
      delete p.createdTimeRange
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
   * 获取页面列表
   * @param {Object} params - 查询参数
   * @returns {Promise} 页面列表
   */
  getPages(params: PageListParams = {}): Promise<ApiResponse> {
    const normalized = (this as any)._normalizeQueryParams(params)
    return apiHandler.get('/api/pages/v1/', normalized)
  },

  /**
   * 根据ID获取页面详情
   * @param {number} pageId - 页面ID
   * @returns {Promise} 页面详情
   */
  getPageById(pageId: number | string): Promise<ApiResponse> {
    return apiHandler.get(`/api/pages/v1/${pageId}`)
  },

  /**
   * 创建页面
   * @param {Object} data - 页面数据
   * @returns {Promise} 创建结果
   */
  createPage(data: PageData): Promise<ApiResponse> {
    return apiHandler.post('/api/pages/v1/', data)
  },

  /**
   * 更新页面
   * @param {number} pageId - 页面ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  updatePage(pageId: number | string, data: PageData): Promise<ApiResponse> {
    return apiHandler.put(`/api/pages/v1/${pageId}`, data)
  },

  /**
   * 删除页面
   * @param {number} pageId - 页面ID
   * @returns {Promise} 删除结果
   */
  deletePage(pageId: number | string): Promise<ApiResponse> {
    return apiHandler.delete(`/api/pages/v1/${pageId}`)
  },

  /**
   * 搜索页面
   * @param {Object} query - 搜索条件
   * @returns {Promise} 搜索结果
   */
  searchPages(query: PageData): Promise<ApiResponse> {
    return apiHandler.post('/api/pages/v1/search', query)
  },

  /**
   * 简单搜索页面（GET方式）
   * @param {Object} params - 搜索参数
   * @returns {Promise} 搜索结果
   */
  searchPagesSimple(params: PageListParams = {}): Promise<ApiResponse> {
    const normalized = (this as any)._normalizeQueryParams(params)
    return apiHandler.get('/api/pages/v1/search/simple', normalized)
  },

  /**
   * 获取页面的API列表
   * @param {number} pageId - 页面ID
   * @returns {Promise} API列表
   */
  getPageApis(pageId: number | string): Promise<ApiResponse> {
    return apiHandler.get(`/api/pages/v1/${pageId}/apis`)
  },

  /**
   * 为页面添加API关联
   * @param {number} pageId - 页面ID
   * @param {Object} data - API关联数据
   * @returns {Promise} 添加结果
   */
  addPageApi(pageId: number | string, data: PageData): Promise<ApiResponse> {
    return apiHandler.post(`/api/pages/v1/${pageId}/apis`, data)
  },

  /**
   * 更新页面API关联
   * @param {number} relationId - 关联ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新结果
   */
  updatePageApi(relationId: number | string, data: PageData): Promise<ApiResponse> {
    return apiHandler.put(`/api/page-apis/v1/${relationId}`, data)
  },

  /**
   * 删除页面API关联
   * @param {number} relationId - 关联ID
   * @returns {Promise} 删除结果
   */
  deletePageApi(relationId: number | string): Promise<ApiResponse> {
    return apiHandler.delete(`/api/page-apis/v1/${relationId}`)
  },

  /**
   * 批量管理页面API关联
   * @param {number} pageId - 页面ID
   * @param {Object} data - 批量操作数据
   * @returns {Promise} 操作结果
   */
  batchManagePageApis(pageId: number | string, data: PageData): Promise<ApiResponse> {
    return apiHandler.post(`/api/pages/v1/${pageId}/apis/batch`, data)
  },

  /**
   * 获取页面统计概览
   * @returns {Promise} 统计数据
   */
  getPagesStats(): Promise<ApiResponse> {
    return apiHandler.get('/api/pages/v1/stats/overview')
  },

  /**
   * 获取页面类型列表
   * @returns {Promise} 页面类型列表
   */
  getPageTypes(): Promise<ApiResponse> {
    return apiHandler.get('/api/pages/v1/types/list')
  },

  /**
   * 获取执行类型列表
   * @returns {Promise} 执行类型列表
   */
  getExecutionTypes(): Promise<ApiResponse> {
    return apiHandler.get('/api/pages/v1/execution-types/list')
  },

  /**
   * 批量更新页面状态
   * @param {Array} pageIds - 页面ID列表
   * @param {string} status - 目标状态
   * @returns {Promise} 更新结果
   */
  batchUpdatePageStatus(pageIds: Array<number | string>, status: string): Promise<ApiResponse> {
    return apiHandler.post('/api/pages/v1/batch/status', { page_ids: pageIds, status })
  },

  /**
   * 批量启用页面
   * @param {Array} pageIds - 页面ID列表
   * @returns {Promise} 启用结果
   */
  batchEnable(pageIds: Array<number | string>): Promise<ApiResponse> {
    return apiHandler.post('/api/pages/v1/batch/enable', { page_ids: pageIds })
  },

  /**
   * 批量禁用页面
   * @param {Array} pageIds - 页面ID列表
   * @returns {Promise} 禁用结果
   */
  batchDisable(pageIds: Array<number | string>): Promise<ApiResponse> {
    return apiHandler.post('/api/pages/v1/batch/disable', { page_ids: pageIds })
  },

  /**
   * 批量删除页面
   * @param {Array} pageIds - 页面ID列表
   * @returns {Promise} 删除结果
   */
  batchDeletePages(pageIds: Array<number | string>): Promise<ApiResponse> {
    return apiHandler.post('/api/pages/v1/batch/delete', { page_ids: pageIds })
  },

  /**
   * 批量导出页面
   * @param {Array} pageIds - 页面ID列表
   * @param {string} format - 导出格式
   * @returns {Promise} 导出结果
   */
  batchExport(pageIds: Array<number | string>, format: string = 'json'): Promise<ApiResponse> {
    return apiHandler.post('/api/pages/v1/batch/export', { page_ids: pageIds, format })
  },

  /**
   * 导入页面数据
   * @param {FormData} formData - 包含文件的表单数据
   * @returns {Promise} 导入结果
   */
  importPages(formData: FormData): Promise<ApiResponse> {
    return apiHandler.post('/api/pages/v1/import/data', formData)
  }
}

// 页面管理相关的工具函数
export const pageUtils = {
  /**
   * 格式化页面类型显示
   * @param {string} type - 页面类型
   * @returns {string} 显示文本
   */
  formatPageType(type: string): string {
    const typeMap: Record<string, string> = {
      page: '页面',
      modal: '弹框',
      drawer: '抽屉',
      tab: '标签页',
      step: '步骤页'
    }
    return typeMap[type] || type
  },

  /**
   * 格式化页面状态显示
   * @param {string} status - 页面状态
   * @returns {string} 显示文本
   */
  formatPageStatus(status: string): string {
    const statusMap: Record<string, string> = {
      active: '活跃',
      inactive: '非活跃',
      draft: '草稿'
    }
    return statusMap[status] || status
  },

  /**
   * 格式化执行类型显示
   * @param {string} type - 执行类型
   * @returns {string} 显示文本
   */
  formatExecutionType(type: string): string {
    const typeMap: Record<string, string> = {
      parallel: '并行',
      serial: '串行'
    }
    return typeMap[type] || type
  },

  /**
   * 获取页面类型颜色
   * @param {string} type - 页面类型
   * @returns {string} 颜色类型
   */
  getPageTypeColor(type: string): string {
    const colorMap: Record<string, string> = {
      page: '',
      modal: 'warning',
      drawer: 'info',
      tab: 'success',
      step: 'primary'
    }
    return colorMap[type] || ''
  },

  /**
   * 获取页面状态颜色
   * @param {string} status - 页面状态
   * @returns {string} 颜色类型
   */
  getPageStatusColor(status: string): string {
    const colorMap: Record<string, string> = {
      active: 'success',
      inactive: 'info',
      draft: 'warning'
    }
    return colorMap[status] || ''
  },

  /**
   * 获取HTTP方法颜色
   * @param {string} method - HTTP方法
   * @returns {string} 颜色类型
   */
  getMethodColor(method: string): string {
    const colorMap: Record<string, string> = {
      GET: 'success',
      POST: 'primary',
      PUT: 'warning',
      DELETE: 'danger',
      PATCH: 'info'
    }
    return colorMap[method] || ''
  },

  /**
   * 验证路由路径格式
   * @param {string} path - 路由路径
   * @returns {boolean} 是否有效
   */
  validateRoutePath(path: string): boolean {
    if (!path) return true // 允许为空
    return /^\/[a-zA-Z0-9\-_\/]*$/.test(path)
  },

  /**
   * 验证JSON格式
   * @param {string} jsonStr - JSON字符串
   * @returns {boolean} 是否有效
   */
  validateJSON(jsonStr: string): boolean {
    if (!jsonStr.trim()) return true
    try {
      JSON.parse(jsonStr)
      return true
    } catch {
      return false
    }
  },

  /**
   * 生成页面树形数据
   * @param {Array} pages - 页面列表
   * @param {Array} systems - 系统列表
   * @returns {Array} 树形数据
   */
  buildPageTree(pages: Array<Record<string, any>>, systems: Array<Record<string, any>>): Array<Record<string, any>> {
    const tree: Array<Record<string, any>> = []
    
    systems.forEach(system => {
      const systemPages = pages.filter(page => page.system_id === system.id)
      
      const systemNode: Record<string, any> = {
        id: `system-${system.id}`,
        label: system.name,
        type: 'system',
        system_id: system.id,
        children: [] as Array<Record<string, any>>
      }
      
      systemPages.forEach(page => {
        systemNode.children.push({
          id: `page-${page.id}`,
          label: page.name,
          type: 'page',
          page_id: page.id,
          system_id: system.id,
          page_type: page.page_type,
          status: page.status,
          api_count: page.api_count || 0
        })
      })
      
      tree.push(systemNode)
    })
    
    return tree
  }
}

export default {
  pageApi,
  pageUtils
}