/**
 * API 统一类型定义
 * 
 * 功能概述：
 * - 整合所有API相关的类型定义
 * - 提供统一的类型导入入口
 * - 确保类型的一致性和可维护性
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024-01-15
 */

// 从common types导出通用类型
export type {
  ApiResponse,
  PaginationParams,
  PaginationData,
  PaginatedResponse,
  BaseEntity,
  CreateRequest,
  UpdateRequest,
  ListParams,
  StatusUpdateRequest,
  BatchOperationRequest,
  BatchOperationResponse,
  CacheOptions,
  ApiHandlerOptions,
  StatsData,
  ErrorInfo,
  ValidationError,
  FileUploadOptions,
  DownloadParams,
  HttpMethod,
  OperationType,
  StatusType
} from '@/types/common';

// 通用工具类型
export type EntityType = 'system' | 'module' | 'category';

/**
 * API操作结果类型
 */
export interface ApiOperationResult<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
  timestamp: string;
}

/**
 * 批量操作结果类型
 */
export interface BatchOperationResult {
  successful: number;
  failed: number;
  errors?: Array<{
    id: number | string;
    error: string;
  }>;
}

/**
 * 分页结果类型
 */
export interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/**
 * 搜索结果类型
 */
export interface SearchResult<T> {
  items: T[];
  total: number;
  query: string;
  suggestions?: string[];
}

/**
 * 导出配置类型
 */
export interface ExportConfig {
  format: 'json' | 'csv' | 'excel';
  filename?: string;
  fields?: string[];
  filters?: Record<string, any>;
}

/**
 * 导入配置类型
 */
export interface ImportConfig {
  file: File;
  format: 'json' | 'csv' | 'excel';
  mapping?: Record<string, string>;
  skipErrors?: boolean;
}

/**
 * API错误类型
 */
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

/**
 * API配置类型
 */
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  headers?: Record<string, string>;
}

/**
 * 缓存配置类型
 */
export interface CacheConfig {
  enabled: boolean;
  ttl: number;
  key?: string;
}

/**
 * 请求选项类型
 */
export interface RequestOptions {
  cache?: CacheConfig;
  timeout?: number;
  retries?: number;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}