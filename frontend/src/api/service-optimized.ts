import { request } from '@/utils/request'
import { ApiResponse } from '@/types/api'
import { SystemService } from './services/SystemService'
import { ModuleService } from './services/ModuleService'
import { SystemConverter } from './converters/SystemConverter'
import { ModuleConverter } from './converters/ModuleConverter'

/**
 * 服务管理API接口 - 重构版
 * 使用分层架构：Service层负责业务逻辑，Converter层负责数据转换
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
    return SystemService.collectSystemListData(params)
  },

  /**
   * 获取系统详情
   * @param systemId - 系统UUID
   * @returns 系统详情数据
   */
  getDetail(systemId: string): Promise<ApiResponse> {
    return SystemService.collectSystemDetailData(systemId)
  },

  /**
   * 创建系统
   * @param systemData - 系统数据
   * @returns 创建结果
   */
  create(systemData: SystemData): Promise<ApiResponse> {
    return SystemService.createSystemData(systemData)
  },

  /**
   * 更新系统
   * @param systemId - 系统UUID
   * @param systemData - 系统数据
   * @returns 更新结果
   */
  update(systemId: string, systemData: SystemData): Promise<ApiResponse> {
    return SystemService.updateSystemData(systemId, systemData)
  },

  /**
   * 删除系统
   * @param systemId - 系统UUID
   * @returns 删除结果
   */
  delete(systemId: string): Promise<ApiResponse> {
    return SystemService.deleteSystemData(systemId)
  },

  /**
   * 更新系统状态
   * @param systemId - 系统UUID
   * @param enabled - 是否启用
   * @returns 更新结果
   */
  updateStatus(systemId: string, enabled: boolean): Promise<ApiResponse> {
    return SystemService.updateSystemStatus(systemId, enabled)
  },

  /**
   * 搜索系统
   * @param keyword - 搜索关键词
   * @returns 搜索结果
   */
  search(keyword: string): Promise<ApiResponse> {
    return SystemService.searchSystemData(keyword)
  },

  /**
   * 按分类获取系统
   * @param category - 系统分类
   * @returns 系统列表
   */
  getByCategory(category: string): Promise<ApiResponse> {
    return SystemService.collectSystemsByCategory(category)
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
    return ModuleService.collectModuleListData(params)
  },

  /**
   * 获取指定系统的模块列表
   * @param systemId - 系统UUID
   * @param params - 查询参数
   * @returns 模块列表数据
   */
  getBySystem(systemId: string, params: ModuleListParams = {}): Promise<ApiResponse> {
    return ModuleService.collectModulesBySystem(systemId, params)
  },

  /**
   * 获取模块详情
   * @param moduleId - 模块UUID
   * @returns 模块详情
   */
  getDetail(moduleId: string): Promise<ApiResponse> {
    return ModuleService.collectModuleDetailData(moduleId)
  },

  /**
   * 创建模块
   * @param moduleData - 模块数据
   * @returns 创建结果
   */
  create(moduleData: ModuleData): Promise<ApiResponse> {
    return ModuleService.createModuleData(moduleData)
  },

  /**
   * 更新模块
   * @param moduleId - 模块UUID
   * @param moduleData - 模块数据
   * @returns 更新结果
   */
  update(moduleId: string, moduleData: ModuleData): Promise<ApiResponse> {
    return ModuleService.updateModuleData(moduleId, moduleData)
  },

  /**
   * 删除模块
   * @param moduleId - 模块UUID
   * @returns 删除结果
   */
  delete(moduleId: string): Promise<ApiResponse> {
    return ModuleService.deleteModuleData(moduleId)
  },

  /**
   * 更新模块状态
   * @param moduleId - 模块UUID
   * @param enabled - 是否启用
   * @returns 更新结果
   */
  updateStatus(moduleId: string, enabled: boolean): Promise<ApiResponse> {
    return ModuleService.updateModuleStatus(moduleId, enabled)
  },

  /**
   * 搜索模块
   * @param keyword - 搜索关键词
   * @param systemId - 系统UUID（可选）
   * @returns 搜索结果
   */
  search(keyword: string, systemId: string | null = null): Promise<ApiResponse> {
    return ModuleService.searchModuleData(keyword, systemId)
  },

  /**
   * 按标签获取模块
   * @param tags - 标签列表
   * @returns 模块列表
   */
  getByTags(tags: string[]): Promise<ApiResponse> {
    return ModuleService.collectModulesByTags(tags)
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

// 数据转换功能已移至专门的Converter类中
// SystemConverter: ./converters/SystemConverter.ts
// ModuleConverter: ./converters/ModuleConverter.ts

// 兼容性API（保持向后兼容）
export const systemApi = {
  getList: (params: SystemListParams = {}) => {
    return systemApiOptimized.getList(params).then(response => ({
      ...response,
      data: SystemConverter.transformListFromBackend(response.data || [])
    }))
  },

  getDetail: (systemId: string) => {
    return systemApiOptimized.getDetail(systemId).then(response => ({
      ...response,
      data: response.data ? SystemConverter.transformFromBackend(response.data) : null
    }))
  },

  create: (systemData: any) => {
    return systemApiOptimized.create(SystemConverter.transformToBackend(systemData))
  },

  update: (systemId: string, systemData: any) => {
    return systemApiOptimized.update(systemId, SystemConverter.transformToBackend(systemData))
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
      data: ModuleConverter.transformListFromBackend(response.data || [])
    }))
  },

  getBySystem: (systemId: string, params: ModuleListParams = {}) => {
    return moduleApiOptimized.getBySystem(systemId, params).then(response => ({
      ...response,
      data: ModuleConverter.transformListFromBackend(response.data || [])
    }))
  },

  getDetail: (moduleId: string) => {
    return moduleApiOptimized.getDetail(moduleId).then(response => ({
      ...response,
      data: response.data ? ModuleConverter.transformFromBackend(response.data) : null
    }))
  },

  create: (moduleData: any) => {
    return moduleApiOptimized.create(ModuleConverter.transformToBackend(moduleData))
  },

  update: (moduleId: string, moduleData: any) => {
    return moduleApiOptimized.update(moduleId, ModuleConverter.transformToBackend(moduleData))
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
  moduleOptimized: moduleApiOptimized
}