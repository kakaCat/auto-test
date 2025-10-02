/**
 * 服务管理模块类型定义
 */

// 基础类型定义
import type { Component } from 'vue'
import { ApiResponse } from '@/types/api'

// 系统分类枚举
export enum SystemCategory {
  BACKEND = 'backend',
  FRONTEND = 'frontend'
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
  [SystemCategory.BACKEND]: '后端服务',
  [SystemCategory.FRONTEND]: '前端应用'
}

// 基础实体接口
export interface BaseEntity {
  id: string
  name: string
  description: string
  enabled: boolean
  order_index: number
  created_at?: string
  updated_at?: string
}

// 系统接口
export interface System extends BaseEntity {
  icon: string
  category: SystemCategory
  url: string
  metadata: Record<string, any>
  modules?: Module[]
}

// 模块接口
export interface Module extends BaseEntity {
  system_id: string
  icon: string
  path: string
  method: HttpMethod
  version: string
  module_type: ModuleType
  tags: string[]
  config: Record<string, any>
}

// 表单数据接口
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

// 分页配置接口
export interface PaginationConfig {
  currentPage: number
  pageSize: number
  total: number
  pageSizes: number[]
  // 兼容统一分页字段
  page?: number
  size?: number
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

// 组件 Props 接口
export interface ServiceManagementProps {
  initialSystemId?: string
  readonly?: boolean
}

// 组件 Emits 接口
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

// 错误处理接口
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

// 导出/导入配置接口
export interface ExportConfig {
  includeModules: boolean
  includeMetadata: boolean
  format: 'json' | 'yaml' | 'csv'
}

export interface ImportConfig {
  overwriteExisting: boolean
  validateData: boolean
  skipErrors: boolean
}