/**
 * 公共类型定义
 * 统一管理项目中的通用类型，避免重复定义
 */

// ============= 基础响应类型 =============
// 统一错误与结果模型
export interface ApiError extends ErrorInfo {}

export interface Result<T = unknown> {
  success: boolean
  message: string
  data?: T
  error?: ApiError
  code?: number | string
  timestamp?: string
}

// 兼容旧命名：保持ApiResponse与Result一致
export interface ApiResponse<T = unknown> extends Result<T> {}

// ============= 分页相关类型 =============
export interface PaginationParams {
  page?: number
  size?: number
  pageSize?: number
}

export interface PaginationData<T> {
  list: T[]
  total: number
  page: number
  // 新规范字段
  size: number
  // 兼容旧字段（逐步废弃）
  pageSize: number
}

export interface PaginatedResponse<T> extends ApiResponse<PaginationData<T>> {}

// ============= 通用请求类型 =============
export interface BaseEntity {
  id: string
  created_at?: string
  updated_at?: string
}

export interface CreateRequest {
  [key: string]: unknown
}

export interface UpdateRequest extends CreateRequest {
  id?: string
}

export interface ListParams extends PaginationParams {
  keyword?: string
  [key: string]: unknown
}

// ============= 状态相关类型 =============
export interface StatusUpdateRequest {
  enabled: boolean
}

export interface BatchOperationRequest {
  ids: string[]
  action: 'enable' | 'disable' | 'delete'
  target_id?: string
}

export interface BatchOperationResponse {
  success_count: number
  failed_count: number
  errors?: string[]
}

// ============= 缓存相关类型 =============
export interface CacheOptions {
  cacheTime?: number
  cacheKey?: string
  invalidateCache?: string[]
}

export interface CacheData<T = unknown> {
  data: T
  expireTime: number
}

// ============= API处理选项 =============
export interface ApiHandlerOptions extends CacheOptions {
  showLoading?: boolean
  showSuccess?: boolean
  showError?: boolean
  retryCount?: number
  retryDelay?: number
  timeout?: number
  cache?: boolean
  transform?: ((data: unknown) => unknown) | null
  successMessage?: string | null
  errorMessage?: string | null
  loadingText?: string
  showProgress?: boolean
  maxConcurrent?: number
  stopOnError?: boolean
}

// ============= 统计数据类型 =============
export interface StatsData {
  total: number
  active: number
  inactive: number
  categories?: Record<string, number>
  trends?: Array<{
    date: string
    count: number
  }>
}

// ============= 错误处理类型 =============
export interface ErrorInfo {
  code?: string | number
  message: string
  details?: unknown
  timestamp?: string
}

export interface ValidationError {
  field: string
  message: string
  value?: unknown
}

// ============= 文件操作类型 =============
export interface FileUploadOptions {
  accept?: string
  maxSize?: number
  multiple?: boolean
}

export interface DownloadParams {
  filename?: string
  contentType?: string
  [key: string]: unknown
}

// ============= 工具类型 =============
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// ============= 常量类型 =============
export const HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'] as const
export type HttpMethod = typeof HTTP_METHODS[number]

export const OPERATION_TYPES = ['create', 'update', 'delete', 'enable', 'disable'] as const
export type OperationType = typeof OPERATION_TYPES[number]

export const STATUS_TYPES = ['enabled', 'disabled', 'maintenance', 'error'] as const
export type StatusType = typeof STATUS_TYPES[number]