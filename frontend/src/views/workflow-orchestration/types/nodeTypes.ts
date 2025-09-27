/**
 * 工作流节点类型定义
 * 
 * 定义了拖拽式工作流设计器中所有节点类型的接口和枚举
 * 包括API调用、数据转换、条件分支、并行执行等节点类型
 */

// 节点类型枚举
export enum NodeType {
  START = 'START',           // 开始节点
  END = 'END',               // 结束节点
  API_CALL = 'API_CALL',     // API调用节点
  DATA_TRANSFORM = 'DATA_TRANSFORM', // 数据转换节点
  CONDITION = 'CONDITION',   // 条件分支节点
  PARALLEL = 'PARALLEL',     // 并行执行节点
  MERGE = 'MERGE'            // 合并节点
}

// 节点状态枚举
export enum NodeStatus {
  IDLE = 'IDLE',             // 空闲状态
  WAITING = 'WAITING',       // 等待执行
  RUNNING = 'RUNNING',       // 执行中
  SUCCESS = 'SUCCESS',       // 执行成功
  FAILED = 'FAILED',         // 执行失败
  SKIPPED = 'SKIPPED'        // 跳过执行
}

// 连接类型枚举
export enum ConnectionType {
  SEQUENCE = 'SEQUENCE',     // 顺序连接
  CONDITION = 'CONDITION',   // 条件连接
  PARALLEL = 'PARALLEL'      // 并行连接
}

// 基础节点接口
export interface BaseNode {
  id: string
  type: NodeType
  name: string
  description?: string
  position: {
    x: number
    y: number
  }
  status: NodeStatus
  config: Record<string, any>
  inputs: NodeInput[]
  outputs: NodeOutput[]
  createdAt: string
  updatedAt: string
}

// 节点输入接口
export interface NodeInput {
  id: string
  name: string
  type: string
  required: boolean
  defaultValue?: any
  description?: string
}

// 节点输出接口
export interface NodeOutput {
  id: string
  name: string
  type: string
  description?: string
}

// API调用节点配置
export interface ApiCallNodeConfig {
  systemId: string
  moduleId: string
  apiId: string
  method: string
  url: string
  headers: Record<string, string>
  parameters: Record<string, any>
  timeout: number
  retryCount: number
  retryDelay: number
}

// API调用节点
export interface ApiCallNode extends BaseNode {
  type: NodeType.API_CALL
  config: ApiCallNodeConfig
  // 支持多个输入输出端口
  maxInputs?: number
  maxOutputs?: number
}

// 数据转换节点配置
export interface DataTransformNodeConfig {
  transformType: 'MAPPING' | 'FORMAT' | 'FILTER' | 'AGGREGATE'
  mappingRules: MappingRule[]
  formatConfig?: FormatConfig
  filterConfig?: FilterConfig
  aggregateConfig?: AggregateConfig
}

// 映射规则
export interface MappingRule {
  sourceField: string
  targetField: string
  transform?: string // JavaScript表达式
  defaultValue?: any
}

// 格式配置
export interface FormatConfig {
  inputFormat: string
  outputFormat: string
  dateFormat?: string
  numberFormat?: string
}

// 过滤配置
export interface FilterConfig {
  conditions: FilterCondition[]
  operator: 'AND' | 'OR'
}

// 过滤条件
export interface FilterCondition {
  field: string
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains' | 'startsWith' | 'endsWith'
  value: any
}

// 聚合配置
export interface AggregateConfig {
  groupBy: string[]
  aggregations: Aggregation[]
}

// 聚合操作
export interface Aggregation {
  field: string
  operation: 'sum' | 'avg' | 'count' | 'min' | 'max'
  alias: string
}

// 数据转换节点
export interface DataTransformNode extends BaseNode {
  type: NodeType.DATA_TRANSFORM
  config: DataTransformNodeConfig
  // 支持多个输入输出端口
  maxInputs?: number
  maxOutputs?: number
}

