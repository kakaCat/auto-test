import { request } from '@/utils/request'
import type { ApiResponse } from '@/types'
import { ModuleConverter } from '../converters/ModuleConverter'

// 查询参数接口
interface ModuleListParams {
  system_id?: string
  keyword?: string
  enabled_only?: boolean
  tags?: string
}

// 数据接口
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

/**
 * 模块服务类
 * 负责模块相关的业务逻辑和数据收集
 */
export class ModuleService {
  /**
   * 收集模块列表数据
   */
  static async collectModuleListData(params: ModuleListParams = {}): Promise<ApiResponse> {
    const response = await request.get('/api/modules/v1/', params)
    if (response.success && response.data) {
      const raw = (response.data as any)?.data ?? response.data
      response.data = ModuleConverter.transformListFromBackend(raw)
    }
    return response
  }

  /**
   * 按系统收集模块数据
   */
  static async collectModulesBySystem(systemId: string, params: ModuleListParams = {}): Promise<ApiResponse> {
    const response = await request.get('/api/modules/v1/', { 
      ...params, 
      system_id: systemId 
    })
    if (response.success && response.data) {
      const raw = (response.data as any)?.data ?? response.data
      response.data = ModuleConverter.transformListFromBackend(raw)
    }
    return response
  }

  /**
   * 收集模块详情数据
   */
  static async collectModuleDetailData(moduleId: string): Promise<ApiResponse> {
    const response = await request.get(`/api/modules/v1/${moduleId}`)
    if (response.success && response.data) {
      const raw = (response.data as any)?.data ?? response.data
      response.data = ModuleConverter.transformFromBackend(raw)
    }
    return response
  }

  /**
   * 创建模块数据
   */
  static async createModuleData(moduleData: ModuleData): Promise<ApiResponse> {
    const backendData = ModuleConverter.transformToBackend(moduleData)
    return await request.post('/api/modules/v1/', backendData)
  }

  /**
   * 更新模块数据
   */
  static async updateModuleData(moduleId: string, moduleData: ModuleData): Promise<ApiResponse> {
    const backendData = ModuleConverter.transformToBackend(moduleData)
    return await request.put(`/api/modules/v1/${moduleId}`, backendData)
  }

  /**
   * 删除模块数据
   */
  static async deleteModuleData(moduleId: string): Promise<ApiResponse> {
    return await request.delete(`/api/modules/v1/${moduleId}`)
  }

  /**
   * 更新模块状态
   */
  static async updateModuleStatus(moduleId: string, enabled: boolean): Promise<ApiResponse> {
    return await request.patch(`/api/modules/v1/${moduleId}/status`, { enabled })
  }

  /**
   * 搜索模块数据
   */
  static async searchModuleData(keyword: string, systemId: string | null = null): Promise<ApiResponse> {
    const params: Record<string, unknown> = { keyword }
    if (systemId) {
      params.system_id = systemId
    }
    return await request.get('/api/modules/v1/search', params)
  }

  /**
   * 按标签收集模块数据
   */
  static async collectModulesByTags(tags: string[]): Promise<ApiResponse> {
    return await request.get('/api/modules/v1/', { tags: tags.join(',') })
  }
}