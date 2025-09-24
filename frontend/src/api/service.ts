/**
 * 服务管理API接口模块
 * 
 * 功能说明：
 * - 提供完整的系统和模块管理API接口
 * - 支持CRUD操作、批量操作、状态管理
 * - 包含分类管理、导入导出、监控等功能
 * - 统一的错误处理和响应格式
 * 
 * 模块结构：
 * - systemApi: 系统管理相关接口
 * - moduleApi: 模块管理相关接口  
 * - categoryApi: 分类和标签管理接口
 * - importExportApi: 导入导出功能接口
 * - monitorApi: 监控和统计接口
 * 
 * 技术特性：
 * - RESTful API设计规范
 * - 统一的参数验证和错误处理
 * - 支持分页、搜索、筛选
 * - 文件上传下载支持
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024
 */

import { request } from '@/utils/request'
import { apiHandler } from '@/utils/apiHandler'
import type { 
  ApiResponse, 
  ApiHandlerOptions,
  ListParams,
  CreateRequest,
  UpdateRequest,
  BatchOperationRequest,
  StatusUpdateRequest
} from '@/types'

// 扩展的接口参数类型定义
export interface SystemListParams extends ListParams {
  category?: string
  enabled?: boolean
}

export interface ModuleListParams extends ListParams {
  system_id?: string
  enabled_only?: boolean
  tags?: string
}

export interface TagListParams {
  systemId?: string
  keyword?: string
}

export interface ExportParams {
  systemIds: string[]
  format: 'json' | 'yaml' | 'excel'
}

export interface AlertListParams extends ListParams {
  level?: 'info' | 'warning' | 'error' | 'critical'
  status?: 'active' | 'resolved'
}

export interface MetricsParams {
  timeRange?: '1h' | '6h' | '24h' | '7d' | '30d'
}

// 扩展的数据类型定义
export interface SystemData extends CreateRequest {
  name: string
  description: string
  category: string
  version: string
  icon?: string
  config?: Record<string, any>
  enabled?: boolean
}

export interface ModuleData extends CreateRequest {
  system_id: string
  name: string
  description: string
  icon?: string
  path: string
  method: string
  version: string
  module_type: string
  tags?: string[]
  config?: Record<string, any>
  order_index?: number
  enabled?: boolean
}

export interface BatchOperationData extends BatchOperationRequest {
  systemIds?: string[]
  moduleIds?: string[]
  targetSystemId?: string
}

export interface TagData extends CreateRequest {
  name: string
  color: string
  description?: string
  systemId?: string
}

export interface AlertHandleData {
  action: 'resolve' | 'acknowledge' | 'ignore'
  comment?: string
}

export interface MonitorConfig {
  [key: string]: any
}

/**
 * 系统管理相关接口（优化版）
 * 
 * 功能范围：
 * - 系统的增删改查操作
 * - 系统状态管理（启用/禁用）
 * - 批量操作支持
 * - 系统统计信息
 * 
 * 技术优化：
 * - 使用通用API处理器减少重复代码
 * - 统一错误处理和缓存管理
 * - 支持批量操作和性能优化
 */
export const systemApi = {
  /**
   * 获取系统列表（优化版）
   * @param params - 查询参数
   * @returns 系统列表数据
   */
  getList(params: SystemListParams = {}): Promise<ApiResponse> {
    return apiHandler.get('/systems', params, {
      cacheTime: 300000,
      successMessage: null
    })
  },

  /**
   * 获取系统详情（优化版）
   * @param systemId - 系统ID
   * @returns 系统详情数据
   */
  getDetail(systemId: string): Promise<ApiResponse> {
    return apiHandler.get(`/systems/${systemId}`, {}, {
      cacheTime: 120000,
      successMessage: null
    })
  },

  /**
   * 创建系统（优化版）
   * @param data - 系统数据
   * @returns 创建结果
   */
  create(data: SystemData): Promise<ApiResponse> {
    return apiHandler.post('/systems', data, {
      invalidateCache: ['systems-list'],
      successMessage: '系统创建成功'
    })
  },

  /**
   * 更新系统（优化版）
   * @param systemId - 系统ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  update(systemId: string, data: Partial<SystemData>): Promise<ApiResponse> {
    return apiHandler.put(`/systems/${systemId}`, data, {
      invalidateCache: ['systems-list', `system-${systemId}`],
      successMessage: '系统更新成功'
    })
  },

  /**
   * 删除系统（优化版）
   * @param systemId - 系统ID
   * @returns 删除结果
   */
  delete(systemId: string): Promise<ApiResponse> {
    return apiHandler.delete(`/systems/${systemId}`, {
      invalidateCache: ['systems-list', `system-${systemId}`],
      successMessage: '系统删除成功'
    })
  },

  /**
   * 切换系统启用状态（优化版）
   * @param systemId - 系统ID
   * @param enabled - 启用状态
   * @returns 切换结果
   */
  toggleEnabled(systemId: string, enabled: boolean): Promise<ApiResponse> {
    return apiHandler.patch(`/systems/${systemId}/status`, { enabled }, {
      invalidateCache: ['systems-list', `system-${systemId}`],
      successMessage: enabled ? '系统已启用' : '系统已禁用'
    })
  },

  /**
   * 批量操作系统（优化版）
   * @param data - 批量操作数据
   * @returns 批量操作结果
   */
  batchOperation(data: BatchOperationData): Promise<ApiResponse> {
    return request.post('/api/systems/batch', data)
  },

  /**
   * 获取系统统计信息（优化版）
   * @returns 统计数据
   */
  getStatistics(): Promise<ApiResponse> {
    return apiHandler.get('/systems/statistics', {}, {
      cacheTime: 120000,
      successMessage: null
    })
  },

  /**
   * 获取启用系统列表（用于API管理和页面管理页面）
   * @returns 启用系统列表
   */
  getEnabledList(): Promise<ApiResponse> {
    return apiHandler.get('/systems/v1/enabled', {}, {
      cacheTime: 300000,
      successMessage: null
    })
  },

  /**
   * 根据分类获取启用系统列表
   * @param category 系统分类 ('backend' 或 'frontend')
   * @returns 指定分类的启用系统列表
   */
  getEnabledListByCategory(category: 'backend' | 'frontend'): Promise<ApiResponse> {
    return apiHandler.get(`/systems/v1/enabled/${category}`, {}, {
      cacheTime: 300000,
      successMessage: null
    })
  }
}

