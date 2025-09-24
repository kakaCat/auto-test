import { request } from '@/utils/request'

/**
 * 服务管理API接口 - 优化版
 * 适配新的后端接口结构，使用自增ID主键和UUID业务标识符
 */

// 查询参数接口
interface SystemListParams {
  keyword?: string
  category?: string
  enabled_only?: boolean
}

interface ModuleListParams {
  system_id?: string
  keyword?: string
  enabled_only?: boolean
  tags?: string
}

// 数据接口
interface SystemData {
  name: string
  description?: string
  icon?: string
  category?: string
  enabled?: boolean
  order_index?: number
  url?: string
  metadata?: Record<string, any>
}

interface ModuleData {
  system_id: string
  name: string
  description?: string
  icon?: string
  url?: string
  enabled?: boolean
  order_index?: number
  metadata?: Record<string, any>
  tags?: string[]
}

interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
}

interface StatsData {
  systems?: Record<string, any>
  modules?: Record<string, any>
  overview?: Record<string, any>
}

// 系统管理相关接口
export const systemApiOptimized = {
  /**
   * 获取系统列表
   * @param params - 查询参数
   * @returns 系统列表数据
   */
  getList(params: SystemListParams = {}): Promise<ApiResponse> {
    return request.get('/api/systems', params)
  },

  /**
   * 获取系统详情
   * @param systemId - 系统UUID
   * @returns 系统详情数据
   */
  getDetail(systemId: string): Promise<ApiResponse> {
    return request.get(`/api/systems/${systemId}`)
  },

  /**
   * 创建系统
   * @param systemData - 系统数据
   * @returns 创建结果
   */
  create(systemData: SystemData): Promise<ApiResponse> {
    return request.post('/api/systems', systemData)
  },

  /**
   * 更新系统
   * @param systemId - 系统UUID
   * @param systemData - 系统数据
   * @returns 更新结果
   */
  update(systemId: string, systemData: SystemData): Promise<ApiResponse> {
    return request.put(`/api/systems/${systemId}`, systemData)
  },

  /**
   * 删除系统
   * @param systemId - 系统UUID
   * @returns 删除结果
   */
  delete(systemId: string): Promise<ApiResponse> {
    return request.delete(`/api/systems/${systemId}`)
  },

  /**
   * 更新系统状态
   * @param systemId - 系统UUID
   * @param enabled - 是否启用
   * @returns 更新结果
   */
  updateStatus(systemId: string, enabled: boolean): Promise<ApiResponse> {
    return request.patch(`/api/systems/${systemId}/status`, { enabled })
  },

  /**
   * 搜索系统
   * @param keyword - 搜索关键词
   * @returns 搜索结果
   */
  search(keyword: string): Promise<ApiResponse> {
    return request.get('/api/systems', { keyword })
  },

  /**
   * 按分类获取系统
   * @param category - 系统分类
   * @returns 系统列表
   */
  getByCategory(category: string): Promise<ApiResponse> {
    return request.get('/api/systems', { category })
  }
}

