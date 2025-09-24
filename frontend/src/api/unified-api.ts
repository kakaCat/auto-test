/**
 * 统一API接口模块 (Unified API Module)
 * 
 * 功能说明：
 * - 适配新的统一后端架构
 * - 提供完整的系统和模块管理API接口
 * - 兼容旧版API调用方式
 * - 统一的错误处理和响应格式
 * 
 * 架构特点：
 * - 使用新的统一API端点 (端口8003)
 * - 支持系统管理、模块管理、API管理
 * - 统一的认证和权限控制
 * - 完整的CRUD操作支持
 * 
 * 兼容性：
 * - 保持与旧版API相同的接口签名
 * - 自动处理数据格式转换
 * - 向后兼容的错误处理
 * 
 * @author AI Assistant
 * @version 2.0.0
 * @since 2024
 */

import { request } from '@/utils/request'

// 统一API基础配置
const UNIFIED_API_BASE = 'http://localhost:8000'

// 查询参数接口
interface SystemListParams {
  keyword?: string
  category?: string
  enabled_only?: boolean
  page?: number
  page_size?: number
}

interface ModuleListParams {
  system_id?: string
  keyword?: string
  enabled_only?: boolean
  tags?: string
  page?: number
  page_size?: number
}

interface TagListParams {
  keyword?: string
  page?: number
  page_size?: number
}

interface LogListParams {
  system_id?: string
  module_id?: string
  level?: string
  start_time?: string
  end_time?: string
  page?: number
  page_size?: number
}

interface MetricsParams {
  system_id?: string
  module_id?: string
  start_time?: string
  end_time?: string
  metric_type?: string
}

// 数据接口
interface SystemData {
  name: string
  description?: string
  category?: string
  icon?: string
  enabled?: boolean
  url?: string
  metadata?: Record<string, any>
}

interface ModuleData {
  system_id: string
  name: string
  description?: string
  path?: string
  method?: string
  enabled?: boolean
  version?: string
  module_type?: string
  tags?: string[]
  config?: Record<string, any>
}

interface BatchOperationData {
  system_ids?: string[]
  module_ids?: string[]
  action: 'enable' | 'disable' | 'delete'
}

interface TagData {
  name: string
  description?: string
  color?: string
}

interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
}

interface RequestConfig {
  baseURL?: string
  [key: string]: any
}

/**
 * 创建统一API请求实例
 * 使用新的统一API服务端点
 */
const unifiedRequest = {
  get(url: string, params: Record<string, any> = {}, config: RequestConfig = {}): Promise<ApiResponse> {
    return request.get(url, params, {
      baseURL: UNIFIED_API_BASE,
      ...config
    })
  },
  
  post(url: string, data: Record<string, any> = {}, config: RequestConfig = {}): Promise<ApiResponse> {
    return request.post(url, data, {
      baseURL: UNIFIED_API_BASE,
      ...config
    })
  },
  
  put(url: string, data: Record<string, any> = {}, config: RequestConfig = {}): Promise<ApiResponse> {
    return request.put(url, data, {
      baseURL: UNIFIED_API_BASE,
      ...config
    })
  },
  
  delete(url: string, config: RequestConfig = {}): Promise<ApiResponse> {
    return request.delete(url, {
      baseURL: UNIFIED_API_BASE,
      ...config
    })
  },
  
  patch(url: string, data: Record<string, any> = {}, config: RequestConfig = {}): Promise<ApiResponse> {
    return request.patch(url, data, {
      baseURL: UNIFIED_API_BASE,
      ...config
    })
  }
}

/**
 * 系统管理API (System Management API)
 * 
 * 功能范围：
 * - 系统的完整生命周期管理
 * - 系统分类和标签管理
 * - 系统状态监控和统计
 * - 批量操作支持
 */
export const unifiedSystemApi = {
  /**
   * 获取系统列表
   * @param params - 查询参数
   * @returns 系统列表数据
   */
  getList(params: SystemListParams = {}): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/systems', params)
  },

  /**
   * 获取系统详情
   * @param systemId - 系统ID
   * @returns 系统详情数据
   */
  getDetail(systemId: string): Promise<ApiResponse> {
    return unifiedRequest.get(`/api/v1/systems/${systemId}`)
  },

  /**
   * 创建系统
   * @param data - 系统数据
   * @returns 创建结果
   */
  create(data: SystemData): Promise<ApiResponse> {
    return unifiedRequest.post('/api/v1/systems', data)
  },

  /**
   * 更新系统
   * @param systemId - 系统ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  update(systemId: string, data: SystemData): Promise<ApiResponse> {
    return unifiedRequest.put(`/api/v1/systems/${systemId}`, data)
  },

  /**
   * 删除系统
   * @param systemId - 系统ID
   * @returns 删除结果
   */
  delete(systemId: string): Promise<ApiResponse> {
    return unifiedRequest.delete(`/api/v1/systems/${systemId}`)
  },

  /**
   * 切换系统启用状态
   * @param systemId - 系统ID
   * @param enabled - 启用状态
   * @returns 切换结果
   */
  toggleEnabled(systemId: string, enabled: boolean): Promise<ApiResponse> {
    return unifiedRequest.patch(`/api/v1/systems/${systemId}/status`, { enabled })
  },

  /**
   * 批量操作系统
   * @param data - 批量操作数据
   * @returns 批量操作结果
   */
  batchOperation(data: BatchOperationData): Promise<ApiResponse> {
    return unifiedRequest.post('/api/v1/systems/batch', data)
  },

  /**
   * 获取系统统计信息
   * @returns 统计数据
   */
  getStatistics(): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/systems/statistics')
  },

  /**
   * 获取系统分类列表
   * @returns 分类列表
   */
  getCategories(): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/systems/categories')
  }
}

