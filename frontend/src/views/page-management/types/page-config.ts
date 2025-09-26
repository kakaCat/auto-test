// 页面配置相关类型定义

// 页面基本信息
export interface PageBasicInfo {
  name: string                    // 页面名称
  path: string                    // 页面路径
  description: string             // 页面描述
  type: PageType                  // 页面类型
  icon: string                    // 页面图标
  enabled: boolean                // 是否启用
  systemId?: number | null        // 所属系统ID
}

// 页面类型
export type PageType = 'normal' | 'modal' | 'fullscreen' | 'embedded' | 'mobile'

// 页面组件
export interface PageComponent {
  id: string                      // 组件唯一ID
  type: ComponentType             // 组件类型
  name: string                    // 组件名称
  props: Record<string, any>      // 组件属性
  style: ComponentStyle           // 组件样式
  position: ComponentPosition     // 组件位置
  children?: PageComponent[]      // 子组件
  events?: ComponentEvent[]       // 组件事件
}

// 组件类型
export type ComponentType = 
  | 'button' | 'input' | 'text' | 'image' | 'divider'           // 基础组件
  | 'form' | 'form-item' | 'select' | 'checkbox' | 'radio'      // 表单组件
  | 'table' | 'list' | 'card' | 'chart'                        // 数据展示
  | 'container' | 'grid' | 'column' | 'tabs'                   // 布局组件
  | 'modal' | 'drawer' | 'dropdown' | 'navigation'             // 交互组件

// 组件样式
export interface ComponentStyle {
  width?: number | string
  height?: number | string
  backgroundColor?: string
  color?: string
  fontSize?: number
  fontWeight?: string | number
  border?: string
  borderRadius?: number
  padding?: string
  margin?: string
  [key: string]: any
}

// 组件位置
export interface ComponentPosition {
  x: number                       // X坐标
  y: number                       // Y坐标
  z: number                       // Z轴层级
  width: number                   // 宽度
  height: number                  // 高度
}

// 组件事件
export interface ComponentEvent {
  type: EventType                 // 事件类型
  trigger: string                 // 触发条件
  action: EventAction             // 执行动作
  config?: Record<string, any>    // 事件配置
}

// 事件类型
export type EventType = 'click' | 'hover' | 'change' | 'load' | 'submit' | 'custom'

// 事件动作
export interface EventAction {
  type: ActionType                // 动作类型
  target?: string                 // 目标对象
  params?: Record<string, any>    // 动作参数
}

// 动作类型
export type ActionType = 
  | 'navigate' | 'refresh' | 'back'                            // 页面操作
  | 'show' | 'hide' | 'enable' | 'disable' | 'update'         // 组件操作
  | 'api-call'                                                 // API调用
  | 'message' | 'notification' | 'sound'                      // 用户反馈
  | 'save' | 'clear' | 'validate'                             // 数据操作

// 页面布局
export interface PageLayout {
  components: PageComponent[]     // 页面组件列表
  canvas: CanvasConfig           // 画布配置
}

// 画布配置
export interface CanvasConfig {
  width: number                   // 画布宽度
  height: number                  // 画布高度
  scale: number                   // 缩放比例
  grid: boolean                   // 是否显示网格
  backgroundColor?: string        // 背景颜色
  backgroundImage?: string        // 背景图片
}

// API配置
export interface PageApiConfig {
  systemId: number | null         // 所属系统ID
  moduleId: number | null         // 所属模块ID
  apis: ApiConfigItem[]           // API配置列表
  flowChart: FlowChart           // API调用流程图
}

// API配置项
export interface ApiConfigItem {
  id: string                      // 配置ID
  apiId: number                   // API接口ID
  name: string                    // API名称
  method: string                  // HTTP方法
  path: string                    // API路径
  callType: ApiCallType          // 调用类型
  order: number                   // 执行顺序
  delay?: number                  // 延迟时间(ms)
  timeout?: number                // 超时时间(ms)
  retry?: number                  // 重试次数
  condition?: string              // 执行条件
  params: ApiParamMapping        // 参数映射
  response: ApiResponseMapping   // 响应映射
  error: ApiErrorConfig          // 错误处理
}