// 模块管理相关接口
export const moduleApiOptimized = {
  /**
   * 获取模块列表
   * @param params - 查询参数
   * @returns 模块列表数据
   */
  getList(params: ModuleListParams = {}): Promise<ApiResponse> {
    return request.get('/api/modules', params)
  },

  /**
   * 获取指定系统的模块列表
   * @param systemId - 系统UUID
   * @param params - 查询参数
   * @returns 模块列表数据
   */
  getBySystem(systemId: string, params: ModuleListParams = {}): Promise<ApiResponse> {
    return request.get('/api/modules', { ...params, system_id: systemId })
  },

  /**
   * 获取模块详情
   * @param moduleId - 模块UUID
   * @returns 模块详情数据
   */
  getDetail(moduleId: string): Promise<ApiResponse> {
    return request.get(`/api/modules/${moduleId}`)
  },

  /**
   * 创建模块
   * @param moduleData - 模块数据
   * @returns 创建结果
   */
  create(moduleData: ModuleData): Promise<ApiResponse> {
    return request.post('/api/modules', moduleData)
  },

  /**
   * 更新模块
   * @param moduleId - 模块UUID
   * @param moduleData - 模块数据
   * @returns 更新结果
   */
  update(moduleId: string, moduleData: ModuleData): Promise<ApiResponse> {
    return request.put(`/api/modules/${moduleId}`, moduleData)
  },

  /**
   * 删除模块
   * @param moduleId - 模块UUID
   * @returns 删除结果
   */
  delete(moduleId: string): Promise<ApiResponse> {
    return request.delete(`/api/modules/${moduleId}`)
  },

  /**
   * 更新模块状态
   * @param moduleId - 模块UUID
   * @param enabled - 是否启用
   * @returns 更新结果
   */
  updateStatus(moduleId: string, enabled: boolean): Promise<ApiResponse> {
    return request.patch(`/api/modules/${moduleId}/status`, { enabled })
  },

  /**
   * 搜索模块
   * @param keyword - 搜索关键词
   * @param systemId - 系统UUID（可选）
   * @returns 搜索结果
   */
  search(keyword: string, systemId: string | null = null): Promise<ApiResponse> {
    const params: ModuleListParams = { keyword }
    if (systemId) {
      params.system_id = systemId
    }
    return request.get('/api/modules', params)
  },

  /**
   * 按标签获取模块
   * @param tags - 标签列表
   * @returns 模块列表
   */
  getByTags(tags: string[]): Promise<ApiResponse> {
    return request.get('/api/modules', { tags: tags.join(',') })
  }
}

// 统计和监控相关接口
export const statsApiOptimized = {
  /**
   * 获取统计信息
   * @returns 统计数据
   */
  getStats(): Promise<ApiResponse<StatsData>> {
    return request.get('/api/stats')
  },

  /**
   * 获取系统统计信息
   * @returns 系统统计数据
   */
  async getSystemStats(): Promise<Record<string, any>> {
    const response = await this.getStats()
    return response.data?.systems || {}
  },

  /**
   * 获取模块统计信息
   * @returns 模块统计数据
   */
  async getModuleStats(): Promise<Record<string, any>> {
    const response = await this.getStats()
    return response.data?.modules || {}
  },

  /**
   * 获取概览统计信息
   * @returns 概览统计数据
   */
  async getOverviewStats(): Promise<Record<string, any>> {
    const response = await this.getStats()
    return response.data?.overview || {}
  }
}

// 健康检查和系统管理接口
export const healthApiOptimized = {
  /**
   * 健康检查
   * @returns 健康状态
   */
  check(): Promise<ApiResponse> {
    return request.get('/api/health')
  },

  /**
   * 初始化数据库
   * @returns 初始化结果
   */
  initDatabase(): Promise<ApiResponse> {
    return request.post('/api/init-db')
  }
}

