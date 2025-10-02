/**
 * Mock管理相关类型定义
 */

// Mock配置项
export interface MockConfig {
  id: string
  apiId: string
  name: string
  description?: string
  enabled: boolean
  priority: number // 优先级，数字越小优先级越高
  matchConditions: MockMatchCondition[] // 匹配条件
  responseData: any // 返回的Mock数据
  responseHeaders?: Record<string, string> // 响应头
  statusCode?: number // HTTP状态码，默认200
  delay?: number // 延迟时间（毫秒）
  updating?: boolean
  createdAt: string
  updatedAt: string
  createdBy?: string
}

// Mock匹配条件
export interface MockMatchCondition {
  id: string
  type: 'exact' | 'partial' | 'regex' | 'contains' // 匹配类型
  field: string // 匹配字段路径，如 'body.userId' 或 'query.type'
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'regex' | 'exists' | 'not_exists'
  value: any // 匹配值
  description?: string
}

// Mock匹配结果
export interface MockMatchResult {
  matched: boolean
  mockConfig?: MockConfig
  matchedConditions: string[] // 匹配的条件ID列表
  reason?: string // 不匹配的原因
}

// Mock执行结果
export interface MockExecutionResult {
  success: boolean
  data: any
  headers?: Record<string, string>
  statusCode: number
  delay: number
  executedAt: string
  mockConfigId: string
  error?: string
}

// Mock统计信息
export interface MockStats {
  apiId: string
  totalMocks: number
  enabledMocks: number
  totalExecutions: number
  successRate: number
  lastExecutedAt?: string
}

// Mock导入导出格式
export interface MockExportData {
  version: string
  apiId: string
  apiName: string
  mocks: MockConfig[]
  exportedAt: string
  exportedBy?: string
}

// Mock模板
export interface MockTemplate {
  id: string
  name: string
  description: string
  category: string
  template: Partial<MockConfig>
  isBuiltIn: boolean
}