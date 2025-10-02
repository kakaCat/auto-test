/**
 * 工作流执行引擎类型定义
 * 
 * 定义了工作流执行过程中的各种类型和接口
 * 包括执行器、调度器、状态管理等
 */

import { NodeStatus, WorkflowNode, NodeConnection, ExecutionContext, NodeExecutionResult } from './nodeTypes'

// 执行模式枚举
export enum ExecutionMode {
  PARALLEL = 'PARALLEL',       // 并行执行
  MIXED = 'MIXED'              // 混合执行
}

// 执行状态枚举
export enum ExecutionStatus {
  PENDING = 'PENDING',         // 等待执行
  RUNNING = 'RUNNING',         // 执行中
  PAUSED = 'PAUSED',           // 暂停
  SUCCESS = 'SUCCESS',         // 成功完成
  FAILED = 'FAILED',           // 执行失败
  CANCELLED = 'CANCELLED',     // 已取消
  TIMEOUT = 'TIMEOUT'          // 超时
}

// 错误处理策略枚举
export enum ErrorHandlingStrategy {
  STOP_ON_ERROR = 'STOP_ON_ERROR',         // 遇到错误停止
  CONTINUE_ON_ERROR = 'CONTINUE_ON_ERROR', // 遇到错误继续
  RETRY_ON_ERROR = 'RETRY_ON_ERROR',       // 遇到错误重试
  SKIP_ON_ERROR = 'SKIP_ON_ERROR'          // 遇到错误跳过
}

// 执行配置接口
export interface ExecutionConfig {
  mode: ExecutionMode
  timeout: number // 总超时时间（毫秒）
  maxRetries: number
  retryDelay: number
  errorHandling: ErrorHandlingStrategy
  enableDebug: boolean
  enableProfiling: boolean
  maxConcurrency: number
  variables: Record<string, any>
}

// 执行计划接口
export interface ExecutionPlan {
  id: string
  workflowId: string
  nodes: ExecutionNode[]
  dependencies: ExecutionDependency[]
  estimatedDuration: number
  createdAt: string
}

// 执行节点接口
export interface ExecutionNode {
  id: string
  nodeId: string
  node: WorkflowNode
  dependencies: string[] // 依赖的节点ID列表
  dependents: string[]   // 依赖此节点的节点ID列表
  level: number          // 执行层级
  estimatedDuration: number
  priority: number
}

// 执行依赖接口
export interface ExecutionDependency {
  fromNodeId: string
  toNodeId: string
  connection: NodeConnection
  condition?: string
}

// 执行实例接口
export interface ExecutionInstance {
  id: string
  workflowId: string
  planId: string
  status: ExecutionStatus
  config: ExecutionConfig
  context: ExecutionContext
  nodeResults: Map<string, NodeExecutionResult>
  currentNodes: string[] // 当前正在执行的节点
  completedNodes: string[] // 已完成的节点
  failedNodes: string[] // 失败的节点
  startTime: string
  endTime?: string
  duration?: number
  progress: ExecutionProgress
  metrics: ExecutionMetrics
  logs: ExecutionLog[]
  error?: ExecutionError
}

// 执行进度接口
export interface ExecutionProgress {
  totalNodes: number
  completedNodes: number
  failedNodes: number
  skippedNodes: number
  percentage: number
  currentPhase: string
  estimatedTimeRemaining: number
}

// 执行指标接口
export interface ExecutionMetrics {
  totalDuration: number
  nodeExecutionTimes: Record<string, number>
  memoryUsage: number
  cpuUsage: number
  networkRequests: number
  errorCount: number
  retryCount: number
  throughput: number
}

// 执行日志接口
export interface ExecutionLog {
  id: string
  timestamp: string
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'
  nodeId?: string
  message: string
  data?: any
  duration?: number
}

// 执行错误接口
export interface ExecutionError {
  code: string
  message: string
  nodeId?: string
  timestamp: string
  stack?: string
  context?: any
  recoverable: boolean
}

// 节点执行器接口
export interface NodeExecutor {
  nodeType: string
  execute(node: WorkflowNode, context: ExecutionContext): Promise<NodeExecutionResult>
  validate(node: WorkflowNode): Promise<boolean>
  cancel(executionId: string): Promise<void>
}

// 工作流调度器接口
export interface WorkflowScheduler {
  schedule(plan: ExecutionPlan, config: ExecutionConfig): Promise<ExecutionInstance>
  execute(instance: ExecutionInstance): Promise<ExecutionInstance>
  pause(instanceId: string): Promise<void>
  resume(instanceId: string): Promise<void>
  cancel(instanceId: string): Promise<void>
  getStatus(instanceId: string): Promise<ExecutionStatus>
  getProgress(instanceId: string): Promise<ExecutionProgress>
  getLogs(instanceId: string, filter?: LogFilter): Promise<ExecutionLog[]>
}

// 日志过滤器接口
export interface LogFilter {
  level?: string[]
  nodeId?: string
  startTime?: string
  endTime?: string
  keyword?: string
  limit?: number
  offset?: number
}

