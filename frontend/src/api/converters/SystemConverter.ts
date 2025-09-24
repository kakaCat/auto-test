/**
 * 系统数据转换器
 * 负责前后端系统数据格式转换
 */
export class SystemConverter {
  /**
   * 将后端系统数据转换为前端格式
   */
  static transformFromBackend(backendSystem: any): any {
    if (!backendSystem) return null;
    
    return {
      id: backendSystem.id,
      uuid: backendSystem.uuid,
      name: backendSystem.name,
      description: backendSystem.description || '',
      icon: backendSystem.icon || 'system',
      category: backendSystem.category || 'other',
      enabled: backendSystem.enabled ?? true,
      order_index: backendSystem.order_index || 0,
      url: backendSystem.url || '',
      metadata: backendSystem.metadata || {},
      created_at: backendSystem.created_at,
      updated_at: backendSystem.updated_at
    };
  }

  /**
   * 将前端系统数据转换为后端格式
   */
  static transformToBackend(frontendSystem: any): any {
    if (!frontendSystem) return null;
    
    return {
      name: frontendSystem.name,
      description: frontendSystem.description,
      icon: frontendSystem.icon,
      category: frontendSystem.category,
      enabled: frontendSystem.enabled,
      order_index: frontendSystem.order_index,
      url: frontendSystem.url,
      metadata: frontendSystem.metadata
    };
  }

  /**
   * 批量转换后端系统数据
   */
  static transformListFromBackend(backendSystems: any[]): any[] {
    if (!Array.isArray(backendSystems)) return [];
    return backendSystems.map(system => this.transformFromBackend(system));
  }
}