// 条件分支节点配置
export interface ConditionNodeConfig {
  conditions: ConditionRule[]
  defaultBranch: string // 默认分支ID
}

// 条件规则
export interface ConditionRule {
  id: string
  name: string
  expression: string // JavaScript表达式
  targetNodeId: string
}

// 条件分支节点
export interface ConditionNode extends BaseNode {
  type: NodeType.CONDITION
  config: ConditionNodeConfig
}

// 并行执行节点配置
export interface ParallelNodeConfig {
  maxConcurrency: number // 最大并发数
  waitForAll: boolean    // 是否等待所有分支完成
  timeoutMs: number      // 超时时间（毫秒）
}

// 并行执行节点
export interface ParallelNode extends BaseNode {
  type: NodeType.PARALLEL
  config: ParallelNodeConfig
}

// 合并节点配置
export interface MergeNodeConfig {
  mergeStrategy: 'FIRST' | 'ALL' | 'MAJORITY' // 合并策略
  timeoutMs: number
}

// 合并节点
export interface MergeNode extends BaseNode {
  type: NodeType.MERGE
  config: MergeNodeConfig
}

// 开始节点
export interface StartNode extends BaseNode {
  type: NodeType.START
  config: {
    inputSchema?: Record<string, any>
  }
}

// 结束节点
export interface EndNode extends BaseNode {
  type: NodeType.END
  config: {
    outputSchema?: Record<string, any>
  }
}

// 联合节点类型
export type WorkflowNode = 
  | StartNode
  | EndNode
  | ApiCallNode
  | DataTransformNode
  | ConditionNode
  | ParallelNode
  | MergeNode

// 节点连接接口
export interface NodeConnection {
  id: string
  fromNodeId: string
  toNodeId: string
  fromOutputId: string
  toInputId: string
  type: ConnectionType
  condition?: string // 条件表达式（用于条件连接）
  config: {
    delay?: number // 延迟时间（毫秒）
    retryOnFailure?: boolean
  }
}

// 工作流定义接口
export interface WorkflowDefinition {
  id: string
  name: string
  description?: string
  version: string
  nodes: WorkflowNode[]
  connections: NodeConnection[]
  variables: WorkflowVariable[]
  settings: WorkflowSettings
  createdAt: string
  updatedAt: string
}

// 工作流变量
export interface WorkflowVariable {
  id: string
  name: string
  type: string
  defaultValue?: any
  description?: string
}

// 工作流设置
export interface WorkflowSettings {
  timeout: number // 总超时时间（秒）
  retryCount: number
  errorHandling: 'STOP' | 'CONTINUE' | 'RETRY'
  logLevel: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'
  enableParallel: boolean
  maxConcurrency: number
}

// 执行上下文
export interface ExecutionContext {
  workflowId: string
  executionId: string
  variables: Record<string, any>
  nodeResults: Record<string, any>
  startTime: string
  endTime?: string
  status: 'RUNNING' | 'SUCCESS' | 'FAILED' | 'CANCELLED'
  error?: string
}

// 节点执行结果
export interface NodeExecutionResult {
  nodeId: string
  status: NodeStatus
  startTime: string
  endTime?: string
  duration?: number
  input?: any
  output?: any
  error?: string
  logs: string[]
}

// 节点模板定义
export interface NodeTemplate {
  type: NodeType
  name: string
  description: string
  icon: string
  category: string
  defaultConfig: Record<string, any>
  inputs: NodeInput[]
  outputs: NodeOutput[]
  configSchema: Record<string, any> // JSON Schema
}