// API调用类型
export type ApiCallType = 'serial' | 'parallel' | 'conditional'

// API参数映射
export interface ApiParamMapping {
  static: Record<string, any>     // 静态参数
  dynamic: Record<string, string> // 动态参数绑定
  transform?: string              // 参数转换规则
}

// API响应映射
export interface ApiResponseMapping {
  extract: Record<string, string> // 数据提取路径
  transform?: string              // 数据转换规则
  target?: string                 // 目标组件或变量
}

// API错误配置
export interface ApiErrorConfig {
  message?: string                // 错误提示信息
  retry?: boolean                 // 是否重试
  fallback?: string               // 降级处理
}

// 页面交互配置
export interface PageInteractionConfig {
  events: InteractionEvent[]      // 交互事件列表
  flowChart: FlowChart           // 交互流程图
}

// 交互事件
export interface InteractionEvent {
  id: string                      // 事件ID
  name: string                    // 事件名称
  trigger: EventTrigger          // 触发器
  condition?: string              // 触发条件
  actions: InteractionAction[]    // 执行动作列表
  enabled: boolean                // 是否启用
}

// 事件触发器
export interface EventTrigger {
  type: EventType                 // 触发类型
  target: string                  // 目标组件ID
  event: string                   // 具体事件
  config?: Record<string, any>    // 触发配置
}

// 交互动作
export interface InteractionAction {
  id: string                      // 动作ID
  type: ActionType                // 动作类型
  target?: string                 // 目标对象
  params: Record<string, any>     // 动作参数
  delay?: number                  // 延迟执行(ms)
  condition?: string              // 执行条件
}

// 流程图
export interface FlowChart {
  nodes: FlowNode[]               // 流程节点
  edges: FlowEdge[]               // 连接线
}

// 流程节点
export interface FlowNode {
  id: string                      // 节点ID
  type: NodeType                  // 节点类型
  label: string                   // 节点标签
  position: { x: number; y: number } // 节点位置
  data?: Record<string, any>      // 节点数据
  style?: Record<string, any>     // 节点样式
}

// 节点类型
export type NodeType = 'start' | 'end' | 'process' | 'decision' | 'api' | 'event' | 'action'

// 连接线
export interface FlowEdge {
  id: string                      // 连接线ID
  source: string                  // 源节点ID
  target: string                  // 目标节点ID
  label?: string                  // 连接线标签
  type?: EdgeType                 // 连接线类型
  style?: Record<string, any>     // 连接线样式
}

// 连接线类型
export type EdgeType = 'default' | 'straight' | 'step' | 'smoothstep' | 'bezier'

// 完整的页面配置数据
export interface PageConfigData {
  basicInfo: PageBasicInfo        // 基本信息
  layout: PageLayout              // 页面布局
  apiConfig: PageApiConfig        // API配置
  interaction: PageInteractionConfig // 交互配置
}

// 页面配置模板
export interface PageConfigTemplate {
  id: string                      // 模板ID
  name: string                    // 模板名称
  description: string             // 模板描述
  category: string                // 模板分类
  config: PageConfigData          // 配置数据
  preview?: string                // 预览图片
  tags?: string[]                 // 标签
  createdAt: string               // 创建时间
  updatedAt: string               // 更新时间
}

// 配置验证结果
export interface ValidationResult {
  valid: boolean                  // 是否有效
  errors: ValidationError[]       // 错误列表
  warnings: ValidationWarning[]   // 警告列表
}

// 验证错误
export interface ValidationError {
  field: string                   // 错误字段
  message: string                 // 错误信息
  code: string                    // 错误代码
}

// 验证警告
export interface ValidationWarning {
  field: string                   // 警告字段
  message: string                 // 警告信息
  code: string                    // 警告代码
}