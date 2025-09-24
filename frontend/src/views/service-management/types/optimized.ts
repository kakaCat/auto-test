/**
 * 服务管理模块类型定义 - 优化版
 * 适配新的数据库结构：自增ID主键 + UUID业务标识符
 */

import type { Component } from 'vue'
import { ApiResponse } from '@/types/api'

// 系统分类枚举
export enum SystemCategory {
  USER_MANAGEMENT = 'user_management',
  CONTENT_MANAGEMENT = 'content_management',
  API_MANAGEMENT = 'api_management',
  WORKFLOW_MANAGEMENT = 'workflow_management',
  AI_SERVICES = 'ai_services',
  MONITORING = 'monitoring',
  SECURITY = 'security',
  CUSTOM = 'custom'
}

// HTTP 方法枚举
export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE',
  PATCH = 'PATCH'
}

// 模块类型枚举
export enum ModuleType {
  GENERAL = '通用模块',
  API = 'API模块',
  FRONTEND = '前端模块',
  BACKEND = '后端模块',
  MONITORING = '监控模块',
  MANAGEMENT = '管理模块'
}

// 系统分类标签映射
export const SystemCategoryLabels: Record<SystemCategory, string> = {
  [SystemCategory.USER_MANAGEMENT]: '用户管理',
  [SystemCategory.CONTENT_MANAGEMENT]: '内容管理',
  [SystemCategory.API_MANAGEMENT]: 'API管理',
  [SystemCategory.WORKFLOW_MANAGEMENT]: '工作流管理',
  [SystemCategory.AI_SERVICES]: 'AI服务',
  [SystemCategory.MONITORING]: '监控系统',
  [SystemCategory.SECURITY]: '安全系统',
  [SystemCategory.CUSTOM]: '自定义'
}

// 基础实体接口 - 优化版
export interface BaseEntityOptimized {
  id: number                    // 自增主键ID
  uuid: string                  // UUID业务标识符
  name: string
  description: string
  enabled: boolean
  order_index: number
  created_at?: string
  updated_at?: string
  created_by?: string
  updated_by?: string
  deleted?: boolean
  deleted_at?: string
}

// 系统接口 - 优化版
export interface SystemOptimized extends BaseEntityOptimized {
  icon: string
  category: SystemCategory
  url: string
  metadata: Record<string, any>
  modules?: ModuleOptimized[]
}

// 模块接口 - 优化版
export interface ModuleOptimized extends BaseEntityOptimized {
  system_id: number             // 系统的自增ID
  system_uuid: string           // 系统的UUID（冗余字段，便于查询）
  icon: string
  path?: string
  method?: HttpMethod
  version?: string
  module_type?: ModuleType
  tags: string[]
  config: Record<string, any>
  url?: string
}

// 向后兼容的系统接口（前端使用UUID）
export interface System {
  id: string                    // 对应 uuid 字段
  name: string
  description: string
  icon: string
  category: SystemCategory
  enabled: boolean
  order_index: number
  url: string
  metadata: Record<string, any>
  modules?: Module[]
  created_at?: string
  updated_at?: string
}

// 向后兼容的模块接口（前端使用UUID）
export interface Module {
  id: string                    // 对应 uuid 字段
  system_id: string             // 对应 system_uuid 字段
  name: string
  description: string
  icon: string
  path?: string
  method?: HttpMethod
  enabled: boolean
  version?: string
  module_type?: ModuleType
  tags: string[]
  config: Record<string, any>
  order_index: number
  url?: string
  created_at?: string
  updated_at?: string
}

// 表单数据接口 - 优化版
export interface SystemFormDataOptimized {
  id: string | null             // UUID，新建时为null
  name: string
  description: string
  icon: string
  category: SystemCategory | ''
  enabled: boolean
  order_index: number
  url: string
  metadata: Record<string, any>
}

export interface ModuleFormDataOptimized {
  id: string | null             // UUID，新建时为null
  system_id: string | null      // 系统UUID
  name: string
  description: string
  icon: string
  path: string
  method: HttpMethod
  enabled: boolean
  version: string
  module_type: ModuleType
  tags: string[]
  config: Record<string, any>
  order_index: number
  url: string
}

// 向后兼容的表单数据接口
export interface SystemFormData {
  id: string | null
  name: string
  description: string
  icon: string
  category: SystemCategory | ''
  enabled: boolean
  order_index: number
  url: string
  metadata: Record<string, any>
}

export interface ModuleFormData {
  id: string | null
  system_id: string | null
  name: string
  description: string
  icon: string
  path: string
  method: HttpMethod
  enabled: boolean
  version: string
  module_type: ModuleType
  tags: string[]
  config: Record<string, any>
  order_index: number
}

// 搜索表单接口
export interface SearchFormData {
  keyword: string
  category: SystemCategory | ''
  enabled: boolean | null
}

export interface ExtendedSearchFormData extends SearchFormData {
  name: string
}

// 分页配置接口
export interface PaginationConfig {
  currentPage: number
  pageSize: number
  total: number
  pageSizes: number[]
}

// 选项接口
export interface SelectOption<T = any> {
  value: T
  label: string
}

// 表单验证规则接口
export interface FormRule {
  required?: boolean
  message: string
  trigger: 'blur' | 'change'
  min?: number
  max?: number
  pattern?: RegExp
}

export interface FormRules {
  [key: string]: FormRule[]
}

