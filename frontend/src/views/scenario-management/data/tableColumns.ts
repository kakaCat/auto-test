/**
 * 用例场景管理页面表格列配置
 */
import { h, VNode } from 'vue'
import { ElIcon, ElTag, ElButton, ElProgress } from 'element-plus'
import { 
  View, Edit, VideoPlay, CopyDocument, Delete 
} from '@element-plus/icons-vue'

// 场景数据接口定义
export interface ScenarioItem {
  id: number
  name: string
  description: string
  type: 'sequential' | 'parallel' | 'mixed'
  apiCount: number
  status: 'active' | 'inactive' | 'draft'
  executionCount: number
  successRate: number
  lastExecutionTime?: string
}

// 表格处理器接口定义
export interface TableHandlers {
  viewScenario?: (row: ScenarioItem) => void
  editScenario?: (row: ScenarioItem) => void
  executeScenario?: (row: ScenarioItem) => void
  copyScenario?: (row: ScenarioItem) => void
  deleteScenario?: (row: ScenarioItem) => void
}

// 表格列模板参数接口
export interface ColumnTemplateParams {
  row: ScenarioItem
  handlers: TableHandlers
}

// 表格列配置接口
export interface TableColumn {
  type?: string
  prop?: string
  label?: string
  width?: number
  minWidth?: number
  fixed?: string
  showOverflowTooltip?: boolean
  template?: (params: ColumnTemplateParams) => VNode | VNode[] | string
}

// 获取执行类型标签
export const getTypeLabel = (type: string): string => {
  const labelMap: Record<string, string> = {
    sequential: '顺序执行',
    parallel: '并行执行',
    mixed: '混合执行'
  }
  return labelMap[type] || type
}

// 获取执行类型颜色
export const getTypeColor = (type: string): string => {
  const colorMap: Record<string, string> = {
    sequential: 'primary',
    parallel: 'success',
    mixed: 'warning'
  }
  return colorMap[type] || 'info'
}

// 获取状态标签
export const getStatusLabel = (status: string): string => {
  const labelMap: Record<string, string> = {
    active: '启用',
    inactive: '禁用',
    draft: '草稿'
  }
  return labelMap[status] || status
}

// 获取状态颜色
export const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    draft: 'warning'
  }
  return colorMap[status] || 'info'
}

// 获取进度条颜色
export const getProgressColor = (percentage: number): string => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 60) return '#e6a23c'
  return '#f56c6c'
}

// 格式化时间
export const formatTime = (time?: string): string => {
  if (!time) return '-'
  return new Date(time).toLocaleString()
}

// 场景表格列配置
export const scenarioTableColumns: TableColumn[] = [
  {
    type: 'selection',
    width: 55
  },
  {
    prop: 'name',
    label: '场景名称',
    minWidth: 200,
    showOverflowTooltip: true
  },
  {
    prop: 'description',
    label: '描述',
    minWidth: 200,
    showOverflowTooltip: true
  },
  {
    prop: 'type',
    label: '执行类型',
    width: 120,
    template: ({ row }: ColumnTemplateParams) => {
      return h(ElTag, { 
        type: getTypeColor(row.type) as any, 
        size: 'small' 
      }, () => getTypeLabel(row.type))
    }
  },
  {
    prop: 'apiCount',
    label: 'API数量',
    width: 100
  },
  {
    prop: 'status',
    label: '状态',
    width: 100,
    template: ({ row }: ColumnTemplateParams) => {
      return h(ElTag, { 
        type: getStatusColor(row.status) as any, 
        size: 'small' 
      }, () => getStatusLabel(row.status))
    }
  },
  {
    prop: 'executionCount',
    label: '执行次数',
    width: 100
  },
  {
    prop: 'successRate',
    label: '成功率',
    width: 100,
    template: ({ row }: ColumnTemplateParams) => {
      return h('div', { class: 'success-rate' }, [
        h('span', `${row.successRate}%`),
        h(ElProgress, {
          percentage: row.successRate,
          strokeWidth: 4,
          showText: false,
          color: getProgressColor(row.successRate)
        })
      ])
    }
  },
  {
    prop: 'lastExecutionTime',
    label: '最后执行',
    width: 150,
    template: ({ row }: ColumnTemplateParams) => {
      return formatTime(row.lastExecutionTime)
    }
  },
  {
    label: '操作',
    width: 250,
    fixed: 'right',
    template: ({ row, handlers }: ColumnTemplateParams) => {
      return [
        h(ElButton, {
          type: 'text',
          onClick: () => handlers.viewScenario?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(View)),
            '查看'
          ]
        }),
        h(ElButton, {
          type: 'text',
          onClick: () => handlers.editScenario?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(Edit)),
            '编辑'
          ]
        }),
        h(ElButton, {
          type: 'text',
          onClick: () => handlers.executeScenario?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(VideoPlay)),
            '执行'
          ]
        }),
        h(ElButton, {
          type: 'text',
          onClick: () => handlers.copyScenario?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(CopyDocument)),
            '复制'
          ]
        }),
        h(ElButton, {
          type: 'text',
          style: 'color: var(--danger-color)',
          onClick: () => handlers.deleteScenario?.(row)
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