// 数据转换工具
export const dataTransformUtils = {
  /**
   * 转换后端系统数据为前端格式
   * @param backendSystem - 后端系统数据
   * @returns 前端系统数据
   */
  transformSystemFromBackend(backendSystem: any): any {
    return {
      id: backendSystem.uuid,
      name: backendSystem.name,
      description: backendSystem.description,
      icon: backendSystem.icon,
      category: backendSystem.category,
      enabled: backendSystem.enabled,
      orderIndex: backendSystem.order_index,
      url: backendSystem.url,
      metadata: backendSystem.metadata,
      createdAt: backendSystem.created_at,
      updatedAt: backendSystem.updated_at
    }
  },

  /**
   * 转换后端模块数据为前端格式
   * @param backendModule - 后端模块数据
   * @returns 前端模块数据
   */
  transformModuleFromBackend(backendModule: any): any {
    return {
      id: backendModule.uuid,
      systemId: backendModule.system_id,
      name: backendModule.name,
      description: backendModule.description,
      icon: backendModule.icon,
      url: backendModule.url,
      enabled: backendModule.enabled,
      orderIndex: backendModule.order_index,
      metadata: backendModule.metadata,
      tags: backendModule.tags,
      createdAt: backendModule.created_at,
      updatedAt: backendModule.updated_at
    }
  },

  /**
   * 转换前端系统数据为后端格式
   * @param frontendSystem - 前端系统数据
   * @returns 后端系统数据
   */
  transformSystemToBackend(frontendSystem: any): any {
    return {
      name: frontendSystem.name,
      description: frontendSystem.description,
      icon: frontendSystem.icon,
      category: frontendSystem.category,
      enabled: frontendSystem.enabled,
      order_index: frontendSystem.orderIndex,
      url: frontendSystem.url,
      metadata: frontendSystem.metadata
    }
  },

  /**
   * 转换前端模块数据为后端格式
   * @param frontendModule - 前端模块数据
   * @returns 后端模块数据
   */
  transformModuleToBackend(frontendModule: any): any {
    return {
      system_id: frontendModule.systemId,
      name: frontendModule.name,
      description: frontendModule.description,
      icon: frontendModule.icon,
      url: frontendModule.url,
      enabled: frontendModule.enabled,
      order_index: frontendModule.orderIndex,
      metadata: frontendModule.metadata,
      tags: frontendModule.tags
    }
  },

  /**
   * 批量转换系统数据
   * @param backendSystems - 后端系统数据列表
   * @returns 前端系统数据列表
   */
  transformSystemsFromBackend(backendSystems: any[]): any[] {
    return backendSystems.map(this.transformSystemFromBackend)
  },

  /**
   * 批量转换模块数据
   * @param backendModules - 后端模块数据列表
   * @returns 前端模块数据列表
   */
  transformModulesFromBackend(backendModules: any[]): any[] {
    return backendModules.map(this.transformModuleFromBackend)
  }
}

// 兼容性API（保持向后兼容）
export const systemApi = {
  getList: (params: SystemListParams = {}) => {
    return systemApiOptimized.getList(params).then(response => ({
      ...response,
      data: dataTransformUtils.transformSystemsFromBackend(response.data || [])
    }))
  },

  getDetail: (systemId: string) => {
    return systemApiOptimized.getDetail(systemId).then(response => ({
      ...response,
      data: response.data ? dataTransformUtils.transformSystemFromBackend(response.data) : null
    }))
  },

  create: (systemData: any) => {
    return systemApiOptimized.create(dataTransformUtils.transformSystemToBackend(systemData))
  },

  update: (systemId: string, systemData: any) => {
    return systemApiOptimized.update(systemId, dataTransformUtils.transformSystemToBackend(systemData))
  },

  delete: systemApiOptimized.delete,
  updateStatus: systemApiOptimized.updateStatus,
  search: systemApiOptimized.search,
  getByCategory: systemApiOptimized.getByCategory
}

export const moduleApi = {
  getList: (params: ModuleListParams = {}) => {
    return moduleApiOptimized.getList(params).then(response => ({
      ...response,
      data: dataTransformUtils.transformModulesFromBackend(response.data || [])
    }))
  },

  getBySystem: (systemId: string, params: ModuleListParams = {}) => {
    return moduleApiOptimized.getBySystem(systemId, params).then(response => ({
      ...response,
      data: dataTransformUtils.transformModulesFromBackend(response.data || [])
    }))
  },

  getDetail: (moduleId: string) => {
    return moduleApiOptimized.getDetail(moduleId).then(response => ({
      ...response,
      data: response.data ? dataTransformUtils.transformModuleFromBackend(response.data) : null
    }))
  },

  create: (moduleData: any) => {
    return moduleApiOptimized.create(dataTransformUtils.transformModuleToBackend(moduleData))
  },

  update: (moduleId: string, moduleData: any) => {
    return moduleApiOptimized.update(moduleId, dataTransformUtils.transformModuleToBackend(moduleData))
  },

  delete: moduleApiOptimized.delete,
  updateStatus: moduleApiOptimized.updateStatus,
  search: moduleApiOptimized.search,
  getByTags: moduleApiOptimized.getByTags
}

// 默认导出
export default {
  system: systemApi,
  module: moduleApi,
  stats: statsApiOptimized,
  health: healthApiOptimized,
  // 优化版API
  systemOptimized: systemApiOptimized,
  moduleOptimized: moduleApiOptimized,
  // 数据转换工具
  transform: dataTransformUtils
}