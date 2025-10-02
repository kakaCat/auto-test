/**
 * API相关的TypeScript类型定义
 */

// 导入公共类型
import type {
  ApiResponse,
  PaginationParams,
  PaginationData,
  BaseEntity,
  CreateRequest,
  UpdateRequest,
  ListParams,
  StatusUpdateRequest,
  BatchOperationRequest,
  BatchOperationResponse,
  StatsData
} from './common'

// 重新导出公共类型，保持向后兼容
export type {
  ApiResponse,
  PaginationParams,
  PaginationData,
  StatusUpdateRequest,
  BatchOperationRequest,
  BatchOperationResponse,
  StatsData
} from './common'

// 系统管理相关类型
export interface SystemData {
  id: string
  name: string
  description?: string
  icon?: string
  category?: string
  enabled?: boolean
  order_index?: number
  url?: string
  metadata?: Record<string, any>
  created_at?: string
  updated_at?: string
}

export interface SystemCreateRequest {
  name: string
  description?: string
  icon?: string
  category?: string
  enabled?: boolean
  order_index?: number
  url?: string
  metadata?: Record<string, any>
}

export interface SystemUpdateRequest extends SystemCreateRequest {}

export interface SystemListParams {
  keyword?: string
  category?: string
  enabled_only?: boolean
}

// 模块管理相关类型
export interface ModuleData {
  id: string
  system_id: string
  name: string
  description?: string
  icon?: string
  path: string
  method?: string
  enabled?: boolean
  version?: string
  module_type?: string
  tags?: string[]
  config?: Record<string, any>
  order_index?: number
  created_at?: string
  updated_at?: string
}

export interface ModuleCreateRequest {
  system_id: string
  name: string
  description?: string
  icon?: string
  path: string
  method?: string
  enabled?: boolean
  version?: string
  module_type?: string
  tags?: string[]
  config?: Record<string, any>
  order_index?: number
}

export interface ModuleUpdateRequest extends ModuleCreateRequest {}

export interface ModuleListParams {
  system_id?: string
  keyword?: string
  enabled_only?: boolean
  tags?: string
}

// 服务管理相关类型
export interface ServiceData {
  id: string
  name: string
  description?: string
  url: string
  method?: string
  enabled?: boolean
  category?: string
  tags?: string[]
  created_at?: string
  updated_at?: string
}

export interface ServiceCreateRequest {
  name: string
  description?: string
  url: string
  method?: string
  enabled?: boolean
  category?: string
  tags?: string[]
}

export interface ServiceUpdateRequest extends ServiceCreateRequest {}

export interface ServiceListParams {
  keyword?: string
  method?: string
  category?: string
}

// API管理相关类型
export interface ApiData {
  id: string
  name: string
  service_name: string
  module_id: string
  version?: string
  method?: string
  protocol?: string
  url: string
  description?: string
  enabled?: boolean
  category?: string
  tags?: string[]
  headers?: Array<Record<string, any>>
  parameters?: Array<Record<string, any>>
  created_at?: string
  updated_at?: string
}

export interface ApiCreateRequest {
  name: string
  service_name: string
  module_id: string
  version?: string
  method?: string
  protocol?: string
  url: string
  description?: string
  enabled?: boolean
  category?: string
  tags?: string[]
  headers?: Array<Record<string, any>>
  parameters?: Array<Record<string, any>>
}

export interface ApiUpdateRequest extends ApiCreateRequest {}

export interface ApiListParams {
  keyword?: string
  method?: string
  category?: string
}

export interface ApiTestRequest {
  parameters?: Record<string, any>
  headers?: Record<string, any>
}

export interface ApiTestResponse {
  success: boolean
  status_code: number
  response_time: number
  response_data: any
  error?: string
}

// 工作流相关类型
export interface WorkflowData {
  id: string
  name: string
  description?: string
  category?: string
  version?: string
  config?: Record<string, any>
  nodes?: Array<Record<string, any>>
  connections?: Array<Record<string, any>>
  status?: string
  created_at?: string
  updated_at?: string
}

export interface WorkflowCreateRequest {
  name: string
  description?: string
  category?: string
  version?: string
  config?: Record<string, any>
  nodes?: Array<Record<string, any>>
  connections?: Array<Record<string, any>>
}

export interface WorkflowUpdateRequest extends WorkflowCreateRequest {}

export interface WorkflowListParams extends PaginationParams {
  keyword?: string
  status?: string
  category?: string
}

export interface WorkflowExecuteRequest {
  data?: Record<string, any>
}

export interface WorkflowExecuteResponse {
  execution_id: string
  status: string
  result?: any
}

// 场景管理相关类型
export interface ScenarioData {
  id: string
  name: string
  description?: string
  scenario_type?: 'normal' | 'exception' | 'boundary' | 'security' | 'performance'
  version?: string
  config?: Record<string, any>
  variables?: Record<string, any>
  tags?: string[]
  is_parameters_saved?: boolean
  saved_parameters_id?: string
  status?: string
  created_at?: string
  updated_at?: string
}

export interface ScenarioCreateRequest {
  name: string
  description?: string
  scenario_type?: 'normal' | 'exception' | 'boundary' | 'security' | 'performance'
  version?: string
  config?: Record<string, any>
  variables?: Record<string, any>
  tags?: string[]
  api_id?: string
}

export interface ScenarioUpdateRequest extends ScenarioCreateRequest {}

export interface ScenarioListParams {
  api_id: string
  keyword?: string
  status?: string
  tags?: string[]
  created_by?: string
  created_time_range?: [string, string]
  is_parameters_saved?: boolean
}

export interface ScenarioExecuteRequest {
  data?: Record<string, any>
}

export interface ScenarioExecuteResponse {
  execution_id: string
  status: string
  result?: any
}