// 执行事件接口
export interface ExecutionEvent {
  type: ExecutionEventType
  instanceId: string
  nodeId?: string
  timestamp: string
  data?: any
}

// 执行事件类型枚举
export enum ExecutionEventType {
  EXECUTION_STARTED = 'EXECUTION_STARTED',
  EXECUTION_COMPLETED = 'EXECUTION_COMPLETED',
  EXECUTION_FAILED = 'EXECUTION_FAILED',
  EXECUTION_CANCELLED = 'EXECUTION_CANCELLED',
  EXECUTION_PAUSED = 'EXECUTION_PAUSED',
  EXECUTION_RESUMED = 'EXECUTION_RESUMED',
  NODE_STARTED = 'NODE_STARTED',
  NODE_COMPLETED = 'NODE_COMPLETED',
  NODE_FAILED = 'NODE_FAILED',
  NODE_SKIPPED = 'NODE_SKIPPED',
  NODE_RETRYING = 'NODE_RETRYING',
  PROGRESS_UPDATED = 'PROGRESS_UPDATED',
  LOG_ADDED = 'LOG_ADDED',
  ERROR_OCCURRED = 'ERROR_OCCURRED'
}

// 执行监听器接口
export interface ExecutionListener {
  onEvent(event: ExecutionEvent): void
}

// 断点配置接口
export interface Breakpoint {
  id: string
  nodeId: string
  condition?: string // 断点条件表达式
  enabled: boolean
  hitCount: number
  createdAt: string
}

// 调试会话接口
export interface DebugSession {
  id: string
  instanceId: string
  breakpoints: Breakpoint[]
  currentNodeId?: string
  variables: Record<string, any>
  callStack: string[]
  status: 'RUNNING' | 'PAUSED' | 'STOPPED'
}

// 性能分析结果接口
export interface ProfilingResult {
  instanceId: string
  totalDuration: number
  nodeProfiles: NodeProfile[]
  bottlenecks: Bottleneck[]
  recommendations: string[]
  generatedAt: string
}

// 节点性能分析接口
export interface NodeProfile {
  nodeId: string
  nodeName: string
  executionCount: number
  totalDuration: number
  averageDuration: number
  minDuration: number
  maxDuration: number
  errorRate: number
  throughput: number
  memoryUsage: number
  cpuUsage: number
}

// 性能瓶颈接口
export interface Bottleneck {
  type: 'SLOW_NODE' | 'HIGH_ERROR_RATE' | 'MEMORY_LEAK' | 'CPU_INTENSIVE'
  nodeId: string
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  description: string
  impact: number // 影响程度（0-100）
  suggestion: string
}

// 执行统计接口
export interface ExecutionStatistics {
  totalExecutions: number
  successfulExecutions: number
  failedExecutions: number
  averageDuration: number
  successRate: number
  errorRate: number
  mostUsedNodes: string[]
  performanceMetrics: PerformanceMetrics
  timeSeriesData: TimeSeriesData[]
}

// 性能指标接口
export interface PerformanceMetrics {
  averageExecutionTime: number
  p50ExecutionTime: number
  p95ExecutionTime: number
  p99ExecutionTime: number
  throughputPerHour: number
  errorRatePercentage: number
  resourceUtilization: ResourceUtilization
}

// 资源利用率接口
export interface ResourceUtilization {
  cpu: number
  memory: number
  network: number
  storage: number
}

// 时间序列数据接口
export interface TimeSeriesData {
  timestamp: string
  executionCount: number
  successCount: number
  failureCount: number
  averageDuration: number
  errorRate: number
}

// 执行队列接口
export interface ExecutionQueue {
  id: string
  name: string
  priority: number
  maxConcurrency: number
  currentExecutions: number
  pendingExecutions: ExecutionQueueItem[]
  status: 'ACTIVE' | 'PAUSED' | 'STOPPED'
}

// 执行队列项接口
export interface ExecutionQueueItem {
  id: string
  workflowId: string
  priority: number
  config: ExecutionConfig
  scheduledTime: string
  submittedTime: string
  estimatedDuration: number
  dependencies: string[]
}

// 资源限制接口
export interface ResourceLimits {
  maxMemory: number // MB
  maxCpuUsage: number // 百分比
  maxExecutionTime: number // 秒
  maxConcurrentNodes: number
  maxNetworkRequests: number
  maxStorageUsage: number // MB
}

// 执行环境接口
export interface ExecutionEnvironment {
  id: string
  name: string
  type: 'DEVELOPMENT' | 'TESTING' | 'STAGING' | 'PRODUCTION'
  config: EnvironmentConfig
  resources: ResourceLimits
  variables: Record<string, any>
  secrets: Record<string, string>
  status: 'ACTIVE' | 'INACTIVE' | 'MAINTENANCE'
}

// 环境配置接口
export interface EnvironmentConfig {
  apiBaseUrl: string
  timeout: number
  retryCount: number
  logLevel: string
  enableDebug: boolean
  enableProfiling: boolean
  enableMetrics: boolean
  customSettings: Record<string, any>
}