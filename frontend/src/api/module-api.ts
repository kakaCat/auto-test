/**
 * 模块管理API (Module Management API)
 * 
 * 功能说明：
 * - 继承BaseApi，提供模块的完整生命周期管理
 * - 支持按系统分组管理模块
 * - 模块标签和分类管理
 * - 模块使用统计和监控
 * - 模块间的关联和依赖管理
 * 
 * 技术特性：
 * - 基于BaseApi的标准化CRUD操作
 * - 统一的错误处理和响应格式
 * - 完整的TypeScript类型支持
 * - 兼容现有API调用方式
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024
 */

import { BaseApi } from './base-api';
import type { BaseEntity, BaseListParams, BaseStatistics } from './base-api';
import type { ApiHandlerOptions } from '@/types';

// ==================== 类型定义 ====================

/**
 * 模块实体接口
 */
export interface ModuleEntity extends BaseEntity {
  system_id: string;           // 所属系统ID
  icon?: string;               // 模块图标
  path: string;                // 模块路径
  method?: string;             // HTTP方法
  version?: string;            // 模块版本
  module_type?: string;        // 模块类型
  tags?: string[];             // 模块标签
  config?: Record<string, any>; // 模块配置
  url?: string;                // 模块URL
  metadata?: Record<string, any>; // 元数据
}

/**
 * 模块列表查询参数
 */
export interface ModuleListParams extends BaseListParams {
  systemId?: string;           // 系统ID筛选（驼峰格式）
  system_id?: string;          // 系统ID筛选（下划线格式，兼容unified-api）
  enabled_only?: boolean;      // 只显示启用的模块
  tags?: string | string[];    // 标签筛选（支持字符串和数组格式）
  moduleType?: string;         // 模块类型筛选（驼峰格式）
  module_type?: string;        // 模块类型筛选（下划线格式，兼容unified-api）
  method?: string;             // HTTP方法筛选
  hasApis?: boolean;           // 是否有API（兼容性字段）
}

/**
 * 创建模块参数
 */
export interface CreateModuleParams {
  system_id: string;           // 所属系统ID（必填）
  name: string;                // 模块名称（必填）
  description?: string;        // 模块描述
  icon?: string;               // 模块图标
  path: string;                // 模块路径（必填）
  method?: string;             // HTTP方法
  enabled?: boolean;           // 是否启用
  version?: string;            // 模块版本
  module_type?: string;        // 模块类型
  tags?: string[];             // 模块标签
  config?: Record<string, any>; // 模块配置
  order_index?: number;        // 排序索引
}

/**
 * 更新模块参数
 */
export interface UpdateModuleParams extends Partial<CreateModuleParams> {
  id: number;                  // 模块ID（必填）
}

/**
 * 模块统计信息
 */
export interface ModuleStatistics extends BaseStatistics {
  modules_by_type: Record<string, number>; // 按类型分组统计
  modules_by_system: Record<string, number>; // 按系统分组统计
}

/**
 * 模块依赖关系
 */
export interface ModuleDependency {
  module_id: string;           // 模块ID
  depends_on: string[];        // 依赖的模块ID列表
  dependents: string[];        // 依赖此模块的模块ID列表
}

// ==================== API类实现 ====================

/**
 * 模块管理API类
 * 继承BaseApi，提供模块管理的完整功能
 */
export class ModuleApi extends BaseApi<ModuleEntity> {
  constructor() {
    super('/api/modules/v1');
  }

  // ==================== 基础CRUD操作 ====================
  // 继承自BaseApi的标准方法：
  // - getList(params): 获取模块列表
  // - getDetail(id): 获取模块详情
  // - create(data): 创建模块
  // - update(id, data): 更新模块
  // - delete(id): 删除模块
  // - toggleEnabled(id): 切换启用状态
  // - batchOperation(operation, ids): 批量操作

  // ==================== 模块特有方法 ====================

  /**
   * 获取指定系统的模块列表
   * @param systemId 系统ID
   * @param params 查询参数
   * @returns 模块列表
   */
  async getBySystem(systemId: string, params: Omit<ModuleListParams, 'system_id'> = {}): Promise<{data: ModuleEntity[], total: number}> {
    try {
      const queryParams = { ...params, system_id: systemId };
      return await this.getList(queryParams);
    } catch (error: any) {
      throw new Error(`获取系统模块列表失败: ${error?.message || error}`);
    }
  }

  /**
   * 获取启用的模块列表
   * @param params 查询参数
   * @returns 启用的模块列表
   */
  async getEnabledModules(params: ModuleListParams = {}): Promise<{data: ModuleEntity[], total: number}> {
    try {
      const queryParams = { ...params, enabled_only: true };
      return await this.getList(queryParams);
    } catch (error: any) {
      throw new Error(`获取启用模块列表失败: ${error?.message || error}`);
    }
  }

  /**
   * 按标签获取模块列表
   * @param tags 标签数组
   * @param params 其他查询参数
   * @returns 模块列表
   */
  async getByTags(tags: string[], params: Omit<ModuleListParams, 'tags'> = {}): Promise<{data: ModuleEntity[], total: number}> {
    try {
      const queryParams = { ...params, tags: tags.join(',') };
      return await this.getList(queryParams);
    } catch (error: any) {
      throw new Error(`按标签获取模块列表失败: ${error?.message || error}`);
    }
  }

