/**
 * 系统管理API (System Management API)
 * 
 * 功能概述：
 * - 系统的CRUD操作
 * - 系统状态管理
 * - 系统统计信息
 * - 系统导入导出
 * 
 * 设计原则：
 * - 继承BaseApi，复用通用功能
 * - 扩展系统特有的业务逻辑
 * - 保持类型安全和一致性
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024-01-15
 */

import { BaseApi, type BaseEntity, type BaseListParams } from './base-api'
import type { ApiHandlerOptions } from '@/types'

/**
 * 系统实体接口
 */
export interface SystemEntity extends BaseEntity {
  id: number
  name: string
  description?: string
  enabled: boolean
  version?: string
  status?: 'active' | 'inactive' | 'maintenance'
  moduleCount?: number
  apiCount?: number
  createdAt?: string
  updatedAt?: string
}

/**
 * 系统列表查询参数
 */
export interface SystemListParams extends BaseListParams {
  status?: 'active' | 'inactive' | 'maintenance'
  version?: string
  hasModules?: boolean
  category?: string
  enabled_only?: boolean
}

/**
 * 系统创建参数
 */
export interface CreateSystemParams {
  name: string
  description?: string
  version?: string
  enabled?: boolean
}

/**
 * 系统更新参数
 */
export interface UpdateSystemParams {
  name?: string
  description?: string
  version?: string
  enabled?: boolean
  status?: 'active' | 'inactive' | 'maintenance'
}

/**
 * 系统统计信息
 */
export interface SystemStatistics {
  total: number
  enabled: number
  disabled: number
  active: number
  inactive: number
  maintenance: number
  totalModules: number
  totalApis: number
  recentlyCreated: number
}

/**
 * 系统管理API类
 * 继承BaseApi，提供系统特有的功能
 */
class SystemApi extends BaseApi<SystemEntity> {
  constructor() {
    super('/api/systems')
  }

  /**
   * 获取系统列表
   */
  async getSystemList(
    params: SystemListParams = {}, 
    options: ApiHandlerOptions = {}
  ): Promise<{data: SystemEntity[], total: number}> {
    return this.getList(params, options)
  }

  /**
   * 获取系统详情
   */
  async getSystemDetail(
    systemId: number, 
    options: ApiHandlerOptions = {}
  ): Promise<SystemEntity> {
    return this.getDetail(systemId, options)
  }

  /**
   * 创建系统
   */
  async createSystem(
    data: CreateSystemParams, 
    options: ApiHandlerOptions = {}
  ): Promise<SystemEntity> {
    return this.create(data, options)
  }

  /**
   * 更新系统
   */
  async updateSystem(
    systemId: number, 
    data: UpdateSystemParams, 
    options: ApiHandlerOptions = {}
  ): Promise<SystemEntity> {
    return this.update(systemId, data, options)
  }

  /**
   * 删除系统
   */
  async deleteSystem(
    systemId: number, 
    options: ApiHandlerOptions = {}
  ): Promise<void> {
    return this.delete(systemId, options)
  }

  /**
   * 切换系统启用状态
   */
  async toggleSystemEnabled(
    systemId: number, 
    enabled: boolean, 
    options: ApiHandlerOptions = {}
  ): Promise<SystemEntity> {
    return this.toggleEnabled(systemId, enabled, options)
  }

  /**
   * 获取启用的系统列表
   */
  async getEnabledSystems(options: ApiHandlerOptions = {}): Promise<SystemEntity[]> {
    return this.getEnabledList(options)
  }

  /**
   * 获取系统统计信息
   */
  async getSystemStatistics(options: ApiHandlerOptions = {}): Promise<SystemStatistics> {
    return this.getStatistics(options) as Promise<SystemStatistics>
  }

  /**
   * 获取启用的系统列表（兼容性方法）
   */
  async getEnabledList(options: ApiHandlerOptions = {}): Promise<SystemEntity[]> {
    return this.getEnabledSystems(options)
  }

  /**
   * 按分类获取启用的系统列表
   */
  async getEnabledListByCategory(
    category: string, 
    options: ApiHandlerOptions = {}
  ): Promise<SystemEntity[]> {
    return this.getSystemList({ category, enabled_only: true }, options).then(result => result.data)
  }

  /**
   * 切换系统启用状态（兼容性方法）
   */
  async toggleEnabled(
    systemId: number, 
    enabled: boolean, 
    options: ApiHandlerOptions = {}
  ): Promise<SystemEntity> {
    return this.toggleSystemEnabled(systemId, enabled, options)
  }

  /**
   * 获取系统分类列表
   */
  async getCategories(options: ApiHandlerOptions = {}): Promise<string[]> {
    return this.apiHandler.get(`${this.baseUrl}/categories`, {}, {
      cache: true,
      cacheTime: 300000,
      loadingText: '获取分类列表中...',
      ...options
    })
  }

  /**
   * 搜索系统
   */
  async searchSystems(
    keyword: string, 
    options: ApiHandlerOptions = {}
  ): Promise<SystemEntity[]> {
    return this.search(keyword, options)
  }

  /**
   * 批量操作系统
   */
  async batchOperateSystems(
    systemIds: number[], 
    operation: 'enable' | 'disable' | 'delete', 
    options: ApiHandlerOptions = {}
  ): Promise<{successful: number, failed: number}> {
    return this.batchOperation({ ids: systemIds, operation }, options)
  }

  /**
   * 导出系统数据
   */
  async exportSystems(
    params: SystemListParams = {}, 
    filename?: string, 
    options: ApiHandlerOptions = {}
  ): Promise<void> {
    return this.export(params, filename, options)
  }

  /**
   * 导入系统数据
   */
  async importSystems(
    file: File, 
    options: ApiHandlerOptions = {}
  ): Promise<any> {
    return this.import(file, options)
  }

  /**
   * 获取系统下的模块数量
   */
  async getSystemModuleCount(
    systemId: number, 
    options: ApiHandlerOptions = {}
  ): Promise<{count: number}> {
    return this.apiHandler.get(`${this.baseUrl}/${systemId}/modules/count`, {}, {
      cache: true,
      cacheTime: 60000,
      loadingText: '统计模块数量中...',
      ...options
    })
  }

  /**
   * 获取系统下的API数量
   */
  async getSystemApiCount(
    systemId: number, 
    options: ApiHandlerOptions = {}
  ): Promise<{count: number}> {
    return this.apiHandler.get(`${this.baseUrl}/${systemId}/apis/count`, {}, {
      cache: true,
      cacheTime: 60000,
      loadingText: '统计API数量中...',
      ...options
    })
  }

  /**
   * 更新系统状态
   */
  async updateSystemStatus(
    systemId: number, 
    status: 'active' | 'inactive' | 'maintenance', 
    options: ApiHandlerOptions = {}
  ): Promise<SystemEntity> {
    return this.apiHandler.patch(`${this.baseUrl}/${systemId}/status`, { status }, {
      successMessage: '状态更新成功',
      loadingText: '更新状态中...',
      ...options
    })
  }
}

// 创建系统API实例
export const systemApi = new SystemApi()

// 导出默认实例
export default systemApi