// 树形表格节点接口
export interface TreeTableNode {
  id: string
  type: 'system' | 'module'
  hasChildren: boolean
  children?: TreeTableNode[]
  parentId?: string
  [key: string]: any
}

// 图标映射接口
export interface IconMap {
  [key: string]: Component
}

// 标签类型映射接口
export interface TagTypeMap {
  [key: string]: 'primary' | 'success' | 'warning' | 'info' | 'danger'
}

// 组件属性接口
export interface ServiceManagementProps {
  initialSystemId?: string
  readonly?: boolean
}

// 组件事件接口
export interface ServiceManagementEmits {
  systemSelected: [systemId: string]
  moduleSelected: [moduleId: string, systemId: string]
  systemCreated: [system: System]
  moduleCreated: [module: Module, systemId: string]
  systemUpdated: [system: System]
  moduleUpdated: [module: Module]
  systemDeleted: [systemId: string]
  moduleDeleted: [moduleId: string, systemId: string]
}

// 错误接口
export interface ServiceError extends Error {
  code?: string
  details?: any
}



// 批量操作接口
export interface BatchOperation {
  action: 'enable' | 'disable' | 'delete'
  targets: Array<{
    type: 'system' | 'module'
    id: string
  }>
}

// 导出配置接口
export interface ExportConfig {
  includeModules: boolean
  includeMetadata: boolean
  format: 'json' | 'yaml' | 'csv'
}

// 导入配置接口
export interface ImportConfig {
  overwriteExisting: boolean
  validateData: boolean
  skipErrors: boolean
}

// 数据转换工具函数类型
export interface DataTransformer {
  // 将优化版数据转换为兼容版数据
  systemOptimizedToCompatible: (system: SystemOptimized) => System
  moduleOptimizedToCompatible: (module: ModuleOptimized) => Module
  
  // 将兼容版数据转换为优化版数据
  systemCompatibleToOptimized: (system: System) => Partial<SystemOptimized>
  moduleCompatibleToOptimized: (module: Module) => Partial<ModuleOptimized>
}

// 统计信息接口
export interface SystemStatistics {
  total_systems: number
  enabled_systems: number
  disabled_systems: number
  systems_by_category: Record<string, number>
}

export interface ModuleStatistics {
  total_modules: number
  enabled_modules: number
  disabled_modules: number
  modules_by_type: Record<string, number>
  modules_by_system: Record<string, number>
}

export interface OverviewStatistics {
  systems: SystemStatistics
  modules: ModuleStatistics
  overview: {
    total_systems: number
    enabled_systems: number
    total_modules: number
    enabled_modules: number
  }
}

// 监控和性能接口
export interface PerformanceMetrics {
  response_time: number
  success_rate: number
  error_rate: number
  throughput: number
  timestamp: string
}

export interface HealthStatus {
  status: 'healthy' | 'warning' | 'error'
  timestamp: string
  version: string
  database: 'connected' | 'disconnected'
  uptime?: number
}

// 默认值常量
export const defaultSystemForm: SystemFormData = {
  id: null,
  name: '',
  description: '',
  icon: 'el-icon-menu',
  category: '',
  enabled: true,
  order_index: 0,
  url: '',
  metadata: {}
}

export const defaultModuleForm: ModuleFormData = {
  id: null,
  system_id: null,
  name: '',
  description: '',
  icon: 'el-icon-service',
  path: '',
  method: HttpMethod.GET,
  enabled: true,
  version: '1.0.0',
  module_type: ModuleType.GENERAL,
  tags: [],
  config: {},
  order_index: 0
}

export const defaultPagination: PaginationConfig = {
  currentPage: 1,
  pageSize: 10,
  total: 0,
  pageSizes: [10, 20, 50, 100]
}

// 数据转换工具函数
export const dataTransformer: DataTransformer = {
  systemOptimizedToCompatible: (system: SystemOptimized): System => ({
    id: system.uuid,
    name: system.name,
    description: system.description,
    icon: system.icon,
    category: system.category,
    enabled: system.enabled,
    order_index: system.order_index,
    url: system.url,
    metadata: system.metadata,
    modules: system.modules?.map(module => dataTransformer.moduleOptimizedToCompatible(module)),
    created_at: system.created_at,
    updated_at: system.updated_at
  }),

  moduleOptimizedToCompatible: (module: ModuleOptimized): Module => ({
    id: module.uuid,
    system_id: module.system_uuid,
    name: module.name,
    description: module.description,
    icon: module.icon,
    path: module.path,
    method: module.method,
    enabled: module.enabled,
    version: module.version,
    module_type: module.module_type,
    tags: module.tags,
    config: module.config,
    order_index: module.order_index,
    url: module.url,
    created_at: module.created_at,
    updated_at: module.updated_at
  }),

  systemCompatibleToOptimized: (system: System): Partial<SystemOptimized> => ({
    uuid: system.id,
    name: system.name,
    description: system.description,
    icon: system.icon,
    category: system.category,
    enabled: system.enabled,
    order_index: system.order_index,
    url: system.url,
    metadata: system.metadata
  }),

  moduleCompatibleToOptimized: (module: Module): Partial<ModuleOptimized> => ({
    uuid: module.id,
    system_uuid: module.system_id,
    name: module.name,
    description: module.description,
    icon: module.icon,
    path: module.path,
    method: module.method,
    enabled: module.enabled,
    version: module.version,
    module_type: module.module_type,
    tags: module.tags,
    config: module.config,
    order_index: module.order_index,
    url: module.url
  })
}