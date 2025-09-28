/**
 * 基础API类 (Base API Class)
 * 
 * 功能概述：
 * - 提供统一的CRUD操作接口
 * - 标准化API调用方式
 * - 统一错误处理和类型定义
 * - 支持批量操作和状态管理
 * 
 * 设计原则：
 * 1. 单一职责：每个方法只负责一种操作
 * 2. 类型安全：使用TypeScript严格类型检查
 * 3. 一致性：统一的参数格式和返回值
 * 4. 可扩展：支持自定义配置和扩展
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024-01-15
 */

import { request } from '@/utils/request'
import { apiHandler } from '@/utils/apiHandler'
import type { ApiHandlerOptions } from '@/types'

/**
 * 基础列表查询参数
 */
export interface BaseListParams {
  page?: number
  pageSize?: number
  keyword?: string
  enabled?: boolean
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

/**
 * 基础实体接口
 */
export interface BaseEntity {
  id: number
  name: string
  enabled: boolean
  createdAt?: string
  updatedAt?: string
}

/**
 * 批量操作参数
 */
export interface BatchOperationParams {
  ids: number[]
  operation: 'enable' | 'disable' | 'delete'
}

/**
 * 统计数据接口
 */
export interface BaseStatistics {
  total: number
  enabled: number
  disabled: number
  recentlyCreated: number
}

/**
 * 基础API类
 * 提供通用的CRUD操作和标准化接口
 */
export class BaseApi<T extends BaseEntity = BaseEntity> {
  protected baseUrl: string
  protected apiHandler = apiHandler

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  /**
   * 获取列表数据
   */
  async getList(
    params: BaseListParams = {}, 
    options: ApiHandlerOptions = {}
  ): Promise<import('@/types').ApiResponse<{data: T[], total: number}>> {
    return this.apiHandler.get(this.baseUrl, params, {
      cache: true,
      loadingText: '加载列表中...',
      ...options
    })
  }

  /**
   * 获取详情数据
   */
  async getDetail(
    id: number, 
    options: ApiHandlerOptions = {}
  ): Promise<import('@/types').ApiResponse<T>> {
    return this.apiHandler.get(`${this.baseUrl}/${id}`, {}, {
      cache: true,
      cacheTime: 60000,
      loadingText: '加载详情中...',
      ...options
    })
  }

  /**
   * 创建数据
   */
  async create(
    data: Partial<T>, 
    options: ApiHandlerOptions = {}
  ): Promise<import('@/types').ApiResponse<T>> {
    return this.apiHandler.post(this.baseUrl, data, {
      successMessage: '创建成功',
      loadingText: '创建中...',
      ...options
    })
  }

  /**
   * 更新数据
   */
  async update(
    id: number, 
    data: Partial<T>, 
    options: ApiHandlerOptions = {}
  ): Promise<import('@/types').ApiResponse<T>> {
    return this.apiHandler.put(`${this.baseUrl}/${id}`, data, {
      successMessage: '更新成功',
      loadingText: '更新中...',
      ...options
    })
  }

  /**
   * 删除数据
   */
  async delete(
    id: number, 
    options: ApiHandlerOptions = {}
  ): Promise<import('@/types').ApiResponse<void>> {
    return this.apiHandler.delete(`${this.baseUrl}/${id}`, {
      successMessage: '删除成功',
      loadingText: '删除中...',
      ...options
    })
  }

  /**
   * 切换启用状态
   */
  async toggleEnabled(
    id: number, 
    enabled: boolean, 
    options: ApiHandlerOptions = {}
  ): Promise<import('@/types').ApiResponse<T>> {
    return this.apiHandler.patch(`${this.baseUrl}/${id}/toggle`, { enabled }, {
      successMessage: `${enabled ? '启用' : '禁用'}成功`,
      loadingText: '状态切换中...',
      showLoading: false,
      ...options
    })
  }

  /**
   * 批量操作
   */
  async batchOperation(
    params: BatchOperationParams, 
    options: ApiHandlerOptions = {}
  ): Promise<import('@/types').ApiResponse<{successful: number, failed: number}>> {
    return this.apiHandler.post(`${this.baseUrl}/batch`, params, {
      successMessage: '批量操作成功',
      loadingText: '批量操作中...',
      ...options
    })
  }

  /**
   * 获取启用的数据列表
   */
  async getEnabledList(
    options: ApiHandlerOptions = {}
  ): Promise<import('@/types').ApiResponse<T[]>> {
    return this.apiHandler.get(`${this.baseUrl}/enabled`, {}, {
      cache: true,
      cacheTime: 300000,
      loadingText: '加载数据中...',
      ...options
    })
  }

  /**
   * 获取统计数据
   */
  async getStatistics(
    options: ApiHandlerOptions = {}
  ): Promise<import('@/types').ApiResponse<BaseStatistics>> {
    return this.apiHandler.get(`${this.baseUrl}/statistics`, {}, {
      cache: true,
      cacheTime: 60000,
      loadingText: '加载统计中...',
      ...options
    })
  }

  /**
   * 搜索数据
   */
  async search(
    keyword: string, 
    options: ApiHandlerOptions = {}
  ): Promise<import('@/types').ApiResponse<T[]>> {
    return this.apiHandler.get(`${this.baseUrl}/search`, { keyword }, {
      cache: true,
      cacheTime: 30000,
      loadingText: '搜索中...',
      ...options
    })
  }

  /**
   * 导出数据
   */
  async export(
    params: BaseListParams = {}, 
    filename?: string, 
    options: ApiHandlerOptions = {}
  ): Promise<void> {
    return request.download(`${this.baseUrl}/export`, params, filename)
  }

  /**
   * 导入数据
   */
  async import(
    file: File, 
    options: ApiHandlerOptions = {}
  ): Promise<import('@/types').ApiResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    
    return this.apiHandler.execute(
      () => request.upload(`${this.baseUrl}/import`, formData),
      {
        successMessage: '导入成功',
        loadingText: '导入中...',
        ...options
      }
    )
  }
}

export default BaseApi