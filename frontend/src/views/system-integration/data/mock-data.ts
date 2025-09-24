// 系统集成模拟数据

import type { Integration } from './table-config'

// 模拟集成数据
export const mockIntegrations: Integration[] = [
  {
    id: '1',
    name: '用户数据同步',
    type: 'sync',
    status: 'running',
    environment: 'production',
    description: '同步用户数据到数据仓库',
    createdAt: '2024-01-15 10:30:00',
    updatedAt: '2024-01-20 14:20:00',
    lastRunTime: '2024-01-20 14:20:00',
    successCount: 1250,
    errorCount: 5,
    progress: 85
  },
  {
    id: '2',
    name: '订单API集成',
    type: 'api',
    status: 'running',
    environment: 'production',
    description: '第三方订单系统API集成',
    createdAt: '2024-01-10 09:15:00',
    updatedAt: '2024-01-20 11:45:00',
    lastRunTime: '2024-01-20 11:45:00',
    successCount: 2340,
    errorCount: 12,
    progress: 92
  },
  {
    id: '3',
    name: '库存管理工作流',
    type: 'workflow',
    status: 'stopped',
    environment: 'testing',
    description: '自动化库存管理流程',
    createdAt: '2024-01-12 16:20:00',
    updatedAt: '2024-01-18 13:30:00',
    lastRunTime: '2024-01-18 13:30:00',
    successCount: 890,
    errorCount: 3,
    progress: 0
  },
  {
    id: '4',
    name: '消息通知队列',
    type: 'queue',
    status: 'error',
    environment: 'development',
    description: '处理系统消息通知',
    createdAt: '2024-01-08 14:45:00',
    updatedAt: '2024-01-19 16:10:00',
    lastRunTime: '2024-01-19 16:10:00',
    successCount: 567,
    errorCount: 23,
    progress: 0
  },
  {
    id: '5',
    name: '财务数据集成',
    type: 'api',
    status: 'pending',
    environment: 'development',
    description: '集成财务系统数据',
    createdAt: '2024-01-20 08:30:00',
    updatedAt: '2024-01-20 08:30:00',
    successCount: 0,
    errorCount: 0,
    progress: 0
  }
]

// 模拟监控数据
export const mockMonitorData = {
  totalIntegrations: 5,
  runningIntegrations: 2,
  errorIntegrations: 1,
  todayExecutions: 156,
  successRate: 94.2,
  avgResponseTime: 245
}

// 统计数据类型
export interface Statistic {
  title: string
  value: number
  icon: string
  color: 'primary' | 'success' | 'warning' | 'danger' | 'info'
}

// 模拟统计数据
export const mockStatistics: Statistic[] = [
  { title: '总集成数', value: 24, icon: 'Connection', color: 'primary' },
  { title: '活跃集成', value: 18, icon: 'CircleCheck', color: 'success' },
  { title: '集成API数', value: 156, icon: 'Link', color: 'warning' },
  { title: '工作流数', value: 42, icon: 'Share', color: 'info' }
]