/**
 * 模块管理API (Module Management API)
 * 
 * 功能范围：
 * - 模块的完整生命周期管理
 * - 模块标签和分类管理
 * - 模块与系统的关联管理
 * - 模块使用统计和监控
 */
export const unifiedModuleApi = {
  /**
   * 获取模块列表
   * @param params - 查询参数
   * @returns 模块列表数据
   */
  getList(params: ModuleListParams = {}): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/modules', params)
  },

  /**
   * 根据系统ID获取模块列表
   * @param systemId - 系统ID
   * @param params - 查询参数
   * @returns 模块列表数据
   */
  getBySystem(systemId: string, params: ModuleListParams = {}): Promise<ApiResponse> {
    return unifiedRequest.get(`/api/v1/systems/${systemId}/modules`, params)
  },

  /**
   * 获取模块详情
   * @param moduleId - 模块ID
   * @returns 模块详情数据
   */
  getDetail(moduleId: string): Promise<ApiResponse> {
    return unifiedRequest.get(`/api/v1/modules/${moduleId}`)
  },

  /**
   * 创建模块
   * @param data - 模块数据
   * @returns 创建结果
   */
  create(data: ModuleData): Promise<ApiResponse> {
    return unifiedRequest.post('/api/v1/modules', data)
  },

  /**
   * 更新模块
   * @param moduleId - 模块ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  update(moduleId: string, data: ModuleData): Promise<ApiResponse> {
    return unifiedRequest.put(`/api/v1/modules/${moduleId}`, data)
  },

  /**
   * 删除模块
   * @param moduleId - 模块ID
   * @returns 删除结果
   */
  delete(moduleId: string): Promise<ApiResponse> {
    return unifiedRequest.delete(`/api/v1/modules/${moduleId}`)
  },

  /**
   * 切换模块启用状态
   * @param moduleId - 模块ID
   * @param enabled - 启用状态
   * @returns 切换结果
   */
  toggleEnabled(moduleId: string, enabled: boolean): Promise<ApiResponse> {
    return unifiedRequest.patch(`/api/v1/modules/${moduleId}/status`, { enabled })
  },

  /**
   * 批量操作模块
   * @param data - 批量操作数据
   * @returns 批量操作结果
   */
  batchOperation(data: BatchOperationData): Promise<ApiResponse> {
    return unifiedRequest.post('/api/v1/modules/batch', data)
  },

  /**
   * 移动模块到其他系统
   * @param moduleId - 模块ID
   * @param targetSystemId - 目标系统ID
   * @returns 移动结果
   */
  moveToSystem(moduleId: string, targetSystemId: string): Promise<ApiResponse> {
    return unifiedRequest.patch(`/api/v1/modules/${moduleId}/move`, {
      target_system_id: targetSystemId
    })
  },

  /**
   * 获取模块使用统计
   * @param moduleId - 模块ID
   * @returns 使用统计数据
   */
  getUsageStatistics(moduleId: string): Promise<ApiResponse> {
    return unifiedRequest.get(`/api/v1/modules/${moduleId}/statistics`)
  },

  /**
   * 获取模块标签列表
   * @param params - 查询参数
   * @returns 标签列表
   */
  getTags(params: TagListParams = {}): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/modules/tags', params)
  }
}

/**
 * 分类和标签管理API (Category and Tag Management API)
 * 
 * 功能范围：
 * - 系统分类管理
 * - 模块标签管理
 * - 分类和标签的CRUD操作
 */
export const unifiedCategoryApi = {
  /**
   * 获取系统分类列表
   * @returns 分类列表
   */
  getSystemCategories(): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/categories/systems')
  },

  /**
   * 获取模块标签列表
   * @param params - 查询参数
   * @returns 标签列表
   */
  getModuleTags(params: TagListParams = {}): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/tags/modules', params)
  },

  /**
   * 创建标签
   * @param data - 标签数据
   * @returns 创建结果
   */
  createTag(data: TagData): Promise<ApiResponse> {
    return unifiedRequest.post('/api/v1/tags', data)
  },

  /**
   * 更新标签
   * @param tagId - 标签ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  updateTag(tagId: string, data: TagData): Promise<ApiResponse> {
    return unifiedRequest.put(`/api/v1/tags/${tagId}`, data)
  },

  /**
   * 删除标签
   * @param tagId - 标签ID
   * @returns 删除结果
   */
  deleteTag(tagId: string): Promise<ApiResponse> {
    return unifiedRequest.delete(`/api/v1/tags/${tagId}`)
  }
}

