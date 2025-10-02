// 系统集成页面常量定义

export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]

// 集成类型选项
export const INTEGRATION_TYPE_OPTIONS = [
  { label: 'API接口', value: 'api', color: 'primary' },
  { label: '工作流', value: 'workflow', color: 'success' },
  { label: '数据同步', value: 'sync', color: 'warning' },
  { label: '消息队列', value: 'queue', color: 'info' }
]

// 集成状态选项
export const INTEGRATION_STATUS_OPTIONS = [
  { label: '运行中', value: 'running', color: 'success' },
  { label: '已停止', value: 'stopped', color: 'info' },
  { label: '错误', value: 'error', color: 'danger' },
  { label: '待配置', value: 'pending', color: 'warning' }
]

// 环境选项
export const ENVIRONMENT_OPTIONS = [
  { label: '开发环境', value: 'development', color: 'info' },
  { label: '测试环境', value: 'testing', color: 'warning' },
  { label: '生产环境', value: 'production', color: 'success' }
]

// 类型定义
export interface Action {
  label: string
  type: 'primary' | 'default' | 'success' | 'warning' | 'danger' | 'info'
  action: string
  icon: string
}

// 页面配置
export const pageConfig = {
  title: '系统集成',
  description: '接口流程编排集成模块，提供一站式接口流程管理体验',
  actions: [
    { label: '新建集成', type: 'primary' as const, action: 'create', icon: 'Plus' },
    { label: '导入配置', type: 'default' as const, action: 'import', icon: 'Upload' },
    { label: '刷新数据', type: 'default' as const, action: 'refresh', icon: 'Refresh' }
  ] as Action[]
}

// 快速创建选项
export const quickCreateOptions = [
  {
    title: 'API接口集成',
    description: '快速创建API接口集成',
    icon: 'Connection',
    type: 'api'
  },
  {
    title: '工作流集成',
    description: '创建复杂的工作流程',
    icon: 'Share',
    type: 'workflow'
  }
]

// 批量操作选项
export const batchActions = [
  { label: '批量启动', action: 'start', type: 'success' as const, icon: 'VideoPlay' },
  { label: '批量停止', action: 'stop', type: 'warning' as const, icon: 'VideoPause' },
  { label: '批量同步', action: 'sync', type: 'info' as const, icon: 'Refresh' },
  { label: '批量删除', action: 'delete', type: 'danger' as const, icon: 'Delete' }
] as Action[]

// 监控数据刷新间隔（毫秒）
export const MONITOR_REFRESH_INTERVAL = 30000

// 默认分页配置
export const DEFAULT_PAGINATION = {
  currentPage: 1,
  pageSize: 20,
  total: 0,
  // 兼容统一分页字段
  page: 1,
  size: 20
}