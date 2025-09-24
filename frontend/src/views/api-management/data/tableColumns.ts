/**
 * API管理页面表格列配置
 */
import { h, VNode } from 'vue'
import { ElIcon, ElTag, ElTooltip, ElSwitch, ElButton } from 'element-plus'
import { Link, View, Edit, VideoPlay, Delete } from '@element-plus/icons-vue'

// API数据接口定义
export interface ApiItem {
  id: number
  name: string
  serviceName: string
  moduleId: string
  version?: string
  method: string
  protocol: string
  url: string
  description: string
  status: 'active' | 'inactive'
  callCount: number
  lastCallTime?: string
  headers?: any[]
  parameters?: any[]
}

// 表格处理器接口定义
export interface TableHandlers {
  handleApiStatusChange?: (row: ApiItem) => void
  viewApi?: (row: ApiItem) => void
  editApi?: (row: ApiItem) => void
  testApi?: (row: ApiItem) => void
  deleteApi?: (row: ApiItem) => void
}

// 表格列模板参数接口
export interface ColumnTemplateParams {
  row: ApiItem
  handlers: TableHandlers
}

// 表格列配置接口
export interface TableColumn {
  prop?: string
  label: string
  width?: number
  minWidth?: number
  fixed?: string
  showOverflowTooltip?: boolean
  template?: (params: ColumnTemplateParams) => VNode | VNode[] | string
}

// 获取方法类型样式
export const getMethodType = (method: string): string => {
  const typeMap: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return typeMap[method] || 'info'
}

// 格式化时间
export const formatTime = (time?: string): string => {
  if (!time) return '-'
  return new Date(time).toLocaleString()
}

// API表格列配置
export const apiTableColumns: TableColumn[] = [
  {
    prop: 'name',
    label: 'API名称',
    minWidth: 150,
    template: ({ row }: ColumnTemplateParams) => {
      return h('div', { class: 'api-name' }, [
        h(ElIcon, { class: 'api-icon' }, () => h(Link)),
        h('span', { class: 'name' }, row.name),
        row.version ? h(ElTag, { size: 'small', type: 'info' }, () => `v${row.version}`) : null
      ])
    }
  },
  {
    prop: 'method',
    label: '方法',
    width: 80,
    template: ({ row }: ColumnTemplateParams) => {
      return h(ElTag, { 
        type: getMethodType(row.method) as any, 
        size: 'small' 
      }, () => row.method)
    }
  },
  {
    prop: 'url',
    label: 'URL',
    minWidth: 200,
    template: ({ row }: ColumnTemplateParams) => {
      return h(ElTooltip, { 
        content: row.url, 
        placement: 'top' 
      }, {
        default: () => h('span', { class: 'url-text' }, row.url)
      })
    }
  },
  {
    prop: 'description',
    label: '描述',
    minWidth: 150,
    showOverflowTooltip: true
  },
  {
    prop: 'status',
    label: '状态',
    width: 80,
    template: ({ row, handlers }: ColumnTemplateParams) => {
      return h(ElSwitch, {
        modelValue: row.status,
        activeValue: 'active',
        inactiveValue: 'inactive',
        onChange: (value: any) => {
          row.status = value as 'active' | 'inactive'
          handlers.handleApiStatusChange?.(row)
        }
      })
    }
  },
  {
    prop: 'callCount',
    label: '调用次数',
    width: 100
  },
  {
    prop: 'lastCallTime',
    label: '最后调用',
    width: 150,
    template: ({ row }: ColumnTemplateParams) => {
      return formatTime(row.lastCallTime)
    }
  },
  {
    label: '操作',
    width: 200,
    fixed: 'right',
    template: ({ row, handlers }: ColumnTemplateParams) => {
      return [
        h(ElButton, {
          type: 'text',
          onClick: () => handlers.viewApi?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(View)),
            '查看'
          ]
        }),
        h(ElButton, {
          type: 'text',
          onClick: () => handlers.editApi?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(Edit)),
            '编辑'
          ]
        }),
        h(ElButton, {
          type: 'text',
          onClick: () => handlers.testApi?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(VideoPlay)),
            '测试'
          ]
        }),
        h(ElButton, {
          type: 'text',
          style: 'color: var(--danger-color)',
          onClick: () => handlers.deleteApi?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(Delete)),
            '删除'
          ]
        })
      ]
    }
  }
]