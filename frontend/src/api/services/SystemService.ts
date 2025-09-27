import { request } from '@/utils/request'
import { ApiResponse } from '@/types/api'
import { SystemConverter } from '../converters/SystemConverter'

// 查询参数接口
interface SystemListParams {
  keyword?: string
  category?: string
  enabled_only?: boolean
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

/**
 * 系统服务类
 * 负责系统相关的业务逻辑和数据收集
 */
export class SystemService {
  /**
   * 收集系统列表数据
   */
  static async collectSystemListData(params: SystemListParams = {}): Promise<ApiResponse> {
    const response = await request.get('/api/systems/v1/', { params });
    if (response.data?.data) {
      response.data.data = SystemConverter.transformListFromBackend(response.data.data);
    }
    return response;
  }

  /**
   * 收集系统详情数据
   */
  static async collectSystemDetailData(systemId: string): Promise<ApiResponse> {
    const response = await request.get(`/api/systems/v1/${systemId}`);
    if (response.data?.data) {
      response.data.data = SystemConverter.transformFromBackend(response.data.data);
    }
    return response;
  }

  /**
   * 创建系统数据
   */
  static async createSystemData(systemData: SystemData): Promise<ApiResponse> {
    const backendData = SystemConverter.transformToBackend(systemData);
    return await request.post('/api/systems/v1/', backendData);
  }

  /**
   * 更新系统数据
   */
  static async updateSystemData(systemId: string, systemData: SystemData): Promise<ApiResponse> {
    const backendData = SystemConverter.transformToBackend(systemData);
    return await request.put(`/api/systems/v1/${systemId}`, backendData);
  }

  /**
   * 删除系统数据
   */
  static async deleteSystemData(systemId: string): Promise<ApiResponse> {
    return await request.delete(`/api/systems/v1/${systemId}`);
  }

  /**
   * 更新系统状态
   */
  static async updateSystemStatus(systemId: string, enabled: boolean): Promise<ApiResponse> {
    return await request.patch(`/api/systems/${systemId}/status`, { enabled });
  }

  /**
   * 搜索系统数据
   */
  static async searchSystemData(keyword: string): Promise<ApiResponse> {
    return await request.get('/api/systems/v1/search', { params: { keyword } });
  }

  /**
   * 按分类收集系统数据
   */
  static async collectSystemsByCategory(category: string): Promise<ApiResponse> {
    return await request.get('/api/systems/v1/', { params: { category } });
  }
}