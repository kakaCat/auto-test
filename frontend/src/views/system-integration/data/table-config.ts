// 系统集成表格配置

import { PAGE_SIZE_OPTIONS } from './constants'

export interface Integration {
  id: string
  name: string
  type: 'api' | 'workflow' | 'sync' | 'queue'
  status: 'running' | 'stopped' | 'error' | 'pending'
  environment: 'development' | 'testing' | 'production'
  description: string
  createdAt: string
  updatedAt: string
  lastRunTime?: string
  successCount: number
  errorCount: number
  progress?: number
}

// 表格列配置
export const tableColumns = [
  {
    type: 'selection',
    width: 55,
    align: 'center'
  },
  {
    prop: 'name',
    label: '集成名称',
    minWidth: 150,
    showOverflowTooltip: true
  },
  {
    prop: 'type',
    label: '类型',
    width: 100,
    align: 'center'
  },
  {
    prop: 'status',
    label: '状态',
    width: 100,
    align: 'center'
  },
  {
    prop: 'environment',
    label: '环境',
    width: 100,
    align: 'center'
  },
  {
    prop: 'description',
    label: '描述',
    minWidth: 200,
    showOverflowTooltip: true
  },
  {
    prop: 'successCount',
    label: '成功次数',
    width: 100,
    align: 'center'
  },
  {
    prop: 'errorCount',
    label: '错误次数',
    width: 100,
    align: 'center'
  },
  {
    prop: 'lastRunTime',
    label: '最后运行时间',
    width: 160,
    align: 'center'
  },
  {
    prop: 'actions',
    label: '操作',
    width: 200,
    align: 'center',
    fixed: 'right'
  }
]

// 表格配置
export const tableConfig = {
  columns: tableColumns,
  pagination: {
    pageSize: 20,
    pageSizes: PAGE_SIZE_OPTIONS,
    layout: 'total, sizes, prev, pager, next, jumper'
  },
  selection: true,
  stripe: true,
  border: true,
  size: 'default' as const
}

// 搜索表单字段类型
export interface Field {
  prop: string
  label: string
  type: 'input' | 'select'
  placeholder: string
  clearable: boolean
  options?: { label: string; value: string }[]
}

// 搜索表单配置类型
export interface SearchConfig {
  fields: Field[]
}

// 集成类型选项
const INTEGRATION_TYPE_OPTIONS = [
  { label: 'API接口', value: 'api' },
  { label: '工作流', value: 'workflow' },
  { label: '数据同步', value: 'sync' },
  { label: '消息队列', value: 'queue' }
]

// 状态选项
const STATUS_OPTIONS = [
  { label: '运行中', value: 'running' },
  { label: '已停止', value: 'stopped' },
  { label: '错误', value: 'error' },
  { label: '待配置', value: 'pending' }
]

// 环境选项
const ENVIRONMENT_OPTIONS = [
  { label: '开发环境', value: 'development' },
  { label: '测试环境', value: 'testing' },
  { label: '生产环境', value: 'production' }
]

// 搜索表单配置
export const searchFormConfig: SearchConfig = {
  fields: [
    {
      prop: 'name',
      label: '集成名称',
      type: 'input' as const,
      placeholder: '请输入集成名称',
      clearable: true
    },
    {
      prop: 'type',
      label: '集成类型',
      type: 'select' as const,
      placeholder: '请选择集成类型',
      clearable: true,
      options: INTEGRATION_TYPE_OPTIONS
    },
    {
      prop: 'status',
      label: '状态',
      type: 'select' as const,
      placeholder: '请选择状态',
      clearable: true,
      options: STATUS_OPTIONS
    },
    {
      prop: 'environment',
      label: '环境',
      type: 'select' as const,
      placeholder: '请选择环境',
      clearable: true,
      options: ENVIRONMENT_OPTIONS
    }
  ]
}

// 表格行操作配置
export const rowActions = [
  { label: '查看', action: 'view', type: 'primary', icon: 'View' },
  { label: '编辑', action: 'edit', type: 'primary', icon: 'Edit' },
  { label: '启动', action: 'start', type: 'success', icon: 'VideoPlay' },
  { label: '停止', action: 'stop', type: 'warning', icon: 'VideoPause' },
  { label: '同步', action: 'sync', type: 'info', icon: 'Refresh' },
  { label: '删除', action: 'delete', type: 'danger', icon: 'Delete' }
]