/**
 * 类型定义统一导出
 * 提供项目中所有类型的统一入口
 */

// 导出公共类型
export * from './common'

// 导出API相关类型
export * from './api'

// 重新导出常用类型，提供更好的开发体验
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
} from './common'

// 业务相关类型
export type {
  SystemData,
  SystemCreateRequest,
  SystemUpdateRequest,
  SystemListParams,
  ModuleData,
  ModuleCreateRequest,
  ModuleUpdateRequest,
  ModuleListParams,
  ServiceData,
  ServiceCreateRequest,
  ServiceUpdateRequest,
  ServiceListParams,
  ApiData,
  ApiCreateRequest,
  ApiUpdateRequest,
  ApiListParams,
  ApiTestRequest,
  ApiTestResponse,
  WorkflowData,
  WorkflowCreateRequest,
  WorkflowUpdateRequest,
  WorkflowListParams,
  WorkflowExecuteRequest,
  WorkflowExecuteResponse,
  ScenarioData,
  ScenarioCreateRequest,
  ScenarioUpdateRequest,
  ScenarioListParams,
  ScenarioExecuteRequest,
  ScenarioExecuteResponse
} from './api'