/**
 * 模块数据转换器
 * 负责前后端模块数据格式转换
 */
export class ModuleConverter {
  /**
   * 将后端模块数据转换为前端格式
   */
  static transformFromBackend(backendModule: any): any {
    if (!backendModule) return null;
    
    return {
      id: backendModule.id,
      uuid: backendModule.uuid,
      system_id: backendModule.system_id,
      name: backendModule.name,
      description: backendModule.description || '',
      icon: backendModule.icon || 'module',
      url: backendModule.url || '',
      enabled: backendModule.enabled ?? true,
      order_index: backendModule.order_index || 0,
      metadata: backendModule.metadata || {},
      tags: backendModule.tags || [],
      created_at: backendModule.created_at,
      updated_at: backendModule.updated_at
    };
  }

  /**
   * 将前端模块数据转换为后端格式
   */
  static transformToBackend(frontendModule: any): any {
    if (!frontendModule) return null;
    
    return {
      system_id: frontendModule.system_id,
      name: frontendModule.name,
      description: frontendModule.description,
      icon: frontendModule.icon,
      url: frontendModule.url,
      enabled: frontendModule.enabled,
      order_index: frontendModule.order_index,
      metadata: frontendModule.metadata,
      tags: frontendModule.tags
    };
  }

  /**
   * 批量转换后端模块数据
   */
  static transformListFromBackend(backendModules: any[]): any[] {
    if (!Array.isArray(backendModules)) return [];
    return backendModules.map(module => this.transformFromBackend(module));
  }
}