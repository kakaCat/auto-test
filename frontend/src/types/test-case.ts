/**
 * 测试用例管理相关类型定义
 */

// 测试用例
export interface TestCase {
  id: string
  apiId: string
  name: string
  description?: string
  enabled: boolean
  category?: string // 测试分类：smoke, regression, integration等
  priority: 'high' | 'medium' | 'low'
  tags: string[]
  
  // 请求配置
  requestConfig: TestRequestConfig
  
  // 期望结果
  expectedResponse: TestExpectedResponse
  
  // 前置条件和后置操作
  preConditions?: TestCondition[]
  postActions?: TestAction[]
  
  // 执行配置
  executionConfig: TestExecutionConfig
  
  // 元数据
  createdAt: string
  updatedAt: string
  createdBy?: string
  lastExecutedAt?: string
  executionCount: number
  successCount: number
}

// 测试请求配置
export interface TestRequestConfig {
  method: string
  url: string
  headers: Record<string, string>
  queryParams: Record<string, any>
  bodyType: 'json' | 'form' | 'raw' | 'none'
  body: any
  timeout: number // 超时时间（毫秒）
  followRedirects: boolean
  validateSSL: boolean
}

// 期望响应
export interface TestExpectedResponse {
  statusCode: number | number[] // 期望的状态码，可以是单个或数组
  headers?: Record<string, string | RegExp> // 期望的响应头
  body?: TestResponseBodyAssertion // 响应体断言
  responseTime?: number // 最大响应时间（毫秒）
  size?: number // 响应大小限制（字节）
}

// 响应体断言
export interface TestResponseBodyAssertion {
  type: 'exact' | 'partial' | 'schema' | 'custom'
  value?: any // 期望值
  schema?: any // JSON Schema
  customScript?: string // 自定义断言脚本
  assertions: TestAssertion[] // 具体断言列表
}

// 测试断言
export interface TestAssertion {
  id: string
  field: string // 字段路径，如 'data.user.id'
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'exists' | 'not_exists' | 'regex' | 'type_of'
  value: any
  description?: string
  enabled: boolean
}

// 测试条件
export interface TestCondition {
  id: string
  type: 'api_call' | 'database_check' | 'variable_set' | 'delay'
  description: string
  config: any // 具体配置，根据type不同而不同
  enabled: boolean
}

// 测试后置操作
export interface TestAction {
  id: string
  type: 'extract_variable' | 'api_call' | 'database_update' | 'notification'
  description: string
  config: any
  enabled: boolean
}

// 测试执行配置
export interface TestExecutionConfig {
  retryCount: number // 重试次数
  retryDelay: number // 重试间隔（毫秒）
  continueOnFailure: boolean // 失败时是否继续执行其他测试
  parallel: boolean // 是否支持并行执行
  environment?: string // 执行环境
  variables: Record<string, any> // 测试变量
}

// 测试执行结果
export interface TestExecutionResult {
  id: string
  testCaseId: string
  status: 'success' | 'failure' | 'error' | 'skipped'
  startTime: string
  endTime: string
  duration: number // 执行时长（毫秒）
  
  // 请求信息
  actualRequest: TestRequestConfig
  
  // 响应信息
  actualResponse: {
    statusCode: number
    headers: Record<string, string>
    body: any
    responseTime: number
    size: number
  }
  
  // 断言结果
  assertionResults: TestAssertionResult[]
  
  // 错误信息
  error?: string
  stackTrace?: string
  
  // 截图和日志
  screenshots?: string[]
  logs: TestLog[]
}

// 断言结果
export interface TestAssertionResult {
  assertionId: string
  passed: boolean
  actual: any
  expected: any
  message: string
}

// 测试日志
export interface TestLog {
  level: 'debug' | 'info' | 'warn' | 'error'
  message: string
  timestamp: string
  data?: any
}

// 测试套件
export interface TestSuite {
  id: string
  name: string
  description?: string
  apiId: string
  testCases: string[] // 测试用例ID列表
  executionOrder: 'parallel' | 'custom'
  customOrder?: string[] // 自定义执行顺序
  enabled: boolean
  tags: string[]
  createdAt: string
  updatedAt: string
}

// 测试套件执行结果
export interface TestSuiteExecutionResult {
  id: string
  suiteId: string
  status: 'running' | 'completed' | 'failed' | 'cancelled'
  startTime: string
  endTime?: string
  totalDuration: number
  
  // 统计信息
  totalTests: number
  passedTests: number
  failedTests: number
  skippedTests: number
  
  // 详细结果
  testResults: TestExecutionResult[]
  
  // 环境信息
  environment: string
  executor?: string
}

// 测试报告
export interface TestReport {
  id: string
  name: string
  type: 'single' | 'suite' | 'batch'
  generatedAt: string
  period: {
    startDate: string
    endDate: string
  }
  
  // 统计数据
  summary: {
    totalExecutions: number
    successRate: number
    averageResponseTime: number
    totalDuration: number
  }
  
  // 详细数据
  executions: TestExecutionResult[]
  trends: TestTrend[]
}

// 测试趋势
export interface TestTrend {
  date: string
  successRate: number
  averageResponseTime: number
  totalExecutions: number
}