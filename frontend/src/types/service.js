/**
 * 服务列表相关的数据结构定义
 */

/**
 * 服务模块接口
 * @typedef {Object} ServiceModule
 * @property {string} id - 模块唯一标识
 * @property {string} name - 模块名称
 * @property {string} description - 模块描述
 * @property {string} icon - 模块图标
 * @property {string} path - 路由路径
 * @property {boolean} enabled - 是否启用
 * @property {string} version - 版本号
 * @property {Array<string>} tags - 标签
 * @property {Object} config - 模块配置
 */

/**
 * 管理系统接口
 * @typedef {Object} ManagementSystem
 * @property {string} id - 系统唯一标识
 * @property {string} name - 系统名称
 * @property {string} description - 系统描述
 * @property {string} icon - 系统图标
 * @property {string} category - 系统分类
 * @property {boolean} enabled - 是否启用
 * @property {number} order - 排序权重
 * @property {Array<ServiceModule>} modules - 系统下的模块列表
 * @property {Object} metadata - 系统元数据
 */

/**
 * 服务列表状态接口
 * @typedef {Object} ServiceListState
 * @property {Array<ManagementSystem>} systems - 管理系统列表
 * @property {boolean} loading - 加载状态
 * @property {string|null} error - 错误信息
 * @property {string|null} selectedSystemId - 当前选中的系统ID
 * @property {string|null} selectedModuleId - 当前选中的模块ID
 * @property {Object} filters - 过滤条件
 */

/**
 * 创建默认的服务模块
 * @param {Partial<ServiceModule>} module - 模块部分数据
 * @returns {ServiceModule} 完整的服务模块对象
 */
export function createServiceModule(module = {}) {
  return {
    id: '',
    name: '',
    description: '',
    icon: 'el-icon-service',
    path: '',
    enabled: true,
    version: '1.0.0',
    tags: [],
    config: {},
    ...module
  }
}

/**
 * 创建默认的管理系统
 * @param {Partial<ManagementSystem>} system - 系统部分数据
 * @returns {ManagementSystem} 完整的管理系统对象
 */
export function createManagementSystem(system = {}) {
  return {
    id: '',
    name: '',
    description: '',
    icon: 'el-icon-menu',
    category: 'default',
    enabled: true,
    order: 0,
    modules: [],
    metadata: {},
    ...system
  }
}

/**
 * 创建默认的服务列表状态
 * @returns {ServiceListState} 服务列表状态对象
 */
export function createServiceListState() {
  return {
    systems: [],
    loading: false,
    error: null,
    selectedSystemId: null,
    selectedModuleId: null,
    filters: {
      category: '',
      enabled: null,
      search: ''
    }
  }
}

/**
 * 服务状态枚举
 */
export const ServiceStatus = {
  ENABLED: 'enabled',
  DISABLED: 'disabled',
  MAINTENANCE: 'maintenance',
  ERROR: 'error'
}

/**
 * 系统分类枚举
 */
export const SystemCategory = {
  BACKEND: 'backend',
  FRONTEND: 'frontend'
}

/**
 * 系统分类显示名称映射
 */
export const SystemCategoryLabels = {
  [SystemCategory.BACKEND]: '后端服务',
  [SystemCategory.FRONTEND]: '前端应用'
}