// 预定义节点模板
export const NODE_TEMPLATES: NodeTemplate[] = [
  {
    type: NodeType.START,
    name: '开始',
    description: '工作流开始节点',
    icon: 'Play',
    category: 'control',
    defaultConfig: {},
    inputs: [],
    outputs: [
      {
        id: 'output',
        name: '输出',
        type: 'any',
        description: '开始节点输出'
      }
    ],
    configSchema: {}
  },
  {
    type: NodeType.END,
    name: '结束',
    description: '工作流结束节点',
    icon: 'Stop',
    category: 'control',
    defaultConfig: {},
    inputs: [
      {
        id: 'input',
        name: '输入',
        type: 'any',
        required: false,
        description: '结束节点输入'
      }
    ],
    outputs: [],
    configSchema: {}
  },
  {
    type: NodeType.API_CALL,
    name: 'API调用',
    description: '调用外部API接口',
    icon: 'Connection',
    category: 'api',
    defaultConfig: {
      timeout: 30000,
      retryCount: 3,
      retryDelay: 1000
    },
    inputs: [
      {
        id: 'input',
        name: '输入数据',
        type: 'object',
        required: false,
        description: 'API请求参数'
      }
    ],
    outputs: [
      {
        id: 'output',
        name: '输出数据',
        type: 'object',
        description: 'API响应结果'
      }
    ],
    configSchema: {
      type: 'object',
      properties: {
        systemId: { type: 'string', title: '系统ID' },
        moduleId: { type: 'string', title: '模块ID' },
        apiId: { type: 'string', title: 'API ID' },
        timeout: { type: 'number', title: '超时时间(ms)', default: 30000 },
        retryCount: { type: 'number', title: '重试次数', default: 3 }
      },
      required: ['systemId', 'moduleId', 'apiId']
    }
  },
  {
    type: NodeType.DATA_TRANSFORM,
    name: '数据转换',
    description: '数据映射和格式转换',
    icon: 'Refresh',
    category: 'data',
    defaultConfig: {
      transformType: 'MAPPING',
      mappingRules: []
    },
    inputs: [
      {
        id: 'input',
        name: '输入数据',
        type: 'any',
        required: true,
        description: '待转换的数据'
      }
    ],
    outputs: [
      {
        id: 'output',
        name: '输出数据',
        type: 'any',
        description: '转换后的数据'
      }
    ],
    configSchema: {
      type: 'object',
      properties: {
        transformType: {
          type: 'string',
          enum: ['MAPPING', 'FORMAT', 'FILTER', 'AGGREGATE'],
          title: '转换类型'
        }
      },
      required: ['transformType']
    }
  },
  {
    type: NodeType.CONDITION,
    name: '条件分支',
    description: '根据条件选择执行分支',
    icon: 'Share',
    category: 'control',
    defaultConfig: {
      conditions: [],
      defaultBranch: ''
    },
    inputs: [
      {
        id: 'input',
        name: '输入数据',
        type: 'any',
        required: true,
        description: '用于条件判断的数据'
      }
    ],
    outputs: [
      {
        id: 'true',
        name: '真分支',
        type: 'any',
        description: '条件为真时的输出'
      },
      {
        id: 'false',
        name: '假分支',
        type: 'any',
        description: '条件为假时的输出'
      }
    ],
    configSchema: {
      type: 'object',
      properties: {
        conditions: {
          type: 'array',
          title: '条件规则',
          items: {
            type: 'object',
            properties: {
              name: { type: 'string', title: '条件名称' },
              expression: { type: 'string', title: '条件表达式' }
            }
          }
        }
      }
    }
  },
  {
    type: NodeType.PARALLEL,
    name: '并行执行',
    description: '并行执行多个分支',
    icon: 'Grid',
    category: 'control',
    defaultConfig: {
      maxConcurrency: 5,
      waitForAll: true,
      timeoutMs: 300000
    },
    inputs: [
      {
        id: 'input',
        name: '输入数据',
        type: 'any',
        required: true,
        description: '并行执行的输入数据'
      }
    ],
    outputs: [
      {
        id: 'output',
        name: '输出数据',
        type: 'array',
        description: '所有分支的执行结果'
      }
    ],
    configSchema: {
      type: 'object',
      properties: {
        maxConcurrency: { type: 'number', title: '最大并发数', default: 5 },
        waitForAll: { type: 'boolean', title: '等待所有分支', default: true },
        timeoutMs: { type: 'number', title: '超时时间(ms)', default: 300000 }
      }
    }
  }
]