/**
 * 模块管理相关接口（优化版）
 * 
 * 功能范围：
 * - 模块的完整生命周期管理
 * - 支持按系统分组管理
 * - 模块标签和分类管理
 * - 模块使用统计和监控
 * - 模块间的关联和依赖管理
 * 
 * 技术优化：
 * - 使用通用API处理器减少重复代码
 * - 智能缓存管理和失效策略
 * - 统一错误处理和用户反馈
 */
export const moduleApi = {
  /**
   * 获取模块列表（优化版）
   * @param params - 查询参数
   * @returns 模块列表数据
   */
  getList(params: ModuleListParams = {}): Promise<ApiResponse> {
    return apiHandler.get('/modules', params, {
      cacheTime: 300000,
      successMessage: null
    })
  },

  /**
   * 获取指定系统的模块列表（优化版）
   * @param systemId - 系统ID
   * @param params - 查询参数
   * @returns 模块列表数据
   */
  getBySystem(systemId: string, params: ModuleListParams = {}): Promise<ApiResponse> {
    return apiHandler.get('/modules', { ...params, system_id: systemId }, {
      cacheTime: 300000,
      successMessage: null
    })
  },

  /**
   * 获取模块详情（优化版）
   * @param moduleId - 模块ID
   * @returns 模块详情数据
   */
  getDetail(moduleId: string): Promise<ApiResponse> {
    return apiHandler.get(`/modules/v1/${moduleId}`, {}, {
      cacheTime: 600000,
      successMessage: null
    })
  },

  /**
   * 创建模块（优化版）
   * @param data - 模块数据
   * @returns 创建结果
   */
  create(data: ModuleData): Promise<ApiResponse> {
    return apiHandler.post('/modules', data, {
      invalidateCache: ['modules-list', `system-${data.system_id}-modules`],
      successMessage: '模块创建成功'
    })
  },

  /**
   * 更新模块（优化版）
   * @param moduleId - 模块ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  update(moduleId: string, data: Partial<ModuleData>): Promise<ApiResponse> {
    const cacheKeys = ['modules-list', `module-${moduleId}`]
    if (data.system_id) {
      cacheKeys.push(`system-${data.system_id}-modules`)
    }
    return apiHandler.put(`/modules/v1/${moduleId}`, data, {
      invalidateCache: cacheKeys,
      successMessage: '模块更新成功'
    })
  },

  /**
   * 删除模块（优化版）
   * @param moduleId - 模块ID
   * @returns 删除结果
   */
  delete(moduleId: string): Promise<ApiResponse> {
    return apiHandler.delete(`/modules/v1/${moduleId}`, {
      invalidateCache: ['modules-list', `module-${moduleId}`],
      successMessage: '模块删除成功'
    })
  },

  /**
   * 切换模块启用状态（优化版）
   * @param moduleId - 模块ID
   * @param enabled - 启用状态
   * @returns 切换结果
   */
  toggleEnabled(moduleId: string, enabled: boolean): Promise<ApiResponse> {
    return apiHandler.patch(`/modules/${moduleId}/status`, { enabled }, {
      invalidateCache: ['modules-list', `module-${moduleId}`],
      successMessage: enabled ? '模块已启用' : '模块已禁用'
    })
  },

  /**
   * 批量操作模块（优化版）
   * @param data - 批量操作数据
   * @returns 批量操作结果
   */
  batchOperation(data: BatchOperationData): Promise<ApiResponse> {
    return request.post('/api/modules/batch', data)
  },

  /**
   * 移动模块到其他系统（优化版）
   * @param moduleId - 模块ID
   * @param targetSystemId - 目标系统ID
   * @returns 移动结果
   */
  moveToSystem(moduleId: string, targetSystemId: string): Promise<ApiResponse> {
    return apiHandler.patch(`/modules/v1/${moduleId}/move`, { targetSystemId }, {
      invalidateCache: ['modules-list', `module-${moduleId}`, `system-${targetSystemId}-modules`],
      successMessage: '模块移动成功'
    })
  },

  /**
   * 获取模块的使用统计（优化版）
   * @param moduleId - 模块ID
   * @returns 使用统计数据
   */
  getUsageStatistics(moduleId: string): Promise<ApiResponse> {
    return apiHandler.get(`/modules/v1/${moduleId}/statistics`, {}, {
      cacheTime: 300000,
      successMessage: null
    })
  },

  /**
   * 获取启用模块列表（用于API管理和页面管理页面）
   * @param systemId - 可选的系统ID
   * @returns 启用模块列表
   */
  getEnabledList(systemId?: string): Promise<ApiResponse> {
    const params = systemId ? { system_id: systemId } : {}
    return apiHandler.get('/modules/v1/enabled', params, {
      cacheTime: 300000,
      successMessage: null
    })
  },

  /**
   * 根据系统ID获取启用模块列表（用于API管理和页面管理页面）
   * @param systemId - 系统ID
   * @returns 启用模块列表
   */
  getEnabledBySystem(systemId: string): Promise<ApiResponse> {
    return apiHandler.get(`/modules/v1/enabled/by-system/${systemId}`, {}, {
      cacheTime: 300000,
      successMessage: null
    })
  }
}

