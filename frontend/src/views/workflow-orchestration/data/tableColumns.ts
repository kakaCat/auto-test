/**
 * 工作流编排页面表格列配置
 */
import { h, VNode } from 'vue'
import { ElIcon, ElTag, ElButton, ElProgress } from 'element-plus'
import { 
  View, Edit, VideoPlay, VideoPause, CopyDocument, Delete, 
  Share, Connection 
} from '@element-plus/icons-vue'

// 工作流数据接口定义
export interface WorkflowItem {
  id: number
  name: string
  version?: string
  category: string
  nodeCount: number
  description: string
  status: 'running' | 'stopped' | 'draft' | 'published'
  executionCount: number
  successRate: number
  lastExecutionTime?: string
  creator: string
}

// 表格处理器接口定义
export interface TableHandlers {
  viewWorkflow?: (row: WorkflowItem) => void
  editWorkflow?: (row: WorkflowItem) => void
  executeWorkflow?: (row: WorkflowItem) => void
  stopWorkflow?: (row: WorkflowItem) => void
  copyWorkflow?: (row: WorkflowItem) => void
  deleteWorkflow?: (row: WorkflowItem) => void
}

// 表格列模板参数接口
export interface ColumnTemplateParams {
  row: WorkflowItem
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

// 获取状态颜色
export const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    running: 'success',
    stopped: 'info',
    draft: 'warning',
    published: 'primary'
  }
  return colorMap[status] || 'info'
}

// 获取状态标签
export const getStatusLabel = (status: string): string => {
  const labelMap: Record<string, string> = {
    running: '运行中',
    stopped: '已停止',
    draft: '草稿',
    published: '已发布'
  }
  return labelMap[status] || status
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

// 工作流表格列配置
export const workflowTableColumns: TableColumn[] = [
  {
    type: 'selection',
    width: 55
  },
  {
    prop: 'name',
    label: '工作流名称',
    minWidth: 200,
    template: ({ row }: ColumnTemplateParams) => {
      return h('div', { class: 'workflow-name' }, [
        h(ElIcon, { class: 'workflow-icon' }, () => h(Share)),
        h('div', { class: 'name-content' }, [
          h('div', { class: 'name' }, row.name),
          row.version ? h('div', { class: 'version' }, `v${row.version}`) : null
        ])
      ])
    }
  },
  {
    prop: 'category',
    label: '分类',
    width: 120,
    template: ({ row }: ColumnTemplateParams) => {
      return h(ElTag, { size: 'small', type: 'info' }, () => row.category)
    }
  },
  {
    prop: 'nodeCount',
    label: '节点数',
    width: 80,
    template: ({ row }: ColumnTemplateParams) => {
      return h('div', { class: 'node-count' }, [
        h(ElIcon, { style: 'margin-right: 4px; color: var(--primary-color)' }, () => h(Connection)),
        h('span', row.nodeCount)
      ])
    }
  },
  {
    prop: 'description',
    label: '描述',
    minWidth: 200,
    showOverflowTooltip: true
  },
  {
    prop: 'status',
    label: '状态',
    width: 100,
    template: ({ row }: ColumnTemplateParams) => {
      return h('div', { class: 'status-indicator' }, [
        h(ElTag, { 
          type: getStatusColor(row.status) as any, 
          size: 'small' 
        }, () => getStatusLabel(row.status)),
        row.status === 'running' ? h('div', { class: 'running-indicator' }) : null
      ])
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
    prop: 'creator',
    label: '创建者',
    width: 100
  },
  {
    label: '操作',
    width: 280,
    fixed: 'right',
    template: ({ row, handlers }: ColumnTemplateParams) => {
      const buttons: VNode[] = [
        h(ElButton, {
          type: 'text',
          onClick: () => handlers.viewWorkflow?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(View)),
            '查看'
          ]
        }),
        h(ElButton, {
          type: 'text',
          onClick: () => handlers.editWorkflow?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(Edit)),
            '编辑'
          ]
        })
      ]

      // 根据状态显示不同的执行/停止按钮
      if (row.status !== 'running') {
        buttons.push(
          h(ElButton, {
            type: 'text',
            onClick: () => handlers.executeWorkflow?.(row)
          }, {
            default: () => [
              h(ElIcon, () => h(VideoPlay)),
              '执行'
            ]
          })
        )
      } else {
        buttons.push(
          h(ElButton, {
            type: 'text',
            style: 'color: var(--warning-color)',
            onClick: () => handlers.stopWorkflow?.(row)
          }, {
            default: () => [
              h(ElIcon, () => h(VideoPause)),
              '停止'
            ]
          })
        )
      }

      buttons.push(
        h(ElButton, {
          type: 'text',
          onClick: () => handlers.copyWorkflow?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(CopyDocument)),
            '复制'
          ]
        }),
        h(ElButton, {
          type: 'text',
          style: 'color: var(--danger-color)',
          onClick: () => handlers.deleteWorkflow?.(row)
        }, {
          default: () => [
            h(ElIcon, () => h(Delete)),
            '删除'
          ]
        })
      )

      return buttons
    }
  }
]