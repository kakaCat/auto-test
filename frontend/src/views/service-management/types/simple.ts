/**
 * 服务管理模块类型定义 - 简化版
 * 使用自增ID作为主键，移除UUID字段
 */

import type { Component } from 'vue'

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

// 基础实体接口 - 简化版
export interface BaseEntity {
  id: number                    // 自增主键ID
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

// 系统接口 - 简化版
export interface System extends BaseEntity {
  icon: string
  category: SystemCategory
  url: string
  metadata: Record<string, any>
  modules?: Module[]
}

// 模块接口 - 简化版
export interface Module extends BaseEntity {
  system_id: number             // 系统的自增ID
  icon: string
  path?: string
  method?: HttpMethod
  version?: string
  module_type?: ModuleType
  tags: string[]
  config: Record<string, any>
  url?: string
}

// 系统表单数据接口
export interface SystemFormData {
  id: number | null             // 自增ID，新建时为null
  name: string
  description: string
  icon: string
  category: SystemCategory | ''
  enabled: boolean
  order_index: number
  url: string
  metadata: Record<string, any>
}

// 模块表单数据接口
export interface ModuleFormData {
  id: number | null             // 自增ID，新建时为null
  system_id: number | null      // 系统自增ID
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

// 搜索表单数据接口
export interface SearchFormData {
  keyword: string
  category: SystemCategory | ''
  enabled: boolean | null
}

// 扩展搜索表单数据接口
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

// 选择选项接口
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
  id: number
  type: 'system' | 'module'
  hasChildren: boolean
  children?: TreeTableNode[]
  parentId?: number
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

// 服务管理组件属性接口
export interface ServiceManagementProps {
  initialSystemId?: number
  readonly?: boolean
}

// 服务管理组件事件接口
export interface ServiceManagementEmits {
  systemSelected: [systemId: number]
  moduleSelected: [moduleId: number, systemId: number]
  systemCreated: [system: System]
  moduleCreated: [module: Module, systemId: number]
  systemUpdated: [system: System]
  moduleUpdated: [module: Module]
  systemDeleted: [systemId: number]
  moduleDeleted: [moduleId: number, systemId: number]
}

// 服务错误接口
export interface ServiceError extends Error {
  code?: string
  details?: any
}

// API响应接口
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  error?: ServiceError
  timestamp?: string
}

// 批量操作接口
export interface BatchOperation {
  action: 'enable' | 'disable' | 'delete'
  targets: Array<{
    type: 'system' | 'module'
    id: number
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

// 系统统计接口
export interface SystemStatistics {
  total_systems: number
  enabled_systems: number
  disabled_systems: number
  systems_by_category: Record<string, number>
}

// 模块统计接口
export interface ModuleStatistics {
  total_modules: number
  enabled_modules: number
  disabled_modules: number
  modules_by_type: Record<string, number>
  modules_by_system: Record<string, number>
}

// 概览统计接口
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

// 性能指标接口
export interface PerformanceMetrics {
  response_time: number
  success_rate: number
  error_rate: number
  throughput: number
  timestamp: string
}

// 健康状态接口
export interface HealthStatus {
  status: 'healthy' | 'warning' | 'error'
  timestamp: string
  version: string
  database: 'connected' | 'disconnected'
  uptime?: number
}

// 默认系统表单数据
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

// 默认模块表单数据
export const defaultModuleForm: ModuleFormData = {
  id: null,
  system_id: null,
  name: '',
  description: '',
  icon: 'el-icon-service',
  path: '/',
  method: HttpMethod.GET,
  enabled: true,
  version: '1.0.0',
  module_type: ModuleType.GENERAL,
  tags: [],
  config: {},
  order_index: 0,
  url: ''
}

// 默认分页配置
export const defaultPagination: PaginationConfig = {
  currentPage: 1,
  pageSize: 10,
  total: 0,
  pageSizes: [10, 20, 50, 100]
}