/**
 * 分类和标签管理相关接口（优化版）
 * 
 * 功能范围：
 * - 系统分类管理
 * - 模块标签管理
 * - 分类层级结构维护
 * - 标签颜色和样式管理
 * 
 * 技术优化：
 * - 使用通用API处理器减少重复代码
 * - 智能缓存管理和失效策略
 * - 统一错误处理和用户反馈
 */
export const categoryApi = {
  /**
   * 获取系统分类列表（优化版）
   * @returns 分类列表
   */
  getSystemCategories(): Promise<ApiResponse> {
    return apiHandler.get('/categories/systems', {}, {
      cacheTime: 600000,
      successMessage: null
    })
  },

  /**
   * 获取模块标签列表（优化版）
   * @param params - 查询参数
   * @returns 标签列表
   */
  getModuleTags(params: TagListParams = {}): Promise<ApiResponse> {
    return apiHandler.get('/categories/tags', params, {
      cacheTime: 300000,
      successMessage: null
    })
  },

  /**
   * 创建新标签（优化版）
   * @param data - 标签数据
   * @returns 创建结果
   */
  createTag(data: TagData): Promise<ApiResponse> {
    const cacheKeys = ['tags-all']
    if (data.systemId) {
      cacheKeys.push(`tags-system-${data.systemId}`)
    }
    return apiHandler.post('/categories/tags', data, {
      invalidateCache: cacheKeys,
      successMessage: '标签创建成功'
    })
  },

  /**
   * 更新标签（优化版）
   * @param tagId - 标签ID
   * @param data - 更新数据
   * @returns 更新结果
   */
  updateTag(tagId: string, data: Partial<TagData>): Promise<ApiResponse> {
    return apiHandler.put(`/categories/tags/${tagId}`, data, {
      invalidateCache: ['tags-all', `tag-${tagId}`],
      successMessage: '标签更新成功'
    })
  },

  /**
   * 删除标签（优化版）
   * @param tagId - 标签ID
   * @returns 删除结果
   */
  deleteTag(tagId: string): Promise<ApiResponse> {
    return apiHandler.delete(`/categories/tags/${tagId}`, {
      invalidateCache: ['tags-all', `tag-${tagId}`],
      successMessage: '标签删除成功'
    })
  }
}

/**
 * 导入导出相关接口（优化版）
 * 
 * 功能范围：
 * - 系统配置批量导出
 * - 配置文件导入和验证
 * - 多格式支持（JSON、YAML、Excel）
 * - 导入模板下载
 * - 数据完整性验证
 * 
 * 技术优化：
 * - 使用通用API处理器减少重复代码
 * - 智能缓存管理和失效策略
 * - 统一错误处理和用户反馈
 */