/**
 * 日志管理API (Log Management API)
 * 
 * 功能范围：
 * - 系统和模块日志查询
 * - 日志统计和分析
 * - 日志级别过滤
 */
export const unifiedLogApi = {
  /**
   * 获取日志列表
   * @param params - 查询参数
   * @returns 日志列表数据
   */
  getList(params: LogListParams = {}): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/logs', params)
  },

  /**
   * 获取日志统计信息
   * @param params - 查询参数
   * @returns 日志统计数据
   */
  getStatistics(params: LogListParams = {}): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/logs/statistics', params)
  }
}

/**
 * 监控API (Monitor API)
 * 
 * 功能范围：
 * - 系统健康状态监控
 * - 性能指标收集
 * - 监控数据统计
 */
export const unifiedMonitorApi = {
  /**
   * 获取健康状态
   * @param systemId - 系统ID（可选）
   * @returns 健康状态数据
   */
  getHealthStatus(systemId: string | null = null): Promise<ApiResponse> {
    const url = systemId ? `/api/v1/monitor/health/${systemId}` : '/api/v1/monitor/health'
    return unifiedRequest.get(url)
  },

  /**
   * 获取监控概览
   * @returns 监控概览数据
   */
  getOverview(): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/monitor/overview')
  },

  /**
   * 获取性能指标
   * @param params - 查询参数
   * @returns 性能指标数据
   */
  getMetrics(params: MetricsParams = {}): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/monitor/metrics', params)
  }
}

/**
 * API管理兼容接口 (API Management Compatibility)
 * 
 * 功能范围：
 * - 兼容旧版API管理接口
 * - 统一的数据格式转换
 */
export const unifiedApiManagementApi = {
  /**
   * 获取统计数据
   * @returns 统计数据
   */
  getStats(): Promise<ApiResponse> {
    return unifiedRequest.get('/api/v1/stats')
  },

  /**
   * 获取服务列表（兼容接口）
   * @param params - 查询参数
   * @returns 服务列表数据
   */
  getServiceList(params: SystemListParams = {}): Promise<ApiResponse> {
    return unifiedSystemApi.getList(params)
  },

  /**
   * 获取模块列表（兼容接口）
   * @param params - 查询参数
   * @returns 模块列表数据
   */
  getModuleList(params: ModuleListParams = {}): Promise<ApiResponse> {
    return unifiedModuleApi.getList(params)
  }
}

/**
 * 兼容性适配器 (Compatibility Adapter)
 * 
 * 提供与旧版API完全兼容的接口映射
 */
export const compatibilityAdapter = {
  // 系统API兼容映射
  systemApi: {
    getList: unifiedSystemApi.getList,
    getDetail: unifiedSystemApi.getDetail,
    create: unifiedSystemApi.create,
    update: unifiedSystemApi.update,
    delete: unifiedSystemApi.delete,
    toggleEnabled: unifiedSystemApi.toggleEnabled,
    batchOperation: unifiedSystemApi.batchOperation,
    getStatistics: unifiedSystemApi.getStatistics
  },

  // 模块API兼容映射
  moduleApi: {
    getList: unifiedModuleApi.getList,
    getBySystem: unifiedModuleApi.getBySystem,
    getDetail: unifiedModuleApi.getDetail,
    create: unifiedModuleApi.create,
    update: unifiedModuleApi.update,
    delete: unifiedModuleApi.delete,
    toggleEnabled: unifiedModuleApi.toggleEnabled,
    batchOperation: unifiedModuleApi.batchOperation,
    moveToSystem: unifiedModuleApi.moveToSystem,
    getUsageStatistics: unifiedModuleApi.getUsageStatistics
  },

  // 分类API兼容映射
  categoryApi: {
    getSystemCategories: unifiedCategoryApi.getSystemCategories,
    getModuleTags: unifiedCategoryApi.getModuleTags,
    createTag: unifiedCategoryApi.createTag,
    updateTag: unifiedCategoryApi.updateTag,
    deleteTag: unifiedCategoryApi.deleteTag
  },

  // 监控API兼容映射
  monitorApi: {
    getHealthStatus: unifiedMonitorApi.getHealthStatus,
    getOverview: unifiedMonitorApi.getOverview,
    getMetrics: unifiedMonitorApi.getMetrics
  },

  // API管理兼容映射
  apiManagementApi: unifiedApiManagementApi
}

/**
 * 默认导出 - 统一API模块
 */
export default {
  system: unifiedSystemApi,
  module: unifiedModuleApi,
  category: unifiedCategoryApi,
  log: unifiedLogApi,
  monitor: unifiedMonitorApi,
  apiManagementApi: unifiedApiManagementApi,
  compatibility: compatibilityAdapter,
  // 兼容性接口
  getModuleList: unifiedApiManagementApi.getModuleList,
  getServiceList: unifiedApiManagementApi.getServiceList
}

/**
 * 命名导出 - 兼容旧版导入方式
 */
export const systemApi = unifiedSystemApi
export const moduleApi = unifiedModuleApi
export const categoryApi = unifiedCategoryApi
export const monitorApi = unifiedMonitorApi