  /**
   * 获取模块统计信息（重写父类方法以支持系统筛选）
   * @param options API处理选项，可包含system_id参数
   * @returns 模块统计数据
   */
  async getStatistics(options: ApiHandlerOptions & { system_id?: string } = {}): Promise<ModuleStatistics> {
    try {
      const { system_id, ...apiOptions } = options;
      const url = system_id 
        ? `${this.baseUrl}/statistics?system_id=${system_id}`
        : `${this.baseUrl}/statistics`;
      return await this.apiHandler.get<ModuleStatistics>(url, {}, apiOptions);
    } catch (error: any) {
      throw new Error(`获取模块统计信息失败: ${error?.message || error}`);
    }
  }

  /**
   * 获取模块依赖关系
   * @param moduleId 模块ID
   * @returns 模块依赖关系
   */
  async getDependencies(moduleId: string): Promise<ModuleDependency> {
    try {
      return await this.apiHandler.get<ModuleDependency>(`${this.baseUrl}/${moduleId}/dependencies`);
    } catch (error: any) {
      throw new Error(`获取模块依赖关系失败: ${error?.message || error}`);
    }
  }

  /**
   * 更新模块依赖关系
   * @param moduleId 模块ID
   * @param dependencies 依赖的模块ID列表
   * @returns 更新结果
   */
  async updateDependencies(moduleId: string, dependencies: string[]): Promise<ModuleDependency> {
    try {
      return await this.apiHandler.put<ModuleDependency>(
        `${this.baseUrl}/${moduleId}/dependencies`,
        { depends_on: dependencies }
      );
    } catch (error: any) {
      throw new Error(`更新模块依赖关系失败: ${error?.message || error}`);
    }
  }

  /**
   * 复制模块
   * @param moduleId 源模块ID
   * @param newName 新模块名称
   * @param systemId 可选的目标系统ID
   * @returns 新创建的模块
   */
  async copyModule(moduleId: string, newName: string, systemId?: string): Promise<ModuleEntity> {
    try {
      return await this.apiHandler.post<ModuleEntity>(`${this.baseUrl}/${moduleId}/copy`, {
        name: newName,
        system_id: systemId
      });
    } catch (error: any) {
      throw new Error(`复制模块失败: ${error?.message || error}`);
    }
  }

  /**
   * 移动模块到其他系统
   * @param moduleId 模块ID
   * @param targetSystemId 目标系统ID
   * @returns 更新结果
   */
  async moveToSystem(moduleId: string, targetSystemId: string): Promise<ModuleEntity> {
    try {
      return await this.apiHandler.put<ModuleEntity>(`${this.baseUrl}/${moduleId}/move`, {
        system_id: targetSystemId
      });
    } catch (error: any) {
      throw new Error(`移动模块失败: ${error?.message || error}`);
    }
  }

  /**
   * 获取模块使用统计
   * @param moduleId 模块ID
   * @param timeRange 时间范围（可选）
   * @returns 使用统计数据
   */
  async getUsageStats(moduleId: string, timeRange?: string): Promise<any> {
    try {
      const params = timeRange ? { time_range: timeRange } : {};
      return await this.apiHandler.get<any>(`${this.baseUrl}/${moduleId}/usage`, params);
    } catch (error: any) {
      throw new Error(`获取模块使用统计失败: ${error?.message || error}`);
    }
  }

  /**
   * 测试模块连接
   * @param moduleId 模块ID
   * @returns 测试结果
   */
  async testConnection(moduleId: string): Promise<any> {
    try {
      return await this.apiHandler.post<any>(`${this.baseUrl}/${moduleId}/test`);
    } catch (error: any) {
      throw new Error(`测试模块连接失败: ${error?.message || error}`);
    }
  }

  // ==================== 兼容性方法 ====================

  /**
   * 兼容旧版API：按系统获取模块（别名方法）
   * @deprecated 请使用 getBySystem 方法
   */
  async getModulesBySystem(systemId: string, params: any = {}): Promise<{data: ModuleEntity[], total: number}> {
    console.warn('getModulesBySystem 方法已废弃，请使用 getBySystem 方法');
    return this.getBySystem(systemId, params);
  }

  /**
   * 兼容旧版API：创建模块（别名方法）
   * @deprecated 请使用 create 方法
   */
  async createModule(data: CreateModuleParams): Promise<ModuleEntity> {
    console.warn('createModule 方法已废弃，请使用 create 方法');
    return this.create(data);
  }

  /**
   * 兼容旧版API：更新模块（别名方法）
   * @deprecated 请使用 update 方法
   */
  async updateModule(moduleId: number, data: Partial<CreateModuleParams>): Promise<ModuleEntity> {
    console.warn('updateModule 方法已废弃，请使用 update 方法');
    return this.update(moduleId, data);
  }

  /**
   * 兼容旧版API：删除模块（别名方法）
   * @deprecated 请使用 delete 方法
   */
  async deleteModule(moduleId: number): Promise<void> {
    console.warn('deleteModule 方法已废弃，请使用 delete 方法');
    return this.delete(moduleId);
  }
}

// ==================== 导出 ====================

/**
 * 模块API实例
 */
export const moduleApi = new ModuleApi();

/**
 * 默认导出
 */
export default moduleApi;