export const importExportApi = {
  /**
   * 导出系统配置（优化版）
   * @param params - 导出参数
   * @returns 导出文件
   */
  exportSystems(params: ExportParams): Promise<void> {
    return request.download('/api/export/systems', params)
  },

  /**
   * 导入系统配置（优化版）
   * @param formData - 包含文件的表单数据
   * @returns 导入结果
   */
  importSystems(formData: FormData): Promise<ApiResponse> {
    return request.upload('/api/import/systems', formData)
  },

  /**
   * 获取导入模板（优化版）
   * @param format - 模板格式
   * @returns 模板文件
   */
  getImportTemplate(format: 'json' | 'yaml' | 'excel' = 'excel'): Promise<void> {
    return request.download('/api/import/template', { format })
  },

  /**
   * 验证导入文件（优化版）
   * @param formData - 包含文件的表单数据
   * @returns 验证结果
   */
  validateImportFile(formData: FormData): Promise<ApiResponse> {
    return request.upload('/api/import/validate', formData)
  }
}

/**
 * 健康检查和监控相关接口（优化版）
 * 
 * 功能范围：
 * - 系统和模块健康状态监控
 * - 性能指标收集和分析
 * - 告警管理和通知
 * - 实时监控数据展示
 * - 历史数据统计和趋势分析
 * 
 * 技术优化：
 * - 使用通用API处理器减少重复代码
 * - 智能缓存管理和失效策略
 * - 统一错误处理和用户反馈
 */
export const monitorApi = {
  /**
   * 获取系统健康状态（优化版）
   * @param systemId - 系统ID (可选，不传则获取所有系统)
   * @returns 健康状态数据
   */
  getHealthStatus(systemId: string | null = null): Promise<ApiResponse> {
    const url = systemId ? `/monitor/health/${systemId}` : '/monitor/health'
    return apiHandler.get(url, {}, {
      cacheTime: 30000,
      successMessage: null
    })
  },

  /**
   * 获取模块性能指标（优化版）
   * @param moduleId - 模块ID
   * @param params - 查询参数
   * @returns 性能指标数据
   */
  getModuleMetrics(moduleId: string, params: MetricsParams = {}): Promise<ApiResponse> {
    return apiHandler.get(`/monitor/modules/${moduleId}/metrics`, params, {
      cacheTime: 60000,
      successMessage: null
    })
  },

  /**
   * 获取系统概览数据（优化版）
   * @returns 概览数据
   */
  getOverview(): Promise<ApiResponse> {
    return apiHandler.get('/monitor/overview', {}, {
      cacheTime: 30000,
      successMessage: null
    })
  },

  /**
   * 获取告警列表（优化版）
   * @param params - 查询参数
   * @returns 告警列表
   */
  getAlerts(params: AlertListParams = {}): Promise<ApiResponse> {
    return apiHandler.get('/monitor/alerts', params, {
      cacheTime: 60000,
      successMessage: null
    })
  },

  /**
   * 处理告警（优化版）
   * @param alertId - 告警ID
   * @param action - 操作类型
   * @param comment - 处理备注
   * @returns 处理结果
   */
  handleAlert(alertId: string, action: 'resolve' | 'acknowledge' | 'ignore', comment: string = ''): Promise<ApiResponse> {
    return apiHandler.patch(`/monitor/alerts/${alertId}`, { action, comment }, {
      invalidateCache: ['alerts'],
      successMessage: `告警已${action === 'resolve' ? '解决' : action === 'acknowledge' ? '确认' : '忽略'}`
    })
  },

  /**
   * 获取监控配置（优化版）
   * @returns 监控配置数据
   */
  getMonitorConfig(): Promise<ApiResponse> {
    return apiHandler.get('/monitor/config', {}, {
      cacheTime: 300000,
      successMessage: null
    })
  },

  /**
   * 更新监控配置（优化版）
   * @param config - 监控配置
   * @returns 更新结果
   */
  updateMonitorConfig(config: MonitorConfig): Promise<ApiResponse> {
    return apiHandler.put('/monitor/config', config, {
      invalidateCache: ['monitor-config'],
      successMessage: '监控配置更新成功'
    })
  }
}

// 默认导出所有API
/**
 * 默认导出所有API模块
 * 
 * 使用方式：
 * import api from '@/api/service'
 * api.system.getList()
 * api.module.create(data)
 * api.monitor.getHealthStatus()
 * 
 * 或者按需导入：
 * import { systemApi, moduleApi } from '@/api/service'
 */
export default {
  system: systemApi,
  module: moduleApi,
  category: categoryApi,
  importExport: importExportApi,
  monitor: monitorApi,
  // 直接暴露常用的API管理方法以保持兼容性
  getModuleList: moduleApi.getList,
  getServiceList: systemApi.getList
}